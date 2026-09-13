# Shared TEC research pass 0.15

Owner: isolated research worker. Input: frozen 0.14; main must run the helper on the assembled 0.15 candidate after Truman exists. All runtime observations below are **NOT RUN**.

## Integration

`tools/update15_research.py` exports `apply(out, game, audit)`. It writes only the 13 existing research definitions, discovered custom torpedo ability/action sources, and 39 localization keys. No player IDs, research-list membership, manifests, ship definitions, models, capture systems or installed files are changed. Existing IDs preserve downstream prerequisites and save references. No new free research unlocks are added.

The local review overlay is `build/update15-research-final/`. `localization-entries.json` is a merge recipe, not a game resource; do not copy it into the game package root. Main helper merges it into `localized_text/en.localized_text`.

## Themed nodes

Tier is the native zero-based tier. Native prices, exotic costs, research times, node positions and prerequisites are retained exactly.

| Technology | Existing node | Tier | Expected result after purchase |
|---|---|---:|---|
| Closed-Cycle Life Support | `trader_planet_health_restore_rate` | 1 | Owned planets recover health 5% faster. Empire-wide planetary effect; does not repair ships. |
| Vacuum Construction Standards | `trader_structure_build_rate` | 2 | Orbital structures at owned planets take 5% less time to build. Empire-wide; ship construction is unchanged. |
| Ice-Hauler Contracts | `trader_mining_track_crystal_rate_0` | 1 | Planetary mining-track crystal income increases by 5%, including its population component. Empire-wide; excludes orbital extractors. |
| Epstein Freight Logistics | `trader_trade_port_income_rate_0` | 2 | Trade credit, metal and crystal income increases by 5%. Empire-wide; escort speed and construction are unchanged. |
| Modular Drydock Assembly | `trader_labor_negotiations` | 2 | Corvettes, frigates and cruisers take 5% less time to build at owned factories. Capital ships and titans are unchanged. |
| Deep-Survey Expeditions | `trader_find_npc_explore` | 0 | Retains the existing one-time expedition grant of four Sunflare scouts and the existing exploration discovery behavior. No permanent speed or hull bonus. |
| Compartmentalized Bulkheads | `trader_max_hull_points_0` | 0 | Ship and starbase maximum hull increases by 5%. Torpedoes and orbital structures receive no benefit from this node. |
| PDC Fire-Control Solutions | `trader_autocannon_weapon_damage_0` | 0 | Point-defense weapon damage increases by 5%. Range, tracking, firing arcs and cadence are unchanged. |
| Compact Warhead Packages | `trader_missile_weapon_damage_0` | 2 | Missile weapon damage and custom launched torpedo impact damage increase by 5%. Torpedo count, speed, health and reload schedules are unchanged. |
| Marine Assault Doctrine | `trader_upgrade_experience_gain_0` | 2 | Scirocco Marine Breaching Teams disrupt for 13 seconds instead of 12. Penalties and the 45-second protection window are unchanged. Does not change capture chance. |
| Combat Damage Control | `trader_max_hull_points_2` | 3 | Ship and starbase passive hull restoration increases by 5%. Existing combat repair delays remain. Combat Engineering Teams retains its fixed 400-point repair cap. |
| Reinforced Torpedo Casings | `trader_missile_weapon_armor` | 4 | Owned torpedoes gain 5% maximum hull. Does not add armor or shields; PDC interception remains useful. |
| Railgun Thermal Management | `trader_improve_gauss_defense_cooldown` | 2 | Railgun weapon cooldowns decrease by 5%. Damage, penetration, firing arcs and tracking speed remain unchanged. |

Deep-Survey Expeditions keeps the native four-scout grant and native discovery node identity. It does not grant four extra scouts on top of that. Existing Sunflare replaces the scout definition, so its current movement/HP still apply. Other nodes replace their old effects; these are not additional bonuses stacked onto the old node reward.

## Inherited technology audit before changes

The supported `trader_loyalist` research graph contains 208 examined native subjects. 57 have matching direct custom-unit/weapon/factory modifiers, planetary/economic modifiers or buff providers. The full exact technology → definitions → modifier mapping and source hashes are in `inherited-research.json`. Matching tag filters are not proof of engine runtime updates or effects on missing subsystems.

