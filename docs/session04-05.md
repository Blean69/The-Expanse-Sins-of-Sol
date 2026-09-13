# Session delivery — corvette/Rocinante follow-up and new ship groundwork

Two complete, mutually exclusive experiments are ready for manual installation. **Use `expanse_rocinante04_amun` alone** to test the custom torpedo model; use `expanse_rocinante04` alone for the stock-Javelis comparison. No installed folder, enabled-mod setting, base-game file or pinned SDK dependency was changed. No game was launched and no new runtime pass is claimed.

| Package | Contents | ZIP SHA-256 |
|---|---|---|
| `build/experiments/expanse_rocinante04.zip` | Smaller/faster torpedoes, corrected hero hull, six aiming PDC rigs | `fa00d7e1de5dca57a4728b3dcb2d7c0b6660afdbbd1dfef9ef638a6a68cb1ff0` |
| `build/experiments/expanse_rocinante04_amun.zip` | Complete0.4 plus actual extracted Amun torpedo appearance | `0037f2f5d06046bd442231372690f999f84a6fefbca023955017a4c3a2368e74` |

The current Martian 750 damage, 1000 penetration and 50 hull /100 armor /50 armor strength are preserved. Speed is1250, turn22.5°/s, acceleration ramps1.5s. The custom appearance retains these values and the existing collision box, expanding only the enclosing sphere by0.16%. The accepted Rocinante rail and all ship navigation/gameplay outside the new mount geometry stay unchanged.

Hero geometry is now coherent in offline views, with six source cannon assemblies and explicit new yaw/pitch joints. It totals92,067triangles, above the SDK guidance; this remains a unique-hero quality/performance experiment. Rotation, collision clearance and in-game shading still require observation. The original archive/master and prior derivatives are preserved.

## Checkpoint and preservation

Source HEAD: `9e40dd4b42853318ef87cc3d7d858f2abf601176`. Pre-existing uncommitted/untracked work remains preserved; no redundant checkpoint commit, reset, stash or push occurred. The package sidecars identify the final dirty source tree as well as ignored dependencies and package hashes.

All12 installed/build trees and six previous ZIPs match `audit/combat04/checkpoint.json`. Baseline preserved tree hashes:

- Name-only: `599ec704a76198a37e5230da722764b11ea17590cd5da6b8ec85aea668630c37`
- Visual: `c3f88816cbd303df5da78f4c8e9f1a7e0ba5d1219d8ccfd9a3827933be3fda68`
- Polish: `922bb383eac8568ac5f365cd992f96d6709620e36c71f4ab639555db0da2aebf`
- Combined0.3 hero: `f87253a45f07ed279f0aced31912378cc7690793a99d0f725db82daac6673d6e`

Pinned schemas remain `8e061033afe53b1393eaefd56617a3fd041eeb5f` on installed game2.0.3(318). All62 schema blobs and527 historical game references match. The additional80 Javelis dependencies were checked by actual path/hash. Existing enabled mods are still the two older, overlapping0.3 variants; they were not silently corrected. Disable them when manually testing the new package.

## Owners and checks

Main owns `tools/build_combat04.py`, `tools/build_torpedo05.py`, `tools/combat04_regression.py`, shared definitions/manifests and documentation integration. Worker A owns weapon/projectile/stealth candidate generators and `audit/combat04-a`, `audit/stealth05-a`; B owns geometry/compiler work and `audit/geometry04-b`, `audit/torpedo05-b`; C owns asset intake and `audit/donnager04-c`, `audit/amun05-c`. Workers used distinct worktrees/output directories. Reviewed tool/audit sources are copied into the main repository; ignored editable/compiler assets remain in their documented worker paths.

Actually passed:52 schemas per complete package; explicit authored reference checks;13 hero and one torpedo binary geometry checks; worker source/muzzle/frame/winding/tangent preservation checks; four negative validator regressions; ZIP/tree correspondence and all frozen baseline checks. Donnager/Amun intake geometry/reference/preservation checks passed. Fifteen Amun mechanics/combat candidate schemas passed, plus an offline counter model and single-roll boarding structure check. Actual stock cloak schema errors are recorded separately, not disguised as passes. No particle/material runtime behavior is implied by these checks.

Full evidence: `audit/combat04/final-offline-results.json`. Build/load commands: `docs/combat04.md` and `docs/torpedo05.md`.

## New ships and blockers

Donnager: preserved licensed source, five checked editable scenes, relative-scale preview, two isolated railgun candidates, measured donor PDC size, local capital/titan cost anchors and carrier feasibility research. Source has1.8million triangles against75k capital guidance. PDC count/layout, optimized game geometry, rail pivots/arcs and final abilities are not integrated. A native frigate factory can build the current MCRN/Cobalt but also other available frigates; an exclusive paid reinforcement ability is a different mechanic. Details and citations: `docs/donnager04.md`.

Amun-Ra: user permission recorded; actual1,600-triangle torpedo extracted and compiled. Source contains four PDC assemblies, fifteen pods and no animation channels. Three-gun selection, ship mounts and six-unit cap are not integrated. Existing cap mechanisms are per player, not a demonstrated shared faction-wide pool. Private provisional weapons specify900-damage/1500-speed torpedoes with25hull/50armor/50strength, three112DPS PDCs, and a3750-damage rail every10seconds. These are candidates, not balanced or packaged gameplay.

The verified spawn event can count individual torpedoes and start a fixed60-second deadline on the fourth. The probe contains no cloak. Installed Eidolon cloak fields are absent from pinned schemas; no schema update was made. Rail/PDC hit-based reveal cannot detect misses. The boarding probe rolls10% once after a scheduled3-second modeled visual; it does not detect a real pod collision or allow interception. These limitations prevent a truthful complete stealth/boarding release. Details: `docs/amun05.md`.

## Smallest workstation order

1. Load the custom-torpedo combined variant alone; build/select both ships and inspect hull surfaces, custom missile orientation/trail and logs.
2. Inspect all six hero PDCs through their arcs, then test interception during an explicit anti-ship attack. Check moving muzzle alignment, supports and the preserved railgun.
3. Count normal2/10s launches,8-round depletion and120s reload; test independent hero salvo, target loss and mid-magazine/mid-reload saves.
4. Verify orbit/phase appearance, destruction and formation/fleet performance, particularly the larger hero mesh budget.

Only afterward attach and test the separate stock-hull stealth-counter/boarding probes. Record all observations in the existing `audit/manual-results.md`; their detailed cases extend `docs/manual-test-checklist.md` rather than creating another results template.
