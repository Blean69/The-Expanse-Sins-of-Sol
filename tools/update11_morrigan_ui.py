"""Render actual selected Morrigan hull and mounted equipment into static game UI.
Editable/rendered source stays separate from standalone game UI PNGs/brushes.
"""
from pathlib import Path
import argparse
import hashlib
import json
import numpy as np
from PIL import Image, ImageDraw, ImageFilter
import jsonschema
from common import Gltf
from polish_ui import render, silhouette, digest, write, ROLES


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--source',type=Path,required=True)
    parser.add_argument('--expected-triangles',type=int,required=True)
    parser.add_argument('--compiler-z',action='store_true',help='Explicitly undo B compiler input Z reflection')
    parser.add_argument('--game',type=Path,required=True)
    parser.add_argument('--sdk',type=Path,required=True)
    args=parser.parse_args()
    root=Path(__file__).resolve().parents[1];out=root/'build/update11-c/ui';generated=out/'generated';source_dir=out/'source'
    if out.exists():raise FileExistsError('Refusing to overwrite existing UI derivative: '+str(out))
    if not args.source.is_file():raise FileNotFoundError('Missing actual selected Morrigan source: '+str(args.source))
    asset=Gltf(args.source);meshes=[];texture_cache={};deps={str(args.source):digest(args.source)};triangle_count=0
    for buffer in asset.g['buffers']:
        path=args.source.parent/buffer['uri'];deps[str(path)]=digest(path)
    for index,node in enumerate(asset.g['nodes']):
        if 'mesh' not in node or index not in asset.world:continue
        for primitive in asset.g['meshes'][node['mesh']]['primitives']:
            indices=asset.accessor(primitive['indices']).reshape(-1,3)
            positions=asset.positions(index,primitive)
            if args.compiler_z:positions[:,2]*=-1 # explicit compiler-input convention
            triangles=positions[indices]
            material=asset.g['materials'][primitive['material']];pbr=material.get('pbrMetallicRoughness')
            if pbr is None:raise ValueError('Source material has no verified PBR color definition')
            if 'baseColorTexture' in pbr:
                texdef=asset.g['textures'][pbr['baseColorTexture']['index']];im=asset.g['images'][texdef['source']];color_path=args.source.parent/im['uri']
                if not color_path.is_file():raise FileNotFoundError('Missing actual Morrigan material color: '+str(color_path))
                deps[str(color_path)]=digest(color_path)
                if str(color_path) not in texture_cache:texture_cache[str(color_path)]=np.asarray(Image.open(color_path).convert('RGBA'))
                tex=texture_cache[str(color_path)]
                uv=asset.accessor(primitive['attributes']['TEXCOORD_0'])[indices]
            else:
                if 'baseColorFactor'not in pbr:raise ValueError('Missing explicit material color')
                tex=np.full((1,1,4),255,dtype=np.uint8);uv=np.zeros((len(triangles),3,2))
            meshes.append((triangles,uv,tex,pbr.get('baseColorFactor',[1,1,1,1]),material.get('alphaMode','OPAQUE')));triangle_count+=len(triangles)
    if triangle_count!=args.expected_triangles:raise ValueError('Unexpected selected Morrigan source geometry count: '+str(triangle_count))
    right=np.array([.78,0,.625]);right/=np.linalg.norm(right)
    up=np.array([-.24,.925,.3]);up-=right*np.dot(up,right);up/=np.linalg.norm(up)
    basis=np.array([right,up,np.cross(right,up)])
    portrait=render(meshes,(1836,864),basis)
    source_dir.mkdir(parents=True,exist_ok=True);portrait.save(source_dir/'morrigan_portrait_master.png')
    mask,coords=silhouette(meshes,(1000,480));mask.save(source_dir/'morrigan_silhouette_master.png')
    with (source_dir/'morrigan_silhouette.svg').open('w') as stream:
        stream.write('<svg xmlns="http://www.w3.org/2000/svg" width="1000" height="480" viewBox="0 0 1000 480"><title>Actual Morrigan selected mesh projected triangle silhouette</title><g fill="white">\n')
        for tri in coords:stream.write('<polygon points="'+' '.join(f'{x:.3f},{y:.3f}' for x,y in tri)+'"/>\n')
        stream.write('</g></svg>\n')
    texdir=generated/'textures';brushdir=generated/'brushes';texdir.mkdir(parents=True,exist_ok=True);brushdir.mkdir(parents=True,exist_ok=True)
    schema_path=args.sdk/'json_schemas/brush-schema.json';raw=schema_path.read_bytes()
    blob=hashlib.sha1(b'blob '+str(len(raw)).encode()+b'\0'+raw).hexdigest()
    if blob!='3e2e9a9c47b6ced821bd2b2ebb9e09f66d390c9f':raise ValueError('Brush schema differs from pinned8e061033 revision')
    schema=json.loads(raw);png_checks=[];brush_checks=[]
    for role in ROLES:
        name='expanse11_morrigan_'+role;brush={'supported_dpis':[150,200],'normal_state':{'texture':name}}
        jsonschema.Draft7Validator(schema).validate(brush);write(brushdir/(name+'.brush'),brush)
        brush_checks.append({'file':str(brushdir/(name+'.brush')),'status':'PASS','texture':name,'dpi_suffixes':['','150','200']})
        for dpi,suffix in [(100,''),(150,'150'),(200,'200')]:
            original=args.game/'textures'/f'trader_light_frigate_{role}{suffix}.png';size=Image.open(original).size
            if role.startswith('main_view_icon'):
                multiplier=8;base_size=tuple(x*multiplier for x in Image.open(args.game/'textures'/f'trader_light_frigate_main_view_icon{suffix}.png').size);large_size=tuple(x*multiplier for x in size)
                small=mask.resize(base_size,Image.Resampling.LANCZOS);iconmask=Image.new('L',large_size);iconmask.paste(small,((large_size[0]-base_size[0])//2,(large_size[1]-base_size[1])//2))
                if role!='main_view_icon':
                    radius=round((2.1 if role.endswith('_sub_selected') else 1.15)*dpi/100*multiplier)
                    wide=iconmask.filter(ImageFilter.MaxFilter(radius*2+1));inner=iconmask.filter(ImageFilter.MaxFilter(max(3,radius//2*2+1)))
                    outline=np.asarray(wide).astype(np.int16)-np.asarray(inner).astype(np.int16);iconmask=Image.fromarray(np.maximum(np.asarray(iconmask),np.clip(outline,0,255).astype(np.uint8)))
                sprite=Image.new('RGBA',large_size,(245,248,252,0));sprite.putalpha(iconmask);sprite=sprite.resize(size,Image.Resampling.LANCZOS)
            else:
                scaled=portrait.copy();scaled.thumbnail(size,Image.Resampling.LANCZOS)
                sprite=Image.new('RGBA',size,(0,0,0,0) if role!='hud_picture' else (14,23,35,255));sprite.alpha_composite(scaled,((size[0]-scaled.width)//2,(size[1]-scaled.height)//2))
            path=texdir/(name+suffix+'.png');sprite.save(path)
            assert sprite.mode=='RGBA' and sprite.size==size and sprite.getbbox()
            alpha=sprite.getextrema()[3];assert alpha==(255,255) if role=='hud_picture' else alpha[0]==0
            png_checks.append({'file':str(path),'sha256':digest(path),'dimensions':list(size),'mode':sprite.mode,'alpha_extrema':list(alpha),'size_reference':str(original)})
    logos={}
    for kind in ('small','large'):
        example=args.sdk/f'examples/mods/super_fast_trader_scout_corvette/mod_{kind}_logo.png';size=Image.open(example).size
        scaled=portrait.copy();scaled.thumbnail(size,Image.Resampling.LANCZOS);logo=Image.new('RGBA',size,(14,23,35,255));logo.alpha_composite(scaled,((size[0]-scaled.width)//2,(size[1]-scaled.height)//2));name=f'expanse11_morrigan_mod_{kind}_logo.png';logo.save(generated/name);logos[kind+'_logo']=name
        png_checks.append({'file':str(generated/name),'sha256':digest(generated/name),'dimensions':list(size),'mode':logo.mode,'alpha_extrema':list(logo.getextrema()[3]),'size_reference':str(example)})
    patches=[]
    for key,role in {'hud_icon':'hud_icon','hud_monochrome_icon':'main_view_icon','hud_picture':'hud_picture','tooltip_picture':'tooltip_picture'}.items():patches.append({'pointer':'/skin_stages/0/gui/'+key,'value':'expanse11_morrigan_'+role})
    for key,role in [('icon','main_view_icon'),('selected_icon','main_view_icon_selected'),('sub_selected_icon','main_view_icon_sub_selected')]:patches.append({'pointer':'/skin_stages/0/main_view_icon/'+key,'value':'expanse11_morrigan_'+role})
    for path,sha in deps.items():
        if digest(path)!=sha:raise ValueError('Morrigan source changed during render: '+path)
    metadata={'game_directory':str(generated),'status':'PASS OFFLINE UI','logos':logos,'source':'Actual selected Morrigan final active source geometry; no other ship imagery','copy_generated_subdirectories':['brushes','textures'],'optional_root_logos':logos,'skin_patches':patches,'entity_manifests_required':[],'runtime':'NOT RUN'}
    write(out/'integration-spec.json',metadata)
    recipe={'source_dependencies':deps,'triangles':triangle_count,'coordinate_conversion':'Undo compiler input Z reflection' if args.compiler_z else 'Source already uses game-facing right-handed glTF axes','camera_basis':basis.tolist(),'material_colors':'Actual source material base-color texture and UVs, or explicit source PBR factor; no invented colors','renderer':'Imported generic CPU double-sided z-buffer from polish_ui.py; studio contrast lift and Lambert shading; not Sins runtime rendering','runtime':'NOT RUN'}
    write(source_dir/'render-recipe.json',recipe)
    validation={'status':'PASS','pinned_brush_schema_blob':blob,'source_dependencies':deps,'triangles':triangle_count,'brush_schema_checks':brush_checks,'png_checks':png_checks,'runtime':'NOT RUN'};write(out/'ui-validation.json',validation)
    canvas=Image.new('RGBA',(1050,1100),(12,19,28,255));draw=ImageDraw.Draw(canvas);y=20
    for role in ROLES:
        sprite=Image.open(texdir/f'expanse11_morrigan_{role}200.png')
        if role=='tooltip_picture':sprite.thumbnail((810,380))
        canvas.alpha_composite(sprite,(20,y));draw.text((830,y+3),role,fill='white');y+=sprite.height+24
    canvas.convert('RGB').save(out/'morrigan-ui-contact-sheet.png')
    audit=root/'audit/update11-c';write(audit/'ui-validation.json',validation);write(audit/'ui-integration-spec.json',metadata);write(audit/'ui-render-recipe.json',recipe)
    print(json.dumps({'status':'PASS','triangles':triangle_count,'brushes':6,'png_files':len(png_checks),'output':str(out),'runtime':'NOT RUN'}))


if __name__=='__main__':main()
