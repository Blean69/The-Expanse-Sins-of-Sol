"""Read-only offline gates for frozen baselines and small experimental packages.

No builders/installers are imported or invoked. A missing dependency is BLOCKED,
never PASS. Reference checking is deliberately scoped to the experimental unit /
weapon / skin / mesh / material graph; untouched effects/audio/death assets form
verified installed boundary references, not a claim about all engine resources.
"""
from pathlib import Path
import argparse
import copy
import hashlib
import json
import math
import subprocess
import sys
import zipfile

PINNED_SCHEMA = '8e061033afe53b1393eaefd56617a3fd041eeb5f'
BASELINES = ('expanse_cobalt_name', 'expanse_corvette_visual')


def read(path):
    return json.loads(Path(path).read_text(encoding='utf-8-sig'))


def sha256(path):
    h = hashlib.sha256()
    with Path(path).open('rb') as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b''):
            h.update(block)
    return h.hexdigest()


def file_hashes(root):
    root = Path(root)
    if not root.is_dir():
        raise FileNotFoundError(f'Missing directory dependency: {root}')
    return {p.relative_to(root).as_posix(): sha256(p) for p in sorted(root.rglob('*')) if p.is_file()}


def tree_hash(files):
    return hashlib.sha256(json.dumps(files, sort_keys=True, separators=(',', ':')).encode()).hexdigest()


class Checks:
    def __init__(self):
        self.rows = []

    def run(self, name, fn, scope='environment'):
        try:
            detail = fn()
            self.rows.append(dict(check=name, scope=scope, status='PASS', detail=detail))
        except (FileNotFoundError, ModuleNotFoundError) as exc:
            self.rows.append(dict(check=name, scope=scope, status='BLOCKED', detail=str(exc)))
        except Exception as exc:
            self.rows.append(dict(check=name, scope=scope, status='FAIL', detail=f'{type(exc).__name__}: {exc}'))

    def result(self):
        statuses = {r['status'] for r in self.rows}
        return dict(status='FAIL' if 'FAIL' in statuses else 'BLOCKED' if 'BLOCKED' in statuses else 'PASS',
                    checks=self.rows, runtime='NOT RUN')


def require(condition, message):
    if not condition:
        raise ValueError(message)


def compare_tree(record):
    actual = file_hashes(record['path'])
    expected = record['files']
    require(actual == expected, f"Frozen tree changed: {record['path']}; added={sorted(actual.keys()-expected.keys())}; "
            f"missing={sorted(expected.keys()-actual.keys())}; changed={sorted(k for k in actual.keys() & expected.keys() if actual[k] != expected[k])}")
    require(tree_hash(actual) == record['tree_sha256'], 'Checkpoint tree hash is inconsistent')
    return dict(path=record['path'], files=len(actual), tree_sha256=tree_hash(actual))


def verify_pins(project_root, game, sdk):
    root, game, sdk = map(Path, (project_root, game, sdk))
    comparison = read(root / 'audit/schema-comparison.json')
    require(comparison['official_commit'] == PINNED_SCHEMA, 'Unexpected schema revision in audit')
    for item in comparison['files']:
        data = (sdk / item['path']).read_bytes()
        blob = hashlib.sha1(b'blob ' + str(len(data)).encode() + b'\0' + data).hexdigest()
        require(blob == item['official_git_blob'], f"SDK drift: {item['path']}")
    installed = read(root / 'audit/installed-file-hashes.json')
    for name, item in installed.items():
        require(sha256(game / name) == item['sha256'], f'Installed dependency drift: {name}')
    return dict(schema_commit=PINNED_SCHEMA, schemas=len(comparison['files']), installed_references=len(installed))


