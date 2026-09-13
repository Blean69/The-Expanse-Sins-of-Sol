# Read-only review — assembled corvette 0.3

Reviewed main `tools/build_combat03.py` and `build/experiments/expanse_corvette_combat03`. No main, installed, or 0.2.1 files were edited. `build/flight03-c/checks/` contains check outputs; temporary negative-test fixtures were removed. Main package hashes were compared before/after the tests and remained unchanged.

The main `check_package` passed with 18 schema checks, one ability, one spawned buff and one spawned torpedo chain. Independent checks covered all 13 new meshes: each binary material-ID set equals the geometry worker's mapping, every copied material file is byte-equal to that mapped source, and every primitive material index is within range. The new hull's `exhaust.0` point and rotation exactly match the 0.2 nozzle used by the private phase-plume recipe. The frozen baseline/0.2.1/source/install/SDK check passed.

## Concrete checker gaps found and resolved by main

1. Particle texture lookup originally checked only keys ending in `texture`, omitting `texture_0`/`texture_1`. An injected missing `texture_0` passed validation.
2. Ability action traversal originally skipped string values inside `target_filters[]`. An injected nonexistent targeting-filter ID passed validation.

The main integrator fixed both loops. Rerunning only those two negative cases now rejects both with explicit missing-reference diagnostics. `negative-check-results.json` records the initial findings, and `negative-check-retest.json` records successful rejection after the fix. A missing inherited projectile skin was already correctly rejected. None of these injected defects exists in the reviewed actual package.

## Integration findings

- Ability → action-data source → on-self buff → create_torpedo follows the installed Ogrov heavy-torpedo ability pattern. The buff retains `source_ability` position context and `current_spawner` launch ownership. All referenced scalar IDs resolve in the originating ADS. Per-launch filter recheck exists in the timed action; same-well constraints are present on all three targeting filters.
- Two ability positions use the geometry worker's measured launch coordinates and orthogonal bases. The sequential selector, two executions per interval, four intervals, 10-second interval and zero first delay author the intended paired cycle. Actual event timing, eight projectile creations and muzzle effects remain runtime tests.
- The private projectile unit deliberately inherits `trader_torpedo_cruiser_torpedo.unit_skin`. That installed skin and its mesh/material/exhaust/texture dependencies resolve; a redundant private skin copy/manifest is unnecessary. Torpedo component, target-filter type and AI target type remain classified as torpedo. Interception effectiveness still requires actual hits and prevented impact damage.
- Six working PDC definitions and mounts are preserved; old aliases are bound to the renamed 0.3 meshes. The original effect aliases are preserved and the Ogrov muzzle alias is appended. No hero ability or railgun files leaked into the ordinary corvette package.
- Private phase effect references resolve, including `texture_0`/`texture_1` after the checker fix. Particle schemas remain unavailable; structural/source checks are not a claim of effect rendering correctness.

No remaining concrete malformed-reference or mesh/material integration defect was found in this snapshot.

## Runtime boundaries

The engine's buff source/target context retention, channel cancellation, cooldown starting after the last interval, target death/phase departure/capture, and save/reload must be observed. The same-well check runs before a launch; it does not prove what an already flying projectile does after its target changes wells. Likewise, 200,000 ability range and 240-second life author a long-range experiment, not unrestricted reach in every possible well.

The ship's `max_range_weapon_index` still points at PDC mount 0; its ordinary weapon list contains PDCs, while torpedoes are an ability. Thus the ability's range does not establish the normal attack/circle_strafe standoff distance. The engine may close to PDC range, interrupt circling to align the ability, or retain channeling alignment. These are direct workstation gates, not reasons to invent a movement field.

Phase-plume node placement uses a verified nozzle transform, but the phase hook's runtime origin and interaction with normal exhaust remain unobserved. New mesh backface appearance, turret aiming/muzzle alignment, and large-fleet performance remain outside offline reference validation.

All runtime tests: NOT RUN by this worker.
