"""UN One: new-only unarmed envoy with bounded civilian repair assistance.
Native shared engineering-team buff is reused, not a competing capture system.
"""
from pathlib import Path
import copy,sys,json,hashlib
MAIN=Path('/run/media/haker/NVME 2/expanse-mod');sys.path.insert(0,str(MAIN/'tools'))
from common import read,write
ROOT=Path(__file__).resolve().parents[1];BASE=MAIN/'build/experiments/expanse_update23';GAME=Path('/run/media/haker/NVME 2/SteamLibrary/steamapps/common/Sins2');ID='expanse25_un_one';ABILITY=ID+'_civilian_relief';SHARED='expanse15_scirocco_engineering_teams'
def changes(base=BASE):
 base=Path(base);meta=read(MAIN/'audit/update25-unone/integration-spec.json');edits={};loc={};origins={};art={}
 def path(n,k):
  p=base/'entities'/f'{n}.{k}';return p if p.exists()else GAME/'entities'/p.name
 def get(n,k):return read(path(n,k))
 def put(n,k,d,source):
  rel=f'entities/{n}.{k}';assert not(base/rel).exists(),rel;edits[rel]=d;origins[rel]=str(path(source,k))
 for rel,h in meta['files'].items():
  p=Path(meta['output_game'])/rel;assert hashlib.sha256(p.read_bytes()).hexdigest()==h
  if(base/rel).exists():assert hashlib.sha256((base/rel).read_bytes()).hexdigest()==h
  else:art[rel]=p
 # This source is already an unarmed civilian frigate with native ordinary costs.
 u=get('expanse19_artemis','unit');u['spatial'].update(copy.deepcopy(meta['spatial']));u['build'].update(build_kind='frigate',build_group_id='frigate',supply_cost=25,build_time=60.,price={'credits':1200.,'metal':200.,'crystal':150.},prerequisites=[['trader_unlock_trade_port']]);u['build'].pop('exotic_price',None)
 u['skin_groups']=[{'skins':[ID]}];u['tags']=['frigate',ID];u['target_filter_unit_type']='frigate';u['physics'].update(max_linear_speed=900.,time_to_max_linear_speed=5.,max_angular_speed=30.);u['health']['durability']=100.
 for h in u['health']['levels']:
  h.update(max_hull_points=800.,max_armor_points=150.,armor_strength=25.,max_shield_points=0.,shield_point_restore_rate=0.);h.pop('shield_burst_restore',None)
 for k in ['weapons','attack','carrier','unit_factory','colonize_ability','item_builds','items','levels','capture_points']:u.pop(k,None)
 u['user_interface']['can_attack']=False;u['abilities']=[{'abilities':['expanse11_no_shields',ABILITY]}];u['antimatter']={'max_antimatter':100.,'antimatter_restore_rate':1.};put(ID,'unit',u,'expanse19_artemis')
 a=get(SHARED,'ability');a['action_data_source']=ABILITY;a['gui'].update(name=ABILITY+'.name',description=ABILITY+'.description');a['active_actions'].pop('auto_cast',None);put(ABILITY,'ability',a,SHARED)
 ads=get(SHARED,'action_data_source');ads['target_filters']=[x for x in ads['target_filters']if x['target_filter_id']=='engineering_target'];tf=ads['target_filters'][0]['target_filter'];tf['unit_types']=['corvette','frigate','cruiser'];tf['ownerships']=['self']
 # A political transport does not repair capital fleets: only unarmed own ships.
 # Existing same-effect shared buff exclusion includes pending applications.
 tf['constraints'].extend([{'constraint_type':'composite_not','constraint':{'constraint_type':'has_weapon','weapon_type':'normal'}},{'constraint_type':'composite_not','constraint':{'constraint_type':'has_weapon','weapon_type':'planet_bombing'}}])
 amounts={'cooldown':90.,'antimatter':25.,'range':2500.,'repair_per_tick':10.,'repair_ticks':15.}
 for row in ads['action_values']:row['action_value']['values']=[amounts[row['action_value_id']]]
 put(ABILITY,'action_data_source',ads,SHARED)
 skin=get('expanse19_artemis','unit_skin');st=skin['skin_stages'][0];st['unit_mesh']=copy.deepcopy(meta['skin_contract']['unit_mesh']);st.pop('child_mesh_alias_bindings',None);st['min_camera_distance']=meta['spatial']['radius']*2.;st['gui'].update(name=ID+'.name',description=ID+'.description');st['gui'].pop('special_operation_names',None);st['effects']['exhaust_effects']=copy.deepcopy(meta['skin_contract']['exhaust_effects']);st['effects']['hyperspace_effects']=copy.deepcopy(get('trader_skirmisher_corvette_frigate','unit_skin')['skin_stages'][0]['effects']['hyperspace_effects']);st['effects'].pop('flair_effects',None)
 # Reuse existing UNN transport acknowledgments, without an armed-ship voice set.
 voice=get('expanse15_truman','unit_skin')['skin_stages'][0]['sounds']['dialogue'];st.setdefault('sounds',{})['dialogue']={k:copy.deepcopy(voice[k])for k in ['selected','order_issued','retreat','hyperspace_charge_started','cannot_hyperspace','spawned','became_crippled','destroyed','insufficient_antimatter','ability_cooldown_is_not_completed']if k in voice};put(ID,'unit_skin',skin,'expanse19_artemis')
 loc.update({ID+'.name':'UN One — Diplomatic Envoy',ID+'.description':'Unarmed UNN diplomatic transport with limited civilian relief. 25 supply;800 hull/150 armor. One per player. Manually dispatch teams to repair a nearby owned unarmed non-capital ship. Ordinary phase travel is a Sins gameplay abstraction, not canonical UN One equipment. Shared civilian portrait pending integration.',ABILITY+'.name':'Civilian Relief Teams',ABILITY+'.description':'Manually assist one owned, damaged, unarmed corvette/frigate/cruiser within2500. Repairs10 hull each second for15seconds, up to150 total;90-second cooldown and25 antimatter. Cannot target this envoy, armed ships, capitals, allies or enemies. Shared engineering-team effect prevents duplicate application and station-repair overlap while active. Teams continue their short assignment after dispatch; no diplomacy income, capture or invulnerability.'})
 report={'status':'OFFLINE NEW-ONLY PROTOTYPE; RUNTIME NOT RUN','unit':ID,'ability':ABILITY,'output_art':meta['output_game'],'base':str(base),'player_recipes':{'expanse18_unn':{'buildable_units_append':[ID],'unit_limits_global_append':[{'tag':ID,'unit_limit':1}]}},'unit_tag_entries_append':[{'name':ID,'localized_name':ID+'.name'}],'research_prerequisite':'trader_unlock_trade_port','stats':{'supply':25,'hull':800,'armor':150,'durability':100,'speed':900,'cost':u['build']['price'],'build_seconds':60,'antimatter':100,'antimatter_restore':1},'function':{'manual':True,'range':2500,'cooldown':90,'antimatter_cost':25,'repair_tick':10,'ticks':15,'maximum_hull_repair':150,'ownership':'self only','types':tf['unit_types'],'requires_unarmed':True,'excluded':['self envoy','armed ships','capital ships','titan','planet','structure','enemy','allied other player']},'shared_repair_interaction':'Uses existing expanse15_scirocco_engineering_teams buff. Native fixed-one/preserve-existing limit and pending target exclusion prevent same-effect overlap; existing station repair excludes this exact ID. Effect ends on target ownership change. It is a dispatched 15-second team effect, not a persistent aura or an interceptable pod.','adaptations':['Humanitarian repair function is a game role, not a claimed show ability.','Phase travel is a Sins transport abstraction; no armed/capital/hero billing classification.','No faction-standing modifier, paid NPC contact, income, strategic resource, capture or global bonus.','The native shared target buff displays the existing engineering-team label, while source command/tooltip is Civilian Relief Teams.','Source art is assembled fan interpretation; portrait remains the existing civilian donor until main renders UN One UI.'],'runtime_unverified':['fresh load and manual ability targeting','ability availability without capital level UI','unarmed/armed and ally/enemy filters','shared repair effect exclusion and station interaction','native15-tick completion, target ownership change, save/reload','one-player limit queues and capture','normal frigate full-cost billing','native hyperspace and nozzle appearance','multiplayer']}
 return edits,loc,origins,art,report
if __name__=='__main__':
 edits,loc,origins,art,report=changes();out=ROOT/'build/update25-unone/fragments'
 for rel,d in edits.items():write(out/rel,d)
 for n,d in [('localization',loc),('origins',origins),('report',report)]:write(out/(n+'.json'),d)
 print(len(edits),'new defs',len(art),'private art dependencies')
