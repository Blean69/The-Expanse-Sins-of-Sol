# 0.17 Fleet voices

This complete playtest package adds 23 normalized recordings to the unchanged 0.16 fleet. It supplies distinct introductions and selection responses for the smaller ships, UNN responses for Truman/Amun-Ra, and capital component-completion dialogue. Pella's railgun recording is held outside the package because Pella has no railgun.

Load `build/experiments/expanse_update17` alone as TEC Enclave, replacing the enabled older Expanse variant. Do not stack versions. No game installation, enabled settings or live session was changed by the builder. The full 0.16 package and ZIP remain available for rollback.

## Voice assignments

| Ship | New callbacks |
| --- | --- |
| Missile-defense platform | Platform reporting: selected neutral/scared and spawned |
| Scirocco | Scirocco reporting: spawned; MCRN orders: selected neutral/scared |
| Raptor | Raptor reporting: spawned; MCRN orders: selected neutral/scared |
| Tachi | MCRN orders: selected neutral |
| Morrigan | Morrigan awaiting orders: selected neutral/scared and spawned |
| Pella | Beltalowda greeting: spawned and one entry in selected neutral |
| Sunflare/Razorback | Got this command: order issued and spawned; good luck catching me: selected and retreat neutral/scared |
| Truman and Amun-Ra | UNN reporting: spawned and selected neutral; looking tough: selected scared; course correction/helm: order issued neutral/scared; attack received/PDC contact/railguns: attack order neutral; PDC contact: attack scared; attack received: attack smug |
| Truman and Amun-Ra | UNN juice: jump charge; reactor scrammed: cannot jump neutral/scared; cooldown: neutral/scared; reaction mass: respective neutral/scared recordings; going down: crippled neutral/scared; retreat: neutral/scared |
| Truman, Raptor, Scirocco, Pella and Donnager | Construction complete: ship component finished building |

Exact per-event arrays are in `audit/update17/dialogue-map.json`. Reusing a scared line for its neutral fallback does not change the recorded delivery. Construction complete is a component callback, not a replacement for ship-specific spawn announcements.

The shared Donnager duty/standing-by identifiers are removed from non-Donnager dialogue pools, including order acknowledgements. Remaining generic warning lines are retained where no replacement was supplied. Truman retains its existing armor/destroyed fallbacks. Rocinante's unique crew is untouched. The unarmed Sunflare no longer acknowledges an attack order with a PDC response. UNN contact and railgun recordings are command acknowledgements; they do not require or announce an actual shot or enemy-detection event.

Pella's selected-neutral pool contains its new greeting and the existing generic request-for-orders line. The native array format has no verified per-line rarity control; the greeting is included once, but a low playback frequency is **not** claimed. More Pella selection recordings would provide additional variation without speculative engine fields.

## Audio processing

All 24 source MP3s are copied and hash-checked unchanged. Twenty-three are processed at the established -18 LUFS target (0.6 LU tolerance), 44.1 kHz mono Vorbis q6. Measured outputs range from -18.50 to -17.98 LUFS; the highest encoded true peak is -2.31 dBTP. Nine clips needed gain plus a lookahead limiter to reach target. No silence trimming, missing-word reconstruction or alteration of clip timing was requested or performed; source/output durations remain within 0.08 seconds to allow MP3 padding.

`audit/update17/audio-intake.json` records input/output measurements, limiter attempts and original/WAV/Ogg hashes. Normalized editable WAVs and source MP3s are local ignored dependencies. All old music and PDC sound files remain byte-identical.

## Identifiable package and rollback

- Current: `build/experiments/expanse_update17.zip`, version **0.17.0**, 1,070 files.
- ZIP SHA-256: `710a0dde1842d1ea3a9e0f5e28649922a482b808a9e60dbfd7bf1645bdf878db`.
- Tree SHA-256: `9c3899619279acec20558bb78e92c4a4ca86fd75301699639c63abfae801e32e`.
- Rollback: `build/experiments/expanse_update16.zip`, SHA-256 `2fe3936f4a544055190227b02d990c25dae7ad9a30297db131c7a69c24355905`.
- Installed references and pinned SDK: game 2.0.3 (318), schema commit `8e061033afe53b1393eaefd56617a3fd041eeb5f`.

Only ten unit skins' dialogue maps, package metadata and the asset record change among existing files. Forty-six new files provide the 23 matching Ogg/sound pairs. Unit gameplay, weapon ranges and cadence, costs, construction times, movement, research, shieldless baseline, torpedoes, meshes, textures, effects and Rocinante's complete skin remain byte-identical to 0.16.

## Verification

**Observed offline passes:** normalization and output-encoding checks for all 23 active clips, all original hashes, ten pinned unit-skin schema checks, 1,161 resolved references, all new sound/Ogg pairs, no unused active recording, no held Pella railgun recording in the package, exact dialogue-only allowlist, archive/tree agreement and preserved 0.16 rollback.

**Not run:** listening/content completeness, in-game trigger behavior and relative dialogue levels, actual selection frequency, save/reload or multiplayer. No new runtime pass is inferred from earlier fleet tests. Previous 0.16 balance/visual and 0.15 research/support checklists remain pending where already marked pending.

For the next test, select and build each named ship, issue movement/attack/retreat orders, trigger jump and failure callbacks, and finish a capital component. Confirm that Truman/Amun-Ra use the new UNN voices, the scout never announces PDCs, and Pella never announces railguns. Check quiet and combat situations for dialogue audibility alongside the unchanged music/PDC audio. Then save/reload and use the same ZIP/hash on both multiplayer clients.

## Build

`python3 tools/build_voice17.py` creates fresh checkpoints, derivatives and package and refuses existing outputs. `--validate-only` checks the frozen result; `--package-existing` packages an already built and reviewed directory when its ZIP does not yet exist. The builder uses the pinned SDK/native speech profile and never installs, enables or launches a mod. Source, documentation and audit JSON are pushed to Git; MP3/WAV/Ogg assets and packages stay local.
