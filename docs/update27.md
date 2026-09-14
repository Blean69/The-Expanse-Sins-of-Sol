# 0.27 Fleet Expansion — local candidate

Standalone cumulative candidate over frozen **0.26 Fleet Polish**. Use the regular package for faction play; **Sandbox deliberately grants the combined roster**. Enable one variant in a fresh game. Old saves can retain ships and research from their original variant.

The user's reported Composite purchase/equip test ran the 0.26 combined-roster laboratory. Its broad UNN roster was intentional laboratory setup, not the normal faction rules. That test confirms receiving and equipping the inert currency-test item; it does not yet establish save/reload, rejection at zero currency or functioning shield plating. The existing laboratory and rollback remain separate.

## Fleet additions

| Hull | Owner / production | Level-one hull / armor | Supply | Weapons |
|---|---|---:|---:|---|
| Nathan Hale, Leonidas-class | UNN capital | 10,000 / 3,800 |155|12 PDCs, two slow medium rail turrets, four light torpedoes per salvo |
| Munroe | UNN cruiser |5,200 /2,400|125|8 PDCs, fixed keel rail, six light torpedoes per salvo |
| Hephaestus | MCRN cruiser / destroyer role |4,000 /2,300|180|10 PDCs, one light turreted rail, five light and three medium tubes |
| Dark Star | OPA capital |3,600 /1,800|140|3 PDCs, Amun-Ra rail and existing stealth/boarding program |
| Laconian procurement frigate | OPA frigate factory |1,500 /800|130|6 PDCs, two light torpedo tubes |

These are initial mod balance values. UNN defensive batteries and Dark Star retain 85 DPS per PDC; the two new Martian/Laconian hulls use 117.6. New UNN rails fire every 60 seconds (Hale 2400 damage per turret; Munroe 1800 fixed keel). Hephaestus uses the weakened Scirocco light rail: 2000 damage every 22.5 seconds. Its medium torpedoes reuse the Martian heavy projectile with a private 3000-damage payload, three per 20 seconds and 12 rounds. Other existing rail, PDC and torpedo balance is preserved.

New hulls require paid faction-specific military research with native tier costs and research times. Ship construction remains separately paid; capitals use the ordinary capital factory and native first-capital entitlement. Civilian research, existing economic multipliers and baseline movement remain unchanged.

## Model work

Nathan Hale uses steel and UNN blue, aligned working rail/PDC assemblies and five actual textured Truman bell/throat assemblies. Munroe retains its detailed four-engine source hull and receives blue UNN markings; the three-engine reference was clarified as likely Laconian. Static sculpted gun tops are replaced by movable mounts rather than retained beneath duplicate turrets.

Hephaestus replaces the four printed engine caps with actual Tachi drive assemblies, retaining eight bow tubes and ten PDC positions in Scirocco-style colors. The small source hangar/marine complement is a visual/lore feature, without added free fighters or a second capture system. The supplied unnamed Laconian frigate gets thermal-panel detail, an exposed Tachi drive and six movable PDCs in requested Martian colors.

Dark Star receives charcoal/graphite surfaces, aligned working Amun-derived guns, an actual textured Tachi drive interior and a capital progression framework. It is a fan-design salvage adaptation. Behemoth's bookmark blade is removed, the resulting seam is closed, and the full cylindrical ship receives white panel surfaces and eight open drive bells with actual textured Tachi interiors. Existing logistics, hospital/refit abilities, health, price and movement remain intact; its titan limit remains shared.

Gathering Storm is 15% larger, smoother and gray metallic toward the supplied reference. A short connected collar closes the floating drive gap while exposing the detailed donor engine. The complete turret assemblies and torpedo launch origins scale with the hull. **Procurement moves to OPA**, gated behind the Behemoth refit route, with existing high-tier research price, ship costs and one-per-player limit. This is a gameplay acquisition adaptation, not a claim that the canonical vessel belonged to OPA.

## Error repairs

The tested laboratory exactly matched all 1,894 files in the frozen 0.26 probe. Its log identifies three concrete repairs included here:

- Required additive scenario arrays are present, fixing missing DLC scenario fields.
- Fixed-axis rail mounts receive a small positive firing arc instead of an invalid zero-width arc. Weapon damage, cadence and tracking speed stay unchanged.
- The passive shieldless ability has a valid HUD icon and description, fixing its missing-GUI assertions. The OPA command's existing Colonize control is placed first on its ordinary ability bar.

One intermittent `inplace_vector` index assertion lacks an attributable entity or call stack and remains unresolved. Warnings from older installed prototype metadata and old replay metadata are outside this candidate. A clean log after testing 0.27 is needed to distinguish remaining errors. No installed folders or saves were modified.

## Validation and limits

Surface treatment follows the supplied renders and the [Scirocco artist’s thermal-panel references](https://paulwk13.artstation.com/projects/Qn3oN8). The ship designers also describe heat-resistant tiles and conventional drive cones in their [North Front interview](https://magazine.artstation.com/2016/02/scenes-concept-art-expanse/).

Offline checks cover schema/reference integrity, actual factory routes, faction research prerequisites, civilian preservation, magazine salvo/fuel values, positive fixed-axis arcs, compiled model previews, sampled muzzle clearance, original audio and rollback hashes. These are not observed in-game combat results. New ship performance, moving turret interpolation, game lighting, save/reload and multiplayer require playtesting.

For the next short test, use the regular candidate and inspect each faction's ship list, research and ordinary production. Check all new guns against ships and torpedoes, inspect engine seams/plumes, then save/reload mid-magazine. The combined Sandbox exists for faster model comparisons only.

Source STL/glTF/ZIP files are not bundled. Paid-source derivatives remain local; no publishing or redistribution has been performed. No installation, game launch, remote push or purchase was performed. 0.26 and its separate Composite probe remain available as rollback/test artifacts.
