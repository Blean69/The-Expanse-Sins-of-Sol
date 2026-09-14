"""Explicit new-hull procurement and OPA Laconian access; civilian invariant."""
import copy
from pathlib import Path
from update20_fleet import GAME
from update21_factions import FACTIONS,WRAPPERS
from validate_experiments import read,require

SHIPS={
 'expanse27_nathan_hale':('unn',2,'Leonidas Battleship Construction','trader_unlock_antiarmor_frigate','expanse15_truman'),
 'expanse27_munroe':('unn',2,'Munroe Cruiser Construction','trader_unlock_antiarmor_frigate','expanse15_truman'),
 'expanse27_hephaestus':('mcrn',3,'Hephaestus Mobile Weapons Platform','expanse22_mcrn_naval_readiness','expanse12_scirocco'),
 'expanse27_laconia_frigate':('opa',3,'Laconian Frigate Procurement','expanse21_opa_surplus','expanse12_raptor'),
 'expanse27_dark_star':('opa',3,'Dark Star Black-Ops Refit','expanse21_opa_surplus','expanse06_amun'),
}
STORM='expanse24_gathering_storm';STORM_RESEARCH=STORM+'_procurement'

def changes(base,unit_edits,sandbox=False):
    base=Path(base);edits={};loc={};origins={};report={'access':{},'research':{}}
    def get(rel):
        if rel in edits:return copy.deepcopy(edits[rel])
        if rel in unit_edits:return copy.deepcopy(unit_edits[rel])
        return read(base/rel) if (base/rel).exists() else read(GAME/rel)
    owners={**{v:k for k,v in FACTIONS.items()},**WRAPPERS}
    players={owner:get('entities/'+owner+'.player') for owner in owners}
    occupied_by_owner={}
    for owner,p in players.items():
        occupied=set();occupied_by_owner[owner]=occupied
        for n in p['research']['research_subjects']+p['research'].get('faction_research_subjects',[]):
            d=get('entities/'+n+'.research_subject')
            if d['domain']=='military':occupied.add((d['field'],*d['field_coord']))
    for uid,(faction,tier,name,parent,icon) in SHIPS.items():
        rel='entities/'+uid+'.unit';require(rel in unit_edits,'Missing finished new hull '+uid)
        node=uid+'_procurement';source='trader_unlock_heavy_cruiser' if tier==2 else 'trader_unlock_torpedo_cruiser'
        d=read(GAME/'entities'/f'{source}.research_subject')
        relevant=[o for o in owners if sandbox or owners[o]==faction]
        occupied=set().union(*(occupied_by_owner[o] for o in relevant))
        x=2*tier;y=0
        while ('military_experimental',x,y) in occupied:y+=1
        for owner in relevant:occupied_by_owner[owner].add(('military_experimental',x,y))
        d.update(name=node+'.name',name_uppercase=node+'.upper',description=node+'.description',
                 prerequisites=[[parent]],field_coord=[x,y],hud_icon=icon+'_hud_icon',
                 tooltip_picture=icon+'_tooltip_picture',tooltip_icon=icon+'_hud_icon')
        edits['entities/'+node+'.research_subject']=d
        origins['entities/'+node+'.research_subject']=str(GAME/'entities'/f'{source}.research_subject')
        loc.update({node+'.name':name,node+'.upper':name.upper(),node+'.description':
            'Authorizes paid '+name.lower()+'. Research cost and time follow the existing military tier. Ship construction is separately paid.'})
        u=get(rel);u['build']['prerequisites']=[[node]];edits[rel]=u
        for owner,owner_faction in owners.items():
            if not sandbox and owner_faction!=faction:continue
            p=players[owner]
            for key,value in [('buildable_units',uid),('theme_picker_mesh_preview_units',uid)]:
                if value not in p[key]:p[key].append(value)
            if node not in p['research']['research_subjects']:p['research']['research_subjects'].append(node)
        report['research'][node]={'faction':faction,'tier':tier,'price':d['price'],'seconds':d['research_time'],'prerequisite':parent,'coord':[x,y]}
    # Reassign the existing expensive research instead of granting foreign
    # manufacturing or lowering its tier, price, duration or unique cap.
    rel='entities/'+STORM_RESEARCH+'.research_subject';d=get(rel)
    d['prerequisites']=[['expanse24_behemoth_refit']]
    d['description']='expanse27.storm_procurement.description';edits[rel]=d
    loc[d['description']]='OPA late Laconian procurement adaptation. Unlocks paid Gathering Storm construction; one per player. Requires Behemoth logistics refit research. Existing tier, research price and construction costs apply.'
    for owner,faction in owners.items():
        p=players[owner];allowed=sandbox or faction=='opa'
        for key,value in [('buildable_units',STORM),('theme_picker_mesh_preview_units',STORM)]:
            p[key]=[n for n in p[key] if n!=value]
            if allowed:p[key].append(value)
        for key in ('research_subjects','faction_research_subjects'):
            p['research'][key]=[n for n in p['research'].get(key,[]) if n!=STORM_RESEARCH]
        if allowed:p['research']['research_subjects'].append(STORM_RESEARCH)
        # The OPA titan route is already available in normal OPA and every
        # sandbox owner. Never add another faction's Titan research as a shim.
        if allowed:require('expanse24_behemoth_refit' in p['research']['research_subjects'],'Missing OPA commissioning route '+owner)
        edits['entities/'+owner+'.player']=p
        report['access'][owner]={'new_hulls':[u for u in SHIPS if u in p['buildable_units']],'gathering_storm':allowed}
    tags=get('uniforms/unit_tag.uniforms');have={x['name'] for x in tags['unit_tags']}
    for uid in SHIPS:
        if uid not in have:tags['unit_tags'].append({'name':uid,'localized_name':uid+'.name'});have.add(uid)
    edits['uniforms/unit_tag.uniforms']=tags
    return edits,loc,origins,report
