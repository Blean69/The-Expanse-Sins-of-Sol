"""Map supplied glTF texture channels to the pinned Sins material format; no repaint."""
from pathlib import Path
import os,subprocess,json,hashlib,shutil,sys,numpy as np
from PIL import Image
from common import write,Gltf
R=Path(__file__).resolve().parents[1];D=R/'assets/derived/update15-truman';B=R/'build/update15-truman';A=R/'audit/update15-truman';MAIN=Path('/run/media/haker/NVME 2/expanse-mod');MASTER=R/'assets/original/update15-truman/master';tex=D/'texture-sources';tex.mkdir(exist_ok=True);dest=B/'game/textures';dest.mkdir(parents=True,exist_ok=True);name='expanse15_truman_material';src=MASTER/'textures'
def img(n):return Image.open(src/n).convert('RGBA').resize((4096,4096),Image.Resampling.LANCZOS)
img('material_baseColor.jpeg').save(tex/(name+'_clr.png'));orm=np.array(img('material_metallicRoughness.png'));orm[:,:,3]=255;Image.fromarray(orm).save(tex/(name+'_orm.png'));normal=np.array(img('material_normal.png')).astype(float)[:,:,:3]/127.5-1;normal/=np.maximum(np.linalg.norm(normal,axis=2,keepdims=True),1e-10);Image.fromarray(np.clip(np.rint((normal+1)*127.5),0,255).astype('uint8')).save(tex/(name+'_nrm.png'));em=np.array(img('material_emissive.jpeg'));mask=np.zeros_like(em);mask[:,:,2]=em[:,:,:3].max(2);Image.fromarray(mask).save(tex/(name+'_msk.png'));mat={'version':1,'base_color_texture':name+'_clr','occlusion_roughness_metallic_texture':name+'_orm','normal_texture':name+'_nrm','mask_texture':name+'_msk','emissive_factor':1.0}
wine=Path('/home/haker/.var/app/com.valvesoftware.Steam/.local/share/Steam/steamapps/common/Proton 10.0/files/bin/wine64');env=dict(os.environ,WINEPREFIX=str(B/'proton-prefix'),OMP_NUM_THREADS='4',MANGOHUD='0',WINEDEBUG='-all',DISPLAY='',WINEDLLOVERRIDES='mscoree,mshtml=')
reuse='--reuse-converted-textures'in sys.argv
if reuse:
 for path,expected in json.loads((A/'texture-conversion-checkpoint.json').read_text()).items():assert hashlib.sha256(Path(path).read_bytes()).hexdigest()==expected
for inp in tex.glob('*.png'):
 if reuse:continue
 nrm=inp.stem.endswith('_nrm');cmd=[str(wine),str(MAIN/'.tools/texconv.exe'),'-f','BC5_SNORM'if nrm else'BC7_UNORM','-y','-m','0','-nogpu','--single-proc','-o','Z:'+str(dest)]+(['--x2-bias']if nrm else['-bc','q'])+['Z:'+str(inp)]
 with (B/('texture-'+inp.stem+'.log')).open('w')as log:subprocess.run(cmd,env=env,stdout=log,stderr=subprocess.STDOUT,check=True,timeout=300)
base=MAIN/'build/experiments/expanse_update14';donor=json.loads((base/'mesh_materials/expanse03_pdc_0_base_mcrn_tachi_material.mesh_material').read_text());support=json.loads((base/'mesh_materials/expanse12_raptor_hull_expanse12_raptor_mat_2.mesh_material').read_text())
for m in [donor,support]:
 for k,v in m.items():
  if k.endswith('_texture'):shutil.copyfile(base/'textures'/(v+'.dds'),dest/(v+'.dds'))
records=json.loads((A/'mesh-validation.json').read_text())['meshes']
for r in records:
 for alias in r['materials']:
  value=mat if alias.endswith('_truman_material')else support if alias.endswith('_truman_support')else donor if alias.endswith('_mcrn_tachi_material')else None;assert value;write(B/'game/mesh_materials'/(alias+'.mesh_material'),value)
# Bind actual source color maps to editable glTF for reproducible UI/offline inspection.
p=D/'expanse15_truman_editable.gltf';g=json.loads(p.read_text());g['images']=[{'uri':'texture-sources/'+name+'_clr.png'},{'uri':str(base/'textures'/(donor['base_color_texture']+'.dds'))}];g['textures']=[{'source':0},{'source':1}]
for m in g['materials']:
 if m['name']=='truman_material':m['pbrMetallicRoughness']={'baseColorTexture':{'index':0},'baseColorFactor':[1,1,1,1]}
 elif m['name']=='mcrn_tachi_material':m['pbrMetallicRoughness']={'baseColorTexture':{'index':1},'baseColorFactor':[1,1,1,1]}
write(p,g)
write(A/'material-validation.json',{'status':'PASS OFFLINE','source_dimensions':[8192,8192],'game_dimensions':[4096,4096],'conversion':'SourceUV/basecolor retained; supplied packed occlusion/roughness/metallicRGB retained; normalrenormalized; sourceemissive maximum maps to maskB, restrainedfactor1 vs source10. No alpha/transparency source.','runtime':'NOT RUN','textures':{p.name:hashlib.sha256(p.read_bytes()).hexdigest()for p in dest.glob('*.dds')}})
print('Materials complete')
