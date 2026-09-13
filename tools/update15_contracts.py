"""Independent data-contract checks for the assembled0.15 package (not engine simulation)."""
from pathlib import Path
import copy
from validate_experiments import read,require
from build_update15 import OUT,BASE,GAME,AUD,PLAYERS

def walk(x):
    if isinstance(x,dict):
        yield x
        for v in x.values():yield from walk(v)
    elif isinstance(x,list):
        for v in x:yield from walk(v)

def run():
    snap=read(AUD/'before-research-definitions.json');report=read(AUD/'research/integration.json')
    for row in report['changes']:
        p=OUT/row['file'];new=read(p)
        if p.suffix=='.ability':
            old=snap[p.name];require(new.pop('level_prerequisites')==[[],[['trader_missile_weapon_damage_0']]],'Warhead prerequisites')
            require(new['level_source']=='research_prerequisites_per_level','Warhead levels')
            new['level_source']=old['level_source'];require(new==old,'Unexpected ability change')
        elif p.suffix=='.action_data_source':
            old=snap[p.name]
            for v in new['action_values']:
                av=v['action_value']
                if 'values'in av:
                    a,b=av['values'];require(b==(round(a*1.05,8)if v['action_value_id']=='heavy_torpedo_damage_value'else a),'Unintended researched scalar');av['values']=[a]
            require(new==old,'Unexpected ADS change')
        elif p.suffix=='.research_subject':
            old=read(GAME/'entities'/p.name)
            for k in ['domain','tier','field','field_coord','price','exotic_price','research_time','prerequisites','windfall']:
                require(new.get(k)==old.get(k),'Changed research structural/economic field '+p.name+'/'+k)
    for pid in PLAYERS:
        old=read(BASE/'entities'/(pid+'.player'));new=read(OUT/'entities'/(pid+'.player'))
        require(new['buildable_units'].pop()=='expanse15_truman','Unexpected roster append')
        require(new['structures'].pop()=='expanse15_missile_defense','Unexpected structure append')
        for i,e in enumerate(new.get('trade',{}).get('trade_ship_escorts',[])):
            require(e['unit']in ['trader_light_frigate','expanse_mcrn_corvette'],'Wrong escort')
            e['unit']=old['trade']['trade_ship_escorts'][i]['unit']
        require(new==old,'Other player behavior changed')
    mag=read(OUT/'entities/expanse15_truman_light_magazine.buff')
    launches=[x for x in walk(mag)if x.get('operator_type')=='create_torpedo']
    require(len(launches)==6 and all(x['torpedo_to_create']=='expanse15_unn_light_torpedo'for x in launches),'UNN must physically spawn six rounds')
    values={v['action_value_id']:v['action_value'].get('values')for v in read(OUT/'entities/expanse15_truman_light_magazine.action_data_source')['action_values']}
    for k,v in {'magazine_capacity_value':36,'magazine_pair_count_value':6,'magazine_pair_interval_value':10.,'magazine_reload_duration_value':120.}.items():require(values[k]==[v,v],'UNN clock/count contract')
    require(values['heavy_torpedo_damage_value']==[375.,393.75],'UNN half damage')
    require(not any('expanse12_raptor_reactor' in str(x)for x in walk(mag)),'UNN inherited Martian reactor clock')
    clocks=[x for x in walk(mag)if x.get('action_type')=='change_buff_memory_float_value']
    for timer in ['next_pair_ready','reload_ready']:require(any(x.get('float_variable')==timer and any(o.get('operator_type')=='add'for o in x['math_operators'])for x in clocks),'Magazine advancement missing '+timer)
    eng=read(OUT/'entities/expanse15_scirocco_engineering_teams.action_data_source');ev={v['action_value_id']:v['action_value']['values']for v in eng['action_values']if 'values'in v['action_value']}
    require(ev['repair_ticks']==[20.] and ev['repair_per_tick']==[20.],'Fixed400repairbudget')
    for fname in ['expanse15_scirocco_engineering_teams','expanse15_scirocco_breaching_teams_guard','expanse15_scirocco_breaching_teams_disruption']:
        buff=read(OUT/'entities'/(fname+'.buff'))
        require(buff['stacking_limit']=={'stacking_limit':'fixed_one','stacking_limit_met_behavior':'preserve_existing_buff'} and buff['stacking_ownership_type']=='for_all_players','Nonstack contract')
    for p in (BASE/'entities').glob('*'):
        if p.stem=='expanse06_amun_boarding' or p.stem.endswith('_marines'):
            require(p.read_bytes()==(OUT/'entities'/p.name).read_bytes(),'Competing capture change')
    return {'status':'PASS offline structural contracts','research_changes_checked':len(report['changes']),'UNN_magazine':'six actual launches per10s;36rounds;120sreload;375/393.75damage','support':'400absolutehull budget; global nonstack; existing capture implementations preserved','players':'only native escort substitutions and new Truman/platform roster entries','runtime':'NOT RUN: existing/new research refresh, filters in engine, timing, save/reload and multiplayer'}
if __name__=='__main__':
    from build_polish import write
    result=run();write(AUD/'contract-checks.json',result);print(result)
