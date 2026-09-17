# 0.28 B120 Combined Fleet alpha

**Public release:** [v0.28-b120-c4](https://github.com/Blean69/The-Expanse-Sins-of-Sol/releases/tag/v0.28-b120-c4)

| Archive | Purpose | SHA-256 |
|---|---|---|
| `expanse_balance28_B120_combined4_release.zip` | Public alpha download, with path-free asset record | `f3ca5294c49664d49080bb5372062c5a8d795dc80bbb20e90feb34309f205620` |
| `expanse_balance28_B120_combined4.zip` | Preserved local candidate and installed copy | `70513486f44dd65708c81f1c63e1a1dd707378cc82e1d881f8e2b32f223ff4c6` |
| `expanse_balance28_B120.zip` | Frozen three-faction rollback | `42b1cf0b31c56f1c48f2a0d89dc69181cb2545b97b4fbf4847ee22cbf0ad73c2` |

The release ZIP is 434,348,460 bytes and contains 2,320 files. Its **only decompressed file change** from the local candidate is `ASSET-SOURCES.md`, updated to remove machine-specific paths and improve credit wording. All game definitions, models, textures, sounds and the menu scene are byte-identical. ZIP integrity and entry-by-entry comparison passed.

The local C4 candidate passed offline JSON/schema, reference, prerequisite and unique research-position checks. The MCRN, UNN and OPA player definitions are byte-identical to B120. A prior local install check matched the candidate files, and C4 is enabled locally. **No C4 game launch, combat, save/reload or multiplayer pass has been observed.** See `audit/balance28_combined4/` for static results. The 0.27.5 menu package remains the previously user-tested baseline.

The [asset record](../ASSET-SOURCES.md) includes known credits and reported permissions. Some third-party model and recording redistribution terms remain undocumented; see [release readiness](open-source-readiness.md).
