# Runtime results

## User workstation observation — after the headless checkpoint

The user reports the Tachi model loads with both baseline mods enabled and fixed autocannon shots originate at the intended visible mounts. Three supplied screenshots show the ship in Sins II, severe missing/backface-culled hull surfaces and firing tracers. This establishes **user-observed loading and fixed-muzzle firing**, not successful turret rotation or interception.

`settings/.enabled_mods` confirms `expanse_cobalt_name` and `expanse_corvette_visual`. Existing `logs/sins2_log_492.txt` records enabling/loading both at 22:31 and lists the visual simulation mod. It also reports missing `display_name` and `logos` in old baseline metadata, then loads using fallback values. Loading therefore does not establish an error-free session. No agent launched the game.

- Evidence: `audit/polish/evidence/codex-clipboard-*.png` (unaltered user screenshots); installed log above, SHA recorded in the polish audit.
- Model loading: **PASS, user-reported and screenshot-supported**, both baselines together; standalone mod combinations not established.
- Fixed muzzle placement: **PASS, user-reported**; screenshot shows firing, but exact emitter placement is not independently measured.
- Surface appearance: **FAIL**, missing hull surfaces visible.
- Six independent PDCs, rotation, dual-purpose interception: **NOT IMPLEMENTED in tested baseline / NOT RUN**. The sequential firing medium autocannon is its expected retained vanilla weapon.
- Save/reload, destruction, construction timing, performance, stock PDC experiment: **NOT RUN / not established by this report**.

The six-PDC polish candidate is a new variant. Its runtime results remain NOT RUN until the user tests that exact package.

## Historical headless preparation

2026-09-12 — Headless setup only. No project game session observed at that checkpoint. All construction, movement, firing, PDC, selection, destruction, save/reload and performance acceptance tests: **NOT RUN** at that time.

Installed but not enabled: `expanse_cobalt_name`, `expanse_corvette_visual`.
Combat candidates and rig candidates are not installed.

## Observation template

- Date / observer:
- Game version / build:
- Mod variant / commit:
- Experimental mod ID / package ZIP SHA-256:
- Source-tree SHA-256 / dirty source state / provenance sidecar:
- Offline dependency report / enabled-mod list:
- Camera distance / zoom:
- Map / faction / research / bonuses / ship counts:
- Test ID and steps:
- Expected:
- Observed:
- PASS / FAIL / BLOCKED / NOT RUN:
- Screenshot, video, save and log paths:
- Follow-up:

## Experimental preparation, 2026-09-12

Stock Garda/Ogrov behavior is packaged; the separate one-Tachi-PDC rig is a candidate blocked by its offline shading-frame check. Their offline records are under `audit/experiments/`; package/provenance files are under ignored `build/experiments/`. See `docs/experiments.md` for availability and limitations. Neither experiment was installed or enabled during preparation. No game was launched. Every runtime row above and in the checklist remains **NOT RUN**.

For PDC observations also record physical mount index, target type/filter group, explicit order, switch latency, cooldown/visual burst versus damaging events, and per-gun/aggregate damage. Record penetration, target durability, armor strength, armor and hull separately. Record whether an intercepted projectile later causes damage.

## User Apply Changes failure and 0.2.1 correction

User-reported Sins II 2.0.3 (318), Proton: **FAIL** applying `expanse_corvette_polish` 0.2.0, `attack_target_type_groups do not match weapon:expanse_polish_pdc_0.weapon`. The same error was found in installed `logs/sins2_log_484.txt`. Corrected the unit explicit group list to match its PDC weapon; retained the unit-level ignore list and every weapon/asset file. Installed mod and ZIP now match version 0.2.1; prior files backed up in `build/hotfix-0.2.0`. Offline checks PASS; retrying Apply Changes in-game is **NOT RUN by agent / awaiting user observation**.

## User workstation observation — six-PDC polish 0.2.1

2026-09-12: user reports that the PDCs now track individually and that the tracers look high quality. This establishes **PASS, user-reported individual tracking and firing appearance** following the 0.2.1 loader correction. The exact enabled-mod combination and package hash were not independently captured during that session. No agent launched the game.

Three new unaltered screenshots are retained in `audit/combat03/evidence/`. The user reports residual hull holes and floating PDC geometry: **FAIL, surface/attachment appearance**. These are the basis for the new derivative. Interception priority during an explicit ship attack order, simultaneous damaging cadence, save/reload, construction, destruction and fleet performance remain **NOT RUN / not established by this report**.

The new 0.3 corvette and hero work are distinct from the user-tested 0.2.1 package. Every new ability, torpedo, flight-pattern, phase-plume and hero runtime test remains **NOT RUN** until its exact package is tested.

## User workstation observation — 0.3 combined setup

