# Geometry 0.3 handoff — Worker B

Outputs are frozen candidates for main integration. No game was launched, installed package changed, or runtime test claimed here. The user observed the preceding corvette version tracking and firing; those observations do not validate these new supports, backing surfaces, hero source, or hardpoints.

## Corvette

`mount-metadata.json` and `output-validation.json` are the integration inputs. The thirteen final meshes are under `build/geometry03-b/corvette/game/meshes`. `assets/derived/geometry03-b/corvette/expanse03_editable.gltf` retains six independent yaw/pitch hierarchies. Mount origins, axes, offsets, and weapon muzzle coordinates remain identical to the previous polish candidate.

The new geometry adds fixed sockets, yaw pedestals, side yokes and pitch pins to physically join the assemblies to the hull. Supports add 912 triangles. It adds 801 inward backing triangles only to seven identified open thin shells: source nodes18,22,78,110,192,410,412. The source materials declared these shells double-sided. Primary hull textures are opaque; an alpha-only explanation did not fit the source data. This is a targeted shell derivative, not a blanket duplication of the ship. Total is 16,335 triangles: hull11,553, six bases226 each and six barrels571 each. Original silhouette geometry and texture coordinates remain present; no new optimization was run on this corvette.

Support surfaces sample the original material0 texture at UV[0.4906005859375,0.4942626953125], verified dark RGB[32,33,35] and flat normal[128,127,255]. Existing material maps are reused. Main remaps each actual compiler material ID listed in output-validation to the corresponding existing Tachi material definition.

`torpedo-mounts.json` gives dorsal/ventral bay front-plane centers and orthonormal directions from named bay nodes22/192/194/196/198/200. These are closed hatch surfaces, not verified open launcher throats. Test release/ignition clearance at these points. `six-pdc-mounts.png` and `torpedo-bay-inspection.png` document source placement.

## Supplied hero intake and permission

The untouched archive SHA256 is `2fef806f80c65f138eed9b877c6cd1ae98f12e597856b96cfb1c6676a16af3e6`; it contains glTF, binary and one background JPEG. Creator, source URL, exact license and attribution terms were absent. The user explicitly attested permission to use the asset. This is recorded as user-attested permission, without inventing license terms or publishing derivatives.

`hero-asset-audit.json` records source/master hashes, all animation tracks and per-part simplification counts. Original432,680 triangles; stand subtree65..68 contains6,068; stand-free426,612. There are163 original mesh nodes and161 retained ship mesh nodes. Only the stand is omitted. The background JPEG is not referenced as a hull texture. Source has four flat-color materials and no UV image textures; the black stand material is not needed by the ship.

The archive has one actual 351-channel,16.625-second animation. Relative-to-hull measurements confirm mechanical movement: cannon components rotate approximately30°, cover90°, and sliding parts translate. The common presentation motion is removed before sampling the deployed end pose. Stand-free animated and high-resolution deployed editable variants are preserved separately. This establishes source animation exists; it does not establish Sins deployment or runtime turret animation support.

Existing pinned meshoptimizer library/source bba256eaa24039b6f93c773063ff7c20143ae0db simplifies each retained named part with attributes preserved, yielding26,707 triangles. All161 source ship meshes retain geometry. Source archive and master are not decimated. The deployed ship is normalized using its longitudinal principal axis, projected source up, and95% of installed Cobalt bounds. The axis removes the display-stand pose tilt. This is a heavier hero candidate, not a fleet-wide budget recommendation.

Three flat source colors/roughness/metalness factors become tiny constant CLR/ORM/NRM/MSK maps. Normal maps use BC5_SNORM; the others BC7_UNORM. Twelve DDS files and three private material definitions are supplied. The source has no authored panel image maps, so none are invented.

## Hero hardpoints and custom armed derivative

`hero-equipment-mounts.json` measures actual source cannon1 barrel-cap planes, not cannon2 trunnion blocks. Isolated part views document the distinction. Each muzzle uses210 unique vertices at the authored cap plane; center is computed from full cap bounds in that plane, plus0.04 outward clearance. Six independent points are named `weapon.pdc.0`..`weapon.pdc.5` in the armed mesh. They are static deployed guns. No rotating hero turret rig is included. Source gun3 points aft in this baked pose; do not silently reorient only its tracer. Runtime firing eligibility/arcs must agree with static barrel directions.

