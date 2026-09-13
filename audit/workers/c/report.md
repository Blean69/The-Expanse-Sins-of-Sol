# Worker C — validation and reproducibility

Owner: Worker C. Isolated worktree `/run/media/haker/NVME 2/expanse-workers/validation`, starting commit `9e40dd4b42853318ef87cc3d7d858f2abf601176`. No shared baseline, master, SDK or settings writes; no game launch, install, enable, commit or push.

## Deliverables and API

- `tools/validate_experiments.py`: new read-only validation functions and CLI. Does not import or call the existing build/install modules, whose baseline behavior remains frozen.
- `tools/experiment_checks_selftest.py`: focused temporary-copy failure injection, asset-independent checks identified separately from local-environment checks. No dependency downloads.
- `audit/workers/c/frozen-validation.json`: all 14 preservation gates PASS, including both build and installed trees, both original ZIPs, shared assets/candidate inputs, settings, exact baseline semantic diff, 62 pinned schemas / 527 installed reference hashes, and MeshBuilder executable hash.
- `audit/workers/c/selftest-results.json`: 17 checks PASS. Actual installed Garda/Ogrov graphs resolve; this means offline references only. Runtime remains NOT RUN.

Integrator imports:

```python
from validate_experiments import check_frozen, validate_package, verify_zip, provenance
frozen = check_frozen(checkpoint_path, project_root, game_path, sdk_path)
checks = validate_package(mod_directory, game_path, sdk_path, project_root)
# Only archive/package experiments when both statuses are PASS.
zip_result = verify_zip(package_zip, mod_directory)
source_record = provenance(package_zip, project_root, dependency_paths=required_ignored_inputs)
```

`validate_package` expects a distinct mod directory directly under `project_root/build/experiments`. `.mod_meta_data` must contain the observed `compatibility_version: 2` structure. Its allowlist accepts entities (unit/unit_skin/weapon/additive manifests), localization, compiled meshes/materials/DDS files, and `ASSET-SOURCES.md`. Source glTFs, candidate directories, reports, provenance and rig metadata belong outside the loadable package. Newly defined entity IDs require additive manifests. Existing vanilla dependencies are resolved through the installed fallback; they need not be copied.

The resolver checks each unit's weapon and skin references, AI weapon matching identity, hull mesh point presence, skin-local mesh/effect aliases (including duplicates), weapon target-group/filter IDs, and spawn-torpedo entity classification. Mesh parsing uses the established project reader; unknown mesh layouts fail explicitly. Materials resolve to textures. Skin effect, sound and death references resolve case-insensitively as observed in Windows game IDs. `trail_effect` uses the verified `.exhaust_trail_effect` extension. It rejects unintegrated weapon candidates. Resolved dependency paths and SHA-256 hashes are returned in the report, including installed fallback files that were outside the original trace snapshot.

Scope limits are explicit: unmodified installed effects/audio/death assets are boundary existence references, not recursively revalidated whole-game resources. This checker does not prove shader rendering, aiming, mount orientation, damage timing, priority, interception or runtime loading. The pinned SDK has no material/localization/mod-metadata schema; those receive structural/reference checks. Draft 7 does not enforce the newer `unevaluatedProperties` keyword used in these schemas, so the integrator must still review exact source diffs. An unavailable file/library is BLOCKED, not a passed skip; missing or unbound referenced IDs are FAIL.

`provenance` hashes all Git-tracked and nonignored untracked source bytes (including dirty/deleted state), records HEAD, and hashes the ZIP and explicitly supplied ignored dependency paths. **Generate final source provenance after all tracked documentation/reports are complete, then save the sidecar only under ignored `build/experiments`, outside the mod directory/ZIP.** This avoids self-hash recursion. Regenerate after any source change. The source commit alone is insufficient for an uncommitted build.

CLI examples after integration (from project root, with the recorded absolute installation paths):

