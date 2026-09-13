# Raptor/Pella source-detail restoration (hulls14)

Built in the isolated `visual14-hulls` worktree from checkpoint `29a4f13cc9413b72a4f606855a3fd0c3273b84b5`. Originals, prior outputs, installed mods, game files, SDK, and pinned schemas were read-only. No runtime test was performed.

The supplied Raptor STL has 1,513,390 triangles. The previous reduction removed important hull recesses and engine curvature. This pass returns to its preserved welded source, retains the same static-gun removals, and allocates 180,000 triangles to the remaining hull plus 16,000 per actual engine bell. Actual prepaint output is 243,749 triangles. These are recovered source features, not subdivision of the low-detail mesh. Meshoptimizer error limits are 0.0007 for hull and 0.00015 for each engine; measured results are in each optimization.json.

| Variant | Previous hull | Restored hull | Assembled with unchanged 9 PDCs |
| --- | ---: | ---: | ---: |
| Raptor |88,730 |266,307 |272,400 |
| Pella |89,430 |267,387 |273,480 |

Paint-boundary clipping adds triangles without changing the existing surface. The gray/orange Raptor and silver Pella material identities stay exact. Pella's same generated Free Navy emblem is projected onto the same existing dorsal forward plating; its existing game texture/material resources are reused. Every compiled meshpoint name, position, rotation and bone index matches 0.13 exactly. Existing rigs and all torpedo, exhaust and boarding coordinates remain exact; only two hull.mesh files are supplied for overlay.

The restored extremal vertices require a small bounding-volume refresh for both ships: Z box center−0.00380325317→0, Z half-extent101.57228469849→101.57608795166, radius109.00537513136→109.02749347259. X/Y half-extents 34.78532050993 stay unchanged. Neutral assembled geometry, including the unchanged PDCs, fits those measured bounds. Main integrator owns unit spatial and firing arc edits.

## Checks actually run

- Source archive SHA256 remains `c06878f57e5b9f04043793226f8c6a06b082848273ea6fc9e9369f474c8dedd6`; original and restored source signed volumes are positive.
- Pinned official MeshBuilder JSON/binary compilation, input winding correction based on actual output, final official facing grid, and tangent-only repair: pass for both hulls. Official binary trailer bytes remain unchanged by tangent repair; zero opposed stored-normal/triangle-winding faces and zero tangent fallbacks.
- Exact previous compiled material names and meshpoint transforms: pass. Triangle totals, current binary SHA256, finite authored tangent correspondence and assembled bounds: pass.
- Independent six-sided exterior grid: 2,998 first-surface hits per hull; 2,995 face outward and 3 are residual narrow grazing/centerline exposures. Two rays lie precisely on the bow Y=0 seam; one hits a side detail approximately 0.011 game units behind its source surface. Untouched-source rays hit outward faces, so these are residual reduction exposures, not claimed original apertures. This is **not** a watertightness pass. Details are retained in exterior-check.json, exterior-detail.json and source-orientation.json.
- Backface-culled aft and oblique comparisons were rendered and visually inspected. The restored rings and recesses are substantially clearer. PNGs are ignored local review artifacts; no derivative model or art is included in the source push.
- `python3 -m py_compile tools/update14_hulls*.py` passed.

Initial compiler attempts encountered sandbox-local Wine socket restrictions and required the existing authorized local compiler escalation. A preliminary Pella grid exceeded the old 300-second wrapper timeout; it was retried with 1200 seconds. An obsolete Raptor preliminary binary pass was stopped, retaining completed JSON. The final wrapper generates the expensive official grid only for final binary output, avoiding redundant diagnostic JSON grids. All final compilation gates passed.

## Reproduction and outputs

Run in an isolated worktree containing the scripts. Read-only dependencies are the `weapon-behavior/assets/derived/update12-a` welded intake and metadata, preserved Tachi donor rig under `tachi-one-pdc`, existing 0.13 package/materials, `.tools/libmeshoptimizer.so`, and pinned SDK/Wine recorded in the scripts. No network or new dependencies are required.

```bash
python3 tools/update14_hulls_geometry.py --variant raptor
python3 tools/update14_hulls_geometry.py --variant pella
python3 tools/update14_hulls_emblem.py
python3 tools/update14_hulls_compile.py --variant raptor
python3 tools/update14_hulls_compile.py --variant pella
python3 tools/update14_hulls_review.py
python3 tools/update14_hulls_source_audit.py
python3 tools/update14_hulls_finalize.py
```

Generated assets are under `assets/derived/update14-hulls/<variant>`, compiled resources under `build/update14-hulls/<variant>/game/meshes`, and text audits under `audit/update14-hulls`. Main integrator separately binds final binary geometry to PDC arc ray tests.

Runtime review: close rear/bow views of Raptor and Pella, inspect the narrow bow seam and side detail, check both plume alignment and unchanged paint/emblem, then compare close-up and fleet performance. New triangle budgets have no runtime performance result yet.
