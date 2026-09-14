"""Private Gathering Storm derivative. Preserves the supplied full-resolution STL.
Numeric materials and geometry are authored for this mod, not a reconstructed UV skin.
"""
from pathlib import Path
import zipfile, hashlib, copy, sys
import numpy as np
from scipy.spatial.transform import Rotation
MAIN=Path('/run/media/haker/NVME 2/expanse-mod')
sys.path.insert(0,str(MAIN/'tools'))
from common import read,write
import update12_scirocco_common as helper
ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'assets/derived/update24-storm';BUILD=ROOT/'build/update24-storm';AUD=ROOT/'audit/update24-storm'
for d in [OUT,BUILD,AUD]:d.mkdir(parents=True,exist_ok=True)
helper.OUT=OUT
ZIP=Path('/home/haker/Downloads/lns-gathering-storm-the-expanse-model_files.zip');ENTRY='gathering-storm-3d-print-whole.stl';raw=zipfile.ZipFile(ZIP).read(ENTRY)
src=np.frombuffer(raw,dtype=np.dtype([('n','<f4',3),('v','<f4',(3,3)),('a','<u2')]),offset=84)['v'].astype(float)
center=(src.min((0,1))+src.max((0,1)))/2
# Source -X is the bow/keel rail. Positive game Z is forward.
rot=np.array([[0,1,0],[0,0,-1],[-1,0,0]],float);scale=375/np.ptp(src[:,:,0]);tri=(src-center)@rot.T*scale
cross=np.cross(tri[:,1]-tri[:,0],tri[:,2]-tri[:,0]);good=np.linalg.norm(cross,axis=1)>1e-9;tri=tri[good];cross=cross[good];n=cross/np.linalg.norm(cross,axis=1,keepdims=True);mid=tri.mean(1)
# Stable, broad facet colors: no noisy per-triangle random paint. Dark keel and
# drive mechanisms, pearl upper facets, ice-blue sides and blush lower facets.
labels=np.where(abs(n[:,1])>.72,'pearl',np.where(n[:,0]*n[:,1]>.1,'blush','ice'))
labels[(mid[:,2]>170)&(np.abs(mid[:,0])<4)]='dark'
labels[(mid[:,2]<-190)&(np.abs(mid[:,0])<9)&(np.abs(mid[:,1])<12)]='dark'
colors={'pearl':[.67,.74,.84,1],'ice':[.25,.46,.66,1],'blush':[.51,.35,.50,1],'dark':[.065,.08,.12,1]}
parts=[helper.frames(tri[labels==k], 'storm_'+k)for k in colors if np.any(labels==k)]
# Find the outermost actual hull intersection at each mount, then place the
# native PDC pivot one unit beyond that surface. No floating guessed cylinders.
def ray(origin,direction):
 e1=tri[:,1]-tri[:,0];e2=tri[:,2]-tri[:,0];h=np.cross(np.broadcast_to(direction,e2.shape),e2);a=(e1*h).sum(1);valid=abs(a)>1e-10;f=np.divide(1,a,out=np.zeros_like(a),where=valid);s=origin-tri[:,0];u=f*(s*h).sum(1);q=np.cross(s,e1);v=f*(q*direction).sum(1);t=f*(e2*q).sum(1);ok=valid&(u>=0)&(v>=0)&(u+v<=1)&(t>0);assert ok.any();return origin+direction*t[ok].min()
points=[{'name':'center','translation':[0,0,0]},{'name':'above','translation':[0,45,0]},{'name':'aura','translation':[0,-45,0]}];rigs=[]
base=MAIN/'build/experiments/expanse_update20';turret=read('/run/media/haker/NVME 2/expanse-workers/tachi-one-pdc/audit/update11-b/mount-metadata.json')['rigs'][0]['turret_override'];turret=copy.deepcopy(turret);turret.update(biaxial_base_mesh='expanse24_storm_pdc_base',biaxial_barrel_mesh='expanse24_storm_pdc_barrel')
for i,(axis,sign,z)in enumerate([(0,-1,25),(0,1,25),(0,-1,-125),(0,1,-125),(1,1,-55),(1,-1,-55)]):
 up=np.eye(3)[axis]*sign;origin=np.array([0.,0.,z])+up*200;p=ray(origin,-up)+up*1.0;forward=np.array([0,0,1]);B=np.column_stack([np.cross(up,forward),up,forward]);name=f'child.expanse24_storm_pdc_{i}';points.append({'name':name,'translation':p.tolist(),'rotation':Rotation.from_matrix(B).as_quat().tolist()});rigs.append({'kind':'pdc','mesh_point':name,'position':p.tolist(),'up':up.tolist(),'forward':forward.tolist(),'yaw_arc':{'min_angle':-180.,'max_angle':180.},'pitch_arc':{'min_angle':-85.,'max_angle':-25.},'turret_override':copy.deepcopy(turret),'surface_clearance':1.0})