```bash
python3 tools/validate_experiments.py frozen --game "$SINS2_GAME" --sdk "$SINS2_SDK"
python3 tools/validate_experiments.py package --mod build/experiments/EXPERIMENT_ID --zip build/experiments/EXPERIMENT_ID.zip --game "$SINS2_GAME" --sdk "$SINS2_SDK"
python3 tools/experiment_checks_selftest.py --root . --game "$SINS2_GAME" --sdk "$SINS2_SDK"
```

`SINS2_GAME` and `SINS2_SDK` must be set to recorded installed paths; this code does not choose a newer remote SDK. The optional CLI `--report` accepts only `audit/experiments`, `audit/workers/c` or `build/worker-c` beneath `--root`. CLI returns nonzero for FAIL or BLOCKED. Integrator can write the returned provenance record into its ignored sidecar itself.

## Checks actually executed

1. `python3 -m py_compile tools/validate_experiments.py` passed.
2. Full read-only frozen check passed, then repeated after adding the MeshBuilder hash gate. Preserved ZIP hashes: name `0854d2769ac8870de3a24a9f660b5c266f67be235829ab09b94b233652efbbb6`; visual `6ee4e3b8248113d75a088859c21d0723d33252baed91b7bebe5c086c14281a1c`.
3. Temporary synthetic tree detects an injected `.weapon`; missing dependency returns BLOCKED; overlay wins over installed fallback; nonexistent typed reference fails.
4. Small copied baseline JSONs validate the expected two muzzle positions and mean `weapon_position`, then reject separately injected muzzle drift, mean drift and gameplay speed drift.
5. Real installed Garda/Ogrov reference graphs and a temporary stock package pass schema/reference gates, including mesh/material/texture dependencies and the torpedo entity chain. ZIP content comparison and source/package provenance generation pass.
6. Missing SDK returns overall BLOCKED; extra combat-candidates directory fails the package layout gate; unbound barrel alias fails reference resolution.

All fixtures were removed with their temporary directories. No baseline rebuild or generated model conversion was needed. Missing dependencies were tested as deliberate fixtures, not silently skipped real checks.

## Proposed additions to existing documentation (main integrator owns edits)

Extend `audit/manual-results.md`'s existing observation template with package ZIP SHA-256, source-tree SHA-256/dirty state, experimental mod ID, dependency report path, enabled-mod list, and camera distance. Keep its existing PASS / FAIL / BLOCKED / NOT RUN field and evidence paths. No competing runtime results file is needed.

Append a compact preflight/experiment gate table to the existing `docs/manual-test-checklist.md`:

- Record ZIP/source hashes and activate only one isolated variant per session. Name baseline, visual baseline, stock PDC behavior, then Tachi one-turret rig.
- Stock test: explicitly attack an enemy eligible ship; incoming enemy torpedoes enter mount-0 coverage; observe that physical mount's tracking, burst timing and target changes while attack order remains. Five unchanged Garda PDCs also defend, so whole-ship interception counts cannot establish mount-0 priority. Do not research the additional light autocannon for this gate.
- Record ship-only/torpedo-only/mixed-target mount-0 shots and damage separately. One mounted weapon uses one budget; visual burst length does not establish damage multiplication. Measure torpedo armor/hull loss separately from target eligibility; intercepted projectiles must not later deal impact damage.
- Rig test: known Garda point-defense targeting only; verify yaw, pitch, muzzle origin, arcs/coverage, absence of duplicated static assembly, selection and save/reload. Defer six-gun results until six guns are actually integrated/tested.
- Check shared overridden-unit scope: Cobalt neutral/garrison users for Tachi; all existing Garda/Ogrov users for stock experiment. Keep separate saves and disable one experiment before enabling another.

This worker did not assemble a persistent experimental package: shared unit/skin/manifests remain the main integrator's ownership. Its test package was temporary and contained installed stock assets only. Final experiment checks must run on the main integrator's actual output.
