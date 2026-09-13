# Gate 1: three identities and three homes

This worker supplies an **offline candidate**, not a demonstrated runtime pass. The installed fixed-map archive is sufficient to generate the scenario; no editor-created seed needs to be requested. SolarForge open/save, game loading, viable construction/victory and multiplayer still need direct observation before the full Sol map is built.

Build from this worktree with `python3 tools/update18_scenario.py`. Use a fresh `--output` for repeat builds; the builder refuses to overwrite existing output. `python3 tools/update18_scenario_test.py` runs malformed-source rejection controls. Dependencies are the readonly 0.17 package, installed Sins2 data, pinned SDK, Python and jsonschema. The editable maintained source is `tools/update18_scenario_source.json`.

The ignored output contains:

- `overlay/entities/`: three full player wrappers generated from one 0.17 `trader_loyalist.player`, four start-mode overlays, and one scenario-only equal home unit.
- `overlay/scenarios/expanse18_sol_three_homes.scenario`: a deterministic native ZIP with all four required members retained.
- `editable/`: unpacked chart/fillings/metadata for inspection and editor handoff.
- `fragments/registrations.json`: project instructions for the integrator's shared manifest, uniforms, localization, and orbital cannon merge. **Do not copy this JSON into an engine configuration file.**
- `fragments/availability.json`: identical per-identity availability records for later restrictions.

Registration requires all three `.player` IDs in `player.entity_manifest` and `player.uniforms.pickable_players`, plus explicit `page_definitions`/`faction_portraits` entries in `gui/front_end_faction_picker_dialog.gui`. The fragments provide three named single-identity pages using the installed single-faction layout, with native TEC portrait placeholders. Existing pages remain. Cloning only `.player` files or adding only `pickable_players` is insufficient. Every native start mode has explicit `player_definition_id` entries; the generator clones the Enclave entry for all three identities in basic, normal, quick and advanced modes. Real picker availability remains a runtime test. Existing players, DLC registrations and original start-mode entries must remain intact.

All three identities use race `trader`, the existing TEC UI, and the same fleet/structures/research/items/ship voices/AI behavior. Names and descriptions are separate localization keys. Existing Truman, Raptor and Pella silhouette icons differentiate UNN/MCRN/OPA independently of player color. These are interim faction badges, not assertions of exclusive hull availability. No new assets or voice generation is required.

The only exact player-ID gate found in baseline mechanics is `trader_orbital_cannon_structure.unit`: its Enclave ability group is restricted to `trader_loyalist`. The fragment appends that unchanged group, including `expanse11_no_shields`, for each clone ID. The Rebel and original Enclave groups remain untouched. The installed non-TEC ability gates are unrelated Vasari/Advent hulls. The integrator owns this shared-unit edit.

## Inherited gameplay and ownership

The generated wrappers preserve every non-presentation field exactly. `report.json` records the full shared gameplay hash, availability, native start configurations, limits, and inherited defaults. This is a parity audit, not removal of existing TEC mechanics:

- Homeworld Home Guard Command, Enclave garrison rules and home income/slot bonuses are identical for all three.
- Civilian research tiers retain income, population and trade bonuses; military tiers retain their existing hull/armor and other baseline modifiers. No clone-specific economic or combat bonus is added.
- Culture retains researched friendly movement bonuses and enemy production penalties. Existing ally/enemy semantics are preserved; these effects are not proof of cross-owner research leakage.
- Trade retains Morrigan/Tachi escorts and original rates. All three use the same supply progression from 100 to 2,000.
- Normal starts are 6,500 credits, 1,650 metal and 850 crystal; the same factories, retrofit bay, two Sunflare scouts, population 500 and home-track levels. No custom exotic starting stock is added.
- Hero limits are the native player-wrapper limits: Rocinante 1, Pella 1, Amun-Ra 6, titan 1, super-capital 1. `global` here is a scope inside each player definition; it is not a new shared mod counter. Per-owner behavior is inferred from the native structure, with three-owner build/research/save/capture tests still pending.
- The baseline shieldless abilities and research overlays remain shared. No item, weapon or research balance is changed by this worker.
- AI names/taunts/voices still use existing TEC content and may mention TEC. They are presentation placeholders; AI gameplay configuration is identical.

