"""Schema and mechanical contracts for the isolated Storm fragments."""
from pathlib import Path
import sys,copy,json,hashlib
MAIN=Path('/run/media/haker/NVME 2/expanse-mod');sys.path.insert(0,str(MAIN/'tools'))
from common import read,write
from update18_tycho import schema_check
sys.path.insert(0,str(Path(__file__).resolve().parent))
from update24_storm_gameplay import changes,ID,BASE
ROOT=Path(__file__).resolve().parents[1];edits,loc,origins,report=changes();schema=[]
for rel,data in edits.items():
 p=ROOT/'build/update24-storm/fragments'/rel;write(p,data);schema.append(schema_check(p,p.suffix[1:].replace('_','-')+'-schema.json',Path(origins[rel])))
u=edits[f'entities/{ID}.unit'];assert u['target_filter_unit_type']=='capital_ship'and u['build']['build_kind']=='cruiser'and u['build']['supply_cost']==300
assert u['tags']==['capital_ship',ID];assert u['abilities']==[{'abilities':[ID+'_light_magazine','expanse12_raptor_reactor','expanse11_no_shields']}];assert len(u['health']['levels'])==10 and len(u['weapons']['weapons'])==7
for level in u['health']['levels']:assert level['max_shield_points']==0 and level['shield_point_restore_rate']==0
assert u['health']['levels'][0]['max_hull_points']==6000 and u['health']['levels'][0]['max_armor_points']==3000
for i in range(6):
 w=edits[f'entities/{ID}_pdc_{i}.weapon'];old=read(BASE/'entities/expanse12_raptor_pdc_0.weapon');assert w['damage']/w['cooldown_duration']==117.6
 for k in old:
  if k not in ['name','turret']:assert w[k]==old[k],k
rail=edits[f'entities/{ID}_keel_rail.weapon'];old=read(BASE/'entities/expanse10_donnager_rail_0.weapon')
for k in old:
 if k not in ['name','turret','pitch_speed','yaw_speed']:assert rail[k]==old[k]
assert 'turret'not in rail and rail['yaw_speed']==rail['pitch_speed']==0
source=read(BASE/'entities/expanse12_raptor_light_magazine.action_data_source');assert edits[f'entities/{ID}_light_magazine.action_data_source']==source
source=read(BASE/'entities/expanse12_raptor_light_magazine.buff');assert edits[f'entities/{ID}_light_magazine.buff']==json.loads(json.dumps(source).replace('expanse12_raptor_light_magazine',ID+'_light_magazine'))
assert report['player_recipes']['expanse18_mcrn']['unit_limits_global_append']==[{'tag':ID,'unit_limit':1}]
meta=read(ROOT/'audit/update24-storm/integration-spec.json');points={p['name'] for p in meta['meshpoints']};assert all(w['mesh_point']in points for w in u['weapons']['weapons']);assert sum(x['blocked']for x in meta['arc_checks'])==0
for rel,data in edits.items():assert not(BASE/rel).exists(),rel
result={'status':'PASS OFFLINE','schema':schema,'new_definitions':len(edits),'checks':['new-only definitions','native capital progression + ordinary cruiser production costs','300 supply and private one-per-player tag recipe','six unchanged117.6 PDC profiles','fixed rail donor damage5000/cooldown30/penetration1500 retained','exact source magazine values and state machine','no shield, capture, hero, free spawn or bombardment','physical point binding and zero sampled PDC ray obstruction'],'runtime':'NOT RUN','limitations':report['runtime_checks_not_run']};write(ROOT/'audit/update24-storm/gameplay-validation.json',result);print('PASS13 schemas and mechanical contracts')
