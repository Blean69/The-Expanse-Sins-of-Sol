"""Replace the timed experiment with a separately packaged passive magazine.
No installed packages are touched; the first experiment remains reproducible.
"""
from pathlib import Path
import argparse,copy,json,shutil,zipfile
from build_polish import write,cp
from build_combat03 import ROOT,frozen,check_package
from validate_experiments import read,require,sha256,verify_zip,provenance
ID='expanse_corvette_ammo03'

def main(a):
    frozen(a.game,a.sdk);base=ROOT/'build/experiments/expanse_corvette_combat03';out=ROOT/'build/experiments'/ID
    require(not out.exists() and not out.with_suffix('.zip').exists(),'Refusing existing magazine output')
    source=read(a.persistent/'integration-recipe.json');require(source['normal_ammo_capacity']==8 and source['rounds_per_successful_pair']==2 and source['pair_interval']==10 and source['reload_after_last_pair']==120,'Wrong requested magazine contract')
    for p in (a.persistent/'entities').iterdir():require(p.name in {'expanse03_torpedo_magazine.ability','expanse03_torpedo_magazine.buff','expanse03_torpedo_magazine.action_data_source','expanse03_heavy_torpedo.unit'},'Unexpected persistent candidate input')
    shutil.copytree(base,out);positions=read(out/'entities/expanse03_torpedo_cycle.ability')['ability_positions']
    for p in list((out/'entities').iterdir()):
        if p.stem.startswith('expanse03_torpedo_cycle'):p.unlink()
    for p in (a.persistent/'entities').iterdir():cp(p,out/'entities'/p.name)
    ability=read(out/'entities/expanse03_torpedo_magazine.ability');ability['ability_positions']=positions;write(out/'entities/expanse03_torpedo_magazine.ability',ability)
    unit=read(out/'entities/trader_light_frigate.unit');unit['abilities']=[{'abilities':['expanse03_torpedo_magazine']}];write(out/'entities/trader_light_frigate.unit',unit)
    for ext in ['ability','buff','action_data_source']:write(out/'entities'/f'{ext}.entity_manifest',{'ids':['expanse03_torpedo_magazine']})
    loc=read(out/'localized_text/en.localized_text');loc={k:v for k,v in loc.items() if not k.startswith('expanse03_torpedo_cycle.')};loc.update(source['localization_additions']);write(out/'localized_text/en.localized_text',loc)
    metadata=read(out/'.mod_meta_data');metadata.update(display_name='The Expanse — Corvette 0.3 AMMO EXPERIMENT',short_description='Eight-round passive torpedo magazine; no active launch channel.',long_description='Pairs every ten seconds; 120-second reload after eight rounds. Autonomous nearest detected same-well enemy targeting. Remaining rounds stored in buff memory; engine/save behavior needs testing. Load alone.')
    write(out/'.mod_meta_data',metadata)
    checks=check_package(out,ROOT/'build/experiments/expanse_corvette_polish',a.game,a.sdk,mode='persistent')
    # Exact asset/PDC/effect preservation across alternative torpedo implementations.
    for directory in ['meshes','mesh_materials','effects','textures','brushes']:
        for p in (base/directory).iterdir():require(sha256(p)==sha256(out/directory/p.name),'Unrelated alternative-experiment asset change')
    write(ROOT/'audit/combat03/magazine-package-validation.json',checks)
    with zipfile.ZipFile(out.with_suffix('.zip'),'w',zipfile.ZIP_DEFLATED) as z:
        for p in sorted(out.rglob('*')):
            if p.is_file():
                i=zipfile.ZipInfo(p.relative_to(out).as_posix(),(2026,9,12,0,0,0));i.compress_type=zipfile.ZIP_DEFLATED;i.external_attr=0o100644<<16;z.writestr(i,p.read_bytes())
    deps=[a.persistent,base];write(out.with_suffix('.dependencies.json'),[str(p.resolve()) for p in deps]);write(out.with_suffix('.provenance.json'),provenance(out.with_suffix('.zip'),ROOT,deps))
    summary={'mod_id':ID,**verify_zip(out.with_suffix('.zip'),out),'installed':False,'runtime':'NOT RUN'};write(ROOT/'audit/combat03/magazine-package-summary.json',summary);frozen(a.game,a.sdk);print(json.dumps(summary,indent=2))
if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__)
    for k in ['game','sdk','persistent']:p.add_argument('--'+k,type=Path,required=True)
    main(p.parse_args())
