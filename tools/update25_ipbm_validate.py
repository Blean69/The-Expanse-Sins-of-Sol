"""Check the IPBM remains a visual-only replacement for native local bombing."""
from pathlib import Path
import copy,hashlib,json,struct
import numpy as np
from PIL import Image
from common import read,read_mesh,write
ROOT=Path(__file__).resolve().parents[1];AUD=ROOT/'audit/update25-ipbm';meta=read(AUD/'integration-spec.json');GAME=Path(meta['output_game']);NATIVE=Path('/run/media/haker/NVME 2/SteamLibrary/steamapps/common/Sins2');a=read_mesh(GAME/'meshes'/(meta['base_mesh']+'.mesh'))
assert a['triangles']==6000 and abs(meta['scale']['reference_length']-meta['scale']['game_length'])<1e-4
assert not(GAME/'entities').exists();assert all('weapon'not in p['name']and'child'not in p['name']for p in a['meshpoints'])
for path,expected in meta['files'].items():
 p=GAME/path;assert p.is_file()and not p.is_symlink();assert hashlib.sha256(p.read_bytes()).hexdigest()==expected
for name in a['materials']:
 m=read(GAME/'mesh_materials'/(name+'.mesh_material'))
 for k,v in m.items():
  if k.endswith('_texture'):assert(GAME/'textures'/(v+'.dds')).is_file()
 assert np.asarray(Image.open(GAME/'textures'/(m['base_color_texture']+'.dds')).convert('RGBA'))[:,:,3].min()>=254
source=read(NATIVE/'effects/Weapon_TechFrigatePlanetBombing_Travel.particle_effect');target=read(GAME/'effects/expanse25_ipbm_local_bombardment_travel.particle_effect');reverse=copy.deepcopy(target);e=next(e for e in reverse['emitters']if e['particle']['type']=='mesh');assert e['particle']['mesh']['mesh']==meta['base_mesh'];e['particle']['mesh']['mesh']='weapon_trader_missile_nuke';node_id=next(x['attachee_id']for x in reverse['emitter_to_node_attachments']if x['attacher_id']==e['id']);next(x for x in reverse['nodes']if x['id']==node_id)['z']=next(x for x in source['nodes']if x['id']==node_id)['z'];assert reverse==source
weapon=read(NATIVE/'entities/trader_siege_frigate_planet_bombing.weapon');assert weapon['weapon_type']=='planet_bombing'and weapon['firing']['firing_type']=='projectile'
skin=read(NATIVE/'entities/trader_siege_frigate.unit_skin');bindings=skin['skin_stages'][0]['effects']['effect_alias_bindings'];alias=next(x for x in bindings if x['alias_name']==weapon['effects']['projectile_travel_effect']);assert alias['alias_binding']['particle_effect'].lower()=='weapon_techfrigateplanetbombing_travel'
resources={}
def visit(a):
 if isinstance(a,dict):
  for k,v in a.items():
   if isinstance(v,str)and(k in ['texture_0','texture_1','texture_2']or k.endswith('_texture'))and v:
    hits=[p for folder in[NATIVE/'textures',NATIVE/'brushes',GAME/'textures']for p in folder.glob(v+'.*')if p.is_file()];assert hits,(k,v);resources[v]=str(hits[0])
   visit(v)
 elif isinstance(a,list):
  for x in a:visit(x)
visit(target)
write(AUD/'offline-validation.json',{'status':'PASS OFFLINE','mesh_triangles':6000,'visual_length_matches_existing_torpedo':True,'source_degenerate_cleanup':{'zero_area':1584,'numerical_slivers':64},'material_and_particle_resources_resolved':True,'stock_particle_resources':resources,'native_local_planet_bombing_chain_verified':True,'effect_changed_fields':['mesh emitter particle.mesh.mesh','mesh emitter attachment node z for the new centered model'],'no_gameplay_definitions_in_package':True,'all_packaged_hashes_verified':True,'scope':'Cosmetic travel mesh only. No actual destructible projectile entity, new damage, range, cooldown, targeting, global launch, or interception behavior.','runtime_not_tested':['visual scale and orientation during bombardment','particle appearance and lifetime','save/reload','multiplayer'],'strategic_acceptance_test':'Not applicable: this is not a strategic impactor prototype. Destroying the visible mesh cannot be claimed to cancel damage.'});print('PASS: native local bombing effect chain, only mesh/offset edits, 6000 triangles, matched torpedo scale, no gameplay.')
