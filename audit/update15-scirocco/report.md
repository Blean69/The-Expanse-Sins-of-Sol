# Scirocco bounded support candidates

Owner: Scirocco worker. Main owns integration of the one unit selection-list patch,
localization, manifests, and final package. Baseline is the preserved 0.14 tree;
this worker has not installed, enabled, launched, committed, or pushed anything.

## Mechanical choices

| Ability | Admission | Effect | Budget |
|---|---|---|---|
| Marine Breaching Teams | Detected, fully built enemy corvette/frigate/cruiser/capital/command/titan in the same gravity well, missing at least 20% hull; range 2,500 | Cosmetic pod takes 3 seconds, then speed modifier −15%, physical weapon cooldown modifier +15%, lasting 12 seconds (13 with Marine Assault Doctrine) | 40 antimatter; 90-second cooldown; globally non-stacking security guard for 45 seconds after impact |
| Combat Engineering Teams | Another friendly fully built ship of the same six ship categories, damaged hull, same well; range 3,500 | 20 absolute hull per tick, 20 one-second ticks; at most 400 restored hull for a small ship or titan alike | 50 antimatter; 60-second cooldown; same effect cannot stack or refresh across players |

The movement and reload modifiers add to the engine's existing scalar modifiers;
they do not shut down movement, weapons, targeting, or PDCs. The custom PDCs have
`weapon_type: normal` and `physical` tags, so the modest cooldown penalty applies
to them too. Ability-driven torpedo magazines are not weapon reloads and are not
slowed. No tracking limits, native weapon statistics, costs, construction times,
shield policy, permanent movement, or other ships' abilities change.

The marine pod is a reused **cosmetic particle**, not an interceptable unit. It
carries no damage or capture operator. This replaces only Scirocco's former
25%-chance capture ability in its selection list. Existing Amun-Ra, Donnager,
and other ships' capture implementations remain unchanged. Unreferenced old
Scirocco capture files may remain in the baseline package without exposure.

Manual targeting checks both existing and pending security guards. The delayed
impact rechecks current ownership, damage, visibility, gravity well and active
guards; its separate arrival filter ignores pending reservations so it cannot
reject its own scheduled application. Global `preserve_existing_buff` ownership
and stack count one form the final same-frame admission guard. Only a newly
started guard spawns the disruption buff. At most one application can own that
45-second protection period, with 32–33 seconds of immunity after the penalty
expires. Neither another pod nor another player refreshes it.

Disruption and engineering use the installed
`on_current_spawner_player_ownership_changed` → `make_buff_dead` pattern. A
capture clears the temporary penalty/repair immediately; the harmless security
guard remains until its original deadline. These native event and concurrency
semantics still require observation in this mod; no runtime pass is claimed.

Engineering repairs hull only, with no armor, shield, percentage-of-hull or
research multiplier. Other kinds of healing may coexist; the 400 cap is for this
one effect, not a cap on all healing received. Combat Damage Control's proposed
passive restoration modifier is separate. Marine Assault Doctrine uses native
`research_prerequisites_per_level` with existing node
`trader_upgrade_experience_gain_0`: the only upgraded support value is 12→13s.

## Four active controls

The shared patch changes `/abilities/0/abilities` in `expanse12_scirocco.unit`:
reactor, corvette launch, Marine Breaching Teams, Combat Engineering Teams first,
then the unchanged light/heavy magazine, death breach, and no-shields passives.
This stays in **one flat ability selection list**, not four competing conditional
groups. Existing fixed-level behavior is retained. The engine UI must still be
checked to ensure all four active controls appear in the intended order.

## Verified references and offline checks

- 7 new entity definitions pass both pinned Draft 7 and Draft 2020-12 schemas.
- Private 0.14 overlay resolves 378 references; Scirocco graph includes 8 abilities,
  8 reachable buffs, 6 torpedo references, and valid typed values and filters.
- Additional explicit checks validate weapon modifier IDs, owner-change cleanup,
  pending/manual versus active/arrival protection, four active controls, and
  exact rest-of-unit equality.
- Existing Amun-Ra and Donnager capture definitions remain hash-identical.
- Native source hashes are recorded in `validation.json`; no SDK update occurred.
- Builders are `tools/update15_scirocco_support.py` and
  `tools/update15_scirocco_validate.py`; output is `build/update15-scirocco`.
- `integration-recipe.json` contains private filenames, exact before/after unit
  selection patch, all new text, and research linkage. It requires no skin patch.

Native templates: TEC robotics repair droids for targeting, range and research
level selection; TEC combat repair item for finite hull-only ticks and visuals;
Vasari repair cloud for ownership-change cleanup; installed Herald purge
corruption for damaged-hull filters; TEC warpath for globally preserved stacks;
the accepted Scirocco boarding implementation for the cosmetic pod and delay.

## Small ordered workstation tests — all NOT RUN

1. Fresh game and save reload: spawn Scirocco; verify reactor, corvette launch,
   marines and engineering controls, tooltip values, antimatter charges and
   cooldowns. Check unchanged torpedo passives and shieldless behavior.
2. Test marines against a full-health enemy (reject), enemy at <80% hull (accept),
   ally (reject), missile/structure/planet (reject). Compare speed and weapon
   cadence: modest penalty, PDCs continue firing, magazine cadence unchanged.
3. Two allied players fire teams at one eligible target nearly simultaneously.
   No stacking or refresh; after 12/13s the effect ends, another team remains
   barred until 45s. Capture or repair the target during the 3s pod flight;
   invalid arrival must not disrupt. Capture during disruption must clear it.
4. Cast engineering on damaged ally versus enemy/self. Count at most 400 hull
   over 20 ticks on frigate and titan; armor/shields unchanged. A second source
   cannot refresh; capture clears the effect. Save/reload mid-repair and mid-guard.
5. Research Marine Assault Doctrine with an existing Scirocco, then build a new
   Scirocco: compare unresearched 12s to researched 13s on both. No other support
   values change. Repeat core cast/guard/repair/capture checks in multiplayer.

No actual in-game, save/reload, research-update, or multiplayer test has run here.
