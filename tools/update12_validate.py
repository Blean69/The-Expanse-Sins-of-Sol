"""Scoped offline gates for the capital fleet update; no game launch required."""
import copy
from pathlib import Path
import numpy as np
from build_update12 import ROOT, GAME, SDK, BASE, AUDIT, ID, SCOUT, PLAYERS, inputs, reviewed
from update12_behavior import CONFIG
from update11_validate import schema_check
from validate_experiments import read, require, file_hashes, sha256, compare_tree, verify_pins, strings
from build_combat04 import binary_geometry
from build_combat03 import check_actions
from amun06_validate_package import AmunResolver, check_action_values
from flight03_effects import changed_paths
from build_hero03 import ability_positions


def preservation():
    snap = read(AUDIT / 'checkpoint.json')
    trees = [compare_tree(x) for x in snap['trees']]
    for path, digest in {**snap['zips'], **snap['originals']}.items():
        require(sha256(path) == digest, 'Frozen original/package changed: ' + path)
    require(sha256(snap['enabled_path']) == snap['enabled_sha256'], 'Enabled settings changed')
    return {'trees': trees, 'old_zips': len(snap['zips']), 'original_packages': snap['originals'], 'pins': verify_pins(ROOT, GAME, SDK)}


def scalars(out, name):
    d = read(out / 'entities' / (name + '.action_data_source'))
    return {x['action_value_id']: x['action_value'].get('values') for x in d.get('action_values', [])}


def objects(d):
    if isinstance(d, dict):
        yield d
        for v in d.values(): yield from objects(v)
    elif isinstance(d, list):
        for v in d: yield from objects(v)


