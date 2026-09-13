"""Build/validate a separate combined0.4 package. Never install or enable it."""
from pathlib import Path
import argparse, copy, json, math, shutil, struct, zipfile
import numpy as np
import jsonschema
from build_polish import write, cp
from build_hero03 import ability_positions, fixed_mount
from build_combat03 import check_actions
from flight03_effects import scale_effect
from validate_experiments import read, require, sha256, file_hashes, compare_tree, verify_pins, verify_zip, provenance, Resolver, strings

ROOT=Path(__file__).resolve().parents[1]
ID='expanse_rocinante04'
HERO='expanse_rocinante_hero'
BASE=ROOT/'build/experiments/expanse_rocinante03'

def frozen(game,sdk):
    checkpoint=read(ROOT/'audit/combat04/checkpoint.json')
    trees=[compare_tree(r) for r in checkpoint['trees']]
    for p,h in checkpoint['packages'].items():require(sha256(p)==h,'Frozen package changed: '+p)
    enabled=checkpoint['enabled_mods'];require(sha256(enabled['path'])==enabled['sha256'],'Enabled mod settings changed')
    old=read(ROOT/'audit/experiments/checkpoint.json')
    for r in old['shared_read_only_inputs'].values():compare_tree(r)
    return {'pins':verify_pins(ROOT,game,sdk),'preserved_trees':trees,'enabled_settings_unchanged':True}

def phase_plume(game,nozzle):
    phase=scale_effect(read(game/'effects/exhaust_tech_medium_01.particle_effect'),1.5,6.0,blue=True)
    f=np.array(nozzle['forward']);f=f/np.linalg.norm(f)
    require(f[2]<-.99,'Unexpected aft exhaust axis')
    yaw=math.atan2(f[0],f[2]);pitch=-math.asin(f[1])
    for node in phase['nodes']:
        require(node['x']==[0,0] and node['y']==[0,0] and all(node[k]==[0,0] for k in ['yaw','pitch','roll']),'Unsupported nonaxial effect')
        positions=[np.array(nozzle['position'])+z*f for z in node['z']]
        for axis,index in [('x',0),('y',1),('z',2)]:node[axis]=sorted(float(p[index]) for p in positions)
        node['yaw']=[yaw,yaw];node['pitch']=[pitch,pitch]
    return phase

def binary_geometry(path):
    b=path.read_bytes();count=struct.unpack_from('<Q',b,53)[0];offset=61;rows=[]
    for _ in range(count):
        v=struct.unpack_from('<12f?',b,offset);offset+=49+(8 if v[-1] else 0);rows.append(v[:-1])
    v=np.array(rows);ni=struct.unpack_from('<Q',b,offset)[0];offset+=8
    idx=np.frombuffer(b,dtype='<u4',count=ni,offset=offset).reshape(-1,3)
    require(np.isfinite(v).all() and idx.max()<len(v),'Invalid geometry')
    n=v[:,3:6];t=v[:,6:9]
    require(np.max(np.abs((n*t).sum(1)))<2e-5 and np.max(np.abs(np.linalg.norm(t,axis=1)-1))<2e-5,'Invalid tangent frame')
    tri=v[:,:3][idx];face=np.cross(tri[:,1]-tri[:,0],tri[:,2]-tri[:,0]);normal=n[idx].mean(1)
    align=(face*normal).sum(1)/np.maximum(np.linalg.norm(face,axis=1)*np.linalg.norm(normal,axis=1),1e-15)
    require(not (align < -1e-5).any(),'Opposed winding')
    return {'mesh':path.name,'triangles':len(idx),'sha256':sha256(path),'opposed_winding':0,'invalid_tangent_frames':0}

