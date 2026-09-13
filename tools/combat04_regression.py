"""Small negative checks for the new exact-delta validator; no installed writes."""
import argparse, copy, json, tempfile
from pathlib import Path
from types import SimpleNamespace
from build_combat04 import ROOT, ID, validate
from build_polish import write
from validate_experiments import read

def main():
    p=argparse.ArgumentParser(description=__doc__)
    for key in ['game','sdk','geometry','combat']:p.add_argument('--'+key,type=Path,required=True)
    a=p.parse_args();package=ROOT/'build/experiments'/ID
    meta=read(a.geometry/'audit/geometry04-b/mount-metadata.json');equipment=read(a.geometry/'audit/geometry04-b/equipment.json');meta['equipment']=equipment
    game_assets=a.geometry/'build/geometry04-b/game'
    cases=[
        ('localization drift','localized_text/en.localized_text',lambda d:d.update(trader_light_frigate_name='Unapproved'), 'Unapproved localization delta'),
        ('hero navigation drift','entities/expanse_rocinante_hero.unit',lambda d:d['physics'].update(max_linear_speed=1),'Unapproved hero stats/navigation/rail/ability change'),
        ('Martian projectile health drift','entities/expanse04_light_torpedo.unit',lambda d:d['health']['levels'][0].update(max_hull_points=1),'expanse04_light_torpedo.unit'),
        ('PDC second budget','entities/expanse_rocinante04_pdc_0.weapon',lambda d:d.update(damage=56),'Unexpected PDC budget/targeting change'),
    ]
    result=[]
    with tempfile.TemporaryDirectory(prefix='expanse04-regression-') as temp:
        out=Path(temp)/'probe'
        for file in package.rglob('*'):
            dest=out/file.relative_to(package)
            if file.is_dir():dest.mkdir(parents=True,exist_ok=True)
            else:dest.parent.mkdir(parents=True,exist_ok=True);dest.symlink_to(file)
        for name,relative,mutate,expected in cases:
            target=out/relative;data=read(target);target.unlink();mutate(data);write(target,data)
            try:
                validate(out,a,meta,equipment,game_assets)
            except (AssertionError,ValueError) as error:
                if expected not in str(error):raise
                result.append({'check':name,'status':'PASS rejected mutation','diagnostic':str(error)})
            else:raise ValueError('Missed regression: '+name)
            target.unlink();target.symlink_to(package/relative)
    write(ROOT/'audit/combat04/regression-checks.json',{'status':'PASS','checks':result,'scope':'Full-environment negative tests; no runtime simulation'})
    print(json.dumps(result,indent=2))

if __name__=='__main__':main()
