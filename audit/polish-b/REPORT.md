# Geometry polish and six-PDC export

**Offline export checks pass. Six-mount rotation, aiming, culling and shading in the game remain NOT RUN for these outputs.** This work responds to the supplied runtime screenshot of substantial holes in the frozen visual baseline. That screenshot is observed user evidence; it is not a test of this derivative.

All writing stayed in this worker worktree: new `tools/polish_geometry*.py`, `assets/derived/polish-b`, `build/polish-b`, and `audit/polish-b`. Original/master assets, the older one-PDC candidates, prior outputs, installed game, pinned SDK, and installed mods were not changed. No game launch, installation, enabling, commit, or publication occurred.

## Hull-hole diagnosis and correction

The compiled baseline had a material-dependent winding mismatch. With face edges and supplied vertex normals expressed in the same coordinates, baseline material0 had 5,563 clearly opposed triangles and material2 had 6,419 at an absolute dot tolerance of 1e-7. Primary/text materials were mostly aligned. The installed stock Cobalt mesh had 7,692 aligned versus24 opposed triangles under the same initial measurement. This agrees with the observed disappearance of broad hull surfaces under backface culling. Alpha alone does not explain the per-material winding evidence.

The old verifier accepted either triangle order to compare geometry and therefore did not catch this culling defect. It also correctly discovered invalid MeshBuilder-generated tangent frames. Those old results remain archived rather than rewritten as passes.

`polish_geometry.py` retains every triangle, normal, UV, and part, and corrects triangle winding against authored normals in game-coordinate source. It emits separate compiler inputs. The current official importer still reverses winding for some primitives. `polish_geometry_winding.py` maps each emitted triangle back to its exact source triangle by material/order, verifies all three positions, reverses only the affected source indices, and reruns the **official MeshBuilder** for JSON and binary with `--fill_triangle_facing_grid`.

**There is no postcompile binary index repair.** Winding-dependent surface-facing grids and the opaque binary trailer come from the official conversion of corrected source indices. A stale grid from before the winding correction is never paired with a repaired mesh.

Final winding validation uses normalized face-normal alignment and a1e-5 cosine tolerance. This avoids treating floating-point differences in nearly perpendicular authored normals as a reliable facing direction. All13 outputs have zero meaningfully opposed triangles. The number of ambiguous triangles and minimum alignment are recorded individually in `output-validation.json`. These ambiguous authored-normal cases remain a visual inspection item; no normals were silently replaced.

## Tangent repair without changing topology or facing metadata

The installed SDK explicitly documents that MeshBuilder generates Mikk tangents (`Shaders/mesh/mesh_pbr_utility.hlsli:152`). Its emitted tangent fields still included zero/nonorthogonal vectors after correct winding. The bounded repair in `polish_geometry_finish.py` matches each emitted vertex to the retained authored source by position, normal and UV; projects its authored tangent onto the normal plane; normalizes it; and retains its handedness sign. **No arbitrary-axis fallbacks were required.** This preserves authored UV direction better than inventing per-face tangents for degenerate UV regions. It does not certify that the original asset's normal maps were baked against this exact optimized topology.

The repair writes only each unskinned vertex's **16-byte tangent XYZ/W field**, using the already verified current binary layout, and updates the corresponding debug JSON tangent array. It asserts that every byte outside those fields is unchanged. Geometry, normals, UVs, indices, primitives, meshpoints, materials, facing data, and opaque trailer remain exactly as emitted by the official winding-corrected compilation. Before/after trailer hashes match for each mesh. Final JSON/binary parity, finite/unit tangent vectors, and normal/tangent orthogonality all pass. Normal-map appearance still requires the user's next runtime test.

## Six independent turret assemblies

The mechanical correction from the one-PDC investigation is applied to each corresponding assembly using its own frame and geometry, not the old sphere-pivot grouping. The sphere is an upper gun detail, not the turret origin. For each source body node427/475/523/571/619/667,84 lower-platform triangles enter the yaw mesh and96 upper-housing triangles enter the pitch mesh, separated by an empty local-Y=.65 gap. The test verifies no triangle crosses that gap for any assembly. Holders and pin details accompany yaw; upper housing, ammo boxes, barrel cluster and attached details accompany pitch. Fixed deployment links remain in the hull. No deployment animation is added.

Counts are exactly **10,560 hull +6×(138 yaw/base +539 pitch/barrel) =14,622 triangles**. No optimization, decimation, silhouette change or triangle removal occurred. Each physical PDC remains one barrel cluster/muzzle and should receive one weapon firing budget.

