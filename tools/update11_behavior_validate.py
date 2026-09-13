#!/usr/bin/env python3
"""Effective candidate + accepted mod + installed data reference check."""
import argparse, json, sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
MAIN=ROOT if ROOT.name=='expanse-mod' else ROOT.parent.parent/'expanse-mod'
sys.path.insert(0,str(MAIN/'tools'))
from amun06_validate_package import AmunResolver, check_action_values

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--candidate',type=Path,default=ROOT/'build/update11-a/reviewed');a=ap.parse_args()
    base=MAIN/'build/experiments/expanse_donnager10_pdc_audio';game=MAIN.parent/'SteamLibrary/steamapps/common/Sins2'
    r=AmunResolver(base,game)
    for p in(a.candidate/'entities').glob('*'):r.index['entities/'+p.name]=(p,'update11-candidate')
    ids=['expanse10_donnager_launch_corvette','expanse06_amun_boarding','expanse10_donnager_marines','expanse11_morrigan_magazine']
    reports=check_action_values(base,game,r,{'abilities':[{'abilities':ids}]})
    for n in ['mcrn_corvette_hud_icon','mcrn_corvette_tooltip_picture']:r.resolve('brushes/'+n+'.brush','launch UI')
    unit=r.unit('expanse04_light_torpedo','Morrigan projectile')
    assert unit['target_filter_unit_type']=='torpedo' and 'torpedo' in unit
    assert unit['health']['levels'][0]=={'max_hull_points':50.,'max_armor_points':100.,'armor_strength':50.}
    pending=['Private expanse_mcrn_corvette.unit is main-owned and absent from this component output; unit must have supply55','Two actual Morrigan ability_positions must be applied by main','Morrigan unit skin must bind expanse04_light_torpedo_muzzle']
    out={'status':'PASS available typed action references against candidate+accepted+installed overlay; INCOMPLETE ship integration explicitly listed','runtime':'NOT RUN','ability_reports':reports,'references_resolved':len(r.edges),'pending_main_integration':pending,'edges':r.edges}
    p=ROOT/'audit/update11-a/reference-validation.json';p.write_text(json.dumps(out,indent=2)+'\n')
    print('PASS',len(r.edges),'available reference edges;3 explicit main integration requirements; runtime NOT RUN')
if __name__=='__main__':main()
