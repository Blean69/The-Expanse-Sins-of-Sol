# Passive magazine alternative — separate candidate

The candidate is generated under `build/combat03-a/persistent` by
`tools/combat03_persistent.py` in Worker A's isolated worktree. The prior
`build/combat03-a/filtered` timed-volley candidate remains unchanged; all eight
of its recorded entity hashes were checked again. No installed files, settings,
assets or SDK files were written. No game or save/reload test was run.

The required engine configuration mechanisms exist in the pinned schemas and
the main memory/timer patterns have installed examples. This allowed a concrete
passive candidate rather than another timed-volley approximation. **Its actual
runtime memory retention and save serialization remain unverified.**

## Definitions and mutually exclusive integration

Add these four private definitions:

- `expanse03_torpedo_magazine.ability`
- `expanse03_torpedo_magazine.buff`
- `expanse03_torpedo_magazine.action_data_source`
- `expanse03_heavy_torpedo.unit` — identical to the filtered projectile candidate

Attach `expanse03_torpedo_magazine` **instead of** `expanse03_torpedo_cycle`.
Do not mount both normal systems: that would provide two independent magazines.
The separate hero salvo may coexist because its independent reserve is intended.
The integration recipe lists exact IDs, localization additions, and required
runtime gates. Main retains ownership of units, skins, manifests and packages.

`ability_positions` still contains the clearly labeled stock Ogrov reference
positions. Main/B must replace that array with verified corvette apertures. The
two spawn actions each use `ability_position_picking_type = next_sequential`;
the second action advances to the second aperture without adding another weapon
or magazine. Projectile health, physics, skin, 750 damage, 1,000 penetration,
240-second lifetime and 200,000 radius are inherited from the filtered candidate.

## Persistent state and transition policy

The ability uses the installed key **`passive_actions.persistant_buff`** (that
spelling is deliberate). It has no `active_actions`, no active cooldown, no
watched active ability, and no move/stop/force-attack operators. There is no
30-second active sequence to hold the ship's movement order.

`per_buff_memory_declaration` declares three floats and one unit variable:

| Variable | Meaning |
|---|---|
| `ammo` | Actual remaining round count, initialized to 8 |
| `next_pair_ready` | Absolute simulation time when another pair may fire |
| `reload_ready` | Absolute simulation time when a depleted magazine refills |
| `selected_target` | Scratch unit reference selected for this firing attempt |

Float action values use the installed `transform_type = current_buff_memory_value`
and `memory_float_variable_id`. Time comes from the installed global
`common_simulation_time_value`, whose transform is `simulation_time`.
On buff start only, ammo becomes eight and the two deadlines become zero.
There are no target-loss or manual-order initialization/reset actions.

One indefinite timer polls every 0.25 seconds. In ordered actions it:

1. Refills to eight only when ammo is zero and the reload deadline has arrived.
2. Clears the scratch target reference. If at least two rounds remain and the
   next-pair deadline has arrived, it selects one eligible target.
3. Issues exactly two `create_torpedo` actions toward that selected target.
4. Debits exactly two rounds under the same ready/valid-target constraint.
5. Sets the next-pair deadline to current simulation time plus 10 seconds.
6. Sets the reload deadline to current simulation time plus 120 seconds **only
   if the just-fired pair depleted the magazine**.

No target means no spawn, no debit and no new deadline. Six remaining rounds
therefore remain six during a target gap. When a target returns after the
next-pair deadline, one pair may fire on the next poll; the system does not
catch up skipped time slots with several pairs. Changing stop/move/attack orders
does not recreate the buff or reset its variables. Reload continues with no
target and ends with eight rounds waiting for the next valid firing opportunity.
Continuous eligibility nominally gives pairs at 0, 10, 20 and 30 seconds, then
the next pair at 150 seconds. Timing starts at the first actual launch; target
acquisition/poll scheduling can introduce up to a poll interval of latency.

The buff has a one-instance stacking limit with `preserve_existing_buff` and
`restart_other_stacked_buffs_when_started = false`. It has no finite interval
count and no completion or source-active-ability cleanup flags. The passive
ability explicitly sets `only_if_owner_unit_operational = false` to preserve
state through operational changes, while firing checks `is_fully_built`,
`can_use_weapons`, and `can_use_missile_weapons`. This is deliberate separation
of stored ammunition from permission to fire. Disabled/crippled/ownership-change
behavior still needs testing; absolute deadlines currently continue during
disable rather than inheriting weapon-cooldown progress freezes.

## Target acquisition policy and evidence

