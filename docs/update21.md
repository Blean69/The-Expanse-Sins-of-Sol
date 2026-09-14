# 0.21.1 — Three Powers / Combined Fleet Sandbox

Stage 2 is a separate candidate over frozen 0.20 Stage 1. Choose **expanse_update21** for asymmetric UNN/MCRN/OPA access, or **expanse_update21_sandbox** for the combined fleet. Do not enable both. The sandbox is a testing configuration, not a fourth faction. Use identical ZIPs on every client, one Expanse version at a time, and 1× supply. Nothing is installed or launched automatically.

Quick Start now grants six patrols and two scouts: exactly 250 supply. Advanced Start reduces home patrols to ten and patrols on each granted planet to two, keeping the maximum starting fleet within its 1,000-supply cap. Normal Start is unchanged. These adjustments apply to both candidate configurations.

## Factions and expansion

- MCRN manufactures Morrigan, Tachi, Raptor, Scirocco and Donnager, with shared scout/support options.
- UNN manufactures Truman and Contract Patrol Frigates; Black-Budget Procurement unlocks the existing six-limited Amun-Ra at full price and 70 supply.
- OPA has Contract Patrol Frigates, Europa's Bane, Artemis, Rocinante and a new repeatable Expeditionary Command Ship. Diverted Martian Surplus unlocks the unique Pella at full prices and 200 supply.

Transitional TEC escort/support hulls remain available to cover scouting, basic colonization, repair, trade and orbital construction. Contract Patrol is an explicitly mod-original shared Earth/Belt placeholder with Morrigan exterior, two 85-DPS PDCs and surplus light torpedo equipment. It is not a canonical class. UNN/OPA automated trade escorts and quick-start patrols use disclosed transitional ships rather than secretly producing ordinary MCRN Tachis. Foreign ships retain their fitted abilities; a purchased Pella's Tachi launch still pays 300 credits, 400 metal and 95 ordinary supply. Capturing foreign ships grants no manufacturer's research tree.

OPA Expeditionary Command is a separate 150-supply capital using Europa's exterior. It costs 3,200 credits / 650 metal / 400 crystal and takes 100 seconds. Level 1 retains Europa's 2,500 hull / 1,500 armor / 250 durability, with modest 3% hull/armor growth per level. It adds capital progression, four equipment slots, repair support and siege stores; no railgun or cloak. The existing 95-supply Europa frigate is unchanged.

Pella uses the native cruiser **production kind at capital yards**, while keeping capital combat classification, progression and capital menu grouping. This is a paid procurement adapter: the native first-free-capital entitlement cannot make Pella free. Exact menu placement needs runtime confirmation. Ordinary colony capitals retain the native first-free-capital opening.

Scirocco, Truman and OPA Command can fit an **Expeditionary Colony Module** immediately without battle experience. It occupies one component slot, costs 475 credits / 75 metal / 75 crystal and takes 20 base seconds (200 away from a shop under native rules). It uses native Akkan colonization: 120 antimatter, 120-second cooldown, 5,000 range, normal planet prerequisites and initial +1 commerce/+1 logistics. It cannot seize a living colony. Existing active ship abilities remain in place. The ordinary cheap colony frigate remains available to every faction.

Tachi, Rocinante, Scirocco, Truman, Donnager and OPA Command receive native local siege stores: 75 planetary damage and 3 population damage per 15 seconds at 4,000 range. These require an explicit hostile planet order. They are **separate siege ammunition**, not a shared anti-ship magazine, and their visual projectile is not interceptable. Ship-to-ship torpedo damage, speed, fuel and magazine definitions remain unchanged. No global planetary attack or map deletion is added.

## Research

Fourteen functional specialty nodes are added with native tier/cost patterns. Common existing research remains. Effects use each owner's research state; existing/new ship and captured-ship behavior still needs runtime testing.

| Owner | Specialty | Effect |
|---|---|---|
| MCRN | Terraforming Directorate Bonds | Paid developed-colony module; +10% local commerce |
| MCRN | Closed-Loop Habitat Engineering | 10% shorter civilian colony development-track build times; no ship-production change |
| MCRN | Precision Manufacturing | 10% ordinary-resource discount on two selected component variants; excludes normal counterparts |
| MCRN | MMC Assault Certification | Trained Scirocco disruption increases from 13 to 14 seconds; no capture-chance increase |
| MCRN | Redundant Command Systems | Paid capital component; +15% antimatter capacity only |
| UNN | Lunar Procurement Offices | Paid developed-colony module; +10% local production rate |
| UNN | Emergency Appropriations | Paid office; 300/100/50 activation cost, +20% local production rate for 30 seconds, 180-second cooldown |
| UNN | Civilian Shipping Requisition | +5% ordinary trade income; no free combat ship |
| UNN | Fleet Train Organization | Paid component; targeted repair, 200 hull cap, 2,000 range, 50 antimatter, 60-second cooldown |
| UNN | Black-Budget Procurement | Paid Amun-Ra construction access |
| OPA | Volatile Recovery Cooperatives | +15% orbital extractor income; no salvage/market multiplier |
| OPA | Spin-Habitat Construction | 10% shorter logistics-track development on asteroid/ice-asteroid colonies |
| OPA | Override-Code Libraries | Compatible guarded boarding range +5%, 6,000 to 6,300; chance and protection unchanged |
| OPA | Diverted Martian Surplus | Paid unique Pella access |

Local procurement and mobilization offices are mutually exclusive. Fleet Train shares Scirocco's repair exclusion. Naval Readiness, Orbital Defense Command, Dockworker Damage Control and Salvage Arbitration are absent until their station/salvage mechanics arrive. Optional signature abilities are also deferred; no extra blanket combat buff is inserted.

## Verification and next test

Offline checks cover schemas, references, private eligibility tags, six real launch frames, owner-specific availability, prices, unchanged audio and anti-ship magazines/rails. The installed `bombing_damage` field is preserved despite being absent from the older pinned schema.

**NOT RUN:** load/menu layout, module-granted colony commands, colony prerequisites/initialization, explicit siege/stop orders, owner/diplomacy transitions, before/after research on existing and new ships, local stacking, capture, save/reload and multiplayer. The Stage 1 boarding edge-case limitations still apply. Start a short three-player match with all three factions before a long FFA.

The existing small Sol — Three Homes map is retained. No full Sol rebuild, new strategic weapon, advanced contested salvage, ProtoTech resource or shield plating is included. 0.19 and 0.20 remain separate rollback packages.
