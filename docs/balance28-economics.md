# Stage A: acquisition and hierarchy

Pure recipe: `tools/balance28_economics.py`, `changes(base) -> (edits, origins, report)`.
Baseline: frozen `expanse_update27_5_menu`, not a previous experimental balance output.
This worker does not install, enable, package, launch, publish or push anything.

## Mechanical changes

| Hull | Before | Stage A |
|---|---|---|
| Truman | Ordinary capital; 185 supply; 4000 credits / 1000 metal / 700 crystal; 100 seconds | Native command class; 400 supply; 7680 / 3016 / 1520; 240 seconds |
| Raptor | Ordinary capital; 10 experience levels; four equipment slots | Cruiser; exact former level-one health and weapons; no experience/equipment slots |
| Hephaestus | Cruiser; 4000 hull / 2300 armor | Ordinary capital; unchanged level one; four equipment slots; +3% hull/armor per level, reaching 5080 / 2921 at level ten |
| Nathan Hale | Existing tier-two ordinary UNN battleship | Same acquisition, price and combat stats; disclosed expeditionary colonization and bounded engineering repair |

Truman retains its current offense-one/defense-two exotic price. Its complete health,
weapon, movement and experience tables are unchanged. Its existing four equipment
slots remain four; promotion does not grant native DLC command abilities or six slots.
Raptor folds the former level-zero 225 antimatter and 0.75 regeneration into its base
antimatter so removing experience does not disable the fixed-level reactor ability.
Its magazine, reactor, corvette launch, boarding and reactor-breach abilities survive.
Hephaestus uses the existing Nathan ordinary-capital experience/antimatter table,
which has no weapon modifiers. Its weapons and fixed-level magazine abilities remain
unchanged. Build price, supply, time, movement and first-level health are preserved.

Nathan uses a private copy of the native colony-frigate colonization ability, with
its existing compiled `weapon.torpedo.0` shuttle origin. It receives no capital colony
commerce/logistics bonuses. Its repair is the existing Scirocco engineering ability,
including the existing flat cap and nonstacking protections. This is an explicit
support-role adaptation of the existing hull, not another cheap Truman. The dangling
Truman-only colony-item AI recommendation is removed from Nathan. The ordinary
450-credit / 100-metal / 50-crystal colony frigate remains in the UNN roster.

## Native acquisition and cap evidence

The installed native command unit uses `super_capital_ship` for `build_kind`,
`build_group_id`, `target_filter_unit_type` and its unit tag; its AI attack class is
`supercapital`. The recipe changes all these actual fields, not only the display text.
The actual supply field is `build.supply_cost`; the check explicitly rejects an
accidental additional `supply` key.

The existing titan factory accepts `super_capital_ship` and `titan`. The ordinary
capital factory accepts `cruiser` and `capital_ship`. No factory fabrication is needed.
A private research definition copies the native command procurement pattern:
military tier three, experimental coordinate `[6,0]`, 360 seconds, 1700 credits /
300 metal / 500 crystal, prerequisite `trader_unlock_titan_factory`. That coordinate
is vacant in the affected baseline UNN research trees. The subject is registered on
the actual UNN player and its legacy mirror; the unit's construction prerequisite
requires the new unlock. All prior research subjects, research-domain data and
playable rosters remain unchanged.

The existing `super_capital_ship` global cap changes from one to two for these
Truman-building players. Truman is the only actual command-tagged unit available in
those rosters. No new tag consumes the already-full tag budget. Menu showcase
`expanse_menu27_*` clones are cosmetic, absent playable build rosters, and intentionally
excluded from gameplay edits and cap reasoning. Native command kind/tag excludes
ordinary-capital first-item eligibility; actual first-free billing still requires
an in-game check because its engine implementation is not exposed in these JSONs.

Existing OPA override codes allow command/titan captures. The recipe adds explicit
Truman-definition exclusions to both acquisition and delayed-resolution filters of
the two existing affected boarding data sources, preserving other capture targets.
It does not create a competing capture system or remove existing excess ships.

## Validation and limits

`python3 tools/check_balance28_economics.py` passes ten schema-covered definitions,
exact acquisition/value assertions, unchanged weapon/physics/movement/art checks,
first-level health preservation, retained cheap colony access, reference source paths,
and idempotent overlay reapplication. The localization file has no installed schema.
Draft-7 schema success alone is not proof of valid unknown fields; changed keys were
also matched to the concrete installed framework. The corrected supply invariant is
explicitly checked.

No runtime tests were performed. In-game acceptance remains required for concurrent
queues, cancellation, death releasing reservations, actual command billing, existing
and newly built ships, ability UI/autocast, save/reload and multiplayer. Native global
caps are not proven absolute ownership guards for diplomatic transfer or arbitrary
reward scripts. Boarding guards cover the mod's supported boarding acquisition and
resolution paths, not every possible external spawn mechanism. Existing saves with
extra Trumans or fitted Raptor equipment are retained and need migration testing.

Do not describe the static cap/graph checks as observed multiplayer or queue passes.
