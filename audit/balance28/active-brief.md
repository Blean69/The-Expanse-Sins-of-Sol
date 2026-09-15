# The Expanse — Sins of Sol
## Targeted implementation brief: Martian Quality and Heavy-Fleet Hierarchy

Continue in the existing local repository. This is the next focused balance increment, not a fresh faction implementation or permission to restart the larger roadmap.

The latest user report is a two-player UNN-versus-MCRN match after faction separation. UNN fielded inexpensive, extremely durable Truman capitals whose concentrated railgun volleys erased Martian support capitals. The user wants scarce but genuinely formidable Martian ships, a capped Truman command class, heavy railguns that struggle against maneuvering light targets, universal orbital Foehammer access, and a functional Razorback escape.

This brief supersedes conflicting earlier instructions to keep Truman at 185 supply, leave all railgun parameters immutable, or make the orbital battery UNN-exclusive. Everything not explicitly changed should be preserved.

**All proposed numbers are first-playtest settings, not established balance findings. The author has not inspected the latest private repository. The local agent must establish the current definitions and tested package before editing.**

## 1. Objectives and preservation rules

Desired identities:
- MCRN: a small, expensive, responsive task force with dangerous torpedo delivery and a superior heavy battle-line flagship.
- UNN: conventional mass, logistics, and durable heavy ships; its most capable battleships are strategic commitments, not cheap general-purpose production.
- OPA: opportunistic independent ships, procurement, recovery, and maneuver. Do not infer OPA balance from a few NPC encounters.

Four standard Tachis should be a meaningful raiding/strike group against comparable investment without adequate defensive coverage. They are not required to defeat an entire fleet or a properly screened installation. Small hulls can still die to a clean heavy-railgun hit.

Keep the 2,000-supply balance target for all factions. Preserve the asymmetric factions, Combined Fleet Sandbox if present, current maps, audio, meshes, functioning PDC rigs, repair/boarding safeguards, colonization, bombardment, and completed research/objective features.

Do not add generic shields, blanket Martian hull buffs, more PDC barrels, global PDC damage increases, a new economy system, new audio, or unrelated ships. Do not reapply historical torpedo damage/speed or metal-price multipliers.

Inspect Git status without discarding, resetting, or automatically stashing work. Preserve the current playable package/hash and record source commit, game version, pinned SDK, relevant installed extensions, and the user's tested version if recorded. Do not assume an old changelog represents the current build.

Use isolated worktrees with explicit read-only access to ignored SDK/assets. Up to three workers are appropriate: (A) economics/classification/access, (B) weapon/flight behavior, (C) validation and test scenario. The integrator owns common definitions, registries, research graphs, final merges, and packages. Do not duplicate an active worker's task.

Do not install, enable, publish, push, buy assets, or launch the game automatically. Deliver offline-checked packages when runtime testing is unavailable. Never label an unobserved gameplay test passed.

## 2. Audit before changing balance

Resolve the actual IDs for Truman, Donnager, Scirocco, standard Tachi, Rocinante, Pella, the newly added Martian destroyer, Raptor, Razorback, and orbital Foehammer platform. Do not guess the destroyer's name. Determine whether the current Razorback shares a definition with a previously named Sunflare and document the exact intended unit.

For each affected unit, report:
- Role, underlying engine class/build group, factory, research access, faction availability, and acquisition paths.
- Supply, ordinary/exotic prices, build time, starting/free-capital discounts, and relevant production modifiers.
- Hull, armor points, armor strength, durability, and any crippled/disabled health state, at matched levels.
- Actual weapon instances, barrels/muzzles, damage per actual firing event, damage recipient/action, reload, burst schedule, penetration, range, targeting, and tracking.
- Movement, acceleration, turning, attack pattern, formation behavior, and hyperspace preparation.
- Items/research/temporary buffs that could explain the reported survivability or volley difference.

Do not equate displayed hull with effective resistance. Verify that one reported twin-gun volley really has the intended number of damage applications. Look for accidental weapon-plus-effect damage, duplicated mounts, action-value multiplication, inherited durability, and repeated level scaling. A real defect gets fixed before an additional balance modifier is applied.

Calculate first-volley damage separately from sustained DPS. Faster Donnager reload cannot repair the specific problem of a Scirocco dying to the first enemy volley.

Separate these comparison budgets: fleet supply, credits/metal/crystal/exotics, production time and infrastructure, research investment, and level. Do not add unlike resources into an unexplained single number.

