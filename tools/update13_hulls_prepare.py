"""Derivative-only plate-normal repair and authored Morrigan panel assignments.
No original reimport, simplification, texture-pixel edits, or shared definition changes.
"""
from pathlib import Path
import sys,json,copy,hashlib
import numpy as np
from collections import defaultdict
sys.path.insert(0,'/run/media/haker/NVME 2/expanse-mod/tools')
from common import Gltf,write
ROOT=Path(__file__).resolve().parents[1];MAIN=Path('/run/media/haker/NVME 2/expanse-mod');OUT=ROOT/'assets/derived/update13-b';AUD=ROOT/'audit/update13-b';BUILD=ROOT/'build/update13-b'
WORK=MAIN.parent/'expanse-workers'

def extract(path):
 g=Gltf(path);parts=[]
 for p in g.g['meshes'][0]['primitives']:
  parts.append({'v':g.accessor(p['attributes']['POSITION']),'n':g.accessor(p['attributes']['NORMAL']),'t':g.accessor(p['attributes']['TANGENT']),'uv':g.accessor(p['attributes']['TEXCOORD_0']),'i':g.accessor(p['indices']).reshape(-1,3),'material':p['material']})
 return g,parts

def smooth(p):
 # Area weights prevent dense tiny groove triangles dominating broad plates.
 v=p['v'];idx=p['i'];tri=v[idx];cross=np.cross(tri[:,1]-tri[:,0],tri[:,2]-tri[:,0]);area=np.linalg.norm(cross,axis=1);fn=cross/np.maximum(area[:,None],1e-12)
 # Compiler-input reflection reverses winding while normals remain outward.
 sign=np.where(np.sum(fn*p['n'][idx].mean(1),axis=1)<0,-1.,1.);fn*=sign[:,None]
 groups=defaultdict(list)
 for f,t in enumerate(tri):
  for k,pt in enumerate(t):groups[tuple(np.round(pt,5))].append((f,int(idx[f,k])))
 nn=p['n'].copy();deviations=[]
 for group in groups.values():
  fs=np.array([x[0]for x in group]);ns=fn[fs];weights=area[fs];match=ns@ns.T>np.cos(np.deg2rad(25));sums=match@(ns*weights[:,None]);sums/=np.maximum(np.linalg.norm(sums,axis=1)[:,None],1e-12)
  for (_,vert),n in zip(group,sums):nn[vert]=n
 old=np.degrees(np.arccos(np.clip(np.sum(p['n'][idx]*fn[:,None,:],axis=2),-1,1)));new=np.degrees(np.arccos(np.clip(np.sum(nn[idx]*fn[:,None,:],axis=2),-1,1)))
 p['n']=nn;t=p['t'].copy();t[:,:3]-=nn*np.sum(t[:,:3]*nn,axis=1)[:,None];norm=np.linalg.norm(t[:,:3],axis=1);assert norm.min()>1e-7;t[:,:3]/=norm[:,None];p['t']=t
 return {'old_corner_face_angle_p95':float(np.percentile(old,95)),'new_corner_face_angle_p95':float(np.percentile(new,95)),'old_corner_face_angle_mean':float(old.mean()),'new_corner_face_angle_mean':float(new.mean()),'maximum_normal_tangent_dot':float(abs(np.sum(nn*t[:,:3],axis=1)).max()),'opposed_corner_normals':int((np.sum(nn[idx]*fn[:,None,:],axis=2)<0).sum())}

def clipped_morrigan(parts):
 # Slice only main gray hull; retain authored turret support colors.
 p=parts[0];packed=np.concatenate([p['v'],p['n'],p['t'],p['uv']],axis=1);tris=packed[p['i']];groups=[[],[],[]]
 # Compiler-space Z sign is reversed. Broad bow cheek band and aft shoulder band.
 limits=[-1e5,-30.,-22.,13.,20.,1e5]
 def clip(poly,z,above):
  result=[]
  for a,b in zip(poly,poly[1:]+poly[:1]):
   ia=a[2]>=z if above else a[2]<=z;ib=b[2]>=z if above else b[2]<=z
   if ia:result.append(a)
   if ia!=ib:result.append(a+(b-a)*(z-a[2])/(b[2]-a[2]))
  return result
 for k,(low,high) in enumerate(zip(limits,limits[1:])):
  mask=(tris[:,:,2].min(1)>=low)&(tris[:,:,2].max(1)<=high);pieces=list(tris[mask]);touch=(tris[:,:,2].max(1)>low)&(tris[:,:,2].min(1)<high)&~mask
  for tri in tris[touch]:
   poly=clip(clip(list(tri),low,True),high,False)
   for j in range(1,len(poly)-1):
    q=np.array([poly[0],poly[j],poly[j+1]])
    if np.linalg.norm(np.cross(q[1,:3]-q[0,:3],q[2,:3]-q[0,:3]))>1e-9:pieces.append(q)
  groups[1 if k in [1,3]else 0].extend(pieces)
 for part in parts[1:3]:groups[part['material']].extend(np.concatenate([part['v'],part['n'],part['t'],part['uv']],axis=1)[part['i']])
 result=[]
 for i,x in enumerate(groups):
  a=np.array(x).reshape(-1,12);n=a[:,3:6];n/=np.linalg.norm(n,axis=1)[:,None];result.append({'v':a[:,:3],'n':n,'t':a[:,6:10],'uv':a[:,10:12],'i':np.arange(len(a)).reshape(-1,3),'material':i})
 return result

