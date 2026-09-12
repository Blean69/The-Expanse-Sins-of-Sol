"""Run installed official MeshBuilder + local Texconv. No game/prefix edits.
Windows: omit --wine. Linux: --wine /absolute/path/to/Proton/files/bin/wine64.
"""
from common import *
import argparse, subprocess

p=argparse.ArgumentParser();p.add_argument('--wine',type=Path);p.add_argument('--skip-textures',action='store_true');args=p.parse_args()
env=dict(os.environ,OMP_NUM_THREADS='4',MANGOHUD='0')
if args.wine:env.update(WINEPREFIX=str(ROOT/'.tools/proton-prefix'),WINEDEBUG='-all',DISPLAY='',WINEDLLOVERRIDES='mscoree,mshtml=')
def windows_path(path):return 'Z:'+str(path) if args.wine else str(path)
def run(exe,arguments,log):
    cmd=([str(args.wine)] if args.wine else [])+[str(exe)]+arguments
    with log.open('w') as h:
        h.write('COMMAND '+json.dumps(cmd)+'\n');h.flush()
        subprocess.run(cmd,env=env,stdout=h,stderr=subprocess.STDOUT,check=True,timeout=300)
for form in ['json','binary']:
    out=ROOT/'build'/('compiler-'+form);out.mkdir(parents=True,exist_ok=True)
    run(SDK/'MeshBuilder/bin/MeshBuilder.exe',['--input_path='+windows_path(ROOT/'assets/derived/baseline/mcrn_corvette_baseline.gltf'),'--output_folder_path='+windows_path(out),'--mesh_output_format='+form,'--fill_triangle_facing_grid'],ROOT/'audit'/('meshbuilder-'+form+'.log'))
    print('Compiled',form,flush=True)
if not args.skip_textures:
    out=ROOT/'build/converted-textures';out.mkdir(exist_ok=True)
    for png in sorted((ROOT/'assets/derived/baseline/game-textures').glob('*.png')):
        normal=png.stem.endswith('_nrm');fmt='BC5_SNORM' if normal else 'BC7_UNORM'
        options=['--x2-bias'] if normal else ['-bc','q']
        run(ROOT/'.tools/texconv.exe',['-f',fmt,'-y','-m','0','-nogpu','--single-proc','-o',windows_path(out)]+options+[windows_path(png)],ROOT/'audit'/('texconv-'+png.stem+'.log'))
        print('Converted',png.name,flush=True)
