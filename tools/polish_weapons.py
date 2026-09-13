"""Prepare six private PDC recipes from reviewed rig metadata, without packaging.

Source assets, the game, pinned SDK and existing outputs are read-only. One
weapon definition and one mount entry are specified for each physical gun.
"""
import argparse
import copy
import hashlib
import json
import os
from pathlib import Path
import subprocess

import jsonschema

ROOT = Path(__file__).resolve().parents[1]
PIN = "8e061033afe53b1393eaefd56617a3fd041eeb5f"
NAME_KEY = "expanse.weapon_name.pdc_autocannon"


def read(path):
    if not path.is_file():
        raise SystemExit(f"BLOCKED: missing local dependency: {path}; no substitute downloaded")
    return json.loads(path.read_text(encoding="utf-8-sig"))


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def write(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2) + "\n")


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--source-root", type=Path, required=True)
    p.add_argument("--rig-metadata", type=Path, required=True)
    p.add_argument("--output", type=Path, default=ROOT / "build/polish-a")
    args = p.parse_args()
    for key in ["SINS2_GAME", "SINS2_SDK"]:
        if not os.environ.get(key):
            raise SystemExit(f"BLOCKED: set {key} to the recorded local installation")
    game, sdk = [Path(os.environ[k]).resolve() for k in ["SINS2_GAME", "SINS2_SDK"]]
    source, output = args.source_root.resolve(), args.output.resolve()
    if not output.is_relative_to(ROOT / "build") or output == ROOT / "build":
        raise SystemExit("Output must be a separate directory below this checkout's build/")
    if any(output.is_relative_to(x) for x in [game, sdk, source / "assets"]):
        raise SystemExit("Refusing an output inside a shared read-only input")
    if output.exists():
        raise SystemExit(f"Refusing to overwrite existing output: {output}")
    snapshot = read(source / "audit/schema-comparison.json")
    assert snapshot["official_commit"] == PIN
    for record in snapshot["files"]:
        path = sdk / record["path"]
        if not path.is_file():
            raise SystemExit(f"BLOCKED: missing pinned SDK schema {path}")
        data = path.read_bytes()
        blob = hashlib.sha1(b"blob " + str(len(data)).encode() + b"\0" + data).hexdigest()
        assert blob == record["official_git_blob"], f"Pinned schema drift: {path}"
    hashes = read(source / "audit/installed-file-hashes.json")
    checked = {}

    def base(relative):
        path = game / relative
        data = read(path)
        assert sha(path) == hashes[relative]["sha256"], f"Installed definition drift: {path}"
        checked[relative] = sha(path)
        return data

    vanilla = base("entities/trader_antifighter_frigate_point_defense_autocannon.weapon")
    skin = base("entities/trader_antifighter_frigate.unit_skin")
    cobalt = base("entities/trader_light_frigate.unit")
    cobalt_weapon_id = cobalt["weapons"]["weapons"][0]["weapon"]
    cobalt_weapon = base(f"entities/{cobalt_weapon_id}.weapon")
    group_data = base("uniforms/attack_target_type_group.uniforms")
    filter_data = base("uniforms/target_filter.uniforms")
    groups = list(dict.fromkeys(["torpedo_strikecraft"] + cobalt_weapon["attack_target_type_groups"]))
    group_map = {x["unit_attack_target_type_group_id"]: x["unit_attack_target_type_group"]["types"]
                 for x in group_data["attack_target_type_groups"]}
    assert all(x in group_map for x in groups)
    filters = {x["target_filter_id"]: x["target_filter"] for x in filter_data["common_target_filters"]}
    target_filter = filters[vanilla["uniforms_target_filter_id"]]
    assert target_filter["ownerships"] == ["enemy"]
    assert set(["torpedo", "corvette", "frigate"]) <= set(target_filter["unit_types"])
    localization = read(game / "localized_text/en.localized_text")
    assert NAME_KEY not in localization, "Unexpected namespace collision with vanilla localization"
    rigs_document = read(args.rig_metadata)
    rigs = rigs_document["rigs"]
    assert len(rigs) == 6 and {r["index"] for r in rigs} == set(range(6))

    template = copy.deepcopy(vanilla)
    template.update(name=NAME_KEY, damage=28.0, cooldown_duration=0.25,
                    penetration=0.0, range=2500.0, yaw_speed=360.0, pitch_speed=360.0,
                    attack_target_type_groups=groups)
    template["effects"]["burst_pattern"] = [0.0, 0.04, 0.08, 0.12, 0.16, 0.20]
    assert "burst_pattern" not in template
    assert template["acquire_target_logic"] == "best_target_in_range"
    assert template["always_check_is_dead_soon"] is True
    assert max(template["effects"]["burst_pattern"]) < template["cooldown_duration"]
    schema = read(sdk / "json_schemas/weapon-schema.json")
    validator = jsonschema.Draft7Validator(schema)
    expected_top_differences = {"name", "damage", "cooldown_duration", "range", "yaw_speed", "pitch_speed", "attack_target_type_groups", "effects", "turret"}
    weapons, mounts, skin_aliases = {}, [], []
    for rig in sorted(rigs, key=lambda r: r["index"]):
        i = rig["index"]
        weapon_id = f"expanse_polish_pdc_{i}"
        weapon = copy.deepcopy(template)
        weapon["turret"] = copy.deepcopy(rig["turret_override"])
        assert set(weapon["turret"]) == set(vanilla["turret"]), "Unexpected rig turret fields"
        assert weapon["turret"]["type"] == "biaxial"
        assert len(weapon["turret"]["muzzle_positions"]) == 1, "One observed muzzle per physical assembly required"
        assert weapon["turret"]["biaxial_base_mesh"] == f"expanse_pdc_{i}_base"
        assert weapon["turret"]["biaxial_barrel_mesh"] == f"expanse_pdc_{i}_barrel"
        validator.validate(weapon)
        changed = {k for k in vanilla.keys() | weapon.keys() if vanilla.get(k) != weapon.get(k)}
        assert changed == expected_top_differences, changed
        effect_changed = {k for k in vanilla["effects"].keys() | weapon["effects"].keys()
                          if vanilla["effects"].get(k) != weapon["effects"].get(k)}
        assert effect_changed == {"burst_pattern"}
        mount = copy.deepcopy(rig["mount"])
        mount["weapon"] = weapon_id
        mounts.append(mount)
        skin_aliases.extend(copy.deepcopy(rig["skin_alias_map"]))
        weapons[weapon_id] = weapon
    assert len({m["weapon"] for m in mounts}) == 6
    assert len({m["mesh_point"] for m in mounts}) == 6, "Independent mesh mounts required"
    aliases = {x["mesh_alias_name"] for x in skin_aliases}
    assert len(aliases) == 12
    for weapon in weapons.values():
        assert {weapon["turret"]["biaxial_base_mesh"], weapon["turret"]["biaxial_barrel_mesh"]} <= aliases
    effect_names = {v for k, v in template["effects"].items() if k.endswith("_effect")}
    effect_bindings = [x for x in skin["skin_stages"][0]["effects"]["effect_alias_bindings"] if x["alias_name"] in effect_names]
    assert len(effect_bindings) == len(effect_names) == 4

    health = cobalt["health"]
    level = health["levels"][0]
    durability_factor = 1 + health["durability"] / 100
    raw_required = (level["max_armor_points"] * (1 + level["armor_strength"] / 100) + level["max_hull_points"]) * durability_factor
    per_gun = template["damage"] / template["cooldown_duration"]
    nominal = [{"overlapping_guns": n, "nominal_raw_dps": n * per_gun,
                "ideal_cobalt_time_seconds": raw_required / (n * per_gun)} for n in range(1, 7)]
    census = []
    for path in sorted((game / "entities").glob("*.weapon")):
        value = read(path)
        if "burst_pattern" in value:
            census.append({"file": str(path.relative_to(game)), "sha256": sha(path),
                           "firing_type": value.get("firing", {}).get("firing_type"),
                           "burst_pattern": value["burst_pattern"]})
    commit = subprocess.check_output(["git", "-C", str(source), "rev-parse", "HEAD"], text=True).strip()
    for weapon_id, weapon in weapons.items():
        write(output / "entities" / (weapon_id + ".weapon"), weapon)
    write(output / "input-rig-metadata.json", rigs_document)
    recipe = {
        "format": "Integrator metadata; not game fields or a complete mod", "source_commit": commit,
        "pinned_sdk_commit": PIN, "status": "SCHEMA-VALID WEAPON RECIPES; runtime NOT RUN; mesh checks belong to Worker B/integrator",
        "weapon_ids": list(weapons), "proposed_unit_mounts": mounts,
        "required_skin_alias_map": skin_aliases, "required_effect_alias_bindings": effect_bindings,
        "required_additive_localization": {NAME_KEY: "PDC autocannon"},
        "existing_fields_changed": sorted(expected_top_differences),
        "budget": {"physical_pdcs": 6, "weapon_entries_per_physical_pdc": 1,
                   "damage_per_nominal_cycle": 28.0, "nominal_cycles_per_second_per_gun": 4,
                   "nominal_raw_dps_per_gun": per_gun, "penetration": 0,
                   "visual_effect_pulses_per_cycle": 6, "nominal_visual_pulses_per_second_per_gun": 24,
                   "nominal_visual_pulses_per_second_six_guns": 144,
                   "visual_pulses_are_not_damage_multiplier_or_canonical_tv_rpm": True,
                   "cobalt_raw_damage_requirement_assuming_documented_model": raw_required,
                   "overlap_table": nominal, "benchmark_selected_overlapping_guns": 3},
        "groups": {x: group_map[x] for x in groups}, "target_filter": target_filter,
        "runtime_uncertainties": ["Damage cycle semantics and visual-burst cadence",
            "Interception preemption while an explicit ship attack order remains active",
            "Real coverage, turret pitch/yaw sign, self-occlusion and muzzle placement",
            "Engine tracking/cooldown update granularity and 1/6/30-ship performance",
            "Torpedo default durability and actual prevention of impact damage after interception"],
        "top_level_burst_added": False, "torpedo_weapons_added": False,
        "input_hashes": {**checked, "rig_metadata": sha(args.rig_metadata)},
        "mesh_validation": "NOT PERFORMED by this recipe generator; do not infer asset checks passed from schema success"}
    write(output / "integration-recipe.json", recipe)
    write(output / "burst-field-evidence.json", {"top_level_property_schema": schema["properties"]["burst_pattern"],
          "effects_property_schema": schema["properties"]["effects"]["properties"]["burst_pattern"],
          "stock_garda_top_level_present": "burst_pattern" in vanilla,
          "stock_garda_effects_pattern": vanilla["effects"]["burst_pattern"],
          "installed_top_level_examples": census,
          "semantics": "Distinct observed fields; schemas do not document damage-per-burst semantics. No multiplier inferred."})
    write(output / "offline-validation.json", {"status": "PASS: weapon recipe checks only", "runtime": "NOT RUN",
          "pinned_schema_count": len(snapshot["files"]), "installed_input_count": len(checked),
          "weapon_schemas_passed": list(weapons), "checked_exact_differences": True,
          "one_weapon_budget_per_mount": True, "unique_mount_count": len(mounts), "unique_alias_count": len(aliases),
          "mesh_dependent_checks": "NOT PERFORMED; separate Worker B/integrator gate required",
          "output_hashes": {p.name: sha(p) for p in sorted((output / "entities").iterdir())}})
    print(f"PASS: six weapon recipes, 62 pinned schemas, 6 unique mounts/12 aliases. Mesh checks not performed. Runtime NOT RUN. {output}")


if __name__ == "__main__":
    main()