def validate(out):
    reviewed(); parts = inputs(); before = file_hashes(BASE); after = file_hashes(out)
    require(not set(before) - set(after), 'Earlier package files removed')
    allowed = {'.mod_meta_data', 'ASSET-SOURCES.md', 'localized_text/en.localized_text', 'uniforms/unit_tag.uniforms',
               'entities/' + SCOUT + '.unit', 'entities/' + SCOUT + '.unit_skin',
               'entities/expanse06_amun_boarding.action_data_source', 'entities/expanse10_donnager_marines.action_data_source'}
    allowed |= {'entities/' + p + '.player' for p in PLAYERS}
    allowed |= {'entities/' + e + '.entity_manifest' for e in ['unit', 'unit_skin', 'weapon', 'ability', 'buff', 'action_data_source']}
    for name, digest in before.items():
        require(after[name] == digest or name in allowed, 'Unintended baseline change: ' + name)
    changed = {n: list(changed_paths(read(BASE / n), read(out / n))) for n in before if before[n] != after[n] and n.endswith(('.unit', '.unit_skin', '.player', '.action_data_source', '.uniforms'))}
    schemas = []
    for p in sorted(out.rglob('*')):
        if p.is_file() and (p.relative_to(out).as_posix() not in before or before[p.relative_to(out).as_posix()] != after[p.relative_to(out).as_posix()]):
            original = GAME / 'entities/trader_battle_capital_ship.unit' if p.suffix == '.unit' and p.stem in ['expanse12_' + k for k in CONFIG] else None
            r = schema_check(p, original)
            if r: schemas.append(r)
    for asset in parts.values():
        for kind in ['metadata', 'ui']:
            for name, digest in file_hashes(asset[kind]['game_directory']).items():
                require(after[name] == digest, 'Reviewed generated asset changed: ' + name)
    resolver = AmunResolver(out, GAME); actions = {}; frames = []; meshes = []; budgets = {}
    for kind, obj in parts.items():
        ident = SCOUT if kind == 'sunflare' else 'expanse12_' + kind
        meta = obj['metadata']; u = resolver.unit(ident, 'capital/scout integrated root')
        actions[ident] = {'graph': check_actions(out, resolver, ident), 'typed': check_action_values(out, GAME, resolver, u)}
        require(len(u['abilities']) == 1, 'Coexisting abilities split into alternative sets')
        require('expanse11_no_shields' in u['abilities'][0]['abilities'], 'Shield guard missing')
        for h in u['health']['levels']:
            require(h.get('max_shield_points', 0) == 0 and h.get('shield_point_restore_rate', 0) == 0, 'New ship gained shields')
        hull = resolver.mesh(meta['hull_mesh'], ident); points = {p['name']: p for p in hull['meshpoints']}
        for nozzle in meta['equipment']['exhausts']:
            require(any(np.allclose(p['position'], nozzle['position'], atol=3e-5) for n, p in points.items() if n.startswith('exhaust.')), 'Missing measured exhaust point')
        if kind != 'sunflare':
            cfg = CONFIG[kind]; mounts = u['weapons']['weapons']
            require(mounts == [r['mount'] for r in meta['rigs']], 'Mount integration changed worker geometry')
            require('weapon.boarding.0' in points, 'Missing boarding visual origin')
            require(len({m['weapon'] for m in mounts}) == len(mounts), 'Physical gun budgets conflated')
            require(u['build']['supply_cost'] == cfg['supply'] and u['build']['build_kind'] == 'capital_ship' and 'titan' not in u['tags'], 'Incorrect capital supply/class')
            require(u['physics']['max_linear_speed'] == cfg['speed'], 'Capital speed drift')
            require(not set(u['ai']['attack_target_type_groups']) & set(u['ai']['attack_target_type_groups_to_ignore']), 'Attack/ignore overlap')
            pdc_damage = 0.
            for rig in meta['rigs']:
                m = rig['mount']; point = points[m['mesh_point']]; rot = np.array(point['rotation']).reshape(3, 3)
                require(np.allclose(point['position'], m['weapon_position'], atol=3e-5) and np.allclose(rot[1], m['up'], atol=3e-5) and np.allclose(rot[2], m['forward'], atol=3e-5), 'Compiled local frame mismatch')
                w = read(out / 'entities' / (m['weapon'] + '.weapon'))
                require(w['turret'] == rig['turret_override'], 'Turret transform differs')
                if rig['kind'] == 'pdc':
                    require(w['damage'] == 14. and w['cooldown_duration'] == .25 and w['penetration'] == 0 and w['range'] == 4500., 'PDC budget drift')
                    pdc_damage += w['damage'] / w['cooldown_duration']
                else:
                    require(w['damage'] == 4000. and w['penetration'] == 1250. and w['cooldown_duration'] == 15., 'Rail budget drift')
                frames.append(m['weapon'])
            expected_pdcs = 12 if kind == 'scirocco' else 9
            require(sum(r['kind'] == 'pdc' for r in meta['rigs']) == expected_pdcs, 'Unexpected PDC count')
            budgets[kind] = {'physical_pdc_count': expected_pdcs, 'per_pdc_raw_dps': 56., 'aggregate_raw_dps_full_coverage': pdc_damage}
            for label in (['light', 'heavy'] if kind == 'scirocco' else ['light']):
                name = 'expanse12_' + kind + '_' + label + '_magazine'; a = read(out / 'entities' / (name + '.ability')); b = read(out / 'entities' / (name + '.buff')); v = scalars(out, name)
                require(a['ability_positions'] == ability_positions(meta['equipment'][label + '_torpedo_ports']), 'Launch point mismatch')
                count = 1 if label == 'heavy' else cfg['light_salvo']; capacity = 5 if label == 'heavy' else cfg['light_capacity']
                require(sum(x.get('operator_type') == 'create_torpedo' for x in objects(b)) == count, 'Wrong physical salvo creation count')
                require(v['magazine_pair_count_value'] == [count] and v['magazine_capacity_value'] == [capacity] and capacity % count == 0, 'Ammo decrement/capacity mismatch')
                require(v['donnager_reactor_extra_progress_tick'] == [.25 * (cfg['reload_factor'] - 1)], 'Reactor magazine progress mismatch')
            blast = scalars(out, 'expanse12_' + kind + '_reactor_breach')
            require(blast['self_destruct_damage_value'] == [1500.] and blast['self_destruct_radius_value'] == [2500.], 'Capital inherited titan blast budget')
        for p in Path(meta['game_directory']).glob('meshes/*.mesh'):
            if p.name not in {x['mesh'] for x in meshes}: meshes.append(binary_geometry(out / 'meshes' / p.name))
        skin = resolver.skin(ident, 'UI references')
        for stage in skin['skin_stages']:
            for branch in [stage['gui'], stage['main_view_icon']]:
                for key, val in branch.items():
                    if key in ['hud_icon', 'hud_monochrome_icon', 'hud_picture', 'tooltip_picture', 'icon', 'selected_icon', 'sub_selected_icon']:
                        resolver.resolve('brushes/' + val + '.brush', ident)

    sun = read(out / 'entities' / (SCOUT + '.unit')); speed = read(GAME / 'entities' / (SCOUT + '.unit'))['physics']['max_linear_speed']
    require(sun['physics']['max_linear_speed'] == speed * 2. == 3000., 'Sunflare normal speed is not 2x native scout')
    require(sun['hyperspace']['charge_time'] == 2 and sun['hyperspace']['charge_time_variance'] == 0, 'Sunflare charge exceeds two seconds')
    require(not sun.get('weapons'), 'Racing scout gained weapons')
    for h in sun['health']['levels']: require(h['max_hull_points'] == 100 and h['max_armor_points'] == 0 and h['armor_strength'] == 0, 'Scout survival budget wrong')
    name = 'expanse12_sunflare_burn'; b = read(out / 'entities' / (name + '.buff')); v = scalars(out, name); t = b['time_actions'][0]
    require(b['make_dead_on_all_finite_time_actions_done'] is True and not b.get('active_duration'), 'Final burn damage tick could race duration expiration')
    require(t['first_action_delay_time_value'] == 'fixed_one' and t['execution_interval_value'] == 'fixed_one' and v[t['execution_interval_count_value']] == [9.], 'Burn needs nine ticks at1..9s')
    damage = [x for x in objects(b) if x.get('operator_type') == 'apply_damage']; require(len(damage) == 1 and damage[0]['damage_affect_type'] == 'hull_only' and v[damage[0]['damage_value']] == [10.], 'Burn damage is not ten hull per tick')
    require(v['speed_scalar'] == [3.] and 'disable_can_passively_regenerate_hull' in b['unit_mutations'], 'Burn must multiply speed by4 without passive healing')
    require(100 - v['self_damage'][0] * v['ticks'][0] == 10., 'Unmodified full-health burn arithmetic changed')
    require(read(out / 'entities/expanse12_pella.unit')['tags'] == ['capital_ship', 'expanse12_pella'], 'Unique Pella unit tag missing')
    tags = copy.deepcopy(read(BASE / 'uniforms/unit_tag.uniforms'))
    tags['unit_tags'].append({'name': 'expanse12_pella', 'localized_name': 'expanse12_pella.name'})
    require(read(out / 'uniforms/unit_tag.uniforms') == tags, 'Pella tag registration differs')
    boarding_names = ['expanse06_amun_boarding', 'expanse10_donnager_marines'] + ['expanse12_' + k + '_marines' for k in CONFIG]
    for name in boarding_names:
        source = name if name.startswith(('expanse06_', 'expanse10_')) else 'expanse10_donnager_marines'
        original_filters = copy.deepcopy(read(BASE / 'entities' / (source + '.action_data_source'))['target_filters'])
        for row in original_filters:
            if row['target_filter_id'] == 'boarding_capital_target':
                row['target_filter']['constraints'].append({'constraint_type': 'composite_not', 'constraint': {'constraint_type': 'has_definition', 'unit_definition': 'expanse12_pella'}})
        actual_filters = read(out / 'entities' / (name + '.action_data_source'))['target_filters']
        require(actual_filters == original_filters, 'Boarding eligibility/hero exclusion differs: ' + name)
    for player in PLAYERS:
        p = read(out / 'entities' / (player + '.player')); old = read(BASE / 'entities' / (player + '.player')); expected = copy.deepcopy(old)
        expected['buildable_units'] += ['expanse12_' + k for k in CONFIG]; expected['unit_limits']['global'].append({'tag': 'expanse12_pella', 'unit_limit': 1})
        require(p == expected, 'Player changes exceed three capital registrations/hero limit')
        require({'tag': 'titan', 'unit_limit': 1} in p['unit_limits']['global'], 'Shared titan limit changed')
    for p in (out / 'entities').glob('*.entity_manifest'):
        require(read(p)['ids'] == sorted(q.stem for q in (out / 'entities').glob('*.' + p.stem) if not (GAME / 'entities' / q.name).exists()), 'Manifest mismatch')
    for p in (out / 'effects').glob('expanse12*.particle_effect'):
        e = read(p); ids = {k: {x['id'] for x in e[k]} for k in ['nodes', 'emitters', 'modifiers']}
        for k in ids: require(len(ids[k]) == len(e[k]), 'Duplicate particle ID')
        for row in e['emitter_to_node_attachments']: require(row['attacher_id'] in ids['emitters'] and row['attachee_id'] in ids['nodes'], 'Bad effect node')
        for row in e['modifier_to_emitter_attachments']: require(row['attacher_id'] in ids['modifiers'] and row['attachee_id'] in ids['emitters'], 'Bad effect modifier')
        for ptr, val in strings(e):
            if ptr[-1].endswith('texture') or ptr[-1] in ['texture_0', 'texture_1']: resolver.resolve('textures/' + val + '.dds', p)
            elif ptr[-1] == 'mesh': resolver.mesh(val, p)
    return {'status': 'PASS OFFLINE ONLY', 'runtime': 'NOT RUN', 'schemas': schemas, 'meshes': meshes, 'checked_mounts': frames,
            'reference_edges': resolver.edges, 'actions': actions, 'pdc_budgets': budgets, 'changes_to_previous_package': changed,
            'sunflare_specification': {'normal_speed': 3000, 'burn_speed': 12000, 'damage_ticks_seconds': list(range(1, 10)), 'raw_hull_damage': 90, 'normal_hull_after_burn': 10, 'runtime': 'NOT RUN'},
            'preservation': preservation()}
