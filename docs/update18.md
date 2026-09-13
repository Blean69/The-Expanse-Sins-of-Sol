# 0.18.0 — Sol Gate 1 candidate

This is the first staged test of three selectable identities and the smallest
three-home Sol map. It contains the complete accepted 0.17 fleet. It is not the
full Sol/salvage/Tycho/composite milestone, nor a completed multiplayer acceptance
test. The candidate has not been installed or enabled automatically.

## Package and rollback

- Candidate: `build/experiments/expanse_update18.zip`, mod ID `expanse_update18`.
- Exact candidate SHA-256: adjacent `expanse_update18.sha256` and
  `audit/update18/package-summary.json` (kept outside the ZIP to avoid a self-hash).
- Rollback: `build/experiments/expanse_update17.zip`, version 0.17.0,
  SHA-256 `710a0dde1842d1ea3a9e0f5e28649922a482b808a9e60dbfd7bf1645bdf878db`.
- Rollback source: `9cea830807166ed2e34d7617868ebde019a301a6`.
- Game: Sins II 2.0.3 (318), Steam build 25127248. References are the installed
  game and SDK 24092025, schema commit `8e061033afe53b1393eaefd56617a3fd041eeb5f`.
- This is a self-contained overlay of the complete prior fleet; do not stack
  earlier Expanse packages underneath it. All players need the same complete
  ZIP, matching game build and compatible installed official content. Map
  transfer alone does not distribute the mod's ships/audio. Different official
  content entitlements have not been tested.

Nothing was pushed remotely, published, installed, or enabled for this milestone.
The working installation and retained 0.17 package were not overwritten.

## Changes

UNN, MCRN and OPA have separate picker names, descriptions and existing ship
silhouette badges. All three are generated from the same TEC Enclave player
definition. They share the same hulls, research, costs, supply, build times,
movement, abilities, voices, shieldless behavior and inherited TEC bonuses.
Portraits and AI presentation still use TEC placeholders. Badges do not imply
exclusive ships. Player color is independent of identity.

Original fleet definitions are unchanged. The only existing unit edit appends
the equivalent orbital-cannon ability group for the three new owner IDs. Native
players, picker entries and start configurations remain available. Custom
identities are also registered outside Sol; their behavior on arbitrary maps
has not been observed yet. Fixed home assignment is specific to this scenario.

The seven-node map contains Sol, Earth, Mars, Jovian Habitats, a separate unowned
Jupiter gas giant and two native NPC market annexes. The three homes use equal
terran placeholders; OPA's visible colonizable home represents orbital habitats,
not Jupiter's surface. Home mechanics select two metal and one crystal asteroid
without random extras, using a scenario-local filling override. Actual engine
override precedence must be checked. No vanilla planet is globally reskinned.

Each home connects to both opponents; Earth and OPA can reach each other without
crossing Mars. Sol has one lane, avoiding a central shortcut. NPC homes are off
the invasion routes. This minimal fixture has no early expansion colonies and
is not the final balanced friends map. The installed seed thumbnail remains a
temporary placeholder. Planet art and 24–28-node geography follow the first
runtime gate.

## Exact test lobby

After choosing to test, extract the candidate into its own `expanse_update18`
mod directory, with `.mod_meta_data` directly inside that directory. Use the
same ZIP on every client and enable this Expanse version alone. Start a new game;
do not use a 0.17 save to assess new faction/home setup.

Select **Sol — Three Homes (Gate 1)**, **Normal** start, three human players,
and no alliances. Use these fixed slots:

| Lobby slot | Identity | Expected owned home |
| --- | --- | --- |
| 1 | United Nations / UNN | Earth |
| 2 | Martian Congressional Republic / MCRN | Mars |
| 3 | Outer Planets Alliance / OPA | Jovian Habitats — OPA Home |

Home assignment is slot-based, not automatically faction-aware. Recheck slots
after changing host or rearranging players. Random starts are disabled in the
archive. Arbitrary faction/slot permutations are not supported as automatic
home mappings. Native Normal starting assets/resources are cloned equally;
confirm the observed values and construction access before continuing.

