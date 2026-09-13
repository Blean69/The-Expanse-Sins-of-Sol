# Manual acceptance checklist

## Donnager0.10 — current next gates

Use only `expanse_donnager10`, and record its package hash in `audit/manual-results.md`. All new Donnager tests are **NOT RUN**. The precise setups and limits are in [Donnager handoff](donnager10.md#workstation-gates-in-order).

| ID | Gate | Result |
|---|---|---|
| D10-1 | Apply Changes/logs, titan factory/research, shared titan cap in both directions, build/cancel/cost, eight slots and ability buttons | NOT RUN |
| D10-2 | PDC0 and rail0 alignment/rotation first, then remaining mounts, slow navigation, selection/UI, shields and four blue nozzles/phase plume | NOT RUN |
| D10-3 | Independent rail cadence; light/front and heavy/rear magazines; PDC ship damage plus interception during an explicit ship attack order | NOT RUN |
| D10-4 | Reactor30s then120s recovery; partial/empty magazine progress; paid Corvette launch/supply race; one40% marine roll and delayed target/caster loss | NOT RUN |
| D10-5 | Own/allied/enemy blast radius and chain reactions; save/reload during timers; one ship and fleet performance; existing0.9 regression | NOT RUN |

## Current polish variant — test these next

Use only `expanse_corvette_polish`; loading and hashes are in `docs/polish.md`. Earlier baseline observations do not transfer to this new package. Record results in the existing runtime log.

| Test | Procedure | Result |
|---|---|---|
| P1 surfaces and UI | Confirm correct mod-browser title/logos and no missing metadata warnings for this variant. Orbit the hull from above/below/fore/aft, especially the three screenshot angles; inspect holes, normals, PDCs and emissive/texture appearance. Check HUD/tooltip/tactical icons and selected states at 100/150/200% UI scale | NOT RUN |
| P2 six physical turrets | Identify mounts 0–5 using the diagram; present targets around and above/below the ship. Each base yaws, each barrel pitches, flashes originate at its own tip, fixed linkage stays fixed, and no static moving geometry is duplicated. Check clipping and arc boundaries | NOT RUN |
| P3 cadence and budget | Verify PDC autocannon display and exactly six firing mounts. Measure one bearing gun before multiple overlapping guns; distinguish visual pulses from damaging events. No hidden seventh autocannon or doubled ship/interception budget | NOT RUN |
| P4 interception while attacking | Keep an explicit attack order on a nearby enemy ship while enemy Ogrov torpedo entities enter the bearing PDC arcs. Observe each gun's switch/latency, projectile armor then hull damage, destruction before arrival, no subsequent impact, and return to ship fire. Repeat idle/moving and saturated salvos | NOT RUN |
| P5 damage and persistence | Measure damage/penetration/target durability/armor strength/armor/hull separately; compare 1/3/6 bearing guns with provisional assumptions. Build, select, move, destroy and save/reload, including while turrets track and torpedoes travel | NOT RUN |
| P6 scope and performance | Check ordinary and applicable neutral/garrison Cobalt users. Compare 1, 6 and 30 ships idle/firing/intercepting with fixed camera/settings; note frame time, simulation speed and save/reload. Unrelated shared vanilla weapons remain unchanged | NOT RUN |

The user subsequently observed the baseline model loading and fixed muzzle firing, and reported surface holes; see `audit/manual-results.md`. This does not establish completion of the full rows below or any new polish variant. The agent has not launched the game. Use a fresh save and only one project variant at a time. Record game build, variant, map, factions, research, bonuses, graphics settings, ship counts, wall-clock timing, screenshot/video or log evidence, and result.

| Test | Procedure and acceptance | Result |
|---|---|---|
| Name-only load | Enable `expanse_cobalt_name`, apply; no new resource/assert errors | NOT RUN |
| Two text entries | Ordinary Cobalt shows MCRN Corvette-class / Fast-attack torpedo frigate; unrelated text still works | NOT RUN |
| Construction | Fresh TEC Enclave and Primacy games; ordinary build menu, queue, cost 300 credits/55 metal, supply 5, base build time 20 s before bonuses; cancel/refund normally | NOT RUN |
| Visual load | Disable name-only, enable visual; model and all materials load without missing-file/alias errors | NOT RUN |
| Shape/orientation | Nose follows actual unit forward; +Z guns, aft exhaust; six visible deployed PDC assemblies; no invisible/backfacing panels | NOT RUN |
| Texture/UI | Color, normal direction, text transparency, mipmaps, distant readability; vanilla icons/voices and shield shape acknowledged | NOT RUN |
| Selection | Click hull, box-select, group-select, control group, fleet grouping, HUD tooltip and tactical icon all work | NOT RUN |
| Movement | Move, turn, strafe, stop, formation movement, collision avoidance, phase jump and arrival; no visible hull-only flip | NOT RUN |
| Baseline firing | Same Cobalt damage/cooldown/range; only two fixed muzzle positions; bullets, muzzle flashes and impacts originate correctly | NOT RUN |
| Baseline point defense | Baseline has no PDC weapon: verify no unexpected interception or damage multiplication. Six gun models are static | NOT RUN |
| Damage/destruction | Shield hit, armor/hull damage, smoke/sparks, explosion, debris, model disappearance, selection release; inspect surface placement | NOT RUN |
| Save/reload | Save while idle, moving and fighting; quit/reload with same mod/version; repeat selection, orders, firing and destruction | NOT RUN |
| Shared assets | Vanilla Cobalt weapon definition, Garda and Ogrov performance unchanged; no global weapon overrides; other units' materials/effects normal | NOT RUN |
| Regression/rollback | Disable project mod and apply; fresh vanilla test returns Cobalt model/text and has no new errors | NOT RUN |

The visual baseline changes the Cobalt definition wherever reused; this is known scope, not faction isolation. Check neutral/garrison appearances and the unchanged special garrison text.

## Next workstation gates — separate variants, stop at the first failure

Packages, hashes and reproduction are in `docs/experiments.md`. Record the ZIP and source-tree hash from the sidecar in the existing `audit/manual-results.md` template. Use fresh separate saves and only one project variant at a time. The headless assignment did not install or enable experiments.

| Gate | Procedure and evidence | Result |
|---|---|---|
| G1 name baseline | Run name-only load/text/construction/selection/movement/save-reload rows above | NOT RUN |
| G2 visual baseline | Disable G1; run visual load, six static assemblies, orientation, fixed muzzle firing, selection, movement, damage/destruction and save/reload; inspect shared neutral/garrison Cobalt scope. Newly observed baseline invalid tangent frames require close normal-map lighting inspection; baseline remains frozen | NOT RUN |
| G3 stock ship control | Only `expanse_exp_stock_pdc`; no Garda light-autocannon unlock. Garda attacks enemy Cobalt in mount 0's forward-left arc. Identify that muzzle, record shots, armor/hull changes; test corvette/strikecraft/flak and friendly exclusion separately | NOT RUN |
| G4 torpedo control/interception | Enemy Ogrov attacks a valid capital/defense target, first without screen, then with Garda. Measure projectile armor/hull loss, destruction before arrival and absence of subsequent collision damage. Increase screen size for destruction evidence if untuned guns lack damage capacity | NOT RUN |
| G5 essential mixed order | Keep tested Garda's explicit attack order against Cobalt active while torpedoes cross mount 0's arc. Close video must show that individual gun's switch latency, tracking, muzzle and recovery to ship fire. Five stock PDCs also defend: aggregate kills cannot establish the experimental gun's priority | NOT RUN |
| G6 one firing budget | Equal-duration ship-only, torpedo-only and mixed trials of mount 0. Count damaging events separately from visual tracers; verify mixed targeting does not double rate. Repeat mid-burst/cooldown and idle/move/attack-move controls | NOT RUN |
| G7 imported rig | OFFLINE BLOCKED: tangent-frame failure; no package available yet. After correction/packaging, disable stock experiment; only `expanse_exp_tachi_one_pdc`. One dorsal aft-facing turret uses stock Garda torpedo/strikecraft eligibility. Present suitable targets in its aft arc; inspect yaw/pitch direction, pivot alignment, barrel tip flash, conservative arcs and clipping. Other five assemblies stay static | NOT RUN |
| G8 persistence/scope/performance | Save with tracking and torpedoes in flight; reload same variant/hash. Repeat movement/selection/destruction. Test 1, 6, 30 ships as below; inspect Cobalt neutral/garrison reuse for rig, Garda/Ogrov reuse for stock experiment | NOT RUN |

For G7 the retained Cobalt fixed autocannon is separate from the single PDC. No dual-purpose PDC or torpedo weapon is added to the imported hull. A Cobalt attack order alone therefore does not provide a target for its stock PDC. Pitch limits/sign and hull occlusion are candidates requiring observation. G3–G6 establish weapon behavior independently from G7's imported geometry; do not combine the experiments to bypass a failed gate.

## Later combat phase — only after the gates above and six-mount integration

| Test | Procedure and acceptance | Result |
|---|---|---|
| Six independent mounts | Inspect each base/yaw and barrel/pitch axis; one firing budget per assembly; no static duplicates | NOT RUN |
| Muzzles/arcs | Fire from each cluster; test targets fore/aft/port/starboard/above/below; no hull penetration, dislocated flashes or impossible coverage | NOT RUN |
| Torpedo salvo | Count actual spawned torpedo units and damage events; verify aperture location, direction, homing and target hit | NOT RUN |
| Interceptability | Enemy PDC can select, hit and destroy incoming torpedoes; destruction prevents their later hit damage | NOT RUN |
| Well-wide reach | Opposite sides of a controlled large well, including target motion; no premature expiration; no unintended cross-well targeting | NOT RUN |
| PDC target eligibility | Hostile torpedo, strikecraft, corvette, frigate; friendlies excluded; record actual accepted/rejected target types | NOT RUN |
| PDC effectiveness | Measure damage, penetration, target durability, armor strength, armor loss, hull loss separately; verify expected vs observed numbers | NOT RUN |
| Interception during attack | Maintain explicit attack order on enemy ship; introduce torpedoes from several directions; PDCs respond while order remains | NOT RUN |
| Priority/recovery | Torpedoes arriving mid-burst preempt ship fire as intended; after threats clear guns return to nearby ships without manual retargeting | NOT RUN |
| Shared budget | Compare shots/damage per physical gun during ship-only, torpedo-only and mixed targets; no doubled rate in mixed engagement | NOT RUN |
| Short-range kill | Controlled small target in actual arc overlap; record time-to-kill against approximately 15 s goal; repeat without faction/research buffs | NOT RUN |
| Standoff | From beyond PDC range, issue attack; corvette engages with torpedoes without unnecessarily rushing into PDC range | NOT RUN |
| Saturation | Increase incoming salvo size; report intercepted fraction, survivors, hull/armor damage and time to death after overwhelm | NOT RUN |
| Save/reload combat | Save with torpedoes in flight and PDC tracking, reload, verify projectile references, mounts, cooldowns and orders | NOT RUN |

## Performance and evidence

Repeat idle/moving/firing/intercepting/destruction at **1 ship**, **6-ship formation**, and **30-ship fleet**, then 60 if stable. Use the same camera, map, controlled targets and settings for vanilla and mod comparisons. Record frame time/FPS, simulation responsiveness, memory and save/reload time. Also test zoomed-out same-well readability; a hull may switch to a tactical icon at distance regardless of mesh detail. Do not change camera/UI ranges merely to claim it is always visible.

Keep the first failure's log and a concise reproduction. Append observations to `audit/manual-results.md` with date and evidence. Use PASS only for the test actually performed; otherwise FAIL, BLOCKED or NOT RUN. Do not infer six-gun behavior from a one-gun test or large-fleet performance from one ship.

## 0.3 corvette and Rocinante gates (all NOT RUN)

Test each named package alone on a fresh save. Keep the working 0.2.1 and baseline folders intact. Record ZIP hash, enabled mods, game build and exact observer in `audit/manual-results.md`.

1. **C03-1 — Loading and geometry:** Apply Changes without errors; construct/select/move one corvette. Orbit the camera around nose, underside, engine and repaired panels. Follow all six PDCs through their aiming range: support sockets/yokes should remain connected and avoid clipping. Compare the three latest screenshots. Check portraits and tactical icons.
2. **C03-2 — Torpedo cycle and interception:** Use a durable stationary enemy with clear vision. Time actual launches: two at 0/10/20/30 seconds; eight total; next pair expected at 150 seconds for the timed experiment. Check dorsal/ventral launch locations, initial direction and clearance from closed hatch surfaces. Repeat against Garda/PDC coverage: destroyed torpedo entities must not later inflict damage. Measure surviving impact damage and separately record shields, armor, durability and penetration. Compare short range and opposite edges of the same gravity well; verify no targeting across wells.
3. **C03-3 — Orders and ammunition:** Repeat with attack, move and stop orders during the cycle. Destroy or move the target out of its gravity well after the first pair; introduce another target. Record whether unused slots/rounds are retained, skipped or reset, and when reload begins. Save/reload during firing and at 30/90 seconds of reload. For the timed experiment, persistent remaining ammunition is NOT implemented; do not mark its magazine acceptance passed merely because an uninterrupted salvo times correctly. Check PDCs continue intercepting during the ability.
4. **C03-4 — Orbit and phase effects:** Observe circling with unchanged acceleration/turn/speed values. Record actual range, collision avoidance and whether abilities stop the orbit or draw the ship into PDC range. Phase between planets, between stars where available and through destabilized lanes: compare blue travel plume length with ordinary exhaust. Check nozzle position/direction and whether residual tunnel or ordinary exhaust remains. Charging/exit effects are still stock.
5. **H03-1 — Hero visual/acquisition (only after complete hero package exists):** Construct from the TEC frigate factory; verify new model, stand absence, deployed guns, hero name and blue plume. Two factories queue the hero simultaneously; verify the configured one-per-empire limit, cancellation/refunds and rebuild after destruction. Check ordinary Cobalt remains unaffected by hero-only weapons, HP, abilities and price.
6. **H03-2 — Hero combat/abilities:** Compare railgun against unbuffed Cobalt/Garda, then Kodiak/capital with separate armor/shield/durability records. Sustained same-target interval expected 10s; retained target-acquisition delay adds 1s on switches. Measure Belter Ingenuity's actual total repair/tick timing; Overcharged Reactor costs 50 AM and raises maximum speed 50% for 10s without changing turning. Fire the independent eight-torpedo salvo during normal firing and during normal reload; verify normal ammo/timer unchanged. Measure +15% natural hull/armor regeneration on self, own ships, allied-player ships and out-of-well controls; scripted repair is outside this bonus. Observe up to2s aura linger, nonstacking, capture/death cleanup and save/reload.
7. **C03/H03-5 — Persistence and scale:** Destroy and rebuild, save/reload, then compare one ship, a small formation and a larger fleet. Record simulation speed, frame rate, projectile counts and effect visibility at close/far zoom. Do not conflate tracers with damaging events or visual projectile disappearance with successful interception.
# Follow-up0.4 workstation gates

Run the combined0.4 package alone. Record results in the existing `audit/manual-results.md`, including exact enabled mods, package hash, game version and save used. All gates below are NOT RUN for0.4 until observed.

1. **Load and build:** Apply Changes without loader errors; build an ordinary corvette and one Rocinante. Inspect hull surfaces from above/below/bow/stern. Check straight axial alignment, support connections, selection outline and unchanged construction/hero cap. Confirm no old static gun remains under each moving assembly.
2. **Six hero guns:** At slow speed, engage targets on both sides and above/below. Observe all six independently tracking within their arcs, physical yaw/pitch pivots and tracer origins at moving muzzle tips. Check collisions with housings and self-intersection. PDC3's inherited aft-pointing pose needs particular attention. Preserve the accepted rail damage/cadence and verify rail/launch/exhaust alignment after rigid geometry correction.
3. **Compact torpedoes:** Inspect both ordinary and hero normal launches and the separate8-round hero salvo. Verify Javelis-sized body/trail/muzzle effect, modestly faster flight, turning against crossing targets, no endless close-range loops, and the same damage/penetration. Count2rounds per10seconds,8before empty,120seconds after empty to reload. Damage values alone do not establish effectiveness.
4. **Defensive engagement:** Issue an explicit attack order against a ship, then send incoming torpedoes from several directions. Establish actual torpedo damage/interception, target choice, one budget per physical gun and continued anti-ship engagement when defensive pressure clears. Compare smaller missile bounds and shorter reaction time against the previous version.
5. **Persistence and performance:** Save/reload mid-magazine, mid-reload and during an engagement. Test target loss/reacquisition, a closer friendly unit beside an enemy, orbiting, phase transitions and destruction. Compare one hero, a corvette formation and a larger fleet at the same camera distance; watch the higher-detail hero's frame-time cost. Do not label this a fleet-performance pass from one ship.
# Amun-Ra component gates — candidates only

These are not installed or complete ship tests. Attach each probe to an isolated stock-hull experiment only after complete-package validation. Record all results in the existing manual-results log.

1. Observe the no-cloak launch telemetry probe: launches 1/2/3, reveal deadline on launch 4, no extension on 5/6, and reset after 60 seconds. Count individual projectiles, including misses/interceptions. Save/reload at count 3 and during the deadline.
2. Exercise tagged PDC/rail hits separately from torpedoes. Confirm hit-time reveal behavior and document that missed shots do not trigger this probe. Later cloak integration must also test all enemy detector qualities, manual toggles, refreshes and jumps.
3. Test one boarding attempt against a valid capital: compare the modeled shuttle's movement with the three-second scheduled roll. Record successful and failed rolls. Test excluded hero/titan targets, insufficient supply, target/caster death, phase departure, concurrent attempts and a save during travel. A success does not prove a calibrated 10% distribution.
4. After full ship integration, test the intended six-unit limit across queued construction, losses, rebuilding and captures. Per-player limits must not be described as a faction-wide shared cap.

## Amun0.6 ordered workstation gates — NOT RUN

Use one combined variant alone in a fresh disposable save. The already accepted Rocinante geometry/performance budget does not require re-optimization.

1. **Core loading and construction:** load `expanse_amun06`, apply changes without parser errors, select/build Amun in TEC, verify portraits/icons, limit six; try a seventh queued ship, rebuild after loss and inspect capture/limit interaction. Verify old Cobalt/Rocinante costs and guns remain unchanged.
2. **Core combat and navigation:** one Amun moves/orbits, selects and phase-jumps; all three PDC yaw/pitch rigs aim from connected supports with correct muzzle alignment. Attack a ship while incoming torpedoes arrive; measure shared firing budget and interception. Check the rail muzzle, damage and ten-second cycle. Check two torpedo ports, two-per-ten cadence, eight capacity and two-minute empty reload. Compare Amun900/1500/25hull/50armor against unchanged Martian750/1250/50hull/100armor; damage effectiveness is separate from target eligibility.
3. **Timed boarding:** launch one modeled pod from its own door toward a valid enemy capital. Check visual orientation/delay, exactly one10% attempt after3s, target supply recheck and correct new owner. Repeat sufficient independent attempts to assess randomness; a single failure is expected90%of the time. Test target/caster destruction, detection loss, simultaneous casts, insufficient supply and save/reload during travel. The visual pod cannot be intercepted. Hero/titan/friendly targets must remain ineligible where filtered.
4. **Optional cloak:** only after the core works, load `expanse_amun06_cloak` alone. Verify Harbinger-gated manual cloak and enemy detector behavior. First three individual torpedoes should not trigger this reveal; fourth during second pair should. Check60s duration, more shots not extending it, successful PDC/rail hit reveal and known miss limitation. Toggle cloak during reveal, save/reload with count3 and during reveal, check expiration restores visibility state appropriately.
5. **Completion/performance:** destruction and save/reload for both variants; one ship, small formation and six Amun alongside the unique Rocinante. Record actual FPS/frame-time observations and errors. Do not mark these gates passed from offline validation.

## Rocinante voice0.7 — NOT RUN

Use one complete voice variant alone. Verify spawn/selection, move/attack/retreat/jump, armor warning and mood routing. Compare perceived volume with vanilla voices and inspect captain/good-news peaks/background. Repeat orders for suppression/overlap, listen for incomplete source phrases, and verify hero destruction/save/reload stop or resume dialogue correctly. Confirm all other ship/effect/engine audio is unchanged. See [voice measurements and detailed test notes](voice07.md).

## Update0.8 ability-set regression — NOT RUN

Load only `expanse_amun08_cloak` in a fresh game; construct Amun and Rocinante. Check boarding/cloak and hero active controls, then boarding cursor/pod/cooldown before assessing its10% capture chance. Verify enemy-view cloak/detectors, fourth missile and60-second reveal, save/reload and supply/ownership constraints. Listen to the six new lines. See [ordered test instructions](update08.md).

## Soundtrack0.9 — NOT RUN

Enable only the chosen0.9 combined variant. Test menu theme/loading, TEC ambient states, the five approved combat tracks (Signal beginning at1:05), battle exit, music slider and voice/effect mix. Observe looping/crossfades and victory/defeat pools when available. Repeat the0.8 ability-control and save/reload gates; no music check establishes boarding/cloak success.

## U11 — Martian fleet integration (new game first)

Use only `expanse_update11`; record ZIP hash, game version, faction and log path. Every U11 result starts NOT RUN. Earlier user observations apply only to earlier packages.

1. **U11-1 load/build/supply:** apply without errors. Morrigan is the starter; MCRN Corvette is a separate option with its own model/icon. Confirm costs25/55/110/500 for Morrigan/Tachi/Rocinante/Donnager, unique hero and shared titan limit. Check neutral/garrison Cobalt users now show Morrigan. Pella is not present.
2. **U11-2 reinforcement:** cast Donnager launch with55 free supply, then54, insufficient resources, and concurrent casts. Confirm exactly one owned Tachi after2s,300credits/55metal payment,20s cooldown and no `unit_spawner` assertion. It must not spawn the Morrigan. Record payment/refund if arrival fails.
3. **U11-3 hull/UI/voice/drive:** inspect restored Donnager bevels/socket15 and all18 mounts; verify larger normal/phase blue plumes at allfour nozzles. Select/order repeatedly for voice variation. Inspect Morrigan's two supports, two turrets, both forward tube collars, drive/UI and orbiting. Morrigan must not announce railguns/hammers.
4. **U11-4 live combat:** attack a ship while incoming torpedoes enter PDC range. Confirm individual budgets and coverage (Don6000,otherExpanse3500), rotation/muzzles, no firing through hulls, and observe whether increased coverage/turn acceleration improves close-orbit survival. Record per-mount shots/damage and target armor/hull. Morrigan should launch at0/10/20/30s, alternate tubes, reload120s after empty; test target loss and acquisition.
5. **U11-5 boarding and shields:** Amun/Don target capital, command-tier supercapital and titan; test detected/hidden target, wrong owner, full supply, existing/queued titan and Rocinante exclusion. Record capture samples (10%/40%, one roll), not just a single outcome. Confirm shieldless TEC/Expanse at all ship levels, mixed armor upgrades preserved, shield-only purchase/research controls hidden, and foreign factions unaffected. Exercise allied shield grants, captured foreign/TEC hulls, TEC planetary shield items and old inventory separately.
6. **U11-6 failure/persistence/performance:** confirm accepted reactor explosion hits allies/enemies as before; destroy a Morrigan, save/reload damaged ships, magazine/reinforcement/boarding states and shield guards. Record one/three higher-detail Donnagers and representative mixed fleet FPS/frame times at matching camera/settings; earlier three-ship performance does not certify this larger geometry. Test old saves only as a separate compatibility observation.

## U12 — Capital fleet and racing scout

Use only `expanse_update12` in a new game. Record its ZIP hash, game version, faction, ship level/items, camera settings and log path. All rows begin NOT RUN.

1. **U12-1 apply/build/limits:** apply without warnings; build Raptor, Pella and Scirocco through TEC capital construction. Verify 150/200/200 supply, prices/experience/component slots, Pella unique tag with existing/queued Pella, and shared titan cap unchanged. Confirm Sunflare replaces the scout at 5 supply and applicable neutral/garrison scope. Verify 2,000-supply sample arithmetic in actual UI.
2. **U12-2 model/mount/UI:** inspect Pella eagle on its forward dorsal panel and model-based icons, silver material and unchanged orange Raptor paint. Check silhouettes/relative scale, all four capital exhausts, Sunflare's single actual nozzle, normal/jump blue plumes and captain variation. Start with one PDC and Scirocco rail; inspect base contact, aiming and muzzle positions through arc extremes before testing all 9/9/12 PDCs. Watch the extended Scirocco rail support at ±15° for hull intersections.
3. **U12-3 combat:** hold an attack order against a ship while hostile torpedoes approach; measure individual PDC shot/damage budgets, target eligibility, prioritization and coverage. Record target armor/hull and ship level. Verify Raptor/Pella 3 light every10s (18 total), Scirocco 5 light every10s (20 total) plus1 heavy every20s (5 total); 120s empty reload, tube cycling, target-loss handling and real projectile interception. Heavy targets are starbase/titan. Scirocco rail should fire every15s with its own damage/penetration; check orbiting does not prevent it from bearing.
4. **U12-4 abilities/scout:** time capital reactor20s plus120s recovery; measure normal/boosted gun and magazine cadence. Test paid Tachi arrival with55/54 free supply, insufficient resources and concurrent casts. Sample boarding odds20/25/25%, detected capital/command/titan eligibility, 600s cooldown, hero exclusions and captured-titan limit behavior. For unmodified Sunflare, measure3,000 normal/12,000 burn maximum speed, damage at seconds1–9 and ten hull remaining from100 without external repair. Test damaged-start death, nine-second buff end,120s cooldown, upgrades/external repairs and two-second jump charge separately from alignment/travel.
5. **U12-5 destruction/persistence/fleet:** inspect capital1,500/2,500 friendly-and-enemy blast and unchanged Donnager damage. Save/reload mid-magazine, reactor, burn, boarding and arrival; verify timers, owner, health, unique limits and visible art. Compare one ship, a formation and the full proposed 2,000-supply fleet at matching camera/settings; record FPS/frame time and logs. Repeat pending U11 reinforcement/shield checks rather than treating inclusion as proof they passed.

## U13 — Model/audio polish

Use only `expanse_update13`, recording ZIP hash, faction, camera settings and logs. Start all new results as NOT RUN.

1. **U13-1 appearance:** load/apply without warnings; inspect painted Scirocco and Morrigan at close and fleet zoom. Inspect Raptor/Pella broad plates at grazing light for crumpling; confirm Pella eagle and mounts remain intact. Source geometry imperfections may still remain. Compare UI to the visible ship.
2. **U13-2 Scirocco guns:** observe each of twelve enlarged biaxial PDCs while attacking a ship and intercepting approaching torpedoes. Inspect base contact, barrel tracking, muzzle origin and hull obstruction at different yaw/elevation. Count one firing budget per mount and compare unchanged damage/cadence. Check existing rail support/arc unchanged.
3. **U13-3 Sunflare:** inspect readable dorsal RAZORBACK lettering from the normal top camera, then orbit the camera to distinguish its other textured facets. Verify nose-forward motion, central aft plume attachment, roll/bank, phase effect and emergency burn; no mirrored text or motion-independent hull rotation should occur.
4. **U13-4 PDC mix:** compare one Morrigan, Pella/Scirocco and Donnager at matching SFX volume, then several ships. Listen close, medium and whole-well: short reports should retain their attack without the earlier overlapping roar. Check for excessive quietness, variation, dropped-sound gaps or clipping; record headphones/speakers and volume. Guns must keep their prior gameplay cadence. No explicit voice cap is claimed.
5. **U13-5 regression:** save/reload affected ships during combat/movement/burn, confirm art/audio persist and destruction stops playback. Check prior build limits, torpedoes, boarding, supplies and reactor effects unchanged. Record fleet frame time; asset checks cannot establish runtime performance.
