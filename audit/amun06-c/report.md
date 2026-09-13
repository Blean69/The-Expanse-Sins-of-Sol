# Amun06 validation and static UI — Worker C

Worker C owns only new `tools/amun06_validate*.py`, `audit/amun06-c/` and `build/amun06-c/` outputs. Main owns every unit, skin, player, manifest and package. Existing source assets, Donnager/Amun05 preparation, SDK and installed game are read only.

## Static UI

Source is Worker B's actual `assets/derived/amun06-b/expanse06_amun_editable.gltf`, with active hull and three selected yaw/pitch assemblies: source pad roots892,910,946. The omitted fourth source pad928 is not restored. The active scene contains27,526 triangles; the unused pod node is excluded. Source coordinates already face game+Z and require no compiler-Z undo for rendering.

Output `build/amun06-c/ui/generated/` contains six new brushes, eighteen standalone PNG sprites covering100/150/200% DPI, and two uniquely named optional package logos. All filenames begin `expanse06_amun_`, including `expanse06_amun_mod_small_logo.png` and `expanse06_amun_mod_large_logo.png`; no baseline image name is overwritten. `integration-spec.json` contains `status`, `skin_patches` and `logos` for main integration.

The renderer uses the actual base-color atlas/UVs and a CPU double-sided z-buffer with the existing studio-light lift. No invented ship image, reconstructed geometry or copied Tachi/Rocinante art is used. Portrait master, silhouette mask, editable projected SVG and recipe stay under `ui/source/`; generated game PNGs/brushes stay under `ui/generated/`. Source glTF/buffer/texture hashes, pinned brush-schema blob, exact PNG dimensions and alpha checks are recorded in `ui-validation.json` and the render recipe. The contact sheet was visually inspected. Tactical icons preserve the actual top-view outline; they do not show every small cannon at tactical zoom.

Actually passed: active-scene triangle count27,526; source dependencies unchanged during rendering; six brush schemas; all twenty PNG dimensions/modes/alpha ranges (eighteen sprites plus logos). Runtime UI loading is NOT RUN.

Reproduce from this worker checkout:

```sh
python3 tools/amun06_validate_ui.py --source '/run/media/haker/NVME 2/expanse-workers/tachi-one-pdc/assets/derived/amun06-b/expanse06_amun_editable.gltf' --expected-triangles 27526 --game '/run/media/haker/NVME 2/SteamLibrary/steamapps/common/Sins2' --sdk '/run/media/haker/NVME 2/SteamLibrary/steamapps/common/Sins of a Solar Empire II - Mod Tools'
```

## Supplemental package helper

`amun06_validate_package.py` exports `check_amun06(mod, base, game, sdk, unit_id, limit_tag, pdc_weapon_ids)` for the main builder. Identifiers are explicitly checked against `expanse_amun_ra` and PDC0/1/2; it does not silently generalize arbitrary faction changes.

The helper checks:

- Prior combined04 package files are byte-identical except metadata, source record, added localization, three player definitions, unit tags and additive manifests. Existing localization values remain identical.
- Each existing player changes only by appending Amun to buildable units and a private per-player global cap6. The Rocinante cap1 and all other player values remain unchanged. The private unit tag is registered without changing existing unit/item tags.
- Exactly three distinct physical PDC origins/budgets use the three expected biaxial definitions. The core ability set is only magazine and boarding; optional cloak/reveal files, native cloak hooks and cloak keys are rejected.
- Exact additive entity manifests resolve new definitions against installed files. Uniform group/filter references use an explicit overlay with declared merge/overwrite intent; dropping/changing installed entries is rejected.
- Existing Resolver geometry/material/weapon/skin checks are supplemented by exact ADS scalar operands (`value_a`, `value_b`, value and supply IDs), target filters, definition IDs, modifier IDs and ADS particle/sound aliases.
- Boarding has one modeled3-second delay, one attempt buff, one10% random check at buff start, one ownership transfer to the initiating ship's owner and target-derived supply checks at cast/attempt. This is a source graph check, not proof of physical pod arrival or engine execution context.
- The six private UI brushes and DPI PNGs resolve.

The pinned schemas declare Draft7 but also use `unevaluatedProperties`, which Draft7 ignores. The helper reports declared-Draft7 results separately from an additional strict Draft2020 interpretation of the same pinned unit schema. The installed Cobalt's `corruption` object is absent from that schema: it is accepted only by exact equality with installed Cobalt, with a source hash and all three penalty-buff references checked. The strict check evaluates the remaining unit fields on an in-memory copy; it does not remove anything from the actual package. No blanket unknown-field exemption or full unknown-field-coverage claim is made.

Six bounded checks using only owned temporary copies passed: reviewed boarding graph accepted; guaranteed capture rejected; repeat-attempt schedule rejected; changed capture recipient rejected; explicit additive private target group preserves installed groups; overwrite that drops installed groups rejected. `negative-checks.json` records diagnostics. Temporary fixtures were removed. No large test framework was added.

Run the full package check after main assembly:

```sh
python3 tools/amun06_validate_package.py --mod '/run/media/haker/NVME 2/expanse-mod/build/experiments/expanse_amun06' --base '/run/media/haker/NVME 2/expanse-mod/build/experiments/expanse_rocinante04_amun' --game '/run/media/haker/NVME 2/SteamLibrary/steamapps/common/Sins2' --sdk '/run/media/haker/NVME 2/SteamLibrary/steamapps/common/Sins of a Solar Empire II - Mod Tools'
python3 tools/amun06_validate_checks.py
```

Required ignored geometry and package paths must exist. Missing inputs fail with a path and remaining checks NOT RUN; they are never counted as passing dependency-dependent checks. `tools/common.py`, `tools/polish_ui.py` and main's existing validation/action utilities are read-only dependencies. No downloads, dependency updates or game launch occurred.

## Runtime boundary and integration status

At initial handoff, UI/component negative checks passed; the complete package check awaits main assembly. Its result belongs in `package-validation.json`, not inferred from this report's component checks.

Workstation testing must establish six-cap queue/capture/rebuild behavior, three turret rotation/muzzle alignment and interception during a ship attack, the boarding target/source-owner context and delayed supply recheck, one attempt rather than repeated rolls, save/reload during the pending boarding delay, and new UI loading. A visible modeled shuttle is not an independently interceptable physical pod. Optional cloak remains outside the core package validation scope. Previous Rocinante triangle/performance decisions were not altered or optimized by this worker.
