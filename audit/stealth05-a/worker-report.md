# Amun-Ra mechanics audit and isolated probes — Worker A

New ownership is confined to `tools/stealth05*.py`, `audit/stealth05-a`, and ignored `build/stealth05-a` in the weapon-behavior worktree. Earlier 0.4 and prior assets/packages remain untouched. No game, install, dependency update, commit or publication occurred.

## Concrete outputs

`build/stealth05-a/probes/entities` contains six private definitions:

- `expanse05_launch_probe.{ability,buff,action_data_source}`: a passive **counter telemetry probe, without cloak**. It observes a verified torpedo-spawn event and shows counted launches and an absolute reveal deadline in the buff tooltip.
- `expanse05_boarding_probe.{ability,buff,action_data_source}`: a manual delayed capital-ship capture probe with a modeled stock shuttle effect, one 10% roll, and supply checks.

`integration-recipe.json` gives the attachment IDs, private gun-tag recipe, future Amun projectile binding, localization entries, unit-limit scope and blockers. There is no Amun ship unit, imported mesh, manifest, installable mod or cloaking buff in this stage. Main retains all shared unit/player/skin/manifest ownership.

The later `build/stealth05-a/combat` stage adds nine private, unbound combat definitions: three PDC weapons, one railgun, Amun torpedo unit/skin, and a private copy of the normal magazine ability/buff/ADS. This is still incomplete. Its recipe supersedes the earlier **proposal-only** torpedo values embedded in the standalone probe recipe.

## Actual installed stealth system

The fourth faction is **Eidolon**, internally `dlc3_herald` / `dlc3_herald_loyalist`. Installed English localization explicitly describes cloak quality levels: 4 Perfect, 3 Good, 2 Standard, 1 Poor, 0 Revealed. Revealed ships can be attacked normally. These quality levels describe available information, not a binary invisibility flag.

Inspected `dlc3_herald_cloak_frigate_cloak.ability`, `.buff`, `.action_data_source`, and damage-degrade buff. The ability applies a buff with `provides_cloak: true`, `required_product: dlc_Herald`, cloak alpha/fade fields, and a `cloak_quality` unit modifier driven by per-buff float memory. Its stock memory sets quality3 or4 by research level. Damage dealt applies −5 quality for30s; damage taken or a completed jump applies −1 for20s. The cloak buff also disables automatic weapon acquisition and shield absorption. Copying it unchanged would conflict with both the requested first-three-launch allowance and autonomous PDC defense, and would alter shield behavior.

**Pinned schema gap:** official revision `8e061033afe53b1393eaefd56617a3fd041eeb5f` lacks the four top-level buff fields `provides_cloak`, `required_product`, `cloak_alpha_value`, `cloak_fade_duration_value`; its modifier enum also lacks `cloak_quality`. Additional installed DLC constraints such as `is_cloaked` are absent from the old constraint enum. The actual stock cloak therefore fails the pinned schema on known enum values; Draft7's treatment of `unevaluatedProperties` can also silently accept unrecognized top-level fields. The report records the actual errors and omissions. No schema replacement/fetch or product-gate removal was attempted. Cloak observations are installed-code evidence, not a claim of complete matching-schema validation or entitlement behavior on a custom TEC ship.

## Four individual launches and fixed reveal window

There is an exact pinned trigger: **`on_current_spawner_spawned_torpedo`**. Installed `pirate_king_capital_ship_mag_blast_missile_on_self.buff` uses it, selects `trigger_event_destination`, filters `has_definition: pirate_large_torpedo_ability`, and applies a buff to that projectile. The same source creates torpedoes through `create_torpedo`, providing evidence for ability-generated missiles as well as normal weapon projectiles.

The standalone probe filters `trader_torpedo_cruiser_torpedo`, allowing a stock Ogrov test independent of imported assets. For Amun, replace that one filter with the final private Amun projectile ID. It does not count PDCs, rail shots or shuttle sprites. Its current state transitions are:

1. First, second and third individual qualifying projectile events increment count1,2,3.
2. Fourth event sets `reveal_until = simulation_time +60`, then clears count.
3. While the deadline is active, further torpedo events and tagged gun hits neither count nor extend it.
4. At/after the deadline, the next individual launch starts a new count. There is no requirement to land a hit and an intercepted/missed torpedo still consumes its launch allowance.

