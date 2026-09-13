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
# Audio candidate intake

## Six-PDC polish derivative

The local polish derivative adds winding correction, tangent-frame repair, separation into six yaw/pitch turret assemblies, static UI portrait rendering, contrast adjustment, silhouette projection, DPI resizing, selection outlines and mod-logo layout. All ship geometry and UI imagery derive from the credited Jakub.Vildomec Tachi model under its recorded CC-BY-4.0 license. The original archive and extracted master remain unchanged. Editable geometry/rendering recipes and generated game assets are kept separately. No new audio or third-party imagery is included, and no publication or redistribution was performed in this assignment.

Audio candidates remain outside all mod outputs. See [the local audio feasibility and permission record](docs/audio-feasibility.md) and `audit/audio/local-source-audit.json` for selected installed Space Engineers source IDs, exact paths, hashes and unresolved per-recording permissions. No audio was copied, converted or distributed.

## Rocinante hero source intake (2026-09-12)

User-supplied archive: `/home/haker/Downloads/Rocinante_(The_Expanse).zip`. The user explicitly confirms: “Dont worry about the license - we got permission to use it”. Record this as **user-attested permission to use the asset**. The archive contains no license file; creator, source URL, exact license terms and attribution requirements remain unspecified. No public distribution or publication was performed. Do not substitute the original Tachi author's CC-BY license for this separate asset.

The original package and extracted master are preserved unchanged in the isolated geometry worker's `assets/derived/geometry03-b` intake structure (exact paths/hashes in the hero audit). Stand removal, deployment-pose baking, normalization and any simplification apply only to separate editable/game derivatives. The supplied animation remains preserved in the editable source; game-triggered deployment is not established.

Hero archive SHA-256: `2fef806f80c65f138eed9b877c6cd1ae98f12e597856b96cfb1c6676a16af3e6`. Preserved package: `assets/derived/geometry03-b/hero-original/Rocinante_(The_Expanse).zip`; extracted files: sibling `hero-master/`, both in `/run/media/haker/NVME 2/expanse-workers/tachi-one-pdc/`. Individual master hashes and relative-animation measurements: `audit/geometry03-b/hero-asset-audit.json`.

Hero derivative changes: remove6,068 printing-stand triangles; retain161 remaining mesh parts; simplify426,612 stand-free triangles to26,707 using the already pinned meshoptimizer; bake the source's deployed pose after removing presentation motion. Add228 original prototype-fitting triangles (keel railgun, supports and two launch ports), for26,935total. The fittings are project-authored additions, not identified original TV geometry. Supply flat-color textures from the source's material factors; no Tachi paint/textures are substituted. Original animated, stand-free animated, normalized deployed and armed derivatives remain separate. Hero UI renders the new deployed model. Game-triggered animation remains unimplemented.

Corvette0.3 derivative adds801 targeted interior triangles and912 support triangles to the14,622-triangle polish model (16,335total). Original PDC pivots, muzzles and authored geometry stay intact. These changes and all generated mesh/material references are audited in `audit/geometry03-b/`.
# Donnager0.4 intake and hero corrective derivative

The supplied Donnager archive `/home/haker/Downloads/mcrn_donnager_the_expanse.zip` has SHA-256 `b03d70d6180b7c6ff50db22df883f576ebb3981c5d4d138f8bdf1e7434079562`. Its own packaged license identifies “MCRN Donnager (The Expanse)” by **owlstraw**, profile https://sketchfab.com/strawfinch, source https://sketchfab.com/3d-models/mcrn-donnager-the-expanse-05e9f9006d914fcd96e95fbd452aaa28, under **CC-BY-4.0**, http://creativecommons.org/licenses/by/4.0/. Exact supplied attribution is preserved in `audit/donnager04-c/asset-source-and-permission.json` and the untouched extracted master. Keep creator/source/license credit and identify changes when sharing a derivative. This intake created uniformly normalized planning scenes and separated two rail assemblies; no PDC splice or game asset distribution occurred. A future splice must retain the separate Tachi donor credit too.

Original/master and editable Donnager paths are under `/run/media/haker/NVME 2/expanse-workers/validation/assets/derived/donnager04-c/`. Audit and source/output manifests identify individual file hashes. Exporter scale is not treated as meters;475.5m/46m is a provisional planning convention.

Rocinante0.4 is a separate corrective derivative under the already recorded user-attested permission. It corrects the small axial normalization tilt, replaces damaging permissive simplification with a conservative normal-aware derivative, separates six complete source cannon assemblies, and adds project-authored aiming supports. Source animations, archive, extracted master and0.3 derivatives remain unchanged. Aiming joints are new measured candidates rather than a claim that the source deployment animation is a usable game turret rig. Full counts and source partition evidence are recorded in `audit/geometry04-b`. No model was pushed or published.
# Amun-Ra source intake and optional torpedo appearance

The user supplied `/home/haker/Downloads/Amun-Ra_Class_Stealth_Ship_[The_Expanse].zip` and explicitly confirmed permission to use the model. Record this as user-attested permission. The archive contains no creator/license text; no specific license or attribution terms are inferred from the other models. Archive SHA-256: `fa0d7ee158c53ee1e07d362eb1cfc49ab08fe3da9f5b11c2cd414c7c50d71441`.

Untouched original/master: `/run/media/haker/NVME 2/expanse-workers/validation/assets/derived/amun05-c/`. Exact hashes and source references are in `audit/amun05-c/`. Separate editable torpedo extraction selects the actual named source subtree, preserves its 1,600 triangles, UVs and four source atlases, and uniformly normalizes it to the Javelis missile length. No source part is reconstructed from a substitute model. Game conversion, where completed, uses a separate `torpedo05-b` derivative with compiler coordinate/winding preparation, generated tangent repair and resized/repacked textures. No archive or extracted master is edited, and nothing is published.

The complete scene has four turret assemblies and fifteen pods; it is not an already integrated three-PDC stealth ship. User permission to use the source is recorded independently of those implementation limitations.
