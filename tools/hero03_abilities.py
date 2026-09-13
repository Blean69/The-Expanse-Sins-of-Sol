"""Generate private Rocinante ability candidates from pinned installed patterns.
No installation; numeric balance is provisional and runtime remains untested.
"""
import argparse, copy, json
from pathlib import Path
import jsonschema

def write(p, d):
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(d, indent=2)+'\n')

def generate(game, sdk, out):
    ent=game/'entities'; generated=out/'generated'; strings={}; rows=[]
    def emit(name, ext, data):
        schema={'ability':'ability','buff':'buff','action_data_source':'action-data-source'}[ext]
        jsonschema.Draft7Validator(json.loads((sdk/'json_schemas'/f'{schema}-schema.json').read_text())).validate(data)
        write(generated/'entities'/f'{name}.{ext}',data);rows.append(f'{name}.{ext}')
    def ads(values, modifiers=()):
        d={'version':0,'action_values':[{'action_value_id':k,'action_value':{'values':[v]}} for k,v in values.items()]}
        if modifiers:d['buff_unit_modifiers']=[{'buff_unit_modifier_id':k,'buff_unit_modifier':{'modifier_type':t,'value_behavior':'scalar','value_id':v}} for k,t,v in modifiers]
        return d
    def gui(name,title,description,icon):
        strings[name+'_name']=title;strings[name+'_description']=description
        return {'name':name+'_name','description':name+'_description','hud_icon':icon,'tooltip_icon':icon}
    def apply(name):return {'actions':[{'action_type':'use_unit_operators_on_single_unit','destination_unit':{'unit_type':'current_spawner'},'operators':[{'operator_type':'apply_buff','buff':name}]}]}
    stack={'stacking_limit':{'stacking_limit':'fixed_one','stacking_limit_met_behavior':'restart_existing_buff'},'stacking_ownership_type':'for_all_players','restart_other_stacked_buffs_when_started':True}
    name='expanse_roci_belter_ingenuity'
    emit(name,'action_data_source',ads({'cooldown':90,'duration':10,'repair':100}))
    emit(name,'ability',{'version':0,'action_data_source':name,'level_source':'fixed_level_0','active_actions':{'cooldown_time':'cooldown','actions':apply(name)},'gui':gui(name,'Belter Ingenuity','Repairs 100 hull per second for 10 seconds. Cooldown: 90 seconds.','trader_combat_repair_system_unit_item_hud_icon')})
    emit(name,'buff',{'version':0,**copy.deepcopy(stack),'make_dead_on_all_finite_time_actions_done':True,'time_actions':[{'execution_interval_value':'fixed_one','execution_interval_count_value':'duration','action_group':{'actions':[{'action_type':'use_unit_operators_on_single_unit','destination_unit':{'unit_type':'current_spawner'},'operators':[{'operator_type':'repair_damage','affect_type':'hull_only','repair_value':'repair'}]}]}}]})
    name='expanse_roci_overcharged_reactor'
    emit(name,'action_data_source',ads({'cooldown':60,'duration':10,'antimatter':50,'speed':.5},[('speed','max_linear_speed','speed')]))
    emit(name,'ability',{'version':0,'action_data_source':name,'level_source':'fixed_level_0','active_actions':{'cooldown_time':'cooldown','antimatter_cost':'antimatter','actions':apply(name)},'gui':gui(name,'Overcharged Reactor','Costs 50 antimatter; increases maximum movement speed by 50% for 10 seconds. Cooldown: 60 seconds.','jiskun_tachyon_boost_hud_icon')})
    emit(name,'buff',{'version':0,**copy.deepcopy(stack),'active_duration':'duration','unit_modifiers':[{'buff_unit_modifier_id':'speed'}]})
    name='expanse_roci_morale'
    a=ads({'linger':2,'repair_bonus':.15},[('hull_repair','hull_point_restore_rate','repair_bonus'),('armor_repair','armor_point_restore_rate','repair_bonus')])
    a['target_filters']=[{'target_filter_id':'allied_ships','target_filter':{'ownerships':['friendly'],'unit_types':['capital_ship','corvette','cruiser','frigate','super_capital_ship','titan']}}]
    emit(name,'action_data_source',a)
    emit(name,'ability',{'version':0,'action_data_source':name,'level_source':'fixed_level_0','passive_actions':{'persistant_buff':name},'gui':gui(name,'Morale Boost','Allied ships in this gravity well receive +15% natural hull and armor repair rate. Does not remove repair delays or increase scripted repair abilities.','trader_colony_capital_ship_inspiring_broadcast_ability_hud_icon')})
    emit(name,'buff',{'version':0,**copy.deepcopy(stack),'time_actions':[{'execution_interval_value':'fixed_one','action_group':{'actions':[{'action_type':'use_unit_operators_on_units_in_gravity_well_of_unit','gravity_well_origin_unit':{'unit_type':'current_spawner'},'operators':[{'constraint':{'constraint_type':'unit_passes_target_filter','unit':{'unit_type':'operand_destination'},'target_filter_id':'allied_ships'},'operator_type':'apply_buff','buff':name+'_recipient'}]}]}}]})
    emit(name+'_recipient','buff',{'version':0,**copy.deepcopy(stack),'active_duration':'linger','unit_modifiers':[{'buff_unit_modifier_id':'hull_repair'},{'buff_unit_modifier_id':'armor_repair'}]})
    write(generated/'localized_text/en.localized_text',strings)
    write(out/'integration-spec.json',{'status':'PASS_OFFLINE_CANDIDATE','runtime':'NOT RUN','abilities':['expanse_roci_belter_ingenuity','expanse_roci_overcharged_reactor','expanse_roci_morale'],'schemas_validated':rows,'aura_limits':'Natural hull/armor regeneration only; 1s refresh and up to2s linger after exit/death; fixed-one prevents duplicate aura stacking. Friendly ownership semantics require allied-player test.','installed_patterns':['trader_combat_repair_system_unit_item.ability','trader_combat_repair_system_unit_item.buff','jiskun_tachyon_boost.ability','jiskun_tachyon_boost.action_data_source','jiskun_tachyon_boost.buff','trader_colony_capital_ship_mobile_trade_port.ability','trader_colony_capital_ship_inspiring_broadcast_on_spawner.buff','singularity_time_dilation_star_bonus.action_data_source']})
    print(f'{len(rows)} ability/ADS/buff schema checks PASS; runtime NOT RUN')
if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--game',type=Path,required=True);p.add_argument('--sdk',type=Path,required=True);p.add_argument('--out',type=Path,default=Path('build/hero03-main'));a=p.parse_args();generate(a.game,a.sdk,a.out)
