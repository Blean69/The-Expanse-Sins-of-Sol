"""Pure native colonization/bombardment fragment authoring; never installs or edits a player.

The integrator supplies final IDs, verified mesh points, and merges eligibility tags,
manifests, item shop lists, unit bindings and localization. These fragments are not
a playable package. Native files are read-only. No ship combat/economy edits here.
"""
from __future__ import annotations
from copy import deepcopy
from pathlib import Path
import json
import hashlib

GAME = Path('/run/media/haker/NVME 2/SteamLibrary/steamapps/common/Sins2')


def native(name, game=GAME):
    return json.loads((Path(game) / 'entities' / name).read_text())


def colony_module(prefix, launch_mesh_point, eligibility_tag, game=GAME):
    """One normal component; fixed first-level native Akkan colony action/init.

    Eligibility MUST be a registered tag placed only on the designated repeatable
    colony capitals. Generic capital_ship alone would leak the module to all caps.
    No capture operator, ownership cheat, script timer, or added active hull slot.
    """
    if not all(isinstance(x, str) and x for x in (prefix, launch_mesh_point, eligibility_tag)):
        raise ValueError('Explicit IDs, mesh point and eligibility tag are required')
    ability = native('trader_colony_capital_ship_colonize.ability', game)
    ability['action_data_source'] = prefix
    ability['level_source'] = 'fixed_level_0'
    ability.pop('min_required_unit_levels')
    action = ability['active_actions']['actions']['actions'][0]
    action['operators'][1]['mesh_point'] = launch_mesh_point
    # Preserve native colony-track initialization buff and its action-value names.
    # Native targeting and the colonize_planet operator remain completely intact.
    source = native('trader_colony_capital_ship_colonize.action_data_source', game)
    source['level_count'] = 1
    for value in source['action_values']:
        value['action_value']['values'] = value['action_value']['values'][:1]
    ability['gui']['name'] = prefix + '.name'
    ability['gui']['description'] = prefix + '.description'
    item = native('trader_derelict_specialist.unit_item', game)
    item.pop('build_prerequisites')
    item.pop('unit_modifiers')
    item.update(name=prefix+'.name', description=prefix+'.description',
                required_unit_tags=[eligibility_tag], ability=prefix,
                hud_icon='trader_colony_capital_ship_colonize_ability_hud_icon')
    # Native specialist economics retained: 475 credits / 75 metal / 75 crystal,
    # 20 base seconds, one component slot. Player missing-shop time scalar applies.
    return {
        prefix+'.ability': ability,
        prefix+'.action_data_source': source,
        prefix+'.unit_item': item,
    }


def local_bombardment_weapon(prefix, game=GAME):
    """Native Akkan separate siege stores; requires explicit hostile planet order.

    The projectile is a standard native bombardment visual, NOT an interceptable
    torpedo object. No ship-to-ship magazine, torpedo damage, or fuel modification.
    """
    weapon = native('trader_colony_capital_ship_planet_bombing.weapon', game)
    weapon['name'] = prefix+'.name'
    assert weapon['weapon_type'] == 'planet_bombing'
    assert weapon['acquire_target_logic'] == 'order_target_only'
    assert weapon['uniforms_target_filter_id'] == 'common_planet_bombing'
    assert (weapon['bombing_damage'], weapon['population_damage'], weapon['cooldown_duration']) == (75, 3, 15)
    return {prefix+'.weapon': weapon}


def native_effect_aliases(game=GAME):
    """Merge by alias_name into each recipient skin stage; do not replace its aliases."""
    stage = native('trader_colony_capital_ship.unit_skin', game)['skin_stages'][0]
    result = [deepcopy(a) for a in stage['effects']['effect_alias_bindings']
              if 'planet_bombing' in a['alias_name'] or a['alias_name']=='trader_colony_shuttle']
    assert len(result) == 5
    return result


