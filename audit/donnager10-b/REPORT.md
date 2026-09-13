# Donnager10 geometry — Worker B

**PASS OFFLINE ONLY, with the inherited PDC shading condition below. Runtime NOT RUN.** Final resources are in `build/donnager10-b/game`; `integration-spec.json` is the exact integration contract. Unit physics, weapon budgets, abilities, skins, package identity, installation and observed runtime results belong to the main integrator. This worker did not install, enable, launch the game, publish, or change earlier outputs.

## Result and ownership

The assembled prototype is **76,299 triangles**, 1.73% above the pinned SDK's 75,000 capital-ship guidance. It has five unique meshes: hull **59,450**, rails **2,957 + 3,060**, and shared donor PDC base/barrel **138 + 539**, instantiated sixteen times. Unique mesh storage contains **66,144 triangles**. The complete editable scene has 35 nodes: hull, two rail gimbals and sixteen base/barrel pairs.

All writing is isolated to new `tools/donnager10_geometry*.py`, `audit/donnager10-b`, `assets/derived/donnager10-b`, and `build/donnager10-b` in the `tachi-one-pdc` worktree. Original intake assets, donor assets, installed game/SDK, and accepted main `expanse_amun09_cloak` resources are read-only dependencies. No intake was repeated.

Donnager source ownership is recorded per node/material/part in `mount-metadata.json`. Only source rail nodes 33–36 move to the two side meshes, partitioned by source-world X sign. Nothing from those moving assemblies remains duplicated in the hull. The new fixed PDC sockets, rail yokes and forward collars are explicitly prototype additions. PDCs come from the existing Tachi donor at physical scale **1.0**, with sixteen distinct weapon/mount references; their meshes can be shared without sharing or duplicating a weapon's firing budget.

## Optimization, scale and surfaces

The actual 1,804,024-triangle source was reduced separately by source node and material, preserving existing UV coordinates. The pinned meshoptimizer `simplifyWithAttributes` used normals and UVs as weighted attributes (0.1 each), permissive minor-seam collapse, maximum normalized attribute error **0.0045**, and a requested index fraction 0.023. Strict seam protection was tested first and retained 1.48 million triangles, so it could not meet the capital budget. This is a deliberate derivative optimization; material partitions remain separate, while small bevel/shading seams may collapse. It is not a claim that every original shading boundary survives unchanged.

The resulting source derivative has **64,483 triangles** after removing eight numerically degenerate slivers. Normals are reconstructed on the final geometry with a **30-degree crease**, separately within source material partitions, so collapsed bevels do not retain inappropriate old normals. No textures or normal detail were invented or baked. The original master's geometry, hierarchy, normals and UVs remain unchanged.

The provisional 475.5 m Donnager / 46 m Tachi convention gives **1085.2456264 game units** of source hull length. Transform: `(evaluated_source_world − [-0.000046789646, 42.71978135, 274.714836017]) × (1085.2456263978258 / 1183.900772034083)`. There is no additional rotation: +Z is bow, +Y is up. This is uniform provisional lore scale, not calibrated exporter meters or primary-verified canonical measurement. Donor guns are not enlarged by the capital/corvette hull ratio.

Three full projected source-versus-reduced masks measure overlap of **99.07%, 99.19%, and 98.01%**. Missing source pixels beyond a two-pixel tolerance are 95/47/130; added pixels beyond that tolerance are zero. `silhouette-comparison.json/png` record resolution and view axes. These masks support silhouette assessment; they do not prove identical shading, UV appearance or runtime performance. The editable asset and annotated first-mount view were visually inspected, and Worker C rendered the actual full scene independently.

## First mount, then repeated layout

`first-mount-proof.png` shows actual PDC0 support contact and the first source rail's drum/yoke. The first PDC's five footprint samples lie on the real reduced hull. Extending the same measured method produces four longitudinal stations at game Z **−370, −150, 50, 240**, with four X/Y sectors at each station. Each support's five samples intersect a nearly planar hull surface; normal agreement with the selected sector axis is at least 0.993. The sockets extend 0.5 units into the sampled surface and 0.6 units above its highest sample, with depths about 1.1–1.8 units. Donor feet overlap the socket top, so no moving assembly floats without a fixed support.

Sixteen PDCs is an explicit **prototype count**, not an assertion about the television ship. Candidate yaw is −180..180 degrees and pitch −85..5. Actual tracking, nearby protrusion obstruction and sector coverage remain runtime gates. Source world position, independent yaw/pitch coordinates, barrel offset, muzzle and skin alias bindings are all in `rigs[]`.

