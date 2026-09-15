# Balance 28 independent numerical audit

Status: **frozen configuration audited; runtime NOT RUN**. No game was launched, package installed, or shared definition modified by this audit. The tested input is `expanse_update27_5_menu`, not a regenerated baseline. Source worktree commit: `8e55e93550b938e0dc62508a9ee8c6ac350332d4`. Main integration independently verified the installed 2,285-file baseline matched this input without drift.

`frozen-snapshot.json` preserves 12 actual unit definitions, 122 mounted weapon records, 115 resolved mechanism definitions, 113 modifier candidates, faction access, compatible factories and hashes for 4,013 consulted files. `baseline-table.csv` is the concise numerical comparison. `snapshot-sha256.json` binds both files. The generator refuses to overwrite an existing snapshot. Candidate results must be reported separately.

## Findings that matter to the balance pass

Truman is a cheap ordinary capital at baseline: 185 supply, 4,000 credits / 1,000 metal / 700 crystal, 100 seconds, no build prerequisite. UNN directly offers it, and every baseline faction grants the first `capital_ship` free. Donnager is a 500-supply titan costing 9,600 / 3,770 / 1,900 and taking 300 seconds. The brief's Truman floors are therefore **7,680 / 3,016 / 1,520 and 240 seconds**, before any deliberate rounding upward. Truman's existing offense ×1 / defense ×2 exotic bill is separate; changing ordinary resources does not silently substitute Donnager's exotic bill.

Truman has **two rail weapon instances and four physical muzzle coordinates**. Donnager has **two rail weapon instances and two muzzle coordinates**. Both have unique weapon IDs and unique mount points, no top-level damaging burst pattern, and no additional `apply_damage` / `create_torpedo` operator in their rail definitions. Their four effect references are the same native Ragnarov muzzle, travel, hull-hit and shield-hit visuals. No double application is demonstrated by this configuration. The exact relationship between native multi-muzzle firing and damage packets is not documented by the consulted primary source or local numeric schema. **Do not multiply or halve damage merely because Truman has twin barrels.** Measure one isolated turret discharge before declaring a runtime duplication defect.

| Rail budget, assuming one configured budget per weapon discharge | Truman | Donnager | Scirocco |
| --- | ---: | ---: | ---: |
| Instances | 2 | 2 | 1 |
| Damage per weapon | 3,500 | 5,000 | 2,000 |
| Reload seconds | 60 | 30 | 22.5 |
| L1 nominal opening total | 7,000 | 10,000 | 2,000 |
| L1 nominal sustained raw DPS | 116.67 | 333.33 | 88.89 |
| Highest-level nominal opening | 10,150 | 10,900 | 2,900 |
| Highest-level damage scalar | +45% | +9% | +45% |
| Highest-level reload scalar | −18% | −22.5% | −18% |

These are configured budgets, not observed hit totals or a time-to-kill simulation. Apply the selected level row once; do not sum all earlier rows. Truman's level scaling closes most of the opening-volley gap with Donnager. Two L1 Trumans have a nominal 14,000 opening budget against Scirocco's visible 5,400 hull and 3,100 armor. That explains why opening volleys deserve separate measurement even though Truman's long-run rail DPS is lower. Armor strength, durability, penetration, crippled state, regeneration, target aspect and intercepted torpedoes make a simple hull-plus-armor division insufficient.

Baseline L1 Truman health is 16,200 hull / 6,500 armor / 105 armor strength / 500 durability; Donnager is 14,520 / 5,000 / 130 / 750. Highest-level values are 29,181.6 / 11,066.12 / 150 / 500 and 26,155 / 7,025 / 175 / 750 respectively. The exact `hull_crippled_percentage` rows are frozen: Truman 0.5→1.0, Donnager 0.5→0.75. These fields and post-cripple behavior must be held constant before judging survivability. No health buff is justified solely by the observed loss report.

## Class, access and cap contracts

Actual identities are: Hephaestus destroyer `expanse27_hephaestus` (currently cruiser, 180 supply); Raptor `expanse12_raptor` (currently capital, 150); Scirocco `expanse12_scirocco` (capital, 200); Pella `expanse12_pella` (capital, 200); Tachi `expanse_mcrn_corvette` (frigate, 95); Rocinante `expanse_rocinante_hero` (frigate, 110); Razorback `trader_scout_corvette` (corvette, 5). Display-name assumptions must not substitute for these IDs. Snapshot retains original L1 economics, health and physics for the Hephaestus/Raptor exchange.