Create a frozen numerical snapshot. All trial multipliers are applied ONCE against that snapshot by the build process, not compounded on every build or worker run. Final output should contain explicit reproducible values.

## 3. Reclassify Truman as a scarce command ship

Adopt the existing supported Command Ship / supercapital framework where available. Do not invent an engine class name or unlock an unrelated DLC dependency silently. A UI label alone is not completion: update production, access, classification, limits, item eligibility, and AI preferences as required.

First candidate:
- Supply: **400**.
- Maximum: **two owned Trumans per player**, shared across alternate skins/variants and acquisition sources.
- Preserve current intended level-matched hull/armor and railgun hit damage initially after correcting actual defects.
- Preserve its present railgun reload interval; apply only the heavy tracking changes specified later.
- Move it to an actual late command-ship unlock/factory path with a displayed limit.
- Remove ordinary first-capital discounts/free-choice access that would provide a supercapital at the price of an opening capital.

For an explicit initial production-price floor, use the higher of its current price and 80% of the current Donnager's corresponding credits, metal, and crystal costs, rounded sensibly. This is a test recipe, not proof of equal resource value. Use a build-time floor of 80% of current Donnager build time, without lowering an already longer time. Retain legitimate current exotic requirements and inspect the existing command-production pattern before adding any new exotic requirement. Report the resulting base and ordinary discounted costs.

Do not mechanically recompute orbital battery prices merely because the old design anchored them to a fraction of Truman cost. Freeze current battery numerical prices unless separately justified.

Limit behavior:
- Reserve/count queued or under-construction ships through a verified native pattern, so parallel factories cannot exceed the limit.
- Death frees capacity; cancellation frees the correct reservation; reconstruction is allowed.
- Exclude production/reward/launch aliases as bypasses.
- Guard any allowed transfer/capture at resolution when possible; reject acquisition safely rather than delete an owned ship.
- Earlier special-ship boarding exclusions should normally keep Truman outside generic boarding. Do not enable boarding merely by moving class tags.
- If the engine can enforce only production limits but not other acquisition routes, state the exact limitation. Do not label it an absolute two-owned cap when it is not.
- Fresh games are the supported balance test. Do not delete excess ships from an unsupported old save to conceal a migration issue.

### Preserve a viable UNN opening and expansion

The previous design made Truman a colonizing/bombarding capital. Its promotion must not make expansion depend on a late two-copy ship.

Keep an ordinary affordable UNN colony vessel. Keep Truman's existing colony/bombardment abilities where sensible, but verify that UNN also has an accessible non-supercapital expeditionary/support option satisfying the prior capital-role requirement.

Prefer an existing suitable ordinary UNN capital. If missing, prepare the smallest disclosed support refit using available art and native colony/support mechanics. Do not create an uncapped cheap Truman clone with both heavy railguns and its original endurance. Use the current OPA expeditionary or native support-capital pattern as a role/cost reference, not as a donor for unnecessary advanced weapons.

No art hunt is required. Report any unavoidable role gap before claiming the faction is complete.

## 4. Correct the Martian ship hierarchy

Promote the actual new Martian destroyer to the ordinary CAPITAL framework. Move Raptor to CRUISER.

Audit menus, factories, tier prerequisites, build groups, selection icons, fleet roles, experience, level tables, item slots, research filters, boarding filters, and AI purchase choices.

Preserve intended level-one combat statistics, supply, price, movement, and armament for this classification change unless a verified integration rule requires a adjustment. Report any such change. Do not apply an unexplained capital-health multiplier, additional railguns, or an automatic price cut to Raptor.

Use a conservative established level progression if the destroyer needs a new table. Check level-one and high-level performance; do not compound existing per-level bonuses.

Do not preserve a full capital scaling/item advantage on a cheap cruiser accidentally, or remove functional abilities silently. Document how Raptor's old progression is represented after reclassification.

Scirocco remains the marine/repair/expeditionary support capital, not the ship balanced to tank multiple heavy battleships head-on. The destroyer supplies the clearer fighting-capital role.

## 5. Heavy railguns: fewer firing opportunities against agile targets

Preserve catastrophic damage when a heavy railgun lands a valid hit. Do NOT make all small ships ineligible targets, reduce heavy hit damage globally, or add a made-up evasion percentage.

Use native geometry and targeting controls. Published weapon fields include pitch/yaw speed, firing tolerances, target-acquisition duration, and target selection; their exact runtime interactions must be checked against the installed build.