Each rail uses its actual complete source side assembly and the measured cylindrical drum center. The pinned weapon schema supports a `gimbal`; the prototype uses **yaw −2..2 degrees, pitch fixed 0**, with a requested 15 degrees/second yaw override. This avoids inventing an authored independent pitch joint. New fixed yokes bridge measured hull contacts to the drum end region. The terminal paired-rail structure supplies the muzzle center; it is a geometric muzzle inference, not an authored named bore socket.

Five yaw poses (−2,−1,0,1,2 degrees) sample 400 vertices per rail. No sampled radial contact occurs outside the original drum/bearing envelope (radius 11.2, axial half-span 19). The source already intersects bearing hardware at neutral; that intended region is excluded from this bounded clearance test. This is **not** a full mesh collision test or proof of continuous, internal or all-angle clearance. The main integrator reviewed and accepted this narrow gimbal candidate for runtime testing.

## Torpedo, engine and hangar references

- Four actual aft circular dark apertures are measured from source `AbsoluteBlack` node 60: source X±72.135 and Y31.788/53.651 at Z≈−207.731. Their ~6.9 source-unit diameters and outward normal are measured. They are assigned heavy-launcher meaning for the prototype because the source has no weapon labels. Each launch reference is 0.2 game units outside the first aft-facing surface, with a clear outward axis ray.
- No verified original light tube was identified on the front. Two new short collars are placed on measured forebody surfaces at game X±18, Y0, source surface Z291.9293 game units; muzzles are Z295.0293. Five footprint samples per collar support placement, and the +Z path is clear through the central forebody opening. These are custom prototype fittings, not canonical identified parts.
- Four complete actual source blue-emission nozzle surfaces from node 30 provide `exhaust.0` through `.3`, centered around game XY±101.739 and Z−523.168. Positions use each whole throat surface, not a single rim-edge vertex. All emit along −Z.
- The actual central aft gold hatch is ~99 source units across. Its measured mouth is near `[0,0,−448.342]`; `hangar.0` and `weapon.boarding.0` are aliases at `[0,0,−508.242]`, **60 game units outside** the closed static hatch. This provides corvette spawn clearance. No animated door, open portal or ship passage through a moving hatch is claimed.

`equipment` separates front light ports, aft heavy ports, four exhausts and the hangar. Main owns the corresponding ability/unit bindings. Existing source hatch and doors remain static.

## Official compiler and tangent checks

Five meshes were compiled to both JSON and binary with the installed pinned MeshBuilder and `--fill_triangle_facing_grid`. The exporter compensates the known Z reflection. MeshBuilder alphabetically sorts material names (`mat_10` precedes `mat_2`); winding correspondence therefore resolves exact material names, never assumes numeric source/compiled order. Per-triangle winding corrections are made in the glTF, followed by official recompilation of facing grids.

Tangent repair changes only each emitted vertex's 16-byte tangent field and matching JSON. Positions, normals, UVs, indices, points and the official opaque/facing-grid trailer remain byte-identical to the official binary. All five meshes have **zero repair fallback tangents**, finite unit orthogonal frames, and matching binary/JSON data. Indexed source/rest geometry differs by at most **1.22310e−5 game units** after compilation. Unused old donor accessor vertices (3,308 base / 7,781 barrel) are explicitly excluded from indexed-geometry conservation; their presence in storage is not extra ship geometry.

The source Donnager has no normal textures. During initial tangent construction, **2,508** vertices with degenerate/cancelling UV tangent sums receive an arbitrary valid orthonormal basis for their generated flat normal map. `uv-frame-fallback.json` proves these all belong to flat Donnager materials, never the detail-normal-mapped donor. This is distinct from the **zero** compiler-repair fallback count.

Hull and rails have zero ambiguous/opposed faces, with minimum face/normal cosine at least 0.868. The old donor retains **three base and nine barrel** faces with nearly perpendicular authored normals: twelve unique faces, **192 instances across sixteen guns**. Exact donor position/normal/UV arrays and unordered triangle membership are verified unchanged before compilation against frozen `polish-b`. The donor's prior audit has the same counts; minimum cosine remains within the existing **−1e−5** winding tolerance. Main explicitly accepted this inherited condition for these two donor meshes only. Hull/rail gates remain strict. Runtime inspection of these donor surfaces is still appropriate.

## Materials and actual checks