Targets are the nearest detected eligible enemy within 200,000, checked in
three dimensions and constrained to the current gravity well. This is autonomous
selection, **not guaranteed focus on the ship named in a manual attack order**.
The inspected `action_unit` selector has no explicit current attack-order-target
enum, so no guessed selector was added. Remaining ammo is independent of orders;
the selected target can differ from an explicit attack order.

Acquisition uses `use_unit_operators_on_units_in_radius_of_unit`,
`max_target_count_value = fixed_one`, ascending `distance_to_unit` sort, an
`operators_constraint` that tests `operand_destination`, and the supported
`change_buff_memory_unit_value` operator. Spawn actions read `unit_type = buff_memory`
with `memory_unit_variable_id = selected_target`. Every spawn/debit rechecks the
selected target and readiness. A live buff tooltip exposes the ammo value; the
ability description does not pretend to display a verified live reload countdown.

Primary installed evidence:

- `advent_battle_capital_ship_energy_absorptive_armor.ability` supplies the
  passive persistent-buff pattern. Its `.buff` and `.action_data_source` show
  per-buff float variables, memory reads, state mutation, absolute simulation
  deadlines, value comparisons and preserve-existing stacking.
- `vasari_loyalist_titan_the_maw_on_self.buff` combines sorted target selection,
  `max_target_count_value = fixed_one`, target filtering on `operand_destination`,
  and per-buff float mutation inside the selected unit operators.
- `trader_capital_ship_insurance_unit_item.ability` supplies an installed
  `only_if_owner_unit_operational = false` example.
- `trader_orbital_cannon.action_data_source` supplies an installed `is_detected`
  target constraint; the prior phase-tunneling evidence supplies the same-well
  constraint.
- Pinned schemas explicitly declare per-buff `unit_variable_ids`,
  `change_buff_memory_unit_value`, `buff_memory` unit selection, radius sorting
  and permission checks. **No installed explicit unit-memory-write example was
  found**, so this part requires particular runtime scrutiny.

Input file hashes and whether they had historical pins are in the recipe.
New observations did not replace the historical game/schema snapshot.

## Offline proof actually obtained

The generator ran successfully with the existing `SINS2_GAME`/`SINS2_SDK` and:

```bash
python3 tools/combat03_persistent.py \
  --source-root '/run/media/haker/NVME 2/expanse-mod'
```

The command refuses an existing destination; use a fresh child of
`build/combat03-a` with `--output` for another reproduction.

**PASS, static candidate checks:** all 62 schema blobs still match the pin;
four generated definitions validate; every referenced memory variable, action
value, and target filter resolves; two creation actions share exactly one
guarded debit of two; no active/channel action, movement operator, finite-volley
completion or target-loss reset is emitted. The eight filtered predecessor
entity hashes remain identical. Syntax compilation and a missing-environment
negative diagnostic also passed without creating output.

**PASS, intended-state model only:** continuous-target schedule; six rounds
retained through a 60-second target gap and changed orders; reacquisition without
catch-up salvos; no duplicate same-timestamp pair; no reload before depletion;
120-second reload from the actual final pair; reload completion without enemies;
and no ammo spent while weapon permissions block firing. The model and expected
events are recorded in `offline-state-model.json`. This model tests the proposed
arithmetic/state policy, not engine action ordering or serialization. No Python
JSON round-trip is presented as evidence of a game save test.

## Remaining runtime gates

First establish that selector constraints are applied before the one-target
limit, that the unit-memory write is visible to subsequent actions, and that
each pair creates exactly two entities before one debit. Then change targets,
lose visibility, issue stop/move/new attack orders, and verify the ammo tooltip
retains the correct count. Observe no movement pin and continued PDC operation.
Test the full four-pair schedule and 120-second refill, including target gaps.

Save and reload with six rounds, with zero rounds during reload, and just before
a deadline. Verify variable serialization, absolute simulation-clock restoration,
and whether `on_buff_started` runs during load and resets memory. These are
**NOT RUN**. Buff teardown/recreation on death, capture, disable or ability
replacement can reset state and must not be confused with ammo retention.

The create-torpedo operator exposes no inspected success result used by this
candidate: if entity creation fails despite a valid selection, the subsequent
debit may still happen. Test target races and engine limits. Four target scans
per second per ship need the existing 1/6/30-ship performance gate. The passive
ability also does not change `max_range_weapon_index`, so navigation standoff
remains independently unresolved. This candidate should be tested separately
from the preserved timed experiment; no runtime success is claimed for either.
