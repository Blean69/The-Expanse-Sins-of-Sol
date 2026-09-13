"""Reproduce the separate higher-detail Donnager candidate from frozen dependencies.
Never replaces an existing candidate, installed mod, original asset, or SDK.
"""
from update11_donnager_common import *
import argparse
import shutil
import subprocess
import sys

def main():
 parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--sdk',type=Path,default=Path('/run/media/haker/NVME 2/SteamLibrary/steamapps/common/Sins of a Solar Empire II - Mod Tools'));parser.add_argument('--wine',type=Path,default=Path('/home/haker/.var/app/com.valvesoftware.Steam/.local/share/Steam/steamapps/common/Proton 10.0/files/bin/wine64'));args=parser.parse_args()
 for p in [SOURCE,FROZEN/'audit/donnager10-b/integration-spec.json',FROZEN/'assets/derived/polish-b/expanse_polish_pdc_0_base.gltf',FROZEN/'build/polish-b/proton-prefix',args.sdk/'MeshBuilder/bin/MeshBuilder.exe',args.wine,Path('/run/media/haker/NVME 2/expanse-mod/.tools/libmeshoptimizer.so')]:
  if not p.exists():raise FileNotFoundError('Missing required ignored/read-only dependency: '+str(p))
 for p in [OUT,AUDIT,BUILD]:
  if p.exists():raise FileExistsError('Refusing to overwrite existing higher-detail candidate: '+str(p))
 for p in [OUT,AUDIT,BUILD]:p.mkdir(parents=True)
 preserved=[p for folder in ['audit/donnager10-b','assets/derived/donnager10-b','build/donnager10-b/game'] for p in (FROZEN/folder).rglob('*') if p.is_file()];write(AUDIT/'preservation-before.json',{str(p):hashlib.sha256(p.read_bytes()).hexdigest() for p in preserved})
 for name in ['layout-candidates.json','main-equipment.json']:shutil.copyfile(FROZEN/'audit/donnager10-b'/name,AUDIT/name)
 layout=read(AUDIT/'layout-candidates.json');layout['pdc_mounts'][15]['support']['bottom']-=.6;write(AUDIT/'layout-candidates.json',layout)
 write(AUDIT/'support-correction.json',{'reason':'Restored higher-fidelity hull is0.473 units lower at one PDC15 footprint; extend fixedsocket into hull while all gunpivots remain unchanged','mount_index':15,'fixed_socket_bottom_delta':-.6,'gun_transform_delta':0,'maximum_restored_hull_footing_embed':.44934651455,'no_moving_geometry_removed':True})
 def run(name,*extra):subprocess.run([sys.executable,str(ROOT/'tools'/('update11_donnager_'+name+'.py')),*map(str,extra)],env=dict(os.environ,OPENBLAS_NUM_THREADS='1'),check=True)
 for name in ['probe','normals','prepare','editable']:run(name)
 for name in ['compile','winding']:run(name,'--sdk',args.sdk,'--wine',args.wine)
 for name in ['finish','materials','mount_checks','silhouette','uv_check']:run(name)
 run('ui','--source',OUT/'update11_donnager_editable.gltf','--expected-triangles',194296,'--game','/run/media/haker/NVME 2/SteamLibrary/steamapps/common/Sins2','--sdk',args.sdk)
 run('handoff')

if __name__=='__main__':main()
