# Corvette checkpoint: workstation experiments

**Historical handoff.** The user subsequently tested baseline loading/firing and a new six-PDC polish variant was prepared; see [polish.md](polish.md). The one-turret blocker below is preserved as a historical result, not the status of the repaired polish meshes.

Starting checkpoint: `9e40dd4b42853318ef87cc3d7d858f2abf601176`. Main checkout was clean before this assignment; no unexpected edits were found. No checkpoint commit, reset, stash, dependency update, push or publication was performed. This handoff consists of uncommitted reviewed source changes plus ignored local packages. Record both HEAD and the source-tree hash, not HEAD alone.

Use installed Sins II **2.0.3 (318), Steam build 25127248**, recorded SDK Steam build **24092025**, and official schema revision **8e061033afe53b1393eaefd56617a3fd041eeb5f**. No newer revision was fetched. Existing environment evidence and loading instructions remain in `environment.md` and `build-and-load.md`.

## Frozen baselines

`audit/experiments/checkpoint.json` records the original built and installed file inventories, ZIPs, settings, master/derived assets and old combat candidates. The checker compares all bytes without invoking baseline builders. The final preservation report is `audit/experiments/final-preservation.json`.

| Baseline | Preserved ZIP SHA-256 | Built and installed tree SHA-256 |
|---|---|---|
| `expanse_cobalt_name` | `0854d2769ac8870de3a24a9f660b5c266f67be235829ab09b94b233652efbbb6` | `599ec704a76198a37e5230da722764b11ea17590cd5da6b8ec85aea668630c37` |
| `expanse_corvette_visual` | `6ee4e3b8248113d75a088859c21d0723d33252baed91b7bebe5c086c14281a1c` | `c3f88816cbd303df5da78f4c8e9f1a7e0ba5d1219d8ccfd9a3827933be3fda68` |

The name mod changes exactly two English entries. The visual mod additionally changes the visible Cobalt mesh, two fixed-gun muzzle positions and their mean weapon position. All other gameplay and the vanilla autocannon definition remain unchanged. Neither has functional PDCs or torpedoes. Both remain installed, disabled, and untouched. The original archive, extracted master, normalized/optimized assets and previous candidates remain untouched.

Tree hashes are SHA-256 of compact sorted JSON mapping relative filenames to SHA-256. They differ from archive hashes because ZIPs also contain archive structure.

## Ownership and isolation

Workers used separate Git worktrees under `/run/media/haker/NVME 2/expanse-workers/`, all starting at the checkpoint. Shared ignored dependencies were explicitly supplied as read-only absolute paths. Workers did not own final unit/skin definitions, manifests or integrated documentation.

| Owner | Reviewed source integrated in main | Separate ignored output/dependency |
|---|---|---|
| A, weapon behavior | `tools/weapon_experiment.py`, `audit/workers/a/` | `weapon-behavior/build/worker-a/` |
| B, one turret | `tools/tachi_rig_experiment.py`, `tools/tachi_verify_compiler.py`, `audit/workers/b/` | `tachi-one-pdc/assets/derived/worker-b/`, `tachi-one-pdc/build/worker-b/` |
| C, validation | `tools/validate_experiments.py`, `tools/experiment_checks_selftest.py`, `audit/workers/c/` | Temporary fixtures removed; reports retained |
| Main integrator | `tools/build_experiments.py`, checkpoint/final audits, shared unit/skin/manifest assembly and docs, `tools/audit_audio_sources.py` | Main `build/experiments/`; audio metadata only |

The worker worktrees remain available locally. An ordinary Git checkout does not include model assets, compiled meshes, SDK binaries or packages. Missing dependencies are BLOCKED; no substitutes are reconstructed or downloaded. Do not run the rig generator in the main checkout during this frozen assignment: its derivative outputs must remain in its isolated worker checkout.

## Separate experiment contents

