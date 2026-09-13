"""Assemble a separate Donnager prototype; never install, enable or rebuild prior mods."""
import argparse, copy, json, shutil, zipfile
from pathlib import Path
import numpy as np
import jsonschema
from build_polish import write, cp
from build_hero03 import ability_positions
from build_amun06 import manifests, patch_pointer
from build_combat04 import binary_geometry, phase_plume
from flight03_effects import scale_effect
from build_combat03 import check_actions
from amun06_validate_package import AmunResolver, check_action_values
from validate_experiments import read, require, file_hashes, sha256, compare_tree, verify_pins, verify_zip, provenance, strings
from donnager10_behavior_validate import validate_components

ROOT=Path(__file__).resolve().parents[1]
GAME=ROOT.parent/'SteamLibrary/steamapps/common/Sins2'
SDK=ROOT.parent/'SteamLibrary/steamapps/common/Sins of a Solar Empire II - Mod Tools'
WORKERS=ROOT.parent/'expanse-workers'
A=WORKERS/'weapon-behavior/build/donnager10-a/final-fit'
B=WORKERS/'tachi-one-pdc'
C=WORKERS/'validation'
BASE=ROOT/'build/experiments/expanse_amun09_cloak'
AUDIT=ROOT/'audit/donnager10'
ID='expanse_donnager10';SHIP='expanse_donnager_battleship'
PLAYERS=['trader_loyalist','trader_rebel','dlc_trader_loyalist']

def preserved():
    snap=read(AUDIT/'checkpoint.json')
    rows=[compare_tree(r) for r in snap['trees']]
    for p,h in snap['zips'].items():require(sha256(p)==h,'Earlier package changed: '+p)
    return {'trees':rows,'old_zips':len(snap['zips']),'pins':verify_pins(ROOT,GAME,SDK)}

def reviewed():
    path=AUDIT/'reviewed-inputs.json'
    require(path.is_file(),'Integrator review/hash manifest missing; build NOT RUN')
    for p,h in read(path).items():require(Path(p).is_file() and sha256(p)==h,'Reviewed dependency missing or changed: '+p)

def new_unit(meta,recipe):
    u=read(GAME/'entities/trader_loyalist_titan.unit')
    for k in ['child_meshes','carrier','exotic_factory','unit_factory','item_access_tags']:u.pop(k,None)
    u['spatial']={k:copy.deepcopy(meta['ship_spatial'][k]) for k in ['box','radius']};u['spatial']['collision_rank']=3
    u['skin_groups']=[{'skins':[SHIP]}];u['tags']=['titan',SHIP]
    u['build']['prerequisites']=[['trader_unlock_loyalist_titan'],['trader_unlock_rebel_titan']]
    u['abilities']=copy.deepcopy(recipe['unit_ability_sets'])
    mounts=[copy.deepcopy(r['mount']) for r in meta['rigs']]
    rail_index=next(i for i,r in enumerate(meta['rigs']) if r['kind']=='rail')
    u['weapons']={'weapons':mounts,'max_range_weapon_index':rail_index}
    w=read(A/'entities'/(mounts[rail_index]['weapon']+'.weapon'))
    u['ai']['attack_target_type_groups']=w['attack_target_type_groups']
    u['ai']['attack_target_type_groups_matching_weapon']=mounts[rail_index]['weapon']
    u['ship_roles']=['attack_ship']
    u['spawn_debris'].pop('custom_debris',None)
    u['spawn_debris']['spawn_loot']['loot_name']=SHIP+'_loot_name'
    # Generic components and consumables accept titan without proprietary access tags.
    ids=['trader_flak_burst','trader_beam_armor','trader_missile_armor','trader_combat_repair_system','trader_heavy_armor','trader_antimatter_engine','trader_rapid_autoloader','trader_targeting_array','trader_salvage_kit','trader_radiation_bomb']
    u['item_builds']=[{'build_group':[n],'weight':5.0} for n in ids]
    return u

