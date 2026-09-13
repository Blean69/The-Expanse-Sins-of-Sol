# Corvette 0.3 and Rocinante preparation

The user observed six PDCs tracking individually and good tracers in the 0.2.1 polish prototype. Remaining hull holes and floating supports were reported. Those observations are recorded in the existing [runtime results](../audit/manual-results.md); new 0.3 runtime behavior is **NOT RUN**.

This work uses installed Sins II **2.0.3 (318)** and official schema pin `8e061033afe53b1393eaefd56617a3fd041eeb5f`. Source checkpoint is `9e40dd4b42853318ef87cc3d7d858f2abf601176` with local uncommitted changes preserved. No dependency update, game launch, installation, enablement, commit or publication was performed.

## Preserved working versions

| ZIP | SHA-256 |
|---|---|
| name-only | `0854d2769ac8870de3a24a9f660b5c266f67be235829ab09b94b233652efbbb6` |
| visual baseline | `6ee4e3b8248113d75a088859c21d0723d33252baed91b7bebe5c086c14281a1c` |
| polish 0.2.1 | `77fafb25e1f8ec8f812c5f5b720bef85f563c451b3866d432c7ae5141f0b2e10` |

`audit/combat03/checkpoint.json` records individual files and tree hashes of all three installed and built copies. Old masters and packages stay intact. The ordinary corvette retains the shared Cobalt scope, including applicable neutral/garrison uses.

## Current package choices

Use **`expanse_corvette_ammo03.zip`** first for the requested ammunition behavior. It stores eight rounds plus pair/reload deadlines in per-buff memory, selects the nearest detected eligible enemy in the same well, launches two, deducts two and sets a 10-second deadline. Empty magazines set a 120-second reload deadline. No target means no ammunition debit. It has no active channel or movement operator. The state persists by design within the buff; engine save serialization, passive-buff lifetime and target-selection ordering are runtime gates. Scanning is4Hz per ship; measure fleet performance. Its target can differ from a manual attack target.

`expanse_corvette_combat03.zip` is the earlier **timed-cycle diagnostic alternative**, preserved separately. Never enable it with the passive-magazine variant: both override Cobalt and would create conflicting behavior. Both include the same geometry, PDCs, UI, orbit pattern and phase effects.

| Package | ZIP SHA-256 |
|---|---|
| Passive ammunition experiment | `b35ca53921724ed7db2b134e424e4de1d4bb378c495b2f7c66c6c299e26f2c8f` |
| Earlier timed diagnostic | `e3ea5be007e007b6787a652059c8eeb639cb2c657df5476069f46eb0b2ea3032` |

## Corvette experiment

`build/experiments/expanse_corvette_combat03.zip` is a separate local experiment. Its matching `.provenance.json` identifies source commit, dirty source tree and package hash. Load this variant alone; it already includes the model, PDCs, names and UI. It is not installed by the agent.

- **Geometry:** 16,335 triangles. Add physical PDC sockets/yokes/pivot supports and 801 targeted interior triangles on source thin shells marked double-sided. Existing authored hull parts, pivots, muzzles and six weapon budgets remain. Compiler-facing data is regenerated, followed only by verified tangent-field repair. Remaining near-perpendicular normal cases and actual culling/clipping need visual testing.
- **Movement:** installed `circle_strafe` attack pattern, with off-plane angle range −45..45 degrees. Cobalt acceleration, turn rates, speed and other physics remain unchanged. This does not establish a desired orbit radius or torpedo standoff.
- **Phase travel:** private blue plume at 4× the ordinary source plume's axial scale replaces this skin's three native travel effects. Charging/exit effects and sounds remain stock. Hook origin and coexistence with ordinary exhaust require runtime observation; no global camera effect is changed.
- **PDCs:** all six working 0.2.1 definitions and unit mounts are preserved byte-for-byte/structurally. One budget per physical gun; no hidden independent interception weapon is added.
- **Heavy torpedoes:** private damageable Ogrov-derived torpedo entity, 750 provisional damage, 1,000 penetration, speed1,000, 240s life. Ability range200,000 plus an explicit same-gravity-well target filter supports a long-range experiment. This is not proof of hitting every moving target on every map. Vanilla projectile skin/effects remain references, not copied shared weapons.
- **Launch positions:** two model-derived dorsal/ventral front-plane centers replace all stock Ogrov coordinates. Rotation follows the installed row-vector convention. The model has closed hatch/front surfaces; aperture clearance and TV-exact launch location are not yet observed. See `audit/geometry03-b/torpedo-mounts.json`.

The timed cycle requests pairs at 0/10/20/30 seconds and a 120-second cooldown starting when the finite buff dies: next ready at150s **if** engine completion occurs at the final interval. This first experiment does not store a persistent remaining-ammunition counter. Each scheduled action rechecks the original target; invalid targets skip that action. Refund, pause/resume and retargeting semantics are not promised. A watched ability may interfere with movement despite explicitly allowing weapons during channeling. Test C03-2/3 before treating it as a completed ammunition system.

## Hero work

