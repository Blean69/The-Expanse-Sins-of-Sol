from pathlib import Path,PurePosixPath
import zipfile,hashlib,json,shutil,numpy as np
from PIL import Image
from common import Gltf
from polish_ui import write,render
ROOT=Path(__file__).resolve().parents[1];SRC=Path('/home/haker/Downloads/Series_6_Sunflare_Racing_Pinnace_[The_Expanse].zip');ORIG=ROOT/'assets/original/update12-sunflare';MASTER=ROOT/'assets/source/update12-sunflare';OUT=ROOT/'assets/derived/update12-c';AUD=ROOT/'audit/update12-c';BUILD=ROOT/'build/update12-c'
for p in [ORIG,MASTER,OUT,AUD,BUILD]:p.mkdir(parents=True,exist_ok=True)
b=SRC.read_bytes();copy=ORIG/SRC.name
if not copy.exists():shutil.copyfile(SRC,copy)
assert copy.read_bytes()==b
with zipfile.ZipFile(SRC)as z:
 for i in z.infolist():
  path=PurePosixPath(i.filename);assert not path.is_absolute()and'..'not in path.parts and not((i.external_attr>>16)&0o170000)==0o120000
  dest=MASTER/path
  if i.is_dir():dest.mkdir(parents=True,exist_ok=True);continue
  data=z.read(i);dest.parent.mkdir(parents=True,exist_ok=True)
  if dest.exists():assert dest.read_bytes()==data
  else:dest.write_bytes(data)
source=next(MASTER.glob('*.gltf'));a=Gltf(source);parts=[];rows=[]
for ni,node in enumerate(a.g['nodes']):
 if 'mesh'not in node:continue
 for pi,p in enumerate(a.g['meshes'][node['mesh']]['primitives']):
  v=a.positions(ni,p);idx=a.accessor(p['indices']).reshape(-1,3);parts.append(v[idx]);rows.append({'node':ni,'name':node.get('name'),'primitive':pi,'triangles':len(idx),'material':p.get('material'),'bounds':[v.min(0).tolist(),v.max(0).tolist()],'attributes':list(p['attributes'])})
tri=np.concatenate(parts);textures=[]
for im in a.g.get('images',[]):
 p=MASTER/im['uri'];x=Image.open(p);textures.append({'path':im['uri'],'size':list(x.size),'mode':x.mode,'sha256':hashlib.sha256(p.read_bytes()).hexdigest()})
report={'archive':str(SRC),'archive_sha256':hashlib.sha256(b).hexdigest(),'source':str(source),'asset_metadata':a.g['asset'],'triangles':len(tri),'nodes':a.g['nodes'],'animations':a.g.get('animations',[]),'skins':a.g.get('skins',[]),'materials':a.g['materials'],'textures':textures,'parts':rows,'bounds':[tri.min((0,1)).tolist(),tri.max((0,1)).tolist()],'creator':'No separate attribution document found; see actual asset_metadata','license':'No separate license document found; see actual asset_metadata','permission':'User supplied package and requested local conversion; no invented license','master_hashes':{str(p.relative_to(MASTER)):hashlib.sha256(p.read_bytes()).hexdigest()for p in MASTER.rglob('*')if p.is_file()}};write(AUD/'source-audit.json',report)
tex=np.full((1,1,4),255,np.uint8);uv=np.zeros((len(tri),3,2));meshes=[(tri,uv,tex,[.6,.65,.7,1],'OPAQUE')]
for name,basis in [('xy',[[1,0,0],[0,1,0],[0,0,1]]),('xz',[[1,0,0],[0,0,1],[0,-1,0]]),('yz',[[0,1,0],[0,0,1],[1,0,0]])]:render(meshes,(1200,650),np.array(basis)).save(AUD/('source-'+name+'.png'))
print(json.dumps({k:report[k]for k in ['asset_metadata','triangles','bounds','parts','textures']}))
