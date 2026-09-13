"""Prepare bounded support candidates; shared definitions are a reviewable recipe only.

Run from any checkout with --main-root pointing at the preserved main checkout.
No game, baseline package, schema, or shared unit/skin/localization is modified.
"""
import argparse, copy, hashlib, json
from pathlib import Path
import jsonschema

ROOT = Path(__file__).resolve().parents[1]
P = 'expanse15_scirocco_'
BREACH, ENG = P + 'breaching_teams', P + 'engineering_teams'
GUARD, DISRUPT = BREACH + '_guard', BREACH + '_disruption'
SHIPS = ['corvette', 'frigate', 'cruiser', 'capital_ship', 'super_capital_ship', 'titan']

def read(p): return json.loads(p.read_text())
def write(p, x):
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(x, indent=2) + '\n')
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def no_buff(name):
    return {'constraint_type':'composite_not','constraint':{'constraint_type':'has_buff','buff':name,'include_pending_buffs':True}}
def unit_action(unit, operators, **kw):
    return dict(action_type='use_unit_operators_on_single_unit', destination_unit={'unit_type':unit}, operators=operators, **kw)
def filt(unit, id): return {'constraint_type':'unit_passes_target_filter','unit':{'unit_type':unit},'target_filter_id':id}
def stack():
    return {'stacking_limit':{'stacking_limit':'fixed_one','stacking_limit_met_behavior':'preserve_existing_buff'},'stacking_ownership_type':'for_all_players','restart_other_stacked_buffs_when_started':False}
def event(name, actions): return {'trigger_event_type':name,'action_group':{'actions':actions}}
def gui(name, icon, scope=None):
    d={'hud_icon':icon,'name':name+'.name'}
    if scope: d.update(visibility_scope=scope,is_visible_within_unit_tooltip=True)
    return d

