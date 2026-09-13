"""Build a separate0.19 balance/fleet candidate from frozen0.18. No install/push."""
from pathlib import Path
import argparse,copy,json,shutil,zipfile
from build_polish import write
from validate_experiments import read,require,file_hashes,tree_hash,sha256,verify_zip,verify_pins,provenance
from update19_balance import changes as balance_changes,BASE,GAME,ROOT
from update19_ships import changes as ship_changes,EUROPA,ARTEMIS
from build_amun06 import manifests

OUT=ROOT/'build/experiments/expanse_update19'
AUD=ROOT/'audit/update19'
SDK=GAME.parent/'Sins of a Solar Empire II - Mod Tools'
PLAYERS=['trader_loyalist','trader_rebel','dlc_trader_loyalist','expanse18_unn','expanse18_mcrn','expanse18_opa']

def preservation():
    d=read(AUD/'checkpoint.json')
    require(sha256(BASE.with_suffix('.zip'))==d['zip_sha256'],'Rollback ZIP changed')
    require(tree_hash(file_hashes(BASE))==d['tree_sha256'],'Rollback tree changed')
    return {'rollback':d,'pins':verify_pins(ROOT,GAME,SDK)}

def inputs():
    d=read(AUD/'integration-inputs.json')
    for part in d.values():
        m=read(ROOT/part['metadata']);require(m['status'].startswith('PASS'),'Art incomplete')
        hashes=m.get('game_file_hashes',m.get('compiled_files',m.get('files')))
        require(hashes,'Missing reviewed art hashes')
        for rel,h in hashes.items():require(sha256(ROOT/part['game']/rel)==h,'Art drift '+rel)
    return d

def definitions():
    paths=inputs();m={k:read(ROOT/v['metadata']) for k,v in paths.items()}
    ui={k:read(ROOT/v['ui']) for k,v in paths.items() if v.get('ui')}
    edits,report=balance_changes()
    private,loc,origins=ship_changes(edits,m['europa'],m['artemis'],m['le_guin'],ui['artemis'],ui['le_guin'])
    edits.update(private);edits['localized_text/en.localized_text'].update(loc)
    for ident in PLAYERS:
        rel='entities/'+ident+'.player';d=read(BASE/rel)
        require(EUROPA not in d['buildable_units'] and ARTEMIS not in d['buildable_units'],'Already registered')
        d['buildable_units'] += [EUROPA,ARTEMIS];edits[rel]=d
    meta=read(BASE/'.mod_meta_data');meta.update(display_name='The Expanse — 0.19 FLEET BALANCE',display_version='0.19.0',short_description='Balanced shared fleet, Europa\'s Bane, Artemis and Le Guin recovery wrecks.',long_description='TEST CANDIDATE: three shared faction identities and the small Sol map retained. Standardized PDCs, slower railguns, faster double-damage torpedoes with30-second fuel. Europa pirate frigate, Artemis native salvage tender/trade visual, Le Guin native derelict visual. Load alone with identical ZIP on every client. Offline validated; runtime, save/reload, and multiplayer remain unverified; existing Windows PDC sound confirmed by user. Full Sol, Tycho and advanced salvage/composite prototypes remain excluded.')
    edits['.mod_meta_data']=meta
    return edits,origins,report

def build():
    preservation();require(not OUT.exists() and not OUT.with_suffix('.zip').exists(),'Existing0.19 candidate')
    edits,origins,report=definitions();shutil.copytree(BASE,OUT,symlinks=True)
    art_files={}
    for part in inputs().values():
        game=ROOT/part['game']
        for rel,h in file_hashes(game).items():
            require(not (OUT/rel).exists(),'Asset name collision '+rel)
            dst=OUT/rel;dst.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(game/rel,dst);art_files[rel]=h
    for rel,d in edits.items():write(OUT/rel,d)
    manifests(OUT,GAME)
    shutil.copy2(ROOT/'docs/update19.md',OUT/'PLAYTEST-README.md')
    with (OUT/'ASSET-SOURCES.md').open('a') as f:f.write('\n\n'+(ROOT/'docs/update19-assets.md').read_text())
    write(AUD/'build-record.json',{'definition_files':sorted(edits),'originals':origins,'art_files':art_files,'runtime':'NOT RUN'})
    write(AUD/'balance.json',report)

def main(a):
    if not (a.validate_only or a.package_existing):build()
    from update19_validate import validate
    result=validate();write(AUD/'package-validation.json',result)
    if a.validate_only:print('PASS OFFLINE0.19');return
    zpath=OUT.with_suffix('.zip');require(not zpath.exists(),'Existing candidate ZIP')
    with zipfile.ZipFile(zpath,'w',zipfile.ZIP_DEFLATED,compresslevel=9) as z:
        for p in sorted(OUT.rglob('*')):
            if p.is_file():
                require(not p.is_symlink(),'Symlink in package')
                zi=zipfile.ZipInfo(p.relative_to(OUT).as_posix(),(2026,9,13,0,0,0));zi.compress_type=zipfile.ZIP_DEFLATED;zi.external_attr=0o100644<<16;z.writestr(zi,p.read_bytes())
    summary={'mod_id':OUT.name,'version':'0.19.0',**verify_zip(zpath,OUT),'installed':False,'runtime':'NOT RUN'}
    write(AUD/'package-summary.json',summary);OUT.with_suffix('.sha256').write_text(summary['zip_sha256']+'  '+zpath.name+'\n')
    deps=[BASE,ROOT/'build/update19-europa/game',ROOT/'build/update19-haulers/artemis/game',ROOT/'build/update19-haulers/le_guin/game',ROOT/'docs/update19.md']
    write(OUT.with_suffix('.provenance.json'),provenance(zpath,ROOT,deps));print(json.dumps(summary,indent=2))

if __name__=='__main__':
    p=argparse.ArgumentParser();g=p.add_mutually_exclusive_group();g.add_argument('--validate-only',action='store_true');g.add_argument('--package-existing',action='store_true');main(p.parse_args())
