"""Independent compiled orientation, frame binding and actual muzzle checks."""
from pathlib import Path
import json,struct,hashlib,inspect,numpy as np
from PIL import Image
from common import read,write,read_mesh
from update14_pdc_arcs import Rays,pose
from scipy.spatial import cKDTree
import polish_ui
R=Path(__file__).resolve().parents[1];A=R/'audit/update15-truman';B=R/'build/update15-truman';D=R/'assets/derived/update15-truman';P='expanse15_truman';meta=read(A/'integration-spec.json');m=read(B/'repaired-json'/(P+'_hull.mesh_json'));v=np.array([x['p']for x in m['non_skinned_vertices']]);idx=np.array(m['vertex_indices']).reshape(-1,3);tri=v[idx];norm=np.cross(tri[:,1]-tri[:,0],tri[:,2]-tri[:,0]);norm/=np.maximum(np.linalg.norm(norm,axis=1)[:,None],1e-15);src=np.load(D/'normalized.npz');st=src['v'][src['i']];sn=src['n'][src['i']].mean(1);tree=cKDTree(st.mean(1));dist,ids=tree.query(tri.mean(1));matched=dist<1e-4;dot=np.einsum('ij,ij->i',norm,sn[ids]);assert not ((dot<-.001)&matched).any();sv=float(np.sum(st[:,0]*np.cross(st[:,1],st[:,2]))/6);assert sv>0
mesh=read_mesh(B/'game/meshes'/(P+'_hull.mesh'));points={p['name']:p for p in mesh['meshpoints']};frames=[]
for r in meta['rigs']:
 mount=r['mount'];got=points[mount['mesh_point']];basis=np.column_stack([np.cross(mount['up'],mount['forward']),mount['up'],mount['forward']]);assert np.allclose(basis,r['basis_columns'],atol=1e-7);actual=np.array(got['rotation']).reshape(3,3).T;assert np.allclose(actual,basis,atol=1e-6),(mount['weapon'],actual,basis);assert np.allclose(got['position'],mount['weapon_position'],atol=4e-5);frames.append({'weapon':mount['weapon'],'position_error':float(np.max(np.abs(np.array(got['position'])-mount['weapon_position']))),'basis_error':float(np.max(np.abs(actual-basis)))})
ray=Rays(st,B/'ray-check');rails=[]
for r in meta['rigs']:
 if r['kind']!='rail':continue
 for mu in r['turret_override']['muzzle_positions']:
  count=0
  for dy in [-3,0,3]:
   for dp in [-3,0,3]:
    y=np.linspace(-12,12,97);p=np.zeros_like(y);o,d=pose(r['mount'],{'barrel_position':[0,0,0],'muzzle_positions':[mu]},y,p,dy,dp);hits=ray(o,d);assert not(hits>0).any(),(r['index'],mu,dy,dp,hits[hits>0]);count+=len(y)
  rails.append({'weapon':r['mount']['weapon'],'muzzle':mu,'rays':count,'blocked':0})
ray.close()
code=inspect.getsource(polish_ui.render).replace('def render(meshes, size, basis, fill=.9):','def render(meshes, size, basis, fill=.9, cull=True):').replace('n = 0','front = np.zeros((size[1], size[0]), dtype=bool)\n    n = 0').replace('coords = xy[n]; zs = xyz[n, :, 2]; n += 1','coords = xy[n]; zs = xyz[n, :, 2]; n += 1\n            facing = normals[local] @ basis[2] > 1e-9\n            if cull and not facing: continue').replace('old[active] = z[active]','old[active] = z[active]\n            front[miny:maxy + 1, minx:maxx + 1][active] = facing').replace('return Image.fromarray(out)','return Image.fromarray(out), float(front[np.isfinite(depth)].mean())');ns={'np':np,'Image':Image,'project':polish_ui.project};exec(code,ns);render=ns['render'];tex=np.full((1,1,4),255,np.uint8);mm=[(tri,np.zeros((len(tri),3,2)),tex,[.4,.43,.45,1],'OPAQUE')];views=[]
for label,cam in [('starboard',[1,.1,.1]),('port',[-1,.1,.1]),('dorsal',[.1,1,.1]),('ventral',[.1,-1,.1]),('bow',[.1,.1,1]),('aft',[.1,.1,-1])]:
 cam=np.array(cam,float);cam/=np.linalg.norm(cam);right=np.cross([0,1,0],cam);right/=np.linalg.norm(right);up=np.cross(cam,right);basis=np.array([right,up,cam]);im,f=render(mm,(700,400),basis,cull=False);views.append({'view':label,'nearest_outward_fraction':f});im,_=render(mm,(1200,600),basis,cull=True);im.save(A/(label+'-culled.png'));assert f>.985,(label,f)
sourceaudit=read(A/'source-audit.json');master=R/'assets/original/update15-truman/master'
for path,expected in sourceaudit['master_hashes'].items():assert hashlib.sha256((master/path).read_bytes()).hexdigest()==expected
assert hashlib.sha256(Path('/home/haker/Downloads/truman_class.zip').read_bytes()).hexdigest()==sourceaudit['archive_sha256']
report={'status':'PASS OFFLINE','source_signed_volume':sv,'source_matched_triangles':int(matched.sum()),'source_opposed_faces':int(((dot<-.001)&matched).sum()),'compiled_mount_frames':frames,'rail_rays':rails,'exterior_views':views,'source_triangle_count':len(st),'assembled_triangles':meta['assembled_triangle_total'],'runtime':'NOT RUN','limits':'Source glTF double-sided intent is not represented by indiscriminate duplicatefaces. Retained authored normals independentlycorroborated bypositivevolume/exteriorcoverage. Surface samples are notwatertightnessproof. Ray evidence excludes movingothergun geometry; rotation andengineconventions requireworkstationobservation.'};write(A/'geometry-validation.json',report);meta['status']='PASS OFFLINE MESH, MATERIAL, MOUNTS, ORIENTATION AND SAMPLED FIRING RAYS';meta['game_file_hashes']={str(p.relative_to(B/'game')):hashlib.sha256(p.read_bytes()).hexdigest()for p in(B/'game').rglob('*')if p.is_file()};write(A/'integration-spec.json',meta);print(json.dumps(report,indent=2))
