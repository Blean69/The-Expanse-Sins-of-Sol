# Series6 Sunflare scout asset handoff

**Offline conversion only; runtime NOT RUN.** Main owns all scout gameplay, player/build-menu registration, abilities, movement, phase effects and package integration. This worker produced only the local visual derivative, mount-free skin resources and actual-model UI.

The supplied ZIP contains one glTF2.0 mesh, its binary buffer, four4096×4096 RGBA textures and a background JPEG. The mesh has60,635 triangles, one material and six transform nodes. There are no animations or skinning. The actual source material/texture names are `Razorback`; the user's requested unit class remains Sunflare. Metadata identifies only OpenSceneGraph3.5.6; no creator, exact license or separate attribution document is present. Record the user-supplied local-conversion request without inventing wider permissions. The ZIP and full extracted master remain unchanged and hash-checked.

The outer scene pose includes an arbitrary presentation translation, rotation and100×scale. Normalization uses the original single mesh's local coordinates, preserving its proportions. A proper determinant+1 rotation maps local+Y bow to game+Z, local+X cockpit-up to game+Y, and local+Z to game+X. Uniform scale gives27.3913gameunits length, provisionally12m against the existing Tachi46m/105gameunit reference. This falls within the requested10–15m scout envelope; the source package does not establish physical units.

The finished derivative has **17,741 triangles**, using the existing pinned meshoptimizer with normal/UV attribute weights and actual indexed source positions. Simplifier relative error is0.00185890, below0.012. No geometry was invented, no mesh parts were arbitrarily deleted, and no new weapon hardware was added. Full-source projected silhouette overlap is99.92%top,99.87%side and99.71%rear. There are no PDCs or torpedo mounts.

Six reduced faces inherited near-perpendicular average corner normals and collapsed UVs. Their positions and UVs remain unchanged; isolated corners receive actual face normals and an explicit longest-edge tangent frame. All other source shading frames are retained. The compiler repair then changes only tangent fields to the retained authored frames, preserving official vertex positions/indices, meshpoints and regenerated facing-grid trailer. Final opposed and near-ambiguous winding counts are both zero; compiler tangent fallback count is zero. The six explicit source-frame repairs are separately recorded in `optimization.json`.

The single Epstein nozzle comes from the measured central engine-mouth ring:98source vertices on localY≈−8.372779, radius≈1.663. Its point is0.1gameunits beyond the mouth and its−Z centerline clears the entire model. The three surrounding prongs are retained hull geometry, not additional engines. Only stock-observed center/above/aura/exhaust.0 equipment names are emitted; there are no artificial weapon points.

Materials preserve the actual supplied UV/albedo and metallic/roughness channels. Four2048² game DDS maps are generated separately from the4096² masters. ORM uses R255 because no AO source exists; G/B retain referenced glTF roughness/metallic. MaskB receives the source emissive maximum channel, so the installed shader's emission is base-color-tinted rather than an independent emissiveRGB texture. Source referenced normals are resized and renormalized without speculative green-channel inversion. The `DirectX` filename conflicts with generic glTF naming expectations; bump direction still requires runtime inspection. The same explicit channel adaptation already used by the accepted Amun-Ra pipeline is applied here.

Six pinned-schema brushes,18 DPI sprites and two optional mod logos are rendered from the actual final derivative using source colors. Portrait: `build/update12-c/ui/source/sunflare_portrait_master.png`. The background JPEG is preserved in intake only and is never packaged as ship art. UI uses installed scout image dimensions.

## Integration

- `audit/update12-c/integration-spec.json`: hull mesh, spatial bounds, measured exhaust, normalization and hashes for the six generated game files in `build/update12-c/game`.
- `audit/update12-c/ui-integration-spec.json`: separate UI directory, six brushes and exact skin property patches.
- `assets/derived/update12-c/expanse12_sunflare_editable.gltf`: game-oriented editable geometry with original texture references; compiler-input glTF/binary are separate siblings.
- `assets/source/update12-sunflare`: untouched extracted master. `assets/original/update12-sunflare`: unchanged original ZIP copy.

No unit, skin, weapon, ability or player definitions are supplied by this worker. Do not install the worker output folder as a mod. Main integrates it into the complete experiment. No audio was added.

## Reproduction and checks

Read-only dependencies: supplied download, unchanged installed game/SDK, main `.tools/libmeshoptimizer.so` and `.tools/texconv.exe`, existing isolated converter prefix copied into this task's own output. Missing dependencies fail explicitly; no replacements/downloads occur. Run from this isolated worker tree:

```sh
python3 tools/update12_sunflare_intake.py
python3 tools/update12_sunflare_geometry.py
python3 tools/update12_sunflare_compile.py
python3 tools/update12_sunflare_ui.py --source 'assets/derived/update12-c/expanse12_sunflare_editable.gltf' --expected-triangles 17741 --game '/run/media/haker/NVME 2/SteamLibrary/steamapps/common/Sins2' --sdk '/run/media/haker/NVME 2/SteamLibrary/steamapps/common/Sins of a Solar Empire II - Mod Tools'
python3 tools/update12_sunflare_validate.py
```

The UI renderer requires a fresh output directory and refuses to overwrite an existing result. Official Wine conversion needs local socket access; the approved command writes only this isolated output and does not launch the game. Checks cover archive/master hashes, official binary/JSON conversion, retained tangent fields/trailer, proper normalization, nozzle point/frame/ray, source/derivative silhouettes, material/DDS references/dimensions, pinned brush schema and PNG alpha/dimensions. Runtime load, perceived scale, tint/normal-map direction, selection, movement, idle/boost/jump plumes and save/reload remain unobserved.
