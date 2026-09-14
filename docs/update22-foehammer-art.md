# Foehammer orbital battery: compiled art handoff

This completes the earlier editable art prototype's **offline compilation**, not its gameplay integration or in-game acceptance test.

## Files

- Game-only assets: `build/update22-foehammer/game/` (18 regular files; 4 meshes plus accepted donor material/DDS dependencies).
- Rig and hashes: `audit/update22-foehammer/integration-spec.json`.
- Preview of actual packaged mesh/DDS files: `audit/update22-foehammer/compiled-game-preview.png`.
- Compiler source: `assets/derived/update22-foehammer/expanse22_foehammer_support.gltf` and `.bin`.
- Build recipe: `tools/update22_foehammer_compile.py`.
- Preview recipe: `tools/update22_foehammer_preview.py`.

Use the normal `ship` shader for the base mesh and all child mesh aliases. The base alias is `expanse22_foehammer_support`. Gun aliases are `expanse22_foehammer_rail`, `expanse22_foehammer_pdc_base`, and `expanse22_foehammer_pdc_barrel`. These private filenames retain exact accepted 0.19 donor mesh bytes; their material references are included. Existing names are not modified.

The contract defines one `gimbal` rail at `child.expanse22_foehammer_rail_0` and two `biaxial` PDC rigs at `child.expanse22_foehammer_pdc_0`/`_1`. Original PDC barrel offsets and muzzle offsets are retained. All coordinates use the established game frame: +Y up, +Z fore. New support UVs use separate projections for each face orientation, avoiding vertical texture stretching and out-of-range compiler warnings.

## Checks actually passed

- Official SDK MeshBuilder emitted both JSON and binary support outputs with triangle-facing data.
- All six named meshpoints match authored position and rotation values.
- Support has 168 triangles and zero opposed winding faces after official regeneration.
- Tangent correction changes only the binary tangent fields, preserving every other byte including the opaque compiler trailer.
- Rail (8,519 triangles), PDC base (138) and PDC barrel (539) are byte-identical to accepted 0.19 game meshes. Total assembled triangle count is 10,041.
- Material/DDS references exist and are included. Original source-game and output SHA-256 maps are recorded.
- Standalone rendering of actual packaged mesh and DDS files was inspected.

The existing build-only Wine prefix was used in place; it was not copied, and none of its drive links enters the game output. The sandbox initially prevented Wine's local IPC socket; the authorized local SDK compile succeeded with the execution override. The game was neither launched nor installed.

## Gameplay integration remains separate

The reference Foehammer weapon is included in the JSON contract for comparison, including 5,000 damage, 30-second interval, 1.5-second acquisition and **zero pitch speed**. Its original ±2-degree yaw / zero-pitch mount limits are recorded as the conservative default. If a larger structure-specific azimuth arc is chosen, make that a deliberate gameplay decision and test it; the art handoff does not silently improve gun tracking.

For PDCs the static outboard mounting planes are beyond the support's X extrema, and the proposed pitch range is -85 to 0 degrees with the inherited outward-up convention. This gives the support a physical mounting location, but it is not a substitute for testing actual native aiming and firing behavior.

Still untested: stationary high/low coverage, native aiming at different directions, effects/muzzle appearance in game, destruction, structure build/limit/infrastructure rules, save/reload and multiplayer. No unit, weapon, research, build menu or shared manifest was edited by this art task.
