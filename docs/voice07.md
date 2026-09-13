# Rocinante voice lines 0.7

Eleven supplied recordings are normalized and packaged in two complete, separately loadable variants. The XO recording is retained only in the original-source intake. Only `here-comes-the-juice (1).wav` was supplied; no short variant or missing words were reconstructed. No game launch, install, enable or publication occurred.

## Packages and loading

| Package | Base | ZIP SHA-256 |
|---|---|---|
| `expanse_amun06_voice07` (289 files) | Combat + boarding | `bf42fad33370fa6f092892e18709c3cd050babda761d358660d2bd1b1353eb77` |
| `expanse_amun06_cloak_voice07` (295 files) | Cloak experiment | `5a1c6a18c55879a9f4c8258f5944f1129cdd240c5fcddfa02900e5dd9cee91ed` |

ZIPs are in `build/experiments`. Use the voice variant corresponding to the experiment you want to test. Each ZIP is a complete mod: extract into a fresh same-named folder under the existing Proton `sins2/mods`, with `.mod_meta_data` at the folder root. **Enable one combined variant alone**, with other Expanse combined variants disabled. Existing folders are preserved for rollback. Start a disposable fresh game for the first audio check. The cloak package retains its previous partial official-schema coverage and Harbinger gate unchanged.

## Measured audio

Common target: −18 LUFS, mono44.1kHz, 24-bit editable WAV then Ogg Vorbis quality6. The installed Cobalt voice sample is mono44.1kHz Vorbis and measured −16.12 LUFS; this provisional mix is slightly quieter. Generated clips measure −18.45 to −17.89 LUFS, encoded true peaks no higher than −2.32 dBTP. Subjective mix has not been auditioned by the agent.

Most recordings use measured two-pass loudness normalization. The captain and good-news recordings have low average level and high peaks; the first gain-limited attempt was correctly rejected. Those two use explicit5ms-lookahead/50ms-release peak limiting, with gain iterated against decoded Ogg measurements. Original copies are untouched; unsuccessful derivatives remain outside package outputs. No silence/word trimming, noise removal, background separation or generated speech was applied. Normalizing a recording also raises its existing background sounds.

| Clip | Input LUFS | Encoded LUFS | Encoded true peak dBTP | Routing |
|---|---:|---:|---:|---|
| `retreat` | -20.19 | -18.12 | -2.37 | `retreat` / `scared` |
| `mars_navy` | -21.07 | -18.10 | -3.49 | `selected` / `neutral` |
| `asteroid_ride` | -21.50 | -18.32 | -2.36 | `attack_order_issued` / `smug` |
| `antenna` | -18.63 | -18.03 | -4.20 | `armor_down` / `neutral` |
| `enemy_railguns` | -21.80 | -17.89 | -2.92 | `attack_order_issued` / `scared` |
| `thanks` | -22.10 | -18.38 | -2.32 | `attack_order_issued` / `smug` |
| `juice_long` | -27.60 | -18.09 | -2.87 | `hyperspace_charge_started` / `neutral` |
| `captain` | -32.39 | -18.35 | -2.99 | `spawned` / `neutral` |
| `freighter_joke` | -23.76 | -18.38 | -2.35 | `selected` / `neutral` |
| `good_news` | -33.31 | -18.10 | -2.81 | `order_issued` / `neutral` |
| `churn` | -20.60 | -18.45 | -2.57 | `attack_order_issued` / `smug` |

The captain line is also in the neutral selection pool. Requested scared/smug assignments are preserved. Retreat mirrors its scared clip into neutral, and attack mirrors its smug pool into neutral so ordinary-state orders have responses without assuming an undocumented mood fallback. No stock Cobalt dialogue remains in the Rocinante map; unmapped mood/event fallback and playback suppression remain runtime questions. The railgun warning is an attack-order line, not an actual enemy-weapon detection event.

The schema supplies arrays of sound references for each category/mood, not a verified per-line rarity field. The freighter joke is a normal member of the three-line neutral selection pool; no invented weights or duplicate entries simulate rarity. Which moods the engine chooses and how repeated orders are throttled need workstation observation.

## Verified files and boundaries

Only `entities/expanse_rocinante_hero.unit_skin` changes among existing gameplay files: exactly `skin_stages[0].sounds.dialogue`. Metadata and asset credits are the other two changed prior files. Each package adds22 files:11 private `.sound` definitions and11 colocated `.ogg` files. Meshes, materials, weapons, health, abilities, PDCs, engine audio, other ships and the Amun cloak experiment remain byte-identical to the respective base.

The dialogue categories/moods pass the pinned unit-skin schema in its declared Draft7 dialect and an additional closed-key evaluation. The pinned SDK has no dedicated sound schema: each private `.sound` exactly matches installed speech `{is_positionable:false,is_looping:false,is_streaming:true}`, and same-stem Ogg resolution/codec are explicitly checked. These are command/UI voices; no engine-distance or camera-zoom fields were invented.

Preservation checks cover18 pre-existing installed/generated trees, prior ZIPs, original WAV hashes,62 pinned schemas and527 recorded game references. The user is testing concurrently: this task never writes enabled settings and does not treat their external playlist changes as an error. Existing uncommitted work is retained; no commit/push was made.

## Reproduction and source record

Main owns `tools/build_voice07.py`, `audit/voice07`, this document and the voice package integration. No new worker changes were needed. Game and SDK paths are read-only constants in the script, using the same installed2.0.3(318)/pinned schema revision. Existing ffmpeg/ffprobe, jsonschema and project helpers are used; nothing is downloaded or updated.

Original files: `assets/original/voice07`. Editable normalized WAVs: `assets/derived/voice07/normalized-wav`. Generated game media: `build/voice07/game/sounds`. Each source and output has an audit hash; ZIP sidecars include HEAD, the uncommitted source digest and ignored dependency hashes. The supplied recordings have no provided audio-specific license/creator attribution; user-authorized local processing is recorded separately from model permission. No public distribution is performed.

```bash
cd "/run/media/haker/NVME 2/expanse-mod"
# Fresh derivative outputs only; retains and checks original copies:
python3 tools/build_voice07.py --normalize-only
# Build fresh package directories from reviewed normalized outputs:
python3 tools/build_voice07.py --package-only
# Existing outputs: validate without changing ZIPs or installed mods:
python3 tools/build_voice07.py --validate-only
```

The builders refuse existing derivative/package destinations. Missing ignored input media fails explicitly rather than substituting assets or reporting a skipped check as passed. The normalization-only command needs the supplied Downloads paths; package-only needs the measured originals/editable WAVs/generated files and existing core/cloak packages.

## Smallest workstation audio test — NOT RUN

1. Load one voice-enabled variant alone, construct/select Rocinante, confirm captain introduction and selection pool. Compare dialogue-slider loudness with one vanilla ship; listen especially to captain and good-news transients/background.
2. Issue move/attack/retreat and phase-jump orders; inspect scared/smug routing when those moods occur. Trigger armor damage separately. Confirm missing mood entries do not cause unwanted silence/errors.
3. Repeat selection/orders to assess overlap, cooldown and repetition. The joke has no guaranteed rarity. Confirm combat effects/engines and other ships sound unchanged.
4. Destroy the hero and save/reload; check interrupted/queued dialogue and subsequent commands. Record cut-off words or bad source tails individually for a later editing pass. No listening or in-game result is marked passed here.
