# Doctrine foundations: bounded Stage 2–5 audit

This work is based on frozen `build/experiments/expanse_update19`, installed game2.0.3(318), and the existing pinned SDK. It does not attribute gameplay observations to new fragments. All generated changes are **offline checked / runtime NOT RUN**. No game install, enable, launch, remote push or shared main definition was performed.

## Stage 2 deliverable

`tools/doctrine_colony_fragments.py` exposes:

```python
edits, strings, origins, report = changes(base, opa_command_id=None,
                                         prefix='expanse_doctrine')
```

The main integrator supplies its current Stage 1 directory as `base`. With an OPA command ID, the helper emits10 entity definitions: three normal colony components, three abilities, three action sources, one shared native planetary-bombing weapon. Without OPA it emits7. `origins` maps every entity to a concrete installed donor for extension-aware validation.

**No shared unit or skin is returned in `edits`.** Merge `report.unit_patches` into the current units, preserving costs, supply, health, combat weapons, active ability lists and magazine definitions. Patch operations are:

- `tags_append`: eligibility only, also merge corresponding `report.unit_tag_entries_append` into the existing explicit unit-tag registry. These are unit tags, never weapon tags.
- `item_builds_append`: native equipment build recommendation; add the generated components to the intended player's `ship_components` list too.
- `colonize_ability`: native command reference to the item-granted ability.
- `weapons_append`: one separate native siege-store installation.
- `report.skin_patches`: merge aliases by `alias_name` into every relevant skin stage. The OPA command patch assumes main creates a same-ID skin cloned from Europa, not a mutation of the existing Europa frigate.

The helper reads actual compiled hull mesh points and existing `ability_positions`. No new import is required. It records the exact local launch frame and source path for every siege installation. Scirocco's colony shuttle uses `weapon.light_torpedo.0`; Truman/Europa use `weapon.torpedo.0`. The older Tachi/Rocinante/Donnager torpedo rigs use explicit ability positions; native weapon `non_turret_muzzle_positions` uses those local positions. Donnager's siege frame is its real aft heavy-torpedo launcher, so facing behavior needs the normal runtime test.

### Colony mechanism and four-button constraint

Installed `gui/hud_ship_window.gui` defines `ability_0_button` through `ability_3_button`, and four corresponding level-up buttons. Scirocco already uses four meaningful active slots: reactor, launch, breaching, engineering. The unit schema's unbounded ability array is **not** proof of an unlimited visible bar.

Native `trader_radiation_bomb.unit_item` proves `ability` attachment; `trader_combat_repair_system_unit_item.ability` demonstrates an item ability. The generated reusable colony module occupies one existing ship-component slot instead of overwriting the ship's buttons. Its only allowed units receive a private eligibility tag; `required_unit_tags=['capital_ship']` alone would leak purchase access to every capital. Every generated component has `max_count_on_unit=1`. Main should preserve the normal `items.levels[].max_ship_component_count=4` framework.

The module copies the first level of native Akkan `trader_colony_capital_ship_colonize`:120AM,120s cooldown,5000 range,3s travel. `level_source='fixed_level_0'` removes the XP dependency; no new research prerequisite is present. The native target filter remains `uniforms_colonizable_planets` (unowned planet + `is_colonizable_planet`), and the actual operator is `colonize_planet`, not an ownership mutation. The normal Akkan colony initialization buff is preserved, including first-level +1 commerce/+1 logistics and price offsets. This is explicit native colony support, not a new ownership shortcut.

Component price is the installed specialist item's475credits/75metal/75crystal,20base seconds. The current player wrapper's missing-component-shop scalar10 means200seconds away from a shop. It is available at level1 without battle XP, but is a paid fitting. If that delay is undesirable, main should choose and disclose an explicit module build-time adjustment rather than silently altering the player's global scalar. No native colony frigate access should be removed.

**Runtime gates:** module appears on the three designated capitals at level1; item ability is usable from the normal item panel; the native `colonize_ability` command resolves an item-granted ability; insufficient AM/resources, missing planet tech, live enemy/neutral owned worlds, already colonized worlds, queued colony ownership changes, save/reload. Without fitting, the capital has no valid colonize ability instance; this is intentionally an equipment path.

### Bombardment inventory and abstraction

No existing custom ship inspected in0.19 has a native planetary-bombing weapon or colony pointer. Actual heavy-object carriers are Donnager and Scirocco (`expanse10_donnager_heavy_torpedo`). Tachi and Rocinante use the *light* projectile even though inherited action-value IDs say `heavy_torpedo`; the helper includes them because the new doctrine explicitly requires checking/providing that expeditionary siege role. Truman receives a separate siege-only installation to satisfy its designated colony-capital role. The new OPA command also receives siege-only stores. Light-only Morrigan, Amun-Ra, Raptor, Pella, existing95-supply Europa remain out of the proposed bombardment set.

