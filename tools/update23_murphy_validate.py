"""Offline integration checks for Murphy art, including outward PDC firing sweeps."""
from pathlib import Path
import hashlib,json,sys
import numpy as np
from common import read,read_mesh,write
ROOT=Path(__file__).resolve().parents[1];AUD=ROOT/'audit/update23-murphy';meta=read(AUD/'integration-spec.json');GAME=Path(meta['output_game']);samples=0;min_clearance=1e9
for rig in meta['rigs']:
 up=np.array(rig['up']);pos=np.array(rig['position']);B=np.column_stack([np.cross(up,rig['forward']),up,rig['forward']]);turret=rig['turret_override'];barrel=np.array(turret['barrel_position']);muzzle=np.array(turret['muzzle_positions'][0])
 for pitch in np.linspace(-85,0,18):
  a=np.deg2rad(pitch);R=np.array([[1,0,0],[0,np.cos(a),-np.sin(a)],[0,np.sin(a),np.cos(a)]])
  for yaw in np.linspace(-180,180,73):
   a=np.deg2rad(yaw);Y=np.array([[np.cos(a),0,np.sin(a)],[0,1,0],[-np.sin(a),0,np.cos(a)]]);direction=B@Y@R@np.array([0,0,1]);offset=B@Y@(barrel+R@muzzle);clearance=rig['outward_hull_plane_clearance']+np.dot(offset,up);assert np.dot(direction,up)>=-1e-8 and clearance>0;min_clearance=min(min_clearance,clearance);samples+=1
# Regular explicit game files only. Stock effect resources are resolved without copying game data.
for p in GAME.rglob('*'):assert not p.is_symlink(),p
for path,expected in meta['files'].items():assert hashlib.sha256((GAME/path).read_bytes()).hexdigest()==expected,path
materials=set()
for p in(GAME/'meshes').glob('*.mesh'):materials.update(read_mesh(p)['materials'])
for name in materials:
 p=GAME/'mesh_materials'/(name+'.mesh_material');assert p.is_file()
 for key,value in read(p).items():
  if key.endswith('_texture'):assert(GAME/'textures'/(value+'.dds')).is_file(),value
native=Path('/run/media/haker/NVME 2/SteamLibrary/steamapps/common/Sins2');effect=read(GAME/'effects/expanse23_murphy_idle_plume.particle_effect');resources={}
def visit(a):
 if isinstance(a,dict):
  for k,v in a.items():
   if isinstance(v,str)and(k in ['texture_0','texture_1','texture_2']or k.endswith('_texture'))and v:
    hits=[p for folder in[native/'textures',native/'brushes',GAME/'textures']for p in folder.glob(v+'.*')if p.is_file()];assert hits,(k,v);resources[v]=str(hits[0])
   visit(v)
 elif isinstance(a,list):
  for v in a:visit(v)
visit(effect)
write(AUD/'offline-validation.json',{'status':'PASS OFFLINE','compiled_model_triangle_count':meta['counts']['assembled'],'firing_ray_sweep_samples':samples,'minimum_muzzle_clearance_from_global_hull_plane':float(min_clearance),'scope':'Analytical outward hemisphere rays in the accepted negative-pitch convention. Does not prove game target acquisition, rig attachment, or particle appearance.','material_and_texture_dependencies_resolved':True,'particle_stock_resources':resources,'all_packaged_files_match_hashes':True,'symlinks':0,'runtime_cases_not_run':['target acquisition and interpolation','allied/enemy target filters','visible firing/mount tracking','PDC own-hull obstruction in engine','save/reload','multiplayer','plume appearance']});print('PASS',samples,'outward firing samples; game runtime not run')
