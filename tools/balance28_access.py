"""Increment A shared access and scout controls; frozen input, no installed writes."""
import copy
from common import read,GAME
PLAYERS={'expanse18_mcrn':'mcrn','trader_loyalist':'mcrn','expanse18_unn':'unn','dlc_trader_loyalist':'unn','expanse18_opa':'opa','trader_rebel':'opa'}
BATTERY='expanse22_foehammer_battery'

def changes(base, prior=None):
    edits=copy.deepcopy(prior or {});origins={};report={}
    def get(rel):return copy.deepcopy(edits[rel]) if rel in edits else read(base/rel)
    rel='entities/trader_scout_corvette.unit';u=get(rel);before=copy.deepcopy(u['hyperspace'])
    u['hyperspace'].update(charge_time=0.1,charge_time_variance=0.0);edits[rel]=u
    report['razorback']={'unit':'trader_scout_corvette','former_name':'Sunflare','before':before,'after':u['hyperspace'],
      'preserved':'Transit speed, alignment angles, movement, high-G burn health cost/cooldown, fleet behavior unchanged.',
      'inhibitor_caveat':'Existing research-gated native Unstoppable Phase Jump already grants phase_jump_disruption_immune. Preserved outside targeted charge edit; no new bypass added. Inhibitor tests must record whether that existing research is active.',
      'runtime':'NOT RUN; 0.1 seconds is charge only, not total escape time.'}
    src='entities/expanse22_unn_orbital_defense.research_subject';node=get(src)
    names={'unn':'expanse22_unn_orbital_defense','mcrn':'expanse28_mcrn_orbital_defense','opa':'expanse28_opa_orbital_defense'}
    loc=get('localized_text/en.localized_text');matrix={}
    for faction in ['mcrn','opa']:
        n=copy.deepcopy(node);ident=names[faction]
        # Choose a free tier/field coordinate across both equivalent player entries.
        occupied=set()
        for pid,f in PLAYERS.items():
            if f!=faction:continue
            for subject in get('entities/'+pid+'.player')['research']['research_subjects']:
                rel=f'entities/{subject}.research_subject';p=base/rel
                if p.exists() or (GAME/rel).exists():
                    s=get(rel) if p.exists() else read(GAME/rel)
                    if s.get('field')==n['field'] and s.get('tier')==n['tier']:occupied.add(tuple(s.get('field_coord',[])))
        coord=tuple(n['field_coord'])
        while coord in occupied:coord=(coord[0],coord[1]+1)
        n.update(field_coord=list(coord),name=ident+'.name',name_uppercase=ident+'.upper',description=ident+'.description')
        rel=f'entities/{ident}.research_subject';edits[rel]=n;origins[rel]=str(base/src)
        title={'mcrn':'Martian Orbital Fire Control','opa':'Belt Orbital Deterrence'}[faction]
        loc.update({ident+'.name':title,ident+'.upper':title.upper(),ident+'.description':'Unlocks the shared Foehammer Orbital Battery: maximum two per owned gravity well, four military slots each. Requires screening against torpedoes and flanking ships.'})
    rel=f'entities/{BATTERY}.unit';u=get(rel);u['build']['prerequisites']=[[n] for n in names.values()];edits[rel]=u
    for pid,f in PLAYERS.items():
        rel='entities/'+pid+'.player';p=get(rel);n=names[f]
        if BATTERY not in p['structures']:p['structures'].append(BATTERY)
        if n not in p['research']['research_subjects']:p['research']['research_subjects'].append(n)
        assert 'trader_unlock_hangar_defense_structure' in p['research']['research_subjects']
        limits=p['unit_limits']['planet'];matches=[x for x in limits if x['tag']==BATTERY]
        assert len(matches)==1 and matches[0]['unit_limit']==2
        edits[rel]=p;matrix[pid]={'research':n,'tier':node['tier'],'research_price':node['price'],'research_seconds':node['research_time'],'cap_tag':BATTERY,'per_planet_limit':2,'builder':p['structure_builder']}
    edits['localized_text/en.localized_text']=loc
    report['battery']={'access':matrix,'cost':u['build']['price'],'build_seconds':u['build']['build_time'],'military_slots':u['structure']['slots_required'],
      'cap':'One shared native planet tag bucket, not one cap per faction. Queue reservations, cancellation and capture counting require runtime verification; no deletion or transfer script added.',
      'weapons':'Unchanged in A. User range/60-second shot interval override is applied with B weapon increment.'}
    return edits,origins,report
