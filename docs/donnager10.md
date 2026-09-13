# Donnager heavy battleship prototype — 0.10

This is a separate, combined experiment, `expanse_donnager10`. It includes the accepted0.9 corvette, Rocinante, Amun-Ra, cloak, boarding, voice and music content. Load it alone, replacing0.9 in the enabled list. This assignment does not install or enable it. **Donnager runtime results: NOT RUN.**

The user confirmed that0.9 cloak, boarding and music work. That observation does not establish Donnager mechanics, statistical capture rates, exact timing or save/reload behavior. The agent has not launched the game.

## Stats and scope

The user chose the **existing shared titan limit**. Donnager is another titan choice at the TEC titan factory, unlocked by the corresponding Loyalist or Rebel titan research. It does not create another titan allowance. Player definitions gain only this buildable unit; their existing limits remain unchanged.

| System | Prototype definition |
|---|---|
| Foundation | Installed Ankylon physics, health levels, experience progression and titan targeting classification |
| Starting durability |14,520 hull;5,000 armor;130 armor strength;6,000 shields;750 durability |
| Speed |575; stock Ankylon acceleration/turning, stop-and-fire navigation |
| Build envelope |300s,150 supply,9,600 credits/2,900 metal/1,900 crystal;3 defense,1 utility,3 ultimate exotics |
| Railguns |Two separate5,000-damage hits/20s each;1,500 penetration;12,000 range |
| PDCs |16 physical biaxial guns;14 damage/.25s each;0 penetration;2,500 range |
| Light torpedoes |Two from the bow per10s;8-round magazine;120s after the last pair;750 damage/1,000 penetration/1,250 speed |
| Heavy torpedoes |One from rear tubes per15s;4-round magazine;120s after the last shot;4,000 damage/1,500 penetration/750 speed |
| Torpedo durability |Both types retain50 hull/100 armor/50 armor strength; genuinely classified torpedo entities, not just particles |
| Inventory |Eight shared ship-component slots, including compatible consumables |

Rail/PDC values are level-one, unmodified values. Ankylon experience progression adds its normal damage/cooldown modifiers at higher levels. Components and reactor boost can modify them further. Scripted torpedo damage is fixed by its private action data; ordinary weapon-damage upgrades do not automatically change it.

One PDC has one firing budget for ships and incoming torpedoes.56 raw DPS per gun gives896 if all16 bear,224 in a four-gun sector,448 in an eight-gun overlap. Six visual tracers per burst do not mean six separately configured damage budgets. Actual damage after armor/durability and interception during attack orders still needs measurement. The installed target groups put torpedoes first, but that alone does not prove interception priority in every order state.

Heavy launches require a starbase or titan. The installed projectile AI group also contains ordinary defenses, so post-launch retargeting remains a runtime question. Both rounds reuse the accepted, compact Martian torpedo appearance; the stock Ogrov mesh was too wide for these rear apertures. Their names, firing ports, speed and damage distinguish them. No existing projectile definition changes.

## Abilities

- **Launch MCRN Corvette:** paid reinforcement ability, one existing Cobalt-based MCRN corvette,300 credits/55 metal,5 available supply,20s cooldown. It uses the verified `spawn_units` operation with supply clamping. The engine chooses the spawn location. This is not a production queue or an animated launch through the hatch; payment/refund and concurrent supply requests need testing.
- **Reactor overcharge:**100 antimatter;30s at+50% movement speed and1.5× reload progress, followed by120s recharge (150s start-to-start). PDC/rail cooldown duration is multiplied by2/3. Private torpedo deadlines also advance faster, in.25s polls. Other ability cooldowns are unaffected. Boundary ordering, partial magazines and saved timers need runtime checks.
- **Martian marine garrison:** one40% capture roll after a3s timed boarding-pod visual,600s cooldown. It targets eligible detected enemy capital ships and rechecks supply. The visual is not a damageable/interceptable boarding entity. It retains the accepted boarding system's target restrictions, including Rocinante exclusion.
- **Reactor breach on death:** stock starbase self-destruct damage envelope—10,000 damage/1,000 penetration over10,000 radius, wave speed5,000—with own, allied, friendly and enemy targets explicitly included. It triggers from death, not a manual scuttle button. Whether travel-delayed damage survives the dying source and ignores friendly target permissions as intended must be observed. Nearby allied losses are intended.

The two magazine controllers and passive death controller coexist with the three active abilities in **one** unconditional outer ability set. This preserves the0.8 fix for alternative ability-set semantics.

