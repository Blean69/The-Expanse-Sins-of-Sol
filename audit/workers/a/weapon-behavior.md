# Worker A: stock-mount weapon behavior experiment

Checkpoint inspected: `9e40dd4`; installed Sins II 2.0.3 (318), Steam build
25127248; pinned SDK schemas `8e061033afe53b1393eaefd56617a3fd041eeb5f`.
All runtime results are **NOT RUN**. No game, installed mod, master asset, prior
candidate, dependency, shared definition, or manifest was changed by this worker.

## Output and ownership

Worker A owns `tools/weapon_experiment.py`, this report, and
`audit/workers/a/torpedo-inherited-references.json` in the isolated worktree
`/run/media/haker/NVME 2/expanse-workers/weapon-behavior`.
Ignored output is `build/worker-a` in that worktree. The main integrator owns
final unit/skin overrides, manifests, package labels, packaging, and shared docs.

Staged game definitions:

- `entities/mcrn_exp_stock_dual_pdc.weapon`: installed Garda PDC with **only**
  `attack_target_type_groups` changed to `torpedo_strikecraft`, `corvette`,
  `light`, `flak`. Its mesh aliases, barrel offset, muzzle, cooldown, damage,
  acquisition logic, tracking speeds, and effects remain stock.
- `entities/mcrn_corvette_torpedo.weapon`, `.unit`, `.unit_skin`: reuse the
  existing identity-isolated candidates after auditing all nine prior candidates.
  Weapon spawn ID and projectile skin ID are the only changes from vanilla;
  the copied skin itself is identical. The skin copy is retained from the prior
  checkpoint for a private projectile identity, not because a visual edit is
  needed. No visual resources are copied.
- `integration-spec.json` contains **integrator metadata, not game fields**.
  `offline-validation.json` records inputs, exact output hashes, and actual checks.

The existing six Tachi PDC candidates have correct draft target groups but still
require imported mesh bindings, skin effect aliases, static geometry removal,
unit mounts, and runtime rig validation. They are not included in this stock
experiment, and none was regenerated or overwritten.

## Smallest complete stock experiment

Clone `entities/trader_antifighter_frigate.unit` into the experimental package,
changing only `/weapons/weapons/0/weapon` to `mcrn_exp_stock_dual_pdc`.
Keep that mount's position `[-10.803879, 3.248876, 6.77173]`, `mesh_point`
`child.pdturret_mount_0`, forward `[0,0,1]`, up `[0,1,0]`, yaw `[-160,10]`,
pitch `[-70,15]` unchanged. Leave the other five PDC entries and the seventh,
research-gated light autocannon unchanged. **Do not research the Garda light
autocannon unlock during this experiment.** There is exactly one weapon entry
for the experimental physical gun. Stock skins and all seven mount setups are
inherited from the installed game.

To exercise the private torpedo chain in the same stock experiment, clone
`entities/trader_torpedo_cruiser.unit`, change its sole weapon ID and
`/ai/attack_target_type_groups_matching_weapon` to `mcrn_corvette_torpedo`.
The latter is an existing cross-reference and must change with the weapon ID.
All Ogrov muzzle positions, navigation, targeting groups, and gameplay values
remain stock. New IDs require additive manifests as listed in the spec.
No Cobalt override or imported assets are needed for this experiment.

This overrides every user of the installed Garda/Ogrov unit IDs, including any
neutral/garrison reuse. It does not alter their shared vanilla weapon files.
Use only this experiment for the stock test, separately from both frozen
baselines and the Tachi turret experiment. A multi-player peer or controlled
opponent using these same unit IDs sees the same override.

## File-resolved weapon and projectile references

The clone chain is Ogrov unit → `mcrn_corvette_torpedo.weapon` →
`mcrn_corvette_torpedo.unit` → `mcrn_corvette_torpedo.unit_skin`.
The weapon has `firing.firing_type = spawn_torpedo`; the projectile has `torpedo:
{}`, `target_filter_unit_type = torpedo`, and
`ai_attack_target.attack_target_type = torpedo`, plus real armor/hull pools.
This is evidence of a damageable torpedo entity definition; it is **not an
observed interception success**.

The projectile skin inherits:

| Relationship | Installed target |
|---|---|
| `unit_mesh.mesh` | `meshes/trader_torpedo_cruiser_torpedo.mesh` |
| Mesh material | `mesh_materials/trader_torpedo_cruiser_torpedo.mesh_material` |
| Material color/mask/normal/ORM | `textures/trader_torpedo_cruiser_{clr,msk,nrm,orm}.dds` |
| Exhaust particle | `effects/torpedo_cruiser_exhaust.particle_effect` |
| Exhaust trail | `effects/trader_large_torpedo.exhaust_trail_effect` |
| Trail texture | `textures/trader_missile_trail.dds` |
| Engine sound | `sounds/ambient_loop_tech_neutrontorp_engine.sound` and `.ogg` |
| Death group → sequence | `death_sequences/torpedo0.death_sequence_group` → `death_sequences/torpedo0_0.death_sequence` |
| Death particle | `effects/trader_torpedo_cruiser_impact.particle_effect` |
| Death sounds | `sounds/EXPLOSION_SUPPORTSHIPDEATH{,_ALT1,_ALT2}.sound` and corresponding `.ogg` |
| Localization | `localized_text/en.localized_text`: `trader_torpedo_cruiser_torpedo_name`, `trader_torpedo_cruiser_torpedo_description` |