def schema_references(out,game,sdk):
    types={'.unit':'unit','.unit_skin':'unit-skin','.weapon':'weapon','.ability':'ability','.buff':'buff','.action_data_source':'action-data-source','.player':'player','.brush':'brush'}
    n=0
    for p in out.rglob('*'):
        if p.suffix in types:
            jsonschema.Draft7Validator(read(sdk/'json_schemas'/(types[p.suffix]+'-schema.json'))).validate(read(p));n+=1
    jsonschema.Draft7Validator(read(sdk/'json_schemas/unit-tag-uniforms-schema.json')).validate(read(out/'uniforms/unit_tag.uniforms'));n+=1
    for manifest in (out/'entities').glob('*.entity_manifest'):
        ext=manifest.stem;actual=read(manifest)['ids']
        expected=sorted(p.stem for p in (out/'entities').glob('*.'+ext) if not (game/'entities'/p.name).exists())
        require(actual==expected,'Wrong additive manifest '+ext)
    resolver=Resolver(out,game)
    for p in (out/'entities').glob('*.unit'):resolver.unit(p.stem,'package root')
    for p in (out/'entities').glob('*.unit_skin'):resolver.skin(p.stem,'package root')
    for p in (out/'meshes').glob('*.mesh'):resolver.mesh(p.stem,'package root')
    for p in (out/'mesh_materials').glob('*.mesh_material'):resolver.material(p.stem,'package root')
    actions={u:check_actions(out,resolver,u) for u in ['trader_light_frigate',HERO]}
    for p in (out/'effects').glob('*.particle_effect'):
        for ptr,v in strings(read(p)):
            if ptr[-1].endswith('texture') or ptr[-1] in {'texture_0','texture_1'}:resolver.resolve('textures/'+v+'.dds',p)
    return {'schemas':n,'ability_graphs':actions,'reference_edges':resolver.edges,
            'resolved_dependency_sha256':{p:sha256(p) for p in sorted({e['resolved'] for e in resolver.edges})},
            'limitations':['No pinned particle/material/localization/metadata schema; explicit structure/reference checks only','Schemas and geometry checks do not establish runtime behavior']},resolver

def expected_hero(meta):
    unit=read(BASE/'entities'/f'{HERO}.unit')
    unit['weapons']['weapons']=[copy.deepcopy(r['mount']) for r in meta['rigs']]+[fixed_mount(meta['equipment']['railgun'],'expanse03_hero_railgun','weapon.rail.0',10,10)]
    unit['ai']['attack_target_type_groups_matching_weapon']=meta['rigs'][0]['mount']['weapon']
    return unit

