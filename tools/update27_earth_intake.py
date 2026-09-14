"""Source-only visual inspection and provenance for the two Earth hulls."""
from pathlib import Path
import argparse,hashlib,zipfile
import numpy as np
from common import write
from polish_ui import render
ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'assets/derived/update27-earth';AUD=ROOT/'audit/update27-earth'
for p in[OUT,AUD]:p.mkdir(parents=True,exist_ok=True)
def source(kind):
 archive,member={'hale':('leonidas-class-the-expanse-model_files.zip','nathanhale.stl'),'munroe':('munroe.zip','monroe.stl')}[kind];path=Path('/home/haker/Downloads')/archive
 with zipfile.ZipFile(path)as z:raw=z.read(member)
 a=np.frombuffer(raw[84:],dtype=[('n','<f4',3),('v','<f4',(3,3)),('a','<u2')]);tt=a['v'].astype(float);q=np.cross(tt[:,1]-tt[:,0],tt[:,2]-tt[:,0]);good=np.linalg.norm(q,axis=1)>1e-8
 return tt[good],{'archive':str(path),'archive_sha256':hashlib.sha256(path.read_bytes()).hexdigest(),'member':member,'source_sha256':hashlib.sha256(raw).hexdigest(),'source_triangles':len(tt),'removed_degenerates':int((~good).sum()),'bounds_min':tt.min((0,1)).tolist(),'bounds_max':tt.max((0,1)).tolist(),'stl_has_uv':False,'stl_has_materials':False}
def main(kind):
 tt,meta=source(kind);lo=tt.min((0,1));hi=tt.max((0,1));tt-=(lo+hi)/2;tex=np.full((4,4,4),[135,155,172,255],dtype=np.uint8);uv=np.zeros(tt.shape[:2]+(2,));parts=[(tt,uv,tex,[1,1,1,1],'OPAQUE')];B=np.array([[.8,0,.6],[-.3,.866,.4],[.52,.5,-.693]])
 for label,m in [('oblique',B),('reverse',B@np.diag([-1,1,-1]))]:render(parts,(1200,900),m).save(AUD/(kind+'-source-'+label+'.png'))
 write(AUD/(kind+'-intake.json'),meta);print(kind,meta,flush=True)
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('kind',choices=['hale','munroe']);main(p.parse_args().kind)
