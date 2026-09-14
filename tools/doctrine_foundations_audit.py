"""Emit proposed Stage 2 fragments and concrete evidence without touching shared builds."""
from pathlib import Path
import hashlib
import json
import jsonschema
from common import read_mesh
from doctrine_colony_fragments import (GAME, colony_module, local_bombardment_weapon,
                                        native_effect_aliases, bombardment_mount)

ROOT = Path(__file__).resolve().parents[1]
BASE = Path('/run/media/haker/NVME 2/expanse-mod/build/experiments/expanse_update19')
SDK = GAME.parent / 'Sins of a Solar Empire II - Mod Tools/json_schemas'
OUT = ROOT / 'build/foundations20-fragments'
AUDIT = ROOT / 'audit/foundations20'


def read(p): return json.loads(p.read_text())
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def write(p, d):
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(d, indent=2) + '\n')


def main():
    from doctrine_colony_fragments import changes
    edits, strings, origins, report = changes(BASE, opa_command_id='expanse21_opa_command', prefix='expanse21')
    checks=[]
    for name,data in edits.items():
        ext=Path(name).suffix
        schema=SDK/({'.ability':'ability','.action_data_source':'action-data-source',
                     '.unit_item':'unit-item','.weapon':'weapon'}[ext]+'-schema.json')
        check_data=json.loads(json.dumps(data)); extensions=[]
        if ext=='.weapon':
            original=Path(origins[name])
            assert data['bombing_damage']==read(original)['bombing_damage']==75.0
            check_data.pop('bombing_damage')
            extensions.append({'path':'/bombing_damage','value':75.0,'source':str(original),'sha256':sha(original)})
        errors=list(jsonschema.Draft202012Validator(read(schema)).iter_errors(check_data))
        assert not errors, [(list(e.path),e.message) for e in errors]
        write(OUT/'entities'/name,data)
        checks.append({'definition':name,'schema':schema.name,'sha256':sha(schema),'status':'PASS',
                       'unchanged_installed_extensions':extensions})
    filters={x['target_filter_id']:x['target_filter'] for x in read(GAME/'uniforms/target_filter.uniforms')['common_target_filters']}
    assert filters['common_planet_bombing']['ownerships']==['enemy']
    assert filters['uniforms_colonizable_planets']['ownerships']==['none']
    assert filters['uniforms_colonizable_planets']['constraints']==[{'constraint_type':'is_colonizable_planet'}]
    write(OUT/'merge-fragments.json',report)
    write(OUT/'localization-fragment.json',strings)
    write(OUT/'native-origins.json',origins)
    inventory=[]
    for name in ['trader_light_frigate','expanse_mcrn_corvette','expanse_rocinante_hero',
                 'expanse_donnager_battleship','expanse12_scirocco','expanse15_truman',
                 'expanse12_raptor','expanse12_pella','expanse19_europa_bane','expanse_amun_ra']:
        path=BASE/'entities'/(name+'.unit');unit=read(path)
        magazines=[a for g in unit['abilities'] for a in g['abilities'] if 'magazine' in a]
        inventory.append({'ship':name,'sha256':sha(path),'magazine_abilities':magazines,
                          'native_bombing_weapons':[w['weapon'] for w in unit.get('weapons',{}).get('weapons',[])
                           if 'planet_bombing' in w['weapon']], 'colonize_ability':unit.get('colonize_ability')})
    write(AUDIT/'current-colony-bombardment-inventory.json',inventory)
    inputs=['entities/trader_colony_capital_ship_colonize.ability',
      'entities/trader_colony_capital_ship_colonize.action_data_source',
      'entities/trader_colony_capital_ship_colonize.buff',
      'entities/trader_colony_capital_ship_planet_bombing.weapon',
      'entities/trader_colony_capital_ship.unit_skin','entities/trader_derelict_specialist.unit_item',
      'entities/trader_radiation_bomb.unit_item','entities/trader_combat_repair_system_unit_item.ability',
      'uniforms/target_filter.uniforms','gui/hud_ship_window.gui']
    write(AUDIT/'fragment-validation.json',{'status':'PASS OFFLINE ONLY','definition_checks':checks,
      'schema_check_count':len(checks),'native_sources':[{'path':str(GAME/x),'sha256':sha(GAME/x)} for x in inputs],
      'baseline':str(BASE),'verified_mounts':report['bombardment'],'runtime':'NOT RUN','shared_main_mutations':False})
    print(json.dumps({'status':'PASS offline','definitions':len(checks),'verified_launch_frames':len(report['bombardment']),
                      'colony_modules':len(report['colony']),'runtime':'NOT RUN'}))


if __name__ == '__main__': main()
