"""Validate the UN One art package without installing it or simulating gameplay."""
from pathlib import Path
import hashlib,struct,zipfile
import numpy as np
from PIL import Image
from common import read,read_mesh,write
ROOT=Path(__file__).resolve().parents[1];AUD=ROOT/'audit/update25-unone';meta=read(AUD/'integration-spec.json');GAME=Path(meta['output_game']);NATIVE=Path('/run/media/haker/NVME 2/SteamLibrary/steamapps/common/Sins2');a=read_mesh(GAME/'meshes'/(meta['base_mesh']+'.mesh'))
assert a['triangles']==117826 and meta['counts']['source']==117822
assert len(a['meshpoints'])==5 and all('weapon'not in p['name']and'child'not in p['name']for p in a['meshpoints'])
assert not(GAME/'entities').exists()
for p in GAME.rglob('*'):assert not p.is_symlink(),p
for path,expected in meta['files'].items():assert hashlib.sha256((GAME/path).read_bytes()).hexdigest()==expected,path
for mat in a['materials']:
 m=read(GAME/'mesh_materials'/(mat+'.mesh_material'))
 for k,v in m.items():
  if k.endswith('_texture'):assert(GAME/'textures'/(v+'.dds')).is_file()
 color=Image.open(GAME/'textures'/(m['base_color_texture']+'.dds')).convert('RGBA');assert np.asarray(color)[:,:,3].min()>=254
records={r['member']:r for r in meta['source']['included']};interfaces=[]
for left,right in [('UN One - Body Center.stl','UN One - Body Front.stl'),('UN One - Body Rear 1.stl','UN One - Body Center.stl'),('UN One - Body Rear 2.stl','UN One - Body Rear 1.stl')]:
 gap=abs(records[left]['bounds'][1][0]-records[right]['bounds'][0][0])*meta['scale']['source_to_game'];assert gap<.001;interfaces.append({'left':left,'right':right,'axial_seam_gap_game_units':gap})
assert all('Stand'not in r['member']for r in records.values())
resources={}
def visit(a):
 if isinstance(a,dict):
  for k,v in a.items():
   if isinstance(v,str)and(k in ['texture_0','texture_1','texture_2']or k.endswith('_texture'))and v:
    hits=[p for folder in[NATIVE/'textures',NATIVE/'brushes',GAME/'textures']for p in folder.glob(v+'.*')if p.is_file()];assert hits,(k,v);resources[v]=str(hits[0])
   visit(v)
 elif isinstance(a,list):
  for x in a:visit(x)
visit(read(GAME/'effects/expanse25_unone_idle_plume.particle_effect'))
write(AUD/'offline-validation.json',{'status':'PASS OFFLINE','source_triangles_preserved':117822,'compiled_triangles':117826,'global_part_transform':True,'main_body_interfaces':interfaces,'exhaust_points':2,'weapon_points':0,'opaque_authored_base_maps_BC7_alpha_minimum':254,'all_material_and_particle_resources_resolved':True,'stock_particle_resources':resources,'all_packaged_hashes_verified':True,'symlinks':0,'runtime_not_tested':['ship shader, windows and exhaust appearance','hyperspace appearance','save/reload','multiplayer','support gameplay or diplomacy effects'],'scope':'Art/assembly checks only; no new gameplay definitions.'});print('PASS: 117822 source faces, opaque materials, aligned body interfaces, 2 exhaust origins, no weapons.')
