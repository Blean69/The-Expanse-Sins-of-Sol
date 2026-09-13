# The Expanse — Sins II corvette prototype

**Current update: [0.14 Hull and firing arc correction](docs/update14.md).** Fixes the Scirocco's inward-facing exterior, restores original Raptor/Pella hull and engine detail, and restricts their PDC arcs with tighter aiming tolerances. Includes the complete 0.13 fleet and audio. Offline checks pass; new runtime tests remain NOT RUN. Earlier packages, installed mods and enabled settings are preserved.

The user has now observed **individual PDC tracking and good tracer appearance** in the polish prototype. Residual hull holes and floating turret supports remain recorded defects. The working **0.2.1** package and installed copy are preserved. New work is staged separately under `build/experiments/expanse_corvette_ammo03` and `build/experiments/expanse_rocinante03`; see [0.3 handoff](docs/combat03.md) for exact package availability and runtime limits.

Start with the [0.3 build/load handoff](docs/combat03.md) and C03/H03 tests in the [existing manual checklist](docs/manual-test-checklist.md). The [polish guide](docs/polish.md) documents the preserved working 0.2.1 version.

The user has tested the older `expanse_cobalt_name` and `expanse_corvette_visual` together: model loading and fixed-muzzle firing worked, but hull holes were visible. [Runtime results and screenshot evidence](audit/manual-results.md) distinguish those observations from untested features. Both installed baselines and all prior packages remain unchanged.

The supported corvette derivative has **16,335 triangles**; the stand-free armed hero has **26,935**. Both retain six PDC assemblies. The hero starts with static deployed geometry; its animation is preserved separately. Original archive/extracted master remain untouched. Editable geometry and UI sources are separate from generated game files. [Asset sources and permissions](ASSET-SOURCES.md) apply to both model and rendered UI imagery.

Use the recorded **Sins II 2.0.3 (318), Steam build 25127248**, and pinned official SDK schema commit `8e061033afe53b1393eaefd56617a3fd041eeb5f`. Dependencies have not been updated. See [environment evidence](docs/environment.md), [Cobalt reference trace](docs/cobalt-reference-trace.md), and [asset audit](docs/asset-audit.md).

PDC rates are provisional; no exact TV RPM is claimed. Interception priority during a ship attack order, actual damage cadence, turret arcs and fleet performance still require observation. The passive torpedo magazine and hero abilities are now packaged experiments; engine timing, targeting and save behavior remain unverified. The shared Cobalt scope includes applicable neutral/garrison uses. Only the hero package appends its private unit to TEC build lists and adds a one-per-empire tag limit; no faction redesign is included.

The [earlier experiment handoff](docs/experiments.md) preserves historical stock-Garda/Ogrov and one-turret work. [Audio feasibility](docs/audio-feasibility.md) records local candidates and unresolved permissions without integrating clips.

Repository: [The Expanse: Sins of Sol](https://github.com/Blean69/The-Expanse-Sins-of-Sol). Assets, SDK dependencies and packages are ignored by Git. The user authorized pushing project source and documentation; model/audio derivatives are not included in that source push.
# Current follow-up:0.4

The latest optional [Amun torpedo appearance variant](docs/torpedo05.md) includes the complete corrected 0.4 ships and the extracted custom missile. Load it alone instead of other Expanse variants. [Amun stealth/boarding work](docs/amun05.md) remains separate candidates with documented schema and runtime gaps.

The latest work is documented in [combined0.4](docs/combat04.md) and [Donnager groundwork](docs/donnager04.md). Existing installed mods and0.3 outputs remain preserved. New0.4 results require their own workstation tests; successful earlier movement/railgun observations are recorded separately from untested changes.

## Current Amun-Ra follow-up

User-observed custom torpedoes, Rocinante appearance/PDC tracking and unique-hero performance are accepted. Keep that geometry budget. See [Amun0.6](docs/amun06.md) for the additive three-PDC ship, accepted timed boarding visual, separately checked cloak experiment and next workstation gates. New Amun runtime tests remain NOT RUN.

## Rocinante voice follow-up

[Voice0.7](docs/voice07.md) adds eleven normalized supplied lines through separate core/cloak combined variants. Original audio and currently tested packages are unchanged; new dialogue runtime tests remain NOT RUN.

## Ability control correction0.8

[Update0.8](docs/update08.md) corrects alternative ability-set grouping on Amun/Rocinante and adds six normalized recordings (17 total). Use the cloak variant to test stealth; the previous enabled0.7 core variant had no cloak. Runtime confirmation is pending.

## Current combined update0.9

[Update0.9](docs/music09.md) includes corrected ability controls,17 Rocinante voices and15 supplied soundtrack tracks. Boarded/Welwala/Signal/Never See Them Coming/Hammerlock are combat tracks; Signal starts at1:05. Use `expanse_amun09_cloak` alone to test stealth. Nothing was installed or enabled by the agent.