## Skeleton and home assignment

Select **Sol — Three Homes (Gate 1)**, Normal start, three non-allied human slots. Slot 1 = UNN/Earth; slot 2 = MCRN/Mars; slot 3 = OPA/Jovian Habitats. Recheck assignments after changing host or rearranging the lobby. Other faction/slot orders are not supported as automatic home mappings. The archive sets native `are_player_slots_randomized=false`; ownership uses zero-based `player_index` 0/1/2. Nothing attempts to infer identity from freely chosen names/colors.

The chart has seven nodes: Sol, the three homes, an unowned linked Jupiter utility well, and two native NPC market annexes. Each home has two direct useful outbound routes; the three pairwise home distances differ by less than 0.1%. Earth and OPA connect without traversing Mars. Sol has one lane and is not an all-home shortcut. Both NPCs are off the direct invasion corridors, and retain native neutrality/markets without becoming playable factions. This small fixture has no early expansion colonies: it is a construction/ownership/victory probe, **not the final friends-playtest geography or a claim of full map balance**.

OPA's victory home is an ordinary eligible, visible, colonizable home named **Jovian Habitats**, with a temporary terran visual. It is linked to the separate unowned gas giant named Jupiter. It is not Ceres, an invisible target, or a surface settlement on a gas giant. All three homes intentionally share the same placeholder native terran skin and economics until the art/normalization gate is proven. No vanilla planet is globally reskinned.

Scenario-local `random_terran_home_planet` filling selects `expanse18_equal_home`: native terran mechanics with precisely two metal and one crystal asteroids and no random extra extractors. This is necessary because the installed terran unit otherwise has variable extra asteroid counts. The override uses documented local filling structures; **actual home-selection precedence must be inspected in the game** before claiming equal observed economy. The full chart and native minimum-distance interpretation also need editor/runtime inspection; the offline overlap check is a conservative map-center separation test only.

`can_gravity_wells_move=false` and zero orbit scalars use installed fixed-scenario patterns. No runtime timers or orbital rewrite exist. Extended-session fixed orbits are untested. The ZIP retains the installed seed's thumbnail as a clearly documented temporary picture; it is not a Sol rendering.

## Capability boundary and acceptance handoff

Installed `scripts/event_metadata.lua` exposes `player.home_planet`, `player.player_index`, `player.race`, and indexed ownership queries. The `player.race` description mixes race/faction terminology and has inconsistent example IDs; it does not establish reliable clone identification. No verified start-time home reassignment API was found. The candidate therefore uses the explicitly permitted fixed-slot fallback and a lobby warning rather than an unproven scripted reassignment.

Offline observed passes: both pinned schema drafts for chart and known player/unit fields, unchanged-source allowance for newer installed fields, scenario-local filling schema, exact gameplay equality, all four start-mode parity, unique IDs/parents/lanes, connected graph, native filling/NPC references, three eligible home slots, deterministic archive/member bytes and negative controls. The pinned SDK lacks a start-mode entity schema and scenario-info schema; those two formats are validated against exact installed templates and observed fields, not falsely reported as schema-validated.

Still required, with zero multiplayer minutes observed here:

1. Integrator merges the fragments and loads the same package and dependencies on all clients. Scenario streaming does **not** distribute the complete mod fleet/audio/assets.
2. Open the scenario in SolarForge with the integrated mod asset search path, save a separate roundtrip copy, and compare names, slots, fixtures, node count, lanes and absence of generated objects. No CLI roundtrip has been claimed.
3. Run a three-human non-allied Normal-start test. Verify picker identities, exact homes, resources, population, extractor counts, build slots, first ship construction, per-owner research and independent hero allocation.
4. Check defeat/victory after each home loss, host changes, intended slot permutations, save/reload and an extended static-orbit session. Confirm markets remain usable.
5. Only after these gates pass, generate the full 24–28-node geography and test expansion/travel fairness. All later operation/study/asset experiments stay separate until their own gates pass.
