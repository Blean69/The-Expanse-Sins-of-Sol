"""Integrate reviewed art using existing frigate, trade and native loot patterns.
No new capture program, faction asymmetry, global salvage or installation.
"""
from pathlib import Path
import copy
from build_polish import write
from validate_experiments import read, require
from update19_balance import BASE, GAME, ROOT, walk
from build_hero03 import ability_positions
from build_amun06 import patch_pointer
from build_update12 import phase_effect
from flight03_effects import scale_effect

EUROPA='expanse19_europa_bane'
ARTEMIS='expanse19_artemis'
MAG='expanse19_europa_magazine'

def renamed(x,old,new):
    if isinstance(x,str):return x.replace(old,new)
    if isinstance(x,list):return [renamed(v,old,new) for v in x]
    if isinstance(x,dict):return {k:renamed(v,old,new) for k,v in x.items()}
    return x

def spatial(meta,rank=1):
    s=meta['ship_spatial']
    return {'radius':s['radius'],'box':copy.deepcopy(s['box']),'collision_rank':rank}

def skin(edits, ident, meta, ui, template, idle=True):
    d=read(template);s=d['skin_stages'][0]
    s['gui'].update(name=ident+'.name',description=ident+'.description')
    s['unit_mesh']={'mesh':meta['hull_mesh'],'shader':'ship','is_shadow_blocker':True}
    s['min_camera_distance']=max(70.,meta['ship_spatial']['radius']*2.)
    s['main_view_icon']['group']='ship'
    aliases={}
    for r in meta.get('rigs',[]):
        for a in r['skin_alias_map']:aliases[a['mesh_alias_name']]=a
    s['child_mesh_alias_bindings']={'map':list(aliases.values())}
    for patch in ui['skin_patches']:patch_pointer(d,patch['pointer'],patch['value'])
    fx=s['effects'];fx.pop('shield_effect',None)
    if idle:
        fx['flair_effects']=[]
        fx['exhaust_effects']={'particle_effects':[{'particle_effect':ident+'_idle_plume'}]}
        fx['hyperspace_effects']=copy.deepcopy(read(BASE/'entities/expanse_mcrn_corvette.unit_skin')['skin_stages'][0]['effects']['hyperspace_effects'])
        for k in ['travel_effect','travel_effect_between_stars','travel_effect_destabilized']:fx['hyperspace_effects'][k]=ident+'_phase_plume'
        edits['effects/'+ident+'_idle_plume.particle_effect']=scale_effect(read(GAME/'effects/exhaust_tech_medium_01.particle_effect'),.8,1.5,blue=True)
        edits['effects/'+ident+'_phase_plume.particle_effect']=phase_effect(meta['equipment']['exhausts'],.8,6.)
    edits['entities/'+ident+'.unit_skin']=d
    return d

