from donnager10_geometry_common import *
from PIL import Image
import argparse,subprocess,shutil
p=argparse.ArgumentParser();p.add_argument('--wine',type=Path,required=True);args=p.parse_args();tex=OUT/'texture-sources';tex.mkdir(exist_ok=True);dest=BUILD/'game/textures';dest.mkdir(parents=True,exist_ok=True);defs=OUT/'materials';defs.mkdir(exist_ok=True);materialdefs={}
def solid(name,color):
 path=tex/(name+'.png');Image.new('RGBA',(16,16),tuple(color)).save(path);return name
flatnormal=solid('expanse10_donnager_flat_nrm',[128,128,255,255]);dark=solid('expanse10_donnager_dark_msk',[0,0,0,0]);emit=solid('expanse10_donnager_emissive_msk',[0,0,255,0]);images={}
for i,image in enumerate(a.g['images']):
 name=f'expanse10_donnager_atlas_{i}_clr';Image.open(SRC/image['uri']).convert('RGBA').save(tex/(name+'.png'));images[i]=name
for i,mat in enumerate(a.g['materials']):
 name=f'expanse10_donnager_mat_{i}';pbr=mat['pbrMetallicRoughness'];factor=np.array(pbr.get('baseColorFactor',[1]*4));metal=pbr.get('metallicFactor',1.);rough=pbr.get('roughnessFactor',1.)
 if 'baseColorTexture' in pbr:clr=images[a.g['textures'][pbr['baseColorTexture']['index']]['source']]
 else:clr=solid(name+'_clr',np.clip(np.rint(factor*255),0,255).astype(int))
 orm=solid(name+'_orm',[255,round(rough*255),round(metal*255),255]);definition={'version':1,'base_color_texture':clr,'occlusion_roughness_metallic_texture':orm,'normal_texture':flatnormal,'mask_texture':emit if max(mat.get('emissiveFactor',[0]))>0 else dark,'emissive_factor':float(max(mat.get('emissiveFactor',[0])))};write(defs/(name+'.mesh_material'),definition);materialdefs[name]=definition
base=Path('/run/media/haker/NVME 2/expanse-mod/build/experiments/expanse_amun09_cloak');dm=read(base/'mesh_materials/expanse03_pdc_0_base_mcrn_tachi_material.mesh_material');materialdefs['mcrn_tachi_material']=dm;write(defs/'mcrn_tachi_material.mesh_material',dm);donorhashes={}
for key,value in dm.items():
 if key.endswith('_texture'):
  src=base/'textures'/(value+'.dds');assert src.is_file();shutil.copyfile(src,dest/src.name);donorhashes[str(src)]=hashlib.sha256(src.read_bytes()).hexdigest()
env=dict(os.environ,WINEPREFIX=str(BUILD/'proton-prefix'),OMP_NUM_THREADS='4',MANGOHUD='0',WINEDEBUG='-all',DISPLAY='',WINEDLLOVERRIDES='mscoree,mshtml=');exe=Path('/run/media/haker/NVME 2/expanse-mod/.tools/texconv.exe');assert exe.is_file()
for inp in sorted(tex.glob('*.png')):
 nrm=inp.stem.endswith('_nrm');cmd=[str(args.wine),str(exe),'-f','BC5_SNORM' if nrm else 'BC7_UNORM','-y','-m','0','-nogpu','--single-proc','-o','Z:'+str(dest)]+(['--x2-bias'] if nrm else ['-bc','q'])+['Z:'+str(inp)]
 with (BUILD/('texconv-'+inp.stem+'.log')).open('w') as log:subprocess.run(cmd,env=env,stdout=log,stderr=subprocess.STDOUT,check=True,timeout=120)
 print(inp.stem,flush=True)
matdest=BUILD/'game/mesh_materials';matdest.mkdir(exist_ok=True);aliases={}
for file in sorted((BUILD/'compiler-json').glob('*.mesh_json')):
 for actual in read(file)['materials']:
  match=[name for name in materialdefs if actual.endswith('_'+name)];assert len(match)==1,(actual,match);write(matdest/(actual+'.mesh_material'),materialdefs[match[0]]);aliases[actual]=match[0]
write(AUDIT/'material-resources.json',{'status':'GENERATED; DDS/reference checks pending','actual_aliases':aliases,'source_material_count':11,'donor_material_count':1,'source_texture_size':[2048,2048],'constant_texture_size':[16,16],'no_source_normal_map':'Flat unit normal derivative; no detail reconstructed or baked','mask':'Source emissive surfaces use maskB1 tinted by base color. No player-color region invented','donor_texture_hashes':donorhashes,'source_materials':str(defs)})
