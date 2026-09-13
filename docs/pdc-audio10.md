# PDC audio0.10.1

Use `build/experiments/expanse_donnager10_pdc_audio_ready.zip`. This is a full combined mod: install its contents in a folder named `expanse_donnager10_pdc_audio` under the recorded Proton `sins2/mods` directory, then enable only **The Expanse —0.10.1 DONNAGER + PDC AUDIO**. Keep the existing0.9/0.10 folders for rollback. Nothing was installed or enabled by the agent.

The supplied0.896-second mono clip is preserved unchanged and normalized to approximately−18LUFS,48kHz Vorbis. It replaces only the PDC muzzle sound in four skins: Corvette6 guns, Rocinante6, Amun-Ra3 and Donnager16. It retains the installed positional, non-looping `weapon_muzzle_light` sound profile and distance handling. Damage, firing cadence, turrets, other sound effects, dialogue and music are unchanged.

Original: `assets/original/pdc-audio10/PDC.mp3`; editable WAV: `assets/derived/pdc-audio10/PDC-normalized.wav`; generated audio: `build/pdc-audio10/game/sounds`. Source, permission context and measurements are in `audit/pdc-audio10`.

The reboot truncated the first ZIP, while the full mod folder and normalized assets remained intact. The interrupted ZIP and its historical summary/provenance remain preserved; use only the **_ready.zip** archive. `python3 tools/build_pdc_audio10.py --recover` validates the existing assets and creates that fresh archive without rewriting them; it refuses an existing archive. Add `--validate-only` to verify the recovered archive again.

Offline checks cover both original/derivative hashes, decoded loudness/peak/duration/codec, four pinned skin schemas, all31 PDC sound bindings, exact non-audio preservation and ZIP/tree integrity. See `validation.json` and `recovered-package-summary.json`. In-game playback/listening: **NOT RUN**. Test one ship first, then several firing together; check burst overlap, mix and zoom attenuation.
