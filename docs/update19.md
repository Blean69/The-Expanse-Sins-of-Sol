# 0.19.0 — fleet balance and extracted hulls

A separate candidate over frozen 0.18.0. The UNN, MCRN and OPA picker entries still share gameplay and the existing Civilian/Military research tree. The small **Sol — Three Homes** scenario is unchanged. This package is not installed or enabled automatically and has not been pushed or published remotely.

Use a fresh test game with **only expanse_update19 enabled**. Every multiplayer client must use the identical ZIP/hash. Extract its contents directly into a folder named `expanse_update19` under the game's local `sins2/mods` directory; `.mod_meta_data` must be immediately inside that folder. Restart after changing versions. Keep 0.17/0.18 folders and ZIPs for rollback; disable them when testing 0.19. Do not treat an old-version save as a supported migration test.

## Balance

- Martian-origin PDCs: **117.6 base DPS per mount**. Earth/Protogen PDCs: **85**. Existing research and temporary modifiers still apply.
- Scirocco: **5,400 hull / 3,100 armor** at level 1, matching Pella at every level. Light railgun damage **4,000 → 2,000**.
- Truman: **16,200 hull** at level 1, three times Pella's hull at every level; existing armor retained. **185 supply**. PDC release tolerance widened from 1° to the working Tachi's 7.5°; slow tracking, range and hull-safe mount arcs preserved.
- Amun-Ra: **70 supply**.
- Martian-origin ship metal prices **+30%**, including Rocinante/Pella and all capital-ship Tachi launch abilities. Earth prices, old ship speeds, build times and other resource prices are unchanged.
- All Expanse railguns: firing interval **×1.5**, acquisition hold **1 → 1.5 seconds**. Tracking and penetration unchanged. Intervals are now Rocinante/Amun-Ra 15s, Scirocco 22.5s, Donnager 30s, Truman 60s.
- All Expanse torpedoes: damage **×2**, speed **×1.7**, actual projectile fuel lifetime **30 seconds**. Magazine capacities, reload schedules, steering and interception HP/armor are unchanged. The missile platform also receives these changes through a private projectile, preserving vanilla Javelis definitions. A torpedo can expire before reaching a distant or evasive target.

## New hulls

**Europa's Bane** is available from the frigate roster in all shared identities: 95 supply, 1,500 credits / 350 metal / 200 crystal, 60s construction, 2,500 hull / 1,500 armor, speed 950. Six articulated Earth PDCs, two UNN light torpedoes every 10s from an eight-round magazine, 120s reload. It reuses the established 10% boarding ability against eligible capital/command/titan targets. The boarding pod remains cosmetic; it is not an interceptable unit. No railgun or cloak. Exact equipment counts and statistics are provisional gameplay choices.

**Artemis salvage tender** is an unarmed frigate-roster civilian: 8 supply, 600 credits / 100 metal / 50 crystal, 35s build, 900 hull / 400 armor, speed 800. It uses the installed game's native loot-collector capability and normal collection order. It does not colonize or capture operational ships. The complete Artemis exterior also replaces automatic TEC trade-ship visuals; native trade behavior, economics and Morrigan/Tachi escort options stay unchanged.

**Le Guin** is a replacement visual for the smallest native derelict. The source hull is already damaged, so it is not represented as an intact flyable hauler. Existing collection requirements/rewards remain native. Find it where a map generates that native derelict type; the Sol test scenario was not altered to force one to spawn.

The complete Artemis was used because the smaller export omits its engine assembly. Manitoba's complete mesh is a distant-view silhouette; detailed parts need verified assembly. Ceres assets are interiors and other station exports need assembly. Those are excluded from this candidate. Full Sol, Tycho, custom salvage progression, composite items and strategic weapon experiments remain excluded.

## Validation and tests still needed

Offline checks cover pinned references/schemas (unchanged newer installed extensions recorded separately), referenced meshes/materials/audio/icons, PDC/railgun arithmetic, torpedo action-value bindings and fuel duration, research tag coverage, faction parity, native trade/derelict preservation and ZIP hashes. Art workers checked compiled triangle winding, tangent frames, texture channels, UI sizes and sampled Europa firing clearance. These are **not gameplay passes**.

The user's working 0.17 report does not validate 0.19. Still untested: fresh load, existing/new ship research refresh, PDC acquisition, real 30-second expiry, boarding/repair interactions, native Artemis collection and Le Guin rewards, save/reload and multiplayer.

Suggested test: compare fresh/researched PDC and torpedo damage on existing and newly built hulls; fly a target away from a torpedo until 30s; test Europa against targets above/below and alongside its hull; collect the same native derelict with a native capital and Artemis; save/reload during magazine reload/collection; then repeat a short combat session with both clients on the identical archive. Record observed passes separately.

## Loading errors and Windows PDC sound

The supplied local logs were from 0.17. Duplicate built-in weapon tags overflowed the registry and dropped the custom cloak tag. Invalid zero-percent shield-burst objects were also reported. This candidate keeps only the custom additive weapon tag and omits disabled optional shield-burst objects, preserving the shieldless baseline. Other old installed-mod metadata, map-generation and performance warnings were not converted into unsupported gameplay changes. A fresh load is needed to confirm the error prompts are resolved.

The PDC audio remains byte-identical to the working package: four mono 48kHz Ogg/Vorbis clips and their sound profiles, using the same format as native effects. No decoder error appeared in the available Proton logs. **Resolved by user report:** the Windows tester can hear the PDC sound; no compatibility fix was needed. This confirms the earlier audio report was not a reproducible silence bug. This candidate's160 existing audio/profile files are unchanged;0.19 itself still awaits the gameplay checks above.
