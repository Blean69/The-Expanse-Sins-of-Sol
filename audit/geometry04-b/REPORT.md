# Worker B — hero geometry04

This separate candidate addresses the user-observed crooked/fragmented appearance and provides six independent biaxial aiming rigs. Original archives, extracted masters, all0.3 artifacts and installed game/SDK remain read-only. No game launch, installation, enablement, shared definition edits, commits or publishing were performed by this worker.

## Diagnosis before repair

`source-pose.json` compares every source segment relative to the engine segment at animation start/end. All fixed hull segments share the same rigid transformation, with no per-segment bend or scale deformation. Only the removed stand and animated equipment differ. The old principal-axis normalization differs from the authored nozzle axis by approximately0.66 degrees; it does not account for the larger apparent surface deformation.

`source-v-optimized.png` renders the original deployed source and0.3 topology with both sides shown and with author-normal culling. The original hull remains coherent in both views. The0.3 surface distortion persists when backface culling is disabled. The earlier permissive simplification/error0.04 and retained normals across collapsed hard features were the concrete problem. Merely adding backfaces would preserve that distortion.

The new derivative reuses the already audited deployed source transforms and the same pinned meshoptimizer library. It lowers the relative error bound from0.04 to0.005 and preserves the existing per-source-part/material decomposition. Pure border/normal locking was measured first and retained approximately426,000 triangles, so it was not silently advertised as an efficient solution. The selected corrective topology has90,128 ship triangles plus the existing228 custom fitting triangles. It uses permissive collapse with a substantially tighter error bound; it is not claimed to lock every material seam.

Geometric normals are recalculated on the resulting faces with a30-degree crease, without changing their coordinates or flat source colors. This removes the obsolete interpolated normals across collapsed hard edges. Seventeen numerically degenerate hull faces (area≤1e-7 or area/longest-edge-squared≤1e-6) were removed after the first strict compiler check found rounding-dependent winding on two microscopic slivers. Their counts are recorded per part. No blanket double-sided backing or hull-shell invention was added.

`hero-aiming-rig-view.png` shows the final corrected editable geometry and a representative source cannon with the new pivot/support positions. Runtime inspection remains required for remaining source seams, shading and hull occlusion.

## Physical axes and preserved equipment

`normalization.json` records the exact additional rigid transform: new_position = R × (old_position − target_center) + target_center. R aligns the previously fitted authored nozzle axis with actual game aft-Z; there is no visual-only hull animation or navigation change. Existing Cobalt scale/target center are preserved. All source components, custom railgun/ports and effect points receive the same transform.

`equipment.json` contains transformed rail, two launcher positions and exhaust. The custom rail and ports retain their exact relationship to the physical hull. Because the old custom rail was authored along old game-Z, its new forward vector includes the same small rigid correction; use the recorded vector and compiled point rather than forcing identity orientation. Exhaust now points along measured aft-Z. No unit physics or weapon gameplay values were edited.

## Six actual source cannons with explicit aiming joints

The source animation rotates each complete cannon group approximately30 degrees around its barrel direction. That is deployment motion, not a usable aiming yaw/pitch pair. The new rig does not mislabel those source animation axes.

For each of six assemblies, cannon1, cannon2, magazines and pins remain together in the pitch mesh. The actual cannon1 muzzle measurements from0.3 are transformed rigidly. Source slide housings, frames, fillers and deployed covers remain fixed in the hull. Ownership lists identify all removed moving source nodes, avoiding hidden static copies underneath.

A new pitch origin is placed at the actual deployed cannon2 mounting-block bounds center. The matching fixed pdc1 outer surface determines the yaw socket position. Added fixed socket, rotating shaft, yoke and trunnion geometry provide a physical connection. These are explicit new aiming joints, not claims that the source asset supplied finished Sins turret mechanics. Yaw and pitch axes are orthogonal, both use the proven game biaxial conventions, and their actual meshpoint rows match right/up/forward.

The six weapons use one base/barrel mesh pair each. Metadata provides mount data, turret geometry fields, local muzzle coordinates and skin aliases; the main integrator owns all final weapon/unit/skin changes. Candidate arcs are yaw−90..90 degrees, pitch−65..10 degrees. These bounds are experimental. Fixed covers or housings may occlude a gun at some angles; axis continuity tests do not prove collision clearance. Preserve the actual aft-facing rest direction of source gun3 until runtime evidence justifies a geometric change.

