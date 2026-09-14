"""0.27 private OPA capital and Behemoth art replacement recipes."""
from pathlib import Path
from copy import deepcopy as cp
import hashlib,json
ROOT=Path(__file__).resolve().parents[1];MAIN=Path('/run/media/haker/NVME 2/expanse-mod');BASE=MAIN/'build/experiments/expanse_update26';AUD=ROOT/'audit/update27-opa';DARK='expanse27_dark_star';BEHE='expanse24_behemoth';NEWBEHE='expanse27_behemoth'

def rename(x,a,b):
 if isinstance(x,str):return x.replace(a,b)
 if isinstance(x,list):return [rename(v,a,b)for v in x]
 if isinstance(x,dict):return {k:rename(v,a,b)for k,v in x.items()}
 return x

def changes(base=BASE,art_directory=AUD):
 base=Path(base);art_directory=Path(art_directory);dark=json.loads((art_directory/(DARK+'-art.json')).read_text());behe=json.loads((art_directory/(NEWBEHE+'-art.json')).read_text());edits={};loc={};origins={};sources={}
 def read(n):
  p=base/'entities'/n;sources[str(p)]=hashlib.sha256(p.read_bytes()).hexdigest();return json.loads(p.read_text())
 def put(n,d,origin):edits['entities/'+n]=d;origins['entities/'+n]=str(base/'entities'/origin)
 def magazine(old,new,ports):
  for ext in ['ability','buff','action_data_source']:
   d=rename(read(old+'.'+ext),old,new)
   if ext=='ability':d['ability_positions']=cp(ports)
   put(new+'.'+ext,d,old+'.'+ext)
  strings=json.loads((base/'localized_text/en.localized_text').read_text())
  for suffix in ['name','description']:loc[new+'.'+suffix]=strings[old+'.'+suffix]
 def skin(origin,new,art):
  d=read(origin+'.unit_skin')
  for s in d['skin_stages']:
   s['unit_mesh']['mesh']=art['hull_mesh'];s['min_camera_distance']=art['spatial']['radius']*1.6
   s['child_mesh_alias_bindings']={'map':[{'mesh_alias_name':art['id']+'_pdc_'+r,'mesh_definition':{'mesh':art['id']+'_pdc_'+r,'shader':'ship','is_shadow_blocker':True}}for r in ['base','barrel']]}
   s['effects']['exhaust_effects']={'particle_effects':[{'particle_effect':art['plumes']['idle']}]}
   for k in ['travel_effect','travel_effect_between_stars','travel_effect_destabilized']:s['effects']['hyperspace_effects'][k]=art['plumes']['phase']
   s['gui'].update(name=new+'.name',description=new+'.description')
   # Independently rendered private portraits are supplied by the art wrapper.
   for k in ['hud_icon','hud_monochrome_icon','hud_picture','tooltip_picture']:s['gui'][k]=art['id']+'_'+('main_view_icon'if k=='hud_monochrome_icon'else k)
   for k,suffix in [('icon','main_view_icon'),('selected_icon','main_view_icon_selected'),('sub_selected_icon','main_view_icon_sub_selected')]:s['main_view_icon'][k]=art['id']+'_'+suffix
  return d
 def armament(unit,art,oldpdc,newpdc):
  pdc=read(oldpdc+'.weapon');pdc['turret']=cp(art['rigs'][0]['turret_override']);put(newpdc+'.weapon',pdc,oldpdc+'.weapon')
  unit['weapons']={'weapons':[{'weapon':newpdc,'mesh_point':r['mesh_point'],'weapon_position':r['position'],'up':r['up'],'forward':r['forward'],'yaw_arc':r['yaw_arc'],'pitch_arc':r['pitch_arc']}for r in art['rigs']],'max_range_weapon_index':0}
  unit['ai']['attack_target_type_groups_matching_weapon']=newpdc;unit['ai']['attack_target_type_groups']=cp(pdc['attack_target_type_groups'])
 # Native capital framework, same Amun movement/target attack pattern, unchanged
 # original rail and projectile/controller identities preserve cloak semantics.
 amun=read('expanse_amun_ra.unit');unit=read('expanse21_opa_command.unit');unit['spatial']=cp(dark['spatial']);unit['physics']=cp(amun['physics'])
 unit.pop('colonize_ability',None)
 for k in ['attack','move','hyperspace','ai','ship_roles','cloak_ability','antimatter']:
  if k in amun:unit[k]=cp(amun[k])
 unit['build'].update(price={'credits':6000.,'metal':1100.,'crystal':800.},build_time=150.,supply_cost=140,build_kind='capital_ship',build_group_id='capital_ship',prerequisites=[['expanse27_dark_star_procurement']]);unit['skin_groups']=[{'skins':[DARK]}];unit['tags']=['capital_ship',DARK];unit['target_filter_unit_type']='capital_ship'
 health=cp(amun['health']);health['levels']=[]
 for i in range(10):
  h=cp(amun['health']['levels'][0]);h['max_hull_points']=3600.*(1+.03*i);h['max_armor_points']=1800.*(1+.03*i);h['experience_given_on_death']=100.+20*i;health['levels'].append(h)
 unit['health']=health
 for level in unit['levels']['levels']:level.pop('weapon_modifiers',None)
 unit['item_builds']=[r for r in unit.get('item_builds',[])if all('colony'not in item for item in r['build_group'])]
 unit['abilities']=cp(amun['abilities']);magazine('expanse06_amun_magazine',DARK+'_magazine',dark['torpedo_ports'])
 unit['abilities']=rename(unit['abilities'],'expanse06_amun_magazine',DARK+'_magazine')
 armament(unit,dark,'expanse06_amun_pdc_0',DARK+'_pdc')
 rail=cp(amun['weapons']['weapons'][-1]);rail.update(mesh_point='weapon.rail.0',weapon_position=dark['rail_position'],non_turret_muzzle_positions=[dark['rail_position']]);unit['weapons']['weapons'].append(rail);unit['weapons']['max_range_weapon_index']=3
 if 'spawn_loot' in unit.get('spawn_debris',{}):unit['spawn_debris']['spawn_loot']['loot_name']=DARK+'.wreck';loc[DARK+'.wreck']='Dark Star wreckage'
 put(DARK+'.unit',unit,'expanse_amun_ra.unit');put(DARK+'.unit_skin',skin('expanse_amun_ra',DARK,dark),'expanse_amun_ra.unit_skin')
 loc[DARK+'.name']='OPAS Dark Star';loc[DARK+'.description']='A salvaged stealth capital: three defensive PDCs, one fixed Amun-Ra railgun, the existing stealth torpedo magazine and guarded boarding. Black-ops salvage is a fan-design adaptation. Fragile compared with dedicated battleships.'
 # Only art/spatial/mount coordinates and private magazine identity change on
 # Behemoth. Existing hull/armor, service, support, cost and speed stay exact.
 old=read(BEHE+'.unit');unit=cp(old);unit['spatial']=cp(behe['spatial']);armament(unit,behe,'expanse24_behemoth_pdc',NEWBEHE+'_pdc');magazine('expanse24_behemoth_magazine',NEWBEHE+'_magazine',behe['torpedo_ports']);unit['abilities']=rename(unit['abilities'],'expanse24_behemoth_magazine',NEWBEHE+'_magazine')
 put(BEHE+'.unit',unit,BEHE+'.unit');put(BEHE+'.unit_skin',skin(BEHE,BEHE,behe),BEHE+'.unit_skin')
 # GUI resources use fresh offline rendered silhouettes; main registers aliases.
 for art in [dark,behe]:
  for role in ['hud_icon','hud_picture','tooltip_picture','main_view_icon','main_view_icon_selected','main_view_icon_sub_selected']:edits['brushes/'+art['id']+'_'+role+'.brush']={'supported_dpis':[150,200],'normal_state':{'texture':art['id']+'_'+role}}
 report={'base':str(base),'status':'PRIVATE FRAGMENT; RESEARCH/PLAYER/REGISTRY MERGES REQUIRED','unit_id':DARK,'behemoth_unit_id':BEHE,'source_definitions_sha256':sources,'origins':origins,'player_recipes':{'opa':{'buildable_units_append':[DARK],'research_requirement':'expanse27_dark_star_procurement','native_procurement':'capital_ship; ordinary first-capital entitlement deliberately retained per main instruction'}},'unit_tag_entries_append':[{'name':DARK,'localized_name':DARK+'.name'}],'research_recipe':{'id':'expanse27_dark_star_procurement','owner':'main','faction':'OPA','tier':3,'role':'priced salvage procurement, no automatic/free unit spawn'},'preserved':['all original Amun definitions and cloak/boarding callbacks','Amun rail and torpedo damage/cadence/projectile type','Behemoth health/armor/support/hospital/AI service semantics/cost/movement','all original model assets'],'art_files':{},'stats':{'dark_star':{'hull':3600,'armor':1800,'supply':140,'price':{'credits':6000,'metal':1100,'crystal':800},'build_time':150,'pdc_count':3,'pdc_dps':85,'railgun':'original expanse06_amun_railgun','max_speed':amun['physics']['max_linear_speed']},'behemoth':{'hull':old['health']['levels'][0]['max_hull_points'],'armor':old['health']['levels'][0]['max_armor_points'],'pdc_count':8}},'distribution':'Local game derivative only. Do not publish paid model or its derivatives.','runtime':{k:'NOT RUN'for k in ['native capital procurement and UI','turret tracking/fire under movement','stealth reveal and boarding on new hull','eight engine plumes','save/reload and multiplayer','model performance']}}
 for art in [dark,behe]:
  for rel in art['art_files']:report['art_files'][rel]=str(Path(art['output_game'])/rel)
  for p in (Path(art['output_game']).parent/'ui').glob(art['id']+'*.png'):report['art_files']['textures/'+p.name]=str(p)
 return edits,loc,origins,report

if __name__=='__main__':
 edits,loc,origins,report=changes();out=ROOT/'build/update27-opa/overlay'
 for rel,d in edits.items():p=out/rel;p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(d,indent=2)+'\n')
 for name,d in [('gameplay-contract',report),('localization',loc),('origins',origins)]:p=AUD/(name+'.json');p.write_text(json.dumps(d,indent=2)+'\n')
 print(json.dumps({'entity_edits':len(edits),'art_files':len(report['art_files']),'stats':report['stats']}))
