# Gathering Storm: update26 art replacement

This is an art-only overlay against the frozen `expanse_update25` package. It replaces the Storm hull and eight numeric color/ORM textures, and adds one drive material. It supplies no unit, weapon, ability, research, effect, movement, or economy changes.

## Appearance and adaptations

The [Gathering Storm appearance description](https://expanse.fandom.com/wiki/Gathering_Storm), citing *Persepolis Rising* chapter 22, describes a narrow crystalline ship with pink and blue facets and an unusual drive. This informed the broad blue, pink and pearl regions. The printable source provides neither a production texture set nor an accurate working drive. The reused Truman engine assembly is an explicit game-art adaptation, not a canonical reconstruction of Laconian propulsion. No story developments or new shield mechanics are included.

The former averaged normals and orientation-dependent paint assignment made the hull appear crumpled and speckled. The replacement uses coherent spatial color regions and hard per-face normals, with orthogonal tangents retained through the official mesh compiler. Roughness is 0.55 and metallic is 0.28 across the crystalline hull regions, retaining restrained reflectivity rather than an all-matte finish. The drive retains its existing native textures. Materials remain opaque.

The central stern opening is clipped geometrically, retaining surrounding hull details. The reused drive includes its bell, throat, rings and internal hardware: 6,123 triangles. The hull and drive total 70,853 triangles; the six unchanged PDC assemblies bring the visible assembly to 74,915. The fixed keel gun remains part of the original hull.

## Dimensions and integration

The outer hull bounds remain exactly those of frozen 0.25: 375 game units long, with half-extents approximately `[38.333924, 28.747783, 187.5]`. The existing fleet scale equates this to a mod-designed 164.31 m; this is not a canonical length claim. Unit spatial bounds, movement, all six PDC rig points, firing arcs and weapon origins remain unchanged.

Only mesh point `exhaust.0` moves, from `[0, 0, -178.628159]` to `[0, 0, -187.899994]`, just beyond the new nozzle. Its rotation is unchanged. The existing idle plume already follows this mesh point, so **no unit-skin, effect or mesh-alias edit is required**. Keep the existing ordinary native hyperspace effects.

The generated `audit/update26-storm/replacement-manifest.json` is the authoritative list of ten changed files, with exact SHA-256 hashes and previous hashes. Copy only those entries from `build/update26-storm/game` into the parent candidate. Twenty-four unchanged dependencies are listed for verification and need no replacement. The overlay directory itself is not a playable package.

## Observed checks and limits

- Official MeshBuilder compilation completed with a facing grid and intact opaque binary trailer.
- Frozen outer box, unit spatial data, non-exhaust mesh points, six PDC arcs and PDC mesh bytes compare unchanged.
- Hull face normals align with their own triangles at a minimum dot product of 0.999966.
- Offline ray sampling checked 1,177,290 rays over the six frozen firing envelopes and their aim allowance; none intersected the hull or added drive.
- Compiled mesh/DDS previews were rendered in oblique, side, top and stern views. The oblique and stern outputs were visually inspected: broad color regions are coherent, the engine has a visible bell and inner hardware, and the keel gun and PDC assemblies remain present.

The software preview is diffuse-only. It does not validate the final in-game specular response, engine particles, animated PDC targeting or gameplay. Those remain untested here and need the parent playtest. No installation or game launch was performed.

## Reproduction

Run the scripts from this isolated worktree, in order: `update26_storm_geometry.py`, `update26_storm_compile.py`, `update26_storm_preview.py`, and `update26_storm_validate.py`. The optional `update26_storm_materials.py` reapplies the same final numeric ORM values without recompiling geometry; rerun validation after it to refresh file hashes. Dependencies are the frozen main 0.25 package, existing main asset helpers, pinned SDK and existing Wine conversion prefix. The geometry build does not modify those inputs.

Artifacts are under `audit/update26-storm/` (integration specification, manifest and previews), `assets/derived/update26-storm/` (editable geometry) and `build/update26-storm/game/` (compiled replacements).
