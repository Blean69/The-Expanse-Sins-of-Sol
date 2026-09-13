"""Focused integration gates for 0.11; offline evidence is not a runtime pass."""
import copy
from pathlib import Path
import numpy as np
import jsonschema
from build_update11 import (ROOT, GAME, SDK, BASE, AUDIT, A, DON, TACHI, MORRIGAN,
                            HERO, AMUN, PLAYERS, SUPPLY, inputs, reviewed_inputs)
from build_hero03 import ability_positions
from build_combat03 import check_actions
from build_combat04 import binary_geometry
from amun06_validate_package import AmunResolver, check_action_values
from flight03_effects import changed_paths, check_structure
from validate_experiments import (read, require, sha256, compare_tree, verify_pins,
                                 file_hashes, strings)


def preservation():
    snap = read(AUDIT / 'checkpoint.json')
    rows = [compare_tree(x) for x in snap['trees']]
    for name, digest in snap['zips'].items():
        require(sha256(name) == digest, 'Earlier ZIP changed: ' + name)
    enabled = snap['enabled']
    if isinstance(enabled, dict) and 'path' in enabled:
        require(sha256(enabled['path']) == enabled['sha256'], 'Enabled mods changed')
    else:
        settings = GAME.parents[1] / 'compatdata/1575940/pfx/drive_c/users/steamuser/AppData/Local/sins2/settings/.enabled_mods'
        require(read(settings) == enabled, 'Enabled mods changed')
    return {'trees': rows, 'prior_zip_hashes': len(snap['zips']),
            'pins': verify_pins(ROOT, GAME, SDK)}


def schema_check(path, original_override=None):
    types = {'.unit': 'unit', '.unit_skin': 'unit-skin', '.weapon': 'weapon',
             '.ability': 'ability', '.buff': 'buff', '.action_data_source': 'action-data-source',
             '.player': 'player', '.unit_item': 'unit-item', '.research_subject': 'research-subject', '.brush': 'brush'}
    if path.suffix not in types:
        return None
    schema = read(SDK / 'json_schemas' / (types[path.suffix] + '-schema.json'))
    data = read(path)
    # The pinned schemas predate installed corruption and DLC extensions.
    # Any schema-unknown field is permitted ONLY when copied exactly from an
    # installed/accepted source at that same path; it is recorded, not validated.
    original = GAME / 'entities' / path.name
    if not original.exists():
        original = BASE / 'entities' / path.name
    if path.stem == TACHI:
        original = BASE / 'entities' / (MORRIGAN + path.suffix)
    if original_override is not None:
        original = Path(original_override)
        require(original.is_file(), 'Missing explicit schema source: ' + str(original))
    source = read(original) if original.is_file() else {}
    extensions = []
    for _ in range(30):
        errors = list(jsonschema.Draft202012Validator(schema).iter_errors(data))
        if not errors:
            break
        progress = False
        for e in errors:
            if e.validator == 'enum':
                template = source
                for part in e.path:
                    template = template[part]
                require(template == e.instance, 'Unknown enum changed from installed source: ' + str(path))
                # The validator exposes the resolved local $ref schema here;
                # absolute_schema_path may elide that reference traversal.
                target_schema = e.schema
                require(isinstance(target_schema.get('enum'), list), 'Cannot scope installed enum extension')
                if e.instance not in target_schema['enum']:
                    target_schema['enum'].append(e.instance)
                    extensions.append({'field': '/' + '/'.join(map(str, e.path)), 'installed_enum': e.instance,
                                       'source': str(original), 'source_sha256': sha256(original)})
                    progress = True
                continue
            if e.validator not in ['unevaluatedProperties', 'additionalProperties'] or not isinstance(e.instance, dict):
                continue
            # Only a concrete properties map is used; do not guess union keys.
            properties = e.schema.get('properties', {})
            if not properties:
                continue
            target, template = data, source
            for part in e.path:
                target = target[part]
                template = template[part]
            unknown = set(target) - set(properties)
            for k in sorted(unknown):
                require(k in template and target[k] == template[k], 'Changed/unknown extension ' + str(path) + ':' + k)
                extensions.append({'field': '/' + '/'.join(map(str, [*e.path, k])), 'source': str(original), 'source_sha256': sha256(original)})
                del target[k]
                progress = True
        if not progress:
            raise ValueError(str(path) + ': ' + errors[0].message + ' at ' + str(list(errors[0].path)))
    jsonschema.Draft7Validator(schema).validate(data)
    jsonschema.Draft202012Validator(schema).validate(data)
    return {'file': path.name, 'status': 'PASS pinned known fields and closed keys', 'exact_source_extensions': extensions}