def check_baseline_semantics(project_root, game):
    root, game = Path(project_root), Path(game)
    loc = read(root / 'src/name-only/en.localized_text')
    require(set(loc) == {'trader_light_frigate_name', 'trader_light_frigate_description'}, 'Name source must contain exactly two existing localization keys')
    vanilla_loc = read(game / 'localized_text/en.localized_text')
    require(all(k in vanilla_loc and isinstance(v, str) for k, v in loc.items()), 'Unknown localization key or non-string value')
    for name in BASELINES:
        out = root / 'build' / name
        require(read(out / 'localized_text/en.localized_text') == loc, f'Wrong baseline localization: {name}')
        require(not list(out.rglob('*.weapon')), f'Combat contamination: {name} contains weapon definitions')
    require(set(file_hashes(root / 'build' / BASELINES[0])) == {'.mod_meta_data', 'localized_text/en.localized_text'}, 'Name baseline file allowlist changed')
    out = root / 'build' / BASELINES[1]
    vanilla_unit = read(game / 'entities/trader_light_frigate.unit')
    unit = read(out / 'entities/trader_light_frigate.unit')
    mount = unit['weapons']['weapons'][0]
    muzzles = read(root / 'audit/derivative-transform.json')['muzzles']
    require(len(mount['non_turret_muzzle_positions']) == 2, 'Visual baseline must have exactly two muzzle positions')
    require(all(math.isclose(a, b, abs_tol=1e-5) for aa, bb in zip(mount['non_turret_muzzle_positions'], muzzles, strict=True) for a, b in zip(aa, bb, strict=True)), 'Visual baseline muzzle coordinates changed')
    mean = [sum(x[i] for x in muzzles) / 2 for i in range(3)]
    require(all(math.isclose(a, b, abs_tol=1e-5) for a, b in zip(mount['weapon_position'], mean, strict=True)), 'Visual baseline weapon_position must equal the two-muzzle mean')
    restored = copy.deepcopy(unit)
    for key in ('weapon_position', 'non_turret_muzzle_positions'):
        restored['weapons']['weapons'][0][key] = vanilla_unit['weapons']['weapons'][0][key]
    require(restored == vanilla_unit, 'Visual baseline changed Cobalt gameplay or another unit field')
    skin = read(out / 'entities/trader_light_frigate.unit_skin')
    vanilla_skin = read(game / 'entities/trader_light_frigate.unit_skin')
    require(skin['skin_stages'][0]['unit_mesh']['mesh'] == 'mcrn_corvette_baseline', 'Unexpected baseline hull')
    skin['skin_stages'][0]['unit_mesh']['mesh'] = vanilla_skin['skin_stages'][0]['unit_mesh']['mesh']
    require(skin == vanilla_skin, 'Unexpected visual baseline skin change')
    return dict(two_localization_entries=True, two_muzzles=muzzles, mean_weapon_position=mean, gameplay_unchanged=True)


def verify_zip(package_zip, mod_dir):
    files = file_hashes(mod_dir)
    with zipfile.ZipFile(package_zip) as archive:
        require(archive.testzip() is None, 'ZIP CRC failure')
        require(len(archive.namelist()) == len(set(archive.namelist())), 'Duplicate ZIP entries')
        require(set(archive.namelist()) == set(files), 'ZIP and package directory file lists differ')
        for name, digest in files.items():
            require(hashlib.sha256(archive.read(name)).hexdigest() == digest, f'ZIP data mismatch: {name}')
    return dict(files=len(files), zip_sha256=sha256(package_zip), tree_sha256=tree_hash(files))


def check_frozen(checkpoint, project_root, game, sdk):
    checks = Checks()
    try:
        snapshot = read(checkpoint)
    except (FileNotFoundError, json.JSONDecodeError) as exc:
        checks.run('Checkpoint dependency', lambda: (_ for _ in ()).throw(exc))
        return checks.result()
    for name, records in snapshot['baselines'].items():
        for kind in ('build', 'installed'):
            checks.run(f'{name}: frozen {kind}', lambda r=records[kind]: compare_tree(r))
        path = Path(records['build']['path']).with_suffix('.zip')
        def check_zip(p=path, r=records):
            require(sha256(p) == r['zip_sha256'], f'Frozen ZIP changed: {p}')
            return verify_zip(p, r['build']['path'])
        checks.run(f'{name}: frozen ZIP', check_zip)
    for name, record in snapshot['shared_read_only_inputs'].items():
        checks.run(f'Unchanged shared input: {name}', lambda r=record: compare_tree(r))
    checks.run('Unchanged enabled-mod settings', lambda: compare_tree(snapshot['settings']))
    checks.run('Exact baseline semantics including muzzle mean', lambda: check_baseline_semantics(project_root, game))
    checks.run('Pinned SDK and installed references', lambda: verify_pins(project_root, game, sdk))
    def compiler_pin():
        path = Path(sdk) / 'MeshBuilder/bin/MeshBuilder.exe'
        digest = sha256(path)
        require(digest == snapshot['meshbuilder_sha256'], f'MeshBuilder drift: {path}')
        return dict(path=str(path), sha256=digest)
    checks.run('Frozen MeshBuilder binary', compiler_pin)
    return checks.result()


def strings(value, path=()):
    if isinstance(value, dict):
        for key, item in value.items():
            yield from strings(item, path + (key,))
    elif isinstance(value, list):
        for i, item in enumerate(value):
            yield from strings(item, path + (str(i),))
    elif isinstance(value, str):
        yield path, value


