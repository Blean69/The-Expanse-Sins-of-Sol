# Murphy destroyer art handoff

This is an art-only, SDK-compiled UNN escort candidate. It adds no unit, weapon, cost, research, faction, manifest, save-format, or capture-system changes. Main integration owns those definitions.

The supplied model is Qwerty1998's [UNN Murphy Class Destroyer](https://www.thingiverse.com/thing:7350801). Its README explicitly describes a made-up UNN ship. The archive records CC Attribution-ShareAlike with no version; the exact text and original ZIP/STL hashes are preserved in `audit/update23-murphy/integration-spec.json`. No stand, UV map, material, or animation was supplied. All **8,302 original triangles** remain; there is no decimation or subdivision.

The licensed RPG class is a lightly protected destroyer rather than a second Truman. A secondary reference gives 102 m, forward/aft railguns, two torpedo tubes, PDC coverage, and two drives. The supplied fan model has **one** modeled drive and is not evidence for an exact licensed-RPG design. Its provisional scale is 102 m using the existing Tachi's 104.9869586 game units / 46 m. Four PDCs, their locations, the new collars, gray/navy paint, and the engine ring are explicitly mod adaptations. The reserve rail origins are attachment points only: this package does not claim to add two modeled railguns. [RPG distributor preview](https://d1vzi28wh99zvq.cloudfront.net/pdf_previews/328833-sample.pdf), [secondary Murphy class reference](https://expanse.fandom.com/wiki/Murphy-class_light_destroyer). The full licensed RPG chapter was not directly inspected.

## Files to integrate

The complete art package is the **20 regular files / 18,794,777 bytes** under:

`build/update23-murphy/game`

Copy only those explicit regular game files. The game package contains no Wine prefix or symlinks. `integration-spec.json` lists every relative filename and SHA-256.

- Hull: `expanse23_murphy_hull.mesh`, **9,454 triangles**, including 1,152 added support, collar, and engine-ring triangles.
- Four biaxial PDCs: private byte-identical aliases of the accepted Morrigan-size base (138 triangles) and barrel (539). Their donor material and texture dependencies are included unchanged.
- Total assembled model: **12,162 triangles**.
- Opaque gray/navy industrial panel textures; no team-color or shield mask introduced.
- One private blue idle plume adapted from the accepted Truman effect at half spatial scale. All referenced stock textures resolve against the installed game. A six-engine absolute Truman phase effect is intentionally not reused.

Use `audit/update23-murphy/integration-spec.json` for the exact spatial box, radius, PDC pivot transforms, native arcs, turret overrides, mesh alias bindings, torpedo positions, exhaust point, and skin fragment. The four weapon entries use `child.expanse23_murphy_pdc_0` through `_3`; the complete small-turret geometry offsets are in each rig's `turret_override`. Weapon definitions call the corresponding field `turret`.

Each mount lies outside a global hull bounding plane and has a short modeled support connected to an actual first-hit hull surface. Restrict PDC pitch to **−85 through 0 degrees** and yaw to **−180 through 180 degrees**, using the existing native negative-pitch outward convention. These limits intentionally prevent aiming inward through the hull. Do not inherit the donor's +5-degree inward margin.

The two forward tube origins are `weapon.torpedo.0/1`. `exhaust.0` retains the accepted Truman rear-facing meshpoint rotation. `weapon.rail.0/1` are optional reserved forward/aft origins, not new railguns or damage recommendations. For initial gameplay the parent can use the established Earth PDC family and UNN light torpedo definitions without changing their shared balance.

## Observed checks

`audit/update23-murphy/offline-validation.json` records:

- Official MeshBuilder binary/JSON conversion with the official triangle-facing grid.
- All 8,302 source faces retained, no source degenerate triangles, and zero compiled opposed winding triangles.
- Every named point's position and rotation matches its authored transform.
- Source-frame matching error below 0.000004 game units; tangent-only repair leaves the official index/grid/trailer bytes unchanged.
- All donor game bytes preserved, all material/DDS dependencies resolved, all packaged hashes verified, and zero symlinks.
- **5,256 sampled PDC firing directions** remain in the outward hemisphere with their muzzles outside the hull bounding planes. This is an offline geometric check, not a game targeting result.
- Actual packaged mesh/DDS previews were rendered and inspected from bow and aft: `compiled-game-bow-preview.png` and `compiled-game-preview.png`.

**Not run:** in-game acquisition, interpolation and firing; visible PDC motion and hull obstruction; exhaust appearance; ally/enemy filters; save/reload; multiplayer. The screenshot renderer does not simulate the Sins ship shader or engine targeting.

## Rebuild

Use the existing dependency Python and run, in order:

```sh
'/run/media/haker/NVME 2/expanse-mod/.tools/venv/bin/python' tools/update23_murphy_art.py prepare
'/run/media/haker/NVME 2/expanse-mod/.tools/venv/bin/python' tools/update23_murphy_art.py compile
'/run/media/haker/NVME 2/expanse-mod/.tools/venv/bin/python' tools/update23_murphy_art.py preview
'/run/media/haker/NVME 2/expanse-mod/.tools/venv/bin/python' tools/update23_murphy_validate.py
```

The `compile` stage needs local Wine IPC, which the sandbox blocks; the allowed escalation ran existing local SDK and texconv binaries only. The established build prefix is used in place and never copied. Originals and installed game data remain read-only.
