#!/usr/bin/env python3
"""Bounded shared TEC research overlay. Main integrator calls apply on fresh assembled candidate.
Installed data/pins are read only. No new player IDs or independent capture mechanics.
"""
import argparse, copy, hashlib, json
from pathlib import Path
import jsonschema

GAME=Path('/run/media/haker/NVME 2/SteamLibrary/steamapps/common/Sins2')
BASE=Path('/run/media/haker/NVME 2/expanse-mod/build/experiments/expanse_update14')
SHIP_TAGS=['frigate','cruiser','corvette','capital_ship','super_capital_ship','titan','starbase']
WARHEAD='trader_missile_weapon_damage_0'
MARINE='trader_upgrade_experience_gain_0'

def read(p):return json.loads(Path(p).read_text(encoding='utf-8-sig'))
def write(p,d):p=Path(p);p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(d,indent=2)+'\n')
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def mod(kind,value,tags=None):
 d={'modifier_type':kind,'value_behavior':'scalar','value':value}
 if tags is not None:d['tags']=tags
 return d

# Reuse existing node identity, UI placement and all economic/prerequisite fields.
SPECS=[
 ('trader_planet_health_restore_rate','Closed-Cycle Life Support','Owned planets recover health 5% faster. Empire-wide planetary effect; does not repair ships.', {'planet_modifiers':[mod('health_points_restore_rate',.05)]}),
 ('trader_structure_build_rate','Vacuum Construction Standards','Orbital structures at owned planets take 5% less time to build. Empire-wide; ship construction is unchanged.', {'planet_modifiers':[mod('structure_build_time',-.05)]}),
 ('trader_mining_track_crystal_rate_0','Ice-Hauler Contracts','Planetary mining-track crystal income increases by 5%, including its population component. Empire-wide; excludes orbital extractors.', {'planet_modifiers':[mod('mining_track_crystal_income_rate',.05),mod('mining_track_crystal_income_rate_per_population',.05)]}),
 ('trader_trade_port_income_rate_0','Epstein Freight Logistics','Trade credit, metal and crystal income increases by 5%. Empire-wide; escort speed and construction are unchanged.', {'empire_modifiers':[mod('trade_credits_income_rate',.05),mod('trade_metal_income_rate',.05),mod('trade_crystal_income_rate',.05)]}),
 ('trader_labor_negotiations','Modular Drydock Assembly','Corvettes, frigates and cruisers take 5% less time to build at owned factories. Capital ships and titans are unchanged.', {'unit_factory_modifiers':[dict(mod('build_time',-.05),build_kinds=['corvette','frigate','cruiser'])]}),
 ('trader_find_npc_explore','Deep-Survey Expeditions','Retains the existing one-time expedition grant of four Sunflare scouts and the existing exploration discovery behavior. No permanent speed or hull bonus.', {}),
 ('trader_max_hull_points_0','Compartmentalized Bulkheads','Ship and starbase maximum hull increases by 5%. Torpedoes and orbital structures receive no benefit from this node.', {'unit_modifiers':[mod('max_hull_points',.05,SHIP_TAGS)]}),
 ('trader_autocannon_weapon_damage_0','PDC Fire-Control Solutions','Point-defense weapon damage increases by 5%. Range, tracking, firing arcs and cadence are unchanged.', {'weapon_modifiers':[mod('damage',.05,['point_defense'])]}),
 (WARHEAD,'Compact Warhead Packages','Missile weapon damage and custom launched torpedo impact damage increase by 5%. Torpedo count, speed, health and reload schedules are unchanged.', {'weapon_modifiers':[mod('damage',.05,['missile'])]}),
 (MARINE,'Marine Assault Doctrine','Scirocco Marine Breaching Teams disrupt for 13 seconds instead of 12. Penalties and the 45-second protection window are unchanged. Does not change capture chance.', {'unit_modifiers':[]}),
 ('trader_max_hull_points_2','Combat Damage Control','Ship and starbase passive hull restoration increases by 5%. Existing combat repair delays remain. Combat Engineering Teams retains its fixed 400-point repair cap.', {'unit_modifiers':[mod('hull_point_restore_rate',.05,SHIP_TAGS)]}),
 ('trader_missile_weapon_armor','Reinforced Torpedo Casings','Owned torpedoes gain 5% maximum hull. Does not add armor or shields; PDC interception remains useful.', {'unit_modifiers':[mod('max_hull_points',.05,['torpedo'])]}),
 ('trader_improve_gauss_defense_cooldown','Railgun Thermal Management','Railgun weapon cooldowns decrease by 5%. Damage, penetration, firing arcs and tracking speed remain unchanged.', {'weapon_modifiers':[mod('cooldown_duration',-.05,['rail_gun'])]}),
]


