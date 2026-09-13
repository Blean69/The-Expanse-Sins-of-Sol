from pathlib import Path
import os,subprocess,shutil,json,struct,hashlib,numpy as np
from scipy.spatial import cKDTree
from common import read_mesh,Gltf
import sys
sys.path.append('/run/media/haker/NVME 2/expanse-mod/tools')
from polish_ui import write
ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'assets/derived/update12-b';BUILD=ROOT/'build/update12-b';AUD=ROOT/'audit/update12-b';MAIN=Path('/run/media/haker/NVME 2/expanse-mod');DONOR=Path('/run/media/haker/NVME 2/expanse-workers/tachi-one-pdc');SDK=Path('/run/media/haker/NVME 2/SteamLibrary/steamapps/common/Sins of a Solar Empire II - Mod Tools');wine=Path('/home/haker/.var/app/com.valvesoftware.Steam/.local/share/Steam/steamapps/common/Proton 10.0/files/bin/wine64');prefix=BUILD/'proton-prefix'
if not prefix.exists():shutil.copytree(DONOR/'build/polish-b/proton-prefix',prefix,symlinks=True)
env=dict(os.environ,WINEPREFIX=str(prefix),OMP_NUM_THREADS='4',MANGOHUD='0',WINEDEBUG='-all',DISPLAY='',WINEDLLOVERRIDES='mscoree,mshtml=')
meta=json.loads((AUD/'integration-spec.json').read_text());sources=json.loads((OUT/'retained-source-frames.json').read_text());records=[]
for kind in ['hull','rail_0','pdc_base','pdc_barrel']:
 name='expanse12_scirocco_'+kind;inp=OUT/(name+'.gltf')
 for fmt in ['json','binary']:
  dest=BUILD/('compiler-'+fmt);dest.mkdir(exist_ok=True);cmd=[str(wine),str(SDK/'MeshBuilder/bin/MeshBuilder.exe'),'--input_path=Z:'+str(inp),'--output_folder_path=Z:'+str(dest),'--mesh_output_format='+fmt,'--fill_triangle_facing_grid']
  with (BUILD/(name+'-'+fmt+'.log')).open('w') as log:subprocess.run(cmd,env=env,stdout=log,stderr=subprocess.STDOUT,check=True,timeout=300)
 # Correct per-triangle compiler winding in source indices, then regenerate official grids.
 jp0=BUILD/'compiler-json'/(name+'.mesh_json');mm=json.loads(jp0.read_text());asset=Gltf(inp);buffer=bytearray(asset.buffers[0]);vv=np.array([x['p']for x in mm['non_skinned_vertices']]);norm=np.array([x['n']for x in mm['non_skinned_vertices']]);allidx=np.array(mm['vertex_indices']);flipped=0
 for pp in mm['primitives']:
  material=mm['materials'][pp['material_index']];matches=[p for p in asset.g['meshes'][0]['primitives']if material.endswith('_'+asset.g['materials'][p['material']]['name'])];assert len(matches)==1;pr=matches[0];ii=allidx[pp['vertex_index_start']:pp['vertex_index_start']+pp['vertex_index_count']].reshape(-1,3);tt=vv[ii];q=np.cross(tt[:,1]-tt[:,0],tt[:,2]-tt[:,0]);nn=norm[ii].mean(1);cos=np.sum(q*nn,axis=1)/np.maximum(np.linalg.norm(q,axis=1)*np.linalg.norm(nn,axis=1),1e-15);flip=cos< -1e-5;at=asset.g['accessors'][pr['indices']];bv=asset.g['bufferViews'][at['bufferView']];arr=np.ndarray((at['count']//3,3),dtype='<u4',buffer=buffer,offset=bv.get('byteOffset',0)+at.get('byteOffset',0));sourcev=asset.accessor(pr['attributes']['POSITION']);sourcev[:,2]*=-1;expected=sourcev[arr];assert np.allclose(np.sort(expected,axis=1),np.sort(tt,axis=1),atol=4e-5);arr[flip]=arr[flip][:,[0,2,1]];flipped+=int(flip.sum())
 if flipped:
  (OUT/(name+'.bin')).write_bytes(buffer)
  for fmt in ['json','binary']:
   cmd=[str(wine),str(SDK/'MeshBuilder/bin/MeshBuilder.exe'),'--input_path=Z:'+str(inp),'--output_folder_path=Z:'+str(BUILD/('compiler-'+fmt)),'--mesh_output_format='+fmt,'--fill_triangle_facing_grid']
   with (BUILD/(name+'-winding-'+fmt+'.log')).open('w')as log:subprocess.run(cmd,env=env,stdout=log,stderr=subprocess.STDOUT,check=True,timeout=300)
 bp=BUILD/'compiler-binary'/(name+'.mesh');jp=BUILD/'compiler-json'/(name+'.mesh_json');m=json.loads(jp.read_text());original=bp.read_bytes();b=bytearray(original);count=struct.unpack_from('<Q',b,53)[0];off=61;binary=[];offsets=[]
 for _ in range(count):
  vals=struct.unpack_from('<12f?',b,off);binary.append(vals[:-1]);offsets.append(off+24);off+=49+(8 if vals[-1] else 0)
 binary=np.array(binary);lookup=[];st=[]
 for r in sources[kind].values():lookup.append(np.concatenate([r['v'],r['n'],r['uv']],axis=1));st.append(r['t'])
 d,si=cKDTree(np.concatenate(lookup)).query(np.concatenate([binary[:,:6],binary[:,10:12]],axis=1));assert d.max()<2e-4,(name,d.max());t=np.concatenate(st)[si];n=binary[:,3:6];t[:,:3]-=n*np.sum(t[:,:3]*n,axis=1)[:,None];length=np.linalg.norm(t[:,:3],axis=1);assert length.min()>1e-8;t[:,:3]/=length[:,None];t[:,3]=np.where(t[:,3]<0,-1.,1.);allowed=np.zeros(len(b),bool)
 for i,s in enumerate(offsets):struct.pack_into('<4f',b,s,*t[i]);allowed[s:s+16]=True;m['non_skinned_vertices'][i]['t']=t[i].tolist()
 assert np.all((np.frombuffer(original,np.uint8)==np.frombuffer(b,np.uint8))|allowed);parsed=read_mesh(bp)['parsed_prefix_bytes'];assert b[parsed:]==original[parsed:];idx=np.array(m['vertex_indices']).reshape(-1,3);v=binary[:,:3];q=np.cross(v[idx[:,1]]-v[idx[:,0]],v[idx[:,2]]-v[idx[:,0]]);ns=n[idx].mean(1);alignment=np.sum(q*ns,axis=1)/np.maximum(np.linalg.norm(q,axis=1)*np.linalg.norm(ns,axis=1),1e-15);assert (alignment< -1e-5).sum()==0
 dest=BUILD/'game/meshes';dest.mkdir(parents=True,exist_ok=True);(dest/(name+'.mesh')).write_bytes(b);write(BUILD/'repaired-json'/(name+'.mesh_json'),m)
 actual=read_mesh(dest/(name+'.mesh'));assert actual['triangles']==meta['counts'][kind]
 for got,want in zip(actual['meshpoints'],meta['meshpoints'][kind]):assert got['name']==want['name']and np.allclose(got['position'],want['translation'],atol=2e-5)
 records.append({'mesh':name,'triangles':len(idx),'sha256':hashlib.sha256(b).hexdigest(),'only_tangent_bytes_changed':True,'official_trailer_preserved':True,'authored_frame_error':float(d.max()),'tangent_fallbacks':0,'opposed_winding_triangles':int((alignment< -1e-5).sum()),'near_ambiguous_winding_triangles':int((abs(alignment)<=1e-5).sum()),'materials':m['materials'],'meshpoints':actual['meshpoints']});print(name,'PASS',flush=True)
write(AUD/'mesh-validation.json',{'status':'PASS OFFLINE','meshes':records,'runtime':'NOT RUN'});meta['status']='PASS OFFLINE MESHES; MATERIAL/UI CHECKS PENDING';write(AUD/'integration-spec.json',meta)
# Generate explicit solid-color material DDS; STL supplies no texture data.
from PIL import Image
tex=OUT/'texture-sources';tex.mkdir(exist_ok=True);dest=BUILD/'game/textures';dest.mkdir(parents=True,exist_ok=True);defs={};colors=[[61,71,79,255],[166,41,14,255],[19,22,24,255]]
for name,color in [('expanse12_scirocco_nrm',[128,128,255,255]),('expanse12_scirocco_orm',[255,180,100,255]),('expanse12_scirocco_msk',[0,0,0,0])]+[(f'expanse12_scirocco_mat_{i}_clr',color) for i,color in enumerate(colors)]:Image.new('RGBA',(16,16),tuple(color)).save(tex/(name+'.png'))
for i in range(3):defs[f'expanse12_scirocco_mat_{i}']={'version':1,'base_color_texture':f'expanse12_scirocco_mat_{i}_clr','occlusion_roughness_metallic_texture':'expanse12_scirocco_orm','normal_texture':'expanse12_scirocco_nrm','mask_texture':'expanse12_scirocco_msk','emissive_factor':0.}
for inp in tex.glob('*.png'):
 nrm=inp.stem.endswith('_nrm');cmd=[str(wine),str(MAIN/'.tools/texconv.exe'),'-f','BC5_SNORM'if nrm else'BC7_UNORM','-y','-m','0','-nogpu','--single-proc','-o','Z:'+str(dest)]+(['--x2-bias']if nrm else['-bc','q'])+['Z:'+str(inp)]
 with (BUILD/('texture-'+inp.stem+'.log')).open('w')as log:subprocess.run(cmd,env=env,stdout=log,stderr=subprocess.STDOUT,check=True,timeout=120)
base=MAIN/'build/experiments/expanse_donnager10_pdc_audio';dm=json.loads((base/'mesh_materials/expanse03_pdc_0_base_mcrn_tachi_material.mesh_material').read_text());defs['mcrn_tachi_material']=dm
for key,value in dm.items():
 if key.endswith('_texture'):shutil.copyfile(base/'textures'/(value+'.dds'),dest/(value+'.dds'))
for r in records:
 for actual in r['materials']:
  match=[k for k in defs if actual.endswith('_'+k)];assert len(match)==1;write(BUILD/'game/mesh_materials'/(actual+'.mesh_material'),defs[match[0]])
for p in dest.glob('*.dds'):assert p.read_bytes()[:4]==b'DDS '
meta['status']='PASS OFFLINE MESHES AND MATERIALS';write(AUD/'integration-spec.json',meta);write(AUD/'material-validation.json',{'status':'PASS OFFLINE','authored':'New procedural grey/orange/dark matte materials; source STL contains no colors or UVs','textures':{p.name:hashlib.sha256(p.read_bytes()).hexdigest()for p in dest.glob('*.dds')},'runtime':'NOT RUN'})