2026-09-12: user reports both ships' movement looks excellent and the Rocinante railgun feels balanced. Treat these as **PASS, user-reported movement appearance and subjective railgun balance**, not measured cadence/damage or all acceptance gates. User reports torpedoes visually oversized and Rocinante bent/crooked; the screenshots support oversized missile appearance and visibly missing hull panels. Surface/shape appearance: **FAIL**.

Read-only `settings/.enabled_mods` snapshot contains `expanse_rocinante03` and `expanse_corvette_combat03` together. Both override Cobalt; the report therefore does not identify which ordinary torpedo implementation was active. The next package must be tested alone. No agent changed enablement. Screenshot originals and installed/build hashes are in `audit/combat04/`. Exact ammunition retention, interception prioritization, save/reload, rail damage timing and standalone package behavior remain **NOT RUN / not established** by this report.
# New 0.4 / optional 0.4.1 results — NOT RUN

Prepared packages: `expanse_rocinante04` (`fa00d7e1de5dca57a4728b3dcb2d7c0b6660afdbbd1dfef9ef638a6a68cb1ff0`) and its mutually exclusive `expanse_rocinante04_amun` alternative (`0037f2f5d06046bd442231372690f999f84a6fefbca023955017a4c3a2368e74`). Neither was installed, enabled or launched during this assignment.

| Gate | Result | Evidence to record at workstation |
|---|---|---|
| Loader / construction / selection | NOT RUN | Exact enabled mod and package hash, log errors, hero cap |
| Corrected hull / six hero PDCs | NOT RUN | Surfaces, pivots, clearance, arcs, moving muzzle alignment |
| Small/custom projectile | NOT RUN | Nose/trail/shading, scale, turns, damage and actual interception |
| Attack-order defensive response | NOT RUN | Ship attack order plus incoming torpedoes, gun target choices |
| Magazine / salvo / save reload | NOT RUN | Individual launch times, remaining rounds, reload deadline, restored state |
| Navigation / rail regression | NOT RUN | Preserve previously user-approved appearance and damage/cadence |
| Formation / fleet performance | NOT RUN | Same camera and fleet comparison, including higher-detail unique hero |
| Amun cloak / limit / boarding | NOT RUN / INCOMPLETE CANDIDATES | Separate probe integration and schema-gap resolution first |
| Donnager gameplay | NOT RUN / NO GAME PACKAGE | Planning assets only |

Earlier user observations below apply to the earlier enabled setup, not these new binaries. Complete runtime observations in this same log; do not infer a pass from schema checks or source previews.
# User workstation acceptance — 0.4.1 follow-up

The user reports: “Torpedos look amazing, rocinante looks miles better, PDC's track properly!” and “Performance with the rocinante is still excellent,” explicitly accepting the current polygon count for the unique hero. The user also accepts continuing with the timed boarding visual.

Read-only inspection now shows **only `expanse_rocinante04_amun` version0.4.1 enabled**. Its installed tree is preserved in `audit/amun06/checkpoint.json`; compare that snapshot to the built package when evaluating this result. No game was launched by the agent.

| Gate | Result | Scope of evidence |
|---|---|---|
| Custom torpedo appearance | PASS — user observed | Visual quality; not a separate measured damage/interception test |
| Corrected Rocinante appearance | PASS — user observed | User reports substantial improvement |
| Independent PDC tracking | PASS — user observed | Tracking works; exhaustive arcs/occlusion not separately logged |
| Current unique-hero geometry/performance | ACCEPTED — user observed | Keep92,067triangles; do not start another optimization pass |
| Timed boarding visual approach | ACCEPTED DESIGN | Continue scheduled visual; no claim that capture behavior was tested |
| Amun gameplay, cloak, boarding, limit | NOT RUN | New integration work follows |

Earlier NOT RUN rows describe the previous delivery checkpoint and are superseded only for the specific observed gates above. Ammo persistence, measured interception and save/reload remain unverified unless separately reported.

## Amun0.6 follow-up runtime record

All new Amun rows below remain **NOT RUN**. Timed modeled boarding is accepted design, not a tested engine result. Existing user observations at the top of this log remain scoped to0.4.1.

| Gate | Result | Evidence to record |
|---|---|---|
| Core load/build/limit6/UI | NOT RUN | Variant hash, TEC player, parser log, queued seventh behavior |
| Three PDCs and explicit attack-order interception | NOT RUN | Per-gun cadence, coverage, damage and tracking clip |
| Private rail/torpedo mounts and ammo | NOT RUN | Shot times, eight-round reload, interception health comparison |
| Timed modeled boarding | NOT RUN | Cast/travel/capture timestamps, target supply, owner, repeated trials |
| Source/target loss and pending boarding save | NOT RUN | Save and logs before/after delayed attempt |
| Optional cloak fourth missile and60s reveal | NOT RUN | Entitlement, detector, second pair, extra shots and hit/miss cases |
| Cloak toggle and counter/reveal save | NOT RUN | Count3 and active-window saves, expiration behavior |
| Destruction, formation and fleet performance | NOT RUN | One, small group, six plus unique hero; timings and screenshots |

