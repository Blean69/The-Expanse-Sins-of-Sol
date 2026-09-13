# 0.15 shared-tree friends playtest

Supported faction: **TEC Enclave (`trader_loyalist`)**. Load this complete package alone. The two existing TEC compatibility player overlays remain; no new faction is created. Costs, construction, movement, hull statistics, weapon statistics, shield guards, old meshes and audio from0.14 are retained exactly, except the expressly requested research effects and Scirocco ability selection.

## Rollback and identity

Frozen baseline:0.14.0, source `ae747f0cfea776511a50dc55d9ba04a54b25c35f`.
ZIP SHA-256 `1826693d5fd007c751b8a4ee48eb4f09433c5526eb873e44befac090bbf3c524`.
Tree SHA-256 `758fa38ffa17fe132d786fd77d2c9445efdc782607b39e028f353a0a63b3f0b1`.
`audit/update15/checkpoint.json` records22 existing trees,22 earlier archives, source inputs and initial enabled settings. New 0.15.0 ZIP SHA-256 `6dd94b534eacdd5c9a1a9752f9a2ab4a069cf65ad3dc495cbd88e36aee7d1b7a`, tree `f43555e72ccdc14a84467242ebe0d1c6255eeac958e90e60bd94f0df99332d49`, 1,024 files. Full identity is in `audit/update15/package-summary.json`; no install or enable operation is performed by the builder. Game2.0.3(318), Steam25127248, SDK24092025 and schema pin are unchanged.

## Bounded support

Scirocco retains reactor overcharge and corvette deployment, and replaces its capture ability with **Marine Breaching Teams**. Enemy must be detected, in the same well, fully built, missing at least20% hull and within2,500. After a3-second cosmetic pod, speed falls15% and physical weapon reload duration rises15% for12seconds. Marine doctrine raises duration to13seconds. A45-second cross-player guard prevents stacking or refreshing. Cost40AM, cooldown90seconds. The pod is cosmetic and cannot be intercepted. This effect neither captures nor disables weapons/PDCs; ability-driven torpedo clocks are unaffected.

**Combat Engineering Teams** targets another friendly damaged ship within3,500. Twenty ticks of20 hull repair cap each application at400 on any ship size, no armor/shield restoration. Cost50AM, cooldown60seconds. The same effect cannot stack or refresh across players. Ownership changes terminate repair and disruption; the harmless breaching guard retains its original deadline. Existing capture implementations on other hulls remain unchanged. See worker report for exact native sources and race-condition design.

## Research and infrastructure

The13 themed names replace existing Civilian/Military node IDs and retain their prices, exotics, research time, tier, placement, prerequisites and native windfall. See `audit/update15-research/README.md` for mapping and `audit/update15/research/integration.json` for the final package's exact affected definitions and numeric expectations. Most bonuses are5%. No shield research is restored. Railgun cooldown falls5%; tracking, arcs, penetration and fast-ship counters are unchanged.

Custom action-spawned torpedo damage is bound explicitly to Compact Warhead Packages. It gains5% through research-dependent ability levels; the underlying physical missile weapon research alone does not affect these scripted impacts. All other magazine values remain identical at both levels. Existing inherited broad hull/armor upgrades can still affect torpedoes; these are recorded in the inherited-research audit, not silently removed. Existing magazine refresh/reset and airborne damage snapshots at research completion remain runtime acceptance cases.

**Orbital Missile Defense** is a local stationary installation unlocked through the existing long-range cruiser research. It retains Gauss platform construction costs/time and art. Native destructible medium missiles fire twice per8seconds,150 damage each,10,000range; the platform turns toward its target. It provides no empire-wide buff and cannot move between planets. Research damage applies through its native missile weapon. No model import is required for this mechanic.

Trade ships use the existing escort service: Morrigan at the first unlock, Tachi at the second. Both native60-second construction entries, counts and prerequisites remain. The second unlock retains its existing heavy-cruiser prerequisite and adds the heavy escort alongside the light-escort entry. Actual escort spawning, lifetime, supply and resupply behavior are native runtime checks.

## UNN Truman prototype

