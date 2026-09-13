# Sunflare / Razorback presentation correction

The finished candidate applies a **180-degree proper roll around the longitudinal game Z axis** to the frozen 0.12 optimized mesh. This brings a RAZORBACK-bearing center prong upward for the main overhead view. The nose remains +Z and the single engine remains -Z. Length, proportions, triangle count (17,741), UV coordinates, source textures, material files, gameplay and movement settings are unchanged. This is a fixed source normalization correction; there is no visible-hull-only runtime rotation.

The model has three similar prongs and labels on several facets. Its source has no canonical top annotation; the discarded scene-root presentation pose does not establish one. Side and overhead comparisons at six rolls are saved as `roll-probe.png` and `roll-top-probe.png`. The main integrator reviewed the comparisons and chose +180 degrees. This corrects the requested presentation, but cannot guarantee that lettering appears upright from every camera side. The user's screenshot alone does not establish a UV error. Decoded 0.12 BC7 albedo matches its source image (mean RGB error 0.592/255; flipped comparison 66.952/255), so no speculative texture flip is applied.

Positions, normals and tangent XYZ receive the same determinant +1 rotation; tangent handedness and UVs are retained. The exhaust position, forward and up rotate with the hull. Semantic `above` and `aura` anchors are re-anchored above and below the rotated bounds. Updated spatial bounds and full exhaust metadata are in `integration-spec.json`. Main must update the scout skin exhaust and phase-effect nozzle consistently. Existing resource IDs are retained for a combined overlay; this worker folder is not a standalone mod.

The pinned official MeshBuilder generated fresh JSON, binary and facing grid. The established tangent-only post-conversion repair preserves the official non-tangent bytes and trailer. Independent final checks read the binary vertex stream, validate winding and orthonormal shading frames, verify every equipment point and the exhaust frame, ray-check engine clearance, and exactly reverse the proper rotation to recover old editable vertices/normals. Original triangle indices and UVs compare exactly. The source archive, extracted master, all four DDS textures and material bytes match their frozen hashes. Six brushes and 18 DPI sprites are rendered from the actual rolled model, plus two optional logos.

## Handoff

- `audit/update13-c/integration-spec.json`: full mesh/material/texture directory and per-file hashes; same contract shape as 0.12.
- `audit/update13-c/ui-integration-spec.json`: rotated UI directory, skin patches and per-file hashes.
- `audit/update13-c/final-validation.json`: actual offline results.
- `assets/derived/update13-c/expanse12_sunflare_editable.gltf`: editable rotated geometry referencing unchanged original textures.
- `build/update13-c/game`: official compiled hull and unchanged material/texture dependencies.
- `build/update13-c/ui/generated`: final UI overlay.

## Reproduction

Run in this isolated worktree with a fresh UI output:

```sh
python3 tools/update13_sunflare_geometry.py
python3 tools/update13_sunflare_compile.py
python3 tools/update13_sunflare_ui.py --source assets/derived/update13-c/expanse12_sunflare_editable.gltf --expected-triangles 17741 --game '/run/media/haker/NVME 2/SteamLibrary/steamapps/common/Sins2' --sdk '/run/media/haker/NVME 2/SteamLibrary/steamapps/common/Sins of a Solar Empire II - Mod Tools'
python3 tools/update13_sunflare_validate.py
```

Read-only local dependency: `/run/media/haker/NVME 2/expanse-workers/validation` holds the original 0.12 Sunflare source, normalized derivative, source audit and converter prefix; `expanse-mod/.tools` holds the pinned texture converter. The candidate uses its own copied prefix. Missing inputs fail explicitly and are not downloaded or reconstructed. Official Wine conversion required local socket access; it did not launch Sins II.

**All new runtime checks remain NOT RUN:** overhead and side orientation, level flight/banking, nozzle alignment, normal/boost/jump plume, UI appearance and save/reload. No installation, enabling, gameplay changes or publication was performed by this worker.
