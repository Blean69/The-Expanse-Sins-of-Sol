# Amun-Ra integration follow-up

The user accepts the working custom torpedo, corrected Rocinante, independent tracking and current unique-hero performance. Keep the accepted92,067-triangle hero and all Martian combat values unchanged. The enabled-mod file now contains only `expanse_rocinante04_amun`; new outputs must preserve this installed baseline and remain separately testable.

The user also accepts the timed boarding visual. The implementation therefore uses one scheduled arrival attempt with a modeled visual and a10%capture roll, rather than claiming a damageable pod or collision callback. Actual target/caster loss, supply and ownership behavior still need runtime tests.

This follow-up integrates the actual Amun hull, three PDCs, private rail/torpedoes, build registration and a six-unit limit. Until clarified otherwise, the existing engine limit is interpreted as **six per player empire**, not a shared pool across different players choosing the same faction. Shared-Cobalt scope, existing hero cap and existing faction data remain unchanged except the minimal addition of the new ship/limit.

Source files, archived packages, installed game and pinned schemas remain read-only. No push or game launch is part of this assignment. Workers retain separate worktrees and new `amun06` output directories. Main owns final definitions, manifests, player edits and package integration; A owns behavior candidates, B geometry and C UI/validation support.

The61.5m Amun /46m Corvette scale convention is provisional secondary evidence from the [ship-size reference table](https://www.st-minutiae.com/resources/comparison/references.html), which cites the Expanse community wiki. The wiki could not be fetched this session. Use uniform relative scaling from the actual central hull, excluding detached posed pods/torpedoes. This is not a primary-verified canonical dimension.

The pinned official schemas still lack some installed Eidolon cloak fields. No download, replacement or silent schema relaxation is authorized by this follow-up. Any supplemental observed-field check must be clearly distinguished from official-schema validation; it cannot be presented as a matching official schema. Release scope depends on that evidence and the complete package checks.

## Separate packages and proposed values

`build/experiments/expanse_amun06` is the combined combat/boarding test. `expanse_amun06_cloak` is the optional combined cloak experiment. Each includes the accepted Corvette and Rocinante: load **one package alone**, never stack these with the old combined package or each other. These new outputs are not installed/enabled by this task. Use a disposable fresh save for each variant. Existing shared-Cobalt replacements still affect applicable neutral/garrison users of that definition; no build-menu or faction redesign was performed.

The Amun is appended to the three existing TEC player definitions, preserving every other field and the Rocinante's one-unit limit. Its private tag imposes six per player. Initial local values are 2,400 hull, 1,200 armor, inherited 150 durability/50 armor strength and shield behavior, 40 supply, 90-second build, 4,000 credits/750 metal/500 crystal. These are provisional ship-specific values, not measured balance results. Accepted corvette orbiting/navigation remains inherited.

| System | Candidate behavior |
|---|---|
| Three PDCs | 28 damage every0.25s, zero penetration,2,500 range:112 raw DPS each,336 only if all bear; one shared anti-ship/interception budget per gun |
| Amun railgun |3,750 damage,1,000 penetration,10s cooldown; fixed forward mount |
| Amun torpedo |900 damage,1,000 penetration,1,500 speed;25 hull/50 armor/50 armor strength; same-well range |
| Magazine |Two every10s, eight total,120s reload after empty |
| Boarding |Manual6,000 range,180s cooldown, modeled3s delay and one10% capture attempt; enemy detected built capitals, target supply checked at cast and transfer; excludes this mod's hero |

The source has four PDC assemblies. The derivative selects three and keeps their fixed supports, with measured yaw/pitch parts; it does not claim this selection is independently verified TV canon. Ship27,526 triangles; separate pod4,481. No hero optimization was repeated. New portraits/icons depict this actual selected ship.

## Optional cloak evidence and limitations

The optional variant preserves the stock `dlc_Herald` entitlement gate. Four individual torpedo launches trigger a fixed60-second reveal, so the fourth normally occurs during the second two-missile pair. Tagged PDC/rail **hits** also reveal. Misses do not reveal because a verified generic weapon-fired event was not established. More fire during the active window is configured not to extend it. Detectors can still expose the ship; no guaranteed invisibility is claimed.

The permanent controller owns the counter/reveal timer independently of manual cloak toggles. Event ordering, buff parenting, toggles, save serialization and visibility restoration are runtime uncertainties. The exact installed cloak fields and native unit hook are checked separately from the unchanged pinned official schemas. The inherited Cobalt `corruption` object is another preexisting pin gap: require exact equality with installed Cobalt and resolve its three penalty buffs. No fields are silently accepted through a blanket unknown-key exception. This is partial official coverage plus strict supplemental checks, never a full official cloak-schema pass.

## Build and load

Run from `/run/media/haker/NVME 2/expanse-mod`. Required ignored dependencies are the accepted0.4.1 package, A's final-reviewed behavior directory, B's completed Amun geometry/material directory, and C's actual-model UI. Missing directories or non-PASS handoffs stop the build; they are not substitutes or skipped passes. Do not update the SDK to make these commands pass.

```bash
python3 tools/build_amun06.py \
 --game '/run/media/haker/NVME 2/SteamLibrary/steamapps/common/Sins2' \
 --sdk '/run/media/haker/NVME 2/SteamLibrary/steamapps/common/Sins of a Solar Empire II - Mod Tools' \
 --behavior '/run/media/haker/NVME 2/expanse-workers/weapon-behavior/build/amun06-a/final-reviewed' \
 --geometry '/run/media/haker/NVME 2/expanse-workers/tachi-one-pdc' \
 --ui '/run/media/haker/NVME 2/expanse-workers/validation/build/amun06-c/ui'
python3 tools/build_amun06_cloak.py \
 --game '/run/media/haker/NVME 2/SteamLibrary/steamapps/common/Sins2' \
 --sdk '/run/media/haker/NVME 2/SteamLibrary/steamapps/common/Sins of a Solar Empire II - Mod Tools' \
 --behavior '/run/media/haker/NVME 2/expanse-workers/weapon-behavior/build/amun06-a/final-reviewed'
```

Builders refuse existing output directories. Add `--validate-only` to check already assembled outputs. They preserve the current checkpoint's installed trees, enabled settings, archived packages and62 pinned schemas. Separate `.provenance.json` and `.dependencies.json` sidecars identify the source commit, dirty source digest, ignored dependency hashes and ZIP hash. Source is intentionally uncommitted; HEAD alone is insufficient to reproduce it. Original behavior/geometry/UI generation commands are in the worker reports under `audit/amun06-a`, `audit/amun06-b` and `audit/amun06-c`.

When testing at the workstation, close the game, create a fresh folder named for the selected mod ID under the existing Proton `sins2/mods`, and extract that ZIP's contents there so `.mod_meta_data` is at its root. Enable just that variant and apply changes. Keep the old installed folders for rollback. The core fallback needs no cloak entitlement; the cloak variant retains the installed Harbinger requirement. No download, install, enable, publish or game launch was performed by these build commands.
