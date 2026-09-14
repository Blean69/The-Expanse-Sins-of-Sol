"""Prepare an isolated Foehammer geometry prototype; no gameplay or installation.
Uses the unchanged editable Donnager rail and two existing PDC rigs. The new
support structure is mod-original. Source stays in game coordinates (+Z fore).
"""
from pathlib import Path
import copy,json,hashlib,sys
import numpy as np
from common import Gltf
ROOT=Path(__file__).resolve().parents[1]
SOURCE=Path('/run/media/haker/NVME 2/expanse-workers/tachi-one-pdc/assets/derived/update11-b/update11_donnager_editable.gltf')
OUT=ROOT/'assets/derived/update20-foehammer';AUD=ROOT/'audit/update20-assets';OUT.mkdir(parents=True,exist_ok=True);AUD.mkdir(parents=True,exist_ok=True)
a=Gltf(SOURCE);g=copy.deepcopy(a.g);g.update(nodes=[],meshes=[],buffers=[],bufferViews=[],accessors=[],scenes=[{'nodes':[]}],scene=0);g['asset']={'version':'2.0','generator':'Sins of Sol Foehammer private geometry prototype; preserved donor dimensions and pivots'}
# Preserve exact material bindings with local, explicit regular-file copies only.
used=set()
for mesh in a.g['meshes']:
 if mesh['name'] in ['donnager_rail_0','donnager_pdc_base','donnager_pdc_barrel']:
  used.update(p['material'] for p in mesh['primitives'])
textures=set()
def indices(o):
 if isinstance(o,dict):
  for k,v in o.items():
   if k.endswith('Texture') and isinstance(v,dict) and 'index'in v:textures.add(v['index'])
   else:indices(v)
 elif isinstance(o,list):
  for v in o:indices(v)
