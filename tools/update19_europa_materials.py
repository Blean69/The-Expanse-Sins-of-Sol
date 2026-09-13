"""Convert explicit Europa UV material approximations to Sins DDS assets and render the actual derivative."""
from pathlib import Path
import os,subprocess,json,hashlib,shutil,sys,numpy as np
from concurrent.futures import ThreadPoolExecutor
from PIL import Image
from common import write,Gltf
from polish_ui import render
R=Path(__file__).resolve().parents[1];D=R/'assets/derived/update19-europa';B=R/'build/update19-europa';A=R/'audit/update19-europa';MAIN=Path('/run/media/haker/NVME 2/expanse-mod');P='expanse19_europa';dest=B/'game/textures';dest.mkdir(parents=True,exist_ok=True);mats=json.loads((D/'materials.json').read_text());tex=D/'texture-sources'
wine=Path('/home/haker/.var/app/com.valvesoftware.Steam/.local/share/Steam/steamapps/common/Proton 10.0/files/bin/wine64');env=dict(os.environ,WINEPREFIX=str(B/'proton-prefix'),OMP_NUM_THREADS='1',MANGOHUD='0',WINEDEBUG='-all',DISPLAY='',WINEDLLOVERRIDES='mscoree,mshtml=')
def convert(inp):
 nrm=inp.stem.endswith('_nrm');cmd=[str(wine),str(MAIN/'.tools/texconv.exe'),'-f','BC5_SNORM'if nrm else'BC7_UNORM','-y','-m','0','-nogpu','--single-proc','-o','Z:'+str(dest)]+(['--x2-bias']if nrm else['-bc','q'])+['Z:'+str(inp)]
 with (B/('texture-'+inp.stem+'.log')).open('w')as log:subprocess.run(cmd,env=env,stdout=log,stderr=subprocess.STDOUT,check=True,timeout=300)
 return inp.name
if '--reuse-converted-textures'not in sys.argv:
 with ThreadPoolExecutor(max_workers=4)as pool:
  for n in pool.map(convert,sorted(tex.glob('*.png'))):print(n,flush=True)
base=MAIN/'build/experiments/expanse_update18';donor=json.loads((base/'mesh_materials/expanse03_pdc_0_base_mcrn_tachi_material.mesh_material').read_text());support=json.loads((base/'mesh_materials/expanse12_raptor_hull_expanse12_raptor_mat_2.mesh_material').read_text())
for mat,label in [(donor,'pdc'),(support,'support')]:
 for k,v in list(mat.items()):
  if k.endswith('_texture'):
   new=P+'_'+label+'_'+k;shutil.copyfile(base/'textures'/(v+'.dds'),dest/(new+'.dds'));mat[k]=new
records=json.loads((A/'mesh-validation.json').read_text())['meshes']
for r in records:
 for alias in r['materials']:
  suffix=next((k for k in mats if alias.endswith('_'+k)),None)
  if suffix:mat={'version':1,**{k:v for k,v in mats[suffix].items()if k.endswith('_texture')or k=='emissive_factor'}}
  elif alias.endswith('_mcrn_tachi_material'):mat=donor
  elif alias.endswith('_'+P+'_support'):mat=support
  else:raise ValueError(alias)
  write(B/'game/mesh_materials'/(alias+'.mesh_material'),mat)
# Bind exact baked color maps and retained normals in editable artifact.
p=D/(P+'_editable.gltf');g=json.loads(p.read_text());g['images']=[];g['textures']=[]
for mat in g['materials']:
 name=mat['name']
 if name in mats:
  g['images'].append({'uri':'texture-sources/'+name+'_clr.png'});g['textures'].append({'source':len(g['images'])-1});mat['pbrMetallicRoughness']={'baseColorTexture':{'index':len(g['textures'])-1},'baseColorFactor':[1,1,1,1],'roughnessFactor':.72,'metallicFactor':.29}
 elif name=='mcrn_tachi_material':
  g['images'].append({'uri':str(dest/(donor['base_color_texture']+'.dds'))});g['textures'].append({'source':len(g['images'])-1});mat['pbrMetallicRoughness']={'baseColorTexture':{'index':len(g['textures'])-1},'baseColorFactor':[1,1,1,1]}
 else:mat['pbrMetallicRoughness']={'baseColorFactor':[.08,.09,.1,1]}
g['asset']['generator']='Europa Bane extracted source derivative; original UVs, approximation of Unreal color parameters; verified articulated retrofit';write(p,g)
asset=Gltf(p);meshes=[];cache={}
for pr in asset.g['meshes'][0]['primitives']:
 v=asset.accessor(pr['attributes']['POSITION']);ii=asset.accessor(pr['indices']).reshape(-1,3);uv=asset.accessor(pr['attributes']['TEXCOORD_0']);mat=asset.g['materials'][pr['material']];pbr=mat['pbrMetallicRoughness'];texdef=pbr.get('baseColorTexture')
 if texdef:
  path=p.parent/asset.g['images'][asset.g['textures'][texdef['index']]['source']]['uri']
  if str(path)not in cache:cache[str(path)]=np.asarray(Image.open(path).convert('RGBA'))
  texture=cache[str(path)]
 else:texture=np.full((1,1,4),255,np.uint8)
 meshes.append((v[ii],uv[ii],texture,pbr['baseColorFactor'],'OPAQUE'))
for name,b in [('side',[[0,0,1],[0,1,0],[-1,0,0]]),('oblique',[[.75,0,.66],[.2,.95,-.23],[-.63,.3,.7]]),('stern',[[1,0,0],[0,1,0],[0,0,-1]])]:render(meshes,(1500,700),np.array(b)).save(A/(name+'.png'))
write(A/'material-validation.json',{'status':'PASS OFFLINE','runtime':'NOT RUN','materials':mats,'private_texture_hashes':{p.name:hashlib.sha256(p.read_bytes()).hexdigest()for p in dest.glob('*.dds')},'limitations':['UV0 preserved; Unreal multichannel layering and RGB paint-mask function not transferred','Source normal maps retained and renormalized; neutral roughness/metallic approximation','Source alpha/decal card geometry excluded instead of importing incorrect opaque cards','Source84kPDC not used; six proven677-triangle mounts substituted at measured exposed surfaces']});meta=json.loads((A/'integration-spec.json').read_text());meta['status']='PASS OFFLINE MESH/MATERIAL/SAMPLED ARC; RUNTIME NOT RUN';meta['compiled_files']={str(p.relative_to(B/'game')):hashlib.sha256(p.read_bytes()).hexdigest()for p in(B/'game').rglob('*')if p.is_file()};write(A/'integration-spec.json',meta);print('Materials and actual geometry previews complete')
