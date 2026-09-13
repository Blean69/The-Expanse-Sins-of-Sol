"""Generate disabled impactor laboratory inputs, never a supported package."""
import copy,json
from pathlib import Path
from build_polish import write
from validate_experiments import read,sha256
ROOT=Path(__file__).resolve().parents[1]
GAME=ROOT.parent/'SteamLibrary/steamapps/common/Sins2'

def main():
    out=ROOT/'build/laboratory/update15-impactor';audit=ROOT/'audit/update15'
    src=GAME/'entities/trader_battle_capital_ship_planet_bombing.weapon'
    torp=GAME/'entities/trader_medium_torpedo.unit'
    w=read(src);w['name']='LAB ONLY — single impactor'
    w['firing']={'firing_type':'spawn_torpedo','torpedo_firing_definition':{'spawned_unit':'expanse15_lab_impactor','duration':120.}}
    w['burst_pattern']=[0.];w['cooldown_duration']=3600.
    # All planetary damage stays exclusively in the actual weapon impact path.
    # The engine accepting that path for planets is NOT established by schema.
    write(out/'expanse15_lab_impactor.weapon',w)
    u=read(torp);u['physics']['max_linear_speed']=350.
    write(out/'expanse15_lab_impactor.unit',u)
    evidence={'status':'DISABLED laboratory candidate; acceptance NOT RUN; excluded from friends package',
      'sources':{str(p):sha256(p)for p in [src,torp]},
      'evidence':['Native planetary bombing uses non-destructible projectile firing; native anti-ship missiles use spawn_torpedo with selectable, damageable torpedo units.','Pinned weapon schema allows both firing types but does not prove the planet_bombing plus spawn_torpedo combination delivers planetary damage.','Candidate replaces only firing mechanism and cadence; retains native75 bombing damage/3 population damage. No delayed planet buff, detached damage action, death explosion, map modification or global launch.'],
      'test':['Use separate developer sandbox: one launcher, one enemy planet, one manually triggered discharge; stop launcher immediately to guarantee only one object.','Control: allow actual torpedo to reach planet; record exact hull and population changes and confirm one impact.','Interception: destroy actual torpedo well before contact; record planet hull and population unchanged beyond120-second lifetime plus margin.','Repeat near contact, after save/reload, and on two synchronized clients. No damage on interception is necessary but insufficient: control impact must damage planet.'],
      'promotion_gate':'All control/interception cases must be observed before any strategic weapon enters a shared package. A renderer-only projectile or timer reaching planet fails.',
      'adaptive_composite':'DEFERRED optional item: no shields/item/research unlock added. Inherited shield interactions and capture/save behavior require runtime testing first.'}
    write(audit/'impactor-investigation.json',evidence)
    print(json.dumps(evidence,indent=2))
if __name__=='__main__':main()
