from common import *
import ctypes as c,time
lib=c.CDLL('/run/media/haker/NVME 2/expanse-mod/.tools/libmeshoptimizer.so');u=c.POINTER(c.c_uint);f=c.POINTER(c.c_float);fn=lib.meshopt_simplifyWithAttributes;fn.argtypes=[u,u,c.c_size_t,f,c.c_size_t,c.c_size_t,f,c.c_size_t,f,c.c_size_t,c.POINTER(c.c_ubyte),c.c_size_t,c.c_float,c.c_uint,f];fn.restype=c.c_size_t
a=Gltf(ROOT/'assets/derived/geometry03-b/hero-master/Rocinante_(The_Expanse).gltf');records=[]
for error,normalweight,options in [(.003,.3,1),(.005,.3,1),(.003,.3,0),(.005,.3,32)]:
 total=0;parts=[]
 for ni,n in enumerate(a.g['nodes']):
  if 'mesh' not in n or ni in [67,68]:continue
  for p in a.g['meshes'][n['mesh']]['primitives']:
   pos=np.ascontiguousarray(a.accessor(p['attributes']['POSITION']),dtype='float32');normal=np.ascontiguousarray(a.accessor(p['attributes']['NORMAL']),dtype='float32');idx=np.ascontiguousarray(a.accessor(p['indices']).flatten(),dtype='uint32');_,used,remap=np.unique(np.concatenate([pos,normal],axis=1),axis=0,return_index=True,return_inverse=True);pos=np.ascontiguousarray(pos[used]);normal=np.ascontiguousarray(normal[used]);idx=np.ascontiguousarray(remap[idx],dtype='uint32');dst=np.zeros_like(idx);weights=np.array([normalweight]*3,dtype='float32');err=c.c_float();nn=fn(dst.ctypes.data_as(u),idx.ctypes.data_as(u),len(idx),pos.ctypes.data_as(f),len(pos),12,normal.ctypes.data_as(f),12,weights.ctypes.data_as(f),3,None,max(12,len(idx)//60*3),error,options,c.byref(err));total+=nn//3;parts.append({'node':ni,'triangles':nn//3,'error':err.value})
 row={'error_limit':error,'normal_weight':normalweight,'options':options,'triangles':total,'parts':parts};records.append(row);print({k:v for k,v in row.items() if k!='parts'},flush=True)
write(ROOT/'audit/geometry04-b/quality-probe-weld.json',records)
