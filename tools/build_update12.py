"""Assemble four new fleet-test roles without touching earlier installed mods."""
import argparse
import copy
import json
import shutil
import zipfile
from pathlib import Path
import numpy as np
from build_polish import write, cp
from build_amun06 import manifests, patch_pointer
from build_update11 import aliases, spatial, voice_pool
from build_combat04 import phase_plume
from flight03_effects import scale_effect
from update12_behavior import CONFIG, generate
from validate_experiments import read, require, file_hashes, sha256, provenance, verify_zip

ROOT = Path(__file__).resolve().parents[1]
GAME = ROOT.parent / 'SteamLibrary/steamapps/common/Sins2'
SDK = GAME.parent / 'Sins of a Solar Empire II - Mod Tools'
WORKERS = ROOT.parent / 'expanse-workers'
BASE = ROOT / 'build/experiments/expanse_update11'
AUDIT = ROOT / 'audit/update12'
ID = 'expanse_update12'
PLAYERS = ['trader_loyalist', 'trader_rebel', 'dlc_trader_loyalist']
SCOUT = 'trader_scout_corvette'


def inputs():
    # Main-reviewed adapter normalizes the worker contracts without changing
    # their source files. It cannot substitute missing geometry.
    path = AUDIT / 'integration-inputs.json'
    require(path.is_file(), 'Missing reviewed worker contracts: ' + str(path))
    contracts = read(path)
    for name in ['raptor', 'pella', 'scirocco', 'sunflare']:
        require(name in contracts, 'Missing asset-dependent experiment: ' + name)
        for field in ['metadata', 'ui']:
            p = Path(contracts[name][field])
            require(p.is_file(), 'Missing ignored dependency: ' + str(p))
            d = read(p)
            require(d['status'].startswith('PASS'), 'Incomplete worker candidate: ' + str(p))
    return {k: {field: read(v[field]) for field in ['metadata', 'ui']} for k, v in contracts.items()}


def reviewed():
    p = AUDIT / 'reviewed-inputs.json'
    require(p.is_file(), 'Main review hash manifest missing')
    for name, digest in read(p).items():
        require(Path(name).is_file() and sha256(name) == digest, 'Reviewed dependency changed/missing: ' + name)


def copy_resources(directory, out):
    require(Path(directory).is_dir(), 'Missing generated assets: ' + str(directory))
    for p in sorted(Path(directory).rglob('*')):
        if p.is_file():
            dst = out / p.relative_to(directory)
            if dst.exists():
                require(sha256(dst) == sha256(p), 'Asset collision: ' + str(dst))
            else:
                cp(p, dst)


def phase_effect(nozzles, width=1.5, length=6.):
    result = None
    for i, nozzle in enumerate(nozzles):
        base = phase_plume(GAME, nozzle)
        d = scale_effect(base, width / 1.5, length / 6., blue=True)
        for original, node in zip(base['nodes'], d['nodes'], strict=True):
            for axis, anchor, scalar in zip(['x', 'y', 'z'], nozzle['position'], [width / 1.5, width / 1.5, length / 6.], strict=True):
                node[axis] = [anchor + (v - anchor) * scalar for v in original[axis]]
        def shift(x):
            if isinstance(x, dict):
                for k, v in x.items():
                    if k in ['id', 'attacher_id', 'attachee_id']: x[k] = v + 1000 * i
                    else: shift(v)
            elif isinstance(x, list):
                for v in x: shift(v)
        shift(d)
        if result is None: result = d
        else:
            for key in ['nodes', 'emitters', 'modifiers', 'emitter_to_node_attachments', 'modifier_to_emitter_attachments']:
                result[key] += d[key]
    require(result is not None, 'No measured exhaust')
    return result


