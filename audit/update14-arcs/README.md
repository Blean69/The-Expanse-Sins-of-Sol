# Pella/Raptor outgoing PDC rays — update 0.14

Owner: `arcs14`. Main integrator owns actual unit and weapon edits. This directory proposes only unit mount arcs and weapon aiming tolerances for the existing nine PDCs on each ship. No package, installed mod, original model, damage, range, cooldown, burst pattern, targeting group or missile-interception definition was changed here.

`integration-spec.json` contains ready-to-apply `mount_arcs` and `weapon_tolerances`; the two `*-proposal.json` files contain per-mount evidence, exact input hashes and reproducible assumptions. Both restored hulls were tested independently, including Pella's emblem paint splits. The comparison called `old_*` in those proposals uses **old arcs against the restored hull**; `baseline-reproduction.json` separately reproduces the issue on the archived 0.13 hulls themselves.

## Proposed limits

Both ships use the same restrictions; each retains its existing mount position, basis, moving parts and local muzzle offset. Pitch minimum remains −85°.

| Mount indices | Yaw minimum | Yaw maximum | Pitch maximum |
|---|---:|---:|---:|
| 0, 1 | −180° | 180° | −23° |
| 2 | −180° | 180° | −9° |
| 3 | −180° | 136° | −7° |
| 4 | −136° | 180° | −7° |
| 5, 6, 7, 8 | −180° | 180° | −7° |

Pitch/yaw firing tolerance changes from 7.5° to 1°. This is an aiming restriction: the gun must align more closely before it shoots. While slewing, it may therefore fire later. The average allowed solid angle is approximately 72.6% of the old rectangle; this is an angular coverage comparison, **not** a prediction of combat DPS. No firing budget changed.

## Coordinate evidence and ray method

Game-space forward is +Z. A mount's local right is `cross(up, forward)`. With these three columns forming `B`, a pose uses `B · Ry(yaw) · Rx(pitch)`. Positive pitch rotates forward toward local −Y (into a surface whose outward direction is mount `up`); negative pitch elevates outward.

The installed `trader_antifighter_frigate.unit` corroborates the signs: its forward dorsal port gun at X=−10.803879 permits yaw [−160°,10°], while its matching starboard gun at X=10.778546 permits [−10°,160°]. Both use forward +Z/up +Y and pitch [−70°,15°]. This supports negative yaw pointing port and negative pitch pointing away from the dorsal hull. The pinned native unit schema supports rectangular `yaw_arc`/`pitch_arc`; the native weapon schema supports the two nonnegative firing tolerances. No automatic hull-occlusion flag was invented. Engine source is unavailable, so actual game tracking remains a workstation check.

An entirely negative pitch interval is also an installed pattern: `advent_carrier_capital_ship.unit` has point-defense pitch [−90°,−5°], `vasari_starbase.unit` has [−55°,−7°], and `advent_battle_capital_ship.unit` has [−85°,−10°]. These definitions omit `initial_angle`, as the proposed mounts do.

For each pose the actual muzzle is computed as:

`pivot + B · Ry(yaw) · (barrel_position + Rx(pitch) · muzzle_position)`.

The tested ray starts there and extends the unchanged 4,500-unit range in the aimed direction. This catches a distant nacelle or hull face beyond the barrel tip; the earlier short barrel-centerline check could not. Two-sided triangle intersection avoids accidentally hiding an obstruction because its face winding is reversed. The C++ BVH uses double precision, with analytic hit/miss/range tests and an independent brute-force NumPy nearest-hit comparison on 64 rays per hull (15 blocked, all identical).

Search uses a 2° pose grid and a 2° inset from obstructed rows/columns. Final checking uses a separate 1° grid, including endpoints, with nine yaw/pitch direction offsets covering −3°, 0°, +3° per axis from the actual muzzle. That envelope exceeds the proposed 1° firing tolerance. Each ship passed 2,137,005 final grid rays and 180,000 additional deterministic random rays between grid points with continuous direction offsets in [−3°,3°]. There were zero hits. Old arcs/tolerance on each restored hull hit it at 4,447 sampled poses.

The archived 0.13 meshes reproduce 2,008 obstructed center-direction poses per ship even without firing tolerance, or 4,410 obstructed poses with the original tolerance. Those old compiled mesh bytes were checked against the original worker output before reading its repaired JSON. This confirms a real outgoing-ray obstruction rather than merely a hypothetical tolerance issue. `final-compiled-geometry.json` binds each restored NPZ to the delivered binary through an order- and winding-independent comparison of every triangle's coordinates and checks all nine compiled mount frames against the native unit vectors.

## Limits and smallest runtime check

This is sampled line-of-fire evidence, not continuous swept-volume proof. It does not test other moving turrets, full barrel mesh collision, engine target-point convergence at contact distance, game interpolation or obstruction by ships other than the firing ship. Runtime is NOT RUN.

Spawn one Raptor and one Pella. Orbit a small hostile around each at close range and above/below the hull; inspect mounts 0/1 beside the bow bays and 3/4 near the forward nacelle obstruction first. Their guns should cease fire as targets enter the excluded hull directions, resume on clear sides, and still intercept torpedoes. A visible shot through a hull calls for that mount's target angle and screenshot; do not widen all arcs to recover coverage.

## Reproduce

Run `tools/update14_pdc_arcs.py` twice with `--variant raptor` / `pella`, `--hull` pointing to the corresponding preserved restored `hull-ray.npz`, `--baseline` to the frozen `expanse_update13`, and separate `--audit`/`--build` paths. Exact hull input paths are in the proposal JSON. Run `tools/update14_pdc_baseline.py` to reproduce the original defect against the byte-matched archived 0.13 mesh and its repaired compiler JSON. Generated BVH source/shared library stay in the ignored build directory.
