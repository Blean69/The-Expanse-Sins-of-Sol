"""Official MeshBuilder compile with retained tangents and verified opaque trailers."""
from pathlib import Path
import sys,os,subprocess,struct,hashlib,copy
import numpy as np
from scipy.spatial import cKDTree
from scipy.spatial.transform import Rotation
MAIN=Path('/run/media/haker/NVME 2/expanse-mod');sys.path.insert(0,str(MAIN/'tools'))
from common import Gltf,read,write,read_mesh
from PIL import Image
ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'assets/derived/update24-storm';BUILD=ROOT/'build/update24-storm';GAME=BUILD/'game';AUD=ROOT/'audit/update24-storm';BASE=MAIN/'build/experiments/expanse_update20'
SDK=Path('/run/media/haker/NVME 2/SteamLibrary/steamapps/common/Sins of a Solar Empire II - Mod Tools');WINE=Path('/home/haker/.var/app/com.valvesoftware.Steam/.local/share/Steam/steamapps/common/Proton 10.0/files/bin/wine64');PREFIX=Path('/run/media/haker/NVME 2/expanse-workers/tachi-one-pdc/build/polish-b/proton-prefix');NAME='expanse24_storm_hull'
env=dict(os.environ,WINEPREFIX=str(PREFIX),OMP_NUM_THREADS='4',MANGOHUD='0',WINEDEBUG='-all',DISPLAY='',WINEDLLOVERRIDES='mscoree,mshtml=')
for d in [GAME/'meshes',GAME/'mesh_materials',GAME/'textures',OUT/'textures',BUILD/'compiler-json',BUILD/'compiler-binary']:d.mkdir(parents=True,exist_ok=True)
def compile(fmt):
 with (BUILD/(NAME+'-'+fmt+'.log')).open('w')as log:subprocess.run([str(WINE),str(SDK/'MeshBuilder/bin/MeshBuilder.exe'),'--input_path=Z:'+str(OUT/(NAME+'.gltf')),'--output_folder_path=Z:'+str(BUILD/('compiler-'+fmt)),'--mesh_output_format='+fmt,'--fill_triangle_facing_grid'],env=env,stdout=log,stderr=subprocess.STDOUT,check=True,timeout=300)
