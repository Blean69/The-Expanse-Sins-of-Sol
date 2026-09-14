# Fleet Doctrine candidate status

The confirmed three-hour user playtest used **0.19 Fleet Balance**. It is evidence for that package only, not later source inspections or generated candidates. Exact baseline hash/version/game/SDK records: `audit/update20/checkpoint.json`. No new runtime result is recorded.

| Work | Status | Identifiable output / limitation |
|---|---|---|
| Existing fleet, PDC audio, ordnance, shieldless rules | Inherited | Frozen0.19 retained; no historical multiplier reapplied |
| Stage1 supply, Morrigan role, autocast/boarding guards | Modified; offline checked |0.20; use Normal Start because the later starting-fleet correction is in0.21.1 |
| Stage2 faction access, research, colony modules and local siege | Implemented; offline checked |0.21.1 asymmetric and combined sandbox; corrected Quick/Advanced starting supply |
| Stage3 battery, picket, station equipment and local research | Implemented; offline checked |0.22.1 asymmetric and combined sandbox; corrected actual constructor list; native station placeholder art disclosed |
| Stage4 important recovery, announcements, contacts | Blocked at synchronized operation/notification gate | Existing ordinary native derelicts and haulers preserved. No false exclusive90-second recovery, globally announced study or free reward system enabled |
| Stage5 real ProtoTech, interruptible study and plating | Blocked at resource/lifecycle/runtime gates | No research promise unlock, sixth resource or conventional shield restoration added |
| New hulls requested alongside doctrine | Implemented; offline checked prototypes | Murphy0.23.2; Behemoth/Gathering Storm0.24; UN One0.25; not labeled Stage4/5 |
| Urshanabi flagship | Geometry blocked | Both supposedly intact holograms are also debris. Actual reconstruction required; retained as reference/wreck donors |
| UN IPBM | Implemented; offline checked cosmetic | Truman native local bombing visual only in0.25; no actual interception/global launch |

Every new candidate remains **runtime NOT RUN**, including loading, before/after research on existing and new ships, capture/ally filters, simultaneous buffs, save/reload and multiplayer. The baseline remains the latest user-tested build.0.22.1 is the next complete doctrine-stage candidate for testing;0.25 is the cumulative new-hull comparison option. Superseded0.22.0/0.23.1 files remain unchanged, but their station constructor access was wrong; use the corrected versions.

## Capability boundary for Stages4–5

The pinned SDK's `add_notification` action admits the native planet-conversion event types, and the installed Lua examples demonstrate fixed pirate notification payloads. Neither proves arbitrary actor+actual-gravity-well messages delivered to enemies without vision. Native derelict capture points and destruction-on-capture do not prove an exclusive claimant, cancellation and exactly-once reward across capture/save/defeat. Do not substitute a global Python timer or rename a pirate alert into a claimed recovery system.

The installed event API exposes research grants and unit observations, but a verified atomic paid commitment connected to persistent lab operation, interruption and one-shot reward has not been established. An ordinary research countdown accompanied by a cosmetic lab would fail the brief. The exotic registry accepts named data, but that does not prove a visible sixth resource, actual receive/spend/reject/save behavior. The existing no-shields guard disables absorption/regen; an item cannot be assumed to override it safely or prevent equip/refill loops.

Detailed paths, source hashes and native examples are in `docs/foundations20/capability-and-integration.md`, `audit/update18-operations/capability-report.json` and `audit/update18-composite/capability-and-interruption-audit.json`. Earlier laboratory probes remain disabled, outside these candidates. Their age does not turn them into gameplay evidence.

## Short next test

Start with a fresh identical-hash three-player game, one owner per faction, using one package variant. Check ordinary openings, fit a colony module on each expeditionary capital, colonize/defend/bombard/recolonize, then construct the new defenses. Fit three station modules, attempt the fourth, compare repair with/without research on an existing station and a newly built station, move ships/factories out of range and destroy/capture the provider. Try simultaneous boarding, queued/captured structure caps, then save/reload mid-reload and mid-construction. Record actual durations, errors and outcomes before another long FFA. Long balance comparisons remain separate from these functional checks.

No installation, enabling, game launch, remote push or publication has been performed. The master brief requires separate authorization for those actions; local source commits and local candidate creation are complete within each indicated stage.