def new_skin(meta,ui,voice):
    skin=read(GAME/'entities/trader_loyalist_titan.unit_skin');skin.pop('name',None)
    s=skin['skin_stages'][0];s['unit_mesh']['mesh']='expanse10_donnager_hull'
    s['min_camera_distance']=800.0
    s['gui'].update(name=SHIP+'_name',description=SHIP+'_description')
    for p in ui['skin_patches']:patch_pointer(skin,p['pointer'],p['value'])
    aliases={x['mesh_alias_name']:x for r in meta['rigs'] for x in r['skin_alias_map']}
    s['child_mesh_alias_bindings']={'map':list(aliases.values())}
    s['sounds']['dialogue']=read(voice['dialogue_json'])
    e=s['effects'];e['effect_alias_bindings']=read(A/'ship-effect-aliases.json')
    e['flair_effects']=[];e['shield_effect']='expanse10_donnager_shield'
    e['exhaust_effects']['particle_effects']=[{'particle_effect':'expanse10_donnager_idle_plume'}]
    # Keep the accepted blue phase-plume presentation, with four actual nozzles.
    e['hyperspace_effects']=read(BASE/'entities/expanse_rocinante_hero.unit_skin')['skin_stages'][0]['effects']['hyperspace_effects']
    for k in ['travel_effect','travel_effect_between_stars','travel_effect_destabilized']:e['hyperspace_effects'][k]='expanse10_donnager_phase_plume'
    return skin

def four_phase(nozzles):
    combined=None
    for i,n in enumerate(nozzles):
        effect=phase_plume(GAME,n)
        def shift(d):
            if isinstance(d,dict):
                for k,v in d.items():
                    if k in ['id','attacher_id','attachee_id']:d[k]=v+1000*i
                    else:shift(v)
            elif isinstance(d,list):
                for v in d:shift(v)
        shift(effect)
        if combined is None:combined=effect
        else:
            for k in ['nodes','emitters','modifiers','emitter_to_node_attachments','modifier_to_emitter_attachments']:combined[k]+=effect[k]
    return combined

def localization():
    loc=read(BASE/'localized_text/en.localized_text');extra=read(A/'localization.json')
    require(not set(loc)&set(extra),'New localization replaces existing entries')
    loc.update(extra);loc.update({SHIP+'_name':'Donnager-class',SHIP+'_description':'Martian heavy battleship. Two heavy railguns, sixteen defensive cannons, front light and rear heavy torpedoes. Shares your titan limit. Reactor breach damages nearby allies and enemies.',SHIP+'_loot_name':'Donnager wreckage'})
    return loc

def voice_checks(voice):
    audit=C/'audit/donnager10-c'
    require(file_hashes(voice['game_directory'])==read(audit/'voice-generated-hashes.json'),'Measured voice output drift')
    records=read(audit/'voice-intake.json')['records'];require(len(records)==20,'Missing supplied captain recording')
    for r in records:
        require(sha256(r['source'])==r['source_sha256'] and sha256(r['original'])==r['source_sha256'],'Supplied captain original changed')
        require(sha256(r['wav'])==r['wav_sha256'] and sha256(r['ogg'])==r['ogg_sha256'],'Normalized captain recording changed')

