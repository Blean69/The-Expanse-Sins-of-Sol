"""Read-only contract review of the actual merged Stage A and Stage B120 trees."""
from pathlib import Path
import json,hashlib,importlib.util
ROOT=Path('/run/media/haker/NVME 2');EXP=ROOT/'expanse-mod/build/experiments'
A=EXP/'expanse_balance28_A';B=EXP/'expanse_balance28_B120';F=EXP/'expanse_update27_5_menu';G=ROOT/'SteamLibrary/steamapps/common/Sins2'
OUT=ROOT/'expanse-workers28/validation/audit/balance28/merged-review.json'
checks=[];read={}
def get(root,name,ext='unit'):
 p=root/'entities'/f'{name}.{ext}'
 if not p.is_file():p=G/'entities'/p.name
 read[str(p)]=hashlib.sha256(p.read_bytes()).hexdigest()
 return json.loads(p.read_text())
def check(name,condition):
 if not condition:raise AssertionError(name)
 checks.append(name)
def strings(x):
 if isinstance(x,str):yield x
 elif isinstance(x,dict):
  for v in x.values():yield from strings(v)
 elif isinstance(x,list):
  for v in x:yield from strings(v)
def classes(name,kind,ai):
 u=get(A,name);check(name+' class/group/filter/tags/AI',u['build']['build_kind']==u['build']['build_group_id']==u['target_filter_unit_type']==kind and kind in u['tags'] and u['ai_attack_target']['attack_target_type']==ai)
 check(name+' baseline movement preserved',u['physics']==get(F,name)['physics'])
 return u
t=classes('expanse15_truman','super_capital_ship','supercapital')
h=classes('expanse27_hephaestus','capital_ship','capital')
r=classes('expanse12_raptor','cruiser','heavy')
check('Truman400 and exact requested economic floors',t['build']['supply_cost']==400 and t['build']['build_time']==240 and t['build']['price']==dict(credits=7680,metal=3016,crystal=1520))
check('Truman unchanged health/levels/mounts/items',all(t[k]==get(F,'expanse15_truman')[k]for k in ['health','levels','weapons','items','abilities']))
check('Truman own prerequisite',t['build']['prerequisites']==[['expanse28_truman_command_procurement']])
check('Hephaestus ten health and experience rows',len(h['health']['levels'])==len(h['levels']['levels'])==10 and h['levels']['type']=='experience')
check('Hephaestus same L1 health/build/mounts except class',h['health']['levels'][0]==get(F,'expanse27_hephaestus')['health']['levels'][0] and all(h['build'][k]==get(F,'expanse27_hephaestus')['build'][k]for k in ['price','supply_cost','build_time','exotic_price'])and h['weapons']==get(F,'expanse27_hephaestus')['weapons'])
check('Hephaestus four ordinary-capital item slots',h['items']['levels'][0]['max_ship_component_count']==4)
check('Raptor one baseline health row, no experience or item access',r['health']['levels']==[get(F,'expanse12_raptor')['health']['levels'][0]] and 'levels'not in r and 'items'not in r and r['item_builds']==[])
check('Raptor baseline economics/mounts',all(r['build'][k]==get(F,'expanse12_raptor')['build'][k]for k in ['price','supply_cost','build_time','exotic_price'])and r['weapons']==get(F,'expanse12_raptor')['weapons'])
check('Factories accept revised classes','super_capital_ship'in get(A,'trader_loyalist_titan_factory_structure')['unit_factory']['build_kinds']and all(k in get(A,'trader_capital_ship_factory_structure')['unit_factory']['build_kinds']for k in ['cruiser','capital_ship']))
n=get(A,'expanse27_nathan_hale');check('Ordinary Nathan Hale colony support',n['build']['build_kind']=='capital_ship' and n['build']==get(F,'expanse27_nathan_hale')['build']and 'colonize'in n['ship_roles']and n['colonize_ability']=='expanse28_nathan_expeditionary_colonize')
check('Nathan colonize ability exists',bool(get(A,n['colonize_ability'],'ability')))
foe=get(A,'expanse22_foehammer_battery');expected=['expanse22_unn_orbital_defense','expanse28_mcrn_orbital_defense','expanse28_opa_orbital_defense']
check('Foehammer OR prerequisite groups',foe['build']['prerequisites']==[[x]for x in expected])
research=[]
for player,node in [('expanse18_unn',expected[0]),('dlc_trader_loyalist',expected[0]),('expanse18_mcrn',expected[1]),('trader_loyalist',expected[1]),('expanse18_opa',expected[2]),('trader_rebel',expected[2])]:
 p=get(A,player,'player');rs=set(strings(p['research']));limits=p['unit_limits'];command=2 if player in ['expanse18_unn','dlc_trader_loyalist'] else 1
 check(player+' command and titan caps',next(x['unit_limit']for x in limits['global']if x['tag']=='super_capital_ship')==command and next(x['unit_limit']for x in limits['global']if x['tag']=='titan')==1)
 check(player+' shared battery access and cap','expanse22_foehammer_battery'in p['structures']and node in rs and [x for x in limits['planet']if x['tag']=='expanse22_foehammer_battery']==[{'tag':'expanse22_foehammer_battery','unit_limit':2}])
 check(player+' free first ordinary capital unchanged',p['starting_free_unit_build_kinds']==['capital_ship'])
 targets=[node]+(['expanse28_truman_command_procurement']if command==2 else[])
 for target in targets:
  check(player+' reachable '+target,target in rs)
  seen=set()
  def visit(rid):
   if rid in seen:return
   seen.add(rid);d=get(A,rid,'research_subject')
   check(player+' owns prerequisite '+rid,rid in rs)
   for group in d.get('prerequisites',[]):
    # All explicit prerequisites here are single AND groups; no invention of unlock bypass.
    for child in group:visit(child)
  visit(target)
  d=get(A,target,'research_subject');collisions=[]
  for rid in rs:
   path=A/'entities'/f'{rid}.research_subject';fallback=G/'entities'/path.name
   if rid==target or not(path.is_file()or fallback.is_file()):continue
   other=get(A,rid,'research_subject')
   if all(other.get(k)==d.get(k)for k in ['domain','field','field_coord']):collisions.append(rid)
  check(player+' research node has unique active coordinates '+target,not collisions)
  research.append({'player':player,'node':target,'closure':sorted(seen),'coordinate':d['field_coord']})