def new_capital(kind, meta):
    prefix = 'expanse12_' + kind; cfg = CONFIG[kind]
    # Shieldless installed Kol overlay carries native capital experience,
    # selection, construction and component behavior with no titan slot use.
    u = read(BASE / 'entities/trader_battle_capital_ship.unit')
    spatial(u, meta)
    u['skin_groups'] = [{'skins': [prefix]}]
    u['tags'] = ['capital_ship'] + ([prefix] if kind == 'pella' else [])
    u['ship_roles'] = ['attack_ship']
    u['build'].update(supply_cost=cfg['supply'], build_time=120. if kind == 'raptor' else 150.,
                      price={'credits': {'raptor': 4500., 'pella': 6000., 'scirocco': 5500.}[kind],
                             'metal': {'raptor': 1200., 'pella': 1700., 'scirocco': 1500.}[kind],
                             'crystal': {'raptor': 850., 'pella': 1200., 'scirocco': 1000.}[kind]})
    u['physics'].update(max_linear_speed=cfg['speed'], time_to_max_linear_speed=5.,
                        max_angular_speed=25., time_to_max_angular_speed=1.25, max_bank_angle=25.)
    u['attack'] = read(BASE / 'entities/expanse_rocinante_hero.unit')['attack']
    first = copy.deepcopy(u['health']['levels'][0])
    for level in u['health']['levels']:
        level['max_hull_points'] *= cfg['hull'] / first['max_hull_points']
        level['max_armor_points'] *= cfg['armor'] / first['max_armor_points']
    mounts = [copy.deepcopy(x['mount']) for x in meta['rigs']]
    match = next((i for i, r in enumerate(meta['rigs']) if r['kind'] == 'rail'), 0)
    u['weapons'] = {'weapons': mounts, 'max_range_weapon_index': match}
    # Main build writes weapons before this function is called.
    template = read(BASE / 'entities' / ('expanse03_hero_railgun.weapon' if meta['rigs'][match]['kind'] == 'rail' else 'expanse10_donnager_pdc_0.weapon'))
    u['ai']['attack_target_type_groups'] = template['attack_target_type_groups']
    u['ai']['attack_target_type_groups_matching_weapon'] = mounts[match]['weapon']
    u['ai']['attack_target_type_groups_to_ignore'] = []
    aids = [prefix + '_light_magazine']
    if kind == 'scirocco': aids.append(prefix + '_heavy_magazine')
    aids += [prefix + '_' + p for p in ['reactor', 'launch_corvette', 'marines', 'reactor_breach']]
    aids.append('expanse11_no_shields')
    u['abilities'] = [{'abilities': aids}]
    # Four ordinary capital component slots; no Ankylon-only components.
    u['item_builds'] = copy.deepcopy(read(BASE / 'entities/expanse_donnager_battleship.unit')['item_builds'])
    u['spawn_debris'].pop('custom_debris', None)
    if 'spawn_loot' in u['spawn_debris']:
        u['spawn_debris']['spawn_loot']['loot_name'] = prefix + '.loot'
    return u


def new_skin(kind, meta, ui, out):
    prefix = 'expanse12_' + kind
    if kind == 'sunflare':
        skin = read(GAME / 'entities/trader_scout_corvette.unit_skin')
    else:
        skin = read(BASE / 'entities/expanse_donnager_battleship.unit_skin')
    s = skin['skin_stages'][0]
    s['gui'].update(name=prefix + '.name', description=prefix + '.description')
    s['gui'].pop('special_operation_names', None)
    s['unit_mesh']['mesh'] = meta['hull_mesh']
    s['child_mesh_alias_bindings'] = aliases(meta) if meta.get('rigs') else {'map': []}
    s['min_camera_distance'] = max(70., meta['ship_spatial']['radius'] * 2.)
    for patch in ui['skin_patches']: patch_pointer(skin, patch['pointer'], patch['value'])
    # Retain accepted generic captain pool with all source sound files unchanged.
    voice_pool(skin, small_ship=kind != 'scirocco')
    s['effects']['flair_effects'] = []
    s['effects'].pop('shield_effect', None)
    s['effects']['exhaust_effects'] = {'particle_effects': [{'particle_effect': prefix + '_idle_plume'}]}
    s['effects']['hyperspace_effects'] = copy.deepcopy(read(BASE / 'entities/expanse_rocinante_hero.unit_skin')['skin_stages'][0]['effects']['hyperspace_effects'])
    for key in ['travel_effect', 'travel_effect_between_stars', 'travel_effect_destabilized']:
        s['effects']['hyperspace_effects'][key] = prefix + '_phase_plume'
    width, length = (.35, .6) if kind == 'sunflare' else (1., 2.)
    write(out / 'effects' / (prefix + '_idle_plume.particle_effect'), scale_effect(read(GAME / 'effects/exhaust_tech_medium_01.particle_effect'), width, length, blue=True))
    write(out / 'effects' / (prefix + '_phase_plume.particle_effect'), phase_effect(meta['equipment']['exhausts'], width, length * 4))
    if kind != 'sunflare':
        # These palettes/models are capitals, not titan death sequences.
        s['death_sequence_group'] = read(GAME / 'entities/trader_battle_capital_ship.unit_skin')['skin_stages'][0]['death_sequence_group']
    return skin