**Stock weapon behavior — `expanse_exp_stock_pdc`.** Ten-file package; no imported model. Garda mount 0 inherits its working mesh, transform, arcs and PDC definition, changing only to a private weapon whose target groups include the verified corvette/light/flak groups alongside torpedo/strikecraft. Five other PDCs remain vanilla. The extra Garda light autocannon remains research-gated: do not unlock it for these tests. Ogrov's weapon reference and AI matching-weapon reference use a private identity-only weapon/projectile/skin chain. No shared vanilla weapon definition is overridden. Installed mesh, material, texture, effect and sound dependencies remain inherited.

This experiment affects every use of the Garda/Ogrov unit IDs, including applicable neutral/garrison units and opposing players using the same mod. It does not alter Cobalt. Torpedoes retain stock 12,000 range, 750 damage, 1,000 penetration and 30-second cooldown; this is neither a well-wide nor salvo-tuning experiment.

**Imported rig — CANDIDATE ONLY; reserved ID `expanse_exp_tachi_one_pdc`.** Cobalt retains the visual baseline's fixed autocannon and gains exactly one aft-facing dorsal PDC with an independent physical assembly. Its private Garda weapon copy changes only barrel and muzzle offsets; it keeps stock point-defense eligibility and gameplay. It is not the dual-purpose weapon. Four existing Garda effect aliases and two child mesh aliases are bound on the experimental Cobalt skin. The experimental hull omits exactly the moving triangles now provided by the base/barrel meshes; fixed deployed linkage stays on the hull. Other five assemblies remain static. Total geometry remains 14,622 triangles with no new optimization pass.

The proposed rig integration preserves the shared-Cobalt scope, including neutral/garrison reuse and unchanged special garrison localization. It is not an ordinary-Cobalt-only or faction-isolated override. Cobalt movement, health, cost, build menu and original autocannon stay unchanged; adding the test PDC intentionally adds its stock defensive damage. Its remaining shading, pitch sign, clipping, aiming and muzzle behavior need workstation inspection. See the worker's annotated view and mount metadata; geometric estimates are not authored or runtime-proven pivots.

The final shading gate found **412/2/18 zero-tangent indexed corners** in hull/base/barrel and **416/0/7 nonorthogonal corners**, respectively. Binary/JSON parity, positions, normals, UVs and total triangle conservation passed. The frozen visual baseline also has **432 zero-tangent and 422 nonorthogonal indexed corners** under this newly added check. This is a newly observed baseline shading risk, not permission to alter it. G2 must inspect normal-map lighting, particularly seams and small PDC parts. Tangents require a separate bounded correction before packaging the imported rig; the unchanged baseline still needs its originally planned runtime acceptance.

## Build, verify and identify

The complete stock experiment lives under main `build/experiments/expanse_exp_stock_pdc` with its matching ZIP and external `.dependencies.json` / `.provenance.json` sidecars. No Tachi experiment package was produced: the generated hull has unresolved invalid shading tangent frames. Geometry/partition/mount outputs remain in Worker B’s separate ignored directories, with exact diagnostics in its report. The packaging gate refuses this incomplete candidate. IDs are folder names; `.mod_meta_data` uses only the observed `compatibility_version: 2` field. Human labels above identify the experiments without inventing metadata keys. Final ZIP hashes and source provenance are recorded by the sidecars and `audit/experiments/package-summary.json`.

To reproduce definitions, use Worker A's report command in its isolated worktree and choose a fresh output path; it refuses overwriting candidates. To reproduce meshes, use Worker B's report command in its isolated worktree with the recorded normalized assets, SDK and installed Proton path. Do not redo model intake/optimization. MeshBuilder is an offline compiler, not a game session.

Main assembly commands, from the project directory, after setting the two recorded paths:

