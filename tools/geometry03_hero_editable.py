"""Separate normalized editable hero glTFs; never reuse compiler-reflected meshes as edits."""
from common import *
import copy
for variant in ['hero','hero-armed']:
 out=ROOT/'assets/derived/geometry03-b'/variant;stem='expanse03_hero_static' if variant=='hero' else 'expanse03_hero_armed';a=Gltf(out/(stem+'.gltf'));g=copy.deepcopy(a.g);buf=bytearray(a.buffers[0]);done=set()
 def values(ai):
  at=g['accessors'][ai];view=g['bufferViews'][at['bufferView']];size={'SCALAR':1,'VEC2':2,'VEC3':3,'VEC4':4}[at['type']];return np.ndarray((at['count'],size),dtype='<u4' if at['componentType']==5125 else '<f4',buffer=buf,offset=view.get('byteOffset',0)+at.get('byteOffset',0))
 for pr in g['meshes'][0]['primitives']:
  for sem in ['POSITION','NORMAL','TANGENT']:
   ai=pr['attributes'][sem]
   if ai in done:continue
   v=values(ai);v[:,2]*=-1
   if sem=='TANGENT':v[:,3]*=-1
   if sem=='POSITION':g['accessors'][ai].update(min=v.min(0).tolist(),max=v.max(0).tolist())
   done.add(ai)
  v=values(pr['attributes']['POSITION']);n=values(pr['attributes']['NORMAL']);idx=values(pr['indices']).reshape(-1,3);tri=v[idx];dot=np.sum(np.cross(tri[:,1]-tri[:,0],tri[:,2]-tri[:,0])*n[idx].mean(1),axis=1);flip=dot<0;idx[flip]=idx[flip][:,[0,2,1]]
 for node in g['nodes'][1:]:
  node['translation'][2]*=-1
  if 'rotation' in node:node['rotation'][0]*=-1;node['rotation'][1]*=-1
 g['asset']['generator']='Normalized editable static hero; not direct compiler input; master preserved';file=stem+'_editable.bin';g['buffers'][0]['uri']=file;(out/file).write_bytes(buf);write(out/(stem+'_editable.gltf'),g)
 print(stem,'editable prepared')
