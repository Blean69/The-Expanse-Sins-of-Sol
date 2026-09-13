"""Assemble an additive Amun combat/boarding experiment, preserving tested04 ships."""
from pathlib import Path
import argparse,copy,json,shutil,zipfile
import numpy as np
import jsonschema
from build_polish import write,cp
from build_hero03 import ability_positions,fixed_mount
from build_combat04 import binary_geometry,phase_plume
from validate_experiments import read,require,sha256,file_hashes,tree_hash,compare_tree,verify_pins,verify_zip,provenance,Resolver,strings
from build_combat03 import check_actions

ROOT=Path(__file__).resolve().parents[1];ID='expanse_amun06';SHIP='expanse_amun_ra'
BASE=ROOT/'build/experiments/expanse_rocinante04_amun'
PLAYERS=['trader_loyalist','trader_rebel','dlc_trader_loyalist']

def frozen(game,sdk):
    snap=read(ROOT/'audit/amun06/checkpoint.json')
    records=[compare_tree(x) for x in snap['trees']]
    for p,h in snap['packages'].items():require(sha256(p)==h,'Preserved ZIP changed: '+p)
    e=snap['enabled_mods'];require(sha256(e['path'])==e['sha256'],'Enabled mods changed during assignment')
    return {'preserved_trees':records,'pins':verify_pins(ROOT,game,sdk),'enabled_settings_unchanged':True}

def new_unit(meta,recipe):
    unit=read(BASE/'entities/expanse_rocinante_hero.unit')
    unit['spatial']={k:copy.deepcopy(meta['spatial'][k]) for k in ['box','radius']};unit['spatial']['collision_rank']=1
    unit['skin_groups']=[{'skins':[SHIP]}];unit['tags']=['frigate',SHIP]
    unit['health']['levels'][0]['max_hull_points']=2400.0;unit['health']['levels'][0]['max_armor_points']=1200.0
    unit['build'].update(build_time=90.0,price={'credits':4000.0,'metal':750.0,'crystal':500.0},supply_cost=40)
    unit['antimatter']={'max_antimatter':200.0,'antimatter_restore_rate':1.0}
    unit['abilities']=[{'abilities':list(recipe['core_ship_abilities'])}]
    mounts=[copy.deepcopy(r['mount']) for r in meta['rigs']]
    mounts.append(fixed_mount(meta['equipment']['railgun'],recipe['private_weapons'][3],'weapon.rail.0',10,10))
    unit['weapons']={'weapons':mounts,'max_range_weapon_index':3}
    unit['ai']['attack_target_type_groups_matching_weapon']=mounts[0]['weapon']
    return unit

def patch_pointer(d,pointer,value):
    parts=pointer.strip('/').split('/');at=d
    for k in parts[:-1]:at=at[int(k)] if isinstance(at,list) else at[k]
    at[int(parts[-1]) if isinstance(at,list) else parts[-1]]=copy.deepcopy(value)

def ship_skin(meta,ui,a):
    skin=read(BASE/'entities/expanse_rocinante_hero.unit_skin');s=skin['skin_stages'][0]
    s['unit_mesh']['mesh']=meta['hull_mesh'];s['gui']['name']=SHIP+'_name';s['gui']['description']=SHIP+'_description'
    for patch in ui['skin_patches']:patch_pointer(skin,patch['pointer'],patch['value'])
    s['child_mesh_alias_bindings']={'map':[x for r in meta['rigs'] for x in r['skin_alias_map']]}
    s['effects']['effect_alias_bindings']=read(a.behavior/'core/ship-effect-aliases.json')
    s['effects']['exhaust_effects']['particle_effects']=[{'particle_effect':'expanse06_amun_idle_plume'}]
    for k in ['travel_effect','travel_effect_between_stars','travel_effect_destabilized']:s['effects']['hyperspace_effects'][k]='expanse06_amun_phase_plume'
    s['min_camera_distance']*=61.5/46
    return skin

def pod_effect(game,mesh_id):
    effect=read(game/'effects/pirate_pillage_shuttle.particle_effect');count=0
    def walk(d):
        nonlocal count
        if isinstance(d,dict):
            for k,v in d.items():
                if k=='mesh' and v=='trader_asset_colony_shuttle':d[k]=mesh_id;count+=1
                else:walk(v)
        elif isinstance(d,list):
            for v in d:walk(v)
    walk(effect);require(count==1,'Expected one modeled boarding shuttle emitter')
    return effect

def localization(a):
    result=read(BASE/'localized_text/en.localized_text');result.update(read(a.behavior/'core/localization.json'))
    result.update({SHIP+'_name':'Amun-Ra-class',SHIP+'_description':'Heavy railgun frigate with three defensive cannons, guided torpedoes and boarding pods. Maximum six per player.'})
    return result

