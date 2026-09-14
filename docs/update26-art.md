# Update26 orbital platform and Murphy art

Foehammer now sits on a circular service ring with an open recoil cradle, connected radial braces, two supported PDC outriggers, and machinery/radiator modules underneath. The rectangular foundation block is removed. Murphy gets steel/navy armor, recessed panel details, small hazard marks, and varied metallic/roughness maps. Its hull, large blue drive, and four PDC rigs are retained exactly.

## Integration contract

Source package (read only): `/run/media/haker/NVME 2/expanse-mod/build/experiments/expanse_update25`.

Compiled output: `/run/media/haker/NVME 2/expanse-workers20/assets/build/update26-art/game`.

Copy only the 25 regular files listed in `audit/update26-platform/combined-art-manifest.json`. The manifest distinguishes replacements from new dependencies and gives SHA-256 for every file. It includes one replacement platform mesh, four new platform material bindings with native/base texture dependencies, two replacement Murphy material bindings, and six new Murphy DDS maps. No entity, weapon, skin, particle, research, or player file is included.

The platform keeps mesh ID `expanse22_foehammer_support`, all six existing meshpoint transforms, and the existing skin bindings. Its rail/PDC meshes and weapon definitions are not modified. Murphy requires no skin or spatial changes.

The main integrator should extend Foehammer's `unit.spatial.box` to fit its deeper service ring. Measured assembled rest-pose bounds are center `[0, -30.5574359131, 36.0456577093]`, extents `[74.3321652212, 49.0093554688, 112.1525234431]`. Retain at least the accepted radius `119.9317921146` (measured new rest-pose radius is `118.6148653921`) and `can_be_displaced_on_collision=false`. These are art bounds, not a reason to alter weapon range, movement, costs, construction time, arcs, or tracking. No shared definitions were edited by this worker.

## Geometry and source provenance

The platform uses native installed mesh donors, with exact file hashes and transforms in `audit/update26-platform/integration-spec.json`:

| Part | Triangles | Placement |
| --- | ---: | --- |
| TEC research habitat ring | 2,382 | Scale 0.31; rotate X 90°; translate `[0,-58,-22]` |
| TEC capital factory left component, twice | 23,764 | Scale 0.08; translate `[±33,-72,-13]`; port rotated Y 180° |
| Authored connected tubular frame | 1,824 | Central recoil column, radial braces, landing legs and PDC sockets |
| Support subtotal | 27,970 | Replaces the old support only |
| Unchanged Foehammer rail | 8,519 | Exact accepted donor pose |
| Two unchanged PDCs | 1,354 | Exact accepted donor poses |
| Assembled total | 37,843 | No donor decimation |

Donor positions are centered once on each native component's bounding box, then uniformly scaled. Original per-vertex normals, UVs and tangent frames are preserved through the transform. The official installed MeshBuilder generates the binary and triangle-facing grid. The helper verifies winding and source frames, repairs only tangent bytes when needed, and verifies the official grid/trailer remains untouched. The support has zero opposed-winding triangles after compilation.

The central column now has actual radial connections into the ring. Each recoil leg lands on a ray-verified ring surface; its upper end lies inside the central column radius. New support stays inside X ±70.9, while existing PDC pivots remain at X ±71. The rail remains at its accepted pose above the support (18.4 units of vertical fire-path clearance). Existing rail `pitch_speed=0`, narrow yaw limits and elevation limitations remain intentional; this art revision cannot improve target acquisition.

## Murphy materials

The existing 9,454-triangle hull has no opposed-winding faces. No geometry rebuild, artificial subdivision, normal averaging, nozzle edit, or drive rescaling was necessary.

Armor roughness spans 78–151/255 and metallic 75–195/255; dark machinery roughness spans 113–157/255 and metallic is 205/255. Navy paint is deliberately rougher and less metallic than exposed steel. Recessed seams and fasteners add restrained normal detail (maximum tilt below 4.8°). Existing nozzle material, masks, emissive behavior and the large plume remain unchanged. Text that bled across shared UV projections was removed during preview review.

Color and ORM maps are mipmapped BC7_UNORM. Normal maps are mipmapped signed BC5 (`BC5S` legacy header, equivalent DXGI BC5_SNORM). New bindings preserve all other accepted material fields.

## Observed validation

- Official mesh compilation and DDS conversion completed with the already installed local SDK/Wine tools; no installation or game launch.
- All six platform meshpoints match the accepted translations and rotations within 0.00002.
- 2,628 sampled PDC yaw/pitch directions clear the new support; minimum muzzle clearance from its outward plane is 1.883768 units.
- Rail fire-path height, ring landing contacts, source frame fidelity, triangle winding, and unchanged source hashes passed.
- Every packaged file matches the manifest, all material textures resolve, no symlinks are packaged, and color/ORM alpha remains opaque.
- Both compiled platform views and both Murphy views were visually inspected. The previews use actual compiled geometry and DDS color maps; they are offline renders.

Not observed: engine metallic/roughness/normal shading, live turret interpolation/target acquisition, selection bounds in game, save/reload, multiplayer, or plume rendering. Existing drive bytes are preserved; this is not a new live plume test.

## Rebuild

Use the project's existing Python environment. In this isolated worktree, run platform `prepare`, `compile`, `preview`; Murphy `prepare`, `compile`, `preview`; then `tools/update26_platform_validate.py`. The compile stages use existing local Wine IPC and may need the existing sandbox escalation. Never copy a Wine prefix into the asset output.

Previews: `audit/update26-platform/compiled-orbital-preview.png`, `compiled-orbital-reverse-preview.png`; `audit/update26-murphy/compiled-material-bow-preview.png`, `compiled-material-aft-preview.png`.
