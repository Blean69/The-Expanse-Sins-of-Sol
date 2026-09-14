"""Check actual acquisition routes, not just valid entity identifiers."""
import sys,json
from pathlib import Path
from update20_fleet import ROOT,GAME
from update21_factions import FACTIONS,WRAPPERS
from validate_experiments import read,require,sha256
from build_polish import write

def run(base):
    def definition(name,kind):
        p=base/'entities'/f'{name}.{kind}';return read(p if p.exists() else GAME/'entities'/p.name)
    rows=[]
    for owner,faction in {**{v:k for k,v in FACTIONS.items()},**WRAPPERS}.items():
        p=definition(owner,'player');factory_kinds=set()
        for n in p['structures']:factory_kinds.update(definition(n,'unit').get('unit_factory',{}).get('build_kinds',[]))
        checked=[]
        for kind,ids in [('ship',p['buildable_units']),('structure',p['structures'])]:
            for n in ids:
                if not any(n.startswith('expanse'+str(v)) for v in range(21,26)):continue
                u=definition(n,'unit');actual=u['build']['build_kind']
                if kind=='structure':require(actual=='structure','Nonstructure in constructor list '+n)
                else:require(actual!='structure' and actual in factory_kinds,'No actual factory for '+owner+' '+n+' '+actual)
                groups=u['build'].get('prerequisites',[])
                require(not groups or any(all(x in p['research']['research_subjects'] for x in g) for g in groups),'Unreachable build prerequisite '+owner+' '+n)
                checked.append({'unit':n,'route':kind,'build_kind':actual})
        rows.append({'owner':owner,'faction':faction,'factory_kinds':sorted(factory_kinds),'checked':checked})
    # All0.25 variants must use the correction, including earlier new structures.
    expected=['expanse22_pdc_picket']
    for row in rows:
        p=definition(row['owner'],'player')
        require(all(n in p['structures'] for n in expected),'Missing picket construction')
        require(not any(n.startswith('expanse22') for n in p['buildable_units']),'Old defense-menu bug inherited')
        caps={x['tag']:x['unit_limit'] for x in p['unit_limits']['global']}
        require(caps['titan']==1 and caps['expanse24_gathering_storm']==1 and caps['expanse25_un_one']==1,'Shared/unique cap definition drift')
    # A siege visual swap must not edit the actual weapon or any magazine.
    prior=ROOT/'build/experiments'/('expanse_update24_sandbox' if base.name.endswith('_sandbox') else 'expanse_update24')
    rel='entities/expanse21_local_bombardment.weapon';require(sha256(base/rel)==sha256(prior/rel),'IPBM changed actual bombing damage/mechanics')
    for f in (prior/'entities').glob('*magazine*'):require(sha256(f)==sha256(base/'entities'/f.name),'Magazine changed during cosmetic integration')
    require(definition('expanse25_un_one','unit').get('is_loot_collector') is False,'Envoy inherited unrelated collector role')
    result={'status':'PASS OFFLINE actual acquisition fields','rows':rows,'cosmetic_bombing_weapon_unchanged':True,'all_prior_magazines_unchanged':True,'runtime':'NOT RUN'}
    write(ROOT/'audit'/base.name.replace('expanse_','')/'acquisition-check.json',result);return result

if __name__=='__main__':
    for suffix in ['', '_sandbox']:
        r=run(ROOT/'build/experiments'/('expanse_update25'+suffix));print(suffix or 'asymmetric',r['status'])
