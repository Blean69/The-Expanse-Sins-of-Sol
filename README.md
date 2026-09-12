# The Expanse — Sins II corvette prototype

Two local mods are built and installed **but not enabled**. The game has not been launched for this project. Start with the name test, then the visual baseline. Neither package implements the proposed torpedo/PDC combat yet.

| Package | What it changes |
|---|---|
| `build/expanse_cobalt_name.zip` | Exactly two English localization entries: **MCRN Corvette-class** / **Fast-attack torpedo frigate** |
| `build/expanse_corvette_visual.zip` | The same text, the Cobalt's visible mesh, and its two fixed-gun muzzle coordinates. All gameplay values and the vanilla autocannon definition are preserved. |

The role description is the intended design, **not a claim that the baseline fires torpedoes**. This is an ordinary Cobalt replacement in existing build menus, not a unique Rocinante hero. All users of the same Cobalt definition/skin are affected, including applicable neutral/garrison uses. Garrison-specific localization remains vanilla because the name-only test deliberately changes only two keys. No factions, research, economy, AI, navigation, stealth, or railguns have been redesigned.

The source model has **140,863 triangles**; the derivative has **14,622**, with all 355 named mesh parts and all six PDC assemblies retained. The original archive and extracted master are untouched. The optimized source, normalized editable model, and 12 editable yaw/pitch rig candidates are separate from compiled game output. The baseline PDC geometry is static; its two front guns stand in for the Cobalt's existing fixed autocannon.

Validated against installed **Sins II 2.0.3 (318), Steam build 25127248**. All 62 installed SDK schemas match current official commit `8e061033afe53b1393eaefd56617a3fd041eeb5f`. See [environment evidence](docs/environment.md), [Cobalt reference trace](docs/cobalt-reference-trace.md), [asset audit](docs/asset-audit.md), and [source/license record](ASSET-SOURCES.md).

## At the PC

1. Start Sins II normally through Flatpak Steam. Open Modding and find the local mod `expanse_cobalt_name`. Enable it and apply changes. The current UI may expose local mods through its installed/manage views.
2. Start a fresh TEC test game. Check the name and description and that unrelated localized text still displays correctly. Follow [the checklist](docs/manual-test-checklist.md).
3. Disable the name test and enable only `expanse_corvette_visual`. Apply changes and start a new test game. Test the visual baseline before introducing combat changes.
4. Keep a separate save per mod variant. To return to vanilla, disable the mod and apply changes. Do not overwrite existing campaign saves during testing.

Installed user-mod directory:

```text
/run/media/haker/NVME 2/SteamLibrary/steamapps/compatdata/1575940/pfx/drive_c/users/steamuser/AppData/Local/sins2/mods/
```

[Build and load instructions](docs/build-and-load.md) include exact commands and portable Windows steps. [Combat prototype notes](docs/combat-prototype.md) capture the six rotating PDCs, short-range high DPS / low penetration, long-range interceptable torpedoes, and saturation vulnerability goals. Schema-checked definition candidates are generated separately under `build/combat-candidates`; they are intentionally incomplete and not installed.

## Observed status

- Passed offline: package integrity, reference tracing, schema/hash checks, official MeshBuilder JSON and binary conversion, DDS format checks, geometry comparison, and exact gameplay-diff checks.
- Not run: game loading, construction, movement, selection, firing, destruction, save/reload, turret rotation, interception, targeting priorities, or performance tests. The checklist records all runtime results as **NOT RUN**.
- Known visual placeholders: vanilla Cobalt UI icons, voice/audio, shield mesh/effect shape, and death effects remain. Material appearance, alpha decals, exhaust alignment and small-detail readability need in-game review.

Repository: https://github.com/Blean69/The-Expanse-Sins-of-Sol . Assets, SDK dependencies and generated packages are ignored by Git; source scripts and audit records are tracked locally. See [ASSET-SOURCES.md](ASSET-SOURCES.md) before sharing the model derivative.
