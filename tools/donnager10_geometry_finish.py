"""Tangent-only binary/JSON repair preserving official geometry/facing trailer.
Reads retained authored tangent frames; orthogonalizes them without altering UVs.
"""
from common import *
import struct,hashlib,copy
from scipy.spatial import cKDTree
from scipy.spatial.transform import Rotation
from PIL import Image,ImageDraw
out=ROOT/'assets/derived/donnager10-b';build=ROOT/'build/donnager10-b';audit=ROOT/'audit/donnager10-b';sources=read(out/'retained-source-frames.json');meta=read(audit/'mount-metadata.json');dest=build/'game/meshes';jdest=build/'repaired-json';dest.mkdir(parents=True,exist_ok=True);jdest.mkdir(exist_ok=True)
sha=lambda b:hashlib.sha256(b).hexdigest();records={};allworld=[]
for kind,frame in meta['frames'].items():
 name='expanse10_'+kind;jp=build/'compiler-json'/(name+'.mesh_json');bp=build/'compiler-binary'/(name+'.mesh');m=read(jp);original=bp.read_bytes();b=bytearray(original);count=struct.unpack_from('<Q',b,53)[0];off=61;binary=[];tangent_offsets=[]
 for _ in range(count):
  vals=struct.unpack_from('<12f?',b,off);binary.append(vals[:-1]);tangent_offsets.append(off+24);off+=49+(8 if vals[-1] else 0)
 binary=np.array(binary);assert count==len(m['non_skinned_vertices']);lookup=[];st=[]
 for mi,r in sources[kind].items():lookup.append(np.concatenate([np.array(r['positions']),np.array(r['normals']),np.array(r['uv'])],axis=1));st.append(np.array(r['tangents']))
 lookup=np.concatenate(lookup);st=np.concatenate(st);features=np.concatenate([binary[:,:6],binary[:,10:12]],axis=1);distance,si=cKDTree(lookup).query(features);assert distance.max()<2e-4,(name,'authored frame match fails',distance.max())
 tang=st[si].copy();norm=binary[:,3:6];norm=norm/np.linalg.norm(norm,axis=1)[:,None];tang[:,:3]-=norm*np.sum(tang[:,:3]*norm,axis=1)[:,None];length=np.linalg.norm(tang[:,:3],axis=1);fallback=np.where(length<1e-8)[0]
 for i in fallback:
  axis=np.eye(3)[np.argmin(abs(norm[i]))];tang[i,:3]=axis-norm[i]*np.dot(axis,norm[i])
 tang[:,:3]/=np.linalg.norm(tang[:,:3],axis=1)[:,None];tang[:,3]=np.where(tang[:,3]<0,-1.,1.);tang=tang.astype('<f4');allowed=np.zeros(len(b),dtype=bool)
 for i,start in enumerate(tangent_offsets):struct.pack_into('<4f',b,start,*tang[i]);allowed[start:start+16]=True;m['non_skinned_vertices'][i]['t']=tang[i].astype(float).tolist()
 before=np.frombuffer(original,dtype='u1');after=np.frombuffer(b,dtype='u1');assert np.all((before==after)|allowed),'Non-tangent bytes changed'
 prefix=read_mesh(bp)['parsed_prefix_bytes'];assert bytes(b[prefix:])==original[prefix:],'Official trailer changed';assert m['vertex_indices']==read(jp)['vertex_indices'];assert m['triangle_facing_datas']==read(jp)['triangle_facing_datas']
 idx=np.array(m['vertex_indices']);indexed=idx.reshape(-1,3);v=binary[:,:3];vn=binary[:,3:6];tri=v[indexed];face=np.cross(tri[:,1]-tri[:,0],tri[:,2]-tri[:,0]);dot=np.sum(face*vn[indexed].mean(1),axis=1);alignment=dot/np.maximum(np.linalg.norm(face,axis=1)*np.linalg.norm(vn[indexed].mean(1),axis=1),1e-15);opposed=int(np.sum(alignment< -1e-5));assert opposed==0,(name,'Winding remains opposed')
 td=np.abs(np.sum(vn*tang[:,:3],axis=1));tl=np.linalg.norm(tang[:,:3],axis=1);assert np.isfinite(tang).all() and td.max()<2e-5 and abs(tl-1).max()<2e-5
 # JSON and binary were sourced from separate official runs; positions/normals/
 # UVs already match within serialization precision; updated tangents exact.
 jv=np.array([x['p']+x['n']+x['t']+x['uv0'] for x in m['non_skinned_vertices']]);bv=binary.copy();bv[:,6:10]=tang;parity=float(abs(jv-bv).max());assert parity<2e-5
 (dest/(name+'.mesh')).write_bytes(b);write(jdest/(name+'.mesh_json'),m)
 info=read_mesh(dest/(name+'.mesh'));assert info['triangles']==meta['counts'][kind]
 assert len(info['meshpoints'])==len(meta['meshpoints'][kind])
 for actual,expected in zip(info['meshpoints'],meta['meshpoints'][kind]):
  assert actual['name']==expected['name'] and np.allclose(actual['position'],expected['translation'],atol=2e-5);assert np.allclose(np.array(actual['rotation']).reshape(3,3),Rotation.from_quat(expected.get('rotation',[0,0,0,1])).as_matrix().T,atol=2e-5)
 B=np.array(frame['basis']);origin=np.array(frame['origin']);world=v@B.T+origin;allworld.append(world[idx]);records[kind]={'status':'PASS OFFLINE; RUNTIME NOT RUN','mesh':str(dest/(name+'.mesh')),'sha256':sha(b),'raw_official_sha256':sha(original),'triangles':len(indexed),'materials':m['materials'],'source_frame_max_match_error':float(distance.max()),'orthogonal_fallback_vertex_count':len(fallback),'tangent_max_abs_normal_dot':float(td.max()),'tangent_max_unit_error':float(abs(tl-1).max()),'opposed_winding_triangles':opposed,'near_ambiguous_winding_triangles':int(np.sum(abs(alignment)<=1e-5)),'minimum_face_normal_cosine':float(alignment.min()),'winding_cosine_tolerance':1e-5,'binary_json_vertex_max_error':parity,'changed_bytes':int(np.sum(before!=after)),'only_tangent_fields_changed':True,'trailer_sha256_before':sha(original[prefix:]),'trailer_sha256_after':sha(bytes(b[prefix:])),'official_triangle_facing_data_unchanged':True,'meshpoints':info['meshpoints']}
