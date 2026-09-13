# Amun06 behavior handoff — Worker A

Use **`build/amun06-a/final-reviewed`**. The earlier `final` stage remains intact. Ownership stayed within `tools/amun06_behavior*.py`, `audit/amun06-a`, and `build/amun06-a`; source models, game, SDK, earlier candidates and installed mods were read-only. Main owns the Amun ship, mounts, skins, build registration/limit, manifests and package integration.

The user reported improved torpedoes, Rocinante appearance/tracking and excellent performance for the preceding0.4 work, and accepted the unique hero's92k triangle count plus a timed boarding visual. Those observations do not establish any new Amun or cloak test as passed. This worker did not launch the game.

## Core: twelve named private definitions

`final-reviewed/core/entities` contains:

- `expanse06_amun_pdc_0`, `_1`, `_2`: one weapon budget per physical gun,28 damage/.25s/0 penetration/2,500 range.112 nominal raw DPS each;336 with all three bearing. Same verified enemy filters/target groups as accepted MCRN PDCs. Actual Amun turret frames remain main/asset-worker bindings.
- `expanse06_amun_railgun`:3,750 damage/1,000 penetration/10s,375 nominal raw DPS. MCRN/Rocinante rail bytes remain unchanged.
- `expanse06_amun_torpedo.unit` and `.unit_skin`:900 damage through its private ADS,1,500 speed,25 hull/50 armor/**50 armor strength**,1,000 penetration,240s lifetime, same-well200,000 range. The new skin references the actual compiled1,600-triangle `expanse05_amun_torpedo` mesh. The reviewed custom enclosing sphere from0.4.1 is retained. The unit/skin names are private; no source asset was reconstructed or recompiled here.
- `expanse06_amun_magazine.{ability,buff,action_data_source}`: existing8-round, two per10s,120s reload-after-empty logic, renamed privately. Main must add the model's actual `ability_positions`; copied Tachi/Rocinante launch coordinates were intentionally omitted.
- `expanse06_amun_boarding.{ability,buff,action_data_source}`: final named timed-shuttle behavior, one10% roll after the accepted3s delayed action, range6,000,180s cooldown. Enemy fully built, detected capital ships in the same well; named Rocinante exclusion; free-supply checks at cast and transfer. No DoT, death prevention, repeated roll or automatic casting.

These are12 entity files: four weapons, two projectile unit/skin files and two ability/buff/ADS triplets. `core/localization.json` provides their names/tooltips; `core/ship-effect-aliases.json` supplies the nine existing PDC/rail/torpedo muzzle/travel/hit aliases to bind in the new ship skin. Boarding's separate alias remains in its ADS.

`integration-recipe.json` provides `core_abilities`, `railgun`, `pdcs`, exact IDs, generated torpedo dependency paths, limit6-per-player scope and integration requirements. Core ship ID/tag is `expanse_amun_ra`. These components do not change the main's chosen ship hull/build/AM/navigation values.

The custom projectile compiler mesh, material and four texture hashes matched B's `audit/torpedo05-b/integration-spec.json`. All204 files of the source `build/experiments/expanse_rocinante04_amun` matched before/after generation, preserving MCRN750 damage/1,250 speed/50 hull/100 armor/50 strength and accepted hero railgun behavior.

## Accepted modeled boarding visual

Main may make exactly two reviewed presentation edits: set the `play_weapon_effects.mesh_point` to **`weapon.boarding.0`**, and bind the existing ADS travel alias's `particle_effect` to **`expanse06_boarding_pod_visual`**. Main copies the installed pirate shuttle particle and replaces its mesh with B's actual pod mesh. `validate_components(..., boarding_model=True)` permits only those two edits; all delay, RNG, targeting, ownership and supply fields must remain identical.

Installed evidence for caster-origin mesh points is stronger than the generic `aura` example alone: `trader_robotics_cruiser_emp_droids.ability` applies operators to the enemy `target`, but its `play_weapon_effects` uses `mesh_point: ability.1`. The actual Hoshiko mesh contains four `ability.1` points at its launcher bank. Ragnarov piercing-shot similarly targets an enemy while using its `bomb` firing point and muzzle/travel effects. This supports binding the Amun caster's actual pod-launch point. Final emitter alignment and timing remain runtime gates.

The3s action delay is accepted behavior, **not collision/arrival detection**. The modeled pod is a particle mesh, not an interceptable entity. It does not gain health or PDC eligibility from using a real model. Capture is one probabilistic attempt per valid delayed application; six separate attempts are not a whole-fleet10% guarantee. Validate concurrent supply/ownership transfer, target loss, caster destruction and pending-arrival saves.

## Optional cloak: separate six-file experiment

`final-reviewed/cloak/entities` contains:

- `expanse06_amun_cloak.ability`: manual, instant cloak activation,30s stock-derived cooldown. Main's unit hook is `cloak_ability: expanse06_amun_cloak`.
- `expanse06_amun_cloak.buff`: observed Eidolon `provides_cloak`, alpha/fade and **`required_product: dlc_Herald`** fields, quality4 modifier. No copied shield-absorption or automatic-acquisition mutation, no damage-dealt degradation, no research edit and no auto-cast are added.
- `expanse06_amun_cloak.action_data_source`: fixed values and memory declarations shared by the manual cloak and controller.
- `expanse06_amun_cloak_controller.ability` / `.buff`: permanent passive controller, separate from the manually removable cloak. Tracks only the private Amun torpedo definition and the private gun tag.
- `expanse06_amun_revealed.buff`: independent60s quality−5 modifier, parented to the permanent controller. Stacking preserves the existing reveal window instead of restarting it.

The first three **individual** Amun torpedo events count only while the cloak buff exists and no reveal window is active. The fourth sets the controller deadline to current simulation time+60, applies the independent reveal modifier, then clears count. Further events during the window do not extend it. Manual cloak toggles do not intentionally recreate the controller or remove its reveal child. After expiry, persistent cloak quality should return without a fresh cast if the player has not manually decloaked. This is an implementation design, not observed engine lifecycle/save behavior.

The magazine remains **two torpedoes every10 seconds**, not one every5. Consequently, the fourth individual missile normally occurs in the **second pair**, at about10s. No ammunition/cadence approximation was silently substituted to obtain three full concealed salvos.

Successful PDC/rail hits carrying `expanse06_cloak_revealing_gun` start the same fixed window. The tag is present on exactly the three private PDCs and railgun; it is absent from torpedoes and pods. Torpedo damage cannot prematurely trigger the copied Eidolon damage-dealt rule because that rule is absent. **Missed gun shots do not reveal**, and a hit reveals at damage time rather than firing time. This is the accepted conservative policy; no nonexistent weapon-fired hook is claimed. Enemy detectors still apply, so a quality4 cloak is not a promise of unconditional invisibility.

The optional set stays separate from the core handoff. Main may assemble it as a distinctly labeled experimental variant after reviewing supplemental validation and full references; it must never be reported as complete official-schema coverage or silently included in the core fallback.

## Strict validation and the real schema gap

Pinned official revision remains `8e061033afe53b1393eaefd56617a3fd041eeb5f`. No SDK/schema file was changed, fetched or replaced.

The pinned buff schema lacks `provides_cloak`, `required_product`, `cloak_alpha_value`, `cloak_fade_duration_value` and the `cloak_quality` modifier enum. The unit schema also lacks **`cloak_ability`**. Further strict checking revealed a preexisting gap: installed vanilla Cobalt and the unchanged0.4/hero units contain a top-level **`corruption` object**, also absent from the pin. Draft7 previously ignored that field because the schema mixes Draft7 with `unevaluatedProperties` keywords. No gameplay field was removed to conceal this mismatch.

`tools/amun06_behavior_validate.py` provides `validate_cloak_candidate(entities, sdk, game, unit_definition=...)`:

1. For every optional file, validate all known data with the unchanged pinned Draft7 schema.
2. Additionally evaluate the **same unchanged schema** using Draft2020's handling of its existing `unevaluatedProperties:false` declarations. This is an extra closed-key check, not a replacement official schema or an assertion that the official dialect changed.
3. Separate only the four exact observed cloak fields and one exact `cloak_quality` modifier shape per relevant buff. Require the product gate literally `dlc_Herald`, alpha/fade0.3/3, quality4, revealed modifier−5, and local ADS references. All extensions and source hashes are reported.
4. For a combined unit, remove only the exact private `cloak_ability` hook for known-subset validation. If inherited `corruption` exists, first require **exact equality with installed `trader_light_frigate.unit`**, verify its three penalty-buff references and record the source/hash as a second installed-only unit extension. No arbitrary unknown field is ignored.
5. Verify six private files, controller/manual ability linkage, every referenced float/value/local buff, declared memory IDs, stock GUI PNGs, exact private projectile filter, private hit tag, fourth-launch threshold, independent reveal application, fixed60s/non-extension transitions, lack of shield/acquisition mutations, and presence of both controller/manual hooks in a supplied unit.

The result is explicitly **“PASS STRICT SUPPLEMENTAL CHECKS — NOT COMPLETE OFFICIAL SCHEMA COVERAGE.”** It is not a runtime result. Existing corruption is reported as an inherited schema exception, not something introduced by this cloak experiment.

`tools/amun06_behavior.py` provides `validate_components(package, candidate, sdk, cloak=False, boarding_model=True)` for the core. It checks the twelve exact components, allowing only actual PDC turret bindings, nonempty real magazine launch positions and the two boarding presentation edits above. Core mode rejects leaked optional cloak files or a unit `cloak_ability` hook. Main/C still verify all meshes, hardpoints, effects, additive manifests, tag/player limits, localization and base preservation. The core Draft7 result must not be described as coverage of inherited out-of-schema Cobalt data.

## Checks actually run

- Generation: **62 pinned schema blobs matched**,12 core component schemas passed, four optional known-schema files passed, two cloak buffs received separately labeled installed-field checks.
- Torpedo mesh/material/four DDS hashes matched the reviewed compiler spec. All204 source0.4.1 files remained unchanged.
- Strict optional validation passed local/global value, memory, six-file dependency, stock GUI asset and transition checks. A synthetic known hero unit plus only the exact cloak/controller hooks passed the combined-unit supplemental check; this is not the still-being-integrated Amun ship.
- **Ten negative cases were rejected:** unknown cloak top-level flag; unknown nested modifier field; missing product gate; threshold3; undeclared memory; counting the Martian projectile; generic physical damage tag; shield mutation; unknown unit field; changed inherited corruption.
- The first strict synthetic-unit attempt correctly failed on inherited `corruption`; it was investigated and replaced with the exact preserved-source check above. It was not counted as a pass or worked around with blanket permissiveness.
- New Amun/cloak/boarding game tests: **NOT RUN**. Complete main-package checks are still the integrator's responsibility.

## Smallest workstation gates

First test the core ship alone: construction/limit6, movement/selection, three PDCs, heavy rail alignment, custom torpedo mounts/timing and unchanged old ships. Then test one timed boarding attempt's visible launch/delay and supply/ownership behavior, including invalid targets and pending-arrival saves. Only then load the separate cloak experiment: manual cloak, detector visibility, first pair/second-pair fourth missile, gun-hit reveal versus misses, uninterrupted60s despite more fire, manual toggles, expiry and saves during count3/reveal. Test formation/fleet performance after individual behavior is established.
