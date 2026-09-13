"""Assemble the one supported shared-tree friends playtest; never install/enable."""
from pathlib import Path
import argparse,copy,json,shutil,zipfile
from build_polish import write,cp
from build_amun06 import manifests,patch_pointer
from validate_experiments import read,require,sha256,file_hashes,compare_tree,verify_pins,verify_zip,provenance
from update11_validate import schema_check
from amun06_validate_package import AmunResolver,check_action_values
from build_combat03 import check_actions
from update15_shared import apply as shared,PLAYERS,INSTALLATION
from update15_truman_gameplay import apply as truman
from update15_research import apply as research
ROOT=Path(__file__).resolve().parents[1]
BASE=ROOT/'build/experiments/expanse_update14'
OUT=ROOT/'build/experiments/expanse_update15'
AUD=ROOT/'audit/update15'
GAME=ROOT.parent/'SteamLibrary/steamapps/common/Sins2'
SDK=GAME.parent/'Sins of a Solar Empire II - Mod Tools'
WORKERS=ROOT.parent/'expanse-workers'

def preservation():
    c=read(AUD/'checkpoint.json')
    trees=[compare_tree(t)for t in c['trees']]
    for p,h in {**c['zips'],**c['originals']}.items():require(sha256(p)==h,'Frozen input changed '+p)
    return {'trees':trees,'pins':verify_pins(ROOT,GAME,SDK),'enabled_settings_unchanged':sha256(c['enabled_path'])==c['enabled_sha256'],'settings_note':'Read only; user may change selected mods during their concurrent testing.'}

def build():
    require(not OUT.exists() and not OUT.with_suffix('.zip').exists(),'Refusing existing0.15')
    preservation()
    sci=WORKERS/'playtest15-scirocco/build/update15-scirocco/integration-recipe.json'
    tm=WORKERS/'playtest15-truman/audit/update15-truman/integration-spec.json'
    tu=tm.with_name('ui-integration-spec.json')
    recipe,meta,ui=map(read,[sci,tm,tu])
    require(all(d['status'].startswith('PASS')for d in [recipe,meta,ui]),'Worker incomplete')
    shutil.copytree(BASE,OUT)
    for name in recipe['entity_files']:cp(Path(recipe['resource_directory'])/'entities'/name,OUT/'entities'/name)
    for p in recipe['patches']:
        d=read(OUT/p['file']);require(d['abilities'][0]['abilities']==p['before'],'Scirocco baseline changed')
        patch_pointer(d,p['pointer'],p['value']);write(OUT/p['file'],d)
    loc=read(OUT/'localized_text/en.localized_text');loc.update(recipe['localization']);write(OUT/'localized_text/en.localized_text',loc)
    shared(OUT,GAME);truman(OUT,GAME,BASE,meta,ui)
    # Freeze the concrete pre-research definitions for independent delta checks.
    write(AUD/'before-research-definitions.json',{p.name:read(p)for p in (OUT/'entities').iterdir()if p.suffix in ['.unit','.weapon','.ability','.action_data_source']})
    write(AUD/'local-audit-dependencies.json',{str(p):sha256(p)for p in [AUD/'before-research-definitions.json',tm.with_name('components.json')]})
    research(OUT,GAME,AUD/'research')
    manifests(OUT,GAME)
    info=read(OUT/'.mod_meta_data');info.update(display_name='The Expanse — 0.15 FRIENDS PLAYTEST',display_version='0.15.0',short_description='Shared TEC tree: bounded Scirocco support, themed research, UNN Truman and trade escorts.',long_description='Load alone. Supported faction: TEC Enclave. Includes complete0.14 fleet/music. Offline validated; runtime/save/multiplayer checks pending. No strategic weapon or optional shield item.')
    write(OUT/'.mod_meta_data',info)
    (OUT/'ASSET-SOURCES.md').write_text((ROOT/'ASSET-SOURCES.md').read_text())
    write(AUD/'integration-inputs.json',{'scirocco':str(sci),'truman':str(tm),'truman_ui':str(tu)})
    deps=[sci,tm,tu]+[p for directory in [Path(meta['game_directory']),Path(ui['game_directory'])]for p in directory.rglob('*')if p.is_file()]
    deps += [Path(recipe['resource_directory'])/'entities'/n for n in recipe['entity_files']]
    write(AUD/'reviewed-inputs.json',{str(p):sha256(p)for p in deps})