compile('json');m=read(BUILD/'compiler-json'/(NAME+'.mesh_json'));g=Gltf(OUT/(NAME+'.gltf'));buffer=bytearray(g.buffers[0]);vv=np.array([v['p']for v in m['non_skinned_vertices']]);nn=np.array([v['n']for v in m['non_skinned_vertices']]);allidx=np.array(m['vertex_indices']);flips=0
for pp in m['primitives']:
 mat=m['materials'][pp['material_index']];pr=next(p for p in g.g['meshes'][0]['primitives']if mat.endswith('_'+g.g['materials'][p['material']]['name']));ii=allidx[pp['vertex_index_start']:pp['vertex_index_start']+pp['vertex_index_count']].reshape(-1,3);q=np.cross(vv[ii[:,1]]-vv[ii[:,0]],vv[ii[:,2]]-vv[ii[:,0]]);flip=np.sum(q*nn[ii].mean(1),axis=1)<-1e-8;at=g.g['accessors'][pr['indices']];bv=g.g['bufferViews'][at['bufferView']];arr=np.ndarray((at['count']//3,3),dtype='<u4',buffer=buffer,offset=bv.get('byteOffset',0)+at.get('byteOffset',0));sv=g.accessor(pr['attributes']['POSITION']);sv[:,2]*=-1;assert np.allclose(np.sort(sv[arr],axis=1),np.sort(vv[ii],axis=1),atol=4e-5);arr[flip]=arr[flip][:,[0,2,1]];flips+=int(flip.sum())
if flips:(OUT/(NAME+'.bin')).write_bytes(buffer);compile('json')
compile('binary');bp=BUILD/'compiler-binary'/(NAME+'.mesh');original=bp.read_bytes();b=bytearray(original);count=struct.unpack_from('<Q',b,53)[0];off=61;rows=[];offsets=[]
for _ in range(count):
 v=struct.unpack_from('<12f?',b,off);rows.append(v[:-1]);offsets.append(off+24);off+=49+(8 if v[-1]else 0)
rows=np.array(rows);ref=np.load(OUT/'reference-frames.npz');ids=sorted({k.split('_')[0]for k in ref.files});lookup=np.concatenate([np.column_stack([ref[i+'_v'],ref[i+'_n'],ref[i+'_uv']])for i in ids]);d,si=cKDTree(lookup).query(np.column_stack([rows[:,:6],rows[:,10:12]]));assert d.max()<2e-4;t=np.concatenate([ref[i+'_t']for i in ids])[si].copy();n=rows[:,3:6];t[:,:3]-=n*np.sum(t[:,:3]*n,axis=1,keepdims=True);t[:,:3]/=np.linalg.norm(t[:,:3],axis=1,keepdims=True);allowed=np.zeros(len(b),bool)
for i,pos in enumerate(offsets):struct.pack_into('<4f',b,pos,*t[i]);allowed[pos:pos+16]=True
assert np.all((np.frombuffer(original,'u1')==np.frombuffer(b,'u1'))|allowed);info=read_mesh(bp);assert b[info['parsed_prefix_bytes']:]==original[info['parsed_prefix_bytes']:];(GAME/'meshes'/(NAME+'.mesh')).write_bytes(b)
m=read(BUILD/'compiler-json'/(NAME+'.mesh_json'));ix=np.array(m['vertex_indices']).reshape(-1,3);q=np.cross(rows[ix[:,1],:3]-rows[ix[:,0],:3],rows[ix[:,2],:3]-rows[ix[:,0],:3]);opposed=int((np.sum(q*n[ix].mean(1),axis=1)<-1e-5).sum());assert opposed==0
meta=read(AUD/'integration-spec.json');assert info['triangles']==meta['source']['remaining_triangles']
for actual,want in zip(info['meshpoints'],meta['meshpoints']):
 assert actual['name']==want['name']and np.allclose(actual['position'],want['translation'],atol=2e-5)
 assert np.allclose(np.array(actual['rotation']).reshape(3,3),Rotation.from_quat(want.get('rotation',[0,0,0,1])).as_matrix().T,atol=2e-5)
# Uniform numeric material channels avoid a fabricated texture-reconstruction claim.
for label,color in meta['colors'].items():
 stem='expanse24_storm_'+label
 rgba=tuple(round(x*255)for x in color)
 channels={'clr':rgba,'nrm':(128,128,255,255),'orm':(255,round(.34*255),round(.52*255),255),'msk':(0,0,0,0)}
 for ch,c in channels.items():
  p=OUT/'textures'/(stem+'_'+ch+'.png');Image.new('RGBA',(16,16),c).save(p)
  cmd=[str(WINE),str(MAIN/'.tools/texconv.exe'),'-f','BC5_SNORM'if ch=='nrm'else'BC7_UNORM','-y','-m','0','-nogpu','--single-proc','-o','Z:'+str(GAME/'textures')]+(['--x2-bias']if ch=='nrm'else['-bc','q'])+['Z:'+str(p)]
  with (BUILD/(stem+'_'+ch+'.log')).open('w')as log:subprocess.run(cmd,env=env,stdout=log,stderr=subprocess.STDOUT,check=True,timeout=120)
 mat={'version':1,'base_color_texture':stem+'_clr','normal_texture':stem+'_nrm','orm_texture':stem+'_orm','team_color_texture':stem+'_msk','emissive_factor':0}
 # Native Sins material keys are verified against an accepted donor.
 donor=read(BASE/'mesh_materials/expanse11_donnager_rail_0_expanse11_donnager_mat_1.mesh_material');keys={k for k in donor if k.endswith('_texture')};print('native material texture keys',keys) if label=='pearl'else None
 mat=copy.deepcopy(donor)
 for k in keys:
  suffix={'base_color_texture':'clr','normal_texture':'nrm','occlusion_roughness_metallic_texture':'orm','mask_texture':'msk'}[k];mat[k]=stem+'_'+suffix
 mat['emissive_factor']=0
 alias=next(x for x in info['materials']if x.endswith('_storm_'+label));write(GAME/'mesh_materials'/(alias+'.mesh_material'),mat)
# Actual native rotating PDC geometry is copied byte-for-byte, including textures.
materials=set();hashes={}
for dest,source in [('expanse24_storm_pdc_base','expanse10_donnager_pdc_base'),('expanse24_storm_pdc_barrel','expanse10_donnager_pdc_barrel')]:
 p=BASE/'meshes'/(source+'.mesh');(GAME/'meshes'/(dest+'.mesh')).write_bytes(p.read_bytes());hashes[str(p)]=hashlib.sha256(p.read_bytes()).hexdigest();materials.update(read_mesh(p)['materials'])
for name in materials:
 p=BASE/'mesh_materials'/(name+'.mesh_material');(GAME/'mesh_materials'/p.name).write_bytes(p.read_bytes())
 for k,v in read(p).items():
  if k.endswith('_texture'):
   p=BASE/'textures'/(v+'.dds');(GAME/'textures'/p.name).write_bytes(p.read_bytes())
meta.update(status='PASS OFFLINE COMPILED HULL / NATIVE ROTATING PDC ASSETS; RUNTIME NOT RUN',output_game=str(GAME),checks={'compiled_triangles':info['triangles'],'degenerate_only_removal':True,'source_frame_error':float(d.max()),'only_tangent_bytes_repaired':True,'opaque_trailer_preserved':True,'opposed_winding_triangles':opposed,'meshpoint_positions_rotations_match':True,'initial_winding_flips':flips},donor_mesh_hashes=hashes,compiled_files={str(p.relative_to(GAME)):hashlib.sha256(p.read_bytes()).hexdigest()for p in sorted(GAME.rglob('*'))if p.is_file()});write(AUD/'integration-spec.json',meta);print('PASS',info['triangles'],'hull triangles')
