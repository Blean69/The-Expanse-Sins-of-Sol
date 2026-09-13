#!/usr/bin/env python3
"""Read-only Donnager component/ADS checks; no package or engine-test claim."""
import argparse, copy, hashlib, json, os, sys
from pathlib import Path
import jsonschema

ROOT=Path(__file__).resolve().parents[1]
def read(p): return json.loads(Path(p).read_text(encoding='utf-8-sig'))
def sha(p): return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def walk(d,path=''):
    if isinstance(d,dict):
        for k,v in d.items():
            yield k,v,path+'/'+k
            yield from walk(v,path+'/'+k)
    elif isinstance(d,list):
        for i,v in enumerate(d): yield from walk(v,path+'/'+str(i))

def deadline_model():
    """Arithmetic model of declared polling, explicitly not a Sins simulation."""
    def finish(seconds,boost_until):
        deadline=float(seconds); now=0.
        while now<seconds+1:
            if now<boost_until and deadline>now: deadline-=.125
            if now>=deadline: return now
            now+=.25
        raise AssertionError('Deadline did not elapse')
    results=[]
    for seconds,boost,expected in [(10,0,10),(10,30,6.75),(15,30,10),(120,0,120),(120,30,105)]:
        actual=finish(seconds,boost); assert actual==expected,(seconds,boost,actual)
        results.append(dict(initial_remaining_seconds=seconds,boost_seconds=boost,modeled_completion=actual))
    return {'status':'PASS arithmetic model only','cases':results,'poll_seconds':.25,'extra_progress_per_active_poll':.125,'runtime':'NOT RUN','boundary_note':'Model polls at t=0; engine event order can shift a boundary poll. It does not establish save serialization or runtime modifiers.'}