Use the existing detailed [checklist](../docs/manual-test-checklist.md), section Amun0.6. No new game session was launched by the agent.

## Rocinante voice0.7 runtime results

| Gate | Status |
|---|---|
| Load voice variant and hear spawn/selection | NOT RUN |
| Order/attack/retreat/jump/armor and mood events | NOT RUN |
| Perceived consistency, clipping, background and source completeness | NOT RUN |
| Rapid-order suppression, destruction, save/reload | NOT RUN |

Offline only: eleven Vorbis files passed decoded loudness/peak/duration checks; exact dialogue-only skin differences and pre-existing package preservation passed. Twelve original clips remain intact, XO held and short juice missing. The agent did not audition or launch the game.

## User report and correction0.8

USER OBSERVED: Amun only exposes the torpedo magazine (attached screenshot). Boarding and cloak were not confirmed. Local enabled setting at inspection: `expanse_amun06_voice07` (no-cloak variant). Offline diagnosis: abilities were split into alternative unconditional sets; corrected to one shared set, including Rocinante. New UI visibility, boarding capture, enemy-view cloak, hero active/passive behavior and six new audio lines: **NOT RUN** after correction. No ship/fleet supply rebalance occurred.

## Soundtrack0.9

USER APPROVED: Welwala, Boarded and Signal for combat; Signal cropped to begin at1:05. OFFLINE PASS:13 normalized Vorbis records, correct channel layouts, Signal64.92-second derivative, pinned race/music schema, exact state/media references and unchanged0.8 ability/voice content. Main menu, state transitions, loops, mix and all newly fixed ability controls: **NOT RUN**. No listening or game launch claimed.

USER APPROVED additions: Never See Them Coming and Hammerlock are combat tracks too. Final0.9 now contains15 music recordings; the earlier13 normalized tracks are unchanged and Signal still starts at65seconds. Both additions passed measured normalization, stereo/duration and Ogg checks. Playback/listening remains NOT RUN.

## Latest user-observed0.9 acceptance

The user reports: cloak is working, boarding is working, and music is great. The enabled mod at inspection is only `expanse_amun09_cloak`, display0.9.0. Installed tree SHA-256: `bb5506432e7666dc0d25bf00573bd7930b5d4463d4df4a87597ddf371323c2d8`. It matches the packaged0.9 tree.

| Behavior | Result / evidence boundary |
|---|---|
| Cloak basic functionality | PASS — user reported; agent did not run the game |
| Boarding basic functionality | PASS — user reported; exact capture counts/targets not supplied |
| Music playback / subjective mix | PASS — user reported |
| Fourth torpedo / exact60-second reveal / detector interactions | NOT ESTABLISHED by this report |
| Capture10% statistical rate, supply races, caster/target loss | NOT ESTABLISHED by this report |
| New-feature save/reload and larger-fleet performance | NOT ESTABLISHED by this report |

This supersedes earlier blanket NOT RUN entries for the three reported basic behaviors only. Existing detailed edge-case checks remain pending. No installed files or source assets were modified to record this result.

## Donnager0.10 runtime record

Game/SDK references remain the recorded2.0.3(318)/pinned revision. New package ID `expanse_donnager10`; package hash comes from `audit/donnager10/package-summary.json`. Not installed or enabled by the agent. **All Donnager runtime tests NOT RUN.** Do not transfer the user's0.9 observations to this new battleship.

| Test | Setup / observations to record | Result |
|---|---|---|
| D10-1 build/limit | Faction, titan research/factory, existing titan/queued titan, costs/supply, component slots, visible controls, logs | NOT RUN |
| D10-2 rig/visual | First PDC0/rail0, camera angle, target bearing/elevation, muzzle/foot contact, then all mounts, travel/shield/UI | NOT RUN |
| D10-3 weapons | Ship level/items, per-mount firing timestamps, target shield/armor/hull, incoming torpedoes during attack order, front/rear salvo and reload | NOT RUN |
| D10-4 abilities | Reactor timestamps and remaining magazine state, corvette ownership/cost/supply, boarding attempts/captures/invalid targets and600s cooldown | NOT RUN |
| D10-5 failure/recovery | Blast owner/allies/enemies and distances, saved timers, performance ship counts/settings/FPS, accepted0.9 regressions | NOT RUN |

## PDC sound0.10.1