def validate(out,a,meta,equipment,geometry_game):
    from combat04_integrate import validate_package as validate_combat, FILES
    report,resolver=schema_references(out,a.game,a.sdk)
    report['combat']=validate_combat(out,BASE,a.sdk,a.combat/'light-final')
    expected_loc=read(BASE/'localized_text/en.localized_text');expected_loc.update(read(a.combat/'light-final/integration-recipe.json')['localization'])
    require(read(out/'localized_text/en.localized_text')==expected_loc,'Unapproved localization delta')
    require(sha256(out/'ASSET-SOURCES.md')==sha256(ROOT/'audit/combat04/packaged-asset-sources.md'),'Packaged source record changed')
    require(read(out/'entities'/f'{HERO}.unit')==expected_hero(meta),'Unapproved hero stats/navigation/rail/ability change')
    require(sha256(out/'entities/trader_light_frigate.unit')==sha256(BASE/'entities/trader_light_frigate.unit'),'Ordinary navigation/gameplay changed')
    require(len(meta['rigs'])==6 and len({r['mount']['weapon'] for r in meta['rigs']})==6,'Six physical gun budgets required')
    for i,r in enumerate(meta['rigs']):
        expected=read(BASE/'entities'/f'expanse03_roci_pdc_{i}.weapon');expected['turret']=r['turret_override']
        require(read(out/'entities'/(r['mount']['weapon']+'.weapon'))==expected,'Unexpected PDC budget/targeting change')
        hull=resolver.mesh('expanse04_hero_hull','hero mount validation')
        point=next(p for p in hull['meshpoints'] if p['name']==r['mount']['mesh_point']);rot=np.array(point['rotation']).reshape(3,3)
        require(np.allclose(point['position'],r['mount']['weapon_position'],atol=2e-5) and np.allclose(rot[1],r['mount']['up'],atol=2e-5) and np.allclose(rot[2],r['mount']['forward'],atol=2e-5),'Hull point frame mismatch')
        basis=np.array(r['basis_columns']);muzzle=np.array(r['yaw_pivot_hull'])+basis@(np.array(r['turret_override']['barrel_position'])+np.array(r['turret_override']['muzzle_positions'][0]))
        require(np.allclose(muzzle,r['muzzle_hull'],atol=2e-5),'Broken pitch/base/muzzle transform chain')
    for name in ['expanse03_roci_torpedo_magazine','expanse03_hero_torpedo_salvo']:
        expected=read(BASE/'entities'/(name+'.ability'));expected['ability_positions']=ability_positions(equipment['torpedo_ports'])
        require(read(out/'entities'/(name+'.ability'))==expected,'Unexpected ability gameplay change')
    require(read(out/'effects/expanse03_roci_phase_plume.particle_effect')==phase_plume(a.game,equipment['exhaust']),'Wrong phase alignment')
    # Whole-tree allowlist: prevents unrelated baseline, faction and old candidate leakage.
    old=file_hashes(BASE);new=file_hashes(out)
    removed={'entities/expanse03_heavy_torpedo.unit','meshes/expanse03_hero_armed.mesh'}|{f'entities/expanse03_roci_pdc_{i}.weapon' for i in range(6)}
    changed={'.mod_meta_data','ASSET-SOURCES.md','localized_text/en.localized_text','entities/expanse_rocinante_hero.unit','entities/expanse_rocinante_hero.unit_skin','entities/trader_light_frigate.unit_skin','effects/expanse03_roci_phase_plume.particle_effect','entities/expanse03_roci_torpedo_magazine.ability','entities/expanse03_hero_torpedo_salvo.ability'}|{'entities/'+n for n in FILES}|{'entities/'+n+'.entity_manifest' for n in ['weapon','unit','unit_skin']}
    generated=file_hashes(geometry_game)
    additions=set(generated)|{'entities/expanse04_light_torpedo.unit','entities/expanse04_light_torpedo.unit_skin'}|{'entities/'+r['mount']['weapon']+'.weapon' for r in meta['rigs']}
    require(set(old)-set(new)==removed,'Unexpected removals')
    require(set(new)-set(old)==additions-set(old),'Unexpected additions or missing generated assets')
    for name,h in old.items():
        if name not in removed|changed|set(generated):require(new[name]==h,'Unrelated existing file changed: '+name)
    for name,h in generated.items():require(new[name]==h,'Geometry input changed: '+name)
    # Verify exact skin edits, beyond permissive Draft7 unknown-key behavior.
    for ident in ['trader_light_frigate',HERO]:
        expected=read(BASE/'entities'/(ident+'.unit_skin'));stage=expected['skin_stages'][0]
        stage['effects']['effect_alias_bindings'].append(read(a.combat/'light-final/integration-recipe.json')['skin_muzzle_alias'])
        if ident==HERO:
            stage['unit_mesh']['mesh']='expanse04_hero_hull'
            stage['child_mesh_alias_bindings']={'map':[b for r in meta['rigs'] for b in r['skin_alias_map']]}
        require(read(out/'entities'/(ident+'.unit_skin'))==expected,'Unexpected skin edit '+ident)
    bins=[binary_geometry(p) for p in sorted((out/'meshes').glob('expanse04*.mesh'))]
    require(len(bins)==13 and sum(x['triangles'] for x in bins)==meta['triangle_total'],'Incomplete compiled hero')
    report.update(status='PASS OFFLINE ONLY',runtime='NOT RUN',geometry=bins,hero_triangles=meta['triangle_total'],one_budget_per_gun=True,all_other_existing_files_preserved=True)
    return report

