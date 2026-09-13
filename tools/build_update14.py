"""Build a separate hull/arc correction over the frozen 0.13 package."""
from pathlib import Path
import argparse
import json
import shutil
import zipfile
import numpy as np
from common import read_mesh
from build_polish import write, cp
from build_combat04 import binary_geometry
from build_combat03 import check_actions
from amun06_validate_package import AmunResolver, check_action_values
from update11_validate import schema_check
from validate_experiments import (read, require, sha256, file_hashes, compare_tree,
                                  verify_pins, verify_zip, provenance)

ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / 'build/experiments/expanse_update13'
OUT = ROOT / 'build/experiments/expanse_update14'
AUD = ROOT / 'audit/update14'
GAME = ROOT.parent / 'SteamLibrary/steamapps/common/Sins2'
SDK = GAME.parent / 'Sins of a Solar Empire II - Mod Tools'
SHIPS = ['expanse12_raptor', 'expanse12_pella']
HULLS = {f'meshes/expanse12_{n}_hull.mesh' for n in ['raptor', 'pella', 'scirocco']}


def preservation():
    d = read(AUD / 'checkpoint.json')
    trees = [compare_tree(t) for t in d['trees']]
    for p, h in {**d['zips'], **d['originals'], d['enabled_path']: d['enabled_sha256']}.items():
        require(sha256(p) == h, 'Frozen file changed: ' + p)
    return dict(trees=trees, zips=len(d['zips']), originals=len(d['originals']),
                pins=verify_pins(ROOT, GAME, SDK), enabled_settings_unchanged=True)


def contracts():
    c = read(AUD / 'integration-inputs.json')
    for p, h in read(AUD / 'reviewed-inputs.json').items():
        require(Path(p).is_file() and sha256(p) == h, 'Missing/changed reviewed input: ' + p)
    require(set(c['resources']) == HULLS, 'Expected exactly three corrected hulls')
    require(set(c['mount_arcs']) == set(SHIPS), 'Expected Raptor/Pella arc proposal')
    require(set(c['spatial']) == set(SHIPS), 'Missing measured hull extents')
    orientation = read(c['scirocco_orientation_audit'])
    require(orientation['status'].startswith('PASS') and
            orientation['after']['matched_faces_opposed_to_preserved_outward_normals'] == 0 and
            orientation['after']['signed_volume'] > 0, 'Scirocco exterior orientation gate failed')
    compiled = read(c['compiled_arc_geometry'])
    require(compiled['status'].startswith('PASS') and
            {r['identity'] for r in compiled['ships']} == set(SHIPS), 'Incomplete compiled ray binding')
    for row in compiled['ships']:
        rel = 'meshes/' + row['identity'] + '_hull.mesh'
        require(sha256(c['resources'][rel]) == row['mesh_sha256'], 'Ray-tested compiled mesh changed')
        require(sha256(row['npz_path']) == row['npz_sha256'], 'Ray input geometry changed')
        require(row['exact_float32_match'] and row['max_coordinate_error'] == 0 and
                row['canonical_compiled_triangle_sha256'] == row['canonical_source_triangle_sha256'],
                'Compiled hull does not exactly match tested triangle surfaces')
        require(read(c['arc_audits'][row['identity']])['hull_sha256'] == row['npz_sha256'],
                'Compiled mesh is bound to a different ray audit')
    for name in SHIPS:
        proposal = read(c['arc_audits'][name])
        require(proposal['status'].startswith('PASS'), 'Arc audit incomplete')
        require(c['mount_arcs'][name] == {e['weapon']: e['mount_overrides'] for e in proposal['entries']},
                'Applied arcs differ from tested proposal')
        for entry in proposal['entries']:
            require(c['weapon_tolerances'][entry['weapon']] == entry['weapon_overrides'],
                    'Applied firing tolerance differs from ray audit')
            require(entry['new_sampled_blocked_poses'] == 0 and entry['random_blocked_rays'] == 0,
                    'Ray audit has unaddressed hull hits')
        spatial = c['spatial'][name]
        geometry = read(c['hull_audits'][name])
        require(geometry['status'].startswith('PASS'), 'Hull compilation incomplete')
        require(spatial == {k: geometry['ship_spatial'][k] for k in ['radius', 'box']},
                'Applied spatial values differ from restored geometry audit')
        old_spatial = read(BASE / 'entities' / (name + '.unit'))['spatial']
        require(set(spatial) == {'radius', 'box'} and set(spatial['box']) == {'center', 'extents'},
                'Unexpected spatial field')
        for old, new in [(old_spatial['radius'], spatial['radius']),
                         (old_spatial['box']['center'], spatial['box']['center']),
                         (old_spatial['box']['extents'], spatial['box']['extents'])]:
            require(np.isfinite(new).all() and np.max(np.abs(np.array(old) - new)) < .05,
                    'Spatial change exceeds measured source restoration allowance')
        mounts = c['mount_arcs'][name]
        require(set(mounts) == {f'{name}_pdc_{i}' for i in range(9)}, 'Incomplete nine-mount arc set')
        for fields in mounts.values():
            require(set(fields) == {'yaw_arc', 'pitch_arc'}, 'Arc proposal changes other mount fields')
            for axis, limits in fields.items():
                require(set(limits) == {'min_angle', 'max_angle'}, 'Invalid arc keys')
                lo, hi = limits['min_angle'], limits['max_angle']
                require(np.isfinite([lo, hi]).all() and lo < hi, 'Empty/nonfinite arc')
                require((-180 <= lo < hi <= 180) if axis == 'yaw_arc' else (-85 <= lo < hi <= 5),
                        'Arc broadened beyond prior limit')
    for name, fields in c.get('weapon_tolerances', {}).items():
        require(name in {f'{s}_pdc_{i}' for s in SHIPS for i in range(9)}, 'Unexpected weapon')
        require(set(fields) <= {'pitch_firing_tolerance', 'yaw_firing_tolerance'}, 'Weapon gameplay edit')
        old = read(BASE / 'entities' / (name + '.weapon'))
        require(all(0 < v <= old[k] for k, v in fields.items()), 'Firing tolerance increased')
    return c


