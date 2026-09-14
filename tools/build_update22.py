"""Stage 3: local orbital defense and bounded engineering services."""
import argparse,copy,json
from pathlib import Path
from update20_fleet import ROOT,GAME
from update21_factions import FACTIONS,WRAPPERS
from update22_stations import changes as stations
from update22_battery import changes as battery,ID,RESEARCH
from doctrine_package import package
from validate_experiments import read,require
from build_polish import write

def definitions(base,sandbox=False):
    se,loc,so,sr=stations(base)
    edits={'entities/'+r:d for r,d in se.items()};origins={'entities/'+r:s for r,s in so.items()}
    be,bl,bo,art,br=battery(base)
    require(not set(edits)&set(be),'Station/battery ownership overlap')
    edits.update(be);origins.update(bo);loc.update(bl)
    # These two owner-scoped technologies share one non-additive upgrade. Even
    # the combined sandbox tops out at22 per target, never24 or percentage HP.
    nodes={}
    for faction,title,slug,y in [('mcrn','Naval Readiness Program','naval_readiness',27),('opa','Dockworker Damage Control','dockworker_damage_control',28)]:
        n='expanse22_'+faction+'_'+slug;nodes[faction]=n
        source=GAME/'entities/trader_unlock_robotics_cruiser.research_subject'
        d=read(source)
        for k in ['prerequisites','player_modifiers','unit_modifiers','weapon_modifiers']:d.pop(k,None)
        d.update(field='military_engineering',field_coord=[4,y],prerequisites=[['trader_unlock_starbase']],name=n+'.name',name_uppercase=n+'.upper',description=n+'.description')
        edits['entities/'+n+'.research_subject']=d;origins['entities/'+n+'.research_subject']=str(source)
        loc.update({n+'.name':title,n+'.upper':title.upper(),n+'.description':'Fitted Repair Anchorage modules on owned engineering stations repair22 hull instead of20 per target per second. At most3targets within6000:66 hull/second total. Requires the paid station and module. Same-effect upgrades do not add; no empire-wide repair aura.'})
    a=edits['entities/expanse22_repair_anchorage.ability']
    a.update(level_source='research_prerequisites_per_level',level_prerequisites=[[],[[nodes['mcrn']],[nodes['opa']]]])
    ads=edits['entities/expanse22_repair_anchorage.action_data_source']
    for v in ads['action_values']:
        if v['action_value_id']=='repair_per_tick':v['action_value']['values']=[20.,22.]
    loc['expanse22_repair_anchorage.description']+=' Naval Readiness or Dockworker Damage Control raises20 to22, capped at66 total per second; researching both grants one upgrade.'
    edits['entities/'+RESEARCH+'.research_subject']['field_coord']=[4,29]
    tags=read(base/'uniforms/unit_tag.uniforms');have={x['name'] for x in tags['unit_tags']}
    for row in sr['unit_tag_entries_append']+[{'name':ID,'localized_name':ID+'.name'}]:
        require(row['name'] not in have,'Duplicate structure tag');tags['unit_tags'].append(row);have.add(row['name'])
    edits['uniforms/unit_tag.uniforms']=tags
    access={}
    for owner,faction in {**{v:k for k,v in FACTIONS.items()},**WRAPPERS}.items():
        p=read(base/'entities'/f'{owner}.player')
        recipe=sr['combined_sandbox'] if sandbox else sr['player_recipes'][faction]
        structures=list(recipe['structures_append']);research=list(nodes.values())+[RESEARCH] if sandbox else ([nodes[faction]] if faction in nodes else [RESEARCH])
        if sandbox or faction=='unn':structures.append(ID)
        p['structures']=list(dict.fromkeys(p['structures']+structures))
        require(all(n in p['structures'] and n not in p['buildable_units'] for n in structures),'Station acquisition must use constructor structures list')
        p['ship_components']=list(dict.fromkeys(p['ship_components']+recipe['ship_components_append']))
        p['research']['research_subjects']=list(dict.fromkeys(p['research']['research_subjects']+research))
        p['unit_limits']['global'].append(recipe['global_unit_limit'])
        # All owners get the same cap, including captured foreign batteries.
        p['unit_limits']['planet'].append({'tag':ID,'unit_limit':2})
        edits['entities/'+owner+'.player']=p
        access[owner]={'faction':faction,'structures':structures,'modules':recipe['ship_components_append'],'research':research}
        for n in structures:
            for group in edits['entities/'+n+'.unit']['build'].get('prerequisites',[]):
                require(all(x in p['research']['research_subjects'] for x in group),'Unavailable station prerequisite '+owner+str(group))
        occupied={}
        for n in p['research']['research_subjects']:
            rel='entities/'+n+'.research_subject';src=base/rel
            if not src.exists():src=GAME/rel
            d=edits.get(rel) or read(src)
            key=(d.get('domain'),d.get('field'),tuple(d.get('field_coord',[])))
            if key in occupied and (n.startswith('expanse22') or occupied[key].startswith('expanse22')):raise AssertionError('Research cell collision '+str(key))
            occupied[key]=n
    text=read(base/'localized_text/en.localized_text');text.update(loc);edits['localized_text/en.localized_text']=text
    meta=read(base/'.mod_meta_data');mode='COMBINED SANDBOX' if sandbox else 'ORBITAL DEFENSE'
    meta.update(display_name='The Expanse — 0.22.1 '+mode,display_version='0.22.1',short_description='Stage3: Foehammer battery, PDC picket and local engineering stations.',long_description='Frozen0.21.1 foundations plus local shieldless orbital defense. Corrected constructor-menu access. UNN Foehammer battery; faction station art uses disclosed native placeholders. Three slots/four modules; bounded owned-only repair, PDC tracking and local shipyard support. Offline validation only; runtime/MP NOT RUN. No installation or publication.')
    edits['.mod_meta_data']=meta
    return edits,origins,art,{'access':access,'stations':sr,'battery':br,'repair_research':nodes,'runtime':'NOT RUN'}

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--sandbox',action='store_true');p.add_argument('--package-existing',action='store_true');a=p.parse_args()
    suffix='_sandbox' if a.sandbox else '';base=ROOT/'build/experiments'/('expanse_update21'+suffix);out=ROOT/'build/experiments'/('expanse_update22_1'+suffix);audit=ROOT/'audit'/('update22_1'+suffix)
    edits,origins,art,report=definitions(base,a.sandbox);write(audit/'integration.json',report)
    print(json.dumps(package(base,out,edits,origins,ROOT/'docs/update22.md',audit,art,a.package_existing),indent=2))
