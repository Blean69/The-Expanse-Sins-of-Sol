"""Editable13-part hero assembly in game coordinates; separate from compiler input."""
from common import *
import copy
out=ROOT/'assets/derived/amun06-b';meta=read(ROOT/'audit/amun06-b/mount-metadata.json');g={'asset':{'version':'2.0','generator':'Editable13-part hero aiming assembly; not direct compiler input'},'scene':0,'scenes':[{'nodes':[0]}],'nodes':[],'meshes':[],'buffers':[],'bufferViews':[],'accessors':[],'materials':[m['original'] for m in meta['materialspec']]};nodeids={};src=Path('/run/media/haker/NVME 2/expanse-workers/validation/assets/derived/amun05-c/master');original=read(src/'Amun-Ra_Class_Stealth_Ship_[The_Expanse].gltf');g['images']=copy.deepcopy(original['images']);g['textures']=copy.deepcopy(original['textures']);g['samplers']=copy.deepcopy(original.get('samplers',[]))
for im in g['images']:im['uri']=str(src/im['uri'])
for kind,frame in meta['frames'].items():
 a=Gltf(out/('expanse06_'+kind+'.gltf'));d=copy.deepcopy(a.g);buf=bytearray(a.buffers[0]);meshi=len(g['meshes']);mesh={'name':kind,'primitives':[]};bufi=len(g['buffers']);vo=len(g['bufferViews']);ao=len(g['accessors'])
 for pr in d['meshes'][0]['primitives']:
  for sem in ['POSITION','NORMAL','TANGENT']:
   at=d['accessors'][pr['attributes'][sem]];vw=d['bufferViews'][at['bufferView']];width=4 if sem=='TANGENT' else 3;v=np.ndarray((at['count'],width),dtype='<f4',buffer=buf,offset=vw['byteOffset']);v[:,2]*=-1
   if sem=='TANGENT':v[:,3]*=-1
   if sem=='POSITION':at.update(min=v.min(0).tolist(),max=v.max(0).tolist())
  at=d['accessors'][pr['indices']];idx=np.ndarray((at['count']//3,3),dtype='<u4',buffer=buf,offset=d['bufferViews'][at['bufferView']]['byteOffset']);pa=d['accessors'][pr['attributes']['POSITION']];na=d['accessors'][pr['attributes']['NORMAL']];v=np.ndarray((pa['count'],3),dtype='<f4',buffer=buf,offset=d['bufferViews'][pa['bufferView']]['byteOffset']);n=np.ndarray((na['count'],3),dtype='<f4',buffer=buf,offset=d['bufferViews'][na['bufferView']]['byteOffset']);tri=v[idx];flip=np.sum(np.cross(tri[:,1]-tri[:,0],tri[:,2]-tri[:,0])*n[idx].mean(1),axis=1)<0;idx[flip]=idx[flip][:,[0,2,1]]
  pr['material']=0;pr['indices']+=ao;pr['attributes']={k:v+ao for k,v in pr['attributes'].items()};mesh['primitives'].append(pr)
 for vw in d['bufferViews']:vw['buffer']=bufi;g['bufferViews'].append(vw)
 for at in d['accessors']:at['bufferView']+=vo;g['accessors'].append(at)
 filename='expanse06_'+kind+'_editable.bin';(out/filename).write_bytes(buf);g['buffers'].append({'uri':filename,'byteLength':len(buf)});g['meshes'].append(mesh);nodeids[kind]=len(g['nodes']);g['nodes'].append({'name':kind,'mesh':meshi})
g['nodes'][0]['children']=[]
for r in meta['rigs']:
 i=r['index'];base=nodeids[f'amun_pdc_{i}_base'];barrel=nodeids[f'amun_pdc_{i}_barrel'];M=np.eye(4);M[:3,:3]=r['basis_columns'];M[:3,3]=r['yaw_pivot_hull'];g['nodes'][base]['matrix']=M.T.flatten().tolist();g['nodes'][base]['children']=[barrel];g['nodes'][barrel]['translation']=r['turret_override']['barrel_position'];g['nodes'][0]['children'].append(base)
write(out/'expanse06_amun_editable.gltf',g);check=Gltf(out/'expanse06_amun_editable.gltf');assert len(check.world)==7;pod=copy.deepcopy(g);pod['scenes']=[{'nodes':[nodeids['amun_boarding_pod']]}];write(out/'expanse06_pod_editable.gltf',pod);print('Editable7-part ship and separate compact pod prepared')
