"""Separate new-hull prototype over completed Stage3 foundations."""
import argparse,json
from update20_fleet import ROOT
from update21_factions import FACTIONS,WRAPPERS
from update23_murphy import changes
from doctrine_package import package
from validate_experiments import read
from build_polish import write
if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--sandbox',action='store_true');p.add_argument('--package-existing',action='store_true');a=p.parse_args()
    suffix='_sandbox' if a.sandbox else '';base=ROOT/'build/experiments'/('expanse_update22'+suffix);out=ROOT/'build/experiments'/('expanse_update23'+suffix);audit=ROOT/'audit'/('update23'+suffix)
    edits,loc,origins,art,r=changes(base);tags=read(base/'uniforms/unit_tag.uniforms');tags['unit_tags']+=r['unit_tag_entries_append'];edits['uniforms/unit_tag.uniforms']=tags
    for owner,faction in {**{v:k for k,v in FACTIONS.items()},**WRAPPERS}.items():
        if a.sandbox or faction in r['factions']:
            rel='entities/'+owner+'.player';d=read(base/rel);d['buildable_units'].append(r['unit']);edits[rel]=d
    text=read(base/'localized_text/en.localized_text');text.update(loc);edits['localized_text/en.localized_text']=text
    meta=read(base/'.mod_meta_data');meta.update(display_name='The Expanse — 0.23.1 Murphy '+('Sandbox' if a.sandbox else 'Prototype'),display_version='0.23.1',short_description='Separate UNN escort addition over Stage3.',long_description='Adds one UNN Murphy escort with compiled fan hull, four tracking PDCs, bounded fore/aft light rails and existing UNN light torpedo family. Does not implement Stage4/5 recovery/ProtoTech. Offline validation only; runtime NOT RUN.')
    edits['.mod_meta_data']=meta;write(audit/'integration.json',r)
    print(json.dumps(package(base,out,edits,origins,ROOT/'docs/update23.md',audit,art,a.package_existing),indent=2))
