"""Freeze a repair-only follow-up without modifying 0.27 or installed mods."""
import argparse,shutil,json
from common import ROOT,read,write
from validate_experiments import require,sha256
from doctrine_package import package,registries
from update27_1_runtime import changes,check

def build(sandbox=False):
    suffix='_sandbox' if sandbox else '';base=ROOT/'build/experiments'/('expanse_update27'+suffix);out=ROOT/'build/experiments'/('expanse_update27_1'+suffix);audit=ROOT/'audit'/('update27_1'+suffix);readme=ROOT/'docs/update27_1.md'
    require(not out.with_suffix('.zip').exists(),'Frozen repair candidate already exists')
    edits,origins,report=changes(base);write(audit/'repairs.json',report)
    meta=read(base/'.mod_meta_data');meta.update(display_version='0.27.1',display_name='The Expanse — 0.27.1 Runtime Repair'+(' Sandbox — Combined Roster' if sandbox else ''),short_description='Repairs tag overflow, starbase-item eligibility, turret sockets and missing level-up effects.',long_description='Repair-only cumulative package over 0.27. Restores the 30-entry native unit-tag budget and existing equipment filters. Adds missing PDC render sockets without geometry changes; supplies required level-up effects on Dark Star/OPA command. No balance/audio changes. '+('Deliberately combined roster. ' if sandbox else 'Normal faction access. ')+'Post-repair runtime, save/reload and multiplayer remain untested. Start a fresh game; the overflow affected the old session during loading.')
    edits['.mod_meta_data']=meta;art={};replacements={}
    manifest=read(ROOT/'audit/update27_1/socket-repair.json')
    for row in manifest['files']:
        rel=row['path'];src=ROOT/'build/update27_1-sockets/game'/rel
        require(sha256(src)==row['sha256'] and sha256(base/rel)==row['previous_sha256'],'Socket art predecessor mismatch '+rel)
        art[rel]=src;replacements[rel]=row['previous_sha256']
    if not out.exists():shutil.copytree(base,out,symlinks=True)
    for rel,d in edits.items():write(out/rel,d)
    for rel,src in art.items():shutil.copy2(src,out/rel)
    registries(out);shutil.copy2(readme,out/'PLAYTEST-README.md')
    write(audit/'acceptance-check.json',check(out,base))
    return package(base,out,edits,origins,readme,audit,art,package_existing=True,art_replacements=replacements)
if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--sandbox',action='store_true');a=p.parse_args();print(json.dumps(build(a.sandbox),indent=2))
