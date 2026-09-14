"""Tune numeric ORM channels without recompiling the validated mesh geometry."""
from pathlib import Path
import os,sys,subprocess,hashlib
from PIL import Image
MAIN=Path('/run/media/haker/NVME 2/expanse-mod');sys.path.insert(0,str(MAIN/'tools'))
from common import read,write
ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'assets/derived/update26-storm';BUILD=ROOT/'build/update26-storm';GAME=BUILD/'game';AUD=ROOT/'audit/update26-storm';meta=read(AUD/'integration-spec.json')
WINE=Path('/home/haker/.var/app/com.valvesoftware.Steam/.local/share/Steam/steamapps/common/Proton 10.0/files/bin/wine64');PREFIX=Path('/run/media/haker/NVME 2/expanse-workers/tachi-one-pdc/build/polish-b/proton-prefix');env=dict(os.environ,WINEPREFIX=str(PREFIX),OMP_NUM_THREADS='1',MANGOHUD='0',WINEDEBUG='-all',DISPLAY='',WINEDLLOVERRIDES='mscoree,mshtml=')
for label in meta['colors']:
 stem='expanse24_storm_'+label+'_orm';p=OUT/'textures'/(stem+'.png');Image.new('RGBA',(16,16),(255,round(.55*255),round(.28*255),255)).save(p)
 with (BUILD/(stem+'-finish.log')).open('w')as log:subprocess.run([str(WINE),str(MAIN/'.tools/texconv.exe'),'-f','BC7_UNORM','-y','-m','0','-nogpu','--single-proc','-o','Z:'+str(GAME/'textures'),'-bc','q','Z:'+str(p)],env=env,stdout=log,stderr=subprocess.STDOUT,check=True,timeout=120)
for p in OUT.glob('*.gltf'):
 g=read(p)
 for m in g['materials']:m['pbrMetallicRoughness'].update(metallicFactor=.28,roughnessFactor=.55)
 write(p,g)
meta['changes']=[s.replace('roughness0.80/metallic0.12','roughness0.55/metallic0.28')for s in meta['changes']];meta['material_finish']={'roughness':.55,'metallic':.28,'scope':'four crystalline hull regions; native drive textures unchanged','rationale':'Restrained reflectivity retains crystal-like contrast; hard face normals address triangular highlights.','preview_limit':'Software preview is diffuse only; game specular lighting not tested.'};meta['compiled_files']={str(p.relative_to(GAME)):hashlib.sha256(p.read_bytes()).hexdigest()for p in sorted(GAME.rglob('*'))if p.is_file()};write(AUD/'integration-spec.json',meta);print('Four ORM maps tuned; compiled mesh unchanged')
