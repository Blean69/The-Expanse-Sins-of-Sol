# 0.20.0 — Fleet Doctrine, Stage 1

Separate test candidate built from frozen **0.19 Fleet Balance**. Your three-hour playtest applies to 0.19, not this candidate. All three faction identities still share the fleet in this first stage. Faction differentiation follows in a separate candidate.

Use one Expanse package at a time. Every multiplayer client needs this exact ZIP and the same lobby settings. Use **1× supply** for the supported 2,000-supply balance; 2×/4,000 is a stress test. This build does not install, enable, launch or publish anything.

## Changes

| Hull | Supply | Other change |
|---|---:|---|
| Morrigan | 40 | 88.2 base DPS per PDC, down from 117.6 |
| Tachi | 95 | 400 metal, including ordinary capital launch paths |
| Europa's Bane | 95 | Unchanged |
| Truman | 185 | Unchanged |
| Donnager | 500 | Unchanged; existing shared titan cap |
| Amun-Ra | 70 | Unchanged |
| Artemis | 8 | Unchanged |
| Raptor / Scirocco / Pella | 150 / 200 / 200 | Unchanged |
| Rocinante / Sunflare | 110 / 5 | Unchanged |

Morrigan penetration was already zero. The requested fallback reduces its damage without changing tracking, firing arcs, range or interception eligibility. Other weapon performance, magazines, projectile fuel, audio, movement, hull/armor, research and construction times are preserved. Tachi remains 300 credits and 20 seconds to build. Native automated trade escorts and local garrisons retain their separate special-operation accounting; ordinary launched Tachis use 95 fleet supply.

Scirocco targeted repair and Rocinante self-repair start with autocast enabled at 80% hull or below. Right-click to toggle. Scirocco repairs owned ships already in range, preserves its 400-point cap and non-stacking effect, and can still be cast manually for smaller losses. Rocinante's repair amount and cooldown are unchanged.

All Expanse boarding variants start with autocast disabled. Manual and automatic attempts require a hostile eligible target at 30% hull or below. A shared target buff reserves one attempt, resolves after three seconds, then retains protection until 33 seconds after launch. Capture probabilities and cooldowns are unchanged. Hero exclusions remain; the earlier Amun-Ra/Europa permission to target titans and command ships remains an explicit exception. Martian boarding targets capitals. Pods remain cosmetic effects.

## Checks and limits

Observed offline: schemas, definition references, acquisition prices, allowed changes, preserved assets/audio/research, shared lock wiring, supply arithmetic and reproducible package contents. Nominal PDC calculations are in the repository audit; they are not observed battle outcomes. Firing arcs mean all mounts will not always bear simultaneously.

**Not run:** game load, actual autocast selection, simultaneous multiplayer boarding, before/after research on existing versus new ships, capture supply accounting, save/reload, defeat transitions and comparison battles. Test a short three-player session before another long FFA. The comparison-force sheet is included.

Boarding rechecks live caster, current ownership, target hostility/health, range and available supply. Target ownership changes cancel resolution permanently. Two native capability gaps remain: a defeated player retaining a live owned caster is not independently rejected; a caster captured and recaptured within the three-second delay is checked only for its final owner. Neither edge case is claimed solved. Native same-tick pending-buff ordering also needs multiplayer verification. Interrupted attempts consume their cooldown; there is no custom refund.

Rollback: retain `expanse_update19.zip`, SHA-256 `0a809e4a4a6f9117c77338b607a65d2b3c489b37c0e49bb58dae5176efe1444e`. No original source assets or earlier package files were changed.
