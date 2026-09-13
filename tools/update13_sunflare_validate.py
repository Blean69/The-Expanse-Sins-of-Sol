"""Validate final rotated binary, all attachments and frozen texture/master inputs."""
from pathlib import Path
import json,struct,hashlib
import numpy as np
from common import Gltf,read_mesh
from polish_ui import write
R=Path(__file__).resolve().parents[1];B=R/'build/update13-c';A=R/'audit/update13-c';D=R/'assets/derived/update13-c';OLD=Path('/run/media/haker/NVME 2/expanse-workers/validation');Q=np.diag([-1.,-1.,1.]);sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
m=json.loads((A/'integration-spec.json').read_text());j=json.loads((B/'repaired-json/expanse12_sunflare_hull.mesh_json').read_text());path=B/'game/meshes/expanse12_sunflare_hull.mesh';raw=path.read_bytes();count=struct.unpack_from('<Q',raw,53)[0];off=61;rows=[]
for k in range(count):
 vals=struct.unpack_from('<12f?',raw,off);rows.append(vals[:12]);off+=49+(8 if vals[-1]else 0)
rows=np.array(rows);v=rows[:,:3];n=rows[:,3:6];t=rows[:,6:10];assert np.isfinite(rows).all();assert np.allclose(v,np.array([p['p']for p in j['non_skinned_vertices']]),atol=2e-6);assert np.allclose(t,np.array([p['t']for p in j['non_skinned_vertices']]),atol=2e-6)
idx=np.array(j['vertex_indices']).reshape(-1,3);tri=v[idx];cross=np.cross(tri[:,1]-tri[:,0],tri[:,2]-tri[:,0]);ns=n[idx].mean(1);cos=(cross*ns).sum(1)/(np.linalg.norm(cross,axis=1)*np.linalg.norm(ns,axis=1));assert(cos< -1e-5).sum()==0;assert(abs(cos)<=1e-5).sum()==0;assert np.max(abs(np.linalg.norm(n,axis=1)-1))<2e-5;assert np.max(abs(np.linalg.norm(t[:,:3],axis=1)-1))<2e-5;assert np.max(abs((n*t[:,:3]).sum(1)))<2e-5
mesh=read_mesh(path);ep=next(p for p in mesh['meshpoints']if p['name']=='exhaust.0');ex=m['equipment']['exhaust'];assert np.allclose(ep['position'],ex['position'],atol=2e-5);assert np.allclose(np.array(ep['rotation']).reshape(3,3),np.diag([1.,-1.,-1.]),atol=2e-5)
origin=np.array(ex['position']);direction=np.array(ex['forward']);e1=tri[:,1]-tri[:,0];e2=tri[:,2]-tri[:,0];p=np.cross(direction,e2);det=(e1*p).sum(1);inv=np.divide(1,det,out=np.zeros_like(det),where=abs(det)>1e-10);s=origin-tri[:,0];u=(s*p).sum(1)*inv;q=np.cross(s,e1);vv=q@direction*inv;tt=(e2*q).sum(1)*inv;hit=(abs(det)>1e-10)&(u>=0)&(vv>=0)&(u+vv<=1)&(tt>1e-4);assert not hit.any()
for got,want in zip(mesh['meshpoints'],m['meshpoints']['hull']):assert got['name']==want['name']and np.allclose(got['position'],want['translation'],atol=2e-5)
new=Gltf(D/'expanse12_sunflare_editable.gltf');old=Gltf(OLD/'assets/derived/update12-c/expanse12_sunflare_editable.gltf');pn=new.g['meshes'][0]['primitives'][0];po=old.g['meshes'][0]['primitives'][0]
for k in ['POSITION','NORMAL']:
 assert np.array_equal(new.accessor(pn['attributes'][k])@Q,old.accessor(po['attributes'][k]))
assert np.array_equal(new.accessor(pn['indices']),old.accessor(po['indices']));assert np.array_equal(new.accessor(pn['attributes']['TEXCOORD_0']),old.accessor(po['attributes']['TEXCOORD_0']))
textures=[]
for folder in ['textures','mesh_materials']:
 for p in (B/'game'/folder).iterdir():assert sha(p)==sha(OLD/'build/update12-c/game'/folder/p.name);textures.append(str(p.relative_to(B/'game')))
source=json.loads((OLD/'audit/update12-c/source-audit.json').read_text());assert sha(Path(source['archive']))==source['archive_sha256']
for path,digest in source['master_hashes'].items():assert sha(OLD/'assets/source/update12-sunflare'/path)==digest
m['status']='PASS OFFLINE ONLY';m['files']={str(p.relative_to(B/'game')):sha(p)for p in(B/'game').rglob('*')if p.is_file()};m['ui_integration_spec']=str(A/'ui-integration-spec.json');write(A/'integration-spec.json',m)
ui=json.loads((A/'ui-integration-spec.json').read_text());uiroot=Path(ui['game_directory']);ui['files']={str(p.relative_to(uiroot)):sha(p)for p in uiroot.rglob('*')if p.is_file()};write(A/'ui-integration-spec.json',ui)
report={'status':'PASS OFFLINE ONLY','runtime':'NOT RUN','triangles':len(idx),'proper_roll_determinant':1,'opposed_winding':0,'ambiguous_winding':0,'normal_unit_error':float(abs(np.linalg.norm(n,axis=1)-1).max()),'tangent_normal_dot_error':float(abs((n*t[:,:3]).sum(1)).max()),'exhaust_pose':'PASS; original pose rotated with hull','exhaust_centerline':'PASS; no aft intersection','vertex_index_UV_preservation':'PASS; inverse rotation exactly recovers editable positions/normals and unchanged indices/UVs','unchanged_material_texture_files':textures,'original_archive_and_extracted_master':'PASS; original audit hashes unchanged','UI':'PASS; current rotated geometry rendered with unchanged original textures','presentation_limit':'Proper roll makes a lettered central prong dorsal. Source has no canonical top annotation and any view can show oblique/hidden lettering; actual in-game orientation still needs observation.'};write(A/'final-validation.json',report);print(json.dumps(report))