# Actual A has no weapon/projectile/magazine numerical modifications. The two
# boarding filters add an explicit Truman exclusion; preserve and disclose it.
for p in (F/'entities').iterdir():
 if p.suffix in ('.weapon','.buff','.action_data_source')or p.name.endswith('torpedo.unit'):
  q=A/'entities'/p.name
  if p.name in ['expanse21_opa_override_codes_boarding.action_data_source','expanse06_amun_boarding.action_data_source']:
   old=json.loads(p.read_text());new=json.loads(q.read_text())
   for index in [0,1]:
    old['target_filters'][index]['target_filter']['constraints'].append({'constraint_type':'composite_not','constraint':{'constraint_type':'has_definition','unit_definition':'expanse15_truman'}})
   check('A boarding only adds explicit Truman exclusion '+p.name,old==new)
  else:check('A keeps '+p.name,q.exists()and p.read_bytes()==q.read_bytes())
check('Razorback charge-only diff contract',get(A,'trader_scout_corvette')['hyperspace']['charge_time']==.1 and get(A,'trader_scout_corvette')['physics']==get(F,'trader_scout_corvette')['physics'])
helper=ROOT/'expanse-workers28/weapons/tools/balance28_weapons.py'
spec=importlib.util.spec_from_file_location('weapons',helper);m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
edits,_,_=m.changes(A,F)
for rel,wanted in edits.items():
 actual=json.loads((B/rel).read_text())
 # Main owns menu/string synchronization separately; proposal files themselves must match.
 check('Merged B exact proposal '+rel,actual==wanted)
for uid in ['expanse15_truman','expanse27_hephaestus','expanse12_raptor','expanse27_nathan_hale']:
 ua=get(A,uid);ub=get(B,uid)
 check('Merged B preserves A class/economy/health '+uid,all(ua.get(k)==ub.get(k)for k in ['build','levels','health','items','target_filter_unit_type','tags']))
report={'status':'PASS — actual merged A and B120 static contracts; runtime NOT RUN','A':str(A),'B':str(B),'checks':checks,'research_closures':research,'read_hashes':read,
 'disclosures':['Truman keeps its existing four item slots; native command source has six. This preserves baseline equipment budget rather than silently buffing slots.',
 'Amun and OPA override boarding exclude Truman at both launch and resolution. This narrows boarding to preserve the command cap; other classes retain existing filters. Must disclose this deliberate exception.',
 'Command cap2 applies to UNN identities; other factions retain native cap1. Captured command over-cap behavior remains a runtime test.',
 'Raptor keeps its exact L1 health/crippled fields and becomes unlevelled; Hephaestus gains ten health rows, reaching +27% hull/armor at top level, with no new level weapon damage scalar.',
 'Prerequisite availability and unique research coordinates verified statically. Native queue enforcement, AI successful construction, UI reachability and damage packet count require game tests.']}
OUT.write_text(json.dumps(report,indent=2)+'\n');print(json.dumps({'status':report['status'],'checks':len(checks),'output':str(OUT)}))
