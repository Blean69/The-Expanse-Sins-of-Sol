# Operations/contact capability gate — 0.18

**No runtime or multiplayer test has been performed. Major recovery and study must remain disabled.** This worker does not change the playable package, installed game, Scirocco support, boarding, research, manifests, localization, or faction state.

Build isolated outputs with `python3 tools/update18_operations.py`. Output: `build/laboratory/update18/operations`. The four item/reward definitions pass the pinned SDK's native schemas. The Lua file compiles with local Lua 5.4; that is not a retail game binding check.

## Findings from installed native data

The retail `scripts/event_metadata.lua` documents a native event interface, API 0.6. It supplies callback-scoped `context.instance` / `context.shared`, simulation time and fixed ticks, per-instance completion/cancellation, unit existence, owner, current gravity well and position queries. `pirate_incursion.lua` exercises a multi-phase event with tracked real units. This is useful evidence for a physical operation prototype, but it does **not** prove serialization of custom tables across save/reload or deterministic retail multiplayer dispatch.

The native pirate script calls `context.show_notification(NOTIFY_PIRATE_INCURSION_STARTED, {})`. It also calls `NOTIFY_PIRATE_KING_ARRIVED` and `NOTIFY_PIRATE_INCURSION_TARGET_CHANGED` with `gravity_well_id` and `target_player_index`. These use existing pirate notification identities. The target index is not documented as an arbitrary operation actor or recipient selector. The installed localized text describes a pirate invasion; simply relabeling that global UI would interfere with actual pirate events. No custom actor/sector templating API was established.

The pinned action schema's `add_notification` branch accepts only `planet_conversion_started` and `planet_conversion_colonized`. `notification-uniforms-schema.json` closes the set of notification type properties with `unevaluatedProperties: false`. Installed planet-conversion buffs use those real events. They are not a supported generic operation broadcast.

Native derelicts are `capturable_unit` with `destroy_on_capture`; loot uniforms define collection durations/ranges and reward pools. The native derelict specialist modifies `unit_capture_points`. None of these definitions proves exclusive claim reservation, one-reward delivery for simultaneous claimants, clear-on-departure behavior, or a start alert after a particular capital commits. No replacement capture system was authored. No fixed placed-site reward was shipped because its binding to an actual placed objective has not been established.

`simulation:give_research(player, id)` exists, but attaching it to an unverified observer/timer would not meet paid commitment, object interruption, exclusive operation or replay requirements. It is deliberately not called here.

## Disabled smoke probe

`tools/update18_operations_probe.lua` and its generated script contain `PROBE_ENABLED = false`. There is no mod metadata or manifest, and the worker does not enable/copy it to the game. It is a laboratory fragment for a future explicitly assembled development package.

If enabled in that isolated development package, after 15 simulation seconds it attempts to spawn **one ordinary scout for player index 0 at that player's real home well**. It records the scout's ID, initial owner, actual well ID and position, then calls the native pirate global-looking start and location notice. It observes that specific object for 90 seconds. Death, owner defeat, owner change, leaving its original gravity well, or moving over 2,500 units from the initial position cancels the probe. Ordinary damage is not a cancellation criterion. No rewards, payment, research unlock, marker, vision sharing or forced camera movement occur. It leaves any surviving scout in place.

The probe logs actor name and actual numeric well ID; that log is **not** the required public actor/sector announcement. Native notification text/sounds remain pirate text/sounds. This probe cannot pass the full milestone by itself; it isolates what the engine actually delivers. No claim is made that its restart guard survives reload.

## Exact required game tests

