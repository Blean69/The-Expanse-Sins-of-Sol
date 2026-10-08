# 0.29.1 — Sol at War hotfix

**Release:** [v0.29.1](https://github.com/Blean69/The-Expanse-Sins-of-Sol/releases/tag/v0.29.1) · **Previous version:** [0.29.0](https://github.com/Blean69/The-Expanse-Sins-of-Sol/releases/tag/v0.29.0)

| Archive | Size | Files | SHA-256 |
|---|---:|---:|---|
| `expanse_sol_at_war_v0.29.1_sins211.zip` | 519,614,469 bytes | 3,194 | `0d102a51649ef5821604224a0ec8a0939b13387cdc8449067aaf5f79c51f1000` |

The archive targets **Sins of a Solar Empire II 2.1.1** and was diagnosed and tested on 2.1.2. It has `.mod_meta_data` at the ZIP root. Extract it into a new folder under the game's `mods` directory, enable only this Expanse package, and begin a fresh match. Do not layer it over the 0.29.0 installation.

0.29.1 fixes the MCRN being unable to build Morrigans. 0.29.0 registered 31 unit tags where the game reads 30, so the game rejected the tag list and the Morrigan's 18-ship limit showed as already full. Four unused hull-identity tags were removed, leaving 27. Ten files differ from 0.29.0: the unit-tag list, six ship definitions that carried the removed tags, and the package's metadata, README and release notes. The other 3,184 files are byte-identical. See the [0.29.1 hotfix notes](release-notes-v0.29.1.md) and the [0.29.0 release notes](release-notes-v0.29.0.md).

The project owner installed 0.29.1 and briefly tested it as MCRN, and reported that it looked good. Offline archive, unit-tag reference and checksum checks passed. This is not a claim that every scenario, save/reload path or multiplayer has been tested; in particular, whether MCRN trade escorts and garrison ships count toward the Morrigan limit has not been checked in a long match.

The GitHub source tree intentionally omits generated meshes, textures, audio and game binaries. The release ZIP is the playable artifact. Project-authored source uses [PolyForm Noncommercial 1.0.0](../LICENSE); third-party assets retain their own terms, as discussed in [source and asset terms](open-source-readiness.md). The project owner confirmed public redistribution rights for the included assets; source-by-source license details are not independently verified here.
