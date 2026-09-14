"""Frozen Stage 1 candidate: supply, role correction and bounded ability control."""
from pathlib import Path
import argparse, json, shutil, zipfile
from build_polish import write
from validate_experiments import read, require, file_hashes, tree_hash, sha256, verify_zip, verify_pins
from update20_fleet import ROOT, BASE, GAME, changes as fleet, balance_report, NAMES
from update20_abilities import changes as abilities
from build_amun06 import manifests

OUT=ROOT/'build/experiments/expanse_update20'
AUD=ROOT/'audit/update20'
SDK=GAME.parent/'Sins of a Solar Empire II - Mod Tools'

def definitions():
    edits,loc,acquisition=fleet()
    ae,al,ar=abilities(BASE)
    require(not set(edits)&set(ae),'Worker ownership conflict')
    edits.update(ae); loc.update(al)
    text=read(BASE/'localized_text/en.localized_text');text.update(loc)
    edits['localized_text/en.localized_text']=text
    meta=read(BASE/'.mod_meta_data')
    meta.update(display_name='The Expanse — 0.20 FLEET DOCTRINE STAGE 1',display_version='0.20.0',
        short_description='2,000-supply fleet roles, repair autocast and guarded boarding.',
        long_description='Separate Stage 1 candidate over 0.19 Fleet Balance. Morrigan 40 supply / 88.2 PDC DPS; Tachi 95 supply / 400 metal. Repair autocast starts enabled at 80% hull. Boarding starts manual with a shared target lock and 30% hull threshold. Read PLAYTEST-README for edge-case limitations. Shared factions and the small Sol map retained. Offline checked; game load, behavior, save/reload and multiplayer NOT RUN. Load alone; all clients need identical package and 1x supply.')
    edits['.mod_meta_data']=meta
    return edits,acquisition,ar

def preservation():
    snap=read(AUD/'checkpoint.json')
    require(sha256(BASE.with_suffix('.zip'))==snap['package']['zip_sha256'],'Rollback ZIP changed')
    require(tree_hash(file_hashes(BASE))==snap['package']['tree_sha256'],'Rollback tree changed')
    return verify_pins(ROOT,GAME,SDK)

def validate():
    from update11_validate import schema_check
    from amun06_validate_package import AmunResolver,check_action_values
    from build_combat03 import check_actions
    from flight03_effects import changed_paths
    import jsonschema
    pins=preservation();edits,acquisition,ar=definitions()
    before,after=file_hashes(BASE),file_hashes(OUT)
    require(set(before)<=set(after),'Deleted baseline file')
    registry={'entities/'+k+'.entity_manifest' for k in ['unit','unit_skin','weapon','ability','buff','action_data_source']}
    allowed=set(edits)|registry|{'PLAYTEST-README.md','FLEET-COMPARISONS.md'}
    require(all(r in allowed for r,h in after.items() if h!=before.get(r)),'Unreviewed package change')
    schemas=[]
    for rel,d in edits.items():
        require(read(OUT/rel)==d,'Definition drift '+rel)
        old=BASE/rel
        result=schema_check(OUT/rel,old if old.exists() else None)
        if result:schemas.append(result)
    uniform=read(OUT/'uniforms/player.uniforms')
    sch=read(SDK/'json_schemas/player-uniforms-schema.json')
    for k,v in uniform.items():jsonschema.validate(v,sch['properties'][k])
    # Supply/pricing are the only changes to existing hulls. Rigs, survivability,
    # research, physics, cap accounting and construction times remain exact.
    deltas={}
    for p in (BASE/'entities').glob('*.unit'):
        rel='entities/'+p.name;a,b=read(p),read(OUT/rel)
        paths=set(changed_paths(a,b));allowed_paths={'/build/supply_cost','/build/price/metal'}
        require(paths<=allowed_paths,'Unrequested hull change '+p.name+str(paths));deltas[p.stem]=sorted(paths)
    protected=[r for r in before if r.endswith(('.ogg','.sound','.mesh','.mesh_material','.dds','.research_subject','.player')) or 'railgun' in r or 'magazine' in r or ('torpedo' in r and r.startswith('entities/')) or r.startswith('scenarios/')]
    for rel in protected:require(after[rel]==before[rel],'Preserved behavior/asset changed '+rel)
    for rel in registry:
        ids=read(OUT/rel)['ids'];require(len(ids)==len(set(ids)),'Duplicate registration')
        for ident in ids:require((OUT/'entities'/f'{ident}.{Path(rel).stem}').exists(),'Missing registered entity')
    resolver=AmunResolver(OUT,GAME);actions=[]
    for ident in NAMES:
        u=resolver.unit(ident,'0.20 Stage 1')
        actions.append({'unit':ident,'actions':check_actions(OUT,resolver,ident),'values':check_action_values(OUT,GAME,resolver,u)})
    require(read(OUT/'entities/expanse20_boarding_target_lock.buff')['stacking_ownership_type']=='for_all_players','Lock is not shared')
    require(after['PLAYTEST-README.md']==sha256(ROOT/'docs/update20.md'),'README mismatch')
    write(AUD/'fleet-arithmetic.json',balance_report(edits));write(AUD/'acquisition.json',acquisition);write(AUD/'ability-integration.json',ar)
    return {'status':'PASS OFFLINE ONLY','schemas':schemas,'actions':actions,'unit_deltas':deltas,
        'preserved_files_checked':len(protected),'pins':pins,'file_count':len(after),
        'runtime':{k:'NOT RUN' for k in ['load','research_existing_and_new','repair_autocast','boarding_shared_lock','capture_supply','save_reload','multiplayer','combat_comparisons']},
        'known_limitations':ar['cancellation']}

def main():
    p=argparse.ArgumentParser();p.add_argument('--validate-only',action='store_true');p.add_argument('--package-existing',action='store_true');a=p.parse_args()
    if not (a.validate_only or a.package_existing):
        preservation();require(not OUT.exists() and not OUT.with_suffix('.zip').exists(),'Existing 0.20 candidate; preserve it')
        edits,_,_=definitions();shutil.copytree(BASE,OUT,symlinks=True)
        for rel,d in edits.items():write(OUT/rel,d)
        manifests(OUT,GAME)
        shutil.copy2(ROOT/'docs/update20.md',OUT/'PLAYTEST-README.md')
        shutil.copy2(ROOT/'docs/update20-fleet-comparisons.md',OUT/'FLEET-COMPARISONS.md')
    result=validate();write(AUD/'package-validation.json',result)
    if a.validate_only:print('PASS OFFLINE 0.20');return
    zp=OUT.with_suffix('.zip');require(not zp.exists(),'Existing package ZIP')
    with zipfile.ZipFile(zp,'w',zipfile.ZIP_DEFLATED,compresslevel=9) as z:
        for f in sorted(OUT.rglob('*')):
            if f.is_file():
                require(not f.is_symlink(),'Symlink in package')
                zi=zipfile.ZipInfo(f.relative_to(OUT).as_posix(),(2026,9,14,0,0,0));zi.compress_type=zipfile.ZIP_DEFLATED;zi.external_attr=0o100644<<16;z.writestr(zi,f.read_bytes())
    summary={'version':'0.20.0','stage':1,**verify_zip(zp,OUT),'installed':False,'runtime':'NOT RUN'}
    write(AUD/'package-summary.json',summary);OUT.with_suffix('.sha256').write_text(summary['zip_sha256']+'  '+zp.name+'\n')
    print(json.dumps(summary,indent=2))

if __name__=='__main__':main()
