# Hull visibility, detail and PDC arcs — 0.14

This separate combined candidate addresses the user-observed 0.13 Scirocco transparency, coarse Raptor/Pella geometry and PDC fire through their own hulls. It includes the complete earlier fleet, voices and music. New runtime tests are **NOT RUN**. Load the new candidate alone; earlier gameplay observations and failed appearance checks remain recorded in [manual results](../audit/manual-results.md).

Scirocco's repaint step recomputed normals from triangle indices that had passed through the compiler coordinate conversion. Most inherited hull faces consequently pointed inward. The correction restores outward orientation before repainting and recompiles the official geometry data. Checking that normals agree with triangle winding is insufficient: both can be consistently inward. New checks compare with the retained source orientation and examine exterior visibility with backface culling. Existing paint, twelve PDC assemblies, rail geometry and attachment frames are retained.

Raptor/Pella detail is recovered from the original STL through less aggressive derivative reduction, including the four engine bells. This restores actual surface detail rather than subdividing the old coarse triangles. Physical scale, nine turret attachments, launcher/exhaust positions, Martian paint, silver Pella materials and the eagle mapping are preserved. Source imperfections may still be visible; larger geometry requires its own fleet performance test.

Assembled Raptor detail increases94,823→272,400 triangles; Pella95,523→273,480. Scirocco stays98,455. The capital spatial bounds receive only a measured rounding-scale correction for restored original extrema: Z center−0.003803→0, Z extent101.572285→101.576088, radius109.005375→109.027493. X/Y extents and collision rank remain unchanged.

Raptor/Pella exterior sampling still finds three narrow grazing/centerline exposures among2,998 surface hits per hull. These are residual seam/detail limitations of the reduced derivative, not a watertightness pass. They are distinct from the broad inward-facing Scirocco shell corrected here.

PDC changes are scoped to the Raptor/Pella mount arcs and any explicitly reviewed firing tolerances. Their nine individual damage/cooldown/range budgets, target categories, missiles, abilities and sounds remain unchanged. Restricting arcs reduces coverage, so blocked guns must hand targets off to suitably facing mounts. Offline sampled rays do not establish continuous hull avoidance or the engine's actual angle/tolerance behavior.

All mounts retain a−85° pitch minimum. Pitch maximum becomes−23° for mounts0/1,−9° for mount2, and−7° for mounts3–8. Mount3 yaw is restricted to[−180°,136°], mirror mount4 to[−136°,180°]; other yaw arcs remain full. Both aiming tolerances become1°, down from7.5°. Average allowed solid angle is about72.6% of the former rectangle; that is not a combat DPS prediction. Each restored hull passed2,137,005 final grid rays plus180,000 random rays with a±3° direction-error envelope. A separate check against the actual archived0.13 hull reproduces2,008 direct blocked rays per ship. See the [arc audit](../audit/update14-arcs/README.md) for coordinate evidence and sampling limits.

## Checkpoint and ownership

Starting source commit: `29a4f13cc9413b72a4f606855a3fd0c3273b84b5`, clean on `main`. Pinned SDK schema commit remains `8e061033afe53b1393eaefd56617a3fd041eeb5f`; game2.0.3(318), Steam25127248 and SDK24092025 remain unchanged. The current installed and enabled0.13 package matches the built0.13 tree. User testing changed the enabled settings since0.13 preparation; this assignment snapshots and preserves that current state.

Preserved0.13 ZIP SHA-256: `3b7904e215a051cee3c633f4b0d470cc0a536d1b1ea49f4bcde877ce35d560dc`; tree SHA-256: `465ed0cf0b3ab2801ecd1fbb1d7ea0d0d56b98c16525129f17200422e77a0568`.

The installed name-only baseline tree remains `599ec704a76198a37e5230da722764b11ea17590cd5da6b8ec85aea668630c37`; installed visual baseline remains `c3f88816cbd303df5da78f4c8e9f1a7e0ba5d1219d8ccfd9a3827933be3fda68`. All protected paths and file hashes are in [the checkpoint](../audit/update14/checkpoint.json). Original archives, supplied STL files and extracted masters are untouched.

