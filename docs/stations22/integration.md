# Stage 3 support-station fragments

`tools/update22_stations.py` exposes `changes(base,prefix='expanse22') -> (edits,strings,origins,report)`. The base should be the integrator's current candidate. This emits only **new** entities and strings. Main owns manifests, player access, unit-tag registration and research graph changes. No installed game file or existing hull/weapon definition is changed.

## Structures

| Definition | Hull / armor | Cost credits / metal / crystal | Time | Military slots | Base weapons |
|---|---:|---:|---:|---:|---|
| expanse22_mcrn_support_station |12000 /4500|4000 /900 /700|240s|8|4×117.6DPS PDC|
| expanse22_unn_support_station |12000 /4500|4000 /900 /700|240s|8|4×85DPS PDC|
| expanse22_opa_support_station |12000 /4500|4000 /900 /700|240s|8|4×85DPS PDC|
| expanse22_pdc_picket |4000 /1500|1200 /250 /100|80s|3|4×85DPS PDC|

All are shieldless. Major stations use the matching native TEC starbase hull with four selected physical PDC mounts, retaining native mount positions, facing and arcs. The picket uses the matching native hangar hull and four actual native PDC mounts, with carrier/strikecraft functionality removed. This is disclosed placeholder art, not an imported Tycho or new canonical class. Major-station durability600 and armor strength75; picket retains native durability600/armor strength40. Normal military infrastructure costs apply; no fleet-supply charge is authored.

A shared `expanse22_major_support_station` unit tag gives a **one-total-per-player** major-station limit across all three aliases, even in the combined sandbox. Asymmetric access lists contain only the appropriate faction's major station plus the common picket. Captured excess is retained; further ordinary builds should remain blocked by the native shared-tag limit until below one. Queued builds, capture, cancellation and rebuilding semantics are NOT RUN. Do not claim the array alone proves them.

Major stations also provide the native ship-component shop service. Their underlying build prerequisite currently uses the valid native `trader_unlock_starbase`; main may replace it with an implemented appropriate node. The picket preserves the valid native hangar-defense unlock. Main must make those prerequisite nodes available in each intended owner tree, or deliberately substitute an existing comparable unlock.

## Three normal slots, four real modules

Every major station has three actual normal equipment slots. Each module occupies one, costs700credits/150metal/100crystal and takes60seconds. One copy of each module is allowed. Item eligibility uses the shared major-station tag, so ordinary capitals, vanilla starbases and the small picket do not gain these items.

- **Ordnance Control:** enables two physical native torpedo-bank mounts. Both retain the existing missile-defense-platform profile exactly:300damage,2shots per8seconds,10000range,30second fuel and the same destructible projectile type. It requires an explicit attack order, as the source platform does. These are separate defensive stores, not a ship-magazine refill. This module is intentionally a modest missile alternative rather than falsely advertising a heavy railgun on an incompatible native turret. The separately implemented Foehammer battery provides the heavy-gun role.
- **Repair Anchorage:** the living station scans within6000 once per simulation second and repairs20hull on at most3eligible owned ships. Maximum calculated throughput60hull/second, irrespective of target max hull. Targets must be fully built, missing at least20hull and not already under the shared station reservation, Scirocco engineering, native retrofit repair or native combat repair. Target selection uses the native distance sort; no unsupported smartest-heal reservation claim is made. The shared one-second reservation includes pending buffs to prevent same-effect repairs from overlapping stations. It adds no healing itself. All healing happens at the living source, so losing the source does not leave a detached repair timer. The existing Stage2 UNN Fleet Train component uses the Scirocco buff and is therefore excluded too.
- **Defense Coordination:** owned armed ships within6000 receive +10% `tracking_speed` tagged only `point_defense`. No range, damage or reload modifier. The native targeting-array parent/child-buff mechanism removes the effect when the parent dies or the target exceeds6000. Fixed-one all-player stacking prevents additive copies.
- **Industrial Drydock:** owned functional orbital ship factories (structure type) within6000 receive a build-time scalar of1/1.10−1, yielding10% more base production **rate**, about9.09% less base time. This is a local factory aura; it does not enable the station's own shipyard, modify global costs or reset ammunition. Native parent death, target distance and fixed-one stacking apply.

All beneficial filters are **owned only**, not automatically allied. Stations and decorative/projectile objects are excluded from repair/tracking because those filters list ordinary ship classes. The industrial filter admits functional orbital factories only. Ownership-change cleanup is present; save/reload and capture behavior require runtime checks.

MCRN Naval Readiness has an exported hook for a later owner-specific20→22repair-per-pulse level, only if its real research node is integrated. No unconditional global +10% healing is applied. Preserve the already implemented `expanse21_unn_fleet_train` and component; do not repurpose that node as a redundant station unlock. OPA advanced salvage services and paid UNN mobilization remain separately integrated abilities/research, not promises on these modules.

## Main merge recipe

1. Copy the returned new entity definitions. Register each suffix in its corresponding manifest and merge returned strings.
2. Merge `report.unit_tag_entries_append` by tag name into the current explicit registry. Never add these to the weapon-tag registry.
3. For each asymmetric owner, merge that faction's `report.player_recipes` structures, ship components and shared global limit. Combined Fleet Sandbox uses `report.combined_sandbox` and the same one-total limit.
4. Preserve prerequisite costs/tiers, or connect a real Stage3-specific unlock. No unimplemented research promise should become purchaseable.
5. Validate loading/controls, weapon origins and fitting slots; then verify the runtime cases below.

## Checks and limits

`python3 tools/update22_stations_check.py` emits the review overlay under `build/stations22-fragments` and audit `audit/stations22/validation.json`.28definitions pass extension-aware schema checks. Narrow checks confirm:

- Private weapon damage, penetration, cadence, burst, range, projectile identity and fuel match their accepted donors; only names and compatible turret-mesh binding differ.
- Native station hull/mount/arc pairs are preserved, with four PDCs plus two equipment-gated banks.
- Four choices compete for three slots; shared-tag limit recipe is one total.
- Shield guards remain and optional zero-percentage burst objects are absent.
- Owned-only filters,3×20repair bound, pending reservation and existing active-repair exclusion are authored.
- Native explicit distance and parent cleanup is present; tracking affects only PDCs; industrial arithmetic is rate-correct.
- Every station weapon-effect alias resolves through its skin.

**Runtime NOT RUN:** fresh load and all construct menus, simultaneous/queued limits, modules and full slots, 3-target selection, overlapping source scan ordering, repair/capture/source-loss interactions, leaving range, native research stacking, actual factory timing, turret coverage and projectile origins, save/reload, multiplayer. Calculated throughput is not an observed healing test. No assets were installed, game launched or repository pushed.
