Current supplied-dialogue work is documented in [voice0.7](voice07.md). The following Space Engineers investigation is historical; its audio remains outside packages.

# Audio intake — research only

No audio was added to any mod, downloaded, converted, played, or distributed. The local Workshop folders already contain unpacked media; extraction is unnecessary for these candidates. `tools/audit_audio_sources.py` records 22 media hashes, header/ffprobe metadata and exact SBC event references in `audit/audio/local-source-audit.json`. This is a selected inventory, not a claim that every installed mod was audited or every requested cue was found.

## Candidate sources and permission record

All paths below are relative to `/run/media/haker/NVME 2/SteamLibrary/steamapps/workshop/content/244850/`.

| Local source | Evidence | Permission status |
|---|---|---|
| [2394430829](https://steamcommunity.com/sharedfiles/filedetails/?id=2394430829) | `Data/AryxLynxonEpsteinDrives_Audio.sbc`; nine WAVs under `Audio/ARLN_EPST/` | Creator and exact audio license not established from local metadata; no local license file found in this scoped source inspection |
| [2036872575](https://steamcommunity.com/sharedfiles/filedetails/?id=2036872575) | `Data/Audio_PDC.sbc`; seven WAVs under `Audio/WEP/` | Root `LICENSE` contains GPL v3 text; authorship and applicability to these particular recordings remain unverified |
| [2860576438](https://steamcommunity.com/sharedfiles/filedetails/?id=2860576438) | `Data/Audio/AudioImpakt.sbc`; six WAV/OGG files under `Audio/sfx/` | Creator and exact audio license not established from local metadata; no local license file found in this scoped source inspection |

The links identify sources; remote pages were not inspected during this local audit. `metadata.mod` supplies only ModVersion 1.0 for these three sources. Access through Workshop does not establish our audio permission record. Before importing any clip, record its actual creator, upstream recording source, exact applicable license, attribution, edits and permission evidence. Do not assume the model's CC-BY license applies to audio. No model/audio derivatives are authorized for publication in this assignment.

## Requested cue map

These are candidates based on filenames and source event wiring, **not listening approval**. Several WAVs use floating-point format (Python `wave` rejects format 3); installed ffprobe successfully identifies their format. Preserve any future editable audio separately from generated OGG and `.sound` files.

| Requested cue | Local lead or remaining gap |
|---|---|
| Epstein start/spool-up | `2394430829/Audio/ARLN_EPST/arylyn_edrive_ignition_01.wav`, wired as Start of `ArcARYLYN_edrive_standard_burn` |
| Low-power loop | `aryx_lynxon_drive_loop_01.wav`, wired as Loop of the same event; actual perceived power requires listening |
| High-burn loop | `aryx_lynxon_heavy_drive_loop.wav`, wired to `ArcARYLYN_Very_Large_Epstein_Drive_Fire`; no verified Sins throttle switch yet |
| Shutdown | No distinct shutdown event established in this source |
| Near/distant engines | Several alternative loops exist; no verified near/far pairing or Sins switching hook |
| PDC servo/traverse | No dedicated cue established |
| PDC spin-up, firing burst, tail/cooldown | `2036872575/Audio/WEP/OneShot{Start,Loop,End}_{2D,3D}.wav`; source event `PDC_Shot`. Start is not proof of mechanical spin-up sound |
| PDC hull/shield impacts | Sins vanilla per-weapon hit-hull and hit-shield effect aliases already contain separate sound lists; no new Expanse clip selected |
| Torpedo release | `2860576438/Audio/sfx/latchrelease.wav`, 0.836 s mono PCM, event `latchrelease` |
| Torpedo ignition | `MissileLaunch1.wav` / `missilelaunch.wav`, source events of those names; listening needed |
| Torpedo travel loop | No dedicated seamless loop established |
| Interception explosion / hull impact | `missilesoundeffect.wav` is wired to event `nuclearoption`; neither name proves suitability. Separate Sins torpedo death versus weapon impact paths need runtime confirmation |
| Railgun charge/discharge/impact | Wishlist only, deferred with railgun work |
| Hull breach/decompression | Vanilla Cobalt damage effect already uses `ambient_loop_airdecompression`; no new clip selected |
| Reactor/drive failure | Vanilla damage uses `ambient_loop_electrical_damage_01`; dedicated failure transition not established |
| Large destruction | Existing death-sequence audio is the initial reference; no new clip selected |

The SE PDC SBC maps Type D3 to filenames ending `_2D` and Type D2 to `_3D`; do not infer spatial suitability from filenames. Some torpedo events also reference `missilelaunch.wav` despite different event/file names. The machine audit records these actual relationships.

## Verified Sins controls and limits of evidence

The pinned installed Cobalt skin uses `skin_stages[0].sounds.move_sounds.engine = engine_techfrigateship`. Installed `sounds/ENGINE_TECHFRIGATESHIP.sound` has `is_positionable: true`, `is_looping: true`, `is_streaming: false`, `min_attenuation_distance: 140.0`, `sound_group: exhaust`. Its media is OGG. Weapon muzzle, shield-hit and hull-hit aliases in the skin each supply sound lists. Movement, firing, hits and damage therefore have existing attachment points.

A survey of all 3,833 installed `.sound` definitions found only `is_positionable`, `is_looping`, `is_streaming`, `min_attenuation_distance`, `sound_group`, and optional `data` (media alias). There is no dedicated sound schema in the pinned 62-schema set. This is evidence of installed usage, not proof that the engine supports no other fields.

Distance attenuation is a plausible route to quieter close-detail sounds. **Minimum attenuation distance is not an established maximum audible distance or an explicit camera zoom gate.** No verified configurable per-group voice cap, near/far crossfade, throttle-dependent engine switch, servo event, or automatic start/loop/end sequence was found in this bounded inspection. SE's `MaxDistance`, `SoundLimit`, `PreventSynchronization`, and Start/Loop/End fields are SE data; do not copy them into Sins definitions.

For a later sound experiment, begin with one engine loop and existing muzzle/impact/death hooks. Audition at close, medium, whole-well and tactical zoom with 1/6/30 ships; check overlapping loops, clipping, stereo spatial behavior, CPU/frame time, stop/destruction cleanup and save/reload. Keep fine mechanical sounds quiet and local in the intended mix, with major impacts/destruction carrying farther only after the actual attenuation behavior is observed. Do not change shared vanilla sound groups globally to achieve this.
