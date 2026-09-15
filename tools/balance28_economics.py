"""Stage A only: pure definition overlay against the frozen 0.27.5 menu package.

No filesystem mutations, installs, runtime claims, damage or torpedo multipliers.
Return (edits keyed by package-relative path, origins, report).
"""
from copy import deepcopy
import hashlib
import json
from pathlib import Path

GAME = Path('/run/media/haker/NVME 2/SteamLibrary/steamapps/common/Sins2')
TRUMAN = 'expanse15_truman'
RAPTOR = 'expanse12_raptor'
HEPH = 'expanse27_hephaestus'
NATHAN = 'expanse27_nathan_hale'
UNLOCK = 'expanse28_truman_command_procurement'
COLONY = 'expanse28_nathan_expeditionary_colonize'


def changes(base):
    base = Path(base)
    edits, origins, reasons = {}, {}, {}
    def read(rel):
        path = base / rel
        if not path.exists():
            path = GAME / rel
        return json.loads(path.read_text())
    def entity(uid, kind):
        return read(f'entities/{uid}.{kind}')
    def put(rel, data, source):
        edits[rel] = data
        reasons[rel] = source
        source_rel = {
            f'entities/{UNLOCK}.research_subject': 'entities/dlc2_trader_unlock_loyalist_super_capital_ship.research_subject',
            f'entities/{COLONY}.ability': 'entities/trader_colony_frigate_colonize.ability',
        }.get(rel, rel)
        source_path = base / source_rel
        origins[rel] = str(source_path if source_path.exists() else GAME / source_rel)
    def unit(uid):
        return entity(uid, 'unit')
    def write_unit(uid, data, reason):
        put(f'entities/{uid}.unit', data, reason)
    def classify(data, kind):
        old = {'capital_ship', 'cruiser', 'super_capital_ship'}
        data['tags'] = [t for t in data.get('tags', []) if t not in old] + [kind]
        data['build']['build_kind'] = kind
        data['build']['build_group_id'] = kind
        data['target_filter_unit_type'] = kind
        data['user_interface']['pip_type'] = kind
        data['ai_attack_target']['attack_target_type'] = {
            'capital_ship': 'capital', 'cruiser': 'heavy', 'super_capital_ship': 'supercapital'
        }[kind]
    def append_ability(data, ability):
        flat = [x for row in data.get('abilities', []) for x in row['abilities']]
        if ability not in flat:
            data['abilities'][0]['abilities'].append(ability)

    old_truman, old_raptor, old_heph = unit(TRUMAN), unit(RAPTOR), unit(HEPH)
    truman, raptor, heph = map(deepcopy, (old_truman, old_raptor, old_heph))
    donnager = unit('expanse_donnager_battleship')
    classify(truman, 'super_capital_ship')
    truman['build']['supply_cost'] = 400.0
    for resource in ('credits', 'metal', 'crystal'):
        truman['build']['price'][resource] = max(
            old_truman['build']['price'].get(resource, 0),
            round(donnager['build']['price'][resource] * 0.8, 6))
    truman['build']['build_time'] = max(old_truman['build']['build_time'],
                                         donnager['build']['build_time'] * 0.8)
    # AND the command unlock with any existing OR prerequisite branches.
    prereqs = truman['build'].get('prerequisites') or [[]]
    truman['build']['prerequisites'] = [list(dict.fromkeys(row + [UNLOCK])) for row in prereqs]
    # Preserve the four existing component slots; native command kind permits standard
    # components already tagged super_capital_ship, not station modules.
    write_unit(TRUMAN, truman, 'Native super_capital_ship classification; economics floor; health/levels/weapons unchanged')

    classify(raptor, 'cruiser')
    # Fold ONLY the former level-zero AM modifiers into base AM before removing levels.
    # All six fixed-level abilities remain usable, including reactor and marine actions.
    zero = old_raptor.get('levels', {}).get('levels', [{}])[0]
    for key, value in zero.get('unit_modifiers', {}).get('additive_values', {}).items():
        if key in ('max_antimatter', 'antimatter_restore_rate'):
            raptor.setdefault('antimatter', {})[key] = old_raptor.get('antimatter', {}).get(key, 0) + value
    raptor.pop('levels', None)
    raptor.pop('items', None)
    raptor['item_builds'] = []
    raptor['health']['levels'] = [deepcopy(old_raptor['health']['levels'][0])]
    write_unit(RAPTOR, raptor, 'Cruiser progression/items removed; exact L1 health, AM and fixed abilities preserved')

    classify(heph, 'capital_ship')
    # Nathan already uses an ordinary capital XP/AM table without weapon scaling.
    heph['levels'] = deepcopy(unit(NATHAN)['levels'])
    heph['antimatter'] = deepcopy(unit(NATHAN)['antimatter'])
    heph['items'] = deepcopy(old_heph.get('items') or old_raptor['items'])
    heph['item_builds'] = deepcopy(old_heph.get('item_builds') or old_raptor['item_builds'])
    first = old_heph['health']['levels'][0]
    heph['health']['levels'] = []
    for index in range(10):
        row = deepcopy(first)
        for key in ('max_hull_points', 'max_armor_points'):
            row[key] = round(first[key] * (1 + 0.03 * index), 6)
        # Existing OPA command pattern, with the destroyer's original L1 bounty.
        row['experience_given_on_death'] = first.get('experience_given_on_death', 35) + 60 * index
        heph['health']['levels'].append(row)
    write_unit(HEPH, heph, 'Ordinary capital; existing native XP/AM; conservative +3% hull/armor per level, no weapon scaling')

    # Existing ordinary UNN hull keeps its procurement and combat configuration.
    # Reuse verified colony shuttle origin already compiled into Nathan's hull.
    nathan = unit(NATHAN)
    append_ability(nathan, COLONY)
    append_ability(nathan, 'expanse15_scirocco_engineering_teams')
    nathan['colonize_ability'] = COLONY
    nathan['item_builds'] = [x for x in nathan.get('item_builds', [])
                           if 'expanse21_truman_colony_module' not in x.get('build_group', [])]
    if 'colonize_planet' not in nathan['ship_roles']:
        # Native role enum is colonize, verified below using the existing colony frigate.
        for role in unit('trader_colony_frigate')['ship_roles']:
            if role not in nathan['ship_roles']:
                nathan['ship_roles'].append(role)
    write_unit(NATHAN, nathan, 'Disclosed expeditionary support refit; native colonize + existing capped/nonstacking repair; no cost/stat changes')
    colony = entity('trader_colony_frigate_colonize', 'ability')
    colony['level_source'] = 'fixed_level_0'
    for action in colony['active_actions']['actions']['actions']:
        for operator in action.get('operators', []):
            if operator.get('operator_type') == 'play_weapon_effects':
                operator['mesh_point'] = 'weapon.torpedo.0'
    colony['gui']['name'] = COLONY + '.name'
    colony['gui']['description'] = COLONY + '.description'
    put(f'entities/{COLONY}.ability', colony, 'Native trader_colony_frigate_colonize; existing Nathan weapon.torpedo.0 shuttle origin')

    unlock = entity('dlc2_trader_unlock_loyalist_super_capital_ship', 'research_subject')
    unlock.update(name=UNLOCK + '.name', name_uppercase=UNLOCK + '.name_uppercase',
                  description=UNLOCK + '.description', hud_icon='expanse15_truman_hud_icon',
                  tooltip_picture='expanse15_truman_tooltip_picture')
    put(f'entities/{UNLOCK}.research_subject', unlock, 'Native command unlock tier3 [6,0], titan-factory prerequisite and unchanged native costs')

    players = []
    for path in sorted((base / 'entities').glob('*.player')):
        data = json.loads(path.read_text())
        roster = data.get('buildable_units', []) + data.get('faction_buildable_units', [])
        if TRUMAN not in roster:
            continue
        # Existing super-capital tag has only Truman in each actual UNN build roster.
        others = []
        for uid in roster:
            if uid == TRUMAN:
                continue
            try:
                if 'super_capital_ship' in unit(uid).get('tags', []):
                    others.append(uid)
            except FileNotFoundError:
                pass
        if others:
            raise ValueError(f'Command cap requires review: {path.name}: {others}')
        for cap in data['unit_limits']['global']:
            if cap['tag'] == 'super_capital_ship':
                cap['unit_limit'] = 2
                break
        else:
            data['unit_limits']['global'].append({'tag': 'super_capital_ship', 'unit_limit': 2})
        subjects = data['research']['research_subjects']
        if UNLOCK not in subjects:
            subjects.append(UNLOCK)
        put('entities/' + path.name, data, 'UNN native aggregate command cap2 and actual command procurement graph registration')
        players.append(path.stem)

    # Existing OPA override codes intentionally permit command/titan capture. Preserve
    # that feature for other targets, but exclude Truman at launch AND delayed resolution.
    capture_guards = []
    for path in sorted((base / 'entities').glob('*.action_data_source')):
        data = json.loads(path.read_text())
        changed = False
        for entry in data.get('target_filters', []):
            fid = entry.get('target_filter_id', '')
            target = entry.get('target_filter', {})
            if fid in ('boarding_capital_target', 'boarding_resolution_target') and 'super_capital_ship' in target.get('unit_types', []):
                guard = {'constraint_type': 'composite_not', 'constraint': {
                    'constraint_type': 'has_definition', 'unit_definition': TRUMAN}}
                constraints = target.setdefault('constraints', [])
                if guard not in constraints:
                    constraints.append(guard)
                    changed = True
        if changed:
            put('entities/' + path.name, data, 'Prevent Truman command capture at acquisition and delayed ownership-change validation; other capture unchanged')
            capture_guards.append(path.stem)

    locpath = 'localized_text/en.localized_text'
    loc = read(locpath)
    loc.update({
        UNLOCK + '.name': 'Truman Command Procurement',
        UNLOCK + '.name_uppercase': 'TRUMAN COMMAND PROCUREMENT',
        UNLOCK + '.description': 'Unlocks the Truman-class command ship at the titan shipyard. 400 fleet supply; a native empire limit of two command ships applies. Full command-ship construction cost.',
        COLONY + '.name': 'Expeditionary Colonization Teams',
        COLONY + '.description': 'Colonizes an eligible neutral planet using the standard colony-frigate service. Nathan Hale expeditionary refit; no extra planetary bonuses.',
    })
    # Replace stale supply/class wording before adding the current acquisition details.
    loc[TRUMAN + '.description'] = ('UNN command battleship. Two heavy railguns, eighteen slower-tracking PDC batteries, and a six-light-torpedo volley. Existing hull, armor and weapon progression retained.')
    loc[RAPTOR + '.description'] = 'Fast Martian cruiser. Nine PDCs, eighteen light torpedoes and fleet-support abilities. 150 supply.'
    # Explain classification and native cap without overwriting useful weapon descriptions.
    for uid, suffix in [(TRUMAN, ' Command Ship: 400 supply, maximum two via the native command cap; requires Truman Command Procurement and the titan shipyard.'),
                        (RAPTOR, ' Cruiser classification: fixed level-one combat stats and abilities; no capital experience or component slots.'),
                        (HEPH, ' Ordinary capital ship: four component slots and conservative hull/armor experience progression.'),
                        (NATHAN, ' Expeditionary refit: standard colonization and bounded Combat Engineering Teams repair; existing procurement and combat stats retained.')]:
        key = uid + '.description'
        if suffix not in loc.get(key, ''):
            loc[key] = loc.get(key, '') + suffix
    put(locpath, loc, 'Stage A acquisition/classification/support tooltips')

    report = {
        'stage': 'A', 'baseline': str(base), 'players': players,
        'truman': {'before_build': old_truman['build'], 'after_build': truman['build'],
                   'health_preserved': truman['health'] == old_truman['health'],
                   'combat_progression_preserved': truman['levels'] == old_truman['levels'],
                   'items_preserved': truman.get('items') == old_truman.get('items'),
                   'native_cap_tag': 'super_capital_ship', 'cap': 2,
                   'factory': 'trader_loyalist_titan_factory_structure'},
        'raptor': {'health_L1_preserved': raptor['health']['levels'][0] == old_raptor['health']['levels'][0],
                   'abilities_preserved': raptor['abilities'] == old_raptor['abilities'], 'fixed_antimatter': raptor['antimatter']},
        'hephaestus': {'health_L1_preserved': heph['health']['levels'][0] == old_heph['health']['levels'][0],
                      'L10_hull': heph['health']['levels'][-1]['max_hull_points'],
                      'L10_armor': heph['health']['levels'][-1]['max_armor_points'],
                      'weapon_level_modifiers': False},
        'capture_guards': capture_guards,
        'menu_cosmetic_clones': 'Excluded from gameplay edits and cap reasoning: expanse_menu27_* are menu-only display entities, absent playable build rosters. Parent may regenerate visual metadata.',
        'new_entity_manifest_entries': {'ability': [COLONY], 'research_subject': [UNLOCK]},
        'new_unit_tags': [],
        'observed_static': ['Native titan factory accepts super_capital_ship; ordinary capital factory accepts cruiser/capital_ship.',
                            'Native command cap uses existing player.unit_limits.global, no new tag budget.',
                            'Native command classification removes capital_ship kind/tag, including first-capital item eligibility.',
                            'Cheap trader_colony_frigate and tier2 Nathan Hale procurement remain available.',
                            'No damage/reload/speed/torpedo/audio/model changes in this fragment.'],
        'untested_runtime': ['Two simultaneous queues, cancellation and death releasing cap reservations.',
                            'Ownership transfer/diplomacy/rewards respecting cap; native cap is not proven an absolute ownership guard.',
                            'First capital discount vs full command billing in actual game.',
                            'Save/reload, multiplayer and legacy saves with already-owned excess ships or Raptor items.',
                            'Existing-hull and newly-built progression, role AI and colony/repair UI in game.'],
        'edit_reasons': reasons,
        'baseline_hashes': {uid: hashlib.sha256((base / f'entities/{uid}.unit').read_bytes()).hexdigest()
                            for uid in (TRUMAN, RAPTOR, HEPH, NATHAN)},
    }
    return edits, origins, report
