"""Integrate reviewed private hull recipes into one faction playtest release."""
import argparse,copy,json,shutil
from pathlib import Path
from update20_fleet import ROOT,GAME
from validate_experiments import read,require,sha256
from build_polish import write
from doctrine_package import package,registries
from update27_earth_gameplay import changes as earth_changes
from update27_opa_gameplay import changes as opa_changes
from update27_mars_gameplay import changes as mars_changes
from update27_storm_patch import changes as storm_changes
from update27_access import changes as access_changes,SHIPS
from update27_fixes import changes as fix_changes
from update27_ui import generate,apply_skin

def gather_art(base):
    """Copy explicit hashed regular files only; never traverse SDK Wine roots."""
    rows={};out=ROOT/'build/update27-art/game'
    def add(rel,p,h,previous=None):
        require(not Path(rel).is_absolute() and '..' not in Path(rel).parts,'Unsafe art member')
        p=Path(p);require(p.is_file() and not p.is_symlink() and sha256(p)==h,'Art hash mismatch '+str(p))
        if rel.startswith('entities/'):return # always regenerate definitions against selected base
        if (base/rel).exists() and sha256(base/rel)==h:return
        if (base/rel).exists():require(previous==sha256(base/rel),'Unapproved predecessor '+rel)
        if rel in rows:require(rows[rel]['sha256']==h,'Conflicting worker art '+rel);return
        dst=out/rel;dst.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(p,dst)
        rows[rel]={'source':str(dst),'sha256':h,'previous_sha256':previous,'worker_source':str(p)}
    manifest=read(ROOT/'audit/update27-earth/game-files-sha256.json')
    earth=read(ROOT/'audit/update27-earth/gameplay-contract.json')
    for rel,h in manifest.items():add(rel,Path(earth['art_directory'])/rel,h)
    manifest=read(ROOT/'audit/update27-opa/compiled-art-manifest.json')
    opa=read(ROOT/'audit/update27-opa/gameplay-contract.json')
    for rel,h in {**manifest['files'],**manifest.get('ui_files',{})}.items():add(rel,opa['art_files'][rel],h)
    for name in ('hephaestus','laconia','storm'):
        manifest=read(ROOT/'audit/update27-mars-laconia'/(name+'-manifest.json'))
        for row in manifest['files']:
            if row['action']=='reuse':
                donor=base/row['path'] if (base/row['path']).exists() else GAME/row['path']
                require(donor.is_file() and sha256(donor)==row['sha256'],'Reused donor dependency drift '+row['path'])
                continue
            add(row['path'],Path(manifest['artifact_root'])/row['path'],row['sha256'],row['previous_sha256'])
    write(ROOT/'audit/update27/art-inputs.json',{'files':rows,'source':'Explicit reviewed worker manifests; local-only paid derivatives.'})
    return rows

def definitions(base,sandbox=False):
    edits={};loc={};origins={};reports={}
    for label,fn in [('earth',earth_changes),('opa',opa_changes),('mars',mars_changes),('storm',storm_changes)]:
        e,l,o,r=fn(base);require(not set(e)&set(edits),'Private definition collision '+label)
        edits.update(e);loc.update(l);origins.update(o);reports[label]=r
    a=read(ROOT/'audit/update27/art-inputs.json')['files'];art={rel:Path(row['source']) for rel,row in a.items()};replacements={rel:row['previous_sha256'] for rel,row in a.items() if row['previous_sha256']}
    for rel,row in a.items():require(sha256(art[rel])==row['sha256'],'Reviewed art changed '+rel)
    # Portraits follow actual reviewed hull geometry instead of donor ships.
    e,uiart=generate(ROOT/'audit/update27-mars-laconia');edits.update(e);art.update(uiart)
    for unit,portrait in [('expanse27_hephaestus','expanse27_hephaestus'),('expanse27_laconia_frigate','expanse27_laconia_frigate'),('expanse24_gathering_storm','expanse27_gathering_storm')]:
        rel='entities/'+unit+'.unit_skin';edits[rel]=apply_skin(edits[rel],portrait)
    e,l,o,r=access_changes(base,edits,sandbox);edits.update(e);loc.update(l);origins.update(o);reports['access']=r
    for n in SHIPS:
        d=edits['entities/'+n+'_procurement.research_subject']
        d.update(hud_icon=n+'_hud_icon',tooltip_icon=n+'_hud_icon',tooltip_picture=n+'_tooltip_picture')
    d=edits['entities/expanse24_gathering_storm_procurement.research_subject'];d.update(hud_icon='expanse27_gathering_storm_hud_icon',tooltip_icon='expanse27_gathering_storm_hud_icon',tooltip_picture='expanse27_gathering_storm_tooltip_picture')
    e,l,r=fix_changes(base,edits);edits.update(e);loc.update(l);reports['runtime_repairs']=r
    text=read(base/'localized_text/en.localized_text');text.update(loc);edits['localized_text/en.localized_text']=text
    meta=read(base/'.mod_meta_data');meta.update(display_name='The Expanse —0.27 Fleet Expansion'+(' Sandbox — Combined Roster' if sandbox else ''),display_version='0.27.0',short_description='Five new hulls, faction procurement, OPA Laconian access and model/error repairs.',long_description='Cumulative local candidate over frozen0.26. UNN Nathan Hale/Munroe; MCRN Hephaestus; OPA Dark Star/Laconian frigate and Gathering Storm. New white Behemoth, connected Storm drive, required scenario fields and passive GUI/fixed-axis repairs. Civilian research and accepted global combat/audio values preserved. '+('Combined roster is deliberately available to every faction. ' if sandbox else 'Regular faction rosters enforced. ')+'New runtime and multiplayer testing not performed. Composite currency lab remains separate; no plating implementation.')
    edits['.mod_meta_data']=meta
    # Only existing Storm launch positions change; no ammo, damage, cadence,
    # targeting or reload data can pass through this narrowly checked exception.
    rel='entities/expanse24_gathering_storm_light_magazine.ability';mag_positions={rel:sha256(base/rel)}
    return edits,origins,art,replacements,mag_positions,reports

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--sandbox',action='store_true');p.add_argument('--gather-art',action='store_true');a=p.parse_args()
    suffix='_sandbox' if a.sandbox else '';base=ROOT/'build/experiments'/('expanse_update26'+suffix);out=ROOT/'build/experiments'/('expanse_update27'+suffix);audit=ROOT/'audit'/('update27'+suffix)
    require(not out.with_suffix('.zip').exists(),'Frozen candidate already exists')
    if a.gather_art:gather_art(base)
    edits,origins,art,replacements,mag_positions,reports=definitions(base,a.sandbox);write(audit/'integration.json',reports)
    # Stage and run independent behavioral wiring checks before freezing ZIP.
    if not out.exists():shutil.copytree(base,out,symlinks=True)
    for rel,src in art.items():
        if (base/rel).exists():require(rel in replacements and sha256(base/rel)==replacements[rel],'Unapproved art overwrite')
        dest=out/rel;dest.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(src,dest)
    for rel,d in edits.items():write(out/rel,d)
    registries(out);shutil.copy2(ROOT/'docs/update27.md',out/'PLAYTEST-README.md')
    from check_update27 import run
    run(suffix)
    print(json.dumps(package(base,out,edits,origins,ROOT/'docs/update27.md',audit,art,True,art_replacements=replacements,magazine_position_replacements=mag_positions),indent=2))
