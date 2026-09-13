# Scirocco asset handoff — update 0.12

Status: **PASS OFFLINE ASSET HANDOFF. Runtime NOT RUN.**

Worker ownership is limited to `tools/update12_scirocco*.py`, this audit directory,
`assets/original/update12-scirocco`, `assets/derived/update12-b`, and
`build/update12-b` in the `tachi-one-pdc` worktree. Unit, skin, weapon, ability,
manifest, localization, fleet balance, installation and publication remain the
main integrator's responsibility.

## Selected outputs

- `build/update12-b/game`: four official binary meshes, six material definitions,
  and ten DDS textures. Copy as an overlay into the new experimental package.
- `build/update12-b/ui-final/generated`: six brushes, eighteen UI PNGs and two
  optional mod logos. Use this refreshed UI; `build/update12-b/ui` is the earlier
  pre-clearance-repair render and is retained only as an intermediate.
- `integration-spec.json`: all thirteen mounts and child mesh points, matching
  turret overrides and skin alias definitions, complete spatial bounds, ten
  torpedo ability origins, four drive origins, boarding origin and file hashes.
- `ui-integration-spec.json`: exact skin UI pointers to apply.
- `assets/derived/update12-b/expanse12_scirocco_editable.gltf` and its `.bin`:
  editable assembled scene. Individual compiler inputs and optimized parts are
  stored beside it. These are ignored local assets, not source-code Git content.

Selected game/UI bundle SHA-256:
`f19227c96266ff7fe04960aab51764981cab83ecb8533c06926a5941573489f9`.
The hash is SHA-256 of the sorted JSON mapping of game and UI relative filenames
to their SHA-256 values; it is not a ZIP hash. The main integrator identifies the
complete package separately.

## Geometry and mount interpretation

The supplied binary STL contains **677,402 triangles**, 159 connected components,
and no material, texture, UV, animation or named semantic hierarchy. The selected
assembled derivative has **89,519 triangles**: hull 75,447; rail 5,948; twelve
instances of the established 138-triangle base and 539-triangle barrel PDC.
The reduction respects error bounds; the rail exceeds its numeric target to
retain geometry within its stricter error bound.

Source +X becomes game +Z (bow), source +Z becomes game +Y (up), and source +Y
becomes game +X. This is a proper rotation with determinant +1, not a reflection.
Length is provisionally 456.52 game units using the existing Tachi scale of
105 units per 46 meters and a 200-meter Scirocco reference. The STL has no units;
the reference is an integration assumption, not source metadata.

| Equipment | Prepared interpretation |
| --- | --- |
| 12 PDCs | Existing complete Tachi biaxial assemblies at measured bow-side, ventral, behind-protrusion and engine-pod hull positions. New fixed sockets meet the measured hull. These are prototype retrofits, not twelve positively identified authored Scirocco PDC assemblies. |
| One railgun | Actual protruding source housing was clipped from fused component 89 along its measured support plane, with matching hull and rail caps. It is absent from the static hull. One-axis gimbal, yaw −15° to +15°, pitch 0°. Its source side is preserved; no claim that this STL matches a particular TV port/starboard layout. |
| Ten torpedo origins | Five light and five heavy prototype collars on measured forward hull surfaces. Each origin is beyond its collar. The division is implementation metadata, not authored tube labels or proof of canon loadout. |
| Four drives | Four distinct source engine bells (components 0–3), origins at actual aft outlet locations, forward vectors −Z. Main integrator supplies Epstein effects and scale. |
| Boarding | `weapon.boarding.0`, 20 game units outboard of a ray-measured hull surface; no moving hatch or source airlock identification claimed. |

Each PDC has one private weapon ID `expanse12_scirocco_pdc_0` through `_11` and
one base/barrel pair. The asset handoff does not allocate damage or duplicate
anti-ship and anti-torpedo weapon budgets.

The initial rail support clipped the hull when yawed: even ±2° failed sampled
clearance. The selected derivative lifts the original rail housing by 8.2 game
units from its cut plane, extends its fixed bearing back into the hull, and
retains its original shape. This is 8 units farther out than the rejected
0.2-unit initial mounting. Five poses over ±15° now pass the bounded check.
Earlier probe reports are diagnostic evidence, not selected-build pass claims.

The new plain gray/orange/dark materials are procedural because STL has no
textures. The orange sockets are new additions. Donor PDCs reuse the unchanged
Tachi material textures. UI uses the actual selected assembled derivative,
with simple preview shading; it is not a captured Sins renderer result.

