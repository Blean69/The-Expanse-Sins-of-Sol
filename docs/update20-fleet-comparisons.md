# Stage1 fleet comparisons

Calculated base PDC envelopes; these are not observed combat outcomes. Range, arcs, target allocation and torpedo interception compete for the same firing budget. Railguns and torpedoes are preserved and excluded from this PDC subtotal.

| Ship | Supply | Credits / metal / crystal | Hull / armor | Durability / armor strength | PDC mounts | Raw PDC DPS/hull | DPS/supply |
|---|---:|---|---|---|---:|---:|---:|
| Morrigan | 40 | 200 / 45.5 / 0 | 600 / 550 | 150 / 50 | 2 | 176.4 | 4.410 |
| Tachi | 95 | 300 / 400 / 0 | 750 / 825 | 150 / 50 | 6 | 705.6 | 7.427 |
| Europa's Bane | 95 | 1500 / 350 / 200 | 2500 / 1500 | 250 / 75 | 6 | 510.0 | 5.368 |
| Truman | 185 | 4000 / 1000 / 700 | 16200 / 6500 | 500 / 105 | 18 | 1530.0 | 8.270 |
| Donnager | 500 | 9600 / 3770 / 1900 | 14520 / 5000 | 750 / 130 | 16 | 1881.6 | 3.763 |
| Amun-Ra | 70 | 4000 / 750 / 500 | 2400 / 1200 | 150 / 50 | 3 | 255.0 | 3.643 |
| Artemis | 8 | 600 / 100 / 50 | 900 / 400 | 50 / 25 | 0 | 0.0 | 0.000 |
| Scirocco | 200 | 5500 / 1950 / 1000 | 5400 / 3100 | 500 / 105 | 12 | 1411.2 | 7.056 |
| Pella | 200 | 6000 / 2210 / 1200 | 5400 / 3100 | 500 / 105 | 9 | 1058.4 | 5.292 |
| Raptor | 150 | 4500 / 1560 / 850 | 4500 / 2600 | 500 / 105 | 9 | 1058.4 | 7.056 |
| Rocinante | 110 | 3000 / 650 / 200 | 3000 / 1650 | 150 / 50 | 6 | 705.6 | 6.415 |
| Sunflare | 5 | 200 / 0 / 0 | 100 / 0 | 50 / 0 | 0 | 0.0 | 0.000 |

Morrigan penetration is already zero. Its private two-weapon derivative receives only the specified25% raw-DPS fallback. Every other PDC stays at its0.19 value. No class multipliers, splash, interference aura or global capital health change.

Using the [official damage model](https://www.sinsofasolarempire2.com/article/525851/the-art-of-war-update---sins-of-a-solar-empire-ii) and installed scalar0.01, exposed-hull DPS is divided by1 + max(durability - penetration,0) ×0.01. Armor-layer DPS is additionally divided by1 + armor_strength ×0.01. These are continuous layer estimates; transition/overkill/cripple details are excluded. The JSON audit lists each hull against representative targets and its isolated+5% fire-control research estimate.

## Comparison setups

Use the1x lobby fleet multiplier (2,000 endgame supply). Keep2x/4,000 as a labeled stress setting. Native trade escorts and local garrisons retain their separate special-operation accounting; they are not ordinary selectable fleet-launch discounts. Do not add a second supply charge to them.

- 500 Donnager: 1 Donnager — **500 supply**; 9600 credits / 3770 metal / 1900 crystal.
- 500 Tachi: 5 Tachi — **475 supply**; 1500 credits / 2000 metal / 0 crystal.
- 500 Morrigan: 12 Morrigan — **480 supply**; 2400 credits / 546 metal / 0 crystal.
- 500 Earth mix: 2 Truman, 3 Morrigan — **490 supply**; 8600 credits / 2136.5 metal / 1400 crystal.
- 1000 Tachi: 10 Tachi — **950 supply**; 3000 credits / 4000 metal / 0 crystal.
- 1000 Morrigan: 25 Morrigan — **1000 supply**; 5000 credits / 1137.5 metal / 0 crystal.
- 1000 mixed: 1 Donnager, 5 Tachi — **975 supply**; 11100 credits / 5770 metal / 1900 crystal.
- 2000 Tachi: 21 Tachi — **1995 supply**; 6300 credits / 8400 metal / 0 crystal.
- 2000 Morrigan: 50 Morrigan — **2000 supply**; 10000 credits / 2275 metal / 0 crystal.
- 2000 mixed: 1 Donnager, 2 Scirocco, 8 Tachi, 8 Morrigan — **1980 supply**; 24600 credits / 11234 metal / 3900 crystal.

The Donnager retains its one-titan limit: two/four-Donnager pure fleets are not legal comparison setups. All costs above exclude research and retain exotic costs listed in the JSON audit.

For equal-resource tests, use the Donnager cost as a shared ceiling in EACH resource (9,600 credits /3,770 metal /1,900 crystal), rather than claiming metal and credits are interchangeable. Under that budget, compare up to9Tachis or48Morrigans and record leftover resources and different supply. Add an equal-supply run separately; neither setup predetermines a winner.

For each force repeat: fresh vs fresh; researched vs researched; bow/stern/port/starboard and above/below approaches; target-focus and withdrawal; multiple Sciroccos repairing one damaged ally; competing boarders at30% target hull. Record actual casualties, surviving resource investment, fired/intercepted/impacting torpedoes, repair/capture use, elapsed time and escape opportunities. Save/reload during reload, repair and boarding. Repeat a short identical-hash three-player session before a longFFA.

**All outcome fields: NOT RUN.** The user reported3hours on0.19, which is preserved; this is not evidence for the new supply/autocast candidate.