def validate(out):
    reviewed_inputs()
    recipe, don, dui, mor, mui = inputs()
    old, new = file_hashes(BASE), file_hashes(out)
    require(not set(old) - set(new), 'Accepted package content removed')
    deltas = {}
    for name in old:
        if new[name] != old[name]:
            p = out / name
            require(p.suffix not in ['.mesh', '.dds', '.png', '.ogg', '.sound'], 'Accepted binary/audio changed: ' + name)
            if p.suffix in ['.unit', '.unit_skin', '.weapon', '.ability', '.action_data_source', '.player', '.uniforms']:
                deltas[name] = list(changed_paths(read(BASE / name), read(p)))
            else:
                deltas[name] = ['content']
    # Focused regressions: accepted explosion, all audio/music, torpedo units
    # and magazines, and the balanced hero rail are byte-for-byte unchanged.
    protected = [n for n in old if n.startswith(('sounds/', 'music/')) or 'reactor_breach' in n
                 or n == 'entities/expanse03_hero_railgun.weapon'
                 or ('torpedo' in n and n.endswith('.unit'))
                 or ('magazine' in n and n.startswith('entities/'))]
    for n in protected:
        require(new[n] == old[n], 'Accepted combat/audio budget changed: ' + n)
    for n, allowed in recipe['allowed_existing_deltas'].items():
        require(set(deltas['entities/' + n]) <= set(allowed), 'Behavior change exceeds reviewed contract: ' + n)
    for d in [don, dui, mor, mui]:
        for n, h in file_hashes(d['game_directory']).items():
            require(new[n] == h, 'Worker generated asset drift: ' + n)

    schemas = []
    for p in sorted(out.rglob('*')):
        if p.is_file() and (p.relative_to(out).as_posix() not in old or new[p.relative_to(out).as_posix()] != old[p.relative_to(out).as_posix()]):
            r = schema_check(p)
            if r:
                schemas.append(r)
    uniform = read(out / 'uniforms/weapon.uniforms')
    expected = read(GAME / 'uniforms/weapon.uniforms')
    expected['weapon_tags'].append(recipe['main_weapon_uniform']['append_weapon_tag'])
    require(uniform == expected, 'Unexpected weapon uniform edits')
    jsonschema.Draft202012Validator(read(SDK / 'json_schemas/weapon-uniforms-schema.json')).validate(uniform)

    resolver = AmunResolver(out, GAME)
    actions = {}
    typed = {}
    for n in [MORRIGAN, TACHI, HERO, AMUN, DON]:
        u = resolver.unit(n, '0.11 integrated ship')
        ai = u.get('ai', {})
        require(not set(ai.get('attack_target_type_groups', [])) & set(ai.get('attack_target_type_groups_to_ignore', [])), 'Attack/ignored group overlap: ' + n)
        actions[n] = check_actions(out, resolver, n)
        typed[n] = check_action_values(out, GAME, resolver, u)
        if n in SUPPLY:
            require(u['build']['supply_cost'] == SUPPLY[n], 'Wrong fleet cost ' + n)
        require(len(u['abilities']) == 1, 'Coexisting ship abilities split into alternative sets')
    require(500 + 4 * 150 + 10 * 55 + 14 * 25 == 2000, 'Requested reference fleet no longer fits')
    for name in PLAYERS:
        u = read(out / 'entities' / (name + '.player'))
        require(u['buildable_units'].count(TACHI) == 1 and MORRIGAN in u['buildable_units'], 'Missing/duplicate starter or Tachi build option')
        require({'tag': 'titan', 'unit_limit': 1} in u['unit_limits']['global'], 'Shared titan construction cap changed')

    geometry = []
    for meta, ident in [(mor, MORRIGAN), (don, DON)]:
        hull = resolver.mesh(meta['hull_mesh'], ident)
        points = {p['name']: p for p in hull['meshpoints']}
        mounts = read(out / 'entities' / (ident + '.unit'))['weapons']['weapons']
        require(mounts == [r['mount'] for r in meta['rigs']], 'Integrated mounts differ from reviewed geometry')
        for rig in meta['rigs']:
            m = rig['mount']; p = points[m['mesh_point']]; rot = np.array(p['rotation']).reshape(3, 3)
            require(np.allclose(p['position'], m['weapon_position'], atol=2e-5) and np.allclose(rot[1], m['up'], atol=2e-5) and np.allclose(rot[2], m['forward'], atol=2e-5), 'Compiled mount basis mismatch')
            w = read(out / 'entities' / (m['weapon'] + '.weapon'))
            require(w['turret'] == rig['turret_override'], 'Rig contract mismatch')
        for p in Path(meta['game_directory']).glob('meshes/*.mesh'):
            geometry.append(binary_geometry(out / 'meshes' / p.name))
    m = read(out / 'entities/expanse11_morrigan_magazine.ability')
    require(m['ability_positions'] == ability_positions(mor['equipment']['light_torpedo_ports']), 'Morrigan torpedo tubes mismatch')
    require(len(read(out / 'entities' / (MORRIGAN + '.unit'))['weapons']['weapons']) == 2, 'Morrigan needs exactly two independent guns')
    for p in (out / 'entities').glob('*pdc_*.weapon'):
        d = read(p)
        require(d['range'] == (6000.0 if p.stem.startswith('expanse10_donnager_') else 3500.0), 'PDC coverage drift')
        if p.name in [q.name for q in (BASE / 'entities').glob('*.weapon')]:
            allowed = {'/range'} | ({'/turret/gimbal_mesh'} if 'donnager' in p.stem else set())
            require(set(changed_paths(read(BASE / 'entities' / p.name), d)) <= allowed, 'PDC damage/firing budget changed')
    voice = read(out / 'entities' / (MORRIGAN + '.unit_skin'))['skin_stages'][0]['sounds']['dialogue']
    require('expanse10_donnager_railguns' not in [v for _, v in strings(voice)] and 'expanse10_donnager_hammers' not in [v for _, v in strings(voice)], 'Railgun dialogue on Morrigan')
    dvoice = read(out / 'entities' / (DON + '.unit_skin'))['skin_stages'][0]['sounds']['dialogue']
    require(len(set(dvoice['selected']['neutral'])) == 3, 'Donnager selection variation missing')
    for p in (out / 'effects').glob('expanse11*.particle_effect'):
        original = BASE / 'effects/expanse10_donnager_idle_plume.particle_effect' if 'donnager' in p.name else GAME / 'effects/exhaust_tech_medium_01.particle_effect'
        # Donnager is a numeric-only scale of an existing topology.
        if 'donnager_idle' in p.name:
            check_structure(read(p), read(original))
        effect = read(p)
        ids = {k: {x['id'] for x in effect[k]} for k in ['nodes', 'emitters', 'modifiers']}
        for k in ids:
            require(len(ids[k]) == len(effect[k]), 'Duplicate effect IDs')
        for x in effect['emitter_to_node_attachments']:
            require(x['attacher_id'] in ids['emitters'] and x['attachee_id'] in ids['nodes'], 'Bad effect node reference')
        for x in effect['modifier_to_emitter_attachments']:
            require(x['attacher_id'] in ids['modifiers'] and x['attachee_id'] in ids['emitters'], 'Bad effect modifier reference')
        for ptr, v in strings(read(p)):
            if ptr[-1] == 'mesh':
                resolver.mesh(v, p)
            elif ptr[-1].endswith('texture') or ptr[-1] in ['texture_0', 'texture_1']:
                resolver.resolve('textures/' + v + '.dds', p)
    for p in (out / 'entities').glob('*.entity_manifest'):
        expected = sorted(q.stem for q in (out / 'entities').glob('*.' + p.stem) if not (GAME / 'entities' / q.name).exists())
        require(read(p)['ids'] == expected, 'Entity manifest mismatch ' + p.name)
    return {'status': 'PASS OFFLINE ONLY', 'runtime': 'NOT RUN', 'schemas': schemas,
            'geometry': geometry, 'action_checks': actions, 'typed_action_checks': typed,
            'reference_edges': resolver.edges, 'changed_existing_files': deltas,
            'protected_combat_audio_files': len(protected),
            'supply': {'implemented': SUPPLY, 'reserved_pella': 150, 'reference_total': 2000},
            'shield_policy': read(AUDIT / 'shield-policy.json'), 'preservation': preservation()}
