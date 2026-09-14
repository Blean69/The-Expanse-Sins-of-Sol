"""Offline source intake/geometry visualization; never installs or edits originals."""
import sys,zipfile,json,hashlib,subprocess
from pathlib import Path
import numpy as np
sys.path.insert(0,'tools');from common import Gltf
out=Path('assets/derived/update20-intake'); report=[]
files=['un-one-from-the-expanse-tv-show-1100-scale-model_files.zip','nauvoobehemothmedina-station-the-expanse-model_files.zip','lns-gathering-storm-the-expanse-model_files.zip','UN IPBM from The Expanse - 2639049.zip','UNN Murphy Class Destroyer - 7350801.zip']
for k,f in enumerate(files):
 p=Path('/home/haker/Downloads')/f;r={'archive':str(p),'sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'entries':[]}
 with zipfile.ZipFile(p) as z:
  for info in z.infolist():
   if info.is_dir():continue
   b=z.read(info);e={'name':info.filename,'bytes':len(b),'sha256':hashlib.sha256(b).hexdigest()}
   if info.filename.lower().endswith('.stl'):
    n=int.from_bytes(b[80:84],'little');assert len(b)==84+50*n
    a=np.frombuffer(b[84:],dtype=np.dtype([('n','<f4',3),('v','<f4',(3,3)),('attr','<u2')]))['v'].astype(float)
    e.update(triangles=n,bounds=[a.min((0,1)).tolist(),a.max((0,1)).tolist()],dimensions=np.ptp(a.reshape(-1,3),axis=0).tolist(),finite=bool(np.isfinite(a).all()),degenerate_triangles=int((np.linalg.norm(np.cross(a[:,1]-a[:,0],a[:,2]-a[:,0]),axis=1)<1e-10).sum()),has_uv=False,has_materials=False)
    np.savez_compressed(out/f'{k}_{Path(info.filename).stem}.npz',tri=a)
   elif info.filename.lower().endswith('.txt'):e['text']=b.decode(errors='replace')
   elif info.filename.lower().endswith('.pdf'):
    dest=out/Path(info.filename).name;dest.write_bytes(b);txt=subprocess.check_output(['pdftotext',str(dest),'-'],text=True);e['text']=txt
   r['entries'].append(e)
 report.append(r)
root=Path('/run/media/haker/NVME 2/expanse-extracted/UNN-Urshanabi/sdk-candidate');rows=[]
for p in sorted(root.rglob('*.gltf')):
 g=Gltf(p);vs=[];n=0;uv=True
 for ni,node in enumerate(g.g['nodes']):
  if 'mesh' not in node:continue
  for prim in g.g['meshes'][node['mesh']]['primitives']:
   vs.append(g.positions(ni,prim));n+=g.accessor(prim['indices']).size//3;uv &= 'TEXCOORD_0' in prim['attributes']
 v=np.concatenate(vs);rows.append({'file':str(p),'sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'triangles':n,'dimensions':np.ptp(v,axis=0).tolist(),'bounds':[v.min(0).tolist(),v.max(0).tolist()],'has_uv':uv,'material_count':len(g.g.get('materials',[])),'images':g.g.get('images',[]),'nodes':len(g.g['nodes'])})
Path('audit/update20-assets/intake.json').write_text(json.dumps({'archives':report,'urshanabi':rows},indent=2))
for r in report:
 print(r['archive'])
 for e in r['entries']:
  if 'triangles' in e:print(e['name'],e['triangles'],e['dimensions'])
  if 'text' in e:print(e['text'][:4500])
print(json.dumps(rows,indent=2))
