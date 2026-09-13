"""Preserve actual user-supplied Amun-Ra and isolate its authored torpedo subtree.
No game statistics, entity files, installed assets, or prior Donnager outputs edited.
"""
from pathlib import Path
import argparse,copy,hashlib,json,subprocess,zipfile
import numpy as np
from PIL import Image,ImageDraw,ImageFont
from common import Gltf,read_mesh
from polish_ui import render
ROOT=Path(__file__).resolve().parents[1];ASSETS=ROOT/'assets/derived/amun05-c';AUDIT=ROOT/'audit/amun05-c';BUILD=ROOT/'build/amun05-c'
GAME=Path('/run/media/haker/NVME 2/SteamLibrary/steamapps/common/Sins2')
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def write(p,d):p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(d,indent=2)+'\n')
def preserve(p,data):
 p.parent.mkdir(parents=True,exist_ok=True)
 if p.exists():
  if p.read_bytes()!=data:raise ValueError('Refusing overwrite of preserved source: '+str(p))
 else:p.write_bytes(data)
def descendants(g,i):
 result=[i]
 for c in g.g['nodes'][i].get('children',[]):result+=descendants(g,c)
 return result
def geometry(g,root=None):
 inv=np.linalg.inv(g.world[root])if root is not None else np.eye(4)
 for i in descendants(g,root)if root is not None else g.world:
  n=g.g['nodes'][i]
  if 'mesh'not in n:continue
  for pi,p in enumerate(g.g['meshes'][n['mesh']]['primitives']):
   assert p.get('mode',4)==4
   v=g.positions(i,p);v=v@inv[:3,:3].T+inv[:3,3];ix=g.accessor(p['indices']).reshape(-1,3);yield i,pi,p,v,ix

def summary(g,i=None):
 rows=list(geometry(g,i));v=np.concatenate([x[3]for x in rows]);return {'root_node':i,'name':g.g['nodes'][i].get('name')if i is not None else'all_active_scene','mesh_nodes':[x[0]for x in rows],'triangles':sum(len(x[4])for x in rows),'bounds_in_root_local_frame':{'min':v.min(0).tolist(),'max':v.max(0).tolist(),'dimensions':np.ptp(v,axis=0).tolist()},'root_world_matrix':g.world[i].tolist()if i is not None else None,'descendants':descendants(g,i)if i is not None else list(g.world)}
def render_rows(g,root,target_length=None):
 rows=list(geometry(g,root));vs=np.concatenate([x[3]for x in rows]);center=(vs.min(0)+vs.max(0))/2;factor=target_length/np.ptp(vs,axis=0)[2]if target_length else 1;meshes=[];textures={}
 for i,pi,p,v,ix in rows:
  mat=g.g['materials'][p['material']];pbr=mat['pbrMetallicRoughness'];tex=g.g['textures'][pbr['baseColorTexture']['index']];uri=g.g['images'][tex['source']]['uri'];path=g.path.parent/uri
  if path not in textures:textures[path]=np.array(Image.open(path).convert('RGBA'))
  uv=g.accessor(p['attributes']['TEXCOORD_0'])[ix];meshes.append((((v-center)*factor)[ix],uv,textures[path],pbr.get('baseColorFactor',[1,1,1,1]),mat.get('alphaMode','OPAQUE')))
 return meshes

