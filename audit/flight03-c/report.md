# Worker C — 0.3 flight pattern and phase plumes

Owner: Worker C. Separate worktree `/run/media/haker/NVME 2/expanse-workers/validation`; writes confined to new `tools/flight03_effects.py`, `audit/flight03-c/`, and ignored `build/flight03-c/`. No installed content, previous worker output, normalized source, shared unit/skin, dependency revision, or enabled-mod setting was changed. No game launch, installation, commit, push or publication.

## Ready integration contract

Copy the contents of `build/flight03-c/generated/` into the new package root: three private `.particle_effect` files under `effects/`. Apply `build/flight03-c/integration-spec.json`:

- `unit_patches[]`: one exact `/attack/attack_pattern` replacement; apply to the corvette and hero units as desired. It does not touch `/physics`, `/move`, weapons, attack ranges, costs or health.
- `skin_patches_by_role.corvette[]`: change the three native phase **travel** effects to `mcrn03_corvette_phase_plume`.
- `skin_patches_by_role.hero[]`: three travel references to `mcrn03_hero_phase_plume`, plus normal exhaust particle effect to `mcrn03_hero_idle_plume`.
- `entity_manifests_required`: empty. Effect filenames establish their IDs; no new entity definitions are introduced here.

The patch metadata is not game content; keep it outside the package. The main integrator owns unit and skin application. All three referenced effect filenames are private and do not replace installed effects.

## Movement evidence and choice

Installed `trader_light_frigate.unit` has `attack.attack_pattern.type = stop_and_fire`. The current 0.2 polish unit's physics and move dictionaries are exactly equal to installed Cobalt values.

Installed combat corvettes use `circle_strafe` with `angle_range_off_gravity_well_plane: [-45.0, 45.0]`. TEC `trader_missile_corvette.unit` also forces a 90-degree yaw alignment. That Shuriken broadside alignment may keep the forward torpedo aperture outside its firing arc. The proposed minimal pattern instead copies the installed `advent_gunship_corvette.unit` pattern, also used by Vasari raider/anti-corvette and other combat corvettes: circle_strafe with the same plane-angle range and **no forced broadside**. These exact fields and enum values exist in pinned `unit-schema.json`.

The unit comparison restores only `/attack/attack_pattern` and then compares equal to vanilla Cobalt. All existing speed, acceleration, angular speed, strafe, bank, collision and navigation values remain intact. Do not describe this as Shuriken agility: Cobalt retains 25-degree/s angular speed rather than Shuriken's 100-degree/s, so it may fly a wider or slower circle. There is no explicit orbit radius field in the examined schema. Orbit distance, torpedo firing opportunity, circling continuity under attack orders and short-range approach remain runtime questions.

## Conditional effect path

Pinned `unit-skin-schema.json` exposes separate `hyperspace_effects.travel_effect`, `travel_effect_between_stars` and `travel_effect_destabilized` references. These provide a phase-only visual hook. Existing Cobalt travel effects contain the large ring/streak tunnel emitters. Redirecting those three references removes that travel tunnel from the affected skin while using a plume effect during that state.

Charge, interstellar charge, destabilized charge, exit effects and charge/enter/exit sounds are preserved. This is travel-tunnel replacement, not removal of every phase transition graphic. Any camera-wide phase overlay or engine visual outside these skin references remains unverified.

The ordinary corvette `exhaust_effects` block remains unchanged so its existing attachment/throttle behavior is preserved. The hero points that same native exhaust hook at a private blue 1.5× plume. No undocumented state expression is introduced into an exhaust definition.

A schema-verified alternative exists: `flair_effects` can attach an effect at `mesh_point_name: exhaust.0` with `constraint: is_not_in_phase_space_or_charging`. It is **not applied**, because it also suppresses charging and replaces native exhaust behavior with a generic flair effect. The native regular exhaust may coexist with the new large phase plume; whether the engine already suppresses it in phase travel must be observed. No exclusive replacement or exact at-rest throttle result is claimed.

State-specific sound hooks are also explicit: `hyperspace_effects` has charge/enter/exit sounds; `sounds.move_sounds` distinguishes engine and hyperspace_travel. This worker adds no audio files or sound changes.

## Private effect recipes and placement

