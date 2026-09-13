from common import *
import argparse,subprocess,shutil
p=argparse.ArgumentParser();p.add_argument('--wine',type=Path,required=True);args=p.parse_args();out=ROOT/'assets/derived/torpedo05-b';build=ROOT/'build/torpedo05-b';dest=build/'game/textures';dest.mkdir(parents=True,exist_ok=True);env=dict(os.environ,WINEPREFIX=str(build/'proton-prefix'),OMP_NUM_THREADS='4',MANGOHUD='0',WINEDEBUG='-all',DISPLAY='',WINEDLLOVERRIDES='mscoree,mshtml=');texconv=Path('/run/media/haker/NVME 2/expanse-mod/.tools/texconv.exe');assert texconv.is_file()
for inp in sorted((out/'texture-sources').glob('*.png')):
 normal=inp.stem.endswith('_nrm');fmt='BC5_SNORM' if normal else 'BC7_UNORM';opt=['--x2-bias'] if normal else ['-bc','q'];cmd=[str(args.wine),str(texconv),'-f',fmt,'-y','-m','0','-nogpu','--single-proc','-o','Z:'+str(dest)]+opt+['Z:'+str(inp)]
 with (build/('texconv-'+inp.stem+'.log')).open('w') as log:subprocess.run(cmd,env=env,stdout=log,stderr=subprocess.STDOUT,check=True,timeout=120)
 dd=dest/(inp.stem+'.dds');assert dd.read_bytes()[:4]==b'DDS ';print(dd.name,flush=True)
matdir=build/'game/mesh_materials';matdir.mkdir(exist_ok=True);m=read(build/'compiler-json/expanse05_amun_torpedo.mesh_json')
for actual in m['materials']:
 source=actual.removeprefix('expanse05_amun_torpedo_');shutil.copy2(out/'materials'/(source+'.mesh_material'),matdir/(actual+'.mesh_material'))
