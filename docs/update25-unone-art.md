# UN One diplomatic hull art

Art-only package for an unarmed diplomatic/support ship. Main integration owns unit class, survivability, costs, abilities, research, and availability. No weapon, unit, or research definitions are included.

## Source and assembly

The supplied ZIP is Lionel SAVOCA's UN One interpretation. The included assembly PDF records **CC BY-SA 4.0** and describes a 52 cm model at 1:100. This implies approximately **52 m as a model-design estimate**, not verified TV dimensions. At the existing Tachi conversion of 104.9869586 game units / 46 m, this hull is about **118.68 game units long**.

The full exterior and exposed connector covers retain their common exported coordinates. Body seams at source X=110, −60, and −147 line up to within 0.001 game units. The mirrored wings remain at their original opposite Y positions. No part was centered independently.

Retained: **117,822 source triangles**, comprising the exterior shells, engines, rear covers, and exposed front/rear/wing connector inserts. No decimation or subdivision. Excluded: printing stand, stand interface, and the repeated internal C1/R1 print pegs. The last two are internal physical-print fasteners, not external ship detail. Original archives and source geometry were not modified. Exact per-part hashes, bounds, and inclusion decisions are in `audit/update25-unone/integration-spec.json`.

The new white/gray diplomatic palette has blue wing tips, subdued bronze side bands, dark blue emissive windows, and a longitudinal UN ONE legend. These are original mod textures applied through newly generated UV coordinates. Source embossed details remain in the mesh. The UV projection is constant within each triangle to avoid stretched material seams. Source base color alpha is explicitly opaque; BC7 may quantize alpha to 254/255, and no cutout/transparent material is used.

Two small engine-glow patches follow first-hit intersections on exposed rear faces of the actual engine block; they are visual interpretation of the supplied model, not a claim about a canon engine count. The package adds only **4 glow triangles**, bringing the compiled hull to **117,826 triangles**. Two rear-facing exhaust origins accompany a restrained private blue idle plume. No copied six-engine absolute phase effect is included.

## Integration

Complete game art directory:

`build/update25-unone/game`

It contains **17 explicit regular files**, with no symlinks or Wine prefix. `integration-spec.json` records every filename and SHA-256, the native spatial box/radius, exact meshpoints, and the skin fragment.

- Mesh: `expanse25_unone_hull`.
- Points: `center`, `above`, `aura`, `exhaust.0`, `exhaust.1`.
- No weapon points, child turret aliases, or armaments.
- Private idle effect: `expanse25_unone_idle_plume`, based on the accepted blue Truman idle effect at 0.12 spatial scale per exhaust attachment. Use normal hyperspace effects until a ship-specific phase plume is authored.
- `skin_contract.unit_mesh` and `skin_contract.exhaust_effects` use established native shapes. Main supplies GUI, voices, camera distances, death sequence, and gameplay.

## Observed validation

Official SDK binary/JSON conversion and triangle-facing grid generation succeeded. All selected source faces remain. All named point positions and rotations match; no compiled winding opposes stored normals. Source-frame error is below 0.000003 game units. Tangent-only repair preserved all official index/grid/trailer bytes. There were 55,352 initial compiler winding corrections, followed by a fresh official grid build.

Material/DDS and stock particle references resolve; base color maps remain effectively opaque; all output hashes match; no symlinks, weapon points, or gameplay definitions occur in the package. The main body interface checks pass. Bow, aft, and top previews use the actual packaged binary mesh and DDS textures and were visually inspected.

**Not tested:** in-game ship shading, emissive windows, exhaust animation, hyperspace appearance, save/reload, multiplayer, or diplomatic/support gameplay. Previews do not simulate the Sins ship shader.

## Rebuild

Run `tools/update25_unone_art.py prepare`, then `compile`, then `preview`, using the existing `/run/media/haker/NVME 2/expanse-mod/.tools/venv/bin/python`. Finish with `tools/update25_unone_validate.py`. The tool reuses the already committed Murphy mesh-frame/export helpers. Only the compile stage requires local Wine IPC outside the sandbox; it invokes already installed SDK/texconv binaries and uses the existing build prefix in place. It does not copy the prefix, install software, or modify the game.
