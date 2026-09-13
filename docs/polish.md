Current observation: the user now reports individual PDC tracking and good tracers with the polish prototype. This guide preserves the working 0.2.1 build; see [the 0.3 handoff](combat03.md) for the next experiments.

# Six-PDC polish candidate

The user tested the old name/visual baselines together: model loading and fixed-muzzle firing worked, while major hull surfaces were missing. Those observations are recorded in the existing `audit/manual-results.md` with the three unaltered screenshots. They are not observations of this new package.

**New mod ID: `expanse_corvette_polish`, display version 0.2.1.** Package: `build/experiments/expanse_corvette_polish.zip` (83 files). SHA-256: `77fafb25e1f8ec8f812c5f5b720bef85f563c451b3866d432c7ae5141f0b2e10`. The package and source hashes are in the matching `.provenance.json`; source remains uncommitted on checkpoint `9e40dd4b42853318ef87cc3d7d858f2abf601176`. The 0.2.1 target-group correction was applied to the already installed polish mod and the ZIP. The agent did not enable mods, launch the game or publish anything.

## What changed

- **Hull surfaces:** corrected inconsistent triangle winding through compiler input and recompiled with the pinned official MeshBuilder, regenerating its surface-facing data. All thirteen final meshes have zero meaningfully opposed triangles at the documented tolerance. Near-perpendicular authored-normal cases still need visual inspection.
- **Shading:** repaired only the 16-byte tangent fields using matched source position/normal/UV frames, orthogonalized against retained normals. No arbitrary fallback frames were needed; all non-tangent bytes, including the freshly compiled facing data/trailer, are unchanged by this step.
- **Six PDCs:** hull plus six separate yaw bases and six pitch/barrel assemblies. Fixed deployment linkage stays on the hull; moving geometry is removed only from this derivative's hull so it does not render twice. All **14,622 triangles** remain: 10,560 hull + 6 × (138 base + 539 barrel). Pivots and muzzle offsets are independently measured for each assembly. Deployment remains static.
- **Weapons:** exactly six private PDC weapon entries replace the one fixed Cobalt medium autocannon. Each physical PDC has one muzzle cluster and one firing budget for both ships and damageable torpedo entities. There is no seventh hidden autocannon and no second anti-missile weapon firing alongside each gun. The weapon name is now `PDC autocannon`; the game may group identical display names in its HUD.
- **Ship UI:** model-derived portraits, HUD/tooltip images and tactical silhouettes, including selected/sub-selected states at the installed 100/150/200 DPI sizes. Six explicit brushes, eighteen PNGs and two mod-browser logos. The pinned SDK prescribes PNG for UI; these are not converted to DDS.
- **Metadata:** uses the full installed SDK example shape, including display name and logos. Existing runtime logs showed the old minimal metadata falling back after missing those fields. Only the new package receives this correction.

Health, durability, armor, regeneration, cost, supply, construction, navigation, shields and build menus retain vanilla Cobalt values. The existing AI matching-weapon reference points to the first private PDC, and the explicit unit target-group list matches that weapon exactly. The unit-level torpedo-ignore setting and all other AI values remain unchanged. No new torpedo launcher, audio, railgun, economy or faction changes are included. The ship remains shared by every user of the Cobalt unit/skin, including applicable neutral/garrison units and their special localization.

## Provisional cadence and damage

| Quantity | Per PDC | Three guns bearing | All six bearing |
|---|---:|---:|---:|
| Damage per nominal cycle | 28 | 84 | 168 |
| Cooldown | 0.25 s | — | — |
| Nominal raw DPS | 112 | 336 | 672 |
| Visual pulses per second | 24 | 72 | 144 |

Range is 2,500; penetration is zero; yaw/pitch tracking is 360°/s. Each cycle has six visual pulses at 0/.04/.08/.12/.16/.20 seconds. The top-level damage burst field is absent. Visual pulses do **not** add a second damage multiplier. Exact damage cadence must be observed in game.

Under the documented damage model, three overlapping guns imply approximately 14.8 seconds against unbuffed Cobalt armor/hull; six imply approximately 7.4 seconds. This is a benchmark assumption, not an observed kill time. Arc overlap, shields, durability, armor strength, accuracy, target movement and bonuses matter independently. Tracking speed is not firing coverage: candidate arcs are yaw ±100°, pitch −75..5°, subject to clipping/sign checks.

No exact TV PDC RPM was established from primary sources. The worker's [official Prime viewing references](../audit/polish-a/weapon-recipe.md) inform the desired rapid visual character, not a claimed canonical or measured ammunition rate. These are explicitly provisional game values.

The PDC uses the installed enemy-only filter admitting torpedo entities and verified Cobalt target groups plus `torpedo_strikecraft`. Nearby larger ships remain eligible in those groups but zero penetration limits effectiveness against durability. Visual-only missiles/projectiles without a damageable torpedo entity are not thereby made interceptable. `best_target_in_range` and first-listed torpedo group do **not** prove interception priority. Whether guns abandon ship fire for incoming torpedoes while an explicit ship attack order remains active is the essential runtime gate.