## Verification actually completed

- Original download and preserved master SHA-256 still match
  `ea72a0b5cb4f57b23851335706f898fd45d9788f78ec06fa64ae272bee7ca64a`.
- Official pinned MeshBuilder produced all four binary and JSON meshes. Its
  winding was corrected in glTF index input and recompiled, retaining the
  compiler's grids and trailer. Tangent repair changes only tangent bytes and
  uses retained source frames, with zero tangent fallbacks.
- All four binaries have zero opposed winding triangles at the established
  −1e−5 tolerance. Hull/rail have zero near-ambiguous faces. The unchanged donor
  has the known three base and nine barrel near-perpendicular faces, twelve
  per gun; no relaxed hull/rail exception was introduced.
- Thirteen compiled mount positions and full frames match the integration
  metadata. Local-to-hull muzzle arithmetic is verified. Twelve fixed PDC
  sockets contain all five recorded surface samples.
- Rail clearance: 600 vertices at each of −15°, −7.5°, 0°, +7.5°, +15°, with zero
  contacts outside the intended bearing allowance. This is bounded sampling,
  not continuous collision detection or a guarantee of unobstructed firing.
- Ten collar supports and outgoing rays, four actual exhausts, and the external
  boarding origin passed checks. All compiled named points are present.
- All generated material texture references resolve locally. Material structure
  is checked against the established six-key profile; the pinned SDK does not
  provide a mesh-material schema.
- Six UI brushes pass the pinned brush schema; all twenty PNG files have the
  expected dimensions/alpha, and UI source hashes match the final editable mesh.
- `python3 tools/update12_scirocco_finish.py` verifies current binary/material/UI
  hashes, original preservation, frame agreement and the exact selected handoff.

## Reproduction and required ignored dependencies

Run from `/run/media/haker/NVME 2/expanse-workers/tachi-one-pdc` with Python 3,
NumPy, SciPy, Pillow and jsonschema. All required files must already exist:

- Original `/home/haker/Downloads/xxx_-_scirocco_whole.stl` and preserved copy.
- Main repository `/run/media/haker/NVME 2/expanse-mod`, especially `.tools/libmeshoptimizer.so`,
  `.tools/texconv.exe`, `tools/polish_ui.py`, and unchanged
  `build/experiments/expanse_donnager10_pdc_audio` donor material/texture files.
- This worktree's `tools/common.py`, `audit/polish-b/mount-metadata.json`,
  `assets/derived/polish-b/expanse_polish_pdc_0_{base,barrel}.gltf` plus their binary
  buffers, and `build/polish-b/proton-prefix` if a new Wine prefix is needed.
- UI helper `/run/media/haker/NVME 2/expanse-workers/validation/tools/polish_ui.py`.
- Installed read-only `.../SteamLibrary/steamapps/common/Sins2` and matching
  `Sins of a Solar Empire II - Mod Tools` (pinned SDK revision
  `8e061033afe53b1393eaefd56617a3fd041eeb5f`).
- Proton Wine at `/home/haker/.var/app/com.valvesoftware.Steam/.local/share/Steam/steamapps/common/Proton 10.0/files/bin/wine64`.

The source scripts form the sequence intake → features → geometry → compile →
mount_checks → UI → finish. Do not rerun intake/optimization just to validate the
existing handoff. Compiler output is separate from its source, and the original
STL is never edited. Wine may require host synchronization permission.

For a new UI render, `update12_scirocco_ui.py` takes `--source`,
`--expected-triangles 89519`, `--game`, `--sdk`, and a fresh `--output` directory.
It refuses to overwrite an existing UI output. The selected source is
`assets/derived/update12-b/expanse12_scirocco_editable.gltf` without `--compiler-z`.
Missing files are errors; none are downloaded or substituted.

## Permission and next runtime gates

Creator, source URL and exact STL license were not supplied. The record states
only that the user supplied this file and requested local conversion. No creator,
license or additional permission document has been invented. Preserve this record
and keep original/model derivatives outside a source-only Git push.

Next workstation test: load and build the integrated ship; inspect its hull,
socket contact and four plumes; move/select/save/reload; observe each PDC's
tracking, both target categories and muzzle alignment; observe the rail at both
arc extremes and check hull obstruction; launch from all ten tube origins;
exercise boarding; then test a formation for performance. No rotation, firing,
interception, scale readability or performance test has been run in game here.
