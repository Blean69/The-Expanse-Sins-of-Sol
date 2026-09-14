# 0.27.5 Finished Fleet Menu

Standalone cumulative menu build over **0.27.4 Hephaestus Repair**. Enable this package alone and restart the game. Keep 0.27.4 for rollback. The user reported no crash in that hotfix test, but Pella still produced its GUI/empty-resource prompt; this is not a comprehensive stability pass.

## Backdrop fleet

- MCRN line: Donnager, Scirocco, Hephaestus and Raptor; one Tachi and one Morrigan patrol the foreground.
- Opposing showcase: Truman, Munroe, Gathering Storm and Amun-Ra; two additional Amun-Ra ships patrol the foreground. Gathering Storm's presence here does not change its regular OPA ownership. Stealth hulls remain visible for the display.

Only these existing detailed hulls are used. Twelve display ships retain the original scene camera, formation positions, opposing sides, patrol routes and 15-second wiped-side respawn. The native no-damage scene setting remains: weapons/effects can run continuously without replacing casualties. This is a visual backdrop, not a balance test.

The private copies have **no construction research prerequisites**. Their private torpedo-magazine abilities run at fixed level zero with no research prerequisites, retaining existing base ammunition/damage/timing values. This prevents the previous menu's unknown rebel-titan prerequisite and avoids querying unrelated technologies on randomly selected backdrop factions. Hephaestus inherits its corrected native `heavy` target type. No cloaking, capture, boarding, ship-launch or equipment hooks operate in this scene.

All existing match definitions, faction access, research, geometry, textures, audio and balance are byte-preserved from 0.27.4. No new unit tags or player acquisition entries are added. The menu copies cannot be manufactured in normal matches.

## Plating status

**Protomolecule plating is not included.** The previously equipped Composite test item only proved a receive/spend/equip route; it has no shield effect. The global shieldless buff disables absorption, restoration and passive regeneration, and those permissions have no native enabling override. A real plating item needs a tested item-bound exception and removal behavior, plus the requested study/production gates. Adding shield capacity alone would not implement it. Existing gameplay remains shieldless.

## Validation

Offline passes: real Lua 5.4 compilation/execution with mocked engine APIs; exact twelve-ship roster including mixed MCRN escorts; both same-race background players still receive distinct sides; foreground movement; delayed respawn of only the wiped side; no native titan equipment injection; scene copies usable with an empty research registry; corrected target types and turret sockets; all original match files unchanged; schema/reference checks and ZIP integrity.

**Not observed:** game-engine menu startup, model framing, firing effects, performance and long-running stability. The earlier menu failed its user test; offline Lua checks did not catch its faction research queries. This version directly removes those dependencies, but still needs the requested user confirmation. Pella's regular-game GUI prompt is not fixed by this visual update and Pella is not in the scene.

No installation, enabled-mod edit, game launch, save modification or publication performed.