def bombardment_mount(weapon_id, mesh_point):
    """Use a caller-verified forward-facing hull point; retains native aim limits.

    mesh_point comes from read_mesh(...)[meshpoints], including name/position.
    The point must face game +Z: caller checks the actual rotation, not just name.
    """
    if mesh_point['rotation'] != [1.,0.,0.,0.,1.,0.,0.,0.,1.]:
        raise ValueError('Mount requires verified identity rotation / forward +Z')
    return {
        'weapon': weapon_id,
        'mesh_point': mesh_point['name'],
        'weapon_position': deepcopy(mesh_point['position']),
        'non_turret_muzzle_positions': [deepcopy(mesh_point['position'])],
        'forward': [0.,0.,1.], 'up': [0.,1.,0.],
        'yaw_arc': {'min_angle': -10., 'max_angle': 10.},
        'pitch_arc': {'min_angle': -10., 'max_angle': 10.},
    }


def changes(base, opa_command_id=None, prefix='expanse_doctrine'):
    """Return (entity edits, localization, native origins, merge report).

    No existing .unit or .unit_skin is emitted. Main applies report.unit_patches
    and report.skin_patches, retaining its Stage 1 modifications. OPA command is a
    separately authored capital, never the existing Europa frigate.
    """
    from common import read_mesh
    base = Path(base)
    def read_entity(name):
        p = base/'entities'/name
        if not p.exists(): p = GAME/'entities'/name
        return json.loads(p.read_text()), p
    edits, strings, origins = {}, {}, {}
    report = {'status':'PROPOSED MERGE FRAGMENTS; runtime NOT RUN',
              'unit_patches':{}, 'skin_patches':{}, 'player_ship_components_append':[],
              'unit_tag_entries_append':[], 'colony':[], 'bombardment':[]}
    bomb_id = prefix+'_local_bombardment'
    edits.update(local_bombardment_weapon(bomb_id))
    origins[bomb_id+'.weapon'] = str(GAME/'entities/trader_colony_capital_ship_planet_bombing.weapon')
    strings[bomb_id+'.name'] = 'Local planetary siege stores'
    designated = {'expanse12_scirocco':('scirocco','weapon.light_torpedo.0'),
                  'expanse15_truman':('truman','weapon.torpedo.0')}
    if opa_command_id:
        assert opa_command_id != 'expanse19_europa_bane', 'OPA command must be a separate capital'
        designated[opa_command_id] = ('opa_command','weapon.torpedo.0')
    inventory = {
       'expanse_mcrn_corvette':'expanse03_torpedo_magazine',
       'expanse_rocinante_hero':'expanse03_roci_torpedo_magazine',
       'expanse_donnager_battleship':'expanse10_donnager_heavy_magazine',
       'expanse12_scirocco':'expanse12_scirocco_heavy_magazine',
       'expanse15_truman':'expanse15_truman_light_magazine',
    }
    if opa_command_id: inventory[opa_command_id] = 'expanse19_europa_magazine'
    for ship_id, magazine_id in inventory.items():
        source_ship_id = 'expanse19_europa_bane' if ship_id == opa_command_id else ship_id
        unit, unit_path = read_entity(source_ship_id+'.unit')
        patch = report['unit_patches'].setdefault(ship_id,{})
        skin_ids = [s for g in unit['skin_groups'] for s in g['skins']]
        # For the new OPA command main clones a skin; patches must target that
        # new skin ID rather than modifying Europa's gameplay/appearance in place.
        for skin_id in skin_ids:
            skin,_ = read_entity(skin_id+'.unit_skin')
            recipient_skin = ship_id if ship_id == opa_command_id else skin_id
            report['skin_patches'][recipient_skin] = {'effect_alias_bindings_merge':native_effect_aliases()}
        skin,_ = read_entity(skin_ids[0]+'.unit_skin')
        mesh_id = skin['skin_stages'][0]['unit_mesh']['mesh']
        mesh_path = base/'meshes'/(mesh_id+'.mesh')
        mesh = read_mesh(mesh_path)
        magazine,magazine_path = read_entity(magazine_id+'.ability')
        positions = magazine.get('ability_positions')
        assert positions, f'Missing actual launcher positions: {magazine_path}'
        position = positions[0]
        names = [p['name'] for p in mesh['meshpoints']]
        # The older hero/Donnager rigs use explicit ability_positions plus center.
        # Native weapon muzzle positions use the same local coordinates directly.
        point_name = next((p['name'] for p in mesh['meshpoints']
                           if p['position'] == position['position']), 'center')
        assert point_name in names
        rot = position['rotation']
        mount = {'weapon':bomb_id, 'mesh_point':point_name,
          'weapon_position':position['position'],
          'non_turret_muzzle_positions':[position['position']],
          'forward':rot[6:9], 'up':rot[3:6],
          'yaw_arc':{'min_angle':-10.,'max_angle':10.},
          'pitch_arc':{'min_angle':-10.,'max_angle':10.}}
        patch['weapons_append'] = [mount]
        report['bombardment'].append({'ship':ship_id,'source_ship':source_ship_id,
          'actual_anti_ship_magazine':magazine_id,
          'siege_eligibility_reason': 'Required designated colony capital with added siege-only stores'
             if ship_id in ['expanse15_truman',opa_command_id] else
             'Explicit Tachi/Rocinante expeditionary requirement' if ship_id in ['expanse_mcrn_corvette','expanse_rocinante_hero'] else
             'Existing true heavy-torpedo carrier',
          'mesh':mesh_id,'mesh_sha256':hashlib.sha256(mesh_path.read_bytes()).hexdigest(),
          'muzzle_source':str(magazine_path)+' /ability_positions/0',
          'mount':mount,'planet_damage':75,'population_damage':3,'interval':15,'range':4000,
          'interceptable':False,'ammunition':'Separate native siege stores; anti-ship magazine unchanged'})
        if ship_id not in designated: continue
        short, launch_point = designated[ship_id]
        assert launch_point in names, f'Missing real colony point {launch_point} in {mesh_id}'
        module_id = prefix+'_'+short+'_colony_module'
        tag = ship_id if ship_id == opa_command_id else prefix+'_'+short+'_colony_capital'
        new = colony_module(module_id,launch_point,tag)
        edits.update(new)
        for name in new:
            suffix = Path(name).suffix
            donor = 'trader_derelict_specialist' if suffix=='.unit_item' else 'trader_colony_capital_ship_colonize'
            origins[name] = str(GAME/'entities'/(donor+suffix))
        strings[module_id+'.name'] = 'Expeditionary Colony Module'
        strings[module_id+'.description'] = ('Native colony shuttle and starting infrastructure. '
          '120 antimatter; 120-second cooldown; 5000 range. Requires an unowned colonizable planet and '
          'the usual planet research. Costs 475 credits, 75 metal, 75 crystal; one equipment slot. '
          'Available immediately without battle experience. Native shop build-time rules apply.')
        patch['tags_append'] = [tag]
        patch['item_builds_append'] = [{'build_group':[module_id],'weight':5.0}]
        patch['colonize_ability'] = module_id
        report['unit_tag_entries_append'].append({'name':tag,'localized_name':module_id+'.name'})
        report['player_ship_components_append'].append(module_id)
        report['colony'].append({'ship':ship_id,'module':module_id,'launch_point':launch_point,
          'base_build_seconds':20,'outside_shop_build_seconds_at_current_scalar':200,
          'component_slots':1,'research_or_xp_prerequisite':False,
          'native_colony_buff':'trader_colony_capital_ship_colonize',
          'first_level_bonus_tracks':{'logistics':1,'commerce':1}})
    report['warnings'] = [
      'Only generated entity definitions are emitted. Main merges unit, skin, player, tags and localization recipes.',
      'OPA command skin recipe assumes main gives the NEW command unit a same-ID cloned Europa skin.',
      'bombing_damage is an unchanged installed extension absent from the pinned weapon schema; preserve it.',
      'No new weapon tags; physical is native. No anti-ship stats, magazines, supply or costs modified.',
      'Tachi and Rocinante currently use light torpedo objects despite old heavy_torpedo action-value names; siege eligibility is explicit doctrine adaptation, not a false heavy-object inventory.',
      'Donnager native siege mount uses its real aft heavy launcher frame. Verify ship facing and target acquisition in runtime.',
      'Item granted colonize_ability command resolution, native level/research bombing modifiers and all ownership/diplomacy stop cases remain runtime NOT RUN.',
    ]
    return edits,strings,origins,report
