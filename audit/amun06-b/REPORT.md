# Amun06 geometry handoff — Worker B

Status: **PASS OFFLINE ONLY. Runtime NOT RUN by this worker.** Main integrates definitions, package identity and runtime observations. This work writes only new `tools/amun06_geometry*.py`, `audit/amun06-b`, `assets/derived/amun06-b`, and `build/amun06-b` in the isolated `tachi-one-pdc` worktree. No game, installed mod, original asset, hero04 or torpedo05 file was changed.

## Geometry and scale

The actual source is Worker C's preserved Amun-Ra glTF master, with its original binary and four 4096² image atlases. The source has no animations or skins. Geometry is transformed out of its presentation/root scale using the inverse central-hull root transform. Source +Y becomes game +Z, source +Z becomes game +Y, and source +X becomes game −X: a proper rigid rotation, followed by uniform scaling and translation.

The central authored hull is 23,556 triangles. Its length is uniformly scaled to **140.36299953 game units**, using the provisional 61.5 m / 46 m Amun/Tachi ratio and the existing Tachi length 104.986959. The 61.5 m value is a secondary reference supplied by the integrator ([comparison references](https://www.st-minutiae.com/resources/comparison/references.html)); it is not primary-verified canonical scale. Detached posed equipment never determines this scale.

The generated ship has **27,526 triangles**: hull 23,842 (central hull + 280 door triangles + six triangles of selected fixed pads), plus three yaw bases of 352 and three pitch assemblies of 876. No decimation, re-meshing, global smoothing, invented supports, or optimization was applied. All geometry, UVs and authored shading frames come from the actual source, partitioned at its joints. Original static source doors remain static.

The source has four PDCs. This prototype deliberately selects roots **892 (starboard-forward), 910 (ventral-aft), and 946 (dorsal-aft)**, omitting **928 (port-mid)**. This is the requested three-gun prototype configuration, not a canonical assertion. Opposing dorsal and ventral mounts provide complementary coverage; the forward mount adds a third approach direction. Geometric pad hemisphere sampling is a selection aid, not proof of game targeting or unobstructed firing arcs.

All fifteen detached posed boarding pods and four posed torpedoes are excluded from the ship. The optional separate boarding-pod mesh uses the actual compact source pod root **122**, retaining all **4,481 triangles** and 22 subparts; the larger deployed showcase pod is not used. This pod is centered and uniformly scaled with the ship. It is a visual effect candidate, with no projectile entity or interception behavior created here. Eight meshes total contain **32,007 triangles**.

## Three mechanical rigs

The source provides real yaw nodes **895/913/949**, pitch nodes **900/918/954**, and cannon nodes **905/923/959**. Source yaw is local Z; pitch is local X. Fixed pads stay with the hull, yaw structures are separate bases, and each cradle/cannon assembly is a separate pitch mesh. There is no duplicate static moving assembly under the rig.

Source yaw poses and exact joint origins are preserved. Each source pitch pose is removed rigidly about its actual joint and placed at horizontal game neutral. Game local Y follows the source yaw axis, and game local +Z follows the actual cannon barrel. Muzzles are measured at the real terminal barrel rings with a small 0.015 source-unit forward clearance. Metadata supplies base-to-barrel offsets, local muzzles, source nodes, unit mount bases, skin aliases and weapon turret overrides. Weapon references are `expanse06_amun_pdc_0` through `_2`.

Configured candidate limits are yaw −180..180 and pitch −85..5 degrees. Rotation, hull clearance, obstruction, firing arc sign and tracking must be checked in game. Rest-pose reconstruction error is at most 2.8e−9 game units; the source matrix's 4.5e−9 orthogonality error is below the explicit 1e−7 source transform tolerance. Compiled mesh-point rows are checked against the required right/up/forward basis with no transpose alternative.

## Equipment locations

`equipment.json` and `integration-spec.json` provide actual measured positions and bases, not reused Tachi coordinates.

- **Rail:** terminal cap between paired forward machined components 9/10 in the welded central-hull component audit, plus 0.02 source-unit clearance. Game muzzle `[-1.86359790, -8.29514659, 66.47124465]`, forward +Z, point `weapon.rail.0`. An independent geometric ray from this point along source +Y intersects zero central-hull triangles. Identification is geometric: the source components do not contain an authored railgun name.
- **Exhaust:** full inner aft nozzle rim circle fit, not an aftmost vertex or edge sample. Eight inner-rim samples give source radius 3.97356026 and maximum radial residual 0.00279676. Emission point `[-1.93304335, -7.84064431, -67.08800670]`, forward −Z, point `exhaust.0`.
- **Torpedoes:** actual named door groups 7 and 12. Centers and surface normals are derived from their local geometry and transformed through the real source pose. These are measured static door positions; an unobstructed/open launch throat has not been established.
- **Boarding:** actual `Shuttle_Bay_Door_R_LP` root 41 surface center and normal, point `weapon.boarding.0`. The opposite door is retained. This is a launch-reference candidate on actual source geometry, not a verified open bay or travel path.

The reported spatial bounds contain only the assembled ship and three neutral PDCs; the separate pod is excluded. Main owns any gameplay unit radius or targeting implications.

## Compiler and materials

Eight meshes were compiled with the installed pinned official MeshBuilder in both JSON and binary modes, using `--fill_triangle_facing_grid`. Inputs explicitly compensate the compiler's Z reflection. Per-triangle winding was compared with authored outward normals and corrected in the glTF indices, then the official compiler regenerated the facing grids. No guessed facing-grid algorithm or unchanged trailer after a winding reversal is used.

The known MeshBuilder tangent defect is handled by a bounded tangent-only repair: retained authored frames are matched by position/normal/UV, orthogonalized to emitted normals, and written to the binary's 16-byte tangent fields plus matching JSON. All other binary bytes, including the official facing-grid trailer, remain identical. No fallback tangent was needed. Across eight meshes, positions/normals/UVs match source within **3.79451e−6**, reconstructed rest pose within **3.79445e−6**, binary/JSON vertex difference is below **5e−7**, and zero triangles have opposed or ambiguous winding. Tangents are finite, unit and orthogonal; every binary point has the verified expected basis.

Eight exact compiler material aliases share four **2048²** DDS maps generated from the untouched 4096² originals. CLR/ORM/mask use BC7, and the normal uses signed BC5 (legacy `BC5S`, equivalent DXGI 84). Every material and texture reference resolves inside the staged game directory. All mipmaps were generated. ORM R is 255 because the source has no AO map; G/B retain source roughness/metallic. Mask B uses maximum emissive RGB while R/G/A are zero. The installed shader tints emission with base color, which does not exactly reproduce independent source emissive RGB. The glTF-referenced normal texture has a DirectX filename; its reference and channels are retained and renormalized after resizing. No unverified green-channel reversal was applied. Normal-map bump direction remains a runtime visual gate.

## Checks actually run

- Actual-source axis inspection and connected-component audit.
- Eight official JSON/binary compiles, winding correction and official recompilation.
- Tangent repair with byte-range/trailer preservation, source frame correspondence, finite unit orthogonal frames, strict mesh-point basis checks and assembled geometry reconstruction: PASS.
- Four texconv conversions, DDS dimensions/formats, eight exact material aliases and all texture references: PASS.
- Unique ship source ownership (37 mesh nodes), exclusion of the fourth gun and detached equipment, three source joint invariants and rail exit ray: PASS.
- SHA-256 preservation of all seven source-master files, all 128 frozen hero04 files and all 26 frozen torpedo05 files: PASS.
- Worker C independently rendered the actual active seven-part 27,526-triangle editable ship. No active geometry changed after that render.

Runtime aiming, launch clearance, pod travel, shading, performance, construction and save/reload remain untested by this worker. No claimed schema or compiler result substitutes for those observations.

## Reproduction and dependency boundaries

Run from the isolated worktree with `OPENBLAS_NUM_THREADS=1`. These commands regenerate the new Amun06 derivative only; preserve the currently frozen output manifest before intentionally rebuilding it.

```sh
export OPENBLAS_NUM_THREADS=1
python3 tools/amun06_geometry_inspect.py
python3 tools/amun06_geometry_components.py
python3 tools/amun06_geometry_prepare.py
python3 tools/amun06_geometry_compile.py --sdk '/run/media/haker/NVME 2/SteamLibrary/steamapps/common/Sins of a Solar Empire II - Mod Tools' --wine '/home/haker/.var/app/com.valvesoftware.Steam/.local/share/Steam/steamapps/common/Proton 10.0/files/bin/wine64'
python3 tools/amun06_geometry_winding.py --sdk '/run/media/haker/NVME 2/SteamLibrary/steamapps/common/Sins of a Solar Empire II - Mod Tools' --wine '/home/haker/.var/app/com.valvesoftware.Steam/.local/share/Steam/steamapps/common/Proton 10.0/files/bin/wine64'
python3 tools/amun06_geometry_finish.py
python3 tools/amun06_geometry_editable.py
python3 tools/amun06_geometry_textures.py --wine '/home/haker/.var/app/com.valvesoftware.Steam/.local/share/Steam/steamapps/common/Proton 10.0/files/bin/wine64'
python3 tools/amun06_geometry_checks.py
python3 tools/amun06_geometry_handoff.py
```

Python uses existing NumPy, SciPy and Pillow; no dependency updates were made. The scripts read the existing `tools/common.py` helper and the pinned main `.tools/texconv.exe`. Compiler setup copies this worker's existing `build/polish-b/proton-prefix` to the separate `build/amun06-b/proton-prefix`, which is the only prefix written. Missing originals, tools, prior preservation manifests or prefix are concrete dependency failures, not skipped passes. No substitute asset download is permitted.

`integration-spec.json` is the integrator contract. `output-validation.json`, `independent-checks.json`, `resource-checks.json` and `final-provenance.json` record checks and hashes. Editable sources remain under `assets/derived/amun06-b`; generated game files are under `build/amun06-b/game`. They are separate from every prior installed or generated baseline.

User-attested permission for local use is recorded by the integrator. Exact creator, source URL and license terms remain unspecified; this worker does not infer redistribution terms or publish derivatives.
