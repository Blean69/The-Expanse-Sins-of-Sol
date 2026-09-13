"""Render standalone Sins II UI PNGs from the preserved normalized Tachi.

Read-only dependencies; output stays under explicitly selected build/polish-c.
The recipe and projected vector triangles remain separate from game sprites.
No runtime/game rendering, DDS conversion, downloads or installation occurs.
"""
from pathlib import Path
import argparse
import hashlib
import json
import math
import sys
import numpy as np
from PIL import Image, ImageDraw, ImageFilter
from common import Gltf

PREFIX = 'mcrn_corvette'
ROLES = ('hud_icon', 'hud_picture', 'tooltip_picture', 'main_view_icon', 'main_view_icon_selected', 'main_view_icon_sub_selected')


def digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def write(path, data):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2) + '\n')


def geometry(source):
    gltf = Gltf(source)
    meshes = []
    count = 0
    textures = {}
    for i, node in enumerate(gltf.g['nodes']):
        if 'mesh' not in node or i not in gltf.world:
            continue
        for primitive in gltf.g['meshes'][node['mesh']]['primitives']:
            idx = gltf.accessor(primitive['indices']).reshape(-1, 3)
            tri = gltf.positions(i, primitive)[idx]
            uv = gltf.accessor(primitive['attributes']['TEXCOORD_0'])[idx]
            material = gltf.g['materials'][primitive['material']]
            pbr = material['pbrMetallicRoughness']
            texture_index = pbr['baseColorTexture']['index']
            uri = gltf.g['images'][gltf.g['textures'][texture_index]['source']]['uri']
            path = source.parent / uri
            if path not in textures:
                textures[path] = np.asarray(Image.open(path).convert('RGBA'))
            meshes.append((tri, uv, textures[path], pbr.get('baseColorFactor', [1, 1, 1, 1]), material.get('alphaMode', 'OPAQUE')))
            count += len(tri)
    return meshes, count, textures


def project(triangles, basis, size, fill):
    xyz = triangles @ basis.T
    lo, hi = xyz[:, :, :2].min((0, 1)), xyz[:, :, :2].max((0, 1))
    zoom = min(size[0] * fill / (hi[0] - lo[0]), size[1] * fill / (hi[1] - lo[1]))
    xy = (xyz[:, :, :2] - (lo + hi) / 2) * zoom
    xy[:, :, 1] *= -1
    xy += np.asarray(size) / 2
    return xyz, xy


def render(meshes, size, basis, fill=.9):
    """Orthographic, double-sided z-buffer with source base-color UV sampling.

    Opaque hull material alpha is ignored, matching glTF alphaMode=OPAQUE.
    Alpha-masked/blended source decals use a 0.5 cutout for this static UI.
    This deliberately avoids importing the hull's prior game-face culling issue.
    """
    tris = np.concatenate([m[0] for m in meshes])
    xyz, xy = project(tris, basis, size, fill)
    out = np.zeros((size[1], size[0], 4), dtype=np.uint8)
    depth = np.full((size[1], size[0]), -np.inf)
    light = np.array([-.4, .8, .6]); light /= np.linalg.norm(light)
    n = 0
    for triangles, uvs, texture, factor, mode in meshes:
        normals = np.cross(triangles[:, 1] - triangles[:, 0], triangles[:, 2] - triangles[:, 0])
        normals /= np.maximum(np.linalg.norm(normals, axis=1, keepdims=True), 1e-12)
        shades = .38 + .62 * np.abs(normals @ light)
        for local, uv in enumerate(uvs):
            coords = xy[n]; zs = xyz[n, :, 2]; n += 1
            minx, miny = np.maximum(np.floor(coords.min(0)).astype(int), [0, 0])
            maxx, maxy = np.minimum(np.ceil(coords.max(0)).astype(int), [size[0] - 1, size[1] - 1])
            if minx > maxx or miny > maxy:
                continue
            x, y = np.meshgrid(np.arange(minx, maxx + 1) + .5, np.arange(miny, maxy + 1) + .5)
            a, b, c = coords
            denominator = (b[1] - c[1]) * (a[0] - c[0]) + (c[0] - b[0]) * (a[1] - c[1])
            if abs(denominator) < 1e-10:
                continue
            w0 = ((b[1] - c[1]) * (x - c[0]) + (c[0] - b[0]) * (y - c[1])) / denominator
            w1 = ((c[1] - a[1]) * (x - c[0]) + (a[0] - c[0]) * (y - c[1])) / denominator
            w2 = 1 - w0 - w1
            z = w0 * zs[0] + w1 * zs[1] + w2 * zs[2]
            old = depth[miny:maxy + 1, minx:maxx + 1]
            active = (w0 >= -1e-6) & (w1 >= -1e-6) & (w2 >= -1e-6) & (z >= old)
            if not active.any():
                continue
            tu = (w0 * uv[0, 0] + w1 * uv[1, 0] + w2 * uv[2, 0]) % 1
            tv = (w0 * uv[0, 1] + w1 * uv[1, 1] + w2 * uv[2, 1]) % 1
            color = texture[np.rint(tv * (texture.shape[0] - 1)).astype(int), np.rint(tu * (texture.shape[1] - 1)).astype(int)].astype(float)
            color *= np.asarray(factor)
            if mode != 'OPAQUE':
                active &= color[:, :, 3] >= 128
            # Static UI studio lift keeps the source black paint legible at 85px.
            color[:, :, :3] = np.power(np.clip(color[:, :, :3] / 255, 0, 1), .65) * 255 * (.65 + .35 * shades[local]) * 1.05
            color[:, :, 3] = 255
            region = out[miny:maxy + 1, minx:maxx + 1]
            region[active] = np.clip(color[active], 0, 255).astype(np.uint8)
            old[active] = z[active]
    return Image.fromarray(out)


