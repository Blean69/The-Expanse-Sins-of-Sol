# 0.26 Fleet Polish — local playtest candidate

Standalone cumulative replacement for0.25, which remains frozen as rollback. Use one variant in a fresh game: normal0.26 enforces faction rosters;0.26 Sandbox grants the combined Expanse roster. Do not enable both. Existing saves may retain old fitted colony items, researched legacy bonuses, or ships; fresh games are the meaningful test of this cleanup.

## Fleet and models

- OPA Expeditionary Command Ship now matches Scirocco length (456.52 game units), retains its full hull detail, and has5,000 hull /3,000 armor at level1. Price4,800 credits /975 metal /600 crystal. Its100-second construction,150 supply, movement and weapon performance are unchanged. Regular Europa's Bane is unchanged.
- **Colonize is directly on the command ship's ability bar**. It reuses the shipped native colony program:120 antimatter,120-second cooldown,5,000 range. No purchased item required. Scirocco and Truman retain their existing paid colony modules.
- Gathering Storm has hard surface normals, coherent blue/pink/pearl facets and a fitted drive assembly. Its length, keel railgun and six PDC mounting/firing parameters are unchanged. Its crystal-knife appearance follows the [wiki's cited novel description](https://expanse.fandom.com/wiki/Gathering_Storm); the reused engine is a mod interpretation.
- Foehammer now has a structural orbital base rather than a rectangular block; the gun/PDC poses and performance are preserved. Murphy has revised steel/navy material response without replacing its working hull, drive or turret rigs.

## Research and production

Military research uses compact rows, corrected tier columns, concrete custom icons for new procurement nodes and explicit display labels. Obsolete TEC warships are removed from player factories, and unused military branches and native Titan-specific equipment are removed from availability. Native starbases and useful infrastructure/equipment remain supported. Old definitions stay on disk for native NPCs and reference compatibility.

Retained technologies keep their mechanical values, prices, research times and prerequisite groups. Civilian research definitions, domain configuration and list ordering are unchanged. Garrison and obsolete heavy trade-escort entries now use available faction hulls so removed TEC production cannot leak through those paths. Native garrison supply and escort rules remain intact.

## Paid NPC services

Use **Sol — Three Homes / Contacts** for guaranteed **Tycho Engineering Bureau** at Tycho Roadstead and **Ceres Shipping Exchange** at Ceres Freeport. Find them through the normal Influence/NPC interface; scout/reveal them as usual. The original Three Homes map remains available. On generated maps these contacts replace the Pranast and Jiskun slots only when those NPCs are present; other minor factions remain unchanged.

- Tycho:4 Influence for one finite recovery component, six-minute service cooldown. Fitting occupies a normal slot and provides+15% native capture points. No boarding probability bonus or exclusive salvage system.
- Ceres:2 Influence for300 metal, four-minute cooldown; or4 Influence for360 seconds of native scout intelligence, ten-minute cooldown and reputation level1. Scout coverage/detection follows the native engine program.

Native NPC portraits, defense fleets and ordinary markets/auctions remain placeholders. These contacts grant no containment sample or plating unlock.

## Plating status and testing

**Adaptive/protomolecule plating is not included.** The native Titan armor item was never that feature. Full ProtoTech study/production and item-bound shield behavior still need runtime acceptance tests. A separately labeled0.26 Composite currency-test package provides the first concrete receive/save/spend/reject test; it is not a gameplay plating unlock and should not be used for fleet balance sessions.

Observed evidence: the user's screenshots show0.25 layout/art/control problems. New evidence: offline schema/reference checks, acquisition/prerequisite checks, model previews and geometric firing-envelope checks. Game loading, engine specular rendering, actual colonization, paid NPC purchases, research effects on existing/new ships, save/reload and multiplayer are **not run by the agent**.

For a short test, inspect the military tabs and new hulls, colonize from a fresh OPA command, buy each NPC service, then compare research on an existing and newly built ship. Save/reload with a colony order or NPC intelligence active. Please report the package variant and any exact loading error.

PDC audio, existing railguns/magazines/projectile mechanics, ordinary ship costs/times/movement outside the requested command price, and the shieldless baseline are preserved. No installation, game launch or remote push was performed.