def validate():
    before,after=file_hashes(BASE),file_hashes(OUT)
    for p,h in read(AUD/'local-audit-dependencies.json').items():require(sha256(p)==h,'Local audit input changed '+p)
    require(set(before)<=set(after),'Baseline file deleted')
    for p,h in read(AUD/'reviewed-inputs.json').items():require(sha256(p)==h,'Reviewed worker input changed: '+p)
    # Explicitly preserve every baseline unit except the Scirocco ability list.
    kept=[]
    for p in (BASE/'entities').glob('*.unit'):
        a,b=read(p),read(OUT/'entities'/p.name)
        if p.stem=='expanse12_scirocco':a['abilities']=b['abilities']
        require(a==b,'Existing ship fields changed '+p.name);kept.append(p.name)
    for p in (BASE/'entities').glob('*.weapon'):require(sha256(p)==sha256(OUT/'entities'/p.name),'Existing weapon changed '+p.name)
    for rel,h in before.items():
        if rel.startswith(('meshes/','textures/','sounds/','effects/')):require(after[rel]==h,'Playable art/audio/effect changed '+rel)
    from update15_contracts import run as check_contracts
    write(AUD/'contract-checks.json',check_contracts())
    truman_contract=read(read(AUD/'integration-inputs.json')['truman'])
    assembled=read(OUT/'entities/expanse15_truman.unit')
    require(assembled['weapons']['weapons']==[r['mount']for r in truman_contract['rigs']],'Truman mounts differ from ray-tested contract')
    for r in truman_contract['rigs']:
        w=read(OUT/'entities'/(r['mount']['weapon']+'.weapon'))
        require(w['turret']==r['turret_override'] and w['yaw_firing_tolerance']==w['pitch_firing_tolerance']==1.,'Truman turret/tolerance contract')
    for p,h in read(ROOT/'audit/update15-truman/handoff-files.json')['resources'].items():
        require(sha256(p)==h,'Final worker resource changed '+p)
        src=Path(p)
        rel=src.relative_to(Path(truman_contract['game_directory'])) if src.is_relative_to(Path(truman_contract['game_directory'])) else src.relative_to(Path(read(read(AUD/'integration-inputs.json')['truman_ui'])['game_directory']))
        require(sha256(OUT/rel)==h,'Final resource not copied exactly '+str(rel))
    schemas=[]
    overrides={'expanse15_truman.unit':BASE/'entities/trader_battle_capital_ship.unit',INSTALLATION+'.unit':BASE/'entities/trader_gauss_defense_structure.unit','expanse15_unn_light_torpedo.unit':BASE/'entities/expanse04_light_torpedo.unit',INSTALLATION+'.unit_skin':GAME/'entities/trader_gauss_defense_structure.unit_skin','expanse15_truman.unit_skin':BASE/'entities/expanse12_scirocco.unit_skin','expanse15_unn_light_torpedo.unit_skin':BASE/'entities/expanse04_light_torpedo.unit_skin'}
    for rel,h in after.items():
        if before.get(rel)==h:continue
        p=OUT/rel;s=schema_check(p,overrides.get(p.name,BASE/rel if (BASE/rel).exists() else None))
        if s:schemas.append(s)
    resolver=AmunResolver(OUT,GAME);graphs={}
    names=['trader_light_frigate','expanse12_raptor','expanse12_pella','expanse12_scirocco','trader_scout_corvette','expanse_donnager_battleship','expanse_mcrn_corvette','expanse_rocinante_hero','expanse_amun_ra','expanse15_truman',INSTALLATION]
    for n in names:
        u=resolver.unit(n,'0.15 combined package')
        graphs[n]={'graph':check_actions(OUT,resolver,n),'typed':check_action_values(OUT,GAME,resolver,u)}
    # Production must never depend on the quarantined lab or optional shields.
    for p in (OUT/'entities').iterdir():
        if p.is_file():require('expanse15_lab_'not in p.read_text() and 'expanse15_adaptive'not in p.read_text(),'Experimental reference in production')
    return {'status':'PASS OFFLINE ONLY','runtime':'NOT RUN','schemas':schemas,'preserved_baseline_units':kept,'preserved_baseline_weapons':len(list((BASE/'entities').glob('*.weapon'))),'references':resolver.edges,'ability_graphs':graphs,'new_files':sorted(set(after)-set(before)),'changed_files':sorted(p for p in before if before[p]!=after[p]),'preservation':preservation()}

def main(a):
    if not(a.validate_only or a.package_existing):build()
    write(AUD/'package-validation.json',validate())
    if a.validate_only:print('PASS OFFLINE; runtime NOT RUN');return
    archive=OUT.with_suffix('.zip');require(not archive.exists(),'Existing archive')
    with zipfile.ZipFile(archive,'w',zipfile.ZIP_DEFLATED)as z:
        for p in sorted(OUT.rglob('*')):
            if p.is_file():
                zi=zipfile.ZipInfo(p.relative_to(OUT).as_posix(),(2026,9,13,0,0,0));zi.compress_type=zipfile.ZIP_DEFLATED;zi.external_attr=0o100644<<16;z.writestr(zi,p.read_bytes())
    result={'mod_id':OUT.name,**verify_zip(archive,OUT),'installed':False,'runtime':'NOT RUN'}
    write(AUD/'package-summary.json',result)
    deps=[BASE,AUD/'integration-inputs.json',AUD/'reviewed-inputs.json']
    write(OUT.with_suffix('.dependencies.json'),list(map(str,deps)));write(OUT.with_suffix('.provenance.json'),provenance(archive,ROOT,deps))
    print(json.dumps(result,indent=2))
if __name__=='__main__':
    ap=argparse.ArgumentParser();g=ap.add_mutually_exclusive_group();g.add_argument('--validate-only',action='store_true');g.add_argument('--package-existing',action='store_true');main(ap.parse_args())
