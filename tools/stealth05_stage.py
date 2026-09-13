#!/usr/bin/env python3
"""Stage isolated launch telemetry and delayed RNG-capture probes; never cloak/package."""
import argparse,copy,hashlib,json
from pathlib import Path
import jsonschema

ROOT=Path(__file__).resolve().parents[1]
PIN='8e061033afe53b1393eaefd56617a3fd041eeb5f'
def read(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def write(p,d):p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(d,indent=2)+'\n')
def unit(t):return {'unit_type':t}
def val(k,values,**kw):return {'action_value_id':k,'action_value':{'values':values,**kw}}
def cmp(a,op,b):return {'constraint_type':'value_comparison','value_a':a,'comparison_type':op,'value_b':b}
def both(*items):return {'constraint_type':'composite_and','constraints':list(items)}
def mem(k,operator,operand):return {'action_type':'change_buff_memory_float_value','float_variable':k,'math_operators':[{'operator_type':operator,'operand_value':operand}]}

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--game',type=Path,required=True);ap.add_argument('--sdk',type=Path,required=True);ap.add_argument('--source-root',type=Path,default=Path('/run/media/haker/NVME 2/expanse-mod'));ap.add_argument('--output',type=Path,default=ROOT/'build/stealth05-a/probes');a=ap.parse_args()
    assert a.output.resolve().is_relative_to(ROOT/'build/stealth05-a') and not a.output.exists(),'Fresh owned output required'
    snapshot=read(a.source_root/'audit/schema-comparison.json');assert snapshot['official_commit']==PIN
    for rec in snapshot['files']:
        p=a.sdk/rec['path'];b=p.read_bytes();assert hashlib.sha1(b'blob '+str(len(b)).encode()+b'\0'+b).hexdigest()==rec['official_git_blob'],p
    evidence={}
    def base(rel):
        p=a.game/rel
        if not p.is_file():raise SystemExit('BLOCKED: missing required installed reference '+str(p))
        evidence[rel]={'sha256':sha(p),'bytes':p.stat().st_size};return read(p)
    refs=['dlc3_herald_cloak_frigate_cloak.ability','dlc3_herald_cloak_frigate_cloak.buff','dlc3_herald_cloak_frigate_cloak.action_data_source','dlc3_herald_cloak_frigate_cloak_damage_dealt_degrade.buff','pirate_king_capital_ship_mag_blast_missile_on_self.buff','dlc2_vasari_loyalist_super_empowered_strikecraft_on_strikecraft.buff','pirate_boarding_crew.ability','pirate_boarding_crew.buff','pirate_boarding_crew.action_data_source','advent_battle_psionic_capital_ship_domination.buff','vasari_battle_capital_ship_disrupt_armor_on_damage_dealer.buff','trader_battle_capital_ship.unit','trader_rebel_titan.unit','trader_loyalist.player']
    data={n:base('entities/'+n) for n in refs}
    schemas={ext:read(a.sdk/'json_schemas'/(name+'-schema.json')) for ext,name in [('.ability','ability'),('.buff','buff'),('.action_data_source','action-data-source')]}
    bs=schemas['.buff'];cloak=data['dlc3_herald_cloak_frigate_cloak.buff']
    missing_cloak_fields=[k for k in ['provides_cloak','required_product','cloak_alpha_value','cloak_fade_duration_value'] if k not in bs['properties']]
    cloak_errors=[{'path':'/'.join(map(str,e.path)),'message':e.message} for e in jsonschema.Draft7Validator(bs).iter_errors(cloak)]
    staged={};counter='expanse05_launch_probe';capture='expanse05_boarding_probe'
    # Source-bound probe intentionally uses an installed projectile so it can be
    # checked on the established Ogrov heavy ability without any imported asset.
    projectile='trader_torpedo_cruiser_torpedo'
    count=mem('launch_count','add','fixed_one')
    reset=mem('launch_count','assign','fixed_zero')
    start=mem('reveal_until','assign','common_simulation_time_value');start['math_operators'].append({'operator_type':'add','operand_value':'reveal_seconds'})
    reveal_group={'actions':[start,reset]}
    launch_filter=both({'constraint_type':'unit_passes_unit_constraint','unit':unit('trigger_event_destination'),'unit_constraint':{'constraint_type':'has_definition','unit_definition':projectile}},cmp('common_simulation_time_value','greater_than_equal_to','reveal_until_memory'))
    threshold_action=copy.deepcopy(start);threshold_action['constraint']=cmp('launch_count_memory','greater_than_equal_to','threshold')
    # Compare count again for reset; start changed only the reveal deadline.
    threshold_reset=copy.deepcopy(reset);threshold_reset['constraint']=cmp('launch_count_memory','greater_than_equal_to','threshold')
    hit_actions=[copy.deepcopy(start),copy.deepcopy(reset)]
    staged[counter+'.buff']={'version':0,'stacking_limit':{'stacking_limit':'fixed_one','stacking_limit_met_behavior':'preserve_existing_buff'},'stacking_ownership_type':'for_all_players','restart_other_stacked_buffs_when_started':False,
      'trigger_event_actions':[{'trigger_event_type':'on_buff_started','action_group':{'actions':[copy.deepcopy(reset),mem('reveal_until','assign','fixed_zero')]}},
       {'trigger_event_type':'on_current_spawner_spawned_torpedo','action_group':{'constraint':launch_filter,'actions':[count,threshold_action,threshold_reset]}},
       {'trigger_event_type':'on_unit_damaged_by_current_spawner','action_group':{'constraint':both({'constraint_type':'damage_has_weapon_tag','weapon_tag':'expanse05_cloak_revealing_gun'},cmp('common_simulation_time_value','greater_than_equal_to','reveal_until_memory')),'actions':hit_actions}}],
      'gui':{'hud_icon':'dlc3_herald_battle_capital_ship_cloak_ability_hud_icon','name':'expanse05.probe.counter.name','visibility_scope':'positive','is_visible_within_unit_tooltip':True,'tooltip_line_groups':[{'lines':[{'rendering_type':'single_value','label_text':'expanse05.probe.counter.count','value_id':'launch_count_memory'},{'rendering_type':'single_value','label_text':'expanse05.probe.counter.deadline','value_id':'reveal_until_memory'}]}]}}
    staged[counter+'.action_data_source']={'version':0,'per_buff_memory_declaration':{'float_variable_ids':['launch_count','reveal_until']},'action_values':[val('threshold',[4.]),val('reveal_seconds',[60.]),val('launch_count_memory',[1.],transform_type='current_buff_memory_value',memory_float_variable_id='launch_count'),val('reveal_until_memory',[1.],transform_type='current_buff_memory_value',memory_float_variable_id='reveal_until')]}
    staged[counter+'.ability']={'version':0,'action_data_source':counter,'level_source':'fixed_level_0','passive_actions':{'persistant_buff':counter,'only_if_owner_unit_operational':False},'gui':{'hud_icon':'dlc3_herald_battle_capital_ship_cloak_ability_hud_icon','name':'expanse05.probe.counter.name','description':'expanse05.probe.counter.description'}}
    # A single delayed application means one RNG roll per arriving effect/cast,
    # not per tick, shot damage event, visual sprite or target death.
    enemy={'unit_types':['capital_ship'],'ownerships':['enemy'],'constraints':[{'constraint_type':'is_fully_built'},{'constraint_type':'is_detected'},{'constraint_type':'is_in_current_gravity_well'},{'constraint_type':'composite_not','constraint':{'constraint_type':'has_definition','unit_definition':'expanse_rocinante_hero'}}]}
    player={'player_type':'unit_owner','owned_unit':unit('first_spawner')}
    check_target={'constraint_type':'unit_passes_target_filter','unit':unit('current_spawner'),'target_filter_id':'boarding_capital_target'}
    chance={'constraint_type':'random_chance','chance_value':'capture_chance'}
    supply={'constraint_type':'player_has_available_supply','player':player,'minimum_available_supply':'capture_target_supply','include_future_supply':True}
    staged[capture+'.buff']={'version':0,'active_duration':'fixed_one','stacking_limit':{'stacking_limit':'fixed_one','stacking_limit_met_behavior':'replace_existing_buff'},'stacking_ownership_type':'for_all_players','restart_other_stacked_buffs_when_started':False,'trigger_event_actions':[{'trigger_event_type':'on_buff_started','action_group':{'constraint':both(check_target,supply,chance),'actions':[{'action_type':'use_unit_operators_on_single_unit','destination_unit':unit('current_spawner'),'operators':[{'operator_type':'change_owner_player','new_owner_player':player}]}]}}]}
    original=data['pirate_boarding_crew.ability'];ability=copy.deepcopy(original);ability['action_data_source']=capture;ability['level_source']='fixed_level_0';active=ability['active_actions'];active.pop('auto_cast');active['target_filters']=['boarding_capital_target'];active['required_available_supply']='boarding_required_supply';action=active['actions']['actions'][0]
    action['operators'][0]['buff']=capture;action['operators'][0]['constraint']={'constraint_type':'unit_passes_target_filter','unit':unit('operand_destination'),'target_filter_id':'boarding_capital_target'}
    action['operators'][1]['mesh_point']='center'
    ability['gui']={'hud_icon':original['gui']['hud_icon'],'name':'expanse05.probe.boarding.name','description':'expanse05.probe.boarding.description','tooltip_line_groups':[{'lines':[{'rendering_type':'single_value','label_text':'expanse05.probe.boarding.chance','value_id':'capture_chance','value_float_format':'percentage'}]}]}
    staged[capture+'.ability']=ability
    aliases=data['pirate_boarding_crew.action_data_source']['effect_alias_bindings'];alias=next(x for x in aliases if x['alias_name']=='pirate_boarding_crew_shuttle')
    staged[capture+'.action_data_source']={'version':0,'target_filters':[{'target_filter_id':'boarding_capital_target','target_filter':enemy}],'effect_alias_bindings':[alias],'action_values':[val('boarding_crew_cooldown_time_value',[180.]),val('boarding_crew_delay_time_value',[3.]),val('boarding_crew_range_value',[6000.]),val('capture_chance',[.1]),val('boarding_required_supply',[1.],transform_type='per_build_or_virtual_supply',transform_unit=unit('target')),val('capture_target_supply',[1.],transform_type='per_build_or_virtual_supply',transform_unit=unit('current_spawner'))]}
    checked=[]
    for name,d in staged.items():
        ext=Path(name).suffix;jsonschema.Draft7Validator(schemas[ext]).validate(d);checked.append(name)
    # Particle is modeled shuttle imagery, not a damageable simulated pod.
    particle=base('effects/pirate_pillage_shuttle.particle_effect')
    meshes=[]
    def walk(d):
        if isinstance(d,dict):
            for k,v in d.items():
                if k=='mesh' and isinstance(v,str):meshes.append(v)
                walk(v)
        elif isinstance(d,list):
            for v in d:walk(v)
    walk(particle)
    for ident in meshes:
        p=a.game/'meshes'/(ident+'.mesh');assert p.exists();evidence[str(p.relative_to(a.game))]={'sha256':sha(p),'bytes':p.stat().st_size}
    loc={'expanse05.probe.counter.name':'Launch counter probe — NO CLOAK','expanse05.probe.counter.description':'Telemetry only: first three selected torpedo spawns count; fourth starts a fixed 60-second reveal deadline. This probe does not conceal or reveal a ship.','expanse05.probe.counter.count':'Counted individual launches','expanse05.probe.counter.deadline':'Reveal deadline (simulation seconds)','expanse05.probe.boarding.name':'Boarding capture probe','expanse05.probe.boarding.description':'One modeled shuttle effect; one 10% capture roll after a 3-second travel delay against an eligible enemy capital ship. Requires free supply. Visual pod cannot be intercepted.','expanse05.probe.boarding.chance':'Capture chance per arriving attempt'}
    for name,d in staged.items():write(a.output/'entities'/name,d)
    write(a.output/'localization.json',loc)
    write(a.output/'integration-recipe.json',{'status':'OFFLINE COMPONENT PROBES ONLY; no Amun/cloak package','launch_probe':{'attach_ability':counter,'observed_projectile':projectile,'private_Amun_binding':'Replace exact trigger_event_destination has_definition with finalized private Amun projectile ID; do not count PDC/rail/pods','count':'individual projectile, fourth triggers','window':'60 seconds from fourth launch or first tagged gun hit, subsequent launches/hits during window do not extend','reset':'count zero on reveal; new launch sequence allowed once absolute deadline expires','weapon_tag_recipe':{'append_to_three_private_PDC_and_heavy_rail_tags':'expanse05_cloak_revealing_gun','never_append_to_torpedo_or_pod':'expanse05_cloak_revealing_gun'},'gun_policy':'first successful tagged PDC/rail hit starts same60s window; misses/firing before impact do not reveal; this is NOT a weapon-fired hook'},'boarding_probe':{'attach_ability':capture,'modeled_pod_effect':'pirate_pillage_shuttle','mesh_references':meshes,'roll_count':'one10% roll per eligible delayed attempt; no damage/death trigger','arrival':'fixed3s delayed action corresponding to stock shuttle effect; not collision of a pod entity','capture_targets':'enemy capital_ship only, excludes named Rocinante; excludes supercapital/titan by unit type; unknown external mod heroes require explicit exclusions','supply':'target supply checked at cast and rechecked before transfer, includes queued/future supply','engine_gates':['delayed visual timing and source-death/cancel behavior','ownership/supply availability atomicity across concurrent attempts','capital ownership health/items/abilities/orders and faction systems','save/load at pending arrival; multiplayer RNG repeatability','visual pod is not interceptable and cannot collide physically']},'Amun_design_only':{'max_owned':6,'limit_semantics':'player empire; shared faction-wide pool across players is not evidenced','PDC_count':3,'ship_unit_and_mounts':'not generated; must use actual asset metadata','proposed_private_torpedo':{'damage':900,'speed':1500,'penetration':1000,'hull':25,'armor':50,'armor_strength':25,'status':'PROPOSAL ONLY, no changed projectile output'},'preserved_MCRN_torpedo':{'damage':750,'speed':1250,'hull':50,'armor':100,'armor_strength':50}},'cloak_release_blockers':['Pinned schemas omit installed DLC cloak fields/quality and is_cloaked. No update authorized in this task.','Preserve required_product dlc_Herald; entitlement behavior on TEC/custom unit untested.','Hit-trigger gun reveal misses are not detected; stock disable_can_auto_acquire_weapon_targets can suppress autonomous PDCs, so do not promise active hidden defensive network.','Counter probe has no provides_cloak and performs no visibility changes. Cloak reset/manual toggle/save restoration need a separate combined experiment.']})
    # Exact deterministic intended-state demonstration; not the engine evaluator.
    count_n=0;deadline=0;events=[]
    for t,kind in [(0,'torpedo'),(10,'torpedo'),(20,'torpedo'),(30,'torpedo'),(35,'torpedo'),(60,'gun_hit'),(89,'torpedo'),(90,'torpedo'),(91,'gun_hit'),(100,'torpedo')]:
        if t>=deadline:
            if kind=='torpedo':
                count_n+=1
                if count_n>=4:deadline=t+60;count_n=0
            else:deadline=t+60;count_n=0
        events.append({'time':t,'event':kind,'count':count_n,'deadline':deadline})
    assert [e['count'] for e in events[:3]]==[1,2,3] and events[3]['deadline']==90 and events[6]['deadline']==90 and events[7]['count']==1 and events[8]['deadline']==151
    write(a.output/'offline-state-model.json',{'runtime':'NOT RUN','events':events,'status':'PASS intended Python state sequence only'})
    write(a.output/'offline-validation.json',{'status':'PASS six component schemas; integrated cloak BLOCKED','runtime':'NOT RUN','schema_pin':PIN,'pinned_schema_count':len(snapshot['files']),'schema_checked':checked,'cloak_absent_top_level_fields':missing_cloak_fields,'installed_cloak_schema_errors':cloak_errors,'installed_reference_sha256':evidence,'reference_scope':'Exact code/mesh evidence hashes; final stock probe skin/UI/sound/particle texture references must be resolved by integrator','generic_weapon_fired_event_exists':False,'spawn_event':'on_current_spawner_spawned_torpedo'})
    print('PASS six standalone component schemas + intended counter state. Integrated cloak BLOCKED; runtime NOT RUN. '+str(a.output))

if __name__=='__main__':main()
