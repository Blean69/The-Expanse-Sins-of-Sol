# Cobalt reference trace

All paths below are relative to the installed `Sins2` directory recorded in `environment.md`. `audit/reference-edges.csv` contains 1,088 edges with **source file, JSON pointer, actual identifier, actual destination and resolution method**. `audit/installed-file-hashes.json` records the inspected files. The graph follows recognized reference fields, not arbitrary same-name enum matches. Sound IDs are resolved case-insensitively where the actual on-disk filename uses uppercase, matching the Windows game environment.

## Primary chain

| From | Verified field / identifier | To |
|---|---|---|
| `entities/trader_light_frigate.unit` | `skin_groups[0].skins[0] = trader_light_frigate` | `entities/trader_light_frigate.unit_skin` |
| Same unit | `weapons.weapons[0].weapon` | `entities/trader_light_frigate_medium_autocannon.weapon` |
| Same skin | `skin_stages[0].gui.name` | `localized_text/en.localized_text`, key `trader_light_frigate_name` |
| Same skin | `skin_stages[0].gui.description` | Same localization file, key `trader_light_frigate_description` |
| Same skin | `skin_stages[0].unit_mesh.mesh` | `meshes/trader_light_frigate.mesh` |
| Same skin | `unit_mesh.shader = ship` | Built-in ship shader selection; installed `shaders/mesh/mesh_ship_*` variants; no invented `ship.shader` file |
| Binary mesh material table | `trader_light_frigate` | `mesh_materials/trader_light_frigate.mesh_material` |
| Material | `base_color_texture` | `textures/trader_light_frigate_clr.dds` |
| Material | `occlusion_roughness_metallic_texture` | `textures/trader_light_frigate_orm.dds` |
| Material | `normal_texture` | `textures/trader_light_frigate_nrm.dds` |
| Material | `mask_texture` | `textures/trader_light_frigate_msk.dds` |

The Cobalt binary mesh prefix contains 6,485 vertices and 7,716 triangles. Its point table has **two points both named `weapon.0`**, plus `exhaust.0`, `aura`, `above`, and `center`. Their positions and rotation matrices are in `audit/cobalt-mesh.json`. The reader also records a 123,970-byte opaque trailer. It does not claim to understand or regenerate that trailer; official MeshBuilder writes the replacement, with `--fill_triangle_facing_grid`.

The vanilla unit has one non-turret weapon entry. Its explicit muzzle positions are `[-15.536330,-0.068320,33.135952]` and `[15.571832,-0.068320,33.135952]`. `mesh_point` is `weapon.0`; `weapon_position` is `[0.017751,-0.068320,33.135952]`. Arcs are yaw ±15°, pitch ±5°. The baseline preserves those arcs, forward/up vectors, weapon ID and firing budget; only the two muzzle positions and their average origin change. Final generated coordinates are in `audit/derivative-transform.json` and the compiler JSON, not guessed from the untransformed source.

## Weapons, effects, and audio

The Cobalt weapon has range 4,000; cooldown 2 seconds; damage 20; penetration 250; `firing.firing_type = projectile`; travel speed 4,000. It uses `common_weapon` and `order_target_or_best_target_in_range`. The apparent four-shot burst `[0,.25,.5,.75]` is in its **effects** block. Do not infer four gameplay damage packets solely from that visual pattern.

Four effect IDs in the weapon are **skin-local aliases** bound under `skin_stages[0].effects.effect_alias_bindings`; they are not standalone `.weapon` or `.effect` files:

| Alias suffix on `trader_light_frigate_medium_autocannon_weapon_` | Binding |
|---|---|
| `muzzle` | `effects/trader_medium_autocannon_weapon_muzzle.particle_effect`; five `weapon_muzzle_tech_medium_autocannon*` sound IDs |
| `projectile_travel` | `effects/trader_medium_autocannon_weapon_projectile_travel.particle_effect` |
| `hit_hull` | `effects/medium_autocannon_impact.particle_effect`; five `weapon_impact_physical_medium_hithull*` sound IDs |
| `hit_shield` | Same impact particle; four `weapon_impact_generic_medium_hitshields*` sound IDs |

Each sound resolves to its actual `.sound` metadata and corresponding same-basename `.ogg`, including uppercase names where present. Full exact filenames for every variant are in the CSV. No audio is copied or replaced by either mod.

Other Cobalt skin relationships:

- Exhaust: `effects/exhaust_tech_medium_01.particle_effect`, using `exhaust.0`. This effect references textures including `t_edgemask_ghost_fade`, `t_gradient_93`, `t_noise_008`, and `zap_clr`; the graph continues to their installed files.
- Hyperspace: the `hyperspace_tech_frigate_*` charge, travel and exit particles, including interstellar and unstable variants. Sounds: `HYPERSPACE_CHARGEUP.sound/.ogg`, `HYPERSPACE_ENTRY.sound/.ogg`, `HYPERSPACE_EXIT.sound/.ogg`, and the travel loop.
- Damage: `tec_damage_embers`, `damage_smoke_1`, `tec_damage_plasma_sparks`, `damage_electricity_2`, `damage_air_decompression`; applicable electrical/decompression loops. Flair `tec_damage_frigate` attaches at `center` under `is_crippled`.
- Shield: `effects/trader_light_frigate.shield_effect` → `meshes/trader_light_frigate_shield.mesh` and `texture_animations/trader_normal_shield_impact.texture_animation`, then material/texture dependencies. This vanilla shield shape remains a visual placeholder.
- Death: `death_sequences/frigate0.death_sequence_group` → `death_sequences/frigate_001.death_sequence` → explosion particles and sound variations. Generic debris group `trader` is selected in `spawn_debris`; its group contents are defined in `uniforms/debris.uniforms` and remain vanilla.
- Engine loop: `sounds/ENGINE_TECHFRIGATESHIP.sound` → `sounds/ENGINE_TECHFRIGATESHIP.ogg`. `.sound` marks it positionable and looping, attenuation distance 140, group `exhaust`.
- Dialogue: spawned, selected, order-issued, attack-order-issued and hyperspace-charge-started `trader_light_frigate_*` sound sets. The skin includes scared/smug placeholder variants; those actual filenames are retained in the graph.
- UI: `trader_light_frigate_hud_icon`, `hud_picture`, `tooltip_picture`, monochrome and selection icons remain vanilla. The special garrison label `trader_light_frigate_name.garrison` is deliberately untouched.

## Interpretation limits

`unresolved-strings.json` includes symbolic alias IDs and enum values such as `small_unit`. An unresolved filename lookup is not automatically a missing asset. Alias resolutions are separately recorded as `skin_local_alias` CSV edges. Uniform group IDs and built-in shader selections are symbolic, so they are explained here rather than assigned imaginary files. The CSV also covers the Ogrov/Garda dependency inspection; filter its source column to follow a particular ship.

No game statistics, weapon definitions, shared effects, shared audio, shared materials, or shared textures were edited in place.
