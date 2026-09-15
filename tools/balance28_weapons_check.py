"""Small in-memory offline check, writing only this worker's audit report."""
import hashlib,json,pathlib
import jsonschema
import balance28_weapons as m
B=pathlib.Path('/run/media/haker/NVME 2/expanse-mod/build/experiments/expanse_update27_5_menu')
SDK=pathlib.Path('/run/media/haker/NVME 2/SteamLibrary/steamapps/common/Sins of a Solar Empire II - Mod Tools/json_schemas')
A=pathlib.Path(__file__).resolve().parents[1]/'audit/balance28-weapons';A.mkdir(parents=True,exist_ok=True)
fp=lambda:{str(p.relative_to(B)):hashlib.sha256(p.read_bytes()).hexdigest()for p in (B/'entities').iterdir()if p.is_file()}
before=fp();edits,origins,report=m.changes(B,B)
assert edits==m.changes(B,B)[0]
assert edits==m.changes(edits,B)[0], 'Applying to overlay must not compound'
# Existing Stage A changes are preserved in post-A input.
overlay={'entities/expanse12_raptor.unit':json.loads((B/'entities/expanse12_raptor.unit').read_text())}
overlay['entities/expanse12_raptor.unit']['build']['supply_cost']=151
after=m.changes(overlay,B)[0]
assert after['entities/expanse12_raptor.unit']['build']['supply_cost']==151
assert m.changes(B,B,tachi_supply=95)[0]['entities/expanse_mcrn_corvette.unit']['build']['supply_cost']==95
opt=m.changes(B,B,donnager_cadence=True)[0]
assert opt['entities/expanse10_donnager_rail_0.weapon']['cooldown_duration']==24
assert edits['entities/expanse10_donnager_rail_0.weapon']['cooldown_duration']==30
errors=[];unavailable=[];checked=0
for rel,d in edits.items():
 schema_path=SDK/(pathlib.Path(rel).suffix[1:].replace('_','-')+'-schema.json')
 if not schema_path.exists():
  unavailable.append({'file':rel,'reason':'Matching pinned schema absent; exact pointer-only derivative reviewed, schema check NOT RUN'});continue
 schema=json.loads(schema_path.read_text());checked+=1
 for err in jsonschema.Draft7Validator(schema).iter_errors(d):errors.append({'file':rel,'pointer':'/'+ '/'.join(map(str,err.absolute_path)),'message':err.message})
# Check all NEW private IDs against the assembled in-memory overlay, and crucial
# typed references against overlay+baseline+native. No packages are generated.
refs={'torpedo_to_create':'unit','persistant_buff':'buff','action_data_source':'action_data_source','weapon':'weapon'}
refcount=0
for rel,d in edits.items():
 for node in m._walk(d):
  for key,ext in refs.items():
   value=node.get(key)
   if isinstance(value,str):
    target=f'entities/{value}.{ext}'
    assert target in edits or (B/target).is_file() or (m.GAME/target).is_file(),(rel,target)
    refcount+=1
  for key in ('abilities','skins'):
   if isinstance(node.get(key),list):
    ext='ability' if key=='abilities' else 'unit_skin'
    for value in node[key]:
     if isinstance(value,str):
      target=f'entities/{value}.{ext}';assert target in edits or (B/target).is_file() or (m.GAME/target).is_file(),(rel,target)
      refcount+=1
# Exclusion fence: private projectile derivatives only; original shared projectiles
# and OPA magazine/ship definitions do not occur in changes.
for rel in ['entities/expanse04_light_torpedo.unit','entities/expanse10_donnager_heavy_torpedo.unit','entities/expanse15_unn_light_torpedo.unit','entities/expanse19_defense_torpedo.unit','entities/expanse_rocinante_hero.unit','entities/expanse12_pella.unit','entities/expanse18_opa.player','entities/expanse18_unn.player','entities/trader_light_frigate.unit']:
 assert rel not in edits,rel
assert fp()==before
report['offline_checks']={'deterministic':'PASS','idempotent_frozen_multiplier':'PASS','stage_a_overlay_preservation':'PASS','95_supply_control':'PASS','optional_cadence_isolated':'PASS','schema_files_checked':checked,'schema_unavailable':unavailable,'schema_errors':errors,'typed_references_resolved':refcount,'shared_torpedo_exclusion':'PASS','frozen_entities_unchanged':'PASS','runtime':'NOT RUN'}
(A/'proposal.json').write_text(json.dumps(report,indent=2)+'\n')
(A/'origins.json').write_text(json.dumps(origins,indent=2)+'\n')
print(json.dumps(report['offline_checks'],indent=2))
