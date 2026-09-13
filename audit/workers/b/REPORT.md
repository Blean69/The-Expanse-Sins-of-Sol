# Worker B: one dorsal Tachi PDC candidate

**CANDIDATE ONLY — NOT READY TO PACKAGE. Runtime tests NOT RUN.** Official JSON/binary conversion and geometric checks passed, but the generated tangent-frame gate failed. No installation, baseline rebuild, game launch, commit, or publication was performed.

Owned outputs: `tools/tachi_rig_experiment.py`, `tools/tachi_verify_compiler.py`, `audit/workers/b/`, ignored `assets/derived/worker-b/` and `build/worker-b/` in this worker's isolated worktree. Shared assets, normalized baseline, rig candidates, pinned SDK, and installed data were read-only. Dependencies are explicit command arguments, not assumed to exist in another conversation.

## Corrected mechanical partition

The representative assembly is existing dorsal rig index 1, initially facing ship aft. Inspection of the existing normalized optimized model and old candidate views showed that node493 is the small sphere above the gun, not the mechanical turret pivot. The previous candidate also placed deployment linkage in the pitch mesh and treated the entire disconnected body mesh as one moving part. Those old candidate/master files remain unchanged.

This derivative keeps fixed deployment linkage nodes **6, 513, 515, 517, 519** in the hull. Body node475 contains disconnected lower platform and upper housing: **84** lower triangles enter the yaw mesh and **96** upper triangles enter the pitch mesh, separated at normalized Y=2.5 with **zero crossing triangles**. This partitions existing triangles without cutting, decimating, or reimporting geometry. Yaw also contains holder nodes497/499. Pitch also contains nodes491/477/485/487/489/493/495. The generated metadata records all node/triangle ownership. Five other complete PDCs stay static.

Triangle counts: hull **13,945**, yaw/base **138**, pitch/barrel **539**, total **14,622**, exactly the frozen visual baseline. The 677 moving triangles do not remain under the turret in the experimental hull. Rest-pose recomposition is exact within floating-point tolerance; no master or baseline geometry was removed.

The game-coordinate frame has local +Z facing hull -Z, local +Y facing hull +Y, and local +X facing hull -X. It is orthonormal with determinant +1. Scale is inherited unchanged from the recorded normalized model, 0.21847177771839144 source-to-game units. Editable derivative glTF files use game coordinates; separate compiler glTF files compensate MeshBuilder's Z reflection, normal/tangent signs, winding, and attachment coordinates.

Yaw pivot is the named lower-platform/body origin **[-0.0296463562, 1.8523238408, -19.4356501639]**. Pitch pivot is the holder-detail pin bounds midpoint, centered on the body's X: **[-0.0296463562, 3.2287776004, -19.6229523509]**. These are geometry-based mechanical estimates, not authored/engine-verified pivots. Barrel position in yaw coordinates is **[0, 1.3764537596, 0.1873021870]**. The one cluster muzzle, estimated from existing optimized barrel tips, is **[-0.0000117219, 0.4073111039, 3.7885186082]** relative to pitch pivot. Hull-coordinate muzzle is in `mount-metadata.json`.

The metadata's yaw -45..45 and pitch -20..0 arcs are deliberately limited experimental bounds. Pitch sign, tracking, hull occlusion, and clearance remain unverified. The annotated side/front view shows actual triangles, fixed deployment geometry, pivots, and muzzle. It is not a runtime image.

## Integration specification, held pending shading fix

Use exactly one copy of installed `trader_antifighter_frigate_point_defense_autocannon.weapon` under mod-specific ID `expanse_tachi_one_pdc_garda`. Change only its turret barrel/muzzle coordinates from `mount-metadata.json`; keep range, damage, targeting groups, cooldown, effects and acquisition logic unchanged. This isolates aiming from the unproven dual-purpose PDC experiment. Preserve the Cobalt autocannon and fixed muzzle coordinates if the integrator retains its existing weapon; the one added PDC receives one weapon entry and one firing budget.

Use hull mesh `expanse_tachi_one_pdc_hull` and the exact `mount`, `turret_override`, and `skin_alias_map` records. Installed Garda meshpoint conventions are reproduced: hull `child.pdturret_mount_0`; base `child.pdturret_barrel_0`; barrel `turret_muzzle.0`. Official binary output verifies those coordinates and the hull mount's [-X,+Y,-Z] rotation. Add the four Garda PDC `effect_alias_bindings` from the installed Garda skin so the copied weapon's existing effects resolve. No new effects/audio are needed.

The compiler emits six material IDs: four hull-prefixed IDs and one each for base/barrel. Copy the existing corresponding `mcrn_tachi_{material,primary,secondary,texts}.mesh_material` definitions under these **emitted** names. Reuse existing texture IDs/files in the experimental package. Do not rebuild textures, rewrite the frozen baseline material files, or copy vanilla weapon/effect assets unnecessarily. Full generated IDs and hashes are in metadata.