The ten suggested generic components are flak burst, beam armor, missile armor, combat repair system, heavy armor, antimatter engine, rapid autoloader, targeting array, salvage kit and radiation bomb. Consumables occupy the same eight slots. Ankylon-only component access is excluded: its beam/missile unlocks and hangar geometry do not belong to this hull. Other generic shop items remain subject to installed faction/research/tag rules. No shared item definitions change.

## Geometry and presentation

The unchanged1,804,024-triangle source is preserved separately. The generated derivative has76,299 assembled triangles across five unique mesh files;16 PDC instances reuse the same base and barrel geometry. Uniform relative scale remains the earlier provisional475.5m/46m convention, about1,085 game units long. It is not a newly verified canonical screen measurement. PDCs retain the donor gun's physical scale.

One PDC support and one rail drum were examined before extending to16 PDCs and two rails. Four longitudinal PDC stations cover four hull sectors. Rails rotate as whole gimbal assemblies around measured drum centers, yaw±2°, pitch fixed,15°/s traverse. Sampled arms/muzzles clear the hull; existing contact inside the drum-bearing region is expected. The arc is a conservative geometry limit, not a canonical claim. Runtime aiming, firing alignment and all-sector coverage remain untested.

The accepted PDC donor retains12 near-perpendicular face/averaged-normal cases (3 base,9 barrel;192 instances across16 guns) within the existing−1e−5 winding tolerance. Their counts match the frozen donor audit. They are explicitly carried forward, not newly repaired or hidden by a general tolerance relaxation. The new hull and rails have zero such ambiguous cases. All five compiled meshes use zero tangent fallback.

Two new short bow collars attach to measured forward-facing surfaces with clear launch rays. Four heavy launch points use measured aft circular apertures, pointing outward. The central rear hatch remains closed and static. The marine visual has an equipment point; corvette reinforcement placement is engine-controlled. No new deployment or hatch animation is claimed.

Four actual engine nozzles use blue idle plumes and a combined blue phase effect four times the idle length. The earlier accepted phase presentation is retained. The Donnager shield impact effect uses its own hull mesh rather than an Ankylon outline; impact radius appearance and performance need testing. Stock titan destruction visuals accompany the separate damaging reactor wave.

Six UI brushes,18 DPI sprites and two mod logos are rendered from the actual derivative. Twenty supplied AI-generated generic Martian captain lines are normalized around−18LUFS, mono44.1kHz Vorbis, with original timing retained. They apply only to Donnager. PDC/contact lines acknowledge attack orders; the construction line acknowledges completed ship components; reaction-mass lines acknowledge insufficient antimatter. These are verified dialogue callbacks, not new gameplay detectors. Rocinante dialogue and music are unchanged.

## Build and provenance

Work ownership: A supplied private combat definitions and the component validator (`tools/donnager10_behavior*`, `audit/donnager10-a`); B supplied editable geometry, equipment/mount metadata, official mesh conversion and geometry checks (`tools/donnager10_geometry*`, `audit/donnager10-b`); C supplied normalized voices, actual-model UI and independent package checks (`tools/donnager10_support*`, `audit/donnager10-c`). They wrote in separate worktrees/output directories. Main reviewed and integrates the unit/skin, player registration, manifests, effects, source records and documentation in `tools/build_donnager10.py` and `audit/donnager10`.

Checkpoint HEAD: `9e40dd4b42853318ef87cc3d7d858f2abf601176`. Pre-existing local changes were preserved; no checkpoint commit, stash, reset or push was made. Preserved installed tree SHA-256 values:

| Mod | SHA-256 |
|---|---|
| `expanse_cobalt_name` | `599ec704a76198a37e5230da722764b11ea17590cd5da6b8ec85aea668630c37` |
| `expanse_corvette_visual` | `c3f88816cbd303df5da78f4c8e9f1a7e0ba5d1219d8ccfd9a3827933be3fda68` |
| `expanse_amun09_cloak` | `bb5506432e7666dc0d25bf00573bd7930b5d4463d4df4a87597ddf371323c2d8` |

The accepted0.9 cloak ZIP remains `dd0075deee3764ee62e4246627135acf28b878d5f8d8cbc0fa6d49bc54fb5228`. The checkpoint contains all earlier installed/generated trees and15 earlier ZIP hashes.

Run from `/run/media/haker/NVME 2/expanse-mod`:

```sh
python3 tools/build_donnager10.py
python3 tools/build_donnager10.py --validate-only
```

The first command requires a fresh destination; it refuses to overwrite an existing experiment. It reads the accepted0.9 package and reviewed ignored worker outputs. Missing dependencies fail explicitly; skipping one is not a pass. It never edits the installed game, SDK, original assets, enabled settings or earlier packages.