def validate(out,meta,recipe,ui,voice,asset_dirs):
    reviewed()
    voice_checks(voice)
    components=validate_components(A,BASE,GAME,SDK,ROOT,integrated=out)
    old=file_hashes(BASE);new=file_hashes(out)
    allowed={'.mod_meta_data','ASSET-SOURCES.md','localized_text/en.localized_text','uniforms/unit_tag.uniforms'}|{'entities/'+p+'.player' for p in PLAYERS}|{'entities/'+e+'.entity_manifest'for e in ['unit','unit_skin','weapon','ability','buff','action_data_source']}
    require(not set(old)-set(new),'Prior package content removed')
    for n,h in old.items():
        if n not in allowed:require(new[n]==h,'Accepted content changed: '+n)
    require(read(out/'entities'/f'{SHIP}.unit')==new_unit(meta,recipe),'Unexpected Donnager unit delta')
    require(read(out/'entities'/f'{SHIP}.unit_skin')==new_skin(meta,ui,voice),'Unexpected Donnager skin delta')
    require(read(out/'localized_text/en.localized_text')==localization(),'Unexpected localization delta')
    tags=read(BASE/'uniforms/unit_tag.uniforms');tags['unit_tags'].append({'name':SHIP,'localized_name':SHIP+'_name'})
    require(read(out/'uniforms/unit_tag.uniforms')==tags,'Unexpected shared tag change')
    sets=read(out/'entities'/f'{SHIP}.unit')['abilities']
    require(len(sets)==1 and set(sets[0])=={'abilities'} and sets[0]['abilities']==recipe['core_abilities'] and len(set(sets[0]['abilities']))==6,'Abilities must coexist in one unconditional set')
    for p in PLAYERS:
        before=read(BASE/'entities'/(p+'.player'));expected=copy.deepcopy(before);expected['buildable_units'].append(SHIP)
        require(read(out/'entities'/(p+'.player'))==expected,'Player edit exceeds one buildable titan')
        require({'tag':'titan','unit_limit':1} in before['unit_limits']['global'],'Missing shared titan limit')
    for directory in asset_dirs:
        for n,h in file_hashes(directory).items():require(new[n]==h,'Reviewed generated asset differs: '+n)
    schemas=[]
    types={'.unit':'unit','.unit_skin':'unit-skin','.weapon':'weapon','.ability':'ability','.buff':'buff','.action_data_source':'action-data-source','.brush':'brush'}
    for p in sorted(out.rglob('*')):
        if p.suffix not in types or p.relative_to(out).as_posix() in old:continue
        data=read(p);extension=None
        if p.name==SHIP+'.unit':
            extension=data.pop('corruption',None)
            require(extension==read(GAME/'entities/trader_loyalist_titan.unit')['corruption'],'Installed Ankylon extension drift')
        schema=read(SDK/'json_schemas'/(types[p.suffix]+'-schema.json'))
        jsonschema.Draft7Validator(schema).validate(data);jsonschema.Draft202012Validator(schema).validate(data)
        schemas.append({'file':p.name,'result':'PASS pinned + closed-key','installed_corruption_extension':extension})
    resolver=AmunResolver(out,GAME);unit=resolver.unit(SHIP,'new Donnager root')
    actions=check_actions(out,resolver,SHIP);typed=check_action_values(out,GAME,resolver,unit)
    for p in (out/'effects').glob('expanse10*'):
        for ptr,v in strings(read(p)):
            k=ptr[-1]
            if k=='mesh':resolver.mesh(v,p)
            elif k.endswith('texture') or k in ['texture_0','texture_1']:resolver.resolve('textures/'+v+'.dds',p)
        if p.suffix=='.particle_effect':
            effect=read(p)
            ids={k:{x['id']for x in effect[k]}for k in ['nodes','emitters','modifiers']}
            for k in ids:require(len(ids[k])==len(effect[k]),'Duplicate private particle IDs '+str(p))
            for x in effect['emitter_to_node_attachments']:require(x['attacher_id'] in ids['emitters'] and x['attachee_id'] in ids['nodes'],'Unresolved private particle node')
            for x in effect['modifier_to_emitter_attachments']:require(x['attacher_id'] in ids['modifiers'] and x['attachee_id'] in ids['emitters'],'Unresolved private particle modifier')
    geometry=[binary_geometry(p)for p in sorted((out/'meshes').glob('expanse10*.mesh'))]
    hull=resolver.mesh('expanse10_donnager_hull',SHIP);points={p['name']:p for p in hull['meshpoints']}
    require(len(meta['rigs'])==18,'Expected16PDCs and2rails')
    for r in meta['rigs']:
        m=r['mount'];point=points[m['mesh_point']];rot=np.array(point['rotation']).reshape(3,3)
        require(np.allclose(point['position'],m['weapon_position'],atol=2e-5) and np.allclose(rot[1],m['up'],atol=2e-5) and np.allclose(rot[2],m['forward'],atol=2e-5),'Compiled mount mismatch '+m['weapon'])
        weapon=read(out/'entities'/(m['weapon']+'.weapon'));require(weapon['turret']==r['turret_override'],'Turret contract mismatch')
    for p in (out/'entities').glob('*.entity_manifest'):
        require(read(p)['ids']==sorted(q.stem for q in (out/'entities').glob('*.'+p.stem) if not (GAME/'entities'/q.name).exists()),'Manifest mismatch')
    return {'status':'PASS OFFLINE ONLY','runtime':'NOT RUN','accepted09_preserved_except_documented_additive_registration':True,'components':components,'schemas':schemas,'geometry':geometry,'actions':actions,'typed_actions':typed,'reference_edges':resolver.edges,'preservation':preserved()}

