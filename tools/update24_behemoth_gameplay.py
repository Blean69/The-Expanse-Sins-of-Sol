"""Private bounded OPA logistics-titan fragment; no player or shared-unit writes.

changes(base, art_contract) -> edits, localization, origins, integration report.
Main owns access, research, tags, registries, publication and the shared titan cap.
"""
from pathlib import Path
from copy import deepcopy as cp
import hashlib, json

MAIN=Path('/run/media/haker/NVME 2/expanse-mod')
ROOT=Path(__file__).resolve().parents[1]
BASE=MAIN/'build/experiments/expanse_update22'
GAME=MAIN.parent/'SteamLibrary/steamapps/common/Sins2'
ID='expanse24_behemoth'
CONTRACT=ROOT/'docs/audit/update24-behemoth/integration-spec.json'

def changes(base=BASE, art_contract=CONTRACT):
    base=Path(base);art_contract=Path(art_contract);art=json.loads(art_contract.read_text());assert art['status'].startswith('PASS OFFLINE')
    edits={};loc={};origins={};sources={}
    def path(name):
        p=base/'entities'/name
        return p if p.exists() else GAME/'entities'/name
    def read(name):
        p=path(name);sources[str(p)]=hashlib.sha256(p.read_bytes()).hexdigest();return json.loads(p.read_text())
    def put(name,d,origin=None):
        key='entities/'+name;assert not (base/key).exists();edits[key]=d
        if origin:origins[key]=str(path(origin))
    def labels(n,title,desc):loc[n+'.name']=title;loc[n+'.description']=desc
    def rename(obj,old,new):
        if isinstance(obj,str):return obj.replace(old,new)
        if isinstance(obj,list):return [rename(v,old,new)for v in obj]
        if isinstance(obj,dict):return {k:rename(v,old,new)for k,v in obj.items()}
        return obj
    def values(ads,changes):
        found=set()
        for row in ads['action_values']:
            k=row['action_value_id']
            if k in changes:row['action_value']['values']=[changes[k]]*len(row['action_value']['values']);found.add(k)
        assert found==set(changes),(found,set(changes))
    labels(ID,'OPA Behemoth','A costly shieldless logistics titan rebuilt from a generation ship. Eight defensive PDCs, limited surplus torpedoes, targeted hospital engineering and a mobile component shop. Thin protection, slow movement and no railguns. Shares the ordinary titan limit.')
    unit=read('expanse_donnager_battleship.unit')
    unit['spatial']={'box':cp(art['ship_spatial']['box']),'radius':art['ship_spatial']['radius'],'collision_rank':3}
    unit['physics'].update(max_linear_speed=250.,time_to_max_linear_speed=20.,max_angular_speed=4.,time_to_max_angular_speed=6.,max_bank_angle=5.,strafe_max_linear_speed=60.,time_to_strafe_max_linear_speed=20.)
    unit['move']['follow_distance']=6500.
    unit['hyperspace'].update(charge_time=12.,charge_time_variance=1.)
    unit['ai']['attack_target_type_groups_to_ignore']=[]
    unit['ai']['attack_target_type_groups_matching_weapon']=ID+'_pdc'
    unit['ai']['attack_target_type_groups']=cp(read('expanse15_truman_pdc_0.weapon')['attack_target_type_groups'])
    unit['weapons']={'weapons':[],'max_range_weapon_index':0}
    pdc=read('expanse15_truman_pdc_0.weapon');pdc['name']=ID+'_pdc.name';pdc['damage']=85.*pdc['cooldown_duration'];pdc['turret']=cp(art['rigs'][0]['turret_override'])
    put(ID+'_pdc.weapon',pdc,'expanse15_truman_pdc_0.weapon');labels(ID+'_pdc','Behemoth point defense','One defensive gun: 85 base damage per second, Earth tracking profile, hull-safe restricted arcs. No railgun.')
    for r in art['rigs']:
        unit['weapons']['weapons'].append({'weapon':ID+'_pdc','mesh_point':r['mesh_point'],'weapon_position':r['position'],'up':r['up'],'forward':r['forward'],'yaw_arc':r['yaw_arc'],'pitch_arc':r['pitch_arc']})
    unit['health']['durability']=350.
    for i,h in enumerate(unit['health']['levels']):
        h.update(max_hull_points=12000.*(1+.06*i),max_armor_points=1500.*(1+.05*i),armor_strength=55.+2*i,hull_point_restore_rate=4.,armor_point_restore_rate=3.,max_shield_points=0.,shield_point_restore_rate=0.)
        h.pop('shield_burst_restore',None)
    for level in unit['levels']['levels']:level.pop('weapon_modifiers',None)
    unit['build'].update(build_time=360.,price={'credits':11000.,'metal':3000.,'crystal':2200.},supply_cost=500,prerequisites=[['trader_unlock_rebel_titan']])
    # Native titan kind, combat type and titan tag preserve ordinary cap/equipment.
    assert unit['build']['build_kind']=='titan'and unit['target_filter_unit_type']=='titan'
    unit['tags']=['titan',ID];unit['skin_groups']=[{'skins':[ID]}]
    unit['ship_component_shop']={}  # Existing mobile-fabricator service; no discount.
    unit['spawn_debris']['spawn_loot']['loot_name']=ID+'_loot_name';loc[ID+'_loot_name']='Behemoth wreckage'
    unit['ship_roles']=['attack_ship'] # Engine role enum; support comes from abilities.
    magazine=ID+'_magazine'
    for ext in ['ability','action_data_source','buff']:
        d=rename(read('expanse19_europa_magazine.'+ext),'expanse19_europa_magazine',magazine)
        if ext=='ability':
            d['ability_positions']=[{'position':p['position'],'rotation':[1,0,0,0,1,0,0,0,1]}for p in art['equipment']['torpedo_ports']]
        put(magazine+'.'+ext,d,'expanse19_europa_magazine.'+ext)
    labels(magazine,'Behemoth surplus torpedo magazine','Eight existing UNN-profile light torpedoes: two per ten seconds, 120-second reload after the last pair. Base damage 750 each, speed 2125, 30-second fuel; native missile research applies. No planetary or global launch capability.')
    # Share the existing repair buff so Scirocco, Fleet Train and this support
    # cannot stack. Buff timers inherit this ability's ADS as in Fleet Train.
    medical=ID+'_hospital';load=ID+'_hospital_grid_load'
    a=read('expanse15_scirocco_engineering_teams.ability');a['action_data_source']=medical
    a['gui'].update(name=medical+'.name',description=medical+'.description')
    a['active_actions']['actions']['actions'].append({'action_type':'use_unit_operators_on_single_unit','destination_unit':{'unit_type':'current_spawner'},'operators':[{'operator_type':'apply_buff','buff':load}]})
    ads=read('expanse15_scirocco_engineering_teams.action_data_source')
    values(ads,{'range':6000.,'repair_per_tick':40.,'repair_ticks':20.,'cooldown':60.,'antimatter':100.})
    ads['action_values'] += [{'action_value_id':n,'action_value':{'values':[v]}}for n,v in [('hospital_duration',20.),('hospital_reload_penalty',.25),('hospital_speed_penalty',-.25)]]
    # Existing repair remains the sole reservation identity. Native active repair
    # and station repair reservations also suppress autocast and manual overlap.
    for tf in ads['target_filters']:
        tf['target_filter']['ownerships']=['self']
        for buff in ['trader_retrofit_bay_repair','trader_combat_repair_system_unit_item','expanse22_repair_anchorage_reservation']:
            tf['target_filter']['constraints'].append({'constraint_type':'composite_not','constraint':{'constraint_type':'has_buff','buff':buff,'include_pending_buffs':True}})
    put(medical+'.ability',a,'expanse15_scirocco_engineering_teams.ability');put(medical+'.action_data_source',ads,'expanse15_scirocco_engineering_teams.action_data_source')
    grid={'version':0,'active_duration':'hospital_duration','stacking_limit':{'stacking_limit':'fixed_one','stacking_limit_met_behavior':'preserve_existing_buff'},'stacking_ownership_type':'for_all_players','restart_other_stacked_buffs_when_started':False,'make_dead_on_current_spawner_ownership_changed_from_buff_ownership':True,'unit_modifiers':[{'modifier_type':'max_linear_speed','value_behavior':'scalar','value_id':'hospital_speed_penalty'}],'weapon_modifiers':[{'modifier_type':'cooldown_duration','value_behavior':'scalar','value_id':'hospital_reload_penalty'}],'gui':{'hud_icon':'trader_combat_repair_system_unit_item_hud_icon','name':load+'.name','visibility_scope':'negative','is_visible_within_unit_tooltip':True}}
    put(load+'.buff',grid)
    labels(medical,'Hospital Engineering Teams','Repairs one other nearby owned ship for 40 hull per second over 20 seconds, capped at 800. Range 6000; 100 antimatter; 60-second cooldown. Autocast below 80% hull. Shares Scirocco/Fleet Train repair exclusion. While operating, Behemoth loses 25% speed and its PDC reload time rises 25% for 20 seconds. Armor and shields are not restored.')
    labels(load,'Hospital grid priority','For 20 seconds, propulsion speed is reduced 25% and PDC cooldown duration increased 25%. The fixed torpedo-magazine schedule is unchanged. No full weapon shutdown.')
    unit['abilities']=[{'abilities':[magazine,medical,'expanse11_no_shields']}]
    put(ID+'.unit',unit,'expanse_donnager_battleship.unit')
    skin=read('expanse_donnager_battleship.unit_skin');s=skin['skin_stages'][0]
    s['unit_mesh']={'mesh':art['hull_mesh'],'shader':'ship','is_shadow_blocker':True};s['min_camera_distance']=art['ship_spatial']['radius']*1.4
    s['child_mesh_alias_bindings']={'map':[{'mesh_alias_name':n,'mesh_definition':{'mesh':n,'shader':'ship','is_shadow_blocker':True}}for n in ['expanse24_behemoth_pdc_base','expanse24_behemoth_pdc_barrel']]}
    for k in ['hud_icon','hud_monochrome_icon','hud_picture','tooltip_picture']:s['gui'][k]=ID+'_'+('main_view_icon'if k=='hud_monochrome_icon'else k)
    s['gui'].update(name=ID+'.name',description=ID+'.description')
    for k,suffix in [('icon','main_view_icon'),('selected_icon','main_view_icon_selected'),('sub_selected_icon','main_view_icon_sub_selected')]:s['main_view_icon'][k]=ID+'_'+suffix
    fx=s['effects'];fx.pop('shield_effect',None);fx['exhaust_effects']={'particle_effects':[{'particle_effect':art['plumes']['idle']}]}
    for k in ['travel_effect','travel_effect_between_stars','travel_effect_destabilized']:fx['hyperspace_effects'][k]=art['plumes']['phase']
    # Keep established PDC audio/effects, remove unused offensive bindings.
    fx['effect_alias_bindings']=[x for x in fx['effect_alias_bindings']if 'rail_gun'not in x['alias_name']and 'planet_bombing'not in x['alias_name']]
    s['sounds']['dialogue']=cp(read('expanse19_europa_bane.unit_skin')['skin_stages'][0]['sounds']['dialogue'])
    put(ID+'.unit_skin',skin,'expanse_donnager_battleship.unit_skin')
    # New UI brushes point to private rendered resources generated by write_preview_ui().
    roles=['hud_icon','hud_picture','tooltip_picture','main_view_icon','main_view_icon_selected','main_view_icon_sub_selected']
    for role in roles:edits['brushes/'+ID+'_'+role+'.brush']={'supported_dpis':[150,200],'normal_state':{'texture':ID+'_'+role}}
    report={'status':'PRIVATE GAMEPLAY FRAGMENT; ACCESS MERGES REQUIRED','unit':ID,'unit_id':ID,'unlock':'trader_unlock_rebel_titan','art_contract':str(art_contract),'base':str(base),'source_definitions_sha256':sources,'scope':'One OPA logistics titan; new files only','shared_definition_merges':[],
      'unit_tag_entries_append':[{'name':ID,'localized_name':ID+'.name'}],
      'player_recipes':{'opa':{'buildable_units_append':[ID],'research_requirement':'trader_unlock_rebel_titan','note':'Retain/restore the native rebel titan unlock chain and titan-factory access, or replace this prerequisite with an equivalent priced OPA titan research in the main integration. Do not grant a second independent titan limit.'}},
      'titan_limit_policy':{'required_existing_global_limit_tag':'titan','extra_per_ship_limit':None,'shares_with_donnager':True,'native_build_kind':'titan','native_target_type':'titan'},
      'stats':{'hull_level_1':12000,'armor_level_1':1500,'armor_strength_level_1':55,'durability':350,'max_speed':250,'turn_rate':4,'fleet_supply':500,'price':unit['build']['price'],'build_time':360,'native_titan_equipment_slots':8,'pdcs':8,'base_dps_per_pdc':85,'railguns':0,'torpedo_magazine_profile':'Unchanged Europa magazine; eight UNN light torpedoes, two per ten seconds,120-second reload,30-second fuel','hospital_max_per_cast':800,'hospital_hull_per_second':40,'hospital_duration':20,'hospital_cooldown':60,'hospital_antimatter':100},
      'service_scopes':{'hospital':'one other owned ship, same gravity well, targeted within6000; fixed absolute cap; shared repair reservation','component_shop':'native mobile component-shop availability, same service semantics as Vasari Fabricator; no price reduction or empire modifier'},
      'mechanical_limits':['Hospital grid load affects normal PDC cooldown only; scripted missile magazine schedule is not a normal weapon cooldown.','The native shared repair timer cancels when target ownership changes, but may finish if the provider dies or leaves after the cast; this is a finite 800-hull dispatched-team budget, not a persistent aura.','Hospital does not claim real interceptable pods or animate drum spin.','Refit uses native mobile shop semantics; exact proximity/UI and alliance behavior must be observed in game.','Current generic Europa crew voice pool is reused; no Behemoth-specific audio or Donnager-name pool.','Source mesh aspect ratio and 2km scale are documented art assumptions.'],
      'observed_passes':[], 'untested':['game load and research menus','native shared titan cap across capture and rebuild','navigation/collision at2km scale','PDC tracking and range in engine','hospital caster-death/save-reload/ownership and manual-autocast behavior','mobile shop availability and allied access','multiplayer synchronization and performance']}
    art_build=Path(art['output_game']).parent
    report['art_directory']=art['output_game']
    report['art_files']={str(p.relative_to(art_build/'gameplay-art')):str(p)for p in sorted((art_build/'gameplay-art').rglob('*'))if p.is_file()}
    report['art_merge_policy']='Copy private art aliases and UI files; any already-present donor material/texture must match bytes and be skipped, never overwritten.'
    return edits,loc,origins,report


