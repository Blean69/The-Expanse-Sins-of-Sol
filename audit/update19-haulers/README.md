# Hauler art derivatives — update19

Private supplied Telltale assets converted in this isolated worker. No install, enable, shared-definition edits, remote push, or original asset changes.

Final game assets: `build/update19-haulers/game`. Integrator copies only this directory's regular files, never the sibling Wine prefix. Editable full-resolution derivatives and normalized textures are under `assets/derived/update19-haulers`.

- **Artemis:** full147.67m source exterior,77,478compiled triangles, three measured engine mouths. The purported compact complete78m variant ends at a cargo bulkhead and omits the original aft thruster section. The intact full source avoids inventing an assembly. Proper identity source-axis rotation, +Z bow/-Z exhaust, +Y dorsal, uniform105/46gameunits per metre.
- **Le Guin:**75,043compiled triangles. Source has damaged/missing hull panels and exposed frame. This is a stationary derelict visual, not an intact working freighter; center mesh point supports native scanning flair. No exhaust fabricated. Source Y maps to game−Z, sourceZ to gameY, determinant+1.
- **Manitoba:** not included.3752-triangle distant silhouette insufficient for requested close hull quality, detailed module assembly transforms unverified.
- **Ceres/Mausoleum:** incomplete interiors or station assemblies outside selected ship scope.

Both meshes compiled with pinned MeshBuilder and official facing grids; only tangent frame bytes patched afterward, official trailer byte-identical. Attribute-constrained simplification relative error limit0.006, source position/UV/tangent references retained.133Artemis and110LeGuin float32microslivers removed beforefinalexport. Nearlyperpendicular bevel normals reframed on split corners. Zero final opposed-winding triangles. This is sampled/offline structural QA, not engine rendering or performance proof.

Textures use supplied UVs, selected Unreal author base-color layers and tint/tiling parameters, conservative scalar roughness/metallicity, normalizedDirectX-to-glTFnormal channels. Full Unreal vertex-painted damage and decal shader logic is not reconstructed. Standalone opaque materials prevent previous hull-alpha problems; sourcecoloralpha forced255; emissionoffpendingverifiedshadertranslation.49unique material source bindings,196full-mipDDS textures, maximum1K. Material slots remain35Artemis/12LeGuin; this preserves seams and source texture fidelity but draw-call performance requires runtime testing.

The busy light speckling in textured CPU previews comes from highly detailed texture patterns and nearest-neighbor UV sampling without mip filtering; flat-color control previews remove that noise and show intact geometry. DDS textures have full mip chains for engine filtering. Do not claim exact Unreal or Sins final appearance from these previews.

Integration contract: `integration-spec.json`. Source/provenance: `source-provenance.json`. Exact regular game-file hashes: `package-validation.json`. UI assets:12brushes and36PNGsprites atnative100/150/200percentDPI. Native-derived standalone skins require integrator-provided localizedstrings `expanse19_artemis.name/.description` and `expanse19_le_guin.name/.description`. No manifests or gameplay unit definitions are authored by this worker.

Artemis skin reuses baselineRocinante blue idle/phase plume definitions; inherited native trade dialogue retained. Verify plume breadth/placement in engine. LeGuin skin retains native derelict capture-active scanner flair and death sequence; no alternate capture implementation.

Rebuild order (python3 with numpy/scipy/Pillow/jsonschema, shared main`.tools`): `tools/update19_haulers.py`, `tools/update19_haulers_compile.py`, `tools/update19_haulers_materials.py`, `tools/update19_haulers_ui.py`. Wine compiler/texconv require local socket access. Every output stays in worker directories. No Blender needed.

Observed passes: MeshBuilder execution, winding/tangent/trailer consistency, materialDDSbindings, skin/brush schemas,actualtrianglepreviews, exactfilehashgeneration. Not run: game load, face culling in engine, plume placement, native scanning activation, savedgames, multiplayer, Windowsgraphics, draw-call/performance assessment.
