"""Build independent local mods with explicit file allowlists. Never edits the game."""
from common import *
import argparse, shutil, zipfile, hashlib
import copy, jsonschema

def zip_mod(out):
    with zipfile.ZipFile(out.with_suffix('.zip'),'w',zipfile.ZIP_DEFLATED) as z:
        for p in sorted(out.rglob('*')):
            if p.is_file(): z.write(p,p.relative_to(out))

def verify_install():
    for name,data in read(ROOT/'audit/installed-file-hashes.json').items():
        assert hashlib.sha256((GAME/name).read_bytes()).hexdigest()==data['sha256'], 'Installed file changed: '+name
    for x in read(ROOT/'audit/schema-comparison.json')['files']:
        b=(SDK/x['path']).read_bytes();h=hashlib.sha1(b'blob '+str(len(b)).encode()+b'\0'+b).hexdigest()
        assert h==x['official_git_blob'], 'SDK changed: '+x['path']

def name_only():
    out=ROOT/'build/expanse_cobalt_name';out.mkdir(parents=True,exist_ok=True)
    loc=read(ROOT/'src/name-only/en.localized_text');vanilla=read(GAME/'localized_text/en.localized_text')
    assert set(loc)=={'trader_light_frigate_name','trader_light_frigate_description'}
    assert all(k in vanilla and isinstance(v,str) for k,v in loc.items())
    write(out/'localized_text/en.localized_text',loc)
    shutil.copy2(ROOT/'src/name-only/.mod_meta_data',out/'.mod_meta_data')
    assert sorted(str(p.relative_to(out)) for p in out.rglob('*') if p.is_file())==['.mod_meta_data','localized_text/en.localized_text']
    zip_mod(out); print('Built',out)

def visual():
    out=ROOT/'build/expanse_corvette_visual';out.mkdir(parents=True,exist_ok=True)
    unit=read(GAME/'entities/trader_light_frigate.unit');skin=read(GAME/'entities/trader_light_frigate.unit_skin')
    original_unit=copy.deepcopy(unit);original_skin=copy.deepcopy(skin)
    info=read(ROOT/'build/compiler-json/mcrn_corvette_baseline.mesh_json')
    assert len(info['vertex_indices'])//3==14622
    points=[x['position'] for x in info['points'] if x['name']=='weapon.0']
    expected=read(ROOT/'audit/derivative-transform.json')['muzzles'];assert np.allclose(points,expected,atol=1e-5)
    assert max(np.linalg.norm(x['p']) for x in info['non_skinned_vertices'])<=unit['spatial']['radius'], 'Visual exceeds vanilla radius'
    unit['weapons']['weapons'][0]['non_turret_muzzle_positions']=points
    unit['weapons']['weapons'][0]['weapon_position']=np.mean(points,axis=0).tolist()
    skin['skin_stages'][0]['unit_mesh']['mesh']='mcrn_corvette_baseline'
    for obj,schema in [(unit,'unit-schema.json'),(skin,'unit-skin-schema.json')]:
        jsonschema.Draft7Validator(read(SDK/'json_schemas'/schema)).validate(obj)
    # Only these visual mounting coordinates may differ in the unit.
    restored=copy.deepcopy(unit)
    for key in ['weapon_position','non_turret_muzzle_positions']:
        restored['weapons']['weapons'][0][key]=original_unit['weapons']['weapons'][0][key]
    assert restored==original_unit
    restored=copy.deepcopy(skin);restored['skin_stages'][0]['unit_mesh']['mesh']=original_skin['skin_stages'][0]['unit_mesh']['mesh'];assert restored==original_skin
    write(out/'entities/trader_light_frigate.unit',unit);write(out/'entities/trader_light_frigate.unit_skin',skin)
    write(out/'localized_text/en.localized_text',read(ROOT/'src/name-only/en.localized_text'))
    shutil.copy2(ROOT/'src/name-only/.mod_meta_data',out/'.mod_meta_data')
    (out/'meshes').mkdir(exist_ok=True);shutil.copy2(ROOT/'build/compiler-binary/mcrn_corvette_baseline.mesh',out/'meshes/mcrn_corvette_baseline.mesh')
    for name in info['materials']:
        short=name.removeprefix('mcrn_corvette_baseline_')
        material=read(ROOT/'assets/derived/baseline/game-materials'/(short+'.mesh_material'))
        write(out/'mesh_materials'/(name+'.mesh_material'),material)
        for key,value in material.items():
            if key.endswith('_texture'):
                target=out/'textures'/(value+'.dds');target.parent.mkdir(exist_ok=True);shutil.copy2(ROOT/'build/converted-textures'/(value+'.dds'),target)
    assert not list(out.rglob('*.weapon')), 'Baseline must inherit all vanilla weapons'
    # Include credit with the distributable, without shipping the original package.
    shutil.copy2(ROOT/'ASSET-SOURCES.md',out/'ASSET-SOURCES.md')
    zip_mod(out)
    write(ROOT/'audit/baseline-validation.json',{'unit_schema':'passed','skin_schema':'passed','exact_gameplay_comparison':'passed; only two mount coordinate fields differ','weapon_definitions_overridden':0,'triangles':len(info['vertex_indices'])//3,'six_pdc_assemblies':'retained geometry; static baseline','in_game_test':'NOT RUN','visual_radius':info['bounding_sphere']['radius'],'vanilla_radius':unit['spatial']['radius'],'output_files':sorted(str(p.relative_to(out)) for p in out.rglob('*') if p.is_file())})
    print('Built',out)

if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('mode',choices=['name','visual','verify']);args=parser.parse_args()
    verify_install()
    if args.mode=='name':name_only()
    if args.mode=='visual':visual()
    print('Installed reference hashes and all 62 current SDK schema hashes unchanged.')
