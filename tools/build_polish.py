"""Integrate reviewed six-PDC, repaired mesh and UI outputs into a NEW local mod.

Installed content, baselines and ignored master assets are read-only. This
script never installs/enables a mod and refuses existing package destinations.
"""
from pathlib import Path
import argparse, copy, json, shutil, zipfile
import jsonschema
import numpy as np
from PIL import Image
from validate_experiments import (read, sha256, require, verify_pins, Resolver,
                                  verify_zip, provenance, compare_tree, file_hashes)

ROOT = Path(__file__).resolve().parents[1]
MOD_ID = 'expanse_corvette_polish'

def write(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2) + '\n')

def cp(source, target):
    if not source.is_file():
        raise FileNotFoundError(f'BLOCKED: missing local ignored input: {source}')
    target.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(source, target)

def patch(data, pointer, old, new):
    keys = pointer.strip('/').split('/'); at = data
    for k in keys[:-1]:
        at = at[int(k)] if isinstance(at, list) else at[k]
    require(at[keys[-1]] == old, f'Unexpected source at {pointer}')
    at[keys[-1]] = new

def preservation(game, sdk):
    frozen = read(ROOT / 'audit/experiments/checkpoint.json')
    for name, records in frozen['baselines'].items():
        for kind in ['build', 'installed']:
            compare_tree(records[kind])
        require(sha256(Path(records['build']['path']).with_suffix('.zip')) == records['zip_sha256'], 'Baseline ZIP drift')
    for record in frozen['shared_read_only_inputs'].values():
        compare_tree(record)
    # User testing intentionally changed settings after the old checkpoint.
    # Preserve this turn's settings snapshot, not the obsolete disabled state.
    settings = read(ROOT / 'audit/polish/checkpoint.json')['settings_at_start']
    current = file_hashes(Path(settings['path']))
    # The user may close the game while we work; window/debug/lobby settings
    # are game-owned. Record differences, never restore those external edits.
    changed = sorted(k for k in current.keys() | settings['files'].keys() if current.get(k) != settings['files'].get(k))
    write(ROOT / 'audit/polish/settings-observation.json', {'changed_since_start':changed,
          'enabled_mods_unchanged':current.get('.enabled_mods') == settings['files'].get('.enabled_mods'),
          'action':'Read only; game/user settings and mod selections since preparation are observed, never restored'})
    return verify_pins(ROOT, game, sdk)