All effects derive from installed `effects/exhaust_tech_medium_01.particle_effect`, retaining its five emitters, attachment topology, timers and textures except the two flame gradients. `advent_light.dds` is an installed blue/white gradient used by installed `advent_medium_missile_exhaust.particle_effect`. It was inspected locally and is referenced directly; no texture copy or conversion is needed. Private effects omit `external_color: primary` so an externally supplied engine/team tint cannot override the blue gradient. The hot core remains white. This is an observed installed texture reference, not a guess about a hex color channel order.

| Effect | Axial length vs ordinary Cobalt plume | Transverse width vs base | Hook |
|---|---:|---:|---|
| `mcrn03_corvette_phase_plume` | 4.0× | 1.25× | Phase travel only |
| `mcrn03_hero_idle_plume` | 1.5× | 1.5× | Native normal exhaust |
| `mcrn03_hero_phase_plume` | 4.0× | 1.5× | Phase travel only |

“4×” describes authored axial dimensions/forward velocities, not a measured on-screen length. Width remains modest so the plume does not become four ship-widths wide. Hero travel is 4× the base plume, approximately 2.67× its own 1.5× normal plume. No extra emitter rate or duplicate particle set is added inside a private effect. Bounds are enlarged using the already present `max_effect_radius_scalar` field.

The normal hero effect stays nozzle-local. Native phase hooks have **no mesh_point field**, so phase effects bake the known nozzle transform into each source effect node. The current compiled `expanse_polish_hull.mesh` has:

- `exhaust.0` position `[0, -10.112395286560059, -49.331363677978516]`.
- Rotation matrix `diag(-1, 1, -1)`, equivalent to a 180-degree yaw.

The recipe applies scaled local offsets through that exact rotation and adds its position; source node yaw receives pi radians. This reproduces the measured nozzle-local transform relative to unit origin. **The engine's phase-effect origin is not established by a schema**, so this remains a placement candidate until tested. Use the same compiled hull/nozzle transform for the hero, or regenerate against the hero's actual nozzle if its scale/origin changes. Do not call the plume correctly aligned based on these offline transforms alone.

## Actual checks and limits

`build/flight03-c/offline-validation.json` and the mirrored audit record contain generated hashes, every read-only dependency hash, exact changed particle pointers, state-hook schema excerpts and 27 resolved effect-to-texture relationships.

- Pinned unit and skin schema Git blobs match revision `8e061033afe53b1393eaefd56617a3fd041eeb5f`.
- Unit schema validation: PASS. Unit structural comparison permits exactly `/attack/attack_pattern`; physics and move unchanged.
- Both patched skin variants validate: PASS.
- Three private effects: observed-field/type structure, unchanged list topology, valid attachment IDs, finite numerical values, and texture references: PASS.
- **Particle-effect schema: NOT AVAILABLE** in the installed/pinned SDK. No particle schema validation is claimed.
- Deliberately inserted unknown effect key and broken node attachment are rejected. Authored corvette phase flame dimensions are 200×12.5 versus source 50×10. Blue gradient IDs and omitted external tint verified for all three private effects.
- Read-only source bytes remain unchanged after generation; previously recorded installed hashes are compared where those references exist in the checkpoint audit. Newly inspected sources have explicit hashes rather than silently rewriting the original snapshot.
- `python3 -m py_compile tools/flight03_effects.py`: PASS.

A complete game package was not built by this worker. Package-level reference checks must include these three effect definitions and their installed texture fallbacks; their hashes are supplied for that check. These are schema/structure-supported experimental hooks with runtime placement risks, not an observed visual result.

## Small workstation gate

1. In a fresh well, compare ordinary corvette movement and attack orbit against 0.2: speed/turning unchanged, hull rotates with actual unit, torpedoes still get launch opportunities, no unexplained PDC-range rush. Repeat against a moving target.
2. Inspect corvette normal exhaust and hero normal blue/larger exhaust while idle, accelerating and braking. Confirm nozzle origin and direction.
3. Phase travel between planets: charging/exit preserved, travel tunnel absent, enlarged blue plume appears only during travel at the actual nozzle. Check from both sides and at close/far camera distances; watch for double normal plumes or effects spawning at hull center.
4. Repeat between stars and through a destabilized lane when available. Verify phase completion and normal plume restoration, then save/reload around travel.

All runtime gates are **NOT RUN**. No global phase rendering, physics, maneuverability, flip-and-burn or weapon behavior was changed by this worker.
