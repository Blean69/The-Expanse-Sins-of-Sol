# Donnager 0.10 behavior handoff

Owner: worker A (`weapon-behavior`). Main owns the final unit, skin, mounts, player/menu registration, manifests, packaging and documentation integration. Use **`build/donnager10-a/final-fit`**. Earlier `final` and `final-reviewed` are retained candidates, not package inputs. No installed game data, SDK, prior package or existing ship was modified. New runtime tests: **NOT RUN**.

## Handoff and checks

`tools/donnager10_behavior.py` generates 36 private entity definitions, localization, ship-side effect aliases, integration recipe, source evidence and candidate hash records. `tools/donnager10_behavior_validate.py` is a read-only callable helper:

```python
validate_components(candidate, base, game, sdk, source_root, integrated=optional_complete_mod)
```

The completed local run recorded in `component-validation.json` passed:

- 62 SDK schema blobs at pinned revision `8e061033afe53b1393eaefd56617a3fd041eeb5f`, plus recorded installed-reference hashes.
- 36 private entity schemas, using their declared Draft7 and an additional evaluation of the same unchanged schema under Draft2020 to enforce its existing closed-key annotations.
- 129 ADS/action-value references, memory declarations, modifier IDs, effect bindings, localization labels, projectile classifications and 62 scoped reference edges. Untouched installed effects/audio/death assets are explicit boundaries, not exhaustive transitive engine validation.
- Five arithmetic deadline cases: unboosted 10/120-second clocks; boosted 10-second clock at 6.75 seconds; boosted 15-second clock at 10 seconds; 120-second clock with 30 seconds of boost at 105 seconds. This is a polling arithmetic model, not the game.
- The generator checked all 338 accepted 0.9 files remained byte-identical before/after generation.

Checks caught and corrected two concrete defects before this handoff: an unsupported radius property was replaced by observed `include_y_axis_in_radius_check`, and both renamed magazine `ammo_label` localization entries were supplied. No check was waived. Geometry and unit bindings remain main/B checks.

## Combat budgets

| System | Private definition | Provisional budget |
|---|---|---|
| PDC | `expanse10_donnager_pdc_0` through `_15` | 14 damage / 0.25 s / 0 penetration / 2,500 range; 56 raw DPS each; 896 for all sixteen |
| Rails | `expanse10_donnager_rail_0`, `_1` | 5,000 damage / 20 s / 1,500 penetration / 12,000 range; 250 raw DPS each |
| Front light torpedoes | `expanse10_donnager_light_magazine` | Existing Martian 750 damage, 1,000 penetration, speed 1,250; eight rounds, pairs every 10 s; 120 s reload after empty |
| Rear heavy torpedoes | `expanse10_donnager_heavy_magazine` | 4,000 damage, 1,500 penetration, speed 750; four rounds, one every 15 s; 120 s reload after empty |

Four PDCs bearing on a sector imply 224 raw DPS; eight overlapping imply 448; sixteen is an upper whole-ship budget, not an assumed target coverage. Each physical gun has exactly one dual-purpose weapon instance. PDC target eligibility and acquisition copy the accepted implementation: the existing common weapon filter, verified ship and torpedo groups, `best_target_in_range`. This does not establish a strict missile-first priority. Explicit ship orders versus incoming torpedoes, collision coverage and damage after durability/armor remain runtime gates.

The rail penetration exceeds the installed Ragnarov rail's 1,000 benchmark. Two simultaneous hits are 10,000 raw damage; no guarantee is made about buffed frigates, armor/durability mitigation, shields, overkill, tracking or actual target survival. B/main will bind the two independently budgeted limited-traverse source rigs. Main's reviewed rail geometry settings are yaw 15, pitch 0, yaw tolerance 0.5 and pitch tolerance 1; these are separate from the unbound source weapon.

Without boost, a continuously eligible target gives light volleys at 0/10/20/30 then 150 seconds (6,000 total magazine damage; steady-cycle raw average 40 DPS), and heavy launches at 0/15/30/45 then 165 seconds (16,000 total; steady-cycle raw average about 96.97 DPS). Interception and target loss reduce those values. Ammo is consumed only by the existing valid-target launch sequence; empty reload proceeds independently of target/order availability.

Both launchers retain a 200,000 query range and explicit same-gravity-well/detected-enemy filters. Light lifetime is 240 seconds, heavy 300: nominal straight-line travel budgets 300,000 and 225,000 distance respectively, before acceleration, steering and moving-target losses. Heavy launch eligibility is restricted to `starbase` and `titan`. The installed projectile AI group `defense_starbase_titan` also contains `defense`, so postlaunch target retargeting could differ; no strict postlaunch exclusivity is claimed.

The reviewed heavy **private unit** uses the accepted Martian light projectile's 16.51-long / 2.94-wide spatial box and custom skin, fitting B's measured aft tube diameter around 6.3. It changes only its private speed and AI groups. The earlier Ogrov appearance was 272 long / 19.4 wide and was rejected for these launch ports. Both projectile health budgets remain 50 hull / 100 armor / 50 armor strength and genuine `torpedo` entity classification. The old large Ogrov candidate is preserved separately. Existing Martian light files remain unchanged.

## Reactor, carrier, boarding and breach

`expanse10_donnager_reactor` is an instant 100-antimatter activation. For 30 seconds it applies +50% maximum speed and a physical-weapon cooldown-duration scalar of −1/3, giving a nominal 1.5× firing rate. A 150-second activation cooldown implements **30 active + 120 recovery**, without a watched-buff channel. On Ankylon movement this is maximum speed 575 → 862.5. PDC nominal whole-ship boosted DPS becomes 1,344, rail interval 13⅓ seconds. Acquisition and projectile travel do not become faster.

