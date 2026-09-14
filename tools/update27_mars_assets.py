"""Bounded asset helpers; frozen0.26 and pinned SDK are read-only inputs."""
from pathlib import Path
import sys,struct,copy,hashlib,ctypes as c
import numpy as np
from collections import defaultdict
from scipy.sparse import coo_matrix,diags
from scipy.spatial.transform import Rotation
MAIN=Path('/run/media/haker/NVME 2/expanse-mod')
sys.path.insert(0,str(MAIN/'tools'))
from common import read,write,read_mesh,Gltf
import update12_scirocco_common as h
ROOT=Path(__file__).resolve().parents[1];BASE=MAIN/'build/experiments/expanse_update26';OUT=ROOT/'assets/derived/update27-mars-laconia';BUILD=ROOT/'build/update27-mars-laconia';GAME=BUILD/'game';AUD=ROOT/'audit/update27-mars-laconia'
for p in [OUT,BUILD,AUD,GAME/'meshes',GAME/'mesh_materials',GAME/'textures']:p.mkdir(parents=True,exist_ok=True)
COLORS={'armor':[.28,.32,.35,1],'orange':[.50,.105,.037,1],'dark':[.065,.075,.085,1],'silver':[.47,.50,.53,1],'nozzle':[.03,.45,.8,1]}
def loadmesh(name):
 p=BASE/'meshes'/(name+'.mesh');b=p.read_bytes();cnt=struct.unpack_from('<Q',b,53)[0];off=61;rows=[]
 for _ in range(cnt):
  r=struct.unpack_from('<12f?',b,off);rows.append(r[:-1]);off+=49+(8 if r[-1]else 0)
 count=struct.unpack_from('<Q',b,off)[0];return np.array(rows),np.frombuffer(b,'<u4',count,off+8).reshape(-1,3)
def frames(t,mat,smooth=35):
 t=np.asarray(t);v=t.reshape(-1,3);q=np.cross(t[:,1]-t[:,0],t[:,2]-t[:,0]);q/=np.linalg.norm(q,axis=1)[:,None];n=np.repeat(q,3,axis=0)
 if smooth:
  _,inv=np.unique(np.round(v,5),axis=0,return_inverse=True);order=np.argsort(inv);cuts=np.flatnonzero(np.diff(inv[order]))+1
  for ids in np.split(order,cuts):
   ns=n[ids].copy();s=(ns@ns.T>=np.cos(np.deg2rad(smooth)))@ns;l=np.linalg.norm(s,axis=1);n[ids]=s/np.maximum(l[:,None],1e-20)
 axes=np.eye(3)[np.argmin(abs(n),axis=1)];tan=axes-n*(axes*n).sum(1)[:,None];tan/=np.linalg.norm(tan,axis=1)[:,None]
 return {'v':v,'n':n,'t':np.column_stack([tan,np.ones(len(v))]),'uv':np.full((len(v),2),.5),'i':np.arange(len(v)).reshape(-1,3),'material':mat}
def save(name,parts,points=()):
 groups=defaultdict(list)
 for part in parts:groups[part['material']].append(part)
 merged=[]
 for material,group in groups.items():
  offsets=np.cumsum([0]+[len(p['v'])for p in group[:-1]]);merged.append({**{k:np.concatenate([p[k]for p in group])for k in ['v','n','t','uv']},'i':np.concatenate([p['i']+offset for p,offset in zip(group,offsets)]),'material':material})
 parts=merged
 h.OUT=OUT;h.savegltf(name,parts,points);h.savegltf(name+'_editable',parts,points,False)
 np.savez_compressed(OUT/(name+'-frames.npz'),**{f'{j}_{k}':p[k]for j,p in enumerate(parts)for k in ['v','n','t','uv']})
 return {'name':name,'triangles':sum(len(p['i'])for p in parts),'meshpoints':list(points)}
def simplify(t,target,error=.001):
 if len(t)<=target:return t,0.
 v,i=np.unique(np.round(t,6).reshape(-1,3),axis=0,return_inverse=True);v=np.ascontiguousarray(v,'float32');idx=np.ascontiguousarray(i,'uint32');dst=np.zeros_like(idx);er=c.c_float();u=c.POINTER(c.c_uint);f=c.POINTER(c.c_float);fn=c.CDLL(str(MAIN/'.tools/libmeshoptimizer.so')).meshopt_simplify;fn.argtypes=[u,u,c.c_size_t,f,c.c_size_t,c.c_size_t,c.c_size_t,c.c_float,c.c_uint,f];fn.restype=c.c_size_t
 count=fn(dst.ctypes.data_as(u),idx.ctypes.data_as(u),len(idx),v.ctypes.data_as(f),len(v),12,target*3,error,0,c.byref(er));q=v[dst[:count]].reshape(-1,3,3).astype(float);valid=np.linalg.norm(np.cross(q[:,1]-q[:,0],q[:,2]-q[:,0]),axis=1)>1e-8;return q[valid],er.value