Identify heavy CAPITAL/STATION railguns separately from light/compact guns on Rocinante, Amun-Ra, Scirocco, and other specialists. Do not apply one global scalar to every weapon tagged railgun.

For turreted heavy guns, prepare this first candidate:
- Pitch/yaw tracking speeds: **0.60 times the current intended baseline**.
- Where firing tolerances are wider than 1 degree, test narrowing them to **1 degree**. Do not widen already tighter tolerances or apply this to PDCs.
- Acquisition-duration candidate: **2.5 seconds**, or retain a longer existing value. Use only after tracing its meaning; otherwise keep the existing value and mark the experiment unresolved.
- Preserve base damage, penetration, range, muzzle positions, and reload except for the Donnager-specific optional cadence change below.

These settings are an experimental starting point, not guaranteed good values. Include an unmodified heavy-tracking control.

Verify whether acquisition duration means time with a target selected or time continuously meeting a firing solution. Do not call it a continuous lock requirement unless the runtime actually resets it appropriately. Inspect native target selection and attack-order behavior; a weapon may select a different easy target instead of tracking the current one.

For FIXED/spinal weapons, changing nonexistent turret speed does nothing. Audit the host turn behavior and relevant fixed firing constraints. Do not globally slow every host ship or rotate visual geometry independently of the authoritative unit. Apply the smallest supported adjustment and report which guns need a different approach.

Key behavior targets:
- Stationary and slowed light ships remain vulnerable.
- Lateral movement near a heavy mount reduces opportunities compared with the same stationary target.
- Ships flying directly toward/away from a gun, or crossing far away, need not be difficult to track.
- Large or stationary targets remain practical targets for heavy guns.
- A swarm is not guaranteed immunity: target switching and long reloads can still produce opportunities.

Record attacks fired, time until first shot, target switches, damage events, and kills. Reduced firing opportunity is NOT the same as an already-fired round physically missing.

Do not claim projectile evasion based on tracer animation. Do not turn railguns into targetable slow missiles, fake misses using zero-damage duplicate weapons, add a custom collision simulator, or silently blacklist corvettes.

Audit tracking/range research, targeting auras, movement debuffs, and hull rotation that can negate the intended distinction. Preserve known turret clearance and the earlier PDC firing-tolerance fix.

## 6. Premium standard Tachi: capability, not a larger health bar

First candidate:
- Supply: **120**, superseding 95 for the ordinary standard Tachi.
- Keep current credits, metal, crystal, and build time initially; retain the previously implemented metal premium.
- Hull, armor points, durability, PDC count, PDC damage, PDC range, and railgun eligibility stay unchanged.
- Improve time to maximum linear speed to **0.80 of current**, without raising maximum linear speed initially.
- Improve maximum angular speed to **1.15 of current**, preserving a coherent supported angular-acceleration setting and reporting it.
- Use the MCRN high-speed torpedo loadout described in Section 7.

The point is improved response, delivery, and withdrawal, not a smaller cheap-gun swarm. The Sunflare/Razorback and Raptor retain their speed/role niches.

Audit actual stop-and-fire/orbit/engagement behavior. The name 'corvette' does not mean the entity uses a native corvette attack pattern. Keep useful stand-off torpedo behavior and player-directed movement. Do not force a corvette to close into lethal PDC range merely because its secondary guns can attack ships.

A movement order must behave honestly: verify whether torpedoes can continue launching while maneuvering. Do not advertise firing during movement if the actual attack controller stops firing.

Do not give generic Tachis the Rocinante hero's railgun, crew bonuses, or unique limits. Apply ordinary Tachi supply to factory, launched, rewarded, and procurement variants without double-counting existing reserve/hangar accounting.

Maintain a **95-supply control** with the same motion/torpedo changes for testing, and the proposed 120-supply main candidate. This separates the value of the upgrade from simply reducing player numbers. If the 120-supply unit remains weak, report it rather than certify balance by arithmetic.

Optional follow-on only if needed after those tests: compress the existing torpedo salvo's inter-launch spacing by about 20%, with the same number of rounds and genuine magazine accounting. Do not create free ammunition, stack a second launch ability on the same tubes, or claim unchanged sustained DPS if the complete cycle becomes shorter. Report both first-salvo concentration and full-cycle throughput. Keep this out of the first candidate unless the user authorizes it after the initial result.

Four Tachis are **480 supply** in the main candidate. Compare them against similar investment and the intended weakly screened targets, not against an entire defended empire.

## 7. Faster MCRN torpedoes, carefully scoped

