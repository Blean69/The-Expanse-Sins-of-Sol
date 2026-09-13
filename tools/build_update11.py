"""Build the isolated 0.11 fleet update from reviewed local assets; never install it.

Requires the accepted 0.10 PDC-audio tree, pinned game/SDK and three isolated
worker outputs. Missing ignored dependencies are fatal, never substituted.
"""
import argparse
import copy
import json
import shutil
import zipfile
from pathlib import Path

from build_polish import write, cp
from build_hero03 import ability_positions
from build_amun06 import manifests, patch_pointer
from build_combat04 import phase_plume
from flight03_effects import scale_effect
from validate_experiments import read, require, file_hashes, sha256, provenance, verify_zip

ROOT = Path(__file__).resolve().parents[1]
GAME = ROOT.parent / 'SteamLibrary/steamapps/common/Sins2'
SDK = ROOT.parent / 'SteamLibrary/steamapps/common/Sins of a Solar Empire II - Mod Tools'
WORKERS = ROOT.parent / 'expanse-workers'
A = WORKERS / 'weapon-behavior/build/update11-a/reviewed'
B = WORKERS / 'tachi-one-pdc'
C = WORKERS / 'validation'
BASE = ROOT / 'build/experiments/expanse_donnager10_pdc_audio'
AUDIT = ROOT / 'audit/update11'
ID = 'expanse_update11'
DON = 'expanse_donnager_battleship'
TACHI = 'expanse_mcrn_corvette'
MORRIGAN = 'trader_light_frigate'
HERO = 'expanse_rocinante_hero'
AMUN = 'expanse_amun_ra'
PLAYERS = ['trader_loyalist', 'trader_rebel', 'dlc_trader_loyalist']
SUPPLY = {DON: 500, TACHI: 55, MORRIGAN: 25, HERO: 110}


def inputs():
    paths = [A / 'integration-recipe.json',
             B / 'audit/update11-b/integration-spec.json',
             B / 'audit/update11-b/ui-integration-spec.json',
             C / 'audit/update11-c/integration-spec.json',
             C / 'audit/update11-c/ui-integration-spec.json']
    for p in paths:
        require(p.is_file(), 'Missing ignored local dependency; build BLOCKED: ' + str(p))
    recipe, don, dui, mor, mui = map(read, paths)
    for d in [don, dui, mor, mui]:
        require(d['status'].startswith('PASS'), 'Incomplete worker output: ' + str(d.get('status')))
    return recipe, don, dui, mor, mui


def reviewed_inputs():
    p = AUDIT / 'reviewed-inputs.json'
    require(p.is_file(), 'Main integrator review manifest missing')
    for name, digest in read(p).items():
        require(Path(name).is_file() and sha256(name) == digest, 'Reviewed input missing or changed: ' + name)


def copy_resources(directory, out):
    directory = Path(directory)
    require(directory.is_dir(), 'Missing generated worker assets: ' + str(directory))
    for p in sorted(directory.rglob('*')):
        if p.is_file():
            dest = out / p.relative_to(directory)
            # Shared donor textures/meshes must remain identical.
            if dest.exists():
                require(sha256(dest) == sha256(p), 'Asset collision with accepted package: ' + str(dest))
            else:
                cp(p, dest)


def aliases(meta):
    return {'map': list({x['mesh_alias_name']: x for r in meta['rigs']
                         for x in r['skin_alias_map']}.values())}


def spatial(unit, meta):
    for k in ['box', 'radius']:
        unit['spatial'][k] = copy.deepcopy(meta['ship_spatial'][k])


def voice_pool(skin, small_ship=False):
    dialogue = copy.deepcopy(read(BASE / 'entities' / (DON + '.unit_skin'))['skin_stages'][0]['sounds']['dialogue'])
    dialogue['selected']['neutral'] = ['expanse10_donnager_standing_by',
                                       'expanse10_donnager_duty', 'expanse10_donnager_orders_scared']
    dialogue['order_issued']['neutral'] = ['expanse10_donnager_course', 'expanse10_donnager_duty']
    if small_ship:
        for moods in dialogue.values():
            for mood, lines in list(moods.items()):
                kept = [x for x in lines if x not in ['expanse10_donnager_railguns', 'expanse10_donnager_hammers']]
                if kept:
                    moods[mood] = kept
                else:
                    del moods[mood]
    skin['skin_stages'][0]['sounds']['dialogue'] = dialogue


def enlarged_phase(nozzles):
    combined = None
    for i, nozzle in enumerate(nozzles):
        original = phase_plume(GAME, nozzle)
        effect = scale_effect(original, 2.0, 3.0, blue=True)
        # Scale emission offsets about each nozzle, never about the hull origin.
        for old, node in zip(original['nodes'], effect['nodes'], strict=True):
            for axis, anchor, scalar in zip(['x', 'y', 'z'], nozzle['position'], [2.0, 2.0, 3.0], strict=True):
                node[axis] = [anchor + (v - anchor) * scalar for v in old[axis]]
        def ids(value):
            if isinstance(value, dict):
                for key, child in value.items():
                    if key in ['id', 'attacher_id', 'attachee_id']:
                        value[key] = child + 1000 * i
                    else:
                        ids(child)
            elif isinstance(value, list):
                for child in value:
                    ids(child)
        ids(effect)
        if combined is None:
            combined = effect
        else:
            for key in ['nodes', 'emitters', 'modifiers', 'emitter_to_node_attachments', 'modifier_to_emitter_attachments']:
                combined[key] += effect[key]
    return combined


