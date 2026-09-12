# Build and load

The ready packages are under `build/`, and both variants have already been copied to the observed user-mod directory. They are not enabled. Use one variant at a time.

## Paths and prerequisites

Project root on this workstation:

```text
/run/media/haker/NVME 2/expanse-mod
```

Scripts default to the sibling `SteamLibrary` installation. On another machine, set `SINS2_GAME` and `SINS2_SDK` to the installed game and official SDK folders. Build paths are always inside this project. The scripts require Python 3 with NumPy, Pillow and jsonschema. They were run with Python 3.14 here; the SDK's recommendation for Python 3.12 applies to its own helper scripts, which this build does not invoke. MeshBuilder and Texconv are called directly.

The SDK remains installed separately. Do not copy it into Git. Microsoft Texconv is a private dependency at `.tools/texconv.exe`; source/release is recorded in `audit/texconv-source.json`. On Linux, the installed Proton runtime used successfully is:

```text
/home/haker/.var/app/com.valvesoftware.Steam/.local/share/Steam/steamapps/common/Proton 10.0/files/bin/wine64
```

Conversion uses `.tools/proton-prefix`, not the game's prefix. The first runtime initialization requires normal host Wine/Proton socket access; a restricted sandbox can block it. Never solve that by running the game or SDK build helper with output paths inside the installation.

## Reproduce the name-only mod

From the project root:

```bash
python3 tools/build.py name
```

Result:

```text
build/expanse_cobalt_name/
    .mod_meta_data
    localized_text/en.localized_text
build/expanse_cobalt_name.zip
```

The ZIP contains `.mod_meta_data` at archive root, not an extra enclosing directory. The localization file contains exactly two existing keys. No unit, skin, weapon, manifest, model, texture or faction override is required for this text-only test. The `.mod_meta_data` contains only the officially documented `compatibility_version: 2`; the folder name identifies the local mod. Confirm compatibility in the actual current UI before testing; no runtime compatibility success is claimed.

## Reproduce asset preparation

Retrieve the same licensed source package separately. Never reconstruct the master from generated `.mesh` files.

```bash
python3 tools/intake.py '/path/to/mcrn_tachi_expanse_tv_show.zip'
python3 tools/audit_assets.py
```

Install ordinary Python dependencies in a local virtual environment if needed. Geometry simplification uses a pinned upstream C library; the older Python meshoptimizer wrapper is not required by the final scripts:

```bash
mkdir -p .tools
git clone https://github.com/zeux/meshoptimizer.git .tools/meshoptimizer-current
git -C .tools/meshoptimizer-current checkout bba256eaa24039b6f93c773063ff7c20143ae0db
g++ -O2 -std=c++11 -shared -fPIC \
  .tools/meshoptimizer-current/src/simplifier.cpp \
  .tools/meshoptimizer-current/src/allocator.cpp \
  -o .tools/libmeshoptimizer.so
python3 tools/optimize_model.py
python3 tools/prepare_model.py
```

The exact archive is SHA-256 locked. A different package requires a new intake/permission audit. The simplified source retains each named part under `assets/derived/optimized-source`. `assets/derived/baseline/mcrn_editable.gltf` adds a reversible uniform fit transform. The compiler-specific glTF/bin live beside it but are separate files. The original archive and master are not modified.

Download the recorded Microsoft `may2026` Texconv release to `.tools/texconv.exe`:

```text
https://github.com/microsoft/DirectXTex/releases/download/may2026/texconv.exe
```

Use Microsoft's release checksum/digest in `audit/texconv-source.json` to verify it. Then compile on this Linux workstation:

```bash
python3 tools/compile_assets.py --wine \
  '/home/haker/.var/app/com.valvesoftware.Steam/.local/share/Steam/steamapps/common/Proton 10.0/files/bin/wine64'
python3 tools/build.py visual
python3 tools/validate_outputs.py
```

MeshBuilder generates both `.mesh_json` for inspection and binary `.mesh` for the game. `--fill_triangle_facing_grid` populates surface-facing data used by effects. The compiler adds the mesh filename prefix to material IDs; the packager uses **those emitted names**, not guessed identifiers.

Texconv generates full mipmaps. BC7 uses its documented fast mode `-bc q` with CPU compression. Normal maps use BC5_SNORM and `--x2-bias`. BC5S legacy DDS headers are valid and match the installed Cobalt normal texture convention; BC7 uses the DX10 header. CPU conversion can take several minutes. `--skip-textures` skips texture conversion only when maps are already up to date. Rebuild textures after modifying any source map.

On Windows, `compile_assets.py` runs without `--wine`; use `python` in place of `python3`, set the two installation variables, and keep Texconv at the same relative location. The Linux C-library optimization step uses `.so`; for an all-Windows optimization build, compile the pinned library as a DLL and update that local loader path, or perform optimization in WSL. **That all-Windows optimization path was not executed here.** Prepared glTFs can also be opened in Blender for non-destructive editing, then passed to the installed official MeshBuilder using its documented `--input_path`, `--output_folder_path`, and `--mesh_output_format=binary` flags.

Optional audit/next-stage preparation:

```bash
python3 tools/trace_game.py
OPENBLAS_NUM_THREADS=1 python3 tools/preview_geometry.py
python3 tools/prepare_pdc_rigs.py
python3 tools/stage_combat_definitions.py
```

Do not use a refreshed trace to silently bless a game update. `trace_game.py` records a new inspection snapshot; compare it to Git and re-audit version/schema compatibility before accepting changes. `build.py verify` checks against the existing snapshot and fails on changed referenced game data or schemas.

## Load or reinstall locally

Observed in-game Windows path: `%LOCALAPPDATA%\sins2\mods`.

Observed host path:

```text
/run/media/haker/NVME 2/SteamLibrary/steamapps/compatdata/1575940/pfx/drive_c/users/steamuser/AppData/Local/sins2/mods
```

For a fresh destination:

```bash
python3 tools/install_local.py name
python3 tools/install_local.py visual
```

These copies already exist from this setup. The installer refuses to overwrite an existing directory. For an update, close the game and back up/remove only the corresponding `expanse_*` user-mod folder before reinstalling. Never copy mod output over `steamapps/common/Sins2`.

In Sins II, open Modding, enable the local test, and apply changes. Start a new TEC game and follow [the manual checklist](manual-test-checklist.md). Use only one of the two project mods. Keep combat candidates outside the mods directory. Existing Cobalt text/skin mods may conflict through the same IDs; use a clean test playlist.

Logs live at the sibling `sins2/logs` directory. Preserve the first failing log and save. To unload, disable the mod and apply changes; to uninstall, remove its own user-mod directory while the game is closed. No game-file restore should be required.

Official workflow reference: [Stardock mod guide](https://stardock.atlassian.net/wiki/spaces/SSEFW/pages/2284027951/How%2Bto%2BCreate%2Ba%2BMod). No mod.io upload or public asset release was performed.
