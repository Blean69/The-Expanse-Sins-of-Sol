# Installed version and official schema evidence

Inspection date: 2026-09-12. Installed game data was treated as read-only. Local mods were copied only into the game's **user-data** mods directory; enabled-mod settings were not changed.

| Evidence | Observed value |
|---|---|
| Flatpak Steam config | `/home/haker/.var/app/com.valvesoftware.Steam/.local/share/Steam/steamapps/libraryfolders.vdf` |
| Library entry 4 | `/run/media/haker/NVME 2/SteamLibrary` |
| Game | `steamapps/common/Sins2` under that library |
| Game manifest | `steamapps/appmanifest_1575940.acf`, build `25127248`, public branch |
| Existing game log | `steamapps/compatdata/1575940/pfx/drive_c/users/steamuser/AppData/Local/sins2/logs/sins2_log_472.txt`, line 2: version `2.0.3 (318)` |
| SDK | `steamapps/common/Sins of a Solar Empire II - Mod Tools` |
| SDK manifest | `steamapps/appmanifest_3172890.acf`, build `24092025` |
| Current official SDK commit | `8e061033afe53b1393eaefd56617a3fd041eeb5f`, 2026-07-07 |
| Schema comparison | All 62 official `json_schemas` blobs match installed bytes; see `audit/schema-comparison.json` |
| MeshBuilder build info | Installed `MeshBuilder/bin/MeshBuilder.buildinfo`, build time 2026-07-07; stored SDK internal SHA differs from public packaging SHA |

The log predates this project: it identifies the installation, **not a mod test**. Build IDs and hashes are stronger evidence than directory timestamps. The official public SDK has no separate `2.0.3` schema tag verified here; instead, its current schemas match the installed SDK and the touched installed unit/skin data validate against them. That does not certify the engine's runtime behavior.

The installed schemas declare Draft 7 while also using `unevaluatedProperties`. Draft 7 validators do not enforce that later keyword. The build therefore also compares the generated unit and skin structurally against vanilla, permitting only the explicitly identified changes. No new guessed game fields are introduced. `.localized_text` and `.mod_meta_data` have no dedicated schemas in this installed set: their structure comes from installed localization and current official mod documentation.

527 referenced installed files have recorded SHA-256 values in `audit/installed-file-hashes.json`. `tools/build.py verify` checks them and all schema hashes for drift. Builds stop on a changed reference. These checks cover inspected references, not every byte of the entire installation. Game and SDK references were never opened for writing.

Official sources:

- [SDK and MeshBuilder documentation](https://github.com/StardockCorp/sins2modtools)
- [Official current mod guide](https://stardock.atlassian.net/wiki/spaces/SSEFW/pages/2284027951/How%2Bto%2BCreate%2Ba%2BMod)

System Wine failed during isolated initialization. Installed Proton 10.0 successfully ran MeshBuilder and Texconv using `.tools/proton-prefix`; it never reused or modified the game's Proton prefix for conversion. Tools are headless command-line runs, not game runs.
