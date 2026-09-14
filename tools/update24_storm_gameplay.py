"""New-only Gathering Storm gameplay fragments. No game or shared-definition writes."""
from pathlib import Path
import copy,json,sys
MAIN=Path('/run/media/haker/NVME 2/expanse-mod');sys.path.insert(0,str(MAIN/'tools'))
from common import read,write
ROOT=Path(__file__).resolve().parents[1];BASE=MAIN/'build/experiments/expanse_update22';GAME=Path('/run/media/haker/NVME 2/SteamLibrary/steamapps/common/Sins2');ID='expanse24_gathering_storm';UNLOCK=ID+'_procurement'
def changes(base=BASE):
 base=Path(base);edits={};loc={};origins={};meta=read(ROOT/'audit/update24-storm/integration-spec.json')
 def path(n,k):
  p=base/'entities'/f'{n}.{k}';return p if p.exists()else GAME/'entities'/f'{n}.{k}'
 def get(n,k):return read(path(n,k))
 def put(n,k,d,source):
  rel=f'entities/{n}.{k}';assert not (base/rel).exists();edits[rel]=d;origins[rel]=str(path(source,k))
 # Magazine's buff memory and recharge semantics are retained exactly.
 old='expanse12_raptor_light_magazine';mag=ID+'_light_magazine'
 for kind in ['ability','buff','action_data_source']:
  d=json.loads(json.dumps(get(old,kind)).replace(old,mag))
  if kind=='ability':d['ability_positions']=[{'position':p['translation'],'rotation':[1,0,0,0,1,0,0,0,1]}for p in meta['meshpoints']if p['name'].startswith('weapon.torpedo.')]
  put(mag,kind,d,old)
 loc[mag+'.name']='Laconian procurement light torpedo magazine'
 loc[mag+'.description']='Eighteen conventional Martian light torpedoes. Three per salvo at ten-second intervals while a detected enemy is available; 120-second reload after the last salvo. Existing warhead, fuel and reactor-overcharge magazine behavior retained.'
 # Native capital progression/items, ordinary cruiser production billing.
 d=get('expanse12_raptor','unit');d['skin_groups']=[{'skins':[ID]}];d['tags']=['capital_ship',ID];d['target_filter_unit_type']='capital_ship';d['build'].update(build_kind='cruiser',build_group_id='cruiser',supply_cost=300,build_time=240.,price={'credits':9000.,'metal':3000.,'crystal':2200.},exotic_price=[{'exotic_type':'offense','count':2},{'exotic_type':'utility','count':2},{'exotic_type':'ultimate','count':2}],prerequisites=[[UNLOCK]])
 d['physics'].update(max_linear_speed=1400.,time_to_max_linear_speed=4.,max_angular_speed=25.)
 # Fast attack ship, not a regenerating titan. Preserve capital per-level curve.
 for level in d['health']['levels']:
  level['max_hull_points']=round(level['max_hull_points']*6000/4500,6);level['max_armor_points']=round(level['max_armor_points']*3000/2600,6)
 d['health']['durability']=500.;d['attack']=get('expanse_donnager_battleship','unit')['attack'];d['spatial'].update(meta['spatial']);d['spatial']['collision_rank']=2
 d['abilities']=[{'abilities':[mag,'expanse12_raptor_reactor','expanse11_no_shields']}]
 # No hero action state, capture, corvette factory, colony or reactor-death splash.
 d.pop('colonize_ability',None);d['weapons']['weapons']=[]
 for i,rig in enumerate(meta['rigs']):
  weapon=ID+f'_pdc_{i}';w=get('expanse12_raptor_pdc_0','weapon');w['name']=ID+'.pdc.name';w['turret']=copy.deepcopy(rig['turret_override']);assert w['damage']/w['cooldown_duration']==117.6;put(weapon,'weapon',w,'expanse12_raptor_pdc_0')
  d['weapons']['weapons'].append({'weapon':weapon,'mesh_point':rig['mesh_point'],'weapon_position':rig['position'],'up':rig['up'],'forward':rig['forward'],'yaw_arc':rig['yaw_arc'],'pitch_arc':rig['pitch_arc']})
 rail=ID+'_keel_rail';w=get('expanse10_donnager_rail_0','weapon');w.pop('turret');w['pitch_speed']=0.;w['yaw_speed']=0.;w['name']=ID+'.rail.name';put(rail,'weapon',w,'expanse10_donnager_rail_0')
 r=meta['fixed_rail'];d['weapons']['weapons'].append({'weapon':rail,'mesh_point':r['mesh_point'],'weapon_position':r['weapon_position'],'non_turret_muzzle_positions':[r['weapon_position']],'up':[0,1,0],'forward':[0,0,1],'yaw_arc':r['yaw_arc'],'pitch_arc':r['pitch_arc']});d['weapons']['max_range_weapon_index']=6;d['ai']['attack_target_type_groups_matching_weapon']=rail;put(ID,'unit',d,'expanse12_raptor')
 skin=get('expanse12_raptor','unit_skin');stage=skin['skin_stages'][0];stage['unit_mesh']['mesh']=meta['hull_mesh'];stage['min_camera_distance']=float(meta['spatial']['radius'])*1.8;stage['gui'].update(name=ID+'.name',description=ID+'.description');stage['child_mesh_alias_bindings']['map']=[{'mesh_alias_name':f'expanse24_storm_pdc_{part}','mesh_definition':{'mesh':f'expanse24_storm_pdc_{part}','shader':'ship','is_shadow_blocker':True}}for part in ['base','barrel']]
 # Generic MCRN acknowledgment replaces the donor Raptor identity line.
 stage['sounds']['dialogue']['spawned']={'neutral':['expanse17_voice_mcrn_orders']};put(ID,'unit_skin',skin,'expanse12_raptor')
 research=get('trader_unlock_loyalist_titan','research_subject');research.update(tier=4,field_coord=[7,4],research_time=420.,price={'credits':4000.,'metal':1000.,'crystal':1600.},exotic_price=[{'exotic_type':'ultimate','count':2}],prerequisites=[['trader_unlock_loyalist_titan']],name=UNLOCK+'.name',name_uppercase=UNLOCK+'.upper');put(UNLOCK,'research_subject',research,'trader_unlock_loyalist_titan')
 loc.update({ID+'.name':'Gathering Storm — Pulsar-class destroyer',ID+'.description':'Rare late-game Laconian procurement prototype. Fast, shieldless capital with six 117.6-DPS PDCs, a fixed keel rail and conventional torpedo magazine. One per player. Narrow rail alignment makes flanking effective. Shared prototype portrait and generic Martian crew.',ID+'.pdc.name':'Laconian procurement PDC',ID+'.rail.name':'Pulsar fixed keel railgun',UNLOCK+'.name':'Laconian Destroyer Procurement',UNLOCK+'.upper':'LACONIAN DESTROYER PROCUREMENT'})
 report={'status':'PRIVATE NEW DEFINITIONS; RUNTIME NOT RUN','unit_id':ID,'unlock':UNLOCK,'art_game_directory':meta['output_game'],'base':str(base),'player_recipes':{'expanse18_mcrn':{'buildable_units_append':[ID],'research_subjects_append':[UNLOCK],'unit_limits_global_append':[{'tag':ID,'unit_limit':1}]}},'unit_tag_entries_append':[ID],'research_merge':{'domain':'military','field':'military_experimental','proposed_field_coord':[7,4],'main_must_resolve_grid_occupancy':True},'weapon_summary':{'pdc_count':6,'pdc_each_dps':117.6,'pdc_range':4500,'rail_damage':w['damage'],'rail_cooldown':w['cooldown_duration'],'rail_penetration':w['penetration'],'rail_tracking_speed':0,'rail_half_arc_degrees':2},'native_dependencies':['expanse12_raptor_reactor ability/buff/action data source','expanse11_no_shields ability/buff','Raptor shared accepted torpedo projectile unit/action chain and military warhead research','Raptor generic crew/effect aliases and plumes','trader_unlock_loyalist_titan native existing research prerequisite'],'adaptations':['Rare MCRN acquisition is a faction-access adaptation; the canonical vessel is Laconian Pulsar-class.','164.306m length, weapon count, resources, speed and hull values are mod design choices, not canonical specifications.','No Magnetar field weapon, automatic hull regrowth, shield or silent-running mechanic supplied.','Existing first-capital discount avoidance uses native build_kind cruiser while unit target type, progression and items remain capital_ship. Runtime purchase/AI verification remains required.','Shared Raptor portrait is explicitly temporary; actual Storm preview is available for main UI packaging.'],'runtime_checks_not_run':['ordinary resource charging including free-first-capital boundary','one-per-player queue/capture/save behavior','research completion existing and newly built units','target tracking and fixed rail alignment','torpedo spawn/reload and overcharge','plume appearance and rendering','multiplayer/save/reload']}
 return edits,loc,origins,report
if __name__=='__main__':
 edits,loc,origins,report=changes();out=ROOT/'build/update24-storm/fragments'
 for rel,d in edits.items():write(out/rel,d)
 for name,d in [('localization',loc),('origins',origins),('report',report)]:write(out/(name+'.json'),d)
 print(len(edits),'new definitions')
