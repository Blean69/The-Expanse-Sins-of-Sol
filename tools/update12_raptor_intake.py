from pathlib import Path
import struct,hashlib,json,shutil,numpy as np
from scipy.sparse import coo_matrix
from scipy.sparse.csgraph import connected_components
import sys
sys.path.insert(0,'/run/media/haker/NVME 2/expanse-mod/tools')
from polish_ui import render,write
ROOT=Path(__file__).resolve().parents[1];src=Path('/home/haker/Downloads/xxx_-_raptor_whole.stl');out=ROOT/'assets/derived/update12-a';audit=ROOT/'audit/update12-a'
out.mkdir(parents=True,exist_ok=True);audit.mkdir(parents=True,exist_ok=True);(ROOT/'assets/original/update12-raptor').mkdir(parents=True,exist_ok=True)
b=src.read_bytes();sha=hashlib.sha256(b).hexdigest();master=ROOT/'assets/original/update12-raptor'/src.name
if not master.exists():shutil.copyfile(src,master)
assert master.read_bytes()==b
n=struct.unpack_from('<I',b,80)[0];assert len(b)==84+50*n
a=np.frombuffer(b,dtype=np.dtype([('n','<f4',(3,)),('v','<f4',(3,3)),('a','<u2')]),offset=84,count=n);tri=a['v'].astype(float)
v,ii=np.unique(np.round(tri.reshape(-1,3),5),axis=0,return_inverse=True);idx=ii.reshape(-1,3);edges=np.concatenate([idx[:,[0,1]],idx[:,[1,2]],idx[:,[2,0]]]);g=coo_matrix((np.ones(len(edges)),(edges[:,0],edges[:,1])),shape=(len(v),len(v)));nc,lab=connected_components(g,directed=False);rows=[]
for i in range(nc):
 mask=lab[idx[:,0]]==i;q=tri[mask];rows.append({'component':i,'triangles':int(mask.sum()),'bounds':[q.min((0,1)).tolist(),q.max((0,1)).tolist()]})
write(audit/'source-audit.json',{'source':str(src),'sha256':sha,'format':'binary STL','triangles':n,'components':sorted(rows,key=lambda x:-x['triangles']),'materials':0,'textures':0,'animations':0,'bounds':[tri.min((0,1)).tolist(),tri.max((0,1)).tolist()],'creator':'Not supplied','license':'Not supplied; do not invent','permission':'User supplied STL and requested local conversion; no license document or creator statement supplied','source_archive_unchanged':True})
# Initial source views; orientation not decided.
# Original X-long axis represented horizontally, no assumption which end is bow yet.
np.savez(out/'source-welded.npz',v=v,i=idx,labels=lab);
import ctypes as c
lib=c.CDLL('/run/media/haker/NVME 2/expanse-mod/.tools/libmeshoptimizer.so');u=c.POINTER(c.c_uint);f=c.POINTER(c.c_float);fn=lib.meshopt_simplify;fn.argtypes=[u,u,c.c_size_t,f,c.c_size_t,c.c_size_t,c.c_size_t,c.c_float,c.c_uint,f];fn.restype=c.c_size_t
pos=np.ascontiguousarray(v,dtype='float32');ii=np.ascontiguousarray(idx.ravel(),dtype='uint32');dst=np.empty_like(ii);error=c.c_float();nn=fn(dst.ctypes.data_as(u),ii.ctypes.data_as(u),len(ii),pos.ctypes.data_as(f),len(pos),12,90000*3,.005,0,c.byref(error));small=pos[dst[:nn].reshape(-1,3)];tex=np.full((1,1,4),255,np.uint8);uv=np.zeros((len(small),3,2));meshes=[(small,uv,tex,[.5,.55,.6,1],'OPAQUE')]
for name,basis in [('top',[[1,0,0],[0,1,0],[0,0,1]]),('side',[[1,0,0],[0,0,1],[0,-1,0]]),('oblique',[[1,0,0],[0,.65,.76],[0,-.76,.65]])]:render(meshes,(1400,600),np.array(basis)).save(audit/(name+'.png'))
print(json.dumps({'triangles':n,'components':nc,'largest':sorted(rows,key=lambda x:-x['triangles'])[:12]}))
