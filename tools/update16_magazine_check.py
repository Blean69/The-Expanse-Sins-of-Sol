"""Restricted interpreter of actual magazine actions, with controlled target/permission inputs.
This verifies data scheduling/ammunition only, not game targeting or save semantics.
"""
import operator
from collections import Counter
from validate_experiments import read,require
MAG='expanse10_donnager_light_magazine'

def simulate(root,level,scenario,initial_ammo=None,initial_reload=None):
    buff=read(root/'entities'/(MAG+'.buff'));ads=read(root/'entities'/(MAG+'.action_data_source'))
    values={v['action_value_id']:v['action_value']for v in ads['action_values']};mem={};now=0.;events=[];minimum=1e9
    def value(k):
        if k=='fixed_zero':return 0.
        if k=='fixed_one':return 1.
        if k=='common_simulation_time_value':return now
        d=values[k];v=d['values'][level]
        if d.get('transform_type')=='current_buff_memory_value':v*=mem.get(d['memory_float_variable_id'],0.)
        else:require('transform_type'not in d,'Unsupported transform')
        return v
    def condition(c):
        if c is None:return True
        t=c['constraint_type']
        if t=='composite_and':return all(condition(x)for x in c['constraints'])
        if t=='value_comparison':return {'equal_to':operator.eq,'greater_than':operator.gt,'less_than':operator.lt,'greater_than_equal_to':operator.ge}[c['comparison_type']](value(c['value_a']),value(c['value_b']))
        if t=='unit_passes_unit_constraint':
            u=c['unit_constraint'];kind=u['constraint_type']
            if kind=='has_buff':return scenario=='reactor' and now<30
            if kind=='is_fully_built':return True
            if kind=='has_permission':return scenario!='disabled' or now>=25
            raise ValueError(kind)
        if t=='unit_passes_target_filter':
            return (scenario!='target_gap' or now>=25)and(c['unit']['unit_type']!='buff_memory' or bool(mem.get('selected_target')))
        raise ValueError(t)
    def execute(a):
        if not condition(a.get('constraint')):return
        t=a.get('action_type',a.get('operator_type'))
        if t=='change_buff_memory_float_value':
            key=a['float_variable']
            for op in a['math_operators']:
                b=value(op['operand_value']);kind=op['operator_type']
                if kind=='assign':mem[key]=b
                elif kind=='add':mem[key]+=b
                elif kind=='subtract':mem[key]-=b
                else:raise ValueError(kind)
        elif t=='change_buff_memory_unit_value':mem[a['unit_variable']]=a['new_unit_value']['unit_type']!='none'
        elif t=='use_unit_operators_on_units_in_radius_of_unit':
            if condition(a['operators_constraint']):
                for op in a['operators']:execute(op)
        elif t=='use_position_operators_on_single_position':
            for op in a['position_operators']:
                if op['operator_type']=='create_torpedo':events.append((now,value(op['damage_value'])))
                else:require(op['operator_type']=='play_point_effect','Unknown position operator')
        else:raise ValueError(t)
    for e in buff['trigger_event_actions']:
        require(e['trigger_event_type']=='on_buff_started','Unknown event')
        for a in e['action_group']['actions']:execute(a)
    if initial_ammo is not None:mem['ammo']=initial_ammo
    if initial_reload is not None:mem['reload_ready']=initial_reload
    tick=buff['time_actions'][0];step=value(tick['execution_interval_value'])
    for i in range(int(190/step)+1):
        now=i*step
        for a in tick['action_group']['actions']:execute(a)
        minimum=min(minimum,mem['ammo'])
    return {'volleys':dict(Counter(t for t,_ in events)),'damage':sorted(set(d for _,d in events)),'minimum_ammo':minimum}

def check_magazine(out,base):
    rows=[]
    for level in [0,1]:
        for scenario in ['normal','target_gap','disabled','reactor']:
            old,new=simulate(base,level,scenario),simulate(out,level,scenario)
            require(old['volleys'].keys()==new['volleys'].keys(),'Changed firing/reload schedule')
            require(all(n==12 and old['volleys'][t]==2 for t,n in new['volleys'].items()),'Volley object count mismatch')
            require(old['damage']==new['damage'] and new['minimum_ammo']==0,'Damage changed or ammo underflow')
            if scenario=='normal':require(list(new['volleys'])[:5]==[0,10,20,30,150],'Four volleys then120s reload')
            if scenario in ['target_gap','disabled']:require(min(new['volleys'])==25,'Fired without supplied target/permission')
            rows.append({'level':level,'scenario':scenario,'volleys':new['volleys'],'per_torpedo_damage':new['damage']})
    for ammo in [2,4,6,8]:
        migrated=simulate(out,0,'normal',initial_ammo=ammo)
        require(min(migrated['volleys'])==120. and all(n==12 for n in migrated['volleys'].values()),'Old partial magazine stuck or free-refilled')
    pending=simulate(out,0,'normal',initial_ammo=0,initial_reload=45.)
    require(min(pending['volleys'])==45.,'Existing empty-magazine reload timer reset')
    return {'existing_empty_magazine':'Pending45second reload completes without reset','old_partial_magazine_migration':'2/4/6/8remaining rounds enter120second reload; no free refill','status':'PASS offline restricted action interpretation','scenarios':rows,'native_filter_truth':'Controlled test inputs; engine filters, target selection, research level transitions and save/reload NOT RUN'}
