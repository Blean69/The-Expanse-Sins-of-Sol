"""Freeze read-only 27.5 mechanics and generate comparison evidence for update28."""
from pathlib import Path
from collections import defaultdict,Counter
import argparse,csv,hashlib,json,subprocess

IDS={
 'Truman':'expanse15_truman','Donnager':'expanse_donnager_battleship',
 'Scirocco':'expanse12_scirocco','Tachi':'expanse_mcrn_corvette',
 'Rocinante':'expanse_rocinante_hero','Pella':'expanse12_pella',
 'Hephaestus':'expanse27_hephaestus','Raptor':'expanse12_raptor',
 'Razorback':'trader_scout_corvette','Foehammer':'expanse22_foehammer_battery',
 'Nathan Hale':'expanse27_nathan_hale','OPA expeditionary':'expanse21_opa_command'}
FACTIONS=['expanse18_mcrn','expanse18_unn','expanse18_opa','trader_loyalist','trader_rebel','dlc_trader_loyalist']
RELEVANT_MODIFIERS={'damage','cooldown_duration','tracking_speed','range','max_hull_points','max_armor_points','armor_strength','durability','max_linear_speed','max_angular_speed','hyperspace_charge_time','unit_build_rate','unit_build_cost','unit_build_price','max_supply'}

def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def walk(x,path=()):
 yield path,x
 if isinstance(x,dict):
  for k,v in x.items():yield from walk(v,path+(k,))
 elif isinstance(x,list):
  for i,v in enumerate(x):yield from walk(v,path+(i,))
def ptr(path):return '/'+ '/'.join(map(str,path))
def strings(x):return [v for _,v in walk(x)if isinstance(v,str)]
def dump(p,x):p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(x,indent=2,ensure_ascii=False)+'\n')

