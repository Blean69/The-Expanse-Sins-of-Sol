# Amun-Ra 0.6 integration result

Two separately loadable combined experiments were prepared locally. No install, enable, game launch, commit, push or public distribution occurred. Latest user observations accept the0.4.1 torpedo appearance, corrected Rocinante, PDC tracking and unique-hero performance. That92,067-triangle hero was preserved. Timed boarding is an accepted design choice; the new Amun behavior remains **NOT RUN** in-game.

## Checkpoint and preservation

Source HEAD: `9e40dd4b42853318ef87cc3d7d858f2abf601176`, with existing local edits intentionally retained. No redundant checkpoint commit or stash was made. `checkpoint.json` records14 installed/generated trees, eight prior ZIPs and the current enabled list. That list contains only `expanse_rocinante04_amun`.

| Preserved tree | SHA-256 |
|---|---|
| Name baseline | `599ec704a76198a37e5230da722764b11ea17590cd5da6b8ec85aea668630c37` |
| Visual baseline, including two muzzle changes | `c3f88816cbd303df5da78f4c8e9f1a7e0ba5d1219d8ccfd9a3827933be3fda68` |
| Installed/tested0.4.1 | `7734eeb09fa0f2b48d849f0721d2fa35c742b536b0abc2ae14318aba1e568492` |

The accepted0.4.1 ZIP remains `0037f2f5d06046bd442231372690f999f84a6fefbca023955017a4c3a2368e74`. All204 preceding package files are preserved in new outputs except the explicitly reviewed metadata/credits, additive localization/manifests/tag and three player additions. Existing Corvette/Rocinante units, skins, weapons, abilities and geometry remain byte-identical. Every prior installed package and enabled setting is unchanged.

## Owners and locations

- Main: `tools/build_amun06.py`, `tools/build_amun06_cloak.py`, final unit/skin/player/manifests/effects/localization, `audit/amun06`, `docs/amun06.md`, existing checklist/results extensions and source-permission record.
- A, isolated `expanse-workers/weapon-behavior`: twelve private combat/boarding definitions and six optional cloak definitions, `build/amun06-a/final-reviewed`; reviewed helpers/report copied to main `tools/amun06_behavior*.py` and `audit/amun06-a`.
- B, isolated `expanse-workers/tachi-one-pdc`: separate editable ship/pod under `assets/derived/amun06-b`, eight official compiled meshes, eight materials and four2K textures under `build/amun06-b/game`; scripts and report copied to main `tools/amun06_geometry*.py`, `audit/amun06-b`.
- C, isolated `expanse-workers/validation`: six UI brushes,18 sprites and two unique logos under `build/amun06-c/ui`, supplemental package/reference checks; copied `tools/amun06_validate*.py`, `audit/amun06-c`.

Shared sources/SDK remained read-only. Worker game and UI handoffs were hash-checked against their manifests and pinned in `reviewed-inputs.json`. Original Amun archive/master and frozen hero/torpedo derivative hashes passed preservation checks. New editable sources remain separate from generated packages.

## Offline checks actually run

- Game2.0.3(318),62 pinned schema blobs at `8e061033afe53b1393eaefd56617a3fd041eeb5f`,527 recorded installed references: PASS unchanged. No newer SDK was substituted.
- Core:72 declared-Draft7 entity/brush/uniform validations; exact private behavior invariants; strict new-unit known-key check and exact inherited installed-Cobalt corruption exception: PASS.
- Eight generated mesh checks: winding, source correspondence, finite orthogonal tangent frames, official trailer preservation and exact hull/rig/muzzle bases: PASS. Ship27,526 triangles; separate pod4,481; zero fallback tangents. Materials/DDS and all actual-model UI references: PASS.
- Full mod-plus-base references,1,122 recorded core resolution edges; three distinct PDC budgets plus one rail, exact AI/weapon target groups, two real launch positions, additive manifests, six-cap/one-hero player changes and unchanged prior files: PASS.
- Boarding: exact3s delayed single10% roll, target-supply checks and initiating-owner expression: PASS offline graph. This establishes configuration, not engine ownership/timing outcomes.
- Optional cloak: exact six-file candidate, all local values/memory/refs, unit hook, fixed fourth-projectile/60s transitions, core-preserving file diff and supplemental installed-field checks: PASS. **Official schema coverage remains partial** for cloak fields/native hook and inherited corruption. Nothing silently waives arbitrary unknown keys.
- Worker negative checks: ten cloak mutations rejected; six graph/overlay cases yielded two expected passes and four expected rejections. Python syntax checks passed. Runtime checks: NOT RUN.

The first core assembly correctly failed the strict key check because geometry-report annotations (`bounds_min`, `bounds_max`, `includes`) had been copied into `spatial`. The builder now selects only official `box`/`radius` fields plus collision rank. No schema was relaxed. That incomplete attempt is retained outside experiments at `build/amun06-incomplete-first`; it has no ZIP and must not be installed. Fresh corrected assembly passed all checks.

## Packages

| ID | Files | ZIP SHA-256 | Tree SHA-256 |
|---|---:|---|---|
| `expanse_amun06` | 267 | `4b7c400d430f18c4ea6f306a10c985df7de25035d0347b414031efc8d1b85aaf` | `e9af852c6e40ea83a7f31c79d574f935597583d5250442ea9c446db29f43aa18` |
| `expanse_amun06_cloak` | 273 | `e4c436e68d0ae52d2edb06fe244445fbaff8f4a97b62bdd92a98e389f1d0775f` | `a238df02a4c71b2d288a60e41a834bbc94d49ec184b146e9eb30a547aba14255` |

Both ZIPs are under `build/experiments` with external `.provenance.json` and `.dependencies.json` records. They contain complete combined mods, so load exactly one alone. The cloak variant retains the native Harbinger product gate; core is the fallback for isolating combat/boarding. Current installation was left untouched.

## Smallest ordered workstation tests

1. Core: load/apply, build/select, inspect actual portraits, six-unit queue/loss limits; move/orbit/jump and confirm old ships unchanged.
2. Three PDC tracking/muzzle/arcs and interception while attacking a ship; rail alignment/cadence; stronger/faster/weaker-health torpedoes, paired magazine and empty reload.
3. One timed pod launch and delayed capture attempt; invalid targets, supply/ownership, source/target death, repeated trials and pending-action save/reload.
4. Separate cloak variant: entitlement/detectors, first three individual missiles/fourth in second pair, fixed60s despite more fire, hit-vs-miss limitation, manual toggles and saves with count3/active reveal.
5. Destruction and save/reload; one ship, small formation and six Amun plus the unique Rocinante for performance.

Remaining uncertainties include source-door clearance, normal-map bump direction, turret aiming and actual PDC target priority, damage effectiveness, capture context/race conditions, cap behavior after capture, cloak event ordering/toggles/serialization and fleet performance. The pod is a timed mesh particle with no interception health. Missed PDC/rail shots do not reveal; successful hits do. Six is per player empire, not a faction-wide pool across multiple players. Scale61.5m/46m is provisional secondary evidence. These limitations are also in `docs/amun06.md` and the existing runtime log/checklist. No audio, Donnager integration or unrelated balance expansion was added here.

Independent final Worker C review also passed the assembled core:72 schema checks, strict remaining unit fields, six manifests, exact caps/budgets, boarding and UI. Pure builder checks matched compiled mount transforms and yaw/pitch/muzzle chains. No additional blocker was found. See `audit/amun06-c/package-validation.json`.