def rayhit(t,o,d):
 o=np.array(o,float);d=np.array(d,float);e1=t[:,1]-t[:,0];e2=t[:,2]-t[:,0];h=np.cross(d,e2);det=np.sum(e1*h,1);inv=np.divide(1,det,out=np.zeros_like(det),where=abs(det)>1e-10);s=o-t[:,0];u=np.sum(s*h,1)*inv;q=np.cross(s,e1);v=q@d*inv;dist=np.sum(e2*q,1)*inv;ok=(abs(det)>1e-10)&(u>=-1e-7)&(v>=-1e-7)&(u+v<=1+1e-7)&(dist>1e-6)
 if not ok.any():raise ValueError(('no hull hit',o.tolist(),d.tolist()))
 return o+d*dist[ok].min()
def rings(rings):
 """Connect outward-wound rings along positive local axis; caps handled separately."""
 out=[]
 for aa,bb in zip(rings[:-1],rings[1:]):
  for i in range(len(aa)):
   j=(i+1)%len(aa);out.extend([[aa[i],aa[j],bb[j]],[aa[i],bb[j],bb[i]]])
 return np.array(out)
def cylinder(a,b,r,segments=32,inner=None):
 a=np.array(a,float);b=np.array(b,float);up=(b-a)/np.linalg.norm(b-a);right=np.eye(3)[np.argmin(abs(up))];right-=up*np.dot(right,up);right/=np.linalg.norm(right);fw=np.cross(up,right);ring=np.array([right*np.cos(i*2*np.pi/segments)+fw*np.sin(i*2*np.pi/segments)for i in range(segments)]);tri=[]
 def face(x,y,z,outward):
  if np.dot(np.cross(y-x,z-x),outward)<0:y,z=z,y
  tri.append([x,y,z])
 for i in range(segments):
  j=(i+1)%segments;aa=a+r*ring[i];ab=a+r*ring[j];ba=b+r*ring[i];bb=b+r*ring[j];side=ring[i]+ring[j];face(aa,ab,bb,side);face(aa,bb,ba,side)
  if inner is None:face(a,aa,ab,-up);face(b,ba,bb,up)
  else:
   ia=a+inner*ring[i];ib=a+inner*ring[j];ja=b+inner*ring[i];jb=b+inner*ring[j];face(ia,jb,ib,-side);face(ia,ja,jb,-side);face(aa,ia,ib,-up);face(aa,ib,ab,-up);face(ba,bb,jb,up);face(ba,jb,ja,up)
 return np.array(tri)
def box(lo,hi):
 lo=np.array(lo);hi=np.array(hi);v=np.array([[x,y,z]for x in[lo[0],hi[0]]for y in[lo[1],hi[1]]for z in[lo[2],hi[2]]]);ix=np.array([[0,1,3],[0,3,2],[4,6,7],[4,7,5],[0,4,5],[0,5,1],[2,3,7],[2,7,6],[0,2,6],[0,6,4],[1,5,7],[1,7,3]]);return v[ix]
def native_drive(center,diameter):
 dv,di=loadmesh('expanse15_truman_hull');bounds=np.array([[-115.8251,-83.3203,-428.4792],[-37.9893,-5.4845,-381.2714]]);di=di[((dv[di,:3]>=bounds[0]-1e-3)&(dv[di,:3]<=bounds[1]+1e-3)).all((1,2))];used,remap=np.unique(di,return_inverse=True);rows=dv[used];v=rows[:,:3];lo=v.min(0);hi=v.max(0);s=diameter/max(hi[:2]-lo[:2]);v=(v-np.r_[(lo[:2]+hi[:2])/2,lo[2]])*s+center
 return {'v':v,'n':rows[:,3:6],'t':rows[:,6:10],'uv':rows[:,10:12],'i':remap.reshape(-1,3),'material':'drive'}
def pdc(t,name,positions):
 rigs=[];pts=[];support=[];lo=t.min((0,1));hi=t.max((0,1));native=read(BASE/'entities/expanse24_gathering_storm_pdc_0.weapon')['turret']
 for j,(anchor,up)in enumerate(positions):
  up=np.array(up,float);anchor=np.array(anchor,float);surface=rayhit(t,anchor+up*500,-up);pivot=surface+up*1.2;B=np.column_stack([np.cross(up,[0,0,1]),up,[0,0,1]]);support.append(cylinder(surface-up*.5,pivot,2.4,segments=8));pt={'name':f'child.{name}_pdc_{j}','translation':pivot.tolist(),'rotation':Rotation.from_matrix(B).as_quat().tolist()};pts.append(pt);turret=copy.deepcopy(native);turret['biaxial_base_mesh']=name+'_pdc_base';turret['biaxial_barrel_mesh']=name+'_pdc_barrel'
  rigs.append({'kind':'pdc','mesh_point':pt['name'],'position':pivot.tolist(),'up':up.tolist(),'forward':[0,0,1],'yaw_arc':{'min_angle':-180.,'max_angle':180.},'pitch_arc':{'min_angle':-85.,'max_angle':-5.},'turret_override':turret,'surface':surface.tolist()})
 return rigs,pts,support
