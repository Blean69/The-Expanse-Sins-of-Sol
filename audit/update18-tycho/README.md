# Tycho-pattern Arsenal — disabled mechanics candidate

The five definitions in `build/laboratory/update18/station/entities` use the **existing TEC starbase mesh**. They are not an import of the supplied Tycho art. Rebuild with `python3 tools/update18_tycho.py`. Nothing is installed, enabled, registered in playable factions, or pushed. Full manifests, shared research, private-tag registration, localization and final art are integrator-owned.

## What is implemented offline

- A stationary, shieldless starbase clone, with native immobile attack behavior and slow angular rotation.
- Sixteen native light-turret placements, their frame vectors and arcs copied exactly. Each uses native biaxial base/barrel meshes plus the working mod's dual-purpose PDC behavior and effects. PDC definition: 10 damage, 0.25-second reload, 180 degrees/second tracking, 7,000 range, zero pierce. All 16 simultaneously bearing would be a theoretical 640 raw damage/second before defenses; actual arcs/interception reduce usable output.
- Four native missile-bank placements, each launches **one actual destructible `trader_medium_torpedo` every 12 seconds**, 300 weapon damage, 750 pierce, 12,000 range. Four simultaneously bearing would be 100 raw damage/second. Native `spawn_torpedo` behavior is used; these are not cosmetic pod effects. Counterplay still needs in-game testing.
- Prototype defense: 75,000 hull, 20,000 armor points, armor strength 200, durability 1,500. Native out-of-combat hull/armor recovery retained. No shields or shield burst; working `expanse11_no_shields` remains attached.
- Initial cost: 10,000 credits, 3,000 metal, 2,000 crystal and two existing defense exotics; 600-second base construction. No ProtoTech Composite requirement. These are new prototype values, not claimed balanced or runtime-observed.
- Three native ship-component slots. Exactly one authored module so far: Industrial Drydock. One copy per station. Native price 1,200 credits / 240 metal / 240 crystal; native 120-second module build time.

Industrial Drydock uses native `mobile_unit_factory_enabled` mutation and `toggle_unit_factory_window` GUI action. It enables **the station's own** corvette/frigate/cruiser factory. Its `unit_factory_modifiers.build_time` scalar is `(1 / 1.15) - 1 = -0.1304347826`, meaning 15% greater base construction rate / about 13.04% less base time in isolation. It does not buff other factories, the whole empire, neighboring wells or visiting ships. Research/other scalar modifiers can change the resulting combined rate; the description says base rate deliberately. Factory throughput and removal/capture during a queue must be tested.

No Heavy Ordnance, Repair Anchorage, Defense Coordination aura, Emergency Lockdown, trade port, strikecraft carrier, phase jamming, or free visitor repair is active. This deliberately avoids adding unverified targeting, stacking or unlimited percentage healing. Three available slots is not a claim of a completed choose-three-of-four upgrade system.

## Limits and inherited behavior

The unit has only the private tag `expanse18_tycho_arsenal`, **not** the generic `starbase` tag. It retains native `build_kind: starbase` and `target_filter_unit_type: starbase` so construction/combat taxonomy is intact. The integration recipe appends native `unit_limits.global: [{tag: expanse18_tycho_arsenal, unit_limit: 1}]` to each player's wrapper and registers the private tag/localized label.

This is a proposed native per-owner limit, **not proof** that it counts queued/constructing copies or prevents acquisition of a second captured station. Excluding the generic starbase tag avoids intentionally inheriting TEC per-planet/per-star tag limits and generic starbase-only component eligibility. Research/auras filtered by `target_filter_unit_type: starbase`, broad weapon tags or all units can still apply. Existing ownership-scoped hull/armor/physical/PDC research continues where its filters match. Existing explicit per-weapon native starbase 25% upgrade modifiers were removed from the new torpedo weapon; the PDC donor has none. Station defense still inherits the native `min_detection_level: 1` installed extension; this is not ordinary vision and must be included in stealth interaction testing.

The schema audit records the unchanged installed `corruption` field and unchanged `min_detection_level` enum as inherited extensions, not official pinned-schema support. All new authored fields pass the pinned schema. Mount/frame/arc identity checks and matching unit-AI/PDC target groups pass offline. Main weapons, costs and ship definitions in 0.17 are untouched.

Existing `trader_unlock_starbase` and `trader_unlock_starbase_unit_factory_unit_item` prerequisites remain in this disabled fragment. The integrator must attach the future themed shared unlock nodes, not leave an unregistered fake research reference. The factory follows each owner's maintained common ship inventory; no independent faction-specific rosters are generated here.

The neutral `expanse18_tycho_bureau` contact never receives this station tag and must not consume the allowance. Native one-time starbase wreckage is retained; no new wreck-every-death or salvage reward system is introduced.

## Runtime acceptance still required

All listed runtime cases are **NOT RUN**, including multiplayer (0 minutes):

1. Build from each faction with required research, verify price/time, legal placement, constructor behavior and private-tag GUI. Verify another queued/constructing/completed copy is denied across different wells; cancel or destroy then rebuild. Check captured stations, capture during construction, owner defeat, save/reload and concurrent orders from clients.
2. Place a normal starbase beside Tycho before/after native TEC starbase-limit research. Confirm intended coexistence without changing normal station limits. Check generic starbase items cannot be fitted and the private Drydock can be fitted once. Test all three slots and capture item eligibility.
3. Verify all 16 PDCs visibly track, fire at ships and intercept real torpedoes; note actual coverage/blind spots and self-hull firing. Verify four torpedo banks actually fire and each spawned object can be destroyed to prevent its impact. Confirm no hidden original medium/beam/PDC weapons remain mechanically active. Native placeholder geometry may still show cosmetic empty turret locations.
4. Test unsupported raids, supported multi-direction attacks, saturating missiles and long-range siege. Record damage output and defense survival before adjusting values. No claim of balance from aggregate raw DPS.
5. Verify the Drydock toggles the factory and produces the owner's shared roster; compare a fixed ship's base build duration before/with module in a controlled test. No other nearby factory or neighboring well should speed up. Capture/remove/destroy during queues, full supply, canceled purchases and save/reload must behave natively without duplicate ships/refunds.
6. Confirm no shields return via research, items, capture or load; test native detection against existing stealth. Test repair support from Scirocco normally without adding a station repair aura.
7. Repeat geometry origin checks after the final Tycho model replaces the placeholder; native TEC mount coordinates must not be reused blindly on a different hull.
