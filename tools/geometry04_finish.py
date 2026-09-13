"""Tangent-only binary/JSON repair preserving official geometry/facing trailer.
Reads retained authored tangent frames; orthogonalizes them without altering UVs.
"""
from common import *
import struct,hashlib,copy
from scipy.spatial import cKDTree
from PIL import Image,ImageDraw
out=ROOT/'assets/derived/geometry04-b';build=ROOT/'build/geometry04-b';audit=ROOT/'audit/geometry04-b';sources=read(out/'retained-source-frames.json');meta=read(audit/'mount-metadata.json');dest=build/'game/meshes';jdest=build/'repaired-json';dest.mkdir(parents=True,exist_ok=True);jdest.mkdir(exist_ok=True)
sha=lambda b:hashlib.sha256(b).hexdigest();records={};allworld=[]
for kind,frame in meta['frames'].items():
 name='expanse04_'+kind;jp=build/'compiler-json'/(name+'.mesh_json');bp=build/'compiler-binary'/(name+'.mesh');m=read(jp);original=bp.read_bytes();b=bytearray(original);count=struct.unpack_from('<Q',b,53)[0];off=61;binary=[];tangent_offsets=[]
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
 for actual,expected in zip(info['meshpoints'],meta['meshpoints'][kind]):assert actual['name']==expected['name'] and np.allclose(actual['position'],expected['translation'],atol=2e-5)
 B=np.array(frame['basis']);origin=np.array(frame['origin']);world=v@B.T+origin;allworld.append(world[idx]);records[kind]={'status':'PASS OFFLINE; RUNTIME NOT RUN','mesh':str(dest/(name+'.mesh')),'sha256':sha(b),'raw_official_sha256':sha(original),'triangles':len(indexed),'materials':m['materials'],'source_frame_max_match_error':float(distance.max()),'orthogonal_fallback_vertex_count':len(fallback),'tangent_max_abs_normal_dot':float(td.max()),'tangent_max_unit_error':float(abs(tl-1).max()),'opposed_winding_triangles':opposed,'near_ambiguous_winding_triangles':int(np.sum(abs(alignment)<=1e-5)),'minimum_face_normal_cosine':float(alignment.min()),'winding_cosine_tolerance':1e-5,'binary_json_vertex_max_error':parity,'changed_bytes':int(np.sum(before!=after)),'only_tangent_fields_changed':True,'trailer_sha256_before':sha(original[prefix:]),'trailer_sha256_after':sha(bytes(b[prefix:])),'official_triangle_facing_data_unchanged':True,'meshpoints':info['meshpoints']}
# Verify all original indexed triangle positions preserved across all13 meshes.
original=np.concatenate([np.array(r['positions'])@np.array(meta['frames'][k]['basis']).T+np.array(meta['frames'][k]['origin']) for k in sources for r in sources[k].values()]);actual=np.concatenate(allworld);assert len(actual)//3==meta['triangle_total'];d,_=cKDTree(original).query(actual);d2,_=cKDTree(actual).query(original);assert max(d.max(),d2.max())<2e-5
# Validate mount rotations from official output against each frame. Matrix rows
# encode the local X/Y/Z vectors, so compare against basis columns transpose.
hullpts=records['hero_hull']['meshpoints'];rotation_errors=[]
for r in meta['rigs']:
 p=next(p for p in hullpts if p['name']==r['mount']['mesh_point']);B=np.array(r['basis_columns']);R=np.array(p['rotation']).reshape(3,3);expected=np.stack([np.cross(r['mount']['up'],r['mount']['forward']),r['mount']['up'],r['mount']['forward']]);err=float(abs(R-expected).max());assert err<2e-5;rotation_errors.append({'index':r['index'],'basis_error':err,'row0_right_row1_up_row2_forward':True,'stored_rows_match_columns_transposed':bool(np.allclose(R,B.T,atol=2e-5))})
# Static weapon/exhaust points use the same strict stock-game row convention.
for mount in meta.get('measured_static_weapon_mounts',[]):
 point=next(p for p in hullpts if p['name']==mount['mesh_point']);expected=np.stack([np.cross(mount['up'],mount['forward']),mount['up'],mount['forward']]);error=float(abs(np.array(point['rotation']).reshape(3,3)-expected).max());assert error<2e-5;rotation_errors.append({'mesh_point':mount['mesh_point'],'basis_error':error,'row0_right_row1_up_row2_forward':True})
for point_name,mount in [('exhaust.0',meta['exhaust_geometry'])]+([('weapon.rail.0',meta['custom_railgun'])] if 'custom_railgun' in meta else []):
 point=next(p for p in hullpts if p['name']==point_name);expected=np.stack([np.cross(mount['up'],mount['forward']),mount['up'],mount['forward']]);error=float(abs(np.array(point['rotation']).reshape(3,3)-expected).max());assert error<2e-5;rotation_errors.append({'mesh_point':point_name,'basis_error':error,'row0_right_row1_up_row2_forward':True})
meta['status']='OFFLINE SIX HERO AIMING RIG CHECKS PASS; RUNTIME NOT RUN';meta['outputs']=records;meta['rest_pose_position_max_error']=float(max(d.max(),d2.max()));meta['rotation_checks']=rotation_errors;meta['tangent_repair']='Exact16-byte tangent-field substitution only; official regenerated winding/index/grid/trailer preserved';write(audit/'mount-metadata.json',meta);write(audit/'output-validation.json',{'status':'PASS OFFLINE ONLY','triangle_total':len(actual)//3,'rest_pose_position_max_error':meta['rest_pose_position_max_error'],'outputs':records,'rotation_checks':rotation_errors,'runtime':'NOT RUN'})
# Two annotated orthographic views from the actual restored triangles.
im=Image.new('RGB',(1400,900),'#151b24');dr=ImageDraw.Draw(im)
for panel,(haxis,daxis) in enumerate([(0,1),(1,0)]):
 cx=350+700*panel;tris=[]
 for kind,xyz in zip(meta['frames'],allworld):
  c='#8295ad' if kind=='hull' else '#61c8d1' if kind.endswith('barrel') else '#efb657'
  for q in xyz.reshape(-1,3,3):tris.append((float(q[:,daxis].mean()),[(float(cx+x[haxis]*5),float(435-x[2]*6)) for x in q],c))
 for _,pts,c in sorted(tris):dr.polygon(pts,fill=c,outline='#384654')
 for r in meta['rigs']:
  p=r['yaw_pivot_hull'];x=cx+p[haxis]*5;y=435-p[2]*6;dr.ellipse((x-8,y-8,x+8,y+8),outline='#ffce7b',width=2);dr.text((x+10,y-7),str(r['index']),fill='#ffe39c')
dr.text((25,18),'HERO SIX AIMING RIG CANDIDATE / RUNTIME NOT RUN',fill='white');dr.text((25,44),'Six independent yaw/pitch rigs; rotation runtime NOT RUN. Left ship X/Z; right ship Y/Z.',fill='white');dr.text((25,850),f'Stand-free optimized hero: {meta["triangle_total"]} triangles. Source deployment baked; six aiming rigs require runtime inspection.',fill='white');im.save(audit/'six-rig-preview.png')
print(json.dumps({'status':'PASS OFFLINE ONLY','triangles':len(actual)//3,'rest_pose_error':meta['rest_pose_position_max_error'],'meshes':len(records),'fallback_tangents':sum(r['orthogonal_fallback_vertex_count'] for r in records.values())}))
