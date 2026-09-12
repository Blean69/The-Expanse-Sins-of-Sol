# Manual acceptance checklist

**Every runtime item is NOT RUN.** Headless preparation did not launch the game. Existing game logs are version evidence only. Use a fresh save and only one project mod at a time. Record game build, variant, map, factions, research, bonuses, graphics settings, ship counts, wall-clock timing, screenshot/video or log evidence, and result.

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

## Combat phase — only after integration and baseline acceptance

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
