"""Prepare hero unit/acquisition candidates; mesh/mount bindings supplied separately.
Output is an incomplete integration candidate, never installed or zipped here.
"""
from pathlib import Path
import argparse,copy,json
import jsonschema
from build_polish import write
from validate_experiments import read,require,sha256

def generate(game,sdk,base,out):
    hero='expanse_rocinante_hero';unit=read(base/'entities/trader_light_frigate.unit')
    unit['skin_groups']=[{'skins':[hero]}]
    unit['tags'].append(hero)
    unit['health']['levels'][0]['max_hull_points']=3000.0
    unit['health']['levels'][0]['max_armor_points']=1650.0
    unit['antimatter']={'max_antimatter':350.0,'antimatter_restore_rate':1.0}
    unit['build'].update(build_time=90.0,price={'credits':3000.0,'metal':500.0,'crystal':200.0},supply_cost=25)
    unit['abilities']=[{'abilities':['expanse03_torpedo_cycle','expanse_roci_belter_ingenuity','expanse03_hero_torpedo_salvo','expanse_roci_overcharged_reactor','expanse_roci_morale']}]
    # Candidate deliberately has no copied Tachi mounts; installable assembly must
    # supply the actual hero model's six PDCs, railgun and launch coordinates.
    unit.pop('weapons');unit['ai'].pop('attack_target_type_groups_matching_weapon')
    jsonschema.Draft7Validator(read(sdk/'json_schemas/unit-schema.json')).validate(unit)
    write(out/'entities'/f'{hero}.unit',unit)
    records=[]
    for ident in ['trader_loyalist','trader_rebel','dlc_trader_loyalist']:
        source=read(game/'entities'/f'{ident}.player');player=copy.deepcopy(source)
        require(hero not in player['buildable_units'],'Hero already present')
        player['buildable_units'].append(hero);player['unit_limits']['global'].append({'tag':hero,'unit_limit':1})
        restored=copy.deepcopy(player);restored['buildable_units'].pop();restored['unit_limits']['global'].pop();require(restored==source,'Unrelated faction change')
        jsonschema.Draft7Validator(read(sdk/'json_schemas/player-schema.json')).validate(player)
        write(out/'entities'/f'{ident}.player',player)
        records.append({'source':str(game/'entities'/f'{ident}.player'),'sha256':sha256(game/'entities'/f'{ident}.player'),'changes':['appendbuildablehero','appendprivateglobaltaglimit1']})
    tags=read(game/'uniforms/unit_tag.uniforms');tags['overwrite_unit_tags']=True;tags['unit_tags'].append({'name':hero,'localized_name':hero+'_name'})
    jsonschema.Draft7Validator(read(sdk/'json_schemas/unit-tag-uniforms-schema.json')).validate(tags)
    write(out/'uniforms/unit_tag.uniforms',tags)
    write(out/'localized_text/en.localized_text',{hero+'_name':'Rocinante',hero+'_description':'Independent gunship with six PDCs, heavy torpedoes, a keel railgun and crew abilities. One per empire.'})
    write(out/'candidate-status.json',{'status':'INCOMPLETE HERO INTEGRATION — DO NOT INSTALL','missing':['hero unit_skin and compiled model/material dependencies','actual hero PDC and railgun mount integration','actual hero torpedo ability positions (cannot share Tachi coordinates)','hero plume attachment and UI imagery','merged private entity manifests and ability dependencies'],'unit_schema':'PASS','player_schemas':3,'tag_schema':'PASS','player_changes':records,'configured_limit':'1 per empire using private tag; queue/capture/rebuild runtime NOT RUN','provisional_values':{'hull':3000,'armor':1650,'antimatter':350,'antimatter_regen':1,'build_seconds':90,'credits':3000,'metal':500,'crystal':200,'supply':25}})
    print('Hero unit, three minimal player overrides and private-tag schema checks PASS; integration incomplete')
if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--game',type=Path,required=True);p.add_argument('--sdk',type=Path,required=True);p.add_argument('--base',type=Path,default=Path('build/experiments/expanse_corvette_combat03'));p.add_argument('--out',type=Path,default=Path('build/hero03-main/unit-candidate'));a=p.parse_args();generate(a.game,a.sdk,a.base,a.out)
