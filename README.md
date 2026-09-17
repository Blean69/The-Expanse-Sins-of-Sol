# The Expanse: Sins of Sol

A Sins of a Solar Empire II mod built around ships and factions from *The Expanse*. The current local playtest candidate is **0.28 B120 Combined Fleet (C4)**. It preserves the B120 combat balance and adds a fourth, selectable sandbox faction with the combined MCRN, UNN and OPA roster. The three regular factions remain separate.

The project targets Sins II **2.0.3 (318)**, Steam build **25127248**, using the pinned official SDK schema commit `8e061033afe53b1393eaefd56617a3fd041eeb5f`. This repository tracks build scripts, definitions, documentation and audits. Generated game assets, supplied models and recordings, tools, and packaged mods stay outside Git.

## Current build

| Package | Purpose | SHA-256 |
|---|---|---|
| [B120 Combined Fleet](build/experiments/expanse_balance28_B120_combined4.zip) | Four factions; combined sandbox has 24 buildable hulls and 216 research subjects | `70513486f44dd65708c81f1c63e1a1dd707378cc82e1d881f8e2b32f223ff4c6` |
| [B120](build/experiments/expanse_balance28_B120.zip) | Three regular factions; frozen combat rollback | `42b1cf0b31c56f1c48f2a0d89dc69181cb2545b97b4fbf4847ee22cbf0ad73c2` |

The Combined Fleet ZIP has 2,320 files and passed offline schema, reference, research-path, starting-mode and archive checks. The three original faction player definitions are byte-identical to B120. It has been installed and enabled locally, but **no game launch or multiplayer test has been observed for C4**. Use a fresh game for testing. The B120 package remains the immediate rollback. See [Combined Fleet implementation](docs/balance28_combined4.md) and [release manifest](docs/current-release.md).

## What is implemented

- MCRN, UNN and OPA playable fleets with faction-specific hulls, production, military research, weapons, abilities and voices, plus the optional Combined Fleet sandbox faction.
- Ship models and UI art for the Rocinante, Tachi, Morrigan, Raptor/Pella, Scirocco, Donnager, Truman, Amun-Ra, Murphy, Nathan Hale, Munroe, Hephaestus, Dark Star, Behemoth, Gathering Storm and other fleet units. These are local gameplay derivatives with source and permission records in [ASSET-SOURCES.md](ASSET-SOURCES.md) and the linked update audits.
- B120 balance: +30% range on custom PDCs; ship railguns match their host PDC range; the orbital Foehammer has a 31,200 range and 60-second charge. Heavy rail tracking is reduced, standard Tachi uses 120 supply, and premium MCRN torpedoes travel 20% faster while retaining their 30-second fuel life. See [exact values and limits](docs/balance28_B120.md) and [increment A](docs/balance28_A.md).
- The Combined Fleet faction exposes the union of all three regular factions' ships, structures, equipment and research using the Martian start and economy. Four technology icons move to avoid overlap; research costs and effects do not change.

The 0.27.5 menu playtest and older releases are documented in [the historical update records](docs/). The current C4 candidate is offline-validated, not a claim of gameplay stability. Protomolecule plating is **not** included as a functioning shield item; the previous currency probe only established that an item could be equipped.

## Build and test

The build scripts expect a local copy of the licensed game, the pinned SDK and the preserved local source assets. Paths and dependencies are recorded in [environment.md](docs/environment.md). To recreate C4, first produce the frozen B120 directory/ZIP following the [0.28 release record](docs/balance28-release.md), then run `python3 tools/build_combined_b120.py` from the repository root. That script deliberately refuses to overwrite an existing candidate. Generated outputs appear in `build/experiments/` and are ignored by Git.

For playtesting, use one Expanse package at a time in the Sins II mods directory. Compare the regular B120 faction matchups before drawing conclusions about the combined sandbox. The [workstation test sheet](audit/balance28/independent/workstation-tests.md) separates observed results from checks still required in game.

## Sharing and licensing

Project-authored source code and documentation are [licensed under PolyForm Noncommercial 1.0.0](LICENSE), which permits personal noncommercial forks but does **not** make the project OSI open source. The playable ZIP contains supplied or adapted models, art and audio whose public redistribution terms are not all established. A noncommercial or fan-project disclaimer does not itself grant those rights. The local package is for the existing playtest; do not upload it as a public binary release yet. [Release readiness](docs/open-source-readiness.md) lists the remaining asset checks. The source-only snapshot excludes generated models, textures, audio, game binaries and rendered image audits.

The project is an unofficial fan work. *The Expanse* and Sins of a Solar Empire II belong to their respective owners. No affiliation or endorsement is claimed. Model-specific credits and documented licenses are in [ASSET-SOURCES.md](ASSET-SOURCES.md).