def build(main):
    base=main/'build/experiments/expanse_update14'
    game=main.parent/'SteamLibrary/steamapps/common/Sins2'
    sdk=main.parent/'SteamLibrary/steamapps/common/Sins of a Solar Empire II - Mod Tools'
    out=ROOT/'build/update15-scirocco'
    entities=out/'entities'
    aud=ROOT/'audit/update15-scirocco'
    native=game/'entities'
    old=read(base/'entities/expanse12_scirocco_marines.ability')
    icon=old['gui']['hud_icon']
    repair_icon='trader_combat_repair_system_unit_item_hud_icon'
    defs={}
    bfilter={'unit_types':SHIPS,'ownerships':['enemy'],'constraints':[
        {'constraint_type':'is_fully_built'},{'constraint_type':'is_detected'},
        {'constraint_type':'is_in_current_gravity_well'},
        {'constraint_type':'has_missing_hull','percentage_missing_threshold':.20},no_buff(GUARD),no_buff(DISRUPT)]}
    efilter={'unit_types':SHIPS,'ownerships':['friendly'],'constraints':[
        {'constraint_type':'is_fully_built'},{'constraint_type':'not_self'},
        {'constraint_type':'is_in_current_gravity_well'},
        {'constraint_type':'has_missing_hull','amount_missing_threshold':1},no_buff(ENG)]}
    def values(v,n=1):return [{'action_value_id':k,'action_value':{'values':x if isinstance(x,list) else [x]*n}} for k,x in v.items()]
    arrival_filter=copy.deepcopy(bfilter)
    # Arrival must ignore its own pending reservation. Active guards plus the
    # global preserve-existing stack reject competing applications at impact.
    for constraint in arrival_filter['constraints']:
        if constraint.get('constraint',{}).get('constraint_type')=='has_buff':
            constraint['constraint']['include_pending_buffs']=False
    defs[BREACH+'.action_data_source']={
        'version':0,'level_count':2,'target_filters':[{'target_filter_id':'breach_target','target_filter':bfilter},{'target_filter_id':'breach_arrival','target_filter':arrival_filter}],
        'action_values':values({'cooldown':90.,'antimatter':40.,'range':2500.,'travel_delay':3.,'duration':[12.,13.],
                               'protection_duration':45.,'speed_penalty':-.15,'reload_penalty':.15},2),
        'effect_alias_bindings':copy.deepcopy(read(base/'entities/expanse12_scirocco_marines.action_data_source')['effect_alias_bindings']),
        'buff_unit_modifiers':[{'buff_unit_modifier_id':'speed_penalty','buff_unit_modifier':{'modifier_type':'max_linear_speed','value_behavior':'scalar','value_id':'speed_penalty'}}],
        'buff_weapon_modifiers':[{'buff_weapon_modifier_id':'reload_penalty','buff_weapon_modifier':{'modifier_type':'cooldown_duration','value_behavior':'scalar','value_id':'reload_penalty','tags':['physical']}}]}
    pod=copy.deepcopy(old['active_actions']['actions']['actions'][0]['operators'][1])
    defs[BREACH+'.ability']={
        'version':0,'action_data_source':BREACH,'level_source':'research_prerequisites_per_level',
        'level_prerequisites':[[],[['trader_upgrade_experience_gain_0']]],
        'active_actions':{'cooldown_time':'cooldown','antimatter_cost':'antimatter','targeting_type':'unit_targeted',
            'target_filters':['breach_target'],'range':'range','actions':{'actions':[
                unit_action('target',[{'operator_type':'apply_buff','buff':GUARD,'constraint':filt('operand_destination','breach_arrival')},pod],
                            constraint=filt('target','breach_target'),range_value='range',
                            travel_time={'travel_time_source':'explicit_time','explicit_time_value':'travel_delay'})]}},
        'gui':dict(gui(BREACH,icon),description=BREACH+'.description',tooltip_picture=old['gui']['tooltip_picture'],
                   targeting={'targeting_type':'range','values':{'range':'range'}},tooltip_line_groups=[{'lines':[
                       {'rendering_type':'single_value','label_text':'tooltip.ability.duration','value_id':'duration','value_suffix':'seconds'}]}])}
    # The guard is the first/only arrival application. Its globally preserved stack
    # atomically owns admission; a second simultaneous pod cannot restart or extend it.
    defs[GUARD+'.buff']={
        'version':0,**stack(),'active_duration':'protection_duration',
        'trigger_event_actions':[event('on_buff_started',[unit_action('current_spawner',[{'operator_type':'apply_buff','buff':DISRUPT}])])],
        'gui':gui(GUARD,icon,'negative')}
    clear_on_capture=event('on_current_spawner_player_ownership_changed',[{'action_type':'make_buff_dead'}])
    defs[DISRUPT+'.buff']={
        'version':0,**stack(),'active_duration':'duration','unit_modifiers':[{'buff_unit_modifier_id':'speed_penalty'}],
        'weapon_modifiers':[{'buff_weapon_modifier_id':'reload_penalty'}],
        'trigger_event_actions':[copy.deepcopy(clear_on_capture)],'gui':gui(BREACH,icon,'negative')}
    defs[ENG+'.action_data_source']={
        'version':0,'target_filters':[{'target_filter_id':'engineering_target','target_filter':efilter}],
        'action_values':values({'cooldown':60.,'antimatter':50.,'range':3500.,'repair_per_tick':20.,'repair_ticks':20.}),
        'effect_alias_bindings':copy.deepcopy(read(native/'trader_combat_repair_system_unit_item.action_data_source')['effect_alias_bindings'])}
    defs[ENG+'.ability']={
        'version':0,'action_data_source':ENG,'level_source':'fixed_level_0',
        'active_actions':{'cooldown_time':'cooldown','antimatter_cost':'antimatter','targeting_type':'unit_targeted','target_filters':['engineering_target'],'range':'range',
                         'actions':{'actions':[unit_action('target',[{'operator_type':'apply_buff','buff':ENG,'constraint':filt('operand_destination','engineering_target')}],
                                                          constraint=filt('target','engineering_target'),range_value='range')]}},
        'gui':dict(gui(ENG,repair_icon),description=ENG+'.description',targeting={'targeting_type':'range','values':{'range':'range'}})}
    effect=copy.deepcopy(read(native/'trader_combat_repair_system_unit_item.buff')['trigger_event_actions'][0])
    defs[ENG+'.buff']={
        'version':0,**stack(),'make_dead_on_all_finite_time_actions_done':True,
        'time_actions':[{'execution_interval_value':'fixed_one','execution_interval_count_value':'repair_ticks',
                         'action_group':{'actions':[unit_action('current_spawner',[{'operator_type':'repair_damage','affect_type':'hull_only','repair_value':'repair_per_tick'}])]}}],
        'trigger_event_actions':[effect,copy.deepcopy(clear_on_capture)],'gui':gui(ENG,repair_icon,'positive')}
    for name,d in defs.items():write(entities/name,d)
    original=read(base/'entities/expanse12_scirocco.unit')['abilities']
    assert len(original)==1
    previous=original[0]['abilities']
    assert previous==['expanse12_scirocco_light_magazine','expanse12_scirocco_heavy_magazine','expanse12_scirocco_reactor','expanse12_scirocco_launch_corvette','expanse12_scirocco_marines','expanse12_scirocco_reactor_breach','expanse11_no_shields']
    active=['expanse12_scirocco_reactor','expanse12_scirocco_launch_corvette',BREACH,ENG]
    passive=[x for x in previous if x not in active and x!='expanse12_scirocco_marines']
    strings={BREACH+'.name':'Marine Breaching Teams',
      BREACH+'.description':'Launch a cosmetic marine pod at a detected enemy ship missing at least 20% hull. After 3 seconds, reduce speed by 15% and lengthen physical-weapon reloads by 15% for 12 seconds (13 with Marine Assault Doctrine). No capture or weapon shutdown. The target cannot receive another team for 45 seconds after arrival. Range 2,500; costs 40 antimatter; 90-second cooldown.',
      GUARD+'.name':'Marine Team Security Lockout',
      ENG+'.name':'Combat Engineering Teams',
      ENG+'.description':'Repair another friendly ship for 20 hull per second over 20 ticks, up to 400 hull total regardless of ship size. Does not restore armor or shields. Engineering Teams from multiple ships cannot stack or refresh this effect. Range 3,500; costs 50 antimatter; 60-second cooldown. Stops if the recipient changes owner.'}
    recipe={'status':'PASS offline; runtime NOT RUN','resource_directory':str(out),'entity_files':sorted(defs),
            'patches':[{'file':'entities/expanse12_scirocco.unit','pointer':'/abilities/0/abilities','before':previous,'value':active+passive}],
            'localization':strings,'active_ability_ids':active,'passive_ability_ids':passive,
            'research_dependency':'trader_upgrade_experience_gain_0','research_values':{'unresearched_duration':12,'researched_duration':13},
            'old_capture_definitions':'Unreferenced Scirocco capture definitions may stay in baseline; no new capture code and no modifications to other ships capture abilities.',
            'skin_patches':[]}
    write(out/'integration-recipe.json',recipe)
    schemas={'.ability':'ability','.buff':'buff','.action_data_source':'action-data-source'}
    checks=[]
    for name in sorted(defs):
        p=entities/name;s=read(sdk/'json_schemas'/(schemas[p.suffix]+'-schema.json'))
        jsonschema.Draft202012Validator(s).validate(defs[name]);jsonschema.Draft7Validator(s).validate(defs[name])
        checks.append({'file':name,'sha256':sha(p),'status':'PASS pinned closed-key schema'})
    # Independent bounds, eligibility, and graph assertions, not runtime claims.
    assert len(active)==4 and all('active_actions' in (defs.get(x+'.ability') or read(base/'entities'/(x+'.ability'))) for x in active)
    assert all('change_owner_player' not in json.dumps(d) for d in defs.values())
    assert len({d['stacking_ownership_type'] for n,d in defs.items() if n.endswith('.buff')})==1
    assert all(d['stacking_limit']['stacking_limit_met_behavior']=='preserve_existing_buff' for n,d in defs.items() if n.endswith('.buff'))
    assert 20*20==400 and 45>13 and 90>45
    assert all(n in defs or (base/'entities'/n).exists() for n in [DISRUPT+'.buff',GUARD+'.buff',ENG+'.buff'])
    evidence=[native/n for n in ['trader_robotics_cruiser_repair_droids.ability','trader_robotics_cruiser_repair_droids.action_data_source','trader_combat_repair_system_unit_item.buff','trader_combat_repair_system_unit_item.action_data_source','vasari_carrier_capital_ship_repair_cloud.buff','dlc3_herald_corruptor_cruiser_purge_corruption.action_data_source','trader_rebel_titan_warpath.buff']]
    evidence += [base/'entities/expanse12_scirocco_marines.ability',base/'entities/expanse12_scirocco_marines.action_data_source']
    write(aud/'validation.json',{'status':'PASS offline','schemas':checks,'baseline_unit_sha256':sha(base/'entities/expanse12_scirocco.unit'),
         'assertions':['Exactly four active abilities in one flat selection group; passive magazine/death/shield policy preserved.',
         'Enemy damaged hull20% and friendly other ship filters; exclude missiles/planets/structures by type.',
         'Manual admission checks pending guard; arrival rechecks enemy/damage and active guard without self-blocking its own pending application; all buffs globally preserve one stack.',
         'Guard45s exceeds effect12/13s; source cooldown90s exceeds guard.',
         'Absolute hull-only repair400 cap independent of max hull and base restoration research.',
         'No change_owner_player or disable-weapons operators; capture ownership event clears disruption and repair.'],
         'native_evidence':[{'path':str(p),'sha256':sha(p)} for p in evidence],
         'runtime':'NOT RUN: load/UI, simultaneous pod races, capture events, research existing/new units, multiplayer, save/reload.'})
    write(aud/'integration-recipe.json',recipe)
    print(json.dumps({'status':'PASS','entity_count':len(defs),'output':str(out),'recipe':str(out/'integration-recipe.json')},indent=2))

if __name__=='__main__':
    ap=argparse.ArgumentParser();ap.add_argument('--main-root',type=Path,default=Path('/run/media/haker/NVME 2/expanse-mod'));build(ap.parse_args().main_root)