for mi in used:indices(g['materials'][mi])
images={g['textures'][ti]['source'] for ti in textures};dependencies=[]
for ii in images:
 p=(SOURCE.parent/g['images'][ii]['uri']).resolve();assert p.is_file() and not p.is_symlink();name=f'donor_{ii}{p.suffix}';(OUT/name).write_bytes(p.read_bytes());g['images'][ii]['uri']=name;dependencies.append({'path':str(p),'sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'copy':name})
# Unused images are removed and remaining references remapped.
imap={x:i for i,x in enumerate(sorted(images))};tmap={x:i for i,x in enumerate(sorted(textures))}
g['images']=[g['images'][x] for x in sorted(images)];g['textures']=[dict(g['textures'][x],source=imap[g['textures'][x]['source']]) for x in sorted(textures)]
materials=[];mmap={}
for mi in sorted(used):
 m=copy.deepcopy(g['materials'][mi]);mmap[mi]=len(materials)
 def remap(o):
  if isinstance(o,dict):
   for k,v in o.items():
    if k.endswith('Texture') and isinstance(v,dict) and 'index'in v:v['index']=tmap[v['index']]
    else:remap(v)
  elif isinstance(o,list):
   for v in o:remap(v)
 remap(m);materials.append(m)
g['materials']=materials;buf=bytearray()
def acc(v,typ,ct=5126):
 v=np.asarray(v,dtype='<u4' if ct==5125 else '<f4');buf.extend(b'\0'*((-len(buf))%4));o=len(buf);buf.extend(v.tobytes());g['bufferViews'].append({'buffer':0,'byteOffset':o,'byteLength':v.nbytes});d={'bufferView':len(g['bufferViews'])-1,'componentType':ct,'count':len(v),'type':typ}
 if typ=='VEC3':d.update(min=v.min(0).tolist(),max=v.max(0).tolist())
 g['accessors'].append(d);return len(g['accessors'])-1
meshids={};source_counts={}
for mesh in a.g['meshes']:
 if mesh['name'] not in ['donnager_rail_0','donnager_pdc_base','donnager_pdc_barrel']:continue
 m={'name':mesh['name'],'primitives':[]};ntri=0
 for p in mesh['primitives']:
  idx=a.accessor(p['indices']).reshape(-1);attrs={k:acc(a.accessor(v),{'POSITION':'VEC3','NORMAL':'VEC3','TANGENT':'VEC4','TEXCOORD_0':'VEC2'}[k]) for k,v in p['attributes'].items()};m['primitives'].append({'mode':4,'material':mmap[p['material']],'attributes':attrs,'indices':acc(idx,'SCALAR',5125)});ntri+=len(idx)//3
 meshids[mesh['name']]=len(g['meshes']);g['meshes'].append(m);source_counts[mesh['name']]=ntri
# Mechanical platform: central machinery vault, frame outriggers, recoil cradle.
tris=[]
def box(lo,hi):
 lo=np.array(lo);hi=np.array(hi);v=np.array([[x,y,z] for x in [lo[0],hi[0]] for y in [lo[1],hi[1]] for z in [lo[2],hi[2]]]);ids=np.array([[0,1,3],[0,3,2],[4,6,7],[4,7,5],[0,4,5],[0,5,1],[2,3,7],[2,7,6],[0,2,6],[0,6,4],[1,5,7],[1,7,3]])
 # ensure outward winding independently of face lookup order
 t=v[ids];n=np.cross(t[:,1]-t[:,0],t[:,2]-t[:,0]);flip=np.sum(n*(t.mean(1)-(lo+hi)/2),axis=1)<0;t[flip]=t[flip][:,[0,2,1]];tris.extend(t)
box([-39,-50,-66],[39,-25,56]);box([-70,-39,-38],[70,-26,-15]);box([-60,-43,28],[60,-27,43]);box([-14,-25,-25],[14,-17,21])
for x in [-32,27]:
 for z in [-55,-22,11,40]:box([x,-25,z],[x+5,-21,z+9])
for x in [-57,42]:box([x,-46,-60],[x+15,-25,-39])
t=np.array(tris,dtype=float);n=np.cross(t[:,1]-t[:,0],t[:,2]-t[:,0]);n/=np.linalg.norm(n,axis=1,keepdims=True);v=t.reshape(-1,3);normal=np.repeat(n,3,axis=0);uv=v[:,[0,2]]/30;tan=np.tile([1.,0,0,1],(len(v),1));tan[np.abs(normal[:,0])>.5,:3]=[0,0,1];mat=len(g['materials']);g['materials'].append({'name':'expanse20_foehammer_support','pbrMetallicRoughness':{'baseColorFactor':[.12,.145,.17,1],'metallicFactor':.7,'roughnessFactor':.72}});meshids['support']=len(g['meshes']);g['meshes'].append({'name':'support','primitives':[{'mode':4,'material':mat,'attributes':{'POSITION':acc(v,'VEC3'),'NORMAL':acc(normal,'VEC3'),'TANGENT':acc(tan,'VEC4'),'TEXCOORD_0':acc(uv,'VEC2')},'indices':acc(np.arange(len(v)),'SCALAR',5125)}]})
def node(kind,pos,rot=[0,0,0,1],name=None):
 g['scenes'][0]['nodes'].append(len(g['nodes']));g['nodes'].append({'name':name or kind,'mesh':meshids[kind],'translation':pos,'rotation':rot})
node('support',[0,0,0]);node('donnager_rail_0',[0,0,0]);pdcs=[]
for s in [-1,1]:
 yaw=[s*71,-31,-26];rotation=[0,0,-s*2**-.5,2**-.5];pitch=[s*(71+1.3764509954),-31,-26+.1873080402];node('donnager_pdc_base',yaw,rotation);node('donnager_pdc_barrel',pitch,rotation);pdcs.append({'yaw_pivot':yaw,'pitch_pivot':pitch,'rotation_quaternion':rotation,'outward_up':[s,0,0],'forward':[0,0,1]})
g['buffers']=[{'uri':'foehammer_orbital_editable.bin','byteLength':len(buf)}];(OUT/'foehammer_orbital_editable.bin').write_bytes(buf);(OUT/'foehammer_orbital_editable.gltf').write_text(json.dumps(g,indent=2)+'\n')
weapon=Path('/run/media/haker/NVME 2/expanse-mod/build/experiments/expanse_update19/entities/expanse10_donnager_rail_0.weapon');w=json.loads(weapon.read_text());report={'status':'isolated editable art only; NOT compiled, installed, or runtime tested','source':str(SOURCE),'source_sha256':hashlib.sha256(SOURCE.read_bytes()).hexdigest(),'source_counts':source_counts,'support_triangles':len(t),'assembled_triangles':source_counts['donnager_rail_0']+2*(source_counts['donnager_pdc_base']+source_counts['donnager_pdc_barrel'])+len(t),'coordinate_system':'+Z forward, +Y up; no compiler reflection','rail_pivot':[0,0,0],'rail_muzzle':[-.5371823312843844,-.000014835910375669655,148.10427678298808],'pdc_mounts':pdcs,'dependencies':dependencies,'reference_weapon':str(weapon),'reference_weapon_sha256':hashlib.sha256(weapon.read_bytes()).hexdigest(),'reference_weapon_values':w,'gameplay_caveat':'Stage3 integrator must preserve weapon fields and validate platform arcs. Existing donor rail has zero pitch speed; do not promise high/low tracking without separately deciding supported structure geometry/rotation. There is no station unit, local cap, ability or game behavior in this art-only deliverable.'}
(AUD/'foehammer-art-prototype.json').write_text(json.dumps(report,indent=2)+'\n');print(report['assembled_triangles'])
