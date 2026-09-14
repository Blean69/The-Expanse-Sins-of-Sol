# 0.27.3 Load Repair

Standalone cumulative replacement for regular 0.27.1. Enable alone; retain the old packages for rollback. This is the control package for testing stability without a new menu scene. The optional `expanse_update27_3_menu.zip` has identical match content plus the requested menu battle. Enable one package, never both.

The user reported another crash after spawning all new ships in one system. Log `sins2_log_496.txt` confirms regular 0.27.1 was enabled and still has load/runtime assertions. The earlier unit-tag overflow is absent from this log; that alone does not prove crash stability.

## Confirmed faults repaired

- Declare two action-source levels for 23 torpedo programs. Their existing base and researched values are preserved exactly; the +5% warhead research tier remains. Also correct the repair anchorage's two-level declaration and repeat its unchanged constants at both levels.
- Replace Behemoth's invalid `support_ship` AI role with the installed `attack_ship` role. Its logistics abilities, health, prices and weapons remain unchanged.
- Remove the unsupported construction-time field from the finite, paid Tycho recovery reward, following the installed finite ship-item pattern. Its price in Influence, equipment slot, inventory restriction and effect remain unchanged. Correct the fitting description accordingly.
- Increase Foehammer's placement clearance from 119.93 to 134.55 to contain its existing model bounds; no weapon range change.
- Add muzzle socket metadata to all eight affected gimbal meshes (Truman, Nathan Hale, Hephaestus, Scirocco, Donnager and Foehammer rails). Geometry, materials, acceleration structures and weapon definitions are preserved. The binary layout is verified against the prior official MeshBuilder A/B proof.

## Evidence and limits

Offline checks cover all action-source static-array lengths, unit roles, placement radii, unit-skin GUI objects, both turret types, pinned schemas/references, audio preservation and ZIP integrity. Existing railgun/PDC numbers, torpedo values, hull statistics, prices, research lists and civilian research are preserved.

**Crash closure is not established.** The last log also reports Scirocco with no GUI definition and an empty resource with a blank source. Its serialized skin contains the GUI and referenced assets; the log provides no stack or named missing resource that proves a specific fix. No game was launched for this repair, and the mass-spawn test, actual research transitions, save/reload and multiplayer are untested.

Test a fresh session with this control package first: allow loading without Skip All, then spawn the new hulls individually before repeating the combined-fleet test. A clean loading log will distinguish remaining runtime faults from failed definition loading. Existing crash-session saves may retain stale state; fresh-session evidence is needed before assessing save compatibility.

The optional menu package adds a separate visual test. Model polish is deferred at the user's request. No installation, enabled-mod change, game launch or publication was performed. Frozen 0.27.1 and the undelivered 0.27.2 menu preview remain unchanged; 0.27.2 lacks these new repairs and is superseded.
