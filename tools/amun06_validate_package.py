"""Small supplemental Amun06 package checks; no package or installed mutation.
Existing project Resolver handles geometry/effects; this adds cap preservation,
uniform overlays, typed action references and core/optional-cloak separation.
"""
from pathlib import Path
import argparse,copy,json,sys,hashlib
import jsonschema
from PIL import Image
MAIN=Path('/run/media/haker/NVME 2/expanse-mod');sys.path.insert(0,str(MAIN/'tools'))
from validate_experiments import Resolver,read,require,sha256,file_hashes,strings,verify_pins
from build_combat03 import check_actions
ID='expanse_amun_ra';PDCS=[f'expanse06_amun_pdc_{i}'for i in range(3)]
PLAYERS=['trader_loyalist','trader_rebel','dlc_trader_loyalist']

def effective_uniform(mod,game,filename,array,idkey,flag):
 base=read(game/'uniforms'/filename);base_map={x[idkey]:x for x in base[array]};path=mod/'uniforms'/filename
 if not path.exists():return base_map
 data=read(path);require(flag in data and isinstance(data[flag],bool),'Specify uniform merge/overwrite intent explicitly: '+filename)
 for k,v in data.items():
  if k not in {array,flag}:require(base.get(k)==v,'Unrelated uniform setting changed: '+filename+'/'+k)
 if data[flag]:require(all(data.get(k)==v for k,v in base.items()if k not in {array,flag}),'Full uniform replacement omits existing settings: '+filename)
 rows=data[array];ids=[x[idkey]for x in rows];require(len(ids)==len(set(ids)),'Duplicate uniform ID: '+filename)
 merged={}if data.get(flag,False)else dict(base_map);merged.update({x[idkey]:x for x in rows})
 require(all(merged.get(k)==v for k,v in base_map.items()),'Changed or removed installed uniform entry: '+filename)
 return merged

class AmunResolver(Resolver):
 def __init__(self,mod,game):
  super().__init__(mod,game)
  self.resolve('uniforms/target_filter.uniforms','Amun uniform overlay');self.resolve('uniforms/attack_target_type_group.uniforms','Amun uniform overlay')
  self.filters=effective_uniform(self.mod,self.game,'target_filter.uniforms','common_target_filters','target_filter_id','overwrite_common_target_filters')
  self.groups=effective_uniform(self.mod,self.game,'attack_target_type_group.uniforms','attack_target_type_groups','unit_attack_target_type_group_id','overwrite_attack_target_type_groups')
 def weapon(self,name,skins,source):
  # Same geometry/effect checks as the project Resolver, but uniforms may be additive.
  path=self.resolve('entities/'+name+'.weapon',source);data=read(path)
  for skin in skins:
   for stage in skin['skin_stages']:
    meshes={b['mesh_alias_name']for b in stage.get('child_mesh_alias_bindings',{}).get('map',[])};effects={b['alias_name']for b in stage.get('effects',{}).get('effect_alias_bindings',[])}
    for k,v in data.get('turret',{}).items():
     if k.endswith('_mesh'):require(v in meshes,'Unbound turret mesh alias '+v)
    for k,v in data.get('effects',{}).items():
     if k.endswith('_effect')and isinstance(v,str):require(v in effects,'Unbound weapon effect alias '+v)
  require(data['uniforms_target_filter_id']in self.filters,'Unknown weapon uniform filter: '+name)
  require(set(data['attack_target_type_groups'])<=set(self.groups),'Unknown weapon attack group: '+name)
  if data['firing']['firing_type']=='spawn_torpedo':
   p=self.unit(data['firing']['torpedo_firing_definition']['spawned_unit'],path);require('torpedo'in p and p['target_filter_unit_type']=='torpedo'and p['ai_attack_target']['attack_target_type']=='torpedo','Invalid torpedo classification')
  return data

