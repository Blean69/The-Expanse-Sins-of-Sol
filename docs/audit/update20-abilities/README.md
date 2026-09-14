# Stage 1 repair and boarding control

Status: implemented and offline checked; every gameplay/save/multiplayer case below is **NOT RUN**. Baseline is the frozen `expanse_update19` package in the main checkout, not an assumed ignored worktree copy.

`tools/update20_abilities.py` exports `changes(base) -> (definition_overlays, localization_fragment, report)`. It does not write units, manifests, localization tables, installations or shared economy data. The main integrator must register new buff `expanse20_boarding_target_lock`, merge the returned strings, and preserve the baseline otherwise. Its CLI writes a private overlay for inspection.

## Repair

Scirocco Combat Engineering Teams uses native `auto_cast.target_definitions`, enabled by default, with a separate target filter requiring at least 20% missing hull. Manual casts still accept smaller losses. Both use owned ships only (`self`, rather than the previous `friendly`), excluding self, projectiles, enemies, unbuilt ships and ships with a pending/active copy of this repair. The 3,500-range autocast constraint prevents selecting remote candidates, and no movement-order operator is authored. Actual order preservation needs a moving-ship runtime test.

The existing global one-stack repair buff and ownership-change cancellation remain unchanged. Its output remains 20 hull/second for 20 seconds: 400 maximum even on a Titan. Cost remains 50 antimatter, cooldown 60 seconds. Native healing caps at maximum hull; this is not a reservation scheduler. Native list order is used; no unverified least-health sorting is claimed.

Rocinante Belter Ingenuity also gains the native self-repair toggle, on by default at 80% hull, excluding its pending/active buff. Its existing repair/cooldown data is unchanged. Scout burn, bombardment, reactor boosts and other abilities are untouched.

## Boarding

All five existing Expanse capture abilities now acquire the **same** target buff immediately before the cosmetic pod travels. The lock's native all-player preserve-existing stack limit and launch filter's pending-buff exclusion prevent overlapping Expanse attempts from independently reaching resolution. One native time action resolves after the inherited three-second delay; the buff then remains until 33 seconds after launch, providing 30 seconds of protection after scheduled resolution. There is no per-frame search, external timer, or second capture probability system.

Both manual and default-off toggleable autocast require an enemy detected built ship at 30% hull or lower, in the same well and within the existing 6,000 range. Heroes Rocinante/Pella are excluded. The expressly approved historical Earth boarding exception remains for **Amun-Ra and Europa's Bane**: capital, command/super-capital and Titan targets. Other capture variants now select capital ships only, following the new doctrine rather than extending that exception to every launcher.

| Ability family | Chance (unchanged) | Cooldown (unchanged) |
|---|---:|---:|
| Amun-Ra / Europa's Bane | 10% | 180 s |
| Donnager | 40% | 600 s |
| Raptor | 20% | 600 s |
| Pella | 25% | 600 s |
| Legacy Scirocco marines definition | 25% | 600 s |

The legacy Scirocco capture definition is patched for consistency but is not newly assigned; current Scirocco support slots remain the integrator's existing definitions.

At resolution the graph rechecks target eligibility, damage, detection, hostility to the stable buff owner, live owned caster, range, and the target's actual supply cost against available supply including queued commitments. The recipient is `buff_owner_player`, not whichever player might later own the initiating ship. A target ownership-change event permanently records cancellation in native buff memory while preserving protection. Successful capture sets the same cancellation flag but occurs only once.

The cosmetic pod remains a visual effect. Shooting its graphic does not cancel boarding and is not described as interception. Native Advent domination/pirate boarding remains unchanged; their successful captures cancel the Expanse operation through target ownership change.

## Cancellation and limitations

- Target destroyed: no target remains; normal dead-unit buff cleanup applies.
- Caster dead, missing or currently captured: live-caster/ownership checks reject resolution. The target lock remains through its scheduled expiry.
- Target healed above threshold, moved beyond range, no longer hostile or no longer eligible: attempt fails at resolution. Normal cooldown is consumed; no refund is invented.
- Target captured by another player: cancellation memory persists even if captured again during the delay.
- No direct `player_is_defeated`/living-player constraint exists in the pinned action schema. A defeated player whose ships disappear is covered by the live-caster guard. **Defeat that leaves a living, owned caster is not independently blocked.** Do not report full defeat safety.
- A caster captured and then recaptured by its original owner within the three-second delay passes the current-owner check. Transient caster ownership history is not recorded. **This rare cancellation edge is not covered.**
- Supply is checked at launch and resolution; it is not reserved for the three-second flight. Parallel captures of different targets still require a same-tick supply test.
- Same-target native buff ordering, default-off toggle behavior, save serialization and multiplayer synchronization must be observed. Schema-valid native operators are not runtime evidence.

## Reference evidence

All runtime keys come from the installed game or pinned SDK, with no unknown-key exceptions:

- `trader_robotics_cruiser_repair_droids.ability`: player-toggleable native targeted repair autocast and ordered target definitions.
- `trader_combat_repair_system_unit_item.ability`: self-repair missing-hull autocast.
- Existing `expanse15_scirocco_engineering_teams.buff`: global non-additive repair and ownership cancellation.
- Existing `expanse06_amun_boarding` family: range, delay, normal synchronized random chance and capture-supply values.
- Existing Expanse magazine ADS/buffs: native per-buff memory declarations and fixed-value assignment.
- `trader_capital_ship_insurance_unit_item.buff`: stable `buff_owner_player` reference.
- Pinned ability/buff/action-data-source schemas: native distance constraints, target filters excluding dead units by default, all-player stacking, finite time actions, ownership-change events and memory.

## Short runtime checklist

1. Two Sciroccos: 79% hull owned target, full-health target, ally, neutral, enemy and projectile. Confirm only owned eligible target is healed, maximum 400 from one simultaneous same-effect instance.
2. Move Scirocco past a damaged ship just outside range; verify no chase/order replacement. Toggle off/on and manually repair a 95%-hull target.
3. Multiple Amun, Europa and Donnager attackers on one 29%-hull capital: one pending operation, one roll, 30 seconds after resolution before another attempt. Attempt during the guard manually and automatically.
4. Repeat with 31% hull, hero, station, native Titan and command ship; verify Earth exception versus Martian capital-only policy.
5. During the delay: destroy/capture caster, heal target, move target, change diplomacy, capture target with native domination, fill available supply. Confirm no unintended capture/refund.
6. Test defeated player retaining ships and rapid caster capture/recapture as explicitly uncovered cases before enabling boarding autocast widely.
7. Save/reload during travel/protection; same-hash multiplayer race with two hostile attackers. No old-save migration is implied.
