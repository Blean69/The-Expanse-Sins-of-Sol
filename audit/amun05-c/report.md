# Amun-Ra 0.5 asset intake and isolated torpedo — Worker C

The actual supplied archive contains a usable, independently authored torpedo subtree. It is now isolated in an editable glTF and uniformly matched to the approved installed Javelis torpedo length. No projectile unit, health, damage, movement, ammo or interception definition was edited. No full-ship conversion, game compilation, installation or runtime test occurred.

## Source and permission

Supplied archive: `/home/haker/Downloads/Amun-Ra_Class_Stealth_Ship_[The_Expanse].zip`, 33,081,566 bytes. SHA256 `fa0d7ee158c53ee1e07d362eb1cfc49ab08fe3da9f5b11c2cd414c7c50d71441`.

The archive and all seven extracted files are preserved byte-for-byte under this worker's `assets/derived/amun05-c/original/` and `master/`. The archive contains no license or attribution document. glTF metadata identifies OpenSceneGraph3.5.6 as exporter, but does not identify a creator, public source URL or license. **Permission is recorded as user-attested**, as authorized by the main integrator; no additional permission request was made and no license was inferred. This record is distinct from the CC-BY records belonging to the Tachi and Donnager. See `asset-source-and-permission.json`. No distribution was performed.

## Measured inventory

| Item | Actual source |
| --- | --- |
| Active nodes / total nodes | 965 / 965 |
| Meshes | 382 |
| Whole posed scene triangles | 102,371 |
| Main central hull | 23,556 triangles |
| Material | One shared atlas material |
| Textures | Four 4096×4096 RGBA PNGs |
| Torpedo instances | Four, 1,600 triangles each |
| Complete PDC assemblies | **Four**, 1,230 triangles each |
| Breaching-pod assemblies | Fifteen, 4,481 triangles each |
| Animations / skins | Zero / zero |

The scene includes detached/posed equipment, so its full bounds do not establish hull size. The central hull alone spans23.3760×61.3621×19.9704 in its authored local frame, with the long axis alongY. A presentation transform and100x FBX conversion exist above it. No physical meters or final ship scale is inferred.

The shared material's actual texture mapping is baseColorTexture0→images0 Base_Color; metallicRoughnessTexture3→images1 Metallic; emissiveTexture1→images3 Emissive; normalTexture2→images2 Normal_DirectX. Filename order is not texture-index order. All texture references resolve. Preserve this mapping when preparing game shader channels. The supplied maps are not already Sins DDS materials; verify packed channels and normal-Y convention instead of assuming the DirectX-named source is ready for glTF or game shader use.

`inventory.json` contains every node, root transform, named subtree, per-mesh counts and attribute sets, exact material/texture mapping and image sizes/hashes. The source format is glTF JSON + external BIN, PNG atlases and one JPEG background. No editable FBX/Blender document is supplied; an FBX name exists only as a node label.

## Torpedo extraction

The four roots are node102 `Torpedo_LP.004`,107 `.005`,112 `.006`,117 `.007`. Their geometry, indices, normals, tangents and UV arrays match exactly. First instance node102 contains mesh nodes105/106 (source mesh IDs38/39). Both complete mesh chunks are retained; nothing was guessed from a spatial slice or reconstructed.

The complete ancestor and instance transform is removed to recover the authored torpedo local frame. Its bounds are approximately[-0.645543,-0.645543,-5.610510] to[0.645527,0.645531,7.068424]. The +Z end is the red narrow nose visible in the actual source render. Local length is12.67893362; the uniform factor is1.3022196104. The centered output is **1.681256×1.681261×16.510756 game units**.

Size reference is the read-only installed `/run/media/haker/NVME 2/SteamLibrary/steamapps/common/Sins2/meshes/trader_medium_torpedo.mesh`; its full Z box length is16.51075554 and recorded sphere radius8.27425861. The candidate matches approved length while preserving its own width/shape. Its centered maximum vertex radius is8.28733873, about0.01308 (0.16%) greater than the stock sphere despite matching length; the existing sphere must not be assumed to enclose every custom vertex. The compiler should calculate private mesh bounds and main should explicitly decide spatial collision radius separately from unchanged health. It does not copy vanilla projectile health or automatically reuse stock collision bounds. Main owns any private unit/skin references and derived bounds decisions.

