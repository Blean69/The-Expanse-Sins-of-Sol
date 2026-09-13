# Six independent PDC recipes — provisional combat values

Owner: Worker A, isolated worktree
`/run/media/haker/NVME 2/expanse-workers/weapon-behavior`.
Owned code is `tools/polish_weapons.py`; ignored output is `build/polish-a`;
reports are in `audit/polish-a`. Old scripts/outputs, source/master assets,
installed game, SDK, and enabled mod settings remain unchanged.

The user reports visual-baseline loading and correct fixed muzzle positions.
That is user-observed evidence for those specific baseline checks. The six
functional turret recipe is new; rotation, targeting, damage and interception
tests for it remain **NOT RUN**.

## Exact integration recipe

Six files `build/polish-a/entities/expanse_polish_pdc_0.weapon` through
`expanse_polish_pdc_5.weapon` are ready for main-integrator review. Each copies
the installed Garda PDC definition, with these deliberate changes:

| Existing game field | Provisional new value |
|---|---:|
| `name` | `expanse.weapon_name.pdc_autocannon` |
| `damage` | 28 |
| `cooldown_duration` | 0.25 s |
| `penetration` | 0, unchanged |
| `range` | 2,500 |
| `yaw_speed`, `pitch_speed` | 360 degrees/s |
| `effects.burst_pattern` | `[0, .04, .08, .12, .16, .20]` |
| `turret` | Exact per-rig Worker B base/barrel aliases, barrel offset and single muzzle |
| `attack_target_type_groups` | `torpedo_strikecraft` plus the installed Cobalt medium-autocannon groups |

Add the English entry `expanse.weapon_name.pdc_autocannon: PDC autocannon`.
This is a new private localization key, using the existing `name` lookup field;
the key is absent from vanilla English localization. There is no localization
schema in the pinned SDK, so this is verified against the installed lookup
structure rather than claimed as schema-validated localization.
Retain existing ship name/description keys for the integrator's final wording.

The complete observed target-group union is `torpedo_strikecraft`, `flak`,
`light`, `antiarmor_lrm`, `carrier_support`, `capital_supercapital_heavy`,
`defense`, `corvette`. Source is
`entities/trader_light_frigate_medium_autocannon.weapon` plus Garda's torpedo
group. Thus nearby larger ships retain the Cobalt's established eligibility;
zero penetration reduces damage effectiveness against durable targets. The
filter remains `common_and_strikecraft_and_torpedo_weapon`, enemy-only.
Starbase/titan attack types are not silently added merely because the broad
filter permits those unit classes. No uniform or vanilla weapon is overridden.

`acquire_target_logic = best_target_in_range`, `always_check_is_dead_soon = true`,
Garda's firing type/travel speed, firing tolerances, damage-affect type, tags and
effect aliases stay unchanged. Torpedoes are listed first, but neither the
schema nor these files proves immediate priority/preemption. Retain one actual
weapon instance per physical assembly. Do not append a second independently
firing anti-missile weapon or keep a hidden seventh fixed autocannon budget.

`integration-recipe.json` is metadata for the integrator, **not game data**. It
contains exactly six mount entries, twelve mesh alias bindings, four inherited
Garda effect bindings, weapon IDs and the one localization addition. All offsets
come from Worker B's actual `audit/polish-b/mount-metadata.json`; the exact input
document used is saved separately in ignored `build/polish-a/input-rig-metadata.json`.
Weapon schema success does not approve its meshes. B/main must independently
pass tangent, compiled geometry, static-duplicate, mount and package gates.
360-degree/second tracking is angular speed, not a promise of 360-degree firing
coverage; B's geometry-derived arc limits remain authoritative candidates.

## Cadence and damage budget

The pinned weapon schema exposes **two distinct fields**: root `burst_pattern`
and `effects.burst_pattern`. The installed Garda PDC only sets the effects field
to `[0,.08,.16,.24,.32]`; this recipe changes that effects timing but leaves root
`burst_pattern` absent. A complete installed census finds 47 weapons with root
bursts: 40 `spawn_torpedo`, five `projectile`, two `beam`. Examples and current
file hashes are recorded in `burst-field-evidence.json`. The schemas do not
describe damage-per-burst semantics, so no damage multiplier is inferred from
either array's length.

The design assumption is four nominal damaging cycles/s at 28 raw damage per
physical PDC: **112 raw DPS per gun**. Six visual pulses per quarter-second
suggest **24 visual pulses/s per gun**, or 144 with all six firing. Visual pulse
count is neither an extra damage multiplier nor a claimed real ammunition RPM.
Measure actual damage cadence and rendering in game before treating either
number as observed behavior. This is a fast visual starting point; runtime
performance may require reducing visual pulses while preserving damage/cooldown.

The user's approximately 15-second small-ship goal is provisionally calibrated
for **three overlapping PDC arcs**, not an assumption that all six always bear.
Using the combat model already documented in `docs/combat-prototype.md`, an
unbuffed Cobalt has durability 150, armor 825, armor strength 50 and hull 750.
At penetration zero, that implies 4,968.75 raw damage for its armor and hull.
Each nominal 28-damage event implies approximately 7.467 armor damage or 11.2
hull damage after armor depletion. Actual shield availability, research,
bonuses, misses, tracking, regeneration and scheduling must be recorded.

| Guns actually covering target | Nominal raw DPS | Ideal Cobalt time, seconds |
|---:|---:|---:|
| 1 | 112 | 44.36 |
| 2 | 224 | 22.18 |
| 3 | 336 | 14.79 |
| 4 | 448 | 11.09 |
| 5 | 560 | 8.87 |
| 6 | 672 | 7.39 |

