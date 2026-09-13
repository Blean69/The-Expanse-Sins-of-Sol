#!/usr/bin/env python3
"""Exact, reviewed combat-only patches and validator for combined 0.4 integration."""
import argparse, copy, hashlib, json
from pathlib import Path
import jsonschema

ROOT=Path(__file__).resolve().parents[1]
FILES=['expanse03_torpedo_magazine.buff','expanse03_hero_torpedo_salvo_on_self.buff','expanse03_torpedo_magazine.action_data_source','expanse03_hero_torpedo_salvo.action_data_source']
def read(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def write(p,d):p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(d,indent=2)+'\n')
def walk(d,path=''):
    if isinstance(d,dict):
        for k,v in d.items():
            yield d,k,v,path+'/'+k
            yield from walk(v,path+'/'+k)
    elif isinstance(d,list):
        for i,v in enumerate(d):yield from walk(v,path+'/'+str(i))
def transformed(d):
    d=copy.deepcopy(d);patches=[]
    for parent,k,v,path in walk(d):
        if k=='torpedo_to_create' and v=='expanse03_heavy_torpedo':
            patches += [{'op':'test','path':path,'value':v},{'op':'replace','path':path,'value':'expanse04_light_torpedo'}];parent[k]='expanse04_light_torpedo'
        if k=='effect' and v=='trader_torpedo_cruiser_torpedo_weapon_muzzle':
            patches += [{'op':'test','path':path,'value':v},{'op':'replace','path':path,'value':'expanse04_light_torpedo_muzzle'}];parent[k]='expanse04_light_torpedo_muzzle'
        if k=='action_value_id' and v=='heavy_torpedo_torpedo_speed_value':
            p=path.rsplit('/',1)[0]+'/action_value/values'
            assert parent['action_value']['values']==[1000.0]
            patches += [{'op':'test','path':p,'value':[1000.0]},{'op':'replace','path':p,'value':[1250.0]}];parent['action_value']['values']=[1250.0]
    return d,patches

def validate_package(package,base,sdk,candidate):
    """Raises on combat drift; caller still runs full mesh/reference/package checks."""
    package,base,sdk,candidate=map(Path,[package,base,sdk,candidate])
    checks=[]
    for name in FILES:
        expected,_=transformed(read(base/'entities'/name));actual=read(package/'entities'/name)
        assert actual==expected, 'Unexpected state/damage/ammo change in '+name
        schema='buff' if name.endswith('.buff') else 'action-data-source'
        jsonschema.Draft7Validator(read(sdk/'json_schemas'/(schema+'-schema.json'))).validate(actual)
        checks.append(name+': exact approved combat delta and schema')
    for name in ['expanse04_light_torpedo.unit','expanse04_light_torpedo.unit_skin']:
        assert read(package/'entities'/name)==read(candidate/'entities'/name),name
        schema='unit-skin' if name.endswith('unit_skin') else 'unit'
        jsonschema.Draft7Validator(read(sdk/'json_schemas'/(schema+'-schema.json'))).validate(read(package/'entities'/name))
        checks.append(name+': exact reviewed candidate and schema')
    assert (package/'entities/expanse03_hero_railgun.weapon').read_bytes()==(base/'entities/expanse03_hero_railgun.weapon').read_bytes(),'Railgun changed'
    if (package/'entities/expanse03_heavy_torpedo.unit').exists():
        assert (package/'entities/expanse03_heavy_torpedo.unit').read_bytes()==(base/'entities/expanse03_heavy_torpedo.unit').read_bytes(),'Preserved large torpedo changed'
    alias=read(candidate/'integration-recipe.json')['skin_muzzle_alias']
    for name in ['trader_light_frigate.unit_skin','expanse_rocinante_hero.unit_skin']:
        p=package/'entities'/name
        assert p.exists(),'Missing required launching ship skin '+name
        bindings=read(p)['skin_stages'][0]['effects']['effect_alias_bindings']
        assert alias in bindings,'Missing launch effect alias in '+name
    manifest=read(package/'entities/unit.entity_manifest')['ids'];assert 'expanse04_light_torpedo' in manifest
    assert 'expanse04_light_torpedo' in read(package/'entities/unit_skin.entity_manifest')['ids']
    for name in FILES:
        for _,k,v,_ in walk(read(package/'entities'/name)):
            assert not (k=='torpedo_to_create' and v=='expanse03_heavy_torpedo'),'Large torpedo remains active'
    return {'status':'PASS: combat-only structural invariants and six schemas','runtime':'NOT RUN','checks':checks,'railgun_byte_preserved':True,'limitations':'Does not validate complete package references, meshes, localization merge or runtime behavior. Main complete-package checker required.'}

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--base',type=Path,required=True);ap.add_argument('--sdk',type=Path,required=True)
    ap.add_argument('--candidate',type=Path,default=ROOT/'build/combat04-a/light');ap.add_argument('--output',type=Path,default=ROOT/'build/combat04-a/integration')
    ap.add_argument('--validate-package',type=Path);ap.add_argument('--report',type=Path)
    a=ap.parse_args()
    if a.validate_package:
        result=validate_package(a.validate_package,a.base,a.sdk,a.candidate)
        if a.report:
            assert a.report.resolve().is_relative_to(ROOT/'audit/combat04-a');write(a.report,result)
        print(json.dumps(result));return
    assert a.output.resolve().is_relative_to(ROOT/'build/combat04-a') and not a.output.exists()
    patches={};hashes={}
    for name in FILES:
        source=a.base/'entities'/name;data,patch=transformed(read(source));hashes[name]=sha(source);patches[name]=patch
        schema='buff' if name.endswith('.buff') else 'action-data-source'
        jsonschema.Draft7Validator(read(a.sdk/'json_schemas'/(schema+'-schema.json'))).validate(data)
        write(a.output/'entities'/name,data)
    write(a.output/'exact-patches.json',{'base':str(a.base),'source_sha256':hashes,'rfc6902_patches':patches,'localization':read(a.candidate/'integration-recipe.json')['localization'],'scope':'Only buffs and ADS listed; ordinary and hero launch skins plus manifests/localization remain main integrator ownership'})
    print('PASS: four candidate schemas, exact projectile/muzzle/speed-only patches; output '+str(a.output))

if __name__=='__main__':main()
