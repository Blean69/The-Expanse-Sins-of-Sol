"""Prepare private 0.3 flight/effect candidates from installed, pinned evidence.

Writes only build/flight03-c and audit/flight03-c in this checkout. Shared unit /
skin files remain the integrator's ownership. Particle effects have no installed
schema: only observed-field structural/reference checks are claimed for them.
"""
from pathlib import Path
import argparse
import copy
import hashlib
import json
import math
import sys
import numpy as np
import jsonschema
from common import read_mesh

PIN = '8e061033afe53b1393eaefd56617a3fd041eeb5f'


def read(path):
    return json.loads(Path(path).read_text(encoding='utf-8-sig'))


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def write(path, data):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2) + '\n')


def strings(value, pointer=''):
    if isinstance(value, dict):
        for key, item in value.items():
            yield from strings(item, pointer + '/' + key)
    elif isinstance(value, list):
        for index, item in enumerate(value):
            yield from strings(item, pointer + '/' + str(index))
    elif isinstance(value, str):
        yield pointer, value


def changed_paths(a, b, pointer=''):
    if isinstance(a, dict) and isinstance(b, dict):
        for key in sorted(a.keys() | b.keys()):
            if key not in a or key not in b:
                yield pointer + '/' + key
            else:
                yield from changed_paths(a[key], b[key], pointer + '/' + key)
    elif isinstance(a, list) and isinstance(b, list) and len(a) == len(b):
        for i, (v, w) in enumerate(zip(a, b)):
            yield from changed_paths(v, w, pointer + '/' + str(i))
    elif a != b:
        yield pointer


def check_structure(candidate, installed):
    """Allow deletion of external_color, numeric changes, blue gradient ID only.

    No invented particle fields, emitter topology or timing is introduced.
    """
    def walk(value, template, pointer=''):
        if isinstance(value, dict):
            assert isinstance(template, dict)
            assert set(value) <= set(template), f'Unknown effect keys at {pointer}: {set(value)-set(template)}'
            for key, item in value.items():
                walk(item, template[key], pointer + '/' + key)
        elif isinstance(value, list):
            assert isinstance(template, list) and len(value) == len(template), pointer
            for i, (a, b) in enumerate(zip(value, template)):
                walk(a, b, pointer + '/' + str(i))
        elif isinstance(value, (int, float)) and not isinstance(value, bool):
            assert isinstance(template, (int, float)) and math.isfinite(value), pointer
        else:
            assert type(value) is type(template), pointer
    walk(candidate, installed)
    node_ids = {n['id'] for n in candidate['nodes']}
    emitter_ids = {e['id'] for e in candidate['emitters']}
    modifier_ids = {m['id'] for m in candidate['modifiers']}
    assert len(node_ids) == len(candidate['nodes'])
    assert len(emitter_ids) == len(candidate['emitters'])
    assert len(modifier_ids) == len(candidate['modifiers'])
    for attachment in candidate['emitter_to_node_attachments']:
        assert attachment['attacher_id'] in emitter_ids and attachment['attachee_id'] in node_ids
    for attachment in candidate['modifier_to_emitter_attachments']:
        assert attachment['attacher_id'] in modifier_ids and attachment['attachee_id'] in emitter_ids