def silhouette(meshes, size, pad=0):
    triangles = np.concatenate([m[0] for m in meshes])
    basis = np.array([[0, 0, 1], [1, 0, 0], [0, 1, 0]])
    _, coords = project(triangles, basis, size, .91)
    mask = Image.new('L', size)
    draw = ImageDraw.Draw(mask)
    for poly in coords:
        draw.polygon([tuple(p) for p in poly], fill=255)
    return mask, coords


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--main-root', type=Path, required=True)
    parser.add_argument('--game', type=Path, required=True)
    parser.add_argument('--sdk', type=Path, required=True)
    parser.add_argument('--out', type=Path, default=Path(__file__).resolve().parents[1] / 'build/polish-c')
    args = parser.parse_args()
    root = Path(__file__).resolve().parents[1]
    out = args.out.resolve()
    if out != (root / 'build/polish-c').resolve():
        raise ValueError('This worker renderer writes only its isolated build/polish-c output')
    source = args.main_root / 'assets/derived/baseline/mcrn_editable.gltf'
    for dep in (source, args.sdk / 'json_schemas/brush-schema.json', args.game / 'entities/trader_light_frigate.unit_skin'):
        if not dep.is_file():
            raise FileNotFoundError(f'Missing read-only dependency: {dep}')
    schema_path = args.sdk / 'json_schemas/brush-schema.json'
    pinned = json.loads((args.main_root / 'audit/schema-comparison.json').read_text())
    if pinned['official_commit'] != '8e061033afe53b1393eaefd56617a3fd041eeb5f':
        raise ValueError('Unexpected SDK schema revision')
    expected = next(row['official_git_blob'] for row in pinned['files'] if row['path'] == 'json_schemas/brush-schema.json')
    raw = schema_path.read_bytes()
    if hashlib.sha1(b'blob ' + str(len(raw)).encode() + b'\0' + raw).hexdigest() != expected:
        raise ValueError('Installed brush schema changed from pinned revision')
    snapshot = json.loads((args.main_root / 'audit/experiments/checkpoint.json').read_text())
    source_lock = snapshot['shared_read_only_inputs']['assets/derived']['files']
    for path in [source, source.parent / 'scene.bin']:
        relative = path.relative_to(args.main_root / 'assets/derived').as_posix()
        if digest(path) != source_lock[relative]:
            raise ValueError(f'Normalized source changed: {path}')
    schema = json.loads(raw)
    import jsonschema
    meshes, count, textures = geometry(source)
    if count != 14622:
        raise ValueError(f'Unexpected normalized source triangle count: {count}')
    right = np.array([.78, 0, .625]); right /= np.linalg.norm(right)
    up = np.array([-.24, .925, .3]); up -= right * np.dot(up, right); up /= np.linalg.norm(up)
    basis = np.array([right, up, np.cross(right, up)])
    for path in textures:
        relative = path.relative_to(args.main_root / 'assets/derived').as_posix()
        if digest(path) != source_lock[relative]:
            raise ValueError(f'Normalized texture source changed: {path}')
    portrait = render(meshes, (1836, 864), basis)
    source_dir = out / 'source'; source_dir.mkdir(parents=True, exist_ok=True)
    portrait.save(source_dir / 'mcrn_corvette_portrait_master.png')
    mask, coords = silhouette(meshes, (1000, 480))
    mask.save(source_dir / 'mcrn_corvette_silhouette_master.png')
    with (source_dir / 'mcrn_corvette_silhouette.svg').open('w') as stream:
        stream.write('<svg xmlns="http://www.w3.org/2000/svg" width="1000" height="480" viewBox="0 0 1000 480">\n<title>Actual Tachi orthographic projected geometry; editable triangle silhouettes</title><g fill="white">\n')
        for triangle in coords:
            stream.write('<polygon points="' + ' '.join(f'{x:.3f},{y:.3f}' for x, y in triangle) + '"/>\n')
        stream.write('</g></svg>\n')
    records = []; patches = []; brush_records = []
    texdir, brushdir = out / 'generated/textures', out / 'generated/brushes'
    texdir.mkdir(parents=True, exist_ok=True); brushdir.mkdir(parents=True, exist_ok=True)
    for role in ROLES:
        name = f'{PREFIX}_{role}'
        brush = {'supported_dpis': [150, 200], 'normal_state': {'texture': name}}
        jsonschema.Draft7Validator(schema).validate(brush)
        write(brushdir / (name + '.brush'), brush)
        brush_records.append({'file': str(brushdir / (name + '.brush')), 'schema': str(args.sdk / 'json_schemas/brush-schema.json'), 'status': 'PASS', 'texture': name, 'supported_dpis': [150, 200], 'resolved_pngs': [str(texdir / f'{name}{suffix}.png') for suffix in ('', '150', '200')]})
        for dpi, suffix in [(100, ''), (150, '150'), (200, '200')]:
            original = args.game / 'textures' / f'trader_light_frigate_{role}{suffix}.png'
            stock = Image.open(original)
            size = stock.size
            if role.startswith('main_view_icon'):
                multiplier = 8
                base_size = tuple(x * multiplier for x in Image.open(args.game / 'textures' / f'trader_light_frigate_main_view_icon{suffix}.png').size)
                small = mask.resize(base_size, Image.Resampling.LANCZOS)
                destination_size = tuple(x * multiplier for x in size)
                iconmask = Image.new('L', destination_size)
                iconmask.paste(small, ((destination_size[0] - base_size[0]) // 2, (destination_size[1] - base_size[1]) // 2))
                if role != 'main_view_icon':
                    radius = round((1.15 if role.endswith('_selected') and not role.endswith('_sub_selected') else 2.1) * dpi / 100 * multiplier)
                    wide = iconmask.filter(ImageFilter.MaxFilter(radius * 2 + 1))
                    inner = iconmask.filter(ImageFilter.MaxFilter(max(3, radius // 2 * 2 + 1)))
                    outline = np.asarray(wide).astype(np.int16) - np.asarray(inner).astype(np.int16)
                    iconmask = Image.fromarray(np.maximum(np.asarray(iconmask), np.clip(outline, 0, 255).astype(np.uint8)))
                sprite = Image.new('RGBA', destination_size, (245, 248, 252, 0)); sprite.putalpha(iconmask)
                sprite = sprite.resize(size, Image.Resampling.LANCZOS)
            else:
                scaled = portrait.copy(); scaled.thumbnail(size, Image.Resampling.LANCZOS)
                sprite = Image.new('RGBA', size); sprite.alpha_composite(scaled, ((size[0] - scaled.width) // 2, (size[1] - scaled.height) // 2))
                if role == 'hud_picture':
                    # Match the opaque stock HUD strip, keeping focus on the ship.
                    yy, xx = np.mgrid[:size[1], :size[0]]
                    glow = np.exp(-((xx / size[0] - .5) ** 2 * 5 + (yy / size[1] - .5) ** 2 * 6))
                    background = np.zeros((size[1], size[0], 4), dtype=np.uint8)
                    for channel, low, high in [(0, 10, 10), (1, 16, 12), (2, 24, 18)]:
                        background[:, :, channel] = low + glow * high
                    background[:, :, 3] = 255
                    base = Image.fromarray(background); base.alpha_composite(sprite); sprite = base
            path = texdir / f'{name}{suffix}.png'; sprite.save(path)
            assert sprite.mode == 'RGBA' and sprite.size == stock.size
            assert sprite.getbbox() and (sprite.getextrema()[3] == (255, 255) if role == 'hud_picture' else sprite.getextrema()[3][0] == 0)
            records.append({'role': role, 'dpi': dpi, 'stock_file': str(original), 'stock_sha256': digest(original), 'generated': str(path), 'generated_sha256': digest(path), 'dimensions': list(size), 'mode': sprite.mode, 'alpha_extrema': list(sprite.getextrema()[3])})
    skin = json.loads((args.game / 'entities/trader_light_frigate.unit_skin').read_text())
    gui_roles = {'hud_icon': 'hud_icon', 'hud_monochrome_icon': 'main_view_icon', 'hud_picture': 'hud_picture', 'tooltip_picture': 'tooltip_picture'}
    for key, role in gui_roles.items():
        patches.append({'pointer': f'/skin_stages/0/gui/{key}', 'old': skin['skin_stages'][0]['gui'][key], 'value': f'{PREFIX}_{role}'})
    for key, role in [('icon', 'main_view_icon'), ('selected_icon', 'main_view_icon_selected'), ('sub_selected_icon', 'main_view_icon_sub_selected')]:
        patches.append({'pointer': f'/skin_stages/0/main_view_icon/{key}', 'old': skin['skin_stages'][0]['main_view_icon'][key], 'value': f'{PREFIX}_{role}'})
    logo_metadata = {}
    logo_example = args.sdk / 'examples/mods/super_fast_trader_scout_corvette'
    for logo in ('mod_small_logo.png', 'mod_large_logo.png'):
        example = logo_example / logo
        size = Image.open(example).size
        scaled = portrait.copy(); scaled.thumbnail(size, Image.Resampling.LANCZOS)
        image = Image.new('RGBA', size, '#101b29'); image.alpha_composite(scaled, ((size[0] - scaled.width) // 2, (size[1] - scaled.height) // 2))
        path = out / 'generated' / logo; image.save(path)
        logo_metadata[logo] = {'generated': str(path), 'sha256': digest(path), 'dimensions': list(size), 'example': str(example), 'example_sha256': digest(example)}
    write(out / 'integration-spec.json', {'root_files_to_copy': ['mod_small_logo.png', 'mod_large_logo.png'], 'logos': {'small_logo': 'mod_small_logo.png', 'large_logo': 'mod_large_logo.png'}, 'metadata_example_path': str(logo_example / '.mod_meta_data'), 'format': 'Integrator metadata; do not package this file', 'unit_skin': 'entities/trader_light_frigate.unit_skin', 'patches': patches, 'copy_generated_subdirectories': ['brushes', 'textures'], 'entity_manifests_required': [], 'scope': 'All users of overridden Cobalt skin, including applicable garrison/neutral users; no UI global overrides', 'runtime': 'NOT RUN'})
    recipe = {'source': str(source), 'source_sha256': digest(source), 'source_buffer_sha256': digest(source.parent / 'scene.bin'), 'triangles': count, 'camera_basis': basis.tolist(), 'portrait_master_size': [1836, 864], 'portrait_fill_fraction': .9, 'lighting': 'Double-sided absolute Lambert ambient0.38/diffuse0.62; source baseColor UV samples; studio gamma lift0.65/exposure1.05 for small UI readability; opaque hull alpha ignored according to glTF alphaMode', 'alpha': 'Opaque materials force alpha255; source alpha decals use cutoff0.5. HUD strip opaque gradient. Other sprites transparent RGBA.', 'silhouette': 'Orthographic +Z right/+X up union of actual source triangles; no culling; no invented geometry', 'ui_format_evidence': str(args.sdk / 'README.md') + ':73; UI stays PNG', 'texture_sources': {str(p): digest(p) for p in textures}, 'runtime': 'NOT RUN'}
    write(source_dir / 'render-recipe.json', recipe)
    write(out / 'ui-validation.json', {'status': 'PASS', 'source_triangles': count, 'source_checkpoint_hashes': 'PASS (normalized glTF/buffer and referenced textures)', 'pinned_brush_schema_hash': 'PASS', 'brush_schema_pass_count': len(ROLES), 'brush_checks': brush_records, 'png_dimensions_alpha_pass_count': len(records), 'sprites': records, 'logos': logo_metadata, 'runtime': 'NOT RUN'})
    contact = Image.new('RGBA', (1050, 950), '#0c131c'); draw = ImageDraw.Draw(contact)
    y = 20
    for role in ROLES:
        sprite = Image.open(texdir / f'{PREFIX}_{role}200.png')
        if role == 'tooltip_picture':
            sprite.thumbnail((810, 380))
        contact.alpha_composite(sprite, (20, y)); draw.text((830, y + 3), role, fill='white')
        y += sprite.height + 24
    contact.convert('RGB').save(out / 'ui-contact-sheet.png')
    print(json.dumps({'status': 'PASS', 'triangles': count, 'sprites': len(records), 'brushes': len(ROLES), 'output': str(out), 'runtime': 'NOT RUN'}))


if __name__ == '__main__':
    main()
