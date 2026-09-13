"""Stage an independent passive magazine experiment; preserve timed candidates.

Buff memory and schema checks are static evidence, not a save-serialization or
runtime test. Model tests exercise the intended state transitions only.
"""
import argparse
import copy
import hashlib
import json
import os
from pathlib import Path

import jsonschema

ROOT = Path(__file__).resolve().parents[1]
IDENTITY = "expanse03_torpedo_magazine"
PROJECTILE = "expanse03_heavy_torpedo"
PIN = "8e061033afe53b1393eaefd56617a3fd041eeb5f"


def read(path):
    if not path.is_file():
        raise SystemExit(f"BLOCKED: missing dependency {path}; no replacement downloaded")
    return json.loads(path.read_text(encoding="utf-8-sig"))


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def write(path, d):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(d, indent=2) + "\n")


def comparison(a, op, b):
    return {"constraint_type": "value_comparison", "value_a": a, "comparison_type": op, "value_b": b}


def conjunction(*args):
    return {"constraint_type": "composite_and", "constraints": list(args)}


def memory_change(variable, ops, constraint=None):
    d = {"action_type": "change_buff_memory_float_value", "float_variable": variable,
         "math_operators": [{"operator_type": op, "operand_value": value} for op, value in ops]}
    if constraint is not None:
        d["constraint"] = copy.deepcopy(constraint)
    return d


def unit_guard(constraint):
    return {"constraint_type": "unit_passes_unit_constraint", "unit": {"unit_type": "current_spawner"},
            "unit_constraint": constraint}


