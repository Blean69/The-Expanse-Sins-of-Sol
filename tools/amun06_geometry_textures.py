"""Amun shared2K material derivative; source4K atlas remains untouched."""
from amun06_geometry_common import *
from PIL import Image
import argparse,subprocess,shutil
P=argparse.ArgumentParser();P.add_argument('--wine',required=True,type=Path);args=P.parse_args();tex=OUT/'texture-sources';tex.mkdir(exist_ok=True);name='expanse06_amun_surface';mat=a.g['materials'][0];pbr=mat['pbrMetallicRoughness']
def image(index):
 path=SRC/a.g['images'][a.g['textures'][index]['source']]['uri'];return Image.open(path).convert('RGBA').resize((2048,2048),Image.Resampling.LANCZOS)
image(pbr['baseColorTexture']['index']).save(tex/(name+'_clr.png'));orm=np.array(image(pbr['metallicRoughnessTexture']['index']));orm[:,:,0]=255;orm[:,:,3]=255;Image.fromarray(orm).save(tex/(name+'_orm.png'));normal=np.array(image(mat['normalTexture']['index'])).astype(float)[:,:,:3]/127.5-1;normal/=np.maximum(np.linalg.norm(normal,axis=2,keepdims=True),1e-10);Image.fromarray(np.clip(np.rint((normal+1)*127.5),0,255).astype('uint8')).save(tex/(name+'_nrm.png'));e=np.array(image(mat['emissiveTexture']['index']));mask=np.zeros_like(e);mask[:,:,2]=e[:,:,:3].max(2);Image.fromarray(mask).save(tex/(name+'_msk.png'));material={'version':1,'base_color_texture':name+'_clr','occlusion_roughness_metallic_texture':name+'_orm','normal_texture':name+'_nrm','mask_texture':name+'_msk','emissive_factor':1.0};write(OUT/'materials'/(name+'.mesh_material'),material)
dest=BUILD/'game/textures';dest.mkdir(parents=True,exist_ok=True);env=dict(os.environ,WINEPREFIX=str(BUILD/'proton-prefix'),OMP_NUM_THREADS='4',MANGOHUD='0',WINEDEBUG='-all',DISPLAY='',WINEDLLOVERRIDES='mscoree,mshtml=');exe=Path('/run/media/haker/NVME 2/expanse-mod/.tools/texconv.exe');assert exe.is_file()
for inp in sorted(tex.glob('*.png')):
 nrm=inp.stem.endswith('_nrm');fmt='BC5_SNORM' if nrm else 'BC7_UNORM';opts=['--x2-bias'] if nrm else ['-bc','q'];cmd=[str(args.wine),str(exe),'-f',fmt,'-y','-m','0','-nogpu','--single-proc','-o','Z:'+str(dest)]+opts+['Z:'+str(inp)]
 with (BUILD/('texconv-'+inp.stem+'.log')).open('w') as log:subprocess.run(cmd,env=env,stdout=log,stderr=subprocess.STDOUT,check=True,timeout=120)
 assert (dest/(inp.stem+'.dds')).read_bytes()[:4]==b'DDS ';print(inp.stem,flush=True)
matdest=BUILD/'game/mesh_materials';matdest.mkdir(exist_ok=True);aliases=[]
for file in sorted((BUILD/'compiler-json').glob('*.mesh_json')):
 for actual in read(file)['materials']:write(matdest/(actual+'.mesh_material'),material);aliases.append(actual)
write(AUDIT/'material-resources.json',{'aliases':aliases,'texture_dimensions':[2048,2048],'source_dimensions':[4096,4096],'normal_map':'Source referenced glTF normals retained and renormalized after resize; DirectX filename ambiguity requires runtime bump inspection, no unverified green reversal','ORM':'R255 (no AO source), G/B source glTF roughness/metallic','mask':'R/G/A0, B=max source emissiveRGB. Emission is base-color-tinted by installed shader, not independent source emissionRGB','source_material':str(OUT/'materials'/(name+'.mesh_material'))})
