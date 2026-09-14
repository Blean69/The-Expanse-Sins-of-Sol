# Fleet Doctrine candidate status

The confirmed three-hour user playtest used **0.19 Fleet Balance**. Later user screenshots document 0.25 research, equipment and model problems; they do not establish a multiplayer acceptance pass. Exact baseline hash/version/game/SDK records: `audit/update20/checkpoint.json`; frozen 0.25 rollback: `audit/update26/checkpoint.json`.

| Work | Status | Identifiable output / limitation |
|---|---|---|
| Existing fleet, PDC audio, ordnance, shieldless rules | Inherited | Frozen0.19 retained; no historical multiplier reapplied |
| Stage1 supply, Morrigan role, autocast/boarding guards | Modified; offline checked |0.20; use Normal Start because the later starting-fleet correction is in0.21.1 |
| Stage2 faction access, research, colony modules and local siege | Implemented; offline checked |0.21.1 asymmetric and combined sandbox; corrected Quick/Advanced starting supply |
| Stage3 battery, picket, station equipment and local research | Implemented; offline checked |0.22.1 asymmetric and combined sandbox; corrected actual constructor list; native station placeholder art disclosed |
| Stage4 important recovery and announcements | Unimplemented at synchronized operation/notification gate | Existing ordinary native derelicts and haulers preserved. No false exclusive90-second recovery or globally announced study enabled |
| Paid NPC contacts | Implemented; offline checked in0.26 | Tycho finite recovery equipment; Ceres metal and native scout intelligence; guaranteed contacts on the new Three Homes / Contacts map. Influence transactions remain untested in-game |
| Stage5 real ProtoTech, interruptible study and plating | Separate currency probe; production/lifecycle gates unresolved | Standalone0.26 Composite test uses a distinct sixth exotic and inert debit item. Regular0.26 has no resource, study, plating or shield restoration |
| Military cleanup, command ship and model polish | Implemented; offline checked in0.26 | Civilian research preserved; compact military layout and supported production; direct OPA command colony ability, enlarged hull and doubled health; Storm drive/shading, Foehammer structural base and Murphy materials |
| New hulls requested alongside doctrine | Implemented; offline checked prototypes | Murphy0.23.2; Behemoth/Gathering Storm0.24; UN One0.25; not labeled Stage4/5 |
| Urshanabi flagship | Geometry blocked | Both supposedly intact holograms are also debris. Actual reconstruction required; retained as reference/wreck donors |
| UN IPBM | Implemented; offline checked cosmetic | Truman native local bombing visual only in0.25; no actual interception/global launch |

The agent has **not run the game**. New0.26 loading, before/after research on existing and new ships, capture/ally filters, simultaneous buffs, save/reload and multiplayer remain untested.0.27 is the cumulative expansion candidate;0.26 is retained unchanged as rollback. The0.26 combined-roster currency laboratory received a user-reported receive/equip pass only. Superseded0.22.0/0.23.1 files remain unchanged, but their station constructor access was wrong; use the corrected versions.

## Capability boundary for Stages4–5

The pinned SDK's `add_notification` action admits the native planet-conversion event types, and the installed Lua examples demonstrate fixed pirate notification payloads. Neither proves arbitrary actor+actual-gravity-well messages delivered to enemies without vision. Native derelict capture points and destruction-on-capture do not prove an exclusive claimant, cancellation and exactly-once reward across capture/save/defeat. Do not substitute a global Python timer or rename a pirate alert into a claimed recovery system.

The installed event API exposes research grants and unit observations, but a verified atomic paid commitment connected to persistent lab operation, interruption and one-shot reward has not been established. An ordinary research countdown accompanied by a cosmetic lab would fail the brief. The official [March 2025 update](https://www.sinsofasolarempire2.com/article/535214/march-2025-total-subjugation-update) documents UI support for up to eight custom exotic types, superseding the earlier fixed-five concern. The standalone0.26 currency probe now makes the receive-one/save/spend-one/reject-zero check concrete, but the user has now confirmed receiving the exotic and equipping its inert test item on a capital. Save/reload and zero-balance rejection remain unconfirmed. The existing no-shields guard disables absorption/regen; an item cannot be assumed to override it safely or prevent equip/refill loops.

Detailed paths, source hashes and native examples are in `docs/foundations20/capability-and-integration.md`, `audit/update18-operations/capability-report.json` and `audit/update18-composite/capability-and-interruption-audit.json`. Earlier probes remain outside regular candidates. The new isolated currency test is documented in `docs/update26-composite-probe.md`; it is not a plating implementation or a gameplay pass.

## Short next test

Start with a fresh identical-hash three-player game, one owner per faction, using one package variant. Check ordinary openings, fit a colony module on each expeditionary capital, colonize/defend/bombard/recolonize, then construct the new defenses. Fit three station modules, attempt the fourth, compare repair with/without research on an existing station and a newly built station, move ships/factories out of range and destroy/capture the provider. Try simultaneous boarding, queued/captured structure caps, then save/reload mid-reload and mid-construction. Record actual durations, errors and outcomes before another long FFA. Long balance comparisons remain separate from these functional checks.

No installation, enabling, game launch, remote push or publication has been performed. The master brief requires separate authorization for those actions; local source commits and local candidate creation are complete within each indicated stage.

## 0.27 fleet expansion

Five paid research hulls are integrated on their assigned regular faction routes: UNN Nathan Hale/Munroe, MCRN Hephaestus, and OPA Dark Star/Laconian frigate. Gathering Storm moves to OPA and gains a connected enlarged drive/turret assembly. Behemoth receives the white cylindrical replacement with its bookmark blade removed. All prior global combat/economy/audio values are preserved. Required scenario fields, invalid fixed-axis arcs and shieldless-helper GUI assertions are repaired. Generic intermittent inplace_vector assertion remains unattributed. New gameplay, shader appearance, save/reload and multiplayer are untested in-engine; see docs/update27.md and audit/update27 acceptance records.
