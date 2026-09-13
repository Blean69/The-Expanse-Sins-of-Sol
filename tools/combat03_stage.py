"""Stage private 0.3 railgun and timed torpedo candidates without installation.

The timed ability has an uninterrupted schedule, not a proven persistent
magazine. Runtime gates are emitted with the recipe. Main owns unit/skin
integration, launch points, manifests, package labels and runtime acceptance.
"""
import argparse
import copy
import hashlib
import json
import os
from pathlib import Path

import jsonschema

ROOT = Path(__file__).resolve().parents[1]
PIN = "8e061033afe53b1393eaefd56617a3fd041eeb5f"
PROJECTILE_ID = "expanse03_heavy_torpedo"
NORMAL_ID = "expanse03_torpedo_cycle"
HERO_ID = "expanse03_hero_torpedo_salvo"
RAIL_ID = "expanse03_hero_railgun"


def read(path):
    if not path.is_file():
        raise SystemExit(f"BLOCKED: missing local dependency: {path}; no substitute downloaded")
    return json.loads(path.read_text(encoding="utf-8-sig"))


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def write(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2) + "\n")


def differences(a, b, p=""):
    if isinstance(a, dict) and isinstance(b, dict):
        return [x for k in sorted(a.keys() | b.keys()) for x in
                ([p + "/" + k] if k not in a or k not in b else differences(a[k], b[k], p + "/" + k))]
    if isinstance(a, list) and isinstance(b, list) and len(a) == len(b):
        return [x for i, (av, bv) in enumerate(zip(a, b)) for x in differences(av, bv, p + "/" + str(i))]
    return [] if a == b else [p]