First open the scenario in SolarForge with the candidate assets available. Save
a separate roundtrip copy; retain the supplied archive. Check all seven nodes,
names, lanes, three ownership indices, local fillings and markets survived.
Then run the game test above and record:

1. Picker availability; one correct owned home each; equal resources,
   population, extractors and usable construction/research slots.
2. All three owners can build their first ship and structure. Research one
   small upgrade for only one player; compare existing and newly built ships
   against unresearched opponents. All players can independently build limited
   heroes; one owner's limit must not consume another's allowance.
3. Both native markets work. Ordinary ships traverse each home-to-home lane;
   no hidden/generated wells, collisions or moving-orbit drift appear.
4. Save/reload after construction/research progress; verify home ownership,
   fleet state, owner limits, research and equal economy remain correct.
5. Check home loss and configured defeat/victory behavior, including OPA's
   visible habitat home. Check host changes using the intended slot mapping.
6. Record actual session duration and desync/load errors, with relevant log
   excerpts. No minimum or observed multiplayer duration is claimed here.

Stop at a failed gate and retain the save/log. Full Sol geography is deliberately
not generated until ownership, construction and victory pass this small test.

## Evidence and remaining work

Observed offline: pinned references unchanged; exact clone gameplay/start
parity; five malformed-map inputs rejected; valid chart/local-filling structure;
manifest and GUI merge checks; reference presence; connected graph; deterministic
scenario archive; allowed-file comparison against 0.17; final ZIP contents and
hash checked. A separate worker reviewed faction/start/picker/owner gates and
found no concrete source defect. Unchanged newer installed schema extensions
are recorded separately from schema-validated fields.

Observed runtime: the user broadly reported 0.17 “seems all good.” **No 0.18
SolarForge/game/save/multiplayer test has been observed; multiplayer minutes: 0.**

Separate laboratory outputs, absent from this package:

- Tycho: shieldless native-starbase placeholder, sixteen PDC mounts, four
  torpedo banks and an Industrial Drydock enabling its own factory with +15%
  shipbuilding rate (about 13.04% less build time). One-per-owner limit recipe
  and three slots remain untested; other proposed modules are unfinished.
- Art: approximate Tycho core recovered from the two support-free print
  jobs. Editable glTF has grey/machinery/ochre materials, docking marks and
  emissive patches; no dynamic lights. Original meshes/UVs were absent.
  Missing accessories, inferred assembly, print artifacts, full texture bake,
  game shader conversion and mount placement remain art work.
- Contacts: native-schema component/reward fragments for limited Ceres/Tycho
  services, with no registration into this candidate.
- Operations: native synchronized event interfaces investigated. Arbitrary
  actor-plus-sector global alerts to enemies without vision are not verified.
  The disabled Lua probe is not a functioning major-recovery/capture system.
- Composite: separate real-sixth-exotic registration/grant/debit probe. HUD,
  receive/save/spend/zero, owner isolation and multiplayer remain untested.
  Paid interruptible study and plating are not implemented. Existing shieldless
  guards block absorption/regeneration, so adding capacity alone would fail.

No planet-killer, new faction asymmetry or additional combat ship is included.

## Reproduction and source reports

Run from the project root with the preserved 0.17 output and installed pinned
references. The builders refuse to overwrite existing candidate directories:

```sh
python3 tools/update18_scenario.py
python3 tools/update18_scenario_test.py
python3 tools/build_update18.py
```

To recheck an existing package tree: `python3 tools/build_update18.py --validate-only`.
Use `--package-existing` only for an already validated tree without a ZIP.
Editable map source: `tools/update18_scenario_source.json`; unpacked editable
archive: `build/laboratory/update18/scenario/editable/`.
Faction availability: `build/laboratory/update18/scenario/fragments/availability.json`.
Source/economy/node reports: `audit/update18-scenario/`.
Final integration report: `audit/update18/package-validation.json`.
Laboratory audits: `audit/update18-operations/`, `audit/update18-composite/`,
`audit/update18-tycho/`, and `audit/update18-tycho-art/`.
