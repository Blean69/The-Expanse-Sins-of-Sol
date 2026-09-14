"""Freeze a load-repair control and optional menu variant, never install."""
import json,shutil
from common import ROOT,read,write
from validate_experiments import require,sha256,file_hashes
from doctrine_package import package,registries
from update27_3_loadfixes import changes,check
BASE=ROOT/'build/experiments/expanse_update27_1'
OUT=ROOT/'build/experiments/expanse_update27_3'
AUD=ROOT/'audit/update27_3'
DOC=ROOT/'docs/update27_3.md'

def stage(base,out,edits,art,doc):
    require(not out.with_suffix('.zip').exists(),'Candidate frozen '+str(out))
    if not out.exists():shutil.copytree(base,out,symlinks=True)
    for rel,d in edits.items():write(out/rel,d)
    for rel,p in art.items():
        (out/rel).parent.mkdir(parents=True,exist_ok=True);shutil.copy2(p,out/rel)
    registries(out);shutil.copy2(doc,out/'PLAYTEST-README.md')

def build():
    require(not OUT.with_suffix('.zip').exists(),'Repair already frozen')
    edits,art,replacements,levels=changes(BASE,AUD,ROOT/'build/update27_3-art')
    meta=read(BASE/'.mod_meta_data');meta.update(display_version='0.27.3',display_name='The Expanse — 0.27.3 Load Repair',short_description='Load error fixes, complete railgun muzzle sockets, preserved fleet balance.',long_description='Cumulative repair over 0.27.1. Correct research action levels, Behemoth engine role, finite Tycho item and Foehammer build clearance; add missing gimbal muzzle sockets without changing geometry. User-reported all-ships crash not yet reproduced or confirmed fixed. Enable alone. Optional menu variant is separate.')
    edits['.mod_meta_data']=meta;stage(BASE,OUT,edits,art,DOC)
    write(AUD/'acceptance-check.json',check(OUT))
    result=package(BASE,OUT,edits,{},DOC,AUD,art,package_existing=True,art_replacements=replacements,action_level_replacements=levels)
    print('Repair:',json.dumps(result),flush=True)
    return result

def menu():
    import build_menu27_2 as scene
    out=ROOT/'build/experiments/expanse_update27_3_menu';audit=ROOT/'audit/menu27_3';doc=ROOT/'docs/menu27_3.md'
    require(not out.with_suffix('.zip').exists(),'Menu already frozen')
    scene.BASE=OUT;scene.AUD=audit;scene.ART=ROOT/'build/menu27_3-art'
    edits,origins,art=scene.prepare()
    meta=read(OUT/'.mod_meta_data');meta.update(display_name='The Expanse — 0.27.3 MENU BATTLE',short_description='0.27.3 load repairs plus twelve-ship MCRN versus UNN menu battle.',long_description='Standalone cumulative optional menu variant. Same match files as 0.27.3 Load Repair; twelve isolated display ships use the existing scene camera, patrol and respawn logic. No scene copies in player build lists. Engine visual/runtime confirmation pending. Enable this OR regular 0.27.3, never both. Restart after changing mods.')
    edits['.mod_meta_data']=meta;stage(OUT,out,edits,art,doc)
    original=file_hashes(OUT);unchanged=[]
    for rel,h in original.items():
        if rel in ['.mod_meta_data','PLAYTEST-README.md'] or rel.endswith('.entity_manifest'):continue
        require(sha256(out/rel)==h,'Menu changed match content '+rel);unchanged.append(rel)
    clones=set(read(audit/'scene-audit.json')['private_units'])
    for p in (out/'entities').glob('*.player'):
        require(not any('"'+n+'"' in p.read_text() for n in clones),'Menu acquisition leak')
    write(audit/'acceptance-check.json',{**check(out),'regular_content_files_unchanged':len(unchanged),'menu_runtime':'NOT RUN','private_units_absent_from_player_lists':len(clones)})
    result=package(OUT,out,edits,origins,doc,audit,art,package_existing=True)
    print('Menu:',json.dumps(result),flush=True)
    return result
if __name__=='__main__':
    import sys
    if '--menu-only' not in sys.argv:build()
    menu()