def validate(mod, game, sdk, recipe, ui):
    unit = read(mod / 'entities/trader_light_frigate.unit')
    stock = read(game / 'entities/trader_light_frigate.unit')
    mounts = unit['weapons']['weapons']
    require(len(mounts) == 6 and len({m['weapon'] for m in mounts}) == 6, 'Expected six distinct physical weapon entries')
    require(mounts == recipe['proposed_unit_mounts'], 'Mount data drift')
    restored = copy.deepcopy(unit)
    restored['weapons'] = stock['weapons']
    restored['ai']['attack_target_type_groups_matching_weapon'] = stock['ai']['attack_target_type_groups_matching_weapon']
    restored['ai']['attack_target_type_groups'] = stock['ai']['attack_target_type_groups']
    require(restored == stock, 'Unexpected change to health, navigation, economy or other unit values')
    require(unit['weapons']['max_range_weapon_index'] == 0, 'Unexpected max range weapon index')
    require(unit['ai']['attack_target_type_groups_matching_weapon'] == mounts[0]['weapon'], 'Stale AI weapon identity')
    ids = recipe['weapon_ids']
    require(read(mod / 'entities/weapon.entity_manifest') == {'ids': ids}, 'Weapon manifest mismatch')
    require(sorted(p.stem for p in (mod / 'entities').glob('*.weapon')) == sorted(ids), 'Unexpected shared/candidate weapons')
    expected_loc = {'trader_light_frigate_name', 'trader_light_frigate_description'} | set(recipe['required_additive_localization'])
    loc = read(mod / 'localized_text/en.localized_text')
    require(set(loc) == expected_loc, 'Unexpected localization scope')
    schemas = 0
    for path in mod.rglob('*'):
        schema = {'.unit':'unit-schema.json','.unit_skin':'unit-skin-schema.json',
                  '.weapon':'weapon-schema.json','.brush':'brush-schema.json'}.get(path.suffix)
        if schema:
            jsonschema.Draft7Validator(read(sdk / 'json_schemas' / schema)).validate(read(path)); schemas += 1
    resolver = Resolver(mod, game); resolver.unit('trader_light_frigate', 'polish-root')
    hull = resolver.mesh(read(mod/'entities/trader_light_frigate.unit_skin')['skin_stages'][0]['unit_mesh']['mesh'], 'polish-rig-check')
    for i, ident in enumerate(ids):
        w = read(mod / 'entities' / (ident + '.weapon'))
        require('burst_pattern' not in w, 'Damage burst added; firing budget would change')
        require(w['damage'] == 28 and w['cooldown_duration'] == .25 and w['penetration'] == 0 and w['range'] == 2500, 'Unreviewed PDC budget')
        require(w['uniforms_target_filter_id'] == 'common_and_strikecraft_and_torpedo_weapon' and 'torpedo_strikecraft' in w['attack_target_type_groups'], 'Interception eligibility removed')
        require(w['acquire_target_logic'] == 'best_target_in_range', 'Unreviewed acquisition logic')
        require(len(w['turret']['muzzle_positions']) == 1, 'A physical PDC must use one cluster muzzle')
        require(w['name'] in loc, 'Unresolved PDC localized name')
        point = next(p for p in hull['meshpoints'] if p['name'] == mounts[i]['mesh_point'])
        rotation = np.array(point['rotation']).reshape(3,3)
        require(np.allclose(rotation[1],mounts[i]['up'],atol=2e-5) and np.allclose(rotation[2],mounts[i]['forward'],atol=2e-5), 'Mount basis disagrees with installed row-vector convention')
        require(np.allclose(rotation[0],np.cross(mounts[i]['up'],mounts[i]['forward']),atol=2e-5), 'Mount handedness mismatch')
    stage = read(mod / 'entities/trader_light_frigate.unit_skin')['skin_stages'][0]
    # Explicit brushes + DPI variants; no guessed atlas or DDS conversion.
    ui_count = 0
    for edit in ui['patches']:
        brush = mod / 'brushes' / (edit['value'] + '.brush')
        b = read(brush); texture = b['normal_state']['texture']
        for dpi in [100] + b.get('supported_dpis', []):
            suffix = '' if dpi == 100 else str(dpi)
            png = mod / 'textures' / (texture + suffix + '.png')
            with Image.open(png) as image:
                expected_alpha = (255,255) if texture.endswith('_hud_picture') else (0,255)
                require(image.mode == 'RGBA' and image.getchannel('A').getextrema() == expected_alpha, f'Bad sprite alpha: {png}')
            resolver.resolve(str(png.relative_to(mod)), brush); ui_count += 1
    meta = read(mod / '.mod_meta_data')
    example = read(sdk / 'examples/mods/super_fast_trader_scout_corvette/.mod_meta_data')
    require(set(meta) == set(example) and meta['compatibility_version'] == 2, 'Unverified metadata shape')
    for name in meta['logos'].values():
        with Image.open(mod / name) as image:
            image.verify()
    require(len(list((mod / 'meshes').glob('*.mesh'))) == 13, 'Expected hull and twelve child meshes')
    allowed = {'.mod_meta_data','ASSET-SOURCES.md','mod_small_logo.png','mod_large_logo.png'}
    kinds = {'entities':{'.unit','.unit_skin','.weapon','.entity_manifest'},'meshes':{'.mesh'},
             'mesh_materials':{'.mesh_material'},'textures':{'.dds','.png'},'brushes':{'.brush'},'localized_text':{'.localized_text'}}
    for name in file_hashes(mod):
        p = Path(name)
        require(name in allowed or len(p.parts)==2 and p.suffix in kinds.get(p.parts[0],set()), f'Package contamination: {name}')
    return {'status':'PASS','schema_count':schemas,'weapons':6,'geometry_meshes':13,'ui_reference_checks':ui_count,
            'exact_nonweapon_unit_values':'PASS','no_shared_vanilla_weapon_overrides':'PASS',
            'references':resolver.edges,'runtime':'NOT RUN',
            'limits':'Schemas/reference/damage-budget checks do not establish runtime culling, rotation, target priority or damage cadence.'}

