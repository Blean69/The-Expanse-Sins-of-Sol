"""Disabled Tycho starbase mechanics, native placeholder mesh; no integration/install."""
from __future__ import annotations
import copy, hashlib, json
from pathlib import Path
import jsonschema
ROOT=Path(__file__).resolve().parents[1]
DRIVE=Path('/run/media/haker/NVME 2')
MAIN=DRIVE/'expanse-mod'
BASE=MAIN/'build/experiments/expanse_update17'
GAME=DRIVE/'SteamLibrary/steamapps/common/Sins2'
SDK=DRIVE/'SteamLibrary/steamapps/common/Sins of a Solar Empire II - Mod Tools'
OUT=ROOT/'build/laboratory/update18/station'
AUDIT=ROOT/'audit/update18-tycho'
ID='expanse18_tycho_arsenal'
PDC=ID+'_pdc'
TORP=ID+'_torpedo'
DOCK=ID+'_industrial_drydock'

def read(p):return json.loads(p.read_text())
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def write(p,d):
 p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(d,indent=2)+'\n')
def source(n):
 p=BASE/'entities'/n
 return p if p.exists() else GAME/'entities'/n

def schema_check(path, schema_name, original):
 """Record only unchanged installed/base extensions; never accept new unknown keys."""
 schema=read(SDK/'json_schemas'/schema_name);data=read(path);old=read(original);extensions=[]
 for _ in range(30):
  errors=list(jsonschema.Draft202012Validator(schema).iter_errors(data))
  if not errors:return {'file':path.name,'status':'PASS','schema':schema_name,'unchanged_source_extensions':extensions}
  progress=False
  for e in errors:
   if e.validator=='enum':
    prior=old
    for part in e.path:prior=prior[part]
    assert prior==e.instance, 'Changed unknown enum '+str(path)
    e.schema['enum'].append(e.instance)
    extensions.append({'path':'/'+'/'.join(map(str,e.path)),'unchanged_enum':e.instance})
    progress=True
    continue
   if e.validator not in ['unevaluatedProperties','additionalProperties'] or not isinstance(e.instance,dict):continue
   props=e.schema.get('properties',{})
   if not props:continue
   target,prior=data,old
   for part in e.path:target,prior=target[part],prior[part]
   for key in sorted(set(target)-set(props)):
    assert key in prior and target[key]==prior[key], 'New or changed unknown field '+str(path)+':'+key
    extensions.append('/'+'/'.join(map(str,[*e.path,key])))
    del target[key];progress=True
  if not progress:raise ValueError('\n'.join(e.message for e in errors[:5]))
 raise ValueError('Extension convergence failed')

