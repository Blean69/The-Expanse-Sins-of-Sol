"""Scirocco derivative helpers. Original assets and installed data are read-only."""
from pathlib import Path
import numpy as np, json, hashlib, os, copy, sys
from scipy.spatial.transform import Rotation
from common import Gltf,read,write,read_mesh
ROOT=Path(__file__).resolve().parents[1];MAIN=Path('/run/media/haker/NVME 2/expanse-mod');DONOR=Path('/run/media/haker/NVME 2/expanse-workers/tachi-one-pdc');OUT=ROOT/'assets/derived/update12-b';AUD=ROOT/'audit/update12-b';BUILD=ROOT/'build/update12-b';PREFIX='expanse12_scirocco'
sys.path.append(str(MAIN/'tools'))
from polish_ui import render
COLORS=[[.24,.28,.31,1],[.65,.16,.055,1],[.075,.085,.095,1]]
def frames(tris,material):
 from collections import defaultdict
 tt=np.asarray(tris,float);vv=tt.reshape(-1,3);q=np.cross(tt[:,1]-tt[:,0],tt[:,2]-tt[:,0]);face=q/np.linalg.norm(q,axis=1)[:,None];norm=np.repeat(face,3,axis=0);groups=defaultdict(list)
 for j,p in enumerate(np.round(vv,5)):groups[tuple(p)].append(j)
 for ids in groups.values():
  ns=norm[ids].copy();matches=ns@ns.T>.866025403784;nn=matches@ns;nn/=np.linalg.norm(nn,axis=1)[:,None];norm[ids]=nn
 uv=[];tan=[]
 for k,nn in enumerate(face):
  ax=np.eye(3)[np.argmin(abs(nn))];ax-=nn*np.dot(ax,nn);ax/=np.linalg.norm(ax);bit=np.cross(nn,ax);uv.extend(np.column_stack([tt[k]@ax,tt[k]@bit]))
  for n in norm[3*k:3*k+3]:t=ax-n*np.dot(ax,n);t/=np.linalg.norm(t);tan.append([*t,1.])
 uv=np.array(uv);uv=.05+.9*(uv-uv.min(0))/np.maximum(np.ptp(uv,axis=0),1e-9)
 return {'v':vv,'n':norm,'t':np.array(tan),'uv':uv,'i':np.arange(len(vv)).reshape(-1,3),'material':material}
def savegltf(name,parts,meshpoints=(),compiler=True):
 g={'asset':{'version':'2.0','generator':'Scirocco original STL derivative; original unchanged'},'scene':0,'scenes':[{'nodes':[0]}],'nodes':[{'mesh':0,'name':name,'children':[]}],'meshes':[{'primitives':[]}],'materials':[],'buffers':[],'bufferViews':[],'accessors':[]};buf=bytearray()
 def acc(a,typ,ct=5126):
  a=np.asarray(a,dtype='<f4'if ct==5126 else'<u4');buf.extend(b'\0'*((-len(buf))%4));start=len(buf);buf.extend(a.tobytes());g['bufferViews'].append({'buffer':0,'byteOffset':start,'byteLength':a.nbytes});x={'bufferView':len(g['bufferViews'])-1,'componentType':ct,'count':len(a),'type':typ}
  if typ=='VEC3':x.update(min=a.min(0).tolist(),max=a.max(0).tolist())
  g['accessors'].append(x);return len(g['accessors'])-1
 for p in parts:
  vv=p['v'].copy();nn=p['n'].copy();tt=p['t'].copy();idx=p['i'].copy();q=np.cross(vv[idx[:,1]]-vv[idx[:,0]],vv[idx[:,2]]-vv[idx[:,0]]);flip=np.sum(q*nn[idx].mean(1),axis=1)<0;idx[flip]=idx[flip][:,[0,2,1]]
  if compiler:vv[:,2]*=-1;nn[:,2]*=-1;tt[:,2]*=-1;tt[:,3]*=-1
  mat=p['material'];factor=COLORS[int(mat[-1])]if'_mat_'in mat else[.18,.2,.22,1];mi=len(g['materials']);g['materials'].append({'name':mat,'pbrMetallicRoughness':{'baseColorFactor':factor}});g['meshes'][0]['primitives'].append({'mode':4,'material':mi,'indices':acc(idx.ravel(),'SCALAR',5125),'attributes':{'POSITION':acc(vv,'VEC3'),'NORMAL':acc(nn,'VEC3'),'TANGENT':acc(tt,'VEC4'),'TEXCOORD_0':acc(p['uv'],'VEC2')}})
 for point in meshpoints:
  p=copy.deepcopy(point)
  if compiler:
   p['translation'][2]*=-1
   if'rotation'in p:p['rotation'][0]*=-1;p['rotation'][1]*=-1
  g['nodes'][0]['children'].append(len(g['nodes']));g['nodes'].append(p)
 g['buffers']=[{'uri':name+'.bin','byteLength':len(buf)}];(OUT/(name+'.bin')).write_bytes(buf);write(OUT/(name+'.gltf'),g)
