# Capital fleet update 0.12

`expanse_update12` is a separate combined package containing 0.11 plus three capital choices and the Sunflare scout. **New runtime tests remain NOT RUN.** Earlier accepted movement, Rocinante, cloak, boarding, explosion and audio observations belong to the packages on which the user reported them.

## Ships and fleet budget

| Ship | Supply | Level-one hull / armor | Speed | Physical PDCs | Normal torpedo magazine |
|---|---:|---:|---:|---:|---|
| MCRN Raptor | 150 | 4,500 / 2,600 | 1,150 | 9 | 18 light; three every 10s |
| Pella, unique Free Navy hero | 200 | 5,400 / 3,100 | 1,150 | 9 | 18 light; three every 10s |
| MCRN Scirocco | 200 | 6,500 / 3,600 | 1,250 | 12 | 20 light; five every 10s; separate five heavy, one every 20s |
| Sunflare racing pinnace | 5 | 100 / 0 | 3,000 | 0 | Unarmed |

The capitals use ordinary TEC capital construction, native experience and four component slots. They are temporarily available to all three existing TEC player definitions. Pella has a separate one-per-player construction limit; Donnager still shares the normal titan limit. These are local prototype values, not a fleet-wide damage rebalance. Existing ship, weapon and audio assets remain unchanged. The shared TEC scout definition also changes applicable neutral/garrison scouts.

The previous 2,000-supply example is now buildable: one Donnager (500), four regular Raptors (600), ten Tachis (550) and fourteen Morrigans (350). To include unique Pella, replace one Raptor and two Morrigans: one Donnager, three Raptors, one Pella, ten Tachis and twelve Morrigans still total 2,000. Scirocco costs the same supply as Pella. This is a composition budget, not a claim that it is competitively balanced or a verified lore census.

Each new PDC has **one independent 14-damage / 0.25-second firing budget**, zero penetration and 4,500 range. Raw DPS is 56 per mount, 504 across nine guns and 672 across twelve, only when every gun can bear. Native capital experience and upgrades subsequently change damage/cooldown. The accepted dual-purpose filter and firing audio are reused. Interception priority while attacking a ship still needs an observed test; eligible targets alone do not prove priority or damage effectiveness.

Scirocco has one source-derived rail assembly: 4,000 raw damage, 1,250 penetration, 15s cooldown. Its hull support raises the existing housing eight game units to permit a sampled ±15° gimbal sweep without intersecting the hull. This is an authored mounting adaptation, not a verified animation from the show. There is no independent barrel-pitch joint. No railguns were added to the supplied TV-style Raptor/Pella hull.

Light torpedoes retain accepted Martian damage, speed, hull and armor. Scirocco heavy torpedoes retain Donnager's existing projectile: 4,000 damage, 1,500 penetration, 750 speed, 50 hull and 100 armor, aimed at starbases/titans. Empty-magazine reload is 120s after the final salvo. Target loss, interrupted salvo schedules and save/reload timing remain runtime gates. Launch collars are derivative additions at measured hull surfaces; they are not claimed as original modeled apertures.

## Abilities, movement and appearance

The capitals retain the accepted orbiting attack behavior. Raptor/Pella are slightly slower than Rocinante; Scirocco matches its 1,250 speed. Four measured engine nozzles carry blue normal plumes and longer blue phase plumes. The old tunnel is not reintroduced.

Capital reactor overcharge lasts 20s, costs 75 antimatter and adds 25% speed and reload rate (Pella 35%); recovery is 120s after the active interval. Native weapon cooldown and the separate magazine timers are both adjusted. Paid corvette reinforcement costs 300 credits/55 metal, requires 55 free supply and uses the existing two-second arrival path, with a 120s cooldown. It summons the private MCRN Tachi, not the Morrigan; it is an engine arrival, not an animated hangar departure. The 0.11 repair of this arrival path still needs runtime confirmation.

Marine boarding uses the accepted three-second timed pod visual and one capture roll: Raptor 20%, Pella/Scirocco 25%, with a 600s cooldown. Existing Amun/Don chances are unchanged. All five boarding paths explicitly exclude Rocinante and Pella. Capturing enemy titans may exceed the construction cap because no verified ownership-change cap parameter is exposed. Capital reactor breach is reduced to 1,500 damage within 2,500 range, affecting nearby friend and foe; Donnager's accepted blast remains unchanged.

Sunflare replaces the TEC scout, preserving auto-explore and native navigation. Its normal speed is twice the installed scout's 1,500. Jump charge is exactly two seconds with no charge variance; turning/alignment and actual phase travel can still take additional time. The **20G burn** multiplies speed and acceleration by four for nine one-second damage ticks: 12,000 maximum speed, ten hull damage at seconds 1–9. It suppresses passive hull regeneration during the burn. Unmodified full health would end at ten hull; starting damaged can kill the scout. External repairs/upgrades and actual engine tick order need testing. The finite ninth action ends the buff; there is no competing nine-second expiry timer. Cooldown is 120s.

Pella has silver/charcoal materials and a pale Free Navy eagle on one forward dorsal panel, based on the two user-supplied TV references. The source STL’s available plating determines placement; it is not an exact recreation of the TV side-panel UV layout. The eagle belongs only to Pella; its model-based UI uses the same derivative. Raptor retains Martian gray/orange paint. Existing generic captain recordings are reused; non-rail ships omit railgun/hammers lines. The supplied Sunflare asset itself carries Razorback livery, which is retained. No new speech or music is generated.

## Asset evidence and scale