def check_action_values(mod,game,resolver,unit):
 from build_combat03 import is_buff_selector
 common=read(resolver.resolve('uniforms/action.uniforms',unit));common_values={v for ptr,v in strings(common)if ptr[-1]=='action_value_id'}|{'fixed_one','fixed_zero'};reports=[]
 for group in unit.get('abilities',[]):
  for aid in group['abilities']:
   abilitypath=resolver.resolve('entities/'+aid+'.ability',ID);ability=read(abilitypath);ads_path=resolver.resolve('entities/'+ability['action_data_source']+'.action_data_source',aid);ads=read(ads_path)
   values=common_values|{x['action_value_id']for x in ads.get('action_values',[])};filters={x['target_filter_id']for x in ads.get('target_filters',[])};modifiers={x['buff_unit_modifier_id']for x in ads.get('buff_unit_modifiers',[])}
   require(len(ads.get('action_values',[]))==len({x['action_value_id']for x in ads.get('action_values',[])}),'Duplicate ADS action values')
   require(len(ads.get('target_filters',[]))==len(filters),'Duplicate ADS target filters')
   seen=set();references=[]
   def walk(d,source):
    if isinstance(d,list):
     for v in d:walk(v,source)
    elif isinstance(d,dict):
     for k,v in d.items():
      if isinstance(v,str):
       if k in {'buff','watched_buff','persistant_buff'}:
        if is_buff_selector(d,k,v):continue
        p=resolver.resolve('entities/'+v+'.buff',source);references.append(str(p))
        if d.get('constraint_type')!='has_buff' and p not in seen:seen.add(p);walk(read(p),p)
       elif k in {'torpedo_to_create','unit_to_create'}:resolver.unit(v,source)
       elif k=='unit_definition':resolver.resolve('entities/'+v+'.unit',source)
       elif k=='action_data_source':resolver.resolve('entities/'+v+'.action_data_source',source)
       elif k in {'value_a','value_b','operand_value','value_id','cooldown_time','antimatter_cost','range','active_duration','required_available_supply','minimum_available_supply'}or k.endswith('_value'):
        require(v in values,'Unknown typed action value '+v+' in '+str(source))
       elif k in {'target_filter','target_filter_id'}:require(v in filters or v in resolver.filters,'Unknown exact action target filter '+v)
       elif k=='buff_unit_modifier_id':require(v in modifiers,'Unknown ADS modifier '+v)
      elif k=='target_filters'and isinstance(v,list)and all(isinstance(x,str)for x in v):require(set(v)<=filters,'Unknown target_filters list member')
      else:walk(v,source)
   walk(ability,abilitypath);walk(ads,ads_path)
   for binding in ads.get('effect_alias_bindings',[]):
    for ptr,val in strings(binding.get('alias_binding',{})):
     if ptr[-1]in {'particle_effect','beam_effect','shield_effect','trail_effect'}:resolver.resolve('effects/'+val+'.'+('exhaust_trail_effect'if ptr[-1]=='trail_effect'else ptr[-1]),ads_path)
     elif 'sounds'in ptr or ptr[-1]=='sound':resolver.resolve('sounds/'+val+'.sound',ads_path)
   reports.append({'ability':aid,'ADS':str(ads_path),'reachable_buffs':sorted(set(references)),'status':'PASS typed scalar/filter/modifier references'})
 return reports

