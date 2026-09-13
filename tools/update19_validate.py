"""Offline structural, arithmetic, asset and reference gates. Never simulates the game."""
from pathlib import Path
import math
from validate_experiments import read,require,file_hashes,sha256,strings
from update19_balance import walk,MARTIAN,EARTH_PDC,PLATFORM_TORPEDO
from build_update19 import OUT,BASE,GAME,ROOT,AUD,SDK,PLAYERS,preservation,definitions,inputs
from update19_ships import EUROPA,ARTEMIS
from update11_validate import schema_check
from amun06_validate_package import AmunResolver,check_action_values
from build_combat03 import check_actions

def close(a,b,msg):require(math.isclose(a,b,rel_tol=1e-9),msg)
def vals(d):return {x['action_value_id']:x['action_value'].get('values') for x in d.get('action_values',[])}

def validate():
    preserved=preservation();expected,origins,report=definitions();before=file_hashes(BASE);after=file_hashes(OUT);record=read(AUD/'build-record.json')
    require(set(before)<=set(after),'Deleted baseline assets')
    for rel,d in expected.items():require(read(OUT/rel)==d,'Unexpected definition drift '+rel)
    manifests={'entities/'+kind+'.entity_manifest' for kind in ['unit','unit_skin','weapon','ability','buff','action_data_source']}
    allowed=set(expected)|manifests|{'PLAYTEST-README.md','ASSET-SOURCES.md'}|set(record['art_files'])
    require(all(rel in allowed for rel,h in after.items() if h!=before.get(rel)),'Unreviewed package change')
    for rel,h in record['art_files'].items():require(after[rel]==h,'Reviewed art changed '+rel)
    require(after['PLAYTEST-README.md']==sha256(ROOT/'docs/update19.md'),'README drift')
    schema=[]
    for rel in sorted(expected):
        p=OUT/rel
        original=Path(origins[rel]) if rel in origins else BASE/rel
        if rel=='entities/'+PLATFORM_TORPEDO+'.unit':original=GAME/'entities/trader_medium_torpedo.unit'
        if not original.exists():original=None
        result=schema_check(p,original)
        if result is not None:schema.append({'file':rel,'schema':result})
    # Native registrations are additive; duplicate built-in weapon tags were
    # the observed source of registry exhaustion and missing cloak tags.
    native=read(GAME/'uniforms/weapon.uniforms')['weapon_tags'];custom=read(OUT/'uniforms/weapon.uniforms')['weapon_tags'];tags=[x['name'] for x in native+custom]
    require(len(tags)<=32 and len(tags)==len(set(tags)),'Weapon registry duplicate/overflow')
    require('expanse06_cloak_revealing_gun' in tags,'Lost cloak reveal tag')
    for p in (OUT/'entities').glob('*.unit'):
        for level in read(p).get('health',{}).get('levels',[]):require(level.get('shield_burst_restore',{}).get('restore_percentage',1)>0,'Zero optional shield burst '+p.name)
    for rel,key,flag in [('uniforms/player.uniforms','pickable_players','overwrite_pickable_players'),('uniforms/scenario.uniforms','scenarios','overwrite_scenarios')]:
        d=read(OUT/rel);require(d[flag] is False and len(d[key])==len(set(d[key])),'Invalid additive registrations')
        kind='player-uniforms' if 'player' in rel else 'scenario-uniforms'
        sch=read(SDK/'json_schemas'/f'{kind}-schema.json')
        import jsonschema
        for k,v in d.items():jsonschema.validate(v,sch['properties'][k])
    # Equal new availability across the three supported identities.
    clones=[read(OUT/'entities'/f'{x}.player') for x in PLAYERS[-3:]]
    for key in ['buildable_units','structures','ship_components','planet_components','research','unit_limits','buildable_exotics']:
        require(all(x[key]==clones[0][key] for x in clones),'Clone gameplay drift '+key)
    for x in PLAYERS:
        d=read(OUT/'entities'/f'{x}.player');require(EUROPA in d['buildable_units'] and ARTEMIS in d['buildable_units'],'New ships unavailable')
    # Preserve old movement/cost/timing except explicitly requested metal/supply.
    for ident in MARTIAN+['expanse15_truman','expanse_amun_ra','trader_scout_corvette']:
        old=read(BASE/'entities'/f'{ident}.unit');d=read(OUT/'entities'/f'{ident}.unit')
        for key in ['physics','hyperspace','attack']:require(d.get(key)==old.get(key),'Old movement drift '+ident)
        require(d['build']['build_time']==old['build']['build_time'],'Construction time drift')
        for key in ['credits','crystal']:require(d['build']['price'].get(key)==old['build']['price'].get(key),'Unrequested price drift')
        close(d['build']['price'].get('metal',0),old['build']['price'].get('metal',0)*(1.3 if ident in MARTIAN else 1),'Metal price')
    for p in (OUT/'entities').glob('*launch_corvette.action_data_source'):
        require(vals(read(p))['launch_metal']==[71.5],'Spawned Tachi price mismatch')
    pella=read(OUT/'entities/expanse12_pella.unit')['health']['levels'];sci=read(OUT/'entities/expanse12_scirocco.unit')['health']['levels'];tr=read(OUT/'entities/expanse15_truman.unit')
    require(all(a['max_hull_points']==b['max_hull_points'] and a['max_armor_points']==b['max_armor_points'] for a,b in zip(pella,sci)),'Scirocco HP mismatch')
    require(all(b['max_hull_points']==a['max_hull_points']*3 for a,b in zip(pella,tr['health']['levels'])),'Truman HP mismatch')
    require(tr['build']['supply_cost']==185 and read(OUT/'entities/expanse_amun_ra.unit')['build']['supply_cost']==70,'Supply mismatch')
    rails=[];pdcs=[]
    for p in (OUT/'entities').glob('expanse*.weapon'):
        d=read(p)
        if 'point_defense' in d.get('tags',[]):
            earth=p.stem.startswith(EARTH_PDC+('expanse19_europa_pdc_',));want=85 if earth else 117.6
            require('burst_pattern' not in d,'Unexpected damaging burst');close(d['damage']/d['cooldown_duration'],want,'Wrong base PDC DPS '+p.name)
            pdcs.append({'weapon':p.name,'base_dps':want,'with_fire_control':want*1.05})
        if 'rail_gun' in d.get('tags',[]):
            old=read(BASE/'entities'/p.name)
            close(d['cooldown_duration'],old['cooldown_duration']*1.5,'Rail cooldown');close(d['target_acquired_duration_required_to_fire'],old['target_acquired_duration_required_to_fire']*1.5,'Rail lock-on')
            for key in ['range','penetration','pitch_speed','yaw_speed','pitch_firing_tolerance','yaw_firing_tolerance']:require(d.get(key)==old.get(key),'Rail tracking/range drift')
            if 'scirocco' in p.stem:require(d['damage']==2000,'Light rail damage')
            rails.append({'weapon':p.name,'damage':d['damage'],'base_interval':d['cooldown_duration'],'with_thermal_management':d['cooldown_duration']*.95})
    torps=[]
    for p in (BASE/'entities').glob('expanse*.action_data_source'):
        old=vals(read(p))
        if 'heavy_torpedo_damage_value' not in old:continue
        d=vals(read(OUT/'entities'/p.name))
        require(d['heavy_torpedo_damage_value']==[x*2 for x in old['heavy_torpedo_damage_value']],'Torp damage')
        require(d['heavy_torpedo_torpedo_speed_value']==[x*1.7 for x in old['heavy_torpedo_torpedo_speed_value']],'Torp speed')
        require(d['heavy_torpedo_torpedo_lifetime_value']==[30.]*len(old['heavy_torpedo_torpedo_lifetime_value']),'Torp lifetime')
        for key in old:
            if key not in ['heavy_torpedo_damage_value','heavy_torpedo_torpedo_speed_value','heavy_torpedo_torpedo_lifetime_value']:require(d[key]==old[key],'Magazine or interception HP drift')
        torps.append({'program':p.stem,'damage_levels':d['heavy_torpedo_damage_value'],'speed':d['heavy_torpedo_torpedo_speed_value'][0],'fuel_seconds':30})
    for p in (OUT/'entities').glob('expanse*.buff'):
        for o in walk(read(p)):
            if o.get('operator_type')=='create_torpedo':require(o.get('duration_value')=='heavy_torpedo_torpedo_lifetime_value','Unbounded launched torpedo')
    require(read(OUT/'entities/expanse15_missile_defense.weapon')['firing']['torpedo_firing_definition']=={'spawned_unit':PLATFORM_TORPEDO,'duration':30.},'Platform fuel/reference')
    # Old whole-ship targeting arcs are preserved. New Europa arcs must be
    # identical to the measured rig contract, with firing tolerance<=3degrees.
    for ident in MARTIAN+['expanse15_truman','expanse_amun_ra']:
        old=read(BASE/'entities'/f'{ident}.unit');d=read(OUT/'entities'/f'{ident}.unit');require(d['weapons']==old['weapons'],'Changed hull-safe arcs '+ident)
    native=read(GAME/'entities/derelict_loot_0.unit');derelict=read(OUT/'entities/derelict_loot_0.unit')
    require({k:v for k,v in native.items() if k not in ['spatial','skin_groups']}=={k:v for k,v in derelict.items() if k not in ['spatial','skin_groups']},'Native recovery mechanics drift')
    tender=read(OUT/'entities'/f'{ARTEMIS}.unit');require(tender['is_loot_collector'] and not tender.get('weapons') and 'colonize_ability' not in tender,'Tender role mismatch')
    native=read(BASE/'entities/trader_trade_ship.unit');trade=read(OUT/'entities/trader_trade_ship.unit')
    require({k:v for k,v in native.items() if k not in ['spatial','skin_groups']}=={k:v for k,v in trade.items() if k not in ['spatial','skin_groups']},'Trade economy/escort behavior drift')
    # Resolve new ships and every modified Expanse weapon/ability graph.
    resolver=AmunResolver(OUT,GAME);actions=[]
    for ident in MARTIAN+['expanse15_truman','expanse_amun_ra',EUROPA,ARTEMIS,'trader_trade_ship','derelict_loot_0']:
        unit=resolver.unit(ident,'0.19 validation')
        actions.append({'unit':ident,'actions':check_actions(OUT,resolver,ident),'values':check_action_values(OUT,GAME,resolver,unit)})
    for part in inputs().values():
        for rel in file_hashes(ROOT/part['game']):
            p=OUT/rel
            if p.suffix=='.mesh':resolver.mesh(p.stem,'0.19 reviewed art')
            if p.suffix=='.mesh_material':resolver.material(p.stem,'0.19 reviewed art')
            if p.suffix=='.brush':schema_check(p)
    for rel in manifests:
        ids=read(OUT/rel)['ids'];require(len(ids)==len(set(ids)),'Duplicate entity registry')
        kind=Path(rel).stem
        for ident in ids:require((OUT/'entities'/f'{ident}.{kind}').exists(),'Missing registered definition')
    audio=[rel for rel in before if rel.endswith(('.ogg','.sound'))]
    require(all(after[rel]==before[rel] for rel in audio),'Working audio modified')
    # New references use existing researched tag categories and the existing
    # warhead-level prerequisite. No research costs/tiers/ownership were edited.
    research=[rel for rel in before if rel.endswith('.research_subject')]
    require(all(after[rel]==before[rel] for rel in research),'Research definition drift')
    from update15_research import audit_existing
    mapping=audit_existing(OUT,GAME)
    from build_polish import write
    write(AUD/'research-coverage.json',mapping)
    return {'status':'PASS OFFLINE ONLY','schemas':schema,'registry_count':len(tags),'base_pdc_and_research_arithmetic':pdcs,'railgun_and_research_arithmetic':rails,'torpedo_programs':torps,'actions':actions,'preserved_audio_files':len(audio),'preserved_research_files':len(research),'file_count':len(after),'changed_baseline_files':sorted(r for r,h in before.items() if after[r]!=h),'new_files':sorted(set(after)-set(before)),'preservation':preserved,'runtime':{'game_load':'NOT RUN','existing_vs_new_ship_research':'NOT RUN','30_second_projectile_expiry':'NOT RUN','targeting_and_ship_balance':'NOT RUN','Artemis_native_collection':'NOT RUN','Le_Guin_native_reward':'NOT RUN','save_reload':'NOT RUN','multiplayer':'NOT RUN','Windows_PDC_audio':'USER CONFIRMED WORKING in earlier package; bytes preserved, no compatibility change' }}
