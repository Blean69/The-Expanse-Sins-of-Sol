"""Main-owned UNN capital prototype over the frozen playable fleet."""
import copy,json
from build_polish import write
from build_update11 import spatial,aliases
from build_update12 import phase_effect,copy_resources
from build_hero03 import ability_positions
from build_amun06 import patch_pointer
from flight03_effects import scale_effect
from validate_experiments import read,require

ID='expanse15_truman'
TORP='expanse15_unn_light_torpedo'

def apply(out,game,base,meta,ui):
    require(meta['status'].startswith('PASS'),'Truman geometry unfinished')
    copy_resources(meta['game_directory'],out);copy_resources(ui['game_directory'],out)
    u=read(base/'entities/trader_battle_capital_ship.unit')
    spatial(u,meta);u['skin_groups']=[{'skins':[ID]}];u['tags']=['capital_ship']
    u['build'].update(build_time=100.,price={'credits':4000.,'metal':1000.,'crystal':700.},supply_cost=250)
    u['physics'].update(max_linear_speed=850.,time_to_max_linear_speed=7.,max_angular_speed=18.,time_to_max_angular_speed=2.,max_bank_angle=20.)
    first=copy.deepcopy(u['health']['levels'][0])
    for h in u['health']['levels']:
        h['max_hull_points']*=22000./first['max_hull_points'];h['max_armor_points']*=6500./first['max_armor_points']
    u['weapons']={'weapons':[copy.deepcopy(r['mount'])for r in meta['rigs']],'max_range_weapon_index':18}
    for r in meta['rigs']:
        pdc=r['kind']=='pdc';w=read(base/'entities'/('expanse12_raptor_pdc_0.weapon'if pdc else'expanse12_scirocco_rail_0.weapon'))
        w['turret']=copy.deepcopy(r['turret_override']);w['name']=ID+('.pdc.name'if pdc else'.rail.name')
        w.update(pitch_firing_tolerance=1.,yaw_firing_tolerance=1.)
        if pdc:w.update(pitch_speed=180.,yaw_speed=180.)
        else:w.update(damage=3500.,cooldown_duration=20.,yaw_speed=20.)
        write(out/'entities'/(r['mount']['weapon']+'.weapon'),w)
        if not pdc:
            u['ai']['attack_target_type_groups']=w['attack_target_type_groups']
    u['ai']['attack_target_type_groups_matching_weapon']=meta['rigs'][18]['mount']['weapon']
    u['ai']['attack_target_type_groups_to_ignore']=[]
    u['abilities']=[{'abilities':[ID+'_light_magazine','expanse11_no_shields']}]
    u['item_builds']=read(base/'entities/expanse_donnager_battleship.unit')['item_builds']
    u['spawn_debris'].pop('custom_debris',None)
    if 'spawn_loot'in u['spawn_debris']:u['spawn_debris']['spawn_loot']['loot_name']=ID+'.loot'
    write(out/'entities'/(ID+'.unit'),u)
    s=read(base/'entities/expanse12_scirocco.unit_skin');st=s['skin_stages'][0]
    st['gui'].update(name=ID+'.name',description=ID+'.description')
    st['unit_mesh']['mesh']=meta['hull_mesh'];st['child_mesh_alias_bindings']=aliases(meta)
    st['min_camera_distance']=meta['ship_spatial']['radius']*2
    for p in ui['skin_patches']:patch_pointer(s,p['pointer'],p['value'])
    st['sounds']['dialogue']=read(game/'entities/trader_battle_capital_ship.unit_skin')['skin_stages'][0]['sounds']['dialogue']
    st['effects']['exhaust_effects']={'particle_effects':[{'particle_effect':ID+'_idle_plume'}]}
    for k in ['travel_effect','travel_effect_between_stars','travel_effect_destabilized']:st['effects']['hyperspace_effects'][k]=ID+'_phase_plume'
    write(out/'effects'/(ID+'_idle_plume.particle_effect'),scale_effect(read(game/'effects/exhaust_tech_medium_01.particle_effect'),1.8,3.,blue=True))
    write(out/'effects'/(ID+'_phase_plume.particle_effect'),phase_effect(meta['equipment']['exhausts'],1.8,12.))
    write(out/'entities'/(ID+'.unit_skin'),s)
    old='expanse12_raptor_light_magazine';new=ID+'_light_magazine'
    for ext in ['ability','buff','action_data_source']:
        d=json.loads(json.dumps(read(base/'entities'/(old+'.'+ext))).replace(old,new).replace('expanse04_light_torpedo',TORP).replace(TORP+'_muzzle','expanse04_light_torpedo_muzzle'))
        if ext=='ability':d['ability_positions']=ability_positions(meta['equipment']['light_torpedo_ports'])
        if ext=='buff':
            # Do not inherit a Martian reactor dependency; stock magazine clock.
            actions=d['time_actions'][0]['action_group']['actions']
            require([a.get('float_variable')for a in actions[:2]]==['next_pair_ready','reload_ready'],'Unexpected reactor clock layout')
            launches=[a for a in actions if a.get('action_type')=='use_position_operators_on_single_position']
            require(len(launches)==3,'Expected three native magazine launch actions')
            d['time_actions'][0]['action_group']['actions']=actions[2:8]+copy.deepcopy(launches)+actions[8:]
        if ext=='action_data_source':
            changes={'heavy_torpedo_damage_value':375.,'heavy_torpedo_torpedo_count_value':36,'magazine_capacity_value':36,'magazine_pair_count_value':6,'combat03_torpedoes_per_interval_value':6}
            for v in d['action_values']:
                if v['action_value_id']in changes:v['action_value']['values']=[changes[v['action_value_id']]]
        write(out/'entities'/(new+'.'+ext),d)
    tu=read(base/'entities/expanse04_light_torpedo.unit');tu['skin_groups']=[{'skins':[TORP]}]
    ts=read(base/'entities/expanse04_light_torpedo.unit_skin');ts['skin_stages'][0]['gui']['name']=TORP+'.name'
    write(out/'entities'/(TORP+'.unit'),tu);write(out/'entities'/(TORP+'.unit_skin'),ts)
    loc=read(out/'localized_text/en.localized_text')
    loc.update({ID+'.name':'UNN Truman-class',ID+'.loot':'Truman wreckage',ID+'.description':'UNN capital prototype. Two heavy railguns and eighteen PDC batteries with slower tracking. Six light torpedoes every 10 seconds; 36-round magazine, 120-second reload. 250 supply. Native TEC crew placeholder.',ID+'.pdc.name':'UNN defensive cannon battery',ID+'.rail.name':'UNN heavy railgun',TORP+'.name':'UNN light torpedo',new+'.name':'UNN light torpedo magazine',new+'.description':'Six torpedoes every 10 seconds while a target is available. 36 rounds; reloads 120 seconds after the final volley. Each deals half the damage of a Martian light torpedo. Same speed and durability; four representative bow launch origins.',new+'.ammo_label':'Torpedoes remaining'})
    write(out/'localized_text/en.localized_text',loc)
