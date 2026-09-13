# Optional Amun torpedo appearance variant

The supplied model contains an actual separate torpedo. It is now compiled into a **self-contained alternative** to the combined 0.4 package:

`build/experiments/expanse_rocinante04_amun.zip`

Load this package alone, **instead of** `expanse_rocinante04` or any earlier Expanse variant. It contains the complete corrected corvette/Rocinante experiment; it does not require stacking an add-on above another mod. No installed mod or enabled-mod setting was changed.

The package has 204 files, SHA-256 `0037f2f5d06046bd442231372690f999f84a6fefbca023955017a4c3a2368e74`, tree hash `7734eeb09fa0f2b48d849f0721d2fa35c742b536b0abc2ae14318aba1e568492`. Metadata display version is 0.4.1. The `torpedo05` source-work name does not mean that the Amun stealth ship is included.

Compared with 0.4, only the private Martian projectile skin/appearance and its enclosing sphere change, plus metadata/asset credit. Its 1,600-triangle mesh retains the source's shape and UVs at Javelis length, 16.510756 game units. Four 1024² game DDS maps derive from unchanged 4096² source atlases. Normal-map direction and the emissive-mask approximation still need an in-game close view. The trail uses the stock Javelis effect with a measured `exhaust.0` point at the custom model's aft end.

**Martian damage, health and movement are unchanged:** 750 damage, 1000 penetration, 1250 speed, 50 hull / 100 armor / 50 armor strength, and the same magazine timing. The existing Javelis collision box encloses the new mesh and is retained. Its enclosing radius increases from 8.274259 to 8.287338, about 0.16%, to include the custom vertices. That explicit bounds adjustment is not a health change. Test grazing interceptions rather than assuming identical physical hit behavior.

This variant does **not** use the stronger but more fragile Amun combat candidates, and does not contain cloak or boarding abilities. The accepted hero railgun, six PDC budgets, navigation, hero abilities and all other 0.4 files remain byte-identical. It inherits the experimental hero's 92,067-triangle performance concern.

## Build and checks

Main owns `tools/build_torpedo05.py` and the final private unit/skin edits. Asset worker C owns the extraction in `audit/amun05-c`; worker B owns the compiler derivative in `audit/torpedo05-b`. Shared inputs remain read-only. Build dependencies and source hashes are in the package's `.dependencies.json` and `.provenance.json` sidecars, outside the ZIP.

```sh
python3 tools/build_torpedo05.py \
  --game '/run/media/haker/NVME 2/SteamLibrary/steamapps/common/Sins2' \
  --sdk '/run/media/haker/NVME 2/SteamLibrary/steamapps/common/Sins of a Solar Empire II - Mod Tools' \
  --worker '/run/media/haker/NVME 2/expanse-workers/tachi-one-pdc' \
  --validate-only
```

For a fresh build with all ignored dependencies present and no existing output, omit only `--validate-only`. The builder refuses overwrites, missing dependencies and changed reviewed inputs. It never installs or starts the game. The separate `audit/torpedo05/packaged-asset-sources.md` snapshot keeps attribution reproducible as later source records are added.

Passed: 52 package schema checks, authored unit/skin/action/projectile reference resolution, exact health/physics/stat preservation, generated material/texture hashes, one independent binary geometry check and the worker's official compiler/winding/tangent/exhaust gates. ZIP/tree correspondence and frozen previous outputs match. The 0.4 validator also rejected four negative cases: localization drift, hero navigation drift, projectile health drift and doubled PDC damage. These are offline checks only.

On the workstation, extract into a new `expanse_rocinante04_amun` folder under the existing Proton `AppData/Local/sins2/mods` directory. Disable older variants and Apply Changes with this one enabled. Use a disposable save. First inspect the custom projectile's nose, trail and normal shading; then test launch cadence and interception during an explicit ship attack; then inspect all hero turret arcs and hull surfaces; finally save/reload and compare performance. The existing manual checklist/results log remains authoritative. All new runtime tests are NOT RUN.
