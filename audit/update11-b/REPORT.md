# Donnager higher-fidelity derivative — Update11 Worker B

**PASS OFFLINE ONLY. This new derivative has not been tested in Sins II.** The user's observation that three previous Donnagers ran smoothly applies to the 76,299-triangle version, not this new mesh. The original archive/master, previous geometry, installed data and SDK remain unchanged.

## Result and integration

The new complete assembly is **194,296 triangles**, versus 76,299 before: hull 166,141; rails 8,519 + 8,804; sixteen unchanged 677-triangle PDC assemblies. There are five unique meshes totaling 184,141 triangles. The increase is intentional and user-authorized; it exceeds the pinned SDK's 75,000 capital guidance and needs a new performance observation. No other ship was reoptimized.

`integration-spec.json` is the main-thread contract. Copy `build/update11-b/game` into the new combined package. The hull is `expanse11_donnager_hull`; each rail has a new `expanse11_donnager_rail_*` mesh and matching skin alias. Weapon IDs and all existing mesh-point names stay `expanse10_*`. Replace each rail's gimbal mesh/skin alias using the supplied rigs; do not rename weapons. Both PDC binary meshes are byte-identical to 0.10 and continue to use their old IDs.

All 18  compiled mount/equipment transforms are exactly equal to the accepted 0.10 arrays. The same 16 biaxial PDCs, two ±2-degree yaw-only rail gimbals, muzzle positions, front collars, aft launch apertures, hangar and four exhaust points remain. Bounds expand by less than 0.8 game units where original extremities are restored; the normalization and physical scale are unchanged. Use the new `ship_spatial` values supplied by the spec.

`ui-integration-spec.json` points to six new `expanse11_donnager_*` brushes and20 PNGs in `build/update11-b/ui/generated`. These were rendered from the actual complete 194,296-triangle editable scene. The portrait and UI contact sheet were visually inspected. They can replace prior Donnager UI via the provided patches; they do not replace the Corvette reinforcement icon, which belongs to main integration.

## How the geometry changed

The derivative is rebuilt from the original 1,804,024-triangle source, not by subdividing the old reduced model. The same pinned meshoptimizer uses source normals/UVs as weighted attributes and preserves node/material partitions. Requested index fraction rises from 0.023 to 0.075; maximum normalized attribute error drops from 0.0045 to 0.002. This retains 182,495 source triangles before removal of 15 numerical slivers, leaving 182,480 actual source triangles. Fixed supports/collars and existing PDCs produce the total above.

Final geometry normals are reconstructed at 30-degree creases within each source material partition. This allows retained bevel geometry to shade correctly instead of inheriting inappropriate pre-collapse normals. UV coordinates and original 2048² color atlases are retained. The source has no detail normal maps; no nonexistent detail is claimed as baked. Material values and all 27 DDS maps are byte-identical to the accepted version; only required new mesh/material alias names change.

Source-versus-derivative silhouette overlap improves from 99.07/99.19/98.01% to **99.75/99.78/99.23%** across the same three projected masks. All views now have zero missing or added pixels beyond the two-pixel tolerance. These are geometric silhouette checks, not proof of identical shading or runtime rendering.

Restoring the real hull exposed a 0.473-unit lower surface at one PDC 15 support corner. Only its fixed socket bottom extends downward 0.6 units to maintain overlap. Its gun pivot, muzzle and angles do not move. Four other restored surfaces meet socket feet 0.11–0.45 units above the old socket top; their slight embedded footing is retained, rather than moving guns or removing source plating. Every five-point footprint remains connected to the hull. Inspect these close up during the next test; all physical PDC geometry is otherwise unchanged.

## Checks actually run

- Original source optimization and crease-normal reconstruction; actual editable assembly: 35 nodes and 194,296 triangles.
- Official pinned MeshBuilder JSON and binary compilation of five meshes with facing grids, followed by measured winding correction and official grid regeneration.
- Tangent-only binary repair: no position/normal/UV/index/point/facing-grid/trailer changes, zero compiler-repair fallback tangents and maximum indexed rest-pose error 1.2231e-5 game units.
- Hull/rails have zero opposed or ambiguous faces and minimum face/normal cosine above 0.86. The two exact old PDC binaries retain their documented 3 base + 9 barrel near-perpendicular faces; this is inherited accepted donor content.
- 4,734 generated flat-material UV-frame fallback vertices are documented separately. These use a flat normal texture; no detail-normal-mapped donor fallback is introduced.
- 18 compiled mount/equipment arrays exact;16 five-point support checks against the new hull;400 vertices per rail at each of −2, −1, 0, 1, 2 degrees show zero contacts outside the existing drum/bearing envelope. Continuous/full internal collision is not proven by this bounded sample.
- 17 material definitions match prior values exactly; all mesh/material/texture references close;27 DDS headers/formats and exact prior hashes pass. The pinned SDK does not provide a mesh-material schema, so no nonexistent schema pass is claimed.
- 6 UI brushes validate against the exact pinned brush schema;20 PNG sizes/alpha and source dependency hashes pass.
- 119 frozen old files, five master files, both original archive copies and seven recorded donor dependencies unchanged. Two reused PDC binaries hash exactly equal.
- All new Python modules syntax-checked. Final handoff gates passed after compilation; no game was launched and no installed package was changed.

## Reproduction and ownership

Only new `tools/update11_donnager*.py`, `audit/update11-b`, `assets/derived/update11-b` and `build/update11-b` were written in the isolated `tachi-one-pdc` worktree. Main owns unit/skin integration, gameplay, increased plume, audio, explosion, shields and final package/push. The accepted explosion and PDC audio are not touched by this worker.

`tools/update11_donnager_build.py` reproduces the sequence into a **fresh** destination and refuses an existing candidate. The individual pipeline stages above were actually run to create this candidate. The wrapper is syntax-checked; a second full build was not performed merely to duplicate already-passing work. Missing ignored assets, donor files, compiler or Wine are hard failures, not skipped passes or download requests.

Read-only dependencies remain explicit in `update11_donnager_common.py`: original master under validation's`assets/derived/donnager04-c/master`, frozen donor/geometry under`expanse-workers/tachi-one-pdc`, intake records and pinned meshoptimizer under main`expanse-mod`. UI reads the prior CPU renderer from validation's`tools/polish_ui.py`; it does not reconstruct missing assets. SDK/game builds and schema pin remain unchanged. Wine needed local-socket sandbox permission for the official compiler only.

Editable compiler glTFs/buffers, full assembled glTF, original-derived normal/UV arrays and material recipe stay under`assets/derived/update11-b`. Generated binary meshes and material aliases stay under`build/update11-b/game`; game UI stays under`build/update11-b/ui/generated`, separate from the editable/source portrait recipe.

## Asset credit and remaining runtime checks

Donnager: **MCRN Donnager (The Expanse)** by **owlstraw**, model05e9f9006d914fcd96e95fbd452aaa28, CC BY 4.0; original source record remains in the accepted intake. PDC donor: Jakub.Vildomec's Tachi, CC BY 4.0 under its existing record. Modifications are the higher-fidelity reduction, generated crease normals, original fixed supports/collars and unchanged articulated donor mounts. Original package/master hashes remain unchanged. No model derivative was published by this worker.

Next workstation check: compare one new Donnager to the screenshot at matching zoom/light; inspect hull bevels and PDC 6/12–15 feet, both rail gimbals/muzzles and all existing equipment points. Then test three ships and a representative fleet for FPS, followed by movement/selection, firing and save/reload. Main's plume/voice/gameplay changes require their own observations. No result from this new geometry is marked runtime passed.