Increase the ACTUAL flight speed of the relevant conventional MCRN anti-ship torpedoes by **20% over the frozen current baseline**.

This is a premium current-MCRN ammunition/loadout benefit by default, not an accidental buff to every shared projectile in the repository. Create private variants only where necessary. Audit Rocinante, Pella, OPA surplus ships, captured ships, UNN/Protogen weapons, NPCs, structures, and siege profiles. List every intended recipient and exception.

Captured equipment may retain its fitted ammunition definition; capture must not grant the new owner's whole research tree or mutate every copy of a shared weapon. Do not silently grant OPA the MCRN improvement through a reused projectile ID. Declare any deliberate hardware-origin sharing.

Preserve damage, penetration, interception HP/armor, magazine capacity, reload schedule, and fuel lifetime. Keep the established 30-second expiry where still current. Do not repeat the historical speed x1.7 or damage x2 changes.

Keep weapon launch/engagement range unchanged. Faster travel with the same lifetime increases potential pursuit distance; document that side effect rather than quietly changing fuel to hide it.

Inspect spawn acceleration, flight speed, steering, target leading, overshoot, and collision. Keep steering values initially unless runtime shows a concrete malfunction. Avoid silently improving speed, homing, missile toughness, and damage together.

Changing a cosmetic travel-speed field is not enough when damage is carried by a spawned torpedo entity.

Do not alter planetary bombardment or platform projectile behavior through shared assets unless explicitly listed. Test the Razorback escape against these new missiles as well as UNN ordnance.

## 8. Donnager: selective sustained-fire improvement

Keep **500 supply**, current intended health/protection, price, build time, PDC count, and per-shot heavy damage after fixing genuine defects.

Prepare an independently identifiable candidate with Donnager heavy-railgun reload interval **0.80 times current**. If current is 30 seconds, the result is **24 seconds**: 25% greater theoretical sustained throughput with unchanged damage per volley.

Apply the Section 5 heavy tracking restrictions too. Faster reload must not mean better tracking or more instant opening damage. This should help Donnager trade against heavy ships, not become an even better corvette executioner.

Use a Donnager-specific weapon derivative where the definition is shared. Do not accelerate Truman, orbital batteries, Scirocco, or hero railguns accidentally.

Keep the cadence experiment separate from the initial Truman/hierarchy correction until it can be compared. Do not apply a hull buff, bigger volley, and reload buff simultaneously.

Audit that both intended heavy guns actually acquire and fire under the tested geometry. If a gun is broken, repair it before compensating with more statistics.

A same-level, similarly prepared Donnager should generally be favored against ONE lower-investment Truman in a clean engagement. It is not guaranteed to defeat TWO Trumans plus support. Compare equal-supply and equal-resource task forces separately.

## 9. Universal orbital Foehammer access

Make the existing orbital Foehammer platform buildable by **UNN, MCRN, and OPA** in the asymmetric mode, through accessible equivalent-tier research and appropriate construction menus.

Retain each faction's research identity, but shared access must not depend on researching another faction's hidden node. The UNN defense branch can retain its own logistics/station benefits; it no longer owns the only counter to heavy ships.

Keep the platform's current actual construction cost, infrastructure footprint, damage, protection, and reload unless a documented defect exists. Do not recalculate prices from the now-more-expensive Truman. Use the Section 5 anti-light tracking behavior for heavy platform guns where applicable; do not copy the Donnager-specific faster reload.

Keep the established two-per-owned-gravity-well limit unless a newer approved value exists. Audit queueing, variants, ownership changes, cancellation, and inherited limit research. Cross-faction unlocks must not create three independent cap buckets.

It remains stationary, expensive, vulnerable without PDC/support coverage, and capable of punishing heavy attackers. It is not a cheap replacement for a field fleet or a perfect anti-small-ship turret.

## 10. Razorback high-burn escape

For the actual requested Razorback scout, set base hyperspace preparation/charge time to **0.1 seconds** and charge-time variance to **0**, where those are the supported installed controls.

Do not alter hyperspace transit velocity/duration, jump from arbitrary locations, bypass inhibitors, or teleport the scout. Preserve current high-G burn health cost, cooldown, movement bonus, and interception vulnerability.

Inspect all remaining delays: alignment, braking, phase-boundary arrival, fleet waiting/synchronization, animation gates, queued orders, and travel restrictions. The numeric charge change does not prove a total 0.1-second escape.

