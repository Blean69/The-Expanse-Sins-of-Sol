# Morrigan starter frigate geometry handoff

**PASS offline; runtime NOT RUN.** Main integrator owns all unit, skin, weapon, magazine, player, voice, shield, build-menu and package definitions. This worker supplies the local derivative and static UI only. No game launch, installation, source modification or publication occurred.

The supplied binary STL has306,518 triangles and57 welded connected components. It contains no materials, texture images, UVs, scene hierarchy, animations, separate yaw/pitch pivots, or documented scale. The source's long axis is X; the engine bell is at+X, bow at−X, and+Z is up. The derivative maps these to game+Z bow/+Y up using a proper determinant+1 rotation, preserving handedness. Its78.75-unit length is an explicit75% scale assumption relative to the current105-unit Tachi, not a claim of canonical dimensions. No separate printing stand was identified in the inspected projections; none was arbitrarily deleted.

Original SHA-256: `72dcce753f7ac17b1a4600fffb649e93af78e9b19527a2386b46a61cdd115188`. Original download and preserved intake copy match exactly. The supplier's identity, original creator and exact license were not supplied. The record documents the user's request for local conversion, and does not invent a license or broader redistribution grant. Master: `assets/original/update11-morrigan/xxx_-_morrigan.stl` in this isolated worker tree.

The hull is reduced with the existing pinned meshoptimizer library, relative error0.00114420 (limit0.004). The two original static gun assemblies and their disjoint endcaps/pins are excluded only from the derivative (component IDs20,21,27,29,30,31,32,33). Their existing hull supports remain. Nine numerical sliver faces were removed after the offline compiler exposed float-precision winding instability. No normal/tangent tolerance was relaxed to hide them.

The finished hull has28,831 triangles, including new supports and two bow collars. Each imported proven Tachi PDC has138 base+539 barrel triangles. Two instances give **30,185 assembled triangles** across three unique compiled meshes. Source STL geometry remains separately editable in the preserved master; normalized, optimized and assembled glTF derivatives remain under `assets/derived/update11-c`.

New matte grey materials, orange gun-support collars and dark launcher mouths are explicitly authored procedural colors. No source texture was supplied or reconstructed. Each face receives valid projected UVs; smooth normals blend only across surfaces within45° and preserve stronger creases. Constant flat-normal DDS textures retain this geometric shading. The PDCs reuse the accepted Tachi material DDS resources read-only.

Two measured surfaces support the PDC yaw pivots. Each new cylinder embeds0.65 game units into the retained source support. The outward/up30° axes retain the accepted biaxial donor's offsets and firing frame. There is one mesh/mount per gun, with one weapon ID each. Two dark open collars attach to measured front-face surfaces; these are clearly new derivative launcher hardware, not asserted original modeled torpedo apertures. Equipment coordinates are in `integration-spec.json`. The actual engine bell's aft plane defines exhaust. No deployment animation or new moving source part is claimed.

Offline checks actually run:

- Source STL parsing, byte-length, bounds,57-component audit and preserved SHA-256 comparison.
- Official installed MeshBuilder JSON and binary conversion for all three unique meshes, including regenerated triangle-facing grids after input-index winding correction.
- Exact16-byte tangent-only repairs from retained authored frames; no other binary bytes, indices, meshpoints or official grid/trailer changed; zero tangent fallbacks.
- Zero opposed winding triangles under the existing−1e−5 tolerance. Hull has zero ambiguous cases; donor has its established3 base+9 barrel cases, unchanged from the accepted donor.
- Meshpoint positions and game row-vector rotation matrices; orthonormal positive-determinant mount frames.
- Both torpedo launch rays unobstructed.64 sampled barrel-centerline orientations (2mounts×8yaw×4pitch) clear the hull. These samples do not prove full swept-mesh clearance or runtime tracking/coverage.
- DDS conversion/header/reference checks,6 pinned-schema UI brushes,18 RGBA DPI sprites and2 optional actual-model logos. The UI is rendered from the assembled derivative. Donor PDCs use a conservative solid render factor in UI; actual game meshes retain the donor textures.
- Annotated actual-geometry mount view: `mount-diagram.png`. Final portrait: `build/update11-c/ui/source/morrigan_portrait_master.png`.

Integration: `audit/update11-c/integration-spec.json` identifies18 mesh/material/DDS files in `build/update11-c/game`, all hashed. `ui-integration-spec.json` identifies the separate UI directory and skin patches. Copy these resources into the main experimental package; do not install this worker folder as a mod. User-facing runtime tests still need loading, both PDCs' rotation/contact/aim/muzzle alignment, alternating launcher mouths, plume alignment, selection/UI, orbiting, interception, destruction and save/reload.

Reproduce from this isolated tree with the original STL, main repo's pinned ignored `.tools` dependencies, unchanged Tachi donor and accepted package present:

```sh
python3 tools/update11_morrigan_intake.py
python3 tools/update11_morrigan_geometry.py
python3 tools/update11_morrigan_compile.py
python3 tools/update11_morrigan_ui.py --source 'assets/derived/update11-c/expanse11_morrigan_editable.gltf' --expected-triangles 30185 --game '/run/media/haker/NVME 2/SteamLibrary/steamapps/common/Sins2' --sdk '/run/media/haker/NVME 2/SteamLibrary/steamapps/common/Sins of a Solar Empire II - Mod Tools'
python3 tools/update11_morrigan_validate.py
```

The UI renderer requires a fresh `build/update11-c/ui` destination. It refuses to overwrite an existing result. Mesh/texture converters require Wine's local socket access; the sandboxed attempt correctly failed and the approved isolated converter invocation completed. Missing ignored dependencies raise explicit failures. No substitute downloads occur.
