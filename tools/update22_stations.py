"""Stage 3 support stations. Pure new definitions plus integrator-owned merge recipes.
No installation, shared-file editing, railgun rebalance or torpedo reload changes.
"""
from __future__ import annotations
from copy import deepcopy as cp
from pathlib import Path
import json, hashlib

GAME=Path('/run/media/haker/NVME 2/SteamLibrary/steamapps/common/Sins2')
SHIPS=['capital_ship','corvette','cruiser','frigate','super_capital_ship','titan']
STATIONS={'mcrn':'MCRN Naval Anchorage','unn':'UNN Fleet Support Station','opa':'OPA Tycho-pattern Engineering Station'}

def read(p):return json.loads(Path(p).read_text())
def value(i,v,**kw):return {'action_value_id':i,'action_value':{'values':[v],**kw}}
def no_buff(n):return {'constraint_type':'composite_not','constraint':{'constraint_type':'has_buff','buff':n,'include_pending_buffs':True}}
def stack(preserve=True):return {'stacking_limit':{'stacking_limit':'fixed_one','stacking_limit_met_behavior':'preserve_existing_buff' if preserve else 'restart_existing_buff'},'stacking_ownership_type':'for_all_players','restart_other_stacked_buffs_when_started':not preserve}
def filter_check(i,unit='operand_destination'):return {'constraint_type':'unit_passes_target_filter','unit':{'unit_type':unit},'target_filter_id':i}


