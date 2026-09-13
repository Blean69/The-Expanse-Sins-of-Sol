# Combined update0.9: ability controls,17 voices and soundtrack

Use **`expanse_amun09_cloak`** for the requested stealth-ship test. It contains the ability-set correction from [update0.8](update08.md), all17 Rocinante voice lines and all15 supplied music recordings. The no-cloak `expanse_amun09` variant remains an isolation fallback. Both are complete mods; enable exactly one alone.

The previous enabled `expanse_amun06_voice07` had no cloak by design. Missing boarding was a separate integration mistake: each ability had been placed in its own alternative unconditional ability set. Update0.8 corrects this to one coexisting ability list on Amun and Rocinante; these corrected unit files are preserved byte-for-byte in0.9. The earlier valid-schema/reference checks did not model alternative-set selection. A regression now catches the original error and protects legitimate conditional vanilla sets.

## Music placement

The user explicitly approved **Welwala, Boarded, Signal, Never See Them Coming and Hammerlock** for combat, and asked to remove Signal's first1:05. The game derivative starts at source65.000seconds and lasts64.920seconds. Its original129.920-second WAV remains untouched. The earlier uncropped derivative is retained outside the package.

| Installed music state | Assignment |
|---|---|
| Front-end/menu | `theme-tune` first, then `the-expanse-soundtrack`; exhaustive shuffle |
| Loading | The Expanse theme, Respite |
| Ambient/non-combat | Respite, Ready to Talk, Tachi Station, Lionel Polanski, Eros radio |
| Early game | Tachi Station / Ready to Talk / theme; losing context adds Lionel Polanski / A Lifetime of Losing |
| Mid game | Lionel Polanski / Lies and Love of Power; winning theme/Ready to Talk; losing A Lifetime of Losing / An Impossible Burden |
| Late game | Lies and Love of Power / Lionel Polanski; winning theme/Tachi Station; losing An Impossible Burden / A Lifetime of Losing |
| All three battle states | **Boarded, Welwala, trimmed Signal, Never See Them Coming, Hammerlock**; no ambient-track fallback in battle pools |
| Victory | The Expanse theme first, Respite |
| Defeat | A Lifetime of Losing first, An Impossible Burden |

Game-phase pools retain an explicit `ambient` fallback using the existing engine field. Track weights are1; exhaustive shuffling and first-track indices use fields actually present in the installed data/schema. First-menu track selection still needs a runtime observation. The mood of non-combat placements is provisional: the agent has not listened to the tracks. Combat placement is user-approved.

These are real Sins II music states, not new map/environment detection. No verified per-planet, asteroid-well, proximity or station music hook was found in the pinned schema. Eros radio is ordinary non-combat soundtrack, not a positional station broadcast. Music remains non-positional, streamed, and uses the installed looping convention. The10-second engine transition/default TEC player settings remain unchanged. Intro videos before mod loading are outside this music hook.

## Scope and offline checks

`uniforms/player_race.uniforms` is a complete copied installed table with `overwrite_races:true`, preserving all race/non-music data and every other race's playlists exactly. Only TEC (`trader`) music pools change. This is intentional for the TEC-based Expanse prototype; other faction campaigns retain vanilla music. The installed `music.uniforms` default player is `trader_loyalist`, supporting the TEC front-end pool, but menu refresh/startup behavior must be tested with the mod loaded.

The race-music table passed the pinned official schema in declared Draft7 and an additional closed-key evaluation.17 exact state names, all15 used sound/media references, positive track weights and in-range first indices were checked. No dedicated `.sound` schema exists at this pin, so each new music definition exactly copies installed `tech_battle.sound`: `is_streaming:true`, `is_looping:true`; same-stem Ogg media follows installed usage.

All0.8 files except metadata/credits remain byte-identical, including corrected abilities,17 voice lines, boarding GUI, weapons, meshes, supply/cost/health/navigation and optional cloak definitions. Each package adds30 music files plus one race-music uniform. Earlier installed/generated trees and ZIPs, original audio and pinned game/SDK references remain unchanged. No install, enable, game launch, commit, push or publication occurred.

## Audio processing

The recordings were measured and normalized toward **−20 LUFS** with a−2.5dBTP target, encoded as44.1kHz Ogg Vorbis quality6. Mono sources remain mono; the four stereo sources (theme tune, Eros radio, Never See Them Coming and Hammerlock) remain stereo. No artificial widening or generated material was added. Other than the requested Signal crop, full durations are retained. The normalized editable WAVs are separate24-bit files.

