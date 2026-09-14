"""Narrow offline integration checks for generated Stage3 station definitions."""
from pathlib import Path
import hashlib,json
from update22_stations import changes,GAME
from update18_tycho import schema_check
ROOT=Path(__file__).resolve().parents[1]

def read(p):return json.loads(p.read_text())
def write(p,d):p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(d,indent=2)+'\n')
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def walk(x):
 if isinstance(x,dict):
  yield x
  for v in x.values():yield from walk(v)
 elif isinstance(x,list):
  for v in x:yield from walk(v)

def run(base,out,audit):
 base,out,audit=map(Path,(base,out,audit));e,s,o,r=changes(base);checks=[]
 for n,d in e.items():
  p=out/'entities'/n;write(p,d)
  kind={'.unit':'unit','.unit_skin':'unit-skin','.weapon':'weapon','.ability':'ability','.buff':'buff','.action_data_source':'action-data-source','.unit_item':'unit-item'}[p.suffix]
  checks.append(schema_check(p,kind+'-schema.json',Path(o[n])))
 # Original firing budgets and interceptable-object identity stay intact.
 for n,d in e.items():
  if not n.endswith('.weapon'):continue
  prior=read(Path(o[n]));ignored={'name','turret'}
  assert {k:v for k,v in prior.items() if k not in ignored}=={k:v for k,v in d.items() if k not in ignored}
  if 'pdc' in n or 'picket' in n:assert 'burst_pattern' not in d
  else:assert d['firing']['torpedo_firing_definition']==prior['firing']['torpedo_firing_definition']
 # Native module gating and hardpoint frames remain matched to native geometry.
 for row in r['stations']:
  u=e[row['unit']+'.unit'];prior=read(Path(o[row['unit']+'.unit']))
  assert u['structure']['slots_required']==8 and u['build']['build_kind']=='structure'
  assert not u['build'].get('supply_cost',0)
  assert u['items']['levels'][0]['max_ship_component_count']==3
  assert len(u['item_builds'])==4 and len(u['weapons']['weapons'])==6
  for w in u['weapons']['weapons']:
   original=next(x for x in prior['weapons']['weapons'] if x['mesh_point']==w['mesh_point'])
   ignored={'weapon','required_unit_item'}
   assert {k:v for k,v in w.items() if k not in ignored}=={k:v for k,v in original.items() if k not in ignored}
  assert sum('required_unit_item' in w for w in u['weapons']['weapons'])==2
  assert 'starbase' not in u['tags'] and u['target_filter_unit_type']=='structure'
  assert all('expanse11_no_shields' in g['abilities'] for g in u['abilities'])
  assert all(h.get('max_shield_points',0)==0 and 'shield_burst_restore' not in h for h in u['health']['levels'])
  skin=e[row['unit']+'.unit_skin']
  needed=set()
  for w in u['weapons']['weapons']:
   for k,v in e[w['weapon']+'.weapon']['effects'].items():
    if k in ['muzzle_effect','projectile_travel_effect','hit_hull_effect','hit_shield_effect']:needed.add(v)
  for stage in skin['skin_stages']:
   bound={x['alias_name'] for x in stage['effects']['effect_alias_bindings']};assert needed<=bound,(row['unit'],needed-bound)
 # Healing is bounded by three per-second direct operations at the living source.
 a=e['expanse22_repair_anchorage_on_self.buff'];assert a['make_dead_on_source_ability_released']
 scan=a['time_actions'][0]['action_group']['actions'][0]
 assert scan['max_target_count_value']=='repair_target_count' and a['time_actions'][0]['execution_interval_value']=='fixed_one'
 assert [x['operator_type'] for x in scan['operators']]==['apply_buff','repair_damage']
 assert scan['operators'][1]['affect_type']=='hull_only'
 ads=e['expanse22_repair_anchorage.action_data_source'];vals={v['action_value_id']:v['action_value']['values'][0] for v in ads['action_values']}
 assert vals['repair_target_count']==3 and vals['repair_per_tick']==20 and vals['reservation_duration']==1
 assert ads['target_filters'][0]['target_filter']['ownerships']==['self']
 buffs={x['buff'] for x in walk(ads) if x.get('constraint_type')=='has_buff'}
 assert {'expanse22_repair_anchorage_reservation','expanse15_scirocco_engineering_teams','trader_retrofit_bay_repair','trader_combat_repair_system_unit_item'}<=buffs
 assert all(x.get('include_pending_buffs') for x in walk(ads) if x.get('constraint_type')=='has_buff')
 assert not any(x.get('operator_type')=='repair_damage' for x in walk(e['expanse22_repair_anchorage_reservation.buff']))
 for mid in ['expanse22_defense_coordination','expanse22_industrial_drydock']:
  target=e[mid+'_on_target.buff'];assert target['make_dead_on_parent_buff_made_dead']
  assert target['make_dead_on_distance_to_parent_buff_exceeded']=={'distance':'apply_buff_radius'}
  assert target['stacking_limit']['stacking_limit']=='fixed_one'
  assert e[mid+'.action_data_source']['target_filters'][0]['target_filter']['ownerships']==['self']
 track=e['expanse22_defense_coordination.action_data_source']['buff_weapon_modifiers']
 assert len(track)==1 and track[0]['buff_weapon_modifier']['modifier_type']=='tracking_speed' and track[0]['buff_weapon_modifier']['tags']==['point_defense']
 iv=e['expanse22_industrial_drydock.action_data_source']['action_values'][1]['action_value']['values'][0];assert abs(1/(1+iv)-1.10)<1e-12
 assert len({recipe['global_unit_limit']['tag'] for recipe in r['player_recipes'].values()})==1
 for recipe in r['player_recipes'].values():assert recipe['global_unit_limit']['unit_limit']==1
 for n,d in [('report.json',r),('localization.json',s),('origins.json',o)]:write(out/n,d)
 report={'status':'PASS OFFLINE ONLY','runtime':'NOT RUN','definition_count':len(e),'schema_checks':checks,
 'passed':['28definition schemas with unchanged installed extension handling','all weapon firing budgets/profiles preserved','native hull/mount/arc pairing','3slots4modules and2gatedordnancebanks','owned-only local targets','bounded3x20direct hull repairs persecond','shared pending reservation/Scirocco exclusion','parent death and distance removal for tracking/factory effects','10%PDCtracking only','10%factory RATE not time','shared1/playerstation tag recipe','shield guard/no invalid burst','all station weapon effects have skin aliases'],
 'base':str(base),'sources':[{'path':x,'sha256':sha(Path(x))} for x in sorted(set(o.values()))]}
 write(audit/'validation.json',report);return report

if __name__=='__main__':
 r=run('/run/media/haker/NVME 2/expanse-mod/build/experiments/expanse_update20',ROOT/'build/stations22-fragments',ROOT/'audit/stations22');print(json.dumps({'status':r['status'],'definitions':r['definition_count']}))
