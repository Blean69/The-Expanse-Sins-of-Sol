# 0.27 Mars/Laconia art handoff

This isolated overlay targets frozen `expanse_update26`. It contains art and the Storm spatial/rig patch only. Main owns the new frigate and Hephaestus gameplay, research, prices, weapons, localization, faction access, icons and final packaging.

## Sources and attribution

Hephaestus source is Adyne's fan design, explicitly not canonical. Its author describes a mobile Callisto destroyer with one railgun, ten PDCs, five small and three medium torpedo tubes, a small hangar and defensive marines. The art follows that source arrangement. [Creator's original model](https://sketchfab.com/3d-models/mcrn-hephaestus-class-destroyer-printable-8774ee0a3a8e41a39c677dbeb6d979bc).

This work is based on “MCRN Hephaestus-Class Destroyer (Printable)” by [Adyne](https://sketchfab.com/Adyne), licensed under [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/). Changes: controlled simplification, coordinate/scale conversion, replacement articulated PDCs, extraction and articulation of the source railgun, fitted firing ports, materials and livery. Retain this credit with distribution.

The supplied `LaconiaFrigate.stl` is an unnamed fan frigate with no creator metadata in the STL. Six guns, procurement identity, game size and additional details are mod adaptations; no canonical class identity is asserted. The user supplied permission for model use earlier in this work.

The Storm retains the supplied original silhouette and existing asset provenance. [Gathering Storm appearance reference](https://expanse.fandom.com/wiki/Gathering_Storm) describes a knife-like crystalline ship. This pass follows the user's newer gray reference for color and modest smoothing; the gray finish is an artistic adaptation. No plot or weapon-lore expansion is introduced.

Source paths and SHA-256 values are recorded in `audit/update27-mars-laconia/source-intake.json`. Native PDC and drive material dependencies are explicitly copied from the frozen package; Wine/SDK trees are never copied recursively.

## Deliverables

Absolute artifact root:
`/run/media/haker/NVME 2/expanse-workers27/mars-laconia/build/update27-mars-laconia/game`

Audit/contracts/previews root:
`/run/media/haker/NVME 2/expanse-workers27/mars-laconia/audit/update27-mars-laconia`

Each ship has `<ship>-integration.json`, `<ship>-manifest.json`, and compiled oblique/side/top/stern/bow previews. Manifests list only the final dependency closure, with file hashes and add/replace/reuse actions against frozen 0.26. Copy add/replace entries; unrelated stale staging files are not part of the delivery. Main derives UI silhouettes from the final previews.

### Gathering Storm

Length grows uniformly by 15% to 431.25 game units. Hull, six gun assemblies, barrel offsets, muzzle offsets, exhaust, child points, fixed keel muzzle, magazine origins and spatial bounds follow the same factor. The keel weapon definition and all combat/movement/economic fields are unchanged.

The final pass replaces the hidden Truman assembly with the existing MCRN Tachi’s actual curved bell and contained throat machinery. A shorter closed connector joins the measured hull at z=-166.75 to the narrow native throat; the flared bell remains exposed in side views. A thin open metallic lip distinguishes the mouth from the dark throat. The opening remains at z=-215.625. Source UVs, normals and drive materials are retained.

Fifteen bounded Taubin smoothing iterations change small actual vertex bumps, with maximum displacement 1.25 units before scale. Keel, stern and 35-unit neighborhoods of all mount pivots are protected. Broad original sculpted facets remain visible; this is not a complete smooth-surface remodel. Materials use restrained gray silver and a darker connector. Fine thermal tiles use shared generated base-color/normal maps, world-aligned UV projections, and authored roughness approximately 0.42–0.47 with metallic 0.32. The lip has lower roughness and higher metallic response. Offline previews are diffuse-only and cannot establish the in-game specular result.

Hull mesh keeps `expanse24_storm_hull`; new gun mesh aliases are `expanse27_storm_pdc_base` and `expanse27_storm_pdc_barrel`. Existing child-point names remain. `tools/update27_storm_patch.py:changes(base)` returns exactly nine edited definitions: unit, magazine, skin, six PDC turret-only derivatives. Skin alias bindings are inside `skin_stages[0]`. Main merges these with its independent procurement changes.

### Hephaestus

270-game-unit source hull conversion. Four existing engine pods and their forward panel detail are retained. The printable aft caps are replaced by exposed 28-unit native Tachi bells, narrow fitted connectors and metallic lips. Source static PDC clusters are removed and replaced by ten native biaxial guns on short octagonal feet. The actual source railgun is extracted as a gimbal mesh; it has bounded yaw ±12° and pitch ±1°, retaining a positive native pitch interval.

Rig order is **PDC indices 0–9, rail index 10**. Hull mesh `expanse27_hephaestus_hull`; PDC aliases `expanse27_hephaestus_pdc_base/barrel`; rail alias `expanse27_hephaestus_rail_0`. All child names, source-derived pivots, accepted arcs and turret fragments are in the contract. Five light and three medium torpedo origins use visible fitted collars centered on the actual source tube-face components, then projected to the retained surface. Four exhaust points are `exhaust.0` through `exhaust.3`, at final opening positions with z=-136.4.

Source has 1,667,487 triangles; controlled simplification preserves hull panels and engine shapes. The rail retains 6,500 triangles. Livery boundaries are cut through triangles so orange bands have straight edges rather than centroid-selected triangular blotches. Full compiled assembled count is recorded by the manifest.

### Laconian frigate

160-game-unit source conversion; original small wedge proportions remain. The source closed engine stub is replaced by an exposed 22-unit Tachi cone with a recessed throat, a short closed connector and metallic rim. Sensor ridges, heat-management strips and two visible launch collars add actual geometry. Six native rotating PDCs use short octagonal feet, with per-mount clearance-derived native arcs.

Hull mesh `expanse27_laconia_frigate_hull`; PDC aliases `expanse27_laconia_frigate_pdc_base/barrel`; child-point suffixes `_pdc_0` through `_pdc_5`. One engine point is `exhaust.0`. Final triangle counts are recorded in the manifest (source STL: 4,294); removing the hidden donor assembly lowers the count while exposing the correct cone geometry.

## Validation and limits

Official MeshBuilder generates mesh binaries and opaque facing grids. Per-corner normal/tangent data is restored against matched source vertices after official compilation; binary geometry, primitive and mesh-point counts are checked. No unverified binary trailer is synthesized. Exact material/texture dependency closure and hashes are validated.

Storm's six original arcs pass 1,177,290 sampled rays. Frigate's six accepted arcs pass 1,435,122 rays. Hephaestus checks include its source rail at minimum/neutral/maximum yaw as a conservative PDC obstacle envelope, and a separate rail-to-hull check. Final counts are recorded in its manifest. PDC sampling uses a 1° grid with an additional ±3° aim envelope; rail sampling uses 0.5° steps and a ±1° envelope. These are discrete muzzle-to-hull checks, not proof of continuous swept-volume clearance or collisions between independently moving PDCs.

All nine Storm JSON changes pass installed SDK schemas plus guards that preserve nonspatial unit fields, non-turret weapon fields, magazine behavior and original arcs. Integration requires main to consume the final accepted contracts rather than earlier draft arcs.

Observed: SDK compilation, offline visual inspection, dependency/hash validation, schema validation and sampled clearance. Untested: game loader, live tracking/animation, specular appearance, projectile targeting, saves and multiplayer. No installation or game launch occurred in this worker.

## Reproduction

The final drive/surface pass is `update27_epstein_surface.py <ship>`, applied after the first compiled/validated art baseline. It records a bounded explicit pre-pass snapshot, preserves every weapon pivot and torpedo origin, and recalculates spatial bounds from hull, drives and mounted meshes. It does not copy SDK or Wine trees. Run the compiler, preview and validator again after this pass.

Initial build: `update27_mars_intake.py`; each `update27_*_geometry.py`; `update27_mars_compile.py <storm|hephaestus|laconia>`; `update27_mars_preview.py <ship>`; `update27_mars_validate.py`. Do not run two SDK/Wine compiles simultaneously against the same existing prefix. The compile script uses explicit read-only dependencies and writes only this worker's derived/staging roots.


## Final surface reference and encoding

The user provided Paul Kiesling’s Scirocco displays/material sheets. The [artist’s project](https://paulwk13.artstation.com/projects/Qn3oN8) and [production design interview](https://magazine.artstation.com/2016/02/scenes-concept-art-expanse/) informed dense thermal tiles, flush access panels and conventional rocket bells. New tile base color and registered tangent normal maps were generated with imagegen, then converted through texconv to 1024×1024 BC7 with mipmaps. No supplied photograph was pasted across a hull. Provenance and raw image hashes are in `surface-provenance.json`. Scalar ORM and mask textures are authored shader data. Native `base_color_factor` is verified in installed materials and the pinned shader; per-face planar UV tangents are calculated consistently with the new normal mapping.

The CPU previews show actual compiled color/geometry but do not render normal-map or specular effects; those require the user’s in-game test.

The final preview’s small speckles include real tile grain/fasteners and native Tachi orange drive flecks. Its nearest-neighbor CPU sampling exaggerates high-frequency texture detail; it does not use the final DDS mip chain. They are not all geometry defects or all preview artifacts. In-game filtering and material appearance remain untested.
