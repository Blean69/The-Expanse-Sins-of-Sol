"""Only spatial/mount/muzzle/magazine positions follow the15% art enlargement."""
from pathlib import Path
import copy,json
ROOT=Path(__file__).resolve().parents[1]
def changes(base):
 base=Path(base);meta=json.loads((ROOT/'audit/update27-mars-laconia/storm-integration.json').read_text());scale=meta['scale'];edits={};origins={};n='expanse24_gathering_storm';u=json.loads((base/'entities'/(n+'.unit')).read_text());u['spatial']=copy.deepcopy(meta['spatial'])
 for m in u['weapons']['weapons']:
  if 'weapon_position'in m:m['weapon_position']=[v*scale for v in m['weapon_position']]
  if 'non_turret_muzzle_positions'in m:m['non_turret_muzzle_positions']=[[v*scale for v in p]for p in m['non_turret_muzzle_positions']]
 edits['entities/'+n+'.unit']=u;origins['entities/'+n+'.unit']=str(base/'entities'/(n+'.unit'))
 aid=n+'_light_magazine';a=json.loads((base/'entities'/(aid+'.ability')).read_text())
 for p in a['ability_positions']:p['position']=[v*scale for v in p['position']]
 edits['entities/'+aid+'.ability']=a;origins['entities/'+aid+'.ability']=str(base/'entities'/(aid+'.ability'))
 for mount in u['weapons']['weapons']:
  if '_pdc_'not in mount['weapon']:continue
  rid=mount['weapon'];w=json.loads((base/'entities'/(rid+'.weapon')).read_text());rig=next(r for r in meta['rigs']if r['mesh_point']==mount['mesh_point']);w['turret']=copy.deepcopy(rig['turret_override']);edits['entities/'+rid+'.weapon']=w;origins['entities/'+rid+'.weapon']=str(base/'entities'/(rid+'.weapon'))
 skin=json.loads((base/'entities'/(n+'.unit_skin')).read_text())
 for alias in skin['skin_stages'][0]['child_mesh_alias_bindings']['map']:
  for kind in ['base','barrel']:
   if alias['mesh_alias_name']=='expanse24_storm_pdc_'+kind:alias['mesh_alias_name']='expanse27_storm_pdc_'+kind;alias['mesh_definition']['mesh']='expanse27_storm_pdc_'+kind
 edits['entities/'+n+'.unit_skin']=skin;origins['entities/'+n+'.unit_skin']=str(base/'entities'/(n+'.unit_skin'))
 report={'scale':scale,'changed_fields':['unit.spatial','unit.weapons.weapons[].weapon_position','unit.weapons.weapons[].non_turret_muzzle_positions','light_magazine.ability_positions[].position','sixPDC.turret private mesh names and scaled barrel/muzzle offsets','unit_skin PDC alias bindings'],'unchanged':'All movement,damage,timings,ammo,price,limits,research and firing arcs','runtime':'NOT RUN'}
 return edits,{},origins,report
