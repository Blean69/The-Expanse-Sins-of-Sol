# 0.27.1 Runtime Repair

Cumulative repair candidate over preserved 0.27 Fleet Expansion. Use the regular package for faction play; Sandbox deliberately grants the combined roster. Enable only one variant and begin a fresh game. Saves created after 0.27's registry failed to load are not validated migration inputs.

## Confirmed faults and changes

The latest log, `sins2_log_544.txt`, identifies the active regular 0.27 package. All 2,248 installed files exactly match the frozen candidate, so this was not an installation mismatch.

- **Unit-tag overflow:** the engine reports `expected_size=30 actual_size=35`, then cannot resolve native `starbase` and `corvette` tags. Five new ship identity tags had no mechanical consumers. Those five are removed from the registry and their hulls; the native class tags, item restrictions, research and unique ship limits remain intact. The registry is back to 30. This directly repairs the failed loading of the tag system used by starbase-only item restrictions. A new equipment matrix checks mobile hull rejection and positive station/capital controls for all six faction/player definitions.
- **Missing turret sockets:** Morrigan's base and barrel lack the child/muzzle mesh points required by the renderer. Reused custom PDC meshes share the omission. Required socket metadata is added at the existing weapon-defined pivot/muzzle positions across affected custom meshes. Official SDK A/B compilation verifies the binary socket layout. Hull geometry, gun shape, normals, materials, acceleration data and weapon statistics remain unchanged.
- **Missing experience effects:** OPA command and Dark Star have experience progression but lack mandatory level-up effect/sound fields. They now use the existing Truman/native effect pair. Experience thresholds and bonuses remain unchanged.

No hull health, price, fleet supply, movement, firing arc, weapon damage/cadence, torpedo program, civilian research or audio changes are included. Station abilities remain available on their intended hosts. No extra ship equipment is granted.

## Evidence and remaining uncertainty

Offline acceptance covers the engine's measured tag limit, all native tags, equipment eligibility, required turret socket types, experience effects, schemas/references, unchanged gameplay/audio, ZIP contents and rollback hashes. These checks are stronger than the 0.27 gate, which missed the unit-tag capacity and mandatory rendering sockets. The prior offline PASS did not establish that the game would load correctly.

The log also ends with formation/order and generic `inplace_vector` assertions, followed by a render/error-dialog timeout. These may be downstream of the failed tag/mesh loads; there is no post-fix runtime trace proving that attribution or that every crash is resolved. A constructor GUI warning occurred in the same failed session; its definition already has a valid GUI and is not changed speculatively. Older disabled prototype metadata and optional scenario ZIP-member messages are separate from the new repairs.

**Post-repair game load, item menus, live PDC tracking, save/reload and multiplayer: NOT RUN.** For the next test: load a fresh regular game, inspect Dark Star's item list, confirm station equipment still works on a station, build Morrigan and the new hulls, then save/reload. If any error remains, retain the new log and note the selected ship/action.

The original 0.27 normal/Sandbox and 0.26 rollback/probe ZIPs remain unchanged. No installed files or saves were altered, and no game launch or publication was performed.