The native Akkan weapon provides75planet damage and3population damage per15seconds at4000range. `weapon_type='planet_bombing'`, `acquire_target_logic='order_target_only'`, and `common_planet_bombing` (enemy planets only) preserve explicit hostile local orders. This uses **separate siege stores**; it neither consumes nor modifies anti-ship magazines. A native projectile visual is **not interceptable ordnance**. Do not relabel it an actual destructible IPBM.

Installed `bombing_damage=75.0` is absent from the pinned weapon schema. Validation preserves it by exact installed-source comparison and validates the remaining schema view; output retains the field. There are no new weapon tags. The native `physical` tag does not add railgun/missile research eligibility, but native unit-level/research interactions with planetary damage still need measurement.

Runtime tests must cover explicit attack, stop, neutral/friendly targets, diplomacy and ownership changing mid-order, native colony defeat/recolonization, native shieldless behavior, and facing/range at each muzzle. Keep the anti-ship30second torpedo lifetime untouched. Merely displaying a torpedo does not prove that destroying an object cancels planetary damage.

## Faction access and research: exact reuse paths

`expanse18_mcrn.player`, `expanse18_unn.player`, `expanse18_opa.player` are real definitions, all currently cloned from the TEC shared baseline. Keep one shared generator for Combined Fleet Sandbox; apply explicit faction access tables only in asymmetric output. A `race` label is insufficient.

Relevant native fields already present in the wrappers:

| Route | Concrete fields / required audit |
|---|---|
| Factory access | `buildable_units`, `faction_buildable_units`; factories admit `unit_factory.build_kinds`, so player access and unit `build.prerequisites` both matter |
| Research | `research.research_subjects`, `research.faction_research_subjects`; preserve common domain tier costs and research prerequisites |
| Colony opening | `trader_colony_frigate` remains available; `starting_free_unit_build_kinds=['capital_ship']` remains intact |
| Launch acquisition | Scirocco/Raptor/Pella/Donnager launch ability -> actual create-unit/operator and cost path; removing a factory list entry does not disable launch |
| Automatic escorts | `trade.trade_ship_escorts` currently creates Morrigan and Tachi as `special_operation_unit_kind='trade_escort'` |
| Garrisons | `garrison.units.random_units`, build kinds and `special_operation_unit_kind='garrison'`; currently includes global Cobalt replacement Morrigan |
| Initial units | `.start_mode`, scenario templates and `starting_units_in_formations`, not the deprecated player starting-unit field |
| Other rewards | Native research windfalls such as `trader_find_npc_explore` and NPC reward definitions |
| Items / hero caps | `ship_components`, per-hull `item_builds`, item required tags/prerequisites, `unit_limits.global` hero/titan tags |

Do not assume a captured ship makes its model's research available. Research checks are against the owning player's eligible tree; manufacturing origin and research owner are distinct. Native build unlocks are expressed by unit `build.prerequisites=[['node_id']]` and the corresponding node appearing in that owner's tree. This is sufficient for Black-Budget Procurement and a unique, paid Pella access path; neither needs a new capture system. Pella's existing per-player cap remains1. Existing Raptor is a repeatable fast capital without railguns: allocate to MCRN and preserve an explicitly disclosed fast counter in every other roster.

UNN/OPA early roles cannot be filled merely by deleting all native entries: `trader_light_frigate` is the globally replaced Morrigan. Keep disclosed shared native escort/colony/robotics placeholders, or author a proper owner-specific refit. Do not leave a faction waiting for random salvage or unique hero access before it can colonize or repair.

The13 themed nodes from `tools/update15_research.py` are already implemented under native IDs. Preserve those IDs, prices, tiers, existing prerequisites and +5% values as the common foundation. Do not recreate them under a second name. Faction specialties require separate node definitions (or deliberate owner-specific listing) because changing one globally shared definition changes its effect for every owner who has that node.

Verified small research/module building blocks:

- Native unlock subject: `trader_unlock_robotics_cruiser.research_subject` demonstrates domain/tier/field/coord/cost/prerequisites. Amun/Pella currently have no build prerequisite: adding one must not accidentally appear in the wrong owner tree.
- Existing Scirocco Marine Assault Doctrine already changes disruption duration12→13seconds via research-dependent action values, not capture chance. Reuse this for MMC certification rather than double-applying a second duration bonus unknowingly.
- Existing trade/extraction/development effect types and graph structure are in `update15_research.py` and its affected-definition audit. Global `unit_factory_modifiers` are not a local developed-shipyard condition.
- Native local production: `trader_starbase_factory_support_on_factories.buff` and `trader_carrier_capital_ship_mass_production_on_factories.buff` use `unit_factory_modifiers`, fixed-one stacking, all-player stacking ownership and death with parent. Their native provider/target filters are the right local template. +10%RATE means time scalar1/1.10−1, not−10%time; +20%RATE means1/1.20−1.
- Stage3-dependent station readiness/defense unlocks and Stage4 salvage specialization remain absent from purchaseable Stage2 nodes until the target mechanic exists. No placeholder promise unlock.