def expected_unit(name, c):
    u = read(BASE / 'entities' / (name + '.unit'))
    u['spatial'].update(c['spatial'][name])
    for mount in u['weapons']['weapons']:
        if mount['weapon'] in c['mount_arcs'][name]:
            mount.update(c['mount_arcs'][name][mount['weapon']])
    return u


def expected_weapon(name, fields):
    w = read(BASE / 'entities' / (name + '.weapon'))
    w.update(fields)
    return w


def build(c):
    require(not OUT.exists() and not OUT.with_suffix('.zip').exists(), 'Refusing existing 0.14 output')
    shutil.copytree(BASE, OUT)
    for rel, src in c['resources'].items():
        cp(Path(src), OUT / rel)
    for name in SHIPS:
        write(OUT / 'entities' / (name + '.unit'), expected_unit(name, c))
    for name, fields in c.get('weapon_tolerances', {}).items():
        write(OUT / 'entities' / (name + '.weapon'), expected_weapon(name, fields))
    meta = read(BASE / '.mod_meta_data')
    meta.update(display_name='The Expanse — 0.14 HULL & FIRING ARC FIX', display_version='0.14.0',
                short_description='Corrected Scirocco exterior, restored Raptor/Pella detail and restricted PDC arcs.',
                long_description='Load alone. Complete 0.13 fleet and audio included. New model visibility, firing coverage and performance require workstation confirmation.')
    write(OUT / '.mod_meta_data', meta)
    (OUT / 'ASSET-SOURCES.md').write_text((ROOT / 'ASSET-SOURCES.md').read_text())


