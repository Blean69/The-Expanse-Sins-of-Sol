from pathlib import Path
import json,hashlib,numpy as np
from scipy.spatial.transform import Rotation
import sys,argparse
sys.path.insert(0,'/run/media/haker/NVME 2/expanse-mod/tools')
ap=argparse.ArgumentParser();ap.add_argument('--variant',choices=['raptor','pella'],default='raptor');args=ap.parse_args();VARIANT=args.variant;PREFIX='expanse12_'+VARIANT
from common import Gltf,read_mesh
from polish_ui import write,render,project
from PIL import ImageDraw
ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'assets/derived/update12-a'/VARIANT;AUD=ROOT/'audit/update12-a'/VARIANT;BUILD=ROOT/'build/update12-a'/VARIANT;m=json.loads((AUD/'integration-spec.json').read_text());j=json.loads((BUILD/'repaired-json'/(PREFIX+'_hull.mesh_json')).read_text());vv=np.array([x['p']for x in j['non_skinned_vertices']]);tri=vv[np.array(j['vertex_indices']).reshape(-1,3)];e1=tri[:,1]-tri[:,0];e2=tri[:,2]-tri[:,0]
def hits(origin,direction):
 origin=np.array(origin,float);direction=np.array(direction,float);direction/=np.linalg.norm(direction);p=np.cross(direction,e2);det=np.sum(e1*p,axis=1);inv=np.divide(1,det,out=np.zeros_like(det),where=abs(det)>1e-10);s=origin-tri[:,0];u=np.sum(s*p,axis=1)*inv;q=np.cross(s,e1);v=q@direction*inv;t=np.sum(e2*q,axis=1)*inv;ok=(abs(det)>1e-10)&(u>=-1e-7)&(v>=-1e-7)&(u+v<=1+1e-7)&(t>1e-4);return np.sort(t[ok])
checks=[]
for i,p in enumerate(m['equipment']['torpedo_ports']):
 hs=hits(p['position'],p['forward']);assert not len(hs);checks.append({'port':i,'ray':'PASS forward unobstructed from measured collar mouth','position':p['position']})
mesh=read_mesh(BUILD/'game/meshes'/(PREFIX+'_hull.mesh'));frames=[];clearance=[]
for r in m['rigs']:
 B=np.array(r['basis_columns']);assert np.allclose(B.T@B,np.eye(3),atol=1e-8)and abs(np.linalg.det(B)-1)<1e-8;p=next(p for p in mesh['meshpoints']if p['name']==r['mount']['mesh_point']);assert np.allclose(np.array(p['rotation']).reshape(3,3),B.T,atol=2e-5);frames.append({'mount':r['index'],'basis':'PASS exact game row-vector convention','support':'Measured sourcehousingcontact;0.5unit embedding; source stowedgun+doors removed onlyderivative'})
 offset=np.array(r['turret_override']['barrel_position']);muzzle=np.array(r['turret_override']['muzzle_positions'][0]);pivot=np.array(r['yaw_pivot_hull'])
 for yaw in range(-180,180,45):
  Y=Rotation.from_euler('y',yaw,degrees=True).as_matrix()
  for pitch in [-85,-45,0,5]:
   P=Rotation.from_euler('x',pitch,degrees=True).as_matrix();start=pivot+B@Y@offset;vec=B@Y@P@muzzle;hs=hits(start,vec);obstruction=bool(len(hs)and hs[0]<np.linalg.norm(vec));clearance.append({'mount':r['index'],'yaw':yaw,'pitch':pitch,'barrel_center_ray_clear':not obstruction,'first_hull_hit_distance':float(hs[0])if len(hs)else None})
for i,p in enumerate(m['equipment']['exhausts']):
 hs=hits(p['position'],p['forward']);assert not len(hs),('blocked exhaust',i);checks.append({'exhaust':i,'ray':'PASS aft unobstructed from actual nozzle outlet'})