# Verify all original indexed triangle positions preserved across all five unique meshes.
referenced_source=[];unreferenced_source_vertices={}
for k,parts in sources.items():
 inp=Gltf(out/('expanse10_'+k+'.gltf'));unreferenced_source_vertices[k]=0
 for mi,r in parts.items():
  pr=inp.g['meshes'][0]['primitives'][int(mi)];used=np.unique(inp.accessor(pr['indices']).flatten());unreferenced_source_vertices[k]+=len(r['positions'])-len(used);referenced_source.append(np.array(r['positions'])[used]@np.array(meta['frames'][k]['basis']).T+np.array(meta['frames'][k]['origin']))
original=np.concatenate(referenced_source);actual=np.concatenate(allworld);assert len(actual)//3==meta['triangle_total'];d,_=cKDTree(original).query(actual);d2,_=cKDTree(actual).query(original);assert max(d.max(),d2.max())<4e-5
# Validate mount rotations from official output against each frame. Matrix rows
# encode the local X/Y/Z vectors, so compare against basis columns transpose.
hullpts=records['donnager_hull']['meshpoints'];rotation_errors=[]
for r in meta['rigs']:
 p=next(p for p in hullpts if p['name']==r['mount']['mesh_point']);B=np.array(r['basis_columns']);R=np.array(p['rotation']).reshape(3,3);expected=np.stack([np.cross(r['mount']['up'],r['mount']['forward']),r['mount']['up'],r['mount']['forward']]);err=float(abs(R-expected).max());assert err<2e-5;rotation_errors.append({'index':r['index'],'basis_error':err,'row0_right_row1_up_row2_forward':True,'stored_rows_match_columns_transposed':bool(np.allclose(R,B.T,atol=2e-5))})
# Static weapon/exhaust points use the same strict stock-game row convention.
for mount in meta.get('measured_static_weapon_mounts',[]):
 point=next(p for p in hullpts if p['name']==mount['mesh_point']);expected=np.stack([np.cross(mount['up'],mount['forward']),mount['up'],mount['forward']]);error=float(abs(np.array(point['rotation']).reshape(3,3)-expected).max());assert error<2e-5;rotation_errors.append({'mesh_point':mount['mesh_point'],'basis_error':error,'row0_right_row1_up_row2_forward':True})
for point_name,mount in [('exhaust.0',meta['exhaust_geometry'])]+([('weapon.rail.0',meta['custom_railgun'])] if 'custom_railgun' in meta else []):
 point=next(p for p in hullpts if p['name']==point_name);expected=np.stack([np.cross(mount['up'],mount['forward']),mount['up'],mount['forward']]);error=float(abs(np.array(point['rotation']).reshape(3,3)-expected).max());assert error<2e-5;rotation_errors.append({'mesh_point':point_name,'basis_error':error,'row0_right_row1_up_row2_forward':True})
meta['status']='OFFLINE DONNAGER MESHES AND18MOUNTS PASS; RUNTIME NOT RUN';meta['outputs']=records;meta['rest_pose_position_max_error']=float(max(d.max(),d2.max()));meta['rotation_checks']=rotation_errors;meta['tangent_repair']='Exact16-byte tangent-field substitution only; official regenerated winding/index/grid/trailer preserved';write(audit/'mount-metadata.json',meta);write(audit/'output-validation.json',{'status':'PASS OFFLINE ONLY','triangle_total':len(actual)//3,'rest_pose_position_max_error':meta['rest_pose_position_max_error'],'outputs':records,'rotation_checks':rotation_errors,'unreferenced_input_vertices_excluded_from_indexed_geometry_check':unreferenced_source_vertices,'runtime':'NOT RUN'})
print(json.dumps({'status':'PASS OFFLINE ONLY','unique_triangles':meta['triangle_total'],'assembled_triangles':meta['assembled_triangle_total'],'meshes':len(records),'rest_pose_error':meta['rest_pose_position_max_error']}))