All four Expanse ships use the supplied normalized PDC muzzle clip in the separate0.10.1 package. Playback, overlapping guns, volume and zoom attenuation: **NOT RUN**. Prior gameplay and sound definitions are preserved except the four explicit skin sound bindings. The reboot-interrupted first ZIP is unusable; test the verified `_ready.zip` from `docs/pdc-audio10.md`.

## User report before update0.11

USER OBSERVED on the prior Donnager/PDC-audio package: PDC sound is good; Donnager explosion deals the desired damage; three Donnagers produced no noticeable performance hit. Donnager selection repeats standing-by, hull looks jagged, reinforcement appears broken/Cobalt icon, Amun refuses titan targets, and close-orbit frigates can kite Donnager defenses. These supersede blanket NOT RUN only for the reported earlier observations; no agent game test occurred. Screenshot `codex-clipboard-9ea5a814-e88b-433c-a4b2-33f071fea9d6.png` depicts the earlier Donnager.

## Update0.11 workstation results

New package and hashes: `audit/update11/package-summary.json`. The agent did not install, enable or launch it. Record timestamp, settings, fleet count, target and logs per row.

| Gate | Result | Observations |
|---|---|---|
| U11-1 load/build/supply/shared scope | NOT RUN | |
| U11-2 paid reinforcement/failure/concurrency | NOT RUN | |
| U11-3 geometry, mounts, sprites, voice, drive | NOT RUN | |
| U11-4 PDC targeting/damage/torpedo schedule | NOT RUN | |
| U11-5 command/titan capture and shield policy | NOT RUN | |
| U11-6 destruction, save/reload, performance | NOT RUN | |

Offline check results belong in `audit/update11/package-validation.json`; successful file/schema/reference checks do not advance these runtime rows.

## Update 0.12 workstation results

The agent did not install, enable or launch this package. New capital/scout/emblem behavior has not been observed in game. Package/hash: `audit/update12/package-summary.json`; offline evidence belongs in `audit/update12/package-validation.json`.

| Gate | Result | Observations |
|---|---|---|
| U12-1 apply/build/supply/hero and titan limits | NOT RUN | |
| U12-2 Pella eagle, models, mounts, sprites, voices, plumes | NOT RUN | |
| U12-3 individual weapons, interception and torpedo timing | NOT RUN | |
| U12-4 reactor, reinforcement, boarding and Sunflare burn | NOT RUN | |
| U12-5 destruction, save/reload and full-fleet performance | NOT RUN | |

Record ship level/items, target state, timestamps, exact package hash and logs before marking any gate observed. Earlier successful user reports do not certify these new assets or behaviors.

## User observations following update 0.12

USER OBSERVED: new fleet models load and look broadly good; Scirocco/Morrigan appear mostly uncolored; Razorback presents its lettering on the wrong-facing axis; no clearly visible rotating Scirocco PDCs; PDC audio sounds good individually but bunches together near many guns. Screenshots supplied in the update0.13 request show those models and Raptor/Pella faceted lighting. This establishes visible loading and reported defects only, not a full pass for earlier U12 gameplay/ability/performance gates.

## Update 0.13 workstation results

New derivative package/hash: `audit/update13/package-summary.json`. No agent installation or game launch. Offline measurements do not mark runtime results passed.

| Gate | Result | Observations |
|---|---|---|
| U13-1 load / painted hulls / Raptor-Pella lighting | NOT RUN | |
| U13-2 Scirocco physical PDC tracking, muzzle and support | NOT RUN | |
| U13-3 Razorback orientation, drive and movement | NOT RUN | |
| U13-4 close/far PDC audio mix with one ship and fleet | NOT RUN | |
| U13-5 save/reload and unchanged gameplay regression | NOT RUN | |

## User observations following update 0.13

USER OBSERVED: the Scirocco exterior appears transparent, Raptor/Pella still have visibly coarse hull and engine geometry, and their PDCs can fire through their own hull. The five supplied screenshots are hashed in `audit/update14/checkpoint.json`. The checkpoint finds `expanse_update13` enabled and an installed copy present. These observations establish defects in the tested configuration, not full passes for the earlier runtime gates. Installed settings changed through user testing since the previous checkpoint; existing recorded mod trees did not change. The 0.14 assignment preserves this new starting state.

## Update 0.14 workstation results

The agent does not install, enable or launch the candidate. Offline checks cannot establish engine firing-angle conventions, final visibility or performance.

| Gate | Result | Observations |
|---|---|---|
| U14-1 load / Scirocco exterior / restored capital detail | NOT RUN | |
| U14-2 Raptor/Pella PDC arcs and incoming torpedo coverage | NOT RUN | |
| U14-3 save/reload and representative fleet performance | NOT RUN | |
