# UN IPBM local bombardment visual

This package replaces only the visible projectile mesh used by native **local `planet_bombing`**. It is not a global weapon, a destructible missile entity, or the separately gated strategic impactor prototype. No damage, cooldown, range, targeting, supply, health, or gameplay definitions are included.

## Source and scale

The supplied `UN IPBM from The Expanse - 2639049.zip` contains trehn's [UN IPBM v2](https://www.thingiverse.com/thing:2639049). Its author describes the missile as seen at the beginning of Season 2, Episode 3. The archive records **CC Attribution–NonCommercial–ShareAlike**, without a version. Exact ZIP, STL, and local-reference hashes are in `audit/update25-ipbm/integration-spec.json`; the original archive remains unchanged.

The v2 source has **39,960 triangles**. Cleanup removes 1,584 exact zero-area faces and 64 numerical slivers (cross-product magnitude ≤1e−10 in source units), leaving 38,312 clean source faces. The existing local meshoptimizer library reduces this to **6,000 triangles**, with reported relative error **0.0002272**, below the 0.0007 limit. The model's nose, body ribs, aft collar, and nozzle silhouette remain visible in the packaged mesh preview.

The model is centered once, retains +Z as its nose direction, and is scaled to **16.5107555 game units long**, matching the accepted `expanse05_amun_torpedo` visual length. Print units are never used directly; this is a visual scale choice, not a claim about canon metric dimensions. Its ballistic body remains wider than the slim light torpedo.

White/gray UNN livery, circumferential bands, and repeated UNN markings are original procedural textures on new cylindrical UVs. The cylindrical seam uses a repeated atlas packed inside [0,1], avoiding SDK out-of-range UV warnings. Source base color alpha is opaque. No emissive gameplay shield mask is introduced. The native travel effect supplies the exhaust visual.

## Verified native integration pattern

The installed `trader_siege_frigate_planet_bombing.weapon` uses `weapon_type: planet_bombing`, projectile firing, and a skin-resolved travel alias. Its skin binds that alias to `Weapon_TechFrigatePlanetBombing_Travel.particle_effect`. That native effect already has one **mesh particle** referencing `weapon_trader_missile_nuke`.

The private effect changes exactly two values from that native pattern:

1. The mesh particle references `expanse25_un_ipbm`.
2. Its attachment node moves the centered mesh forward by half its length, preserving the native tail-origin convention.

The native exhaust emitter, particle lifecycle, attachments, and other effect fields remain unchanged. `tools/update25_ipbm_validate.py` reverses those two edits and asserts exact equality with the installed native effect. This is a verified existing pattern rather than a guessed `projectile_mesh_pattern_effect` schema.

Main integration should apply the provided alias entry to the appropriate ship's existing `skin_stages[].effects.effect_alias_bindings[]`. Use that ship's actual bombardment travel alias; do not replace the whole alias list or change its weapon values. The exact fragment is in `integration-spec.json` under `effect_fragment`.

The package contains **7 regular files / 1,872,192 bytes** under:

`build/update25-ipbm/game`

- Mesh: `expanse25_un_ipbm.mesh`.
- One private material and four texture dependencies.
- Travel effect: `expanse25_ipbm_local_bombardment_travel.particle_effect`.

Every file has a SHA-256 entry in the integration spec. There are no entities, manifests, symlinks, or Wine prefixes in the package.

## Observed validation and limits

SDK binary/JSON compilation with the official facing grid succeeded. All named transforms match; source-frame matching error is below 0.0000002 game units. The compiled mesh has zero triangles opposed to stored normals. Tangent-only repair preserved the official index/grid/trailer bytes. Material/DDS and stock particle resources resolve, output hashes match, and the visual length matches the accepted torpedo. Packaged-mesh previews were inspected.

**Not run:** in-game bombardment orientation/scale, particle appearance/lifetime, save/reload, or multiplayer. This cosmetic mesh has no independently targetable health. It must **not** be described as interceptable, and destroying an associated visible mesh cannot be claimed to cancel planetary damage. That acceptance test remains exclusive to a separately implemented real-object strategic prototype.

Rebuild using the existing dependency Python: `tools/update25_ipbm_art.py prepare`, `compile`, `preview`, then `tools/update25_ipbm_validate.py`. Compilation uses the existing local SDK/Wine pipeline and build prefix in place; it installs nothing and does not modify the game. The tool reuses already committed Murphy exporter and UN One preview helpers.