def changes(balance, europa, artemis, le_guin, artemis_ui, le_guin_ui):
    edits={};origins={};loc={}
    def source(rel):return copy.deepcopy(balance[rel]) if rel in balance else read(BASE/rel if (BASE/rel).exists() else GAME/rel)
    def emit(ident,kind,d,original):
        rel='entities/'+ident+'.'+kind;edits[rel]=d;origins[rel]=str(original)
    # The requested pirate frigate uses the established two-shot stateful
    # magazine and the existing10% boarding system, without cloak or railgun.
    d=source('entities/expanse_mcrn_corvette.unit')
    d['spatial']=spatial(europa)
    d['physics']['max_linear_speed']=950.;d['physics']['strafe_max_linear_speed']=190.
    d['physics']['max_angular_speed']=20.
    d['move']['follow_distance']=europa['ship_spatial']['radius']*5
    d['build'].update(build_time=60.,supply_cost=95,price={'credits':1500.,'metal':350.,'crystal':200.})
    d['health']['durability']=250.
    d['health']['levels'][0].update(max_hull_points=2500.,max_armor_points=1500.,armor_strength=75.,experience_given_on_death=100.)
    d['skin_groups']=[{'skins':[EUROPA]}]
    d['weapons']={'weapons':[copy.deepcopy(r['mount']) for r in europa['rigs']],'max_range_weapon_index':0}
    d['abilities']=[{'abilities':[MAG,'expanse06_amun_boarding','expanse11_no_shields']}]
    d['ai']['attack_target_type_groups_matching_weapon']=europa['rigs'][0]['mount']['weapon']
    for r in europa['rigs']:
        w=source('entities/expanse15_truman_pdc_0.weapon');w['turret']=copy.deepcopy(r['turret_override'])
        # Keep within the worker's +/-3degree sampled clearance envelope.
        w.update(name=EUROPA+'.pdc',range=4500.,pitch_firing_tolerance=3.,yaw_firing_tolerance=3.)
        emit(r['mount']['weapon'],'weapon',w,BASE/'entities/expanse15_truman_pdc_0.weapon')
    emit(EUROPA,'unit',d,BASE/'entities/expanse_mcrn_corvette.unit')
    for kind in ['ability','buff','action_data_source']:
        original=BASE/('entities/expanse03_torpedo_magazine.'+kind)
        obj=renamed(source('entities/expanse03_torpedo_magazine.'+kind),'expanse03_torpedo_magazine',MAG)
        if kind=='ability':obj['ability_positions']=ability_positions(europa['equipment']['torpedo_ports'])
        if kind=='buff':
            for o in walk(obj):
                if o.get('operator_type')=='create_torpedo':o['torpedo_to_create']='expanse15_unn_light_torpedo'
        if kind=='action_data_source':
            for a in obj['action_values']:
                if a['action_value_id']=='heavy_torpedo_damage_value':a['action_value']['values']=[x/2 for x in a['action_value']['values']]
        emit(MAG,kind,obj,original)
    sk=skin(edits,EUROPA,europa,europa['ui'],BASE/'entities/expanse_mcrn_corvette.unit_skin')
    sounds=copy.deepcopy(read(BASE/'entities/expanse15_truman.unit_skin')['skin_stages'][0]['sounds'])
    for moods in sounds['dialogue'].values():
        for mood,lines in moods.items():moods[mood]=[x for x in lines if x!='expanse17_voice_unn_rail']
    sk['skin_stages'][0]['sounds']=sounds
    origins['entities/'+EUROPA+'.unit_skin']=str(BASE/'entities/expanse_mcrn_corvette.unit_skin')
    loc.update({EUROPA+'.name':"Europa's Bane",EUROPA+'.description':'Pirate frigate adapted from the former UNN ship. Six Earth PDCs (85 base DPS each), two UNN light torpedoes every 10 seconds from an eight-round magazine, and the existing 10% boarding attempt. No railgun or cloak. Prototype loadout and statistics; exact screen weapon count is unverified.',EUROPA+'.pdc':'Europa\'s Bane PDC',MAG+'.name':'UNN light torpedo magazine',MAG+'.description':'Eight torpedoes. Fires two every 10 seconds while a detected enemy is available in the same gravity well; reloads 120 seconds after the last pair. 30-second projectile fuel life. Research applies.',MAG+'.ammo_label':'Torpedoes remaining'})
    # Artemis: native civilian construction plus native loot-collector flag.
    d=source('entities/trader_colony_frigate.unit')
    for key in ['colonize_ability','antimatter','attack']:d.pop(key,None)
    d['spatial']=spatial(artemis);d['skin_groups']=[{'skins':[ARTEMIS]}]
    d['build'].update(build_time=35.,supply_cost=8,price={'credits':600.,'metal':100.,'crystal':50.})
    d['health']['levels'][0].update(max_hull_points=900.,max_armor_points=400.)
    d['abilities']=[{'abilities':['expanse11_no_shields']}]
    d['ship_roles']=[];d['is_loot_collector']=True
    d['user_interface']['can_attack']=False;d['user_interface']['selection_group_unit_type']='combat_ship'
    d['move']['follow_distance']=artemis['ship_spatial']['radius']*5
    emit(ARTEMIS,'unit',d,BASE/'entities/trader_colony_frigate.unit')
    skin(edits,ARTEMIS,artemis,artemis_ui,GAME/'entities/trader_colony_frigate.unit_skin')
    origins['entities/'+ARTEMIS+'.unit_skin']=str(GAME/'entities/trader_colony_frigate.unit_skin')
    loc.update({ARTEMIS+'.name':'Artemis salvage tender',ARTEMIS+'.description':'Unarmed civilian scavenger adapted from Artemis. Collects existing native loot and derelicts using the normal collection order. 900 hull, 400 armor, 8 supply. No boarding, weapons or custom capture system; protect it with escorts.'})
    # Native automatic trader inherits its original economics and behavior.
    trade=source('entities/trader_trade_ship.unit');trade['spatial']=spatial(artemis);trade['skin_groups']=[{'skins':['expanse19_artemis_trade']}]
    emit('trader_trade_ship','unit',trade,BASE/'entities/trader_trade_ship.unit')
    trade_skin=copy.deepcopy(edits['entities/'+ARTEMIS+'.unit_skin'])
    trade_skin['skin_stages'][0]['gui'].update(name='expanse19_artemis_trade.name',description='expanse19_artemis_trade.description')
    native_trade_skin=read(GAME/'entities/trader_trade_ship.unit_skin')['skin_stages'][0]
    if 'sounds' in native_trade_skin:trade_skin['skin_stages'][0]['sounds']=copy.deepcopy(native_trade_skin['sounds'])
    emit('expanse19_artemis_trade','unit_skin',trade_skin,GAME/'entities/trader_colony_frigate.unit_skin')
    loc.update({'expanse19_artemis_trade.name':'Civilian cargo hauler','expanse19_artemis_trade.description':'Artemis-pattern civilian trade ship. Existing automatic trade behavior, income and Morrigan/Tachi escort choices are unchanged.'})
    # LeGuin's source is damaged: replace only the smallest native derelict
    # visual/spatial. Native destroy-on-capture and reward mechanics stay exact.
    derelict=read(GAME/'entities/derelict_loot_0.unit');derelict['spatial'].update(radius=le_guin['ship_spatial']['radius'],box=copy.deepcopy(le_guin['ship_spatial']['box']))
    derelict['skin_groups']=[{'skins':['expanse19_le_guin']}]
    emit('derelict_loot_0','unit',derelict,GAME/'entities/derelict_loot_0.unit')
    skin(edits,'expanse19_le_guin',le_guin,le_guin_ui,GAME/'entities/derelict_loot_0.unit_skin',idle=False)
    origins['entities/expanse19_le_guin.unit_skin']=str(GAME/'entities/derelict_loot_0.unit_skin')
    loc.update({'expanse19_le_guin.name':'Le Guin derelict','expanse19_le_guin.description':'Damaged civilian hull. Recover using the native derelict-collection command. Existing collection requirement and rewards are unchanged; no active engines or weapons.'})
    return edits,loc,origins