def walk(x):
 if isinstance(x,dict):
  yield x
  for v in x.values():yield from walk(v)
 elif isinstance(x,list):
  for v in x:yield from walk(v)
def strings(x):
 if isinstance(x,str):yield x
 elif isinstance(x,dict):
  for v in x.values():yield from strings(v)
 elif isinstance(x,list):
  for v in x:yield from strings(v)
def resolve(base,game,name):
 p=base/'entities'/name
 return p if p.exists() else game/'entities'/name

def inventory(base,game):
 units={p.stem:read(p)for p in (base/'entities').glob('*.unit')if p.stem.startswith('expanse') or p.stem in {'trader_light_frigate','trader_scout_corvette'}}
 weapons={p.stem:read(p)for p in (base/'entities').glob('*.weapon')if p.stem.startswith('expanse')}
 return units,weapons

def matches(m,d):
 return (not m.get('tags') or bool(set(m['tags'])&set(d.get('tags',[])))) and (not m.get('weapon_type') or m['weapon_type']==d.get('weapon_type'))

def audit_existing(base,game):
 units,weapons=inventory(base,game)
 player=read(resolve(base,game,'trader_loyalist.player'))
 refs={v for v in strings(player['research'])if (game/'entities'/(v+'.research_subject')).exists() or (base/'entities'/(v+'.research_subject')).exists()}
 rows=[]
 for rid in sorted(refs):
  p=resolve(base,game,rid+'.research_subject');d=read(p);effects=[]
  for key,defs in [('unit_modifiers',units),('weapon_modifiers',weapons)]:
   for m in d.get(key,[]):
    affected=[n for n,u in defs.items()if matches(m,u)]
    if affected:effects.append({'category':key,'modifier':m,'affected_definitions':sorted(affected),'expectation':'Owner research modifier applies to matching definitions; actual runtime refresh requires existing/new ship comparison.'})
  for m in d.get('unit_factory_modifiers',[]):
   affected=[n for n,u in units.items()if not m.get('build_kinds') or u.get('build',{}).get('build_kind')in m['build_kinds']]
   if affected:effects.append({'category':'unit_factory_modifiers','modifier':m,'affected_definitions':sorted(affected),'expectation':'Affects future construction at owned factories; existing units unchanged.'})
  other={k:v for k,v in d.items()if k.endswith('_modifiers')and k not in {'unit_modifiers','weapon_modifiers','unit_factory_modifiers'}}
  if other:effects.append({'category':'economic/planetary','modifiers':other,'affected_definitions':['owned planets / economy matching native filters'],'expectation':'Does not directly modify custom hull or weapon fields.'})
  if d.get('buff_providers'):effects.append({'category':'buff_providers','providers':d['buff_providers'],'affected_definitions':['runtime target-filter matches; native provider behavior retained'],'expectation':'Target-filter dispatch, not direct stat inheritance; runtime and saved-buff behavior NOT RUN.'})
  if effects:rows.append({'technology':rid,'domain':d['domain'],'tier':d['tier'],'source':str(p),'sha256':sha(p),'effects':effects})
 # Supplement direct matching with concrete research dependencies in custom action/ability definitions.
 dependencies=[]
 for p in sorted((base/'entities').iterdir()):
  if p.suffix not in {'.ability','.buff','.action_data_source','.unit'}:continue
  if not(p.stem.startswith('expanse')or p.stem in units):continue
  d=read(p);matched=sorted(refs.intersection(strings(d)))
  if matched:dependencies.append({'definition':p.name,'research_dependencies':matched})
 torps=[n for n,u in units.items()if u.get('target_filter_unit_type')=='torpedo']
 return {'supported_player':'trader_loyalist','node_count_examined':len(refs),'matching_technology_count':len(rows),'technology_mapping':rows,'explicit_custom_research_dependencies':dependencies,'custom_units':sorted(units),'custom_weapons':sorted(weapons),'spawned_torpedoes':sorted(torps),'semantic_limits':['Tag lists are interpreted as OR, consistent with native multi-class hull and factory research. The affected_definitions arrays show structural tag matches, not a promise that an absent subsystem gains behavior: e.g. scalar antimatter on a torpedo with no antimatter data has no useful benefit.','No weapon-tag modifier reaches literal torpedo impact action values. Native missile damage/range upgrades currently bypass these custom impact actions.','Unfiltered native hull, armor-strength and hull-repair modifiers also match owned torpedo units. Existing inherited nodes remain unless one of the 13 replacements explicitly scopes them.','Native +35% capital/titan hull angular-speed research remains; no new weapon tracking or range improvement is introduced.','Native tier bonuses, culture, items, levels and temporary buffs combine with research. This audit is a single-node definition match, not a simulated full game.'],'runtime_status':'NOT RUN'}


