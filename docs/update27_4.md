# 0.27.4 Hephaestus Repair

Standalone cumulative repair over **regular 0.27.3**. Enable this package alone. This release contains no custom menu scene: 0.27.3 Menu Battle failed the user's startup test and is not recommended. Frozen predecessors remain unchanged for diagnosis/rollback.

Changes from confirmed log faults:

- Hephaestus: replace invalid `capital_supercapital_heavy` with native `heavy` AI target classification. The former is a weapon target-group style name, not a valid ship target type. Both repair and menu logs rejected it during loading. No weapon damage, tracking, movement, hull or price changes.
- Three engineering stations and the PDC picket: disable the inherited selected-planet control flag. The engine permits it only on carriers, factories, exotic factories and trade ports. The structures remain individually selectable with their existing equipment/abilities.
- Donnager: remove the unused rebel-titan alternative from its construction prerequisite. Its MCRN owners retain their existing loyalist-titan unlock, costs and tier. All six supported player definitions now resolve every prerequisite of every buildable ship and structure.
- Murphy: remove the printed aft stub and replace it with the existing textured Tachi Epstein bell/throat, attached by a closed connector. The donor contributes 1,200+ triangles; source UVs and materials are retained. Existing weapon/exhaust hardpoints, collision bounds, UNN hull texture, stats and audio are preserved. No PDC or rail model was replaced.

Offline checks pass: native AI target types, selected-planet control eligibility, all owned procurement references, 65 action-source level tables, 48 biaxial turret pairs and eight rail gimbals, pinned schemas/references, exact combat/audio preservation, Murphy's official SDK compilation/winding/attachment checks, and ZIP integrity. The aft preview verifies the assembled compiled drive; it is not an in-game rendering test.

**Not established:** crash-free loading, Hephaestus spawning/combat, Pella spawning, save/reload or multiplayer. The Pella `no gui_definition` and following blank-source resource error remain unresolved. Its skin GUI and named dependencies exist, and its unit definition is unchanged from 0.26. The available log does not prove whether this is an independent defect or follows failed definition initialization. Do not interpret offline checks as a runtime pass.

Test this repair in a fresh session. Check loading before using Skip All. Test Hephaestus as MCRN and Pella as OPA through their normal production paths, then repeat debug spawning separately; that will distinguish faction/production context from model loading. Stop and retain the log if an assertion recurs. The menu variant also logged an unknown Donnager rebel-titan prerequisite before any fleet-spawn completion message; Hephaestus is a shared suspect, not a proven sole cause.

No installation, enabled-mod change, game launch, save modification or publication performed. Model polish beyond Murphy's requested drive correction remains deferred.