| Track | Source seconds | Game seconds | Encoded LUFS | True peak dBTP |
|---|---:|---:|---:|---:|
| `welwala` | 136.573 | 136.573 | -20.30 | -2.26 |
| `eros_radio` | 186.408 | 186.408 | -20.08 | -7.92 |
| `theme` | 57.156 | 57.156 | -20.01 | -8.82 |
| `tachi_station` | 131.067 | 131.067 | -20.02 | -2.55 |
| `signal` | 129.920 | 64.920 | -20.04 | -5.53 |
| `respite` | 95.907 | 95.907 | -19.91 | -3.16 |
| `ready_to_talk` | 108.680 | 108.680 | -20.02 | -3.46 |
| `lionel_polanski` | 149.013 | 149.013 | -20.21 | -2.58 |
| `lies_and_power` | 120.400 | 120.400 | -19.64 | -2.40 |
| `boarded` | 90.280 | 90.280 | -20.05 | -5.37 |
| `impossible_burden` | 166.680 | 166.680 | -19.91 | -2.28 |
| `lifetime_losing` | 95.533 | 95.533 | -19.88 | -2.27 |
| `expanse_theme` | 64.373 | 64.373 | -19.99 | -5.22 |
| `never_see_them_coming` | 89.314 | 89.314 | -20.05 | -7.29 |
| `hammerlock` | 109.260 | 109.260 | -20.05 | -8.45 |

Decoded outputs passed loudness/peak, duration, codec and channel-layout checks. Peak headroom and loudness are measured results, not a listening-quality certification. Stock mix sliders, transition timing, loop behavior, late-loading menus and fleet performance remain runtime checks.

## Packages and reproduction

ZIPs are in `build/experiments`, with external source/dependency/hash provenance. Choose the cloak variant, extract it into a fresh same-named Proton `sins2/mods` folder with `.mod_meta_data` at its root, and enable it alone. Keep prior folders disabled for rollback. For the first ability test, use a new game/newly constructed ship. Returning to the menu or restarting after enabling may be needed to hear the new front-end pool; no automatic restart was performed.

| ID | Files | ZIP SHA-256 |
|---|---:|---|
| `expanse_amun09_cloak` | 338 | `dd0075deee3764ee62e4246627135acf28b878d5f8d8cbc0fa6d49bc54fb5228` |
| `expanse_amun09` | 332 | `4a5c9b63d457af844caed998fa139fa4c45335f081eb735b7e3ee6518e739cb2` |

Main owns `tools/build_music09.py`, `audit/music09` and this documentation. Original soundtrack copies: `assets/original/music09`; normalized/trimmed WAVs: `assets/derived/music09/normalized-wav`; generated music: `build/music09/game/sounds`. Input/output/source permission records accompany the audit and package credits. User supplied the recordings for local editing; no audio license/creator information or public-distribution grant is invented from model permissions.

```bash
cd '/run/media/haker/NVME 2/expanse-mod'
# Fresh derivative directories only; Signal's65-second crop is built in:
python3 tools/build_music09.py --normalize
# Fresh combined package directories only:
python3 tools/build_music09.py
# Existing output validation; does not rewrite ZIPs/installations:
python3 tools/build_music09.py --validate-only
```

Missing ignored source files, base0.8 packages, existing local ffmpeg or pinned SDK data are concrete errors, not skipped passes. No dependencies were updated. The0.8 corrected package remains separately available for isolating controls/audio from music.

## Smallest next test — all new runtime gates NOT RUN

1. Enable only0.9 cloak. Re-enter the menu and confirm theme tune; load a fresh TEC game and check ambient music/slider volume.
2. Construct Amun: confirm boarding and cloak controls. Launch boarding at a valid enemy capital with free fleet supply; inspect cursor/pod/cooldown before assessing its10% capture roll. Ninety percent of valid attempts should not capture. Verify Rocinante repair/salvo/reactor controls too.
3. Enter battle: hear Boarded/Welwala/Signal/Never See Them Coming/Hammerlock; verify Signal starts at its requested1:05 section. Leave battle and check transition to non-combat music without unwanted overlap or abrupt looping.
4. Check enemy-view cloak/detectors, fourth individual torpedo/60-second reveal, boarding ownership/supply, destruction and save/reload. Listen to the six added voice lines separately from music and combat effects.

Victory/defeat pools and longer-term game-phase transitions can be checked as those states become available. Their configuration is verified offline; their actual playback has not been observed.

The two additional MP3 recordings were appended before this turn completed. The first unpublished13-track build was preserved under `build/music09/first-13-track-packages`; only the final15-track ZIPs above should be loaded. Existing soundtrack derivatives were hash-checked unchanged during the additions. MP3-source padding accounts for small decoded/container duration differences within the verified80ms tolerance.