The supplied STLs contain geometry without textures or animation. Their new materials and supported turret/launcher fittings are authored derivatives; originals remain unchanged. Raptor/Pella use the TV hull's nine PDC layout and four source engine bells. TV references distinguish this hull from the book Raptor with different dimensions/armament; “MCRN Raptor” is the user's requested gameplay name. [TV Pella reference](https://expanse.fandom.com/wiki/Pella_%28TV%29), [book Raptor comparison](https://expanse.fandom.com/wiki/Raptor-class_fast_attack_cruiser).

The Scirocco source supports twelve fitted PDCs and one separated rail assembly, with five light and five heavy launcher collars and four source nozzles. The reference reports variant differences of twelve to fourteen PDCs. The source rail is on the opposite side to a commonly reported TV description; conversion preserves proper handedness rather than silently mirroring the ship. [TV Scirocco reference](https://expanse.fandom.com/wiki/Scirocco-class_%28TV%29).

Scale is provisional: Raptor/Pella 89m (203.152 game units), Scirocco 200m (456.522), Sunflare 12m (27.391), against the existing 46m / 105-unit Tachi reference. These choices preserve each source's proportions; source STL units do not establish canon dimensions. Check relative silhouettes and engine appearance in game before treating them as final.

Detailed sources, transformations, pivots, clearance checks and image recipes are in `audit/update12-a`, `audit/update12-b` and `audit/update12-c`. Original/master assets, editable derivatives, game meshes/textures and rendered UI remain separate. See [asset-source record](../ASSET-SOURCES.md).

## Build and load

Use the recorded Sins II 2.0.3 (318), Steam build 25127248 and SDK build 24092025, with 62 schemas pinned at `8e061033afe53b1393eaefd56617a3fd041eeb5f`. No schema/dependency update is needed.

```sh
python3 tools/build_update12.py
python3 tools/build_update12.py --validate-only
```

Run from the repository root with the full local ignored assets. The builder requires the intact `build/experiments/expanse_update11` plus exact worker contracts/resources in `audit/update12/integration-inputs.json` and `reviewed-inputs.json`. It fails explicitly on missing/changed dependencies and refuses to overwrite an existing output or ZIP. `--package-existing` validates and packages an already assembled candidate, without rebuilding it. Asset conversion commands and isolated output requirements are documented in each worker's report. A source-only checkout cannot perform the asset-dependent build; missing assets are not a passing or skipped-success result.

The ready output is `build/experiments/expanse_update12.zip`. At the workstation, extract its contents into a new `expanse_update12` directory under Proton's `steamapps/compatdata/1575940/pfx/drive_c/users/steamuser/AppData/Local/sins2/mods`. `.mod_meta_data` must be immediately inside that folder. Enable **only The Expanse — 0.12 CAPITAL FLEET** among Expanse versions, then apply. This package includes the earlier ships/audio; do not layer it over earlier variants. No installation, enabled-settings change or game launch is performed by this assignment.

Package and preserved checkpoint hashes are recorded in `audit/update12/package-summary.json` and `checkpoint.json`. The adjacent ignored ZIP `.provenance.json` records the source commit/status and dependency hashes. Source and documentation may be pushed under the user's existing authorization; supplied models, soundtracks, textures and generated packages are excluded.

## Offline results and preserved checkpoint

The final 920-file package passed 116 pinned-schema checks, eleven unique compiled-mesh checks, 31 physical mount checks and 1,532 resolved reference edges. Private player tags, Pella/Rocinante boarding exclusions, ammo accounting, Sunflare finite damage timing and unchanged earlier resource hashes are checked. Native installed `corruption` data absent from the older schema is accepted only by exact equality to its recorded installed source; arbitrary unknown fields are still rejected.

Two older reference helpers were corrected for the unarmed native scout: optional absent effect aliases mean an empty set, and `make_buff_dead` / `buff_has_mutation` use verified live-buff selectors rather than entity filenames. All seven enum values were checked against the pinned schema, two invalid-selector cases rejected, and an `apply_buff` value remains an entity reference. This does not weaken missing-reference checks for actual created buffs.

Checkpoint source: `ad9ea086385c98c4e8516ae8214bf0d28541660a`. All fifteen frozen trees, nineteen earlier ZIPs, three new original packages, enabled settings, 62 schemas and 527 recorded installed references remain unchanged. Prior 0.11 ZIP SHA-256: `a807a4f6a5adaa919911d7ee7b3c8f10e6c534da867c437370f5b8446bcb349c`; tree: `043b1dcbdfe3eb0fe33747570cdf4a97378bb1760a2206a7055c1485ca39b57d`.

New 0.12 ZIP SHA-256: `e0575d558cd8c7f7893b3bd3c6520132b704c51cd15c9514c0b2b126ef81c73c`; package tree: `4ad401a51cacdeab7eae2985871b8b0462a232b2c12faba218c1dfba474d33f8`. Raptor/Pella assembled counts are 94,823 / 95,523; Scirocco 89,519; Sunflare 17,741. Those counts and sampled offline clearance do not certify engine performance or continuous turret motion.

## Ownership and next tests

Main owns unit/skin/player/manifests, behavior, integration checks, documents and final package. Worker A owns Raptor/Pella conversion and the emblem (`tools/update12_raptor*`, `tools/update12_pella*`, `audit/update12-a`), worker B Scirocco (`tools/update12_scirocco*`, `audit/update12-b`), worker C Sunflare (`tools/update12_sunflare*`, `audit/update12-c`). The resumed independent review wrote `audit/update12-review` only. Writing workers used separate worktrees and output directories with shared references read-only.

Run the ordered U12 gates in the [existing checklist](manual-test-checklist.md), recording results in the [existing runtime record](../audit/manual-results.md): loading/build/limits, model and mount alignment, weapon schedules/interception, scout burn and capital abilities, then destruction/save/reload/fleet performance. Offline schema, mesh and reference checks do not establish these behaviors in the engine.