def main():
 ap=argparse.ArgumentParser();ap.add_argument('--base',type=Path,required=True);ap.add_argument('--game',type=Path,required=True);ap.add_argument('--output',type=Path,required=True);a=ap.parse_args()
 if (a.output/'frozen-snapshot.json').exists():raise SystemExit('Snapshot already exists; choose a new output, never overwrite the frozen input.')
 files={}
 for root in [a.game,a.base]:
  for sub in ['entities','uniforms']:
   for p in (root/sub).glob('*'):
    if p.is_file():files[(sub+'/'+p.name).lower()]=p
 cache={};touched={}
 def get(rel):
  p=files[rel.lower()]
  if p not in cache:cache[p]=json.loads(p.read_text(encoding='utf-8-sig'))
  touched[str(p)]={'sha256':sha(p),'package_override':p.is_relative_to(a.base)}
  return cache[p]
 def ent(n,ext):return get('entities/'+n+'.'+ext)
 players={n:ent(n,'player')for n in FACTIONS}
 # Resolve literal acquisition references rather than assuming the class menu is sufficient.
 reverse=defaultdict(list);modifiers=[];factories=[]
 for rel,p in files.items():
  if p.suffix not in {'.unit','.player','.buff','.ability','.action_data_source','.research_subject','.unit_item'}:continue
  j=get(rel)
  if p.suffix=='.unit' and 'unit_factory'in j:factories.append({'unit':p.stem,'build':j.get('build'),'factory':j['unit_factory']})
  for path,v in walk(j):
   if isinstance(v,str)and v in IDS.values():reverse[v].append({'file':rel,'pointer':ptr(path),'scope':'menu_display_only'if 'menu27'in p.stem or 'theme_picker'in str(path)else'candidate_gameplay_reference'})
   if p.suffix in {'.research_subject','.action_data_source','.buff','.unit_item'} and isinstance(v,dict)and v.get('modifier_type')in RELEVANT_MODIFIERS:
    if p.is_relative_to(a.base)or p.stem.startswith('trader_'):
     modifiers.append({'file':rel,'pointer':ptr(path),'modifier':v,'action_values':j.get('action_values',[]),'player_research_membership':[n for n,x in players.items()if p.stem in strings(x.get('research',{}))]})
 units={};rows=[];mechanisms={}
 for label,uid in IDS.items():
  u=ent(uid,'unit');mounts=u.get('weapons',{}).get('weapons',[]);weapons=[];groups=defaultdict(list)
  for k,m in enumerate(mounts):
   w=ent(m['weapon'],'weapon');kind='rail'if 'rail_gun'in w.get('tags',[])else'pdc'if 'point_defense'in w.get('tags',[])else'other'
   record={'mount_index':k,'mount':m,'definition':w,'kind':kind,'muzzle_count':len(w.get('turret',{}).get('muzzle_positions',m.get('non_turret_muzzle_positions',[]))), 'configured_damage_budget':w.get('damage'),'configured_cooldown':w.get('cooldown_duration'),'nominal_raw_damage_per_second':w['damage']/w['cooldown_duration']if w.get('cooldown_duration',0)>0 and 'damage'in w else None,'top_level_damage_burst':w.get('burst_pattern'),'visual_burst_only':w.get('effects',{}).get('burst_pattern'),'additional_damage_actions':[{'pointer':ptr(p),'value':v}for p,v in walk(w)if isinstance(v,dict)and v.get('operator_type')in ['apply_damage','create_torpedo']]}
   weapons.append(record);groups[kind].append(record)
  abilities=[n for g in u.get('abilities',[])for n in g.get('abilities',[])]+([u['colonize_ability']]if isinstance(u.get('colonize_ability'),str)else[])
  queue=[(n,'ability')for n in abilities];seen=set();mechanic_ids=[];magazines=[]
  while queue:
   n,ext=queue.pop();rel='entities/'+n+'.'+ext
   if rel in seen or rel.lower()not in files:continue
   seen.add(rel);j=get(rel);mechanisms[rel]=j;mechanic_ids.append(rel)
   if ext=='action_data_source':
    values={v['action_value_id']:v['action_value']for v in j.get('action_values',[])}
    if 'magazine_capacity_value'in values:
     bf=ent(n,'buff')if ('entities/'+n+'.buff').lower()in files else{}
     creates=[{'pointer':ptr(p),'operator':v}for p,v in walk(bf)if isinstance(v,dict)and v.get('operator_type')=='create_torpedo']
     counts={key:values[key].get('values')for key in values if key in ['magazine_capacity_value','magazine_pair_count_value','magazine_pair_interval_value','magazine_reload_duration_value','heavy_torpedo_damage_value','heavy_torpedo_armor_penetration_value','heavy_torpedo_range_value','heavy_torpedo_torpedo_lifetime_value','heavy_torpedo_torpedo_speed_value']}
     projectile_ids=sorted({x['operator']['torpedo_to_create']for x in creates});projectiles={p:ent(p,'unit')for p in projectile_ids}
     magazines.append({'id':n,'values':counts,'actual_create_torpedo_operators':creates,'projectile_definitions':projectiles,'movement_order_gate_present':any(x=='is_attacking'or x=='is_moving'for x in strings(bf)),'notes':'Actual flight comes from projectile physics; ADS speed may be tooltip-only. Full buff retained for gate/ammo review.'})
   for path,v in walk(j):
    if not isinstance(v,str)or not path:continue
    key=path[-1]
    if key in ['buff','persistant_buff','action_data_source','ability']:
     targetext='buff'if key in ['buff','persistant_buff']else key
     queue.append((v,targetext))
  health=u.get('health',{});levels=health.get('levels',[{}]);levelmods=u.get('levels',{}).get('levels',[{}]);l1,lmax=levels[0],levels[-1]
  access={}
  for pn,p in players.items():
   access[pn]={'direct_buildable':uid in p.get('buildable_units',[])or uid in p.get('faction_buildable_units',[]),'structure_buildable':uid in p.get('structures',[]),'ability_created':uid in p.get('ability_created_units',[]),'free_first_kind':u.get('build',{}).get('build_kind')in p.get('starting_free_unit_build_kinds',[]),'prerequisites':u.get('build',{}).get('prerequisites',[]),'relevant_limits':{scope:[x for x in ll if x.get('tag')in u.get('tags',[])]for scope,ll in p.get('unit_limits',{}).items()}}
  rails=groups['rail'];first=sum(w['configured_damage_budget']for w in rails);dps=sum(w['nominal_raw_damage_per_second']for w in rails)
  dm=levelmods[-1].get('weapon_modifiers',{}).get('scalar_values',{});last_first=first*(1+dm.get('damage',0));last_dps=dps*(1+dm.get('damage',0))/(1+dm.get('cooldown_duration',0))
  units[uid]={'label':label,'definition':u,'access':access,'compatible_factories':[f for f in factories if u.get('build',{}).get('build_kind')in f['factory'].get('build_kinds',[])],'literal_references':reverse[uid],'weapons':weapons,'mechanism_files':sorted(mechanic_ids),'magazines':magazines,'duplicate_weapon_ids':{n:c for n,c in Counter(m['weapon']for m in mounts).items()if c>1},'duplicate_mount_points':{n:c for n,c in Counter(m.get('mesh_point')for m in mounts).items()if c>1},'rail_budget_summary':{'configured_instances':len(rails),'physical_muzzles':sum(w['muzzle_count']for w in rails),'level_1_nominal_opening':first,'level_1_nominal_dps':dps,'highest_level_nominal_opening':last_first,'highest_level_nominal_dps':last_dps,'notes':'Configured per-weapon damage budget, not multiplied by visual muzzles. Engine packet distribution/muzzle multiplicity not established offline. Highest-level table uses that level row once, not sum of prior rows.'}}
  price=u.get('build',{}).get('price',{});ph=u.get('physics',{})
  rows.append({'ship':label,'id':uid,'class':u.get('target_filter_unit_type'),'supply':u.get('build',{}).get('supply_cost'),'credits':price.get('credits',0),'metal':price.get('metal',0),'crystal':price.get('crystal',0),'build_seconds':u.get('build',{}).get('build_time'),'hull_L1':l1.get('max_hull_points'),'armor_L1':l1.get('max_armor_points'),'armor_strength_L1':l1.get('armor_strength'),'durability':health.get('durability'),'hull_highest':lmax.get('max_hull_points'),'armor_highest':lmax.get('max_armor_points'),'pdc_instances':len(groups['pdc']),'rail_instances':len(rails),'rail_muzzles':sum(w['muzzle_count']for w in rails),'rail_opening_L1_nominal':first,'rail_dps_L1_nominal':dps,'rail_opening_highest_nominal':last_first,'speed':ph.get('max_linear_speed'),'acceleration_time':ph.get('time_to_max_linear_speed'),'turn_speed':ph.get('max_angular_speed'),'turn_acceleration_time':ph.get('time_to_max_angular_speed'),'attack_pattern':u.get('attack',{}).get('attack_pattern',{}).get('type'),'jump_charge':u.get('hyperspace',{}).get('charge_time')})
 snapshot={'status':'READ-ONLY FROZEN NUMERICAL INPUT; runtime NOT RUN','base':str(a.base),'source_commit':subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip(),'mod_metadata':get('.mod_meta_data')if '.mod_meta_data'in files else json.loads((a.base/'.mod_meta_data').read_text()),'unit_ids':IDS,'units':units,'mechanisms':mechanisms,'modifier_candidates':modifiers,'players':{n:{k:p[k]for k in ['buildable_units','structures','ability_created_units','starting_free_unit_build_kinds','unit_limits','max_supply','research']if k in p}for n,p in players.items()},'read_source_hashes':touched,'limitations':['No game launch. Literal references distinguish acquisition from display but require semantic access checks.','Definitions establish configured damage pipeline, not observed per-muzzle event count.','Health pools exclude durability/armor mitigation, disable thresholds, regeneration and research/aura effects.']}
 dump(a.output/'frozen-snapshot.json',snapshot)
 with (a.output/'baseline-table.csv').open('w',newline='')as f:
  wr=csv.DictWriter(f,fieldnames=list(rows[0]));wr.writeheader();wr.writerows(rows)
 dump(a.output/'snapshot-sha256.json',{'frozen-snapshot.json':sha(a.output/'frozen-snapshot.json'),'baseline-table.csv':sha(a.output/'baseline-table.csv')})
 print(json.dumps({'units':len(units),'weapons':sum(len(x['weapons'])for x in units.values()),'mechanisms':len(mechanisms),'modifier_candidates':len(modifiers),'read_sources':len(touched),'output':str(a.output)}))

if __name__=='__main__':main()
