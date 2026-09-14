"""Stage 2: same foundations generate asymmetric and combined candidates."""
import argparse,copy,json
from pathlib import Path
from update21_factions import BASE,ROOT,GAME,COMMAND,foundations,players
from doctrine_colony_fragments import changes as colony
from validate_experiments import read,require
from build_polish import write
from doctrine_package import package

def definitions(sandbox=False):
    from update21_research import changes as research_changes
    edits,loc,origins=foundations(BASE)
    ce,cl,co,cr=colony(BASE,COMMAND,'expanse21')
    for rel,d in ce.items():edits['entities/'+rel]=d;origins['entities/'+rel]=co[rel]
    loc.update(cl)
    def get(ident,kind):
        rel=f'entities/{ident}.{kind}'
        if rel not in edits:edits[rel]=read(BASE/rel)
        return edits[rel]
    for ident,p in cr['unit_patches'].items():
        d=get(ident,'unit')
        for tag in p.get('tags_append',[]):
            if tag not in d['tags']:d['tags'].append(tag)
        d.setdefault('item_builds',[]).extend(p.get('item_builds_append',[]))
        if 'colonize_ability' in p:d['colonize_ability']=p['colonize_ability']
        d['weapons']['weapons'].extend(p.get('weapons_append',[]))
    for ident,p in cr['skin_patches'].items():
        d=get(ident,'unit_skin')
        for stage in d['skin_stages']:
            aliases=stage['effects'].setdefault('effect_alias_bindings',[]);have={x['alias_name'] for x in aliases}
            aliases.extend(copy.deepcopy(x) for x in p['effect_alias_bindings_merge'] if x['alias_name'] not in have)
    tags=edits['uniforms/unit_tag.uniforms']['unit_tags'];have={x['name'] for x in tags}
    tags.extend(x for x in cr['unit_tag_entries_append'] if x['name'] not in have)
    re,rl,rp,rr=research_changes(BASE)
    require(not set(edits)&set(re),'Research ownership collision: '+str(set(edits)&set(re)))
    edits.update(re);loc.update(rl)
    for patch in rr['shared_definition_merges']:
        rel=patch['file'];source=BASE/rel
        if not source.exists():source=GAME/rel
        if rel not in edits:edits[rel]=read(source)
        edits[rel].update(copy.deepcopy(patch['set_fields']));origins[rel]=str(source)
    # Exclusions are authored symmetrically; do not depend on which item the
    # engine examines first when a player queues a replacement district.
    for rel,d in list(edits.items()):
        if not rel.endswith('.unit_item'):continue
        for other in d.get('other_item_requirements',{}).get('mutually_exclusive_items',[]):
            target='entities/'+other+'.unit_item'
            if target not in edits:
                source=BASE/target
                if not source.exists():source=GAME/target
                edits[target]=read(source);origins[target]=str(source)
            rows=edits[target].setdefault('other_item_requirements',{}).setdefault('mutually_exclusive_items',[])
            if Path(rel).stem not in rows:rows.append(Path(rel).stem)
    # Research helper supplies explicit player ownership and equipment lists.
    research=rp['research'];items=rp['items']
    for row in cr['colony']:
        faction={'expanse12_scirocco':'mcrn','expanse15_truman':'unn',COMMAND:'opa'}[row['ship']]
        items[faction].append(row['module'])
    access=players(BASE,edits,loc,research,items,rp['planet_items'],sandbox)
    text=read(BASE/'localized_text/en.localized_text');text.update(loc);edits['localized_text/en.localized_text']=text
    meta=read(BASE/'.mod_meta_data');mode='COMBINED FLEET SANDBOX' if sandbox else 'THREE POWERS'
    meta.update(display_name='The Expanse — 0.21.1 '+mode,display_version='0.21.1',short_description='Stage 2: faction doctrine, expeditionary capitals and local siege.',
      long_description='Separate Stage 2 candidate over frozen 0.20. '+mode+'. Shared hull foundations, ordinary 2,000 supply at 1x. Colony components preserve active ship abilities. Native local bombardment uses separate siege stores, not interceptable projectiles. Read PLAYTEST-README. Offline checked only; runtime and multiplayer NOT RUN. No automatic installation or publication.')
    edits['.mod_meta_data']=meta
    starts=[]
    def supply(o):
        if isinstance(o,list):return sum(supply(x) for x in o)
        if not isinstance(o,dict):return 0
        if 'unit' in o:
            rel='entities/'+o['unit']+'.unit';path=BASE/rel
            if not path.exists():path=GAME/rel
            unit=edits.get(rel) or read(path)
            return unit.get('build',{}).get('supply_cost',0)*o.get('count',[1,1])[-1]
        return sum(supply(x) for x in o.values())
    for rel,d in edits.items():
        if not rel.endswith('.start_mode'):continue
        for cfg in d['faction_configurations']:
            if cfg['player_definition_id'] not in access:continue
            given=cfg.get('additional_starting_planets',{})
            used=supply(cfg['home_planet'])+given.get('count',0)*supply(given)
            research=cfg.get('starting_research',{}).get('starting_research_subjects',[])
            cap=100
            for n,value in enumerate([250,500,1000,1500,2000]):
                if 'trader_max_supply_'+str(n) in research:cap=value
            require(used<=cap,'Starting fleet exceeds supply: '+rel+' '+cfg['player_definition_id']+f' {used}/{cap}')
            starts.append({'mode':rel,'player':cfg['player_definition_id'],'maximum_starting_supply':used,'cap':cap})
    return edits,origins,{'access':access,'colony_bombardment':cr,'research':rr,'sandbox':sandbox,'starting_supply':starts}

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--sandbox',action='store_true');p.add_argument('--package-existing',action='store_true');a=p.parse_args()
    suffix='_sandbox' if a.sandbox else '';out=ROOT/'build/experiments'/('expanse_update21'+suffix);audit=ROOT/'audit'/('update21'+suffix)
    edits,origins,report=definitions(a.sandbox);write(audit/'integration.json',report)
    print(json.dumps(package(BASE,out,edits,origins,ROOT/'docs/update21.md',audit,package_existing=a.package_existing),indent=2))