def build(out):
    require(not out.exists() and not out.with_suffix('.zip').exists(), 'Refusing an existing fleet package')
    reviewed(); parts = inputs(); shutil.copytree(BASE, out)
    for obj in parts.values():
        for k in ['metadata', 'ui']: copy_resources(obj[k]['game_directory'], out)
    behavior = generate(out, {k: v['metadata'] for k, v in parts.items()})
    for kind in CONFIG:
        prefix = 'expanse12_' + kind
        write(out / 'entities' / (prefix + '.unit'), new_capital(kind, parts[kind]['metadata']))
        write(out / 'entities' / (prefix + '.unit_skin'), new_skin(kind, parts[kind]['metadata'], parts[kind]['ui'], out))
    scout = read(BASE / 'entities' / (SCOUT + '.unit'))
    spatial(scout, parts['sunflare']['metadata'])
    scout['physics']['max_linear_speed'] = read(GAME / 'entities' / (SCOUT + '.unit'))['physics']['max_linear_speed'] * 2.
    scout['physics']['time_to_max_linear_speed'] = 2.5
    scout['hyperspace'].update(charge_time=2., charge_time_variance=0.)
    for h in scout['health']['levels']:
        h.update(max_hull_points=100., max_armor_points=0., armor_strength=0., armor_point_restore_rate=0.)
    scout['build'].update(price={'credits': 200.}, supply_cost=5)
    for group in scout['abilities']: group['abilities'].append('expanse12_sunflare_burn')
    write(out / 'entities' / (SCOUT + '.unit'), scout)
    write(out / 'entities' / (SCOUT + '.unit_skin'), new_skin('sunflare', parts['sunflare']['metadata'], parts['sunflare']['ui'], out))
    for name in PLAYERS:
        p = out / 'entities' / (name + '.player'); d = read(p)
        d['buildable_units'] += ['expanse12_' + k for k in CONFIG]
        d['unit_limits']['global'].append({'tag': 'expanse12_pella', 'unit_limit': 1})
        write(p, d)
    p = out / 'uniforms/unit_tag.uniforms'; d = read(p)
    d['unit_tags'].append({'name': 'expanse12_pella', 'localized_name': 'expanse12_pella.name'}); write(p, d)
    # Apply the same explicit hero exclusion to each relevant capture path.
    for p in (out / 'entities').glob('*.action_data_source'):
        if not (p.stem == 'expanse06_amun_boarding' or p.stem.endswith('_marines')): continue
        d = read(p)
        for row in d.get('target_filters', []):
            if row['target_filter_id'] == 'boarding_capital_target':
                row['target_filter']['constraints'].append({'constraint_type': 'composite_not', 'constraint': {'constraint_type': 'has_definition', 'unit_definition': 'expanse12_pella'}})
        write(p, d)
    loc = read(out / 'localized_text/en.localized_text'); loc.update(behavior['localization'])
    for key in ['expanse06_amun_boarding.description', 'expanse10_donnager_marines.description']:
        loc[key] = loc[key].replace('Rocinante is excluded.', 'Rocinante and Pella are excluded.')
    for kind, title in [('raptor', 'MCRN Raptor-class'), ('pella', 'Pella — Free Navy flagship'), ('scirocco', 'MCRN Scirocco-class')]:
        prefix = 'expanse12_' + kind; loc[prefix + '.name'] = title; loc[prefix + '.loot'] = title + ' wreckage'
        loc[prefix + '.description'] = {'raptor': 'Fast Martian light capital. Nine PDCs, eighteen light torpedoes and fleet-support abilities. 150 supply.',
                                      'pella': 'Stolen Martian light capital in silver Free Navy livery. Unique hero, provisionally available to TEC. 200 supply.',
                                      'scirocco': 'Fast assault capital with a light railgun, defensive cannons and light/heavy torpedo batteries. 200 supply.'}[kind]
    loc.update({'expanse12_sunflare.name': 'Sunflare racing pinnace', 'expanse12_sunflare.description': 'Unarmed racing scout. 3,000 normal speed, 100 hull and no armor. Emergency 20G burn risks the ship for a rapid escape.',
                'trader_scout_corvette_name': 'Sunflare racing pinnace', 'trader_scout_corvette_name.garrison': 'Sunflare racing pinnace'})
    write(out / 'localized_text/en.localized_text', loc)
    manifests(out, GAME)
    info = read(out / '.mod_meta_data'); info.update(display_name='The Expanse — 0.12 CAPITAL FLEET', display_version='0.12.0', short_description='Raptor and Scirocco capitals, silver Pella hero and Sunflare racing scout.', long_description='Load alone. Includes 0.11 and its earlier ships/audio. New capital and scout runtime tests remain pending. Pella is temporarily on the TEC roster; custom factions deferred.')
    info['logos'] = parts['raptor']['ui']['logos']; write(out / '.mod_meta_data', info)
    (out / 'ASSET-SOURCES.md').write_text((ROOT / 'ASSET-SOURCES.md').read_text())
    write(AUDIT / 'behavior-build.json', behavior)


