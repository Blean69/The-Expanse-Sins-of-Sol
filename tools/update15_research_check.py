#!/usr/bin/env python3
"""Integration contract checks, including dynamic discovery of future Truman torpedo program."""
import copy, json, tempfile
from pathlib import Path
from update15_research import BASE,GAME,SPECS,build_overlay,read,write,sha,resolve

def run(overlay,audit):
 overlay=Path(overlay);report=read(Path(audit)/'integration.json');checks=[]
 for rec in report['changes']:
  p=overlay/rec['file'];old=read(resolve(BASE,GAME,p.name));new=read(p)
  assert sha(p)==rec['sha256']
  if p.suffix=='.ability':
   assert new['level_source']=='research_prerequisites_per_level'
   assert new['level_prerequisites']==[[],[['trader_missile_weapon_damage_0']]]
   del new['level_prerequisites'];new['level_source']=old['level_source'];assert new==old
  elif p.suffix=='.action_data_source':
   orig={v['action_value_id']:v for v in old['action_values']}
   for v in new['action_values']:
    av=v['action_value'];ov=orig[v['action_value_id']]['action_value']
    if 'values'in ov:
     assert av['values'][0]==ov['values'][0]
     expected=round(ov['values'][0]*1.05,8)if v['action_value_id']=='heavy_torpedo_damage_value'else ov['values'][0]
     assert av['values'][1]==expected
     av['values']=ov['values']
   assert new==old,'Changed torpedo behavior beyond damage second level'
  elif p.suffix=='.research_subject':
   for k in ('domain','tier','field','field_coord','price','exotic_price','research_time','prerequisites','windfall'):
    assert new.get(k)==old.get(k),(p.name,k)
  checks.append(p.name)
 # Future-source discovery: realistic new program with independent UNN torpedo entity.
 with tempfile.TemporaryDirectory(prefix='research15-contract-',dir='/tmp')as td:
  root=Path(td);base=root/'base';out=root/'out'
  oldid='expanse12_raptor_light_magazine';newid='expanse15_truman_light_magazine'
  for ext in ('ability','action_data_source','buff'):
   d=read(BASE/'entities'/(oldid+'.'+ext));text=json.dumps(d).replace(oldid,newid).replace('expanse04_light_torpedo','expanse15_unn_light_torpedo')
   d=json.loads(text)
   if ext=='action_data_source':
    next(v for v in d['action_values']if v['action_value_id']=='heavy_torpedo_damage_value')['action_value']['values']=[375.0]
   write(base/'entities'/(newid+'.'+ext),d)
  write(base/'entities/expanse15_unn_light_torpedo.unit',read(BASE/'entities/expanse04_light_torpedo.unit'))
  r=build_overlay(base,out,GAME)
  p=r['torpedo_programs'][newid]
  assert p['damage_before']==375 and p['damage_after']==393.75
  assert p['torpedo_entities']==['expanse15_unn_light_torpedo']
  # Refuse unknown source level semantics instead of silently overwriting existing research logic.
  a=read(base/'entities'/(newid+'.ability'));a['level_source']='unit_level';write(base/'entities'/(newid+'.ability'),a)
  try:build_overlay(base,root/'invalid',GAME)
  except AssertionError:pass
  else:raise AssertionError('Unexpected existing ability-level source accepted')
 result={'status':'PASS','checked_change_contracts':len(checks),'tests':['13 original node costs/times/tiers/fields/prerequisites/windfalls preserved','Every torpedo value at level0 exactly preserved','Level1 changes only actual impact damage by5%; timing/count/lifetime/health descriptors identical','Ability changes restricted to research-level source + two-level prerequisite list','Synthetic new Truman program dynamically discovered,375→393.75,correctUNNentitybinding','Unknown existing level semantics rejected'],'runtime_status':'NOT RUN'}
 write(Path(audit)/'contract-checks.json',result);print(json.dumps(result,indent=2))

if __name__=='__main__':run('build/update15-research-verified','audit/update15-research')