Main owns `tools/build_update14.py`, `audit/update14`, shared unit/weapon integration and documentation. Three isolated workers own `tools/update14_scirocco*` / `audit/update14-scirocco`, `tools/update14_hulls*` / `audit/update14-hulls`, and `tools/update14_pdc*` / `audit/update14-arcs`. Their worktrees and output directories are separate under `expanse-workers/visual14-*`. [Asset attribution](../ASSET-SOURCES.md) carries forward. Only source scripts and text audits are pushed; models, textures, recordings, renders and packages remain ignored.

## Reproduction and workstation order

The package builder consumes reviewed local mesh and arc contracts, fails if required inputs change, and refuses existing output paths. It never installs, enables or launches the mod. Worker reports contain asset reproduction commands. Do not regenerate frozen packages merely to validate them.

```sh
python3 tools/build_update14.py
python3 tools/build_update14.py --validate-only
```

`--package-existing` validates an already assembled candidate and creates its archive, refusing an existing ZIP. `--validate-only` checks the package directory and does not require or recreate its ZIP. All new inputs are listed and hashed in `audit/update14/integration-inputs.json` and `reviewed-inputs.json`.

At the workstation, extract `build/experiments/expanse_update14.zip` into a new `expanse_update14` folder under Proton's `steamapps/compatdata/1575940/pfx/drive_c/users/steamuser/AppData/Local/sins2/mods`. `.mod_meta_data` must be immediately inside that folder. Enable only **The Expanse — 0.14 HULL & FIRING ARC FIX** among Expanse variants, then apply in a new test game.

1. Load/apply and inspect Scirocco from both sides, above and below; compare Raptor/Pella plating and all four engine bells with0.13. Confirm paint, eagle and attached turrets remain visible.
2. Circle targets and incoming torpedoes around Raptor/Pella at different elevations. Confirm near-side guns track and fire, obstructed guns hold fire, and shots originate at barrel tips. Inspect arc edges and blind spots, then verify unchanged damage/cadence.
3. Save/reload during combat and compare one capital with the intended mixed fleet at identical camera/settings. Record frame times and logs; additional triangles and restricted coverage need runtime acceptance.

These are U14-1 through U14-3 in the [manual checklist](manual-test-checklist.md). Earlier pending ability, shield, supply and performance tests remain pending.

## Completed package checks

The929-file candidate passes20 changed-entity schema checks, three binary mesh checks, exact retained attachment/material identities, measured unit bounds, and2,694 references across nine ship graphs. Exact comparison against0.13 permits only three hull binaries, two unit arc/bounds edits, eighteen weapon aiming-tolerance edits, metadata and attribution. Every other file, including all skins, audio, abilities, damage, cooldowns, target filters and manifests, is byte-identical.

Both compiled capital hulls exactly match the ray-tested geometry after order/winding-independent float32 comparison; all18 compiled PDC frames match the unit basis. The sampled exterior and ray limitations above remain applicable. Scirocco's orientation check finds zero opposed faces among71,764 source-matched triangles, versus69,890 before. Its compiled backface-culling samples show99.998–100% nearest-surface outward coverage.

All21 protected trees,21 previous ZIPs, supplied reference/original hashes and current enabled settings remain unchanged. All62 pinned schemas and527 recorded installed references match. Source syntax, source diff checks, standalone package validation and ZIP-to-directory verification passed. New runtime checks remain NOT RUN.

Package: `build/experiments/expanse_update14.zip`. ZIP SHA-256: `1826693d5fd007c751b8a4ee48eb4f09433c5526eb873e44befac090bbf3c524`; tree SHA-256: `758fa38ffa17fe132d786fd77d2c9445efdc782607b39e028f353a0a63b3f0b1`. [Package summary](../audit/update14/package-summary.json) and [validation results](../audit/update14/package-validation.json) record actual checks. The adjacent ignored `.provenance.json` records the final source commit and exact local dependencies. Nothing was installed or enabled by the agent.