def save(path,template,parts):
 g=copy.deepcopy(template);g['bufferViews']=[];g['accessors']=[];g['meshes']=[{'primitives':[]}];buf=bytearray()
 def acc(a,typ,ct=5126):
  a=np.asarray(a,dtype='<f4'if ct==5126 else'<u4');buf.extend(b'\0'*((-len(buf))%4));start=len(buf);buf.extend(a.tobytes());g['bufferViews'].append({'buffer':0,'byteOffset':start,'byteLength':a.nbytes});item={'bufferView':len(g['bufferViews'])-1,'componentType':ct,'count':len(a),'type':typ}
  if typ=='VEC3':item.update(min=a.min(0).tolist(),max=a.max(0).tolist())
  g['accessors'].append(item);return len(g['accessors'])-1
 for p in parts:g['meshes'][0]['primitives'].append({'mode':4,'material':p['material'],'indices':acc(p['i'].ravel(),'SCALAR',5125),'attributes':{'POSITION':acc(p['v'],'VEC3'),'NORMAL':acc(p['n'],'VEC3'),'TANGENT':acc(p['t'],'VEC4'),'TEXCOORD_0':acc(p['uv'],'VEC2')}})
 g['buffers']=[{'uri':path.stem+'.bin','byteLength':len(buf)}];path.parent.mkdir(parents=True,exist_ok=True);path.with_suffix('.bin').write_bytes(buf);write(path,g)

if __name__=='__main__':
 import shutil
 for kind in ['morrigan','raptor','pella']:
  src=WORK/('validation/assets/derived/update11-c'if kind=='morrigan'else'weapon-behavior/assets/derived/update12-a/'+kind);prefix=('expanse11_'if kind=='morrigan'else'expanse12_')+kind;dest=OUT/kind;dest.mkdir(parents=True,exist_ok=True);aud=AUD/kind;build=BUILD/kind;build.mkdir(parents=True,exist_ok=True)
  spec=MAIN/('audit/update11-c/integration-spec.json'if kind=='morrigan'else'audit/update12-a/'+kind+'/integration-spec.json');meta=json.loads(spec.read_text());g,parts=extract(src/(prefix+'_hull.gltf'));oldcount=sum(len(p['i'])for p in parts);hullparts=clipped_morrigan(parts)if kind=='morrigan'else parts;records=[smooth(p)for p in hullparts];save(dest/(prefix+'_hull.gltf'),g.g,hullparts)
  # All material resources already exist in frozen base. Pella emblem image retained verbatim for editable/UI.
  for im in g.g.get('images',[]):
   p=src/im['uri'];target=dest/im['uri'];target.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(p,target)
  frames={}
  for i,p in enumerate(hullparts):
   p=copy.deepcopy(p);p['v'][:,2]*=-1;p['n'][:,2]*=-1;p['t'][:,2]*=-1;p['t'][:,3]*=-1;frames[str(i)]={k:p[k].tolist()for k in ['v','n','t','uv']}
  write(dest/'retained-source-frames.json',{'hull':frames})
  eg,ep=extract(src/(prefix+'_editable.gltf'));newedit=[]
  for p in hullparts:
   p=copy.deepcopy(p);p['v'][:,2]*=-1;p['n'][:,2]*=-1;p['t'][:,2]*=-1;p['t'][:,3]*=-1;newedit.append(p)
  # Editable hull slots match source materials; remaining primitives are actual mounted turrets.
  newedit.extend(ep[len(parts):]);save(dest/(prefix+'_editable.gltf'),eg.g,newedit)
  for im in eg.g.get('images',[]):
   p=src/im['uri'];target=dest/im['uri'];target.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(p,target)
  newcount=sum(len(p['i'])for p in hullparts);meta['counts']['hull']=newcount;meta['assembled_triangle_total']+=newcount-oldcount;meta['game_directory']=str(build/'game');meta['editable_source']=str(dest/(prefix+'_editable.gltf'));meta['status']='PENDING COMPILATION';write(aud/'integration-spec.json',meta)
  rec={'source':str(src),'input_hashes':{str(p):hashlib.sha256(p.read_bytes()).hexdigest()for p in [src/(prefix+'_hull.gltf'),src/(prefix+'_hull.bin'),src/(prefix+'_editable.gltf'),src/(prefix+'_editable.bin')]},'before_triangles':oldcount,'after_triangles':newcount,'geometry_change':'Only planar clipping for Morrigan paint boundaries; surface and silhouette unchanged'if kind=='morrigan'else'None: exact positions, indices and UVs preserved','normal_policy':'Area-weighted 25 degree corner crease; no cross-material smoothing','diagnostics':records,'runtime':'NOT RUN'};write(aud/'shading-and-paint.json',rec);print(kind,oldcount,newcount,records,flush=True)
