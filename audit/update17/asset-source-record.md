## 0.17 supplied fleet voice recordings

User supplied 24 MP3 recordings and requested ship/event integration. Original files are preserved unchanged in local assets/original/voice17 with hashes in audit/update17/checkpoint.json. Twenty-three clips are normalized to -18 LUFS (0.6 LU tolerance), encoded as 44.1 kHz mono Vorbis q6 with measured true peak no higher than -1.5 dBTP. Full timing is retained without trimming or reconstructing words. Input and output measurements appear in audit/update17/audio-intake.json.

“Pella bringing up the railguns” remains held locally, outside the playable package: Pella has no railgun. This audio release changes dialogue bindings only; music, weapon sounds and existing gameplay are preserved. Source-only Git distribution excludes original and processed audio and built packages. No listening or in-game voice-trigger validation is claimed.