Final total92,067 triangles: fixed hull67,377, six yaw meshes192 each, six pitch/cannon meshes3,923 each. Support geometry adds1,728 triangles. This prioritizes a coherent unique hero over the earlier destructive triangle ceiling. Fleet performance and any later optimization need separate measured acceptance gates.

## Outputs and integration

- `mount-metadata.json`: thirteen mesh frames/counts, six unit mounts, turret overrides, skin child bindings, equipment transforms, source ownership and final mesh hashes.
- `output-validation.json`: official JSON/binary and tangent/winding/meshpoint checks.
- `independent-geometry-checks.json`: rest muzzle reconstruction, shaft/trunnion attachment invariants, rigid equipment transform and preservation checks.
- `material-resources.json`:21 actual compiler material aliases and twelve unchanged hero DDS maps.
- `integration-spec.json`: concise artifact and mount handoff for the main-owned package.
- `final-provenance.json`: final source/artifact hashes and preservation results.

Meshes: `build/geometry04-b/game/meshes/expanse04_hero_hull.mesh` and `expanse04_hero_pdc_0..5_base/barrel.mesh`. Materials/textures are in sibling directories. Editable thirteen-part hierarchy: `assets/derived/geometry04-b/expanse04_hero_editable.gltf`; compiler glTF inputs have explicit Z compensation and are separate. Generated artifacts and source assets remain ignored by Git.

## Offline checks and reproduction

The pinned official MeshBuilder compiles each input to JSON and binary with triangle-facing grids. Winding corrections alter source indices and then regenerate official grids; no index or trailer bytes are hand-patched. Generated tangent frames receive the established bounded16-byte-per-vertex repair, with every other binary byte and official trailer preserved. Checks require binary/JSON parity, non-opposed winding, unit orthogonal finite frames, source position reconstruction and strict stock-game matrix-row conventions.

Independent checks reconstruct every muzzle from base origin + base basis × (barrel offset + muzzle offset), test shaft and trunnion continuity for five yaw and four pitch samples, and verify rigid rail/port/exhaust transformations. They do not simulate game targeting or collisions. All155 files in the prior0.3 frozen manifest and24 earlier read-only inputs were rehashed unchanged.

Commands, run from this isolated worktree with OPENBLAS_NUM_THREADS=1:

1. `python3 tools/geometry04_diagnose.py` and `geometry04_compare.py` inspect existing evidence.
2. `python3 tools/geometry04_source.py` creates the bounded corrective part derivative; `geometry04_quality_probe*.py` records the evaluated offline alternatives.
3. `python3 tools/geometry04_rig.py` produces thirteen compiler inputs and metadata.
4. `python3 tools/geometry04_compile.py --sdk <pinned SDK> --wine <installed Proton wine64>`.
5. `python3 tools/geometry04_winding.py --sdk <same SDK> --wine <same wine64>` regenerates official grids after source corrections.
6. `python3 tools/geometry04_finish.py`, then `geometry04_resources.py`, `geometry04_editable.py`, `geometry04_view.py`, `geometry04_checks.py`, `geometry04_spec.py` and `geometry04_provenance.py`.

Dependency paths are the existing read-only0.3 source/master/deployed files in this worker worktree, the installed SDK and game, the main project's pinned `.tools/libmeshoptimizer.so`, and existing hero DDS/material sources. Compilation uses `build/geometry04-b/proton-prefix`, copied from the worker-owned prior prefix only. Missing ignored dependencies must fail rather than download substitutes. Do not rerun against installed baselines or a shared Wine prefix.

## Small workstation gate

Load the separate hero04 experiment. Inspect all hull sides and panel shading near/medium zoom, then order targets around all six gun directions and above/below to inspect yaw, pitch, fixed-cover clearance and actual muzzle alignment. Check aft gun3 explicitly. Fire the unchanged rail and torpedo definitions from their rigidly transformed fittings; inspect the centered exhaust. Check a single hero and the intended maximum hero count for performance. Save/reload after firing and moving. No runtime result for this candidate is reported as passed here.