def validate_components(candidate,base,game,sdk,source_root,*,integrated=None):
    candidate,base,game,sdk,source_root=map(Path,[candidate,base,game,sdk,source_root])
    os.environ['SINS2_GAME']=str(game);os.environ['SINS2_SDK']=str(sdk)
    sys.path.insert(0,str(source_root/'tools'))
    from validate_experiments import Resolver,verify_pins
    pins=verify_pins(source_root,game,sdk)
    recipe=read(candidate/'integration-recipe.json')
    target=Path(integrated) if integrated else candidate
    resolver=Resolver(base,game)
    for p in target.rglob('*'):
        if p.is_file():resolver.index[p.relative_to(target).as_posix().lower()]=(p,'candidate' if not integrated else 'integrated')
    schemas={'.weapon':'weapon','.unit':'unit','.ability':'ability','.buff':'buff','.action_data_source':'action-data-source'}
    docs={name:read(target/'entities'/name) for name in recipe['all_entity_files']}
    checks=[]
    for name,d in docs.items():
        original=read(candidate/'entities'/name); normalized=copy.deepcopy(d)
        # Main-owned geometry binding is the only permitted component delta.
        if name.endswith('.weapon'):
            if 'turret' not in original:normalized.pop('turret',None)
            if '_rail_' in name:
                for k,expected in [('yaw_speed',15.),('pitch_speed',0.),('yaw_firing_tolerance',.5),('pitch_firing_tolerance',1.)]:
                    if integrated:assert normalized.get(k)==expected,('Unreviewed rail geometry speed/tolerance',name,k)
                    if k in original:normalized[k]=original[k]
                    else:normalized.pop(k,None)
        if '_magazine.ability' in name:normalized.pop('ability_positions',None)
        if '_marines.buff' in name:
            for k,v,path in walk(normalized):
                if k=='mesh_point' and isinstance(v,str):
                    parent=normalized
                    bits=path.split('/')[1:]
                    for bit in bits[:-1]:parent=parent[int(bit)] if isinstance(parent,list) else parent[bit]
                    original_parent=original
                    for bit in bits[:-1]:original_parent=original_parent[int(bit)] if isinstance(original_parent,list) else original_parent[bit]
                    parent[bits[-1]]=original_parent[bits[-1]]
        if '_marines.action_data_source' in name:
            for got,want in zip(normalized.get('effect_alias_bindings',[]),original.get('effect_alias_bindings',[]),strict=True):
                if 'particle_effect' in got and 'particle_effect' in want:got['particle_effect']=want['particle_effect']
        assert normalized==original,('Unexpected component delta',name)
        schema=read(sdk/'json_schemas'/(schemas[Path(name).suffix]+'-schema.json'))
        jsonschema.Draft7Validator(schema).validate(d)
        jsonschema.Draft202012Validator(schema).validate(d)
        checks.append(name)
    common=read(game/'uniforms/action.uniforms')
    common_values={v for k,v,_ in walk(common)if k=='action_value_id'}
    uniform_filters={x['target_filter_id'] for x in read(game/'uniforms/target_filter.uniforms')['common_target_filters']}
    group_rows=read(game/'uniforms/attack_target_type_group.uniforms')['attack_target_type_groups']
    groups={x['unit_attack_target_type_group_id']:x['unit_attack_target_type_group'] for x in group_rows}
    loc=read(game/'localized_text/en.localized_text');loc.update(read(base/'localized_text/en.localized_text'));loc.update(read(candidate/'localization.json'))
    if integrated:loc.update(read(target/'localized_text/en.localized_text'))
    aliases=read(candidate/'ship-effect-aliases.json')
    skin_aliases={x['alias_name'] for x in aliases}
    for row in aliases:
        for k,v,_ in walk(row):
            if k in ['particle_effect','beam_effect','sound']:resolver.resolve(('sounds/' if k=='sound' else 'effects/')+v+'.'+k,'ship effect aliases')
    value_keys={'value_id','value_a','value_b','operand_value','active_duration','execution_interval_value','first_execution_delay_value','execution_interval_count_value','executions_per_interval_value','cooldown_time','antimatter_cost','credits_cost','metal_cost','crystal_cost','required_available_supply','range','first_action_delay_time_value','execution_interval','value'}
    refs=[];value_count=0
    for ability_id in recipe['core_abilities']:
        name=ability_id+'.ability';ability=docs[name]
        ads_path=resolver.resolve('entities/'+ability['action_data_source']+'.action_data_source',name)
        ads=read(ads_path)
        values={x['action_value_id'] for x in ads.get('action_values',[])}|common_values
        assert len({x['action_value_id']for x in ads.get('action_values',[])})==len(ads.get('action_values',[]))
        filters={x['target_filter_id']for x in ads.get('target_filters',[])}|uniform_filters
        memory=ads.get('per_buff_memory_declaration',{})
        float_ids=set(memory.get('float_variable_ids',[]));unit_ids=set(memory.get('unit_variable_ids',[]))
        unit_modifiers={x['buff_unit_modifier_id']for x in ads.get('buff_unit_modifiers',[])}
        weapon_modifiers={x['buff_weapon_modifier_id']for x in ads.get('buff_weapon_modifiers',[])}
        ads_aliases={x['alias_name']for x in ads.get('effect_alias_bindings',[])}
        todo=[(name,ability),(str(ads_path),ads)];done=set()
        while todo:
            source,obj=todo.pop()
            if source in done:continue
            done.add(source)
            for k,v,path in walk(obj):
                if k=='binding' and v in ['unit_skin','action_data_source']:
                    parent=obj
                    for bit in path.split('/')[1:-1]:parent=parent[int(bit)]if isinstance(parent,list)else parent[bit]
                    if 'effect' in parent:assert parent['effect'] in (skin_aliases if v=='unit_skin' else ads_aliases),(source,path,parent['effect'])
                if k=='target_filters' and isinstance(v,list) and all(isinstance(x,str)for x in v):assert set(v)<=filters,(source,path,v)
                if not isinstance(v,str):continue
                if (k.endswith('_value') or k in value_keys) and not k in {'transform_type'}:
                    assert v in values,(source,path,'missing action value',v);value_count+=1
                if k in ['float_variable','memory_float_variable_id']:assert v in float_ids,(source,path,'undeclared float',v)
                if k in ['unit_variable','memory_unit_variable_id']:assert v in unit_ids,(source,path,'undeclared unit memory',v)
                if k=='buff_unit_modifier_id':assert v in unit_modifiers,(source,path,v)
                if k=='buff_weapon_modifier_id':assert v in weapon_modifiers,(source,path,v)
                if k in ['target_filter_id','target_filter']:assert v in filters,(source,path,v)
                if k in ['buff','persistant_buff','watched_buff']:
                    p=resolver.resolve('entities/'+v+'.buff',source);refs.append(str(p))
                    # has_buff only tests existence; it does not inherit this ADS.
                    parent=obj
                    for bit in path.split('/')[1:-1]:parent=parent[int(bit)]if isinstance(parent,list)else parent[bit]
                    if parent.get('constraint_type')!='has_buff':todo.append((str(p),read(p)))
                if k in ['torpedo_to_create','unit_definition'] or k=='unit' and '/required_units/' in path:
                    p=resolver.resolve('entities/'+v+'.unit',source);refs.append(str(p))
                    if k=='torpedo_to_create':
                        u=resolver.unit(v,source);assert 'torpedo'in u and u['target_filter_unit_type']=='torpedo' and u['ai_attack_target']['attack_target_type']=='torpedo'
                if k in ['hud_icon','tooltip_picture','tooltip_icon']:
                    rel='brushes/'+v+'.brush';resolver.resolve(rel if rel.lower()in resolver.index else 'textures/'+v+'.png',source)
                if k in ['name','description','label_text']:assert v in loc,(source,path,'missing localization',v)
                if k in ['particle_effect','beam_effect','sound']:
                    resolver.resolve(('sounds/'if k=='sound'else'effects/')+v+'.'+k,source)
    for name,d in docs.items():
        if name.endswith('.weapon'):
            assert d['uniforms_target_filter_id'] in uniform_filters
            assert set(d['attack_target_type_groups'])<=groups.keys()
            assert all(v in skin_aliases for k,v in d['effects'].items()if k.endswith('_effect')and isinstance(v,str))
            assert 'physical' in d['tags']
    assert sum(docs[x+'.weapon']['damage']/docs[x+'.weapon']['cooldown_duration']for x in recipe['pdc_ids'])==896
    assert recipe['shared_titan_limit']['confirmed_user_choice'] and recipe['shared_titan_limit']['build_kind']=='titan'
    return {'status':'PASS private component schemas, exact delta and scoped references','schema_count':len(checks),'pin_check':pins,'schema_coverage':'Pinned Draft7 plus same schema evaluated under Draft2020 for closed keys; no schema modifications','checked_action_value_references':value_count,'references':resolver.edges,'resolved_unique_files':{str(p):sha(p)for p in {Path(x['resolved'])for x in resolver.edges}},'magazine_arithmetic':deadline_model(),'heavy_projectile_group':groups['defense_starbase_titan'],'bound_unit_geometry_checked':False,'runtime':'NOT RUN','limits':['Reference traversal stops at untouched installed effect/audio/death resources','Main must validate unit, manifests, mount positions, turret frames, alias attachment and package preservation','Existing defense_starbase_titan includes defense; heavy launch filters strictly starbase/titan but postlaunch retargeting remains an engine question']}

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--candidate',type=Path,required=True);p.add_argument('--base',type=Path,required=True);p.add_argument('--game',type=Path,required=True);p.add_argument('--sdk',type=Path,required=True);p.add_argument('--source-root',type=Path,required=True);p.add_argument('--integrated',type=Path);p.add_argument('--report',type=Path,required=True);a=p.parse_args()
    assert a.report.resolve().is_relative_to(ROOT/'audit/donnager10-a'),'Report outside worker ownership'
    report=validate_components(a.candidate,a.base,a.game,a.sdk,a.source_root,integrated=a.integrated)
    a.report.parent.mkdir(parents=True,exist_ok=True);a.report.write_text(json.dumps(report,indent=2)+'\n');print(report['status']);print('schemas',report['schema_count'],'action values',report['checked_action_value_references'],'references',len(report['references']))