def manifests(out,game):
    for ext in ['unit','unit_skin','weapon','ability','buff','action_data_source']:
        write(out/'entities'/(ext+'.entity_manifest'),{'ids':sorted(p.stem for p in (out/'entities').glob('*.'+ext) if not (game/'entities'/p.name).exists())})

def package_validation(out,a,meta,recipe,ui):
    from amun06_behavior import validate_components
    from amun06_validate_package import check_amun06
    behavior=validate_components(out,a.behavior,a.sdk,cloak=False,boarding_model=True)
    for directory in [a.geometry/'build/amun06-b/game',a.ui/'generated']:
        for name,h in file_hashes(directory).items():require(sha256(out/name)==h,'Packaged reviewed asset differs: '+name)
    require(read(out/'entities'/f'{SHIP}.unit')==new_unit(meta,recipe),'Unexpected Amun unit fields')
    require(read(out/'entities'/f'{SHIP}.unit_skin')==ship_skin(meta,ui,a),'Unexpected Amun skin fields')
    require(read(out/'localized_text/en.localized_text')==localization(a),'Unapproved localization change')
    require(sha256(out/'ASSET-SOURCES.md')==sha256(ROOT/'audit/amun06/packaged-asset-sources.md'),'Asset credit drift')
    checks=check_amun06(out,BASE,a.game,a.sdk,SHIP,SHIP,recipe['private_weapons'][:3])
    resolver=Resolver(out,a.game)
    for unit in ['trader_light_frigate','expanse_rocinante_hero',SHIP]:resolver.unit(unit,'package root');check_actions(out,resolver,unit)
    for p in (out/'meshes').glob('*.mesh'):resolver.mesh(p.stem,'package root')
    for p in (out/'mesh_materials').glob('*.mesh_material'):resolver.material(p.stem,'package root')
    for p in (out/'effects').glob('*.particle_effect'):
        for ptr,v in strings(read(p)):
            if ptr[-1].endswith('texture') or ptr[-1] in ['texture_0','texture_1']:resolver.resolve('textures/'+v+'.dds',p)
            elif ptr[-1]=='mesh':resolver.mesh(v,p)
    geometry=[binary_geometry(p) for p in sorted((out/'meshes').glob('expanse06*.mesh'))]
    require(len(meta['rigs'])==3 and len(geometry)==8,'Expected three rigs, hull and modeled pod')
    hull=resolver.mesh(meta['hull_mesh'],'Amun model hardpoints')
    for r in meta['rigs']:
        mount=r['mount'];point=next(p for p in hull['meshpoints'] if p['name']==mount['mesh_point']);rot=np.array(point['rotation']).reshape(3,3)
        require(np.allclose(point['position'],mount['weapon_position'],atol=2e-5) and np.allclose(rot[1],mount['up'],atol=2e-5) and np.allclose(rot[2],mount['forward'],atol=2e-5),'Compiled PDC mount differs from unit')
        w=read(out/'entities'/(mount['weapon']+'.weapon'));require(w['turret']==r['turret_override'],'Actual turret frame not bound')
    expected_phase=phase_plume(a.game,meta['equipment']['exhaust'])
    require(read(out/'effects/expanse06_amun_phase_plume.particle_effect')==expected_phase,'Incorrect phase nozzle')
    require(read(out/'effects/expanse06_boarding_pod_visual.particle_effect')==pod_effect(a.game,meta['pod_mesh']),'Unexpected boarding particle changes')
    allowed={'.mod_meta_data','ASSET-SOURCES.md','localized_text/en.localized_text','uniforms/unit_tag.uniforms'}|{'entities/'+p+'.player' for p in PLAYERS}|{'entities/'+e+'.entity_manifest' for e in ['unit','unit_skin','weapon','ability','buff','action_data_source']}
    old=file_hashes(BASE);new=file_hashes(out)
    require(not set(old)-set(new),'Existing content removed')
    for name,h in old.items():
        if name not in allowed:require(new[name]==h,'Working04 content changed: '+name)
    return {'status':'PASS OFFLINE ONLY','runtime':'NOT RUN','behavior':behavior,'supplemental':checks,'geometry':geometry,'references':resolver.edges,'preservation':frozen(a.game,a.sdk),'working04_files_preserved':True}

