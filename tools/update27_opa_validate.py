"""Private OPA integration checks against frozen0.26 and the pinned SDK."""
from pathlib import Path
from copy import deepcopy as cp
import hashlib,json,sys
import numpy as np
ROOT=Path(__file__).resolve().parents[1];MAIN=Path('/run/media/haker/NVME 2/expanse-mod');sys.path.insert(0,str(MAIN/'tools'))
from common import read,write,read_mesh
from update11_validate import schema_check
from amun06_validate_package import AmunResolver,check_action_values
from build_combat03 import check_actions
sys.path.insert(0,str(ROOT/'tools'))
from update27_opa_gameplay import changes,BASE,DARK,BEHE,NEWBEHE,rename,AUD
GAME=MAIN.parent/'SteamLibrary/steamapps/common/Sins2'

def dictionaries(d):
 if isinstance(d,dict):
  yield d
  for x in d.values():yield from dictionaries(x)
 elif isinstance(d,list):
  for x in d:yield from dictionaries(x)

def main():
 edits,loc,origins,report=changes();view=ROOT/'build/update27-opa/validation-view';view.mkdir(exist_ok=True)
 for p in BASE.rglob('*'):
  if p.is_file():
   dest=view/p.relative_to(BASE);dest.parent.mkdir(parents=True,exist_ok=True)
   if not dest.exists():dest.symlink_to(p)
 for rel,d in edits.items():
  p=view/rel
  if p.is_symlink():p.unlink()
  write(p,d)
 for rel,source in report['art_files'].items():
  p=view/rel;p.parent.mkdir(parents=True,exist_ok=True)
  if not p.exists():p.symlink_to(source)
  else:assert p.read_bytes()==Path(source).read_bytes()
 text=read(BASE/'localized_text/en.localized_text');text.update(loc);p=view/'localized_text/en.localized_text'
 if p.is_symlink():p.unlink()
 write(p,text)
 tags=read(BASE/'uniforms/unit_tag.uniforms');tags['unit_tags']+=report['unit_tag_entries_append'];p=view/'uniforms/unit_tag.uniforms'
 if p.is_symlink():p.unlink()
 write(p,tags)
 # Main owns the real pricedresearch; a private schema-compatible prerequisite
 # stub here only supports graph checking until its real node is integrated.
 source=read(BASE/'entities/expanse24_behemoth_refit.research_subject');p=view/'entities/expanse27_dark_star_procurement.research_subject';write(p,source)
 schemas=[]
 for rel in edits:
  r=schema_check(view/rel,Path(origins[rel])if rel in origins else None)
  if r:schemas.append(r)
 resolver=AmunResolver(view,GAME);results=[]
 for ident in [DARK,BEHE]:
  u=resolver.unit(ident,'OPA27 private audit');results.append({'unit':ident,'actions':check_actions(view,resolver,ident),'values':check_action_values(view,GAME,resolver,u)})
 # Exact Amun projectile identity allows the shared cloak controller's spawned
 # torpedo has_definition condition to count these launches without a new system.
 dark=read(view/'entities'/(DARK+'.unit'));amun=read(BASE/'entities/expanse_amun_ra.unit');assert dark['physics']==amun['physics'];assert dark['target_filter_unit_type']=='capital_ship'and dark['build']['build_kind']=='capital_ship';assert dark['tags']==['capital_ship',DARK];assert dark['weapons']['weapons'][-1]['weapon']=='expanse06_amun_railgun'

 assert 'colonize_ability' not in dark
 assert dark['cloak_ability']==amun['cloak_ability'] and dark['ship_roles']==amun['ship_roles'] and dark['antimatter']==amun['antimatter']
 def strings(d):
  if isinstance(d,str):yield d
  elif isinstance(d,list):
   for x in d:yield from strings(x)
  elif isinstance(d,dict):
   for x in d.values():yield from strings(x)
 pending=[DARK+'_magazine','expanse06_amun_cloak','expanse06_amun_cloak_controller','expanse06_amun_boarding'];chain={}
 while pending:
  name=pending.pop()
  for ext in ['ability','buff','action_data_source']:
   f=view/'entities'/(name+'.'+ext)
   if not f.exists() or f.name in chain:continue
   d=read(f);v=set(strings(d));assert 'expanse_amun_ra'not in v and 'expanse06_amun_magazine'not in v,(f.name,'hardcoded origin')
   chain[f.name]={'sha256':hashlib.sha256(f.read_bytes()).hexdigest(),'unit_definition_filters':sorted({x['unit_definition'] for x in dictionaries(d) if 'unit_definition'in x})}
   pending.extend(x for x in v if any((view/'entities'/(x+'.'+k)).exists() for k in ['ability','buff','action_data_source']))
 controller=read(view/'entities/expanse06_amun_cloak_controller.buff');spawn_trigger=next(x for x in controller['trigger_event_actions']if x['trigger_event_type']=='on_current_spawner_spawned_torpedo');assert 'expanse06_amun_torpedo'in set(strings(spawn_trigger))
 magazine=read(view/'entities'/(DARK+'_magazine.buff'));assert {d['torpedo_to_create']for d in dictionaries(magazine)if 'torpedo_to_create'in d}=={'expanse06_amun_torpedo'}
 assert 'expanse06_cloak_revealing_gun'in read(BASE/'entities/expanse06_amun_railgun.weapon')['tags']
 write(AUD/'amun-chain-audit.json',{'status':'PASS STATIC IDENTITY/RESOLUTION; NOT RUNTIME','files':chain,'retained_projectile':'expanse06_amun_torpedo','retained_cloak_ability':dark['cloak_ability'],'removed_command_colonize':True,'semantics':'Original current_spawner controller counts launches, reveals on fourth torpedo for60seconds, resets launch_count, re-arms after reveal_until; shared native boarding target lock and OPA research wrapper unchanged. No exact Amun hull or original magazine ID occurs in reachable ability/buff/ADS chain.'})
 for l in dark['levels']['levels']:assert 'weapon_modifiers'not in l
 assert all(l.get('max_shield_points',0)==0 and 'shield_burst_restore'not in l for l in dark['health']['levels'])
 assert dark['abilities']==rename(amun['abilities'],'expanse06_amun_magazine',DARK+'_magazine')
 for new,old in [(DARK,'expanse06_amun'),(NEWBEHE,'expanse24_behemoth')]:
  for ext in ['ability','buff','action_data_source']:
   a=rename(read(view/'entities'/(new+'_magazine.'+ext)),new+'_magazine',old+'_magazine');b=read(BASE/'entities'/(old+'_magazine.'+ext))
   if ext=='ability':a['ability_positions']=b['ability_positions']
   assert a==b,(new,ext)
 for new,old in [(DARK+'_pdc','expanse06_amun_pdc_0'),(NEWBEHE+'_pdc','expanse24_behemoth_pdc')]:
  a=read(view/'entities'/(new+'.weapon'));b=read(BASE/'entities'/(old+'.weapon'));a.pop('turret');b.pop('turret');assert a==b;assert a['damage']/a['cooldown_duration']==85.
 behe=read(view/'entities'/(BEHE+'.unit'));old=read(BASE/'entities'/(BEHE+'.unit'))
 for k in ['health','build','physics','move','levels','items','ship_component_shop']:assert behe[k]==old[k],k
 restored=cp(behe);restored['spatial']=old['spatial'];restored['weapons']=old['weapons'];restored['ai']=old['ai'];restored['abilities']=old['abilities'];assert restored==old
 for name,unit in [(DARK,dark),(NEWBEHE,behe)]:
  art=read(AUD/(name+'-art.json'));assert art['checks']['sampled_muzzle_rays_clear']==len(art['rigs'])*17*9
  hull=read_mesh(view/'meshes'/(art['hull_mesh']+'.mesh'));pts={x['name']:x for x in hull['meshpoints']}
  for r,w in zip(art['rigs'],unit['weapons']['weapons']):assert w['mesh_point']in pts and np.allclose(w['weapon_position'],pts[w['mesh_point']]['position'],atol=.003)
  for j,e in enumerate(art['exhausts']):assert np.allclose(e['position'],pts[f'exhaust.{j}']['position'],atol=.003)
  for rel,h in art['art_files'].items():assert hashlib.sha256((view/rel).read_bytes()).hexdigest()==h
 for p,h in report['source_definitions_sha256'].items():assert hashlib.sha256(Path(p).read_bytes()).hexdigest()==h
 validation={'status':'PASS OFFLINE SCHEMAS/REFERENCES/VALUES/PRESERVATION; REAL RESEARCH PROVIDED BY MAIN','schemas':schemas,'abilities':results,'checks':{'shared_Amun_cloak_boarding_rail_identity':True,'original_magazines_byte_preserved_private_layout_only':True,'no_offense_level_bonus_added':True,'Earth85DPS_per_PDC':True,'Behemoth_health_support_economy_movement_unchanged':True,'attachment_and_exhaust_positions_verified':True,'all_art_hashes_match':True,'source_definitions_unchanged':True},'limits':['Private research stub validates prerequisite resolution only; actual tier3priced node and player access must be checked by main.','Muzzle rays are sampled in source geometry; in-engine turret tracking, engine trails and performance remain untested.'],'runtime':report['runtime']};write(AUD/'validation.json',validation);print(json.dumps({'status':validation['status'],'schemas':len(schemas)}))
if __name__=='__main__':main()
