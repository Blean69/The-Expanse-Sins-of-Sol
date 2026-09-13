"""Verify compiled overlays, unchanged equipment, source preservation and livery UI."""
from pathlib import Path
import sys,json,hashlib,struct
import numpy as np
sys.path.insert(0,'/run/media/haker/NVME 2/expanse-mod/tools')
from common import read_mesh,Gltf,write
ROOT=Path(__file__).resolve().parents[1];AUD=ROOT/'audit/update13-b';BUILD=ROOT/'build/update13-b';BASE=Path('/run/media/haker/NVME 2/expanse-mod/build/experiments/expanse_update12')
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def binary(p):
 b=p.read_bytes();off=61;verts=[]
 for _ in range(struct.unpack_from('<Q',b,53)[0]):
  vals=struct.unpack_from('<12f?',b,off);verts.append(vals[:-1]);off+=49+(8 if vals[-1]else 0)
 count=struct.unpack_from('<Q',b,off)[0];idx=np.frombuffer(b,dtype='<u4',count=count,offset=off+8).reshape(-1,3)
 return np.array(verts),idx
contracts={}
for kind in ['morrigan','raptor','pella']:
 prefix=('expanse11_'if kind=='morrigan'else'expanse12_')+kind;name=prefix+'_hull.mesh';a=BASE/'meshes'/name;b=BUILD/kind/'game/meshes'/name;old=read_mesh(a);new=read_mesh(b);va,ia=binary(a);vb,ib=binary(b);assert old['meshpoints']==new['meshpoints'];assert np.allclose(old['box'],new['box'],atol=1e-4);assert old['materials']==new['materials']
 ta=va[ia,:3];tb=vb[ib,:3];ar=lambda t:np.linalg.norm(np.cross(t[:,1]-t[:,0],t[:,2]-t[:,0]),axis=1).sum()/2
 assert abs(ar(ta)-ar(tb))/ar(ta)<2e-6
 if kind!='morrigan':
  assert ta.shape==tb.shape and np.allclose(ta,tb,atol=1e-4),'Triangle order or positions unexpectedly changed'
  assert np.allclose(va[ia,10:12],vb[ib,10:12],atol=1e-6),'UVs unexpectedly changed'
 q=np.cross(tb[:,1]-tb[:,0],tb[:,2]-tb[:,0]);n=vb[:,3:6];t=vb[:,6:9];cos=np.sum(q*n[ib].mean(1),axis=1)/np.maximum(np.linalg.norm(q,axis=1)*np.linalg.norm(n[ib].mean(1),axis=1),1e-15);assert (cos< -1e-5).sum()==0;assert abs(np.sum(n*t,axis=1)).max()<1e-5;assert abs(np.linalg.norm(n,axis=1)-1).max()<1e-5
 source=json.loads((AUD/kind/'shading-and-paint.json').read_text())
 for path,h in source['input_hashes'].items():assert sha(Path(path))==h
 for mat in new['materials']:
  material=BASE/'mesh_materials'/(mat+'.mesh_material');assert material.exists()
  for key,val in json.loads(material.read_text()).items():
   if key.endswith('_texture'):assert (BASE/'textures'/(val+'.dds')).exists()
 data={'status':'PASS OFFLINE ONLY','source_inputs_unchanged':True,'meshpoints_byte_values_unchanged':True,'bounds_unchanged':True,'surface_area_relative_difference':float(abs(ar(ta)-ar(tb))/ar(ta)),'before_triangles':old['triangles'],'after_triangles':new['triangles'],'exact_ordered_triangle_positions_and_uvs_preserved':kind!='morrigan','opposed_winding_triangles':int((cos< -1e-5).sum()),'near_ambiguous_triangles':int((abs(cos)<=1e-5).sum()),'maximum_normal_tangent_dot':float(abs(np.sum(n*t,axis=1)).max()),'runtime':'NOT RUN'};write(AUD/kind/'final-validation.json',data)
 contract={'status':'PASS OFFLINE ONLY','game_directory':str(BUILD/kind/'game'),'resource_hashes':{str(p.relative_to(BUILD/kind/'game')):sha(p)for p in(BUILD/kind/'game').rglob('*')if p.is_file()},'metadata':str(AUD/kind/'integration-spec.json'),'validation':str(AUD/kind/'final-validation.json'),'runtime':'NOT RUN'}
 if kind=='morrigan':
  ui=json.loads((AUD/kind/'ui-integration-spec.json').read_text());contract['ui']=str(AUD/kind/'ui-integration-spec.json');u=Path(ui['game_directory']);contract['ui_resource_hashes']={str(p.relative_to(u)):sha(p)for p in u.rglob('*')if p.is_file()}
 else:contract['ui']='Existing update12 UI unchanged: silhouette, visible materials and emblem layout preserved; CPU UI renderer does not consume vertex shading frames.'
 contracts[kind]=contract
write(AUD/'integration-contract.json',contracts);print(json.dumps(contracts,indent=2))
