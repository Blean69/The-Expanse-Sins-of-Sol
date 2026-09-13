#!/usr/bin/env python3
"""Read-only installed TEC shield grant audit for main integration."""
import json,hashlib
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
MAIN=ROOT if ROOT.name=='expanse-mod' else ROOT.parent.parent/'expanse-mod'
GAME=MAIN.parent/'SteamLibrary/steamapps/common/Sins2'
def read(p):return json.loads(p.read_text())
def walk(d,path=''):
    if isinstance(d,dict):
        yield path,d
        for k,v in d.items():yield from walk(v,path+'/'+k)
    elif isinstance(d,list):
        for i,v in enumerate(d):yield from walk(v,path+'/'+str(i))
rows=[]
for p in sorted((GAME/'entities').iterdir()):
    if not p.name.startswith(('trader_','dlc2_trader_')) or p.suffix not in ['.unit_item','.research_subject','.ability','.buff','.action_data_source']:continue
    d=read(p);hits=[]
    for path,obj in walk(d):
        if 'shield' in obj.get('modifier_type','') or obj.get('operator_type')=='repair_damage' and obj.get('affect_type')=='shields_only':hits.append({'path':path,'definition':obj})
    if hits:rows.append({'file':p.name,'sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'hits':hits})
mut=read(GAME/'uniforms/unit_mutation.uniforms')
names=['disable_can_shields_absorb_damage','disable_can_have_shields_restored','disable_can_passively_regenerate_shields']
examples={n:[] for n in names}
for p in(GAME/'entities').glob('*.buff'):
    d=read(p)
    for n in names:
        if n in d.get('unit_mutations',[]):examples[n].append(p.name)
shield_only_items=['trader_backup_shield_generator','trader_starbase_additional_shield_generator']
shield_research=['trader_shields_corvette','trader_shields_frigate','trader_shields_cruiser','trader_shields_0','trader_shields_1','trader_shield_burst_restore','trader_unlock_backup_shield_generator_unit_item','trader_upgrade_backup_shield_generator_unit_item']
mixed_items=['trader_starbase_structural_integrity_0','trader_starbase_structural_integrity_1','trader_starbase_structural_integrity_2']
for n in shield_only_items+mixed_items:assert(GAME/'entities'/(n+'.unit_item')).is_file()
for n in shield_research:assert(GAME/'entities'/(n+'.research_subject')).is_file()
out={'status':'READ-ONLY installed evidence, no runtime shield proof','shield_modifier_and_repair_hits':rows,'guard_mutations':names,'installed_mutation_permission_mappings':{path:obj for path,obj in walk(mut)if any(n in obj.get('disabling_mutations',[])for n in names)},'installed_buff_examples':examples,'shield_only_ship_shop_items_to_hide':shield_only_items,'shield_only_research_to_hide':shield_research,'mixed_items_keep_other_modifiers':mixed_items,'mixed_ADS_or_buff_keep_other_effects':['trader_carrier_capital_ship_deploy_missile_battery.buff','trader_command_cruiser_embolden.action_data_source','trader_support_capital_ship_energy_transfer.ability'],'native_Shield_Surge':'trader_loyalist_titan_shield_surge.ability contains4 repair_damage/shields_only operators; remove ability from TEC Ankylon coexisting set or disable it rather than charge antimatter for no effect. No replacement ability invented.','planetary_shield_scope':'trader_starbase_planetary_shield_array and trader_loyalist_titan_planetary_shield_array are PLANET modifier abilities, not ship health shields. Preserve unless user scope includes planetary shields. If removing, hide their2items and2unlock research nodes too.','guard_qualification':'All3mutation IDs exist and their permission disabling mappings are verified. Passive guard should prevent absorption and restoration including outside allied buffs, but zero displayed capacity under externally added capacity is not proven by these permission flags. Test allied grants, captured ships, saved games, shield burst and ability removal/reapplication.','research_graph_requirement':'Before removing listed research from player rosters, identify surviving prerequisites and surgically remove only dependencies on hidden nodes; do not orphan unrelated mixed armor/economy research.','main_scope':'No shared unit/skin/player/uniform/research/item modified by worker.'}
p=ROOT/'audit/update11-a/shield-gap-audit.json';p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(out,indent=2)+'\n');print(len(rows),'installed files with shield modifier/repair definitions audited;',p)
if not all(examples.values()):raise AssertionError('Missing installed mutation usage')
