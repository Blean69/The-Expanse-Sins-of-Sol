# Combined 0.4 follow-up

Main integration preserves all installed mods and the 0.3 package files. The checkpoint is `audit/combat04/checkpoint.json` at source commit `9e40dd4b42853318ef87cc3d7d858f2abf601176`. Existing local changes are retained. Package provenance also records the dirty source tree and ignored dependency hashes; the commit alone does not reproduce these uncommitted changes.

The user reports successful corvette/hero movement and satisfactory hero railgun balance in the previous session. Those observations are recorded in the existing `audit/manual-results.md`. The enabled-mod file currently lists both `expanse_rocinante03` and `expanse_corvette_combat03`, which overlap Cobalt definitions. This does not establish which ordinary torpedo implementation was active. The0.4 test must load the combined package alone.

## Projectile change

The actual installed Javelis is `trader_long_range_cruiser`, using `trader_long_range_cruiser_medium_missile` and `trader_medium_torpedo`. The similarly named antiarmor frigate is Kalev and was not used as missile evidence. The private light torpedo references the installed Javelis mesh/trail and launch effect. No stock missile file changes or copied stock binary assets are needed.

| Property |0.3 |0.4 candidate |
|---|---:|---:|
| Visible missile length, game units |272.083 |16.5108 |
| Maximum speed |1000 |1250 |
| Linear acceleration duration, s |2 |1.5 |
| Angular speed, degrees/s |15 |22.5 |
| Angular acceleration duration, s |2 |1.5 |
| Damage / penetration |750 /1000 |750 /1000 |
| Projectile hull / armor / armor strength |50 /100 /50 |50 /100 /50 |

Normal magazines remain 8 rounds, two per 10 seconds,120 seconds to reload after emptying. Hero salvo remains independent. The old large projectile stays preserved in 0.3 and the source candidates for potential Donnager use. Increased speed and smaller bounds can affect interception even though damage and health are unchanged; test actual hits and mitigation. The finite200,000 range and240-second lifetime are not proof of arbitrary whole-well reach against moving targets.

## Hero geometry and rig

The source comparison found a rigid hull through the deployment animation. The old PCA axis differed from the measured authored engine axis by about 0.66 degrees. More significantly, permissive simplification distorted hull surfaces even with backface culling disabled. A separate corrective derivative tightens the error bound from 0.04 to 0.005 and recalculates normals with a 30-degree crease. The simplifier still allows permissive collapse; this is not a claim that every seam is locked. It retains source part identities, removes the printing stand and carries the existing project-authored launch ports and railgun along with the same rigid coordinate correction.

Six independent yaw/pitch mount candidates replace the six fixed hero mounts. Each retains one weapon definition and one damage budget:28damage every0.25seconds,112rawDPS per physical PDC,672maximum across six before arcs and mitigation. Their dual-purpose target filter and target-group order remain unchanged. Rotating geometry is not an additional anti-missile weapon. Neither first-choice interception under explicit attack orders nor successful turret tracking is proved by offline checks.

All hero gameplay fields outside mount geometry remain unchanged, including movement, health, cost, abilities and the accepted2500damage/1000penetration/10-second railgun. Hero rail/torpedo/exhaust coordinates move with the corrected geometry. Ordinary corvette geometry and navigation remain unchanged. The initial game pose remains deployed; game-triggered deployment animation is still deferred.

## Reproduction and ownership

Main owns `tools/build_combat04.py`, shared unit/skin definitions, manifests, package integration and this documentation. Weapon worker owns `tools/combat04*.py` in `expanse-workers/weapon-behavior` and `audit/combat04-a`. Geometry worker owns `tools/geometry04*.py` in `expanse-workers/tachi-one-pdc` and `audit/geometry04-b`. Donnager worker owns `tools/donnager04*.py` in `expanse-workers/validation` and `audit/donnager04-c`. Separate worktrees and output directories isolate writes. Shared sources and SDK are read-only.

The builder requires the reviewed worker outputs and existing combined 0.3 package; it refuses missing dependencies and existing output directories. A clean checkout without ignored source/assets is insufficient. It does not fetch replacements, install or enable mods. Use `--validate-only` to recheck a completed package.

Only after the package summary reports successful offline checks, manually extract its contents into a new `expanse_rocinante04` folder under the Proton `AppData/Local/sins2/mods` directory. Disable all older Expanse variants for this test, enable0.4 and Apply Changes. Keep existing folders for rollback. Use a fresh disposable save. Do not stack0.4 with the name, visual, polish, timed-magazine, passive-magazine or0.3 hero alternatives.

The combined package continues overriding shared Cobalt, including applicable neutral/garrison uses. It retains the existing TEC hero build registration and one-hero limit. No faction/build-menu redesign solves that shared scope here. Donnager is a separate asset/design study in `docs/donnager04.md`, not included as an unfinished playable entity.

Use the 0.4 section of the existing manual checklist and results log. No game launch or runtime pass occurred during this build session.

## Built package and measured limits

`build/experiments/expanse_rocinante04.zip` contains 198 files. SHA-256: `fa00d7e1de5dca57a4728b3dcb2d7c0b6660afdbbd1dfef9ef638a6a68cb1ff0`. Tree hash: `a673fdade01f53a5db871a9303e5505dae16f6d6c214e9acb32a258413c2792f`.

The hero totals 92,067 triangles: 67,377 fixed hull, six 192-triangle yaw meshes and six 3,923-triangle cannon meshes. This exceeds the pinned 12,500-frigate and 75,000-capital guidance. The one-hero limit makes it a bounded quality experiment, not a reason to claim performance is acceptable. A later texture-baking/optimization pass remains necessary for a production-quality budget. Seventeen microscopic rounding-sensitive slivers were removed; source panels were not replaced by invented hull geometry.

Actually passed: 52 package schema checks, authored action/projectile references, 80 additional Javelis dependency hashes, 13 independent compiled-geometry checks, exact ordinary-navigation/hero-gameplay/rail preservation and six per-gun budgets. The compiler regenerated winding/facing data; only tangent fields were subsequently repaired, with no fallback tangent and unchanged trailers. All 12 installed/build trees and six prior ZIPs match the checkpoint; enabled-mod settings are unchanged.

```sh
python3 tools/build_combat04.py \
  --game '/run/media/haker/NVME 2/SteamLibrary/steamapps/common/Sins2' \
  --sdk '/run/media/haker/NVME 2/SteamLibrary/steamapps/common/Sins of a Solar Empire II - Mod Tools' \
  --geometry '/run/media/haker/NVME 2/expanse-workers/tachi-one-pdc' \
  --combat '/run/media/haker/NVME 2/expanse-workers/weapon-behavior/build/combat04-a' \
  --validate-only
```

Remove only `--validate-only` when building in a fresh output location with the same preserved dependencies. The builder deliberately refuses to replace the existing package. Worker reproduction commands and exact local dependencies are recorded in `audit/combat04-a/worker-report.md` and `audit/geometry04-b/REPORT.md`.