def build_overlay(base,out,game=GAME,audit=None):
 base,out,game=map(lambda p:Path(p).resolve(),(base,out,game))
 if out==base or out.is_relative_to(game) or 'mods'in out.parts:raise ValueError('Use separate candidate overlay')
 if out.exists() and any(out.iterdir()):raise FileExistsError(out)
 out.mkdir(parents=True,exist_ok=True)
 initial=audit_existing(base,game)
 sdk=game.parent/'Sins of a Solar Empire II - Mod Tools/json_schemas'
 checks=[];changes=[];mapping=[];loc={};installed={str(game/'entities/trader_robotics_cruiser_repair_droids.ability'):sha(game/'entities/trader_robotics_cruiser_repair_droids.ability')}
 for kind in ['research-subject','ability','action-data-source']:
  sp=sdk/(kind+'-schema.json');installed[str(sp)]=sha(sp)
 def stage(name,d,before=None):
  ext=Path(name).suffix;schema={'.research_subject':'research-subject','.ability':'ability','.action_data_source':'action-data-source'}[ext]
  jsonschema.Draft202012Validator(read(sdk/(schema+'-schema.json'))).validate(d)
  write(out/'entities'/name,d);checks.append(name)
  changes.append({'file':'entities/'+name,'sha256':sha(out/'entities'/name),'source_sha256':sha(resolve(base,game,name))})
 for rid,title,desc,effects in SPECS:
  name=rid+'.research_subject';p=resolve(base,game,name);old=read(p);d=copy.deepcopy(old)
  if p.is_relative_to(game):installed[str(p)]=sha(p)
  for k in list(d):
   if k.endswith('_modifiers'):del d[k]
  if rid=='trader_find_npc_explore':
   assert old['windfall']['units_given']['required_units']==[{'unit':'trader_scout_corvette','count':[4,4]}]
  d.update(effects)
  key='expanse15.research.'+rid
  for k,val in [('name',title),('name_uppercase',title.upper()),('description',desc)]:d[k]=key+'.'+k;loc[d[k]]=val
  assert not any('shield'in o.get('modifier_type','')for o in walk(effects))
  allowed=set(effects)|{k for k in old if k.endswith('_modifiers')}|{'name','name_uppercase','description'}
  assert {k:v for k,v in d.items()if k not in allowed}=={k:v for k,v in old.items()if k not in allowed}
  stage(name,d,old)
  mapping.append({'technology':title,'definition':rid,'domain':old['domain'],'tier':old['tier'],'cost_and_prerequisites_preserved':{k:old[k]for k in ('price','exotic_price','research_time','prerequisites','field','field_coord')if k in old},'old_effects':{k:v for k,v in old.items()if k.endswith('_modifiers')},'new_effects':effects,'expected_mechanical_result':desc,'scope':'Empire-wide owner research; Marine effect only on Scirocco cast, not a global debuff.'if rid==MARINE else 'Empire-wide owner research; filters in modifiers restrict applicability.'})
 # Detect only private fixed-level torpedo programs with the verified impact value.
 programs={}
 for p in (base/'entities').glob('expanse*.ability'):
  a=read(p);sid=a.get('action_data_source');sp=base/'entities'/(str(sid)+'.action_data_source')
  if not sp.exists():continue
  s=read(sp);avs={v['action_value_id']:v['action_value']for v in s.get('action_values',[])}
  if 'heavy_torpedo_damage_value'not in avs:continue
  assert a['level_source']=='fixed_level_0',(p.name,'unexpected level semantics')
  assert avs['heavy_torpedo_damage_value'].get('values') and len(avs['heavy_torpedo_damage_value']['values'])==1
  # Resolve actual buff graph and verify create_torpedo binds this exact damage value.
  graph=[a,s];seen=set();pending=list(strings(a))+list(strings(s))
  while pending:
   ref=pending.pop();bp=base/'entities'/(ref+'.buff')
   if ref in seen or not bp.exists():continue
   seen.add(ref);bd=read(bp);graph.append(bd);pending.extend(strings(bd))
  launch_ops=[o for obj in graph for o in walk(obj)if o.get('operator_type')=='create_torpedo']
  assert launch_ops and all(o['damage_value']=='heavy_torpedo_damage_value'for o in launch_ops),(p.name,'unverified torpedo damage binding')
  torpedo_units=sorted({o['torpedo_to_create']for o in launch_ops})
  for tid in torpedo_units:
   td=read(resolve(base,game,tid+'.unit'))
   assert td.get('target_filter_unit_type')=='torpedo' and 'torpedo'in td.get('tags',[]),tid
  a['level_source']='research_prerequisites_per_level';a['level_prerequisites']=[[],[[WARHEAD]]]
  stage(p.name,a)
  programs.setdefault(sid,{'abilities':[],'torpedo_entities':torpedo_units,'resolved_buff_graph':sorted(seen),'damage_before':avs['heavy_torpedo_damage_value']['values'][0]})['abilities'].append(p.stem)
  if (out/'entities'/sp.name).exists():continue
  s['level_count']=2
  for v in s.get('action_values',[]):
   av=v['action_value']
   if 'values'in av:
    assert len(av['values'])==1,(sp.name,v)
    av['values']=[av['values'][0],round(av['values'][0]*1.05,8)if v['action_value_id']=='heavy_torpedo_damage_value'else av['values'][0]]
  stage(sp.name,s)
 for sid,rec in programs.items():rec['damage_after']=round(rec['damage_before']*1.05,8)
 write(out/'localization-entries.json',loc)
 units,weapons=inventory(base,game);numeric=[]
 for rid,title,desc,effects in SPECS:
  for category,definitions in [('unit_modifiers',units),('weapon_modifiers',weapons)]:
   for m in effects.get(category,[]):
    for n,u in definitions.items():
     if not matches(m,u):continue
     field=m['modifier_type'];val=u.get(field) if category=='weapon_modifiers' else u.get('health',{}).get('levels',[{}])[0].get(field)
     if isinstance(val,(float,int)):numeric.append({'technology':title,'definition':n,'field':field,'unresearched_definition_value':val,'researched_expected_single_bonus':round(val*(1+m['value']),8),'existing_and_new_units':'Same owner research modifier expected; existing current HP may preserve fraction/absolute amount per engine and is NOT RUN.'})
 report={'status':'PASS offline schema, exact preserved node-economic fields, unchanged torpedo timing/count values','runtime_status':'NOT RUN','changes':changes,'schema_checks':checks,'mapping':mapping,'torpedo_programs':programs,'single_node_numeric_checks':numeric,'installed_sources':installed,'integration':{'procedure':'Overlay entities, merge localization-entries.json into localized_text/en.localized_text. No new entity IDs or player changes required. Main Scirocco worker binds Marine doctrine independently. Call on complete candidate containing Truman before packaging.','source_ability_pattern':'trader_robotics_cruiser_repair_droids.ability, level_prerequisites=[[],[[trader_retrofit_bay_repair_rate_0]]]','research_program_runtime_risks':['Existing persistent magazine buff might retain old action-source level until its next magazine cycle; launch/research mid-magazine must be observed.','Torpedoes already launched may keep their launch-time damage snapshot; compare pre/post unlock missiles.','Ability level transition may restart persistent buff/ammo state; test before/after research, save/reload and host/client parity before claiming behavior pass.']},'limitations':['No research-based weapon tracking, penetration, firing arcs or speed change. Railgun cooldown only −5%.','Shield guard and hidden shield-only research preserved; foreign captured hulls/foreign allied buffs retain prior policy limits.','Deep-Survey retains native four-scout windfall, not an additional new reward.','Other native unfiltered hull/armor research still applies to torpedo entities, listed in inherited-research audit.','Research replacements retain old node IDs for prerequisites/save compatibility; downstream upgrade names and benefits remain native.']}
 if audit:
  write(Path(audit)/'inherited-research.json',initial);write(Path(audit)/'integration.json',report)
 return report

def apply(out,game=GAME,audit=None):
 """Main-owned integration: prepared fresh package; writes only 13 nodes,torpedo programs,localization."""
 import tempfile
 out=Path(out)
 with tempfile.TemporaryDirectory(prefix='research15-',dir='/tmp')as tmp:
  overlay=Path(tmp)/'overlay';report=build_overlay(out,overlay,game,audit)
  for p in (overlay/'entities').iterdir():write(out/'entities'/p.name,read(p))
  loc=read(out/'localized_text/en.localized_text');loc.update(read(overlay/'localization-entries.json'));write(out/'localized_text/en.localized_text',loc)
 return report

if __name__=='__main__':
 ap=argparse.ArgumentParser();ap.add_argument('--base',type=Path,default=BASE);ap.add_argument('--out',type=Path,required=True);ap.add_argument('--audit',type=Path,default=Path('audit/update15-research'));a=ap.parse_args()
 r=build_overlay(a.base,a.out,GAME,a.audit);print(json.dumps({'files':len(r['changes']),'schemas':len(r['schema_checks']),'programs':len(r['torpedo_programs'])}))
