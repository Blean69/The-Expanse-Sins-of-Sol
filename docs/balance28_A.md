# The Expanse 0.28 — A

First standalone checkpoint over the tested 0.27.5 menu build. Weapon ranges, heavy tracking, Tachi premium changes and faster torpedoes follow in B; they are deliberately absent from A.

| Change | Before | A |
|---|---|---|
| Truman engine class | Capital | Command / supercapital |
| Truman supply | 185 | 400 |
| Truman credits / metal / crystal | 4,000 / 1,000 / 700 | 7,680 / 3,016 / 1,520 |
| Truman construction | 100 s | 240 s |
| Truman exotics | 1 offense + 2 defense | Unchanged |
| Truman native production cap | No Truman-specific cap | Shared command tag limit 2 on both UNN identities |
| Raptor | Capital, experience + 4 equipment slots | Cruiser, fixed former level-one stats/abilities, no capital equipment or progression |
| Hephaestus | Cruiser, 4,000 hull / 2,300 armor | Ordinary capital; same level one, 4 equipment slots, +3% hull/armor per level; level ten 5,080 / 2,921 |
| Razorback charge / variance | 2 / 0 s | 0.1 / 0 s |
| Orbital battery access | UNN | UNN, MCRN and OPA |

Truman uses the existing titan shipyard and a military tier-three command procurement unlock: 1,700 credits / 300 metal / 500 crystal, 360 seconds, requiring titan-factory research. Its command build kind excludes the ordinary first-capital category; actual in-game billing still needs checking. Health, weapons, reload and level scaling remain unchanged. Its existing four equipment slots stay four. Native command production limits and explicit existing-boarding launch/resolution exclusions are configured; simultaneous queues, cancellation, death/rebuild and diplomatic transfers are NOT runtime-verified. This is not a proven absolute ownership cap across arbitrary external reward scripts. No old-save ships are deleted.

Raptor retains all fixed-level reactor, magazine, launch and boarding abilities, with 225 antimatter and 0.75/s regeneration folded into its base before removing capital experience. Hephaestus keeps its 180 supply, 6,000 / 1,950 / 1,000 ordinary prices, existing exotics, 150-second construction, level-one combat stats and weapon damage. Its conservative progression adds no weapon modifier.

UNN keeps its ordinary 450-credit / 100-metal / 50-crystal colony frigate. Existing tier-two Nathan Hale gains native colony-frigate colonization and the existing bounded, nonstacking Combat Engineering Teams repair. Its combat stats, price and acquisition remain unchanged. This disclosed support refit preserves expansion without an inexpensive Truman copy.

All three factions have equivalent tier-two orbital battery research through their own visible nodes. Each uses the same battery definition and one shared two-per-owned-gravity-well tag bucket. Its 2,000 / 500 / 350 cost, 120-second construction, four military slots, 4,000 hull / 3,000 armor and weapons remain unchanged in A. Queuing, ownership transfer and cancellation still require runtime checks.

Razorback is the existing `trader_scout_corvette` (formerly Sunflare). Only its base charge timer changes; transit, alignment, high-G burn costs/cooldown and fleet synchronization remain unchanged. This is not a guaranteed 0.1-second total escape. The existing research-gated Unstoppable Phase Jump already grants disruption immunity and is preserved; inhibitor tests must distinguish researched and unresearched scouts.

Smallest next test: in a fresh UNN game, confirm colony access and Nathan colony/repair buttons, research/build Truman at the titan shipyard, queue a third across multiple factories, cancel one and retry. As Mars, verify capital Hephaestus and cruiser Raptor. Check the visible orbital unlock on all three factions and a solo Razorback jump. Then proceed to B comparisons.


## Evidence and limits

Baseline: user-confirmed 0.27.5 Finished Fleet Menu, source `8e55e93550b938e0dc62508a9ee8c6ac350332d4`, ZIP SHA-256 `98ca0c15b7ff6e9eaa09b0a5d96774da039bc39d39d6496ba6a2536bea8ccfbc`. Installed baseline matched all 2,285 files. Rollback retained unchanged.

This candidate has **offline validation only**. Game loading, cap/queue/capture behavior, weapon geometry, damage timing, save/reload, existing/new research effects and multiplayer comparisons are **NOT RUN**. Fresh games are the supported test. No install, enable, publish, push or game launch was performed.

Models, audio, menu scene, civilian economy and unrelated faction features are preserved. No generic shields or protomolecule plating added by this targeted increment.
