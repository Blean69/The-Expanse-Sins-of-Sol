"""Small independent Donnager integration checks; shared package is read-only."""
from pathlib import Path
import argparse,copy,hashlib,json,sys
MAIN=Path('/run/media/haker/NVME 2/expanse-mod');ROOT=Path(__file__).resolve().parents[1]
SUPPORT=MAIN.parent/'expanse-workers/validation'
sys.path.insert(0,str(MAIN/'tools'))
from validate_experiments import read,require,file_hashes,verify_zip,sha256
from amun06_validate_package import AmunResolver,check_action_values
from build_combat03 import check_actions
from build_update08 import check_single_set
ID='expanse_donnager_battleship';PLAYERS=['trader_loyalist','trader_rebel','dlc_trader_loyalist']

def check(mod,game):
 base=MAIN/'build/experiments/expanse_amun09_cloak';a=MAIN.parent/'expanse-workers/weapon-behavior/build/donnager10-a/final-fit'
 for p in [mod,base,game,a]:require(p.is_dir(),'Missing required dependency; remaining checks NOT RUN: '+str(p))
 old,new=file_hashes(base),file_hashes(mod)
 allowed={'.mod_meta_data','ASSET-SOURCES.md','localized_text/en.localized_text','uniforms/unit_tag.uniforms'}|{'entities/'+n+'.player'for n in PLAYERS}|{'entities/'+n+'.entity_manifest'for n in ['unit','unit_skin','weapon','ability','buff','action_data_source']}
 require(not set(old)-set(new),'Deleted accepted base file')
 for n,h in old.items():
  if n not in allowed:require(new[n]==h,'Changed accepted base file: '+n)
 for n in ['expanse_rocinante_hero','expanse_amun_ra']:
  unit=read(mod/'entities'/(n+'.unit'));check_single_set(unit,read(base/'entities'/(n+'.unit'))['abilities'][0]['abilities'])
 u=read(mod/'entities'/(ID+'.unit'));skin=read(mod/'entities'/(ID+'.unit_skin'));recipe=read(a/'integration-recipe.json')
 require(len(recipe['unit_ability_sets'])==1 and set(recipe['unit_ability_sets'][0])=={'abilities'},'Worker recipe split/conditional ability set')
 check_single_set(u,recipe['unit_ability_sets'][0]['abilities'])
 require('titan' in u['tags'] and ID in u['tags'] and u['build']['build_kind']=='titan','Donnager does not share titan build route/tag')
 for name in PLAYERS:
  before=read(base/'entities'/(name+'.player'));expected=copy.deepcopy(before);expected['buildable_units'].append(ID)
  after=read(mod/'entities'/(name+'.player'));require(after==expected,'Player changes exceed buildable addition: '+name)
  require([x for x in after['unit_limits']['global'] if x['tag']=='titan']==[{'tag':'titan','unit_limit':1}],'Shared titan limit changed')
 stock=read(game/'entities/trader_loyalist_titan.unit')
 for key in ['items','health','physics','levels','antimatter','corruption']:require(u[key]==stock[key],'Inherited titan field changed: '+key)
 require(u['items']=={'levels':[{'max_ship_component_count':8}]},'Eight titan component slots missing')
 require(not any(k in u for k in ['child_meshes','carrier','unit_factory','exotic_factory','item_access_tags']),'Proprietary titan chain retained')
 for ident in ['trader_unlock_loyalist_titan','trader_unlock_rebel_titan']:require([ident] in u['build']['prerequisites'],'Missing research route: '+ident)
 inv=[]
 for entry in u['item_builds']:
  for ident in entry['build_group']:
   p=game/'entities'/(ident+'.unit_item');require(p.is_file(),'Missing component: '+ident);d=read(p)
   require('titan' in d['required_unit_tags'],'Item incompatible with titan: '+ident)
   require(not d.get('required_item_access_tags'),'Proprietary item access retained: '+ident)
   require(not ident.startswith('trader_loyalist_titan_'),'Proprietary Ankylon item in roster')
   inv.append({'id':ident,'type':d['item_type'],'sha256':sha256(p),'ability':d.get('ability')})
 previous=read(base/'localized_text/en.localized_text');current=read(mod/'localized_text/en.localized_text')
 require(all(current.get(k)==v for k,v in previous.items()),'Accepted localization entry changed')
 tags=read(base/'uniforms/unit_tag.uniforms');expected=copy.deepcopy(tags);expected['unit_tags'].append({'name':ID,'localized_name':ID+'_name'})
 require(read(mod/'uniforms/unit_tag.uniforms')==expected,'Tag changes exceed one additive record')
 voice=read(SUPPORT/'build/donnager10-c/voice/dialogue.json');require(skin['skin_stages'][0]['sounds']['dialogue']==voice,'Donnager voice mapping changed')
 for n,h in read(SUPPORT/'audit/donnager10-c/voice-generated-hashes.json').items():require(new.get(n)==h,'Packaged audio differs from measured derivative: '+n)
 ui=read(SUPPORT/'audit/donnager10-c/ui-validation.json')
 for r in ui['png_checks']:
  p=Path(r['file']);relative=p.relative_to(SUPPORT/'build/donnager10-c/ui/generated').as_posix();require(new.get(relative)==r['sha256'],'UI PNG drift: '+relative)
 for dep,h in ui['source_dependencies'].items():require(sha256(dep)==h,'UI source dependency changed: '+dep)
 resolver=AmunResolver(mod,game);resolved=resolver.unit(ID,'independent Donnager root');actions=check_actions(mod,resolver,ID);typed=check_action_values(mod,game,resolver,resolved)
 for item in inv:
  if item['ability']:
   ap=resolver.resolve('entities/'+item['ability']+'.ability','Donnager item '+item['id']);ad=read(ap)
   resolver.resolve('entities/'+ad['action_data_source']+'.action_data_source',ap)
 return {'status':'PASS INDEPENDENT OFFLINE INTEGRATION','runtime':'NOT RUN','accepted09_preserved':True,'shared_titan_limit':1,'single_coexisting_ability_set':u['abilities'],'component_slots':8,'compatible_items':inv,'audio_files_verified':40,'ui_pngs_verified':20,'actions':actions,'typed_actions':typed,'reference_edges':resolver.edges,'zip':verify_zip(mod.with_suffix('.zip'),mod)}
if __name__=='__main__':
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('--mod',type=Path,default=MAIN/'build/experiments/expanse_donnager10');p.add_argument('--game',type=Path,default=MAIN.parent/'SteamLibrary/steamapps/common/Sins2');args=p.parse_args();report=check(args.mod,args.game);out=ROOT/'audit/donnager10-c/package-independent-validation.json';out.write_text(json.dumps(report,indent=2)+'\n');print(json.dumps({k:report[k]for k in ['status','shared_titan_limit','component_slots','audio_files_verified','ui_pngs_verified','zip','runtime']},indent=2))