Each base pivot is its named lower-platform/body origin. Each pitch pivot is the corresponding holder-pin bounds midpoint in that gun's local frame. Muzzles are estimated from the existing optimized barrel tips. These are independently measured geometry estimates, not runtime-proven mechanical centers. All six basis matrices are orthonormal and each emitted mount rotation agrees with its intended basis. Exact unit mounts, turret offsets, aliases and emitted meshpoint values are in `mount-metadata.json` under `rigs` and `outputs`.

Alias pattern: `expanse_pdc_<index>_base` / `expanse_pdc_<index>_barrel`, index0..5. Mesh pattern: `expanse_polish_pdc_<index>_base` / `_barrel`; hull `expanse_polish_hull`. The unit mount point is `child.<base alias>`, base point `child.<barrel alias>`, and barrel point `turret_muzzle.0`. The metadata's yaw±100° and pitch−75..5° limits are provisional experiment limits, **not verified unobstructed coverage**. Correct sign, self-intersection, obstruction by the fixed hull/linkage, tracking speed and muzzle alignment require runtime observation.

## Ready outputs and dependencies

Final candidate game meshes: `build/polish-b/game/meshes/*.mesh` (13 files). Use these tangent-repaired outputs, not `compiler-binary`. Debug counterparts: `build/polish-b/repaired-json/*.mesh_json`. Raw official outputs/logs remain separately under `build/polish-b/compiler-*`.

Editable assembly: `assets/derived/polish-b/expanse_polish_editable.gltf`,13 buffers named `*_editable.bin`, actual hull→yaw→pitch hierarchy, separate parts, game-coordinate source and original material/image references. Image paths reference the existing normalized source assets read-only. The editable assembly is not a direct compiler input; use the documented preparation scripts. Compiler glTF/bin and retained source-frame evidence remain separate in the same derived directory.

The final material IDs emitted by MeshBuilder are in `outputs.<part>.materials`. Use matching copies of existing source material definitions under those emitted IDs and reuse the same texture IDs. This geometry work creates no additional texture/audio content. Attribution and derivative permission remain governed by the existing project asset-source record; no derivatives were distributed.

New audit records: `mount-metadata.json`, `output-validation.json`, `winding-correction.json`, `source-preservation.json`, and `six-pdc-mounts.png`.

Checks run: four script syntax checks;13 official JSON and13 binary conversions initially, then official reconversion after mapped winding corrections; all13 binary tangent-field repairs; unchanged bytes/trailer assertions; all13 final geometry/winding/frame/meshpoint/parity checks; source hash comparisons against the earlier worker checkpoint; editable hierarchy and rest-pose comparisons. Every final output conserves geometry and the complete assembly's maximum position discrepancy from the frozen baseline is **2.5053e-6 game units**. Required frozen dependency hashes match the earlier checkpoint. All runtime outcomes remain NOT RUN for these outputs.

## Reproduction order

Run from this isolated worktree with the same local ignored dependencies and pinned SDK. Python requires NumPy, Pillow and SciPy; the latter is already installed locally. No dependency update is needed.

```bash
OPENBLAS_NUM_THREADS=1 python3 tools/polish_geometry.py \
  --source-root '/run/media/haker/NVME 2/expanse-mod' \
  --sdk '/run/media/haker/NVME 2/SteamLibrary/steamapps/common/Sins of a Solar Empire II - Mod Tools' \
  --wine '/home/haker/.var/app/com.valvesoftware.Steam/.local/share/Steam/steamapps/common/Proton 10.0/files/bin/wine64' --compile
OPENBLAS_NUM_THREADS=1 python3 tools/polish_geometry_winding.py \
  --sdk '/run/media/haker/NVME 2/SteamLibrary/steamapps/common/Sins of a Solar Empire II - Mod Tools' \
  --wine '/home/haker/.var/app/com.valvesoftware.Steam/.local/share/Steam/steamapps/common/Proton 10.0/files/bin/wine64'
OPENBLAS_NUM_THREADS=1 python3 tools/polish_geometry_finish.py
OPENBLAS_NUM_THREADS=1 python3 tools/polish_geometry_editable.py
```

Conversion uses only `build/polish-b/proton-prefix`, initially copied from the worker's prior isolated prefix. The sandbox blocks Wine's local sockets, so the official headless conversion used authorized escalation. It never used the game's prefix.

The next workstation check should first orbit the camera around the stationary hull and inspect both front-facing hull surfaces and normal-map lighting. Then check each numbered turret against targets fore/aft/port/starboard/above/below, including while moving and after save/reload. Observe yaw, pitch, muzzle effects and self-clipping separately from dual-purpose targeting and damage tests. The offline diagram is a geometry view, not proof of runtime culling or turret motion.