def strings(d, p=""):
    if isinstance(d, dict):
        for k, v in d.items():
            yield from strings(v, p + "/" + k)
    elif isinstance(d, list):
        for i, v in enumerate(d):
            yield from strings(v, p + "/" + str(i))
    elif isinstance(d, str):
        yield p, d


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--source-root", type=Path, required=True)
    ap.add_argument("--output", type=Path, default=ROOT / "build/combat03-a")
    args = ap.parse_args()
    for k in ["SINS2_GAME", "SINS2_SDK"]:
        if not os.environ.get(k):
            raise SystemExit(f"BLOCKED: set {k} to the recorded local installation")
    game, sdk = [Path(os.environ[k]).resolve() for k in ["SINS2_GAME", "SINS2_SDK"]]
    source, out = args.source_root.resolve(), args.output.resolve()
    if not out.is_relative_to(ROOT / "build") or out == ROOT / "build" or out.exists():
        raise SystemExit("Use a fresh separate output below this checkout's build/; existing outputs are read-only")
    if any(out.is_relative_to(x) for x in [game, sdk, source / "assets"]):
        raise SystemExit("Shared input paths are read-only")
    snapshot = read(source / "audit/schema-comparison.json")
    assert snapshot["official_commit"] == PIN
    for record in snapshot["files"]:
        path = sdk / record["path"]
        if not path.is_file():
            raise SystemExit(f"BLOCKED: missing pinned SDK schema: {path}")
        b = path.read_bytes()
        assert hashlib.sha1(b"blob " + str(len(b)).encode() + b"\0" + b).hexdigest() == record["official_git_blob"], path
    old_hashes = read(source / "audit/installed-file-hashes.json")
    observed = {}

    def base(relative):
        path = game / relative
        value = read(path)
        digest = sha(path)
        if relative in old_hashes:
            assert digest == old_hashes[relative]["sha256"], f"Installed drift: {relative}"
        observed[relative] = {"sha256": digest, "matches_historical_pin": True if relative in old_hashes else None,
                              "note": "Historical pin checked" if relative in old_hashes else "Newly inspected dependency; recorded without replacing historical snapshot"}
        return value

    torpedo = base("entities/trader_torpedo_cruiser_torpedo.unit")
    ogrov_weapon = base("entities/trader_torpedo_cruiser_torpedo.weapon")
    ogrov_skin = base("entities/trader_torpedo_cruiser.unit_skin")
    projectile_skin = base("entities/trader_torpedo_cruiser_torpedo.unit_skin")
    ability_source = base("entities/trader_torpedo_cruiser_heavy_torpedo.ability")
    buff_source = base("entities/trader_torpedo_cruiser_heavy_torpedo_on_self.buff")
    ads_source = base("entities/trader_torpedo_cruiser_heavy_torpedo.action_data_source")
    charged = base("entities/vasari_starbase_charged_salvo.ability")
    charged_buff = base("entities/vasari_starbase_charged_salvo_on_self.buff")
    charged_ads = base("entities/vasari_starbase_charged_salvo.action_data_source")
    phase_tunneling = base("entities/vasari_loyalist_titan_phase_tunneling.action_data_source")
    rail_source = base("entities/trader_rebel_titan_rail_gun.weapon")
    rail_skin = base("entities/trader_rebel_titan.unit_skin")
    cobalt = base("entities/trader_light_frigate.unit")
    cobalt_weapon = base("entities/trader_light_frigate_medium_autocannon.weapon")
    garda = base("entities/trader_antifighter_frigate.unit")
    harcka = base("entities/trader_antiarmor_frigate.unit")
    kodiak = base("entities/trader_heavy_cruiser.unit")
    kol = base("entities/trader_battle_capital_ship.unit")
    group_doc = base("uniforms/attack_target_type_group.uniforms")
    filter_doc = base("uniforms/target_filter.uniforms")
    action_uniforms = base("uniforms/action.uniforms")
    gravity = base("entities/gravity_well.unit")
    neutron = base("entities/neutron_star.unit")
    groups = list(dict.fromkeys(cobalt_weapon["attack_target_type_groups"] + ["defense_starbase_titan", "defense_civilian"]))
    group_map = {x["unit_attack_target_type_group_id"]: x["unit_attack_target_type_group"]["types"] for x in group_doc["attack_target_type_groups"]}
    assert all(x in group_map for x in groups)
    filters = {x["target_filter_id"]: x["target_filter"] for x in filter_doc["common_target_filters"]}
    same_well = phase_tunneling["target_filters"][0]["target_filter"]["constraints"][0]["constraint"]
    assert same_well == {"constraint_type": "is_in_current_gravity_well"}
    private_projectile = copy.deepcopy(torpedo)
    private_projectile["ai"]["attack_target_type_groups"] = groups
    assert private_projectile["target_filter_unit_type"] == "torpedo"
    assert private_projectile["ai_attack_target"]["attack_target_type"] == "torpedo" and "torpedo" in private_projectile
    assert private_projectile["skin_groups"] == torpedo["skin_groups"]
    assert private_projectile["health"] == torpedo["health"]
    assert private_projectile["physics"] == torpedo["physics"]

    rail = copy.deepcopy(rail_source)
    rail.update(name="expanse03.weapon_name.railgun", damage=2500.0,
                uniforms_target_filter_id="common_weapon", attack_target_type_groups=groups)
    assert rail["cooldown_duration"] == 10.0 and rail["penetration"] == 1000.0
    assert differences(rail_source, rail) == ["/attack_target_type_groups", "/damage", "/name", "/uniforms_target_filter_id"]
    staged = {PROJECTILE_ID + ".unit": private_projectile, RAIL_ID + ".weapon": rail}
    localization = {"expanse03.weapon_name.railgun": "Keel-mounted railgun"}
    recipe_abilities = []
    generated_pairs = []

    for identity, per_interval, count, interval, hero in [(NORMAL_ID, 2, 4, 10.0, False), (HERO_ID, 8, 1, 0.0, True)]:
        buff_id = identity + "_on_self"
        ability = copy.deepcopy(ability_source)
        ability["action_data_source"] = identity
        ability["level_source"] = "fixed_level_0"
        ability.pop("level_prerequisites")
        active = ability["active_actions"]
        active.pop("antimatter_cost")
        active["cooldown_reset_type"] = "on_spawned_buff_made_dead"
        active["stop_use_type"] = charged["active_actions"]["stop_use_type"]
        active["watched_buff"] = buff_id
        active["channeling_will_disable_weapons"] = False
        active["actions"]["actions"][0]["operators"][0]["buff"] = buff_id
        if hero:
            active.pop("auto_cast")
        else:
            active["auto_cast"].pop("caster_constraint")
            active["auto_cast"]["type"] = "pick_target_within_current_gravity_well"
        ability["gui"]["name"] = identity + ".name"
        ability["gui"]["description"] = identity + ".description"
        localization[identity + ".name"] = "Overwhelming torpedo salvo" if hero else "Heavy torpedo cycle (experimental)"
        localization[identity + ".description"] = ("Fire eight heavy torpedoes from an independent salvo reserve. Experimental; 120-second ability cooldown." if hero else
            "Four paired heavy-torpedo launches at 0, 10, 20 and 30 seconds; then a 120-second reload. Experimental: interruption, remaining ammunition and save/reload behavior are unverified.")
        buff = copy.deepcopy(buff_source)
        buff["make_dead_on_source_ability_released"] = charged_buff["make_dead_on_source_ability_released"]
        buff["make_dead_on_current_spawner_ownership_changed_from_buff_ownership"] = charged_buff["make_dead_on_current_spawner_ownership_changed_from_buff_ownership"]
        timer = buff["time_actions"][0]
        timer.update(executions_per_interval_value="combat03_torpedoes_per_interval_value",
                     execution_interval_count_value="combat03_interval_count_value",
                     execution_interval_value="combat03_interval_value",
                     first_action_delay_time_value="combat03_first_delay_value")
        # Recheck the original target's eligibility for every timed pair. Without
        # this, a cast-time same-well check would not guard later intervals after
        # the target changes gravity wells. Skipped intervals still need runtime
        # testing for their effect on magazine accounting.
        timer["action_group"]["actions"][0]["constraint"] = copy.deepcopy(
            active["actions"]["actions"][0]["constraint"])
        create = timer["action_group"]["actions"][0]["position_operators"][0]
        assert create["operator_type"] == "create_torpedo"
        create["torpedo_to_create"] = PROJECTILE_ID
        ads = copy.deepcopy(ads_source)
        for record in ads["target_filters"]:
            tf = record["target_filter"]
            if record["target_filter_id"] in ["heavy_torpedo_target_filter", "heavy_torpedo_auto_cast_low_priority_target_filter"]:
                tf["unit_types"] = list(dict.fromkeys(tf["unit_types"] + ["corvette"]))
            tf.setdefault("constraints", []).append(copy.deepcopy(same_well))
        values = {x["action_value_id"]: x["action_value"] for x in ads["action_values"]}
        replacements = {"heavy_torpedo_antimatter_cost_value": 0.0,
                        "heavy_torpedo_cooldown_time_value": 120.0,
                        "heavy_torpedo_damage_value": 750.0,
                        "heavy_torpedo_range_value": 200000.0,
                        "heavy_torpedo_torpedo_count_value": 8.0,
                        "heavy_torpedo_torpedo_lifetime_value": 240.0}
        for key, value in replacements.items():
            values[key]["values"] = [value]
        for key, value in {"combat03_torpedoes_per_interval_value": per_interval,
                           "combat03_interval_count_value": count,
                           "combat03_interval_value": interval,
                           "combat03_first_delay_value": 0.0}.items():
            ads["action_values"].append({"action_value_id": key, "action_value": {"values": [float(value)]}})
        staged[identity + ".ability"] = ability
        staged[buff_id + ".buff"] = buff
        staged[identity + ".action_data_source"] = ads
        action_ids = {x["action_value_id"] for x in ads["action_values"]}
        target_ids = {x["target_filter_id"] for x in ads["target_filters"]}
        for doc in [ability, buff]:
            for pointer, value in strings(doc):
                if value.endswith("_value") and not pointer.endswith("/rendering_type"):
                    assert value in action_ids, (identity, pointer, value)
                if value.endswith("_target_filter") and not pointer.endswith("/constraint_type"):
                    assert value in target_ids, (identity, pointer, value)
        pair_times = [i * interval for i in range(count) for _ in range(per_interval)]
        assert len(pair_times) == 8
        if not hero:
            assert pair_times == [0, 0, 10, 10, 20, 20, 30, 30]
        generated_pairs.append({"ability": identity, "nominal_torpedo_spawn_times": pair_times,
                                "expected_cooldown_start_if_buff_dies_at_last_interval": max(pair_times),
                                "expected_next_ready_time": max(pair_times) + 120,
                                "runtime_status": "NOT RUN; schedule calculation only"})
        recipe_abilities.append({"ability_id": identity, "unit_scope": "hero only" if hero else "ordinary corvette and hero",
                                 "ability_positions_replace_required": True,
                                 "reference_positions_source": "entities/trader_torpedo_cruiser_heavy_torpedo.ability#/ability_positions",
                                 "launchpoint_hook": "ability_positions; next_sequential position selection; real aperture positions supplied by B/main",
                                 "auto_cast": "manual only (auto_cast absent)" if hero else "always; target within same gravity well, no weapon_has_target prerequisite",
                                 "cooldown_budget": "own private ability/buff; independent from other ability ID"})

    schema_names = {".unit": "unit-schema.json", ".weapon": "weapon-schema.json", ".ability": "ability-schema.json",
                    ".buff": "buff-schema.json", ".action_data_source": "action-data-source-schema.json"}
    for filename, value in staged.items():
        jsonschema.Draft7Validator(read(sdk / "json_schemas" / schema_names[Path(filename).suffix])).validate(value)
    rail_alias_ids = {v for k, v in rail["effects"].items() if k.endswith("_effect")}
    rail_aliases = [x for x in rail_skin["skin_stages"][0]["effects"]["effect_alias_bindings"] if x["alias_name"] in rail_alias_ids]
    assert len(rail_aliases) == len(rail_alias_ids) == 4
    torpedo_alias = ogrov_weapon["effects"]["muzzle_effect"]
    torpedo_aliases = [x for x in ogrov_skin["skin_stages"][0]["effects"]["effect_alias_bindings"] if x["alias_name"] == torpedo_alias]
    assert len(torpedo_aliases) == 1
    direct_effect_files = {}
    for alias in rail_aliases + torpedo_aliases:
        binding = alias["alias_binding"]
        if "particle_effect" in binding:
            path = game / "effects" / (binding["particle_effect"] + ".particle_effect")
            base(str(path.relative_to(game)))
            direct_effect_files[str(path.relative_to(game))] = sha(path)
        for sound in binding.get("sounds", []):
            for suffix in [".sound", ".ogg"]:
                path = game / "sounds" / (sound + suffix)
                if not path.is_file():
                    raise SystemExit(f"BLOCKED: unresolved inherited effect sound {path}")
                direct_effect_files[str(path.relative_to(game))] = sha(path)
    benchmark = []
    for identity, unit in [("Cobalt", cobalt), ("Garda", garda), ("Harcka", harcka), ("Kodiak", kodiak), ("Kol level 1", kol)]:
        h = unit["health"]; level = h["levels"][0]
        factor = 1 + max(h["durability"] - rail["penetration"], 0) / 100
        shields = level.get("max_shield_points", 0)
        armor = level["max_armor_points"] * (1 + level["armor_strength"] / 100)
        hull = level["max_hull_points"]
        benchmark.append({"unit": identity, "durability": h["durability"], "armor_strength": level["armor_strength"],
                          "armor": level["max_armor_points"], "hull": hull, "shields": shields,
                          "ideal_raw_damage_requirement": (shields + armor + hull) * factor,
                          "rail_one_shot_under_simplified_unbuffed_model": 2500 >= (shields + armor + hull) * factor})
    assert benchmark[0]["ideal_raw_damage_requirement"] == 1987.5
    assert benchmark[0]["rail_one_shot_under_simplified_unbuffed_model"]
    for filename, value in staged.items():
        write(out / "entities" / filename, value)
    blockers = [
        "Replace both ability_positions arrays with verified real launch apertures before packaging; emitted positions are unchanged stock Ogrov reference points.",
        "Observed schemas/definitions support timer fields, not a proven persistent magazine: cancellation, target loss, retargeting and remaining ammunition are unresolved.",
        "cooldown_reset_type=on_spawned_buff_made_dead is current-schema supported but no explicitly set installed example was found; verify buff completion time and next-ready t150.",
        "The watched-buff ability may count as channeling; channeling_will_disable_weapons=false is explicit but not runtime proof of uninterrupted PDCs/navigation.",
        "Ability range is not max_range_weapon_index; no verified ability-based stop-and-fire standoff selection found.",
        "Actual spawn count, per-projectile damage, interception preventing impact, lifetime and same-well filtering require runtime observations.",
        "Hero8 ability has a separate120-second cooldown/reserve and does not consume normal timed-cycle ammo; user-facing cooldown remains provisional."]
    recipe = {"status": "EXPERIMENTAL TIMED ABILITY CANDIDATES; railgun definition schema-ready; runtime NOT RUN",
              "schema_commit": PIN, "unit_ability_integration": recipe_abilities,
              "railgun_weapon_id": RAIL_ID, "railgun_unit_scope": "hero only",
              "railgun_mount": "Main/B supplies one fixed keel-aligned weapon entry and real non_turret_muzzle_positions; no invented mount coordinates emitted",
              "required_skin_effect_alias_bindings": torpedo_aliases + rail_aliases,
              "projectile_id": PROJECTILE_ID, "projectile_skin_inherited": "trader_torpedo_cruiser_torpedo",
              "additive_manifest_ids": {ext.lstrip("."): [Path(f).stem for f in staged if Path(f).suffix == ext] for ext in schema_names},
              "localization_additions": localization, "nominal_schedules": generated_pairs,
              "normal_torpedo_damage_per_created_entity": 750.0, "normal_complete_cycle_nominal_raw_damage": 6000.0,
              "normal_complete_cycle_nominal_raw_dps_over_150_seconds": 40.0,
              "hero_salvo_nominal_raw_damage": 6000.0, "railgun_nominal_raw_dps": 250.0,
              "torpedo_range": 200000.0, "torpedo_lifetime": 240.0, "torpedo_speed": torpedo["physics"]["max_linear_speed"],
              "railgun_target_acquired_duration_required_to_fire": rail["target_acquired_duration_required_to_fire"],
              "weapon_burst_magazine_substitute_added": False, "ordinary_torpedo_weapon_added": False,
              "railgun_benchmarks": benchmark, "required_runtime_gates": blockers,
              "installed_input_hashes": observed, "direct_effect_dependencies": direct_effect_files}
    write(out / "integration-recipe.json", recipe)
    weapon_schema = read(sdk / "json_schemas/weapon-schema.json")
    ability_schema = read(sdk / "json_schemas/ability-schema.json")
    write(out / "ammo-cadence-evidence.json", {"weapon_properties": list(weapon_schema["properties"]),
          "weapon_magazine_fields_observed": [],
          "ability_fields": {k: ability_schema["properties"]["active_actions"]["properties"][k] for k in ["cooldown_reset_type", "stop_use_type", "watched_buff", "channeling_will_disable_weapons", "max_charge_count"]},
          "time_action_schema": ability_schema["$defs"]["time_action"],
          "charge_examples": ["advent_guardian_cruiser_shield_projection.ability", "advent_battle_psionic_capital_ship_domination.ability"],
          "charge_limit": "max_charge_count is observed, but no verified eight-round magazine with four10-second paired launches then120-second full reload was established from charge mechanics",
          "normal_candidate_source_buff": "trader_torpedo_cruiser_heavy_torpedo_on_self.buff with installed charged-salvo timer keys",
          "same_well_constraint_source": "vasari_loyalist_titan_phase_tunneling.action_data_source#/target_filters/0/target_filter/constraints/0/constraint",
          "source_gravity": {"neutron_star": neutron["gravity_well_fixture"], "neutron_star_spatial": neutron["spatial"], "common_gravity_well": gravity["gravity_well"]},
          "range_inference": "200000 numeric range and240s duration provide margin over a conservatively inferred125000 opposite-edge neutron-star scale; not a universal same-well guarantee under all maps/modifiers/motion",
          "unresolved": blockers})
    write(out / "offline-validation.json", {"result": "PASS for candidate definition schemas and explicit reference checks only", "runtime": "NOT RUN",
          "schema_count": len(snapshot["files"]), "schemas_passed": sorted(staged),
          "private_create_torpedo_chain": "Both buffs point to private torpedo unit -> installed torpedo skin -> installed mesh/effects",
          "normal_schedule_arithmetic": generated_pairs[0], "hero_schedule_arithmetic": generated_pairs[1],
          "railgun_exact_differences": differences(rail_source, rail),
          "private_projectile_exact_differences": differences(torpedo, private_projectile),
          "local_action_value_and_filter_references": "PASS", "same_well_constraint_schema_and_installed_evidence": "PASS",
          "installed_alias_dependencies": "PASS: five aliases and direct particle/sound resources exist",
          "package_readiness": "BLOCKED until real aperture integration and explicit experimental labeling; no complete-magazine or runtime-success claim",
          "output_hashes": {p.name: sha(p) for p in sorted((out / "entities").iterdir())}})
    print(f"PASS: {len(staged)} private candidate definitions /62 pinned schemas. Runtime NOT RUN; launchpoints and magazine behavior gates unresolved. {out}")


if __name__ == "__main__":
    main()
