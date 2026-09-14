# Stage 2 owner-scoped access and research audit

This report distinguishes recommendations from the authored research overlay. Runtime opening, menus, research propagation, capture, save/reload and multiplayer are **NOT RUN**. `implementation.json` records the exact authored research mapping, inherited template costs/tier/time and offline checks.

## Integrator API

`tools/update21_research.py: changes(base)` returns `(edits, strings, patches, report)`.

- **Pass the integrated Stage 1 package**, not 0.19: the private boarding/repair ADS must inherit the new guards/autocast.
- `edits`: 34 NEW definitions; no shared units or players are rewritten.
- `patches.research`, `.items`, `.planet_items`: maps keyed `mcrn`, `unn`, `opa`. Add them to the corresponding owner's research/ship-component/planet-component lists. Combined sandbox may add all lists; coordinates occupy distinct extra rows.
- Apply each `report.shared_definition_merges` entry by loading the existing file and updating only `set_fields`. These preserve normal boarding costs/chances and existing Scirocco disruption levels while adding owner-research levels. Item counterpart exclusions are symmetric merges.
- `origins` is empty intentionally: all authored definitions pass the pinned closed schemas without installed-extension exemptions. Templates are recorded in the mapping.
- Register new ability/ADS/buff/item/research IDs in their normal manifests. No new unit tags/resources are required.

## Authored specialties

| Owner | Research | Actual implementation |
|---|---|---|
| MCRN civilian | Terraforming Directorate Bonds | Unlocks paid level-5 planet component; +10% local commerce income only while fitted; native Commercial District cost/slot framework. |
| MCRN civilian | Closed-Loop Habitat Engineering | `any_development_track_build_time`, scalar -0.10. Civilian colony development only. |
| MCRN civilian | Precision Manufacturing | Two private equipment contracts: Combat Repair System and Antimatter Engine ordinary prices ×0.90; native effects, exotic costs and native prerequisite retained. Mutually exclusive with standard counterpart. |
| MCRN military | MMC Assault Certification | Existing Scirocco disruption duration [12,13] becomes [12,13,14], with the new trained level after existing Marine Assault Doctrine. No capture probability change. |
| MCRN military | Redundant Command Systems | Paid capital/command slot component; `max_antimatter` scalar +0.15; no native engine active ability copied. |
| UNN civilian | Lunar Procurement Offices | Paid developed-colony component; `factory_unit_build_time` scalar -1/11 = +10% nominal local production rate. |
| UNN civilian | Emergency Appropriations | Paid alternative office; manual activation costs 300 credits/100 metal/50 crystal, 30 seconds, 180-second cooldown; local `factory_unit_build_time` -1/6 = +20% nominal production rate. No autocast; mutually exclusive with passive Lunar office. |
| UNN civilian | Civilian Shipping Requisition | `trade_credits_income_rate`, `trade_metal_income_rate`, `trade_crystal_income_rate`, each scalar +0.05. No free ships. |
| UNN military | Black-Budget Procurement | Exact gate **expanse21_unn_black_budget**; main adds Amun build prerequisite. Existing 70 supply, six-unit cap, 4,000/750/500 price and 90-second build preserved. |
| UNN military | Fleet Train Organization | Paid capital/command targeted repair component. 10 hull/second ×20 =200 cap, range2,000, 50 antimatter/60-second cooldown. Reuses Scirocco's exact non-stacking buff ID; its owning ADS supplies the smaller repair amount. No magazine reset. |
| OPA civilian | Volatile Recovery Cooperatives | Orbital extractor metal/crystal income scalar +0.15; no mining-track or reward multipliers. |
| OPA civilian | Spin-Habitat Construction | Asteroid/ice-asteroid `logistics_track_build_time` scalar -0.10; does not discount rail batteries/ships/fortresses. |
| OPA military | Override-Code Libraries | Existing Amun/Europa guarded boarding range [6000,6300] under owner research; all other ADS values duplicated unchanged. Capturing a compatible hull can use the owner's research without unlocking manufacturing. |
| OPA military | Diverted Martian Surplus | Exact gate **expanse21_opa_surplus**; main gates paid Pella acquisition, preserving one-per-player cap, 200 supply, 6,000/2,210/1,200 plus1 offense/2 defense,150seconds. |

This delivers14 implemented nodes. The remaining four named specialties are explicitly **absent**, not purchasable placeholders: MCRN Naval Readiness and UNN Orbital Defense Command require Stage3 structures; OPA Dockworker Damage Control requires local engineering support; OPA Salvage Arbitration requires Stage4 reward-specific handling. No bonus is claimed from a deferred node.

Research costs, tier, research time and icons are copied from appropriate native templates, with identifiers recorded in JSON. New prerequisites preserve essential native chains. New rows use the existing Civilian/Military fields. UI scroll/placement requires runtime inspection.