Native command evidence is `entities/dlc2_trader_loyalist_super_capital_ship.unit`: `build_kind`, `build_group_id`, `target_filter_unit_type` and unit tag use **`super_capital_ship`**; `ai_attack_target.attack_target_type` instead uses **`supercapital`**. It has ten experience levels and six item slots. Native construction is supported by `trader_loyalist_titan_factory_structure` (`super_capital_ship`, `titan`), whereas ordinary capitals/cruisers use the capital factory. Existing baseline global limits include titan ×1 and super-capital ×1. Moving Truman to command therefore requires a deliberate compatible cap change, factory/access review and preservation of the titan limit. An added Truman ×2 tag alone does not bypass an overlapping command ×1 limit. Native queue reservation, cancellation and capture behavior remain runtime test gates; the data tag is not proof of a universal owned-count invariant.

The command's native DLC unlock is not permission to copy unrelated product prerequisites. Faction unlock, construction access and AI research path need to be verified against the intended mod's own availability. Moving Truman out of `capital_ship` removes its eligibility for that free-first-capital rule while leaving cheaper UNN colonization/support available through the retained ordinary-capital path. Hephaestus becoming capital must acquire coherent levels, item eligibility and filters; Raptor becoming cruiser must lose capital-only free-first and level/item assumptions without altering L1 combat stats.

## Actual torpedo application

Magazine buffs use `create_torpedo` with an explicit impact damage value, penetration and 30-second lifetime. Spawned projectile entities contain an empty `torpedo` component and no mounted weapon, so these chains do not show an impact-plus-secondary-weapon double hit. Flight speed comes from the projectile entity's `physics.max_linear_speed`; an ADS speed used by the tooltip is not itself proof of changed flight.

Baseline light projectile `expanse04_light_torpedo` is 2,125 speed; heavy `expanse10_donnager_heavy_torpedo` is 1,275. Private MCRN hardware raises those to **2,550 and 1,530** respectively. Original source projectile HP, armor, steering, ramp time and 30-second life remain unchanged. The same duration at higher speed also permits greater travel distance; this is an unavoidable consequence of the requested speed change, not an unrelated range setting.

| Host / magazine | Capacity | Per interval | Interval | Reload after empty | L1 damage per torpedo |
| --- | ---: | ---: | ---: | ---: | ---: |
| Tachi | 8 | 2 | 10 s | 120 s | 1,500 |
| Donnager light | 48 | 12 | 10 s | 120 s | 1,500 |
| Donnager heavy | 4 | 1 | 15 s | 120 s | 8,000 |
| Truman light | 36 | 6 | 10 s | 120 s | 750 |
| Scirocco light | 20 | 5 | 10 s | 120 s | 1,500 |
| Scirocco heavy | 5 | 1 | 20 s | 120 s | 8,000 |
| Raptor light | 18 | 3 | 10 s | 120 s | 1,500 |
| Hephaestus light | 20 | 5 | 10 s | 120 s | 1,500 |
| Hephaestus medium | 12 | 3 | 20 s | 120 s | 3,000 |

Magazine controllers search for eligible nearby targets and check completed construction and weapon permissions. The inspected controllers have no explicit attack-order-only gate, so autonomous launch while moving is structurally plausible; it still needs an actual move-order / attack-order interception test. The magazine's radius of 200,000 does not ensure a missile can reach a target before fuel expires. Full-rate long-run torpedo damage must include finite ammo and the wait after the final interval, not just damage divided by interval.

Premium aliases are assigned to standard MCRN Tachi, private MCRN Morrigan, Raptor, Scirocco, Donnager and Hephaestus launch chains. Shared OPA/UNN/NPC Morrigan and hero launch chains remain baseline. Captured upgraded MCRN ships retain fitted hardware. **Pella-created standard Tachis also receive the standard Tachi equipment and supply cost; Pella's own magazine remains unchanged.** This is hardware-origin scope, not a dynamically checked owner buff.

## Research and item confounders