class Resolver:
    """Exact typed relative path lookup, casefolded for Windows game IDs.

    Only same-relative-path overrides take precedence. Ambiguous casefolded
    names fail instead of guessing. Traversal stops at unmodified installed
    effect/audio/death resources, with those boundaries recorded in edges.
    """
    def __init__(self, mod, game):
        self.mod, self.game = Path(mod), Path(game)
        self.index = {}
        self.edges = []
        self.done = set()
        self.meshes = {}
        for origin, root in [('installed', self.game), ('mod', self.mod)]:
            if not root.is_dir():
                raise FileNotFoundError(f'Missing {origin} dependency directory: {root}')
            local = {}
            for path in root.rglob('*'):
                if path.is_file():
                    key = path.relative_to(root).as_posix().lower()
                    require(key not in local, f'Ambiguous casefolded path: {key}')
                    local[key] = (path, origin)
            self.index.update(local)

    def resolve(self, relative, source):
        require('..' not in Path(relative).parts and not Path(relative).is_absolute(), f'Invalid reference: {relative}')
        found = self.index.get(relative.lower())
        require(found is not None, f'Missing reference {relative} from {source}')
        path, origin = found
        self.edges.append(dict(source=str(source), reference=relative, resolved=str(path), origin=origin))
        return path

    def mesh(self, name, source):
        path = self.resolve(f'meshes/{name}.mesh', source)
        if path not in self.meshes:
            # Existing project reader supports this installed unskinned layout.
            # Any unknown binary layout is a failure, never silently skipped.
            from common import read_mesh
            self.meshes[path] = read_mesh(path)
            for material in self.meshes[path]['materials']:
                self.material(material, path)
        return self.meshes[path]

    def material(self, name, source):
        path = self.resolve(f'mesh_materials/{name}.mesh_material', source)
        if path in self.done:
            return
        self.done.add(path)
        for key, value in read(path).items():
            if key.endswith('_texture') and isinstance(value, str):
                self.resolve(f'textures/{value}.dds', path)

    def skin(self, name, source):
        path = self.resolve(f'entities/{name}.unit_skin', source)
        data = read(path)
        for stage in data['skin_stages']:
            for bindings, key in [(stage.get('child_mesh_alias_bindings', {}).get('map', []), 'mesh_alias_name'), (stage.get('effects', {}).get('effect_alias_bindings', []), 'alias_name')]:
                names = [b[key] for b in bindings]
                require(len(names) == len(set(names)), f'Duplicate skin aliases: {path}')
            for ptr, value in strings(stage):
                key = ptr[-1]
                if key == 'mesh':
                    self.mesh(value, path)
                elif key in ('particle_effect', 'beam_effect', 'trail_effect', 'shield_effect'):
                    self.resolve(f"effects/{value}.{'exhaust_trail_effect' if key == 'trail_effect' else key}", path)
                elif key == 'death_sequence_group':
                    self.resolve(f'death_sequences/{value}.death_sequence_group', path)
                elif key == 'sound' or key.endswith('_sound') or 'sounds' in ptr or 'dialogue' in ptr:
                    self.resolve(f'sounds/{value}.sound', path)
        return data

    def weapon(self, name, skins, source):
        path = self.resolve(f'entities/{name}.weapon', source)
        data = read(path)
        for skin in skins:
            for stage in skin['skin_stages']:
                meshes = {b['mesh_alias_name'] for b in stage.get('child_mesh_alias_bindings', {}).get('map', [])}
                effects = {b['alias_name'] for b in stage.get('effects', {}).get('effect_alias_bindings', [])}
                for key, value in data.get('turret', {}).items():
                    if key.endswith('_mesh'):
                        require(value in meshes, f'Unbound turret mesh alias {value}: {path} on {source}')
                for key, value in data.get('effects', {}).items():
                    if key.endswith('_effect') and isinstance(value, str):
                        require(value in effects, f'Unbound weapon effect alias {value}: {path} on {source}')
        filters = read(self.resolve('uniforms/target_filter.uniforms', path))
        groups = read(self.resolve('uniforms/attack_target_type_group.uniforms', path))
        filter_ids = {x['target_filter_id'] for x in filters['common_target_filters']}
        group_ids = {x['unit_attack_target_type_group_id'] for x in groups['attack_target_type_groups']}
        require(data['uniforms_target_filter_id'] in filter_ids, f'Unknown weapon filter: {path}')
        require(set(data['attack_target_type_groups']) <= group_ids, f'Unknown weapon target group: {path}')
        if data['firing']['firing_type'] == 'spawn_torpedo':
            projectile = data['firing']['torpedo_firing_definition']['spawned_unit']
            p = self.unit(projectile, path)
            require('torpedo' in p and p['target_filter_unit_type'] == 'torpedo' and p['ai_attack_target']['attack_target_type'] == 'torpedo', f'Projectile lacks observed torpedo classification: {projectile}')
        return data

    def unit(self, name, source):
        path = self.resolve(f'entities/{name}.unit', source)
        data = read(path)
        if path in self.done:
            return data
        self.done.add(path)
        skins = [self.skin(skin, path) for group in data.get('skin_groups', []) for skin in group['skins']]
        mounts = data.get('weapons', {}).get('weapons', [])
        require(not mounts or skins, f'Armed unit has no resolved skin: {path}')
        for mount in mounts:
            self.weapon(mount['weapon'], skins, path)
            if 'mesh_point' in mount:
                for skin in skins:
                    for stage in skin['skin_stages']:
                        mesh = self.mesh(stage['unit_mesh']['mesh'], path)
                        require(mount['mesh_point'] in {point['name'] for point in mesh['meshpoints']}, f"Missing hull mount mesh point {mount['mesh_point']}: {path}")
        matching = data.get('ai', {}).get('attack_target_type_groups_matching_weapon')
        if matching:
            matching_path = self.resolve(f'entities/{matching}.weapon', path)
            require(matching in {m['weapon'] for m in mounts}, f'AI group matching weapon is not mounted: {path}')
            require(data['ai'].get('attack_target_type_groups') == read(matching_path)['attack_target_type_groups'],
                    f'attack_target_type_groups do not match weapon:{matching}.weapon on {path}')
        return data


