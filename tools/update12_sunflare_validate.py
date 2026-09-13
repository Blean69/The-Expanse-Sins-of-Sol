from pathlib import Path
import json,hashlib,struct,numpy as np
from PIL import Image,ImageDraw
from common import Gltf,read_mesh
from polish_ui import write,render
ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'assets/derived/update12-c';AUD=ROOT/'audit/update12-c';BUILD=ROOT/'build/update12-c';MASTER=ROOT/'assets/source/update12-sunflare';m=json.loads((AUD/'integration-spec.json').read_text());j=json.loads((BUILD/'repaired-json/expanse12_sunflare_hull.mesh_json').read_text());v=np.array([x['p']for x in j['non_skinned_vertices']]);n=np.array([x['n']for x in j['non_skinned_vertices']]);t=np.array([x['t']for x in j['non_skinned_vertices']]);tri=v[np.array(j['vertex_indices']).reshape(-1,3)];assert np.isfinite(v).all()and np.isfinite(n).all()and np.isfinite(t).all();assert np.max(abs(np.linalg.norm(n,axis=1)-1))<2e-5;assert np.max(abs(np.linalg.norm(t[:,:3],axis=1)-1))<2e-5;assert np.max(abs(np.sum(n*t[:,:3],axis=1)))<2e-5
mesh=read_mesh(BUILD/'game/meshes/expanse12_sunflare_hull.mesh');point=next(p for p in mesh['meshpoints']if p['name']=='exhaust.0');e=m['equipment']['exhaust'];assert np.allclose(point['position'],e['position'],atol=2e-5);expected=np.array([[-1,0,0],[0,1,0],[0,0,-1]]);assert np.allclose(np.array(point['rotation']).reshape(3,3),expected,atol=2e-5)
origin=np.array(e['position']);direction=np.array(e['forward']);e1=tri[:,1]-tri[:,0];e2=tri[:,2]-tri[:,0];p=np.cross(direction,e2);det=np.sum(e1*p,axis=1);inv=np.divide(1,det,out=np.zeros_like(det),where=abs(det)>1e-10);s=origin-tri[:,0];u=np.sum(s*p,axis=1)*inv;q=np.cross(s,e1);vv=q@direction*inv;tt=np.sum(e2*q,axis=1)*inv;hit=(abs(det)>1e-10)&(u>=0)&(vv>=0)&(u+vv<=1)&(tt>1e-4);assert not hit.any(),'Engine centerline intersects ship aft of nozzle'
R=np.array(m['normalization']['proper_rotation']);assert np.allclose(R.T@R,np.eye(3))and abs(np.linalg.det(R)-1)<1e-9
source=json.loads((AUD/'source-audit.json').read_text());assert hashlib.sha256(Path(source['archive']).read_bytes()).hexdigest()==source['archive_sha256'];assert hashlib.sha256((ROOT/'assets/original/update12-sunflare'/Path(source['archive']).name).read_bytes()).hexdigest()==source['archive_sha256']
for path,sha in source['master_hashes'].items():assert hashlib.sha256((MASTER/path).read_bytes()).hexdigest()==sha
# Position-silhouette coverage of complete original and complete reduced geometry.
a=Gltf(Path(source['source']));pr=a.g['meshes'][0]['primitives'][0];raw=a.accessor(pr['attributes']['POSITION']);indices=a.accessor(pr['indices']).reshape(-1,3);norm=m['normalization'];raw=(raw-np.array(norm['source_mesh_local_center']))@R.T*norm['uniform_scale'];original=raw[indices];checks=[]
for name,B in [('top',[[0,0,1],[1,0,0],[0,1,0]]),('side',[[0,0,1],[0,1,0],[-1,0,0]]),('rear',[[1,0,0],[0,1,0],[0,0,-1]])]:
 B=np.array(B);aa=original@B.T;bb=tri@B.T;lo=aa[:,:,:2].min((0,1));hi=aa[:,:,:2].max((0,1));size=(1200,650);zoom=min(size[0]*.9/(hi[0]-lo[0]),size[1]*.9/(hi[1]-lo[1]));masks=[]
 for geometry in [aa,bb]:
  xy=(geometry[:,:,:2]-(lo+hi)/2)*zoom;xy[:,:,1]*=-1;xy+=np.array(size)/2;mask=Image.new('L',size);draw=ImageDraw.Draw(mask)
  for q in xy:draw.polygon([tuple(p)for p in q],fill=255)
  masks.append(np.array(mask)>0)
 union=masks[0]|masks[1];inter=masks[0]&masks[1];iou=float(inter.sum()/union.sum());assert iou>.98,(name,iou);checks.append({'view':name,'silhouette_iou':iou,'threshold':.98});canvas=np.zeros((size[1],size[0],3),np.uint8);canvas[inter]=[145,160,175];canvas[masks[0]&~masks[1]]=[255,60,40];canvas[masks[1]&~masks[0]]=[40,200,255];Image.fromarray(canvas).save(AUD/('silhouette-'+name+'.png'))
# Actual-model portrait annotation identifies the single exhaust point.
portrait=Image.open(BUILD/'ui/source/sunflare_portrait_master.png');draw=ImageDraw.Draw(portrait);draw.text((24,24),'SUNFLARE | +Z bow | central engine nozzle | unarmed',fill='white');portrait.save(AUD/'annotated-view.png')
textures=[]
for p in (BUILD/'game/textures').glob('*.dds'):
 b=p.read_bytes();assert b[:4]==b'DDS ';height,width=struct.unpack_from('<II',b,12);assert(width,height)==(2048,2048);textures.append({'file':p.name,'size':[width,height],'mipmaps':struct.unpack_from('<I',b,28)[0],'sha256':hashlib.sha256(b).hexdigest()})
assert len(textures)==4
for p in (BUILD/'game/mesh_materials').glob('*.mesh_material'):
 mat=json.loads(p.read_text())
 for k,val in mat.items():
  if k.endswith('_texture'):assert(BUILD/'game/textures'/(val+'.dds')).is_file()
for alias in j['materials']:assert(BUILD/'game/mesh_materials'/(alias+'.mesh_material')).is_file()
report={'status':'PASS OFFLINE ONLY','runtime':'NOT RUN','source_preserved':True,'proper_rotation_determinant':float(np.linalg.det(R)),'exhaust_meshpoint_position_and_frame':'PASS','exhaust_centerline_clear':'PASS','normal_unit_error':float(np.max(abs(np.linalg.norm(n,axis=1)-1))),'tangent_normal_dot_error':float(np.max(abs(np.sum(n*t[:,:3],axis=1)))),'silhouette_checks':checks,'dds_checks':textures,'rendering_limits':'DirectX-named source normal map retained without speculative green reversal; in-game bump direction remains unobserved. Independent emissiveRGB approximated by base-color-tinted maskB in installed shader.'};write(AUD/'final-validation.json',report);m['status']='PASS OFFLINE ONLY';m['files']={str(p.relative_to(BUILD/'game')):hashlib.sha256(p.read_bytes()).hexdigest()for p in(BUILD/'game').rglob('*')if p.is_file()};m['ui_integration_spec']=str(AUD/'ui-integration-spec.json');m['source_archive_sha256']=source['archive_sha256'];write(AUD/'integration-spec.json',m);print(json.dumps({'status':'PASS OFFLINE ONLY','triangles':m['assembled_triangle_total'],'files':len(m['files']),'silhouette':checks}))