This means **four individual torpedoes**, not four paired salvos. A two-round burst crosses the threshold after its fourth projectile, normally the second pair. There is no duplicated weapon budget or fake projectile count. Buff float-memory writes and save-clock restoration remain runtime gates even though the action syntax is supported and related memory mechanisms are installed.

The probe does not contain `provides_cloak`, `cloak_quality`, or a visibility operator; its “reveal” deadline is telemetry for a later integrated cloak. Thus a schema PASS cannot be mistaken for a functioning stealth ship. Future cloak integration must map the deadline to observed cloak quality without resetting memory by manual toggling, ability refresh or save loading, and must preserve the DLC product gate. Quality/detector interactions need observation: three allowed launches do not guarantee no enemy detection.

## Conservative rail/PDC reveal policy

The pinned trigger enum has **no generic weapon-fired event**. `has_recently_fired_weapon` is a state constraint, not a discrete event; polling it cannot accurately count shots and would include torpedoes. Damage-dealt events occur at impact and misses never trigger them.

The probe includes the viable conservative **successful-hit** policy: append the private string tag `expanse05_cloak_revealing_gun` only to the three Amun PDC definitions and its private railgun, then use `on_unit_damaged_by_current_spawner` with `damage_has_weapon_tag` to start the same60s window. This exact constraint shape is installed in `dlc2_vasari_loyalist_super_empowered_strikecraft_on_strikecraft.buff` (stock tag `beam`); weapon tags are schema-supported strings, so the new private tag is a deliberate declaration, not an invented enum. Never attach it to torpedoes or boarding visuals. Gun hits while already revealed do not prolong the window.

This policy leaves firing-to-impact latency and **missed gun shots unrevealed**. It must not be advertised as immediate reveal on firing. The stock alternative `disable_can_auto_acquire_weapon_targets` reduces automatic fire while cloaked, but also suppresses the desired autonomous PDC network and does not by itself establish how explicit attack orders behave. Do not promise a permanently hidden fully active rail/PDC ship; keep the integrated release candidate incomplete until this policy and the cloak schema gap are resolved through a specifically labeled experiment. No routine user-approval gate is implied by this finding.

## Boarding: actual roll point, ownership and visual pod

Installed `pirate_boarding_crew.ability` uses a delayed action and `play_weapon_effects` with effect `pirate_pillage_shuttle`. That particle actually contains a mesh emitter referencing **`trader_asset_colony_shuttle.mesh`**. It is a modeled visual, but it is **not a simulated damageable boarding pod**. Its sprites/mesh cannot be intercepted by PDCs. The stock pirate mechanic applies a damage-over-time buff and captures at prevented target death; that is not the requested10% arrival roll.

The private probe replaces that mechanic. It preserves the stock3s delayed travel-action pattern and modeled shuttle alias, applies one private short-lived buff, and rolls exactly once in `on_buff_started`. `random_chance` with `chance_value`0.1 is documented by the schema as0 never/1 always and is used in installed combat buffs. On success, `change_owner_player` transfers to `unit_owner(first_spawner)`, matching installed Advent domination and pirate boarding ownership patterns. No damage, death prevention, hull restoration or repeated time action is added.

Target filter is enemy `capital_ship`, fully built, detected and in the same well, with an explicit `has_definition` exclusion for `expanse_rocinante_hero`. Titans and super-capital target types are excluded automatically by this narrow type list. Other mods' capital-class heroes require explicit additional exclusions; there is no verified universal “hero” flag. The normal Rocinante currently uses a non-capital target type but the explicit exclusion protects future changes.

Dynamic `per_build_or_virtual_supply` reads the target's actual supply. `required_available_supply` checks the cast, and `player_has_available_supply` with `include_future_supply: true` rechecks immediately before transfer. These are evidence-backed fields, but concurrent captures and supply reservation/overflow still need runtime tests. Cooldown180s, range6,000 and travel3s are inherited provisional probe settings. No automatic casting is added. One attempt has10% success; six independent attempts can reach roughly46.9% probability of at least one success, so the six-ship cap does not imply a whole-fleet10% capture limit.

