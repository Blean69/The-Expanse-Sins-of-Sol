# 0.4 weapon and carrier audit — Worker A

Ownership: `tools/combat04*.py`, this audit directory, and ignored `build/combat04-a` in the weapon-behavior worktree. All previous stages, main packages, installed game and SDK were read-only. No install, game launch, dependency update, commit or publication.

## Light torpedo ready for integration

Use `build/combat04-a/light-final/entities/expanse04_light_torpedo.{unit,unit_skin}`. Full changed normal/hero buffs and ADS are in `build/combat04-a/integration/entities`; `exact-patches.json` supplies RFC6902 test/replace operations against the current combined `expanse_rocinante03` package, with source hashes. Main owns assembly, manifests, launching ship skins and localization.

The actual installed **Javelis LRM Cruiser** is `trader_long_range_cruiser`, not `trader_antiarmor_frigate`; the latter is localized **Kalev Gauss Frigate**. Javelis weapon `trader_long_range_cruiser_medium_missile` spawns `trader_medium_torpedo`. Current `expanse03_heavy_torpedo` uses the Ogrov projectile. Both units have the `torpedo` component and `target_filter_unit_type: torpedo`.

| Observed value | Current Ogrov-derived | Installed Javelis | New private light candidate |
|---|---:|---:|---:|
| Mesh full longitudinal length | 272.0826 | 16.5108 | 16.5108 |
| Spatial radius | 136.1605 | 8.2743 | 8.2743 |
| Mesh triangles | 908 | 3,076 | 3,076 (reference) |
| Maximum speed | 1,000 | 1,750 | 1,250 |
| Time to maximum linear speed | 2 s | 7 s | 1.5 s |
| Maximum angular speed | 15°/s | 75°/s | 22.5°/s |
| Time to maximum angular speed | 2 s | 3 s | 1.5 s |
| Hull / armor / armor strength | 50 / 100 / 50 | 5 / 10 / 25 | 50 / 100 / 50 |

Bounds come from both installed `.unit` data and parsed actual `.mesh` headers. New mesh length is 6.07% of the current projectile. No rescale, mesh conversion or copied vanilla binaries are needed. Private skin references the installed Javelis mesh, material, textures, trail and death effect. Its smaller camera-distance settings also come from Javelis. Only GUI name/description become private localized keys.

The four physics edits are provisional, supported fields—not claims of a canonical speed or a verified hit rate. Linear acceleration inferred from a simple speed/time ratio rises from 500 to 833.3 units/s²; the engine's actual easing is not established. Angular ramp similarly increases. Unchanged strafe and braking fields retain the current heavy projectile behavior.

Damage **750**, penetration **1,000**, lifetime **240 s**, range **200,000** plus same-well filter, health and normal **8-round / 2 per 10 s / 120 s after empty** state machine are untouched. Normal+hero salvo tooltip speed is updated to 1,250. Independent hero salvo capacity/cooldown is unchanged. Railgun bytes remain 2,500 damage / 1,000 penetration / 10 s. A smaller collider and faster approach affect interception opportunity even when damage and ammo remain identical.

Both normal magazine and hero salvo launch actions replace the old heavy muzzle alias with `expanse04_light_torpedo_muzzle`, bound to installed `javelis_torpedo_muzzle` and its stock sound alternatives. Add that alias to both Cobalt and Rocinante skins. This avoids retaining a huge Ogrov launch plume around the smaller projectile. Existing launch coordinates and muzzle sequencing remain main-owned and unchanged by this patch.

The original `expanse03_heavy_torpedo` remains intact in all prior stages/packages as a large Ogrov-style Donnager option. It is unused in the new light-only integration and should be omitted from that package. A future Donnager-specific copy needs a distinct ID when any behavior changes.

## Carrier implementation findings

Sova `trader_carrier_capital_ship.unit` already has `unit_factory.build_kinds: ["corvette"]`, a base build point and `required_mutation: mobile_unit_factory_enabled`. Its `trader_carrier_capital_ship_mobile_unit_factory.ability` applies a persistent buff, exposes GUI action `toggle_unit_factory_window`, and the buff supplies that mutation and a build-time modifier. The corresponding three-level ADS gives build-time scalar bonuses 0, −0.15, −0.40. This is a concrete native queue path with ordinary resource/supply/construction behavior, unlike an invented spawn mechanism.

**Current MCRN Corvette-class is still Cobalt's `build_kind: frigate`.** A Donnager with Sova's corvette-only factory cannot produce it. The narrowest native candidate is a factory attached only to the new Donnager with `build_kinds: ["frigate"]`, a model-verified hangar build point, and a private copy of Sova's fixed-level factory ability/buff/ADS (start with no build-time bonus). This would expose other player-available frigates too. The pinned `unit_factory_definition` has no specific-unit whitelist: fields are build_kinds, build_rate_scalar, rally offset, required_ability, required_mutation, hyperspace-spawn options and build point. Do not silently change Cobalt's build kind or faction menus to hide this limitation.