The report `torpedo-inherited-references.json` retains 80 exact inherited
JSON-pointer relationships, verifies 58 previously recorded file hashes, checks
the two localization keys, and adds the trail/texture relationship missing from
the earlier trace. Those two newly observed files and the localization file are
explicitly marked as lacking a prior file hash pin; they were not silently added
to the historical snapshot. Secondary effect textures, animations, UI icons,
and sound relationships are listed there. They stay inherited from base game.

The weapon muzzle alias
`trader_torpedo_cruiser_torpedo_weapon_muzzle` resolves in Ogrov skin
`/skin_stages/0/effects/effect_alias_bindings` to
`effects/trader_torpedo_cruiser_muzzle.particle_effect` and
`sounds/weapon_muzzle_tech_neutrontorp.sound` (same-name `.ogg`).
The stock Ogrov skin's hull/shield hit aliases exist but are not explicit
`hit_hull_effect` or `hit_shield_effect` fields on the installed torpedo weapon;
do not invent such edits to claim the collision damage path is proven.

The PDC's four aliases resolve in Garda skin at the same binding array:
`*_weapon_muzzle` → `trader_point_defense_autocannon_weapon_muzzle`,
`*_weapon_projectile_travel` → `trader_point_defense_autocannon_weapon_projectile_travel`,
and `*_weapon_hit_hull` / `*_weapon_hit_shield` → `pd_autocannon_impact`
under `effects/` with `.particle_effect` extension. Existing sound sets remain
inherited. Exact bindings for a future Tachi skin are emitted in the spec.
Stock Garda mesh aliases `pdturret_mount_0`, `pdturret_barrel_0` bind to
`meshes/trader_asset_frigate_pdturret_mount_0.mesh` and
`meshes/trader_asset_frigate_pdturret_barrel_0.mesh`. No skin edit is needed here.

## Eligibility, priority, and effectiveness are separate questions

`uniforms/target_filter.uniforms` defines
`common_and_strikecraft_and_torpedo_weapon`: enemy ownership; capital ships,
corvettes, cruisers, frigates, starbases, strikecraft, structures, super-capital
ships, titans and torpedoes. Its constraint list is empty. The weapon's target
groups narrow that list. `uniforms/attack_target_type_group.uniforms` gives
`torpedo_strikecraft = [torpedo,strikecraft]`, `corvette = [corvette]`,
`light = [light]`, `flak = [flak]`. Cobalt is filter type `frigate`, attack type
`light`; Garda is `frigate` / `flak`; the projectile is `torpedo` / `torpedo`.
Thus the proposed gun's configuration admits these three targets. A heavy
cruiser is not automatically admitted simply because its filter class is cruiser.

The pinned weapon schema allows `order_target_only`,
`order_target_or_best_target_in_range`, and `best_target_in_range`.
The candidate keeps Garda's `best_target_in_range` and
`always_check_is_dead_soon = true`. No inspected schema defines a separate
numeric weapon interception-priority field or guarantees group-order preemption.
The projectile and Cobalt both have `ai_attack_target.attack_priority = 50`;
this alone does not make the torpedo outrank a ship.
Acquisition group ordering, target persistence, interrupt timing, explicit unit
attack orders, and dead-soon avoidance remain runtime-dependent. No unsupported
priority key or independent second gun was added.

| Budget/health quantity | Untuned value / assumption |
|---|---|
| One PDC damage / penetration / cooldown | 2 / 0 / 1 s |
| One PDC nominal raw DPS | 2, pending observed damage cadence |
| Six PDCs, all covering one target | At most 12 nominal raw DPS before armor/durability, ignoring bonuses |
| Stock test anti-ship guns | One widened PDC, plus **zero** light autocannon if unlock is absent |
| Stock test anti-torpedo guns | Six PDCs, one widened plus five stock |
| PDC visual burst pattern | `[0,.08,.16,.24,.32]`; do not multiply damage by five without observation |
| PDC range / travel / yaw and pitch | 5,000 / 6,000 / 125 degrees per second |
| Torpedo damage / penetration / cooldown | 750 / 1,000 / 30 s |
| Torpedo armor / armor strength / hull | 100 / 50 / 50 |
| Torpedo durability | Absent from installed definition; engine/default behavior unresolved |
| Torpedo speed / acceleration time / duration | 1,000 / 2 s / 30 s |

Using the documented combat model already recorded in `docs/combat-prototype.md`,
zero-penetration PDC hits against unmodified Cobalt (durability 150, armor
strength 50) imply about 0.533 armor damage per nominal 2-damage event and 0.8
hull damage after armor is depleted. The implied raw damage requirement is
4,968.75, or 331.25 raw DPS for a 15-second kill with all relevant guns covering
the target. Dividing that whole-ship goal by six gives about 55.21 raw DPS per
gun only if all six arcs overlap. None of those higher values is implemented.

