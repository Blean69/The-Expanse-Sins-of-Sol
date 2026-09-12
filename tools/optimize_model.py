"""Simplify each named source part independently, retaining all six PDCs.

Uses the pinned upstream meshoptimizer C API; original files are never edited.
Attribute-aware permissive simplification allows imported shading seams to
collapse while weighting normals and UVs. Output requires visual review.
"""
from common import *
import ctypes as c, shutil, copy, hashlib

lib=c.CDLL(str(ROOT/'.tools/libmeshoptimizer.so'))
u=c.POINTER(c.c_uint);f=c.POINTER(c.c_float)
fn=lib.meshopt_simplifyWithAttributes
fn.argtypes=[u,u,c.c_size_t,f,c.c_size_t,c.c_size_t,f,c.c_size_t,f,c.c_size_t,c.POINTER(c.c_ubyte),c.c_size_t,c.c_float,c.c_uint,f];fn.restype=c.c_size_t
a=Gltf(ROOT/'assets/source/tachi/scene.gltf');g=copy.deepcopy(a.g);binary=bytearray(a.buffers[0]);records=[]
for mi,mesh in enumerate(g['meshes']):
    for pi,p in enumerate(mesh['primitives']):
        v=np.ascontiguousarray(a.accessor(p['attributes']['POSITION']),dtype='float32');idx=np.ascontiguousarray(a.accessor(p['indices']).flatten(),dtype='uint32');dst=np.zeros_like(idx)
        attr=np.ascontiguousarray(np.concatenate([a.accessor(p['attributes']['NORMAL']),a.accessor(p['attributes']['TEXCOORD_0'])],axis=1),dtype='float32');weights=np.array([.05,.05,.05,.2,.2],dtype='float32');err=c.c_float()
        target=max(6,len(idx)//36*3)
        n=fn(dst.ctypes.data_as(u),idx.ctypes.data_as(u),len(idx),v.ctypes.data_as(f),len(v),12,attr.ctypes.data_as(f),20,weights.ctypes.data_as(f),5,None,target,.05,32,c.byref(err))
        assert n>0 and n%3==0 and n<=len(idx)
        dst=dst[:n];binary.extend(b'\0'*((-len(binary))%4));off=len(binary);binary.extend(dst.tobytes());vi=len(g['bufferViews']);g['bufferViews'].append({'buffer':0,'byteOffset':off,'byteLength':dst.nbytes});p['indices']=len(g['accessors']);g['accessors'].append({'bufferView':vi,'componentType':5125,'count':n,'type':'SCALAR','min':[int(dst.min())],'max':[int(dst.max())]})
        records.append(dict(mesh=mi,name=mesh.get('name'),primitive=pi,input_triangles=len(idx)//3,output_triangles=n//3,error=float(err.value)))
out=ROOT/'assets/derived/optimized-source';out.mkdir(parents=True,exist_ok=True);g['buffers'][0]['byteLength']=len(binary);(out/'scene.bin').write_bytes(binary);write(out/'scene.gltf',g);shutil.copytree(a.path.parent/'textures',out/'textures',dirs_exist_ok=True)
report=dict(upstream_commit='bba256eaa24039b6f93c773063ff7c20143ae0db',input_triangles=sum(r['input_triangles'] for r in records),output_triangles=sum(r['output_triangles'] for r in records),parts=len(records),target_ratio=1/12,error_limit=.05,attribute_weights=weights.tolist(),options='meshopt_SimplifyPermissive (32)',removed_parts=0,records=records)
write(ROOT/'audit/optimization.json',report);print('Optimized',report['input_triangles'],'->',report['output_triangles'],'triangles;',len(records),'parts retained')