**`build/experiments/expanse_rocinante03.zip`** is the separate 164-file hero experiment, SHA-256 `6c86c8ed0a514345255bfd9a2341d453c77b4544d88cee20a24d9b0f64681983`. It includes the ordinary passive-magazine corvette too, so load it alone. It is not installed. Hero-only changes do not alter ordinary corvette definitions or assets.

The hero uses **26,935 triangles**, above the suggested 12,500 budget: 26,707 retained source triangles plus 228 prototype-fitting triangles. Test performance even with the one-per-empire limit. The hero PDCs are **static deployed**, with six independent firing budgets and narrow fixed arcs (yaw±15°, pitch±5°); they do not rotate or run deployment animations in this package. Their actual barrel-cap positions are measured on this new model. The ordinary corvette retains all six working rotating PDCs.

A visible project-authored keel railgun and two launch fittings provide real muzzle locations. They are geometric prototype additions, not authenticated TV-exact parts of the source. The railgun uses the installed fixed-gun mount pattern; hero torpedo abilities have their own measured port coordinates instead of borrowing Tachi coordinates. Source animation is preserved in the stand-free editable model. Three flat-color source materials and new model-derived portraits are included.

The normal hero magazine is the passive memory variant. Its ability ID is private to the hero so its launch coordinates can differ; each unit owns its buff memory. The separate manual eight-torpedo salvo has its own ability/buff and does not write to magazine memory. The hero's normal blue plume is 1.5× the source effect's axial size; phase travel uses 6×, hence 4× its normal length, transformed to the fitted engine opening and measured axis. Particle-hook interpretation still needs observation.

Rocinante is a separate unit. Its new archive contains actual relative PDC-cover and cannon motion, as well as global presentation movement. The printing stand is identified separately and removed only from a derivative; original archive/master remain unchanged. The user confirms permission to use it; creator, exact license and attribution requirements are not supplied. No public distribution occurs.

Main hero definitions under `build/hero03-main` define:

| Feature | Provisional configuration |
|---|---|
| Belter Ingenuity | 100 hull/s for10s,90s cooldown |
| Overcharged Reactor | 50AM,+50% maximum speed for10s,60s cooldown |
| Morale Boost | +15% natural hull/armor regeneration, same-well friendly ships;1s refresh/2s recipient linger |
| Normal torpedoes | Passive eight-round magazine; hero-specific measured launch coordinates |
| Independent salvo | Eight private torpedo entities, its own120s cooldown |
| Railgun | 2,500 raw damage,1,000 penetration,10s same-target cooldown plus stock1s acquisition delay |
| Health/AM | 3,000 hull;1,650 armor;350AM with1/s regeneration |
| Construction | 90s;3,000 credits/500metal/200crystal;25 supply |
| Acquisition | Append to TEC frigate-factory buildable list; private tag limit1 per empire |

Railgun arithmetic predicts one shot against unbuffed Cobalt/Garda under the documented damage model, not every upgraded frigate. Kodiak's ideal threshold is3,910 raw damage, so two shots; capital shields/armor require more. No global combat values change. Hero price/health/durations are local starting values for review.

The private tag uses the installed player `unit_limits.global` mechanism; it does not consume the vanilla titan allowance. Three TEC player definitions would each receive only a buildable-unit append and a private-tag limit append. This is a per-empire cap, not proof of a universe-wide or once-ever hero. Queue/capture/rebuild behavior requires testing.

Natural-regeneration modifiers do not amplify scripted repair abilities and do not bypass post-damage repair delays. Shared-aura stacking is configured fixed-one; cleanup and allied-player ownership semantics remain runtime gates.

## Reproduction and ownership

Main owns `tools/build_combat03.py`, `tools/prepare_geometry03_inputs.py`, `tools/hero03_abilities.py`, `tools/hero03_unit_candidate.py`, shared definitions/manifests and documentation. Worker A owns `tools/combat03_stage.py` and `audit/combat03-a`; B owns `tools/geometry03_*.py`, `audit/geometry03-b` and its ignored asset outputs; C owns `tools/flight03_effects.py` and `audit/flight03-c`. Workers write in separate worktrees/output directories. Shared assets, game files and SDK are read-only.

Build prerequisites remain ignored local dependencies. Use the pinned game/SDK paths from `docs/environment.md`; do not download substitutes when a dependency is missing. Current reviewed combat input is the A worker's **filtered** subdirectory; original unfiltered staging is historical only.

```bash
python3 tools/prepare_geometry03_inputs.py --worker '/run/media/haker/NVME 2/expanse-workers/tachi-one-pdc'
python3 tools/build_combat03.py \
  --game '/run/media/haker/NVME 2/SteamLibrary/steamapps/common/Sins2' \
  --sdk '/run/media/haker/NVME 2/SteamLibrary/steamapps/common/Sins of a Solar Empire II - Mod Tools' \
  --combat '/run/media/haker/NVME 2/expanse-workers/weapon-behavior/build/combat03-a/filtered' \
  --geometry build/combat03-inputs/geometry \
  --flight '/run/media/haker/NVME 2/expanse-workers/validation/build/flight03-c' \
  --torpedo-mounts '/run/media/haker/NVME 2/expanse-workers/tachi-one-pdc/audit/geometry03-b/torpedo-mounts.json'
```

