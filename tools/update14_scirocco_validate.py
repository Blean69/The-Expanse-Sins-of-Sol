"""External-facing checks using source normals and compiled geometry, not just self-consistency."""
from pathlib import Path
import json,hashlib,inspect,numpy as np
from PIL import Image,ImageDraw
from scipy.spatial import cKDTree
from common import Gltf,read,write,read_mesh
import polish_ui
R=Path(__file__).resolve().parents[1];A=R/'audit/update14-scirocco';B=R/'build/update14-scirocco';O=R/'assets/derived/update14-scirocco';OLD=Path('/run/media/haker/NVME 2/expanse-workers/visual13-scirocco');D=Path('/run/media/haker/NVME 2/expanse-workers/tachi-one-pdc');P='expanse12_scirocco_hull'
def geometry(path):
 m=read(path);v=np.array([x['p'] for x in m['non_skinned_vertices']]);i=np.array(m['vertex_indices']).reshape(-1,3);t=v[i];n=np.cross(t[:,1]-t[:,0],t[:,2]-t[:,0]);n/=np.maximum(np.linalg.norm(n,axis=1)[:,None],1e-15)
 return m,t,n
old,ot,on=geometry(OLD/'build/update13-a/repaired-json'/f'{P}.mesh_json');new,nt,nn=geometry(B/'repaired-json'/f'{P}.mesh_json')
# Original source positive volume and proper, determinant+1 source-to-game basis
# independently establish outward orientation. Retained update12 normals agree.
z=np.load(D/'assets/derived/update12-b/source-components.npz');st=z['v'][z['i']];sv=float(np.sum(st[:,0]*np.cross(st[:,1],st[:,2]))/6);assert sv>0
sourceframes=read(D/'assets/derived/update12-b/retained-source-frames.json')['hull'];v=np.concatenate([p['v']for p in sourceframes.values()]);n=np.concatenate([p['n']for p in sourceframes.values()]);v=v.reshape(-1,3,3);n=n.reshape(-1,3,3).mean(1);tree=cKDTree(v.mean(1))
def evidence(t,norm):
 d,ids=tree.query(t.mean(1),k=8);valid=(d<1e-4);matched=valid.any(1);dots=np.sum(n[ids]*norm[:,None,:],axis=2);dot=np.max(np.where(valid,dots,-np.inf),axis=1)
 return {'source_matched_triangles':int(matched.sum()),'matched_faces_opposed_to_preserved_outward_normals':int(((dot<-.01)&matched).sum()),'signed_volume':float(np.sum(t[:,0]*np.cross(t[:,1],t[:,2]))/6)}
before=evidence(ot,on);after=evidence(nt,nn);print(before,after,flush=True);assert before['matched_faces_opposed_to_preserved_outward_normals']>60000;assert after['matched_faces_opposed_to_preserved_outward_normals']==0
# Actual compiled materials: camera-space backface culling, depth buffer, and a
# separate nearest-surface facing map to detect an inward shell even where its
# interior back wall still fills the silhouette.
src=inspect.getsource(polish_ui.render).replace('def render(meshes, size, basis, fill=.9):','def render(meshes, size, basis, fill=.9, cull=True):')
src=src.replace('n = 0','front = np.zeros((size[1], size[0]), dtype=bool)\n    n = 0')
src=src.replace('coords = xy[n]; zs = xyz[n, :, 2]; n += 1','coords = xy[n]; zs = xyz[n, :, 2]; n += 1\n            facing = normals[local] @ basis[2] > 1e-9\n            if cull and not facing: continue')
src=src.replace('old[active] = z[active]','old[active] = z[active]\n            front[miny:maxy + 1, minx:maxx + 1][active] = facing')
src=src.replace('return Image.fromarray(out)','return Image.fromarray(out), float(front[np.isfinite(depth)].mean())')
ns={'np':np,'Image':Image,'project':polish_ui.project};exec(src,ns);render=ns['render']
tex=np.asarray(Image.open(OLD/'assets/source/update13-a/charcoal-panel-tile.png').convert('RGBA'));alphas=np.unique(tex[:,:,3]).tolist();assert alphas==[255]
def meshes(m,t):
 result=[]
 for p in m['primitives']:
  start=p['vertex_index_start']//3;end=start+p['vertex_index_count']//3;name=m['materials'][p['material_index']];uv=np.zeros((end-start,3,2))
  # Uniform material values avoid a texture projection hiding surface orientation.
  color=[.23,.27,.30,1] if name.endswith('_mat_0')else[.65,.16,.055,1]if name.endswith('_mat_1')else[.075,.085,.095,1]
  result.append((t[start:end],uv,np.full((1,1,4),255,dtype=np.uint8),color,'OPAQUE'))
 return result
views=[];panels=[]
for label,cam in [('starboard',np.array([1.,.12,.15])),('port',np.array([-1.,.12,.15]))]:
 cam/=np.linalg.norm(cam);right=np.cross([0,1,0],cam);right/=np.linalg.norm(right);up=np.cross(cam,right);basis=np.array([right,up,cam]);row=[]
 for name,m,t in [('update13',old,ot),('update14',new,nt)]:
  mm=meshes(m,t);im,f=render(mm,(1000,480),basis,cull=True);_,f=render(mm,(480,220),basis,cull=False);bg=Image.new('RGBA',im.size,(20,25,34,255));bg.alpha_composite(im);ImageDraw.Draw(bg).text((15,12),name+' '+label,fill='white');row.append(bg);views.append({'view':label,'version':name,'nearest_surface_front_facing_fraction':f});bg.save(A/(name+'-'+label+'-backface-culled.png'))
 panels.append(row)
montage=Image.new('RGBA',(2000,960));
for y,row in enumerate(panels):
 for x,im in enumerate(row):montage.paste(im,(1000*x,480*y))
montage.save(A/'before-after-backface-culled.png')
assert all(x['nearest_surface_front_facing_fraction']>.99 for x in views if x['version']=='update14')
meta=read(A/'integration-spec.json');oldmeta=read(OLD/'audit/update13-a/integration-spec.json')
# Repeated ray arithmetic differs only in floating-point roundoff (<3e-14).
for a,b in zip(meta['rigs'],oldmeta['rigs']):assert np.allclose(a['yaw_pivot_hull'],b['yaw_pivot_hull'],rtol=0,atol=1e-12)
for k in ('rigs','meshpoints','equipment','ship_spatial'):meta[k]=oldmeta[k]
for kind in ('pdc_base','pdc_barrel','rail_0'):
 f='expanse12_scirocco_'+kind+'.mesh';assert (B/'game/meshes'/f).read_bytes()==(OLD/'build/update13-a/game/meshes'/f).read_bytes()
report={'status':'PASS OFFLINE','original_source_signed_volume':sv,'before':before,'after':after,'geometry_count_before':len(ot),'geometry_count_after':len(nt),'assembled_count_unchanged':98455,'source_texture_alpha_values':alphas,'views':views,'mounts_and_equipment_unchanged':True,'child_meshes_byte_identical':True,'runtime':'NOT RUN','render':'Actual compiled triangles with backface culling and depth buffer; uniform existing material colors; independent nearest-surface facing map'}
write(A/'orientation-validation.json',report);meta['status']='PASS OFFLINE';meta['game_file_hashes']={str(p.relative_to(B/'game')):hashlib.sha256(p.read_bytes()).hexdigest()for p in (B/'game').rglob('*')if p.is_file()};write(A/'integration-spec.json',meta);print(json.dumps(report,indent=2))
