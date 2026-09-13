from common import *
import argparse,subprocess,shutil
p=argparse.ArgumentParser();p.add_argument('--sdk',type=Path,required=True);p.add_argument('--wine',type=Path,required=True);args=p.parse_args();out=ROOT/'assets/derived/geometry04-b';build=ROOT/'build/geometry04-b';prefix=build/'proton-prefix';build.mkdir(parents=True,exist_ok=True)
if not prefix.exists():shutil.copytree(ROOT/'build/polish-b/proton-prefix',prefix,symlinks=True)
env=dict(os.environ,WINEPREFIX=str(prefix),OMP_NUM_THREADS='4',MANGOHUD='0',WINEDEBUG='-all',DISPLAY='',WINEDLLOVERRIDES='mscoree,mshtml=')
for inp in sorted(out.glob('expanse04_*.gltf')):
 if 'editable' in inp.name:continue
 for fmt in ['json','binary']:
  dest=build/('compiler-'+fmt);dest.mkdir(exist_ok=True);cmd=[str(args.wine),str(args.sdk/'MeshBuilder/bin/MeshBuilder.exe'),'--input_path=Z:'+str(inp),'--output_folder_path=Z:'+str(dest),'--mesh_output_format='+fmt,'--fill_triangle_facing_grid']
  with (build/(inp.stem+'-'+fmt+'.log')).open('w') as log:subprocess.run(cmd,env=env,stdout=log,stderr=subprocess.STDOUT,check=True,timeout=300)
 print(inp.stem,flush=True)