def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--weapons',type=Path,required=True);ap.add_argument('--geometry',type=Path,required=True)
    ap.add_argument('--ui',type=Path,required=True);ap.add_argument('--game',type=Path,required=True);ap.add_argument('--sdk',type=Path,required=True)
    ap.add_argument('--validate-only',action='store_true',help='Check the existing polish package without rebuilding it')
    a=ap.parse_args(); preservation(a.game,a.sdk)
    recipe=read(a.weapons/'integration-recipe.json');ui=read(a.ui/'integration-spec.json')
    weapon_check=read(a.weapons/'offline-validation.json')
    require(weapon_check['status'].startswith('PASS'), 'BLOCKED: weapon recipe check failed')
    for name,digest in weapon_check['output_hashes'].items():
        require(sha256(a.weapons/'entities'/name)==digest,'Weapon source drift: '+name)
    geometry=read(a.geometry/'integration-spec.json')
    require(geometry['status']=='PASS', 'BLOCKED: geometry offline gates have not passed')
    require(read(a.ui/'ui-validation.json')['status']=='PASS','BLOCKED: UI offline gates failed')
    for sprite in read(a.ui/'ui-validation.json')['sprites']:
        require(sha256(Path(sprite['generated']))==sprite['generated_sha256'],'UI source drift')
    out=ROOT/'build/experiments'/MOD_ID
    if a.validate_only:
        for mesh in geometry['meshes']:
            require(sha256(out/'meshes'/Path(mesh['path']).name)==mesh['sha256'],'Packaged geometry differs from reviewed repaired mesh')
        checks=validate(out,a.game,a.sdk,recipe,ui)
        print(json.dumps({'status':checks['status'],**verify_zip(out.with_suffix('.zip'),out),'runtime':'NOT RUN'},indent=2))
        return
    require(not out.exists() and not out.with_suffix('.zip').exists(),'Refusing existing polish output')
    unit=read(a.game/'entities/trader_light_frigate.unit');skin=read(a.game/'entities/trader_light_frigate.unit_skin')
    require(recipe['proposed_unit_mounts']==geometry['mounts'],'Weapon/geometry mount recipes disagree')
    unit['weapons']['weapons']=recipe['proposed_unit_mounts'];unit['weapons']['max_range_weapon_index']=0
    unit['ai']['attack_target_type_groups_matching_weapon']=recipe['weapon_ids'][0]
    unit['ai']['attack_target_type_groups']=read(a.weapons/'entities'/(recipe['weapon_ids'][0]+'.weapon'))['attack_target_type_groups']
    stage=skin['skin_stages'][0];stage['unit_mesh']['mesh']=geometry['hull_mesh']
    stage['child_mesh_alias_bindings']={'map':recipe['required_skin_alias_map']}
    stage['effects']['effect_alias_bindings'].extend(recipe['required_effect_alias_bindings'])
    for edit in ui['patches']:patch(skin,edit['pointer'],edit['old'],edit['value'])
    write(out/'entities/trader_light_frigate.unit',unit);write(out/'entities/trader_light_frigate.unit_skin',skin)
    for ident in recipe['weapon_ids']:cp(a.weapons/'entities'/(ident+'.weapon'),out/'entities'/(ident+'.weapon'))
    write(out/'entities/weapon.entity_manifest',{'ids':recipe['weapon_ids']})
    loc=read(ROOT/'src/name-only/en.localized_text');loc.update(recipe['required_additive_localization'])
    loc['trader_light_frigate_description']='Fast-attack corvette with six dual-purpose point-defense cannons.'
    write(out/'localized_text/en.localized_text',loc)
    for mesh in geometry['meshes']:
        source=Path(mesh['path']);require(sha256(source)==mesh['sha256'],f'Geometry output drift: {source}')
        cp(source,out/'meshes'/source.name)
        for ident, source_material in mesh['material_sources'].items():
            material=read(Path(source_material));write(out/'mesh_materials'/(ident+'.mesh_material'),material)
            for key,val in material.items():
                if key.endswith('_texture'):cp(ROOT/'build/converted-textures'/(val+'.dds'),out/'textures'/(val+'.dds'))
    for source in (a.ui/'generated').rglob('*'):
        if source.is_file():cp(source,out/source.relative_to(a.ui/'generated'))
    meta=read(a.sdk/'examples/mods/super_fast_trader_scout_corvette/.mod_meta_data')
    meta.update(display_name='The Expanse — Corvette Polish',display_version='0.2.1',
                short_description='MCRN corvette with six rotating dual-purpose PDCs.',
                long_description='Cobalt-based MCRN corvette prototype with repaired hull surfaces, custom ship UI and six independent PDC mounts. Runtime acceptance pending.',logos=ui['logos'])
    write(out/'.mod_meta_data',meta);cp(ROOT/'ASSET-SOURCES.md',out/'ASSET-SOURCES.md')
    checks=validate(out,a.game,a.sdk,recipe,ui);write(ROOT/'audit/polish/package-validation.json',checks)
    with zipfile.ZipFile(out.with_suffix('.zip'),'w',zipfile.ZIP_DEFLATED) as z:
        for path in sorted(out.rglob('*')):
            if path.is_file():
                info=zipfile.ZipInfo(path.relative_to(out).as_posix(),(2026,9,12,0,0,0));info.compress_type=zipfile.ZIP_DEFLATED;info.external_attr=0o100644<<16
                z.writestr(info,path.read_bytes())
    summary=verify_zip(out.with_suffix('.zip'),out)
    deps=[a.weapons,a.geometry/'integration-spec.json',a.ui]
    deps += [Path(x['path']) for x in geometry['meshes']]
    deps += [ROOT/'assets/derived/baseline/game-materials',ROOT/'build/converted-textures']
    write(out.with_suffix('.dependencies.json'),[str(p.resolve()) for p in deps])
    write(out.with_suffix('.provenance.json'),provenance(out.with_suffix('.zip'),ROOT,deps))
    write(ROOT/'audit/polish/package-summary.json',dict(mod_id=MOD_ID,**summary,runtime='NOT RUN',installed=False))
    preservation(a.game,a.sdk)
    print(json.dumps(summary,indent=2))

if __name__=='__main__':
    try:main()
    except (ValueError,FileNotFoundError) as e:raise SystemExit(str(e))