def write_preview_ui(build):
    """Standard game portraits from the already rendered model, no external assets."""
    from PIL import Image,ImageFilter
    build=Path(build);out=build/'gameplay-art';portrait=Image.open(build/'behemoth-oblique.png').convert('RGBA');side=Image.open(build/'behemoth-side.png').convert('RGBA');mask=side.getchannel('A');files={}
    for role in ['hud_icon','hud_picture','tooltip_picture','main_view_icon','main_view_icon_selected','main_view_icon_sub_selected']:
        for dpi,suffix in [(100,''),(150,'150'),(200,'200')]:
            size=Image.open(GAME/'textures'/('trader_light_frigate_'+role+suffix+'.png')).size
            if role.startswith('main_view_icon'):
                alpha=mask.resize(size,Image.Resampling.LANCZOS)
                if role!='main_view_icon':alpha=alpha.filter(ImageFilter.MaxFilter(3))
                img=Image.new('RGBA',size,(235,243,250,0));img.putalpha(alpha)
            else:
                p=portrait.copy();p.thumbnail(size,Image.Resampling.LANCZOS);img=Image.new('RGBA',size,(14,23,35,255)if role=='hud_picture'else(0,0,0,0));img.alpha_composite(p,((size[0]-p.width)//2,(size[1]-p.height)//2))
            rel='textures/'+ID+'_'+role+suffix+'.png';path=out/rel;path.parent.mkdir(parents=True,exist_ok=True);img.save(path);files[rel]=str(path)
    return files


if __name__=='__main__':
    edits,loc,origins,report=changes();build=ROOT/'build/update24-behemoth';overlay=build/'gameplay'
    for rel,d in edits.items():
        p=overlay/rel;p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(d,indent=2)+'\n')
    report['art_files']=write_preview_ui(build)
    report['localization']=loc;report['origins']=origins
    (ROOT/'docs/audit/update24-behemoth/gameplay-spec.json').write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps({'definitions':len(edits),'unit':ID,'overlay':str(overlay),'ui_resources':len(report['art_files'])}))
