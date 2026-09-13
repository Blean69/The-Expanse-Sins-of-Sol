"""Simplify and render actual recovered print geometry; no image editing or invented source mesh."""
from pathlib import Path
import ctypes as c, numpy as np
from build_polish import write
from polish_ui import render
ROOT=Path(__file__).resolve().parents[1];D=ROOT/'assets/derived/tycho18-recovery-solid';A=ROOT/'audit/update18-tycho-art';A.mkdir(parents=True,exist_ok=True)
lib=c.CDLL(str(ROOT/'.tools/libmeshoptimizer.so'));u=c.POINTER(c.c_uint);f=c.POINTER(c.c_float);fn=lib.meshopt_simplify
fn.argtypes=[u,u,c.c_size_t,f,c.c_size_t,c.c_size_t,c.c_size_t,c.c_float,c.c_uint,f];fn.restype=c.c_size_t
meshes=[];records=[]
for name in ['upper','lower']:
 z=np.load(D/(name+'.npz'));v=np.ascontiguousarray(z['v'],dtype='float32');idx=np.ascontiguousarray(z['i'].ravel(),dtype='uint32');dst=np.empty_like(idx);err=c.c_float()
 count=fn(dst.ctypes.data_as(u),idx.ctypes.data_as(u),len(idx),v.ctypes.data_as(f),len(v),12,120000*3,.012,0,c.byref(err))
 faces=dst[:count].reshape(-1,3);vertices,remap=np.unique(faces,return_inverse=True);v=v[vertices];faces=remap.reshape(-1,3)
 np.savez_compressed(D/(name+'-simplified.npz'),v=v,i=faces)
 tri=v[faces];uv=np.zeros((len(tri),3,2));meshes.append((tri,uv,np.full((1,1,4),255,np.uint8),[.46,.49,.51,1],'OPAQUE'))
 records.append({'part':name,'source_triangles':len(idx)//3,'simplified_triangles':len(faces),'relative_error':err.value});print(records[-1],flush=True)
write(A/'simplification.json',records)
for name,view in [('side',[[1,0,0],[0,1,0],[0,0,1]]),('top',[[1,0,0],[0,0,1],[0,-1,0]]),('oblique',[[.8,0,-.6],[-.3,.866,-.4],[.52,.5,.69]])]:
 render(meshes,(1050,850),np.array(view),fill=.88).save(A/(name+'.png'));print(name,flush=True)
