#!/usr/bin/env python3
"""Strict supplemental validation for isolated, installed-evidenced cloak fields.

Never writes/updates schemas and never labels the complete cloak official-PASS.
"""
import argparse,copy,hashlib,json
from pathlib import Path
import jsonschema

IDS=['expanse06_amun_cloak.ability','expanse06_amun_cloak.buff','expanse06_amun_cloak.action_data_source','expanse06_amun_cloak_controller.ability','expanse06_amun_cloak_controller.buff','expanse06_amun_revealed.buff']
EXT={'.ability':'ability','.buff':'buff','.action_data_source':'action-data-source','.unit':'unit'}
def read(p):return json.loads(Path(p).read_text(encoding='utf-8-sig'))
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def walk(x,path=''):
    if isinstance(x,dict):
        for k,v in x.items():
            yield k,v,path+'/'+k
            yield from walk(v,path+'/'+k)
    elif isinstance(x,list):
        for i,v in enumerate(x):yield from walk(v,path+'/'+str(i))
def strict(name,value,sdk):
    schema=read(sdk/'json_schemas'/(EXT[Path(name).suffix]+'-schema.json'))
    for label,validator in [('pinned Draft7',jsonschema.Draft7Validator),('additional closed-key evaluation',jsonschema.Draft202012Validator)]:
        error=next(validator(schema).iter_errors(value),None)
        if error:raise AssertionError(f'{name}: {label}: /'+ '/'.join(map(str,error.path))+': '+error.message)