def main(args):
    preserved()
    meta_path=B/'audit/donnager10-b/integration-spec.json';ui_path=C/'audit/donnager10-c/ui-integration-spec.json';voice_path=C/'audit/donnager10-c/voice-integration-spec.json'
    for p in [meta_path,ui_path,voice_path,A/'integration-recipe.json']:
        require(p.is_file(),'Missing ignored worker dependency; build NOT RUN: '+str(p))
    meta=read(meta_path);ui=read(ui_path);voice=read(voice_path);recipe=read(A/'integration-recipe.json')
    require(all(d['status'].startswith('PASS')for d in [meta,ui,voice]),'Incomplete geometry/UI/audio checks; package not ready')
    reviewed()
    dirs=[B/'build/donnager10-b/game',Path(ui['game_directory']),Path(voice['game_directory'])]
    out=ROOT/'build/experiments'/ID
    if args.package_existing:require(out.is_dir() and not out.with_suffix('.zip').exists(),'Packaging recovery requires an existing unzipped assembly')
    if not args.validate_only and not args.package_existing:
        require(not out.exists() and not out.with_suffix('.zip').exists(),'Refusing existing Donnager package')
        shutil.copytree(BASE,out)
        for p in (A/'entities').iterdir():cp(p,out/'entities'/p.name)
        for directory in dirs:
            for p in directory.rglob('*'):
                if p.is_file():cp(p,out/p.relative_to(directory))
        for r in meta['rigs']:
            p=out/'entities'/(r['mount']['weapon']+'.weapon');w=read(p);w['turret']=r['turret_override']
            if r['kind']=='rail':w.update(yaw_speed=15.0,pitch_speed=0.0,yaw_firing_tolerance=0.5,pitch_firing_tolerance=1.0)
            write(p,w)
        for kind,key in [('light','light_torpedo_ports'),('heavy','heavy_torpedo_ports')]:
            p=out/'entities'/('expanse10_donnager_'+kind+'_magazine.ability');d=read(p);d['ability_positions']=ability_positions(meta['equipment'][key]);write(p,d)
        p=out/'entities/expanse10_donnager_marines.ability';d=read(p)
        for op in d['active_actions']['actions']['actions'][0]['operators']:
            if op['operator_type']=='play_weapon_effects':op['mesh_point']='weapon.boarding.0'
        write(p,d)
        write(out/'entities'/f'{SHIP}.unit',new_unit(meta,recipe));write(out/'entities'/f'{SHIP}.unit_skin',new_skin(meta,ui,voice))
        for ident in PLAYERS:
            p=out/'entities'/(ident+'.player');d=read(p);d['buildable_units'].append(SHIP);write(p,d)
        p=out/'uniforms/unit_tag.uniforms';d=read(p);d['unit_tags'].append({'name':SHIP,'localized_name':SHIP+'_name'});write(p,d)
        write(out/'localized_text/en.localized_text',localization())
        write(out/'effects/expanse10_donnager_idle_plume.particle_effect',scale_effect(read(GAME/'effects/exhaust_tech_medium_01.particle_effect'),1.5,1.5,blue=True))
        write(out/'effects/expanse10_donnager_phase_plume.particle_effect',four_phase(meta['equipment']['exhausts']))
        shield=read(GAME/'effects/trader_loyalist_titan.shield_effect');shield['primary']['mesh']='expanse10_donnager_hull';write(out/'effects/expanse10_donnager_shield.shield_effect',shield)
        manifests(out,GAME)
        info=read(out/'.mod_meta_data');info.update(display_name='The Expanse — 0.10 DONNAGER PROTOTYPE',display_version='0.10.0',short_description='Donnager titan-slot battleship, sixteen PDCs, two railguns, heavy torpedoes and Martian captain voices.',long_description='Load alone. Includes the accepted0.9 ships, cloak, boarding, voices and music. Adds a Donnager in the shared titan slot with eight component slots. New Donnager runtime tests NOT RUN.');info['logos']=ui['logos'];write(out/'.mod_meta_data',info)
        (out/'ASSET-SOURCES.md').write_text((AUDIT/'packaged-asset-sources.md').read_text())
    report=validate(out,meta,recipe,ui,voice,dirs);write(AUDIT/'package-validation.json',report)
    if not args.validate_only:
        with zipfile.ZipFile(out.with_suffix('.zip'),'w',zipfile.ZIP_DEFLATED)as z:
            for p in sorted(out.rglob('*')):
                if p.is_file():
                    info=zipfile.ZipInfo(p.relative_to(out).as_posix(),(2026,9,13,0,0,0));info.compress_type=zipfile.ZIP_DEFLATED;info.external_attr=0o100644<<16;z.writestr(info,p.read_bytes())
    summary={'mod_id':ID,**verify_zip(out.with_suffix('.zip'),out),'installed':False,'runtime':'NOT RUN'};write(AUDIT/'package-summary.json',summary)
    deps=[BASE,A,meta_path,B/'audit/donnager10-b/final-provenance.json',ui_path,voice_path,C/'audit/donnager10-c/voice-intake.json',C/'audit/donnager10-c/ui-validation.json',*dirs];write(out.with_suffix('.dependencies.json'),list(map(str,deps)));write(out.with_suffix('.provenance.json'),provenance(out.with_suffix('.zip'),ROOT,deps));print(json.dumps(summary,indent=2))

if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);g=p.add_mutually_exclusive_group();g.add_argument('--validate-only',action='store_true');g.add_argument('--package-existing',action='store_true',help='Revalidate a previously assembled, unzipped candidate before packaging; never rewrites its files');main(p.parse_args())
