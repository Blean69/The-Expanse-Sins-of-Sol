# Behemoth / Nauvoo private art prototype

The supplied archive is usable. All **24,046 original triangles** are retained;
640 small fitting triangles and eight accepted 677-triangle PDC assemblies bring
the assembled neutral pose to **30,102 triangles**. No decimation, stand removal,
voxel reconstruction, hull deformation, or invented interior was needed.

Generated files are in this worker checkout's `build/update24-behemoth`:

- `game/`: compiled hull and exact donor PDC aliases, DDS material sets, blue
  engine effects; deliberately no unit definitions or manifests.
- `source/expanse24_behemoth_editable.gltf`: textured editable hull plus named
  attachment points. Turrets remain separate native child meshes at runtime.
- `behemoth-oblique.png`, `behemoth-side.png`, `behemoth-aft.png`: assembled
  orthographic previews, including donor gun geometry. Preview shading is not
  evidence of game rendering or runtime emission.
- `integration-spec.json` in this audit folder: exact source hashes, measured
  scale, attachments, donor pivot/muzzle contract, file hashes and offline checks.

Reproduction: run `tools/update24_behemoth_geometry.py`, then
`tools/update24_behemoth_compile.py` with the established project dependency
Python. The latter uses the pinned MeshBuilder and texconv through the existing
Wine prefix in place; it never installs a package or copies a Wine prefix.

Scale uses **104.987 / 46 game units per metre**, matching Tachi, and a rounded
2,000-metre design length. The original aspect ratio is preserved, yielding an
approximately 781-metre maximum width. The width is this model's interpretation;
it is not asserted to be the canonical drum diameter. Bow is +Z; all eight
authored nozzle mouth centers are measured at the opposite end. Nozzle radius
is approximately 81.7 game units. Static drum and simplified engine geometry
remain source limitations; there are no missing STL sections in this download.

Eight small PDCs are mounted on measured fore/aft collar surfaces. Their count
and two forward cosmetic torpedo ports are restrained retrofit design choices,
not a claim about TV or book weapon totals. Donor PDC scale, base/barrel bytes,
pivot and muzzle data are preserved. Materials are authored opaque charcoal
industrial panel maps, subdued ochre repair bands and emissive running lights.
Flat BC5 normals avoid adding false bumps; full mip chains accompany BC7 color,
ORM and mask maps. This is not a projection of reference screenshots.

The SDK compilation checks pass: no opposing winding, all source faces retained,
all attachment positions/rotations match, material texture links resolve,
accepted donor bytes match, and only tangent fields changed after MeshBuilder.
The official facing-grid trailer remains byte-identical. The installed SDK
ships no mesh-material or particle-effect schema; those resources are checked
against observed field shapes and attachment identities, **not** described as
schema validated. No game launch, playtest, multiplayer or performance claim.

The logistical role follows the show's retrofitted civilian ship: missile launch
overloaded its power grid, while spinning the drum later made a medical refuge
possible. These support modest local repair and limited defensive armament,
not another Donnager weapon budget. Sources: [SYFY, It Reaches Out](https://www.syfy.com/the-expanse/season-3/blogs/episode-recap-it-reaches-out),
[SYFY, Fallen World](https://www.syfy.com/the-expanse/season-3/blogs/episode-recap-fallen-world).
The rounded 2-km scale follows the description of its scale in
[Forbes' account of the Nauvoo launch](https://www.forbes.com/sites/kevinmurnane/2017/03/01/science-and-tech-in-syfys-the-expanse-the-spectacular-launch-of-the-nauvoo/).
The original archive PDF identifies RingBuilder and states Creative Commons
Public Domain; the intact original archive and entry hashes are recorded.