def main(a):
    pins=frozen(a.game,a.sdk);out=ROOT/'build/experiments'/ID
    for p in [a.geometry/'audit/geometry04-b/output-validation.json',a.geometry/'audit/geometry04-b/mount-metadata.json',a.combat/'light-final/offline-validation.json']:
        require(p.is_file(),'Missing ignored reviewed dependency: '+str(p))
    meta=read(a.geometry/'audit/geometry04-b/mount-metadata.json');equipment=read(a.geometry/'audit/geometry04-b/equipment.json');meta['equipment']=equipment
    checks=read(a.geometry/'audit/geometry04-b/output-validation.json')
    require(checks['status'].startswith('PASS'),'Geometry offline checks incomplete')
    require(len(checks['outputs'])==13,'Incomplete geometry gate set')
    for item in checks['outputs'].values():
        require(sha256(item['mesh'])==item['sha256'],'Reviewed mesh hash drift')
        require(item['only_tangent_fields_changed'] and item['trailer_sha256_before']==item['trailer_sha256_after'] and item['orthogonal_fallback_vertex_count']==0,'Unsafe compiler repair')
    geometry_game=a.geometry/'build/geometry04-b/game'
    require(geometry_game.is_dir(),'Missing ignored compiled geometry: '+str(geometry_game))
    for item in read(a.combat/'light-final/offline-validation.json')['installed_readonly_evidence'].values():
        p=a.game/item['actual_relative_path'];require(sha256(p)==item['sha256'],'New projectile dependency drift: '+str(p))
    if not a.validate_only:
        require(not out.exists() and not out.with_suffix('.zip').exists(),'Refusing to overwrite existing experiment')
        shutil.copytree(BASE,out)
        for directory in [a.combat/'light-final/entities',a.combat/'integration/entities']:
            for p in directory.iterdir():cp(p,out/'entities'/p.name)
        for p in geometry_game.rglob('*'):
            if p.is_file():cp(p,out/p.relative_to(geometry_game))
        (out/'entities/expanse03_heavy_torpedo.unit').unlink();(out/'meshes/expanse03_hero_armed.mesh').unlink()
        for i,r in enumerate(meta['rigs']):
            old=out/'entities'/f'expanse03_roci_pdc_{i}.weapon';weapon=read(old);weapon['turret']=r['turret_override'];old.unlink()
            write(out/'entities'/(r['mount']['weapon']+'.weapon'),weapon)
        write(out/'entities'/f'{HERO}.unit',expected_hero(meta))
        recipe=read(a.combat/'light-final/integration-recipe.json')
        for ident in ['trader_light_frigate',HERO]:
            p=out/'entities'/(ident+'.unit_skin');skin=read(p);stage=skin['skin_stages'][0]
            stage['effects']['effect_alias_bindings'].append(recipe['skin_muzzle_alias'])
            if ident==HERO:
                stage['unit_mesh']['mesh']='expanse04_hero_hull';stage['child_mesh_alias_bindings']={'map':[b for r in meta['rigs'] for b in r['skin_alias_map']]}
            write(p,skin)
        for name in ['expanse03_roci_torpedo_magazine','expanse03_hero_torpedo_salvo']:
            p=out/'entities'/(name+'.ability');ability=read(p);ability['ability_positions']=ability_positions(equipment['torpedo_ports']);write(p,ability)
        write(out/'effects/expanse03_roci_phase_plume.particle_effect',phase_plume(a.game,equipment['exhaust']))
        for ext in ['weapon','unit','unit_skin']:
            write(out/'entities'/(ext+'.entity_manifest'),{'ids':sorted(p.stem for p in (out/'entities').glob('*.'+ext) if not (a.game/'entities'/p.name).exists())})
        loc=read(out/'localized_text/en.localized_text');loc.update(recipe['localization']);write(out/'localized_text/en.localized_text',loc)
        metadata=read(out/'.mod_meta_data');metadata.update(display_version='0.4.0',display_name='The Expanse — Corvette & Rocinante 0.4 EXPERIMENT',short_description='Compact torpedoes and a repaired Rocinante with six aiming PDC rigs.',long_description='Combined package: load alone. Preserves movement and hero railgun balance. Javelis-sized faster torpedoes; conservative hero hull and six yaw/pitch rigs. Higher-detail unique hero: performance and all new runtime behavior require testing. Donnager groundwork is separate.')
        write(out/'.mod_meta_data',metadata);cp(ROOT/'audit/combat04/packaged-asset-sources.md',out/'ASSET-SOURCES.md')
    report=validate(out,a,meta,equipment,geometry_game);report['preservation']=frozen(a.game,a.sdk)
    write(ROOT/'audit/combat04/package-validation.json',report)
    if not a.validate_only:
        with zipfile.ZipFile(out.with_suffix('.zip'),'w',zipfile.ZIP_DEFLATED) as z:
            for p in sorted(out.rglob('*')):
                if p.is_file():
                    info=zipfile.ZipInfo(p.relative_to(out).as_posix(),(2026,9,12,0,0,0));info.compress_type=zipfile.ZIP_DEFLATED;info.external_attr=0o100644<<16;z.writestr(info,p.read_bytes())
    deps=[BASE,a.geometry/'audit/geometry04-b',geometry_game,a.combat/'light-final',a.combat/'integration']
    write(out.with_suffix('.dependencies.json'),[str(p.resolve()) for p in deps])
    summary={'mod_id':ID,**verify_zip(out.with_suffix('.zip'),out),'runtime':'NOT RUN','installed':False,'schemas':report['schemas'],'hero_triangles':report['hero_triangles']}
    write(ROOT/'audit/combat04/package-summary.json',summary)
    write(out.with_suffix('.provenance.json'),provenance(out.with_suffix('.zip'),ROOT,deps));print(json.dumps(summary,indent=2))

if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__)
    for k in ['game','sdk','geometry','combat']:p.add_argument('--'+k,type=Path,required=True)
    p.add_argument('--validate-only',action='store_true')
    main(p.parse_args())
