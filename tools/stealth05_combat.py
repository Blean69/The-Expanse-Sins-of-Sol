#!/usr/bin/env python3
"""Private unbound Amun combat candidates, preserving every source 0.4 byte."""
import argparse,copy,hashlib,json
from pathlib import Path
import jsonschema

ROOT=Path(__file__).resolve().parents[1]
def read(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def write(p,d):p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(d,indent=2)+'\n')
def main():
    ap=argparse.ArgumentParser();ap.add_argument('--base',type=Path,required=True);ap.add_argument('--sdk',type=Path,required=True);ap.add_argument('--output',type=Path,default=ROOT/'build/stealth05-a/combat');a=ap.parse_args()
    assert a.output.resolve().is_relative_to(ROOT/'build/stealth05-a') and not a.output.exists(),'Fresh output required'
    source_hashes={str(p.relative_to(a.base)):sha(p) for p in a.base.rglob('*') if p.is_file()}
    for need in ['expanse04_light_torpedo.unit','expanse04_light_torpedo.unit_skin','expanse03_hero_railgun.weapon','expanse_polish_pdc_0.weapon','expanse03_torpedo_magazine.ability','expanse03_torpedo_magazine.buff','expanse03_torpedo_magazine.action_data_source']:
        if not (a.base/'entities'/need).is_file():raise SystemExit('BLOCKED missing reviewed0.4 dependency '+need)
    staged={};torp='expanse05_amun_torpedo';mag='expanse05_amun_magazine';tag='expanse05_cloak_revealing_gun'
    old=read(a.base/'entities/expanse04_light_torpedo.unit');d=copy.deepcopy(old);d['physics']['max_linear_speed']=1500.;d['health']['levels'][0].update(max_hull_points=25.,max_armor_points=50.,armor_strength=50.);d['skin_groups']=[{'skins':[torp]}];staged[torp+'.unit']=d
    assert old['health']['levels'][0]['max_hull_points']==50 and old['health']['levels'][0]['max_armor_points']==100 and old['health']['levels'][0]['armor_strength']==50
    skin=read(a.base/'entities/expanse04_light_torpedo.unit_skin');skin['skin_stages'][0]['gui'].update(name=torp+'.name',description=torp+'.description');staged[torp+'.unit_skin']=skin
    rail=read(a.base/'entities/expanse03_hero_railgun.weapon');rail['damage']=3750.;rail['name']='expanse05.amun.rail.name';rail['tags'].append(tag);assert rail['penetration']==1000 and rail['cooldown_duration']==10;staged['expanse05_amun_railgun.weapon']=rail
    for i in range(3):
        w=read(a.base/'entities/expanse_polish_pdc_0.weapon');w.pop('turret');w['tags'].append(tag);w['name']='expanse05.amun.pdc.name';assert (w['damage'],w['cooldown_duration'],w['penetration'])==(28,.25,0);staged[f'expanse05_amun_pdc_{i}.weapon']=w
    for ext in ['ability','buff','action_data_source']:
        d=read(a.base/'entities'/('expanse03_torpedo_magazine.'+ext))
        if ext=='ability':
            d['action_data_source']=mag;d['passive_actions']['persistant_buff']=mag;d.pop('ability_positions',None);d['gui']['name']=mag+'.name';d['gui']['description']=mag+'.description'
        elif ext=='buff':
            def replace(x):
                if isinstance(x,dict):
                    for k,v in x.items():
                        if k=='torpedo_to_create':assert v=='expanse04_light_torpedo';x[k]=torp
                        else:replace(v)
                elif isinstance(x,list):
                    for v in x:replace(v)
            replace(d)
            if 'gui' in d:d['gui']['name']=mag+'.name'
        else:
            values={'heavy_torpedo_damage_value':900.,'heavy_torpedo_torpedo_speed_value':1500.,'heavy_torpedo_torpedo_hull_value':25.,'heavy_torpedo_torpedo_armor_value':50.}
            for v in d['action_values']:
                if v['action_value_id'] in values:v['action_value']['values']=[values[v['action_value_id']]]
            values={v['action_value_id']:v['action_value']['values'] for v in d['action_values']}
            for k,n in [('heavy_torpedo_armor_penetration_value',1000),('magazine_capacity_value',8),('magazine_pair_count_value',2),('magazine_pair_interval_value',10),('magazine_reload_duration_value',120)]:assert values[k]==[n]
        staged[mag+'.'+ext]=d
    names={'.ability':'ability','.buff':'buff','.action_data_source':'action-data-source','.unit':'unit','.unit_skin':'unit-skin','.weapon':'weapon'}
    for name,d in staged.items():jsonschema.Draft7Validator(read(a.sdk/'json_schemas'/(names[Path(name).suffix]+'-schema.json'))).validate(d)
    assert source_hashes=={str(p.relative_to(a.base)):sha(p) for p in a.base.rglob('*') if p.is_file()},'0.4 source changed'
    for name,d in staged.items():write(a.output/'entities'/name,d)
    write(a.output/'localization.json',{torp+'.name':'Amun-Ra attack torpedo',torp+'.description':'Fast, fragile guided torpedo. Damage900; penetration1,000; speed1,500; hull25; armor50; armor strength50.',mag+'.name':'Amun-Ra torpedo magazine',mag+'.description':'Eight torpedoes. Launches two every10seconds while an eligible target is available; reloads120seconds after the last pair. Mounts and cloaking integration remain experimental.','expanse05.amun.rail.name':'Amun-Ra heavy railgun','expanse05.amun.pdc.name':'Amun-Ra PDC autocannon'})
    write(a.output/'integration-recipe.json',{'status':'INCOMPLETE UNBOUND COMBAT CANDIDATES — do not package or install','files':list(staged),'torpedo':{'id':torp,'damage':900,'speed':1500,'penetration':1000,'hull':25,'armor':50,'armor_strength':50,'size':'same installed Javelis reference as0.4','lifetime':240,'range':200000,'same_well':True,'magazine':8,'per_pair':2,'pair_seconds':10,'reload_seconds':120},'rail':{'id':'expanse05_amun_railgun','damage':3750,'penetration':1000,'cooldown':10,'raw_dps':375},'PDC':{'ids':[f'expanse05_amun_pdc_{i}'for i in range(3)],'damage':28,'cooldown':.25,'penetration':0,'range':2500,'raw_dps_per_mount':112,'raw_dps_all_three_bearing':336,'source_target_filter_and_groups_preserved':True,'turret':'intentionally omitted until actual three assemblies are identified; no copied Tachi transforms'},'cloak_probe':{'ability':'expanse05_launch_probe','required_projectile_filter_replace':{'from':'trader_torpedo_cruiser_torpedo','to':torp},'private_gun_tag_already_on_three_PDC_and_rail':tag,'torpedo_has_no_reveal_gun_tag':True},'required_integration':['Model-owned three PDC mounts/rig metadata, rail hardpoint and torpedo launch ability_positions','Amun unit/skin, manifests, localized keys, player build entry/private tag limit6','Bind existing light muzzle and hero rail/PDC effect aliases in Amun skin; final reference resolution','Cloak schema/quality mapping plus runtime gate; probe alone does not cloak','Boarding modeled effect is not an interceptable arrival-tracked pod'], 'preservation':'All0.4 source files hashed before and after; MCRN projectile and hero rail definitions unchanged'})
    write(a.output/'offline-validation.json',{'status':'PASS nine candidate schemas; integration incomplete','runtime':'NOT RUN','schema_count':len(staged),'source_files_unchanged':len(source_hashes),'source_sha256':source_hashes,'candidate_sha256':{p.name:sha(p)for p in sorted((a.output/'entities').iterdir())}})
    print(f'PASS {len(staged)} schemas; {len(source_hashes)} reviewed0.4 source files unchanged. '+str(a.output))
if __name__=='__main__':main()