The TV ship is used as a scale/role reference: approximately376m, six drives and two heavy railguns. The commonly cited TV armament count is42PDCs; our eighteen visible independently tracking batteries are representative gameplay mounts, not an assertion of exact production-model placement. [TV lore reference](https://expanse.fandom.com/wiki/Truman-class_dreadnought_(TV)).

The original textured model is retained at high detail, with its actual dorsal/ventral railgun assemblies separated. Uniform scaling preserves proportions. Eighteen donor PDCs use sampled restrictive arcs and180°/s tracking versus360°/s on Martian capitals. Two3500-damage rails reload every20seconds, with20°/s yaw, ±12° arcs and1° firing tolerances. New baseline:22,000hull,6,500armor,850speed,250supply;100-second build costs4,000credits/1,000metal/700crystal, plus the same inherited capital exotics. It costs less and builds faster than the existing Martian capitals. Existing Martian statistics are unchanged.

UNN light torpedoes reuse the Martian light model, physics and durability. Each deals375damage versus750Martian, or393.75versus787.5with the new warhead research. Six launch per10seconds,36round magazine,120-second reload after the sixth volley. Four measured bow origins represent tube groups. Native TEC captain dialogue avoids inappropriate Martian allegiance lines. This first combat prototype has the torpedo passive and normal capital components; a unique UNN active-ability suite is deferred.

## Excluded experiments

No Adaptive Composite shield item or unlock is included. Its optional implementation waits for inherited shield/capture/damage tests.

`build/laboratory/update15-impactor` contains disabled investigation inputs only, with no package manifest, player entry or launcher. The candidate combines native planetary bombing with an actual destructible torpedo firing path. The pinned schema's support for both concepts does not establish that their combination works. All damage must remain tied to actual impact; no timer applies planetary damage. See `audit/update15/impactor-investigation.json`. Acceptance requires a control impact that damages one planet AND an intercepted object that causes zero planetary damage, including after lifetime expiry, save/reload and on both clients. This is untested and excluded from the friends package.

## Test status and workstation checklist

Observed offline passes: 83 schema checks, 3,210 resolved references, 36 exact research contracts, 67 preserved baseline units and 68 preserved weapon files. Truman has 306,774 assembled triangles and 3,437,424 unobstructed sampled firing rays. These samples are finite checks, not proof of complete hull occlusion or runtime performance.

Offline checks are recorded separately in `package-validation.json` and `contract-checks.json`: schema/reference resolution, exact baseline preservation, research change contracts, actual torpedo launch count, bounded support values, and compiled asset/arc audits. These are data checks, not an engine or multiplayer pass.

**All following runtime cases are NOT RUN by the builder:**

1. Fresh TEC Enclave game, Apply Changes with no errors; spawn every new/old hull, verify four Scirocco active controls and Truman textures, scale, drives, PDC/rail tracking. Repeat using saved existing ships.
2. At each relevant research node, record an already-built and newly-built ship before/after. Compare PDC damage, rail cooldown, hull/regeneration, economic/build effects and native windfall. Record existing HP treatment. Research Warheads mid-magazine and mid-reload: no free refill or reset; compare missiles launched before/after unlock and after save/reload.
3. Breach damaged enemy versus healthy, allied, hidden, out-of-range and other-well targets. Simultaneous casts from two allied players must yield one penalty and one45s guard. Repeat during guard and just after expiry. Capture before arrival and while debuffed; no hostile effect follows ownership change.
4. Repair small ship and titan: ≤400 per application, no armor/shields. Simultaneous own/allied casts must not stack or refresh. Capture recipient while repairing; repair stops. Compare pre/post damage-control research and save during repair.
5. Test existing Amun-Ra/Donnager capture, hero exclusions and titan limit. Existing shieldless hulls stay shieldless after inherited research, allied effects and captured-unit transitions.
6. Unlock both trade escorts; observe Morrigan/Tachi creation, replacement and supply handling. Build missile installation, intercept its actual missiles, verify local targeting and no remote effects.
7. Truman launches six actual375-damage rounds every10s, six volleys then120s reload. Compare Martian750damage. Test fast orbiting attackers against its restricted, slower rails/PDCs.
8. Two clients load the identical ZIP/hash and supported faction. Repeat research, simultaneous support, capture, save/rehost and escort tests. Log both clients' errors/desync evidence. No multiplayer pass is claimed until this is observed.

Rollback: keep0.14 installed separately, disable0.15, select0.14alone, and use the pre0.15save. Do not promise cross-version save compatibility.

Raw Truman component inventory and the pre-research game-definition snapshot remain local ignored audit dependencies. Their generators, hashes, integration contracts and validation results are committed; model/audio assets remain local.
