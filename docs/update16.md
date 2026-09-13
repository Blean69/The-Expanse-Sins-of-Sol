# 0.16 battleship balance patch

Complete package: `build/experiments/expanse_update16.zip`. Load **alone**, as **TEC Enclave**. No install, enable or game launch was performed. Source is based on `4f46771`; original 0.15 and earlier packages remain intact.

| Change | 0.15 | 0.16 |
|---|---:|---:|
| Truman PDC range, all 18 mounts | 4,500 | 6,000 |
| Donnager PDC range, all 16 mounts | 6,000 | 8,000 |
| Truman railgun cooldown, both guns | 20 seconds | 40 seconds |
| Donnager light torpedoes per volley | 2 | 12 |
| Donnager light magazine capacity | 8 | 48 |
| Scirocco PDC support radius | 6.6 | 3.0 at gun / 4.0 at hull |

Truman rail damage and penetration are unchanged. Railgun Thermal Management gives a 38-second cooldown instead of 19 seconds, retaining the same 5% research modifier. PDC damage, tracking speeds, firing arcs, aiming tolerances, target filters and interception behavior are unchanged. The user's later test confirmed Truman PDCs do target ships, so this patch does not replace that behavior.

Donnager launches twelve **actual** light torpedo entities per volley. It retains four volleys at ten-second intervals, then reloads 120 seconds after the final volley. With continuous eligible targets and no overcharge, launches occur at 0, 10, 20, 30, then 150 seconds. The original reactor clock acceleration remains. Per-torpedo damage, speed and durability remain unchanged; both warhead research levels use the new counts. Heavy torpedoes are unchanged.

Older saved magazines may contain 2/4/6/8 rounds, below the new firing threshold. A bounded guard empties that undersized partial magazine and starts a normal 120-second reload, avoiding both a permanent stall and an immediate free refill. Empty magazines already reloading retain their existing timer. This is checked in a restricted offline interpreter; actual engine save migration remains untested.

The Scirocco circles were oversized black cylindrical footings, not an effect or shield. The twelve footings are now narrower tapered supports using the existing hull finish. Gun attachment planes and all native mesh metadata are unchanged. Bottom ends extend slightly farther into the hull where measured contact requires it. Eight hull contacts per support pass. Hull panels, gun meshes, pivots, launch origins and all unit definitions remain unchanged. The geometry preview in `audit/update16/mount-comparison.png` is a cropped render of actual compiled geometry and diffuse textures, not an in-game screenshot; its cutaway edges are preview cropping.

## Identity and rollback

- Version: **0.16.0**, 1,024 files.
- ZIP SHA-256: `2fe3936f4a544055190227b02d990c25dae7ad9a30297db131c7a69c24355905`.
- Tree SHA-256: `1bb86afd5ebfe89dcc40d5d025324397bf8d0db6dfc3bdf495b0936567e54779`.
- Rollback 0.15 ZIP SHA-256: `6dd94b534eacdd5c9a1a9752f9a2ab4a069cf65ad3dc495cbd88e36aee7d1b7a`.

`audit/update16/checkpoint.json` records the preserved packages, trees, original inputs and initial enabled settings. Installed game and pinned SDK are unchanged. User-provided runtime observations are recorded separately in `runtime-feedback.json`.

## Verification

**Observed offline passes:** 38 pinned schema checks, 1,121 resolved references, exact 42-file change allowlist, valid compiled normals/tangents, unchanged native mesh metadata, twelve supported pedestals, actual twelve-object launch graph, and eight before/after magazine scheduling scenarios covering both research levels, target gaps, weapon permission and reactor state. Four partial-magazine migration cases pass. All existing unit files, unrelated weapons, research, audio and texture files remain byte-identical.

**Runtime NOT RUN for this patch:** new mount appearance, effective range and target acquisition, interception performance, rail cadence under modifiers, larger volleys and battle performance, actual old-save migration, research transitions, save/reload and multiplayer. The unchanged 0.15 support/research runtime checklist still applies.

Focused playtest:

1. Spawn a fresh Donnager and Truman; confirm PDC reach and ship/torpedo targeting on exposed sides while preserving hull-limited arcs.
2. Verify Truman's two railguns each use a 40-second base cooldown; 38 seconds after Thermal Management.
3. Count Donnager's twelve light torpedoes per volley, four volleys and subsequent reload. Repeat under reactor overcharge and after Warhead research.
4. Load an older Donnager with a partial magazine: it should enter reload, then resume twelve-round volleys without getting stuck or immediately refilling. Test an already-empty/reloading magazine too.
5. Inspect all twelve Scirocco supports from both sides; no large dark disks, floating guns or altered pivots.
6. Save/reload and repeat on two clients with the same ZIP/hash before calling the patch multiplayer-validated.

Possible later additions: clearer magazine/reload countdowns and a distinctive UNN damage-control ability. Neither is included in this focused patch. New crew audio can be integrated separately when supplied.
