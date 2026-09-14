# Behemoth logistics-titan fragment

`tools/update24_behemoth_gameplay.py` exports
`changes(base, art_contract) -> edits, localization, origins, report`.
All 15 authored definitions/brushes are new. The default baseline is frozen0.22.
No shared unit, weapon, research, player or capture definition is edited.

The prototype is **an OPA logistics titan**, with the ordinary `titan` build kind,
target type and generic titan tag. It therefore uses the native shared titan
cap; do not add a separate per-Behemoth allowance. Main integration must add OPA
build access and the unique tag, and restore the priced native rebel titan
unlock chain or replace that prerequisite with comparable OPA research. The
fragment never grants a free ship or free research.

All numbers below are deliberate mod balance choices, not lore specifications:

| Property | Prototype |
|---|---:|
| Level1 hull / armor | 12,000 / 1,500 |
| Level1 armor strength / durability | 55 / 350 |
| Level10 hull / armor | 18,480 / 2,175 |
| Normal speed / turn speed | 250 / 4 |
| Acceleration time | 20seconds |
| Supply | 500 |
| Credits / metal / crystal | 11,000 / 3,000 / 2,200 |
| Construction | 360seconds |
| Exotic prices | Native Donnager titan baseline, unchanged |
| Equipment capacity | Native eight titan slots |
| PDCs | Eight at85 baseDPS each; Earth tracking and6000range |
| Railguns / bombardment | None |

The ten native experience levels retain antimatter progression but no weapon
damage or cooldown leveling bonuses. Every level stays shieldless and below
Donnager hull, armor, strength and durability. A huge civilian exterior is not
equivalent to a purpose-built warship's armor. Limited arcs and low agility
preserve flanking and concentrated-fire counters.

The missile magazine is an exact private copy of Europa's existing UNN-profile
magazine and action values: **eight torpedoes, two per10seconds,120-second reload
after the last pair;750 base damage,2125speed and30-second fuel**. Existing missile
research remains applicable. The original projectile entity and all previous
magazines are unchanged. Two measured forward positions replace Europa's port
positions. These are cosmetic tube fixtures, with no interception claims.

**Hospital Engineering Teams** repairs one other owned ship within6000 for
40hull/second over20seconds: **800 maximum** on any hull size,100antimatter and a
60-second cooldown. Autocast defaults on at20% missing hull; manual casts still
require a damaged eligible target. It uses the existing Scirocco repair buff,
so the shared pending-buff reservation prevents stacking with Scirocco or Fleet
Train. Active native repair and station repair reservations also block the
initial cast. No armor or shields are restored.

For20seconds after dispatch, **Hospital Grid Priority** cuts Behemoth speed25%
and increases normal PDC cooldown25%. This is a small power-allocation tradeoff,
not weapon shutdown. Scripted missile-magazine schedules are unaffected and
the tooltip says so. Target ownership changes cancel the shared repair buff.
Dispatched teams may finish after the provider dies or leaves; this is a finite
800-hull effect, not an aura falsely described as provider-bound.

A native **mobile ship-component shop** uses the existing Fabricator/retrofit
service field without discounts, free equipment or global resource bonuses.
Its proximity and allied-access behavior is native and needs in-game checking;
the targeted healing itself explicitly allows only owned ships. No factory,
free squadron, second capture system, orbital weapon or mapwide action exists.

The skin uses the actual compiled Behemoth art and eight-nozzle blue plumes.
Eighteen rendered PNG resources and six brush definitions provide actual-model
portraits at standard DPI sizes. Generic Europa's Bane dialogue is reused, with
no Donnager-name or railgun lines.

Observed offline passes: all15 closed schema checks (only copied corruption
data is an accepted source extension), skin/weapon/material/effect references,
three ability action graphs, typed ADS values/filters/modifiers, shared repair
identity, exact85DPS×8, unchanged missile ADS, native titan slots/classification,
and all weapon meshpoints. The private validation view links frozen baseline
files and only writes its own local overlay; it is not a distributable package.

**Not run:** engine load/menus, live titan cap,2km navigation/collision, PDC
aiming, repairs/ownership/caster death, save/reload, mobile refit scope, multiplayer
and performance. Main owns final access merges, registries and packaging.