p=m['equipment']['boarding'];assert not len(hits(p['position'],p['forward']));checks.append({'boarding':'PASS outward ray from measured prototype pod origin'})
assert len(m['rigs'])==9 and len(m['equipment']['torpedo_ports'])==9 and len(m['equipment']['exhausts'])==4
assert all(p['position'][2]>80 and p['inner_diameter']>=2.936114 for p in m['equipment']['torpedo_ports'])
# Diagram actual derivative side/top projection, labelled known pivots and apertures.
a=Gltf(OUT/(PREFIX+'_editable.gltf'));ts=[]
for i,node in enumerate(a.g['nodes']):
 if 'mesh'in node:
  for p in a.g['meshes'][node['mesh']]['primitives']:ts.append(a.positions(i,p)[a.accessor(p['indices']).reshape(-1,3)])
alltri=np.concatenate(ts);basis=np.array([[0,0,1],[1,0,0],[0,1,0]]);size=(1400,700);tex=np.full((1,1,4),255,np.uint8);im=render([(alltri,np.zeros((len(alltri),3,2)),tex,[.35,.4,.45,1],'OPAQUE')],size,basis);draw=ImageDraw.Draw(im)
xyz=alltri@basis.T;lo=xyz[:,:,:2].min((0,1));hi=xyz[:,:,:2].max((0,1));zoom=min(size[0]*.9/(hi[0]-lo[0]),size[1]*.9/(hi[1]-lo[1]))
for label,pos in [(f'PDC {r["index"]}',r['yaw_pivot_hull'])for r in m['rigs']]+[(f'Tube {i}',p['position'])for i,p in enumerate(m['equipment']['torpedo_ports'])]+[(f'Engine {i}',e['position'])for i,e in enumerate(m['equipment']['exhausts'])]:
 q=(np.array(pos)@basis.T)[:2];q=(q-(lo+hi)/2)*zoom;q[1]*=-1;q+=np.array(size)/2;x,y=q;draw.ellipse((x-5,y-5,x+5,y+5),fill=(255,180,25,255));draw.text((x+8,y+8),label,fill='white')
im.save(AUD/'mount-diagram.png')
source=json.loads((ROOT/'audit/update12-a/source-audit.json').read_text());assert hashlib.sha256(Path(source['source']).read_bytes()).hexdigest()==source['sha256'];assert hashlib.sha256((ROOT/'assets/original/update12-raptor/xxx_-_raptor_whole.stl').read_bytes()).hexdigest()==source['sha256']
optimization=json.loads((AUD/'optimization.json').read_text());R=np.array(optimization['source_to_game_rotation']);assert np.allclose(R.T@R,np.eye(3))and abs(np.linalg.det(R)-1)<1e-9;m['normalization']={k:optimization[k]for k in ['source_center','source_to_game_rotation','uniform_scale','provisional_length']};m['normalization']['proper_rotation_determinant']=float(np.linalg.det(R))
report={'status':'PASS OFFLINE GEOMETRY/FRAMES/REFERENCES; runtime NOT RUN','launch_rays':checks,'mount_frames':frames,'sampled_barrel_center_rays':clearance,'sampled_obstructions':sum(not x['barrel_center_ray_clear']for x in clearance),'limits':'Centerline samples do not prove full swept-mesh clearance, target coverage or game aiming. No runtime claim.','source_preserved':True};write(AUD/'mount-validation.json',report);m['identity']=PREFIX;m['palette']='Procedural MCRN gray/orange'if VARIANT=='raptor'else'Procedural silver, high metallic low roughness';m['railgun_count']=0;m['source_has_animations']=False;m['source_PDC_state']='Nine stowed guns; derivative removes gun bodies/doors/latches/braces and retains bay housings';m['torpedo_layout']='Nine new collars on measured forward faces:4outer+2middle+3lower; source aperture/screen correspondence unverified';m['equipment']['boarding']['mesh_point']='weapon.boarding.0';m['status']='PASS OFFLINE ONLY';m['runtime']='NOT RUN';m['ui_integration_spec']=str(AUD/'ui-integration-spec.json');m['source_sha256']=source['sha256'];m['files']={str(p.relative_to(BUILD/'game')):hashlib.sha256(p.read_bytes()).hexdigest()for p in (BUILD/'game').rglob('*')if p.is_file()};write(AUD/'integration-spec.json',m);print(json.dumps({'status':'PASS OFFLINE','sampled_obstructions':report['sampled_obstructions'],'files':len(m['files'])}))