Native scalar modifiers combine with other native bonuses. The +10%/+20% production-rate equivalents describe each modifier against unmodified time, not a guarantee of multiplicative stacking with every existing economy upgrade.

## Essential shared opening

Keep these exact working definitions available to every faction until art/refits genuinely replace their function:

- `trader_scout_corvette`: current Sunflare exterior, 200 credits,12seconds,5supply; scout ability unchanged. Harmful burn autocast remains untouched.
- `trader_colony_frigate`: no research gate;450credits/100metal/50crystal,30seconds,5supply; native colony initialization and type prerequisites.
- `trader_constructor_ship` through `player.structure_builder`, not ordinary combat menus. Retain `trader_frigate_factory_structure`, `trader_capital_ship_factory_structure`, both research labs, retrofit bay and native extraction/trade structures.
- Repair progression: `trader_unlock_retrofit_bay_repair_ability` (military tier1,700/100/125,120seconds) -> `trader_unlock_robotics_cruiser` (tier1,750/125/150,150seconds). Robotics costs500/95/45,25seconds,6supply. Keep both nodes; removing the first breaks the second. Scirocco support does not replace every faction's ordinary repair access.
- Keep native colony-type, trade, extraction, structure, equipment and exotic prerequisites; the new specialty nodes are optional branches.

A disclosed contractor escort/refit is better than an Earth/OPA opening with no affordable combat unit. Current Europa costs1,500/350/200 and95supply, so it should not be their only repeatable early combat choice. The parent's private contractor patrol approach avoids naming a shared Martian hull an Earth design. Raptor remains a useful MCRN150-supply fast capital; Pella is its scarce OPA derivative, not repeatable basic expansion.

## Acquisition and inherited leakage checks

The 0.19 player wrappers contain more than `buildable_units`:

- `faction_buildable_units` includes native Titan/supercapital entries.
- Garrison random roster includes Morrigan and several native TEC combat hulls.
- Trade escort research grants Morrigan and Tachi outside the ordinary ship menu.
- Normal starts supply both shipyards, retrofit bay and two scouts. Quick starts grant ten Morrigans; every start-mode clone must use the intended faction starter or be explicitly labeled combined/stress.
- Capital launch abilities can continue deploying Tachis even without their factory entry. Keep full Stage1 supply/cost accounting; OPA Pella's inherited launch is a deliberately procured foreign capability, not a production-tree unlock.
- Hero caps are existing per-player tag limits, not global shared caps.

**Pella first-free-capital trap:** players inherit `starting_free_unit_build_kinds=['capital_ship']`. Merely adding research before ordinary capital construction does not guarantee full price if the entitlement is saved. Main's proposed paid acquisition adapter uses `build_kind='cruiser'` while retaining capital combat classification/progression and UI group. Native **capital ship factories**, not frigate factories, support cruiser builds. Frigate factories support only corvette/frigate. This adapter needs menu and full-price runtime verification; do not say it is a frigate-yard purchase.

## Conservative research pruning

An exact isolated chain exists:

`dlc2_trader_unlock_loyalist_super_capital_ship` -> `dlc2_trader_upgrade_loyalist_super_limit_0` -> `dlc2_trader_upgrade_loyalist_super_limit_1`.

No other listed research node depends on these three. They can be removed as a set from asymmetric players if no supercapital production exists; retain in combined sandbox as appropriate. Prune corresponding supercapital-only shop entries separately if they have no eligible hull.

Do **not** blindly remove `trader_unlock_titan_factory` or `trader_unlock_loyalist_titan` from MCRN/combined: current Donnager requires loyalist OR rebel Titan unlock. Also do not call native Titan equipment unlocks dead merely because Ankylon is absent: their required tag is the generic `titan`, and Donnager has that tag. Six Titan component research leaves depend on the Titan unlock; actual item fit/visual compatibility requires a separate check before removal.

Do not remove native repair, antimatter or component branches simply because visible native combat hulls have been hidden. They continue supporting the Expanse capitals and these new equipment contracts.

## Reference basis and tests

Installed templates include `trader_commercial_district.unit_item`, `trader_industrial_complex.unit_item`, native planet component passive buffs, `trader_counter_deployment` build-time modifiers, `trader_antimatter_engine.unit_item`, existing Scirocco support ADS and ordinary item build prerequisites. All implementation keys are pinned-schema supported. No Windows/Linux-specific scripts or external runtime state are introduced.

Offline:34 closed definition-schema passes; existing Amun, Europa and Scirocco action/value references resolve after merge; all new component ability ADS references resolve. Full packaging must also verify brush/localization manifests and complete owner research graphs.

Runtime: each faction must build scout, contractor escort, cheap colony ship, lab and support route; buy its designated colony capital; research a specialty with an existing and newly built target; ensure enemy/allied owners gain no effect; fit/unfit/capture modules; test local income/rate while module is present/absent, exactly one mobilization payment, cooldown and save/reload; buy full-price Pella after intentionally retaining first-free-capital entitlement. All remain NOT RUN.