## Stage 3 prepared work and necessary rebase

`tools/update18_tycho.py` is a disabled laboratory, not a finished candidate. It contains a native placeholder starbase,16PDC+4torpedo mounts,3normal slots and Industrial Drydock. The drydock modifies **only this station's own factory**, with `mobile_unit_factory_enabled` and build-time scalar1/1.15−1. It is not an aura improving neighboring shipyards.

Do **not** integrate that generator unchanged: it reads0.17, writes invalid zero-percent `shield_burst_restore`, uses old40DPS station PDCs, leaves only one implemented module, and carries old shared-faction integration assumptions. Rebase from latest frozen candidate, omit disabled burst objects, preserve native source references, and bind OPA-only access in asymmetric output. Its75000hull/20000armor design is a prior station proposal, not an instruction to give a Foehammer battery that endurance.

A one-gun battery can use the installed orbital defense `build`/military-slot framework and unchanged private copy of the final Donnager railgun, plus two modest PDC mounts. Existing `player.unit_limits.planet` and unique unit tags are the native local-cap mechanism. A new battery tag should get local limit2 while remaining outside old `superweapon`/`starbase` limit research. Queued builds, captures, cancellation and aliases remain runtime tests; do not claim a static limit array proves these cases. Main or the orbital worker owns this implementation.

## Stage 4–5 gates: concrete rather than speculative

| Capability | Existing evidence | Current gate / minimum next proof |
|---|---|---|
| Native ordinary salvage | Existing Artemis and Le Guin native derelict paths; native `capture_points_total`, `destroy_on_capture`, collection range/duration | Preserve current behavior. This does not prove exclusive timed claims or custom sample rewards |
| Minor contacts | `tools/update18_operations.py` emits4schema-valid native item/reward fragments; Jiskun material/vision rewards, Pranast service pattern | Integrate finite costs/cooldowns and neutral contact placement separately. Vision service is ordinary vision, not cloak detection |
| All-player notices | Installed `pirate_incursion.lua` calls `context.show_notification(NOTIFY_PIRATE_INCURSION_STARTED,{})` and location/target-player variants | Arbitrary operation text including actual actor+well and enemy-without-vision delivery has not been proven. Existing action `add_notification` schema accepts only planet_conversion_started/colonized; custom guessed enum is invalid |
| Operation state | `event_metadata.lua` documents context.instance/shared, current_tick, on_start/update/complete/cancel, tracked unit death, owner/unit/well queries | Native engine binding, save/reload restoration, exclusive claim, paid commitment callback and dedup must be proven. Lua syntax checking is not engine API validation |
| Finite study and lab loss | Documented `simulation:give_research(player,subject)` and real unit existence/owner checks | No verified atomic paid ability/item commitment -> unique saved lab operation -> unlock route. Cosmetic180s buff beside an unrelated unstoppable research queue is rejected |
| Distinct exotic | `tools/update18_composite_probe.py` creates separate exotic and one-receipt/one-debit fragments. `exotic.uniforms.type_datas` and exotic costs accept names, native insufficient_custom_exotics_a/b/c sounds exist | Registry/UI sixth-slot behavior, receive1/display/save/spend1/reject0 and multiplayer serialization are NOT RUN. Do not replace an existing exotic or invent client-side balances |
| Manufacturing | `player.buildable_exotics` has factory time/price/prerequisite entries; native exotic factory research modifiers exist | Actual study knowledge gate and operational-lab restriction are not yet bound. Do not make first lab cost the resource it must produce |
| Adaptive plating | Native item capacity/restore-rate/delay modifiers exist; unit_mutation shield permissions are documented | Persistent expanse11_no_shields disables absorption/restoration/regeneration. Need conditional item lifecycle removing/reapplying guard, swap/refill prevention, capture/save semantics; no verified enabling mutation overrides disabling permission. Do not remove guard globally |

Existing detailed gate records: `audit/update18-operations/capability-report.json`, `audit/update18-composite/capability-and-interruption-audit.json`, `audit/update18-composite/resource-probe.json`. They are prior capability records, not runtime passes. The old composite audit's suggestion to retain a zero-percent burst object is obsolete and contradicted by the0.19 loader fix; always omit the optional disabled object.

A small explicitly experimental operation/resource smoke package can be authored separately with only the verified native paths. It must not claim that unseen enemies receive arbitrary actor/well notices or that lab loss cancels a paid unlock until those assertions are observed. Later gates do not block delivering Stage2 colony/bombardment or Stage3 ordinary orbital structures.

## Evidence

`audit/foundations20/fragment-validation.json`:10definition schema checks (one unchanged installed extension),6real siege launch frames, source hashes. `current-colony-bombardment-inventory.json`: frozen0.19 capability inventory. Generated files stay in `build/foundations20-fragments` and require the documented main-thread merges. No gameplay, save/reload, AI or multiplayer result is claimed.
