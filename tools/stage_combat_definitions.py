"""Generate schema-checked, uninstalled combat definition candidates.
No .mod_meta_data or Cobalt override is emitted: this is a subsequent change.
"""
from common import *
import copy,jsonschema

out=ROOT/'build/combat-candidates';out.mkdir(parents=True,exist_ok=True)
torp=read(GAME/'entities/trader_torpedo_cruiser_torpedo.weapon');projectile=read(GAME/'entities/trader_torpedo_cruiser_torpedo.unit');skin=read(GAME/'entities/trader_torpedo_cruiser_torpedo.unit_skin')
torp['firing']['torpedo_firing_definition']['spawned_unit']='mcrn_corvette_torpedo'
projectile['skin_groups'][0]['skins']=['mcrn_corvette_torpedo']
# Leave Ogrov kinetics, damage, range and lifetime untouched in the dependency
# isolation stage. Gravity-well range and salvos are separate experimental edits.
write(out/'entities/mcrn_corvette_torpedo.weapon',torp);write(out/'entities/mcrn_corvette_torpedo.unit',projectile);write(out/'entities/mcrn_corvette_torpedo.unit_skin',skin)
weapons=['mcrn_corvette_torpedo'];rigs=read(ROOT/'audit/pdc-rig-candidates.json')['rigs']
for rig in rigs:
    w=read(GAME/'entities/trader_antifighter_frigate_point_defense_autocannon.weapon');idx=rig['index'];name=f'mcrn_corvette_pdc_{idx}'
    # Eligibility experiment. Damage/rate stay vanilla to isolate target logic.
    w['attack_target_type_groups']=['torpedo_strikecraft','corvette','light','flak']
    w['acquire_target_logic']='best_target_in_range'
    w['turret'].update(biaxial_base_mesh=f'mcrn_pdc_{idx}_base',biaxial_barrel_mesh=f'mcrn_pdc_{idx}_barrel',barrel_position=[0.,0.,0.],muzzle_positions=[rig['muzzle_local']])
    write(out/'entities'/(name+'.weapon'),w);weapons.append(name)
for ext,ids in [('weapon',weapons),('unit',['mcrn_corvette_torpedo']),('unit_skin',['mcrn_corvette_torpedo'])]:write(out/'entities'/(ext+'.entity_manifest'),{'ids':ids})
results=[]
for path in (out/'entities').iterdir():
    schema={'.weapon':'weapon-schema.json','.unit':'unit-schema.json','.unit_skin':'unit-skin-schema.json'}.get(path.suffix)
    if schema:jsonschema.Draft7Validator(read(SDK/'json_schemas'/schema)).validate(read(path));results.append(path.name)
write(ROOT/'audit/combat-candidate-validation.json',{'schema_passed':results,'installed':False,'runtime_test':'NOT RUN','shared_vanilla_edits':0,'incomplete_dependencies':['PDC mesh aliases require combat skin bindings and compiled rig assets.','Candidate weapon effects still use vanilla alias names: copy Garda/Ogrov effect_alias_bindings into the future ship skin.','Combat hull must omit the moving gun geometry before rigs are attached.','Ship weapon entries, arcs, engagement distance, torpedo launch points and actual salvo mechanism are not yet authored.'],'intent':'Isolate dependencies and target eligibility before damage/range tuning; not a playable combat mod.'})
print('Validated',len(results),'isolated combat candidates; not packaged or installed.')
