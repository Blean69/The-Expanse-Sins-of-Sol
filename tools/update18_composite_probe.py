#!/usr/bin/env python3
"""Build DISABLED resource capability fragments; never a playable plating/production unlock.
The integrator owns applying shared registration/player/localization fragments.
"""
import argparse,copy,hashlib,json
from pathlib import Path
import jsonschema

ROOT=Path(__file__).resolve().parents[1]
MAIN=Path('/run/media/haker/NVME 2/expanse-mod')
BASE=MAIN/'build/experiments/expanse_update17'
GAME=Path('/run/media/haker/NVME 2/SteamLibrary/steamapps/common/Sins2')
SDK=GAME.parent/'Sins of a Solar Empire II - Mod Tools/json_schemas'
EXOTIC='expanse18_prototech_composite'
GRANT='expanse18_composite_probe_receive_one'
LOCK='expanse18_composite_probe_production_disabled'
DEBIT='expanse18_composite_probe_debit_one'
ELIGIBLE=['expanse_rocinante_hero','expanse12_pella','expanse12_raptor','expanse12_scirocco','expanse15_truman','expanse_donnager_battleship']

def read(p):return json.loads(Path(p).read_text(encoding='utf-8-sig'))
def write(p,d):p=Path(p);p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(d,indent=2)+'\n')
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def walk(x,path=''):
 if isinstance(x,dict):
  yield path,x
  for k,v in x.items():yield from walk(v,path+'/'+k)
 elif isinstance(x,list):
  for i,v in enumerate(x):yield from walk(v,path+'/'+str(i))
def strings(x):
 if isinstance(x,str):yield x
 elif isinstance(x,dict):
  for v in x.values():yield from strings(v)
 elif isinstance(x,list):
  for v in x:yield from strings(v)

def inventory():
 ids=[]
 for p in (BASE/'entities').iterdir():
  if any(k in p.stem.lower()for k in ['plating','prototech','adaptive_composite','protomolecule']):ids.append(p.name)
 guard=read(BASE/'entities/expanse11_no_shields.buff')
 mutation=read(GAME/'uniforms/unit_mutation.uniforms')
 rows=[]
 for n in ELIGIBLE:
  p=BASE/'entities'/(n+'.unit');d=read(p);h=d['health']['levels'][0];rows.append({'unit':n,'sha256':sha(p),'unmodified_base_hull':h['max_hull_points'],'base_shields':h.get('max_shield_points',0),'base_shield_regeneration':h.get('shield_point_restore_rate',0),'base_shield_delay':h.get('shield_point_restore_cooldown_duration_after_damage_taken'),'shield_burst':h.get('shield_burst_restore'),'guard_present_in_all_ability_sets':all('expanse11_no_shields'in group['abilities']for group in d['abilities']),'design_only_12_percent_capacity':round(h['max_hull_points']*.12,2),'design_only_regeneration_1_percent_capacity':round(h['max_hull_points']*.12*.01,2),'not_implemented':'Resource, shield-guard lifecycle, study interruption and refill tests have not passed runtime gates.'})
 refs=[]
 for p in sorted((BASE/'entities').iterdir()):
  if p.suffix not in {'.unit','.buff','.ability','.action_data_source','.unit_item','.research_subject'}:continue
  d=read(p)
  hits=[{'path':path,'modifier':v}for path,v in walk(d)if 'shield'in v.get('modifier_type','')]
  if hits:refs.append({'definition':p.name,'shield_modifiers':hits})
 players={n:read(BASE/'entities'/(n+'.player'))for n in ['trader_loyalist','trader_rebel','dlc_trader_loyalist']}
 hidden={n:[x for x in strings(d['research'])if x.startswith('trader_shield')]for n,d in players.items()}
 return {'baseline':str(BASE),'plating_entity_inventory':ids,'actual_item_absent':not ids,'shield_guard':guard,'permissions':{k:v for k,v in mutation['permission_infos'].items()if 'shield'in k},'eligibility_audit':rows,'remaining_shield_modifiers_in_baseline':refs,'shield_named_research_still_listed':hidden,'warnings':['No plating item or guard change generated.','Foreign shields/research/providers can act differently after capture; zero capacity and disabled restoration/absorption are distinct protections.','Removing global guard from an eligible hull would restore inherited shielding behavior even when item is absent; prohibited as shortcut.','A cosmetic rename does not avoid shield bypass, drain, shield-only damage or native shield recharge-delay semantics.']}

