# 0.3 heavy torpedo and hero railgun candidates

Worker A owns `tools/combat03_stage.py`, `audit/combat03-a`, and ignored
`build/combat03-a` in `/run/media/haker/NVME 2/expanse-workers/weapon-behavior`.
The reviewed final inputs are under **`build/combat03-a/filtered`**. Initial
staging remains at the parent output directory, unchanged; the filtered version
adds an eligibility check before every timed launch. Use the filtered version.
Main owns final unit/skin definitions, launch positions, manifests, package
assembly and documentation integration. No installed file, prior milestone
output, source/master model, SDK, or enabled setting was changed by this worker.
No game was launched and no push was performed.

## Files and integration ownership

The ordinary corvette uses these four private definitions:

- `expanse03_heavy_torpedo.unit`
- `expanse03_torpedo_cycle.ability`
- `expanse03_torpedo_cycle_on_self.buff`
- `expanse03_torpedo_cycle.action_data_source`

Hero-only additions are:

- `expanse03_hero_railgun.weapon`
- `expanse03_hero_torpedo_salvo.ability`
- `expanse03_hero_torpedo_salvo_on_self.buff`
- `expanse03_hero_torpedo_salvo.action_data_source`

Both torpedo abilities use the same private projectile unit and inherit its
installed skin. No private skin/mesh/material/texture copy is needed. Hero-only
files must stay outside the ordinary package. `integration-recipe.json` lists
ability IDs, manifests by entity type, localization additions, exact inherited
effect aliases and required runtime gates. It is **integrator metadata, not
game data**. No ordinary `.weapon` with a guessed burst magazine was emitted.

**Main/B must replace `ability_positions` in both abilities.** The emitted
arrays retain the installed Ogrov's four positions as explicitly marked
reference geometry. They are not Tachi launch apertures. Each buff uses the
verified `ability_position_picking_type = next_sequential` hook; provide the
actual paired aperture positions. Railgun integration requires one fixed
keel-aligned weapon mount and verified muzzle positions. No rail coordinates
were invented by this worker.

## Timed launch candidate and its limits

Installed evidence comes from:

- `entities/trader_torpedo_cruiser_heavy_torpedo.ability`, its
  `.action_data_source`, and `_on_self.buff`: cast action applies a buff;
  `executions_per_interval_value` controls repeated `create_torpedo` operations.
- `entities/vasari_starbase_charged_salvo.ability`, its `.action_data_source`,
  and `_on_self.buff`: two torpedoes per interval, finite interval count, explicit
  first delay/interval, `watched_buff`, and `stop_use_type = on_spawned_buff_removed`.
- Pinned `ability-schema.json`: `cooldown_reset_type` accepts
  `on_start_use_ability` and `on_spawned_buff_made_dead`; `channeling_will_disable_weapons`
  accepts a boolean. These exact fields are used, without invented ammo keys.

Normal candidate values are first delay 0, two torpedoes per interval, four
intervals, spacing 10 seconds; `make_dead_on_all_finite_time_actions_done = true`.
The independent ability cooldown is 120 seconds, reset using
`on_spawned_buff_made_dead`. **If** the engine completes the finite buff with
the last interval, the intended uninterrupted schedule is:

| Time from activation | Intended action |
|---:|---|
| 0 s | Launch two |
| 10 s | Launch two |
| 20 s | Launch two |
| 30 s | Launch two; finite buff completes |
| 30–150 s | 120-second cooldown/reload |
| 150 s | Next cycle ready |

This is a **scheduled volley candidate, not verified persistent ammunition**.
There is no exposed weapon-level `ammo`, `magazine`, or `reload` field in the
inspected schema. Root `burst_pattern` was deliberately not used as a substitute:
duplicate simultaneous timestamps, total-versus-per-projectile damage, and
cooldown origin would introduce additional unresolved behavior. Ability
`max_charge_count` exists and appears in installed shield-projection/domination
abilities, but those examples do not establish the requested magazine policy.

Target-loss policy is explicit: every scheduled interval rechecks
`unit_passes_target_filter` against the **original target**, including enemy
ownership, allowed class and current gravity well. An ineligible target causes
that scheduled action to do nothing. **The candidate does not maintain a
separate remaining-round count or implement refund, pause, resume, or transfer
of unused rounds to a new target.** Whether an unsuccessful action still advances
the engine's finite interval counter must be measured; do not present skipped
slots as ammunition preserved for later. Retargeting a ship does not author a
new target into the already created buff. Treat target loss/interruption as
unresolved prototype behavior, not a completed magazine implementation.