def main():
 ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('--archive',type=Path,default=Path('/home/haker/Downloads/Amun-Ra_Class_Stealth_Ship_[The_Expanse].zip'));ap.add_argument('--target-length',type=float,default=16.510756);a=ap.parse_args()
 if not a.archive.is_file():raise FileNotFoundError('Required supplied Amun-Ra archive missing; no asset checks run: '+str(a.archive))
 for d in [ASSETS,AUDIT,BUILD]:d.mkdir(parents=True,exist_ok=True)
 arc=ASSETS/'original'/a.archive.name;preserve(arc,a.archive.read_bytes());master=ASSETS/'master'
 with zipfile.ZipFile(arc)as z:
  assert z.testzip()is None,'Archive CRC failure'
  for info in z.infolist():
   if info.is_dir():continue
   p=master/info.filename
   if not p.resolve().is_relative_to(master.resolve()):raise ValueError('Unsafe archive member')
   if (info.external_attr>>16)&0o170000==0o120000:raise ValueError('Archive symlink unsupported')
   preserve(p,z.read(info))
 lock={str(p.relative_to(master)):sha(p)for p in sorted(master.rglob('*'))if p.is_file()};write(AUDIT/'source-hashes.json',{'supplied_archive':str(a.archive),'archive_sha256':sha(arc),'archive_copy':str(arc),'master':str(master),'master_hashes':lock})
 g=Gltf(next(master.glob('*.gltf')));top=g.g['nodes'][2]['children'];torps=[i for i in top if g.g['nodes'][i]['name'].startswith('Torpedo_LP')];pdcs=[i for i in top if g.g['nodes'][i]['name'].startswith('Turret_Pad_LP')];pods=[i for i in top if g.g['nodes'][i]['name'].startswith('Breaching_Pod_LP')];assert torps==[102,107,112,117]and pdcs==[892,910,928,946]
 inventory={'asset':g.g['asset'],'file_formats':['glTF2 JSON + external BIN','PNG atlases','JPEG background'],'source_text_license_present':False,'creator':'Not identified in archive metadata','node_count':len(g.g['nodes']),'active_nodes':len(g.world),'mesh_count':len(g.g['meshes']),'material_count':len(g.g['materials']),'animations':len(g.g.get('animations',[])),'skins':len(g.g.get('skins',[])),'whole_scene':summary(g),'central_hull_only':summary(g,3),'top_groups':[summary(g,i)for i in top],'torpedo_roots':torps,'PDC_roots':pdcs,'breaching_pod_roots':pods,'materials':g.g['materials'],'textures':g.g['textures'],'images':[],'hierarchy':g.g['nodes'],'mesh_rows':[],'axes_and_scale':'Global scene has presentation transform and 100x FBX scaling; detached equipment makes scene bounds unsuitable for ship size. Torpedo extraction cancels complete ancestor/instance transform and uses the authored subtree local frame.'}
 for im in g.g['images']:
  p=master/im['uri']
  with Image.open(p)as image:inventory['images'].append({'definition':im,'dimensions':list(image.size),'mode':image.mode,'bytes':p.stat().st_size,'sha256':sha(p)})
 for i,pi,p,v,ix in geometry(g):
  assert np.isfinite(v).all()and ix.min()>=0 and ix.max()<len(v)
  inventory['mesh_rows'].append({'node':i,'primitive':pi,'triangles':len(ix),'vertices':len(v),'attributes':list(p['attributes']),'material':p['material']})
 write(AUDIT/'inventory.json',inventory)
 # All four exact torpedo local meshes are compared before selecting first instance.
 sigs=[]
 for ti in torps:
  h=hashlib.sha256()
  for i,pi,p,v,ix in geometry(g,ti):
   # Floating roundoff from inverse root transforms is excluded via original data;
   # all descendants of each torpedo are identity wrappers in this source.
   for key,aid in sorted(p['attributes'].items()):h.update(key.encode());h.update(g.accessor(aid).tobytes())
   h.update(ix.tobytes())
  sigs.append(h.hexdigest())
 assert len(set(sigs))==1,'Source torpedo instances differ; choose explicitly'
 root=torps[0];rows=list(geometry(g,root));vs=np.concatenate([x[3]for x in rows]);lo=vs.min(0);hi=vs.max(0);center=(lo+hi)/2;factor=a.target_length/(hi[2]-lo[2]);assert hi[2]-lo[2]>max(hi[0]-lo[0],hi[1]-lo[1])
 # Compact torpedo only, preserving both original mesh chunks and all UV/tangents.
 out=ASSETS/'torpedo-editable';out.mkdir(exist_ok=True);gg={'asset':{'version':'2.0','generator':'amun05_intake.py; exact subtree isolation and uniform size normalization'},'scene':0,'scenes':[{'nodes':[0]}],'nodes':[{'name':'amun05_torpedo_Javelis_length_EDITABLE','children':[]}],'meshes':[],'materials':copy.deepcopy(g.g['materials']),'textures':copy.deepcopy(g.g['textures']),'images':copy.deepcopy(g.g['images']),'samplers':copy.deepcopy(g.g.get('samplers',[])),'buffers':[],'bufferViews':[],'accessors':[]};blob=bytearray()
 def acc(data,ctype,typ,target):
  data=np.ascontiguousarray(data,dtype='<f4'if ctype==5126 else'<u4');blob.extend(b'\0'*((-len(blob))%4));offset=len(blob);blob.extend(data.tobytes());vi=len(gg['bufferViews']);gg['bufferViews'].append({'buffer':0,'byteOffset':offset,'byteLength':data.nbytes,'target':target});ai=len(gg['accessors']);spec={'bufferView':vi,'byteOffset':0,'componentType':ctype,'count':len(data),'type':typ}
  if typ=='VEC3':spec.update(min=data.min(0).tolist(),max=data.max(0).tolist())
  gg['accessors'].append(spec);return ai
 for i,pi,p,v,ix in rows:
  attrs={'POSITION':acc((v-center)*factor,5126,'VEC3',34962)}
  for key,aid in p['attributes'].items():
   if key=='POSITION':continue
   data=g.accessor(aid);attrs[key]=acc(data,5126,{2:'VEC2',3:'VEC3',4:'VEC4'}[data.shape[1]],34962)
  mi=len(gg['meshes']);gg['meshes'].append({'name':g.g['nodes'][i]['name'],'primitives':[{'mode':4,'material':p['material'],'indices':acc(ix.reshape(-1),5125,'SCALAR',34963),'attributes':attrs}]});ni=len(gg['nodes']);gg['nodes'].append({'name':g.g['nodes'][i]['name'],'mesh':mi});gg['nodes'][0]['children'].append(ni)
 for im in gg['images']:preserve(out/im['uri'],(master/im['uri']).read_bytes())
 (out/'amun05_torpedo.bin').write_bytes(blob);gg['buffers']=[{'uri':'amun05_torpedo.bin','byteLength':len(blob)}];write(out/'amun05_torpedo.gltf',gg)
 installed=GAME/'meshes/trader_medium_torpedo.mesh'
 if not installed.is_file():raise FileNotFoundError('Required installed Javelis mesh missing: '+str(installed))
 stock=read_mesh(installed);stocklength=2*stock['box'][5];assert abs(stocklength-a.target_length)<1e-5,'Requested length differs from installed Javelis'
 torp={'selected_root':root,'selected_mesh_nodes':[x[0]for x in rows],'selected_source_meshes':[g.g['nodes'][x[0]]['mesh']for x in rows],'same_geometry_and_attributes_all_four_instances':True,'instance_attribute_hashes':sigs,'source_local_bounds':{'min':lo.tolist(),'max':hi.tolist(),'dimensions':(hi-lo).tolist()},'source_local_center':center.tolist(),'uniform_factor':float(factor),'target_length':a.target_length,'target_dimensions':((hi-lo)*factor).tolist(),'coordinate_convention':'Right-handed glTF, local+Z long axis, no compiler handedness conversion applied. Source+Z end is the narrow nose; verify against preview before integration.','game_entity_changes':[],'health_damage_motion_ammo_changes':'NONE','output_scene':str(out/'amun05_torpedo.gltf'),'dependencies':{str(p):sha(p)for p in sorted(out.rglob('*'))if p.is_file()},'installed_size_reference':{'path':str(installed),'sha256':sha(installed),'full_length':stocklength,'box':stock['box'],'sphere':stock['sphere']},'next_integration':'Convert using existing verified compiler convention. Map atlas channels to verified game shader channels; these source textures are not already game-ready DDS. Use private mesh/material/skin IDs; preserve approved MCRN projectile stats. Bounds/collision choice remains main-owned.'}
 candidate_radius=float(np.linalg.norm(((vs-center)*factor).astype('<f4').astype(float),axis=1).max());torp['candidate_centered_vertex_radius']=candidate_radius;torp['stock_sphere_radius_delta']=candidate_radius-stock['sphere'][3];torp['bounds_note']='Length and shape normalization do not guarantee identical sphere: custom radius is about0.01308 larger than stock. Compiler must calculate private mesh bounds; main explicitly decides spatial collision radius separately from unchanged health.'
 write(AUDIT/'torpedo-extraction.json',torp)
 write(AUDIT/'equipment.json',{'PDC_count':len(pdcs),'requested_three_discrepancy':'Actual source contains four complete geometric assemblies. No assembly silently dropped.','PDCs':[summary(g,i)for i in pdcs],'breaching_pod_count':len(pods),'breaching_pods':[summary(g,i)for i in pods],'torpedo_count':len(torps),'torpedoes':[summary(g,i)for i in torps],'animation_state':'No animations or skins. Authored object hierarchy/rest poses exist; pivots/axes/muzzles need later verification, not runtime-ready.'})
 scene=Gltf(out/'amun05_torpedo.gltf');tr=render_rows(scene,0);right=np.array([.5,0,.8660254]);up=np.array([-.4,.887,.231]);up-=right*np.dot(up,right);up/=np.linalg.norm(up);basis=np.array([right,up,np.cross(right,up)]);portrait=render(tr,(1400,500),basis);portrait.save(AUDIT/'torpedo-isolated-preview.png');side=render(tr,(1400,330),np.array([[0,0,1],[1,0,0],[0,1,0]]));side.save(AUDIT/'torpedo-side-preview.png')
 # Actual complete representative source PDC/pod renders, preserving authored poses.
 panel=Image.new('RGBA',(1400,900),'#101722');d=ImageDraw.Draw(panel)
 for index,(name,ri)in enumerate([('PDC representative: Turret_Pad_LP.003',928),('Breaching pod representative: Breaching_Pod_LP.020',47)]):
  im=render(render_rows(g,ri),(640,660),basis);panel.alpha_composite(im,(30+index*690,80));d.text((30+index*690,30),name,fill='white',font_size=19)
 d.text((30,780),'Actual source object hierarchy; no animation channels or runtime rig test.',fill='white',font_size=20);panel.save(AUDIT/'equipment-preview.png')
 preservation=lock=={str(p.relative_to(master)):sha(p)for p in sorted(master.rglob('*'))if p.is_file()};assert preservation and sha(arc)==sha(a.archive)
 vv=np.concatenate([x[3]for x in geometry(scene)]);assert np.allclose(np.ptp(vv,axis=0)[2],a.target_length,atol=1e-5);assert sum(len(x[4])for x in geometry(scene))==1600
 write(AUDIT/'offline-checks.json',{'status':'PASS','archive_CRC':'PASS','archive_master_hashes_unchanged':preservation,'finite_source_positions_and_indices':'PASS','same_torpedo_geometry_all_instances':'PASS','isolated_torpedo_triangles':1600,'isolated_length':float(np.ptp(vv,axis=0)[2]),'texture_copies_byte_identical':all(sha(out/im['uri'])==sha(master/im['uri'])for im in gg['images']),'runtime':'NOT RUN','compiler_and_game_package':'NOT RUN'})
 print(json.dumps({'status':'PASS','triangles':inventory['whole_scene']['triangles'],'PDCs':len(pdcs),'pods':len(pods),'torpedoes':len(torps),'output':str(out),'archive_sha256':sha(arc)}))
if __name__=='__main__':main()
