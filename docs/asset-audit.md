# Asset intake and derivative audit

The received package is glTF 2.0 JSON + external binary + PNG textures + `license.txt`. Its metadata names an upstream FBX, but **no FBX or Blender file is actually supplied**. The archive is preserved unchanged. See [source and permission record](../ASSET-SOURCES.md).

| Measurement | Source | Prepared derivative |
|---|---:|---:|
| Triangles | 140,863 | 14,622 |
| Named mesh parts | 355 | 355 retained in editable glTF |
| Nodes | 714 | Original hierarchy retained; normalized version adds one fit parent |
| Materials | 4 | 4 in compiled baseline |
| Source texture images | 10 × 4096² | Color/ORM/normal maps resized to 2048²; constant maps 4² |
| PDC barrel assemblies | 6 | 6 retained |
| Animations / skins | 0 / 0 | No deployment or skin animation added |

The SDK recommends a 12,500-polygon frigate maximum; this derivative is 17% over that recommendation and 89.62% below source triangle count. The user's updated preference allows a modest overrun. Treat the 14,622 figure as triangles, not an ambiguous Blender quad count. Actual large-fleet performance remains unknown.

## Structure and moving parts

`audit/asset-audit.json` records every node's name, parent, children, transform, material assignments, world bounds and triangle count. Source node 0 is `Sketchfab_model`; node 1 is the original FBX-name wrapper; node 2 is `RootNode`. Many named transforms have one mesh child; the PDC assemblies also have grouped subtrees. All source mesh nodes are in the active scene. glTF has no universal hidden-object flag here; no hidden objects were removed simply because they were not obvious in one view.

Distinct hull, engine, tank, piping, bay and gun pieces exist. PDC geometry accounts for 66,626 source triangles including bays/doors; other geometry accounts for 74,237. Each gun has separate body, barrels, holders, sphere, swivels, ammo box and details. Bay doors, shielding, pistons and hinges are separate. Six barrel mesh nodes:

| Index | Exact mesh node | Paired sphere node |
|---:|---|---:|
| 439 | `pdc_gun_barrels.002_PDC_0` | 445 |
| 487 | `pdc_gun_barrels.001_PDC_0` | 493 |
| 535 | `pdc_gun_barrels.003_PDC_0` | 541 |
| 583 | `pdc_gun_barrels.004_PDC_0` | 589 |
| 631 | `pdc_gun_barrels.006_PDC_0` | 637 |
| 679 | `pdc_gun_barrels.005_PDC_0` | 685 |

All six appear exposed in the source pose; the offline view shows deployed assemblies. There is no deployment animation to preserve. The source transforms are not certified engine pivots. `audit/pdc-rig-candidates.json` records sphere-origin pivot estimates, forward/up axes, cluster muzzle estimates and explicit per-node yaw/pitch partitions. Twelve editable candidate glTF files are under `assets/derived/pdc-rigs/`. They are **not yet game-mounted**. Remove exactly their moving parts from a separate combat hull before attaching rotating child meshes, or static duplicates will remain.

## Scale and coordinate conventions

Source world bounds: minimum `[-85.6892,-70.4472,-182.6169]`, maximum `[85.6893,70.2076,297.9347]`. Dimensions: approximately `171.38 × 140.65 × 480.55` source units. No reliable physical meter scale is provided. The named forward hull and aft main engine support a +Z-forward, +Y-up interpretation.

The derivative is uniformly scaled and centered to fit inside the vanilla Cobalt box and radius, without changing collision or navigation values. The final geometric radius is **57.846863**, below vanilla **58.548069**. The exact transform is generated in `audit/derivative-transform.json`.

Official MeshBuilder reflects glTF Z during import. The baseline compiler input compensates positions, normals, tangent handedness, triangle winding, and attachment coordinates. Generated JSON confirms nose/muzzles at +Z and exhaust at -Z. Editable source stays separate from this compiler-specific representation. Rig candidates need the same compiler conversion before final export.

## Geometry and texture work

Simplification uses pinned upstream meshoptimizer, individually per named part, with normals/UV weights and permissive seam collapse. No whole object or PDC is removed. The complete per-part input/output counts and error values are in `audit/optimization.json`. The source is never decimated or merged. Only the compiler input combines primitives by material to reduce draw overhead.

Source materials are `material`, `Primary`, `Secondary`, and alpha-blended `Texts`, all marked double-sided. The first three have color, packed AO/roughness/metallic, and normal textures. Primary's 0.8 roughness factor is baked into the derivative ORM green channel. Six planar text quads lack tangents; they receive analytic planar tangents and a flat normal texture. Other source tangents are retained through the coordinate transform. Their original MikkTSpace provenance is not certified; if normal-map artifacts appear, regenerate tangents on the simplified topology with a verified MikkTSpace exporter.

Game textures: BC7_UNORM color/ORM/mask, BC5_SNORM normals, mipmaps included. Normal conversion uses Texconv `--x2-bias` to map unsigned source channels to signed normals. Team color and emissive masks are initially zero; source painted colors and markings remain. Normal direction, alpha decals, backfaces, mip readability and shader appearance need review in Sins II. No custom shader was added.

Further optimization candidates include dense engine rings, repeated small pipes, tiny bolts and interior surfaces hidden behind hull panels. Their occlusion is not proven by this intake, so they have not been blindly deleted. UV rebaking and a separate distant LOD may improve quality per triangle after the first visual test.

`audit/geometry-comparison.png` is an offline diagnostic projection with face-sampled texture colors, not a full material render. Source-versus-derivative silhouette IoU is 97.89% top, 98.59% side, 98.51% oblique at the recorded preview resolution. This supports broad shape preservation in those views; it does not prove surface shading quality, every viewing angle, or in-game readability.

## Required mount/effect follow-up

- Baseline: one unchanged Cobalt autocannon uses two fixed muzzle estimates on the front port/starboard PDC clusters. Four other gun assemblies are cosmetic. No sixfold damage multiplication occurs.
- Rotating PDC phase: validate all six yaw origins, barrel pitch origins, local muzzle vectors, handedness and hull-obstructed arcs. The source gun ball is a candidate pivot, not a verified mechanism.
- Torpedo phase: the named torpedo bay exists, but exact launcher aperture coordinates and directions need editor inspection. No guessed firing ports are installed.
- Exhaust is centered at the aft envelope; inspect whether it emerges from the engine bell and adjust only its mesh point if needed.
- Shield shell, death effects, selection icons and voices remain vanilla. Damage/explosion surface data are generated by official MeshBuilder. Inspect for Cobalt-shaped shield flashes or badly placed effects before calling the visual work complete in-game.
