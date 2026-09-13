# Raptor and Free Navy Pella assets — final offline candidate

Owner: isolated Raptor/Pella worker, `expanse-workers/weapon-behavior`.
Main integrator owns unit/skin definitions, abilities, weapon balance, manifests and package integration. This worker changed no installed game data, installed mod, original source archive/STL, or prior package.

## Deliverables

- `audit/update12-a/{raptor,pella}/integration-spec.json`: final current meshes, nine biaxial mounts, nine torpedo ports, four exhaust outlets, `weapon.boarding.0`, spatial bounds and final per-file SHA256 maps.
- `build/update12-a/{raptor,pella}/game`: compiled meshes, materials and DDS. Copy these directories as overlays; shared Tachi textures are identical to the previous package.
- `build/update12-a/{raptor,pella}/ui/generated`: six brushes, eighteen DPI-specific UI sprites, two optional package logos. GUI patches are in each `ui-integration-spec.json`.
- Pella final actual-model portrait: `build/update12-a/pella/ui/source/ship_portrait_master.png`.
- `assets/derived/update12-a/{raptor,pella}/*_editable.gltf`: assembled editable derivatives, separate from compiled game meshes.
- `final-validation.json`: checks and final integration-spec hashes.

## Identity, source and scope

Source `/home/haker/Downloads/xxx_-_raptor_whole.stl` and unchanged local original both hash `c06878f57e5b9f04043793226f8c6a06b082848273ea6fc9e9369f474c8dedd6`. Source has 1,513,390 triangles. It supplies no textures, UVs, animation tracks, license or creator metadata. The user supplied it for local conversion; no independent redistribution license is claimed. Nine stowed gun assemblies are identified by actual disconnected components. Derivatives remove those gun bodies, doors, latches and braces while retaining bay housings, then attach nine existing proven yaw/pitch donor guns to measured hull supports. Original STL is untouched.

The current reduced hull is reused. No new optimization pass was made on resume. Raptor has 94,823 assembled triangles; Pella has 95,523, including 700 additional triangles needed to clip paint boundaries on the existing plating. Each uses only three unique compiled meshes. There are no railguns in these variants. Length remains the earlier provisional 89 m / 46 m Tachi scale convention (203.152 game units), not a new canonical measurement. Game +Z is bow and +Y is up. Source-to-game transform is a proper rotation and uniform scale, not a reflection.

Nine forward tubes are **authored retrofits on measured forward faces**: four outer, two middle and three lower. They are not claimed as nine positively identified TV/source launch apertures. Four exhaust origins use actual measured engine bells. The boarding origin uses a measured external surface; the original STL does not identify an airlock.

## Pella paint

Pella uses procedural silver with a higher metallic/lower roughness material than the gray/orange MCRN Raptor. The user eagle and TV screenshots guided an imagegen-generated pale gray eagle on charcoal paint. Source images, both generated passes and source PNG are preserved under `assets/derived/update12-a/pella/emblem-sources` and `texture-sources`.

The emblem is mapped directly onto existing **dorsal forward plating**, within game X [-9,9], Z [54,72], Y >18. It is one dorsal marking, not mirrored port/starboard decals. The available STL surface is not the exact TV screenshot panel: placement is a prototype adaptation. Triangle clipping substitutes material/UVs on the original surface. It adds **zero layered decal planes**, zero offset patches and zero floating marking geometry. The rest of the silver hull and every MCRN Raptor material remain unchanged by the emblem step. Final UI views deliberately show this dorsal surface. Earlier `ui-first-pass`, `ui-underside-preview` and `emblem-top-preview.png` are superseded render experiments, not package inputs.

The generated 1254 px source was transcoded by pinned texconv to a valid 1024² BC7 DDS with eleven mip levels. No generated asset is left solely in the Codex image cache. `emblem-source.json` records both exact prompts and source hashes. This is a reference-guided recreation, not a claim of pixel-identical logo extraction or studio-authored UVs.

## Checks actually run

Both variants passed:

- Installed official MeshBuilder JSON and binary compilation, with compiler-authored triangle-facing grids.
- Current source/compiled triangle count agreement; zero opposed winding triangles under the existing -1e-5 tolerance.
- Retained authored tangent-frame restoration: only tangent bytes differ from compiler binary; official trailer/grid bytes unchanged; zero tangent fallback.
- Exact nine game mount frames, proper bases, expected turret and weapon IDs, four exhaust names and boarding point.
- Nine forward torpedo rays and four aft exhaust rays unobstructed; boarding ray unobstructed.
- 288 sampled barrel centerline poses per variant (nine mounts × eight yaw angles × four pitch angles): zero measured hull obstructions.
- Original STL and preserved-original hashes unchanged.
- Mesh-material references resolve against generated DDS; BC dimensions divisible by four.
- Six brushes per variant validated against pinned brush schema blob `3e2e9a9c47b6ced821bd2b2ebb9e09f66d390c9f`; twenty PNGs each, including optional logos, have intended dimensions, alpha and recorded hashes.
- Final game/UI SHA256 maps and source-to-compiled consistency in `final-validation.json`.

All game runtime tests are **NOT RUN**. Sampled centerline clearance does not prove full swept mesh clearance, accurate target coverage, in-game turret aiming, engine plume attachment or visual backface behavior. Inspect those in game, including both ship sides (the emblem is intentionally dorsal only), close and far zoom, construction, movement, targeting, launch origins, destruction and save/reload.

## Reproduction

Run from this isolated worktree using Python 3. Required read-only dependencies are the main repo tools, `.tools/libmeshoptimizer.so`, `.tools/texconv.exe`, installed Sins2, installed Mod Tools at pinned revision 8e061033afe53b1393eaefd56617a3fd041eeb5f, preserved Raptor STL, and `expanse-workers/tachi-one-pdc/assets/derived/polish-b` plus its mount metadata and Wine prefix. Compiler uses installed Proton 10.0 Wine. Missing ignored assets are required inputs; do not substitute.

For a fresh derivative, use existing intake once, geometry with `--variant raptor` and `--variant pella`, then `update12_pella_emblem.py`. Preserve the generated emblem PNG inputs; regenerating from a prompt is not byte reproducible. Run `update12_raptor_compile.py --variant ...` for each variant. Run `update12_raptor_ui.py --variant ... --source <variant editable gltf> --expected-triangles 94823` (Raptor) or `95523` (Pella), with installed `--game` and `--sdk` paths. UI refuses to overwrite an existing output. Then run `update12_raptor_validate.py --variant ...` and finally `update12_raptor_finalize.py`. Do not rerun geometry over reviewed results merely to obtain a new checkpoint.
