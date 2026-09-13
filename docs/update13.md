# Model and PDC audio polish 0.13

`expanse_update13` is a separate complete combined package based on the preserved 0.12 fleet. The user reported successful model loading and good individual PDC sound, with uncolored hulls, faceted shading, unclear Scirocco turrets, wrong-facing Razorback lettering and excessive sound overlap. **New 0.13 in-game checks remain NOT RUN.**

Scirocco gains mapped charcoal plating and broad Martian red/orange regions guided by the supplied Paul Kiesling artwork. The supplied material images are contact sheets, not a usable original UV layout for the STL; no exact original-skin graft is claimed. Existing twelve PDCs use the same Tachi/Pella-family rig, now with 2.2× visual hardware and correspondingly measured supports, barrel offsets and muzzles. Weapon counts, target groups, damage, cooldown and rail gameplay remain unchanged. Rotation and full swept clearance need runtime inspection even when sampled offline checks pass.

Morrigan gains clear orange bow and shoulder bands over its gray hull, with refreshed model-based sprites. Paint boundaries split triangles on the existing surfaces rather than adding floating decals. Raptor/Pella get area-weighted crease normals to reduce broad-plate lighting distortion from densely tessellated detail; positions, triangle topology, UVs, mounts and Pella's eagle remain unchanged. This addresses shading, not every possible defect in the supplied geometry.

Sunflare/Razorback receives a proper 180° roll around the model's longitudinal axis, including equipment positions and frames. Its existing readable lettering panel now faces upward in the reviewed top presentation. Bow stays +Z and exhaust −Z; no UV mirroring or movement-independent visual rotation is introduced. The triangular source has lettering on multiple facets, so arbitrary underside/camera views can still show inverted lettering. Source pose alone does not establish a unique canon top. Its texture pixels, proportions, gameplay speed/health and burn ability are unchanged.

The earlier PDC recording is 0.896s long and a gun can fire every0.25s: roughly four overlapping recordings per continuously firing gun. Four source-derived0.20s variants replace that repeated long clip, with short fades and −10dB additional gain. Positional/non-looping/light-muzzle routing remains the installed pattern; minimum attenuation distance changes100→70. That field is not a maximum audible range or explicit zoom gate. No supported per-ship concurrency cap was found in the installed sound definitions or pinned schema set. Sound-list variation follows existing vanilla usage; exact selection behavior remains engine-dependent.

A deterministic unattenuated sixteen-gun synthetic mix fell from +22.17dBFS peak to −0.40dBFS, with no above-full-scale samples in the new test. This is an intentionally synchronized sum, **not an engine recording or a guarantee against clipping with larger fleets**. Vorbis container timing remains0.20s; decoded block padding ranges below0.225s, still below the0.25s gun interval. Listen in-game before accepting loudness and texture. No weapon firing budget was altered to solve sound overlap.

## Build/load and preservation

Keep Sins II2.0.3(318), Steam25127248, SDK24092025 and pinned schema commit `8e061033afe53b1393eaefd56617a3fd041eeb5f`. Original assets, installed game data, earlier mod packages and enabled settings are read-only for this work. Checkpoint commit is `ba144b41dccd10f4c2147d2f464861dd81f1aaaf`; prior0.12 ZIP SHA-256 is `e0575d558cd8c7f7893b3bd3c6520132b704c51cd15c9514c0b2b126ef81c73c`. Detailed frozen hashes are in `audit/update13/checkpoint.json`.

```sh
python3 tools/update13_audio.py
python3 tools/build_update13.py
python3 tools/build_update13.py --validate-only
```

Audio generation and the package builder refuse existing outputs. Do not run generation again to validate an existing package. `--package-existing` validates/packages an already assembled candidate without regenerating resources, and refuses an existing ZIP. Full builds require the local ignored model/audio resources and exact worker contracts listed in `audit/update13/integration-inputs.json` and `reviewed-inputs.json`; missing dependencies fail explicitly. No assets are downloaded or replaced. Worker reports record asset reproduction in their separate worktrees.

At the workstation, extract `build/experiments/expanse_update13.zip` into a new `expanse_update13` directory in Proton's `steamapps/compatdata/1575940/pfx/drive_c/users/steamuser/AppData/Local/sins2/mods`. `.mod_meta_data` belongs immediately inside that directory. Enable **only The Expanse — 0.13 MODEL & AUDIO POLISH** among Expanse variants, then apply. All earlier ships and audio are included. The agent does not install, enable or launch this build.

Main owns the integration, skin/audio bindings, scoped unit/mount/effect updates, validators and documents. Isolated worker A owns Scirocco (`tools/update13_scirocco*`, `audit/update13-a`), B the Morrigan/Raptor/Pella hulls (`tools/update13_hulls*`, `audit/update13-b`), C Sunflare (`tools/update13_sunflare*`, `audit/update13-c`). Main audio recipe is `tools/update13_audio.py`; combined builder is `tools/build_update13.py`. Editable resources and game outputs are separate. [Asset attribution and edits](../ASSET-SOURCES.md) remain applicable. Source/documentation may be pushed under existing authorization; no model, recording or texture derivative is published.

Use U13-1 through U13-5 in the [existing checklist](manual-test-checklist.md), recording observations in the [runtime record](../audit/manual-results.md). Start with model loading/appearance, then twelve physical turrets, scout orientation, sound mix, and save/reload. Remaining U12 gameplay gates are not automatically passed by this polish release.

## Completed offline checks

The929-file package passes22 changed-entity schema checks, eight integrated mesh checks, thirteen Scirocco mount-frame checks and2,696 resolved references across nine ship graphs. All ability/weapon gameplay values compare against0.12; only the reviewed Scirocco turret offsets/mount geometry and scout spatial data differ. Eight armed Expanse skins receive the new PDC sound list. Worker checks additionally validate material mappings, UI sizes, original preservation, normals/UVs and bounded turret clearance. The Scirocco rail binary and equipment positions are unchanged.

Selected assembled counts: Scirocco98,455; Morrigan34,217; Raptor94,823; Pella95,523; Sunflare17,741. Extra Scirocco/Morrigan faces result from paint boundaries and supports, with no new whole-model simplification. Raptor/Pella triangle counts and geometry stay intact.

All17 frozen trees,20 previous ZIPs, new references/originals and enabled settings remain unchanged;62 schemas and527 recorded installed dependencies still match the pinned audit. Package SHA-256: `3b7904e215a051cee3c633f4b0d470cc0a536d1b1ea49f4bcde877ce35d560dc`; tree SHA-256: `465ed0cf0b3ab2801ecd1fbb1d7ea0d0d56b98c16525129f17200422e77a0568`. Source commit and dependency hashes are in the adjacent ignored `.provenance.json`. These are offline results only.
