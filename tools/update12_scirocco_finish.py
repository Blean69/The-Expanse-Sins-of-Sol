"""Validate the selected Scirocco outputs and write the integrator handoff.

Does not run intake, optimize, compile, render, install, or launch the game.
Missing ignored dependencies are errors, never passes or reconstructed assets.
"""
from update12_scirocco_common import *
from PIL import Image


def digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def main():
    spec = read(AUD / 'integration-spec.json')
    mesh_report = read(AUD / 'mesh-validation.json')
    mount_report = read(AUD / 'mount-checks.json')
    ui = read(AUD / 'ui-integration-spec.json')
    ui_report = read(AUD / 'ui-validation.json')
    source = read(AUD / 'source-audit.json')
    source_path = Path(source['source'])
    master = ROOT / 'assets/original/update12-scirocco' / source_path.name
    assert digest(source_path) == digest(master) == source['sha256']
    assert mesh_report['status'] == 'PASS OFFLINE'
    assert mount_report['status'] == 'PASS BOUNDED OFFLINE'
    assert ui['status'] == 'PASS OFFLINE UI' and ui_report['status'] == 'PASS'
    assert ui_report['triangles'] == spec['assembled_triangle_total'] == 89519
    for path, sha in ui_report['source_dependencies'].items():
        assert digest(path) == sha, ('Stale UI source', path)
    for png in ui_report['png_checks']:
        assert digest(png['file']) == png['sha256']
        with Image.open(png['file']) as image:
            assert list(image.size) == png['dimensions'] and image.mode == 'RGBA'
    game = BUILD / 'game'
    parsed = {}
    for record in mesh_report['meshes']:
        path = game / 'meshes' / (record['mesh'] + '.mesh')
        assert digest(path) == record['sha256'], ('Stale binary report', str(path))
        actual = read_mesh(path)
        assert actual['triangles'] == record['triangles']
        assert record['opposed_winding_triangles'] == 0
        assert record['tangent_fallbacks'] == 0
        assert record['official_trailer_preserved'] and record['only_tangent_bytes_changed']
        permitted = 3 if record['mesh'].endswith('pdc_base') else 9 if record['mesh'].endswith('pdc_barrel') else 0
        assert record['near_ambiguous_winding_triangles'] == permitted
        parsed[record['mesh']] = actual
        for material in record['materials']:
            definition = read(game / 'mesh_materials' / (material + '.mesh_material'))
            assert set(definition) == {'version', 'base_color_texture', 'normal_texture',
                                       'occlusion_roughness_metallic_texture', 'mask_texture', 'emissive_factor'}
            assert definition['version'] == 1
            for key, texture in definition.items():
                if key.endswith('_texture'):
                    texture_path = game / 'textures' / (texture + '.dds')
                    assert texture_path.read_bytes()[:4] == b'DDS '
    points = {p['name']: p for p in parsed[spec['hull_mesh']]['meshpoints']}
    assert len(points) == len(spec['meshpoints']['hull'])
    for rig in spec['rigs']:
        point = points[rig['mount']['mesh_point']]
        assert np.allclose(point['position'], rig['yaw_pivot_hull'], atol=2e-5)
        # Official binary serializes frame vectors as rows, metadata as columns.
        assert np.allclose(np.array(point['rotation']).reshape(3, 3).T,
                           rig['basis_columns'], atol=2e-6)
    for key, prefix in [('light_torpedo_ports', 'weapon.light_torpedo'),
                        ('heavy_torpedo_ports', 'weapon.heavy_torpedo')]:
        for index, port in enumerate(spec['equipment'][key]):
            assert np.allclose(points[f'{prefix}.{index}']['position'], port['position'], atol=2e-5)
    for index, exhaust in enumerate(spec['equipment']['exhausts']):
        point = points[f'exhaust.{index}']
        assert np.allclose(point['position'], exhaust['position'], atol=2e-5)
        assert np.allclose(np.array(point['rotation']).reshape(3, 3)[2], exhaust['forward'], atol=2e-6)
    assert np.allclose(points['weapon.boarding.0']['position'], spec['equipment']['boarding']['position'], atol=2e-5)
    clearance = read(AUD / 'rail-clearance.json')
    assert [row['angle_degrees'] for row in clearance['sweeps']] == [-15, -7.5, 0, 7.5, 15]
    assert all(not row['outside_bearing_contacts'] for row in clearance['sweeps'])
    material_report = read(AUD / 'material-validation.json')
    for name, sha in material_report['textures'].items():
        assert digest(game / 'textures' / name) == sha
    files = {str(p.relative_to(game)): digest(p) for p in sorted(game.rglob('*')) if p.is_file()}
    ui_root = Path(ui['game_directory'])
    ui_files = {str(p.relative_to(ui_root)): digest(p) for p in sorted(ui_root.rglob('*')) if p.is_file()}
    combined_hash = hashlib.sha256(json.dumps({'game': files, 'ui': ui_files}, sort_keys=True).encode()).hexdigest()
    spec.update(status='PASS OFFLINE ASSET HANDOFF', ui_directory=str(ui_root),
                ui_integration_spec=str(AUD / 'ui-integration-spec.json'),
                game_file_hashes=files, ui_file_hashes=ui_files,
                asset_bundle_sha256=combined_hash,
                material_validation='Exact existing six-key ship material profile; no matching material schema in pinned SDK',
                runtime='NOT RUN')
    write(AUD / 'integration-spec.json', spec)
    write(AUD / 'final-validation.json', {
        'status': 'PASS OFFLINE ASSET HANDOFF', 'asset_bundle_sha256': combined_hash,
        'source_and_master_sha256': source['sha256'], 'source_unchanged': True,
        'mesh_count': len(mesh_report['meshes']), 'assembled_triangles': spec['assembled_triangle_total'],
        'proper_compiled_mount_frames': 13, 'torpedo_ports': 10, 'engine_nozzles': 4,
        'boarding_origin': 'weapon.boarding.0; 20 units outward from measured hull',
        'rail_clearance': '600 samples per pose at -15, -7.5, 0, 7.5, 15 degrees; continuous collision proof not claimed',
        'donor_winding_exception': 'Same 3 base and 9 barrel near-perpendicular donor faces; zero opposed faces at -1e-5 tolerance',
        'runtime': 'NOT RUN'})
    print(json.dumps({'status': spec['status'], 'asset_bundle_sha256': combined_hash,
                      'game_files': len(files), 'ui_files': len(ui_files), 'runtime': 'NOT RUN'}))


if __name__ == '__main__':
    main()