“Arrival” here means **the scheduled delayed action**, not a physical collision event. A genuine interceptable pod would need its own unit, health/skin/mesh chain, a proven arrival/death distinction, and a capture callback that runs only after successful arrival. This stage does not claim that additional mechanism exists. Test travel visualization against actual transfer timing, target loss/jumps, caster death, duplicate attempts, pending-arrival saves, health/items/abilities after capture and multiplayer RNG before using the probe in ordinary play.

## Six-ship limit and weapon scope

Existing player definitions and the project's hero integration support `player.unit_limits.global` entries `{tag: private_tag, unit_limit:6}`, combined with the tag on the new unit and a declared unit tag. This is a **per-player empire limit**. It is not evidence for one shared six-ship pool across multiple players choosing the same faction. Preserve existing player lists/tags and append only the new ship/limit when main integrates. Queue, simultaneous factories, captured units and rebuild after losses need tests.

No Amun mounts were invented. Three actual PDC assemblies must be selected from the asset worker's source audit; each receives one firing budget. No change was made to MCRN projectile50 hull /100 armor /50 strength, damage750 or speed1,250.

At main's direction, `stealth05_combat.py` staged these explicit provisional Amun values in separate private definitions:

- Torpedo: damage900, speed1,500, hull25, armor50, **armor strength50**, penetration1,000. This supersedes the initial unimplemented strength25 suggestion. It retains the small Javelis mesh,240s life, same-well200,000 range and8/2/10/120 magazine logic. `expanse05_amun_torpedo` is the exact new projectile ID for the launch-counter filter.
- Heavy rail:3,750 damage,1,000 penetration,10s cooldown,375 nominal raw DPS. Existing MCRN/Rocinante rail remains2,500/1,000/10.
- Exactly three PDC definitions:28 damage/.25s/0 penetration/2,500 range,112 raw DPS each and336 with all three bearing. Existing target groups, enemy filter, visual bursts and per-gun budgets remain. Their copied Tachi turret fields were deliberately removed because no Amun pivots are approved yet; the weapons are unbound candidates.

All three Amun PDCs and its rail already have the private hit-reveal tag. Torpedoes do not. No ship unit, hardpoint coordinate or ability launch position was copied from a different model. The nine definitions require actual Amun geometry, private ship skin aliases, manifests, limit integration and separately resolved cloaking before becoming a package.

## Offline evidence and smallest tests

`stealth05_stage.py` ran against the recorded local game and SDK. All62 pinned schema blobs matched; all six standalone probe definitions passed Draft7 schema checks. The actual stock cloak's known schema failures are recorded separately rather than reported as passes. A deterministic Python model passed the intended count1/2/3, fourth-event reveal, non-extension, expiry and tagged-gun-hit transitions; it is not an engine simulation. A structural check confirmed boarding has exactly one random-chance constraint and ownership operator, no damage/death hook, and no repeated time action. `stealth05_combat.py` then passed nine additional candidate schemas and verified all198 files in the reviewed combined0.4 source package were byte-unchanged before/after generation. Source hashes, exact missing schema fields and actual projectile/model references are in the corresponding validation JSON. Complete probe packaging, texture/sound/UI reference resolution and mounting are not claimed.

Smallest workstation order:

1. Attach the counter probe to stock Ogrov and log individual launches4/5/6, confirm count/deadline with target loss and projectile interception. It should make no visibility change.
2. Append the private gun tag in a separate stock test, prove successful hits start the window and misses do not; verify continued events do not extend it. Save/load during count3 and mid-window.
3. Test the boarding probe alone against an ordinary capital, excluded Rocinante, titan, insufficient-supply player and two concurrent arrivals. Compare visible arrival with transfer time; record failures as well as successes.
4. Only after those results, combine with a separately resolved cloak implementation and actual Amun mounts. Test enemy detection tiers, toggling, three allowed torpedoes, fourth reveal, rail/PDC hit policy, destruction and save/reload.

No game tests were run by this worker. 0.4 remains separate and unchanged.