def scale_effect(original, width_scalar, length_scalar, *, blue=False, nozzle=None):
    effect = copy.deepcopy(original)
    for node in effect['nodes']:
        for axis, scalar in [('x', width_scalar), ('y', width_scalar), ('z', length_scalar)]:
            node[axis] = [x * scalar for x in node[axis]]
        if nozzle:
            # Verified imported nozzle is yaw180 about Y: R=diag(-1,1,-1).
            for i, axis in enumerate(('x', 'y', 'z')):
                node[axis] = sorted(nozzle['position'][i] + v * (-1 if axis in ('x', 'z') else 1) for v in node[axis])
            node['yaw'] = [angle + math.pi for angle in node['yaw']]
    for emitter in effect['emitters']:
        particle = emitter['particle']
        if blue:
            particle.pop('external_color', None)
        billboard = particle.get('billboard', {})
        if 'width' in billboard:
            billboard['width'] = [x * width_scalar for x in billboard['width']]
        if 'height' in billboard:
            billboard['height'] = [x * length_scalar for x in billboard['height']]
        if blue and 'gradient_texture' in billboard:
            billboard['gradient_texture'] = 'advent_light'
        if 'forward_velocity' in emitter:
            emitter['forward_velocity'] = [x * length_scalar for x in emitter['forward_velocity']]
        if 'camera_offset' in particle:
            particle['camera_offset'] = [x * width_scalar for x in particle['camera_offset']]
        light = particle.get('light', {})
        if 'surface_radius' in light:
            light['surface_radius'] *= width_scalar
    for modifier in effect['modifiers']:
        for key, scalar in [('width_change_rate', width_scalar), ('height_change_rate', length_scalar)]:
            if key in modifier:
                modifier[key] = [x * scalar for x in modifier[key]]
    effect['max_effect_radius_scalar'] *= max(width_scalar, length_scalar)
    check_structure(effect, original)
    return effect


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--main-root', type=Path, required=True)
    parser.add_argument('--game', type=Path, required=True)
    parser.add_argument('--sdk', type=Path, required=True)
    args = parser.parse_args()
    root = Path(__file__).resolve().parents[1]
    out, audit = root / 'build/flight03-c', root / 'audit/flight03-c'
    hashes = {}
    def load(path):
        path = Path(path)
        if not path.is_file():
            raise FileNotFoundError(f'Missing required local dependency: {path}')
        hashes[str(path)] = sha(path)
        return read(path)
    pinned = load(args.main_root / 'audit/schema-comparison.json')
    assert pinned['official_commit'] == PIN
    schemas = {}
    for schema in ('unit-schema.json', 'unit-skin-schema.json'):
        path = args.sdk / 'json_schemas' / schema
        schemas[schema] = load(path)
        blob = hashlib.sha1(b'blob ' + str(path.stat().st_size).encode() + b'\0' + path.read_bytes()).hexdigest()
        assert blob == next(x['official_git_blob'] for x in pinned['files'] if x['path'] == 'json_schemas/' + schema), f'Schema pin changed: {schema}'
    assert not list((args.sdk / 'json_schemas').glob('*particle*')), 'A particle schema appeared: inspect before proceeding'
    unit = load(args.game / 'entities/trader_light_frigate.unit')
    shuriken = load(args.game / 'entities/trader_missile_corvette.unit')
    donor = load(args.game / 'entities/advent_gunship_corvette.unit')
    skin = load(args.game / 'entities/trader_light_frigate.unit_skin')
    current_skin_file = args.main_root / 'build/experiments/expanse_corvette_polish/entities/trader_light_frigate.unit_skin'
    current_skin = load(current_skin_file)
    current_mesh = args.main_root / 'build/experiments/expanse_corvette_polish/meshes' / (current_skin['skin_stages'][0]['unit_mesh']['mesh'] + '.mesh')
    hashes[str(current_mesh)] = sha(current_mesh)
    mesh = read_mesh(current_mesh)
    nozzle = next(p for p in mesh['meshpoints'] if p['name'] == 'exhaust.0')
    assert np.allclose(np.asarray(nozzle['rotation']).reshape(3, 3), np.diag([-1, 1, -1])), 'Nozzle rotation differs; cannot use current baked transform recipe'
    ordinary_file = args.game / 'effects/exhaust_tech_medium_01.particle_effect'
    ordinary = load(ordinary_file)
    blue_donor = load(args.game / 'effects/advent_medium_missile_exhaust.particle_effect')
    assert any(e['particle'].get('billboard', {}).get('gradient_texture') == 'advent_light' for e in blue_donor['emitters'])
    no_effect = load(args.game / 'effects/Buff_FighterBlinkActivate.particle_effect')
    assert no_effect['emitters'] == [], 'Installed empty-effect example changed'
    game_index = {p.relative_to(args.game).as_posix().lower(): p for p in args.game.rglob('*') if p.is_file()}
    effect_data = {
        'mcrn03_corvette_phase_plume': scale_effect(ordinary, 1.25, 4, blue=True, nozzle=nozzle),
        'mcrn03_hero_idle_plume': scale_effect(ordinary, 1.5, 1.5, blue=True),
        'mcrn03_hero_phase_plume': scale_effect(ordinary, 1.5, 4, blue=True, nozzle=nozzle),
    }
    effect_checks = []
    references = []
    for name, effect in effect_data.items():
        path = out / 'generated/effects' / (name + '.particle_effect')
        write(path, effect)
        for pointer, value in strings(effect):
            key = pointer.rsplit('/', 1)[-1]
            if 'texture' not in key or key.startswith('texture_animation_'):
                continue
            relative = ('texture_animations/' + value + '.texture_animation') if key == 'texture_animation' else ('textures/' + value + '.dds')
            resolved = game_index.get(relative.lower())
            if resolved is None:
                raise ValueError(f'Unresolved effect texture {name}{pointer}: {value}')
            hashes[str(resolved)] = sha(resolved)
            references.append({'source': str(path), 'pointer': pointer, 'reference': value, 'installed_target': str(resolved), 'sha256': hashes[str(resolved)]})
        effect_checks.append({'file': str(path), 'sha256': sha(path), 'schema': 'NOT AVAILABLE in pinned SDK; no schema PASS claimed', 'observed_structure_and_attachment_references': 'PASS', 'changed_pointers': list(changed_paths(ordinary, effect)), 'particle_emitter_count': len(effect['emitters'])})
    patched_unit = copy.deepcopy(unit)
    patched_unit['attack']['attack_pattern'] = copy.deepcopy(donor['attack']['attack_pattern'])
    assert patched_unit['physics'] == unit['physics'] and patched_unit['move'] == unit['move']
    restored = copy.deepcopy(patched_unit); restored['attack']['attack_pattern'] = unit['attack']['attack_pattern']; assert restored == unit
    jsonschema.Draft7Validator(schemas['unit-schema.json']).validate(patched_unit)
    keys = ['travel_effect', 'travel_effect_between_stars', 'travel_effect_destabilized']
    role_patches = {}
    schema_checks = []
    for role in ('corvette', 'hero'):
        changes = [{'pointer': '/skin_stages/0/effects/hyperspace_effects/' + key, 'value': f'mcrn03_{role}_phase_plume'} for key in keys]
        if role == 'hero':
            changes.append({'pointer': '/skin_stages/0/effects/exhaust_effects/particle_effects/0/particle_effect', 'value': 'mcrn03_hero_idle_plume'})
        patched_skin = copy.deepcopy(current_skin)
        for change in changes:
            obj = patched_skin
            parts = change['pointer'].strip('/').split('/')
            for p in parts[:-1]:
                obj = obj[int(p)] if isinstance(obj, list) else obj[p]
            change['old_in_corvette_02_skin'] = obj[parts[-1]]
            obj[parts[-1]] = change['value']
        jsonschema.Draft7Validator(schemas['unit-skin-schema.json']).validate(patched_skin)
        schema_checks.append({'role': role, 'unit_skin_schema': 'PASS'})
        role_patches[role] = changes
    spec = {
        'format': 'Integrator metadata, not a game definition',
        'unit_patches': [{'pointer': '/attack/attack_pattern', 'old_cobalt': unit['attack']['attack_pattern'], 'value': donor['attack']['attack_pattern']}],
        'skin_patches_by_role': role_patches,
        'copy_generated_subdirectories': ['effects'],
        'entity_manifests_required': [],
        'unit_physics_and_move_unchanged': True,
        'torpedo_orbit_alignment_note': 'Generic installed circle_strafe selected; Shuriken yaw90 broadside alignment omitted because forward torpedo arcs may not bear. Actual orbit distance and firing behavior remain runtime-dependent.',
        'phase_hook': 'Three native travel_effect keys only; charge/exit effects and sounds remain existing. Normal corvette exhaust unchanged. Hero gets private1.5x blue normal plume.',
        'phase_dimensions': {'corvette': {'length_vs_base': 4.0, 'width_vs_base': 1.25}, 'hero': {'length_vs_base': 4.0, 'width_vs_base': 1.5}, 'hero_normal': {'length_vs_base': 1.5, 'width_vs_base': 1.5}},
        'nozzle_evidence': {'mesh': str(current_mesh), 'mesh_sha256': hashes[str(current_mesh)], 'meshpoint': nozzle, 'phase_effect_transform': 'Baked unit-space translation and yaw180 into every source node; travel hooks expose no mesh_point field.'},
        'runtime_uncertainties': ['Hyperspace effect origin may differ from unit origin; nozzle position/direction must be observed before claiming alignment.', 'Native normal exhaust may coexist with phase-only plume; do not claim an exclusive exhaust replacement until observed.', 'Source external_color was removed on private blue effects; verify that ordinary/resting throttle and hero emissive appearance remain desired.', 'Travel tunnel removal applies to three skin travel assets only; charging/exit visuals and any global camera overlay remain.', 'circle_strafe with retained Cobalt turning/speed limits may produce a wide/slow orbit; do not claim Shuriken agility.', 'Minimum/maximum actual orbit range follows engine weapon logic; no explicit orbit radius field was invented.'],
        'runtime': 'NOT RUN'}
    write(out / 'integration-spec.json', spec)
    schema_defs = schemas['unit-skin-schema.json']['$defs']
    report = {'status': 'PASS (offline observed-structure/schema/reference checks only)', 'pinned_schema_revision': PIN, 'unit_schema': 'PASS', 'unit_exact_change': '/attack/attack_pattern only', 'unit_physics_and_move_unchanged': True, 'skin_schema_checks': schema_checks, 'particle_effect_checks': effect_checks, 'source_dependency_sha256': hashes, 'reference_edges': references, 'state_hook_evidence': {'hyperspace_effects': schema_defs['unit_hyperspace_effects_definition'], 'flair_effects': schema_defs['unit_flair_effect_definition'], 'exhaust_effects': schema_defs['unit_exhaust_particle_effect_definition']}, 'installed_comparison': {'cobalt': unit['attack'], 'tec_missile_corvette': shuriken['attack'], 'generic_circle_strafe_donor': donor['attack']}, 'generated_file_sha256': {str(p.relative_to(out)): sha(p) for p in (out / 'generated').rglob('*') if p.is_file()}, 'runtime': 'NOT RUN'}
    installed_lock = load(args.main_root / 'audit/installed-file-hashes.json')
    locked_count = 0
    for path, expected in list(hashes.items()):
        assert sha(path) == expected, f'Read-only dependency changed during work: {path}'
        source_path = Path(path)
        if source_path.is_relative_to(args.game):
            relative = source_path.relative_to(args.game).as_posix()
            if relative in installed_lock:
                assert expected == installed_lock[relative]['sha256'], f'Installed reference drift: {relative}'
                locked_count += 1
    report['previously_pinned_game_references_checked'] = locked_count
    write(out / 'offline-validation.json', report)
    write(audit / 'offline-validation.json', report)
    write(audit / 'integration-spec.json', spec)
    print(json.dumps({'status': 'PASS', 'effects': len(effect_data), 'unit_schema': 'PASS', 'skin_schemas': len(schema_checks), 'particle_schema': 'NOT AVAILABLE', 'references': len(references), 'runtime': 'NOT RUN'}))


if __name__ == '__main__':
    main()
