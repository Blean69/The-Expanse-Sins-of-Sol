# Worker C — static ship UI polish

Owner: Worker C, isolated worktree `/run/media/haker/NVME 2/expanse-workers/validation`. Only new `tools/polish_ui.py`, `audit/polish-c/` records, and ignored `build/polish-c/` output were written. Previous worker outputs, installed content, normalized sources, original archive, extracted master, shared definitions, and SDK were not changed.

## Integration contract

Copy **the contents of `build/polish-c/generated/`** into the new experimental package root: 6 `.brush` definitions, 18 standalone PNG textures, `mod_small_logo.png`, and `mod_large_logo.png` (26 files). Apply `build/polish-c/integration-spec.json`'s seven `patches[]` objects to `entities/trader_light_frigate.unit_skin`; each contains an exact JSON pointer, previous installed value and proposed value. The main integrator owns that skin and `.mod_meta_data`. No entity manifests are required for these brush/PNG assets.

`integration-spec.json` also provides `logos.small_logo = mod_small_logo.png` and `logos.large_logo = mod_large_logo.png`. Their structure and sizes come from pinned SDK `examples/mods/super_fast_trader_scout_corvette/.mod_meta_data` and its two example images. The logo images themselves were newly rendered from the supplied Tachi; no vanilla or SDK image pixels were copied.

Do not package the source masters, SVG, recipe, report, trace, integration metadata, or contact sheets. Keep them beside generated output in the project only. Preview: `build/polish-c/ui-contact-sheet.png`.

## Verified reference and file conventions

Installed Cobalt `.unit` selects Cobalt `.unit_skin`; seven GUI/main-view icon fields resolve to six existing image families. `gui.hud_monochrome_icon` reuses the `main_view_icon` family. No matching Cobalt `.brush` sidecars are installed: original references use implicit same-ID textures. Proposed mod-specific explicit brushes use schema-verified `normal_state.texture` and `supported_dpis: [150, 200]`. Their image IDs are unique `mcrn_corvette_*` names, preserving other ships' UI assets.

| Family | 100% | 150% | 200% | Generated alpha |
|---|---|---|---|---|
| HUD icon | 85×40 | 128×60 | 170×80 | Transparent RGBA |
| HUD picture | 265×85 | 397×127 | 530×170 | Opaque RGBA |
| Tooltip picture | 459×216 | 689×324 | 918×432 | Transparent RGBA |
| Tactical icon | 25×12 | 38×18 | 50×24 | Transparent RGBA |
| Selected icon | 36×23 | 54×35 | 72×46 | Transparent RGBA |
| Sub-selected icon | 46×33 | 69×50 | 92×66 | Transparent RGBA |
| Small mod logo | 85×40 | — | — | Opaque RGBA |
| Large mod logo | 459×216 | — | — | Opaque RGBA |

Dimensions match every installed source exactly, including uneven 150% rounding. These are **standalone PNGs**, not authored atlases. Pinned SDK README line 73 explicitly specifies PNG for UI elements; no DDS output or conversion is needed. The brush schema describes engine texture-page optimization internally and DPI name postfixes. The explicit brush definitions preserve that supported path without inventing an atlas configuration.

## Source and rendering method

`assets/derived/baseline/mcrn_editable.gltf` from the main project supplies the existing 14,622-triangle normalized source. Its glTF, buffer and referenced texture hashes are checked against the recorded checkpoint before rendering. The installed brush-schema Git blob is checked against pinned SDK revision `8e061033afe53b1393eaefd56617a3fd041eeb5f`.

`tools/polish_ui.py` performs CPU orthographic projection with a z-buffer, source base-color UV sampling and simple double-sided studio lighting. OPAQUE material alpha is forced opaque according to glTF semantics; decals use a 0.5 alpha cutout. No face culling is used, so the prior game's hull-facing issue is not baked into sprites. A documented gamma/exposure lift makes source black paint readable at small UI sizes. This is a static illustration, not an emulation of the game's ship shader: normal maps, PBR metal reflections, in-game lights and animated turrets are not claimed. Original TACHI/navy markings come from source textures.

Transparent portrait masters are fitted without stretching into each observed UI rectangle. The opaque HUD panel has a newly generated dark background. Tactical icons are white neutral silhouettes projected from the same geometry, with outlines for selected/sub-selected states; there are no invented ship parts or faction emblems. All six static source PDC assemblies participate in the projection.

Editable sources remain under `build/polish-c/source/`: Python rendering recipe (tracked tool), JSON recipe, 1836×864 portrait master PNG, 1000×480 silhouette PNG, and editable SVG triangles projected from the actual source. The SVG is a geometric silhouette, not AI-generated imagery. Source-derived assets stay ignored by Git.

These renders are derivatives of **MCRN Tachi [Expanse TV Show] by Jakub.Vildomec, CC-BY-4.0**, under the existing `ASSET-SOURCES.md` record. Main integrator should append “static UI portrait rendering, contrast adjustment, silhouette projection, DPI resizing, selection outlines, and mod-logo layout” to its derivative change notice and retain the existing attribution/license links with the new package. No release or publication was performed.

## Checks performed and limits

- Pinned brush-schema blob and normalized glTF/buffer/texture checkpoint hashes: PASS.
- Six explicit brushes validated against that schema: PASS; per-file results and resolved DPI filenames in `ui-validation.json`.
- All 18 generated PNG files: exact stock dimensions, RGBA mode, expected alpha extrema, nonempty image bounds: PASS. Both logo sizes/RGBA/opaque alpha checked against the SDK example dimensions.
- Contact sheet visually inspected after the lighting and aspect-preservation adjustments: continuous hull surface, readable source color blocking, three distinct tactical selection states. This is offline visual inspection only.
- `python3 -m py_compile tools/polish_ui.py`: PASS.

Runtime GUI lookup, DPI switching, mod-browser logos, HUD/tooltip layout, tactical icon tint and zoom readability: **NOT RUN**. Test the new package's mod-browser entry first, then construction-panel/HUD/tooltip images at 100/150/200% UI scale, followed by neutral/selected/sub-selected tactical states at normal and distant zoom. Shared Cobalt skin scope remains applicable to neutral/garrison users.

The main validator must admit PNG textures, `.brush` files and the two root logos for this new package, resolve every brush's base/150/200 texture filename, and validate the full observed mod metadata rather than the old baseline's compatibility-version-only placeholder. This worker did not alter the shared validator or package definitions. Full six-turret simulation and geometry validation remain the respective main/rig workers' responsibility.

## Reproduce

After integrating the tool, from the main project root:

```bash
OPENBLAS_NUM_THREADS=1 python3 tools/polish_ui.py --main-root '/run/media/haker/NVME 2/expanse-mod' --game '/run/media/haker/NVME 2/SteamLibrary/steamapps/common/Sins2' --sdk '/run/media/haker/NVME 2/SteamLibrary/steamapps/common/Sins of a Solar Empire II - Mod Tools'
```

Output defaults to that checkout's `build/polish-c`. All dependencies must already exist; missing sources or pin mismatches stop the build explicitly. No downloads, installs or game launches occur.
