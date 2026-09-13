# Update11 behavior handoff — worker A

Owned source: `tools/update11_behavior.py`, `tools/update11_behavior_validate.py`, `tools/update11_behavior_shield_audit.py`. Reviewed generated files: `build/update11-a/reviewed`. Main retains unit, skin, player, uniform, manifest, localization and package integration ownership. Original game, SDK and accepted PDC-audio package were read only.

The first `build/update11-a/candidate` run stopped at a source-evidence assertion (`unit_type` is not an installed unit field). The assertion was corrected to the actual `tags` classification and generation ran to a fresh `reviewed` directory. The incomplete directory is preserved and must not be packaged.

## Corrected components

- Corvette deployment: the current runtime log records `unit_spawner ASSERT(false)` immediately after `use_ability`. Stock TEC reinforcement abilities use hyperspace arrival. The revised ability uses that path, two-second arrival, one explicitly required private `expanse_mcrn_corvette`, owner attribution and available-supply clamping. Main's new supply allocation is55; active gate and spawning budget both use55. Resource price stays300credits/55metal and cooldown20seconds. This is engine-placed reinforcement arrival; it does not animate an actual hangar. The precise engine assertion cause cannot be proven without source/runtime debugging, and successful repair is not yet observed.
- Icon: actual MCRN model brushes `mcrn_corvette_hud_icon` and `mcrn_corvette_tooltip_picture` replace the Cobalt ability icon. The tooltip's unit reference follows the private MCRN unit.
- Boarding: Amun and Donnager target filters now include installed `capital_ship`, `super_capital_ship` (command ships), and `titan`. Enemy/detected/built/same-well conditions, Rocinante exclusion, initial supply requirement, delayed supply recheck, three-second timed visual and one random roll remain. Amun10%/180seconds and Donnager40%/600seconds are unchanged.
- Morrigan: private `expanse11_morrigan_magazine` uses one create-torpedo operation per event, four total rounds, one every10seconds and120seconds after empty. The ability's sequential position picker alternates the two tube frames supplied by main. Damage750, penetration1000, velocity1250 and the accepted50hull/100armor/50strength projectile are unchanged. No existing magazine is edited.

## Additional concrete engine diagnostics

The same runtime log reports Amun's `torpedo_strikecraft` group in both attack and ignored groups. Main should remove that sole ignored group. It also reports the cloak revealing tag missing from uniforms: the current package lacks `uniforms/weapon.uniforms`. Main must preserve the installed19 weapon-tag records and threshold, and append the exact private tag/localization supplied in the integration contract. Existing cloak weapon/buff definitions already reference it.

These findings are recorded as actual log diagnostics. They are not inferred from the user's successful cloak report, and the successful report does not negate the diagnostics.

## Offline checks actually run

`python3 tools/update11_behavior.py --output build/update11-a/reviewed` verified all62 pinned schema files, then passed both Draft7 and strict Draft202012 validation for7 candidate entities and strict validation of the proposed full weapon-uniform structure. It checked projectile counts, cadence values, original capture odds/cooldowns, preserved restrictions/supply checks and byte-identical accepted base files.

`python3 tools/update11_behavior_validate.py` resolved38 concrete reference edges against the proposed candidate, accepted package and installed game. It separately reports three unresolved integration requirements: the main-owned private MCRN unit with55supply, actual Morrigan tube frames, and the Morrigan skin's existing light-torpedo muzzle binding. It does not substitute the Cobalt under the missing private unit ID or call the complete package valid.

`python3 tools/update11_behavior_shield_audit.py` inspected17 installed TEC/DLC2 TEC files containing shield modifiers or repair operators. Its JSON report distinguishes shield-only purchases from mixed upgrades and planet shielding; it does not modify them.

No installation, game launch, schema/dependency update, commit or push was performed by this worker.

## Required runtime evidence

Test launch with normal and insufficient resources, exactly55 supply free, less than55 free, and two concurrent casts. Confirm exactly one correctly owned MCRN corvette appears after two seconds with the proper icon and that the previous spawner assertion is gone. Engine payment/refund behavior on a rejected delayed arrival is not established offline.

Test boarding each supported class, detection and supply rejection, one delayed attempt and a recorded probability sample. **Captured titans may exceed the construction titan limit.** The native `change_owner_player` operation has no cap option, and pinned action-value/constraint definitions expose no global player tag-count query. Existing construction limits remain; their application to capture is unresolved. Test while owning and while building a titan. No invented count constraint or silent titan exclusion is supplied.

Test Morrigan tube alternation, shots at0/10/20/30 seconds under a continuously eligible target, then a new magazine after the empty reload. Check target loss, interrupted eligibility and save/reload. The expected schedule is a specification, not an observed in-game result.

Main's shield guard must be tested against allied shield-grant/restore abilities, research/item upgrades, capture and save/reload. The three verified disabling mutations prevent the relevant permissions according to installed mappings; they do not themselves promise that externally added shield capacity vanishes from the HUD.
