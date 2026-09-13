# Asset sources and permissions

## Supplied model

- Title: **MCRN Tachi [Expanse TV Show]**
- Creator: [Jakub.Vildomec](https://sketchfab.com/Jakub.Vildomec)
- Source: https://sketchfab.com/3d-models/mcrn-tachi-expanse-tv-show-76fc983ab08c449b9042491a00e621cf
- Model ID: `76fc983ab08c449b9042491a00e621cf`
- Exact license in supplied `license.txt` and glTF metadata: **CC-BY-4.0**, https://creativecommons.org/licenses/by/4.0/
- Package: `mcrn_tachi_expanse_tv_show.zip`, 66,985,861 bytes.
- SHA-256: `47abb4ac87c2af477a906bdab4e87f20551e72917877e6dfa489a11946320142`
- Evidence: untouched archive under `assets/original/`; extracted license and metadata under `assets/source/tachi/`; per-file hashes in `audit/source-checksums.json`.
- Received from the user and inspected 2026-09-12. Sketchfab's page returned HTTP 403 during verification; license identification is from the supplied package, not an independently observed current download page.

Required supplied credit:

> This work is based on "MCRN Tachi [Expanse TV Show]" (https://sketchfab.com/3d-models/mcrn-tachi-expanse-tv-show-76fc983ab08c449b9042491a00e621cf) by Jakub.Vildomec (https://sketchfab.com/Jakub.Vildomec) licensed under CC-BY-4.0 (http://creativecommons.org/licenses/by/4.0/)

Changes in this derivative: per-part geometry simplification, uniform scaling and recentering to the Cobalt envelope, compiler coordinate conversion, texture resizing and DDS encoding, roughness-factor baking, flat normal maps for text decals, zero team-color/emissive masks, and game material/attachment setup. Original source remains unchanged. No affiliation or endorsement is implied.

Keep the credit, license link, and change notice with any shared derivative and on its release page. The license permits adaptation and commercial use, with attribution and change identification; do not add restrictions inconsistent with that license. See the [CC BY 4.0 terms](https://creativecommons.org/licenses/by/4.0/). The model license is evidence of the creator's asset permission; this record does not establish separate rights to Expanse trademarks, logos, characters, or other franchise property. No separate franchise permission was supplied.

## Installed game and SDK

Sins of a Solar Empire II, Ironclad Games / Stardock Entertainment. Local game references are read only. The installed SDK's `License.md` says proprietary / all rights reserved. SDK binaries, schemas, vanilla models, textures, effects, and audio are **not** vendored into this repository. Build scripts read the user's own installation and generate the small overrides locally. Hashes, paths, relationships and selected factual values document the inspection.

## Build tooling

- [Official Sins II SDK](https://github.com/StardockCorp/sins2modtools), installed Steam build 24092025; schemas match commit `8e061033afe53b1393eaefd56617a3fd041eeb5f`. MeshBuilder is executed in place with outputs directed to the project.
- [meshoptimizer](https://github.com/zeux/meshoptimizer), MIT, revision `bba256eaa24039b6f93c773063ff7c20143ae0db`. Kept in ignored `.tools/` with its upstream license. Its attribute-aware simplifier is compiled locally; not bundled with the mod.
- [Microsoft DirectXTex / Texconv](https://github.com/microsoft/DirectXTex), MIT, `may2026` release; source URL/digest recorded in `audit/texconv-source.json`. Private build dependency, not bundled.
- [Sins2 Blender extension](https://github.com/largeBIGsnooze/sins2-blender-extension): binary-prefix reader used as a format reference only. The current mesh trailer is opaque to that reference; official MeshBuilder generates all game meshes.
- Python, NumPy, Pillow and jsonschema are build dependencies. Diagnostic previews use CPU geometry projection, not AI-generated assets and not screenshots of Sins II.

`assets/original`, `assets/source`, `assets/derived`, `.tools`, and `build` are separate and ignored by Git. Keep local originals backed up; retrieve the licensed package separately on another machine. No upload of model assets or a public release was performed by this setup.
# Audio candidate intake

## Six-PDC polish derivative

The local polish derivative adds winding correction, tangent-frame repair, separation into six yaw/pitch turret assemblies, static UI portrait rendering, contrast adjustment, silhouette projection, DPI resizing, selection outlines and mod-logo layout. All ship geometry and UI imagery derive from the credited Jakub.Vildomec Tachi model under its recorded CC-BY-4.0 license. The original archive and extracted master remain unchanged. Editable geometry/rendering recipes and generated game assets are kept separately. No new audio or third-party imagery is included, and no publication or redistribution was performed in this assignment.

Audio candidates remain outside all mod outputs. See [the local audio feasibility and permission record](docs/audio-feasibility.md) and `audit/audio/local-source-audit.json` for selected installed Space Engineers source IDs, exact paths, hashes and unresolved per-recording permissions. No audio was copied, converted or distributed.

## Rocinante hero source intake (2026-09-12)

User-supplied archive: `/home/haker/Downloads/Rocinante_(The_Expanse).zip`. The user explicitly confirms: “Dont worry about the license - we got permission to use it”. Record this as **user-attested permission to use the asset**. The archive contains no license file; creator, source URL, exact license terms and attribution requirements remain unspecified. No public distribution or publication was performed. Do not substitute the original Tachi author's CC-BY license for this separate asset.

The original package and extracted master are preserved unchanged in the isolated geometry worker's `assets/derived/geometry03-b` intake structure (exact paths/hashes in the hero audit). Stand removal, deployment-pose baking, normalization and any simplification apply only to separate editable/game derivatives. The supplied animation remains preserved in the editable source; game-triggered deployment is not established.

Hero archive SHA-256: `2fef806f80c65f138eed9b877c6cd1ae98f12e597856b96cfb1c6676a16af3e6`. Preserved package: `assets/derived/geometry03-b/hero-original/Rocinante_(The_Expanse).zip`; extracted files: sibling `hero-master/`, both in `/run/media/haker/NVME 2/expanse-workers/tachi-one-pdc/`. Individual master hashes and relative-animation measurements: `audit/geometry03-b/hero-asset-audit.json`.

Hero derivative changes: remove6,068 printing-stand triangles; retain161 remaining mesh parts; simplify426,612 stand-free triangles to26,707 using the already pinned meshoptimizer; bake the source's deployed pose after removing presentation motion. Add228 original prototype-fitting triangles (keel railgun, supports and two launch ports), for26,935total. The fittings are project-authored additions, not identified original TV geometry. Supply flat-color textures from the source's material factors; no Tachi paint/textures are substituted. Original animated, stand-free animated, normalized deployed and armed derivatives remain separate. Hero UI renders the new deployed model. Game-triggered animation remains unimplemented.

Corvette0.3 derivative adds801 targeted interior triangles and912 support triangles to the14,622-triangle polish model (16,335total). Original PDC pivots, muzzles and authored geometry stay intact. These changes and all generated mesh/material references are audited in `audit/geometry03-b/`.
# Donnager0.4 intake and hero corrective derivative

The supplied Donnager archive `/home/haker/Downloads/mcrn_donnager_the_expanse.zip` has SHA-256 `b03d70d6180b7c6ff50db22df883f576ebb3981c5d4d138f8bdf1e7434079562`. Its own packaged license identifies “MCRN Donnager (The Expanse)” by **owlstraw**, profile https://sketchfab.com/strawfinch, source https://sketchfab.com/3d-models/mcrn-donnager-the-expanse-05e9f9006d914fcd96e95fbd452aaa28, under **CC-BY-4.0**, http://creativecommons.org/licenses/by/4.0/. Exact supplied attribution is preserved in `audit/donnager04-c/asset-source-and-permission.json` and the untouched extracted master. Keep creator/source/license credit and identify changes when sharing a derivative. This intake created uniformly normalized planning scenes and separated two rail assemblies; no PDC splice or game asset distribution occurred. A future splice must retain the separate Tachi donor credit too.

Original/master and editable Donnager paths are under `/run/media/haker/NVME 2/expanse-workers/validation/assets/derived/donnager04-c/`. Audit and source/output manifests identify individual file hashes. Exporter scale is not treated as meters;475.5m/46m is a provisional planning convention.

Rocinante0.4 is a separate corrective derivative under the already recorded user-attested permission. It corrects the small axial normalization tilt, replaces damaging permissive simplification with a conservative normal-aware derivative, separates six complete source cannon assemblies, and adds project-authored aiming supports. Source animations, archive, extracted master and0.3 derivatives remain unchanged. Aiming joints are new measured candidates rather than a claim that the source deployment animation is a usable game turret rig. Full counts and source partition evidence are recorded in `audit/geometry04-b`. No model was pushed or published.
# Amun-Ra source intake and optional torpedo appearance

The user supplied `/home/haker/Downloads/Amun-Ra_Class_Stealth_Ship_[The_Expanse].zip` and explicitly confirmed permission to use the model. Record this as user-attested permission. The archive contains no creator/license text; no specific license or attribution terms are inferred from the other models. Archive SHA-256: `fa0d7ee158c53ee1e07d362eb1cfc49ab08fe3da9f5b11c2cd414c7c50d71441`.

Untouched original/master: `/run/media/haker/NVME 2/expanse-workers/validation/assets/derived/amun05-c/`. Exact hashes and source references are in `audit/amun05-c/`. Separate editable torpedo extraction selects the actual named source subtree, preserves its 1,600 triangles, UVs and four source atlases, and uniformly normalizes it to the Javelis missile length. No source part is reconstructed from a substitute model. Game conversion, where completed, uses a separate `torpedo05-b` derivative with compiler coordinate/winding preparation, generated tangent repair and resized/repacked textures. No archive or extracted master is edited, and nothing is published.

The complete scene has four turret assemblies and fifteen pods; it is not an already integrated three-PDC stealth ship. User permission to use the source is recorded independently of those implementation limitations.

## Amun-Ra 0.6 ship, turret and pod derivative

Under the same user-attested permission above, this separate derivative retains the central hull, three of the source's four PDC assemblies and one compact boarding pod. It removes detached presentation copies from the game hull, preserves fixed turret supports, separates the three yaw/pitch rigs, applies measured local pivots and a uniform provisional 61.5m/46m relative scale, and converts the source materials to four 2K DDS atlases. The ship has 27,526 triangles; the separate modeled pod has 4,481. No new simplification pass or destructive master change was performed. Turret neutral poses, compiler winding and tangent preparation are derivative changes; actual rotation and visual travel remain runtime tests.

Editable inputs and output provenance: `/run/media/haker/NVME 2/expanse-workers/tachi-one-pdc/assets/derived/amun06-b/` and `audit/amun06-b/`. Generated meshes/materials/textures: sibling `build/amun06-b/game/`. Static UI imagery is rendered directly from the selected seven-part ship in the validation worker's separate `build/amun06-c/ui/`. Source-door launch points remain static; no deployment animation is claimed. Original archives, extracted masters, working Rocinante and earlier torpedo derivative remain unchanged. Nothing was installed or published by this follow-up.

## Rocinante dialogue 0.7 — supplied recordings

The user supplied twelve WAV recordings from `/home/haker/Downloads` and requested local integration and normalization for the Rocinante. This is authorization for this local editing task, not a verified license or public distribution grant. The original creator, upstream recording source, exact license and attribution terms were not supplied. Do not apply any model's CC-BY license or model-specific permission to these recordings. Nothing was published or uploaded.

Untouched source copies are preserved under `assets/original/voice07`; per-file SHA-256 and source/header metadata are recorded in `audit/voice07/audio-intake.json`. Separate 24-bit normalized WAVs are under `assets/derived/voice07/normalized-wav`; generated mono44.1kHz Ogg Vorbis and installed-convention `.sound` files are under `build/voice07/game/sounds`. Eleven lines are used. The XO clip is held for another ship; the unnumbered short “Here comes the juice” was not supplied and was not reconstructed.

Edits: stereo-to-mono conversion where needed, common−18 LUFS loudness normalization, peak control,44.1kHz resampling and Ogg encoding. The captain introduction needed explicit lookahead limiting because its high peak prevented simple gain matching. Full original timing is retained; no words, background replacement, synthetic voice or missing endings were generated. Speech completeness and subjective mix require listening. Existing shared combat/effect/engine audio was left unchanged.

### Supplied source checksums

- `cut-out-the-computer-cores-it-s-time-to-leave.wav` — `7ec2476d0cd0fcfbbd612c9f893bc890dbe9dbe40dc05fd93e15bfb865b43c89`
- `i-flew-with-the-mars-navy-for-20-years.wav` — `dce76ab8f11de3444a66822e09f2476a4b3adc58031994d3d2466a82e7a6225e`
- `we-re-gonna-take-em-for-a-ride-alex-go-around-the-asteroid.wav` — `9442eaef5bee8e385e30692abcc39c233bd781c0514816ece89ed00fcedc64dc`
- `the-antenna-array-up-top-has-seen-better-days.wav` — `2f813566b7ddd6bff21f73a7243f9be6cd5e911b081c33ec37a908cf83a2a7cf`
- `hey-hey-you-seen-the-xo.wav` — `991a1e042e318aecaccdb446e5b253fd376bb16a7f6f9b4df166c2d768a55f11` (held)
- `shit-i-think-they-re-diverting-power-to-the-rail-guns.wav` — `1b1027555d53e7322b6df715cf11688b9f500cbedd2eac9493d144934ad371b3`
- `in-the-case-i-have-to-kill-you-i-just-wanted-to-say-thanks.wav` — `0efab840ef6926a19508a35188ac7e152425a5156170b53048d0b472f9055218`
- `here-comes-the-juice (1).wav` — `a5a3b69d789329fc036ee7c57ccbdcc260a170c33f69dabe3bc1da512a27c722`
- `captain-of-the-rocinante.wav` — `f5d05a1767d90f310f0346c2bef657bd993fd8cb1f26df89a9c072c73790946a`
- `the-only-way-this-ship-ll-pass-for-a-freighter-is-if-no-one-looks-close-enough.wav` — `bbea796d95f8710a63aaef3d1dc23d92d8c6d6548049cdda5e3949ba557e89ab`
- `avasarala-you-ll-get-the-good-news-in-short-order.wav` — `6c92646436f3ec67105ef69bbf688e02e00e4c3b7ceccdc18fd7d89352a97c63`
- `welcome-to-the-churn.wav` — `e24978b5e335fcc9c0df446dc8c30d6c8bc9b420e06c084d14009e278e3fe843`

## Six additional Rocinante recordings — update0.8

The user supplied six additional WAV recordings and requested local integration. Audio creator, exact license and upstream recording attribution remain unspecified; model permission is not substituted for audio permission. Originals are retained unchanged under `assets/original/voice08`, normalized editable WAVs under `assets/derived/voice08/normalized-wav`, and generated game audio under `build/voice08/game/sounds`. No audio was uploaded or published.

Edits: measured loudness normalization toward−18 LUFS, controlled peaks, mono44.1kHz conversion and Ogg Vorbis encoding. Full supplied timing is preserved. No missing speech, background replacement or synthetic voice was generated. `audit/update08/audio-intake.json` records input/output hashes and decoded output measurements.

- `easy-there-partner.wav`: `fde696beaff53720dd603c14c3a02fa7a7576aa5427cadcccedebbe11862ab43`; order_issued / neutral.
- `donkey-balls.wav`: `1ee64b51d5b004d97a0b000d3d881d5d5fa854bb98c23d3a2ce0062e73c957d8`; selected / neutral.
- `did-you-just-say-donkey-balls.wav`: `702f87cbac85bfbe99a9e2f12e537a298c14bca6cf0d8141f34324ed38ead4e9`; selected / neutral.
- `debris-field-buckle-up.wav`: `4e11f5cc289067691ab16b629f209bb6081489a7a436ed7fd8b90a015af2ca80`; order_issued / neutral.
- `damn-straight-do-not-lose-that-ship.wav`: `0034ca4eb04b1784caf6cd3998c5e82835fdc0ddf849340873e7aebe707ce4b2`; attack_order_issued / smug.
- `could-you-pass-me-the-drill.wav`: `5b82dc63834792f6758a02caa35b374a33908726476b73fe5dbd8f5f45347aa7`; selected / neutral.

## Supplied soundtrack — update0.9

The user supplied thirteen WAV soundtrack recordings and requested local music integration. Creator, exact audio license and attribution terms were not supplied; the model permissions are not applied to audio. Originals are preserved unchanged under `assets/original/music09`; separate normalized24-bit WAVs are under `assets/derived/music09/normalized-wav`; generated Ogg/music definitions are under `build/music09/game/sounds`. No publication or upload was performed.

Edits: measured normalization toward−20 LUFS, controlled peaks,44.1kHz Ogg Vorbis encoding, preserving the supplied mono/stereo layout. At the user's explicit request, **Signal begins at source1:05 (65 seconds)**; its opening65seconds are omitted only from the game derivative. Other track durations are preserved. No missing stereo image, synthetic music or new source material was generated. Detailed measurements/hashes are in `audit/music09/audio-intake.json`. The user approved Boarded, Welwala and trimmed Signal for combat; other playlist moods are provisional.

- `welwala-soundtrack.wav` — `bc6d9240ae04fb8054214b24017e0a4818947ba1d6616f84b6901b41fb376b62`.
- `track-from-eros-radio-deep-inc-touch.wav` — `e8ba44a2986bb2e0dbd8519027180519b1a85be81a7c99f38a9aa958b832a736`.
- `theme-tune.wav` — `371f871510b867c9c50f4542f5c8cb3579a354b34512ab8d012cdfa3e2164ed6`.
- `tachi-station-soundtrack.wav` — `a217950840f2832df59d46f0def5ca85d71c648607eb824eaecfb4306934d41a`.
- `signal-soundtrack.wav` — `be0e77071762c1c79adf0922c01430473400a8bc5458f175165d94fd48d4fdf4`.
- `respite-soundtrack.wav` — `4b686e099224c9651f876c18bafc6314fb36a331bf51b58f51f6420312ed92f0`.
- `ready-to-talk-soundtrack.wav` — `74d06514d47c9d31ed5be3375cb0372ac2f3bc58e4d353928fec9423c90937f1`.
- `lionel-polanski-soundtrack.wav` — `c0b37408a32822356366783d1963cae7463b5562c51d6cc4f306a0fe64624778`.
- `lies-and-love-of-power-soundtrack.wav` — `dda3058c2fe42efdbea52b9770d6601e97a055c5a15dfd1b12921d049c920345`.
- `boarded-soundtrack.wav` — `24edae959fa326aec9348986afd3c46b58fc9ae578e8a870b2e3537dc57732f4`.
- `an-impossible-burden-soundtrack.wav` — `88f6ce630e07ff77f0df7b907d339f076b74de23dd6f26f91cef70a9c78dcfaa`.
- `a-lifetime-of-losing-soundtrack.wav` — `a3497fca6aadf7b7d3deac4908678a699f0fa8f0e285912100baae68d072f7a0`.
- `the-expanse-soundtrack.wav` — `143e5a9b39d3b68a3efa53569a17eab83f5046e9e8845406d6c9679b15a2ec6d`.

Two further user-supplied MP3 tracks, **Never See Them Coming** and **Hammerlock**, are also approved for combat. Their untouched source files are retained alongside the WAV originals; separate normalized WAV/Ogg derivatives preserve their stereo layouts and decoded timing. No earlier normalized track was changed by these additions.

- `Never See Them Coming.mp3` — `3f8ba9401a6618371b75b4c95ecf57f4f6d7b4338c85e18d683dfe6aa8dbd6c4`.
- `Hammerlock.mp3` — `14b59abae934a67d2604cf4dd72b527fe5b0aef16cf1f6a98af7c9e49d239308`.

## Donnager prototype 0.10

MCRN Donnager (The Expanse), creator **owlstraw**, Sketchfab model05e9f9006d914fcd96e95fbd452aaa28. Source: https://sketchfab.com/3d-models/mcrn-donnager-the-expanse-05e9f9006d914fcd96e95fbd452aaa28 . Licensed Creative Commons Attribution4.0 International: https://creativecommons.org/licenses/by/4.0/ . Credit creator, source and license; identify modifications. No creator endorsement implied. Original supplied archive SHA-256 b03d70d6180b7c6ff50db22df883f576ebb3981c5d4d138f8bdf1e7434079562.

Derivative changes: uniform scale/centering, topology reduction and normal/tangent correction, two separated rail assemblies with limited gimbals,16 existing Tachi-derived PDC assemblies and connecting supports, two forward launcher collars, measured equipment points, game material/texture conversion and UI renders. The master and supplied archive remain unchanged. The donor Tachi attribution and permission record above also applies. Local test preparation only; no distribution or publication performed.

## Donnager generic Martian-captain speech

20 MP3 recordings supplied locally by the user, described by the user as AI-generated generic Martian-captain speech. Creator/provider, upstream voice identity, exact license and redistribution terms are unspecified. No model permission is applied to these recordings. Exact source filenames and SHA-256 hashes are recorded in the accompanying voice-intake audit; preserved original MP3s remain unchanged. Local derivative processing: mono 44.1 kHz Vorbis at approximately −18 LUFS, full timing retained. No listening-quality or in-game playback certification.

## PDC firing clip0.10.1

User-supplied extracted `PDC.mp3`, explicitly requested for local PDC audio integration. Original and normalized derivative records: [source record](audit/pdc-audio10/asset-source-record.md), [measurements](audit/pdc-audio10/audio-intake.json). No independent license or publication claim.

## Morrigan and Donnager update0.11

Morrigan source: user-supplied `/home/haker/Downloads/xxx_-_morrigan.stl`, SHA-256 `72dcce753f7ac17b1a4600fffb649e93af78e9b19527a2386b46a61cdd115188`. Creator, source page and exact license were not supplied. The user's explicit request authorizes this local intake/conversion; no separate redistribution terms are asserted. The unchanged 306,518-triangle STL is preserved under the isolated worker's `assets/original/update11-morrigan`. Derivative: proper rotation/uniform normalization, source hull reduction, replacement of two static gun assemblies by credited Tachi PDCs, connecting collars and bow launch collars, procedural gray/orange materials (STL contained no textures), compiled game meshes and actual-model UI renders. Final assembled count: 30,185 triangles. See [Morrigan audit](audit/update11-c/REPORT.md).

Donnager0.11 retains the owl straw / Tachi attribution and license records above. The new derivative restores original bevel/detail geometry to 194,296 assembled triangles; it is not subdivision of the old reduced hull. Existing gun pivots, PDC meshes and textures remain unchanged; one fixed socket extends 0.6 units into the restored hull. See [Donnager audit](audit/update11-b/REPORT.md). Original archives/masters remain untouched.

New sprites are renders of these derivatives and inherit their source records. Editable models, source audio, rendered asset imagery and generated game packages stay outside the source push. User-supplied captain speech is reused for Morrigan without railgun/hammers lines; no new audio or voice identity is introduced.
