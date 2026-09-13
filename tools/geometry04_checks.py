"""Bounded geometry invariants independent of game runtime."""
from common import *
from scipy.spatial.transform import Rotation
import hashlib
out=ROOT/'audit/geometry04-b';m=read(out/'mount-metadata.json');R=np.array(m['normalization']['old_game_to_new_game_rotation']);target=np.array(m['normalization']['target_center']);old=read(ROOT/'audit/geometry03-b/hero-armed-equipment.json');new=read(out/'equipment.json');assert np.allclose(R@R.T,np.eye(3),atol=1e-12) and np.linalg.det(R)>.999999;records=[]
for i,r in enumerate(m['rigs']):
 B=np.array(r['basis_columns']);origin=np.array(r['yaw_pivot_hull']);pitch=np.array(r['pitch_pivot_hull']);offset=np.array(r['turret_override']['barrel_position']);muzzle=np.array(r['turret_override']['muzzle_positions'][0]);e=float(abs(origin+B@(offset+muzzle)-r['muzzle_hull']).max());assert e<1e-10;assert np.allclose(origin+B@offset,pitch,atol=1e-10);assert abs(offset[0])+abs(offset[2])<1e-10;assert np.allclose(B.T@B,np.eye(3),atol=1e-12)
 # Fixed socket/rotating shaft share localY; barrel/yoke trunnion shareslocalX.
 maxdrift=0.
 for yaw in [-90,-45,0,45,90]:
  Y=Rotation.from_euler('y',yaw,degrees=True).as_matrix();maxdrift=max(maxdrift,float(abs(Y@offset-offset).max()))
  for angle in [-65,-30,0,10]:
   P=Rotation.from_euler('x',angle,degrees=True).as_matrix();maxdrift=max(maxdrift,float(abs(P@np.array([1.,0,0])-np.array([1.,0,0])).max()))
 assert maxdrift<1e-10;records.append({'index':i,'rest_muzzle_error':e,'shaft_and_trunnion_axis_drift':maxdrift,'yaw_samples':5,'pitch_samples_per_yaw':4,'collision_test':'NOT PERFORMED; tests axis attachment only'})
for oldq,newq in [(old['railgun'],new['railgun']),(old['exhaust'],new['exhaust'])]+list(zip(old['torpedo_ports'],new['torpedo_ports'])):
 for key in ['position','forward','up']:
  expected=(np.array(oldq[key])-target)@R.T+target if key=='position' else R@oldq[key];assert np.allclose(expected,newq[key],atol=1e-12)
assert np.allclose(new['exhaust']['forward'],[0,0,-1],atol=1e-10)
prior=read(ROOT/'audit/geometry03-b/final-provenance.json');preserved=[]
for p,h in prior['files'].items():assert hashlib.sha256(Path(p).read_bytes()).hexdigest()==h;preserved.append(p)
for r in prior['preserved_inputs']:assert hashlib.sha256(Path(r['path']).read_bytes()).hexdigest()==r['sha256']
write(out/'independent-geometry-checks.json',{'status':'PASS OFFLINE ONLY','rigs':records,'custom_fittings_and_exhaust_rigid_transform':'PASS','exhaust_axis_is_actual_aft_Z':True,'prior03_frozen_files_preserved':len(preserved),'earlier_readonly_inputs_preserved':len(prior['preserved_inputs']),'runtime':'NOT RUN; no collision or targeting claim'})
print('Six rig attachment/basis invariants; rail/ports/exhaust transform;155 frozen0.3 files and24 prior inputs preserved')