def validate_cloak_candidate(entities,sdk,game,*,unit_definition=None):
    entities,sdk,game=map(Path,[entities,sdk,game]);d={n:read(entities/n)for n in IDS}
    source_names=['dlc3_herald_cloak_frigate.unit','dlc3_herald_cloak_frigate_cloak.ability','dlc3_herald_cloak_frigate_cloak.buff','dlc3_herald_cloak_frigate_cloak.action_data_source','dlc3_herald_cloak_frigate_cloak_damage_dealt_degrade.buff']
    source={n:read(game/'entities'/n)for n in source_names};source_hashes={n:sha(game/'entities'/n)for n in source_names}
    ads=d['expanse06_amun_cloak.action_data_source'];values={v['action_value_id']:v['action_value']for v in ads['action_values']}
    assert len(values)==len(ads['action_values']),'Duplicate local action value'
    expected={'threshold':4.,'reveal_seconds':60.,'cloak_alpha_value':.3,'cloak_fade_duration_value':3.,'amun_cloak_quality':4.,'amun_reveal_quality':-5.,'cooldown_time_value':30.}
    for key,num in expected.items():assert values[key]=={'values':[num]},('Wrong fixed value',key)
    stockvalues={v['action_value_id']:v['action_value']['values']for v in source['dlc3_herald_cloak_frigate_cloak.action_data_source']['action_values']}
    assert 4. in stockvalues['cloak_quality_value'] and stockvalues['damage_dealt_cloak_quality_degrade_modifier_value']==[-5.,-5.]
    assert stockvalues['cloak_alpha_value']==[.3,.3] and stockvalues['cloak_fade_duration_value']==[3.,3.]
    memory=ads['per_buff_memory_declaration'];assert memory=={'float_variable_ids':['launch_count','reveal_until']}
    globals_d=read(game/'uniforms/action.uniforms')['common_action_values'];globals_v={v['action_value_id']for v in globals_d}
    all_values=set(values)|globals_v
    referenced_values=[];references=[];gui_assets=[]
    value_keys={'value_id','value_a','value_b','operand_value','active_duration','execution_interval_value','first_execution_delay_value','execution_interval_count_value','executions_per_interval_value','cooldown_time','stacking_limit','cloak_alpha_value','cloak_fade_duration_value'}
    for name,obj in d.items():
        assert 'unit_mutations' not in obj,'No shield/acquisition mutation permitted'
        for key,value,path in walk(obj):
            if key in value_keys and isinstance(value,str):
                assert value in all_values,('Unresolved action value',name,path,value);referenced_values.append((name,path,value))
            if key in ['float_variable','memory_float_variable_id']:
                assert value in memory['float_variable_ids'],('Undeclared memory',name,path,value)
            if key in ['action_data_source','persistant_buff','buff'] and isinstance(value,str):
                suffix='.action_data_source' if key=='action_data_source' else '.buff'
                assert value+suffix in d,('Unresolved private cloak ref',name,path,value);references.append((name,path,value))
            if key in ['hud_icon','tooltip_picture'] and isinstance(value,str):
                paths=[game/'brushes'/(value+'.brush'),game/'textures'/(value+'.png')]
                found=[p for p in paths if p.is_file()]
                assert found,('Unresolved stock GUI asset',name,path,value)
                gui_assets.append({'id':value,'resolved':str(found[0]),'sha256':sha(found[0])})
    clo=d['expanse06_amun_cloak.buff'];rev=d['expanse06_amun_revealed.buff'];extension_records=[]
    for name in IDS:
        known=copy.deepcopy(d[name])
        if name=='expanse06_amun_cloak.buff':
            observed={}
            for key in ['provides_cloak','required_product','cloak_alpha_value','cloak_fade_duration_value']:
                assert known[key]==source['dlc3_herald_cloak_frigate_cloak.buff'][key],('Unobserved cloak property',key)
                observed[key]=known.pop(key)
            assert observed['required_product']=='dlc_Herald' and observed['provides_cloak'] is True
            extension_records.append({'file':name,'exact_installed_extensions':observed})
        if name in ['expanse06_amun_cloak.buff','expanse06_amun_revealed.buff']:
            expected_value='amun_cloak_quality' if name=='expanse06_amun_cloak.buff' else 'amun_reveal_quality'
            modifiers=known.pop('unit_modifiers')
            assert modifiers==[{'modifier_type':'cloak_quality','value_behavior':'additive','value_id':expected_value}],'Unrecognized modifier field/value'
            extension_records.append({'file':name,'exact_observed_modifier_shape':modifiers[0]})
        strict(name,known,sdk)
    assert clo['stacking_limit']['stacking_limit_met_behavior']=='preserve_existing_buff'
    assert rev['active_duration']=='reveal_seconds' and rev['stacking_limit']['stacking_limit_met_behavior']=='preserve_existing_buff'
    assert 'make_dead_on_parent_buff_made_dead' not in rev and 'make_dead_on_source_ability_released' not in rev
    manual=d['expanse06_amun_cloak.ability'];controller=d['expanse06_amun_cloak_controller.ability']
    assert manual['level_source']=='fixed_level_0' and 'ai_only_auto_cast' not in manual['active_actions']
    assert manual['active_actions']['actions']['actions'][0]['operators']==[{'operator_type':'apply_buff','buff':'expanse06_amun_cloak'}]
    assert controller['passive_actions']=={'persistant_buff':'expanse06_amun_cloak_controller','only_if_owner_unit_operational':False}
    assert 'active_actions' not in controller and 'passive_actions' not in manual
    cb=d['expanse06_amun_cloak_controller.buff'];events=cb['trigger_event_actions']
    assert [e['trigger_event_type']for e in events]==['on_buff_started','on_current_spawner_spawned_torpedo','on_unit_damaged_by_current_spawner']
    assert cb['stacking_limit']['stacking_limit_met_behavior']=='preserve_existing_buff' and cb['restart_other_stacked_buffs_when_started'] is False
    for event in events[1:]:
        clauses=event['action_group']['constraint']['constraints']
        assert {'constraint_type':'unit_passes_unit_constraint','unit':{'unit_type':'current_spawner'},'unit_constraint':{'constraint_type':'has_buff','buff':'expanse06_amun_cloak','include_pending_buffs':False}} in clauses
        assert {'constraint_type':'value_comparison','value_a':'common_simulation_time_value','comparison_type':'greater_than_equal_to','value_b':'reveal_until_memory'} in clauses
    spawn=events[1]['action_group'];hit=events[2]['action_group']
    assert spawn['constraint']['constraints'][0]=={'constraint_type':'unit_passes_unit_constraint','unit':{'unit_type':'trigger_event_destination'},'unit_constraint':{'constraint_type':'has_definition','unit_definition':'expanse06_amun_torpedo'}}
    assert hit['constraint']['constraints'][0]=={'constraint_type':'damage_has_weapon_tag','weapon_tag':'expanse06_cloak_revealing_gun'}
    # Exact transition shape prevents an unreviewed reroll/reset or hidden timer.
    def memory_action(variable,ops):return {'action_type':'change_buff_memory_float_value','float_variable':variable,'math_operators':ops}
    zero=memory_action('launch_count',[{'operator_type':'assign','operand_value':'fixed_zero'}])
    start=memory_action('reveal_until',[{'operator_type':'assign','operand_value':'common_simulation_time_value'},{'operator_type':'add','operand_value':'reveal_seconds'}])
    apply={'action_type':'use_unit_operators_on_single_unit','destination_unit':{'unit_type':'current_spawner'},'operators':[{'operator_type':'apply_buff','buff':'expanse06_amun_revealed'}]}
    threshold={'constraint_type':'value_comparison','value_a':'launch_count_memory','comparison_type':'greater_than_equal_to','value_b':'threshold'}
    assert events[0]['action_group']['actions']==[zero,memory_action('reveal_until',[{'operator_type':'assign','operand_value':'fixed_zero'}])]
    assert spawn['actions']==[memory_action('launch_count',[{'operator_type':'add','operand_value':'fixed_one'}]),{**start,'constraint':threshold},{**apply,'constraint':threshold},{**zero,'constraint':threshold}]
    assert hit['actions']==[start,apply,zero]
    assert 'time_actions' not in cb and 'trigger_event_actions' not in clo and 'trigger_event_actions' not in rev
    if unit_definition is not None:
        u=copy.deepcopy(unit_definition);assert u.pop('cloak_ability')=='expanse06_amun_cloak'
        if 'corruption' in u:
            source_unit=game/'entities/trader_light_frigate.unit';existing=read(source_unit)['corruption']
            assert u['corruption']==existing,'Inherited Cobalt corruption may not change'
            for buff in existing['negative_corruption_buffs']:assert (game/'entities'/(buff+'.buff')).is_file(),buff
            extension_records.append({'file':'main Amun unit','exact_preserved_installed_extension':{'corruption':u.pop('corruption')},'source':'trader_light_frigate.unit','source_sha256':sha(source_unit),'scope':'Preexisting Cobalt data, not introduced by cloak; excluded only after exact byte-structure equality check'})
        strict('amun.unit',u,sdk)
        assert source['dlc3_herald_cloak_frigate.unit']['cloak_ability']=='dlc3_herald_cloak_frigate_cloak'
        abilities=[x for group in u['abilities']for x in group['abilities']]
        assert 'expanse06_amun_cloak_controller' in abilities,'Missing permanent controller ability'
        assert 'expanse06_amun_cloak' in abilities,'Expected explicit manual cloak ability entry'
        assert 'cloak_ability' not in read(sdk/'json_schemas/unit-schema.json')['properties'],'Reaudit if official unit schema changes'
        extension_records.append({'file':'main Amun unit','exact_installed_extension':{'cloak_ability':'expanse06_amun_cloak'},'source':'dlc3_herald_cloak_frigate.unit'})
    return {'status':'PASS STRICT SUPPLEMENTAL CHECKS — NOT COMPLETE OFFICIAL SCHEMA COVERAGE','official_schema':'Unchanged pinned Draft7 validates known subsets;2 cloak buffs, optional unit cloak hook and any exact inherited Cobalt corruption object are explicitly listed installed-only extensions','additional_unknown_key_check':'Same pinned schema additionally evaluated with Draft2020 unevaluatedProperties handling; no schema files modified','extensions':extension_records,'source_sha256':source_hashes,'checked_private_files':IDS,'resolved_local_or_uniform_values':referenced_values,'resolved_private_references':references,'GUI_assets':gui_assets,'unit_hook_checked':unit_definition is not None,'runtime':'NOT RUN','limitations':['No proof of engine memory/event ordering or save serialization','No proof of product entitlement or cloak detector rendering','Hits reveal; missed PDC/rail shots do not','Three individual torpedoes: second pair reveals on fourth projectile']}

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--entities',type=Path,required=True);p.add_argument('--sdk',type=Path,required=True);p.add_argument('--game',type=Path,required=True);p.add_argument('--report',type=Path);a=p.parse_args()
    result=validate_cloak_candidate(a.entities,a.sdk,a.game)
    if a.report:
        root=Path(__file__).resolve().parents[1]/'audit/amun06-a';assert a.report.resolve().is_relative_to(root);a.report.parent.mkdir(parents=True,exist_ok=True);a.report.write_text(json.dumps(result,indent=2)+'\n')
    print(result['status'])
