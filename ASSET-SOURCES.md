# Asset sources and permissions

## Supplied model

- Title: **MCRN Tachi [Expanse TV Show]**
- Creator: [Jakub.Vildomec](https://sketchfab.com/Jakub.Vildomec)
- Source: https://sketchfab.com/3d-models/mcrn-tachi-expanse-tv-show-76fc983ab08c449b9042491a00e621cf
- Model ID: `76fc983ab08c449b9042491a00e621cf`
- Exact license in supplied `license.txt` and glTF metadata: **CC-BY-4.0**, https://creativecommons.org/licenses/by/4.0/
- Package: `mcrn_tachi_expanse_tv_show.zip`, 66,985,861 bytes.
- SHA-256: `47abb4ac87c2af477a906bdab4e87f20551e72917877e6dfa489a11946320142`
- Evidence: untouched archive under `assets/original/`; extracted license and metadata under `assets/source/tachi/`; per-file hashes in `audit/source-checksums.json`.
- Received from the user and inspected 2026-09-12. Sketchfab's page returned HTTP 403 during verification; license identification is from the supplied package, not an independently observed current download page.

Required supplied credit:

> This work is based on "MCRN Tachi [Expanse TV Show]" (https://sketchfab.com/3d-models/mcrn-tachi-expanse-tv-show-76fc983ab08c449b9042491a00e621cf) by Jakub.Vildomec (https://sketchfab.com/Jakub.Vildomec) licensed under CC-BY-4.0 (http://creativecommons.org/licenses/by/4.0/)

Changes in this derivative: per-part geometry simplification, uniform scaling and recentering to the Cobalt envelope, compiler coordinate conversion, texture resizing and DDS encoding, roughness-factor baking, flat normal maps for text decals, zero team-color/emissive masks, and game material/attachment setup. Original source remains unchanged. No affiliation or endorsement is implied.

Keep the credit, license link, and change notice with any shared derivative and on its release page. The license permits adaptation and commercial use, with attribution and change identification; do not add restrictions inconsistent with that license. See the [CC BY 4.0 terms](https://creativecommons.org/licenses/by/4.0/). The model license is evidence of the creator's asset permission; this record does not establish separate rights to Expanse trademarks, logos, characters, or other franchise property. No separate franchise permission was supplied.

## Installed game and SDK

Sins of a Solar Empire II, Ironclad Games / Stardock Entertainment. Local game references are read only. The installed SDK's `License.md` says proprietary / all rights reserved. SDK binaries, schemas, vanilla models, textures, effects, and audio are **not** vendored into this repository. Build scripts read the user's own installation and generate the small overrides locally. Hashes, paths, relationships and selected factual values document the inspection.

## Build tooling

- [Official Sins II SDK](https://github.com/StardockCorp/sins2modtools), installed Steam build 24092025; schemas match commit `8e061033afe53b1393eaefd56617a3fd041eeb5f`. MeshBuilder is executed in place with outputs directed to the project.
- [meshoptimizer](https://github.com/zeux/meshoptimizer), MIT, revision `bba256eaa24039b6f93c773063ff7c20143ae0db`. Kept in ignored `.tools/` with its upstream license. Its attribute-aware simplifier is compiled locally; not bundled with the mod.
- [Microsoft DirectXTex / Texconv](https://github.com/microsoft/DirectXTex), MIT, `may2026` release; source URL/digest recorded in `audit/texconv-source.json`. Private build dependency, not bundled.
- [Sins2 Blender extension](https://github.com/largeBIGsnooze/sins2-blender-extension): binary-prefix reader used as a format reference only. The current mesh trailer is opaque to that reference; official MeshBuilder generates all game meshes.
- Python, NumPy, Pillow and jsonschema are build dependencies. Diagnostic previews use CPU geometry projection, not AI-generated assets and not screenshots of Sins II.

`assets/original`, `assets/source`, `assets/derived`, `.tools`, and `build` are separate and ignored by Git. Keep local originals backed up; retrieve the licensed package separately on another machine. No upload of model assets or a public release was performed by this setup.
