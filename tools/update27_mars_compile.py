"""Compile isolated 0.27 art via pinned SDK and existing Wine prefix in place."""
from update27_mars_assets import *
import os,subprocess,argparse
from scipy.spatial import cKDTree
from PIL import Image
SDK=Path('/run/media/haker/NVME 2/SteamLibrary/steamapps/common/Sins of a Solar Empire II - Mod Tools');WINE=Path('/home/haker/.var/app/com.valvesoftware.Steam/.local/share/Steam/steamapps/common/Proton 10.0/files/bin/wine64');PREFIX=Path('/run/media/haker/NVME 2/expanse-workers/tachi-one-pdc/build/polish-b/proton-prefix');ENV=dict(os.environ,WINEPREFIX=str(PREFIX),OMP_NUM_THREADS='4',MANGOHUD='0',WINEDEBUG='-all',DISPLAY='',WINEDLLOVERRIDES='mscoree,mshtml=')
def build(key,materials_only=False):
 meta=read(AUD/(key+'-integration.json'));usedm=set();names=[]
 for mesh in meta['meshes']:
  name=mesh['name'];names.append(name)
  if materials_only:usedm.update(read_mesh(GAME/'meshes'/(name+'.mesh'))['materials']);continue
  def run(fmt):
   out=BUILD/(key+'-'+fmt);out.mkdir(exist_ok=True)
   with(BUILD/(name+'-'+fmt+'.log')).open('w')as log:subprocess.run([str(WINE),str(SDK/'MeshBuilder/bin/MeshBuilder.exe'),'--input_path=Z:'+str(OUT/(name+'.gltf')),'--output_folder_path=Z:'+str(out),'--mesh_output_format='+fmt,'--fill_triangle_facing_grid'],env=ENV,stdout=log,stderr=subprocess.STDOUT,check=True,timeout=300)
  run('json');m=read(BUILD/(key+'-json')/(name+'.mesh_json'));g=Gltf(OUT/(name+'.gltf'));buffer=bytearray(g.buffers[0]);vv=np.array([v['p']for v in m['non_skinned_vertices']]);nn=np.array([v['n']for v in m['non_skinned_vertices']]);allidx=np.array(m['vertex_indices']);flips=0
  for pp in m['primitives']:
   mat=m['materials'][pp['material_index']];pr=next(p for p in g.g['meshes'][0]['primitives']if mat.endswith('_'+g.g['materials'][p['material']]['name']));ii=allidx[pp['vertex_index_start']:pp['vertex_index_start']+pp['vertex_index_count']].reshape(-1,3);q=np.cross(vv[ii[:,1]]-vv[ii[:,0]],vv[ii[:,2]]-vv[ii[:,0]]);flip=np.sum(q*nn[ii].mean(1),axis=1)<-1e-8;at=g.g['accessors'][pr['indices']];bv=g.g['bufferViews'][at['bufferView']];arr=np.ndarray((at['count']//3,3),dtype='<u4',buffer=buffer,offset=bv.get('byteOffset',0)+at.get('byteOffset',0));sv=g.accessor(pr['attributes']['POSITION']);sv[:,2]*=-1;assert np.allclose(np.sort(sv[arr],axis=1),np.sort(vv[ii],axis=1),atol=5e-5);arr[flip]=arr[flip][:,[0,2,1]];flips+=int(flip.sum())
  if flips:(OUT/(name+'.bin')).write_bytes(buffer);run('json')
  run('binary');bp=BUILD/(key+'-binary')/(name+'.mesh');raw=bp.read_bytes();b=bytearray(raw);cnt=struct.unpack_from('<Q',b,53)[0];off=61;rows=[];offsets=[]
  for _ in range(cnt):
   r=struct.unpack_from('<12f?',b,off);rows.append(r[:-1]);offsets.append(off+24);off+=49+(8 if r[-1]else 0)
  rows=np.array(rows);ref=np.load(OUT/(name+'-frames.npz'));ids=sorted({k.split('_')[0]for k in ref.files});lookup=np.concatenate([np.column_stack([ref[i+'_v'],ref[i+'_n'],ref[i+'_uv']])for i in ids]);d,si=cKDTree(lookup).query(np.column_stack([rows[:,:6],rows[:,10:12]]));assert d.max()<2e-4;t=np.concatenate([ref[i+'_t']for i in ids])[si].copy();n=rows[:,3:6];t[:,:3]-=n*np.sum(t[:,:3]*n,axis=1)[:,None];t[:,:3]/=np.linalg.norm(t[:,:3],axis=1)[:,None];allowed=np.zeros(len(b),bool)
  for j,pos in enumerate(offsets):struct.pack_into('<4f',b,pos,*t[j]);allowed[pos:pos+16]=True
  assert np.all((np.frombuffer(raw,'u1')==np.frombuffer(b,'u1'))|allowed);info=read_mesh(bp);assert b[info['parsed_prefix_bytes']:]==raw[info['parsed_prefix_bytes']:];assert info['triangles']==mesh['triangles'];(GAME/'meshes'/(name+'.mesh')).write_bytes(b);usedm.update(info['materials'])
  for got,want in zip(info['meshpoints'],mesh['meshpoints']):
   assert got['name']==want['name']and np.allclose(got['position'],want['translation'],atol=5e-5)
  mesh['source_frame_error']=float(d.max());mesh['winding_flips']=flips
 for name,source in meta['copied_meshes'].items():
  (GAME/'meshes'/(name+'.mesh')).write_bytes((BASE/'meshes'/(source+'.mesh')).read_bytes());usedm.update(read_mesh(GAME/'meshes'/(name+'.mesh'))['materials'])
 # Every material either has an explicit numeric recipe or an exact native source.
 for mat in usedm:
  native=next((v for k,v in meta.get('native_materials',{}).items()if mat.endswith('_'+k)),None)
  numeric=next((k for k in meta['colors']if mat.endswith('_'+k)),None)
  if numeric:
   stem='expanse27_'+key+'_'+numeric;rgba=tuple(round(v*255)for v in meta['colors'][numeric]);folder=OUT/'textures';folder.mkdir(exist_ok=True)
   channels={'clr':rgba,'orm':(255,round(.43*255),round(.32*255),255),'nrm':(128,128,255,255),'msk':(0,0,0,0)}
   for channel,color in channels.items():
    p=folder/(stem+'_'+channel+'.png');Image.new('RGBA',(16,16),color).save(p)
    with(BUILD/(p.stem+'.log')).open('w')as log:subprocess.run([str(WINE),str(MAIN/'.tools/texconv.exe'),'-f','BC7_UNORM','-y','-m','0','-nogpu','--single-proc','-o','Z:'+str(GAME/'textures'),'-bc','q','Z:'+str(p)],env=ENV,stdout=log,stderr=subprocess.STDOUT,check=True,timeout=120)
   md={'version':1,'base_color_texture':stem+'_clr','occlusion_roughness_metallic_texture':stem+'_orm','normal_texture':stem+'_nrm','mask_texture':stem+'_msk','emissive_factor':0.0};write(GAME/'mesh_materials'/(mat+'.mesh_material'),md)
  else:
   source=BASE/'mesh_materials'/((native or mat)+'.mesh_material');assert source.exists(),source;(GAME/'mesh_materials'/(mat+'.mesh_material')).write_bytes(source.read_bytes())
  for k,v in read(GAME/'mesh_materials'/(mat+'.mesh_material')).items():
   if k.endswith('_texture')and not(GAME/'textures'/(v+'.dds')).exists():(GAME/'textures'/(v+'.dds')).write_bytes((BASE/'textures'/(v+'.dds')).read_bytes())
 meta['compiled']=True;meta['compiled_meshes']=names;meta['wine_prefix_used_in_place']=str(PREFIX);meta['used_materials']=sorted(usedm);write(AUD/(key+'-integration.json'),meta);print(key,'compiled',flush=True)
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('key');p.add_argument('--materials-only',action='store_true');a=p.parse_args();build(a.key,a.materials_only)
