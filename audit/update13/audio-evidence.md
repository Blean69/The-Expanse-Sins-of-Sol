# PDC overlap evidence

The installed `sounds/weapon_muzzle_tech_pointdefense_autocannon.sound` profile uses positional, non-looping, non-streaming playback, minimum attenuation100 and group `weapon_muzzle_light`. The accepted custom clip inherited that profile. It decodes to roughly0.896 seconds and is bound to a muzzle triggered every0.25 seconds, allowing about four simultaneous copies per gun before considering other guns.

The installed `uniforms` and the pinned62-schema SDK directory were searched for audio/sound groups, concurrency/instance limits and cooldown hooks. No configurable per-ship voice limit or dedicated sound schema was found. The earlier complete installed `.sound` key survey in `docs/audio-feasibility.md` is consistent with the current observed profile. This bounded result is not a claim that the engine has no internal sound limiter.

The new `.sound` definitions use only the same five keys, changing minimum attenuation100→70. Four existing-waveform windows and a quieter mix mitigate repetition through assets, not invented engine fields. The accepted clip, original MP3 and previous normalized WAV stay byte-identical. All eight armed Expanse skins point their existing PDC muzzle alias to the four new sound IDs; other muzzle, hit, dialogue, music and gameplay definitions are unchanged.

The `audio.json` report records exact source offsets, fades, gain, waveform hashes, Vorbis container and decoded timing, and synthetic mix statistics. FFmpeg's Vorbis decoding can expose block padding: source WAVs and containers are0.20s; decoded samples remain0.1973–0.22s, below0.25s. Padding is not treated as intentional extra recording. The temporary−6dB comparison is not packaged; the selected reports are−10dB relative to the prior normalized recording.

No engine playback or human listening result is claimed. Test the new mix at consistent SFX volume, multiple zoom levels and ship counts, especially one small ship versus sixteen active Donnager PDCs. Four variant candidates do not establish exactly how the engine selects from a list or limits concurrent sounds.
