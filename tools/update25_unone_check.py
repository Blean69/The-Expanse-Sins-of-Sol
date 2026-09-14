"""Offline UN One schema and bounded-support review. Never launches game."""
from pathlib import Path
import sys,copy
MAIN=Path('/run/media/haker/NVME 2/expanse-mod');sys.path.insert(0,str(MAIN/'tools'))
from common import read,write
from update18_tycho import schema_check
sys.path.insert(0,str(Path(__file__).resolve().parent))
from update25_unone_gameplay import changes,ID,ABILITY,SHARED,BASE
ROOT=Path(__file__).resolve().parents[1];edits,loc,origins,art,report=changes();checks=[]
for rel,d in edits.items():
 p=ROOT/'build/update25-unone/fragments'/rel;write(p,d);checks.append(schema_check(p,p.suffix[1:].replace('_','-')+'-schema.json',Path(origins[rel])))
u=edits[f'entities/{ID}.unit'];assert u['build']['supply_cost']==25 and u['build']['build_kind']=='frigate'and u['target_filter_unit_type']=='frigate';assert not u.get('weapons')and not u['user_interface']['can_attack'];assert u['abilities']==[{'abilities':['expanse11_no_shields',ABILITY]}]
for key in ['unit_factory','capture_points','carrier','colonize_ability','items','item_builds']:assert key not in u
assert u['antimatter']=={'max_antimatter':100.,'antimatter_restore_rate':1.}
a=edits[f'entities/{ABILITY}.ability'];assert 'auto_cast'not in a['active_actions'];apply=a['active_actions']['actions']['actions'][0]['operators'][0];assert apply['buff']==SHARED
ads=edits[f'entities/{ABILITY}.action_data_source'];tf=ads['target_filters'][0]['target_filter'];assert len(ads['target_filters'])==1 and tf['ownerships']==['self']and tf['unit_types']==['corvette','frigate','cruiser']
assert {'constraint_type':'not_self'}in tf['constraints'];assert all({'constraint_type':'composite_not','constraint':{'constraint_type':'has_weapon','weapon_type':k}}in tf['constraints']for k in ['normal','planet_bombing'])
assert any(x.get('constraint',{}).get('buff')==SHARED and x['constraint'].get('include_pending_buffs')for x in tf['constraints'])
vals={x['action_value_id']:x['action_value']['values'][0]for x in ads['action_values']};assert vals=={'cooldown':90.,'antimatter':25.,'range':2500.,'repair_per_tick':10.,'repair_ticks':15.};assert vals['repair_per_tick']*vals['repair_ticks']==150
shared=read(BASE/'entities'/f'{SHARED}.buff');assert shared['stacking_limit']['stacking_limit']=='fixed_one';assert shared['time_actions'][0]['execution_interval_count_value']=='repair_ticks';assert shared['make_dead_on_all_finite_time_actions_done']
station=read(BASE/'entities/expanse22_repair_anchorage.action_data_source');assert any(x.get('constraint',{}).get('buff')==SHARED for x in station['target_filters'][0]['target_filter']['constraints'])
assert 'trader_unlock_trade_port'in read(BASE/'entities/expanse18_unn.player')['research']['research_subjects'];assert len(edits)==4
result={'status':'PASS OFFLINE','schemas':checks,'mechanical_checks':['unarmed ordinary paid frigate25supply','no free capital/hero/capture/production','manual owned-only unarmed noncapital filter','shared fixed-one engineering buff with pending exclusion','existing station filter excludes shared engineering effect','150 maximum hull repair over15ticks,90s cooldown25AM','valid UNN native trade-port prerequisite','native ordinary hyperspace + actual two-nozzle idle effect'],'runtime':'NOT RUN','unverified':report['runtime_unverified']};write(ROOT/'audit/update25-unone/gameplay-validation.json',result);print('PASS4 schemas and bounded relief contracts')