Weapon modifiers do not intrinsically accelerate scripted magazines. Each new private magazine therefore subtracts 0.125 seconds from each pending deadline every 0.25-second poll **only while the Donnager reactor buff is active**. Wall-clock progress remains 1×, yielding approximately 1.5× combined progress. Fully elapsed clocks are not moved backward. Thirty seconds of boost contributes at most about 15 seconds of extra magazine progress; a 120-second reload boosted only for those 30 seconds takes approximately 105 seconds, not 80. Poll ordering adds up to a polling interval of timing uncertainty. This does not accelerate carrier, boarding or reactor ability cooldowns, or change existing ships' magazines. Save/reload and engine modifier application remain unobserved for this new behavior.

`expanse10_donnager_launch_corvette` copies installed pirate mercenary `spawn_units` logic with a single `required_units` entry for existing `trader_light_frigate`. The cost is the accepted Cobalt's 300 credits / 55 metal / 5 supply, with 20-second cooldown. Ability supply requirement and spawn-time available-supply clamp are both retained; owner is the caster owner and research prerequisites are checked. `in_hyperspace:false` and arrival delay zero request local deployment. The operator has no observed arbitrary hangar-coordinate field. Engine placement, prevention of overlap, simultaneous supply/resource changes and failure/refund behavior need a runtime test. This is a paid ability, not a native ship-factory queue or expanded factory roster.

`expanse10_donnager_marines` copies the working Amun 0.9 chain and changes only its namespaced IDs/text, capture chance to 0.4 and cooldown to 600 seconds. It retains exactly one probability roll, three-second timed delivery, existing valid enemy-capital constraints, hero exclusions, supply checks and owner transfer. It reuses the actual modeled boarding-pod visual. Main binds `weapon.boarding.0`; this is the user-accepted timed visual, not a physically interceptable pod or arrival-detected capture.

`expanse10_donnager_reactor_breach` is a passive `on_current_spawner_made_dead` trigger. It combines the installed volatile-nanites death-trigger pattern with the installed TEC starbase explosion damage/effect actions. It has no low-health self-destruct action or five-second active charge. The copied blast schedules 10,000 damage / 1,000 penetration in radius 10,000 with travel speed 5,000: outer-edge delay up to two seconds. It excludes the already-dead source and checks full three-dimensional radius.

The breach target filter explicitly lists **`self`, `ally`, `friendly`, `enemy`**, includes all installed stock explosion unit classes, and sets `respect_can_be_targeted_permissions:false`. Thus owner's other ships and allies are deliberately eligible in the authored configuration. This is not proof that the engine applies friendly damage: test same-owner, allied, enemy and outside-radius targets. Also verify scheduled damage survives source/buff teardown, explosion effects remain visible and only one wave fires. The timer's `make_buff_dead` prevents repeated use; interactions with delayed actions are a runtime gate.

## Ankylon foundation, titan cap and item slots

`source-evidence.json` contains exact installed Ankylon physics, all health levels, build data and item records. Level zero: 14,520 hull, 5,000 armor, armor strength 130, 6,000 shields; durability 750. Maximum linear speed 575, time to maximum speed 7.1875, maximum angular speed 18, time to maximum angular speed 20. Its item capacity is `items.levels[0].max_ship_component_count = 8`.

The latest explicit user choice is the **shared existing titan limit**. Main's new ship ID is `expanse_donnager_battleship`, mod ID `expanse_donnager10`, using the `titan` tag and titan build kind. Do not add an independent private cap or change the existing titan limit. A Donnager and an Ankylon/Ragnarov should compete for that existing slot. Main handles the verified TEC titan build/research route.

Consumables such as flak burst, radiation bomb and salvage kit are `ship_component` items with a `consumable_stack_count`; they share the eight component slots rather than using a new consumable inventory. Their observed required-unit tag lists include `titan`. **Do not grant `trader_loyalist_titan` item-access tags**, which would unlock Ankylon-specific upgrades. Main's proposed roster contains generic components and consumables only; each still obeys its own existing availability/research constraints.

## Smallest ordered workstation gates

1. Confirm Donnager build/research availability and competition for the existing titan slot; construct, select, move, save/reload. Check eight generic component/consumable slots without proprietary Ankylon upgrades.
2. Fire the two rails and sector PDCs on controlled targets. Record muzzle/traverse clearance, simultaneous gun count and damage. Add incoming torpedoes during an explicit anti-ship order; check each physical PDC shares one budget.
3. Record light and heavy launch ports, individual projectile counts and reload timelines. Heavy should launch only at a starbase/titan; kill the target in flight to probe retargeting. Intercept both projectile types with a known PDC network.
4. Activate reactor while moving and while each magazine has a pending deadline. Measure 30-second speed/rate effect, recovery, both magazine clocks and save/reload midway. Confirm existing ships are unaffected.
5. Deploy one corvette with sufficient resources/supply, then attempt with insufficient supply/resources and near collision obstacles. Test the modeled marine pod, one 40% capture roll, valid/invalid targets and ten-minute cooldown.
6. Destroy Donnager amid separately controlled owner, ally and enemy targets at known distances. Measure blast count, damage, two-second outer wave delay and radius exclusions. Keep the test fleet small until owner damage and source-death scheduling are observed.

All Donnager engine behavior above remains **NOT RUN**. Schema, reference and arithmetic checks establish reviewable data, not successful engine execution.
