# Donnager10 support — Worker C

The 20 user-provided MP3s were copied unchanged to `assets/original/donnager10-voice`. The source inventory records exact filenames and SHA-256 hashes. User describes these as AI-generated generic Martian-captain recordings. Provider, upstream voice identity, exact license and public-distribution terms were not supplied; none are inferred from model permissions. Original downloads and preserved copies remain untouched. This voice set is for the Donnager only; existing Rocinante speech remains unchanged.

All 20 passed two-pass loudness normalization and decoded Ogg measurement: target −18 LUFS within 0.6 LUFS; true peaks below −1.5 dBTP; mono 44.1 kHz Vorbis quality 6. Full timing is preserved without silence removal or cropping; MP3 container/decoded padding differences are bounded by 80 ms. Editable 24-bit WAVs stay in `assets/derived/donnager10-c/normalized-wav`; generated 20 Ogg/20 sound files are under `build/donnager10-c/voice/game/sounds`. No limiter fallback was needed. A hash verification run after generation passed. No listening or game playback test has been run.

The normalized derivative imports only read-only `run`, `probe`, and `measure` helper functions from main `tools/build_voice07.py`. Its exact hash, local ffmpeg version, installed titan skin, stock speech profile and pinned unit-skin schema hashes are in `voice-intake.json`. The Donnager dialogue was tested on an in-memory copy of the installed TEC titan skin under declared Draft7 and supplementary closed-key validation, and every event/mood combination appears on that installed titan. There is no dedicated sound schema in the pinned SDK: sound definitions exactly copy the installed non-positional, streamed, non-looping speech profile.

`voice-integration-spec.json` identifies the game directory and exact `/skin_stages/0/sounds/dialogue` replacement. `voice-generated-hashes.json` binds the 40 generated files. The dialogue pools additionally share the two either-mood takes with neutral/scared attack responses; destroyed and crippled takes serve both appropriate moods. No scheduling, probability or missing-mood fallback is invented.

Semantic limits:

- PDC/contact lines are attack-order acknowledgements, not incoming-threat detection or verified automatic interception callbacks.
- `Construction finished.mp3` uses `ship_component_finished_building`, an inventory component completion callback. It does not announce new carrier-produced fleet ships.
- The reactor-scram line uses `cannot_hyperspace`; it does not prove a real reactor/drive failure detector.
- Reaction mass means the existing `insufficient_antimatter` response here, without adding a fuel system.
- The juice line uses `hyperspace_charge_started`. Reactor-overcharge ability playback is not bound.

| Exact source filename | Event / mood | LUFS | Peak dBTP |
|---|---|---:|---:|
| `Bringing up railguns, neutral..mp3` | `attack_order_issued` / `neutral` | -17.99 | -5.04 |
| `Plotting course correction neutral.mp3` | `order_issued` / `neutral` | -18.55 | -2.31 |
| `Multiple bogies, bringing up the PDC's (either).mp3` | `attack_order_issued` / `neutral` | -17.97 | -4.54 |
| `Looking tough out here, what are our orders (scared).mp3` | `selected` / `scared` | -18.00 | -5.27 |
| `For mars! Bringing up the hammers (either).mp3` | `attack_order_issued` / `smug` | -18.02 | -6.10 |
| `Insufficient reaction mass (neutral).mp3` | `insufficient_antimatter` / `neutral` | -18.00 | -5.92 |
| `Insufficient reaciton mass (scared).mp3` | `insufficient_antimatter` / `scared` | -18.05 | -4.19 |
| `Ability on cooldown (neutral).mp3` | `ability_cooldown_is_not_completed` / `neutral` | -18.29 | -2.60 |
| `Armor down! (scared).mp3` | `armor_down` / `scared` | -17.99 | -7.68 |
| `Attack order recieved (neutral).mp3` | `attack_order_issued` / `neutral` | -18.02 | -3.23 |
| `retreat neutral.mp3` | `retreat` / `neutral` | -18.01 | -2.47 |
| `Retreat scared.mp3` | `retreat` / `scared` | -17.97 | -5.29 |
| `Here comes the juice (reactor overcharge or jump).mp3` | `hyperspace_charge_started` / `neutral` | -17.99 | -5.14 |
| `Were going down! (crippled).mp3` | `became_crippled` / `scared` | -18.00 | -7.32 |
| `Reporting for duty.mp3` | `spawned` / `neutral` | -17.97 | -4.82 |
| `standing by for orders.mp3` | `selected` / `neutral` | -18.02 | -3.51 |
| `Hostile contact! PDC's to auto track.mp3` | `attack_order_issued` / `neutral` | -18.00 | -6.61 |
| `Reactores scrammed, we cant engage the drives.mp3` | `cannot_hyperspace` / `neutral` | -17.99 | -4.41 |
| `Construction finished.mp3` | `ship_component_finished_building` / `neutral` | -18.00 | -2.77 |
| `Ship destroyed voice.mp3` | `destroyed` / `neutral` | -17.97 | -6.44 |

Reproduce from this worker checkout with `python3 tools/donnager10_support_voice.py` in fresh derivative directories, or `python3 tools/donnager10_support_voice.py --verify` to hash-check current originals/derivatives without rewriting them. Missing required inputs fail explicitly. No installed mods, SDK, main package files or prior source assets were edited.

Static UI now passed from B's actual final editable scene: 35 active nodes, 76,299 triangles, five unique meshes, +Z bow / +Y up with no compiler reflection. Six new brushes and 18 DPI PNG sprites plus two logos match installed TEC titan dimensions and the pinned brush schema. The portrait uses the actual two Donnager JPEG base-color maps and donor PDC base-color texture; normal/metallic maps are not evaluated by the studio UI renderer. Portrait master, SVG silhouette and recipe remain editable source; generated game sprites are separate. The preview was visually inspected and source dependency hashes were rechecked unchanged during rendering. There is no invented ship imagery. `ui-integration-spec.json` includes game_directory, skin_patches and logos. Runtime UI rendering remains NOT RUN.

Read-only draft review confirmed titan-compatible generic inventory, eight inherited slots, removal of proprietary access/children/factories, and the shared titan build route. Main was advised to add narrow guards for exact prior localization/tag preservation, one unconditional ability set, and hash-bound voice input. The inherited shield impact radii and four-nozzle phase plume remain runtime appearance gates. `donnager10_support_validate.py` is a small independent final integration check. It now passed against the completed 490-file package: exact accepted0.9 file preservation with reviewed additive registration exceptions; unchanged Amun/Rocinante ability sets; one Donnager set containing all six abilities; shared titan cap1; eight slots and ten compatible generic items; inherited Ankylon health/physics/levels/antimatter/corruption unchanged; exact tag/localization preservation; 40 measured audio files; 20 PNG hashes and source dependencies; action references; and ZIP/tree equality. `package-independent-validation.json` records the actual run, with runtime NOT RUN.

ZIP SHA-256: `2a9650d771178b1ae5ff83d2c5d2076dfcb546290bc233a8d4e352aebcad484f`. Tree SHA-256: `9f1d4d51af96e2721f839610bc5402d279b72fb2f8084471b75fd219def62f48`. No unresolved offline integration blocker was found. Main applied the narrow draft-review guards. The inherited shield presentation, turret aiming, automatic targeting during orders, carrier spawn/cost/supply behavior, one-shot boarding and reactor-death wave still require actual runtime evidence.

Run `python3 tools/donnager10_support_validate.py` after main assembly. The archived copy resolves ignored worker assets through the explicit canonical support path; the report is written only into the checkout where that script lives. This worker changed no main package, installed mod, game file, SDK schema, source master or existing audio.
