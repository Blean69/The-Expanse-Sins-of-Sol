from pathlib import Path
import zipfile,hashlib,json,shutil,sys,numpy as np
from common import Gltf,write
from polish_ui import render
R=Path(__file__).resolve().parents[1];O=R/'assets/original/update15-truman';D=R/'assets/derived/update15-truman';A=R/'audit/update15-truman';O.mkdir(parents=True,exist_ok=True);D.mkdir(parents=True,exist_ok=True);A.mkdir(parents=True,exist_ok=True)
src=Path('/home/haker/Downloads/truman_class.zip');data=src.read_bytes();p=O/src.name
if not p.exists():p.write_bytes(data)
assert p.read_bytes()==data
master=O/'master'
with zipfile.ZipFile(p) as z:
 for f in z.infolist():
  q=Path(f.filename);assert not q.is_absolute() and '..' not in q.parts and not(f.external_attr>>16&0o170000)==0o120000
 if not master.exists():z.extractall(master)
 for f in z.infolist():
  if not f.is_dir():assert (master/f.filename).read_bytes()==z.read(f), 'Preserved master differs from supplied archive: '+f.filename
g=Gltf(master/'scene.gltf');rows=[];parts=[]
for node,n in enumerate(g.g['nodes']):
 if'mesh'not in n:continue
 for pr in g.g['meshes'][n['mesh']]['primitives']:
  v=g.positions(node,pr);idx=g.accessor(pr['indices']).ravel().reshape(-1,3);m=g.world[node][:3,:3];nn=g.accessor(pr['attributes']['NORMAL'])@np.linalg.inv(m);nn/=np.linalg.norm(nn,axis=1)[:,None];t=g.accessor(pr['attributes']['TANGENT']);t[:,:3]=t[:,:3]@m.T;t[:,:3]/=np.linalg.norm(t[:,:3],axis=1)[:,None];uv=g.accessor(pr['attributes']['TEXCOORD_0']);parts.append(dict(v=v,n=nn,t=t,uv=uv,i=idx,material='truman_material'));rows.append({'node':node,'vertices':len(v),'triangles':len(idx),'bounds':[v.min(0).tolist(),v.max(0).tolist()]})
np.savez(D/'source-parts.npz',**{f'{i}_{k}':v for i,p in enumerate(parts) for k,v in p.items() if k!='material'})
verts=np.concatenate([p['v'] for p in parts]);write(A/'source-audit.json',{'archive_sha256':hashlib.sha256(data).hexdigest(),'master_hashes':{str(p.relative_to(master)):hashlib.sha256(p.read_bytes()).hexdigest() for p in master.rglob('*')if p.is_file()},'parts':rows,'bounds':[verts.min(0).tolist(),verts.max(0).tolist()],'triangles':sum(len(p['i'])for p in parts),'animations':0,'source_material_double_sided':True,'credit':g.g['asset']['extras']})
tex=np.full((1,1,4),255,np.uint8);meshes=[(p['v'][p['i']],p['uv'][p['i']],tex,[.5,.55,.6,1],'OPAQUE')for p in parts]
for name,basis in [('xy',[[1,0,0],[0,1,0],[0,0,1]]),('xz',[[1,0,0],[0,0,1],[0,-1,0]]),('yz',[[0,1,0],[0,0,1],[1,0,0]])]:render(meshes,(1400,800),np.array(basis)).save(A/(name+'.png'))
print(json.dumps(rows));print(verts.min(0),verts.max(0))