## Loading the new candidate

The agent left the two existing installed baselines unchanged. The installed polish mod is now patched to 0.2.1; restart Sins II before retrying Apply Changes. Its earlier 0.2.0 files/ZIP are backed up in `build/hotfix-0.2.0`. Their preserved hashes remain in `audit/experiments/checkpoint.json`. The user closed the game during preparation; four game-owned window/debug/lobby/settings files changed. These external edits were recorded in `audit/polish/settings-observation.json` and left untouched; the enabled-mod list did not change.

For the next test, extract the ZIP **contents** into a new folder named `expanse_corvette_polish` inside:

```text
/run/media/haker/NVME 2/SteamLibrary/steamapps/compatdata/1575940/pfx/drive_c/users/steamuser/AppData/Local/sins2/mods/
```

The new folder must directly contain `.mod_meta_data`, `entities`, `meshes`, `textures`, etc. Disable `expanse_cobalt_name`, `expanse_corvette_visual` and the stock experiment in the game's mod screen; enable only **The Expanse — Corvette Polish** and apply. This new mod already includes the ship name, model, weapons and UI. Keep a separate fresh test save. Do not merge its contents into a baseline folder or load it over an old experiment save.

Run P1–P6 in the existing manual checklist and record observations in `audit/manual-results.md`. New-package culling/shading, UI, rotation, tracking, interception, damage timing and save/reload remain **NOT RUN**.

## Reproduction, evidence and ownership

Workers used separate worktrees and output directories under `/run/media/haker/NVME 2/expanse-workers/`. Shared source assets/SDK were read-only. A owns weapon recipes (`tools/polish_weapons.py`, `audit/polish-a`); B owns geometry/export (`tools/polish_geometry*.py`, `audit/polish-b`); C owns UI (`tools/polish_ui.py`, `audit/polish-c`). Main owns unit/skin/manifest integration, the package builder, checks and this documentation.

Editable geometry is in the B worker's `assets/derived/polish-b/expanse_polish_editable.gltf`, with separate hull→yaw→pitch hierarchy and original material/image references. Compiler inputs, raw official outputs and tangent-repaired game meshes are separate. Editable UI recipe/SVG/masters are in the C worker's `build/polish-c/source`; game files are in `generated`. These ignored dependencies are absent from an ordinary Git checkout; no substitutes are downloaded when missing. Attribution/derivative changes are recorded in `ASSET-SOURCES.md` and included in the package.

Reproduce worker outputs using their reports, then from main:

```bash
python3 tools/prepare_polish_inputs.py --worker '/run/media/haker/NVME 2/expanse-workers/tachi-one-pdc'
python3 tools/build_polish.py \
  --weapons '/run/media/haker/NVME 2/expanse-workers/weapon-behavior/build/polish-a' \
  --geometry build/polish-inputs/geometry \
  --ui '/run/media/haker/NVME 2/expanse-workers/validation/build/polish-c' \
  --game '/run/media/haker/NVME 2/SteamLibrary/steamapps/common/Sins2' \
  --sdk '/run/media/haker/NVME 2/SteamLibrary/steamapps/common/Sins of a Solar Empire II - Mod Tools'
```

Assembly refuses existing outputs. Add `--validate-only` to the second command to check the already built package without rebuilding it. Existing baseline builders/installers are never called. Final provenance is refreshed after documentation changes into the ignored sidecar, outside the ZIP, avoiding a self-hash loop.

Observed offline results: 62 pinned schema blobs and 527 installed reference hashes preserved; all 13 final binaries independently rechecked for winding and valid tangent frames; 14 authored entity/brush schemas pass; six unique physical weapons/12 aliases and all referenced mod/base resources resolve; all 18 UI sizes/alpha and both logo dimensions pass; ZIP contents match the 83-file directory. Three deliberate temporary corruptions—duplicate physical weapon identity, hidden seventh weapon and unrelated hull-health change—were rejected. No production data was changed by these tests.

Schema success alone does not verify gameplay; unchanged installed effects/audio/death resources are existence-checked boundaries, not a claim of complete engine-level dependency validation. Main JSON reports are in `audit/polish/`. Runtime priority, hull occlusion, normal-map appearance, six simultaneous firing budgets and fleet performance still require observation.

## 0.2.1 loader correction

The user observed Apply Changes fail on 0.2.0: `attack_target_type_groups do not match weapon:expanse_polish_pdc_0.weapon`. The unit retained the Cobalt group list while its matching weapon added torpedoes. The explicit unit list now exactly matches the PDC weapon list; the separate unit torpedo-ignore list remains intact. No weapon rates, damage, mounts, meshes or UI assets changed. The only installed changes are `entities/trader_light_frigate.unit` and the metadata version. The overlay resolver now enforces this cross-reference; nineteen regression checks passed, including rejection of the old mismatch and acceptance of matched groups with torpedo-ignore retained. Actual Apply Changes after the fix remains NOT RUN by the agent.
