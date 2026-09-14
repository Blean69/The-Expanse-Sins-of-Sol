"""Repairs backed by the user's0.26 runtime log; no balance multipliers."""
import copy
from pathlib import Path
from update20_fleet import GAME
from validate_experiments import read, require

def changes(base, prior_edits=None):
    base=Path(base); current=prior_edits or {}; edits={};loc={};report={'runtime_after_fix':'NOT RUN','rail_mounts':[]}
    def get(rel):
        if rel in current:return copy.deepcopy(current[rel])
        return read(base/rel) if (base/rel).exists() else read(GAME/rel)
    # scenario.uniforms is parsed per provider; even additive files require
    # these arrays. Empty additions preserve installed DLC scenario lists.
    rel='uniforms/scenario.uniforms';d=get(rel)
    d.setdefault('dlc_scenarios',[]);d.setdefault('dlc_multiplayer_scenarios',[])
    d.setdefault('fake_server_scenarios',[]);edits[rel]=d
    # The engine renders this passive in ordinary unit ability menus. Omitting
    # GUI does not hide it and causes "has no gui.hud_icon" assertions.
    rel='entities/expanse11_no_shields.ability';d=get(rel)
    d['gui']={'hud_icon':'unit_analysis_defense_icon','name':'expanse27.shieldless.name','description':'expanse27.shieldless.description'}
    edits[rel]=d;loc.update({'expanse27.shieldless.name':'Shieldless Hull',
        'expanse27.shieldless.description':'This hull uses armor and structural protection. Conventional shield absorption, restoration and regeneration are disabled.'})
    # Scan all exported mounts, including new derivatives supplied by workers.
    names={p.name for p in (base/'entities').glob('*.unit')}|{Path(p).name for p in current if p.endswith('.unit')}
    for name in sorted(names):
        rel='entities/'+name;d=get(rel);changed=False
        for mount in d.get('weapons',{}).get('weapons',[]):
            w=get('entities/'+mount['weapon']+'.weapon')
            for axis in ('pitch','yaw'):
                arc=mount.get(axis+'_arc')
                if arc and arc['max_angle']<=arc['min_angle'] and w.get(axis+'_speed',0)<=0:
                    require(arc['max_angle']==arc['min_angle'],'Inverted weapon arc '+name)
                    center=arc['min_angle'];tolerance=min(1.,max(.1,w.get(axis+'_firing_tolerance',1.)))
                    mount[axis+'_arc']={'min_angle':center-tolerance,'max_angle':center+tolerance};changed=True
                    report['rail_mounts'].append({'unit':name,'weapon':mount['weapon'],'axis':axis,'before':arc,'after':mount[axis+'_arc']})
        # The native ordinary ship bar has four buttons. Keep the requested
        # command's actionable colony control ahead of its passive hull label.
        if name=='expanse21_opa_command.unit':
            for group in d.get('abilities',[]):
                ids=group['abilities'];colony=d['colonize_ability']
                if colony in ids:
                    group['abilities']=[colony]+[n for n in ids if n!=colony];changed=True
        if changed:edits[rel]=d
    report.update(scenario_required_arrays='added empty DLC arrays without replacing installed lists',
        shieldless_passive='GUI only; original buff mutations untouched',
        command_colony='first ordinary ability slot',
        unresolved=['Generic inplace_vector index assertion has no attributable entity or call stack in the supplied log.',
                    'Old installed prototype metadata and old replay metadata warnings are outside this candidate.'])
    return edits,loc,report
