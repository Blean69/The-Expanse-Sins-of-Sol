"""UN One and native local IPBM cosmetic; separate new-hull release."""
import argparse,copy,json
from pathlib import Path
from update20_fleet import ROOT,GAME
from update21_factions import FACTIONS,WRAPPERS
from update25_unone_gameplay import changes,ID
from doctrine_package import package
from validate_experiments import read,require,sha256
from build_polish import write

def definitions(base,sandbox=False):
    edits,loc,origins,art,report=changes(base)
    # An envoy does not silently inherit Artemis's independent collector role.
    edits['entities/'+ID+'.unit']['is_loot_collector']=False
    spec=read(ROOT/'audit/update25-ipbm/integration-spec.json')
    for rel,h in spec['files'].items():
        src=Path(spec['output_game'])/rel;require(src.is_file() and not src.is_symlink() and sha256(src)==h,'IPBM art drift '+rel)
        if (base/rel).exists():require(sha256(base/rel)==h,'IPBM donor collision '+rel)
        elif rel in art:require(sha256(art[rel])==h,'Envoy/IPBM collision')
        else:art[rel]=src
    # Only Truman's native local-siege travel alias changes. The shared bombing
    # weapon, all anti-ship magazines and all other ship skins remain untouched.
    skinrel='entities/expanse15_truman.unit_skin';skin=read(base/skinrel)
    weapon=read(base/'entities/expanse21_local_bombardment.weapon');alias=weapon['effects']['projectile_travel_effect']
    count=0
    for stage in skin['skin_stages']:
        for row in stage['effects']['effect_alias_bindings']:
            if row['alias_name']==alias:row['alias_binding']=copy.deepcopy(spec['effect_fragment']['entry']['alias_binding']);count+=1
    require(count==len(skin['skin_stages']),'Missing actual siege alias in Truman skin')
    edits[skinrel]=skin;origins[skinrel]=str(base/skinrel)
    tags=read(base/'uniforms/unit_tag.uniforms');tags['unit_tags']+=report['unit_tag_entries_append'];edits['uniforms/unit_tag.uniforms']=tags
    access={}
    for owner,faction in {**{v:k for k,v in FACTIONS.items()},**WRAPPERS}.items():
        d=read(base/'entities'/f'{owner}.player');d['unit_limits']['global'].append({'tag':ID,'unit_limit':1})
        if sandbox or faction=='unn':
            require(report['research_prerequisite'] in d['research']['research_subjects'],'Unavailable envoy prerequisite')
            d['buildable_units'].append(ID)
        edits['entities/'+owner+'.player']=d;access[owner]=ID in d['buildable_units']
    text=read(base/'localized_text/en.localized_text');text.update(loc);edits['localized_text/en.localized_text']=text
    meta=read(base/'.mod_meta_data');meta.update(display_name='The Expanse — 0.25 New Hulls'+(' Sandbox' if sandbox else ''),display_version='0.25.0',short_description='Murphy, Behemoth, Gathering Storm, UN One and local IPBM visuals.',long_description='Separate new-hull candidate over completed and corrected Stage1–3 foundations. UN One provides bounded manual civilian relief. Truman local siege gets supplied UN IPBM visual only; no new damage/object interception/global launch. Stage4 exclusive recovery and Stage5 ProtoTech remain gated and absent. Offline checks only; runtime/MP NOT RUN.')
    edits['.mod_meta_data']=meta
    report.update(access=access,inherited_collector_removed=True,ipbm={'ship':'expanse15_truman','actual_alias':alias,'effect':spec['effect_fragment']['entry']['alias_binding'],'weapon_unchanged':True,'actual_unit_created':False,'interceptable':False,'global_launch':False})
    return edits,origins,art,report

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--sandbox',action='store_true');p.add_argument('--package-existing',action='store_true');a=p.parse_args()
    suffix='_sandbox' if a.sandbox else '';base=ROOT/'build/experiments'/('expanse_update24'+suffix);out=ROOT/'build/experiments'/('expanse_update25'+suffix);audit=ROOT/'audit'/('update25'+suffix)
    edits,origins,art,r=definitions(base,a.sandbox);write(audit/'integration.json',r)
    print(json.dumps(package(base,out,edits,origins,ROOT/'docs/update25.md',audit,art,a.package_existing),indent=2))