# Exact forwardmost rail-tip point and aftmost centreline drive geometry.
rail=tri.reshape(-1,3)[np.argmax(tri[:,:,2])].copy();points.append({'name':'weapon.keel_rail.0','translation':rail.tolist()})
for i,sign in enumerate([-1,1]):
 p=ray(np.array([sign*7.,0.,300.]),np.array([0.,0.,-1.]));p[2]+=.4;points.append({'name':f'weapon.torpedo.{i}','translation':p.tolist()})
drive=ray(np.array([0.,0.,-300.]),np.array([0.,0.,1.]));drive[2]-=.4;points.append({'name':'exhaust.0','translation':drive.tolist(),'rotation':[0.,1.,0.,0.]})
for suffix,compiler in [('_hull',True),('_editable',False)]:
 name='expanse24_storm'+suffix;helper.savegltf(name,parts,points,compiler);p=OUT/(name+'.gltf');g=read(p)
 for m in g['materials']:m['pbrMetallicRoughness']={'baseColorFactor':colors[m['name'].removeprefix('storm_')],'metallicFactor':.52,'roughnessFactor':.34}
 g['asset']['generator']='Gathering Storm full STL derivative; authored pearlescent facet materials; no simplification';write(p,g)
np.savez_compressed(OUT/'reference-frames.npz',**{f'{i}_{k}':p[k] for i,p in enumerate(parts)for k in ['v','n','t','uv']})
lo=tri.min((0,1));hi=tri.max((0,1));report={'status':'GEOMETRY AUTHORED; COMPILATION PENDING','source':{'zip':str(ZIP),'zip_sha256':hashlib.sha256(ZIP.read_bytes()).hexdigest(),'entry':ENTRY,'entry_sha256':hashlib.sha256(raw).hexdigest(),'author':'dredeth','license':'CC BY-NC 4.0 (archive intake)','original_triangles':len(src),'removed_degenerates':int((~good).sum()),'remaining_triangles':len(tri),'simplification':False},'hull_mesh':'expanse24_storm_hull','chosen_length_metres':375/(104.987/46),'game_units_per_metre':104.987/46,'source_units_are_not_metres':True,'source_to_game_rotation':rot.tolist(),'source_center':center.tolist(),'scale':float(scale),'colors':colors,'meshpoints':points,'rigs':rigs,'fixed_rail':{'mesh_point':'weapon.keel_rail.0','weapon_position':rail.tolist(),'forward':[0,0,1],'yaw_arc':{'min_angle':-2.,'max_angle':2.},'pitch_arc':{'min_angle':-2.,'max_angle':2.},'turret':False},'spatial':{'box':{'center':((hi+lo)/2).tolist(),'extents':((hi-lo)/2).tolist()},'radius':float(np.linalg.norm(tri.reshape(-1,3),axis=1).max())},'runtime':'NOT RUN','adaptations':['164.306 m design length and six PDC mounts are mod choices, not a verified canonical specification.','Six real rotating donor PDC rigs; fixed source keel rail geometry is not a turret.','Two unmodeled torpedo apertures use actual forward hull surface origins; no invented launcher geometry claim.','Pearl/blue/blush static facet materials approximate crystalline appearance; not an angle-dependent iridescent shader.','Printable source seams remain; no fabricated topology fill.']}
write(AUD/'integration-spec.json',report);print(len(tri),'triangles; six measured native PDC rigs')
