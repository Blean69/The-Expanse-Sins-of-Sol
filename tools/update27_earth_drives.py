"""Replace Hale's five plain print recesses with accepted detailed Truman bells."""
import argparse,copy,hashlib,shutil
import numpy as np
from common import read,write
from update27_earth_geometry import ROOT,BASE,OUT,BUILD,GAME,AUD,IDS
from update26_platform_common import load_parts,export,compile as compile_mesh
from update23_murphy_art import frames

def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def split(poly,n,d):
 inside=[];outside=[]
 for i,a in enumerate(poly):
  b=poly[(i+1)%len(poly)];da=a@n-d;db=b@n-d;(inside if da<=0 else outside).append(a)
  if(da<=0)!=(db<=0):q=a+(b-a)*da/(da-db);inside.append(q);outside.append(q)
 return inside,outside

def aperture(tri,c,radius,depth):
 planes=[(np.array([np.cos(a),np.sin(a),0]),radius+np.dot(c,[np.cos(a),np.sin(a),0]))for a in np.arange(48)*2*np.pi/48]+[(np.array([0,0,1]),c[2]+depth)];out=[];count=0
 for t in tri:
  if t[:,2].min()>c[2]+depth or (t[:,:2].min(0)>c[:2]+radius).any()or(t[:,:2].max(0)<c[:2]-radius).any():out.append(t);continue
  rem=list(t);pieces=[]
  for n,d in planes:
   if len(rem)<3:break
   rem,other=split(rem,n,d)
   if len(other)>=3:pieces.extend([[other[0],other[j],other[j+1]]for j in range(1,len(other)-1)])
  if len(rem)>=3:count+=1
  out.extend(pieces)
 out=np.array(out);q=np.cross(out[:,1]-out[:,0],out[:,2]-out[:,0]);return out[np.linalg.norm(q,axis=1)>1e-7],count

def prepare():
 kind='hale';a=read(AUD/(kind+'-integration.json'));name=a['hull_mesh'];D=OUT/'drive-revision';D.mkdir(exist_ok=True);frozen=D/'previous-hale.mesh'
 if not frozen.exists():shutil.copyfile(GAME/'meshes'/(name+'.mesh'),frozen);write(D/'previous-integration.json',a)
 previous=read(D/'previous-integration.json');parts=load_parts(frozen);details=[]
 source=BASE/'meshes/expanse24_storm_hull.mesh';dp=next(p for p in load_parts(source)if p['material'].endswith('_storm_drive'));used=np.unique(dp['i']);v=dp['v'][used];lo=v.min(0);hi=v.max(0);center=np.r_[(lo[:2]+hi[:2])/2,lo[2]];diam=22.;scale=diam/max(hi[:2]-lo[:2]);driveparts=[]
 for p in parts:
  p['material']=p['material'].removeprefix(name+'_')
  if p['material']!='machinery':continue
  tri=p['v'][p['i']]
  for i,e in enumerate(a['exhausts']):
   c=np.array(e['position'])+[0,0,.15];tri,n=aperture(tri,c,11.05,23.);q=copy.deepcopy(dp);q['v']=(q['v']-center)*scale+c;q['material']='epstein_drive';driveparts.append(q);details.append({'nozzle':i,'opening_center':c.tolist(),'diameter':diam,'depth':float((hi[2]-lo[2])*scale),'aperture_radius':11.05,'aperture_depth':23.,'old_faces_touched':n})
  p.update(frames(tri));p['material']='machinery'
 first=driveparts[0]
 for q in driveparts[1:]:
  off=len(first['v']);first['i']=np.concatenate([first['i'],q['i']+off])
  for k in ['v','n','t','uv']:first[k]=np.concatenate([first[k],q[k]])
 parts.append(first);export(name,parts,a['meshpoints'],D/name)
 before=previous['counts']['hull'];after=sum(len(p['i'])for p in parts);a['counts']['hull']=after;a['counts']['assembled']=previous['counts']['assembled']-before+after
 a['drive_revision']={'donor':str(source),'donor_sha256':sha(source),'donor_material':dp['material'],'upstream_donor':'Accepted Truman bell, inner throat and support rings; retained in Storm0.26 as a UV-preserving component','triangles_per_drive':len(dp['i']),'uniform_scale_from_storm_component':scale,'source_uvs_normals_tangents_preserved':True,'nozzles':details,'previous_hull_sha256':sha(frozen),'weapon_mounts_unchanged':a['rigs']==previous['rigs'],'exhaust_meshpoints_unchanged':a['exhausts']==previous['exhausts'],'munroe':'Detailed four-engine source hardware retained; radial surface depth varies across bell/throat, no flat cap substitution.'};write(D/'new-integration.json',a);print('PREPARED',a['counts'],flush=True)

def compile():
 D=OUT/'drive-revision';a=read(D/'new-integration.json');name=a['hull_mesh'];B=BUILD/'drive-revision';B.mkdir(exist_ok=True);check=compile_mesh(name,D/name,B,GAME,a['meshpoints']);a['compile_checks'][name]=check
 rel='mesh_materials/'+name+'_epstein_drive.mesh_material';source=BASE/'mesh_materials/expanse24_storm_hull_storm_drive.mesh_material';d=read(source);write(GAME/rel,d);a['files'][rel]=sha(GAME/rel);a['source_dependency_hashes'][str(source)]=sha(source)
 for k,v in d.items():
  if k.endswith('_texture'):
   rel='textures/'+v+'.dds'
   if not(GAME/rel).exists():shutil.copyfile(BASE/rel,GAME/rel)
   a['files'][rel]=sha(GAME/rel)
 a['files']['meshes/'+name+'.mesh']=sha(GAME/'meshes'/(name+'.mesh'));a['drive_revision']['compiled']=True;write(AUD/'hale-integration.json',a);write(AUD/'drive-revision.json',a['drive_revision']);print('COMPILED DRIVE REVISION',flush=True)
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('stage',choices=['prepare','compile']);globals()[p.parse_args().stage]()
