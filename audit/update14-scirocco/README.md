# Scirocco exterior orientation repair — update 0.14

Owner: `scirocco14`, isolated worktree `visual14-scirocco`.

The update 0.13 repaint read compiler-input geometry, undid its Z reflection, then regenerated normals from its post-compiler triangle indices. On 74,615 of 75,447 imported hull triangles those indices opposed the preserved, originally authored outward normals. The repaint consequently made most of the outer shell face inward. This was a culling defect, not transparent paint: the retained albedo has alpha 255 throughout.

`tools/update14_scirocco_build.py` restores each imported triangle to its preserved outward normal before the existing stripe clipping and normal/tangent calculation. It retains the existing hull shape, detail budget, paint boundaries, PDC supports, and equipment layout. Original model files remain read-only. No arbitrary subdivision or additional hull faces were added.

Only `build/update14-scirocco/game/meshes/expanse12_scirocco_hull.mesh` is a changed integration resource. The three child meshes in that output are exact copies of 0.13 and may be omitted from the overlay. Existing materials, textures, UI, unit, weapon, and skin definitions remain unchanged. The handoff metadata preserves the exact 0.13 mount/equipment/spatial values after checking negligible arithmetic roundoff from reproducing the support rays.

Offline results:

- Official pinned MeshBuilder JSON/binary compile passed, with official facing-grid trailer retained and tangent-only binary repair validated.
- Hull count remains 84,383 triangles; complete assembled ship remains 98,455.
- Against original-derived update 0.12 face normals, 69,890 of 71,764 matching faces were opposed before; zero are opposed after. Coincident STL faces are matched against all coincident candidates to avoid arbitrary nearest-neighbor tie selection.
- Compiled signed volume changes from -4,194,687 to +4,261,861 game units cubed, agreeing with the original STL's positive orientation.
- Actual compiled hull, backface-culled with a depth buffer: nearest exterior surfaces facing outward change from 1.765% to 100% on the starboard sample and 2.456% to 99.998% on the port sample. These are sampled offline views, not a claim that every possible camera angle has been tested.
- Twelve PDCs, one rail, all child mesh binaries, all mount frames, and all equipment positions are preserved.

Commands run in this worktree:

```sh
python3 tools/update14_scirocco_build.py
python3 tools/update14_scirocco_compile.py
python3 tools/update14_scirocco_validate.py
python3 -m py_compile tools/update14_scirocco_build.py tools/update14_scirocco_compile.py tools/update14_scirocco_validate.py
```

The compile first encountered the sandbox Wine local-socket restriction and succeeded when the same bounded offline command ran with escalation. It did not launch Sins or modify installed game/mod files.

Render evidence: `before-after-backface-culled.png` and individual port/starboard images in this audit directory. These are local ignored renders, not source repository assets. They use compiled triangle positions/winding and existing uniform material colors, isolating culling from texture detail. Inward hulls can still fill their silhouette with the distant inside surface; the separately measured nearest-surface facing map detects that failure.

Runtime: NOT RUN. Workstation test: load the new standalone candidate; orbit a freshly spawned Scirocco on both sides, above and below, checking exterior plating and the unchanged tracking PDCs/rail.