def check_boarding(mod,resolver):
 ability=read(mod/'entities/expanse06_amun_boarding.ability');buff=read(mod/'entities/expanse06_amun_boarding.buff');ads=read(mod/'entities/expanse06_amun_boarding.action_data_source');values={x['action_value_id']:x['action_value']for x in ads['action_values']}
 actions=ability['active_actions']['actions']['actions'];require(len(actions)==1,'Boarding should schedule one modeled attempt');travel=actions[0]['travel_time'];require(travel['travel_time_source']=='explicit_time'and values[travel['explicit_time_value']]['values']==[3.0],'Boarding travel must use reviewed3s modeled delay')
 require(sum(x.get('operator_type')=='apply_buff'and x.get('buff')=='expanse06_amun_boarding'for x in actions[0]['operators'])==1,'Boarding must apply exactly one attempt buff')
 events=buff.get('trigger_event_actions',[]);require(len(events)==1 and events[0]['trigger_event_type']=='on_buff_started'and not buff.get('time_actions'),'Boarding must roll once on arrival-buff start')
 found=[]
 def collect(d):
  if isinstance(d,dict):
   found.append(d)
   for v in d.values():collect(v)
  elif isinstance(d,list):
   for v in d:collect(v)
 collect(buff);chances=[x for x in found if x.get('constraint_type')=='random_chance'];require(len(chances)==1 and values[chances[0]['chance_value']]['values']==[.1],'Boarding must have one10% roll')
 captures=[x for x in found if x.get('operator_type')=='change_owner_player'];require(len(captures)==1,'Unexpected repeated ownership transfer');require(captures[0]['new_owner_player']=={'player_type':'unit_owner','owned_unit':{'unit_type':'first_spawner'}},'Capture recipient must be initiating ship owner')
 required=ability['active_actions']['required_available_supply'];require(values[required].get('transform_type')=='per_build_or_virtual_supply'and values[required]['transform_unit']=={'unit_type':'target'},'Cast-time supply must derive from selected target')
 supply=[x for x in found if x.get('constraint_type')=='player_has_available_supply'];require(len(supply)==1 and values[supply[0]['minimum_available_supply']].get('transform_type')=='per_build_or_virtual_supply','Missing delayed target-supply recheck')
 return {'modeled_delay_seconds':3,'chance':.1,'attempts_per_cast':1,'supply_rechecked':True,'physical_interceptable_pod':False,'runtime':'NOT RUN; source/target context, delay and capture are not established by this offline graph'}