def validate(c):
    before, after = file_hashes(BASE), file_hashes(OUT)
    allowed = HULLS | {'.mod_meta_data', 'ASSET-SOURCES.md'}
    for name in SHIPS:
        rel = 'entities/' + name + '.unit'
        allowed.add(rel)
        require(read(OUT / rel) == expected_unit(name, c), 'Unexpected unit change: ' + name)
    for name, fields in c.get('weapon_tolerances', {}).items():
        rel = 'entities/' + name + '.weapon'
        allowed.add(rel)
        require(read(OUT / rel) == expected_weapon(name, fields), 'Unexpected weapon change: ' + name)
    require(set(before) == set(after), 'Unexpected file additions/removals')
    for rel, h in before.items():
        require(after[rel] == h or rel in allowed, 'Unrelated baseline content changed: ' + rel)
    for rel, src in c['resources'].items():
        require(after[rel] == sha256(src), 'Mesh differs from reviewed input: ' + rel)
    schemas = []
    for rel in after:
        if before[rel] != after[rel]:
            checked = schema_check(OUT / rel, BASE / rel if rel.endswith('.unit') else None)
            if checked:
                schemas.append(checked)
    meshes, points = [], []
    for rel in sorted(HULLS):
        meshes.append(binary_geometry(OUT / rel))
        old, new = read_mesh(BASE / rel), read_mesh(OUT / rel)
        require(new['meshpoints'] == old['meshpoints'], 'Hull attachments moved: ' + rel)
        require(new['materials'] == old['materials'], 'Hull material bindings changed: ' + rel)
        name = Path(rel).stem.removesuffix('_hull')
        unit_box = read(OUT / 'entities' / (name + '.unit'))['spatial']['box']
        center, extents = np.array(new['box'][:3]), np.array(new['box'][3:])
        require(np.all(np.abs(center - unit_box['center']) + extents <= np.array(unit_box['extents']) + 1e-4),
                'Restored hull exceeds unit spatial box: ' + rel)
        points.append(dict(mesh=rel, unchanged_meshpoints=len(new['meshpoints']),
                           restored_hull_inside_unit_box=True))
    resolver = AmunResolver(OUT, GAME)
    graphs = {}
    for name in ['trader_light_frigate', *SHIPS, 'expanse12_scirocco', 'trader_scout_corvette',
                 'expanse_donnager_battleship', 'expanse_mcrn_corvette', 'expanse_rocinante_hero', 'expanse_amun_ra']:
        unit = resolver.unit(name, '0.14 combined ship')
        graphs[name] = dict(graph=check_actions(OUT, resolver, name),
                            typed=check_action_values(OUT, GAME, resolver, unit))
    return dict(status='PASS OFFLINE ONLY', runtime='NOT RUN', schemas=schemas, meshes=meshes,
                attachment_checks=points, references=resolver.edges, ability_graphs=graphs,
                changed_files=sorted(p for p in before if before[p] != after[p]),
                preservation=preservation())


def main(args):
    preservation()
    c = contracts()
    if not (args.validate_only or args.package_existing):
        build(c)
    write(AUD / 'package-validation.json', validate(c))
    if args.validate_only:
        print('PASS OFFLINE PACKAGE TREE; runtime NOT RUN; archive not requested')
        return
    archive = OUT.with_suffix('.zip')
    require(not archive.exists(), 'Refusing existing ZIP')
    with zipfile.ZipFile(archive, 'w', zipfile.ZIP_DEFLATED) as z:
        for p in sorted(OUT.rglob('*')):
            if p.is_file():
                item = zipfile.ZipInfo(p.relative_to(OUT).as_posix(), (2026, 9, 13, 0, 0, 0))
                item.compress_type = zipfile.ZIP_DEFLATED
                item.external_attr = 0o100644 << 16
                z.writestr(item, p.read_bytes())
    summary = dict(mod_id=OUT.name, **verify_zip(archive, OUT), installed=False, runtime='NOT RUN')
    write(AUD / 'package-summary.json', summary)
    deps = [BASE, AUD / 'integration-inputs.json', AUD / 'reviewed-inputs.json',
            *[Path(p) for p in c['resources'].values()]]
    write(OUT.with_suffix('.dependencies.json'), list(map(str, deps)))
    write(OUT.with_suffix('.provenance.json'), provenance(archive, ROOT, deps))
    print(json.dumps(summary, indent=2))


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    group = parser.add_mutually_exclusive_group()
    group.add_argument('--validate-only', action='store_true')
    group.add_argument('--package-existing', action='store_true')
    main(parser.parse_args())