If assembly succeeded but a check stopped ZIP creation, `--package-existing` revalidates that unzipped candidate and packages it only after every check passes. It does not rewrite its files or bypass reviewed-input hashes. This recovered the first assembly after a validator scope bug was fixed; no baseline was rebuilt.

Dependencies are the installed game/SDK paths in the builder; A's `expanse-workers/weapon-behavior/build/donnager10-a/final-fit`; B's `expanse-workers/tachi-one-pdc/build/donnager10-b/game` and audit integration spec; C's `expanse-workers/validation/build/donnager10-c` voice/UI outputs and audit specs. All worker paths are siblings of the repository. Editable source assets stay in worker `assets/derived/donnager10-*`; generated game assets stay under worker `build`. The original archives and extracted masters remain read-only. Do not reconstruct missing files or download substitutes.

The official schema pin remains `8e061033afe53b1393eaefd56617a3fd041eeb5f`, SDK build24092025, game2.0.3(318). Official schemas predate the installed corruption/cloak extensions. Donnager's corruption object is compared exactly to installed Ankylon; it is not falsely described as covered by the older schema. Existing0.9 cloak files are preserved byte-for-byte.

`audit/donnager10/package-validation.json` records actual checks. `package-summary.json` records ZIP and tree hashes. ZIP-adjacent `.provenance.json` records source commit, dirty source-tree hash, ignored dependency hashes and package hash. The HEAD alone does not identify this dirty working tree. Earlier provenance files remain unchanged.

### Completed offline handoff

The package contains490 files, approximately74.6MiB compressed. ZIP SHA-256: `2a9650d771178b1ae5ff83d2c5d2076dfcb546290bc233a8d4e352aebcad484f`. Tree SHA-256: `9f1d4d51af96e2721f839610bc5402d279b72fb2f8084471b75fd219def62f48`.

Actual completed checks:44 new schema-covered documents (including36 private combat definitions), the exact installed Ankylon corruption extension,129 typed action-value references, five compiled meshes,18 mount bases, required equipment points, measured voice/UI hashes, six coexisting abilities, compatible components, shared titan limit, exact prior-content preservation and ZIP/tree consistency.28 prior installed/generated trees and15 older ZIPs are preserved. C independently passed the assembled package; its report is `audit/donnager10-c/package-independent-validation.json`. B's qualified geometry result is `audit/donnager10-b/REPORT.md`.

Integration exposed a validator defect: a `has_buff` query was recursively validating another ability's buff using the querying ability's action values. The two existing action helpers now resolve that reference without executing it; actual applied buffs still receive full checks under their own ability. The full package passed, and four deliberate invalid resolver fixtures (missing reactor value or referenced buff, against both helpers) were correctly rejected. See `audit/donnager10/action-scope-regression.json`. No game definition was changed to conceal the diagnostic.

## Workstation gates, in order

1. **Load/build/limits:** enable only0.10 in a disposable test game. Check Apply Changes/logs, titan research/factory entry, price and supply. An existing titan must prevent Donnager construction and vice versa; test queue/cancel/death cases. Inspect UI, eight component slots and all active ability buttons.
2. **Mounts and movement:** one Donnager, one isolated target. Zoom into PDC0 and rail0 first; check base contact, limited rotation, aiming and muzzle alignment from both sides and above/below. Then inspect the other mounts, slow movement, turning, selection, idle and phase plumes. Record clipping, shields and performance.
3. **Weapons:** time the two rails independently; test light pairs/front and heavy singles/rear, magazine exhaustion and reload. Intercept both types with defensive ships. Send incoming torpedoes while Donnager retains a ship attack order; measure interception, PDC ship damage, coverage and saturation. Heavy damage should be measured separately against shields, armor and hull.
4. **Abilities:** check overcharge movement/reload while magazines are partially full and during empty reload;30s duration and150s next activation. Launch corvettes at normal, insufficient-resource and near-full supply states. Test one marine attempt, then a larger recorded sample for40% probability, supply shortage and target/caster loss. A single success does not verify the percentage.
5. **Destruction/save/performance:** own/allied/enemy targets inside and outside10,000; kill Donnager and record damage and chain reactions. Save/reload during reactor, magazine reload and boarding delay. Compare one ship and a large surrounding fleet; verify all accepted0.9 ships, cloak, dialogue and music remain functional.

Record results in the existing `audit/manual-results.md`, with game version, package hash, setup and observed outcome. No Donnager runtime gate is marked passed by offline schemas or these geometry checks.