- Custom PDCs carry `autocannon`, `physical` and `point_defense`; native autocannon damage research currently reaches them. The first themed node targets `point_defense` specifically; later native autocannon damage nodes remain.
- Custom rails carry `rail_gun`, not `gauss` or `beam`. Native gauss cooldown/range and beam damage nodes bypass them. The themed thermal node explicitly matches `rail_gun`, reducing cooldown 5%, without changing tracking, penetration, damage or arc coverage. A 20-second rail becomes 19 seconds; a 15-second rail becomes 14.25 seconds.
- Custom torpedoes are launched by `create_torpedo` actions. Their impact damage comes from `heavy_torpedo_damage_value`, not a missile-tagged `.weapon`. Existing missile damage/range research therefore bypasses their action damage/range.
- Unfiltered native hull/armor research matches owned torpedo units too. The two replaced hull nodes are now ship/starbase-only. Unchanged `trader_max_hull_points_1` still adds 12.5% hull; `trader_hull_damage_reduction_0/1/2` still add 10/15/25 armor strength. These inherited durability bonuses are disclosed rather than silently removing existing counters/balance tonight.
- Native missile armor research currently adds 50% torpedo armor. Reinforced Torpedo Casings replaces that reward with 5% torpedo maximum hull. It does not preserve the old 50% armor reward alongside the new benefit.
- Unfiltered antimatter, experience or jump modifiers structurally match torpedo tags but do not create missing antimatter/experience/hyperspace subsystems. Scalar zero-capacity fields remain zero.
- Native corvette speed research reaches Sunflare because of its `corvette` tag. Tachi/Rocinante/Morrigan remain `frigate`, so they do not gain that corvette speed upgrade. Native capital/titan hull angular-speed research remains; this pass adds no weapon tracking bonus.
- Shield-only nodes removed by the existing policy remain absent; no shield modifiers, guard removal or shield-capacity overrides are introduced. Foreign captured ships/allied foreign effects retain prior shield-policy limitations.

## Torpedo program upgrade

Verified installed pattern: `trader_robotics_cruiser_repair_droids.ability` uses research-dependent ability levels with `[[], [[research_id]]]`. The first level exists before research; the second follows Compact Warhead Packages. The helper verifies actual referenced buff graphs, real `create_torpedo` operators, the bound damage value and each torpedo unit type/tag. It rejects existing non-fixed level sources rather than overwriting unknown semantics.

| Program | Unresearched impact | Researched impact |
|---|---:|---:|
| `expanse10_donnager_light_magazine` | 750 | 787.5 |
| `expanse12_pella_light_magazine` | 750 | 787.5 |
| `expanse06_amun_magazine` | 900 | 945 |
| `expanse12_raptor_light_magazine` | 750 | 787.5 |
| `expanse10_donnager_heavy_magazine` | 4000 | 4200 |
| `expanse12_scirocco_light_magazine` | 750 | 787.5 |
| `expanse03_torpedo_magazine` | 750 | 787.5 |
| `expanse03_hero_torpedo_salvo` | 750 | 787.5 |
| `expanse11_morrigan_magazine` | 750 | 787.5 |
| `expanse12_scirocco_heavy_magazine` | 4000 | 4200 |

The synthetic new Truman contract check verifies `expanse15_truman_light_magazine` binds the UNN torpedo entity and upgrades 375 → 393.75. The final main audit must confirm this against the real assembled Truman. Every cooldown, interval, salvo/magazine count, lifetime, steering, penetration, antimatter and display-health value remains identical at both levels; only impact damage increases.

## Before/after verification

- PASS offline: 34 candidate entities validate against installed pinned schemas; exact node economic fields and all non-damage torpedo values are preserved.
- PASS offline: ability graph discovery finds 11 abilities sharing 10 action sources. Rocinante normal magazine shares Tachi source; its independent salvo is also upgraded.
- PASS offline: synthetic new Truman program discovered, 375 → 393.75; unsupported existing level semantics rejected.
- PASS static single-node calculations: `integration.json` contains per-definition base/result numeric checks. Existing and newly built units are expected to receive the same owner-level research modifier; these are calculations, not observed gameplay.
- NOT RUN: existing-ship modifier refresh, new-build values, current HP behavior on max-hull change, research during a persistent magazine/reload, torpedo damage snapshot timing, save/reload, capture-owner transition and multiplayer parity.

## Small workstation matrix

1. Start the single supported TEC Enclave faction in a fresh game. Record one existing Tachi, Scirocco, rail capital and their PDC/torpedo stats; confirm shields remain absent.
2. Purchase one themed node at a time. Compare existing and newly built copies. Verify PDC +5% damage and unchanged arcs/tracking/range; rail −5% cooldown and unchanged tracking; measured torpedo impacts 750→787.5 and UNN 375→393.75 when available, accounting separately for defenses.
3. Research Compact Warheads halfway through a magazine and during the 120-second reload. Check whether the persistent buff retains its original level, refreshes without resetting ammunition, or resets. Test already-launched versus newly launched missiles. If ammo resets or save divergence occurs, the upgrade must be gated out of the playtest rather than claimed safe.
4. Research Marine Assault Doctrine, then compare Scirocco 12→13 seconds with the same 45-second guard; test allied/enemy/ownership capture filters and fixed engineering 400-point cap. Research passive damage control and confirm it does not multiply explicit engineering ticks.
5. Save/reload after research and during a magazine/support buff. Repeat the focused tests with host/client and captured hulls. Report observed passes separately from these pending cases.