def model_checks():
    """Reference oracle for intended state, not an emulator of the game engine."""
    class Magazine:
        def __init__(self):
            self.ammo, self.next_pair, self.reload_ready = 8, 0.0, 0.0
            self.launches = []

        def tick(self, now, available=True, can_fire=True, order="attack"):
            # Orders intentionally have no state effect: this is autonomous fire.
            if self.ammo == 0 and now >= self.reload_ready:
                self.ammo = 8
            if available and can_fire and self.ammo >= 2 and now >= self.next_pair:
                self.launches.append((now, 2))
                self.ammo -= 2
                self.next_pair = now + 10
                if self.ammo == 0:
                    self.reload_ready = now + 120

    m = Magazine()
    for t in range(151):
        m.tick(t)
    assert m.launches == [(0, 2), (10, 2), (20, 2), (30, 2), (150, 2)]
    missing = Magazine()
    missing.tick(0)
    for t in range(1, 61):
        missing.tick(t, available=False, order="move")
    assert missing.ammo == 6 and missing.reload_ready == 0 and missing.next_pair == 10
    missing.tick(60, available=True, order="attack new target")
    assert missing.ammo == 4 and missing.launches == [(0, 2), (60, 2)]
    missing.tick(60, available=True)
    assert missing.ammo == 4, "No duplicate pair on same tick"
    missing.tick(70); missing.tick(80)
    assert missing.ammo == 0 and missing.reload_ready == 200
    missing.tick(199.75)
    assert missing.ammo == 0
    missing.tick(200, available=False)
    assert missing.ammo == 8 and len(missing.launches) == 4
    missing.tick(201)
    assert missing.ammo == 6
    blocked = Magazine()
    for t in range(100):
        blocked.tick(t, can_fire=False)
    assert blocked.ammo == 8 and not blocked.launches
    blocked.tick(100, order="move")
    assert blocked.ammo == 6 and blocked.launches == [(100, 2)]
    return {"result": "PASS: intended state-machine model only; NOT game runtime",
            "continuous_target": m.launches, "target_loss_and_reacquisition": missing.launches,
            "asserted": ["Four paired launches at0/10/20/30, next150", "No ammo debit or reload during60-second target gap",
                         "Changed orders do not reset ammo", "Reacquisition resumes remaining ammo without catch-up salvos",
                         "Only depleted magazine starts120-second reload", "No duplicate pair atsame timestamp",
                         "Reload completes without targets", "Permission-blocked firing retains ammo"],
            "save_serialization_test": "NOT RUN; no Python round-trip presented as engine save evidence"}


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--source-root", type=Path, required=True)
    ap.add_argument("--timed-source", type=Path, default=ROOT / "build/combat03-a/filtered")
    ap.add_argument("--output", type=Path, default=ROOT / "build/combat03-a/persistent")
    args = ap.parse_args()
    out, source, previous = args.output.resolve(), args.source_root.resolve(), args.timed_source.resolve()
    if not out.is_relative_to(ROOT / "build/combat03-a") or out.exists():
        raise SystemExit("Use a fresh output under build/combat03-a; existing stages stay unchanged")
    for key in ["SINS2_GAME", "SINS2_SDK"]:
        if not os.environ.get(key):
            raise SystemExit(f"BLOCKED: set {key}")
    game, sdk = [Path(os.environ[k]).resolve() for k in ["SINS2_GAME", "SINS2_SDK"]]
    snapshot = read(source / "audit/schema-comparison.json")
    assert snapshot["official_commit"] == PIN
    for rec in snapshot["files"]:
        path = sdk / rec["path"]
        if not path.is_file():
            raise SystemExit(f"BLOCKED: missing pinned schema {path}")
        data = path.read_bytes()
        assert hashlib.sha1(b"blob " + str(len(data)).encode() + b"\0" + data).hexdigest() == rec["official_git_blob"], path
    pinned = read(source / "audit/installed-file-hashes.json")
    evidence = {}

    def base(relative):
        path = game / relative
        value = read(path)
        h = digest(path)
        if relative in pinned:
            assert h == pinned[relative]["sha256"], path
        evidence[relative] = {"sha256": h, "historical_pin_checked": relative in pinned}
        return value

    mem_source = base("entities/advent_battle_capital_ship_energy_absorptive_armor.action_data_source")
    permanent_source = base("entities/advent_battle_capital_ship_energy_absorptive_armor.ability")
    permanent_buff = base("entities/advent_battle_capital_ship_energy_absorptive_armor.buff")
    maw = base("entities/vasari_loyalist_titan_the_maw_on_self.buff")
    base("entities/trader_capital_ship_insurance_unit_item.ability")
    detector_source = base("entities/trader_orbital_cannon.action_data_source")
    global_values = base("uniforms/action.uniforms")
    normal = read(previous / "entities/expanse03_torpedo_cycle.ability")
    normal_buff = read(previous / "entities/expanse03_torpedo_cycle_on_self.buff")
    ads = copy.deepcopy(read(previous / "entities/expanse03_torpedo_cycle.action_data_source"))
    projectile = read(previous / "entities" / (PROJECTILE + ".unit"))
    assert permanent_source["passive_actions"]["persistant_buff"] == "advent_battle_capital_ship_energy_absorptive_armor"
    assert mem_source["per_buff_memory_declaration"]["float_variable_ids"] == ["stack_count", "stacks_expiry_time"]
    global_ids = {x["action_value_id"] for x in global_values["common_action_values"]}
    assert {"common_simulation_time_value", "fixed_zero", "fixed_one"} <= global_ids
    variables = ["ammo", "next_pair_ready", "reload_ready"]
    ads["per_buff_memory_declaration"] = {"float_variable_ids": variables, "unit_variable_ids": ["selected_target"]}
    constants = {"magazine_capacity_value": 8, "magazine_pair_count_value": 2,
                 "magazine_pair_interval_value": 10, "magazine_reload_duration_value": 120,
                 "magazine_poll_interval_value": 0.25}
    for key, value in constants.items():
        ads["action_values"].append({"action_value_id": key, "action_value": {"values": [float(value)]}})
    for variable in variables:
        ads["action_values"].append({"action_value_id": "magazine_" + variable + "_value",
            "action_value": {"transform_type": "current_buff_memory_value", "memory_float_variable_id": variable, "values": [1.0]}})
    for rec in ads["target_filters"]:
        rec["target_filter"].setdefault("constraints", []).append({"constraint_type": "is_detected"})
    ability = {"version": 0, "action_data_source": IDENTITY, "level_source": "fixed_level_0",
               "passive_actions": {"persistant_buff": IDENTITY, "only_if_owner_unit_operational": False},
               "gui": copy.deepcopy(normal["gui"]), "ability_positions": copy.deepcopy(normal["ability_positions"])}
    ability["gui"]["name"] = IDENTITY + ".name"
    ability["gui"]["description"] = IDENTITY + ".description"
    selected = {"unit_type": "buff_memory", "memory_unit_variable_id": "selected_target"}
    target_ok = {"constraint_type": "unit_passes_target_filter", "unit": selected, "target_filter_id": "heavy_torpedo_target_filter"}
    ready = conjunction(comparison("magazine_ammo_value", "greater_than_equal_to", "magazine_pair_count_value"),
                        comparison("common_simulation_time_value", "greater_than_equal_to", "magazine_next_pair_ready_value"),
                        unit_guard({"constraint_type": "is_fully_built"}),
                        unit_guard({"constraint_type": "has_permission", "permission_type": "can_use_weapons"}),
                        unit_guard({"constraint_type": "has_permission", "permission_type": "can_use_missile_weapons"}))
    reload_due = conjunction(comparison("magazine_ammo_value", "equal_to", "fixed_zero"),
                             comparison("common_simulation_time_value", "greater_than_equal_to", "magazine_reload_ready_value"))
    actions = [memory_change("ammo", [("assign", "magazine_capacity_value")], reload_due),
               {"action_type": "change_buff_memory_unit_value", "unit_variable": "selected_target", "new_unit_value": {"unit_type": "none"}},
               {"constraint": ready, "action_type": "use_unit_operators_on_units_in_radius_of_unit",
                "radius_origin_unit": {"unit_type": "current_spawner"}, "radius_value": "heavy_torpedo_range_value",
                "max_target_count_value": "fixed_one", "include_radius_origin_unit": False,
                "include_y_axis_in_radius_check": True,
                "target_sort": {"sort_steps": [{"sort_type": "distance_to_unit", "sort_order": "ascending",
                                                 "distance_reference_unit": {"unit_type": "current_spawner"}}]},
                "operators_constraint": {"constraint_type": "unit_passes_target_filter", "unit": {"unit_type": "operand_destination"},
                                         "target_filter_id": "heavy_torpedo_target_filter"},
                "operators": [{"operator_type": "change_buff_memory_unit_value", "unit_variable": "selected_target",
                               "new_unit_value": {"unit_type": "operand_destination"}}]}]
    spawn = copy.deepcopy(normal_buff["time_actions"][0]["action_group"]["actions"][0])
    spawn["constraint"] = conjunction(copy.deepcopy(ready), copy.deepcopy(target_ok))
    spawn["position_operators"][0]["torpedo_target_unit"] = selected
    assert spawn["position_operators"][0]["operator_type"] == "create_torpedo"
    actions += [copy.deepcopy(spawn), copy.deepcopy(spawn),
                memory_change("ammo", [("subtract", "magazine_pair_count_value")], conjunction(copy.deepcopy(ready), copy.deepcopy(target_ok))),
                memory_change("next_pair_ready", [("assign", "common_simulation_time_value"), ("add", "magazine_pair_interval_value")], target_ok),
                memory_change("reload_ready", [("assign", "common_simulation_time_value"), ("add", "magazine_reload_duration_value")],
                              conjunction(copy.deepcopy(target_ok), comparison("magazine_ammo_value", "equal_to", "fixed_zero")))]
    buff = {"version": 0, "stacking_limit": copy.deepcopy(permanent_buff["stacking_limit"]),
            "stacking_ownership_type": permanent_buff["stacking_ownership_type"],
            "restart_other_stacked_buffs_when_started": False,
            "trigger_event_actions": [{"trigger_event_type": "on_buff_started", "action_group": {"actions": [
                memory_change("ammo", [("assign", "magazine_capacity_value")]),
                memory_change("next_pair_ready", [("assign", "fixed_zero")]),
                memory_change("reload_ready", [("assign", "fixed_zero")]) ]}}],
            "time_actions": [{"first_action_delay_time_value": "fixed_zero", "execution_interval_value": "magazine_poll_interval_value",
                              "action_group": {"actions": actions}}],
            "gui": {"hud_icon": normal["gui"]["hud_icon"], "name": IDENTITY + ".name", "visibility_scope": "positive",
                    "tooltip_line_groups": [{"lines": [{"rendering_type": "single_value", "label_text": IDENTITY + ".ammo_label",
                                                        "value_id": "magazine_ammo_value"}]}]}}
    assert "active_actions" not in ability and len(buff["time_actions"]) == 1
    assert "execution_interval_count_value" not in buff["time_actions"][0]
    assert not any(k.startswith("make_dead_on_") for k in buff)
    assert buff["stacking_limit"]["stacking_limit_met_behavior"] == "preserve_existing_buff"
    staged = {IDENTITY + ".ability": ability, IDENTITY + ".buff": buff,
              IDENTITY + ".action_data_source": ads, PROJECTILE + ".unit": projectile}
    schema_map = {".ability": "ability-schema.json", ".buff": "buff-schema.json", ".action_data_source": "action-data-source-schema.json", ".unit": "unit-schema.json"}
    for name, value in staged.items():
        jsonschema.Draft7Validator(read(sdk / "json_schemas" / schema_map[Path(name).suffix])).validate(value)
    declared_values = {x["action_value_id"] for x in ads["action_values"]} | global_ids
    declared_filters = {x["target_filter_id"] for x in ads["target_filters"]}
    def walk(d, key=""):
        if isinstance(d, dict):
            for k, v in d.items():
                if k in ["float_variable", "memory_float_variable_id"]:
                    assert v in variables, (k, v)
                if k in ["unit_variable", "memory_unit_variable_id"]:
                    assert v == "selected_target", (k, v)
                if k in ["operand_value", "value_a", "value_b", "execution_interval_value", "first_action_delay_time_value", "radius_value", "max_target_count_value", "value_id"]:
                    assert v in declared_values, (k, v)
                if k == "target_filter_id":
                    assert v in declared_filters, v
                walk(v, k)
        elif isinstance(d, list):
            for v in d:
                walk(v, key)
    for val in [ability, buff, ads]:
        walk(val)
    spawn_actions = [x for x in actions if x.get("action_type") == "use_position_operators_on_single_position"]
    assert len(spawn_actions) == 2
    debit = [x for x in actions if x.get("float_variable") == "ammo" and x["math_operators"][0]["operator_type"] == "subtract"]
    assert len(debit) == 1 and debit[0]["constraint"] == spawn_actions[0]["constraint"] == spawn_actions[1]["constraint"]
    for name, value in staged.items():
        write(out / "entities" / name, value)
    model = model_checks()
    write(out / "offline-state-model.json", model)
    write(out / "integration-recipe.json", {"status": "PASSIVE PER-BUFF MEMORY CANDIDATE; runtime NOT RUN",
          "ability_to_add": IDENTITY, "ability_to_remove": "expanse03_torpedo_cycle",
          "mutually_exclusive_normal_magazine_modes": ["expanse03_torpedo_cycle", IDENTITY],
          "manifest_ids": {"ability": [IDENTITY], "buff": [IDENTITY], "action_data_source": [IDENTITY], "unit": [PROJECTILE]},
          "launch_positions": "Replace ability_positions with B/main's verified pair; untouched stock Ogrov reference positions retained here",
          "normal_ammo_capacity": 8, "rounds_per_successful_pair": 2, "pair_interval": 10, "reload_after_last_pair": 120,
          "state_location": "per_buff_memory_declaration: ammo,next_pair_ready,reload_ready floats and selected_target unit",
          "target_policy": "Nearest detected eligible enemy in same gravity well within200000; independent of current manual attack target/order",
          "target_loss_policy": "No valid selection means no create_torpedo and no ammo debit; expired next-pair deadline retained, ready to resume without catch-up salvos",
          "poll_interval_seconds": 0.25, "timer_clock": "common_simulation_time_value; absolute deadlines",
          "permission_guards": ["is_fully_built", "can_use_weapons", "can_use_missile_weapons"],
          "no_active_actions_or_move_operators": True,
          "localization_additions": {IDENTITY + ".name": "Heavy torpedo magazine (experimental)",
             IDENTITY + ".description": "Autonomous paired launches from an eight-round magazine. Ten seconds between pairs;120-second reload only when depleted. Remaining rounds are held in buff memory. Save/reload behavior is unverified.",
             IDENTITY + ".ammo_label": "Torpedoes remaining"},
          "unchanged_dependencies": "expanse03_heavy_torpedo.unit matches filtered candidate; same inherited projectile skin and Ogrov muzzle alias",
          "runtime_gates": ["Actual four-pair timing and120-second reload;0.25-second polling may quantize first acquisition",
             "Unit-memory selector and operator filtering/order; no installed unit-memory-write example found",
             "Remaining ammo survives target loss, stop/move/new attack orders; autonomous target can differ from attack order",
             "Buff memory serialization, simulation-clock restoration and on_buff_started behavior across save/reload",
             "Passive buff lifetime across disable/death/ownership changes and no unintended free magazine resets",
             "PDC movement/rotation/fire continues; missile disable/cripple rules need explicit verification",
             "Creation failure cannot currently be observed before ammo debit; test engine limits/invalid target races",
             "Nearest-target scans at4Hz per ship:1/6/30-ship performance",
             "Ability range still does not guarantee vanilla navigation standoff"],
          "input_evidence": evidence})
    write(out / "offline-validation.json", {"status": "PASS: schema, structural/state-reference checks and intended-state model only",
          "runtime": "NOT RUN", "pinned_schema_count": len(snapshot["files"]), "schema_validated_files": list(staged),
          "explicit_checks": ["No active_actions/channel or movement operators", "Infinite passive timer; no finite-volley completion death",
             "Eight rounds stored in buff memory", "Two create operators and one guarded debit2", "No target means no ammo debit",
             "Reload guard requires depleted ammo and expired120-second deadline", "All memory/action-value/filter IDs resolve",
             "Preserve-existing stacking and no restart-on-reapplication", "Filtered timed candidate remains unchanged"],
          "unit_memory_write_status": "Current schema supports it; no installed explicit example found; runtime NOT RUN",
          "save_serialization": "NOT RUN", "state_model": model,
          "output_hashes": {p.name: digest(p) for p in sorted((out / "entities").iterdir())}})
    print(f"PASS: four passive candidate schemas and intended-state tests; no game or save test. {out}")


if __name__ == "__main__":
    main()