1. A developer assembles the disabled script into a disposable operations-test package and verifies how retail script discovery/loading works. Enable only this probe in that disposable copy. Keep the playable package and current saves intact. Use a fresh three-human, non-allied lobby with player index 0's home outside the other two players' vision. Record game/package hashes and slot indices.
2. At commitment (after the tracked scout was actually created), record whether **all three** clients hear/see each native notice. Distinguish global start from targeted location notice. Confirm whether player identity and the actual named home well are displayed; inspect focus behavior without adding vision. A player-specific or generic-only result fails the production announcement gate.
3. Repeat in fresh sessions: normal completion, scout death at 30 seconds, movement beyond 2,500 range, jump out, capture by another player, owner defeat. Record whether termination arrives on each client exactly once. Ordinary incoming damage that leaves the scout alive/in-range should not reset progress. No research or material reward should ever appear in this smoke test.
4. Save at 45 seconds and reload as host and clients. Observe whether the original scout/owner/time survives, whether another scout appears, whether historical notices replay, and whether interruption/completion fires once. Test host change and disconnect separately. Do not call this synchronization verified from a successful local run.
5. Before implementing recovery, establish a supported commitment binding to the **real site and eligible claimant**, exclusive claims, ownership changes, reward availability/full slots and exactly-once settlement. Two simultaneous capitals, two sites, cancel/retry, scuttle and captured/summoned units require separate trials. A scout automatically spawned by this probe is not a salvage operation or a paid lab study.
6. Only after a genuine custom notification interface or a narrowly scoped non-conflicting native path is demonstrated, implement generic sound plus actor/event/actual-sector text. Repeat the enemy-without-vision test at commitment. No completion-only or owner-only substitution is accepted.

All cases above are currently **NOT RUN**; elapsed multiplayer test duration is **0 minutes**.

## Contact fragments and economics

The generated `contact-fragments.json` is project integration data, **not** a `.player` file or invented engine field. The integrator owns full NPC wrappers, registration, scenario placement and localization. These fragments also remain disabled pending native service tests.

| Contact | Service | Native pattern and initial bounded cost | Mechanical scope |
| --- | --- | --- | --- |
| Tycho Engineering Bureau | Recovery Component | `ship_component` reward; reputation 2, 4 Influence, 360-second service cooldown | One normal equipment slot; one copy per ship; +15% native capture points; no XP bonus or reward generation. Existing derelict-specialist research prerequisite retained. |
| Ceres Shipping Exchange | Bonded Material Shipment | `assets` reward; reputation 0, 2 Influence, 240-second cooldown | 300 metal once per purchase, owner receives it. No input refund, credit conversion, repeating income or automatic reward. |
| Ceres Shipping Exchange | Temporary Shipping Registry Access | Existing `jiskun_share_vision` ability reward; reputation 1, 4 Influence, 600-second cooldown | Native NPC scouts share ordinary vision for 360 seconds. Not stealth detection and not a permanent full-map reveal. |

The recovery component's `unit_capture_points` modifier is a **general native capture modifier**, not an isolated major-recovery speed multiplier. Its interactions with captureable objects and native capture mechanics still need testing. It does not add a boarding ability. Do not advertise a 15% reduction in duration: a +15% rate would correspond to approximately 13% less time only where native behavior is strictly proportional. Existing Rocinante/Scirocco combat abilities remain untouched; their requested bespoke recovery specializations depend on the major-operation gate.

The influence costs are based on native Pranast tiered services (1/2/4/6 Influence and 180/240/360/480 seconds), and rewards use documented existing types. Repeated shipments still require Influence and cooldown; no self-funding buy/sell conversion is authored. This is an initial economic review, not measured multiplayer balance.

The Tycho contact is separate from the player-built station and cannot consume a player station allowance. Native NPC references begin allied to playable players, which is service diplomacy rather than automatic OPA ownership. A full clone must audit native fleets/support abilities before claiming it cannot repair visitors; this fragment adds no visit-triggered aura. Keep Ceres itself contestable and put the NPC home at a separately named Freeport. Preserve native markets rather than deleting them from reference NPCs. Late sample authorization is explicitly **GATED**, with no fake/free composite reward.

Before adding contacts to a friends package: verify all three clones can purchase the same services, rewards go only to the buyer, items obey full-slot/research/one-per-unit constraints, captured equipment behavior, repeat purchases/cooldowns, native service range, NPC loss, save/reload and multiplayer settlement. Existing faction research remains per owner.
