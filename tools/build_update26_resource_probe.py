"""Separately labeled native currency receive/spend test; never production/plating."""
import copy,json
from pathlib import Path
from update20_fleet import ROOT,GAME
from update21_factions import FACTIONS,WRAPPERS
from doctrine_package import package
from validate_experiments import read,require
from build_polish import write
RESOURCE='expanse18_prototech_composite'
GRANT='expanse26_composite_receive_one_test'
DEBIT='expanse26_composite_spend_one_test'

def definitions(base):
 old=ROOT/'build/laboratory/update18/composite/resource-probe';edits={};loc={}
 ex=read(old/'entities'/f'{RESOURCE}.exotic');ex['description']=RESOURCE+'.probe26_description';loc[ex['name']]='ProtoTech Composite';loc[ex['description']]='Distinct experimental resource. Currency test only; no plating, containment study or refinery enabled.';edits['entities/'+RESOURCE+'.exotic']=ex
 grant=read(old/'entities/expanse18_composite_probe_receive_one.research_subject')
 grant.update(domain='military',field='military_engineering',name=GRANT+'.name',name_uppercase=GRANT+'.upper',description=GRANT+'.description',hud_icon='expanse19_artemis_hud_icon',tooltip_picture='expanse19_artemis_tooltip_picture')
 occupied=[]
 for p in (base/'entities').glob('*.player'):
  if p.stem not in {*FACTIONS.values(),*WRAPPERS}:continue
  for n in read(p)['research']['research_subjects']:
   f=base/'entities'/f'{n}.research_subject';d=read(f if f.exists() else GAME/'entities'/f.name)
   if d['field']=='military_engineering':occupied.append(d['field_coord'][1])
 grant['field_coord']=[0,max(occupied)+1];edits['entities/'+GRANT+'.research_subject']=grant
 loc.update({GRANT+'.name':'LAB TEST: receive one Composite',GRANT+'.upper':'LAB TEST: RECEIVE ONE COMPOSITE',GRANT+'.description':'One-time native windfall: exactly one distinct ProtoTech Composite. Costs 1 credit and 1 second. Save/reload at balance 1 before spending. This is a currency test, not a study or production unlock.'})
 debit=read(old/'entities/expanse18_composite_probe_debit_one.unit_item');debit.update(name=DEBIT+'.name',description=DEBIT+'.description',build_prerequisites=[[GRANT]],hud_icon='expanse19_artemis_hud_icon',tooltip_picture='expanse19_artemis_tooltip_picture');edits['entities/'+DEBIT+'.unit_item']=debit
 loc[DEBIT+'.name']='LAB TEST: spend one Composite';loc[DEBIT+'.description']='Inert defense-slot test item: costs 1 ProtoTech Composite and 1 credit. No shield or combat benefit. After purchasing, a second eligible ship must be unable to buy at balance 0.'
 uniform=read(old/'merge/uniforms/exotic.uniforms');edits['uniforms/exotic.uniforms']=uniform
 for owner in [*FACTIONS.values(),*WRAPPERS]:
  p=read(base/'entities'/f'{owner}.player');p['research']['research_subjects'].append(GRANT);p['ship_components'].append(DEBIT);edits[f'entities/{owner}.player']=p
 text=read(base/'localized_text/en.localized_text');text.update(loc);edits['localized_text/en.localized_text']=text
 meta=read(base/'.mod_meta_data');meta.update(display_name='The Expanse — 0.26 COMPOSITE CURRENCY TEST',display_version='0.26.0-probe',short_description='Separate receive 1/save/spend 1/reject 0 test. No plating.',long_description='LABORATORY ONLY. Combined fleet roster plus one native experimental exotic resource, one one-time credit-priced grant and an inert item sink. No study, refinery, free random stock or shield item. Do not use for balance multiplayer sessions.');edits['.mod_meta_data']=meta
 return edits

if __name__=='__main__':
 base=ROOT/'build/experiments/expanse_update26_sandbox';out=ROOT/'build/experiments/expanse_update26_composite_probe';edits=definitions(base)
 print(json.dumps(package(base,out,edits,{},ROOT/'docs/update26-composite-probe.md',ROOT/'audit/update26-composite-probe'),indent=2))
