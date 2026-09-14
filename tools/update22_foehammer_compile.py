"""Compile only the new Foehammer support mesh; reuse verified gun bytes.
No game install, no original asset mutation, no Wine-prefix copying.
Run from the isolated checkout using the established Python dependency runtime.
"""
from pathlib import Path
import copy, hashlib, json, os, struct, subprocess
import numpy as np
from scipy.spatial import cKDTree
from scipy.spatial.transform import Rotation
from common import Gltf, read, read_mesh, write
ROOT=Path(__file__).resolve().parents[1]
BASE=Path('/run/media/haker/NVME 2/expanse-mod/build/experiments/expanse_update19')
SOURCE=ROOT/'assets/derived/update20-foehammer/foehammer_orbital_editable.gltf'
OUT=ROOT/'assets/derived/update22-foehammer';BUILD=ROOT/'build/update22-foehammer';GAME=BUILD/'game';AUD=ROOT/'audit/update22-foehammer'
SDK=Path('/run/media/haker/NVME 2/SteamLibrary/steamapps/common/Sins of a Solar Empire II - Mod Tools')
WINE=Path('/home/haker/.var/app/com.valvesoftware.Steam/.local/share/Steam/steamapps/common/Proton 10.0/files/bin/wine64')
PREFIX=Path('/run/media/haker/NVME 2/expanse-workers/tachi-one-pdc/build/polish-b/proton-prefix')
NAME='expanse22_foehammer_support'
for p in [SOURCE, SDK/'MeshBuilder/bin/MeshBuilder.exe',WINE,PREFIX]:
 if not p.exists():raise FileNotFoundError(p)
for p in [OUT,BUILD,AUD]:p.mkdir(parents=True,exist_ok=True)
a=Gltf(SOURCE);support=next(m for m in a.g['meshes'] if m['name']=='support');assert len(support['primitives'])==1
p=support['primitives'][0];v=a.accessor(p['attributes']['POSITION']);n=a.accessor(p['attributes']['NORMAL']);t=a.accessor(p['attributes']['TANGENT']);uv=a.accessor(p['attributes']['TEXCOORD_0']);idx=a.accessor(p['indices']).reshape(-1,3)
# Normalize only the new support UVs; donor gun UVs remain byte-identical.
lo=v.min(0);span=np.maximum(v.max(0)-lo,1e-9);uv=np.zeros((len(v),2));t=np.zeros((len(v),4));dominant=np.argmax(np.abs(n),axis=1)
for axis,axes in [(0,(2,1)),(1,(0,2)),(2,(0,1))]:
 mask=dominant==axis;aa,bb=axes;uv[mask,0]=(v[mask,aa]-lo[aa])/span[aa];uv[mask,1]=(v[mask,bb]-lo[bb])/span[bb];t[mask,aa]=1;t[mask,3]=np.where(np.cross(n[mask],t[mask,:3])[:,bb]<0,-1.,1.)
reference={'p':v.copy(),'n':n.copy(),'t':t.copy(),'uv':uv.copy()}
points=[{'name':'center','translation':[0,0,0]},{'name':'above','translation':[0,35,0]},{'name':'aura','translation':[0,-55,0]},{'name':'child.expanse22_foehammer_rail_0','translation':[0,0,0]}]
for s in [-1,1]:points.append({'name':f'child.expanse22_foehammer_pdc_{0 if s<0 else 1}','translation':[s*71,-31,-26],'rotation':[0,0,-s*2**-.5,2**-.5]})
g={'asset':{'version':'2.0','generator':'Foehammer support; official MeshBuilder Z compensation'},'scene':0,'scenes':[{'nodes':[0]}],'nodes':[{'name':NAME,'mesh':0,'children':[]}],'meshes':[{'name':NAME,'primitives':[]}],'materials':[{'name':'support_mat','pbrMetallicRoughness':{'baseColorFactor':[1,1,1,1]}}],'buffers':[],'bufferViews':[],'accessors':[]};buf=bytearray()
def acc(x,typ,ct=5126):
 x=np.asarray(x,dtype='<u4' if ct==5125 else '<f4');buf.extend(b'\0'*((-len(buf))%4));off=len(buf);buf.extend(x.tobytes());g['bufferViews'].append({'buffer':0,'byteOffset':off,'byteLength':x.nbytes});d={'bufferView':len(g['bufferViews'])-1,'componentType':ct,'count':len(x),'type':typ}
 if typ=='VEC3':d.update(min=x.min(0).tolist(),max=x.max(0).tolist())
 g['accessors'].append(d);return len(g['accessors'])-1
for x in [v,n,t]:x[:,2]*=-1
t[:,3]*=-1
g['meshes'][0]['primitives']=[{'mode':4,'material':0,'indices':acc(idx.reshape(-1),'SCALAR',5125),'attributes':{'POSITION':acc(v,'VEC3'),'NORMAL':acc(n,'VEC3'),'TANGENT':acc(t,'VEC4'),'TEXCOORD_0':acc(uv,'VEC2')}}]
for pt in points:
 q=copy.deepcopy(pt);q['translation'][2]*=-1
 if 'rotation'in q:q['rotation'][0]*=-1;q['rotation'][1]*=-1
 g['nodes'][0]['children'].append(len(g['nodes']));g['nodes'].append(q)
