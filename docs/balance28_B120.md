# The Expanse 0.28 — B120

Cumulative over Increment A, retaining Truman command economics/access, hierarchy, universal battery access, Nathan support and Razorback charge. Main candidate is **B120**; B95 and B-tracking-control change only the factor named in their headings.

| Change | Frozen 0.27.5 | B120 |
|---|---:|---:|
| Standard Tachi supply | 95 | 120 (four = 480) |
| Tachi time to maximum speed | 5 s | 4 s |
| Tachi maximum linear speed | 1,250 | 1,250 |
| Tachi maximum angular speed | 25°/s | 28.75°/s |
| Tachi angular ramp | 1.25 s | 1.25 s |
| MCRN light torpedo speed | 2,125 | 2,550 |
| MCRN heavy torpedo speed | 1,275 | 1,530 |
| Donnager/orbital heavy yaw | 15°/s | 9°/s |
| Truman/Nathan Hale heavy yaw | 20°/s | 12°/s |
| Donnager heavy reload | 30 s | 30 s |
| Truman heavy reload | 60 s | 60 s |
| Orbital Foehammer charge | 0 s | 60 s |
| Orbital Foehammer reload | 30 s | 30 s |

All 146 custom PDC weapon definitions gain exactly 30% range: 3,500→4,550; 4,500→5,850; 6,000→7,800; 8,000→10,400. Ship railguns match their host's updated PDC range, including compact/fixed guns. Orbital Foehammer alone uses 3× the ship Foehammer range: **12,000→31,200**. Damage, penetration, muzzles and PDC tracking remain unchanged. Orbital charge and reload are separate native fields; their combined cycle and target-loss behavior are not inferred from arithmetic.

Heavy tracking affects Donnager, Truman, Nathan Hale and the orbital gun. Existing 0.5°/1° tolerances stay unchanged. Acquisition stays 1.5 s because continuous-lock/reset semantics were not verified. Compact Scirocco/Hephaestus rails and fixed rail host turning stay unchanged. No evasion, target blacklist or guaranteed miss mechanic is added.

Private premium torpedoes equip standard Tachi, MCRN Morrigan, Raptor, Scirocco, Donnager and Hephaestus. Damage, armor/HP, magazines, reload, steering and **30-second fuel life** stay unchanged. Same lifetime with greater speed raises the maximum-speed travel-distance ceiling by 20%. Foreign/shared projectiles and planetary ordnance remain unchanged. The MCRN Morrigan is a definition derivative using exactly the existing hull/art/stats; MCRN production, starts, escorts and garrisons use it. OPA Pella's **own** ordnance stays unchanged, but the standard Martian Tachis it launches retain the premium Martian hardware and candidate supply. Captured fitted hardware also retains its loadout.

No higher Tachi hull, weapon damage, additional PDCs or railgun is granted. Launch reserve checks follow the selected 95/120 supply variant; existing launch capacity/cost/cooldown is preserved.

Control comparisons must record loadout and research. Targeting Array supplies +75% self tracking/+25% range, or a separate +50% tracking/+15% range allied aura; Rapid Autoloader supplies temporary cooldown reductions. Those existing counter-builds are retained. Two native start-mode files have exact MCRN-only reference substitutions; a matching SDK schema is unavailable, so their schema checks are NOT RUN, although JSON and reference checks apply.

Smallest next test: compare A and B120 in a fresh game; inspect Tachi supply/speed, time one heavy shot against stationary and laterally moving targets, time orbital charge with target held/lost, then verify a Martian torpedo expires after 30 seconds. Use B95 to isolate fleet-number pressure and B-tracking-control to isolate heavy tracking. Compare Donnager cadence only after these checks. Save/reload and both-player faction swap remain required before strong balance conclusions.


## Evidence and limits

Baseline: user-confirmed 0.27.5 Finished Fleet Menu, source `8e55e93550b938e0dc62508a9ee8c6ac350332d4`, ZIP SHA-256 `98ca0c15b7ff6e9eaa09b0a5d96774da039bc39d39d6496ba6a2536bea8ccfbc`. Installed baseline matched all 2,285 files. Rollback retained unchanged.

This candidate has **offline validation only**. Game loading, cap/queue/capture behavior, weapon geometry, damage timing, save/reload, existing/new research effects and multiplayer comparisons are **NOT RUN**. Fresh games are the supported test. No install, enable, publish, push or game launch was performed.

Models, audio, menu scene, civilian economy and unrelated faction features are preserved. No generic shields or protomolecule plating added by this targeted increment.
