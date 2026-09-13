"""Freeze source-only audit metadata for the two verified hull overlays."""
from pathlib import Path
import sys,json,hashlib,numpy as np
sys.path.insert(0,'/run/media/haker/NVME 2/expanse-mod/tools')
from common import read_mesh,Gltf
ROOT=Path(__file__).resolve().parents[1];BASE=Path('/run/media/haker/NVME 2/expanse-mod/build/experiments/expanse_update13');AUD=ROOT/'audit/update14-hulls'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def write(p,d):p.write_text(json.dumps(d,indent=2)+'\n')
records=[]
for variant in ['raptor','pella']:
 prefix='expanse12_'+variant;aud=AUD/variant;meta=json.loads((aud/'integration-spec.json').read_text());mesh=ROOT/'build/update14-hulls'/variant/'game/meshes'/(prefix+'_hull.mesh');got=read_mesh(mesh);old=read_mesh(BASE/'meshes'/mesh.name);assert got['meshpoints']==old['meshpoints'];assert got['materials']==old['materials'];validation=json.loads((aud/'mesh-validation.json').read_text());assert validation['status']=='PASS OFFLINE';assert sha(mesh)==validation['meshes'][0]['sha256'];assert got['triangles']==meta['counts']['hull']
 g=Gltf(ROOT/'assets/derived/update14-hulls'/variant/(prefix+'_editable.gltf'));v=np.concatenate([g.accessor(p['attributes']['POSITION'])for p in g.g['meshes'][0]['primitives']]);box=meta['ship_spatial']['box'];center=np.array(box['center']);extents=np.array(box['extents']);assert (abs(v-center)<=extents+1e-5).all();assert np.linalg.norm(v-center,axis=1).max()<=meta['ship_spatial']['radius']+1e-5
 opt=json.loads((aud/'optimization.json').read_text());original=Path('/home/haker/Downloads/xxx_-_raptor_whole.stl');opt['original_sha256']=sha(original);opt['source_welded_sha256']=sha(Path('/run/media/haker/NVME 2/expanse-workers/weapon-behavior/assets/derived/update12-a/source-welded.npz'));write(aud/'optimization.json',opt)
 exterior=json.loads((aud/'exterior-check.json').read_text());hits=sum(r['first_surface_hits']for r in exterior['six_sided_exterior_grid']);backfaces=sum(r['inward_facing_first_surfaces']for r in exterior['six_sided_exterior_grid']);record=dict(variant=variant,mesh=str(mesh),sha256=sha(mesh),old_hull_triangles=old['triangles'],hull_triangles=got['triangles'],assembled_triangles=meta['assembled_triangle_total'],meshpoints_and_rotations_exact=True,material_names_exact=True,assembled_neutral_pose_bounds='PASS',outward_surface_sample_hits=hits-backfaces,backface_surface_sample_hits=backfaces,exterior_test_limit='Three narrow grazing/centerline exposures remain. Not a watertightness claim.',runtime='NOT RUN');records.append(record);meta['files']={'meshes/'+mesh.name:sha(mesh)};meta['status']='PASS OFFLINE MESH, MATERIAL-IDENTITY, POINTS, AND BOUNDS; THREE RESIDUAL EXTERIOR SAMPLE EXPOSURES';meta['runtime']='NOT RUN';write(aud/'integration-spec.json',meta)
write(AUD/'final-validation.json',dict(status='PASS scoped offline checks; sampled surface limitation documented',records=records,owner='hulls14',runtime='NOT RUN'));print(json.dumps(records,indent=2))
