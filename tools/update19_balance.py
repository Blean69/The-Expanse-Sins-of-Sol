"""User-requested balance overlay and observed loader corrections over 0.18.

Pure explicit definition edits; no install/settings changes. Research multipliers,
tracking speeds/arcs, magazine counts and reloads retain their existing behavior.
"""
from pathlib import Path
import copy
from build_polish import write
from validate_experiments import read, require

ROOT=Path(__file__).resolve().parents[1]
BASE=ROOT/'build/experiments/expanse_update18'
GAME=ROOT.parent/'SteamLibrary/steamapps/common/Sins2'
MARTIAN=['trader_light_frigate','expanse_mcrn_corvette','expanse_rocinante_hero',
         'expanse12_raptor','expanse12_pella','expanse12_scirocco','expanse_donnager_battleship']
EARTH_PDC=('expanse15_truman_pdc_','expanse06_amun_pdc_')
PLATFORM_TORPEDO='expanse19_defense_torpedo'

def walk(x):
    if isinstance(x,dict):
        yield x
        for v in x.values():yield from walk(v)
    elif isinstance(x,list):
        for v in x:yield from walk(v)

def changes():
    edits={};rows=[]
    def edit(rel):
        if rel not in edits:edits[rel]=read(BASE/rel)
        return edits[rel]
    for p in sorted((BASE/'entities').glob('expanse*.weapon')):
        original=read(p);rel='entities/'+p.name
        if 'point_defense' in original.get('tags',[]):
            d=edit(rel);dps=85. if p.stem.startswith(EARTH_PDC) else 117.6
            require('burst_pattern' not in d,'Unexpected damaging PDC burst')
            d['damage']=round(dps*d['cooldown_duration'],6)
            # Truman's 1-degree release tolerance is narrower than the working
            # Tachi7.5deg. Match that tolerance while retaining180deg/s tracking
            # and authored outward arcs; not a hull-obstruction bypass.
            if p.stem.startswith('expanse15_truman_pdc_'):
                d['pitch_firing_tolerance']=7.5;d['yaw_firing_tolerance']=7.5
            rows.append({'definition':p.name,'kind':'PDC','base_dps_before':original['damage']/original['cooldown_duration'],'base_dps_after':dps})
        if 'rail_gun' in original.get('tags',[]):
            d=edit(rel);d['cooldown_duration']=original['cooldown_duration']*1.5
            d['target_acquired_duration_required_to_fire']=original['target_acquired_duration_required_to_fire']*1.5
            if p.stem=='expanse12_scirocco_rail_0':d['damage']=2000.
            rows.append({'definition':p.name,'kind':'railgun','damage_before':original['damage'],'damage_after':d['damage'],'interval_before':original['cooldown_duration'],'interval_after':d['cooldown_duration'],'acquisition_before':original['target_acquired_duration_required_to_fire'],'acquisition_after':d['target_acquired_duration_required_to_fire']})
    pella=read(BASE/'entities/expanse12_pella.unit')
    sc=edit('entities/expanse12_scirocco.unit');tr=edit('entities/expanse15_truman.unit')
    require(len(sc['health']['levels'])==len(tr['health']['levels'])==len(pella['health']['levels']),'Level count drift')
    for a,b,c in zip(sc['health']['levels'],tr['health']['levels'],pella['health']['levels']):
        a['max_hull_points']=c['max_hull_points'];a['max_armor_points']=c['max_armor_points']
        b['max_hull_points']=c['max_hull_points']*3
    tr['build']['supply_cost']=185
    edit('entities/expanse_amun_ra.unit')['build']['supply_cost']=70
    for ident in MARTIAN:
        d=edit('entities/'+ident+'.unit');old=d['build']['price']['metal'];d['build']['price']['metal']=round(old*1.3,6)
        rows.append({'definition':ident+'.unit','kind':'metal price','before':old,'after':d['build']['price']['metal']})
    for p in sorted((BASE/'entities').glob('*launch_corvette.action_data_source')):
        launch=edit('entities/'+p.name)
        for v in launch['action_values']:
            if v['action_value_id']=='launch_metal':v['action_value']['values']=[round(x*1.3,6) for x in v['action_value']['values']]
    # Both researched and unresearched action-value levels receive the same
    # factor. create_torpedo binds the real projectile's native duration_value.
    count=0
    for p in sorted((BASE/'entities').glob('expanse*.action_data_source')):
        original=read(p)
        if not any(v['action_value_id']=='heavy_torpedo_damage_value' for v in original.get('action_values',[])):continue
        d=edit('entities/'+p.name);record={'definition':p.name,'kind':'torpedo'}
        for v in d['action_values']:
            key=v['action_value_id'];values=v['action_value'].get('values')
            if key=='heavy_torpedo_damage_value':v['action_value']['values']=[x*2 for x in values];record['damage']=v['action_value']['values']
            elif key=='heavy_torpedo_torpedo_speed_value':v['action_value']['values']=[x*1.7 for x in values];record['speed']=v['action_value']['values']
            elif key=='heavy_torpedo_torpedo_lifetime_value':v['action_value']['values']=[30. for x in values];record['lifetime']=30.
        require(set(record)=={'definition','kind','damage','speed','lifetime'},'Incomplete torpedo values')
        rows.append(record);count+=1
    require(count==11,'Unexpected magazine/salvo count')
    for p in sorted((BASE/'entities').glob('expanse*.unit')):
        if read(p).get('target_filter_unit_type')=='torpedo':
            d=edit('entities/'+p.name);d['physics']['max_linear_speed']*=1.7
    # The Expanse defense installation uses a native medium torpedo. Give its
    # new values a private entity so vanilla ships/factions are not also changed.
    pw=edit('entities/expanse15_missile_defense.weapon')
    require(pw['firing']['firing_type']=='spawn_torpedo','Platform firing type drift')
    native=read(GAME/'entities/trader_medium_torpedo.unit')
    native['physics']['max_linear_speed']*=1.7
    edits['entities/'+PLATFORM_TORPEDO+'.unit']=native
    pw['damage']*=2;pw['firing']['torpedo_firing_definition'].update(spawned_unit=PLATFORM_TORPEDO,duration=30.)
    # Loader errors: duplicate tags exhausted the32-slot weapon-tag registry,
    # dropping the cloak tag. Supply only the one custom additive registration.
    tags=edit('uniforms/weapon.uniforms');tags['weapon_tags']=[x for x in tags['weapon_tags'] if x['name']=='expanse06_cloak_revealing_gun']
    require(len(tags['weapon_tags'])==1,'Missing custom cloak weapon tag')
    # Omit disabled optional shield-burst objects rather than invalid0percent.
    # Several hulls carry the same pattern even though the latest log reported
    # only the TEC Enclave supercapital first. Do not restore a positive burst.
    removed={}
    for p in sorted((BASE/'entities').glob('*.unit')):
        old=read(p);bad=[i for i,x in enumerate(old.get('health',{}).get('levels',[])) if x.get('shield_burst_restore',{}).get('restore_percentage')==0]
        if not bad:continue
        d=edit('entities/'+p.name)
        for i in bad:
            require(d['health']['levels'][i].get('max_shield_points',0)==0,'Unexpected shielded hull')
            del d['health']['levels'][i]['shield_burst_restore']
        removed[p.name]=bad
    edits['uniforms/player.uniforms']={'overwrite_pickable_players':False,'pickable_players':['expanse18_unn','expanse18_mcrn','expanse18_opa']}
    edits['uniforms/scenario.uniforms']={'overwrite_scenarios':False,'scenarios':['expanse18_sol_three_homes']}
    loc=edit('localized_text/en.localized_text')
    loc['expanse15_missile_defense.description']='Local defense installation. Two interceptable missiles per 8-second cycle, 300 base damage each, 10,000 range and 30-second fuel life. Requires the existing Javelis unlock. No empire-wide bonuses; cannot move between planets.'
    # One bounded, current note avoids rewriting every original ability tooltip.
    loc['expanse19.balance.note']='Base PDC output: Martian 117.6 DPS / Earth 85 DPS per mount. Railgun intervals and lock-on time are 50% longer. Expanse torpedoes: double damage, 70% faster, 30-second flight lifetime. Research and active modifiers still apply.'
    return edits,{'rows':rows,'scirocco_base_hull':5400,'scirocco_base_armor':3100,'truman_base_hull':16200,'truman_armor':'unchanged6500base','truman_supply':185,'amun_supply':70,'removed_zero_shield_bursts':removed,
        'interpretations':['HP uses Pella hull baseline forTruman; armor retained to avoid accidental armor buff','Scirocco matches Pella hull+armor points at every level','Martian-origin Pella/Rocinante included in metal+PDC standardization; Sunflare and Earth prices unchanged','Earth PDC class includes Protogen Amun-Ra','DPS values are base per mount; existing research/reactor modifiers still apply','Railgun target-acquisition hold also1.0->1.5s, no new charge animation','Fuel applies to real projectiles from both magazine and salvo, no independent damage timer','Orbital missile installation included via private torpedo clone'],
        'runtime':'NOT RUN'}

if __name__=='__main__':
    edits,report=changes();out=ROOT/'build/laboratory/update19/balance'
    require(not out.exists(),'Existing balance output')
    for rel,d in edits.items():write(out/rel,d)
    write(ROOT/'audit/update19/balance.json',report);print('Balance definitions:',len(edits))