The 49 staged files contain five meshes, seventeen exact compiler material aliases and twenty-seven DDS maps. Donnager uses two original 2048² base-color atlases, 16² constant color/ORM/mask/flat-normal maps, and source material factors. Existing donor 2048² detail maps and its 4² mask are copied byte-for-byte from the accepted package. BC7 and signed BC5 DDS headers, dimensions and reference closure were checked. No arbitrary player-color region was introduced. Original emissive surfaces use a base-color-tinted emission mask, so independent source emission RGB is approximated by the game's material convention.

Actually run: optimization probes; final crease-normal reconstruction; source/reduced silhouette comparisons; source-derived support/port geometry measurements; first mount visual inspection; five official JSON/binary compiles and winding/grid regeneration; strict18 mount bases and required center/boarding/four-exhaust points; binary/JSON/frame/trailer conservation; indexed rest reconstruction; twenty-three texture conversions; donor texture hash checks; all staged reference/hash checks; editable scene count; and original/donor/prior-checkpoint preservation. These pass under the documented inherited donor condition. Unit/weapon/material schema and assembled-package validation belong to the integrator; no runtime pass is claimed here.

Both supplied and preserved source archive hashes match `b03d70d6180b7c6ff50db22df883f576ebb3981c5d4d138f8bdf1e7434079562`. All five extracted master files, eight recorded donor dependencies, and **229 frozen prior files** (hero04 128, torpedo05 26, Amun06 75) are unchanged. `final-provenance.json` records this work's final files and dependencies.

## Reproduction

From this isolated worktree, use existing Python NumPy/SciPy/Pillow and `OPENBLAS_NUM_THREADS=1`. No dependency or schema update is needed. New outputs are separate from original assets and prior packages. Rebuilding intentionally supersedes this candidate's frozen hashes; do not run these to update an installed baseline.

1. `python3 tools/donnager10_geometry_probe.py`
2. `python3 tools/donnager10_geometry_normals.py`
3. `python3 tools/donnager10_geometry_layout.py`
4. `python3 tools/donnager10_geometry_equipment.py`
5. `python3 tools/donnager10_geometry_prepare.py`
6. `python3 tools/donnager10_geometry_editable.py`
7. `python3 tools/donnager10_geometry_proof.py`
8. Run `donnager10_geometry_compile.py`, then `donnager10_geometry_winding.py`, each with `--sdk '/run/media/haker/NVME 2/SteamLibrary/steamapps/common/Sins of a Solar Empire II - Mod Tools' --wine '/home/haker/.var/app/com.valvesoftware.Steam/.local/share/Steam/steamapps/common/Proton 10.0/files/bin/wine64'`.
9. `python3 tools/donnager10_geometry_finish.py`
10. Run `donnager10_geometry_textures.py --wine` with the same Wine path.
11. Run `donnager10_geometry_silhouette.py`, `donnager10_geometry_checks.py`, `donnager10_geometry_uv_check.py`, and `donnager10_geometry_handoff.py`.

`point_alias.py` was used to append the accepted boarding alias without changing the already-rendered geometry; fresh `prepare.py` now emits that alias directly. The compiler script can rebuild a single named mesh with `--mesh`. The dedicated Wine prefix is copied from this worker's existing `build/polish-b/proton-prefix` into `build/donnager10-b/proton-prefix`. Missing source archives/master, donor assets, pinned tools, prior preservation manifests or that prefix are errors, not skipped passes or substitute-download triggers.

## Asset credit and next runtime gates

Donnager source is **MCRN Donnager (The Expanse)** by **owlstraw**, [source model](https://sketchfab.com/3d-models/mcrn-donnager-the-expanse-05e9f9006d914fcd96e95fbd452aaa28), [creator](https://sketchfab.com/strawfinch), licensed [CC BY 4.0](http://creativecommons.org/licenses/by/4.0/). Original packaged attribution is preserved. The PDC donor is Jakub.Vildomec's separately credited CC BY 4.0 Tachi asset under its existing source record. A distributed combined derivative requires both credits, license links and description of modifications. No distribution happened here.

Smallest geometry runtime sequence: load/select at multiple zooms and check surfaces/scale; inspect each PDC sector and shared-budget behavior; test limited rail rotation and muzzle alignment; fire front light and rear heavy torpedoes; observe all four nozzles; launch a corvette clear of the static hatch; then construction/movement, destruction, save/reload and one-ship/formation/fleet performance. Every such result remains **NOT RUN by this worker**.
