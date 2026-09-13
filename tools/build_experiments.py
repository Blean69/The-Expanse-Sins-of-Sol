"""Assemble only the two reviewed experiments; never install or build baselines.

Worker inputs are explicit, read-only paths. Existing output directories are
refused. Run from the main checkout after worker offline checks have passed.
"""
from pathlib import Path
import argparse, copy, json, shutil, zipfile
from validate_experiments import (check_frozen, validate_package, verify_zip,
                                  require, read, sha256, provenance)

ROOT = Path(__file__).resolve().parents[1]

def write(path, data):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2) + '\n')

def copy_file(source, target):
    if not source.is_file():
        raise FileNotFoundError(f'BLOCKED: missing ignored local dependency {source}')
    target.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(source, target)

def patch_pointer(data, pointer, value):
    keys = pointer.strip('/').split('/')
    cursor = data
    for key in keys[:-1]:
        cursor = cursor[int(key)] if isinstance(cursor, list) else cursor[key]
    require(keys[-1] in cursor, f'Patch must address an existing verified key: {pointer}')
    cursor[keys[-1]] = copy.deepcopy(value)

def stock(out, inputs, game):
    spec = read(inputs / 'integration-spec.json')
    validation = read(inputs / 'offline-validation.json')
    require(validation == read(ROOT / 'audit/workers/a/offline-validation.json') and validation['status'] == 'PASS', 'Worker A evidence drift or incomplete checks')
    for name, digest in validation['output_hashes'].items():
        require(sha256(inputs / 'entities' / name) == digest, f'Weapon input drift: {name}')
    require(spec['unit_overrides'] == {
        'entities/trader_antifighter_frigate.unit': [
            {'pointer': '/weapons/weapons/0/weapon', 'value': 'mcrn_exp_stock_dual_pdc'}],
        'entities/trader_torpedo_cruiser.unit': [
            {'pointer': '/weapons/weapons/0/weapon', 'value': 'mcrn_corvette_torpedo'},
            {'pointer': '/ai/attack_target_type_groups_matching_weapon', 'value': 'mcrn_corvette_torpedo'}]}, 'Unreviewed stock integration edits')
    # Definitions are checked again against installed/pinned data below.
    for relative, edits in spec['unit_overrides'].items():
        unit = read(game / relative)
        for edit in edits:
            patch_pointer(unit, edit['pointer'], edit['value'])
        write(out / relative, unit)
    for kind, ids in spec['additive_manifest_ids'].items():
        write(out / 'entities' / f'{kind}.entity_manifest', {'ids': ids})
        for ident in ids:
            copy_file(inputs / 'entities' / f'{ident}.{kind}', out / 'entities' / f'{ident}.{kind}')
    # The widened group list is the sole PDC definition change.
    weapon = read(out / 'entities/mcrn_exp_stock_dual_pdc.weapon')
    vanilla = read(game / 'entities/trader_antifighter_frigate_point_defense_autocannon.weapon')
    require(weapon['attack_target_type_groups'] == ['torpedo_strikecraft', 'corvette', 'light', 'flak'], 'Unexpected PDC groups')
    weapon['attack_target_type_groups'] = vanilla['attack_target_type_groups']
    require(weapon == vanilla, 'Unexpected stock PDC gameplay change')
    return [inputs / 'integration-spec.json', inputs / 'offline-validation.json', inputs / 'entities']