def build():
 native=read(source('trader_starbase.unit'));unit=copy.deepcopy(native)
 light=read(source('trader_starbase_light_autocannon.weapon'))
 donor=read(source('expanse10_donnager_pdc_0.weapon'))
 pdc=copy.deepcopy(donor)
 pdc.update(name=PDC+'.name',damage=10.0,range=7000.0,cooldown_duration=.25,pitch_speed=180.,yaw_speed=180.)
 pdc['turret']=copy.deepcopy(light['turret'])
 torp=read(source('trader_starbase_medium_missile.weapon'))
 torp.update(name=TORP+'.name',damage=300.,cooldown_duration=12.,range=12000.,burst_pattern=[0.])
 torp.pop('modifiers',None)
 torp['firing']['torpedo_firing_definition']['spawned_unit']='trader_medium_torpedo'
 unit['weapons']['weapons']=[]
 for w in native['weapons']['weapons']:
  if w['weapon'] not in ['trader_starbase_light_autocannon','trader_starbase_medium_missile']:continue
  q=copy.deepcopy(w);q['weapon']=PDC if 'light_autocannon' in w['weapon'] else TORP
  q.pop('required_unit_item',None)
  unit['weapons']['weapons'].append(q)
 assert len(unit['weapons']['weapons'])==20
 unit['ai']['attack_target_type_groups']=copy.deepcopy(pdc['attack_target_type_groups'])
 unit['ai']['attack_target_type_groups_matching_weapon']=PDC
 unit['ai'].pop('attack_target_type_groups_to_ignore',None)
 # Native starbase is already immobile; retain slow angular aiming without travel.
 unit['physics']['can_move_linear']=False
 unit['tags']=[ID]
 unit['items']['levels']=[{'max_ship_component_count':3}]
 unit['build'].update(build_time=600.,price={'credits':10000.,'metal':3000.,'crystal':2000.})
 unit['build']['exotic_price']=[{'exotic_type':'defense','count':2}]
 # Keep valid native prerequisites in disabled prototype; integrator replaces with
 # the shared themed station unlock after building the complete research graph.
 unit['build']['prerequisites']=[['trader_unlock_starbase']]
 unit['health']['durability']=1500.
 h=unit['health']['levels'][0]
 h.update(max_hull_points=75000.,max_armor_points=20000.,armor_strength=200.,max_shield_points=0.,shield_point_restore_rate=0.)
 h['shield_burst_restore']['restore_percentage']=0.
 unit['abilities']=[{'abilities':['expanse11_no_shields']}]
 unit.pop('trade_port',None);unit.pop('carrier',None)
 unit['child_meshes']=[copy.deepcopy(x) for x in native['child_meshes'] if x['mesh_alias_name'] in ['trader_starbase_component_missile','trader_starbase_component_construction']]
 for x in unit['child_meshes']:
  if x['mesh_alias_name']=='trader_starbase_component_missile':x.pop('required_unit_item',None)
  else:x['required_unit_item']=DOCK
 unit['skin_groups']=[{'skins':[ID]}]
 unit['spawn_debris']['spawn_loot']['loot_name']=ID+'.loot'
 # Preserve existing native one-off wreckage behavior; no new salvage death system.
 skin=read(source('trader_starbase.unit_skin'))
 skin['name']={'group':'starbase'}
 stage=skin['skin_stages'][0]
 stage['gui'].update(name=ID+'.name',description=ID+'.description')
 stage['effects'].pop('shield_effect',None)
 stage['sounds']['dialogue'].pop('shields_down',None)
 donor_skin=read(source('expanse_donnager_battleship.unit_skin'))['skin_stages'][0]
 aliases={x['alias_name']:copy.deepcopy(x) for x in stage['effects']['effect_alias_bindings']}
 donor_aliases={x['alias_name']:x for x in donor_skin['effects']['effect_alias_bindings']}
 for k in ['muzzle_effect','projectile_travel_effect','hit_hull_effect','hit_shield_effect']:
  alias=pdc['effects'][k]
  assert alias in donor_aliases
  aliases[alias]=copy.deepcopy(donor_aliases[alias])
 stage['effects']['effect_alias_bindings']=list(aliases.values())
 dock=read(source('trader_starbase_unit_factory.unit_item'))
 dock.update(name=DOCK+'.name',description=DOCK+'.description',required_unit_tags=[ID])
 dock['unit_factory_modifiers']=[{'modifier_type':'build_time','value_behavior':'scalar','values':[(1/1.15)-1]}]
 dock['max_count_on_unit']=1
 dock['build_prerequisites']=[['trader_unlock_starbase_unit_factory_unit_item']]
 defs={ID+'.unit':(unit,'unit-schema.json',source('trader_starbase.unit')),
       ID+'.unit_skin':(skin,'unit-skin-schema.json',source('trader_starbase.unit_skin')),
       PDC+'.weapon':(pdc,'weapon-schema.json',source('expanse10_donnager_pdc_0.weapon')),
       TORP+'.weapon':(torp,'weapon-schema.json',source('trader_starbase_medium_missile.weapon')),
       DOCK+'.unit_item':(dock,'unit-item-schema.json',source('trader_starbase_unit_factory.unit_item'))}
 checks=[]
 for name,(data,schema,original) in defs.items():
  p=OUT/'entities'/name;write(p,data);checks.append(schema_check(p,schema,original))
 # Mount positions, frames and arcs copied exactly from matching native geometry.
 mounts=[]
 for w in unit['weapons']['weapons']:
  orig=next(x for x in native['weapons']['weapons'] if x['mesh_point']==w['mesh_point'])
  assert {k:v for k,v in orig.items() if k not in ['weapon','required_unit_item']}=={k:v for k,v in w.items() if k!='weapon'}
  mounts.append({'mesh_point':w['mesh_point'],'position':w['weapon_position'],'yaw_arc':w['yaw_arc'],'pitch_arc':w['pitch_arc'],'weapon':w['weapon']})
 assert unit['ai']['attack_target_type_groups']==pdc['attack_target_type_groups']
 assert unit['tags']==[ID] and 'starbase' not in unit['tags']
 assert unit['unit_factory']['required_mutation']=='mobile_unit_factory_enabled'
 assert dock['unit_mutations']==['mobile_unit_factory_enabled']
 assert dock['unit_factory_modifiers'][0]['values'][0]==1/1.15-1
 fragments={'format':'PROJECT integration recipe, not engine configuration',
  'status':'DISABLED_RUNTIME_PENDING','entity_files':sorted(defs),'shared_player_recipe':{
    'structures_append':[ID], 'ship_components_append':[DOCK],
    'unit_limits_global_append':[{'tag':ID,'unit_limit':1}],
    'same_for_factions':['expanse18_unn','expanse18_mcrn','expanse18_opa']},
  'unit_tag_uniform_append':{'name':ID,'localized_name':ID+'.name'},
  'research_integration':{'station_current_native_prerequisite':'trader_unlock_starbase','station_requested_themed_unlock':'Tycho-pattern Arsenal Construction','drydock_current_native_prerequisite':'trader_unlock_starbase_unit_factory_unit_item'},
  'excluded_modules':{'heavy_ordnance':'GATED pending art, optional two-rail mounts and shared item access','repair_anchorage':'GATED; no unbounded or unverified radius repair','defense_coordination':'GATED; no unverified PDC-only local aura','emergency_lockdown':'deferred until passive modules tested'},
  'station_limit_runtime_gate':'Global tag limit recipe not proven to count simultaneous queued/constructing copies, captured stations, or coexist with normal starbases. No per-player script ledger.',
  'tycho_contact':'Separate ID expanse18_tycho_bureau, never given station tag or counted allowance',
  'art':'Uses native TEC starbase placeholder. Custom Tycho art integrator-owned. Does not represent supplied geometry.',
  'allowed_candidate_without_runtime_claim':'Laboratory only; do not silently enable.'}
 write(OUT/'integration-record.json',fragments)
 write(OUT/'localization-fragment.json',{
  ID+'.name':'Tycho-pattern Arsenal Station', ID+'.loot':'Tycho arsenal wreckage',
  ID+'.description':'Stationary shieldless arsenal prototype. Sixteen PDC mounts and four interceptable torpedo banks. Three equipment slots. Industrial Drydock enables this station\'s own ship factory. Native TEC placeholder art; per-player construction/capture limit tests pending.',
  PDC+'.name':'Tycho dual-purpose PDC',TORP+'.name':'Tycho defense torpedo bank',
  DOCK+'.name':'Industrial Drydock',
  DOCK+'.description':'Enables this station\'s own corvette, frigate and cruiser factory with a 15% faster base construction rate (about 13.04% less base time). One per station; occupies one of three slots. No bonus to other factories or neighboring wells.'})
 write(AUDIT/'offline-validation.json',{'status':'PASS','schema_checks':checks,'mount_count':len(mounts),'native_pdc_mounts':16,'native_torpedo_banks':4,'ai_groups_match_weapon':True,'unique_station_tag':ID,'generic_starbase_tag_absent':True,'slots':3,'drydock_build_time_scalar':1/1.15-1,'runtime_status':'NOT RUN','multiplayer_minutes':0})
 write(AUDIT/'mechanics-summary.json',{'status':'DISABLED_LABORATORY','unit':ID,'hull':75000,'armor':20000,'armor_strength':200,'durability':1500,'cost':unit['build']['price'],'exotics':unit['build']['exotic_price'],'build_seconds':600,'pdc':{'count':16,'damage':10,'cooldown':.25,'range':7000,'max_all_mounts_raw_damage_per_second':640,'tracking_degrees_per_second':180,'note':'All mounts cannot necessarily bear; actual interception/mitigation/fire arcs require combat tests.'},'torpedoes':{'banks':4,'damage':300,'cooldown':12,'projectiles_per_bank_per_cycle':1,'all_banks_raw_damage_per_second':100,'range':12000,'spawned_unit':'trader_medium_torpedo'},'drydock_scope':'SELF FACTORY ONLY','mounts':mounts,'sources':[{'path':str(p),'sha256':sha(p)} for p in sorted({v[2] for v in defs.values()}|{source('expanse_donnager_battleship.unit_skin')})]})
 print(json.dumps({'output':str(OUT),'definitions':len(defs),'validation':'PASS offline','runtime':'NOT RUN'}))

if __name__=='__main__':build()