def build(out):
    from update11_shields import apply as remove_shields
    recipe, don, dui, mor, mui = inputs()
    reviewed_inputs()
    require(not out.exists() and not out.with_suffix('.zip').exists(), 'Refusing to overwrite an existing update package')
    shutil.copytree(BASE, out)
    for p in (A / 'entities').iterdir():
        cp(p, out / 'entities' / p.name)
    for d in [don, dui, mor, mui]:
        copy_resources(d['game_directory'], out)

    # Preserve the accepted six-PDC Tachi as its own buildable unit before the
    # shared Cobalt definition becomes the smaller starter Morrigan.
    t = read(BASE / 'entities' / (MORRIGAN + '.unit'))
    t['skin_groups'] = [{'skins': [TACHI]}]
    t['build']['supply_cost'] = SUPPLY[TACHI]
    t['ai']['attack_target_type_groups_to_ignore'] = []
    ts = read(BASE / 'entities' / (MORRIGAN + '.unit_skin'))
    ts['skin_stages'][0]['gui'].update(name=TACHI + '_name', description=TACHI + '_description')
    ts['skin_stages'][0]['gui'].pop('special_operation_names', None)
    write(out / 'entities' / (TACHI + '.unit'), t)
    write(out / 'entities' / (TACHI + '.unit_skin'), ts)

    m = copy.deepcopy(t)
    m['skin_groups'] = [{'skins': [MORRIGAN]}]
    m['build'].update(supply_cost=25, build_time=15.0, price={'credits': 200.0, 'metal': 35.0})
    m['health']['levels'][0].update(max_hull_points=600.0, max_armor_points=550.0)
    m['physics'].update(max_linear_speed=1450.0, max_angular_speed=30.0)
    m['abilities'] = [{'abilities': ['expanse11_morrigan_magazine']}]
    m['weapons'] = {'weapons': [copy.deepcopy(r['mount']) for r in mor['rigs']], 'max_range_weapon_index': 0}
    m['ai']['attack_target_type_groups_matching_weapon'] = mor['rigs'][0]['mount']['weapon']
    m['ai']['attack_target_type_groups_to_ignore'] = []
    spatial(m, mor)
    write(out / 'entities' / (MORRIGAN + '.unit'), m)
    ms = read(BASE / 'entities' / (MORRIGAN + '.unit_skin'))
    s = ms['skin_stages'][0]
    s['unit_mesh']['mesh'] = mor['hull_mesh']
    s['child_mesh_alias_bindings'] = aliases(mor)
    for patch in mui['skin_patches']:
        patch_pointer(ms, patch['pointer'], patch['value'])
    voice_pool(ms, small_ship=True)
    for key in ['travel_effect', 'travel_effect_between_stars', 'travel_effect_destabilized']:
        s['effects']['hyperspace_effects'][key] = 'expanse11_morrigan_phase_plume'
    write(out / 'entities' / (MORRIGAN + '.unit_skin'), ms)
    write(out / 'effects/expanse11_morrigan_phase_plume.particle_effect', phase_plume(GAME, mor['equipment']['exhaust']))
    for r in mor['rigs']:
        w = read(BASE / 'entities/expanse_polish_pdc_0.weapon')
        w['turret'] = r['turret_override']
        w['range'] = 3500.0
        write(out / 'entities' / (r['mount']['weapon'] + '.weapon'), w)
    p = out / 'entities/expanse11_morrigan_magazine.ability'
    a = read(p)
    a['ability_positions'] = ability_positions(mor['equipment']['light_torpedo_ports'])
    write(p, a)

    d = read(out / 'entities' / (DON + '.unit'))
    d['build']['supply_cost'] = SUPPLY[DON]
    # Retain slow Ankylon translation and physical rail arcs; reduce the long
    # angular acceleration lag that compounds close-orbit tracking problems.
    d['physics']['time_to_max_angular_speed'] = 3.0
    spatial(d, don)
    write(out / 'entities' / (DON + '.unit'), d)
    ds = read(out / 'entities' / (DON + '.unit_skin'))
    ds['skin_stages'][0]['unit_mesh']['mesh'] = don['hull_mesh']
    ds['skin_stages'][0]['child_mesh_alias_bindings'] = aliases(don)
    voice_pool(ds)
    for patch in dui['skin_patches']:
        patch_pointer(ds, patch['pointer'], patch['value'])
    ds['skin_stages'][0]['effects']['exhaust_effects']['particle_effects'] = [{'particle_effect': 'expanse11_donnager_idle_plume'}]
    for key in ['travel_effect', 'travel_effect_between_stars', 'travel_effect_destabilized']:
        ds['skin_stages'][0]['effects']['hyperspace_effects'][key] = 'expanse11_donnager_phase_plume'
    write(out / 'entities' / (DON + '.unit_skin'), ds)
    write(out / 'effects/expanse11_donnager_idle_plume.particle_effect',
          scale_effect(read(BASE / 'effects/expanse10_donnager_idle_plume.particle_effect'), 2.0, 3.0, blue=True))
    write(out / 'effects/expanse11_donnager_phase_plume.particle_effect', enlarged_phase(don['equipment']['exhausts']))
    for r in don['rigs']:
        p = out / 'entities' / (r['mount']['weapon'] + '.weapon')
        w = read(p)
        w['turret'] = r['turret_override']
        write(p, w)
    for p in (out / 'entities').glob('*.weapon'):
        w = read(p)
        if 'pdc_' in p.stem and p.stem.startswith('expanse'):
            w['range'] = 6000.0 if p.stem.startswith('expanse10_donnager_') else 3500.0
            write(p, w)
    p = out / 'entities' / (HERO + '.unit')
    u = read(p); u['build']['supply_cost'] = SUPPLY[HERO]
    u['ai']['attack_target_type_groups_to_ignore'] = []
    write(p, u)
    p = out / 'entities' / (AMUN + '.unit')
    u = read(p); u['ai']['attack_target_type_groups_to_ignore'] = []; write(p, u)

    for name in PLAYERS:
        p = out / 'entities' / (name + '.player')
        u = read(p); u['buildable_units'].append(TACHI); write(p, u)
    uniform = read(GAME / 'uniforms/weapon.uniforms')
    uniform['weapon_tags'].append(recipe['main_weapon_uniform']['append_weapon_tag'])
    write(out / 'uniforms/weapon.uniforms', uniform)
    loc = read(out / 'localized_text/en.localized_text')
    loc.update(recipe['localization'])
    loc.update({TACHI + '_name': 'MCRN Corvette-class', TACHI + '_description': 'Fast-attack torpedo frigate. Six PDCs and twin light torpedo launchers. 55 fleet supply.',
                'trader_light_frigate_name': 'Morrigan-class patrol frigate',
                'trader_light_frigate_name.garrison': 'Morrigan-class garrison frigate',
                'trader_light_frigate_description': 'Fast Martian starter frigate. Two PDCs and two bow tubes; fires one light torpedo every 10 seconds. 25 fleet supply.'})
    write(out / 'localized_text/en.localized_text', loc)
    shield_report = remove_shields(out, GAME)
    write(AUDIT / 'shield-policy.json', shield_report)
    manifests(out, GAME)
    info = read(out / '.mod_meta_data')
    info.update(display_name='The Expanse — 0.11 MARTIAN FLEET', display_version='0.11.0',
                short_description='Morrigan starter, restored Donnager detail, shieldless TEC hulls and fleet supply pass.',
                long_description='Load alone. Includes prior ships, music and voices. Adds Morrigan, separate MCRN Corvette, broader boarding and deployment fixes. New update runtime tests remain pending.')
    info['logos'] = dui['logos']
    write(out / '.mod_meta_data', info)
    (out / 'ASSET-SOURCES.md').write_text((ROOT / 'ASSET-SOURCES.md').read_text())
    return [BASE, A, *[Path(x['game_directory']) for x in [don, dui, mor, mui]]]