The shared native **Targeting Array self upgrade adds +75% tracking and +25% range**. Its separate nearby-friendly aura is +50% tracking / +15% range and excludes recipients with the self effect; do not add the two blindly. A fitted self array can turn a 0.6 tracking multiplier into 1.05 of the original speed under the ordinary scalar relationship. The new heavy tracking weakness therefore has an existing equipment counter. The [official turret geometry journal](https://www.sinsofasolarempire2.com/article/535259/dev-journal-23-combat-geometry-part-one---turrets) also explains why close lateral motion is harder to track and extra range can make tracking easier. Neither that explanation nor `target_acquired_duration_required_to_fire` proves continuous uninterrupted lock/reset behavior.

Rapid Autoloader has a passive −10% / −20% reload modifier and an active −40% / −80% reload modifier lasting 30 seconds. Engine combination/clamping must be observed instead of assuming unconstrained additive negative reload. Heavy Armor adds +25% hull and +25% armor. Donnager's reactor can additionally raise speed +50% and physical reload rate through its −1/3 cooldown scalar; disable it in baseline rail timing tests. The mod's rail-compatible research `trader_improve_gauss_defense_cooldown` applies −5% cooldown to `rail_gun`. Gauss-only research does not affect weapons tagged only `rail_gun` / `physical`.

The native Ragnarov rail-unlock item has +100% rail damage and −25% cooldown, but it requires the private `trader_rebel_titan` item access tag and is not offered in the three asymmetric faction shops. It is **not an established ordinary Donnager/Truman bonus** or an explanation for duplicate damage. The snapshot records modifier candidates and their filters so broad keyword matches are not mistaken for reachable effects.

## Latest range and escape settings

After the requested universal custom-PDC ×1.3 change, host PDC / ship rail ranges are Donnager 10,400; Truman and Nathan Hale 7,800; Scirocco, Raptor, Pella and Hephaestus 5,850; Tachi and Rocinante 4,550. Hosts without rails simply keep their PDC range. Foehammer rail uses the Donnager ship-rail benchmark ×3 = **31,200**. Its requested **60-second shot charge** is `firing.charge_duration`, separate from the retained 30-second reload. Do not label this a proven 60- or 90-second combined cycle until runtime timing establishes overlap and interruption behavior.

Tachi's test version uses 120 supply, acceleration ramp 5→4 seconds and angular speed 25→28.75, retaining angular ramp 1.25 seconds and max linear speed 1,250. The 95-supply control must share the same hardware and movement; only supply and dependent launch availability checks differ. Optional Donnager cadence is two rail reloads 30→24 with no changed volley, HP or supply; default does not include it.

Razorback's actual baseline jump charge is 2 seconds; proposed charge 0.1 seconds is distinct from its existing research scalar. Its existing `trader_scout_corvette_unstoppable_phase_jump` ability can acquire phase-disruption immunity from native research. New short charge does not introduce this bypass, but inhibitor tests must be run both without and with that research. Keep the existing nine self-damage ticks, 100 hull / zero armor, normal speed 3,000 and 20G-burn behavior unchanged.

## Independent proposal review

`weapons-review.json` binds the reviewed weapons helper by SHA256. The independent review executed all 203 proposed files without writing a candidate package; checked source paths and hashes, exact allowed weapon numeric differences, preserved numeric ability/buff leaves, ADS speed-only differences, projectile speed-only mutation, overlay idempotence, isolated 95-supply control and isolated optional Donnager reload variant. Exact `trader_light_frigate` consumers were searched across native and mod research, buffs, abilities, items and action data. Only trade-escort presentation and the deliberately unchanged foreign Eivonns spawn refer to that ID; no exact-ID research filter was found requiring the private Morrigan alias.

This is not a schema-validation result and is not gameplay validation. Final integrated manifests, references, class contracts and candidate hashes require separate checks. `workstation-tests.md` provides the required runtime gates. The baseline snapshot remains unchanged regardless of candidate integration.

## Actual merged A and B120 follow-up

`merged-review.json` records **576 passing static checks** against the actual `expanse_balance28_A` and `expanse_balance28_B120` directories, with hashes for every consulted definition. Revised class/factory contracts, UNN command cap ×2 alongside titan ×1, free-first eligibility, exact economic floors, unchanged L1 foundations, Hephaestus level/item coherence, Raptor's removed level/item access, Nathan Hale colony path, six-faction shared battery cap/access, prerequisite closure and unique research coordinates passed. Every one of the 203 Stage B helper results matched the actual B120 JSON, and B retained Stage A's class/economic/health changes. This is a configuration comparison, not an engine schema or gameplay pass.

The integrated cap policy **explicitly excludes Truman from Amun-Ra and OPA override boarding, at both launch and resolution**. Other command/titan filters remain as before. This deliberate exception prevents these existing acquisition paths from bypassing Truman's limit; it must be disclosed rather than described as unchanged boarding. Native queue/cancel behavior still requires runtime verification. Truman keeps four existing item slots even though the native command template has six, preserving its equipment budget. Other factions retain their original command cap ×1; only the two UNN identities gain ×2.
