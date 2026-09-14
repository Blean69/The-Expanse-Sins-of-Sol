"""Stage 1 ability overlays. No unit, registry, localization or installation mutation."""
from __future__ import annotations
import argparse
import copy
import json
from pathlib import Path

BASE = Path('/run/media/haker/NVME 2/expanse-mod/build/experiments/expanse_update19')
LOCK = 'expanse20_boarding_target_lock'
BOARDING = ('expanse06_amun_boarding', 'expanse10_donnager_marines',
            'expanse12_raptor_marines', 'expanse12_pella_marines', 'expanse12_scirocco_marines')
REPAIR = 'expanse15_scirocco_engineering_teams'


def unit(name): return {'unit_type': name}
def owner(name): return {'player_type': 'unit_owner', 'owned_unit': unit(name)}
def negate(constraint): return {'constraint_type': 'composite_not', 'constraint': constraint}
def conjunction(*constraints):
    if len(constraints) > 5:
        return conjunction(*constraints[:4], conjunction(*constraints[4:]))
    return {'constraint_type': 'composite_and', 'constraints': list(constraints)}
def passes(name, filter_id):
    return {'constraint_type': 'unit_passes_target_filter', 'unit': unit(name), 'target_filter_id': filter_id}
def within(a, b, value):
    return {'constraint_type': 'distance_between_units_comparison', 'unit_a': unit(a),
            'unit_b': unit(b), 'comparison_type': 'less_than_equal_to', 'compare_value': value}
def operate(destination, operators, **kwargs):
    return {'action_type': 'use_unit_operators_on_single_unit', 'destination_unit': unit(destination),
            'operators': operators, **kwargs}
def val(name, number, **extra):
    return {'action_value_id': name, 'action_value': {'values': [number], **extra}}
def target(name, body): return {'target_filter_id': name, 'target_filter': body}


