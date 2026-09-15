Stage B weapon/flight proposal; runtime NOT RUN.

Integration: import `tools/balance28_weapons.py` and call
`changes(stage_a_directory_or_json_overlay, frozen_27_5_directory)`.
Returned edits map relative filenames to JSON objects. Origins record the exact
frozen source and SHA256. `proposal.json` lists every changed pointer, all 173
existing-file replacements and 30 new files. Main integrator must register new
entities and package separately from Stage A; this helper never writes game files.
A mapping overlay is merged over the frozen package and is not mutated.

Default Stage B includes 146 tag-identified PDC weapon ranges multiplied by 1.3
exactly once, including all custom fleet and station weapons. All 14 mounted ship
or orbital rail definitions use their host's new PDC range, with orbital Foehammer
as the sole 3× exception. No other base-game weapon is globally changed. Shared
Amun/Dark Star rail can remain shared because both hosts now have 4,550 PDC range.

Range groups: Tachi, Rocinante, Amun, Dark Star, Morrigan and contract patrol
3,500→4,550; Raptor/Pella/Scirocco/Hephaestus/Gathering Storm/Laconia/Europa/OPA
command 4,500→5,850; UNN 6,000→7,800; Donnager/MCRN station/orbital defensive
PDCs 8,000→10,400. Orbital main rail 12,000→31,200. Shared custom OPA/UNN PDCs
are deliberately included by the latest ALL PDC override, while their torpedoes,
hull speed and damage remain frozen.

Heavy tracking changes apply to Donnager, Truman, Nathan Hale and orbital
Foehammer. Pitch remains zero where the mount has no pitch axis. Yaw becomes
9 from 15 for Donnager/orbital, 12 from 20 for Truman/Nathan Hale. Existing 0.5°
or 1° tolerances stay unchanged; none of those heavy mounts needed widening or
new synthetic axes. Scirocco and Hephaestus compact cruiser rails retain 30°/s.
Fixed Rocinante/Amun/Dark Star/Murphy/Munroe/Gathering Storm rails retain their
host flight and fixed mount definitions. The official turret journal explains
why lateral close-orbit movement can outpace a turret and why fixed weapons
need host rotation, but does not establish a guaranteed dodge mechanic:
https://www.sinsofasolarempire2.com/article/535259/dev-journal-23-combat-geometry-part-one---turrets

Pinned schema defines `target_acquired_duration_required_to_fire` only as a
number. Existing 1.5-second values remain; there is no claim of continuous lock,
reacquisition reset, or configurable evasive immunity. Native
`vasari_heavy_cruiser_medium_wave_cannon.weapon` proves `firing.charge_duration`
can coexist with projectile fire and cooldown. Orbital sets real charge 60 s,
leaves cooldown 30 s. Whether those combine sequentially, overlap, or restart
on target loss requires a timed runtime test; do not label this “60 s reload.”

Raw heavy budgets (damage applications still require observation):

| Host | Weapon instances | Damage / instance | Reload | Nominal opening damage | Nominal sustained damage/s |
|---|---:|---:|---:|---:|---:|
| Donnager | 2 | 5,000 | 30 s | 10,000 | 333.33 |
| Truman | 2 | 3,500 | 60 s | 7,000 | 116.67 |
| Nathan Hale | 2 | 2,400 | 60 s | 4,800 | 80 |

Each Truman/Nathan Hale instance has two existing muzzle positions; that is not
proof of two damage applications. No muzzle, weapon count or damage changes
are made. Optional `donnager_cadence=True` changes only its two cooldowns to 24 s,
nominal 416.67 damage/s (+25%); first volley remains 10,000. Default is false.
The `heavy_tracking=False` control retains baseline heavy speeds/tolerances.

Tachi: supply 95→120; acceleration ramp 5→4 s; max angular speed 25→28.75°/s;
max linear speed remains 1,250. Angular ramp remains 1.25 s, so angular
acceleration increases coherently from 20→23°/s². `tachi_supply=95` is the explicit
supply control. Four existing launch-corvette ADS supply checks become 120,
including Pella's launch path because it spawns the same Tachi. Other launch
costs, cooldowns and hull physics stay frozen. Menu display hull stats are not
edited by this helper; shared weapon ranges naturally appear through references.

MCRN private light projectile: 2,125→2,550 speed. Private heavy projectile:
1,275→1,530. Each differs from its original only at `/physics/max_linear_speed`.
Nine private magazine triplets preserve ability positions, all damage and
penetration, torpedo HP/armor, 30 s fuel, steering, launch range, magazines and
reloads; only private entity/ADS/buff links and speed display values change.
Recipients are Tachi, private MCRN Morrigan, Raptor, Scirocco, Donnager,
Hephaestus. The latter keeps distinct light and medium magazine damage using the
existing shared heavy projectile geometry. No OPA/Laconia/Pella/Rocinante/UNN
projectile or magazine changes; no missile defense, station, boarding or IPBM
speed change. Retained 30 s lifetime implies a 20% higher maximum-speed distance
ceiling, not a precise integrated pursuit distance prediction.

The bounded private Morrigan unit retains `skin_groups` pointing to the existing
Morrigan skin, every stat and both existing PDCs. Only its ability reference
changes. Exactly four entries each in `expanse18_mcrn.player` and the gameplay
alias `trader_loyalist.player` use it: buildable list, garrison random unit, trade
escort and model preview. Foreign/NPC original Morrigan and contract patrol stay
unchanged. Six additional exact unit-reference replacements in quick/advanced
start modes affect only MCRN and trader_loyalist configurations. Research has no
explicit unit-filter dependency on trader_light_frigate; original weapon tags
retain upgrade eligibility. The one research exact match is a display-only escort
listing, preserved because the skin/name are identical. Native foreign Eivonn
ship spawning deliberately retains the original hull. Captured upgraded MCRN hulls retain fitted equipment; the change is
not implemented through a global owner modifier. Existing saved projectiles and
buff instances may retain old definitions until they expire; compare fresh ships
in new games before interpreting migration behavior.

Checks actually run: `python3 tools/balance28_weapons_check.py`. Of 203 changed definitions, 201 JSON
objects pass the pinned schemas with Draft7Validator; 149 critical typed entity
references resolve against candidate+baseline+game. Pinned SDK contains no
matching .start_mode schema: those two schema checks are explicitly NOT RUN,
with exact pointer-only changes reviewed separately. Frozen entity hashes
unchanged, deterministic proposals, repeated-overlay idempotence, Stage A overlay
preservation, supply95 control, optional cadence isolation and shared projectile
exclusion all pass. This is a targeted reference check, not a replacement for
main's full merged reference/manifest validation. No install, packaging, enabling,
push or game launch performed here.

Smallest runtime gates: (1) Compare fresh Stage A/B Tachi and 95-supply control
against stationary and close-orbit heavy targets, record hit fractions and focus
fire separately; (2) time Donnager/Truman/Nathan rail first volleys and reloads,
confirm per-mount damage; (3) orbital charge with target retained, lost and
switched; (4) compare MCRN private torpedo speeds and fuel against unchanged
OPA/UNN shots, verify magazine counts and PDC interception during attack orders;
(5) MCRN build/escort/garrison Morrigan and Tachi launch supply rejection/success,
then save/reload. Optional Donnager cadence belongs in a separate test package.

OPA Pella launches standard expanse_mcrn_corvette hulls; these are intentionally
MCRN-origin hardware with the same 120 supply and private faster light torpedoes.
Pella own installed torpedo magazine remains unchanged.