g['buffers']=[{'uri':NAME+'.bin','byteLength':len(buf)}];write(OUT/(NAME+'.gltf'),g);(OUT/(NAME+'.bin')).write_bytes(buf)
env=dict(os.environ,WINEPREFIX=str(PREFIX),OMP_NUM_THREADS='4',MANGOHUD='0',WINEDEBUG='-all',DISPLAY='',WINEDLLOVERRIDES='mscoree,mshtml=')
def compile(fmt,suffix=''):
 dest=BUILD/('compiler-'+fmt);dest.mkdir(exist_ok=True)
 with (BUILD/(NAME+suffix+'-'+fmt+'.log')).open('w') as log:
  subprocess.run([str(WINE),str(SDK/'MeshBuilder/bin/MeshBuilder.exe'),'--input_path=Z:'+str(OUT/(NAME+'.gltf')),'--output_folder_path=Z:'+str(dest),'--mesh_output_format='+fmt,'--fill_triangle_facing_grid'],env=env,stdout=log,stderr=subprocess.STDOUT,check=True,timeout=300)
compile('json');m=read(BUILD/'compiler-json'/(NAME+'.mesh_json'));vv=np.array([q['p'] for q in m['non_skinned_vertices']]);nn=np.array([q['n'] for q in m['non_skinned_vertices']]);ii=np.array(m['vertex_indices']).reshape(-1,3);cross=np.cross(vv[ii[:,1]]-vv[ii[:,0]],vv[ii[:,2]]-vv[ii[:,0]]);flip=np.sum(cross*nn[ii].mean(1),axis=1)<0
assert len(flip)==len(idx)
if flip.any():
 b=bytearray((OUT/(NAME+'.bin')).read_bytes());ix=g['accessors'][g['meshes'][0]['primitives'][0]['indices']];view=g['bufferViews'][ix['bufferView']];aidx=np.ndarray((ix['count']//3,3),dtype='<u4',buffer=b,offset=view['byteOffset']);aidx[flip]=aidx[flip][:,[0,2,1]];(OUT/(NAME+'.bin')).write_bytes(b);compile('json','-winding')
compile('binary');m=read(BUILD/'compiler-json'/(NAME+'.mesh_json'));bp=BUILD/'compiler-binary'/(NAME+'.mesh');original=bp.read_bytes();b=bytearray(original);count=struct.unpack_from('<Q',b,53)[0];off=61;binary=[];tangent_offsets=[]
for _ in range(count):
 vals=struct.unpack_from('<12f?',b,off);binary.append(vals[:-1]);tangent_offsets.append(off+24);off+=49+(8 if vals[-1] else 0)
binary=np.array(binary);features=np.concatenate([binary[:,:6],binary[:,10:12]],axis=1);lookup=np.concatenate([reference['p'],reference['n'],reference['uv']],axis=1);distance,match=cKDTree(lookup).query(features);assert distance.max()<2e-4
# Tangent-only replacement preserves official index/facing/opaque trailer bytes.
tang=reference['t'][match].copy();norm=binary[:,3:6];tang[:,:3]-=norm*np.sum(norm*tang[:,:3],axis=1,keepdims=True);tang[:,:3]/=np.linalg.norm(tang[:,:3],axis=1,keepdims=True);allowed=np.zeros(len(b),dtype=bool)
for i,pos in enumerate(tangent_offsets):struct.pack_into('<4f',b,pos,*tang[i]);allowed[pos:pos+16]=True
assert np.all((np.frombuffer(original,dtype='u1')==np.frombuffer(b,dtype='u1'))|allowed)
info=read_mesh(bp);prefix=info['parsed_prefix_bytes'];assert b[prefix:]==original[prefix:]
ix=np.array(m['vertex_indices']).reshape(-1,3);vv=binary[:,:3];nn=binary[:,3:6];cross=np.cross(vv[ix[:,1]]-vv[ix[:,0]],vv[ix[:,2]]-vv[ix[:,0]]);opposed=int((np.sum(cross*nn[ix].mean(1),axis=1)<-1e-5).sum());assert opposed==0
for actual,expected in zip(info['meshpoints'],points):
 assert actual['name']==expected['name'] and np.allclose(actual['position'],expected['translation'],atol=2e-5)
 assert np.allclose(np.array(actual['rotation']).reshape(3,3),Rotation.from_quat(expected.get('rotation',[0,0,0,1])).as_matrix().T,atol=2e-5)
(GAME/'meshes').mkdir(parents=True,exist_ok=True);(GAME/'meshes'/(NAME+'.mesh')).write_bytes(b)
# Private file aliases with exact accepted donor bytes and exact donor materials.
donors={'expanse22_foehammer_rail':'expanse11_donnager_rail_0','expanse22_foehammer_pdc_base':'expanse10_donnager_pdc_base','expanse22_foehammer_pdc_barrel':'expanse10_donnager_pdc_barrel'};source_hashes={};materials=set();hashfile=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
for new,old in donors.items():
 source=BASE/'meshes'/(old+'.mesh');assert source.is_file() and not source.is_symlink();dest=GAME/'meshes'/(new+'.mesh');dest.write_bytes(source.read_bytes());source_hashes[str(source)]=hashfile(source);materials.update(read_mesh(source)['materials'])
# Support uses a private alias of accepted opaque gray industrial Donnager material.
base_material=BASE/'mesh_materials/expanse11_donnager_rail_0_expanse11_donnager_mat_1.mesh_material';support_material=m['materials'][0]
(GAME/'mesh_materials').mkdir(exist_ok=True);write(GAME/'mesh_materials'/(support_material+'.mesh_material'),read(base_material));source_hashes[str(base_material)]=hashfile(base_material);textures=set()
for name in materials:
 source=BASE/'mesh_materials'/(name+'.mesh_material');assert source.is_file() and not source.is_symlink();(GAME/'mesh_materials'/source.name).write_bytes(source.read_bytes());source_hashes[str(source)]=hashfile(source)
for p in (GAME/'mesh_materials').glob('*.mesh_material'):
 for k,value in read(p).items():
  if k.endswith('_texture'):textures.add(value)
(GAME/'textures').mkdir(exist_ok=True)
for name in textures:
 source=BASE/'textures'/(name+'.dds');assert source.is_file() and not source.is_symlink();(GAME/'textures'/source.name).write_bytes(source.read_bytes());source_hashes[str(source)]=hashfile(source)
prior=read(ROOT/'audit/update20-assets/foehammer-art-prototype.json');source_rig=read('/run/media/haker/NVME 2/expanse-workers/tachi-one-pdc/audit/update11-b/mount-metadata.json')['rigs'][0]['turret_override'];turret=copy.deepcopy(source_rig);turret.update(biaxial_base_mesh='expanse22_foehammer_pdc_base',biaxial_barrel_mesh='expanse22_foehammer_pdc_barrel')
rigs=[{'kind':'rail','mesh_point':'child.expanse22_foehammer_rail_0','position':[0,0,0],'up':[0,1,0],'forward':[0,0,1],'yaw_arc':{'min_angle':-2.,'max_angle':2.},'pitch_arc':{'min_angle':0.,'max_angle':0.},'turret_override':{'type':'gimbal','gimbal_mesh':'expanse22_foehammer_rail','muzzle_positions':[prior['rail_muzzle']]}}]
for j,pt in enumerate(points[-2:]):
 s=-1 if j==0 else 1;rigs.append({'kind':'pdc','mesh_point':pt['name'],'position':pt['translation'],'up':[s,0,0],'forward':[0,0,1],'yaw_arc':{'min_angle':-180.,'max_angle':180.},'pitch_arc':{'min_angle':-85.,'max_angle':0.},'turret_override':turret})
world=[]
for ni,node in enumerate(a.g['nodes']):
 for p in a.g['meshes'][node['mesh']]['primitives']:world.append(a.positions(ni,p))
world=np.concatenate(world);lo=world.min(0);hi=world.max(0);center=(hi+lo)/2
report={'status':'OFFLINE COMPILED ASSET CHECKS PASS; RUNTIME NOT RUN','source_editable':str(SOURCE),'source_editable_sha256':hashfile(SOURCE),'output_game':str(GAME),'base_mesh':NAME,'aliases':[NAME,*donors],'rigs':rigs,'counts':{'support':len(idx),'rail':8519,'pdc_base':138,'pdc_barrel':539,'assembled':10041},'spatial':{'box':{'center':center.tolist(),'extents':((hi-lo)/2).tolist()},'radius':float(np.linalg.norm(world-center,axis=1).max())},'meshpoints':info['meshpoints'],'checks':{'meshpoint_position_and_rotation_match':True,'source_frame_error':float(distance.max()),'opposed_winding_triangles':opposed,'only_tangent_fields_repaired':True,'opaque_trailer_unchanged':True,'initial_winding_flips':int(flip.sum()),'donor_game_bytes_unchanged':True},'source_game_hashes':source_hashes,'files':{str(p.relative_to(GAME)):hashfile(p) for p in sorted(GAME.rglob('*')) if p.is_file()},'reference_weapon':prior['reference_weapon_values'],'limitations':['Rail preserves zero pitch speed and donor narrow yaw arc; stationary elevation blindspots remain.','No shared gameplay, unit, build limit or infrastructure definition supplied.','PDC negative pitch follows existing native outward rig convention; runtime aiming not tested.','Firing/destruction effects and multiplayer are not tested.'],'wine_prefix_used_in_place':str(PREFIX),'wine_prefix_copied':False}
write(AUD/'integration-spec.json',report);print(json.dumps({'game':str(GAME),'files':len(report['files']),'checks':report['checks']}))