## Checks actually run

- Python syntax compilation: PASS.
- Existing normalized and candidate dependencies present: PASS.
- Exact triangle conservation and no duplicated static moving triangles: PASS.
- Empty-gap body partition, axis determinant and rest-pose reconstruction: PASS.
- Official pinned SDK MeshBuilder JSON and binary generation for all three meshes: PASS, using an isolated copied Proton prefix in `build/worker-b/proton-prefix`. Initial sandbox invocation failed because Wine sockets were blocked; the headless compiler subsequently ran under approved escalation. No game's prefix was used.
- Official emitted triangle counts and all meshpoint positions: PASS.
- All indexed compiled positions versus editable outputs: PASS, maximum <5.1e-7 after accounting for compiler primitive order and winding.
- Reassembled compiled positions/normals/UV versus frozen baseline: PASS across **43,866 indexed corners**, maximum combined error **1.815e-6**. Normals and UV exactly match to JSON precision.
- Compiler-input hull positions/normals/tangents/UV versus baseline input: PASS, maximum attribute error **2.463e-6**.
- Binary/JSON vertices, normals, tangents and UV parity: PASS, maximum **5.1e-7**.
- Read-only required input hashes unchanged during generation: PASS.
- **Generated tangent frames: FAIL. Emitted tangent equality is NOT PRESERVED.**

The installed SDK shader source, `Shaders/mesh/mesh_pbr_utility.hlsli:152`, explicitly documents MeshBuilder-generated Mikk tangents. Retaining original vertex context did not resolve the emitted defects. At tolerance 2e-5:

| Output | Zero tangent indexed corners | Nonorthogonal indexed corners | Maximum abs(normal dot tangent) |
|---|---:|---:|---:|
| Frozen baseline (read only) | 432 | 422 | 1.0 |
| Experimental hull | 412 | 416 | 1.0 |
| Experimental base | 2 | 0 | 0.000001156 |
| Experimental barrel | 18 | 7 | 0.025680687 |

All normals are unit within tolerance, all vertices are finite, and tangent signs are ±1. The zero-tangent total is inherited in aggregate (432), while nonorthogonal count increases from 422 to423. Count agreement does not certify per-corner equivalence or acceptable shading. There are no zero-area geometric triangles under a 1e-10 threshold; some affected UV triangles are degenerate, but that does not explain every invalid frame. Exact per-output evidence is in `compiler-geometry-check.json`. That checker intentionally exits **1** and marks package gate **BLOCKED**. Do not silently weaken the gate or claim output-frame validation passed. Existing baseline shading is also a newly discovered runtime risk; leave frozen files unchanged and add explicit normal-map inspection to its existing runtime checklist.

The bounded assignment stops at this blocker. A later export/tangent repair should preserve geometry and source UVs, verify the relevant official converter behavior, and repeat frame checks before this rig is packaged. No broader exporter redesign or new optimization pass was attempted here.

## Reproduction

Run from the worker worktree, with unchanged local ignored inputs:

```bash
OPENBLAS_NUM_THREADS=1 python3 tools/tachi_rig_experiment.py \
  --source-root '/run/media/haker/NVME 2/expanse-mod' \
  --sdk '/run/media/haker/NVME 2/SteamLibrary/steamapps/common/Sins of a Solar Empire II - Mod Tools' \
  --wine '/home/haker/.var/app/com.valvesoftware.Steam/.local/share/Steam/steamapps/common/Proton 10.0/files/bin/wine64' \
  --compile
OPENBLAS_NUM_THREADS=1 python3 tools/tachi_verify_compiler.py \
  --source-root '/run/media/haker/NVME 2/expanse-mod'
```

The second command currently fails the documented frame gate. It requires existing compiler outputs and locally installed SciPy; missing dependencies fail explicitly, never count as PASS. Generation without `--compile` only prepares candidate glTFs and geometry metadata and must not be reported as a compiled pass. Do not run these scripts in the main frozen asset tree during this assignment.

## Workstation gate and extension

After the shading blocker is resolved and main integration passes references/schemas, test this rig separately from dual-purpose targeting: first inspect idle/rest alignment and no duplicate geometry; place hostile strikecraft/torpedoes aft/above the ship within the narrow mount arcs; observe yaw, pitch, tracking and muzzle flashes from several camera angles; inspect normal-map appearance; repeat while moving and after save/reload. The unchanged Garda PDC does not validate ship targeting, mixed-order interception priority, or six-gun behavior.

Extend to the other five assemblies only after this one is observed working. Map each assembly's actual lower platform, pitch housing and fixed deployment linkages individually; do not reuse the invalid sphere-pivot/nearest-node grouping automatically. Derive each local orientation, repeat triangle partition/recomposition and frame checks, add one mount and one firing budget per assembly, then measure individual and overlapping firing arcs. No deployment animation is introduced.