def validate_package(mod_dir, game, sdk, audit_root):
    mod, game, sdk, root = map(Path, (mod_dir, game, sdk, audit_root))
    checks = Checks()
    def structure():
        require(mod.name not in BASELINES, 'Experimental package uses frozen baseline ID')
        require(mod.resolve().parent == (root / 'build/experiments').resolve(), 'Experimental package must be a direct child of build/experiments')
        require(read(mod / '.mod_meta_data') == {'compatibility_version': 2}, 'Unexpected mod metadata for this experiment')
        files = file_hashes(mod)
        allowed = {'.mod_meta_data', 'ASSET-SOURCES.md'}
        for rel in files:
            p = Path(rel)
            require(rel in allowed or (len(p.parts) == 2 and (p.parts[0], p.suffix) in {
                ('entities', '.unit'), ('entities', '.unit_skin'), ('entities', '.weapon'), ('entities', '.entity_manifest'),
                ('localized_text', '.localized_text'), ('meshes', '.mesh'), ('mesh_materials', '.mesh_material'), ('textures', '.dds')}), f'Unexpected experiment file / candidate contamination: {rel}')
        return dict(mod_id=mod.name, files=len(files), tree_sha256=tree_hash(files))
    checks.run('Package layout and separation', structure, 'asset-independent')
    def manifests():
        for path in (mod / 'entities').glob('*.entity_manifest'):
            data = read(path)
            require(set(data) == {'ids'} and isinstance(data['ids'], list), f'Unknown manifest shape: {path}')
            require(len(data['ids']) == len(set(data['ids'])), f'Duplicate manifest IDs: {path}')
            extension = path.stem
            require(extension in ('unit', 'unit_skin', 'weapon'), f'Unsupported manifest kind: {path}')
            for name in data['ids']:
                require(isinstance(name, str) and (mod / 'entities' / f'{name}.{extension}').is_file(), f'Manifest does not resolve to packaged definition: {name}.{extension}')
        for path in (mod / 'entities').iterdir():
            if path.suffix in ('.unit', '.unit_skin', '.weapon') and not (game / 'entities' / path.name).exists():
                manifest = mod / 'entities' / f'{path.suffix[1:]}.entity_manifest'
                require(manifest.is_file(), f'New entity missing additive manifest: {path.name}')
                require(path.stem in read(manifest)['ids'], f'New entity missing from additive manifest: {path.name}')
        return 'All new entity IDs registered; no vanilla dependency copies required'
    checks.run('Additive manifests', manifests)
    checks.run('Pinned SDK and installed references', lambda: verify_pins(root, game, sdk))
    def schemas():
        import jsonschema
        count = 0
        for path in mod.rglob('*'):
            schema = {'.unit': 'unit-schema.json', '.unit_skin': 'unit-skin-schema.json', '.weapon': 'weapon-schema.json'}.get(path.suffix)
            if path.is_file() and schema:
                jsonschema.Draft7Validator(read(sdk / 'json_schemas' / schema)).validate(read(path))
                count += 1
        return dict(validated=count, limitation='Draft 7 does not enforce unevaluatedProperties; integrator must review exact source diffs. Installed SDK has no mesh_material, localized_text or mod_meta_data schema; these are checked structurally/by references only')
    checks.run('Pinned schemas for authored definitions', schemas)
    resolver = None
    def references():
        nonlocal resolver
        resolver = Resolver(mod, game)
        units = sorted((mod / 'entities').glob('*.unit'))
        require(units, 'No experimental unit override; candidate is not a complete experiment')
        for path in units:
            resolver.unit(path.stem, 'package-root')
        # Every authored skin/mesh/material must also parse and resolve, even unused.
        for path in (mod / 'entities').glob('*.unit_skin'):
            resolver.skin(path.stem, 'package-root')
        for path in (mod / 'meshes').glob('*.mesh'):
            resolver.mesh(path.stem, 'package-root')
        for path in (mod / 'mesh_materials').glob('*.mesh_material'):
            resolver.material(path.stem, 'package-root')
        reached = {Path(edge['resolved']) for edge in resolver.edges}
        orphaned = [p.name for p in (mod / 'entities').glob('*.weapon') if p not in reached]
        require(not orphaned, f'Unintegrated weapon candidates in package: {orphaned}')
        return dict(edges=len(resolver.edges), mesh_count=len(resolver.meshes), boundary='Installed effect/audio/death resources checked for existence only; no runtime or whole-game closure claim')
    checks.run('Overlay references, mount aliases, torpedo entity classification', references)
    result = checks.result()
    result['reference_edges'] = resolver.edges if resolver else []
    result['resolved_dependency_sha256'] = {p: sha256(p) for p in sorted({e['resolved'] for e in result['reference_edges']})}
    return result


