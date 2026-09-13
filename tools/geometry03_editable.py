"""Separate editable six-rig assembly; does not touch compiler or game files."""
from common import *
import copy
out=ROOT/'assets/derived/geometry03-b/corvette';meta=read(ROOT/'audit/geometry03-b/mount-metadata.json');normalized=read(Path(meta['source_root'])/'assets/derived/baseline/mcrn_editable.gltf');g={'asset':{'version':'2.0','generator':'Editable six-PDC assembly; direct compiler import is not supported'},'scene':0,'scenes':[{'nodes':[0]}],'nodes':[],'meshes':[],'buffers':[],'bufferViews':[],'accessors':[],'materials':copy.deepcopy(normalized['materials']),'images':copy.deepcopy(normalized['images']),'textures':copy.deepcopy(normalized['textures']),'samplers':copy.deepcopy(normalized.get('samplers',[]))};lookup={m['name'].lower():i for i,m in enumerate(g['materials'])};nodeids={}
for im in g['images']:im['uri']=str((Path(meta['source_root'])/'assets/derived/baseline')/im['uri'])
for kind,frame in meta['frames'].items():
 name='expanse03_'+kind;a=Gltf(out/(name+'.gltf'));d=copy.deepcopy(a.g);buf=bytearray(a.buffers[0]);meshi=len(g['meshes']);mesh={'name':kind,'primitives':[]};bufi=len(g['buffers']);view_offset=len(g['bufferViews']);acc_offset=len(g['accessors'])
 for pr in d['meshes'][0]['primitives']:
  for sem in ['POSITION','NORMAL','TANGENT']:
   at=d['accessors'][pr['attributes'][sem]];vw=d['bufferViews'][at['bufferView']];width=4 if sem=='TANGENT' else 3;v=np.ndarray((at['count'],width),dtype='<f4',buffer=buf,offset=vw['byteOffset']);v[:,2]*=-1
   if sem=='TANGENT':v[:,3]*=-1
   if sem=='POSITION':at.update(min=v.min(0).tolist(),max=v.max(0).tolist())
  pp=d['accessors'][pr['attributes']['POSITION']];np_=d['accessors'][pr['attributes']['NORMAL']];v=np.ndarray((pp['count'],3),dtype='<f4',buffer=buf,offset=d['bufferViews'][pp['bufferView']]['byteOffset']);n=np.ndarray((np_['count'],3),dtype='<f4',buffer=buf,offset=d['bufferViews'][np_['bufferView']]['byteOffset']);at=d['accessors'][pr['indices']];vw=d['bufferViews'][at['bufferView']];idx=np.ndarray((at['count']//3,3),dtype='<u4',buffer=buf,offset=vw['byteOffset']);tri=v[idx];dot=np.sum(np.cross(tri[:,1]-tri[:,0],tri[:,2]-tri[:,0])*n[idx].mean(1),axis=1);flip=dot<0;idx[flip]=idx[flip][:,[0,2,1]]
  matname=d['materials'][pr['material']]['name'].removeprefix('mcrn_tachi_');pr['material']=lookup[matname];pr['indices']+=acc_offset;pr['attributes']={k:x+acc_offset for k,x in pr['attributes'].items()};mesh['primitives'].append(pr)
 for vw in d['bufferViews']:vw['buffer']=bufi;g['bufferViews'].append(vw)
 for at in d['accessors']:at['bufferView']+=view_offset;g['accessors'].append(at)
 file=name+'_editable.bin';(out/file).write_bytes(buf);g['buffers'].append({'uri':file,'byteLength':len(buf)});g['meshes'].append(mesh);nodeids[kind]=len(g['nodes']);g['nodes'].append({'name':kind,'mesh':meshi})
g['nodes'][nodeids['hull']]['children']=[]
for r in meta['rigs']:
 i=r['index'];base=nodeids[f'pdc_{i}_base'];bar=nodeids[f'pdc_{i}_barrel'];M=np.eye(4);M[:3,:3]=r['basis_columns'];M[:3,3]=r['yaw_pivot_hull'];g['nodes'][base]['matrix']=M.T.flatten().tolist();g['nodes'][base]['children']=[bar];g['nodes'][bar]['translation']=r['turret_override']['barrel_position'];g['nodes'][0]['children'].append(base)
write(out/'expanse03_editable.gltf',g);check=Gltf(out/'expanse03_editable.gltf');assert len(check.world)==13;print('Editable13-part assembly prepared with hierarchy and original material/image references')
