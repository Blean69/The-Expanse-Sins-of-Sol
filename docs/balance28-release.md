# Balance 0.28 delivery

**A was delivered before B. All candidates are cumulative, standalone packages containing the working Expanse menu. Nothing was installed, enabled, published or pushed; no game was launched.**

Use A for the first construction/classification check, then B120 as the main combat test. The other packages isolate individual factors. C is an optional comparison, not an adopted balance recommendation.

| Package | Purpose | SHA-256 |
|---|---|---|
| [A](</run/media/haker/NVME 2/expanse-mod/build/experiments/expanse_balance28_A.zip>) | Truman command economics/cap, hierarchy, UNN support, orbital access, scout charge | `e455bad555ce081ef1248f5288ca0d3c37809e73033093c595898d5d82b900f7` |
| [B120](</run/media/haker/NVME 2/expanse-mod/build/experiments/expanse_balance28_B120.zip>) | A + ranges, heavy tracking,120-supply Tachi and premium torpedoes | `42b1cf0b31c56f1c48f2a0d89dc69181cb2545b97b4fbf4847ee22cbf0ad73c2` |
| [B95](</run/media/haker/NVME 2/expanse-mod/build/experiments/expanse_balance28_B95.zip>) | Same as B120;95-supply Tachi and matching launch checks | `24a4637cbc504e3f7b82672bac847cc9733c055c5c17e0456cfe9a7cfc9cbf5b` |
| [B-tracking-control](</run/media/haker/NVME 2/expanse-mod/build/experiments/expanse_balance28_B-tracking-control.zip>) | Same as B120;original heavy tracking | `e4f9b914b61e17c2686c05133e9532a677faa0fe3fcf8921c9ff4912c397488f` |
| [C-cadence](</run/media/haker/NVME 2/expanse-mod/build/experiments/expanse_balance28_C-cadence.zip>) | Same as B120;Donnager rail reload30→24s only | `16a53d9cb93ba7db4f1e5995a458730e255b65279b60ff7d1d7ad0dab76bd510` |

Rollback: [tested 0.27.5 menu](</run/media/haker/NVME 2/expanse-mod/build/experiments/expanse_update27_5_menu.zip>), SHA-256 `98ca0c15b7ff6e9eaa09b0a5d96774da039bc39d39d6496ba6a2536bea8ccfbc`. It and the older 0.27.4 rollback remain unchanged. The installed tested package matched all 2,285 baseline files. Source base: `8e55e93550b938e0dc62508a9ee8c6ac350332d4`; each stage records exact implementation-file hashes in its `source.json`. Pinned schema commit: `8e061033afe53b1393eaefd56617a3fd041eeb5f`; game 2.0.3 (318), Steam build 25127248.

## Exact changes and access

[Increment A tables and limitations](</run/media/haker/NVME 2/expanse-mod/docs/balance28_A.md>) · [B120 tables and scope](</run/media/haker/NVME 2/expanse-mod/docs/balance28_B120.md>) · [Full baseline/mechanism audit](</run/media/haker/NVME 2/expanse-mod/audit/balance28/independent/README.md>) · [Production modifiers](</run/media/haker/NVME 2/expanse-mod/audit/balance28/production-modifier-audit.json>). Each stage acceptance.json contains every changed numerical path; the original definitions remain in frozen-definitions.json.

Truman rises 185→400 supply, 4,000/1,000/700→7,680/3,016/1,520 resources, 100→240 s construction. It uses tier-three native command research/titan factory and native command cap 2, with existing boarding launch/resolution exclusions. Base and ordinary non-discounted command resource bills are the same; reachable UNN lightweight construction discounts exclude this build kind. Actual billing/cap reservations and external transfers remain untested.

Raptor becomes an unlevelled cruiser with its former level-one stats and fixed abilities; Hephaestus becomes a capital with four slots and +3% hull/armor per level. Existing cruiser build-time modifiers consequently apply to Raptor and cease applying to Hephaestus. Base economics remain unchanged. Nathan receives the disclosed existing colony/repair support refit. All six faction/player aliases receive reachable equivalent-tier battery research with one shared two-per-well cap; no separate faction buckets.

B adds 30% PDC range (3500→4550,4500→5850,6000→7800,8000→10400). Ship rails match host PDC range; orbital Foehammer reaches 31,200 with actual charge 60 s and separate retained reload 30 s. Heavy yaw becomes 9°/s on Donnager/orbital and 12°/s on Truman/Nathan. Existing tolerances and 1.5 s acquisition remain; continuous-lock semantics were not established. No damage, penetration or PDC count increases.

Tachi 95→120 supply, linear ramp 5→4 s, angular speed 25→28.75°/s; max speed 1,250 unchanged. Premium MCRN torpedoes 2,125→2,550 (light) and 1,275→1,530 (heavy), same 30 s fuel and damage. Private Morrigan preserves foreign shared equipment; captured hardware and Pella-launched standard Tachis deliberately retain Martian ammunition.

## Observed versus untested

- Observed user evidence: latest 27.5 menu was used for the two-player UNN/MCRN test; these candidates have no observed gameplay passes.
- Offline passes: pinned schemas/references/actions/registries, archive integrity, preserved art/audio/menu, deterministic multipliers; independent merged A/B review passed 576 static checks. Packaged controls differ only in the intended five supply files, seven tracking files or two cadence files.
- Not run: game loading, turret hit timing/multi-muzzle damage events, continuous-lock semantics, cap queue/cancel/death/transfer behavior, before/after research on existing/new hulls, save/reload and multiplayer. Two inherited start-mode files have no matching SDK schema; their exact MCRN-only pointer changes and references were checked separately.
- Known confounders: Targeting Array self +75% tracking / +25% range (separate allied aura +50% / +15%); Rapid Autoloader and reactor cooldown effects; matched levels and equipment are essential. Existing researched Razorback disruption immunity remains, so inhibitor tests must distinguish research state.

[Runtime test sheet](</run/media/haker/NVME 2/expanse-mod/audit/balance28/independent/workstation-tests.md>). Start with A: UNN colony/Nathan support, paid Truman construction and third-queue rejection; verify Hephaestus/Raptor classification and battery access. Then compare B120 with the two controls. Swap the two players’ factions before making matchup claims. Fresh games; same-candidate save/reload only.
