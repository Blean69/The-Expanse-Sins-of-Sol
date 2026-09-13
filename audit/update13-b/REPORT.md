# Update 0.13 hull visual repairs — isolated worker B

Status: **PASS OFFLINE ONLY**. In-game appearance and performance remain **NOT RUN**.

Owner: hulls13, isolated worktree `expanse-workers/visual13-hulls`. Overlay contract is `audit/update13-b/integration-contract.json`; no unit, skin, weapon, sound, player, manifest, or gameplay definitions were changed.

## Morrigan paint

The previous model assigned the entire STL hull to the gray material; its orange material appeared only on the turret support collars. This was a livery assignment gap, not a missing texture-file reference.

The derivative now assigns two prominent orange-red regions across the bow cheeks and aft shoulder, preserving charcoal plating and darker machinery. The existing Martian material/DDS resources are reused without editing pixels. Paint boundaries split triangles at exact planes, so a large triangle cannot produce a zigzag paint edge. No additional texture dependency or borrowed reference-art texture is required.

Hull triangles increase from **28,831 to 32,863**, assembled total **34,217** including two unchanged PDC assemblies. This is coplanar paint subdivision, not a new optimization pass or added silhouette geometry. Bounds, equipment points, surface area, turret scale and weapon placement remain unchanged. The regenerated portrait, HUD and tooltip images use the actual colored derivative; six brushes and twenty PNG outputs passed the existing pinned brush/UI checks. Root logo images are optional and need not replace the combined package's logo.

Preview: `build/update13-b/morrigan/ui/source/morrigan_portrait_master.png`.

## Raptor and Pella shading

The previous hull generator averaged every coincident face normal with equal weight within a 45-degree threshold. Dense narrow grooves could pull the corners of a large plate toward their normals, even when their area was tiny. That is a plausible contributor to the crumpled appearance in the user's screenshots.

The new derivative uses face-area weighted corner normals with a 25-degree crease threshold. This retains hard plate boundaries while reducing narrow-facet bias. Tangents are projected back onto the corrected normal plane and renormalized. This addresses shading only: the source's optimized surface detail is retained, and remaining genuine geometric facets are not claimed to be repaired by normals alone.

The main gray Raptor hull's mean corner-to-face normal angle decreases from **5.94 to 2.29 degrees**; 95th percentile from **21.49 to 11.32 degrees**. Pella shows corresponding values **5.93 to 2.28** and **21.47 to 11.32**. These are diagnostic measures, not a substitute for observing the in-game result.

Raptor hull remains **88,730 triangles**; Pella remains **89,430 triangles**. The validation compares ordered compiled triangle positions and UVs against the frozen 0.12 package: unchanged within compiler float tolerance. All meshpoints match exact parsed values. Pella's silver material, Free Navy emblem texture and UV layout are preserved. Existing Raptor/Pella UI is retained because its CPU renderer uses geometry/materials rather than vertex shading frames, and neither geometry nor visible color layout changed.

## Offline checks run

- Pinned official MeshBuilder JSON and binary compilation for all three hulls, including official facing grids.
- Retained source-frame matching and tangent repair, verifying only tangent bytes change after official compilation and opaque trailers remain intact.
- Zero opposed-winding triangles and no non-unit normals or non-orthogonal normal/tangent frames in the final compiled overlays.
- Exact equipment meshpoint preservation; unchanged bounding boxes and surface area (relative tolerance 0.000002).
- Exact ordered triangle-position and UV correspondence for Raptor/Pella.
- Material and texture references resolve against the frozen 0.12 package without copying unnecessary dependencies.
- Existing source glTF/binary input hashes unchanged after processing.
- Morrigan actual-mesh UI render and existing pinned brush/schema/dimension/alpha checks.

## Reproduce

Run in the isolated worker checkout or integrated main checkout with the recorded ignored source dependencies available:

```bash
python3 tools/update13_hulls_prepare.py
python3 tools/update13_hulls_compile.py --variant morrigan
python3 tools/update13_hulls_compile.py --variant raptor
python3 tools/update13_hulls_compile.py --variant pella
python3 tools/update13_hulls_ui.py --source assets/derived/update13-b/morrigan/expanse11_morrigan_editable.gltf --expected-triangles 34217 --game '/run/media/haker/NVME 2/SteamLibrary/steamapps/common/Sins2' --sdk '/run/media/haker/NVME 2/SteamLibrary/steamapps/common/Sins of a Solar Empire II - Mod Tools'
python3 tools/update13_hulls_validate.py
```

The UI renderer refuses to overwrite an existing UI output. Use a fresh isolated output environment for a clean reproducibility run. Wine requires its local IPC sockets; restricted-shell attempts failed with `wineserver: bind: Operation not permitted`, then the same pinned offline tool ran successfully with a scoped escalation. No game launch or installation took place.

## Asset source and permission record

No new external artwork was imported. This change derives only from the project's already-audited Morrigan STL derivative, Raptor/Pella derivatives and existing Pella emblem. Original archives, extracted masters, donor turrets, source textures, and installed game/SDK inputs were read-only. Their existing source/permission records remain applicable. The user's screenshots provided diagnosis and direction; they were not grafted onto these hulls or included in the overlay.

## Workstation checks

1. Inspect Morrigan from both sides, above and below: readable orange bands, retained dark recesses, unchanged two PDC mounts and torpedo mouths.
2. Inspect Raptor/Pella broad forward plates under changing illumination and zoom; compare the crumpled artifacts against 0.12 screenshots.
3. Verify Pella's eagle remains visible and correctly placed; check all hull PDCs and torpedo effects remain aligned.
4. Observe a mixed formation for performance. No runtime pass is asserted here.
