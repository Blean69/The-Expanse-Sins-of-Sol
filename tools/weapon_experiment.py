"""Stage stock-mount weapon experiments; never build/install a baseline.

Requires the recorded installation, pinned SDK schemas, and prior combat
candidates. Shared inputs are read-only. The integrator authors unit overrides
and manifests using the emitted integration-spec.json (which is not game data).
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


def read(path):
    return json.loads(path.read_text(encoding="utf-8-sig"))


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def require(path, label):
    if not path.is_file():
        raise SystemExit(f"BLOCKED: missing {label}: {path}; no substitute or download attempted")
    return path


def write(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2) + "\n")


def pointers(a, b, pointer=""):
    if isinstance(a, dict) and isinstance(b, dict):
        return [p for k in sorted(a.keys() | b.keys()) for p in
                ([pointer + "/" + k] if k not in a or k not in b else pointers(a[k], b[k], pointer + "/" + k))]
    if isinstance(a, list) and isinstance(b, list) and len(a) == len(b):
        return [p for i, (x, y) in enumerate(zip(a, b)) for p in pointers(x, y, pointer + "/" + str(i))]
    return [] if a == b else [pointer]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source-root", required=True, type=Path)
    parser.add_argument("--output", type=Path, default=ROOT / "build/worker-a")
    args = parser.parse_args()
    for variable in ("SINS2_GAME", "SINS2_SDK"):
        if not os.environ.get(variable):
            raise SystemExit(f"BLOCKED: set {variable} explicitly to the recorded local installation")
    game, sdk = (Path(os.environ[key]).resolve() for key in ("SINS2_GAME", "SINS2_SDK"))
    source, out = args.source_root.resolve(), args.output.resolve()
    if not out.is_relative_to(ROOT / "build") or out == ROOT / "build":
        raise SystemExit("Output must be a separate directory below this checkout's build/")
    if any(out.is_relative_to(p) for p in (game, sdk, source / "assets", source / "build/combat-candidates")):
        raise SystemExit("Refusing shared input output directory")
    if out.exists():
        raise SystemExit(f"Output already exists: {out}; choose a fresh experimental output directory")

    snapshot = read(require(source / "audit/schema-comparison.json", "pinned schema evidence"))
    assert snapshot["official_commit"] == PIN, "Unexpected pinned schema revision"
    schema_hashes = {}
    for record in snapshot["files"]:
        path = require(sdk / record["path"], "pinned SDK schema")
        data = path.read_bytes()
        blob = hashlib.sha1(b"blob " + str(len(data)).encode() + b"\0" + data).hexdigest()
        assert blob == record["official_git_blob"], f"Pinned SDK drift: {path}"
        schema_hashes[record["path"]] = digest(path)
    installed = read(require(source / "audit/installed-file-hashes.json", "installed hash evidence"))
    checked_inputs = {}
    def base(relative):
        path = require(game / relative, "installed definition")
        actual = digest(path)
        assert relative in installed and installed[relative]["sha256"] == actual, f"Installed snapshot drift: {relative}"
        checked_inputs[relative] = actual
        return read(path)

    stock_pdc = base("entities/trader_antifighter_frigate_point_defense_autocannon.weapon")
    stock_torpedo = base("entities/trader_torpedo_cruiser_torpedo.weapon")
    stock_projectile = base("entities/trader_torpedo_cruiser_torpedo.unit")
    stock_projectile_skin = base("entities/trader_torpedo_cruiser_torpedo.unit_skin")
    garda = base("entities/trader_antifighter_frigate.unit")
    garda_skin = base("entities/trader_antifighter_frigate.unit_skin")
    ogrov = base("entities/trader_torpedo_cruiser.unit")
    ogrov_skin = base("entities/trader_torpedo_cruiser.unit_skin")
    cobalt = base("entities/trader_light_frigate.unit")
    filters = base("uniforms/target_filter.uniforms")
    groups = base("uniforms/attack_target_type_group.uniforms")
    group_map = {x["unit_attack_target_type_group_id"]: x["unit_attack_target_type_group"]["types"]
                 for x in groups["attack_target_type_groups"]}
    selected_groups = ["torpedo_strikecraft", "corvette", "light", "flak"]
    for group in selected_groups:
        assert group in group_map, group
    filter_map = {x["target_filter_id"]: x["target_filter"] for x in filters["common_target_filters"]}
    assert filter_map[stock_pdc["uniforms_target_filter_id"]]["ownerships"] == ["enemy"]
    assert set(["frigate", "corvette", "torpedo"]) <= set(filter_map[stock_pdc["uniforms_target_filter_id"]]["unit_types"])
    assert cobalt["ai_attack_target"]["attack_target_type"] == "light"
    assert stock_projectile["target_filter_unit_type"] == "torpedo"
    assert stock_projectile["ai_attack_target"]["attack_target_type"] == "torpedo"
    assert "torpedo" in stock_projectile

    # Audit all nine existing candidate definitions before reuse. They are never
    # overwritten, and a diverged candidate stops preparation for integrator review.
    candidates = source / "build/combat-candidates/entities"
    rigs = read(require(source / "audit/pdc-rig-candidates.json", "existing rig metadata"))["rigs"]
    expected_torpedo = copy.deepcopy(stock_torpedo)
    expected_torpedo["firing"]["torpedo_firing_definition"]["spawned_unit"] = "mcrn_corvette_torpedo"
    expected_projectile = copy.deepcopy(stock_projectile)
    expected_projectile["skin_groups"][0]["skins"] = ["mcrn_corvette_torpedo"]
    expectations = {"mcrn_corvette_torpedo.weapon": expected_torpedo,
                    "mcrn_corvette_torpedo.unit": expected_projectile,
                    "mcrn_corvette_torpedo.unit_skin": stock_projectile_skin}
    for rig in rigs:
        value = copy.deepcopy(stock_pdc)
        value["attack_target_type_groups"] = selected_groups
        value["turret"].update(biaxial_base_mesh=f"mcrn_pdc_{rig['index']}_base",
                               biaxial_barrel_mesh=f"mcrn_pdc_{rig['index']}_barrel",
                               barrel_position=[0., 0., 0.], muzzle_positions=[rig["muzzle_local"]])
        expectations[f"mcrn_corvette_pdc_{rig['index']}.weapon"] = value
    candidate_audit = {}
    for name, expected in expectations.items():
        path = require(candidates / name, "existing combat candidate")
        assert read(path) == expected, f"Unexpected existing candidate changes: {path}"
        candidate_audit[name] = digest(path)

    pdc = copy.deepcopy(stock_pdc)
    pdc["attack_target_type_groups"] = selected_groups
    pdc_id = "mcrn_exp_stock_dual_pdc"
    staged = {pdc_id + ".weapon": pdc, **{k: v for k, v in expectations.items() if k.startswith("mcrn_corvette_torpedo.")}}
    schemas = {".weapon": "weapon-schema.json", ".unit": "unit-schema.json", ".unit_skin": "unit-skin-schema.json"}
    for name, value in staged.items():
        schema = schemas[Path(name).suffix]
        jsonschema.Draft7Validator(read(sdk / "json_schemas" / schema)).validate(value)
    assert pointers(stock_pdc, pdc) == ["/attack_target_type_groups"]
    assert pointers(stock_torpedo, expected_torpedo) == ["/firing/torpedo_firing_definition/spawned_unit"]
    assert pointers(stock_projectile, expected_projectile) == ["/skin_groups/0/skins/0"]

    pdc_aliases = {v for k, v in pdc["effects"].items() if k.endswith("_effect")}
    garda_bindings = garda_skin["skin_stages"][0]["effects"]["effect_alias_bindings"]
    selected_aliases = [x for x in garda_bindings if x["alias_name"] in pdc_aliases]
    assert len(selected_aliases) == len(pdc_aliases) == 4
    aliases = {x["mesh_alias_name"] for x in garda_skin["skin_stages"][0]["child_mesh_alias_bindings"]["map"]}
    assert {pdc["turret"]["biaxial_base_mesh"], pdc["turret"]["biaxial_barrel_mesh"]} <= aliases
    torpedo_alias = expected_torpedo["effects"]["muzzle_effect"]
    assert torpedo_alias in {x["alias_name"] for x in ogrov_skin["skin_stages"][0]["effects"]["effect_alias_bindings"]}

    # Verify schema-valid proposed unit results in memory. Shared definitions and
    # manifests are intentionally not emitted by this worker.
    proposed_garda, proposed_ogrov = copy.deepcopy(garda), copy.deepcopy(ogrov)
    proposed_garda["weapons"]["weapons"][0]["weapon"] = pdc_id
    proposed_ogrov["weapons"]["weapons"][0]["weapon"] = "mcrn_corvette_torpedo"
    proposed_ogrov["ai"]["attack_target_type_groups_matching_weapon"] = "mcrn_corvette_torpedo"
    for value in (proposed_garda, proposed_ogrov):
        jsonschema.Draft7Validator(read(sdk / "json_schemas/unit-schema.json")).validate(value)
    assert pointers(garda, proposed_garda) == ["/weapons/weapons/0/weapon"]
    assert pointers(ogrov, proposed_ogrov) == ["/ai/attack_target_type_groups_matching_weapon", "/weapons/weapons/0/weapon"]
    assert sum(x["weapon"] == pdc_id for x in proposed_garda["weapons"]["weapons"]) == 1
    assert len(proposed_garda["weapons"]["weapons"]) == len(garda["weapons"]["weapons"]) == 7

    for name, value in staged.items():
        write(out / "entities" / name, value)
    spec = {
        "format": "integrator instructions, NOT game data", "schema_revision": PIN,
        "unit_overrides": {
            "entities/trader_antifighter_frigate.unit": [{"pointer": "/weapons/weapons/0/weapon", "value": pdc_id}],
            "entities/trader_torpedo_cruiser.unit": [
                {"pointer": "/weapons/weapons/0/weapon", "value": "mcrn_corvette_torpedo"},
                {"pointer": "/ai/attack_target_type_groups_matching_weapon", "value": "mcrn_corvette_torpedo"}]},
        "additive_manifest_ids": {"weapon": [pdc_id, "mcrn_corvette_torpedo"], "unit": ["mcrn_corvette_torpedo"], "unit_skin": ["mcrn_corvette_torpedo"]},
        "stock_skin_overrides_required": [], "cobalt_changes": [],
        "representative_garda_mount": proposed_garda["weapons"]["weapons"][0],
        "tachi_pdc_effect_alias_bindings_required": selected_aliases,
        "projectile_chain": [
            "entities/trader_torpedo_cruiser.unit#/weapons/weapons/0/weapon -> entities/mcrn_corvette_torpedo.weapon",
            "entities/mcrn_corvette_torpedo.weapon#/firing/torpedo_firing_definition/spawned_unit -> entities/mcrn_corvette_torpedo.unit",
            "entities/mcrn_corvette_torpedo.unit#/skin_groups/0/skins/0 -> entities/mcrn_corvette_torpedo.unit_skin",
            "entities/mcrn_corvette_torpedo.unit_skin#/skin_stages/0/unit_mesh/mesh -> meshes/trader_torpedo_cruiser_torpedo.mesh"],
        "base_dependency_trace": "audit/reference-edges.csv (baseline repository; downstream vanilla dependencies inherited)",
        "pdc_groups": {k: group_map[k] for k in selected_groups},
        "pdc_filter": filter_map[stock_pdc["uniforms_target_filter_id"]],
        "damage_assumptions": {"raw_damage_per_gun": 2, "cooldown_seconds": 1, "penetration": 0,
            "nominal_raw_dps_per_gun": 2, "six_gun_nominal_raw_dps_if_all_overlap": 12,
            "stock_experiment_anti_ship_guns": 1, "stock_experiment_anti_torpedo_guns": 6,
            "visual_burst_length": 5, "burst_multiplies_damage": "UNVERIFIED; do not multiply by 5",
            "torpedo_damage": 750, "torpedo_penetration": 1000, "torpedo_cooldown_seconds": 30},
        "runtime_test": "NOT RUN", "installed": False,
        "test_constraints": ["Do not research trader_unlock_antifighter_frigate_light_autocannon_weapon.",
            "The five vanilla PDCs also intercept. Identify mount 0 by tracking/muzzle evidence; total kills alone do not establish its preemption.",
            "Ogrov target groups remain vanilla: use a valid enemy capital/defense/starbase/titan target protected by Garda.",
            "Full-health torpedoes may survive a sparse 5000-range screen; distinguish lack of damage capacity from lack of target eligibility.",
            "No priority guarantee follows from first group ordering or best_target_in_range."]}
    write(out / "integration-spec.json", spec)
    write(out / "offline-validation.json", {
        "status": "PASS", "runtime": "NOT RUN", "schema_revision": PIN,
        "schema_hashes_verified": len(schema_hashes), "input_hashes": checked_inputs,
        "existing_candidates_verified": candidate_audit, "staged_schema_valid": sorted(staged),
        "proposed_unit_schemas_valid": ["trader_antifighter_frigate", "trader_torpedo_cruiser"],
        "checks": ["Pinned schema bytes", "Existing candidate contents unchanged", "Referenced installed input hashes",
            "Exact weapon/projectile/unit allowlisted differences", "Enemy filter and existing groups",
            "Garda effect and turret aliases", "Ogrov muzzle alias", "One entry for experimental physical gun"],
        "output_hashes": {p.name: digest(p) for p in sorted((out / "entities").iterdir())}})
    print(f"PASS: {len(staged)} staged definitions, two in-memory proposed unit overrides, {len(schema_hashes)} pinned schemas. Runtime NOT RUN. {out}")


if __name__ == "__main__":
    main()