def main(args):
    from update11_validate import validate, preservation
    preservation()
    out = ROOT / 'build/experiments' / ID
    if args.validate_only or args.package_existing:
        deps = [BASE, A, *[Path(x['game_directory']) for x in inputs()[1:]]]
    else:
        deps = build(out)
    report = validate(out)
    write(AUDIT / 'package-validation.json', report)
    if not args.validate_only:
        require(not out.with_suffix('.zip').exists(), 'Refusing an existing ZIP')
        with zipfile.ZipFile(out.with_suffix('.zip'), 'w', zipfile.ZIP_DEFLATED) as z:
            for p in sorted(out.rglob('*')):
                if p.is_file():
                    zi = zipfile.ZipInfo(p.relative_to(out).as_posix(), (2026, 9, 13, 0, 0, 0))
                    zi.compress_type = zipfile.ZIP_DEFLATED
                    zi.external_attr = 0o100644 << 16
                    z.writestr(zi, p.read_bytes())
    summary = {'mod_id': ID, **verify_zip(out.with_suffix('.zip'), out), 'installed': False, 'runtime': 'NOT RUN'}
    write(AUDIT / 'package-summary.json', summary)
    write(out.with_suffix('.dependencies.json'), list(map(str, deps)))
    write(out.with_suffix('.provenance.json'), provenance(out.with_suffix('.zip'), ROOT, deps))
    print(json.dumps(summary, indent=2))


if __name__ == '__main__':
    p = argparse.ArgumentParser(description=__doc__)
    g = p.add_mutually_exclusive_group()
    g.add_argument('--validate-only', action='store_true')
    g.add_argument('--package-existing', action='store_true')
    main(p.parse_args())