Editable candidate:

`/run/media/haker/NVME 2/expanse-workers/validation/assets/derived/amun05-c/torpedo-editable/amun05_torpedo.gltf`

Required adjacent dependencies are `amun05_torpedo.bin` and all four original `images/*.png` files. Exact absolute paths and hashes are in `torpedo-extraction.json`. All four atlases are copied unchanged so the original UVs remain meaningful; this is deliberately not an atlas-repacking or texture-reduction pass. A later game material can use a smaller baked atlas after visual comparison.

The candidate remains **right-handed glTF**. No official compiler Z reflection, winding adjustment, tangent conversion or game material export has been applied. Use the established pipeline once, not an assumed second conversion. Conversion should introduce private mesh/material/skin references and preserve the approved MCRN torpedo entity's statistics. Preview images show actual UV-sampled source colors with the existing static studio-light lift; they are not in-game render tests.

## PDC and breaching-pod findings

The archive contains four complete geometric PDC assemblies, not three:

- Node892 `Turret_Pad_LP.001`: base895, barrel-base900, barrel905.
- Node910 `Turret_Pad_LP.002`: base913, barrel-base918, barrel923.
- Node928 `Turret_Pad_LP.003`: base931, barrel-base936, barrel941.
- Node946 `Turret_Pad_LP.004`: base949, barrel-base954, barrel959.

Each includes the pad and separate base/barrel-base/barrel subtrees with mesh geometry and authored rest transforms. No assembly was discarded to match the expected count. This is promising for later articulation, but authored transforms do not prove correct game yaw/pitch axes, muzzle centers, tracking arcs or firing. Those measurements and runtime checks are outside this intake. `equipment.json` preserves their complete descendant IDs, rest transforms and geometric bounds.

Fifteen explicit `Breaching_Pod_LP` subtrees include the pod shell, three clamp-leg root/mid/clamp chains and a charge object. Some are in different poses or detached from the hull; pod020 has a visibly detached charge component in its source pose. There are no deployment/boarding animation channels, capture mechanics or carrier definitions in the archive. These are available source objects, not implemented boarding gameplay.

## Outputs, checks and reproduction

Owned new paths only:

- `tools/amun05_intake.py`, `tools/amun05_validate.py`.
- `assets/derived/amun05-c/`: preserved archive/master and compact torpedo derivative.
- `audit/amun05-c/`: inventory, equipment report, permission record, extraction metadata, checks and source-rendered previews.
- `build/amun05-c/source-and-output-hashes.json`: final source/helper/asset/audit provenance.

From this isolated worker checkout:

```sh
python3 tools/amun05_intake.py --archive '/home/haker/Downloads/Amun-Ra_Class_Stealth_Ship_[The_Expanse].zip' --target-length 16.510756
python3 tools/amun05_validate.py
```

Local dependencies are existing numpy/Pillow and read-only `tools/common.py`/`tools/polish_ui.py`, the actual archive and installed Javelis mesh. No dependency updates/downloads are required. A missing required file raises a diagnostic with its path; dependency checks are not represented as passed if inputs are absent.

Actually run and passed: ZIP CRC and preserved source hashes; all active source indices/finite positions; four torpedo instances' exact attribute comparison; extracted two-mesh triangle count; exact retained indices/normals/tangents/UVs; uniform position transform/centering; approved size match; local normal lengths; texture-reference and byte-identical atlas checks; Python compilation. The torpedo oblique/side and representative PDC/pod renders were visually inspected.

Game shader conversion, compiler validation, exhaust attachment placement, collision selection and runtime rendering/interception remain **NOT RUN**. No `.unit`, `.unit_skin`, weapon, manifest or gameplay file is part of this worker output. Previous Donnager paths remain untouched.
