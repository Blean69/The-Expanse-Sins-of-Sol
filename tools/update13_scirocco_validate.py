"""Bounded checks for the Scirocco visual overlay. This never launches Sins."""
from pathlib import Path
import json,hashlib,numpy as np,ast
from scipy.spatial.transform import Rotation
from common import read,write,read_mesh,Gltf
R=Path(__file__).resolve().parents[1];D=Path('/run/media/haker/NVME 2/expanse-workers/tachi-one-pdc');A=R/'audit/update13-a';O=R/'assets/derived/update13-a';B=R/'build/update13-a';P='expanse12_scirocco';meta=read(A/'integration-spec.json');old=read(D/'audit/update12-b/integration-spec.json')
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
# Load only the pure ray function from this worker's geometry script.
g=Gltf(D/'assets/derived/update12-b/expanse12_scirocco_hull.gltf');h=[]
for p in g.g['meshes'][0]['primitives']:
 v=g.accessor(p['attributes']['POSITION']);v[:,2]*=-1;h.append(v[g.accessor(p['indices']).reshape(-1,3)])
hull=np.concatenate(h);cache={};tree=ast.parse((R/'tools/update13_scirocco_build.py').read_text());fn=next(x for x in tree.body if isinstance(x,ast.FunctionDef)and x.name=='ray');exec(compile(ast.Module(body=[fn],type_ignores=[]),'ray','exec'))
frames=read(O/'retained-source-frames.json');barrel=np.concatenate([np.array(p['v'])for p in frames['pdc_barrel'].values()]);samples=barrel[np.linspace(0,len(barrel)-1,48).astype(int)];poses=[]
for r in meta['rigs']:
 if r['kind']!='pdc':continue
 basis=np.array(r['basis_columns']);up=basis[:,1];origin=np.array(r['yaw_pivot_hull']);off=np.array(r['turret_override']['barrel_position']);muzzle=np.array(r['turret_override']['muzzle_positions'][0]);assert np.allclose(origin+basis@(off+muzzle),r['muzzle_hull']);assert np.linalg.det(basis)>.99999
 for yaw in (-180,-90,0,90,180):
  for pitch in (-85,-45,0,5):
   yy=Rotation.from_rotvec([0,np.deg2rad(yaw),0]).as_matrix();xx=Rotation.from_rotvec([np.deg2rad(pitch),0,0]).as_matrix();local=(samples@xx.T+off)@yy.T;q=local@basis.T+origin;hits=[]
   for pos in q:
    surface=ray(pos+up*200,-up);clearance=float((pos-surface)@up)
    if clearance<-.05:hits.append(clearance)
   poses.append({'mount':r['index'],'yaw':yaw,'pitch':pitch,'samples':len(q),'below_outer_hull_samples':len(hits),'worst':min(hits)if hits else None})
write(A/'pdc-clearance.json',{'status':'PASS BOUNDED OFFLINE'if not any(x['below_outer_hull_samples']for x in poses)else 'REVIEW COLLISIONS','poses':poses,'runtime':'NOT RUN','caveat':'48barrel vertices at20poses per gun against retained hull; not a continuous collision proof'})
assert not any(x['below_outer_hull_samples']for x in poses),[(x['mount'],x['yaw'],x['pitch'],x['below_outer_hull_samples'],x['worst'])for x in poses if x['below_outer_hull_samples']]
mesh_report=read(A/'mesh-validation.json');actual={}
for row in mesh_report['meshes']:
 path=B/'game/meshes'/(row['mesh']+'.mesh');assert sha(path)==row['sha256'];m=read_mesh(path);actual[row['mesh']]=m
 assert row['opposed_winding_triangles']==0 and row['tangent_fallbacks']==0 and row['official_trailer_preserved']
 for material in row['materials']:
  data=read(B/'game/mesh_materials'/(material+'.mesh_material'))
  for key,val in data.items():
   if key.endswith('_texture'):assert (B/'game/textures'/(val+'.dds')).read_bytes()[:4]==b'DDS '
points={p['name']:p for p in actual[P+'_hull']['meshpoints']}
for r in meta['rigs']:
 p=points[r['mount']['mesh_point']];assert np.allclose(p['position'],r['yaw_pivot_hull'],atol=3e-5);assert np.allclose(np.array(p['rotation']).reshape(3,3).T,r['basis_columns'],atol=2e-6)
assert len([r for r in meta['rigs']if r['kind']=='pdc'])==12
assert meta['rigs'][-1]==old['rigs'][-1] and meta['equipment']==old['equipment']
for k in ('light_torpedo_ports','heavy_torpedo_ports'):
 for i,r in enumerate(meta['equipment'][k]):assert np.allclose(points['weapon.'+k.replace('_ports','')+'.'+str(i)]['position'],r['position'],atol=3e-5)
assert sha(B/'game/meshes'/f'{P}_rail_0.mesh')==sha(D/'build/update12-b/game/meshes'/f'{P}_rail_0.mesh')
ui=read(A/'ui-integration-spec.json');uir=read(A/'ui-validation.json');uiroot=Path(ui['game_directory']).resolve()
for r in uir['png_checks']:assert sha(R/r['file'])==r['sha256']
for path,digest in uir['source_dependencies'].items():assert sha(R/path)==digest
files={str(p.relative_to(B/'game')):sha(p)for p in sorted((B/'game').rglob('*'))if p.is_file()};uifiles={str(p.relative_to(uiroot)):sha(p)for p in sorted(uiroot.rglob('*'))if p.is_file()}
meta.update(status='PASS OFFLINE ASSET HANDOFF',game_file_hashes=files,ui_file_hashes=uifiles,ui_directory=str(uiroot),ui_integration_spec=str(A/'ui-integration-spec.json'),asset_bundle_sha256=hashlib.sha256(json.dumps({'game':files,'ui':uifiles},sort_keys=True).encode()).hexdigest(),runtime='NOT RUN')
write(A/'integration-spec.json',meta);write(A/'final-validation.json',{'status':meta['status'],'meshes':len(actual),'proper_mount_frames':13,'pdc_count':12,'barrel_clearance_poses':len(poses),'triangle_total':meta['assembled_triangle_total'],'rail_binary_unchanged':True,'equipment_unchanged':True,'gameplay':'No unit/weapon files in asset overlay; only mounts/turret offsets need integrator patch','asset_bundle_sha256':meta['asset_bundle_sha256'],'runtime':'NOT RUN'})
print(meta['status'],meta['asset_bundle_sha256'])