Test a solo Razorback with a queued jump while torpedoes pursue it, both during and after high burn. Verify the correct hull is changed, not all scouts or every ship using shared move data.

Keep other ships' charge behavior and intentional blockade/inhibitor counters intact. If the scout still waits for its fleet, document the supported individual-jump command or relevant scout-only behavior rather than globally disabling fleet coordination.

Do not promise guaranteed escape from every chase. The requirement is that a successful escape burn is not routinely nullified by an unrelated long generic preparation timer.

## 11. Integration order and tests

Build cumulative checkpoints, not a single opaque edit:

A. Inventory/defect corrections; Truman economics/cap/command role; destroyer/Raptor classification; universal platform access; Razorback charge. Verify basic faction expansion and construction remain viable.
B. Heavy-railgun geometry, Tachi supply/motion, and premium Martian torpedoes. Retain isolated baseline/control builds sufficient to attribute results.
C. Optional Donnager cadence variant after comparison, then a recommended integrated candidate.

Do not run a full economic/faction rewrite to force match outcomes. Freeze unrelated OPA changes until it receives a proper player test.

Required comparisons, matched for research/level and repeated from several headings:
- One Truman vs one Donnager, before/after cadence change.
- Two Trumans against an equal-supply mixed MCRN force; also compare actual production investment/time.
- Four Tachis vs a comparable weak-screen force and against a prepared screen.
- Four Tachis from one direction vs split approaches.
- Tachi 95-supply control vs 120-supply candidate.
- Heavy gun against a stationary corvette, lateral near orbit, radial approach/retreat, distant crossing, and a large slow ship.
- A heavy gun surrounded by several corvettes, so one-on-one results are not mistaken for swarm behavior.
- Martian torpedoes against weak/medium/dense PDC coverage, including magazines, expiry, and maneuvering targets.
- Razorback solo escape vs old and new projectiles; inhibitor and group-wait cases.
- All three factions building/researching orbital batteries under the correct shared local limit.
- Simultaneous Truman construction at several factories; capture/reward paths; loss and rebuild.
- Destroyer/Raptor production, levels/items, targeting and boarding classification.
- An opening, colonization, bombardment, and recolonization cycle for each faction after the Truman change.

Log first shot, first volley, successful firing opportunities, target switches, actual damage, hits/launches, time to combat disable vs final destruction, survivor value, and unused/effective PDC coverage where observable. State what can only be judged from video/manual observation.

Research owner, hull origin, and weapon loadout are separate dimensions. Check existing and newly built units, allied/captured ships, and max research. Test save/reload within the SAME candidate; do not imply old-version save compatibility.

Have the two players swap factions in a short rematch before drawing strong conclusions about faction-wide win rates. Player skill, starting geometry, and timing can affect the result; one session is valuable evidence, not a full matchup distribution.

Deliver package ID/hash, source revision, exact before/after tables, new access matrix, cap/queue rules, successful offline checks, runtime observations or NOT RUN, known limitations, and the smallest next user test. Maintain the original rollback.

Do not publish, push, install, or enable automatically. Do not claim balance is proven because the theoretical DPS table improved.

## Documentation leads

These are primary-source capability leads, not permission to overwrite installed data with old examples. The locally installed implementation and supported extensions remain authoritative.

1. Turret geometry and modding controls: https://www.sinsofasolarempire2.com/article/535259/dev-journal-23-combat-geometry-part-one---turrets
2. Missile/PD geometry and velocity: https://stardock.atlassian.net/wiki/spaces/SSEFW/pages/2592473108/Sins+II+Dev+Journal+Combat+Geometry+Part+Two+-+Missiles+and+Point+Defense
3. Damage layers: https://www.sinsofasolarempire2.com/article/525851/the-art-of-war-update---sins-of-a-solar-empire-ii
4. Weapon schema inspected for this brief: https://github.com/StardockCorp/sins2modtools/blob/8e061033afe53b1393eaefd56617a3fd041eeb5f/json_schemas/weapon-schema.json
5. Official movement/hyperspace example: https://github.com/StardockCorp/sins2modtools/blob/8e061033afe53b1393eaefd56617a3fd041eeb5f/examples/mods/super_fast_trader_scout_corvette/trader_scout_corvette.unit

**Success:** UNN cannot buy a supercapital battle line at ordinary-capital economics. Martian ships earn their premium through delivery, maneuvering, and credible heavy support. Four Tachis are a serious commitment; a clean railgun hit is still a disaster; outmaneuvering a heavy gun meaningfully improves their chances.