def build(out,audit):
 out,audit=Path(out).resolve(),Path(audit).resolve()
 if out.exists():raise FileExistsError(out)
 if not out.is_relative_to(ROOT/'build/laboratory/update18/composite'):raise ValueError('Probe output must remain under isolated laboratory/composite')
 out.mkdir(parents=True);source_hashes={}
 def source(rel):
  p=GAME/rel;source_hashes[str(p)]=sha(p);return read(p)
 ex=source('entities/utility.exotic');ex.update(name=EXOTIC+'.name',description=EXOTIC+'.description',insufficient_exotics_player_sound_id='insufficient_custom_exotics_a',pip_color='#67DDBB',ai_trade_value=1200)
 grant=source('entities/trader_economic_exotic_build_rate.research_subject')
 for k in ['exotic_factory_modifiers','extra_text_filter_strings','prerequisites','exotic_price']:grant.pop(k,None)
 grant.update(tier=0,field='civilian_policy',field_coord=[1,0],research_time=1.,price={'credits':1.},windfall={'exotics_given':[{'exotic_type':EXOTIC,'count':1}]},name=GRANT+'.name',name_uppercase=GRANT+'.name_uppercase',description=GRANT+'.description')
 lock=copy.deepcopy(grant);lock.pop('windfall');lock.update(tier=4,field_coord=[10,20],research_time=180.,price={'credits':9999999.},name=LOCK+'.name',name_uppercase=LOCK+'.name_uppercase',description=LOCK+'.description')
 debit=source('entities/trader_heavy_armor.unit_item')
 debit.pop('unit_modifiers',None);debit.update(name=DEBIT+'.name',description=DEBIT+'.description',build_time=1.,price={'credits':1.},exotic_price=[{'exotic_type':EXOTIC,'count':1}],build_prerequisites=[[GRANT]],max_count_on_unit=1)
 resources={EXOTIC+'.exotic':ex,GRANT+'.research_subject':grant,LOCK+'.research_subject':lock,DEBIT+'.unit_item':debit}
 checks=[]
 for n,d in resources.items():
  kind={'.exotic':'exotic','.research_subject':'research-subject','.unit_item':'unit-item'}[Path(n).suffix];sp=SDK/(kind+'-schema.json');source_hashes[str(sp)]=sha(sp)
  jsonschema.Draft202012Validator(read(sp)).validate(d);write(out/'entities'/n,d);checks.append(n)
 native_uniform=source('uniforms/exotic.uniforms')
 assert EXOTIC not in [v['name']for v in native_uniform['type_datas']]
 registration=copy.deepcopy(native_uniform);registration['overwrite_type_datas']=True;registration['type_datas'].append({'name':EXOTIC,'entity':EXOTIC})
 assert registration['type_datas'][:-1]==native_uniform['type_datas']
 sp=SDK/'exotic-uniforms-schema.json';source_hashes[str(sp)]=sha(sp);jsonschema.Draft202012Validator(read(sp)).validate(registration)
 # The registration file is a fragment under merge/, not automatically loaded.
 write(out/'merge/uniforms/exotic.uniforms',registration);checks.append('merge/uniforms/exotic.uniforms')
 manifest={'exotic':[EXOTIC],'research_subject':[GRANT,LOCK],'unit_item':[DEBIT]}
 loc={EXOTIC+'.name':'ProtoTech Composite',EXOTIC+'.description':'Distinct engineered exotic material. DISABLED LABORATORY REGISTRATION PROBE; no gameplay production or plating is unlocked.',GRANT+'.name':'LAB PROBE: receive one composite',GRANT+'.name_uppercase':'LAB PROBE: RECEIVE ONE COMPOSITE',GRANT+'.description':'One-time native research windfall gives exactly one ProtoTech Composite to this owner. This is a currency test, not a containment study.',LOCK+'.name':'DISABLED: composite production gate',LOCK+'.name_uppercase':'DISABLED: COMPOSITE PRODUCTION GATE',LOCK+'.description':'Unlisted probe-only prerequisite. Do not grant or add this node to the research tree. It prevents test-resource fabrication.',DEBIT+'.name':'LAB PROBE: spend one composite',DEBIT+'.description':'Inert test component. Costs one ProtoTech Composite and one credit; occupies a normal defense slot. No hull, armor, shield or ability benefit. Use a second capital to test insufficient-resource rejection after spending.'}
 write(out/'merge/localization.json',loc)
 write(out/'merge/manifest-additions.json',manifest)
 player_fragment={'scope':'Apply manually to each chosen test player wrapper only; never production baseline','append_research_subjects':[GRANT],'append_ship_components':[DEBIT],'optional_display_entry':{'exotic_name':EXOTIC,'exotic_definition':{'factory_build_time':180.,'factory_build_price':{'credits':800.,'metal':250.,'crystal':250.},'factory_build_prerequisites':[[LOCK]]}},'do_not_register_research_subject':[LOCK],'test_node_placement':'Native civilian_policy coordinate [1,0] is vacant in inspected0.17canonical tree; integrator must preserve reservation against other18nodes.','production_status':'DISABLED: optional entry has unreachable prerequisite; no free starting stock, survey drops or market/NPC routes provided.'}
 write(out/'merge/player-fragments.json',player_fragment)
 inv=inventory();write(audit/'inventory-and-shields.json',inv)
 report={'status':'OFFLINE SCHEMA PASS; DISABLED FRAGMENTS ONLY; RUNTIME NOT RUN','resource_id':EXOTIC,'distinct_from_existing_exotics':True,'existing_type_entries_unchanged':native_uniform['type_datas'],'schema_checks':checks,'source_hashes':source_hashes,'output_resources':{str(p.relative_to(out)):sha(p)for p in out.rglob('*')if p.is_file()},'runtime_gates':[{'gate':x,'status':'NOT RUN'}for x in ['new exotic accepted by engine registry','receive1 from actual windfall','distinct resource visible in HUD / insufficient-resource feedback','save/reload balance1','spend1 on real item leaves0','second eligible empty-slot purchase rejected at0','simultaneous purchases cannot overspend','ownerA receipt/spend never changes ownerB/C balances','multiplayer and save parity']],'no_dependent_features_built':['real paid containment study','composite refinery/production','Adaptive Composite Plating','global study announcements'],'integration_warning':'Do not copy merge/ into game expecting registration. Main owns merging uniforms/manifests/player/localization into a deliberately separate disabled probe package; no mod metadata or playable package emitted.'}
 write(audit/'resource-probe.json',report);write(out/'DISABLED.json',{'enabled':False,'runtime_verified':False,'purpose':'Manual laboratory resource registration/debit probe, not friends-playtest gameplay.'})
 return report

if __name__=='__main__':
 ap=argparse.ArgumentParser();ap.add_argument('--out',type=Path,default=ROOT/'build/laboratory/update18/composite/resource-probe');ap.add_argument('--audit',type=Path,default=ROOT/'audit/update18-composite');a=ap.parse_args();r=build(a.out,a.audit);print(json.dumps({'status':r['status'],'schema_checks':len(r['schema_checks']),'resource_id':r['resource_id']}))