The charged-salvo flags `make_dead_on_source_ability_released` and ownership-
change cleanup are retained. Cancellation, disable, ownership change, target
destruction, target phase jump and source death must be observed separately.
An early-dead buff may start the 120-second cooldown early rather than finish
the original four-pair schedule. Save/reload must preserve only behavior actually
observed, not an assumed counter. No explicit installed use of the
`on_spawned_buff_made_dead` enum was found; it is current-schema-supported and
must be tested for exact timing, including whether finite completion occurs at
30 seconds or the next scheduled update/interval.

Normal auto-cast seeks a target within the current gravity well; Ogrov's
`weapon_has_target` prerequisite is removed so a nearby PDC target is not required
for long-range launch eligibility. The ability remains associated with the
watched finite buff. `channeling_will_disable_weapons = false` expresses the
intent to preserve PDC firing, but it is not proof that the engine treats the
30-second action as non-channeling or permits normal movement throughout.
These are required workstation observations.

Hero salvo uses a separate ability ID, buff ID and action-data source: eight
`create_torpedo` executions in one interval, manual activation, and its own
provisional 120-second cooldown after completion. It does not debit or refill
the normal timed cycle. This is a separate gameplay reserve represented by an
independent ability, not a claim that a persistent numerical ammo inventory
exists. Hero cooldown is provisional and stated explicitly in localization.

## Real torpedo entity, range and damage

Each buff uses the installed operator fields `operator_type = create_torpedo`,
`torpedo_to_create = expanse03_heavy_torpedo`, `torpedo_source_unit = current_spawner`,
`torpedo_target_unit = target`, `damage_affect_type = hull_and_armor_and_shields`,
and scoped damage/penetration/lifetime values. The private unit inherits the
Ogrov torpedo's `torpedo: {}`, target-filter type `torpedo`, AI attack type
`torpedo`, 50 hull, 100 armor, armor strength 50, speed 1,000, and acceleration
time 2 seconds. Durability is absent in the source; no default is invented.
Only its AI attack-target groups broaden to installed ship/structure groups.
This is a real torpedo-unit definition with health, not merely a visual bullet.
Interception and prevention of later collision damage remain **NOT RUN**.

Damage per created torpedo is provisionally **750**, penetration **1,000**.
Eight successful hits have 6,000 nominal raw damage; over the intended
150-second uninterrupted cycle this is 40 raw DPS before defenses. The separate
hero salvo adds up to 6,000 raw damage when used. These values do not bypass PDCs.

Both abilities have numerical range **200,000** and lifetime **240 seconds**.
The same-well constraint is the exact schema-supported
`{"constraint_type":"is_in_current_gravity_well"}`, observed inside the installed
phase-tunneling action-data source's inverse constraint. It is added positively
to every private torpedo target filter and rechecked before each pair. Allowed
targets are enemy capital ships, corvettes, cruisers, frigates, starbases,
structures, super-capital ships and titans. Strikecraft, torpedoes, planets and
friendly units are not included in this heavy anti-ship target set.

The largest inspected fixture `inner_move_distance` is neutron star 50,000;
its spatial radius is 7,500, while `gravity_well.unit` sets outer movement
distance 5,000. Conservatively adding those and doubling suggests a scale of
125,000 for opposite-edge testing. This is an inference about scale, not an
engine radius formula or a universal map guarantee. At speed 1,000, range
200,000 needs about 200 seconds of straight flight plus acceleration/turning;
240 seconds supplies margin. Test the actual largest chosen well, modifiers,
vertical separation, moving targets, line of approach and target phase changes.
Do not claim all possible modded wells are covered or targets in another well
are unreachable based only on a large number.

**Standoff is unresolved:** ability range is not the unit's
`weapons.max_range_weapon_index`. No verified `max_range_ability` selector was
found. The unit may still close to PDC/railgun weapon range under vanilla
stop-and-fire navigation. No fake zero-damage range weapon or navigation
redesign was added to conceal this limitation.

## Hero railgun

