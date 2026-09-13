# Donnager groundwork — 0.4

This is an asset and design study, not a playable Donnager package. The current assignment preserves the tested corvette movement and Rocinante railgun. Donnager balance values below are proposals for a later isolated experiment, not claims about canonical weapon performance or observed Sins II behavior.

## Evidence and scale

The official [SYFY CQB recap](https://www.syfy.com/the-expanse/photos/cqb-season-1-episode-4) establishes the Tachi escaping from Donnager's hangar, the battleship being boarded, and Yao scuttling it. This supports a carrier/support role with vulnerability to saturation and close combat. It does not establish onboard ship manufacturing. Production model reference: [Gautam Singh's Donnager work](https://gautamsingh.artstation.com/projects/ZyEXR), credited to the television production with Ryan Dening's concept. The [official concept gallery](https://www.syfy.com/the-expanse/season-1/blogs/the-expanse-concept-art-gallery) provides additional visual context.

The [Force Recon Donnager breakdown](https://www.youtube.com/watch?v=fFoLbsA5Sx0) was located, but its contents/transcript could not be fetched in this session. Do not cite it as directly verified numeric evidence. The [licensed Ships of the Expanse product](https://greenroninstore.com/products/ships-of-the-expanse) was located, but its ship statistics were not inspected.

For planning, use the commonly listed **475.5 m Donnager / 46 m Corvette = 10.337 length ratio**, explicitly provisional. The [TV community reference](https://expanse.fandom.com/wiki/Donnager-class_(TV)) is secondary evidence and reports conflicting PDC counts: 59 in the breakdown versus 43 visible on many television models. Do not mix the [book configuration](https://expanse.fandom.com/wiki/Donnager-class_(Books)) into a supposedly exact television layout. Neither a final PDC count nor screen-accurate railgun angle limits is established here.

The supplied model's exporter units are not meters: measured extent is approximately 450.755 ×450.755 ×1183.901, with +Z forward. Normalize uniformly; never stretch one axis to meet a length target. Use the same game-units-per-meter scale as the existing corvette for a relative-size preview. Donor PDCs retain their physical size rather than scaling by the battleship/corvette length ratio. Collision, minimum camera distance, docking clearance and fleet readability require separate runtime checks before this relative scale becomes a final game setting.

## Asset work and mounting plan

The source contains 1,804,024 triangles,61 meshes,11 materials and67 nodes; no animations or skins. Preserve this full master. A later game derivative needs substantial optimization with normal/material boundaries preserved—the Rocinante regression demonstrates why triangle count alone is not a quality test.

Two mirrored railgun assemblies can be separated geometrically, but the source groups are material chunks, not authored yaw/pitch rigs. Candidate drum-center pivots are estimates. Validate a single assembly's limited traverse, barrel alignment and hull clearance first; document the tested arc instead of inventing a canonical angle. Keep the ship's actual navigation frame aligned with its hull.

PDC splicing starts with a measured existing Tachi assembly, its support and its yaw/pitch rig. Use one damaging weapon budget per physical gun. Lay out fore/aft and port/starboard sectors using the production references, then test occlusion and overlapping defensive coverage. A full network is intentionally deferred until the disputed physical count/layout is resolved and one representative mounting works.

## Balance and abilities to prototype

Treat Donnager as an expensive battleship with embarked corvettes, not a cheap mobile replacement for the whole TEC economy. Preserve global balance and vanilla weapon definitions. Derive private definitions and compare against the installed capital/titan benchmarks recorded in the weapon worker's0.4 report.

| Feature | Minimal experiment | Constraint / counterplay |
|---|---|---|
| Two heavy railguns | Use the accepted hero rail as a damage reference, then test separate broadside arcs | Two copies of2500 damage/10s would total500 raw DPS with both on target; do not silently boost penetration or cadence |
| Heavy torpedoes | Retain the large Ogrov appearance under the existing private heavy-projectile ID | Reuse damage750/penetration1000 initially; interceptable unit health remains independently tested |
| PDC network | Sector-based mounted weapons using the established dual-purpose filter | Current gun is112 raw DPS;43 copies=4,816 and59=6,608 before mitigation. Those totals are warnings against blindly copying the corvette's per-gun tuning |
| Embarked Corvette | Paid, supply-consuming production with a long build time, or bounded reserve deployment if the factory cannot filter the roster | Carrying a Tachi is supported by the episode; manufacturing new ships is a gameplay adaptation. No free unlimited spawns |
| Battle-stations mode | Temporary defensive/repair emphasis with a meaningful antimatter or mobility cost, using verified local modifiers only | Do not duplicate anti-ship and interception weapons to simulate a firing-rate bonus |
| Damage-control teams | Bounded local repair, patterned after an installed repair ability | Overwhelming incoming torpedoes must still be dangerous; avoid whole-well invulnerability |
| Emergency corvette launch | A limited reserve or cooldown-based launch, if the engine can enforce supply and count | Keep separate from normal production; do not pretend a scripted spawn automatically pays costs or consumes supply |

Choose a small ability set after factory feasibility is established. A broad passive fleet buff is not needed for the first Donnager: Rocinante already owns the morale repair role. Self-destruct is supported by the story but would add avoidable balance/UI work and is not part of the first prototype.

Test hull/armor/shields, armor strength, penetration and raw damage separately. Start with isolated vanilla capital and titan targets, then the six-PDC corvette and controlled missile saturation. Set cost, supply and durability from those measured matchups rather than scaling hit points by visual volume. Deployment/manufacturing, rail arcs, multi-direction interception and fleet performance remain untested.

## Installed balance anchors and carrier limitation

The installed starting Kol and Sova each cost50supply,2,500credits/850metal/600crystal and75seconds. Ragnarov and Ankylon cost150supply,9,600/2,900/1,900 and300seconds. These currency summaries omit exotics and prerequisites; the complete read-only definitions and hashes are in `audit/combat04-a/carrier-evidence.json`. Kol starts at3,750hull/2,420armor/2,650shields and500durability, versus Ragnarov12,800/4,425/6,575 and750durability. These are comparison anchors, not approved Donnager stats.

For the first Donnager balance candidate, use the **150-supply/300-second titan cost envelope as a conservative test starting point**, because adding a carrier role, two large rails and a full PDC network to a50-supply capital could overwhelm the existing roster. This is a proposal, not an implemented cost or canon claim. Begin durability at an installed battleship anchor, then tune only this ship from observed effective damage, time-to-kill and defensive saturation. Visual size alone does not require titan mechanics, titan technology or faction-wide changes.

Sova's installed `unit_factory` and mobile factory ability provide a real paid production queue. However, it accepts `build_kinds: ["corvette"]` and the current MCRN remains Cobalt's `build_kind: "frigate"`. A private Donnager factory accepting frigates can build it, but also exposes other available frigates. The pinned schema has no per-unit factory whitelist. Do not silently recategorize Cobalt or change player menus to conceal this limitation.

Recommended first carrier experiment: a private Sova-pattern factory with no construction-speed bonus, restricted to the new Donnager and a measured hangar build point. Clearly disclose the broader frigate roster. If exclusive MCRN production is essential, use a separately labeled **paid reinforcement ability** patterned after installed pirate mercenary spawning and Overseer `required_units`, with one `trader_light_frigate`, owner supply constraint, actual costs, cooldown and prerequisites. This is not a native build queue. Cost/supply atomicity, position, count and arrival after carrier death need tests before acceptance. No factory or spawn ability was packaged in 0.4.

## Concrete local deliverables

Reviewed inventory, license, scale and rail candidates are in `audit/donnager04-c/report.md` and `integration-spec.json`. Editable source remains in `/run/media/haker/NVME 2/expanse-workers/validation/assets/derived/donnager04-c/`, separate from generated packages. Five scene checks and original/master/donor hash checks passed.

The provisional length is1085.2456game units, versus measured Kol837.1276 and Sova826.6402. The two isolated source rail assemblies contain63,432 and63,431triangles. The pinned SDK capital guidance is75,000triangles for the whole model; the source is24.05times that. At677triangles per existing Tachi PDC,43guns alone consume29,111triangles, or59consume39,943. Reduce dense engine/rail detail and budget the hull plus physical gun count before a final conversion. No Donnager game mesh or playable package is eligible yet.

## Next milestone after user-accepted0.9

The user has now reported working cloak, boarding and music in0.9. Keep that accepted combined package intact while preparing a separate Donnager prototype. Existing intake/normalized scenes and measured rail candidates remain the starting point; do not restart the source import or alter the master.

First deliverable: one buildable TEC-foundation battleship with a uniformly scaled, optimized derivative, connected PDC mounts, two limited-traverse railguns, heavy interceptable torpedoes, UI imagery and the established blue drive effects. Aim near the installed75k capital-ship triangle guidance for the complete assembled model, and assess geometry quality before exceeding it. A prototype mounting/coverage layout must be labeled as such until the disputed TV gun count/layout is verified. Preserve per-gun versus whole-ship damage budgets explicitly; copying every corvette gun's112DPS would overwhelm the initial balance.

Stage the work as hull/one rail/one donor PDC geometry first, then the full tested mounting approach and buildable capital package, then the embarked-corvette ability. For exclusive MCRN launch behavior, a paid, supply-checked reinforcement ability is the practical initial candidate; a native factory can expose other frigates and must not be described as an exclusive whitelist. This remains unimplemented. Broad faction/fleet-supply changes are deferred.

Workstation gates: silhouette/scale against existing ships, rail traverse and hull clearance, PDC coverage/interception during an attack order, torpedo mounts, carrier launch clearance/supply, selection/construction/destruction, save/reload and small-fleet performance. Existing0.9 timing/capture edge cases should be logged alongside these sessions without reopening accepted basic functionality.