```bash
export SINS2_GAME='/run/media/haker/NVME 2/SteamLibrary/steamapps/common/Sins2'
export SINS2_SDK='/run/media/haker/NVME 2/SteamLibrary/steamapps/common/Sins of a Solar Empire II - Mod Tools'
python3 tools/build_experiments.py stock --weapon-input '/run/media/haker/NVME 2/expanse-workers/weapon-behavior/build/worker-a' --game "$SINS2_GAME" --sdk "$SINS2_SDK"
```

The assembler also reserves a `tachi --rig-worker PATH` mode, but it is blocked until the rig shading-frame gate passes; no ready-to-load Tachi output is claimed. These commands refuse existing experiment outputs and never call baseline builders/installers. They archive only after required offline checks PASS. Preserve the current artifacts; reproduce in a separate project copy with required local dependencies explicitly provided if outputs already exist. Sidecars enumerate ignored input hashes. Archive timestamps/order are fixed. Compiler output stability is checked from actual bytes, not assumed across tool versions.

Read-only checks are safe to repeat:

```bash
python3 tools/validate_experiments.py frozen --game "$SINS2_GAME" --sdk "$SINS2_SDK"
python3 tools/validate_experiments.py package --mod build/experiments/expanse_exp_stock_pdc --zip build/experiments/expanse_exp_stock_pdc.zip --game "$SINS2_GAME" --sdk "$SINS2_SDK"
python3 tools/experiment_checks_selftest.py --root . --game "$SINS2_GAME" --sdk "$SINS2_SDK"
```

The resolver uses each mod plus the installed game, checks new entity manifests, skin-local aliases, meshpoints, materials/textures, target filters/groups and actual torpedo entity references. It stops at unchanged installed effect/audio/death resources after verifying existence; it does not claim complete engine-level closure. The pinned schemas' Draft 7/newer-keyword mismatch still requires exact diff review, which was performed. Missing-environment checks are distinguished from asset-independent self-tests; a skipped/missing dependency is never a PASS.

Final provenance must be refreshed after source/doc edits using `provenance(zip_path, project_root, dependency_paths)` from `tools/validate_experiments.py`, writing only the ignored sidecar. The package summary intentionally does not embed its own source-tree hash. A dirty build's source-file map identifies the exact bytes in addition to the checkpoint commit.

## Next workstation session

No experiment was installed/enabled in this assignment. For a later workstation test, copy/extract only the chosen experiment's contents into its own matching folder under the existing user mod directory recorded in `build-and-load.md`; `.mod_meta_data` must be directly inside that folder. Use the game's mod screen to activate just that variant and apply changes. Keep each variant's saves separate. Never overlay experiment files into either baseline folder.

Follow the available gates in the existing manual checklist: name baseline; visual baseline; stock ship/torpedo controls and mixed explicit-order test; stock persistence and 1/6/30-ship performance. G7, one imported turret, is BLOCKED at offline packaging until shading frames are corrected; its runtime test is still NOT RUN. Do not manually assemble the rejected candidate to bypass that gate. Record results only in the existing `audit/manual-results.md` template. All remain **NOT RUN**.

The essential unresolved behavior is whether the same widened PDC interrupts ship fire for incoming torpedoes while an explicit attack order remains active. Group order and `best_target_in_range` do not prove priority. Observe mount 0 directly because the five stock PDCs can mask its behavior. Stock PDC damage is 2 per nominal one-second cycle, at most 12 raw DPS for six overlapping guns before mitigation; visual bursts do not prove multiple damage events. Stock torpedoes have 100 armor, armor strength 50 and 50 hull, with durability absent from the definition. Sparse defenses may hit without killing them. Verify damage separately from eligibility and require that intercepted torpedoes cause no later impact damage.

Six imported functional guns, high-DPS/low-penetration balance, well-wide torpedo reach, salvo accuracy, standoff and saturation tuning await this evidence. Audio remains the separate local feasibility/permission audit in `audio-feasibility.md`. No railgun, new ship, faction, economy, shield, AI redesign, stealth or flip-and-burn work was added.
