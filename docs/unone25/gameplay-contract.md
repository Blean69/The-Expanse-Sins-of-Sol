# UN One envoy prototype

The unarmed transport receives one small humanitarian support function using the already integrated native engineering-team pattern. This is a mod role, not a claim that UN One had a canonical repair beam, phase drive or faction-standing power.

`tools/update25_unone_gameplay.py:changes(base)` returns `(edits, localization, origins, art, report)` against frozen0.23.1. Four new definitions: unit, skin, ability, action data source. No shared definition changes. Main must register the private tag `expanse25_un_one`, add the unit to UNN/wrapper access, and apply the one-per-player global limit in the report. Build prerequisite `trader_unlock_trade_port` already exists in UNN research. No additional research node is necessary.

UN One uses ordinary frigate billing:25 supply,1,200 credits,200 metal,150 crystal,60-second build;800 hull/150 armor,100 durability,900 speed. It has no weapon, factory, carrier, capture, capital progression, item slots or passive economic benefit. It has100 antimatter and regenerates1 per second. This resource is the game's existing action resource; no new currency is invented.

**Civilian Relief Teams** is manual,25 antimatter,90-second cooldown,2,500 initial range. It repairs10 hull per second for15 ticks: at most150 hull. Only the owner's damaged, fully built, unarmed corvette/frigate/cruiser is eligible, excluding the envoy itself. Normal weapons and bombardment weapons both disqualify a target. Capitals, titans, structures, planets, enemies and other players' allied ships are excluded.

It applies the existing `expanse15_scirocco_engineering_teams` buff with source-specific action values. The shared fixed-one effect and pending-buff exclusion prevent duplicate relief/engineering applications. Existing station repair already excludes this exact shared buff. Target ownership change terminates the effect. The dispatched team completes its bounded15-second assignment even if its transport departs; this is not a permanent local aura, an interceptable pod or a capture attempt. The existing generic engineering status label remains on the target.

Skin uses the reviewed two-nozzle UN One art contract and private idle plume from `audit/update25-unone/integration-spec.json`, ordinary native hyperspace effects, and existing generic UNN acknowledgments. Civilian donor GUI art is temporary; main can produce a UN One portrait. Phase travel is explicitly a Sins navigation abstraction. Art hashes are verified before returning dependencies; no original mesh or frozen package is changed.

`tools/update25_unone_check.py`: four pinned schemas and bounded-function contracts pass offline. Game ability availability on this unarmed frigate, filtering, repair timing, source/target ownership changes, save/reload, queue/capture limits, rendering and multiplayer remain untested. No native diplomacy or standing modification is promised.