The exhaust is fitted from the entire nozzle circumference in its authored axial plane. A minimum game-Z slice was rejected because it picked one rim edge. The corrected fit uses152 unique rim points,64 inner-circle points, maximum radial residual0.00622, opening center about[0.32729,-10.40216,-49.22762], outward axis[0.00593774,-0.00979545,-0.99993439]. Emission point adds0.1 outward clearance. Actual up/forward basis is recorded and compiled; its0.66° tilt must not be replaced by an arbitrary aft-Z direction.

The supplied model did not identify a railgun or torpedo launcher by name. With main/user authorization, the separate armed derivative adds clearly custom prototype fittings: an open-bore keel railgun with two hull pylons, plus dorsal and ventral launch fittings placed against measured local hero hull surfaces. These are not claims of TV-accurate original equipment. They add228 triangles, giving26,935 total. Metadata supplies exact `weapon.rail.0`, two launch positions and full bases. The static source-only variant remains separate.

Main integration inputs: `hero-armed-mount-metadata.json`, `hero-armed-equipment.json`, `hero-armed-output-validation.json`, `hero-armed-resources.json`. Complete generated files are under `build/geometry03-b/hero-armed/game/{meshes,mesh_materials,textures}`. Source-only static game mesh is under `build/geometry03-b/hero/game`. Both have normalized editable glTF/bin files under their respective asset directories; compiler inputs retain explicit Z compensation and must not be mistaken for editable game-coordinate sources.

## Offline validation actually run

All13 corvette meshes and both hero variants were compiled separately to JSON and binary with the pinned official MeshBuilder, with official triangle facing grids regenerated after source winding corrections. A bounded tangent-field-only repair uses retained authored frames projected against normals. Exact16-byte tangent writes are checked: all other binary bytes and official facing trailer remain identical. JSON/binary parity, finite/unit/orthogonal tangent frames, non-opposed face winding, source position conservation, triangle counts, meshpoint positions and strict stock-game right/up/forward matrix rows pass. No tangent fallback was required. Position errors: corvette≤2.5053e-6; hero≤2.0487e-6 game units. Strict hero checks cover six PDCs plus exhaust and rail where applicable.

Winding records are `corvette-winding-correction.json`, `hero-winding-correction.json`, `hero-armed-winding-correction.json`. The generic `winding-correction.json` was overwritten by an early hero helper and is obsolete. Corvette per-primitive counts were recovered exactly by generating raw inputs in isolated scratch and comparing each final triangle; no final corvette output was changed. Use only the variant-specific records.

Final source/archive preservation and output SHA256s are recorded in `final-provenance.json`. Existing baseline, earlier polish, and source assets were read-only throughout. Master preservation is verified by hashes rather than assumed. Source scripts remain uncommitted in the isolated worker worktree at9e40dd4b42853318ef87cc3d7d858f2abf601176; the final provenance hashes identify the actual changed scripts.

## Reproduction and runtime gates

Scripts are under `tools/geometry03*.py`; run from this worker worktree with OPENBLAS_NUM_THREADS=1. Read-only ignored dependencies are the main project normalized source/polish compiler input, installed game/SDK, existing meshoptimizer/texconv, and copied hero master. Compile/winding scripts require explicit --sdk and --wine and use their own output Wine prefixes. The ordering is corvette generate→compile→winding→finish→editable; hero intake/optimize→measure mounts→compile→winding→finish→textures→armed generate→armed compile→armed winding→armed finish→resources→editable. Do not automatically run these against installed packages or shared prefixes. Missing dependencies must fail, never trigger replacement downloads.

Next visual tests: inspect hull from all sides at near/medium zoom, turn six corvette turrets through full permitted arcs and watch support contact/overlap, inspect normal-map seams and backed shell interiors, then fire torpedoes from both corvette hatch points. Test the hero separately: no stand, deployed six guns, directional muzzle alignment (especially aft gun3), actual tilted centered exhaust, custom rail bore and both custom launch ports. Hero deployment and gun rotation are not implemented. Hero closed/thin source surfaces, sustained performance, weapon eligibility, interception priority, and all new saves/runtime behavior remain unverified here.