These are arithmetic estimates, not observed kill times. The values are a
provisional ship-only balance change, not a canonical Expanse weapon spec.
Against larger targets, independently inspect their attack-target type, damage,
penetration, durability, armor strength, armor loss, hull loss and shields;
group eligibility alone cannot prove effectiveness. No hull/shield/economy
changes or torpedo definitions are included in this PDC polish.

For an installed Ogrov torpedo, armor 100 / armor strength 50 / hull 50 would
require about 200 raw damage **if its absent durability field means zero**.
That is about 1.79 seconds of uninterrupted 112-DPS fire by one gun, before
tracking, cooldown scheduling, misses and projectile travel. A maximum-speed
torpedo crosses 2,500 range in about 2.5 seconds. This rough comparison makes
interception plausible but does not certify it; the real engine's default
durability and arrival geometry remain test gates.

## TV-show reference limits

Official [Prime Video Season 1](https://www.primevideo.com/detail/0PKSW854X596KEIDJJJC6NYKS6)
lists episode 4, “CQB,” and its Donnager battle; official
[Prime Video Season 6](https://www.primevideo.com/detail/0P5PBGVVW11X6D7IBS6OP020Q8?tr=mp)
provides the final-season battle episodes. These are appropriate licensed
viewing references for the user to compare visual cadence. Their accessible
episode descriptions do **not** establish a numerical PDC firing rate. Official
SYFY/Prime searches did not produce verified canonical RPM or a measured clip
cadence. No video was played or timed by this worker, and no fan-wiki/fan-video
number was promoted to canon. The selected six-pulse pattern is an explicit
art/gameplay approximation pending user visual feedback, not a TV measurement.

## Existing enabled-mod and metadata evidence

Read-only observed file:
`/run/media/haker/NVME 2/SteamLibrary/steamapps/compatdata/1575940/pfx/drive_c/users/steamuser/AppData/Local/sins2/settings/.enabled_mods`
lists both `expanse_cobalt_name` and `expanse_corvette_visual`, display version
`1.0`. This identifies the user's “both mods”; no setting was changed.

The relevant log is:
`/run/media/haker/NVME 2/SteamLibrary/steamapps/compatdata/1575940/pfx/drive_c/users/steamuser/AppData/Local/sins2/logs/sins2_log_318_[2026-09-12][22-30-07]_492.txt`.
It was initially read as `sins2_log_492.txt` and was renamed by the external
game/session lifecycle before this evidence capture. The final path was checked
and hashed; this worker did not rename it or launch the game.
Exact line numbers, snippets and file hashes are recorded in
`enabled-mods-readonly-evidence.json`. Observed warnings include:

```text
WARNING : corrupt mod meta_data : C:\users\steamuser\AppData\Local\sins2\mods\expanse_cobalt_name\.mod_meta_data
WARNING : corrupt mod meta_data : C:\users\steamuser\AppData\Local\sins2\mods\expanse_corvette_visual\.mod_meta_data
```

Subsequent discovery reports the visual mod as:

```text
Found mod : [expanse_corvette_visual] { name=expanse_corvette_visual , version=1.0 , compatibility_version=2 , target game version=0.0.0 , bundled_mods=[] , dependencies=0 }
```

The log later enables both mods, syncs their resource providers, loads both
English localization files, and lists the visual mod in `simulation_mods`.
Those parsed/fallback values are observed diagnostics, **not proof of the exact
required metadata field names or defaults**. Main owns the new package's
metadata audit against SDK/examples; the frozen installed metadata remains
untouched. A separate startup-crash recovery line appears earlier; no cause is
assigned from these snippets, and an error-free baseline run is not claimed.

## Checks run and next runtime observations

Executed successfully:

```bash
SINS2_GAME='/run/media/haker/NVME 2/SteamLibrary/steamapps/common/Sins2' \
SINS2_SDK='/run/media/haker/NVME 2/SteamLibrary/steamapps/common/Sins of a Solar Empire II - Mod Tools' \
python3 tools/polish_weapons.py \
  --source-root '/run/media/haker/NVME 2/expanse-mod' \
  --rig-metadata '/run/media/haker/NVME 2/expanse-workers/tachi-one-pdc/audit/polish-b/mount-metadata.json'
```

**PASS for weapon recipes only:** all 62 pinned schemas match; six installed
reference definitions match their checkpoint hashes; six weapon schemas
validate; exact field changes are allowlisted; there are six unique mounts,
twelve unique aliases and four resolving Garda effect bindings; groups/filter
exist; no root burst or extra weapon instance is added. Output hashes and
limitations are in `offline-validation.json`. No mesh-dependent check was
performed by this generator; its success must not be reported as a mesh pass.
Separate asset-independent checks passed: Python syntax compilation and a
negative invocation with missing environment variables produced a clear
`BLOCKED` diagnostic before writing any output.

At runtime, first inspect each muzzle/axis independently, then compare ship-only,
torpedo-only and mixed engagements with the explicit ship attack order held.
Record the individual gun switching targets, recovery, arc coverage, actual
health changes and shared cooldown budget. Measure close-range visual cadence,
audio overlap, and frame timing at 1/6/30 ships. The whole-ship 15-second target
is evaluated only after counting which guns actually bear. No game was launched,
no installed package changed, and no torpedo tuning was added by this worker.