The builder refuses an existing output; add `--validate-only` to check it. It never installs or enables anything. To test on the workstation, extract ZIP contents into a distinct `expanse_corvette_combat03` folder inside the existing Proton `.../AppData/Local/sins2/mods/` directory. Disable other Cobalt variants, enable this experiment and Apply Changes. Use a fresh disposable save and the ordered C03/H03 gates in the [existing checklist](manual-test-checklist.md).

Schemas cannot establish engine targeting, interception damage, timer persistence or visual correctness. There is no pinned particle-effect schema; those effects receive observed-structure and reference checks only. Missing dependency checks are blocked, never counted as passes.

## Passive-magazine reproduction

After the timed diagnostic package exists, run:

```bash
python3 tools/build_magazine03.py \
  --game '/run/media/haker/NVME 2/SteamLibrary/steamapps/common/Sins2' \
  --sdk '/run/media/haker/NVME 2/SteamLibrary/steamapps/common/Sins of a Solar Empire II - Mod Tools' \
  --persistent '/run/media/haker/NVME 2/expanse-workers/weapon-behavior/build/combat03-a/persistent'
```

This creates a separate 92-file package and never changes the timed predecessor. A worker's independent state model passed eight intended-state invariants, including no debit without a target, empty-magazine reload, no catch-up salvos and disabled-firing behavior. Those are **offline model results**, not observations of Sins II. The selector's unit-memory write is supported by the pinned schema but lacks an explicit installed usage example; test it before assuming the magazine works. Creation failures are not observable by this script, so a failed projectile creation may still debit rounds.

## Hero reproduction and checks

First generate the main ability/unit candidates and verify the B worker's final armed mesh:

```bash
python3 tools/hero03_abilities.py --game '/run/media/haker/NVME 2/SteamLibrary/steamapps/common/Sins2' --sdk '/run/media/haker/NVME 2/SteamLibrary/steamapps/common/Sins of a Solar Empire II - Mod Tools'
python3 tools/hero03_unit_candidate.py --game '/run/media/haker/NVME 2/SteamLibrary/steamapps/common/Sins2' --sdk '/run/media/haker/NVME 2/SteamLibrary/steamapps/common/Sins of a Solar Empire II - Mod Tools'
python3 tools/prepare_hero03_inputs.py --worker '/run/media/haker/NVME 2/expanse-workers/tachi-one-pdc'
python3 tools/build_hero03.py \
  --game '/run/media/haker/NVME 2/SteamLibrary/steamapps/common/Sins2' \
  --sdk '/run/media/haker/NVME 2/SteamLibrary/steamapps/common/Sins of a Solar Empire II - Mod Tools' \
  --hero-metadata '/run/media/haker/NVME 2/expanse-workers/tachi-one-pdc/audit/geometry03-b/hero-armed-equipment.json' \
  --hero-spec build/combat03-inputs/hero/integration-spec.json \
  --hero-game '/run/media/haker/NVME 2/expanse-workers/tachi-one-pdc/build/geometry03-b/hero-armed/game' \
  --ui '/run/media/haker/NVME 2/expanse-workers/validation/build/flight03-c/hero-ui' \
  --combat '/run/media/haker/NVME 2/expanse-workers/weapon-behavior/build/combat03-a/filtered' \
  --hero-abilities build/hero03-main
```

Hero validation covers 51 schema checks, seven distinct physical weapon budgets, exact compiled point positions/bases, five ability graphs, private manifests, preserved ordinary-unit/assets, and minimal player/tag edits. The tag file explicitly sets the schema-supported `overwrite_unit_tags: true`, preserves all 14 stock tags and item-access tags, and adds only the hero tag. Runtime merge/queue behavior is unobserved. Hero source-only/static and armed derivatives, source PNGs and compiled DDS/mesh files are separate; exact paths/hashes are in the B worker report and package dependency sidecar.

Final offline checks: 62 schema pins and 527 historical installed-reference hashes preserved; old installed/build/package trees unchanged; 13 corvette meshes plus one armed hero independently checked for winding and shading frames; 18 schema checks per corvette alternative and 51 for the combined hero package; explicit action/projectile/filter/effect references resolved; 19 existing regression checks passed. Two missing texture/filter-list mutations found checker gaps, which were corrected and the same negative cases then rejected. No particle-effect schema exists. No runtime result is inferred from these checks.

Smallest workstation order: **(1)** passive corvette package—loading, repaired geometry, barrel supports and uninterrupted torpedo timing; **(2)** target loss/orders/interception plus mid-magazine and mid-reload saves; **(3)** orbit/phase alignment; **(4)** hero package alone—construction cap, static muzzles, railgun, independent salvo, repair/AM/aura; **(5)** destruction/save reload and formation/fleet performance. Use the older timed package only to isolate a passive-selector failure. A closer friendly ship beside an eligible enemy is an essential selector test: establish whether filtering occurs before the one-target limit.