def changes(base, prefix='expanse22'):
 base=Path(base);edits={};strings={};origins={};report={'status':'OFFLINE AUTHORING; runtime NOT RUN','player_recipes':{},'unit_tag_entries_append':[], 'stations':[], 'modules':[], 'blocked_or_deferred':[]}
 def source(n):
  p=base/'entities'/n
  return p if p.exists() else GAME/'entities'/n
 def donor(n):return read(source(n))
 def emit(n,d,original):edits[n]=d;origins[n]=str(source(original))
 def loc(i,name,description):strings[i+'.name']=name;strings[i+'.description']=description
 family=prefix+'_major_support_station';pdc_m=prefix+'_station_mcrn_pdc';pdc_e=prefix+'_station_earth_pdc';torp=prefix+'_station_defense_torpedo'
 repair=prefix+'_repair_anchorage';track=prefix+'_defense_coordination';industry=prefix+'_industrial_drydock';ordnance=prefix+'_ordnance_control'
 module_ids=[ordnance,repair,track,industry]
 report['unit_tag_entries_append'].append({'name':family,'localized_name':family+'.name'});strings[family+'.name']='Major support station'
 native=donor('trader_starbase.unit');retrofit=donor('trader_retrofit_bay_structure.unit')
 native_skin=donor('trader_starbase.unit_skin')
 # Existing native mounts and biaxial meshes remain paired. Actual PDC projectile,
 # audio, penetration and cooldown copied unchanged from accepted custom ships.
 for wid,donor_name in [(pdc_m,'expanse10_donnager_pdc_0.weapon'),(pdc_e,'expanse15_truman_pdc_0.weapon')]:
  w=donor(donor_name);w['name']=wid+'.name';w['turret']=cp(donor('trader_starbase_light_autocannon.weapon')['turret'])
  emit(wid+'.weapon',w,donor_name);loc(wid,'Anchorage point defense','One native-mounted PDC using the established faction damage and interception profile.')
 w=donor('expanse15_missile_defense.weapon');w['name']=torp+'.name';emit(torp+'.weapon',w,'expanse15_missile_defense.weapon')
 loc(torp,'Anchorage defense torpedoes','Existing local defense-platform torpedo profile; two independent banks when Ordnance Control is fitted.')
 # Every station has the same four fitting choices and three actual native slots.
 descriptions={
  ordnance:('Ordnance Control','Enables two local defense torpedo banks. Each retains the existing platform profile: 300 damage, two shots per 8 seconds, 10000 range, 30-second fuel. Requires an explicit attack order. Separate defense stores; no ship magazine refills.'),
  repair:('Repair Anchorage','Repairs 20 hull points on up to 3 nearby owned ships each second within 6000. A shared reservation prevents overlapping station repairs. No armor or shields. Does not add healing while Scirocco engineering or native active repair is present.'),
  track:('Defense Coordination','Owned armed ships within 6000 gain 10% point-defense tracking speed only. One bonus from this effect; expires on leaving range or losing the provider. No weapon damage, range or reload bonus.'),
  industry:('Industrial Drydock','Owned functional orbital ship factories within 6000 construct ships 10% faster by rate (about 9.09% less base time). One bonus from this effect; no global modifier or magazine rearming.')}
 for mid in module_ids:
  d=donor('trader_derelict_specialist.unit_item');d.pop('unit_modifiers',None);d.pop('build_prerequisites',None)
  d.update(name=mid+'.name',description=mid+'.description',required_unit_tags=[family],build_time=60.,price={'credits':700.,'metal':150.,'crystal':100.},max_count_on_unit=1)
  d['hud_icon']={ordnance:'trader_starbase_unlock_torpedo_weapon_unit_item_hud_icon',repair:'trader_retrofit_bay_repair_ability_hud_icon',track:'trader_targeting_array_unit_item_hud_icon',industry:'trader_starbase_factory_support_unit_item_hud_icon'}[mid]
  if mid!=ordnance:d['ability']=mid
  else:d['build_group_id']='offense'
  emit(mid+'.unit_item',d,'trader_derelict_specialist.unit_item');loc(mid,*descriptions[mid]);report['modules'].append({'item':mid,'slots':1,'price':d['price'],'seconds':60,'scope':'Local/owned only'})
 # Two native aura families share explicit parent death and range removal semantics.
 for mid,mode in [(track,'tracking'),(industry,'industry')]:
  a=donor('trader_targeting_array_unit_item.ability');a['action_data_source']=mid;a['passive_actions']['persistant_buff']=mid+'_on_self'
  a['gui']={'name':mid+'.name','description':mid+'.description','targeting':{'targeting_type':'radius','values':{'radius':'apply_buff_radius'}}}
  emit(mid+'.ability',a,'trader_targeting_array_unit_item.ability')
  ads=donor('trader_targeting_array_unit_item.action_data_source');ads.pop('buff_weapon_modifiers',None)
  tf={'unit_types':SHIPS if mode=='tracking' else ['structure'],'ownerships':['self'],'constraints':[{'constraint_type':'is_fully_built'},{'constraint_type':'not_self'}]}
  tf['constraints'].append({'constraint_type':'has_weapon','weapon_type':'normal'} if mode=='tracking' else {'constraint_type':'is_unit_factory','must_be_functional':True})
  ads['target_filters']=[{'target_filter_id':'station_target_filter','target_filter':tf}]
  ads['action_values']=[value('apply_buff_radius',6000),value('station_modifier_value',.10 if mode=='tracking' else 1/1.10-1)]
  if mode=='tracking':ads['buff_weapon_modifiers']=[{'buff_weapon_modifier_id':'station_modifier','buff_weapon_modifier':{'modifier_type':'tracking_speed','value_behavior':'scalar','value_id':'station_modifier_value','tags':['point_defense']}}]
  else:ads['buff_unit_factory_modifiers']=[{'buff_unit_factory_modifier_id':'station_modifier','buff_unit_factory_modifier':{'modifier_type':'build_time','value_behavior':'scalar','value_id':'station_modifier_value'}}]
  emit(mid+'.action_data_source',ads,'trader_targeting_array_unit_item.action_data_source')
  parent=donor('trader_targeting_array_unit_item_on_self.buff')
  action=parent['time_actions'][0]['action_group']['actions'][0]
  action['operators'][0]['constraint']['target_filter_id']='station_target_filter';action['operators'][0]['buff']=mid+'_on_target'
  parent['make_dead_on_current_spawner_ownership_changed_from_buff_ownership']=True
  emit(mid+'_on_self.buff',parent,'trader_targeting_array_unit_item_on_self.buff')
  child=donor('trader_targeting_array_unit_item_on_target.buff');child.pop('weapon_modifiers',None);child.update(stack(False))
  key='weapon_modifiers' if mode=='tracking' else 'unit_factory_modifiers';ref='buff_weapon_modifier_id' if mode=='tracking' else 'buff_unit_factory_modifier_id'
  child[key]=[{ref:'station_modifier'}];child['make_dead_on_current_spawner_ownership_changed_from_buff_ownership']=True
  child['gui']={'hud_icon':edits[mid+'.unit_item']['hud_icon'],'name':mid+'.name','visibility_scope':'positive'}
  emit(mid+'_on_target.buff',child,'trader_targeting_array_unit_item_on_target.buff')
 # Fixed-throughput repair is performed by the living local provider, not by a
 # detached target heal timer. Reservation lasts1second and adds no heal itself.
 marker=repair+'_reservation'
 a=donor('trader_targeting_array_unit_item.ability');a['action_data_source']=repair;a['passive_actions']['persistant_buff']=repair+'_on_self'
 a['gui']={'name':repair+'.name','description':repair+'.description','targeting':{'targeting_type':'radius','values':{'radius':'apply_buff_radius'}}};emit(repair+'.ability',a,'trader_targeting_array_unit_item.ability')
 ads={'version':0,'target_filters':[{'target_filter_id':'repair_target_filter','target_filter':{'unit_types':SHIPS,'ownerships':['self'],'constraints':[{'constraint_type':'is_fully_built'},{'constraint_type':'not_self'},no_buff(marker),no_buff('expanse15_scirocco_engineering_teams'),no_buff('trader_retrofit_bay_repair'),no_buff('trader_combat_repair_system_unit_item')]}}],
 'action_values':[value('apply_buff_radius',6000),value('repair_target_count',3),value('repair_per_tick',20),value('reservation_duration',1),value('minimum_missing_hull',20),value('target_missing_hull',1,transform_type='per_missing_hull_points',transform_unit={'unit_type':'operand_destination'})]}
 emit(repair+'.action_data_source',ads,'trader_retrofit_bay_repair.action_data_source')
 parent=donor('trader_targeting_array_unit_item_on_self.buff');parent['make_dead_on_current_spawner_ownership_changed_from_buff_ownership']=True
 action=parent['time_actions'][0]['action_group']['actions'][0];action['max_target_count_value']='repair_target_count'
 action['operators_constraint']={'constraint_type':'composite_and','constraints':[filter_check('repair_target_filter'),{'constraint_type':'value_comparison','value_a':'target_missing_hull','comparison_type':'greater_than_equal_to','value_b':'minimum_missing_hull'}]}
 action['target_sort']={'sort_steps':[{'sort_order':'ascending','sort_type':'distance_to_unit','distance_reference_unit':{'unit_type':'current_spawner'}}]}
 action['operators']=[{'operator_type':'apply_buff','buff':marker},{'operator_type':'repair_damage','affect_type':'hull_only','repair_value':'repair_per_tick'}]
 emit(repair+'_on_self.buff',parent,'trader_targeting_array_unit_item_on_self.buff')
 d={'version':0,'active_duration':'reservation_duration',**stack(True),'make_dead_on_current_spawner_ownership_changed_from_buff_ownership':True};emit(marker+'.buff',d,'trader_retrofit_bay_repair.buff')
 # Exact native hull/turret model pairing, modest health and real military slots.
 for faction,title in STATIONS.items():
  uid=prefix+'_'+faction+'_support_station';u=cp(native)
  for key in ['unit_factory','carrier','trade_port','unit_modifiers']:u.pop(key,None)
  u['physics']['can_move_linear']=False
  u['structure']={'slot_type':'military','slots_required':8,'roles':['defense'],'build_group_id':'military'}
  u['build']=cp(retrofit['build']);u['build'].update(build_time=240.,price={'credits':4000.,'metal':900.,'crystal':700.},build_radius=native['build']['build_radius'],prerequisites=[['trader_unlock_starbase']])
  u['tags']=['structure',family,uid];u['target_filter_unit_type']='structure';u['virtual_supply_cost']=40
  u['items']={'levels':[{'max_ship_component_count':3}],'requires_ship_component_shop_to_purchase_items':False}
  u['ship_component_shop']={};u['item_builds']=[{'build_group':[mid],'weight':5.} for mid in module_ids]
  u['health']['durability']=600.
  h=cp(retrofit['health']['levels'][0]);h.update(max_hull_points=12000.,max_armor_points=4500.,armor_strength=75.,max_shield_points=0.,shield_point_restore_rate=0.)
  h.pop('shield_burst_restore',None);u['health']['levels']=[h]
  u['abilities']=[{'abilities':['expanse11_no_shields']}]
  pd=pdc_m if faction=='mcrn' else pdc_e;u['weapons']['weapons']=[]
  for w in native['weapons']['weapons']:
   if w['mesh_point'] in ['child.turret_mount_0','child.turret_mount_4','child.turret_mount_8','child.turret_mount_12']:
    q=cp(w);q['weapon']=pd;u['weapons']['weapons'].append(q)
   elif w['weapon']=='trader_starbase_medium_missile' and w['mesh_point'] in ['weapon.0','weapon.2']:
    q=cp(w);q['weapon']=torp;q['required_unit_item']=ordnance;u['weapons']['weapons'].append(q)
  u['weapons']['max_range_weapon_index']=0
  u['ai']['attack_target_type_groups']=cp(edits[pd+'.weapon']['attack_target_type_groups']);u['ai']['attack_target_type_groups_matching_weapon']=pd;u['ai']['attack_target_type_groups_to_ignore']=[]
  u['skin_groups']=[{'skins':[uid]}]
  u['child_meshes']=[cp(x) for x in native['child_meshes'] if x['mesh_alias_name']=='trader_starbase_component_missile']
  for child in u['child_meshes']:child['required_unit_item']=ordnance
  emit(uid+'.unit',u,'trader_starbase.unit')
  skin=cp(native_skin);skin['name']={'group':'starbase'}
  for stage in skin['skin_stages']:
   stage['gui']['name']=uid+'.name';stage['gui']['description']=uid+'.description';stage['effects'].pop('shield_effect',None)
   stage['sounds'].get('dialogue',{}).pop('shields_down',None)
   aliases={x['alias_name']:cp(x) for x in stage['effects']['effect_alias_bindings']}
   for donor_skin in ['expanse_donnager_battleship.unit_skin','expanse15_truman.unit_skin','expanse15_missile_defense.unit_skin']:
    dp=source(donor_skin)
    if dp.exists():
     ds=read(dp)['skin_stages'][0]
     for alias in ds['effects'].get('effect_alias_bindings',[]):aliases[alias['alias_name']]=cp(alias)
   stage['effects']['effect_alias_bindings']=list(aliases.values())
  emit(uid+'.unit_skin',skin,'trader_starbase.unit_skin')
  loc(uid,title,'Owned shieldless engineering station using shared native TEC starbase art. One major support station per player; 8 military slots. Four PDCs, three fitting slots among four modules. Local services require fitted equipment; no free visiting aura, global economic bonus or magazine refill.')
  report['unit_tag_entries_append'].append({'name':uid,'localized_name':uid+'.name'})
  report['player_recipes'][faction]={'structures_append':[uid],'ship_components_append':module_ids,'global_unit_limit':{'tag':family,'unit_limit':1}}
  report['stations'].append({'unit':uid,'title':title,'price':u['build']['price'],'build_seconds':240,'military_slots':8,'fleet_supply':0,'hull':12000,'armor':4500,'durability':600,'armor_strength':75,'pdc_count':4,'pdc_base_dps_per_mount':edits[pd+'.weapon']['damage']/edits[pd+'.weapon']['cooldown_duration'],'optional_torpedo_banks':2,'normal_item_slots':3,'shared_native_art':True})
 # Shared small picket: actual native hangar PDC mounts, without a strikecraft
 # carrier. One common defensive profile at85DPS/mount; no special auras or slots.
 picket=prefix+'_pdc_picket';pw=picket+'_weapon'
 w=donor('expanse15_truman_pdc_0.weapon');w['name']=pw+'.name';w['turret']=cp(donor('trader_hangar_defense_structure_point_defense_autocannon.weapon')['turret'])
 emit(pw+'.weapon',w,'expanse15_truman_pdc_0.weapon');loc(pw,'Picket point defense','Standard defensive PDC profile; four native mounts with one shared firing budget per mount.')
 p=donor('trader_hangar_defense_structure.unit');p.pop('carrier',None);p['abilities']=[{'abilities':['expanse11_no_shields']}]
 p['build'].update(build_time=80.,price={'credits':1200.,'metal':250.,'crystal':100.})
 p['structure']['slots_required']=3;p['skin_groups']=[{'skins':[picket]}]
 p['ai']['attack_target_type_groups']=cp(w['attack_target_type_groups']);p['ai']['attack_target_type_groups_matching_weapon']=pw;p['ai']['attack_target_type_groups_to_ignore']=[]
 for mount in p['weapons']['weapons']:mount['weapon']=pw
 for h in p['health']['levels']:h.update(max_shield_points=0.,shield_point_restore_rate=0.);h.pop('shield_burst_restore',None)
 emit(picket+'.unit',p,'trader_hangar_defense_structure.unit')
 ps=donor('trader_hangar_defense_structure.unit_skin')
 for stage in ps['skin_stages']:
  stage['gui'].update(name=picket+'.name',description=picket+'.description');stage['effects'].pop('shield_effect',None)
  aliases={x['alias_name']:cp(x) for x in stage['effects']['effect_alias_bindings']}
  for x in donor('expanse15_truman.unit_skin')['skin_stages'][0]['effects']['effect_alias_bindings']:aliases[x['alias_name']]=cp(x)
  stage['effects']['effect_alias_bindings']=list(aliases.values())
 emit(picket+'.unit_skin',ps,'trader_hangar_defense_structure.unit_skin')
 loc(picket,'PDC Picket','Shieldless missile-defense installation using converted native hangar art. Four standard defensive PDC mounts; no strikecraft, missiles or support aura. Uses 3 military slots. Low penetration preserves heavy-ship counters.')
 for recipe in report['player_recipes'].values():recipe['structures_append'].append(picket)
 report['picket']={'unit':picket,'native_art':'trader_hangar_defense_structure','pdc_count':4,'dps_per_mount':w['damage']/w['cooldown_duration'],'penetration':w['penetration'],'military_slots':3,'price':p['build']['price'],'build_seconds':80,'carrier_removed':True}
 report['combined_sandbox']={'structures_append':[prefix+'_'+x+'_support_station' for x in STATIONS]+[picket],'ship_components_append':module_ids,'global_unit_limit':{'tag':family,'unit_limit':1}}
 report['capture_rule']='No forced deletion. Captured excess survives; native shared-tag limit prevents ordinary additional construction until below1. Capture/queued construction behavior NOT RUN.'
 report['research_extension_points']={'mcrn_naval_readiness':{'owned_station_tag':prefix+'_mcrn_support_station','repair_module':repair,'bounded_action_value':'repair_per_tick','base_value':20,'suggested_researched_value':22,'merge_rule':'Main adds owner-specific research level only after that node is present; do not change global shared value.'},'unn_fleet_train':{'owned_station_tag':prefix+'_unn_support_station','module':repair,'existing_stage21_node':'expanse21_unn_fleet_train','existing_stage21_module':'expanse21_unn_fleet_train_module','interaction':'Existing fleet-train module applies expanse15_scirocco_engineering_teams, so the station repair filter already excludes it. Preserve that implemented node/module; do not replace it with a redundant station unlock.'}}
 report['blocked_or_deferred']=['Ordnance Control enables modest existing defense torpedoes, not a new heavy railgun. Heavy gun role belongs to separate Foehammer battery.','OPA native placeholder does not claim imported Tycho model, habitat animation,12–16modeledPDCs or new salvage progression.','Paid UNN mobilization and custom OPA recovery specialization are separate main-thread research/Stage4 integrations.']
 report['runtime_cases']=['Fresh load with explicit unit tags and constructor menu','All3normal slots and4module choices','Local ownership filters,source/target capture and leaving6000range','Three-target fixed repair cap,pending reservations,overlapping stations and Scirocco interaction','PDCtracking only+10%,no range/damage/cooldown drift','Factory10%rate is9.09%less base time,not global','Missile component slots/gating,both banks,all native muzzle arcs','Unique limit queued construction,cancellation,capture and save/reload','Shared/native placeholder model and weapon effect origins']
 return edits,strings,origins,report
