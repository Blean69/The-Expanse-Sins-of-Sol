# 0.25.0 — New hulls candidate

This is the cumulative new-hull experiment over0.24, corrected0.23.2/0.22.1 and the separately delivered doctrine Stages1–3. It includes Murphy, Behemoth, Gathering Storm, UN One and a Truman local-bombardment visual. **It is not completion of Stage4/5.** Exclusive recovery/global announcements and interruptible ProtoTech/plating remain absent at documented capability gates. The confirmed three-hour playtest belongs only to0.19 Fleet Balance.

Use one variant in a fresh game. Asymmetric: MCRN manufactures Gathering Storm through rare late procurement, OPA builds Behemoth in its shared titan slot, UNN builds Murphy and UN One. Combined sandbox: every owner can access the full roster, with the same prices, ordinary supply and caps. Capturing a foreign unit does not unlock its production tree. All previous candidate ZIPs remain available; prefer corrected0.22.1/0.23.2 over their earlier menu-defective versions.

## UN One envoy

Unarmed UNN transport, one per player,25supply. Costs1200credits/200metal/150crystal,60seconds, native trade-port research prerequisite; ordinary frigate billing.800hull,150armor,100durability,900speed,100antimatter with1/second regeneration. It does not inherit Artemis's independent loot-collector role, trade behavior or any capital discount.

Civilian Relief Teams is manual: one owned damaged unarmed corvette/frigate/cruiser within2500,25antimatter,90second cooldown. Repairs10hull each second for15seconds, maximum150. Excludes self, armed/planet-bombing ships, capitals, titans, allies and enemies. The existing engineering-team buff prevents duplicate application and station-repair addition while active. Teams can finish their finite assignment after dispatch, with the inherited target-ownership cancellation rule. No income, standing modifier, global aura, boarding or invulnerability. This humanitarian function and phase travel are game adaptations, not claimed TV specifications.

The supplied parts retain their assembled coordinates:117822source faces plus4glow faces. Printing stand, stand interface and internal repeated pegs are excluded; visible connector covers remain. White/gray finish, blue tips, bronze details/windows, hull name and two measured nozzle origins.52m is an uncertain author-model estimate, not independently verified TV length. Existing civilian portrait and generic UNN acknowledgments remain temporary.

## IPBM visual

Truman's existing native local-bombing travel alias now uses the supplied UN IPBM model. No weapon, planetary damage, range, cooldown, filter, ordnance entity or ship magazine changes. It is a cosmetic native mesh-particle effect and **cannot be shot down as an actual unit**. No global launch, map destruction or strategic superweapon is included.

Source v2 has39960faces:1584zero-area and64numerical sliver faces removed, then bounded simplification to6000triangles with reported relative error0.0002272. It matches the accepted16.51game-unit torpedo length instead of using printing units. Gray/white UNN materials preserve ribs/nozzle. The native siege-frigate travel-effect structure differs only by the mesh reference and tail-origin alignment. Actual local flight/orientation still needs a game check.

## Earlier new hulls retained

- Murphy:95supply, four85-DPS Earth PDCs, modest fixed fore/aft750damage/30second rails, two light torpedoes per10seconds from an eight-round magazine. Exact original8302hull faces retained.
- Behemoth:500supply, shared titan cap,12000hull/1500armor, eight85-DPS PDCs, no rails, slow250speed, finite800-hull hospital cast with a temporary power tradeoff, native mobile refit service. Full24046source faces retained.
- Gathering Storm:300supply, one per player, expensive tier4 procurement,6000hull/3000armor,1400speed, six117.6-DPS PDCs, fixed5000damage/30second keel rail,18-round conventional magazine. Full source detail retained except five degenerate faces. Crystalline blue/pink finish; no Magnetar weapon, cloak or conventional shields.

Exact costs, prerequisites, scope and source citations are in `docs/update23.md`, `docs/update24.md`, `docs/update20-asset-intake.md` and the per-version audit records. These numerical values are mod balancing choices. The Urshanabi extraction remains broken debris requiring actual reconstruction; it is not presented as an intact playable flagship.

## Evidence and next test

Offline PASS: schemas with preserved installed extensions, explicit definition/weapon/effect references, acquisition lists and prerequisites, equipment ability graphs, tag/limit definitions, source/frame/winding/material checks, bounded sampled PDC arcs, exact magazine operation counts, source hashes and unchanged established audio/ordnance. These are not observed gameplay results.

Runtime NOT RUN: fresh load, new constructors and factories, research on existing/new ships, price charging/free-capital boundary, queued/captured limits, actual aim/torpedo origins, large Behemoth navigation, manual/autocast relief filters, shared repair/source-loss behavior, mobile refit, IPBM orientation, save/reload and multiplayer. Run a short identical-hash three-player session before another long FFA; record actual duration/errors/outcomes. Do not mix saves across candidate versions.

No installation, enabling, launch, remote push or publication was performed. Original models and frozen baselines remain intact. Working PDC audio is unchanged.
