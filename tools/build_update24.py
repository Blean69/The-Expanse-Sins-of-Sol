"""Separate Behemoth/Storm hull experiment after Stage3 and Murphy."""
import argparse,json
from pathlib import Path
from update20_fleet import ROOT,GAME
from update21_factions import FACTIONS,WRAPPERS
from doctrine_package import package
from validate_experiments import read,require,sha256
from build_polish import write

def definitions(base,sandbox=False):
    from update24_storm_gameplay import changes as storm
    from update24_behemoth_gameplay import changes as behemoth
    edits={};loc={};origins={};art={};reports={};access={}
    for faction,fn,specpath in [('mcrn',storm,ROOT/'audit/update24-storm/integration-spec.json'),('opa',behemoth,ROOT/'docs/audit/update24-behemoth/integration-spec.json')]:
        e,l,o,r=fn(base);require(not set(e)&set(edits),'Private hull definition collision')
        edits.update(e);loc.update(l);origins.update(o);reports[faction]=r
        for rel,path in r.get('art_files',{}).items():
            src=Path(path);require(src.is_file() and not src.is_symlink(),'Missing hull UI art '+rel)
            require(not (base/rel).exists() and rel not in art,'UI art collision '+rel);art[rel]=src
        spec=read(specpath)
        for rel,h in spec.get('files',spec.get('compiled_files',{})).items():
            src=Path(spec['output_game'])/rel;require(src.is_file() and not src.is_symlink() and sha256(src)==h,'Art source drift '+rel)
            if (base/rel).exists():require(sha256(base/rel)==h,'Existing art collision '+rel)
            elif rel in art:require(sha256(art[rel])==h,'New art collision '+rel)
            else:art[rel]=src
    tags=read(base/'uniforms/unit_tag.uniforms');have={x['name'] for x in tags['unit_tags']}
    for faction,r in reports.items():
        for x in r['unit_tag_entries_append']:
            row={'name':x,'localized_name':x+'.name'} if isinstance(x,str) else x
            require(row['name'] not in have,'Duplicate new hull tag');tags['unit_tags'].append(row);have.add(row['name'])
        if r.get('unlock'):
            rel='entities/'+r['unlock']+'.research_subject'
            if rel not in edits:
                # Behemoth's fragment references a native Rebel unlock absent
                # from our TEC-loyalist-derived OPA tree. A private equivalent
                # preserves native cost/tier/prerequisite without that dead end.
                source=GAME/rel;node=read(source);r['unlock']='expanse24_behemoth_refit';rel='entities/'+r['unlock']+'.research_subject'
                node.update(name=r['unlock']+'.name',name_uppercase=r['unlock']+'.upper',description=r['unlock']+'.description')
                edits[rel]=node;origins[rel]=str(source)
                edits['entities/'+r['unit_id']+'.unit']['build']['prerequisites']=[[r['unlock']]]
                loc.update({r['unlock']+'.name':'Behemoth Logistics Refit',r['unlock']+'.upper':'BEHEMOTH LOGISTICS REFIT',r['unlock']+'.description':'Unlocks the OPA Behemoth at the ordinary titan foundry. Shares the existing one-titan limit. Native titan research costs and infrastructure prerequisites apply; ship construction is separately paid.'})
            node=edits[rel];node['field_coord']=[2*node['tier'],30 if faction=='mcrn' else 31]
            if sandbox and faction=='mcrn':node['prerequisites']=[['trader_unlock_loyalist_titan'],['trader_unlock_rebel_titan']]
    edits['uniforms/unit_tag.uniforms']=tags
    for owner,faction in {**{v:k for k,v in FACTIONS.items()},**WRAPPERS}.items():
        d=read(base/'entities'/f'{owner}.player');added=[]
        # Every owner has the same unique Storm cap, even after foreign capture.
        d['unit_limits']['global'].append({'tag':reports['mcrn']['unit_id'],'unit_limit':1})
        for origin,r in reports.items():
            if not sandbox and origin!=faction:continue
            uid=r['unit_id'];d['buildable_units'].append(uid);added.append(uid)
            if r.get('unlock'):d['research']['research_subjects'].append(r['unlock'])
            for recipe in r.get('player_recipes',{}).values():
                for item in recipe.get('ship_components_append',[]):
                    if item not in d['ship_components']:d['ship_components'].append(item)
        d['research']['research_subjects']=list(dict.fromkeys(d['research']['research_subjects']))
        for uid in added:
            u=edits['entities/'+uid+'.unit']
            prereqs=u['build'].get('prerequisites',[])
            require(not prereqs or any(all(n in d['research']['research_subjects'] for n in group) for group in prereqs),'New hull unavailable prerequisite '+owner+' '+uid)
        occupied={}
        for n in d['research']['research_subjects']:
            rel='entities/'+n+'.research_subject';src=base/rel
            if not src.exists():src=GAME/rel
            node=edits.get(rel) or read(src);key=(node.get('domain'),node.get('field'),tuple(node.get('field_coord',[])))
            if key in occupied and (n.startswith('expanse24') or occupied[key].startswith('expanse24')):raise AssertionError('Research placement collision '+str(key))
            occupied[key]=n
            if n.startswith('expanse24'):
                groups=node.get('prerequisites',[]);require(not groups or any(all(x in d['research']['research_subjects'] for x in g) for g in groups),'Missing procurement prerequisite '+owner)
        edits['entities/'+owner+'.player']=d;access[owner]=added
    text=read(base/'localized_text/en.localized_text');text.update(loc);edits['localized_text/en.localized_text']=text
    meta=read(base/'.mod_meta_data');meta.update(display_name='The Expanse — 0.24 Capital Prototypes'+(' Sandbox' if sandbox else ''),display_version='0.24.0',short_description='Behemoth logistics titan and scarce Laconian destroyer.',long_description='Separate hull prototypes over frozen0.23.1. OPA Behemoth shares titan cap. Gathering Storm is costly late MCRN procurement with one-per-player limit. Existing Stage1–3 foundations preserved. No Stage4/5 claims, global weapons or shields. Offline checks only; runtime/MP NOT RUN.')
    edits['.mod_meta_data']=meta
    return edits,origins,art,{'ships':reports,'access':access,'runtime':'NOT RUN'}

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--sandbox',action='store_true');p.add_argument('--package-existing',action='store_true');a=p.parse_args()
    suffix='_sandbox' if a.sandbox else '';base=ROOT/'build/experiments'/('expanse_update23_2'+suffix);out=ROOT/'build/experiments'/('expanse_update24'+suffix);audit=ROOT/'audit'/('update24'+suffix)
    edits,origins,art,r=definitions(base,a.sandbox);write(audit/'integration.json',r)
    print(json.dumps(package(base,out,edits,origins,ROOT/'docs/update24.md',audit,art,a.package_existing),indent=2))
