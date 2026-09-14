"""Private command upgrade overlay; main merges player/component availability.

Preserves regular Europa assets, shared magazines, and boarding/repair programs.
"""
from pathlib import Path
from copy import deepcopy as cp
import hashlib,json
ROOT=Path(__file__).resolve().parents[1];MAIN=Path('/run/media/haker/NVME 2/expanse-mod');BASE=MAIN/'build/experiments/expanse_update25'
ID='expanse21_opa_command';ART='expanse26_opa_command';COLONY=ID+'_colony_module';MAG=ART+'_magazine'
CONTRACT=ROOT/'audit/update26-command/art-contract.json'
def rename(x,a,b):
    if isinstance(x,str):return x.replace(a,b)
    if isinstance(x,list):return [rename(v,a,b)for v in x]
    if isinstance(x,dict):return {k:rename(v,a,b)for k,v in x.items()}
    return x

def changes(base=BASE,art_contract=CONTRACT):
    base=Path(base);art=json.loads(Path(art_contract).read_text());s=art['scale'];edits={};origins={};sources={};loc={}
    def read(n):
        p=base/'entities'/n;sources[str(p)]=hashlib.sha256(p.read_bytes()).hexdigest();return json.loads(p.read_text())
    def put(n,d,old):edits['entities/'+n]=d;origins['entities/'+n]=str(base/'entities'/old)
    def scaled(v):return [x*s for x in v]
    old=read(ID+'.unit');unit=cp(old);regular=read('expanse19_europa_bane.unit');sci=read('expanse12_scirocco.unit')
    assert abs(s*old['spatial']['box']['extents'][2]-sci['spatial']['box']['extents'][2])<1e-6
    unit['spatial']['radius']*=s
    for k in ['center','extents']:unit['spatial']['box'][k]=scaled(unit['spatial']['box'][k])
    for i,h in enumerate(unit['health']['levels']):
        for k in ['max_hull_points','max_armor_points']:
            assert old['health']['levels'][0][k]==regular['health']['levels'][0][k]
            h[k]=old['health']['levels'][i][k]*2
    unit['build']['price']={k:v*1.5 for k,v in old['build']['price'].items()}
    for entry in unit['weapons']['weapons']:
        for k in ['weapon_position']:entry[k]=scaled(entry[k])
        if 'non_turret_muzzle_positions'in entry:entry['non_turret_muzzle_positions']=[scaled(p)for p in entry['non_turret_muzzle_positions']]
        source=entry['weapon']
        if source.startswith('expanse19_europa_pdc_'):
            new=source.replace('expanse19_europa',ART);d=read(source+'.weapon');turret=d['turret']
            turret['biaxial_base_mesh']=ART+'_pdc_base';turret['biaxial_barrel_mesh']=ART+'_pdc_barrel';turret['barrel_position']=scaled(turret['barrel_position']);turret['muzzle_positions']=[scaled(p)for p in turret['muzzle_positions']]
            put(new+'.weapon',d,source+'.weapon');entry['weapon']=new
    # AI matching key must reference the command's derived weapon identity.
    ai=unit.get('ai',{})
    if ai.get('attack_target_type_groups_matching_weapon','').startswith('expanse19_europa_pdc_'):
        ai['attack_target_type_groups_matching_weapon']=ai['attack_target_type_groups_matching_weapon'].replace('expanse19_europa',ART)
    for ext in ['ability','buff','action_data_source']:
        source='expanse19_europa_magazine';d=rename(read(source+'.'+ext),source,MAG)
        if ext=='ability':
            for p in d['ability_positions']:p['position']=scaled(p['position'])
            # Keep accepted labels: same magazine stats, private launch layout.
            d['gui']['name']=source+'.name';d['gui']['description']=source+'.description'
        put(MAG+'.'+ext,d,source+'.'+ext)
    strings=json.loads((base/'localized_text/en.localized_text').read_text())
    for key in ['name','description']:loc[MAG+'.'+key]=strings['expanse19_europa_magazine.'+key]
    for group in unit['abilities']:
        group['abilities']=[MAG if x=='expanse19_europa_magazine'else x for x in group['abilities']]
    assert COLONY not in sum([x['abilities']for x in unit['abilities']],[])
    unit['abilities'][0]['abilities'].append(COLONY)
    unit['item_builds']=[row for row in unit['item_builds']if COLONY not in row['build_group']]
    put(ID+'.unit',unit,ID+'.unit')
    skin=read(ID+'.unit_skin')
    for stage in skin['skin_stages']:
        stage['unit_mesh']['mesh']=ART+'_hull';stage['min_camera_distance']*=s
        for row in stage['child_mesh_alias_bindings']['map']:
            row['mesh_alias_name']=row['mesh_alias_name'].replace('expanse19_europa',ART)
            row['mesh_definition']['mesh']=row['mesh_definition']['mesh'].replace('expanse19_europa',ART)
        effects=stage['effects'];effects['exhaust_effects']=rename(effects['exhaust_effects'],'expanse19_europa_bane',ART)
        effects['hyperspace_effects']=rename(effects['hyperspace_effects'],'expanse19_europa_bane',ART)
    put(ID+'.unit_skin',skin,ID+'.unit_skin')
    # This is the already-shipped native colony program, directly available now.
    colony=read(COLONY+'.ability');assert colony['action_data_source']==COLONY
    loc[ID+'.description']='An enlarged OPA command cruiser with twice the base hull and armor of Europa\u2019s Bane. Direct colonization, engineering support and guarded boarding. Six existing defensive PDCs and an unchanged eight-torpedo magazine.'
    loc[COLONY+'.name']='Colonize'
    loc[COLONY+'.description']='Colonize a nearby eligible neutral planet. Native colony shuttle: range 5000, 120 antimatter, 120-second cooldown; grants one logistics and one commerce capacity. Available directly without fitting an item.'
    report={'status':'PRIVATE VALIDATED FRAGMENT; PLAYER ITEM REMOVAL REQUIRED','unit_id':ID,'base':str(base),'art_contract':str(art_contract),'art_directory':art['output_game'],'art_files':{k:str(Path(art['output_game'])/k)for k in art['files']},'source_definitions_sha256':sources,
     'player_recipes':{'all_players_exposing_command_colony_item':{'ship_components_remove':[COLONY],'note':'Remove from every player item availability list and any recommendation. Do not remove its ability or action data source: command references that native program directly. Preserve the old item definition for old-save resolution.'}},
     'stats':{'hull_level_1':unit['health']['levels'][0]['max_hull_points'],'armor_level_1':unit['health']['levels'][0]['max_armor_points'],'price':unit['build']['price'],'build_time':unit['build']['build_time'],'supply':unit['build']['supply_cost'],'scale':s,'length':s*old['spatial']['box']['extents'][2]*2},
     'preserved':['regular Europa unit/art','physics and movement','build time and fleet supply','six PDC damage/range/tracking/arcs and target filters','shared magazine source files and entire cadence/damage/fuel/targeting semantics','repair and capture abilities/actions/guards','native progression and regeneration','accepted color textures and full triangle detail'],
     'private_derivations':{'magazine':MAG,'pdcs':[ART+'_pdc_'+str(i)for i in range(6)]},
     'untested':['Game load, command-bar placement and native colonization execution','Legacy saves with an already-fitted colony item may retain an extra ability acquisition path; fresh ships use direct ability only','Engine turret attachment, exhaust visibility, collision, save/reload and multiplayer']}
    return edits,loc,origins,report

def main():
    edits,loc,origins,report=changes();out=ROOT/'build/update26-command/overlay';out.mkdir(parents=True,exist_ok=True)
    for rel,d in edits.items():p=out/rel;p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(d,indent=2)+'\n')
    for name,data in [('localization',loc),('origins',origins),('gameplay-contract',report)]:
        p=ROOT/'audit/update26-command'/(name+'.json');p.write_text(json.dumps(data,indent=2)+'\n')
    print(json.dumps(report['stats']))
if __name__=='__main__':main()
