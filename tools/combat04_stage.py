#!/usr/bin/env python3
"""Stage private Javelis-sized torpedo; inspect pinned local carrier references."""
import argparse, copy, hashlib, json, os
from collections import Counter
from pathlib import Path
import jsonschema
from common import read_mesh

ROOT = Path(__file__).resolve().parents[1]
PIN = '8e061033afe53b1393eaefd56617a3fd041eeb5f'
def read(p): return json.loads(p.read_text(encoding='utf-8-sig'))
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def write(p, d):
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(d, indent=2)+'\n')

def main():
    a=argparse.ArgumentParser()
    a.add_argument('--source-root', type=Path, default=Path('/run/media/haker/NVME 2/expanse-mod'))
    a.add_argument('--output', type=Path, default=ROOT/'build/combat04-a/light')
    args=a.parse_args(); out=args.output.resolve()
    if not out.is_relative_to(ROOT/'build/combat04-a') or out.exists(): raise SystemExit('Use fresh output under owned build/combat04-a')
    for key in ['SINS2_GAME','SINS2_SDK']:
        if not os.environ.get(key): raise SystemExit('BLOCKED: missing '+key)
    game=Path(os.environ['SINS2_GAME']);sdk=Path(os.environ['SINS2_SDK'])
    snapshot=read(args.source_root/'audit/schema-comparison.json')
    assert snapshot['official_commit']==PIN
    for r in snapshot['files']:
        p=sdk/r['path']
        if not p.is_file(): raise SystemExit('BLOCKED: missing pinned dependency '+str(p))
        b=p.read_bytes();assert hashlib.sha1(b'blob '+str(len(b)).encode()+b'\0'+b).hexdigest()==r['official_git_blob'],p
    evidence={}
    def dependency(rel, parse=True):
        p=game/rel
        if not p.is_file() and p.parent.is_dir():
            matches=[f for f in p.parent.iterdir() if f.name.casefold()==p.name.casefold()]
            if len(matches)==1:p=matches[0]
        if not p.is_file():raise SystemExit('BLOCKED: missing installed dependency '+str(p))
        evidence[rel]={'sha256':sha(p),'bytes':p.stat().st_size,'actual_relative_path':str(p.relative_to(game))}
        return read(p) if parse else p
    j=dependency('entities/trader_medium_torpedo.unit')
    oldpath=ROOT/'build/combat03-a/persistent/entities/expanse03_heavy_torpedo.unit'
    if not oldpath.exists():raise SystemExit('BLOCKED: missing previous private torpedo '+str(oldpath))
    oldhash=sha(oldpath);old=read(oldpath);new=copy.deepcopy(old)
    new['spatial']=copy.deepcopy(j['spatial'])
    new['physics'].update(max_linear_speed=1250.0,time_to_max_linear_speed=1.5,max_angular_speed=22.5,time_to_max_angular_speed=1.5)
    new['skin_groups']=[{'skins':['expanse04_light_torpedo']}]
    skin=dependency('entities/trader_medium_torpedo.unit_skin')
    skin['skin_stages'][0]['gui'].update(name='expanse04.light_torpedo.name',description='expanse04.light_torpedo.description')
    candidates={'expanse04_light_torpedo.unit':new,'expanse04_light_torpedo.unit_skin':skin}
    for name,value in candidates.items():
        ext='unit-skin' if name.endswith('.unit_skin') else 'unit'
        jsonschema.Draft7Validator(read(sdk/'json_schemas'/(ext+'-schema.json'))).validate(value)
    changed=[k for k in old if new[k]!=old[k]];assert changed==['spatial','physics','skin_groups']
    assert new['health']==old['health'] and new['ai']==old['ai'] and new['torpedo']=={} and new['target_filter_unit_type']=='torpedo'
    comparison={}
    for ident in ['trader_medium_torpedo','trader_torpedo_cruiser_torpedo']:
        d=dependency('entities/'+ident+'.unit'); m=read_mesh(dependency('meshes/'+ident+'.mesh',False))
        comparison[ident]={'physics':d['physics'],'health':d['health'],'spatial':d['spatial'],'mesh':{k:m[k] for k in ['box','sphere','triangles','materials']},'length':2*m['box'][5]}
    material=dependency('mesh_materials/trader_medium_torpedo.mesh_material')
    for k,v in material.items():
        if k.endswith('_texture'):dependency('textures/'+v+'.dds',False)
    trail=dependency('effects/trader_medium_torpedo.exhaust_trail_effect');dependency('textures/'+trail['texture']+'.dds',False)
    dependency('sounds/engine_techsupportship.sound');dependency('sounds/engine_techsupportship.ogg',False)
    deathgroup=dependency('death_sequences/torpedo0_1.death_sequence_group')
    nested_particles=set()
    for sequence in deathgroup['death_sequences']:
        sequence_data=dependency('death_sequences/'+sequence+'.death_sequence')
        for event in sequence_data['events']:
            nested_particles.update(event.get('particle_effects',[]))
            for sound in event.get('sounds',[]):
                dependency('sounds/'+sound+'.sound');dependency('sounds/'+sound+'.ogg',False)
    source_skin=dependency('entities/trader_long_range_cruiser.unit_skin')
    muzzle=next(x for x in source_skin['skin_stages'][0]['effects']['effect_alias_bindings'] if x['alias_name']=='trader_long_range_cruiser_medium_missile_weapon_muzzle')
    muzzle=copy.deepcopy(muzzle);muzzle['alias_name']='expanse04_light_torpedo_muzzle'
    nested_particles.add(muzzle['alias_binding']['particle_effect'])
    for sound in muzzle['alias_binding']['sounds']:
        dependency('sounds/'+sound+'.sound');dependency('sounds/'+sound+'.ogg',False)
    def particle_textures(d):
        if isinstance(d,dict):
            for k,v in d.items():
                if isinstance(v,str) and (k in ['texture_0','texture_1','texture'] or k.endswith('_texture')):
                    dependency('textures/'+v+'.dds',False)
                elif isinstance(v,str) and k=='particle_effect':nested_particles.add(v)
                particle_textures(v)
        elif isinstance(d,list):
            for v in d:particle_textures(v)
    checked_particles=set()
    while nested_particles-checked_particles:
        ident=next(iter(nested_particles-checked_particles));checked_particles.add(ident)
        particle_textures(dependency('effects/'+ident+'.particle_effect'))
    carrier={}
    for ident in ['trader_battle_capital_ship','trader_carrier_capital_ship','trader_loyalist_titan','trader_rebel_titan']:
        d=dependency('entities/'+ident+'.unit'); mounts=Counter(x['weapon'] for x in d['weapons']['weapons']);weapons=[]
        for wid,count in mounts.items():
            w=dependency('entities/'+wid+'.weapon')
            weapons.append({'id':wid,'mount_count':count,**{k:w[k] for k in ['damage','penetration','cooldown_duration','range','burst_pattern'] if k in w},'scope':'raw definition; mount unlocks, arcs, level bonuses and burst distribution are not a runtime DPS measurement'})
        carrier[ident]={'build':d['build'],'level_zero_health':d['health']['levels'][0],'durability':d['health'].get('durability'),'factory':d.get('unit_factory'),'abilities':d.get('abilities'),'weapons':weapons}
    for n in ['trader_carrier_capital_ship_mobile_unit_factory.ability','trader_carrier_capital_ship_mobile_unit_factory.buff','trader_carrier_capital_ship_mobile_unit_factory.action_data_source','trader_pirate_mercenary_base_unit_item.ability','trader_pirate_mercenary_base_unit_item.action_data_source','eivonns_light_ships.ability','trader_light_frigate.unit']:
        dependency('entities/'+n)
    factory_schema=read(sdk/'json_schemas/unit-schema.json')['$defs']['unit_factory_definition']
    recipe={'status':'OFFLINE CANDIDATE; runtime NOT RUN','private_entity_files':list(candidates),'source_heavy_torpedo':{'path':str(oldpath),'sha256':oldhash,'preserve_as_future_large_torpedo':True},
      'replace_references':{'torpedo_to_create':{'from':'expanse03_heavy_torpedo','to':'expanse04_light_torpedo','scope':'ordinary and Rocinante normal magazine buffs and hero independent salvo buff only'}},
      'action_value_patches':[{'action_value_id':'heavy_torpedo_torpedo_speed_value','action_value':{'values':[1250.0]},'scope':'every corresponding normal and hero salvo ADS showing this tooltip'}],
      'skin_muzzle_alias':muzzle,'replace_muzzle_effect_alias':{'from':'trader_torpedo_cruiser_torpedo_weapon_muzzle','to':muzzle['alias_name'],'scope':'light torpedo launch play_point_effect operators; bind alias in both launching ship skins'},
      'localization':{'expanse04.light_torpedo.name':'MCRN light torpedo','expanse04.light_torpedo.description':'Compact guided torpedo. Speed 1,250; damage 750; penetration 1,000. Interceptable projectile with 50 hull, 100 armor and 50 armor strength.'},
      'preserve':{'damage':750,'penetration':1000,'capacity':8,'pair_count':2,'pair_interval':10,'reload_after_last_pair':120,'lifetime':240,'range':200000,'same_well_filter':True,'hero_railgun':{'damage':2500,'penetration':1000,'cooldown':10}},
      'expected_tooltip':{'damage':750,'penetration':1000,'speed':1250,'hull':50,'armor':100,'armor_strength':50,'lifetime':240,'range':200000,'magazine':8,'per_pair':2,'pair_seconds':10,'reload_seconds':120},
      'integration_notes':['Add private unit and unit_skin IDs to their intended manifests; add two new localization keys using existing localization manifest method.','Use installed mesh/material/textures/trail/death/sound references; no vanilla binary copies or mesh derivative required.','Keep existing expanse03_heavy_torpedo unit and its Ogrov references intact as separate large candidate. Do not leave unneeded heavy entity in light-only package.','Worker traces new Javelis mesh/material/textures/trail/death/sound and nested particle texture dependencies. Main validates final unit/skin/UI/localization references.','Do not replace ability state machine, actions order, ammo memory, hero railgun or damage ADS values.'],
      'runtime_gates':['Javelis-size hull/trail and new launch plume at actual two apertures','22.5deg/s turn and1.5s ramps avoid looping/missed close shots','Smaller spatial collision radius changes interception geometry; verify PDC actual damage and hit rates','Speed1250 reduces defensive reaction time; firing/ammo damage budget unchanged does not imply identical combat balance','No change to240s lifespan; finite200000 range is not proof all moving targets in every gravity well are reachable','Save/reload ammo and target loss remain inherited runtime gates']}
    for name,value in candidates.items():write(out/'entities'/name,value)
    write(out/'integration-recipe.json',recipe);write(out/'mesh-comparison.json',comparison)
    write(out/'carrier-evidence.json',{'units':carrier,'unit_factory_schema':factory_schema,'stock_Cobalt_build_kind':'frigate','preferred_local_factory':{'build_kinds':['frigate'],'base_build_point':'Must use verified Donnager hangar position/rotation; not stock Sova coordinates','scope_warning':'Allows other player-available frigates; schema has no per-unit whitelist. Broadens only new carrier, not global build menus.'},'alternative_spawn_ability':{'reference':'trader_pirate_mercenary_base_unit_item.ability','operator':'spawn_units','units':{'required_units':[{'unit':'trader_light_frigate','count':[1,1]}]},'constrain_available_supply_to_owner_player':True,'check_research_prerequisites':True,'caveat':'Costed replacement/reinforcement ability is not a native production queue; no claim it preserves construction/cancel/refund behavior. Supply/price must match final corvette build definition.'}})
    assert sha(oldpath)==oldhash
    write(out/'offline-validation.json',{'status':'PASS for two schemas, exact field delta and enumerated dependencies','runtime':'NOT RUN','pinned_schema_count':len(snapshot['files']),'source_previous_unchanged':True,'candidate_sha256':{str(p.relative_to(out)):sha(p)for p in sorted((out/'entities').iterdir())},'installed_readonly_evidence':evidence,'particle_textures_checked':sorted(checked_particles),'reference_coverage':'New Javelis mesh/material/textures/trail/death/sound plus nested particle texture dependencies; main final package resolver covers unit/skin/UI/localization integration. No particle-effect schema exists.'})
    print('PASS: two private schemas, preserved health/AI/ammo recipe, pinned schemas, explicit dependency checks. '+str(out))

if __name__=='__main__':main()
