# Tycho: printed-core recovery and editable material study

The supplied archive contains five G-code print jobs and a four-page Printables
PDF. It does **not** contain the seven STL names advertised in that PDF, or any
original mesh/UV/texture data. The user confirmed this was the only available
download. The source website could not be accessed; no alternate original mesh
is claimed.

The two core halves were sliced with `support_material=0`. Their positive
extrusion segments were parsed as inert data, rasterized and joined into an
approximate solid surface. Printer commands were never executed. Supported
accessory jobs lack semantic support labels and were excluded. This avoids
claiming printer supports as real antenna/docking geometry.

Recovery uses 0.4 mm voxels at the original 25% print scale, 1.2 mm morphological
closing, enclosed-void fill, largest-component selection and mild smoothing.
The ring/hub core is recognizable, but print infill, facets and inferred assembly
remain visible. Missing accessories and original topology cannot be recovered by
this process. The two halves initially had 7,944,222 triangles; simplification
reduced them to 239,008. The final study removes 20 degenerate triangles and adds
480 triangles for 240 small light patches, totaling **239,468 triangles**.

The new materials are grey structural metal, dark machinery, ochre panels,
docking marks, warm habitat windows and cool work lights. They are artistic
additions, not recovered source paint. Light patches share two emissive
materials; there are zero dynamic light objects. Material zones follow source
coordinates. The editable derivative includes new UVs, but a full texture atlas
and game mask conversion are pending.

The SDK README documents game mask channels R=primary team color,
G=secondary team color, B=emissive strength, A=emissive hue strength, and ORM
R=occlusion/G=roughness/B=metalness. The current glTF uses standard emissive
factors only; this is not proof of equivalent Iron Engine emission. Keep these
channels separate when preparing the eventual compiled game asset.

## Local files

- Original: `assets/original/tycho18/tycho-station-from-the-expanse-print_files.zip`.
- Original PDF: `assets/original/tycho18/source-sheet.pdf`.
- Recovery intermediates: `assets/derived/tycho18-recovery-solid/`.
- Editable art: `assets/derived/tycho18-material-study/tycho18_reconstructed_core.gltf`
  and adjacent `.bin`.
- Actual geometry preview: `audit/update18-tycho-art/materials.png` and
  `materials-side.png`. These are CPU model renders, not game screenshots.
- Source/file hashes and limitations: `recovery.json`, `simplification.json`,
  `materials.json`, `tooling.json` in this audit folder.

Rebuild in order with `python3 tools/update18_tycho_recover.py`,
`python3 tools/update18_tycho_preview.py`, then
`python3 tools/update18_tycho_materials.py`. The recovery script alone prepends
the isolated `.tools/tycho18-packages` dependency directory; other existing
build dependencies were not upgraded. Editable art retains print-scale units,
not a verified lore/gameplay scale.

Visual inspection observed the joined circular core and ring, materials and
small light patches. **Not run:** MeshBuilder conversion, game transparency,
night-side/bloom, functional mounts, scale, ring rotation or multiplayer. This
art is not included in 0.18 Gate 1. The separate native-starbase mechanics
prototype continues to use a native placeholder until art/export is verified.

## Attribution

Derived from **Tycho Station from The Expanse** by **ewr2san**, Printables model
5439: https://www.printables.com/model/5439-tycho-station-from-the-expanse .
The included PDF identifies **Creative Commons Attribution-NonCommercial 4.0**:
https://creativecommons.org/licenses/by-nc/4.0/ . Preserve that attribution and
these change notes with a derivative. Source ZIP SHA-256:
`1f4ff63097207029b6a15cf2947b1ff426177d64d04827e618a36e39d29ba407`.
Changes: print-path reconstruction, inferred core assembly, simplification,
new UV/material zones and original light patches. No source website license
verification, public asset upload or publication occurred in this milestone.
