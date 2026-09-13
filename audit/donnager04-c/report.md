# Donnager 0.4 intake and geometry preparation — Worker C

The actual supplied archive is preserved and audited. This milestone produces editable, high-poly planning assets, not an installable Donnager. No game export, installation, game launch, runtime test, dependency update or publication occurred. The existing Tachi/Rocinante assets, installed game and SDK were read only.

## Source and permission record

`/home/haker/Downloads/mcrn_donnager_the_expanse.zip` is 43,359,119 bytes. SHA256: `b03d70d6180b7c6ff50db22df883f576ebb3981c5d4d138f8bdf1e7434079562`.

The archive's `license.txt` and glTF metadata identify **MCRN Donnager (The Expanse)** by **owlstraw**, profile `https://sketchfab.com/strawfinch`, model `https://sketchfab.com/3d-models/mcrn-donnager-the-expanse-05e9f9006d914fcd96e95fbd452aaa28`, license **CC-BY-4.0**. The packaged attribution text is preserved in `asset-source-and-permission.json` and the unchanged master. It records creator credit and commercial use allowed; no additional creator correspondence is claimed. Retain the packaged credit and license link and identify derivative changes if these assets are later shared. Nothing was distributed here.

The prospective PDC donor is the existing Jakub.Vildomec Tachi derivative, separately credited/licensed under its existing CC-BY-4.0 record. No donor geometry has yet been spliced into the Donnager. A future combined derivative needs both asset records; the Donnager credit cannot replace the Tachi credit.

## Actual inventory

| Item | Measured result |
| --- | --- |
| Source triangles | 1,804,024 |
| Meshes / nodes / materials | 61 / 67 / 11 |
| Engine group | 873,680 triangles |
| Body group | 803,481 triangles |
| Railguns group | 126,863 triangles |
| Animations / skins | 0 / 0 |
| Images | Two 2048×2048 RGB JPEG base-color textures |
| Source formats supplied | glTF2.0 JSON, external BIN, JPEG, license text |
| FBX / Blender source | Not supplied; `DonnyFBX.fbx` is only a hierarchy label |

All 67 nodes are reachable from the selected scene. Every primitive has positions, normals and one UV set; no tangents are supplied. All 11 materials declare `doubleSided:true`. Nine materials use factors/emission or share the gray texture; the two provided images are `GreyHull_baseColor.jpeg` and `OrangeHull_baseColor.jpeg`. No normal/ORM/mask game textures are supplied. `asset-inventory.json` records complete material definitions, per-node transforms, vertex/triangle counts, image sizes/hashes and bounds.

The source-world bounds are X[-225.377559,225.377465], Y[-182.657677,268.097240], Z[-317.235550,866.665222], dimensions450.755024×450.754917×1183.900772. Center is approximately[0,42.719781,274.714836]. The positiveZ end is forward, supported by forward rail barrels and negativeZ engine-emission geometry. +Y follows the evaluated glTF convention; assigning canonical dorsal/ventral to a nearly roll-symmetric hull still needs reference review. The FBX-related100x matrices do not establish exporter units as meters.

No dedicated PDC objects, turret pivots, bones or animation channels were found. The views show no clearly separated usable PDC assemblies. This is not proof that every minor surface detail has been identified. No hidden/inactive node was found; enclosed/interior triangles have not been classified by a visibility test. Zero degenerate triangles at the recorded world-space tolerance is a geometry check, not an outward-normal/culling guarantee.

## Editable assets and scale

All paths below are within `/run/media/haker/NVME 2/expanse-workers/validation/assets/derived/donnager04-c/`:

- `original/mcrn_donnager_the_expanse.zip`: identical preserved archive.
- `master/`: extracted files, byte-identical to archive members.
- `normalized-preview/donnager04_centered.gltf`: one added parent transform centers the complete source and normalizes length to100 arbitrary units. Original mesh data, UVs, materials, hierarchy and geometry are retained; no optimization.
- `normalized-preview/donnager04_provisional_475p5m.gltf`: separate parent transform using the integrator's provisional475.5m Donnager /46m Tachi convention. This is a secondary lore convention, not calibrated exporter meters or primary-verified screen scale.
- `rail-assembly-preview/donnager04_rail_negative_X.gltf` and `donnager04_rail_positive_X.gltf`: two complete source rail assemblies, still high-poly and unrigged, with estimated drum-centered parent transforms. Each retains material assignments, normals and UVs. Texture paths resolve into the neighboring normalized-preview folder, so keep that folder when moving these candidates.

The existing normalized Tachi is104.986959 game units long. Applying475.5/46 gives a10.336957 hull-length ratio and Donnager dimensions413.193343×413.193246×1085.245626 game units. Installed Kol mesh dimensions are173.715698×209.445862×837.127563; Sova262.717316×167.765549×826.640198. These are measured mesh boxes, not navigation radii or canonical meters. Correct ship scale still requires a workstation comparison of visual framing, collision, formation spacing, selection and build presentation. `provisional-scale-comparison.png` shows the actual source silhouettes under this convention.

