# Hero UI from the actual new model

New owned tool: `tools/flight03_hero_ui.py`. Input is Worker B's actual `assets/derived/geometry03-b/hero/expanse03_hero_static.gltf` and matching buffer, with its three generated sRGB flat-color PNGs. The input has **26,707 triangles**. Compiler-input position Z is negated back into game coordinates before rendering. No Tachi model, texture, portrait or silhouette is used as input; only the generic CPU rendering functions and observed Sins UI dimensions are reused.

Output: `build/flight03-c/hero-ui/generated/` contains six private `expanse03_hero_*` brushes, 18 standalone PNG sprites at the observed 100/150/200 DPI sizes, and two optional root logo PNGs named `expanse03_hero_mod_small_logo.png` / `expanse03_hero_mod_large_logo.png`. The optional logos are distinct filenames so copying them cannot silently replace the ordinary corvette's mod-browser logos.

`hero-ui/integration-spec.json` supplies `hero_skin_patches[]` and `optional_root_logos`. Main integrator owns their application to the hero skin and mod metadata. No entity manifest is needed for these images/brushes. Copy generated assets only; keep the integration spec, source renders and audits outside loadable packages.

`hero-ui/source/` keeps an editable projected SVG silhouette, master PNGs and rendering recipe separate from game output. Source buffers/texture hashes are recorded. Double-sided CPU z-buffer rendering uses the actual flat material colors with the documented studio contrast lift; no in-game PBR shader, material texture detail or dynamic turret behavior is claimed.

All six brushes passed the pinned brush schema (blob `3e2e9a9c47b6ced821bd2b2ebb9e09f66d390c9f`); 20 PNG files passed size/mode/alpha checks. HUD pictures/logos are opaque; icons and tooltip portraits are transparent RGBA. Source bytes remained unchanged during rendering. Contact sheet `hero-ui/hero-ui-contact-sheet.png` was visually inspected: distinct gray/orange source material blocks, full visible ship silhouette and three separate tactical selection states. Python compilation passed.

Generated image/brush validation is mirrored in `audit/flight03-c/hero-ui-validation.json`; exact patches and source recipe are alongside it. These images inherit the new hero asset's source/license record from the main integrator/Worker B; do not attribute them to the earlier Jakub Tachi package by assumption. Add static portrait rendering, flat-color lighting, silhouette projection and DPI/selection-logo layouts to that new asset's derivative-change record.

Runtime GUI lookup, hero HUD/tooltip placement, team tint, DPI switching, tactical readability and logo display remain NOT RUN. No installation, game launch, main-package edit or publication was performed.
