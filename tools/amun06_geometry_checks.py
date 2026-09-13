"""Independent source preservation, assignment and aiming-reference invariants."""
from amun06_geometry_common import *
from scipy.spatial.transform import Rotation
import hashlib
m=read(AUDIT/'mount-metadata.json');assert [r['source_pad_root'] for r in m['rigs']]==[892,910,946];assert m['selection']['omitted_pdc_root']==928;assert len(m['rigs'])==3;assign=m['source_ownership'];shipnodes=[q['node'] for q in assign if q['part']!='amun_boarding_pod'];assert len(shipnodes)==len(set(shipnodes));excluded=set(descendants(928))
for root in m['selection']['excluded_detached_pods']+m['selection']['excluded_detached_torpedoes']:excluded.update(descendants(root))
assert not(set(shipnodes)&excluded);assert m['ship_triangle_total']==27526 and m['pod_triangle_total']==4481;rigchecks=[]
for r in m['rigs']:
 B=np.array(r['basis_columns']);origin=np.array(r['yaw_pivot_hull']);offset=np.array(r['turret_override']['barrel_position']);tip=np.array(r['turret_override']['muzzle_positions'][0]);pitch=np.array(r['pitch_pivot_hull']);error=float(abs(origin+B@(offset+tip)-r['muzzle_hull']).max());assert error<1e-7;assert np.allclose(origin+B@offset,pitch,rtol=0,atol=1e-7);assert np.allclose(B.T@B,np.eye(3),rtol=0,atol=1e-7);assert np.linalg.det(B)>.999999;source_up=matrix(r['source_yaw_node'])[:3,2]/np.linalg.norm(matrix(r['source_yaw_node'])[:3,2]);expected=np.array(m['normalization']['source_to_game_rotation'])@source_up;assert np.allclose(expected,r['mount']['up'],atol=1e-10);rigchecks.append({'index':r['index'],'rest_muzzle_error':error,'source_matrix_tolerance':1e-7,'basis_orthogonality_max_error':float(abs(B.T@B-np.eye(3)).max()),'actual_source_yaw_axis_preserved':True,'source_pitch_origin_preserved':True,'runtime':'NOT RUN'})
# Source rail exit ray: triangle geometry only, independent of game targeting.
tri=np.concatenate([q['v'][q['i']] for ni in descendants(3) for q in arrays(ni)]);origin=np.array(m['equipment']['railgun']['source_position']);ray=np.array([0.,1.,0.]);e1=tri[:,1]-tri[:,0];e2=tri[:,2]-tri[:,0];h=np.cross(np.tile(ray,(len(tri),1)),e2);det=np.sum(e1*h,1);valid=abs(det)>1e-10;inverse=np.divide(1,det,out=np.zeros_like(det),where=valid);s=origin-tri[:,0];u=inverse*np.sum(s*h,1);q=np.cross(s,e1);v=inverse*np.sum(ray*q,1);t=inverse*np.sum(e2*q,1);hits=np.where(valid&(u>=0)&(v>=0)&(u+v<=1)&(t>1e-6))[0];assert len(hits)==0
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
for p,h in m['source_hashes'].items():assert sha(p)==h,p
prior=[]
for folder in ['geometry04-b','torpedo05-b']:
 record=read(ROOT/'audit'/folder/'final-provenance.json')
 for p,h in record['files'].items():assert sha(p)==h,p
 prior.append({'checkpoint':folder,'frozen_files_preserved':len(record['files'])})
write(AUDIT/'independent-checks.json',{'status':'PASS OFFLINE ONLY','source_master_files_preserved':len(m['source_hashes']),'prior_frozen_checkpoints':prior,'ship_triangle_count':27526,'pod_triangle_count':4481,'unique_ship_source_mesh_nodes':len(shipnodes),'detached_equipment_and_fourth_gun_excluded':True,'rig_checks':rigchecks,'source_rail_forward_ray_hits':len(hits),'launch_door_aperture_clearance':'NOT TESTED IN GAME; measured source static door surfaces, not proved open launch throats','runtime':'NOT RUN'});print('PASS:3 source joints, unique mesh ownership, rail exit ray, read-only input/frozen checkpoint hashes')
