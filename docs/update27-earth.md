# Update 27 private Earth hull additions

Base: `4e8b214b5c1a3429a7dbee9d3e99aefc21cfc793`; reference package `expanse_update26`. This worker owns only new art and private ship definitions. Main integration owns build menus, research prerequisites, tag/manifest registration, localized-text merge and the shared shieldless-passive visibility correction. No existing unit or weapon is overwritten.

## Source and interpretation

- **Nathan Hale:** supplied `leonidas-class-the-expanse-model_files.zip`, `nathanhale.stl`; 22,306 input triangles, no degenerate triangles. The supplied PDF credits RingBuilder and declares public domain. It is one fused print mesh without UVs. [The TV Leonidas reference](https://expanse.fandom.com/wiki/Leonidas-class_battleship) describes an older battleship with two railguns and five drives; this is a secondary source. Its provisional 270 m length is used relative to the existing 46 m Tachi proxy. Twelve modeled PDC batteries represent gameplay coverage rather than asserting the complete screen armament count.
- **Munroe:** supplied `munroe.zip`, `monroe.stl`; 608,432 input triangles, eight actual degenerates removed. The ZIP contains no author/license record; this is recorded as a user-supplied asset under the existing permission authorization. The official licensed [Green Ronin ship preview](https://greenronin.com/blog/2021/06/07/ships-of-the-expanse-the-ships-and-deck-plans/) and [Munroe sheet](https://greenronin.com/wp-content/uploads/2021/06/GRR6607_ShipsOfTheExpanse_Munroe.pdf) describe a 200 m light destroyer: thick hull, a forward keel railgun, extensive defensive cannons and six torpedo tubes (two forward, two dorsal and two ventral). Its requested **cruiser** game classification is a mod adaptation. Four engine mouths and eight PDC stations are taken from the actual supplied mesh. The unrelated three-engine screenshots were not used to change it.

No plot outcomes are used. Health, damage, cost, supply, salvo size and representational weapon counts are gameplay choices, not lore statistics.

## Geometry, surfaces and rigs

The fused print gun tops are cut at actual bearings. Intersection loops are stitched and capped; meshes are never independently recentered. The existing working Truman turret geometry supplies the moving mounts. Nathan Hale gets two 0.75-scale twin rail turrets and twelve 0.65-scale PDCs. Munroe gets eight 0.55-scale PDCs; its detailed forward keel rail remains fixed.

| Hull | Remaining hull triangles | Complete assembled triangles | Engines | Moving mounts |
|---|---:|---:|---:|---|
| Nathan Hale | 62,017 | 79,697 | 5 | 12 PDC + 2 rail |
| Munroe | 254,029 | 259,445 | 4 | 8 PDC |

No broad decimation was needed: replacing Munroe's extremely dense fused PDC tops removed the excess while preserving every remaining original hull triangle. The STL's small relief details and four-drive silhouette remain. New material assignments add steel armor, blue bands, contrasting machinery and light metal panels. New procedural BC7 textures and retained normal/mask resources supply the surface palette. The STL has no original color map to recover. UVs deliberately tile and trigger the SDK's out-of-range UV warning; this is not a missing texture or invalid mesh. Offline previews show base color and triangle geometry, not engine PBR lighting.

Exhaust origins were measured on circular nozzle-mouth planes, not bounding-box ends or an exterior flange. Idle effects attach locally at each mouth; phase effects include the same measured positions. An engine check remains necessary for final plume size and visual orientation.

PDC angular rectangles are selected against the stationary hull and resting rail silhouettes initially on a 2-degree sampling grid, then rechecked against the compiled hull on a 1-degree grid with a 3-degree envelope, while weapon tolerance is 1 degree. Moving sibling PDCs are excluded; this is sampled hull clearance, not a proof over every continuous animation state. Some Hale aft arcs are intentionally narrow because neighboring hull structures obstruct them. Rail yaw remains only ±12 degrees with no elevation tracking; Munroe's fixed rail uses a ±2-degree acquisition cone and requires hull alignment. Fast flanking ships therefore remain useful.

Official MeshBuilder outputs retain their triangle grid and trailer. Source normal/winding agreement is checked; only tangent bytes are repaired after compilation. Every gun attachment has a compiled meshpoint and a matching unit origin.

## Private combat recipe

| Setting | Nathan Hale | Munroe |
|---|---:|---:|
| Game role | Capital | Cruiser |
| Base hull / armor | 10,000 / 3,800 | 5,200 / 2,400 |
| Fleet supply | 155 | 125 |
| Speed | 800 | 950 |
| Build seconds | 90 | 80 |
| Credits / metal / crystal | 3,200 / 800 / 500 | 2,600 / 750 / 400 |
| PDC DPS each | 85 | 85 |
| Rail damage / cooldown | 2,400 each / 60 s | 1,800 / 60 s |
| Torpedoes per volley / interval | 4 / 10 s | 6 / 12 s |
| Magazine / reload | 24 / 120 s | 36 / 120 s |

Hale additionally costs one offense and one defense exotic. Torpedoes reuse the accepted UNN program, target restrictions, destructible projectile entity, 30-second fuel, damage and research response. Capital rail progression bonuses are removed to keep the private weapon values predictable. No second capture mechanic, free colony ability, conventional shield pool or economic income is added. Existing UNN crew voices are reused. Both ships require main integration to supply appropriately priced research access.

## Handoff and evidence

- Tool entry points: `update27_earth_intake.py`, `update27_earth_geometry.py`, `update27_earth_compile.py`, `update27_earth_ui.py`, `update27_earth_gameplay.py`, `update27_earth_validate.py`, `update27_earth_clearance.py`.
- Private game directory: `/run/media/haker/NVME 2/expanse-workers27/earth/build/update27-earth/game`.
- Contracts, source hashes, exact meshpoint/rig layouts, per-mesh compiler results, localization and origins: `audit/update27-earth/`.
- Final explicit game manifest: `audit/update27-earth/game-files-sha256.json`.
- Main calls `changes(base)` to obtain private definitions, localization, source origins and contract. Art file paths resolve from each hashed integration contract's `game_output`, so cherry-picking the scripts does not silently relocate the compiled assets.

Only regular owned game files may be copied; duplicate donor textures must match the accepted package bytes. Do not copy `.tools`, source archives or any Wine prefix. Runtime acceptance still requires live target acquisition, turret animation, nozzle effects, research/build menus, save/reload and multiplayer. Offline passes are recorded separately in `validation.json` and do not claim those runtime tests.

Observed offline: 45 schema checks, native reference/action-value resolution for both ships, compiled winding/frame checks, 125 explicitly hashed game files, zero blocked PDC rays on the final one-degree sweep, and zero blocked rail muzzle rays over their horizontal arcs. Both compiled bow/aft previews were visually inspected.


## Requested detailed drive revision

Post-build `update27_earth_drives.py prepare` then `compile` replaces Nathan Hale's five simple print recesses with actual accepted Truman bell/throat/support-ring geometry, selected from the existing Storm drive component. Original donor UVs, normal frames and textured material remain; no procedural stand-in cone. A 48-plane cylindrical subtraction removes the old inner print surfaces without deleting the surrounding five drive housings. Each new bell is 22 game units across and uniformly scaled; its mouth matches the original measured exhaust center. Hull count is now **62,017**, assembled **79,697**. Gun mounts, firing arcs, plume attachment positions, game dimensions, health and all costs are unchanged.

Munroe already contains approximately **36,000 triangles of bell/throat hardware per drive** in its immediate nozzle regions. A compiled-mesh radial probe finds varied recessed depths and complex central hardware rather than a flat printer cap. Its four existing detailed drives and dense body are retained unchanged; see `munroe-drive-audit.json`. The three-engine reference remains excluded.

After the drive revision, regenerate Hale previews, UI, private recipe audits and final validation/manifest. `drive-revision.json` records exact donor hashes, scale, local clipping dimensions, counts and invariant checks. The update adds actual donor surface texture detail to Hale's engines; new whole-hull photographic texture projection is not claimed.
