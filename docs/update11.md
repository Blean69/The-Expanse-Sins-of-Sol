# Martian fleet update0.11

This is a separate combined mod, `expanse_update11`, for the next workstation session. It includes the accepted ships, soundtrack and audio. **New runtime tests have not been run.** The user observed correct explosion damage, good PDC audio and acceptable performance with three previous Donnagers; those observations do not certify this higher-detail derivative.

## Fleet composition and scope

| Ship | Supply each | Reference count | Supply total |
|---|---:|---:|---:|
| Donnager | 500 | 1 | 500 |
| Pella — reserved design, not implemented | 150 | 4 | 600 |
| MCRN Corvette / Tachi | 55 | 10 | 550 |
| Morrigan | 25 | 14 | 350 |
| **Reference fleet** | | **29** | **2,000** |

This uses the user's desired composition as a gameplay budget, not a verified census of the fictional navy. Fleet capacity and its research are unchanged. More expensive supply per ship produces fewer stronger hulls. Pella has no placeholder unit or build button. Until it exists, the example reserves600 supply for that role. Rocinante costs110 supply and remains unique; it can replace two Tachis. Amun remains40 and is outside this Martian reference composition. No whole-game damage balance is claimed from the arithmetic.

`trader_light_frigate` now represents the Morrigan. Its shared definition still affects applicable TEC neutral/garrison users. The accepted six-PDC Tachi is preserved as private `expanse_mcrn_corvette`, appended to the three existing TEC player build lists and used by Donnager reinforcement. The shared titan construction limit remains one, including Donnager. No Pella, new faction or supply-cap research was added.

Morrigan starting values:200credits/35metal,15s construction,25supply,600hull/550armor,150durability,1450speed and30°/s maximum turn rate. It inherits the accepted circle-strafe pattern. Two physical PDCs each retain one28damage/.25s budget:112 raw DPS each,224 aggregate at full eligible coverage. Four light torpedoes launch one every10s, alternating two bow tubes; empty reload120s. This is half the Tachi magazine and launch rate, preserving750damage/1000penetration and accepted projectile hull/armor. These are provisional local balance settings.

## Donnager and combat fixes

The new Donnager restores original detail:194,296 assembled triangles versus76,299 previously. All18 gun/equipment point arrays remain identical; two rail gimbals retain their physical ±2° limit. Materials/PDC meshes are unchanged. Fixed socket15 extends downward0.6 units for contact with restored plating. New actual-model sprites accompany Donnager and Morrigan. Morrigan totals30,185 triangles, with two supported biaxial PDCs and two added forward launch collars. Its78.75-unit length is a provisional 75% Tachi scale, not a canon measurement.

PDC range rises from2500 to3500 on Tachi, Rocinante, Amun and Morrigan; Donnager reaches6000. Each existing gun's damage, cooldown, targeting filter, projectile and firing sound are unchanged. Donnager still has16 independent56raw-DPS guns (896aggregate at full coverage). Range does not guarantee every gun can bear. Donnager keeps575linear speed and18°/s maximum turn rate; time to reach maximum turn rate drops20→3s. Long-range railgun kiting remains a possible counter; no impossible rail arcs or artificial movement are added. Test coverage during ship attack orders.

Donnager's local blue plume is three times its previous length and twice its width, at the same four nozzles. Its blue phase plume is also enlarged about the four nozzle anchors, retaining a four-to-one length ratio to the normal plume. Selection now draws from three supplied lines; movement acknowledgements from two. Morrigan uses generic captain dialogue with railgun and hammers lines omitted. All sound files and the accepted reactor-breach damage definitions are byte-identical.

Reinforcement now names the private55-supply MCRN unit, uses its actual model icon and follows the installed hyperspace-reinforcement arrival path. It costs300credits/55metal, requires55 free supply, arrives after2s and retains20s cooldown. This addresses the logged `unit_spawner ASSERT(false)`; successful runtime repair is pending. Arrival placement is engine-controlled, not an animated launch from the hangar.

