"""Private capital loadouts and Sunflare burn from installed, pinned definitions."""
import copy
from pathlib import Path
import jsonschema
from build_polish import write
from validate_experiments import read, require, sha256
from donnager10_behavior import renamed, setvals, vals, av, has_creation
from build_hero03 import ability_positions

ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / 'build/experiments/expanse_update11'
GAME = ROOT.parent / 'SteamLibrary/steamapps/common/Sins2'
SDK = GAME.parent / 'Sins of a Solar Empire II - Mod Tools'
CONFIG = {
    'raptor': dict(supply=150, hull=4500., armor=2600., speed=1150., light_salvo=3, light_capacity=18, light_interval=10., reactor_speed=.25, reload_factor=1.25, boarding=.20),
    'pella': dict(supply=200, hull=5400., armor=3100., speed=1150., light_salvo=3, light_capacity=18, light_interval=10., reactor_speed=.35, reload_factor=1.35, boarding=.25),
    'scirocco': dict(supply=200, hull=6500., armor=3600., speed=1250., light_salvo=5, light_capacity=20, light_interval=10., reactor_speed=.25, reload_factor=1.25, boarding=.25),
}


def generate(out, metadata):
    local = {}
    files = []
    def emit(name, ext, data):
        schema = read(SDK / 'json_schemas' / ({'action_data_source': 'action-data-source'}.get(ext, ext) + '-schema.json'))
        jsonschema.Draft202012Validator(schema).validate(data)
        p = out / 'entities' / (name + '.' + ext)
        require(not p.exists(), 'Refusing existing private behavior: ' + str(p))
        write(p, data); files.append(str(p.relative_to(out)))
    for kind, cfg in CONFIG.items():
        prefix = 'expanse12_' + kind
        meta = metadata[kind]
        for rig in meta['rigs']:
            rail = rig['kind'] == 'rail'
            w = read(BASE / 'entities' / ('expanse03_hero_railgun.weapon' if rail else 'expanse10_donnager_pdc_0.weapon'))
            w['turret'] = copy.deepcopy(rig['turret_override'])
            w['name'] = prefix + ('.rail.name' if rail else '.pdc.name')
            if rail:
                w.update(damage=4000., penetration=1250., cooldown_duration=15., yaw_speed=30., pitch_speed=0., yaw_firing_tolerance=1., pitch_firing_tolerance=1.)
            else:
                w['range'] = 4500.
            emit(rig['mount']['weapon'], 'weapon', w)
        local[prefix + '.pdc.name'] = kind.title() + ' PDC'
        local[prefix + '.rail.name'] = 'Scirocco light railgun'
        for heavy in ([False, True] if kind == 'scirocco' else [False]):
            label = 'heavy' if heavy else 'light'
            source = 'expanse10_donnager_' + label + '_magazine'
            ident = prefix + '_' + label + '_magazine'
            count = 1 if heavy else cfg['light_salvo']
            capacity = 5 if heavy else cfg['light_capacity']
            interval = 20. if heavy else cfg['light_interval']
            for ext in ['ability', 'buff', 'action_data_source']:
                d = renamed(read(BASE / 'entities' / (source + '.' + ext)), 'expanse10_donnager', prefix)
                # Retain existing heavy projectile definition: only this new
                # magazine's cadence changes; no duplicate health/damage edit.
                d = renamed(d, prefix + '_heavy_torpedo', 'expanse10_donnager_heavy_torpedo')
                if ext == 'ability':
                    d['ability_positions'] = ability_positions(meta['equipment'][label + '_torpedo_ports'])
                elif ext == 'buff':
                    acts = d['time_actions'][0]['action_group']['actions']
                    templates = [x for x in acts if has_creation(x)]
                    require(templates, 'Magazine has no installed-pattern torpedo creation')
                    replacement = []
                    inserted = False
                    for act in acts:
                        if has_creation(act):
                            if not inserted:
                                replacement.extend(copy.deepcopy(templates[0]) for _ in range(count)); inserted = True
                        else:
                            replacement.append(act)
                    acts[:] = replacement
                else:
                    setvals(d, {'heavy_torpedo_torpedo_count_value': capacity,
                                'combat03_torpedoes_per_interval_value': count,
                                'combat03_interval_count_value': capacity // count,
                                'combat03_interval_value': interval,
                                'magazine_capacity_value': capacity,
                                'magazine_pair_count_value': count,
                                'magazine_pair_interval_value': interval,
                                'donnager_reactor_extra_progress_tick': .25 * (cfg['reload_factor'] - 1.)})
                emit(ident, ext, d)
            local[ident + '.name'] = 'Martian heavy torpedoes' if heavy else 'Martian light torpedoes'
            local[ident + '.ammo_label'] = 'Torpedoes remaining'
            local[ident + '.description'] = f'{capacity} torpedoes; {count} every {interval:g} seconds, cycling measured launcher positions. Reloads 120 seconds after empty. ' + ('Targets detected enemy starbases and titans. ' if heavy else 'Targets detected enemies in the same gravity well. ') + 'Reactor overdrive accelerates magazine progress.'
        for part in ['reactor', 'launch_corvette', 'marines', 'reactor_breach']:
            ident = prefix + '_' + part
            exts = ['ability', 'action_data_source'] + ([] if part == 'launch_corvette' else ['buff'])
            for ext in exts:
                d = renamed(read(BASE / 'entities' / ('expanse10_donnager_' + part + '.' + ext)), 'expanse10_donnager', prefix)
                if ext == 'action_data_source':
                    if part == 'reactor':
                        setvals(d, {'cooldown': 140., 'duration': 20., 'antimatter': 75., 'speed': cfg['reactor_speed'], 'reload_duration_scalar': 1. / cfg['reload_factor'] - 1.})
                    elif part == 'launch_corvette':
                        setvals(d, {'pirate_mercenary_base_cooldown_time_value': 120.})
                    elif part == 'marines':
                        setvals(d, {'capture_chance': cfg['boarding'], 'boarding_crew_cooldown_time_value': 600.})
                    elif part == 'reactor_breach':
                        setvals(d, {'self_destruct_damage_value': 1500., 'self_destruct_radius_value': 2500.})
                if part == 'reactor_breach':
                    # Shared visual alias remains bound to the existing tested
                    # effect; damage values above are private to these capitals.
                    d = renamed(d, prefix + '_reactor_breach_explosion', 'expanse10_donnager_reactor_breach_explosion')
                if part == 'marines' and ext == 'ability':
                    for action in d['active_actions']['actions']['actions']:
                        for op in action.get('operators', []):
                            if op['operator_type'] == 'play_weapon_effects':
                                op['mesh_point'] = 'weapon.boarding.0'
                emit(ident, ext, d)
            if part == 'reactor':
                title = 'Reactor overdrive'
                desc = f'For 20 seconds: +{cfg["reactor_speed"] * 100:g}% speed and {(cfg["reload_factor"] - 1) * 100:g}% faster weapon/magazine progress. Costs 75 antimatter; 120 seconds of recovery after the boost.'
            elif part == 'launch_corvette':
                title = 'Request MCRN reinforcement'
                desc = 'One MCRN Corvette arrives after 2 seconds. Costs 300 credits and 55 metal, requires 55 free supply; 120-second cooldown. Arrival placement is controlled by the engine.'
            elif part == 'marines':
                title = 'Marine boarding party'
                desc = f'One {cfg["boarding"] * 100:g}% capture attempt after 3 seconds against a detected capital, command ship or titan. Requires free supply; 600-second cooldown. Hero ships are excluded. Timed pod visual; captured titans may exceed the construction cap.'
                local[ident + '.chance'] = 'Capture chance per attempt'
            else:
                title = 'Capital reactor breach'
                desc = 'Destruction damages nearby friendly and enemy ships: 1,500 damage within 2,500 range.'
            local[ident + '.name'] = title; local[ident + '.description'] = desc

    ident = 'expanse12_sunflare_burn'
    ability = read(BASE / 'entities/expanse_roci_overcharged_reactor.ability')
    ability = renamed(ability, 'expanse_roci_overcharged_reactor', ident)
    ability['active_actions'].pop('antimatter_cost')
    ability['active_actions'].update(cooldown_reset_type='on_start_use_ability', execute_time=0., stop_time=0., stop_use_type='on_stop_time_elapsed')
    ability['gui'] = {'name': ident + '.name', 'description': ident + '.description',
                      'hud_icon': 'trader_volatile_accelerants_unit_item_hud_icon', 'tooltip_icon': 'trader_volatile_accelerants_unit_item_hud_icon'}
    emit(ident, 'ability', ability)
    buff = read(GAME / 'entities/trader_volatile_accelerants_unit_item.buff')
    buff['stacking_limit']['stacking_limit_met_behavior'] = 'preserve_existing_buff'
    buff['restart_other_stacked_buffs_when_started'] = False
    tick = buff['time_actions'][0]
    tick.update(first_action_delay_time_value='fixed_one', execution_interval_count_value='ticks')
    op = tick['action_group']['actions'][0]['operators'][0]
    op.update(damage_value='self_damage', penetration_value='penetration')
    buff['unit_modifiers'] = [{'buff_unit_modifier_id': x} for x in ['speed', 'acceleration']]
    buff['unit_mutations'] = ['disable_can_passively_regenerate_hull']
    buff['gui'] = {'name': ident + '.name', 'hud_icon': 'trader_volatile_accelerants_unit_item_hud_icon', 'visibility_scope': 'positive'}
    emit(ident, 'buff', buff)
    ads = {'version': 0, 'action_values': [av(k, v) for k, v in {'cooldown': 120., 'ticks': 9., 'self_damage': 10., 'penetration': 1000., 'speed_scalar': 3.}.items()],
           'buff_unit_modifiers': [{'buff_unit_modifier_id': key, 'buff_unit_modifier': {'modifier_type': modifier, 'value_behavior': 'scalar', 'value_id': 'speed_scalar'}} for key, modifier in [('speed', 'max_linear_speed'), ('acceleration', 'max_linear_acceleration')]]}
    emit(ident, 'action_data_source', ads)
    local[ident + '.name'] = '20G burn'
    local[ident + '.description'] = 'Emergency burn for 9 seconds: 4x normal speed and acceleration, taking 10 hull damage each second. Disables passive hull regeneration during the burn. Can destroy an already damaged ship. 120-second cooldown.'
    return {'files': files, 'localization': local, 'config': CONFIG,
            'burn_evidence': {str(p): sha256(p) for p in [GAME / 'entities/trader_volatile_accelerants_unit_item.buff', GAME / 'entities/trader_volatile_accelerants_unit_item.action_data_source', GAME / 'uniforms/unit_mutation.uniforms']},
            'runtime': 'NOT RUN'}
