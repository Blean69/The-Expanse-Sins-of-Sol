# 0.22.1 — Stage3 Orbital Defense candidate

Supersedes0.22.0: new defenses now use the actual player `structures` constructor list. The earlier candidate incorrectly listed them in ship production. Old files are retained for audit; use this corrected package.

Separate successors to frozen0.21.1 asymmetric and combined packages. Use one package only in a fresh game. No game installation, runtime test, multiplayer test or remote publication has been performed. Original0.19,0.20 and0.21.1 packages remain available for rollback. The user's three-hour playtest refers to0.19 only.

## New defenses

UNN Orbital Defense Command unlocks a Foehammer Orbital Battery: one unchanged Donnager railgun and two unchanged Donnager PDC profiles, using newly compiled fixed-platform art. It costs2000credits/500metal/350crystal, takes120seconds, uses4military slots and has4000hull/3000armor. Two batteries per gravity well across all matching aliases, including captured batteries. No forced deletion of captured excess; further builds are expected to remain blocked. Queue/capture counting needs runtime testing. The rail keeps its narrow yaw and zero pitch mount limits; native stationary body rotation remains8degrees/second. Elevation coverage is a specific runtime check. MCRN/OPA can capture batteries; their asymmetric research does not manufacture them. All owners can test them in the combined sandbox.

Every faction gains a four-PDC picket, using the existing TEC hangar exterior with strikecraft removed:1200/250/100,80seconds,3military slots,4000hull/1500armor. Each PDC retains the85DPS Earth profile. It does not replace an escort fleet against armored ships.

## Engineering stations

MCRN Naval Anchorage, UNN Fleet Support and OPA Tycho-pattern Engineering Station use disclosed native TEC starbase art. This is not an imported Tycho model. Each costs4000/900/700, takes240seconds, uses8military slots, has12000hull/4500armor and four faction-profile PDCs. A shared tag permits one major station total per player, including the combined sandbox. Captured excess survives; ordinary future construction is expected to be blocked until below the cap. Each provides the ordinary ship-component shop service.

Three normal equipment slots compete for four700/150/100 modules,60seconds each:

| Module | Actual benefit and scope |
|---|---|
| Ordnance Control | Two physical local defense-torpedo banks, existing300damage/two shots per8seconds profile; explicit attack orders. Independent defensive stores, not a ship magazine refill. |
| Repair Anchorage | Up to3owned ships within6000,20hull each per second, maximum60total. Shared pending reservation prevents same-effect addition; excludes Scirocco engineering/Fleet Train and specified native active repair. |
| Defense Coordination | Owned armed ships within6000 get10% PDC tracking only. No rail tracking, damage, range or firing-rate boost. |
| Industrial Drydock | Owned functional orbital factories within6000 gain10% nominal production rate, about9.09% less base build time. No empire-wide effect. |

Naval Readiness (MCRN) and Dockworker Damage Control (OPA) raise fitted local station repair20→22 per target, maximum66total. Both researched in the sandbox still give one upgrade. These owner-scoped technologies can improve captured engineering stations, but do not grant foreign production. Paid modules and source proximity remain necessary. UNN Fleet Train and paid shipyard mobilization from0.21.1 remain intact. Ordnance Control is a modest torpedo alternative to the suggested heavy-gun module; the separate Foehammer supplies that role without inventing a gun on an incompatible station mount.

## Evidence and next test

Offline checks cover schema/source extensions, explicit references, unit tags and limits, faction access/prerequisites, research-cell collisions, preserved audio/rail/magazine/projectile files, and exact compiled battery art hashes. Calculated DPS/repair/rate values are not observed combat results.

Runtime NOT RUN: load/menu errors, three slots/four choices, stationary weapon elevation and flanking, modules actually activating, repair pulse selection/pending ordering, source capture/death and leaving range, stacking with existing research, factory timing, queued/captured station limits, save/reload, identical-hash multiplayer. In particular, verify research updates both existing fitted stations and newly built ones. Test a short three-player session before another long FFA. Do not mix saves across candidate versions.

Stage4 important recovery/global announcements and Stage5 interruptible ProtoTech/plating remain capability-gated and absent. No global strategic launch, free recovery reward, new exotic or shield restoration is bundled here. Separate new-hull art preparation is ongoing.
