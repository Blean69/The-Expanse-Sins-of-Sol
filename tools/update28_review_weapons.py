"""Independent, read-only review of the Stage B proposal generator."""
from pathlib import Path
import importlib.util,json,hashlib

ROOT=Path('/run/media/haker/NVME 2')
BASE=ROOT/'expanse-mod/build/experiments/expanse_update27_5_menu'
GAME=ROOT/'SteamLibrary/steamapps/common/Sins2'
HELPER=ROOT/'expanse-workers28/weapons/tools/balance28_weapons.py'
OUT=ROOT/'expanse-workers28/validation/audit/balance28/weapons-review.json'
spec=importlib.util.spec_from_file_location('proposal',HELPER);m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def diff(a,b,path=''):
 if type(a)!=type(b):return [path]
 if isinstance(a,dict):return sum(([path+'/'+k] if k not in a or k not in b else diff(a[k],b[k],path+'/'+k) for k in sorted(a.keys()|b.keys())),[])
 if isinstance(a,list):return [path] if len(a)!=len(b) else sum((diff(x,y,path+'/'+str(i))for i,(x,y)in enumerate(zip(a,b))),[])
 return []if a==b else[path]
def walk(x):
 yield x
 if isinstance(x,dict):
  for v in x.values():yield from walk(v)
 elif isinstance(x,list):
  for v in x:yield from walk(v)

edits,origins,r=m.changes(BASE,BASE)
checks=[]
for rel,new in edits.items():
 origin=origins[rel];src=Path(origin['source']);old=json.loads(src.read_text())
 assert src==BASE/origin['source_relative'] or src==GAME/origin['source_relative'],rel
 assert sha(src)==origin['sha256'],rel
 if rel.endswith('.weapon'):
  allowed={'/range','/pitch_speed','/yaw_speed','/pitch_firing_tolerance','/yaw_firing_tolerance','/firing/charge_duration'}
  assert set(diff(old,new))<=allowed,(rel,diff(old,new))
 if 'expanse28_mcrn_'in rel and rel.endswith('.unit') and 'torpedo'in rel:
  assert diff(old,new)==['/physics/max_linear_speed'],rel
  assert new['physics']['max_linear_speed']==old['physics']['max_linear_speed']*1.2,rel
 # Compare all numeric leaves: cloned ability/buff numbers cannot change; ADS may
 # change its explicitly named speed tooltip only. Unit identity strings may differ.
 if 'expanse28_mcrn_'in rel and rel.endswith(('.ability','.buff')):
  before=[v for v in walk(old)if type(v)in (int,float,bool)]
  after=[v for v in walk(new)if type(v)in (int,float,bool)]
  assert before==after,rel
 if 'expanse28_mcrn_'in rel and rel.endswith('.action_data_source'):
  for a,b in zip(old['action_values'],new['action_values']):
   if a['action_value_id']=='heavy_torpedo_torpedo_speed_value':
    assert b['action_value']['values']==[x*1.2 for x in a['action_value']['values']],rel
   else:assert a==b,(rel,a['action_value_id'])
 checks.append({'file':rel,'origin_sha256':sha(src),'changed_pointers':diff(old,new)})

# Pure overlay rerun must not compound frozen-derived multipliers.
again,_,_=m.changes(edits,BASE)
assert again==edits,'Repeated proposal compounded values'
control,_,_=m.changes(BASE,BASE,tachi_supply=95)
delta={f:diff(control[f],edits[f])for f in edits if control[f]!=edits[f]}
assert all(f.endswith('launch_corvette.action_data_source')or f=='entities/expanse_mcrn_corvette.unit'for f in delta),delta
assert delta['entities/expanse_mcrn_corvette.unit']==['/build/supply_cost']
optional,_,_=m.changes(BASE,BASE,donnager_cadence=True)
optional_delta={f:diff(edits[f],optional[f])for f in edits if edits[f]!=optional[f]}
assert set(optional_delta)=={'entities/expanse10_donnager_rail_0.weapon','entities/expanse10_donnager_rail_1.weapon'},optional_delta
assert all(v==['/cooldown_duration']for v in optional_delta.values()),optional_delta
assert all(optional[f]['cooldown_duration']==24 for f in optional_delta)

explicit_refs=[]
for folder in (GAME/'entities',BASE/'entities'):
 for p in folder.iterdir():
  if p.suffix not in ('.research_subject','.buff','.action_data_source','.unit_item','.ability'):continue
  try:j=json.loads(p.read_text())
  except (ValueError,UnicodeError):continue
  if any(v=='trader_light_frigate'for v in walk(j)):
   explicit_refs.append(str(p))
assert all(Path(p).name in ('trader_unlock_trade_escorts_0.research_subject','eivonns_light_ships.ability')for p in explicit_refs),explicit_refs
report={'status':'PASS — static proposal review only; runtime NOT RUN','helper':str(HELPER),'helper_sha256':sha(HELPER),
 'files_checked':len(checks),'checks':checks,'idempotent_overlay':True,'control95_delta':delta,'optional_donnager_delta':optional_delta,
 'explicit_original_morrigan_consumers':explicit_refs,
 'morrigan_research_result':'No exact-unit-ID gameplay research filters found. Trade escort units_listing is presentation; native Eivonns spawn deliberately keeps original. Tag-based point_defense/missile upgrades retained by cloning.',
 'limitations':['Not JSON-schema validation; final integrated package requires its independent reference/manifest/schema contracts.',
 'No gameplay or per-muzzle damage event measurement. Equal numeric inputs prove preserved configuration, not measured damage equivalence.',
 '60-second firing charge retains separate 30-second reload. Their engine scheduling must be timed in game.',
 'Private standard Tachi hardware persists on capture and Pella-launched Tachis. Pella own magazine and Rocinante own magazine remain baseline.',
 'Acquisition duration remains unchanged: installed field does not establish continuous lock/reset semantics.'],
 'range_and_rails':r['railguns']}
OUT.write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps({'status':report['status'],'checked':len(checks),'output':str(OUT),'helper_sha256':report['helper_sha256']}))
