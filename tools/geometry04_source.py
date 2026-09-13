"""Bounded source-derived repair after visual comparison proves 0.3 distortion.
Reuses the already audited deployed transforms; never modifies original/0.3 assets.
"""
from common import *
import ctypes as c,hashlib
out=ROOT/'assets/derived/geometry04-b';audit=ROOT/'audit/geometry04-b';out.mkdir(exist_ok=True);a=Gltf(ROOT/'assets/derived/geometry03-b/hero-master/Rocinante_(The_Expanse).gltf');deployed=Gltf(ROOT/'assets/derived/geometry03-b/hero/rocinante_stand_free_deployed.gltf');bymesh={n['mesh']:i for i,n in enumerate(deployed.g['nodes'])};meta=read(ROOT/'audit/geometry03-b/hero-mount-metadata.json');norm=meta['normalization'];Cold=np.array(norm['source_to_game_rotation']);center=np.array(norm['source_rotated_center']);target=np.array(norm['target_center']);scale=norm['scale'];eq=read(ROOT/'audit/geometry03-b/hero-armed-equipment.json');forward=-np.array(eq['exhaust']['forward']);up=np.array([0.,1.,0.]);up-=forward*np.dot(up,forward);up/=np.linalg.norm(up);R=np.stack([np.cross(up,forward),up,forward]);assert np.linalg.det(R)>.999999
lib=c.CDLL('/run/media/haker/NVME 2/expanse-mod/.tools/libmeshoptimizer.so');u=c.POINTER(c.c_uint);f=c.POINTER(c.c_float);fn=lib.meshopt_simplifyWithAttributes;fn.argtypes=[u,u,c.c_size_t,f,c.c_size_t,c.c_size_t,f,c.c_size_t,f,c.c_size_t,c.POINTER(c.c_ubyte),c.c_size_t,c.c_float,c.c_uint,f];fn.restype=c.c_size_t;records=[];arrays={}
for ni,n in enumerate(a.g['nodes']):
 if 'mesh' not in n or ni in [67,68]:continue
 di=bymesh[n['mesh']];M=deployed.world[di]
 for pi,p in enumerate(a.g['meshes'][n['mesh']]['primitives']):
  pos=np.ascontiguousarray(a.accessor(p['attributes']['POSITION']),dtype='float32');normal=np.ascontiguousarray(a.accessor(p['attributes']['NORMAL']),dtype='float32');idx=np.ascontiguousarray(a.accessor(p['indices']).flatten(),dtype='uint32');dst=np.zeros_like(idx);weights=np.array([.1]*3,dtype='float32');err=c.c_float();nn=fn(dst.ctypes.data_as(u),idx.ctypes.data_as(u),len(idx),pos.ctypes.data_as(f),len(pos),12,normal.ctypes.data_as(f),12,weights.ctypes.data_as(f),3,None,max(12,len(idx)//60*3),.005,32,c.byref(err));ii=dst[:nn].reshape(-1,3);used,remap=np.unique(ii,return_inverse=True);wp=pos[used]@M[:3,:3].T+M[:3,3];v=((wp@Cold.T-center)*scale)@R.T+target;no=normal[used]@np.linalg.inv(M[:3,:3])@Cold.T@R.T;no/=np.linalg.norm(no,axis=1)[:,None];ii=remap.reshape(-1,3);q=v[ii];dot=np.sum(np.cross(q[:,1]-q[:,0],q[:,2]-q[:,0])*no[ii].mean(1),axis=1);ii[dot<0]=ii[dot<0][:,[0,2,1]];key=f'n{ni}';arrays[key+'_v']=v;arrays[key+'_n']=no;arrays[key+'_i']=ii;records.append({'key':key,'node':ni,'parent_node':a.parents[ni],'name':a.g['nodes'][a.parents[ni]]['name'],'material':p['material'],'triangles':nn//3,'source_triangles':len(idx)//3,'simplifier_error':err.value})
# Carry forward only the authorized custom rail/ports, rigidly transformed with
# the entire physical hero. Original static PDC geometry is not duplicated.
static=Gltf(ROOT/'assets/derived/geometry03-b/hero/expanse03_hero_static.gltf');armed=Gltf(ROOT/'assets/derived/geometry03-b/hero-armed/expanse03_hero_armed.gltf');staticcounts={p['material']:static.accessor(p['indices']).size for p in static.g['meshes'][0]['primitives']}
for p in armed.g['meshes'][0]['primitives']:
 idx=armed.accessor(p['indices']).flatten()[staticcounts[p['material']]:].reshape(-1,3)
 if not len(idx):continue
 used,remap=np.unique(idx,return_inverse=True);v=armed.accessor(p['attributes']['POSITION'])[used];no=armed.accessor(p['attributes']['NORMAL'])[used];v[:,2]*=-1;no[:,2]*=-1;v=(v-target)@R.T+target;no=no@R.T;key='custom'+str(p['material']);arrays[key+'_v']=v;arrays[key+'_n']=no;arrays[key+'_i']=remap.reshape(-1,3);records.append({'key':key,'node':None,'name':'Preserved custom rail/ports','material':p['material'],'triangles':len(idx),'source_triangles':len(idx),'simplifier_error':0})
np.savez_compressed(out/'parts.npz',**arrays);write(audit/'parts.json',records)
def transform_equipment(m):
 r=__import__('copy').deepcopy(m)
 for field in ['position','muzzle_hull','weapon_position','opening_center']:
  if field in r:r[field]=((np.array(r[field])-target)@R.T+target).tolist()
 for field in ['forward','up']:
  if field in r:r[field]=(R@r[field]).tolist()
 return r
updated={k:[transform_equipment(q) for q in val] if isinstance(val,list) else transform_equipment(val) if isinstance(val,dict) else val for k,val in eq.items()};write(audit/'equipment.json',updated);write(audit/'normalization.json',{'old_game_to_new_game_rotation':R.tolist(),'pivot':target.tolist(),'source_to_game_rotation':(R@Cold).tolist(),'source_rotated_center':(R@center).tolist(),'scale':scale,'target_center':target.tolist(),'equation':'new_position = R @ (old_position - target_center) + target_center','geometry_change':'Uniform rigid normalization only; original source per-segment deployed poses retained. Corrective simplification max error0.005 vs0.04, same pinned library.'});print('Prepared',sum(r['triangles'] for r in records),'triangles incl228 preserved custom fittings',flush=True)
