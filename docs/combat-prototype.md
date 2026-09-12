# Next change: corvette combat prototype

This follows the visual baseline. `build/combat-candidates` contains nine schema-checked definition candidates and additive manifests. It has no `.mod_meta_data`, no Cobalt override, and is not installed. It is **not a playable combat mod**. Inspect `audit/combat-candidate-validation.json` for unresolved integration dependencies.

The agreed design is one ordinary, buildable MCRN corvette; six rotating hull-mounted PDC assemblies; high close-range DPS with low penetration; a small salvo of accurate, highly damaging, interceptable torpedoes; eventual engagement across the same gravity well; and rapid loss when defenses are saturated. Higher ship costs and quality over quantity are future tuning goals for this ship, not permission to rebalance the economy. No railgun, stealth, flip-and-burn, faction, research, AI or economy redesign is included.

## Verified Ogrov chain

`entities/trader_torpedo_cruiser.unit` references `trader_torpedo_cruiser_torpedo.weapon`. That weapon uses `firing.firing_type = spawn_torpedo` and `firing.torpedo_firing_definition.spawned_unit = trader_torpedo_cruiser_torpedo`. This resolves to `entities/trader_torpedo_cruiser_torpedo.unit`, which selects its same-name `.unit_skin`. The trace continues through projectile mesh, material, textures, exhaust, impact aliases, death effects and audio in `audit/reference-edges.csv`.

| Installed Ogrov field | Value |
|---|---:|
| Weapon range | 12,000 |
| Cooldown | 30 s |
| Damage / penetration | 750 / 1,000 |
| Spawned torpedo duration | 30 s |
| Projectile speed / time to max speed | 1,000 / 2 s |
| Projectile hull / armor / armor strength | 50 / 100 / 50 |
| Projectile durability | **Not explicitly present** in the unit; do not invent an observed value |
| Projectile target-filter type | `torpedo` |
| Projectile AI attack-target type | `torpedo` |

The weapon uses `common_weapon`, groups `defense_starbase_titan` and `capital`, and `order_target_only`. These groups exclude many small ships. Merely raising range does not implement the desired target eligibility.

The isolated draft copies are `mcrn_corvette_torpedo.weapon`, `.unit`, and `.unit_skin`. Only their internal identity references change; inherited kinetics, damage, range and lifetime remain unchanged at this isolation stage. The skin still references existing vanilla visual dependencies. The future ship skin must include Ogrov muzzle aliases. Any later modified projectile, weapon, effect or skin gets its own `mcrn_*` ID rather than altering shared definitions.

**Gravity-well reach:** the current weapon schema exposes numeric `range`, not an observed “same gravity well” range field. A large number is an experiment, not proof of unlimited same-well engagement. Test opposite-edge positions in the largest controlled well, target visibility, auto-acquisition, attack orders and whether targets in another well stay ineligible. Lifespan must exceed flight time plus acceleration/turning margin: 30 seconds at 1,000 speed cannot support arbitrary well-wide distances. Inspect the actual chosen well size, then set the mod-specific range and projectile duration/speed together. Leave navigation vanilla.

**Salvos:** multiple muzzle positions and `effects.burst_pattern` do not prove multiple damaging torpedo units spawn. Count projectile entities in the runtime test. Inspect the spawn-torpedo implementation exposed by schemas/examples before choosing the salvo mechanism. Do not substitute a purely visual projectile and call it interceptable.

## Verified Garda PDC chain

`entities/trader_antifighter_frigate.unit` mounts six copies of `trader_antifighter_frigate_point_defense_autocannon.weapon`. It also has a separate research-gated light autocannon. That second weapon is **not** a model for duplicating each physical PDC's firing budget.

Installed PDC: damage 2, penetration 0, cooldown 1 s, range 5,000, projectile travel speed 6,000, yaw/pitch speed 125, `always_check_is_dead_soon = true`, `acquire_target_logic = best_target_in_range`. The `point_defense` tag is present. Its target filter is `common_and_strikecraft_and_torpedo_weapon`; its groups contain only `torpedo_strikecraft`.

`uniforms/target_filter.uniforms` shows that filter permits enemy capital ships, corvettes, cruisers, frigates, starbases, strikecraft, structures, super-capital ships, titans and torpedoes. **The group restriction is narrower than the filter.** `uniforms/attack_target_type_group.uniforms` maps `torpedo_strikecraft` to `[torpedo, strikecraft]`; `corvette`, `light` and `flak` each map to the corresponding actual type. The eligibility candidates widen the group's list to those four verified groups. They retain Garda damage/rate so the first experiment isolates target logic.

Six candidate weapon definitions each reference one base alias and one barrel alias. Each physical gun gets **one** weapon entry shared between anti-ship and interception duties. Candidate local coordinates and part assignments are in `audit/pdc-rig-candidates.json`; no candidate is currently mounted in-game. The installed Garda `unit_skin` demonstrates the actual `child_mesh_alias_bindings.map` → `mesh_alias_name` / `mesh_definition` relationship and `turret.type = biaxial`, `biaxial_base_mesh`, `biaxial_barrel_mesh`, `barrel_position`, and `muzzle_positions` fields.

`best_target_in_range` is the verified candidate for independent target acquisition while the ship has an attack order. Placing `torpedo_strikecraft` first expresses the intended preference but does **not** establish strict priority or immediate preemption. Inspect and observe acquisition, persistence, dead-soon avoidance, cooldown and tracking. If the engine will not reliably preempt ship targets, report that limitation before attempting any workaround. Do not create parallel full-rate anti-ship and anti-torpedo weapons on the same gun.

## Damage and tuning

Eligibility is not effectiveness. The widened vanilla PDC is still only damage 2 / cooldown 1 / penetration 0. Check actual damage events, durability, armor strength, armor pool and hull pool independently. Do not multiply DPS by a visual burst's length without observing the engine's damage cadence.

The [official combat guide](https://stardock.atlassian.net/wiki/spaces/SSEFW/pages/1762066537/Combat%2BGuide) describes effective durability as `max(durability - penetration, 0)`, with damage scaled by `100 / (100 + effective durability)`. Armor applies a further `100 / (100 + armor strength)` factor while damage hits the armor pool. Penetration does not remove armor strength. Confirm the current executable's observed result against that documented model.

For a controlled unupgraded Cobalt target (durability 150, armor 825, armor strength 50, hull 750), a **zero-penetration** weapon needs about 4,968.75 raw damage to remove both pools in that simplified model. A 15-second target therefore needs roughly 331.25 raw DPS **from guns whose arcs actually cover the target**, ignoring regeneration, misses, shields, buffs and tracking time. This is a calculation, not an observed kill time or a committed balance setting. Shield research and TEC faction bonuses can invalidate a casual comparison.

Tune one ship and controlled targets after the baseline passes. Record raw and effective per-gun DPS, overlap count, interception success vs salvo size, and time-to-kill. Keep long-range torpedoes as the chosen `max_range_weapon_index` candidate so the unit is not deliberately configured around its short-range PDCs; verify stop-and-fire behavior and range selection before claiming standoff works. Preserve all vanilla physics and navigation. Six 360° guns are not realistic coverage: derive hull-obstructed yaw/pitch arcs from actual mounting surfaces.

Remaining integration: compiler-ready rig export, combat hull without duplicate static guns, twelve skin alias bindings, six weapon mounts, torpedo aperture locations, real salvo spawning, long-range lifetime/range experiment, and ship-only damage/health/cost tuning. All are tracked as pending, with runtime tests in the manual checklist.
