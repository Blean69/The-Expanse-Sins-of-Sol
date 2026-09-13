"""Self-contained optional0.4 variant using the extracted Amun torpedo appearance."""
from pathlib import Path
import argparse, copy, json, shutil, zipfile
from build_combat04 import ROOT, frozen, schema_references, binary_geometry
from build_polish import write, cp
from validate_experiments import read, require, sha256, file_hashes, tree_hash, verify_zip, provenance
from common import read_mesh

ID='expanse_rocinante04_amun'
BASE=ROOT/'build/experiments/expanse_rocinante04'

def main(a):
    frozen(a.game,a.sdk)
    require(sha256(BASE.with_suffix('.zip'))==read(ROOT/'audit/combat04/package-summary.json')['zip_sha256'],'Completed0.4 changed')
    require(tree_hash(file_hashes(BASE))==read(ROOT/'audit/combat04/package-summary.json')['tree_sha256'],'Completed0.4 tree changed')
    spec_path=a.worker/'audit/torpedo05-b/integration-spec.json'
    require(spec_path.is_file(),'Missing reviewed torpedo handoff: '+str(spec_path))
    spec=read(spec_path);require(spec['status']=='COMPLETE OFFLINE APPEARANCE CANDIDATE; RUNTIME NOT RUN','Torpedo compiler gates incomplete')
    for item in [spec['material']]+spec['textures']:
        require(sha256(item['path'])==item['sha256'],'Reviewed torpedo material/texture drift')
    inputs=a.worker/'build/torpedo05-b/game';require(inputs.is_dir(),'Missing ignored game assets: '+str(inputs))
    checks=read(a.worker/'audit/torpedo05-b/output-validation.json');item=checks['outputs']['amun_torpedo']
    require(checks['status']=='PASS OFFLINE ONLY' and checks['triangle_total']==1600,'Incomplete torpedo checks')
    require(sha256(item['mesh'])==item['sha256'] and item['only_tangent_fields_changed'] and item['trailer_sha256_before']==item['trailer_sha256_after'] and item['orthogonal_fallback_vertex_count']==0,'Unsafe or changed torpedo mesh')
    meta=read(a.worker/'audit/torpedo05-b/mount-metadata.json')
    for p,h in meta['source_hashes'].items():require(sha256(p)==h,'Torpedo editable source drift')
    mesh=read_mesh(Path(item['mesh']));out=ROOT/'build/experiments'/ID
    unit=read(BASE/'entities/expanse04_light_torpedo.unit');old_radius=unit['spatial']['radius']
    # Retain the established collision box, which encloses the new shape.
    require(all(abs(mesh['box'][i]-unit['spatial']['box']['center'][i])+mesh['box'][i+3]<=unit['spatial']['box']['extents'][i]+1e-5 for i in range(3)),'New shape exceeds retained Javelis box')
    unit['spatial']['radius']=max(old_radius,mesh['sphere'][3])
    skin=read(BASE/'entities/expanse04_light_torpedo.unit_skin');skin['skin_stages'][0]['unit_mesh']['mesh']='expanse05_amun_torpedo'
    source_record=ROOT/'audit/torpedo05/packaged-asset-sources.md'
    require(source_record.is_file(),'Missing package attribution snapshot')
    if not a.validate_only:
        require(not out.exists() and not out.with_suffix('.zip').exists(),'Refusing existing optional variant')
        shutil.copytree(BASE,out)
        for p in inputs.rglob('*'):
            if p.is_file():cp(p,out/p.relative_to(inputs))
        write(out/'entities/expanse04_light_torpedo.unit',unit);write(out/'entities/expanse04_light_torpedo.unit_skin',skin)
        metadata=read(out/'.mod_meta_data');metadata.update(display_name='The Expanse — Rocinante 0.4 + Amun Torpedo APPEARANCE',display_version='0.4.1',short_description='Complete0.4 experiment with the extracted Amun torpedo appearance.',long_description='Load alone instead of0.4. Same Martian health, damage, ammo and movement; only private projectile mesh/materials and minimally enlarged enclosing sphere change. This is not the Amun stealth ship. Cloak, stronger Amun weapons and boarding remain separate candidates; runtime tests pending.')
        write(out/'.mod_meta_data',metadata);cp(source_record,out/'ASSET-SOURCES.md')
    require(read(out/'entities/expanse04_light_torpedo.unit')==unit,'Unexpected health/physics/gameplay change')
    require(read(out/'entities/expanse04_light_torpedo.unit_skin')==skin,'Unexpected projectile skin change')
    require(sha256(out/'ASSET-SOURCES.md')==sha256(source_record),'Attribution drift')
    previous=file_hashes(BASE);now=file_hashes(out);generated=file_hashes(inputs)
    allowed={'.mod_meta_data','ASSET-SOURCES.md','entities/expanse04_light_torpedo.unit','entities/expanse04_light_torpedo.unit_skin'}
    require(not set(previous)-set(now) and set(now)-set(previous)==set(generated),'Unexpected package contents')
    for p,h in previous.items():
        if p not in allowed:require(now[p]==h,'Unrelated0.4 file changed: '+p)
    for p,h in generated.items():require(now[p]==h,'Generated torpedo asset drift: '+p)
    geometry=binary_geometry(out/'meshes/expanse05_amun_torpedo.mesh');require(geometry['triangles']==1600,'Wrong geometry')
    report,resolver=schema_references(out,a.game,a.sdk)
    report.update(status='PASS OFFLINE ONLY',runtime='NOT RUN',geometry=geometry,unchanged_health=unit['health'],bounds={'retained_box':unit['spatial']['box'],'old_radius':old_radius,'new_radius':unit['spatial']['radius']},all_other_04_files_byte_preserved=True)
    report['preservation']=frozen(a.game,a.sdk);write(ROOT/'audit/torpedo05/package-validation.json',report)
    if not a.validate_only:
        with zipfile.ZipFile(out.with_suffix('.zip'),'w',zipfile.ZIP_DEFLATED) as z:
            for p in sorted(out.rglob('*')):
                if p.is_file():
                    info=zipfile.ZipInfo(p.relative_to(out).as_posix(),(2026,9,12,0,0,0));info.compress_type=zipfile.ZIP_DEFLATED;info.external_attr=0o100644<<16;z.writestr(info,p.read_bytes())
    summary={'mod_id':ID,**verify_zip(out.with_suffix('.zip'),out),'schemas':report['schemas'],'runtime':'NOT RUN','installed':False}
    write(ROOT/'audit/torpedo05/package-summary.json',summary)
    deps=[BASE,inputs,a.worker/'audit/torpedo05-b',source_record]
    write(out.with_suffix('.dependencies.json'),[str(p.resolve()) for p in deps]);write(out.with_suffix('.provenance.json'),provenance(out.with_suffix('.zip'),ROOT,deps))
    print(json.dumps(summary,indent=2))

if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__)
    for k in ['game','sdk','worker']:p.add_argument('--'+k,type=Path,required=True)
    p.add_argument('--validate-only',action='store_true');main(p.parse_args())