def tachi(out, worker, game):
    metadata_path = worker / 'audit/workers/b/mount-metadata.json'
    meta = read(metadata_path)
    shading = read(worker / 'audit/workers/b/compiler-geometry-check.json')
    require(shading.get('package_gate') == 'PASS', 'BLOCKED: rig shading-frame gate has not passed; candidate only')
    require(meta['compiled'] and meta['total_triangles'] == 14622, 'Incomplete rig compiler candidate')
    require(all(v == 'PASS' for k, v in meta['checks'].items() if k != 'runtime_rotation'), 'Rig offline check failed')
    unit = read(ROOT / 'build/expanse_corvette_visual/entities/trader_light_frigate.unit')
    original = copy.deepcopy(unit)
    unit['weapons']['weapons'].append(meta['mount'])
    restored = copy.deepcopy(unit); restored['weapons']['weapons'].pop()
    require(restored == original, 'Rig must add exactly one mount to frozen visual unit')
    skin = read(ROOT / 'build/expanse_corvette_visual/entities/trader_light_frigate.unit_skin')
    stage = skin['skin_stages'][0]
    stage['unit_mesh']['mesh'] = 'expanse_tachi_one_pdc_hull'
    stage['child_mesh_alias_bindings'] = {'map': meta['skin_alias_map']}
    garda_stage = read(game / 'entities/trader_antifighter_frigate.unit_skin')['skin_stages'][0]
    prefix = 'trader_antifighter_frigate_point_defense_autocannon_weapon_'
    bindings = [x for x in garda_stage['effects']['effect_alias_bindings'] if x['alias_name'].startswith(prefix)]
    require(len(bindings) == 4, 'Expected exactly four stock PDC effect aliases')
    stage['effects']['effect_alias_bindings'].extend(bindings)
    weapon = read(game / 'entities/trader_antifighter_frigate_point_defense_autocannon.weapon')
    original_weapon = copy.deepcopy(weapon)
    weapon['turret'] = meta['turret_override']
    restored = copy.deepcopy(weapon)
    for key in ['barrel_position', 'muzzle_positions']:
        restored['turret'][key] = original_weapon['turret'][key]
    require(restored == original_weapon, 'Rig weapon must change only turret offsets')
    write(out / 'entities/trader_light_frigate.unit', unit)
    write(out / 'entities/trader_light_frigate.unit_skin', skin)
    write(out / 'entities/expanse_tachi_one_pdc_garda.weapon', weapon)
    write(out / 'entities/weapon.entity_manifest', {'ids': ['expanse_tachi_one_pdc_garda']})
    copy_file(ROOT / 'src/name-only/en.localized_text', out / 'localized_text/en.localized_text')
    copy_file(ROOT / 'ASSET-SOURCES.md', out / 'ASSET-SOURCES.md')
    deps = [metadata_path, worker / 'audit/workers/b/compiler-geometry-check.json']
    for mesh in meta['outputs']:
        path = Path(mesh['mesh'])
        require(sha256(path) == mesh['sha256'], f'Worker compiled mesh drift: {path}')
        copy_file(path, out / 'meshes' / path.name)
        deps.append(path)
        for material_id in mesh['materials']:
            short = material_id.removeprefix('expanse_tachi_one_pdc_' + mesh['kind'] + '_')
            material_path = ROOT / 'assets/derived/baseline/game-materials' / (short + '.mesh_material')
            material = read(material_path)
            deps.append(material_path)
            write(out / 'mesh_materials' / (material_id + '.mesh_material'), material)
            for key, value in material.items():
                if key.endswith('_texture'):
                    source = ROOT / 'build/converted-textures' / (value + '.dds')
                    copy_file(source, out / 'textures' / source.name)
                    deps.append(source)
    return list(dict.fromkeys(deps))

def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('experiment', choices=['stock', 'tachi'])
    p.add_argument('--weapon-input', type=Path)
    p.add_argument('--rig-worker', type=Path)
    p.add_argument('--game', type=Path, required=True)
    p.add_argument('--sdk', type=Path, required=True)
    args = p.parse_args()
    frozen = check_frozen(ROOT / 'audit/experiments/checkpoint.json', ROOT, args.game, args.sdk)
    require(frozen['status'] == 'PASS', 'Frozen checkpoint check failed; inspect with validate_experiments.py frozen')
    ident = {'stock': 'expanse_exp_stock_pdc', 'tachi': 'expanse_exp_tachi_one_pdc'}[args.experiment]
    out = ROOT / 'build/experiments' / ident
    require(not out.exists() and not out.with_suffix('.zip').exists(), f'Refusing to overwrite {out}')
    if args.experiment == 'stock':
        require(args.weapon_input is not None, '--weapon-input required')
        deps = stock(out, args.weapon_input, args.game)
    else:
        require(args.rig_worker is not None, '--rig-worker required')
        deps = tachi(out, args.rig_worker, args.game)
    copy_file(ROOT / 'src/name-only/.mod_meta_data', out / '.mod_meta_data')
    checks = validate_package(out, args.game, args.sdk, ROOT)
    write(ROOT / 'audit/experiments' / f'{ident}-offline.json', checks)
    require(checks['status'] == 'PASS', f'Candidate left unzipped; offline checks {checks["status"]}')
    # Stable archive timestamps/order make identical inputs yield identical ZIPs.
    with zipfile.ZipFile(out.with_suffix('.zip'), 'w', zipfile.ZIP_DEFLATED) as archive:
        for path in sorted(out.rglob('*')):
            if path.is_file():
                info = zipfile.ZipInfo(path.relative_to(out).as_posix(), (2026, 9, 12, 0, 0, 0))
                info.compress_type = zipfile.ZIP_DEFLATED
                info.external_attr = 0o100644 << 16
                archive.writestr(info, path.read_bytes())
    result = verify_zip(out.with_suffix('.zip'), out)
    write(out.with_suffix('.dependencies.json'), [str(p.resolve()) for p in deps])
    write(out.with_suffix('.provenance.json'), provenance(out.with_suffix('.zip'), ROOT, deps))
    print(json.dumps({'id': ident, 'offline': checks['status'], 'runtime': 'NOT RUN', 'installed': False, **result}, indent=2))

if __name__ == '__main__':
    try:
        main()
    except (FileNotFoundError, ValueError) as error:
        raise SystemExit(str(error))