The base is `entities/trader_rebel_titan_rail_gun.weapon`: existing 10-second
cooldown, penetration 1,000, range 12,000, projectile travel speed 4,500,
`order_target_only`, and one-second target-acquisition requirement. The private
copy changes only damage to **2,500**, its localized name, filter to installed
`common_weapon`, and existing target groups to permit small ships as well as
heavy ships/structures. Tracking remains fixed at zero; actual firing direction
comes from the hero mount. Target changes can add the retained acquisition delay,
so 10 seconds is nominal sustained-target cadence rather than a guaranteed
first-shot/retarget interval. No railgun is attached to ordinary corvettes.

Using the documented damage model, armor strength remains relevant even at high
penetration. The following unbuffed stock-pool calculations are not observed kills:

| Benchmark | Raw damage required at 1,000 penetration | 2,500 nominal one-shot prediction |
|---|---:|---|
| Cobalt | 1,987.5 | Yes |
| Garda | 1,187.5 | Yes |
| Harcka | 1,845 | Yes |
| Kodiak | 3,910 | No; two ideal hits |
| Level-1 Kol, including stock shields | 11,361 | No |

No promise is made for every frigate, researched shields, veterancy, items,
faction buffs or shield-burst recovery. Layer overflow, travel/miss behavior,
target acquisition and real time-to-kill require in-game verification.

## Exact inherited visual references

The ordinary skin needs only the installed Ogrov alias
`trader_torpedo_cruiser_torpedo_weapon_muzzle`, bound to
`effects/trader_torpedo_cruiser_muzzle.particle_effect` and
`sounds/weapon_muzzle_tech_neutrontorp.sound` plus its same-name `.ogg`.
Hero railgun additionally needs the four
`trader_rebel_titan_rail_gun_weapon_{muzzle,projectile_travel,hit_hull,hit_shield}`
aliases from `trader_rebel_titan.unit_skin`. Their particle files are
`trader_titan_rail_gun_weapon_muzzle`, `trader_titan_rail_gun_weapon_travel`, and
`trader_titan_rail_gun_weapon_impact` under `effects/` with `.particle_effect`.
The exact inherited sound arrays and direct file hashes are in the recipe.
Large vanilla rail effects are placeholders requiring size/alignment review
on the small hero hull. No external audio was added.

The private projectile selects `trader_torpedo_cruiser_torpedo.unit_skin` from
installed data, continuing to `meshes/trader_torpedo_cruiser_torpedo.mesh`, its
same-name mesh material, Ogrov textures, torpedo exhaust/trail, and `torpedo0`
death sequence. Those downstream references are the same chain recorded in
`audit/workers/a/torpedo-inherited-references.json`; do not duplicate them into
the mod unless an actual derivative changes them.

## Actual offline checks and next workstation gates

The final generator is `tools/combat03_stage.py`. Set the same `SINS2_GAME` and
`SINS2_SDK` paths used by previous builds, then run:

```bash
python3 tools/combat03_stage.py \
  --source-root '/run/media/haker/NVME 2/expanse-mod' \
  --output '/run/media/haker/NVME 2/expanse-workers/weapon-behavior/build/combat03-a/fresh-reproduction'
```

Output must be fresh; existing stages are never overwritten. Both initial and
filtered staging runs validated eight private definitions against all 62
unchanged pinned schemas. The filtered run additionally validated the exact
installed target-filter constraint copied into each timer action. Railgun and
projectile exact differences, private action-value/filter references, two
ability/buff/projectile chains, five inherited aliases, direct particle/sound
file existence, and schedule arithmetic passed. Previously pinned inputs were
hash-checked; newly inspected dependencies are explicitly recorded as new
observations without rewriting the historical snapshot. Syntax compilation and
a missing-environment negative diagnostic passed independently. Model/launch-
aperture checks were not performed by Worker A and were not reported as passes.

The smallest runtime sequence is: verify launch locations and count eight real
entities; time all four pairs, final buff completion and next ready event; repeat
while PDCs engage ships and incoming threats; then test target death/jump/loss,
cancel, retarget and interrupted save/reload. Measure torpedo armor/hull damage,
interception death and absence of later impact. Test opposite-well-edge flight
and exclusion of another-well targets separately from standoff. Hero-only tests
then check rail acquisition/cadence/damage and an eight-torpedo activation during
the normal cycle/reload, confirming their budgets remain independent.

**All these new runtime gates remain NOT RUN.** The outputs are concrete
experimental candidates; they do not establish persistent magazine behavior,
non-channeling movement, correct long-range navigation or observed one-shot kills.