def main(a):
    frozen(a.game,a.sdk)
    for label,path in [('accepted package',BASE),('behavior',a.behavior),('geometry',a.geometry/'build/amun06-b/game'),('UI',a.ui/'generated')]:
        require(path.is_dir(),'Missing ignored '+label+' dependency; build NOT RUN: '+str(path))
    meta=read(a.geometry/'audit/amun06-b/integration-spec.json')
    recipe=read(a.behavior/'integration-recipe.json');ui=read(a.ui/'integration-spec.json')
    require(meta['status'].startswith('PASS') and ui['status'].startswith('PASS'),'Incomplete geometry/UI handoff')
    out=ROOT/'build/experiments'/ID;game_assets=a.geometry/'build/amun06-b/game'
    reviewed=read(ROOT/'audit/amun06/reviewed-inputs.json')
    for path,h in reviewed.items():require(sha256(path)==h,'Reviewed dependency changed: '+path)
    if not a.validate_only:
        require(not out.exists() and not out.with_suffix('.zip').exists(),'Refusing existing Amun experiment')
        shutil.copytree(BASE,out)
        for directory in [a.behavior/'core/entities']:
            for p in directory.iterdir():cp(p,out/'entities'/p.name)
        for directory in [game_assets,a.ui/'generated']:
            for p in directory.rglob('*'):
                if p.is_file():cp(p,out/p.relative_to(directory))
        for r in meta['rigs']:
            p=out/'entities'/(r['mount']['weapon']+'.weapon');weapon=read(p);weapon['turret']=r['turret_override'];write(p,weapon)
        p=out/'entities/expanse06_amun_magazine.ability';ability=read(p);ability['ability_positions']=ability_positions(meta['equipment']['torpedo_ports']);write(p,ability)
        p=out/'entities/expanse06_amun_boarding.ability';ability=read(p)
        for op in ability['active_actions']['actions']['actions'][0]['operators']:
            if op['operator_type']=='play_weapon_effects':op['mesh_point']='weapon.boarding.0'
        write(p,ability)
        p=out/'entities/expanse06_amun_boarding.action_data_source';ads=read(p)
        for binding in ads['effect_alias_bindings']:
            if binding['alias_name']=='pirate_boarding_crew_shuttle':binding['alias_binding']['particle_effect']='expanse06_boarding_pod_visual'
        write(p,ads)
        write(out/'entities'/f'{SHIP}.unit',new_unit(meta,recipe));write(out/'entities'/f'{SHIP}.unit_skin',ship_skin(meta,ui,a))
        for ident in PLAYERS:
            p=out/'entities'/(ident+'.player');player=read(p);player['buildable_units'].append(SHIP);player['unit_limits']['global'].append({'tag':SHIP,'unit_limit':6});write(p,player)
        p=out/'uniforms/unit_tag.uniforms';tags=read(p);tags['unit_tags'].append({'name':SHIP,'localized_name':SHIP+'_name'});write(p,tags)
        write(out/'effects/expanse06_amun_idle_plume.particle_effect',read(BASE/'effects/expanse03_roci_idle_plume.particle_effect'))
        write(out/'effects/expanse06_amun_phase_plume.particle_effect',phase_plume(a.game,meta['equipment']['exhaust']))
        write(out/'effects/expanse06_boarding_pod_visual.particle_effect',pod_effect(a.game,meta['pod_mesh']))
        manifests(out,a.game);write(out/'localized_text/en.localized_text',localization(a))
        metadata=read(out/'.mod_meta_data');metadata.update(display_name='The Expanse — Amun-Ra 0.6 COMBAT & BOARDING',display_version='0.6.0',short_description='Adds the Amun-Ra combat frigate and timed boarding pods.',long_description='Complete combined experiment: load alone. Preserves tested Corvette/Rocinante. Amun has three PDCs, private heavy weapons, a six-per-player limit and one 10% timed boarding attempt. This core variant has no cloak. New behavior/runtime acceptance pending.')
        if 'logos' in ui:metadata['logos']=ui['logos']
        write(out/'.mod_meta_data',metadata);cp(ROOT/'audit/amun06/packaged-asset-sources.md',out/'ASSET-SOURCES.md')
    report=package_validation(out,a,meta,recipe,ui);write(ROOT/'audit/amun06/package-validation.json',report)
    if not a.validate_only:
        with zipfile.ZipFile(out.with_suffix('.zip'),'w',zipfile.ZIP_DEFLATED) as z:
            for p in sorted(out.rglob('*')):
                if p.is_file():
                    i=zipfile.ZipInfo(p.relative_to(out).as_posix(),(2026,9,12,0,0,0));i.compress_type=zipfile.ZIP_DEFLATED;i.external_attr=0o100644<<16;z.writestr(i,p.read_bytes())
    summary={'mod_id':ID,**verify_zip(out.with_suffix('.zip'),out),'runtime':'NOT RUN','installed':False};write(ROOT/'audit/amun06/package-summary.json',summary)
    deps=[BASE,a.behavior,game_assets,a.geometry/'audit/amun06-b',a.ui]
    write(out.with_suffix('.dependencies.json'),[str(p.resolve()) for p in deps]);write(out.with_suffix('.provenance.json'),provenance(out.with_suffix('.zip'),ROOT,deps));print(json.dumps(summary,indent=2))

if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__)
    for key in ['game','sdk','behavior','geometry','ui']:p.add_argument('--'+key,type=Path,required=True)
    p.add_argument('--validate-only',action='store_true');main(p.parse_args())