Amun and Donnager boarding accept `capital_ship`, `super_capital_ship` (command tier), and `titan`. Existing10%/180s and40%/600s odds/cooldowns, detection/supply gates,3s delay and Rocinante exclusion remain. The accepted timed pod visual stays. **Native capture may exceed the titan construction cap**; the engine's ownership-change operation exposes no verified cap parameter. Construction limits remain intact. Test capture with an existing/queued titan. Ordinary TEC command cruisers are classified as cruisers, not the super-capital command tier.

Two concrete log errors are corrected: Amun, Tachi and Rocinante no longer list torpedo/strikecraft in both attack and ignored groups, and the existing cloak-revealing weapon tag is registered alongside all19 installed weapon tags. No cloak timing or detection mechanic is otherwise changed.

## Shield policy

TEC/DLC TEC and Expanse unit definitions lose shield health/regen/burst and direct shield bonuses. Combat hulls/structures receive a hidden permanent native permission guard against shield absorption/restoration/regeneration. Shield-only shops/research and native shield abilities are removed where not needed by surviving prerequisites; mixed armor/hull upgrades retain those bonuses. TEC planetary-shield providers are disabled without changing global planets or foreign factions. Exact files and changed pointers are in `audit/update11/shield-policy.json`.

This is scoped by unit/provider definition. Captured TEC/Expanse hulls stay shieldless under other owners; captured foreign hulls keep their foreign shielding. External allied providers may still add a visible capacity bar, though the native guard blocks its use. Existing saved inventory/buffs may retain obsolete UI or occupied slots; no destructive save migration/refund or automatic ability respec is attempted. Start a fresh test game, then separately test save/reload. No removed shield capacity is silently converted to hull points.

## Build, package and load

Use the recorded installed game2.0.3(318), Steam25127248 and SDK24092025 with62 schemas pinned at `8e061033afe53b1393eaefd56617a3fd041eeb5f`. No dependency update is required. The accepted input is `build/experiments/expanse_donnager10_pdc_audio`; its valid recovered ZIP is `expanse_donnager10_pdc_audio_ready.zip`. Do not use the earlier reboot-truncated ZIP.

From the repository root:

```sh
python3 tools/build_update11.py
python3 tools/build_update11.py --validate-only
```

The builder requires the local ignored inputs listed by `audit/update11/reviewed-inputs.json`, including isolated A reviewed behavior, B geometry/UI and C geometry/UI. It fails if missing/changed and refuses existing output. Assets are not supplied by Git. Worker source and their text reports document reproduction. Use a separate fresh output checkout to regenerate assets; never rebuild over originals or the accepted package. `--package-existing` only validates/packages an already assembled candidate without rewriting it, and refuses an existing ZIP.

The final ZIP is `build/experiments/expanse_update11.zip`. Extract its contents into a new `expanse_update11` folder under Proton's `steamapps/compatdata/1575940/pfx/drive_c/users/steamuser/AppData/Local/sins2/mods`. `.mod_meta_data` must be immediately inside that folder. At the workstation, enable **only The Expanse — 0.11 MARTIAN FLEET** among Expanse variants, then apply. Do not layer it over0.10/name/visual variants. The agent does not install, enable or launch the game.

`audit/update11/package-summary.json` records package/tree SHA-256. Adjacent ignored `.provenance.json` records source commit, source-tree hash/status and dependency hashes. Source and documentation are pushed under the user's authorization; model/audio assets and generated packages are excluded.

## Review ownership and runtime order

Main integrator: `tools/build_update11.py`, `tools/update11_validate.py`, unit/skin/player/uniform/manifests, fleet values, voice assignment, plume, documents, packaging and push. WorkerA: `tools/update11_behavior*.py`, `tools/update11_shields.py`, `audit/update11-a`. WorkerB: `tools/update11_donnager*.py`, `audit/update11-b`. WorkerC: `tools/update11_morrigan*.py`, `audit/update11-c`. Each wrote in an isolated worktree/output directory; shared inputs were read-only. Existing local work was retained.

The ordered U11 tests extend the existing [checklist](manual-test-checklist.md) and [results record](../audit/manual-results.md): first loading/build options and supply, then Donnager reinforcement, then geometry/voice/plume and PDC coverage, then command/titan boarding and shield suppression, finally destruction, saved state and fleet performance. None is marked passed by schema validation.