def check_amun06(mod,base,game,sdk,unit_id=ID,limit_tag=ID,pdc_weapon_ids=None,project_root=MAIN):
 require(unit_id==ID and limit_tag==ID and (pdc_weapon_ids is None or list(pdc_weapon_ids)==PDCS),'Unexpected Amun handoff identifiers')
 mod,base,game,sdk=map(Path,[mod,base,game,sdk])
 for name,p in [('package',mod),('preserved base',base),('installed game',game),('pinned SDK',sdk)]:require(p.is_dir(),'Missing '+name+' dependency; check NOT RUN: '+str(p))
 pins=verify_pins(project_root,game,sdk);unit=read(mod/'entities'/f'{ID}.unit');prior=file_hashes(base);current=file_hashes(mod)
 require(not set(prior)-set(current),'Previous package files removed')
 allowed={'.mod_meta_data','ASSET-SOURCES.md','localized_text/en.localized_text','uniforms/unit_tag.uniforms'}|{'entities/'+p+'.player'for p in PLAYERS}|{p for p in prior if p.endswith('.entity_manifest')}
 for p,h in prior.items():
  if p not in allowed:require(current[p]==h,'Previous package file changed: '+p)
 for p in set(current)-set(prior):require(not any(s in Path(p).name.lower()for s in ['cloak','revealed']),'Optional cloak candidate leaked into core: '+p)
 require('cloak_ability'not in unit,'Native cloak hook leaked into official-schema core')
 for rel in set(current)-set(prior):
  path=mod/rel
  if path.suffix in {'.unit','.unit_skin','.buff','.ability','.action_data_source'}:
   for ptr,val in strings(read(path)):
    require(not any('cloak'in k for k in ptr) and val!='cloak_quality','Observed-only cloak field leaked into core: '+rel+'/'+('/'.join(ptr)))
   def no_cloak_keys(d):
    if isinstance(d,dict):
     require(not any('cloak'in k for k in d),'Observed-only cloak key leaked into core: '+rel)
     for v in d.values():no_cloak_keys(v)
    elif isinstance(d,list):
     for v in d:no_cloak_keys(v)
   no_cloak_keys(read(path))
 for player in PLAYERS:
  old=read(base/'entities'/(player+'.player'));new=read(mod/'entities'/(player+'.player'));expected=copy.deepcopy(old)
  require(ID not in expected['buildable_units'],'Amun unexpectedly already in base player');expected['buildable_units'].append(ID);require(not any(x['tag']==ID for x in expected['unit_limits']['global']),'Amun cap already in base')
  expected['unit_limits']['global'].append({'tag':ID,'unit_limit':6});require(new==expected,'Player edit exceeds append Amun+six cap: '+player)
  hero=[x for x in new['unit_limits']['global']if x['tag']=='expanse_rocinante_hero'];require(hero==[{'tag':'expanse_rocinante_hero','unit_limit':1}],'Rocinante cap changed')
 require(ID in unit['tags'],'Amun unit lacks private cap tag')
 oldtags=read(base/'uniforms/unit_tag.uniforms');tags=read(mod/'uniforms/unit_tag.uniforms');require(tags.get('overwrite_unit_tags')is True,'Full tag table must express replacement');expected=copy.deepcopy(oldtags);extra=[x for x in tags['unit_tags']if x not in oldtags['unit_tags']];require(len(extra)==1 and extra[0]['name']==ID,'Wrong private tag additions');expected['unit_tags'].append(extra[0]);require(tags==expected,'Unrelated unit-tag or item-access edit')
 oldloc=read(base/'localized_text/en.localized_text');loc=read(mod/'localized_text/en.localized_text');require(all(loc.get(k)==v for k,v in oldloc.items()),'Prior localization changed');require(extra[0]['localized_name']in loc,'Missing cap-tag localization')
 mounts=unit.get('weapons',{}).get('weapons',[]);require(sorted(m['weapon']for m in mounts)==sorted(PDCS+['expanse06_amun_railgun']),'Unexpected additional independently firing weapon budget');selected=[m for m in mounts if m['weapon']in PDCS];require(len(selected)==3 and sorted(m['weapon']for m in selected)==PDCS,'Exactly three physical PDC entries required');require(len({tuple(m['weapon_position'])for m in selected})==3,'PDCs share the same declared physical origin')
 require(len([m for m in mounts if m['weapon'].startswith('expanse06_amun_pdc_')])==3,'Additional independently firing PDC budget')
 for name in PDCS:require(read(mod/'entities'/(name+'.weapon'))['turret']['type']=='biaxial','PDC is not intended yaw/pitch turret: '+name)
 required_abilities={'expanse06_amun_magazine','expanse06_amun_boarding'};actual={n for g in unit.get('abilities',[])for n in g['abilities']};require(actual==required_abilities,'Core ability set must be magazine+boarding only')
 types={'.unit':'unit','.unit_skin':'unit-skin','.weapon':'weapon','.ability':'ability','.buff':'buff','.action_data_source':'action-data-source','.player':'player','.brush':'brush'};schemas=0
 for p in mod.rglob('*'):
  if p.suffix in types:jsonschema.Draft7Validator(read(sdk/'json_schemas'/(types[p.suffix]+'-schema.json'))).validate(read(p));schemas+=1
 for name in ['unit-tag','target-filter','attack-target-type-group']:
  path=mod/'uniforms'/(name.replace('-','_')+'.uniforms')
  if path.exists():jsonschema.Draft7Validator(read(sdk/'json_schemas'/(name+'-uniforms-schema.json'))).validate(read(path));schemas+=1
 manifest_checks=[]
 for suffix in ['unit','unit_skin','weapon','ability','buff','action_data_source']:
  expected=sorted(p.stem for p in (mod/'entities').glob('*.'+suffix)if not (game/'entities'/p.name).exists());path=mod/'entities'/(suffix+'.entity_manifest');require(path.is_file(),'Missing additive entity manifest: '+suffix);require(read(path)['ids']==expected,'Incorrect additive manifest '+suffix);manifest_checks.append(suffix)
 resolver=AmunResolver(mod,game);resolver.unit(ID,'Amun06 package root')
 installed_cobalt=game/'entities/trader_light_frigate.unit';observed=read(installed_cobalt)['corruption'];require(unit.get('corruption')==observed,'Inherited corruption extension differs from installed Cobalt')
 for name in observed['negative_corruption_buffs']:resolver.resolve('entities/'+name+'.buff','installed corruption extension')
 strict_unit=copy.deepcopy(unit);strict_unit.pop('corruption');jsonschema.Draft202012Validator(read(sdk/'json_schemas/unit-schema.json')).validate(strict_unit)
 corruption_record={'field':'corruption','status':'OBSERVED INSTALLED EXTENSION; absent pinned schema','exact_installed_Cobalt_equality':True,'source':str(installed_cobalt),'source_sha256':sha256(installed_cobalt),'penalty_buffs':observed['negative_corruption_buffs'],'strict_other_fields':'PASS additional Draft2020 interpretation of SAME pinned Draft7 schema; does not certify excluded corruption field'}
 action_values=check_action_values(mod,game,resolver,unit)
 # Existing action walker adds localization/effect binding checks after exact typed refs.
 actions=check_actions(mod,resolver,ID);boarding=check_boarding(mod,resolver)
 ship_skin=resolver.skin(ID,'Amun UI integration')['skin_stages'][0]
 for key,role in {'hud_icon':'hud_icon','hud_monochrome_icon':'main_view_icon','hud_picture':'hud_picture','tooltip_picture':'tooltip_picture'}.items():require(ship_skin['gui'][key]=='expanse06_amun_'+role,'Amun GUI still uses another ship image: '+key)
 for key,role in [('icon','main_view_icon'),('selected_icon','main_view_icon_selected'),('sub_selected_icon','main_view_icon_sub_selected')]:require(ship_skin['main_view_icon'][key]=='expanse06_amun_'+role,'Amun tactical icon does not match selected geometry')
 metadata=read(mod/'.mod_meta_data');require(all(isinstance(metadata.get(k),str)and metadata[k]for k in ['display_name','display_version','short_description','long_description']),'Incomplete mod metadata display fields')
 for key in ['small_logo','large_logo']:resolver.resolve(metadata['logos'][key],'mod metadata logo')
 brush_checks=[]
 for p in (mod/'brushes').glob('expanse06_amun*.brush'):
  d=read(p);name=d['normal_state']['texture']
  for suffix in ['']+[str(x)for x in d.get('supported_dpis',[])]:
   image=resolver.resolve('textures/'+name+suffix+'.png',p)
   with Image.open(image)as im:require(im.mode=='RGBA'and im.getbbox()is not None,'Invalid UI image '+str(image))
  brush_checks.append(p.name)
 require(len(brush_checks)==6,'Expected six Amun-specific static UI brushes')
 return {'status':'PASS OFFLINE CORE CHECKS','runtime':'NOT RUN','pins':pins,'prior_files_preserved_except_reviewed_integration_fields':True,'players_six_cap_and_hero_one_preserved':PLAYERS,'three_physical_PDC_budgets':True,'schemas':schemas,'declared_schema_dialect':'Draft7; schema also contains unevaluatedProperties that Draft7 ignores','known_unit_extension':corruption_record,'additive_manifests':manifest_checks,'typed_action_graphs':action_values,'existing_action_graph_checks':actions,'boarding':boarding,'UI_brushes':brush_checks,'references':resolver.edges,'limits':['Six-cap queue/capture/rebuild enforcement needs runtime testing','Boarding timing, recipient ownership and randomness need runtime testing','PDC interception during explicit ship attack and shared budget need runtime testing','No optional cloak fields or files allowed in core; separate observed-field candidate is outside this gate']}

def main():
 p=argparse.ArgumentParser(description=__doc__)
 for k in ['mod','base','game','sdk']:p.add_argument('--'+k,type=Path,required=True)
 a=p.parse_args();root=Path(__file__).resolve().parents[1];out=root/'audit/amun06-c/package-validation.json'
 try:result=check_amun06(a.mod,a.base,a.game,a.sdk)
 except Exception as exc:
  result={'status':'FAIL / remaining checks NOT RUN','error':str(exc),'runtime':'NOT RUN'};out.parent.mkdir(parents=True,exist_ok=True);out.write_text(json.dumps(result,indent=2)+'\n');raise
 out.parent.mkdir(parents=True,exist_ok=True);out.write_text(json.dumps(result,indent=2)+'\n');print(json.dumps({k:v for k,v in result.items()if k not in ['references','typed_action_graphs','pins']},indent=2))
if __name__=='__main__':main()