def main(args):
    from update12_validate import validate, preservation
    preservation(); out = ROOT / 'build/experiments' / ID
    if not (args.validate_only or args.package_existing): build(out)
    write(AUDIT / 'package-validation.json', validate(out))
    if not args.validate_only:
        require(not out.with_suffix('.zip').exists(), 'Refusing existing ZIP')
        with zipfile.ZipFile(out.with_suffix('.zip'), 'w', zipfile.ZIP_DEFLATED) as z:
            for p in sorted(out.rglob('*')):
                if p.is_file():
                    zi = zipfile.ZipInfo(p.relative_to(out).as_posix(), (2026, 9, 13, 0, 0, 0)); zi.compress_type = zipfile.ZIP_DEFLATED; zi.external_attr = 0o100644 << 16
                    z.writestr(zi, p.read_bytes())
    summary = {'mod_id': ID, **verify_zip(out.with_suffix('.zip'), out), 'installed': False, 'runtime': 'NOT RUN'}
    write(AUDIT / 'package-summary.json', summary)
    deps = [BASE, AUDIT / 'integration-inputs.json', AUDIT / 'reviewed-inputs.json'] + [Path(v[k]['game_directory']) for v in inputs().values() for k in ['metadata', 'ui']]
    write(out.with_suffix('.dependencies.json'), list(map(str, deps))); write(out.with_suffix('.provenance.json'), provenance(out.with_suffix('.zip'), ROOT, deps))
    print(json.dumps(summary, indent=2))


if __name__ == '__main__':
    p = argparse.ArgumentParser(description=__doc__); g = p.add_mutually_exclusive_group()
    g.add_argument('--validate-only', action='store_true'); g.add_argument('--package-existing', action='store_true'); main(p.parse_args())