def changes(base: Path = BASE):
    edits, strings, report = {}, {}, {'status': 'offline authored; runtime NOT RUN', 'boarding': {}}
    def read(name, ext): return json.loads((base/'entities'/f'{name}.{ext}').read_text())
    def put(name, ext, value): edits[f'entities/{name}.{ext}'] = value
    repair, rads = read(REPAIR, 'ability'), read(REPAIR, 'action_data_source')
    manual = rads['target_filters'][0]['target_filter']
    manual['ownerships'] = ['self']
    auto = copy.deepcopy(manual)
    for c in auto['constraints']:
        if c['constraint_type'] == 'has_missing_hull':
            c.clear(); c.update(constraint_type='has_missing_hull', percentage_missing_threshold=0.2)
    rads['target_filters'].append(target('engineering_auto_target', auto))
    repair['active_actions']['auto_cast'] = {
        'enabled_by_default_behavior': 'always',
        'target_definitions': [{'target_filter': 'engineering_auto_target',
            'target_constraint': within('current_spawner', 'target', 'range')}]}
    put(REPAIR, 'ability', repair); put(REPAIR, 'action_data_source', rads)
    strings[REPAIR+'.description'] = ('Repairs one nearby owned ship for 20 hull per second for 20 seconds (400 maximum). '
        'Same-effect repairs do not stack. Autocast starts enabled and selects ships at 80% hull or lower already within 3,500 range. '
        'Manual casting can repair smaller hull losses. Costs 50 antimatter; 60-second cooldown.')
    report['repair'] = {'owned_only': True, 'default_autocast': True, 'autocast_remaining_hull_maximum': 0.8,
                        'repair_per_second': 20, 'seconds': 20, 'maximum': 400, 'antimatter': 50, 'cooldown': 60,
                        'manual_threshold_unchanged': True, 'buff_stacking_unchanged': True,
                        'range': 3500, 'no_move_orders_authored': True}
    for name in BOARDING:
        ability, ads = read(name, 'ability'), read(name, 'action_data_source')
        values = {v['action_value_id']: v['action_value']['values'][0] for v in ads['action_values']}
        old = ads['target_filters'][0]['target_filter']
        eligible = copy.deepcopy(old)
        # Explicit historical Amun/Europa Titan/command exception; no expansion of it to other launchers.
        eligible['unit_types'] = old['unit_types'] if name == BOARDING[0] else ['capital_ship']
        eligible['constraints'] += [{'constraint_type': 'has_missing_hull', 'percentage_missing_threshold': 0.7},
                                    negate({'constraint_type': 'is_dead_soon'})]
        start = copy.deepcopy(eligible)
        start['constraints'].append(negate({'constraint_type': 'has_buff', 'buff': LOCK, 'include_pending_buffs': True}))
        ads['target_filters'] = [target('boarding_capital_target', start), target('boarding_resolution_target', eligible),
            target('boarding_live_caster', {'unit_types': ['frigate','cruiser','capital_ship','super_capital_ship','titan'],
                'ownerships': ['self'], 'constraints': [{'constraint_type': 'has_health'}, negate({'constraint_type': 'is_dead_soon'})]})]
        ads['action_values'] += [val('boarding_lock_duration', values['boarding_crew_delay_time_value'] + 30),
            val('boarding_cancelled', 1, transform_type='current_buff_memory_value', memory_float_variable_id='boarding_cancelled')]
        ads['per_buff_memory_declaration'] = {'float_variable_ids': ['boarding_cancelled']}
        active = ability['active_actions']
        visual = copy.deepcopy(active['actions']['actions'][0])
        visual['operators'] = [o for o in visual['operators'] if o['operator_type'] == 'play_weapon_effects']
        # Lock is acquired immediately, not after the cosmetic travel delay. Native preserve-existing
        # plus pending-buff exclusion provides a single target budget across every Expanse launcher.
        active['actions']['actions'] = [operate('target', [{'operator_type': 'apply_buff', 'buff': LOCK}],
            range_value='boarding_crew_range_value', constraint=passes('target', 'boarding_capital_target')), visual]
        active['auto_cast'] = {'enabled_by_default_behavior': 'never', 'target_definitions': [
            {'target_filter': 'boarding_capital_target', 'target_constraint': within('current_spawner', 'target', 'boarding_crew_range_value')}]}
        put(name, 'ability', ability); put(name, 'action_data_source', ads)
        scope = 'capital and command ships or titans' if name == BOARDING[0] else 'capital ships'
        strings[name+'.description'] = (f'Board hostile {scope} at 30% hull or lower within 6,000 range. '
            f'{values["capture_chance"]*100:g}% capture chance after 3 seconds; {values["boarding_crew_cooldown_time_value"]:g}-second cooldown. '
            'Heroes are excluded. One Expanse boarding attempt per target, followed by 30 seconds of protection. '
            'Caster, target, hostility, range and fleet supply are checked again. Autocast starts disabled. Pods are visual effects.')
        report['boarding'][name] = {'chance_before_after': values['capture_chance'],
            'cooldown_before_after': values['boarding_crew_cooldown_time_value'], 'range_before_after': values['boarding_crew_range_value'],
            'delay_before_after': values['boarding_crew_delay_time_value'], 'target_types': eligible['unit_types']}
    # Self repair follows the same native toggle convention without changing its fixed heal.
    roci = 'expanse_roci_belter_ingenuity'
    ability = read(roci, 'ability')
    ability['active_actions']['auto_cast'] = {'enabled_by_default_behavior': 'always', 'caster_constraint': {
        'constraint_type': 'unit_passes_unit_constraint', 'unit': unit('current_spawner'), 'unit_constraint': conjunction(
            {'constraint_type': 'has_missing_hull', 'percentage_missing_threshold': 0.2},
            negate({'constraint_type': 'has_buff', 'buff': roci, 'include_pending_buffs': True}))}}
    put(roci, 'ability', ability)
    strings['expanse_roci_belter_ingenuity_description'] = ('Rapid self-repair: 100 hull per second for 10 seconds. '
        '90-second cooldown. Autocast starts enabled and activates at 80% hull or lower; right-click to toggle.')
    report['rocinante_repair'] = {'default_autocast': True, 'remaining_hull_maximum': 0.8, 'numbers_unchanged': True}
    buff_owner = {'player_type': 'buff_owner_player'}
    check = conjunction(passes('current_spawner', 'boarding_resolution_target'),
        passes('first_spawner', 'boarding_live_caster'),
        {'constraint_type': 'players_have_alliance_relationship', 'player_a': owner('first_spawner'), 'player_b': buff_owner, 'relationship_type': 'self'},
        {'constraint_type': 'players_have_alliance_relationship', 'player_a': owner('current_spawner'), 'player_b': buff_owner, 'relationship_type': 'enemy'},
        within('first_spawner', 'current_spawner', 'boarding_crew_range_value'),
        {'constraint_type': 'player_has_available_supply', 'player': buff_owner, 'minimum_available_supply': 'capture_target_supply', 'include_future_supply': True},
        {'constraint_type': 'value_comparison', 'value_a': 'boarding_cancelled', 'comparison_type': 'equal_to', 'value_b': 'fixed_zero'},
        {'constraint_type': 'random_chance', 'chance_value': 'capture_chance'})
    lock = {'version': 0, 'active_duration': 'boarding_lock_duration',
        'stacking_limit': {'stacking_limit': 'fixed_one', 'stacking_limit_met_behavior': 'preserve_existing_buff'},
        'stacking_ownership_type': 'for_all_players', 'restart_other_stacked_buffs_when_started': False,
        'make_dead_on_current_spawner_ownership_changed_from_buff_ownership': False,
        'time_actions': [{'first_action_delay_time_value': 'boarding_crew_delay_time_value',
            'execution_interval_count_value': 'fixed_one', 'action_group': {'constraint': check,
                'actions': [operate('current_spawner', [{'operator_type': 'change_owner_player', 'new_owner_player': buff_owner}])]}}],
        'trigger_event_actions': [{'trigger_event_type': 'on_buff_started', 'action_group': {
            'actions': [{'action_type': 'change_buff_memory_float_value', 'float_variable': 'boarding_cancelled',
                         'math_operators': [{'operator_type': 'assign', 'operand_value': 'fixed_zero'}]}]}},
            {'trigger_event_type': 'on_current_spawner_player_ownership_changed', 'action_group': {
            'actions': [{'action_type': 'change_buff_memory_float_value', 'float_variable': 'boarding_cancelled',
                         'math_operators': [{'operator_type': 'assign', 'operand_value': 'fixed_one'}]}]}}],
        'gui': {'hud_icon': 'pirate_boarding_crew_hud_icon', 'name': LOCK+'.name', 'visibility_scope': 'negative', 'is_visible_within_unit_tooltip': True}}
    put(LOCK, 'buff', lock)
    strings[LOCK+'.name'] = 'Boarding engagement / recovery protection'
    report['new_buffs'] = [LOCK]
    report['cancellation'] = {'target_ownership_changed': 'Permanent cancellation flag; lock remains through original 33-second expiry.',
        'caster_dead_or_currently_captured': 'Resolution fails live-caster/owner check; lock still expires at 33 seconds.',
        'target_dead': 'No target remains to capture; normal target-owned buff cleanup.',
        'target_healed_out_of_threshold_or_left_range_or_not_hostile': 'Resolution fails; cooldown is consumed, no refund.',
        'player_defeat': 'No explicit defeated-player constraint exists in pinned action schema. Caster existence/health/ownership guards apply; defeat that leaves a living owned caster is NOT independently rejected.',
        'caster_captured_then_recaptured_within_delay': 'Current owner checked at resolution; transient caster ownership loss is not remembered. NOT claimed covered.',
        'simultaneous_attempts': 'Shared preserve-existing target buff and pending-buff exclusion authored; engine ordering still requires multiplayer runtime test.',
        'save_reload': 'Uses native buff lifetime/memory and synchronized random_chance, no external timer; runtime NOT RUN.'}
    return edits, strings, report


def main():
    parser = argparse.ArgumentParser(); parser.add_argument('--out', type=Path, required=True); parser.add_argument('--base',type=Path,default=BASE)
    args=parser.parse_args(); edits, strings, report=changes(args.base)
    for relative, data in edits.items():
        p=args.out/relative; p.parent.mkdir(parents=True,exist_ok=True); p.write_text(json.dumps(data,indent=2)+'\n')
    (args.out/'localization-fragment.json').write_text(json.dumps(strings,indent=2)+'\n')
    (args.out/'integration-report.json').write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps({'definitions': len(edits), 'new_buffs': report['new_buffs']}))

if __name__ == '__main__': main()