These editable scenes use normal right-handed glTF coordinates. They have **not** received the established official compiler Z-reflection/winding preparation or been converted to game meshes. Do not feed a second inconsistent axis conversion into a future pipeline.

## Railgun preparation and hardpoints

The four `Railguns` child meshes are material/export chunks, not separate authored gun components. Welding positions to0.0001 exporter units reveals 874 connected components because fine details are disconnected. Treating every connected component as a moving turret part would be incorrect.

A whole-assembly split by sign of evaluated source-worldX partitions every rail triangle exactly: negativeX 63,432; positiveX 63,431. Nothing crosses the centerplane. Each assembly is24.240863×40.382358×215.666117 exporter units. This split is implemented in the editable candidates; it does not identify fixed cradles versus moving barrels.

The symmetric main drum's measured bounds suggest centers[-117.54735,42.7197,487.5269] and[117.54735,42.7198,487.5269] in source world coordinates. CircularXZ cross-section and axialY span suggest a possible Y-axis rotation. These are clearly labeled geometric estimates, **not valid game mounts or verified pivots**. A limited sweep, fixed-versus-moving separation, hull collision clearance, bore-center muzzle and weapon arc remain unresolved. No guessed `muzzle_positions` or rotation limits were emitted. Rotating the source's common `Railguns` parent would rotate both guns around its shared origin and is unsuitable.

`donnager-planning-view.png` marks the measured drums on actual projected source geometry; `railguns-isolated-view.png` shows both complete assemblies. Previews use source material averages and a CPU triangle painter with a subpixel raster cutoff; they are not UV-accurate game renders or hidden-geometry tests.

## Donor PDC scale and optimization budget

The existing PDC 0 donor comprises 138 base +539 barrel triangles = 677 per physical assembly. After the known compiler-input Z reflection is reversed and the recorded barrel offset is applied, its combined local dimensions are4.860631×3.655473×6.531393 game units. Under the provisional46m Tachi convention, that is2.129684×1.601644×2.861728m. Keeping donor scale1.0 at the same game-units-per-meter preserves physical gun size; do not enlarge each PDC by the 10.336957 capital/corvette hull ratio.

No full PDC network count or coordinates were guessed. Resolve visible locations, sectors, paired coverage and rail sweep before placing mounts. Parent research reports a59-versus43 discrepancy; this intake does not settle it.

The installed pinned SDK `README.md:58–67` says final Capital Ship assets should not exceed75,000 polys (Frigate12,500; Cruiser25,000; Titan225,000), with typical assets below those limits. Current triangles are24.05× the capital figure; the railguns alone exceed it. Installed Kol 53,790 and Sova 62,647 triangles provide practical references. For budget illustration only: 43 donor PDCs cost 29,111 triangles, leaving 45,889 under 75k; 59 cost 39,943, leaving 35,057 for hull and rails. The count is not established, so neither is a proposed network.

A later optimization pass should preserve the distinctive four-engine silhouette, forward hull, rail drums/barrels and readable markings while replacing dense engine/mechanical microdetail and repeated tiny rail parts with low-poly surfaces/baked maps. First identify interior/enclosed geometry and material/UV borders; do not blindly remove geometry or trust double-sided rendering to hide normal errors. Reduce rails independently of hull and budget articulated PDCs before final mesh conversion. No optimization was performed in this bounded intake.

## Reproduction and verification

From this isolated worker checkout:

```sh
python3 tools/donnager04_intake.py --archive /home/haker/Downloads/mcrn_donnager_the_expanse.zip --preview-length 100 --donnager-meters 475.5 --tachi-meters 46
python3 tools/donnager04_validate.py
```


Required local dependencies: existing Python numpy/Pillow/scipy, unchanged `tools/common.py`, actual supplied archive, the existing Tachi normalized scene/buffer in the main project, PDC 0 base/barrel glTF/buffers plus mount metadata in worker B's `assets/derived/polish-b` and `audit/polish-b`, and installed game meshes. Missing dependencies fail with a clear path; no substitute download or reconstruction occurs. SDK/game versions were not updated. README is a local SDK snapshot rather than a Git worktree; the provenance records its SHA256.

Actually run: intake including archive CRC and preserved-byte checks; all source triangle indices/finite coordinates; normalized triangle-count and length preservation; whole-rail partition and reloaded bounds checks; five glTF scenes' local-normal, buffer and image references; unchanged donor hashes; Python compilation; visual inspection of the planning, isolated-rail and scale views. These passed. `offline-checks.json`, `derivative-validation.json` and `build/donnager04-c/source-and-output-hashes.json` record results/provenance.

Game shader/material conversion, final mesh export, full PDC placement, functional rail rotation, carrier mechanics and all runtime gates remain **NOT RUN / NOT IMPLEMENTED here**. Worker A owns installed carrier-mechanics research; main integrator owns its documentation and any subsequent ship definitions. No Donnager package is eligible for installation yet.