If **only** MCRN corvettes may be produced, an explicit costed reinforcement ability is another supported local experiment. `trader_pirate_mercenary_base_unit_item.ability` combines `spawn_units`, caster ownership, supply constraints, credit cost and cooldown. `vasari_overseer_tower.ability` demonstrates `units.required_units` with `{unit, count:[1,1]}`. The schema supports `metal_cost` and `crystal_cost` too. Use one required `trader_light_frigate` (the shared MCRN baseline), real current supply/cost values, `constrain_available_supply_to_owner_player: true`, and research prerequisites enabled. This is a reinforcement ability, **not a native build queue**; creation/cost atomicity, refunds, hangar positioning and carrier-death during delayed arrival require tests. It must not be advertised as ordinary construction until observed.

The installed `trader_carrier_capital_ship_rapid_manufacturing.ability` uses `spawn_detached_strikecraft`. That is not a drop-in corvette construction mechanism. Do not use it to claim ordinary MCRN corvettes are built. Carrier manufacturing is the recommended first Donnager ability experiment; stage extra combat buffs only after main chooses hull class/role and mounting budgets. No faction, research tree or global modifier change is needed for the local factory proposal.

## Local balance anchors for Donnager

These are installed unbuffed starting values, not a final Donnager tuning proposal. Full mount counts and individual weapon definitions are captured in `carrier-evidence.json`.

| Ship | Supply | Credits / metal / crystal | Build seconds | Hull / armor / shields | Durability |
|---|---:|---|---:|---|---:|
| Kol | 50 | 2,500 / 850 / 600 | 75 | 3,750 / 2,420 / 2,650 | 500 |
| Sova | 50 | 2,500 / 850 / 600 | 75 | 4,585 / 1,610 / 1,650 | 500 |
| Ragnarov | 150 | 9,600 / 2,900 / 1,900 | 300 | 12,800 / 4,425 / 6,575 | 750 |
| Ankylon | 150 | 9,600 / 2,900 / 1,900 | 300 | 14,520 / 5,000 / 6,000 | 750 |

Exotics and prerequisites are also in the JSON; table currency columns omit exotics for readability. Kol has two 150-damage / 600-penetration / 10-second gauss mounts. Ragnarov has sixteen such gauss mounts, plus one 750 / 1,000 / 10 railgun definition. Sova has nine stock 4 / 0 / 1 point-defense mounts; Ragnarov fourteen and Ankylon twenty-two. Their arcs, item unlocks, level bonuses, different engagement distances and simultaneous bearing limit realized damage.

The experimental corvette's PDC is 28 / 0 / 0.25 per gun: 112 raw DPS before mitigation. Six bearing guns give 672 raw DPS. Do not simply multiply that by a large Donnager's proposed mount count and call it balanced. Main should set a whole-ship PDC budget first and divide among physical mounts, accounting for overlap. Keep the accepted Rocinante railgun unchanged; do not silently assign each future Donnager rail the hero's 2,500 damage. Ogrov-sized future torpedoes can remain a separate class, with ammunition and aggregate salvo budgets specified before tuning.

## Checks actually run

- `combat04_stage.py --output build/combat04-a/light-final`: **PASS**, 62 pinned schema blobs match; two private entity schemas; exact top-level delta limited to spatial/physics/skin; retained health, target eligibility and torpedo marker; previous heavy source hash unchanged; 80 installed files hashed, including mesh/material/texture/trail, death sequence → impact particle → textures, muzzle particle → textures, and engine/muzzle/death sound+OGG files.
- Initial case-sensitive sound probe reported missing `engine_techsupportship.sound`. Inspection found actual `ENGINE_TECHSUPPORTSHIP.sound` and other uppercase stock paths. Resolver now records the actual unique case-insensitive path instead of falsely treating these dependencies as absent. No substitute sound was downloaded or created.
- `combat04_integrate.py --base .../expanse_rocinante03 --sdk ...`: **PASS**, four changed buff/ADS schemas and exact replacement pointers generated. All other buff/ADS fields remain identical to source.
- `validate_package(package, base03, sdk, lightFinal)` is callable for main's final combined package. It asserts six schemas, exact approved changes, manifests, both launch aliases, no remaining active heavy projectile references, and byte-preserved railgun. It supplements the complete package reference checker. Its complete-package result is pending main assembly; it is not listed as already passed here.
- All game/runtime checks: **NOT RUN by worker**. No particle-effect schema is present; nested texture resolution is an offline dependency check, not particle schema validation.

Next workstation gates: inspect projectile and plume scale at each ordinary/hero port; confirm torpedoes turn and hit nearby/moving targets without looping; verify enemy PDC eligibility and actual damage against smaller collider/unchanged health; compare defensive response time; repeat uninterrupted 8-round cycle, target loss, movement orders, mid-magazine/mid-reload saves; confirm unchanged railgun; measure many simultaneous missiles. Carrier queue/spawn tests are separate from light-torpedo acceptance.
