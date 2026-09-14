"""Native paid Influence contacts; no study, sample or salvage-state substitute."""
import copy,json,zipfile
from pathlib import Path
from update20_fleet import ROOT,GAME
from validate_experiments import read,require,sha256

ITEM='expanse26_tycho_recovery_component'
METAL='expanse26_ceres_material_shipment'
VISION='expanse26_ceres_registry_access'

def changes(base):
 base=Path(base);edits={};loc={};origins={};art={};report={'runtime':'NOT RUN','contacts':{}}
 def labels(n,name,desc):
  loc[n+'.name']=name;loc[n+'.description']=desc
  return {'name':n+'.name','description':n+'.description'}
 item=read(GAME/'entities/trader_derelict_specialist.unit_item')
 item.update(labels(ITEM,'Tycho Recovery Equipment','Paid recovery component: +15% native capture points while fitted; one equipment slot. Does not improve boarding chance or create exclusive salvage claims.'))
 item['unit_modifiers']=[{'modifier_type':'unit_capture_points','value_behavior':'scalar','values':[.15]}]
 # Influence purchase supplies the component. Fitting requires no unrelated
 # civilian research, and no research tree is modified to deliver this service.
 item.pop('build_prerequisites',None)
 item.pop('price',None);item['is_finite']=True;item['always_show_in_shop']=True
 item['hud_icon']='expanse19_artemis_hud_icon'
 item['other_item_requirements']={'mutually_exclusive_items':['trader_derelict_specialist']}
 edits['entities/'+ITEM+'.unit_item']=item
 # One normal component; mutual exclusion prevents stacking native +150% and
 # contact +15%. Native specialist has no changed effect, price or research.
 native_item=read(GAME/'entities/trader_derelict_specialist.unit_item')
 native_item.setdefault('other_item_requirements',{}).setdefault('mutually_exclusive_items',[]).append(ITEM)
 edits['entities/trader_derelict_specialist.unit_item']=native_item
 origins['entities/trader_derelict_specialist.unit_item']=str(GAME/'entities/trader_derelict_specialist.unit_item')
 edits['entities/'+ITEM+'.npc_reward']={'version':0,'gui':{'hud_icon':item['hud_icon'],**labels(ITEM,'Tycho Recovery Equipment','Receive one equippable recovery component. +15% native capture points, one slot; no change to boarding probability. Fitting takes the normal component build time.')},'type':'ship_component','item':ITEM}
 edits['entities/'+METAL+'.npc_reward']={'version':0,'gui':{'hud_icon':'expanse19_artemis_hud_icon',**labels(METAL,'Bonded Metal Shipment','Receive 300 metal once per paid purchase. Two Influence; four-minute service cooldown. No passive income.')},'type':'assets','assets':{'metal':300.0}}
 vision=read(GAME/'entities/jiskun_share_vision.npc_reward');vision['gui']={'hud_icon':'expanse12_sunflare_hud_icon',**labels(VISION,'Shipping Registry Access','Native scout intelligence for 360 seconds. Coverage follows Ceres contact scouts and the engine detection rules. Four Influence; ten-minute service cooldown.')};edits['entities/'+VISION+'.npc_reward']=vision
 specs=[('pranast_united_npc','Tycho Engineering Bureau','Paid engineering and recovery services at Tycho Roadstead.',[
  {'reward':ITEM,'required_reputation_level':0,'influence_point_cost':4,'cooldown_duration':360}]),
  ('jiskun_force_npc','Ceres Shipping Exchange','Paid material shipments and temporary scout intelligence at Ceres Freeport.',[
   {'reward':METAL,'required_reputation_level':0,'influence_point_cost':2,'cooldown_duration':240},
   {'reward':VISION,'required_reputation_level':1,'influence_point_cost':4,'cooldown_duration':600}])]
 for ident,name,desc,rewards in specs:
  d=read(GAME/'entities'/f'{ident}.player')
  for visual in d['npc']['visuals']:visual.update(labels('expanse26_'+ident,name,desc))
  d['npc']['reputation']['rewards']=rewards
  # Native markets, neutral ownership, scouts and AI remain intact. This menu
  # provides contracts, not free allied fleet auras or sample authorization.
  edits['entities/'+ident+'.player']=d;origins['entities/'+ident+'.player']=str(GAME/'entities'/f'{ident}.player')
  report['contacts'][ident]={'display_name':name,'rewards':rewards,'native_scouts_and_markets':'preserved','native_player_sha256':sha256(GAME/'entities'/f'{ident}.player')}
 # Existing fixed scenario gets guaranteed contacts. Other generated maps show
 # these services only when the corresponding native NPC filling is selected.
 src=base/'scenarios/expanse18_sol_three_homes.scenario';out=ROOT/'build/update26-contacts/scenarios/expanse26_sol_three_homes.scenario';out.parent.mkdir(parents=True,exist_ok=True)
 with zipfile.ZipFile(src) as z:members={n:z.read(n) for n in z.namelist()}
 chart=json.loads(members['galaxy_chart.json']);changed=[]
 for root in chart['root_nodes']:
  for node in root.get('child_nodes',[]):
   if node['id']==5:node['primary_fixture_override_name']='expanse26.tycho_roadstead';changed.append(5)
   if node['id']==6:node['primary_fixture_override_name']='expanse26.ceres_freeport';node['ownership']={'npc_filling_name':'jiskun_force'};changed.append(6)
 require(changed==[5,6],'Unexpected fixed map topology')
 members['galaxy_chart.json']=(json.dumps(chart,indent=2)+'\n').encode()
 info=json.loads(members['scenario_info.json']);info['name']=':Sol — Three Homes / Contacts';info['description']=':Fixed three-player Sol test map with Tycho Engineering Bureau and Ceres Shipping Exchange. Normal start recommended. Paid services in the Influence panel; native NPC visuals remain placeholders. Slot1 Earth, Slot2 Mars, Slot3 Belt.';members['scenario_info.json']=(json.dumps(info,indent=2)+'\n').encode()
 with zipfile.ZipFile(out,'w',zipfile.ZIP_DEFLATED) as z:
  for n,blob in members.items():
   zi=zipfile.ZipInfo(n,(2026,9,14,0,0,0));zi.compress_type=zipfile.ZIP_DEFLATED;z.writestr(zi,blob)
 art['scenarios/'+out.name]=out
 u=read(base/'uniforms/scenario.uniforms')
 u['scenarios'].append('expanse26_sol_three_homes');edits['uniforms/scenario.uniforms']=u;report['scenario_registration']=u
 loc['expanse26.tycho_roadstead']='Tycho Roadstead';loc['expanse26.ceres_freeport']='Ceres Freeport'
 report['map']={'file':out.name,'changed_nodes':changed,'topology_preserved':True,'old_scenario_retained':True,'other_maps':'Pranast and Jiskun slots provide the renamed services where present; other NPCs unchanged.'}
 report['registry_additions']={'npc_reward':[ITEM,METAL,VISION]}
 report['limits']=['Native NPC art/defense fleets and auction markets retained.','Native Jiskun provides_detection flag retained; no invented stealth exception.','Exclusive salvage, sample authorization, containment study and ProtoTech remain absent.','Influence charging, timed vision, fitting and multiplayer require in-game validation.']
 return edits,loc,origins,art,report
