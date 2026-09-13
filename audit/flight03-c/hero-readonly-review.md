# Read-only review — Rocinante abilities and acquisition

Reviewed main integrator `tools/hero03_abilities.py` and `build/hero03-main/generated/entities` without editing or running the generator. Source/output hashes and checks are in `hero-readonly-checks.json`. Ten ability/buff/action-data-source definitions pass the matching installed schemas; all six ability HUD/tooltip icon references resolve to installed PNG files. No concrete malformed definition or missing icon was found in this snapshot. Runtime behavior remains NOT RUN.

## Ability integration checks

- `fixed_level_0` is a pinned ability-schema enum. Installed `dlc3_herald_battle_capital_ship_cloak.ability` demonstrates this level source together with active actions and no antimatter-cost field. Belter Ingenuity can therefore use the same no-AM form; no guessed `zero_antimatter` setting is needed.
- The repair buff's `fixed_one` interval, `duration` interval count, `repair_damage`/`hull_only` operator and finite-time completion match `trader_combat_repair_system_unit_item.buff`. The scalar action-value array has one entry, consistent with level zero. Actual first-tick timing and total restored hull should still be measured.
- Overcharged Reactor follows installed `jiskun_tachyon_boost`'s `max_linear_speed` scalar modifier. The proposed 0.5 is a +50% maximum-speed modifier, not new angular speed or acceleration. **Cobalt has no antimatter component.** Hero unit integration must add a valid pool and restore rate for the explicit 50-cost ability to work; installed `trader_robotics_cruiser.unit` demonstrates `antimatter: {max_antimatter: 350, antimatter_restore_rate: 1}`. Choose intended hero values rather than silently inheriting “no AM”.
- Add the three abilities to the hero unit's observed `abilities: [{abilities: [...]}]` structure and include new ability/buff/action_data_source IDs in additive entity manifests. The candidates by themselves do not expose abilities on a ship.

## Morale aura

The proposed persistent passive ability shape matches `trader_colony_capital_ship_mobile_trade_port.ability`. The one-second scanning buff follows `trader_colony_capital_ship_inspiring_broadcast_on_spawner.buff`; replacing its radius action with the installed Jiskun gravity-well action uses verified fields and selectors.

`ownerships: [friendly]` is the same filter convention used by stock Inspiring Broadcast and Jiskun. The six included unit types cover ships, excluding structures/starbases and strikecraft as intended by the current description. There is no explicit self-exclusion, so expect the hero to be eligible if “friendly” includes self; verify own-player and allied-player recipients. This observation is stronger than an invented `allies_only` or priority field, but a runtime diplomacy check is still needed.

`hull_point_restore_rate` and `armor_point_restore_rate` scalar modifiers are present in installed `singularity_time_dilation_star_bonus.action_data_source`. A +0.15 bonus applies to natural rates. Zero natural regeneration stays zero, damage cooldowns remain, and `repair_damage` active/scripted restoration is not automatically boosted. The existing tooltip accurately states that limitation.

Recipient duration 2s with 1s refresh intentionally permits up to 2s lingering after departure or loss of source coverage. `fixed_one`/`for_all_players` on the recipient prevents two Rocinantes applying additive copies to the same target; second refresh restarts the same named buff. The native lifetime of the persistent emitter buff when its source dies, is captured or loses its ability is not established by schema validation. Observe cleanup, well transitions and save/reload. Do not describe the aura as instant-removal or prove nonstacking solely by passing a schema.

## Verified uniqueness mechanism

Prerequisites are research ID lists in the examined build schemas, not an observed owned-unit-count gate. There is a direct installed mechanism in `player-schema.json`:

```json
"unit_limits": {
  "global": [
    { "tag": "titan", "unit_limit": 1 },
    { "tag": "super_capital_ship", "unit_limit": 1 }
  ]
}
```

Installed TEC `trader_loyalist.player`, `trader_rebel.player`, and `dlc_trader_loyalist.player` use those entries. “Global” here is inside a player definition, providing a stock precedent for an empire-wide type/tag limit rather than a single planet's limit.

For the intended new hero, the main integrator can append a **private hero tag** and `{tag: private_hero_tag, unit_limit: 1}` to the relevant player limit lists, add that tag to the hero unit's `tags`, and add the hero ID to the intended players' `buildable_units`. Preserve every existing limit. Do not reuse `titan` or `super_capital_ship` for the hero: that would consume the user's normal endgame ship allowance.

Register the private tag's display name using installed `uniforms/unit_tag.uniforms`'s `unit_tags` entries `{name, localized_name}` plus localization. The matching schema supports `overwrite_unit_tags`; do not assume unobserved merge semantics. A reviewed append preserving the existing tag data is the conservative path. This required registration does not justify changing existing tags or faction balance.

A cloned Cobalt `build.build_kind = frigate` supplies a known ordinary frigate-factory path. The type remains a special named frigate unless additional hero progression systems are actually implemented. This review does not authorize extra leveling, faction or research changes.

Call this **configured one-per-empire using the installed tag limit**, not runtime-proven uniqueness. Test two factories ordering the hero simultaneously, multiple queued orders, cancel/refund, save/reload, capture/gift interactions if available, and whether another build becomes possible after destruction. The inspected mechanism does not establish a permanent once-ever acquisition rule or a universe-wide single Rocinante across all players.