For a torpedo, **if** missing durability behaves as zero, its two pools need
approximately 200 raw damage: 150 for armor and 50 for hull. One 2-DPS PDC is
therefore inadequate for a normal straight inbound traversal of a 5,000-unit
coverage zone (~5 seconds at maximum speed). Actual burst cadence, overlap,
tracking and projectile durability must be measured. A surviving torpedo alone
does not prove ineligibility. Use several Garda screens or a 30-ship controlled
network to distinguish acquisition/damage from insufficient total firepower;
do not silently lower torpedo health or call a visual explosion interception.

## Proposed additions to the existing runtime checklist

The integrator should extend the existing checklist/results template with these
rows, rather than create another results log. Every row begins **NOT RUN**.

1. Stock rig control: with no light-autocannon research, attack an enemy Cobalt
   positioned in mount 0's forward-left coverage. Identify the mount on close
   video, verify it fires, and record armor then hull changes. The other five
   guns should not shoot that target. Test strikecraft/corvette/flak and a
   friendly exclusion control separately.
2. Torpedo control: have an enemy Ogrov attack an allowed capital/defense target
   with no defense screen. Count spawned entities, health pools, arrival damage,
   lifetime and launch location. Stock groups deliberately exclude Cobalt/Garda
   as Ogrov's attack target. This stage is not well-wide or salvo tuning.
3. Interception-only: position friendly Garda between that target and the enemy
   Ogrov. Record PDC acquisition and projectile armor/hull losses. Increase
   coverage only as needed to observe destruction before arrival. Compare the
   protected target's damage against control; projectile death must prevent the
   later collision hit. Death VFX alone is insufficient.
4. **Essential mixed test:** keep the tested Garda under an explicit attack
   order against the nearby Cobalt while enemy torpedoes cross mount 0's arc.
   Keep the Cobalt in range and the order active throughout. Video the individual
   experimental muzzle, target switches, latency, attack-order indicator, and
   return to Cobalt after threats clear. Repeat mid-burst, mid-cooldown, idle,
   move, and attack-move controls. Five vanilla PDCs can intercept independently;
   aggregate kills alone cannot prove the widened gun switched targets.
5. Shared budget: measure the same mount's damaging events over equal windows
   for ship-only, torpedo-only, and mixed cases. Do not count five visual tracers
   as five damaging events without health/timing evidence. Mixed targets must
   not grant a second full-rate firing stream. Compare preemption vs persistence
   while preserving identical cooldowns and bonuses.
6. Save/reload while the isolated projectile is in flight and the PDC is tracking;
   verify references, target state, armor/hull values, and no delayed damage from
   already destroyed projectiles. Repeat 1 ship, 6 formation, and 30 fleet with
   frame timing. Stop if an earlier gate fails.

Record per-gun/whole-network damage, durability, armor strength, armor and hull
separately, plus buffs/research and which arcs overlap. The full six imported
PDC implementation, 15-second shredding, well-wide range, accurate salvos,
standoff and saturation tuning remain pending these tests.

## Actual offline checks and reproduction

Run in the isolated worktree with the existing source checkout read-only:

```bash
SINS2_GAME='/run/media/haker/NVME 2/SteamLibrary/steamapps/common/Sins2' \
SINS2_SDK='/run/media/haker/NVME 2/SteamLibrary/steamapps/common/Sins of a Solar Empire II - Mod Tools' \
python3 tools/weapon_experiment.py \
  --source-root '/run/media/haker/NVME 2/expanse-mod'
```

Observed result: **PASS** — all 62 pinned schema blobs match; 11 relevant
installed JSON inputs match the existing hash snapshot; all nine existing
combat candidates equal their prior intended contents; four staged definitions
and two in-memory proposed unit overrides validate with the pinned Draft 7
schemas; exact allowlisted differences, enemy filter/groups, Garda mesh/effect
aliases, Ogrov muzzle alias, and single experimental mount entry pass.
The script refuses an existing output directory; repeat with a fresh `--output`
under this checkout's `build/`. Missing ignored candidates, rig audit or SDK
files produce **BLOCKED**, never a passing skip. The later-schema keyword caveat
in project environment docs still applies, so exact structural comparisons are
also required and were run.

Additional observed **PASS**: asset-independent Python syntax compilation and
a negative invocation without `SINS2_GAME`/`SINS2_SDK` returned a clear
`BLOCKED: set SINS2_GAME explicitly` diagnostic without generating output.
These two checks do not stand in for any game-, SDK-, or asset-dependent check.

Separate read-only reference audit: 80 inherited torpedo relationships checked,
58 checkpoint-pinned files match, two localization keys exist, and previously
untraced exhaust trail and its texture exist with new observed hashes. This
does not certify all engine-level implicit references or runtime collision code.

No full mod package was built by Worker A. Four complete definition inputs are
ready for integrator assembly. Model-dependent checks are outside this worker's
stock-hull experiment and were not represented as passed. No sounds were added.
