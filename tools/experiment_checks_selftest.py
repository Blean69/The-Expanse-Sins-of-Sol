"""Focused failure-injection checks; temporary copies only, never game writes."""
from pathlib import Path
import argparse
import copy
import json
import shutil
import tempfile
import zipfile
from validate_experiments import Checks, Resolver, check_baseline_semantics, compare_tree, file_hashes, tree_hash, validate_package, verify_zip, provenance


def dump(path, data):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data))


def rejected(fn, fragment):
    try:
        fn()
    except Exception as exc:
        assert fragment in str(exc), str(exc)
        return str(exc)
    raise AssertionError('Injected defect was not rejected')


def main(root, game, sdk):
    report = Checks()
    with tempfile.TemporaryDirectory(prefix='expanse-worker-c-') as name:
        tmp = Path(name)
        source = tmp / 'frozen'
        source.mkdir()
        dump(source / 'known.json', {'known': True})
        record = {'path': str(source), 'files': file_hashes(source)}
        record['tree_sha256'] = tree_hash(record['files'])
        report.run('Unchanged synthetic frozen tree', lambda: compare_tree(record), 'asset-independent')
        dump(source / 'contaminant.weapon', {})
        report.run('Injected baseline weapon contamination rejected', lambda: rejected(lambda: compare_tree(record), 'contaminant.weapon'), 'asset-independent')
        missing = Checks()
        missing.run('dependency', lambda: compare_tree({'path': str(tmp / 'missing')}))
        report.run('Missing dependency is BLOCKED, not PASS', lambda: None if missing.result()['status'] == 'BLOCKED' else (_ for _ in ()).throw(AssertionError(missing.result())), 'asset-independent')
        fakegame = tmp / 'game'
        fakegame.mkdir()
        mod = tmp / 'mod'
        mod.mkdir()
        dump(fakegame / 'entities/example.unit', {'vanilla': True})
        dump(mod / 'entities/example.unit', {'override': True})
        resolver = Resolver(mod, fakegame)
        report.run('Mod override precedes installed reference', lambda: None if resolver.resolve('entities/example.unit', 'selftest') == mod / 'entities/example.unit' else (_ for _ in ()).throw(AssertionError()), 'asset-independent')
        dump(fakegame / 'entities/fallback.unit', {})
        resolver = Resolver(mod, fakegame)
        report.run('Untouched installed dependency fallback resolves', lambda: resolver.resolve('entities/fallback.unit', 'selftest').name, 'asset-independent')
        report.run('Injected missing reference fails explicitly', lambda: rejected(lambda: resolver.resolve('entities/missing.weapon', 'selftest'), 'Missing reference'), 'asset-independent')
        # Only small definitions copied; no source model or baseline package writes.
        for rel in ['src/name-only/en.localized_text', 'audit/derivative-transform.json']:
            dest = tmp / rel
            dest.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(root / rel, dest)
        for baseline in ('expanse_cobalt_name', 'expanse_corvette_visual'):
            dest = tmp / 'build' / baseline
            dest.mkdir(parents=True)
            for rel in ['.mod_meta_data', 'localized_text/en.localized_text'] + ([] if baseline.endswith('name') else ['entities/trader_light_frigate.unit', 'entities/trader_light_frigate.unit_skin']):
                target = dest / rel
                target.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(root / 'build' / baseline / rel, target)
        report.run('Recorded baseline semantics accepted read-only', lambda: check_baseline_semantics(tmp, game))
        unitpath = tmp / 'build/expanse_corvette_visual/entities/trader_light_frigate.unit'
        unit = json.loads(unitpath.read_text())
        changed = copy.deepcopy(unit)
        changed['weapons']['weapons'][0]['non_turret_muzzle_positions'][0][0] += 1
        dump(unitpath, changed)
        report.run('Injected wrong fixed muzzle rejected', lambda: rejected(lambda: check_baseline_semantics(tmp, game), 'muzzle coordinates'))
        changed = copy.deepcopy(unit)
        changed['weapons']['weapons'][0]['weapon_position'][0] += 1
        dump(unitpath, changed)
        report.run('Injected wrong muzzle mean rejected', lambda: rejected(lambda: check_baseline_semantics(tmp, game), 'weapon_position'))
        changed = copy.deepcopy(unit)
        changed['physics']['max_linear_speed'] += 1
        dump(unitpath, changed)
        report.run('Injected gameplay change rejected', lambda: rejected(lambda: check_baseline_semantics(tmp, game), 'gameplay'))
        mod = tmp / 'build/experiments/expanse_selftest_stock'
        dump(mod / '.mod_meta_data', {'compatibility_version': 2})
        for filename in ['trader_antifighter_frigate.unit', 'trader_torpedo_cruiser.unit']:
            dest = mod / 'entities' / filename
            dest.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(game / 'entities' / filename, dest)
        # Read-only integration graph check includes real hulls, aliases and torpedo.
        resolver = Resolver(mod, game)
        report.run('Installed Garda mount and Ogrov projectile graphs resolve', lambda: [resolver.unit(p.stem, 'selftest')['version'] for p in (mod / 'entities').glob('*.unit')])
        for filename in ['schema-comparison.json', 'installed-file-hashes.json']:
            dest = tmp / 'audit' / filename
            dest.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(root / 'audit' / filename, dest)
        result = validate_package(mod, game, sdk, tmp)
        report.run('Minimal stock package full offline validation', lambda: {k: result[k] for k in ('status', 'checks', 'runtime')} if result['status'] == 'PASS' else (_ for _ in ()).throw(AssertionError(result)))
        archive = mod.with_suffix('.zip')
        with zipfile.ZipFile(archive, 'w') as stream:
            for path in sorted(mod.rglob('*')):
                if path.is_file():
                    stream.write(path, path.relative_to(mod))
        report.run('ZIP bytes and layout match package', lambda: verify_zip(archive, mod), 'asset-independent')
        report.run('Package provenance records commit/source hashes/ZIP hash', lambda: {k: v for k, v in provenance(archive, root).items() if k not in ('source_files', 'source_status')}, 'asset-independent')
        blocked = validate_package(mod, game, tmp / 'absent-sdk', tmp)
        report.run('Missing SDK full validation is BLOCKED', lambda: None if blocked['status'] == 'BLOCKED' else (_ for _ in ()).throw(AssertionError(blocked)), 'environment')
        dump(mod / 'combat-candidates/contaminant.weapon', {})
        contaminated = validate_package(mod, game, sdk, tmp)
        report.run('Experimental package rejects candidate directory', lambda: None if contaminated['checks'][0]['status'] == 'FAIL' else (_ for _ in ()).throw(AssertionError(contaminated)), 'asset-independent')
        shutil.rmtree(mod / 'combat-candidates')
        weapon = json.loads((game / 'entities/trader_antifighter_frigate_point_defense_autocannon.weapon').read_text())
        weapon['turret']['biaxial_barrel_mesh'] = 'missing_alias'
        dump(mod / 'entities/trader_antifighter_frigate_point_defense_autocannon.weapon', weapon)
        resolver = Resolver(mod, game)
        report.run('Injected missing mount alias rejected', lambda: rejected(lambda: resolver.unit('trader_antifighter_frigate', 'selftest'), 'Unbound turret mesh alias'))
        # Runtime loader requires the explicit AI groups to match the named
        # weapon. The schema only types the fields, so test their relationship.
        cobalt = json.loads((game / 'entities/trader_light_frigate.unit').read_text())
        medium = json.loads((game / 'entities/trader_light_frigate_medium_autocannon.weapon').read_text())
        medium['attack_target_type_groups'] = ['torpedo_strikecraft'] + medium['attack_target_type_groups']
        dump(mod / 'entities/trader_light_frigate.unit', cobalt)
        dump(mod / 'entities/trader_light_frigate_medium_autocannon.weapon', medium)
        report.run('Mismatched unit and matching-weapon groups rejected', lambda: rejected(
            lambda: Resolver(mod, game).unit('trader_light_frigate', 'selftest'), 'attack_target_type_groups do not match weapon'))
        cobalt['ai']['attack_target_type_groups'] = medium['attack_target_type_groups']
        dump(mod / 'entities/trader_light_frigate.unit', cobalt)
        report.run('Matching groups accepted with unit torpedo-ignore preserved', lambda:
            Resolver(mod, game).unit('trader_light_frigate', 'selftest')['ai']['attack_target_type_groups_to_ignore'])
    result = report.result()
    print(json.dumps(result, indent=2, default=str))
    return 0 if result['status'] == 'PASS' else 2


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--root', type=Path, required=True)
    parser.add_argument('--game', type=Path, required=True)
    parser.add_argument('--sdk', type=Path, required=True)
    args = parser.parse_args()
    raise SystemExit(main(args.root, args.game, args.sdk))