def provenance(package_zip, repo_root, dependency_paths=()):
    repo = Path(repo_root)
    def git(*args):
        return subprocess.check_output(['git', '-C', str(repo), *args]).decode().strip()
    # Hash the complete tracked+untracked nonignored source set, not just HEAD.
    names = subprocess.check_output(['git', '-C', str(repo), 'ls-files', '-z', '--cached', '--others', '--exclude-standard']).decode().split('\0')
    source_files = {n: sha256(repo / n) if (repo / n).is_file() else 'DELETED' for n in sorted(set(names)) if n}
    deps = {str(Path(p).resolve()): sha256(p) if Path(p).is_file() else tree_hash(file_hashes(p)) for p in dependency_paths}
    return dict(source_commit=git('rev-parse', 'HEAD'), source_status=git('status', '--short'), source_tree_sha256=tree_hash(source_files), source_files=source_files, ignored_dependency_hashes=deps, package_sha256=sha256(package_zip), package_path=str(Path(package_zip).resolve()), runtime='NOT RUN')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('mode', choices=['frozen', 'package'])
    parser.add_argument('--root', type=Path, default=Path(__file__).resolve().parents[1])
    parser.add_argument('--game', type=Path, required=True)
    parser.add_argument('--sdk', type=Path, required=True)
    parser.add_argument('--checkpoint', type=Path)
    parser.add_argument('--mod', type=Path)
    parser.add_argument('--zip', type=Path)
    parser.add_argument('--report', type=Path)
    args = parser.parse_args()
    if args.mode == 'frozen':
        result = check_frozen(args.checkpoint or args.root / 'audit/experiments/checkpoint.json', args.root, args.game, args.sdk)
    else:
        parser.error('--mod is required for package') if not args.mod else None
        result = validate_package(args.mod, args.game, args.sdk, args.root)
        if args.zip:
            extra = Checks()
            extra.run('ZIP matches validated directory', lambda: verify_zip(args.zip, args.mod), 'asset-independent')
            result['checks'].extend(extra.rows)
            if extra.result()['status'] != 'PASS':
                result['status'] = extra.result()['status']
            result['provenance'] = provenance(args.zip, args.root)
    rendered = json.dumps(result, indent=2) + '\n'
    if args.report:
        target = args.report.resolve()
        allowed = ((args.root / 'audit/experiments').resolve(), (args.root / 'audit/workers/c').resolve(), (args.root / 'build/worker-c').resolve())
        require(any(target.is_relative_to(base) for base in allowed), 'Report destination must be audit/experiments, audit/workers/c, or build/worker-c')
        args.report.parent.mkdir(parents=True, exist_ok=True)
        args.report.write_text(rendered)
    print(json.dumps({k: v for k, v in result.items() if k not in ('reference_edges', 'provenance')}, indent=2))
    return 0 if result['status'] == 'PASS' else 2


if __name__ == '__main__':
    sys.exit(main())
