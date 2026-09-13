# Scirocco visual revision 13

Worker ownership: tools/update13_scirocco*.py, audit/update13-a, assets/derived/update13-a, assets/source/update13-a, build/update13-a in the isolated visual13-scirocco worktree. Shared definitions and package integration belong to the main integrator.

## What changed

The twelve existing PDC rigs were already biaxial and shared the same source hardware family as Pella. Their 3.79-unit barrel offset on a 456.52-unit capital made them visually tiny. All twelve base/barrel meshes now use 2.2×visual scale, preserving their counts and existing independent weapon IDs. Matching pitch pivots, muzzle offsets, hull origins and supported pedestals are included in the full integration contract. Each wider 6.6-unit-radius socket was measured at eight footprint points. The old narrow sockets remain enclosed inside the wider footings; no static guns were duplicated. One ventral installation had surrounding belly machinery that necessitated a taller support.

The retained hull has newly authored planar UVs, a generated charcoal armor panel albedo and broad orange-red bands. Paint edges geometrically split existing triangles so stripes do not follow arbitrary triangle boundaries. The exact prior rail mesh, launch ports, exhausts, boarding origin, hull scale and gameplay remain unchanged. The model has 98,455 assembled triangles; no reimport or optimization pass occurred. Additional triangles are paint-boundary subdivisions and socket geometry.

The supplied Paul Kiesling images informed color/material direction. They are compressed presentation sheets rather than the STL's missing original texture coordinates. This derivative does not claim to graft the original atlas, does not embed their pixels and does not invent their license. See asset-sources.json for source hashes and the generated material record.

## Integration

Use integration-spec.json after its final PASS status, overlay its game_directory resources and ui_directory resources into the new combined package. Preserve existing IDs. Patch only Scirocco unit mount positions and its PDC weapon turret offsets from rigs; do not change firing budgets. Apply skin aliases/UI fields and ship_spatial from the contract. No unit, weapon, skin or manifest files are emitted by this worker.

The original rail binary is required to remain byte-identical to update 12. Its original bounded traverse and support arrangement are unchanged. PDC count remains 12. Original mount arcs remain yaw ±180°, pitch −85° to 5°.

## Reproduction

Required read-only dependencies: tachi-one-pdc/assets/derived/update12-b and audit/update12-b; its build/update12-b/game and build/polish-b/proton-prefix; main expanse-mod/.tools/texconv.exe; pinned installed SDK MeshBuilder; Proton 10 wine64; installed Sins2 UI texture sizes; editable generated assets/source/update13-a/charcoal-panel-tile.png. Missing ignored dependencies fail rather than passing a skipped check.

Run python3 tools/update13_scirocco_build.py, then update13_scirocco_compile.py. The compiler needs Wine local socket access. Render with update13_scirocco_ui.py using the new editable glTF, expected triangle count 98455, installed --game/--sdk, and a fresh --output build/update13-a/ui-<revision>. Then run update13_scirocco_validate.py. The UI renderer refuses an existing output directory. Source/generated assets and game outputs remain ignored by Git.

## Validation limits

Official mesh compilation plus retained tangent restoration checks zero opposed winding, tangent frames, meshpoint origins/rotations and required material references. The PDC sweep checks 48 barrel vertices at 20 yaw/pitch poses per gun against retained hull:240 poses and 11,520 surface samples. It is a bounded offline collision check, not proof over every triangle and continuous motion. Turret rotation, in-game material appearance, muzzle alignment while tracking and firing, and performance remain NOT RUN. User-provided screenshots establish the prior visual defect only.
