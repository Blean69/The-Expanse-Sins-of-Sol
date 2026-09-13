"""Validate support reachability in a private symlink view of frozen 0.14."""
import json
from pathlib import Path
from build_combat03 import check_actions
from amun06_validate_package import AmunResolver, check_action_values
from update15_scirocco_support import ROOT, read, write, sha, BREACH, ENG, GUARD, DISRUPT

MAIN=Path('/run/media/haker/NVME 2/expanse-mod')
BASE=MAIN/'build/experiments/expanse_update14'
GAME=MAIN.parent/'SteamLibrary/steamapps/common/Sins2'
OUT=ROOT/'build/update15-scirocco'
VIEW=ROOT/'build/update15-scirocco-validation'
AUD=ROOT/'audit/update15-scirocco'

if not VIEW.exists():
    for p in BASE.rglob('*'):
        if p.is_file():
            q=VIEW/p.relative_to(BASE);q.parent.mkdir(parents=True,exist_ok=True);q.symlink_to(p)

def own_write(q,d):
    if q.is_symlink():q.unlink()
    write(q,d)

recipe=read(OUT/'integration-recipe.json')
for p in (OUT/'entities').glob('*'):own_write(VIEW/'entities'/p.name,read(p))
u=read(BASE/'entities/expanse12_scirocco.unit')
u['abilities'][0]['abilities']=recipe['patches'][0]['value']
own_write(VIEW/'entities/expanse12_scirocco.unit',u)
loc=read(BASE/'localized_text/en.localized_text');loc.update(recipe['localization'])
own_write(VIEW/'localized_text/en.localized_text',loc)
r=AmunResolver(VIEW,GAME)
unit=r.unit('expanse12_scirocco','bounded-support-validation')
graph=check_actions(VIEW,r,'expanse12_scirocco')
typed=check_action_values(VIEW,GAME,r,unit)
# Check all new buff weapon modifier IDs, which the older generic graph walk omits.
bads=read(OUT/'entities'/(BREACH+'.action_data_source'))
weapon_modifiers={x['buff_weapon_modifier_id'] for x in bads['buff_weapon_modifiers']}
assert read(OUT/'entities'/(DISRUPT+'.buff'))['weapon_modifiers'][0]['buff_weapon_modifier_id'] in weapon_modifiers
# Native event explicitly terminates either time-based effect at an ownership change.
for b in [DISRUPT,ENG]:
    trigger=read(OUT/'entities'/(b+'.buff'))['trigger_event_actions']
    assert any(x['trigger_event_type']=='on_current_spawner_player_ownership_changed' and x['action_group']['actions']==[{'action_type':'make_buff_dead'}] for x in trigger)
# Pending-effect rejection is required on the manual target filter as well as the
# arriving operator. A global preserve-existing guard also covers same-frame races.
for a,id,b in [(BREACH,'breach_target',GUARD),(ENG,'engineering_target',ENG)]:
    ads=read(OUT/'entities'/(a+'.action_data_source'))
    f=next(x['target_filter']for x in ads['target_filters']if x['target_filter_id']==id)
    assert any(x.get('constraint',{}).get('buff')==b and x['constraint'].get('include_pending_buffs') is True for x in f['constraints'])
    ab=read(OUT/'entities'/(a+'.ability'))
    assert ab['active_actions']['target_filters']==[id]
    arrival=ab['active_actions']['actions']['actions'][0]['operators'][0]
    assert arrival['constraint']['target_filter_id']==('breach_arrival' if a==BREACH else id)
    assert arrival['constraint']['unit']['unit_type']=='operand_destination'
# Existing ship costs, construction, physics, hull, weapon definitions, target
# handling, skin, and four previous passive abilities remain byte/value identical.
before=read(BASE/'entities/expanse12_scirocco.unit');after=dict(unit)
after['abilities']=before['abilities'];assert after==before
for n in ['expanse06_amun_boarding','expanse10_donnager_marines']:
    for ext in ['ability','action_data_source','buff']:
        p=BASE/'entities'/f'{n}.{ext}'
        if p.exists():assert sha(p)==sha(VIEW/'entities'/p.name)
write(AUD/'references.json',{'status':'PASS OFFLINE','ability_graph':graph,'typed':typed,'reference_count':len(r.edges),'references':r.edges,
    'extra_checks':['All support-only weapon modifiers resolve.','Owner-change event removes disruption and repair.','Manual admission blocks pending effects; delayed impact excludes its own pending reservation while rejecting active guards.','Only Scirocco abilities selection changed; exact rest-of-unit equality.','Other ships capture definitions unchanged.'],
    'runtime':'NOT RUN. Engine concurrency, support level change on existing ship, save/reload, ownership events, multiplayer, and ability visibility require workstation tests.'})
print(json.dumps({'status':'PASS','graph':graph,'reference_count':len(r.edges)},indent=2))
