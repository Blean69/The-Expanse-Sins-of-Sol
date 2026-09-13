# Truman model derivative — update 0.15

Owner: isolated Truman worker, `/run/media/haker/NVME 2/expanse-workers/playtest15-truman`. Main integration owns unit statistics, weapons, abilities, research, localization and packaging. This worker supplies model resources and measured attachment frames only.

The supplied `truman_class.zip` is SHA-256 `a7ad8ce87bc9ac6d04b1873bfb3a2814ab93a7453f52a55a5f3d2937a191941c`. The archive and extracted master are preserved under `assets/original/update15-truman`. The glTF contains 293,253 triangles across seven mesh partitions sharing one textured material, four 8192² texture maps, no skeleton and no animations. The supplied material requests double-sided rendering; the game export instead retains authored normals and checks exterior orientation. No general face duplication is applied.

Credit: This work is based on [“Truman Class”](https://sketchfab.com/3d-models/truman-class-ec7e5f790d2940e489bf28c6e6d4427e) by [mohamedhussien](https://sketchfab.com/mohamedhussien), licensed under [CC-BY-4.0](http://creativecommons.org/licenses/by/4.0/). The bundled license text and glTF attribution agree.

The main integrator selected a provisional 376 m TV-class length. Uniform scaling uses the established 105 game units per 46 m convention, preserving the supplied silhouette; width is not distorted to fit a different reference. The source aft direction is +Z. A proper 180° Y rotation makes game +Z the bow. Editable geometry uses game coordinates; compiler-input geometry has the explicit Z conversion required by the tested exporter pipeline.

All original detail is retained except 393 numerically near-collinear triangles with double area below 0.0001 in game units after float32 conversion. Those tiny slivers can change face sign between MeshBuilder JSON decimal serialization and its binary output. This is a numerical cleanup, not a model reduction. The completed assembled derivative has **306,774 triangles**, including eighteen 677-triangle PDC assemblies and their fixed supports.

Two actual dorsal/ventral heavy railgun assemblies are separated along existing component boundaries and placed on their retained circular bearings. They use narrow ±12° yaw and zero pitch. Each assembly has two modeled barrel outlets, supplied as alternating muzzle positions. Six exhaust origins come directly from the six source engine bells. Four launch origins are measured on forward hull surfaces; exact television launcher correspondence is unverified. The model's 5,371 connected components do not provide named deployable PDC assemblies. Eighteen measured, supported Tachi-donor PDC retrofits represent three six-sided batteries; this is a gameplay representation rather than a claim to have identified 42 individual original-model gun mounts.

PDC outgoing rays use the actual barrel offset, muzzle and mount basis. The compiled matrix is stored by columns; `reshape(3,3).T` must match the unit's right/up/forward basis. Pitch signs and aim tolerance follow the verified update 0.14 convention. Conservative native rectangular arcs are chosen from source-hull obstruction tests and checked at 1° intervals with a ±3° direction envelope. Main should use 1° firing tolerances. Some aft mounts have restricted elevation because engine pods obstruct low-angle shots. This trades coverage for hull avoidance. Sampling does not prove a continuous swept-volume clearance, and neighboring moving turret geometry is not included.

Source color, normal, occlusion/roughness/metallic and emissive maps are adapted to 4096² game textures with their existing UVs. Normal vectors are renormalized after reduction; no unverified green-channel flip is introduced. Source emissive strength 10 is restrained to game factor 1. Emission uses the installed mask convention; it is not independent full-color source emission. No alpha transparency is added. PDC and support textures reuse existing tested derivative resources.

The static UI is rendered from the final assembled Truman geometry and source color map, with the actual PDC donor color texture. `ui-final` supersedes the intermediate pre-cleanup `ui` render. Source dependency hashes, triangle counts, pinned brush schema checks and PNG sizes are recorded. These CPU previews are not game-engine screenshots.

Reproduction, from this worker worktree:

```sh
python3 tools/update15_truman_intake.py
python3 tools/update15_truman_components.py
python3 tools/update15_truman_geometry.py
python3 tools/update15_truman_compile.py
python3 tools/update15_truman_materials.py
python3 tools/update15_truman_ui.py --variant truman --source assets/derived/update15-truman/expanse15_truman_editable.gltf --expected-triangles 306774 --game '/run/media/haker/NVME 2/SteamLibrary/steamapps/common/Sins2' --sdk '/run/media/haker/NVME 2/SteamLibrary/steamapps/common/Sins of a Solar Empire II - Mod Tools'
python3 tools/update15_truman_validate.py
```

The Wine steps need local IPC/socket access and use only the pinned SDK plus this worker's isolated prefix. They neither install nor enable nor launch the game. The UI tool refuses an existing output folder. `--reuse-converted-textures` can finish material binding after an interrupted mesh stage only when every saved PNG/DDS conversion checkpoint hash matches.

Runtime tests remain **NOT RUN**: material appearance, all six drive plumes, PDC tracking/arc-edge handoff, railgun articulation, missile launch positions, save/reload and fleet performance require workstation observation. Main's lore/balance and package reports control the playable unit behavior.
