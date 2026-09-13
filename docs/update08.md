# Update 0.8: ability controls and six more voice lines

The user's screenshot shows only the Amun-Ra torpedo magazine. The read-only enabled-mod inspection found `expanse_amun06_voice07`, the **combat/boarding** variant; cloak is deliberately absent from that variant.

A separate integration defect explains the missing boarding control. The ship had multiple unconditional objects under `abilities`, one per ability. Installed ships place coexisting abilities in one object's inner `abilities` list. Multiple outer entries are used for alternative player/special-operation sets, as shown by the installed Novalith and Vasari fabricator. The old schema/reference checks accepted the shape and traversed all references without checking set selection. This was our configuration error, consistent with only the first set's magazine appearing.

## Correction

Update0.8 collects the Amun's abilities into one unconditional set: magazine + boarding, plus cloak controller + manual cloak in the cloak variant. The same defect was present on Rocinante; its magazine, Belter Ingenuity, torpedo salvo, Overcharged Reactor and morale passive now share one set. This can make previously unavailable abilities/passives functional: it is a behavior correction, not a balance result. Ability definitions and costs were not retuned.

A regression check rejects the original split layout for both ships and variants, accepts the corrected layout, and refuses to flatten legitimate conditional vanilla sets. Future Amun and hero source generators were corrected too; earlier generated/installed packages were not rebuilt. Historical0.6 builders now describe the corrected source and should not be used to validate the old split-set outputs; use the0.8 validation command below.

The boarding ability also gains the exact installed pirate boarding range-cursor/tooltip-picture GUI fields. Its label is **Launch boarding pod**. The cloak label is **Activate cloak**. The magazine description now describes its magazine rather than stale mount-integration work. No inventory item or consumable is required. Native cloak controls may be presented separately by the HUD; exact placement still needs a runtime check.

## Which package to test

For the user's requested stealth test, use **`expanse_amun08_cloak`**. It contains cloak, boarding, the complete existing ships, and all17 Rocinante recordings. It retains the native `dlc_Herald` product requirement and the previously documented partial official-schema coverage of installed cloak fields. The ordinary **`expanse_amun08`** package is a no-cloak fallback for isolating boarding/combat.

Both are complete mods. Close the game, extract the chosen ZIP into a fresh same-named folder under the existing Proton `sins2/mods` directory, and enable **only that combined variant**. Do not stack it with0.6/0.7 or the other0.8 variant. Start a new disposable game and construct a new ship for the first test so an old save cannot mask a changed ability set. No folder was installed, overwritten or enabled by the agent.

| Package | Files | ZIP SHA-256 |
|---|---:|---|
| `expanse_amun08_cloak` | 307 | `4db81a8044c7a75443e09981bdc23265dda56cc93bfb9c72105aff7a430cc72c` |
| `expanse_amun08` | 301 | `ae4b3d4a90841ab9f50320835427ffb54816482efc7df1b573ae74ece3e03c58` |

## Minimal workstation test

1. Build a new Amun in the cloak variant. Confirm magazine and **Launch boarding pod**, plus the cloak control. The magazine/controller are automatic/passive; their existence does not make them consumables. Check Rocinante's repair, salvo and reactor controls too; morale is passive.
2. Select **Launch boarding pod**, then an enemy detected, fully built capital ship within6,000 range, with enough free fleet supply to own the target. Verify targeting cursor, cooldown and modeled pod first. There is one **10% chance** after the fixed3-second delay;90% of valid attempts will not capture. A failed capture alone does not prove the ability is broken. Cooldown180seconds. Friendly ships, this mod's hero and non-capital targets remain excluded by the unchanged filter. The pod is an uninterceptable timed visual, not a physical boarding entity.
3. Activate cloak while not firing and inspect from an enemy viewpoint/detector context. Seeing your own ship is not sufficient evidence of enemy visibility. The fourth individual torpedo (normally the second pair) or a successful PDC/rail hit should start the existing60-second reveal. Further shots should not extend it. Gun misses are a known limitation and do not reveal. Product entitlement, event timing and controller persistence remain runtime gates.
4. Save/reload during cloak/reveal and pending boarding. Check target/caster loss, supply changes and the correct receiving owner. Do not infer capture success from the pod visual. Record screenshots of the full ability bar, enabled variant and first relevant log if controls remain absent.

No UI appearance, capture or cloak test was run by the agent. User evidence establishes the old magazine-only display; it does not establish boarding/cloak success or failure independently.

## New recordings

The six new supplied WAVs are preserved untouched. All six passed normalization and decoded Ogg checks: approximately−18 LUFS, peaks below−2.4dBTP, mono44.1kHz. Existing11 recordings and their dialogue pools are preserved, with six additions. The XO recording stays held; no missing short juice line is reconstructed.

| Recording | Category/mood | Encoded LUFS | Peak dBTP |
|---|---|---:|---:|
| `easy-there-partner.wav` | `order_issued` / `neutral` | -18.22 | -3.11 |
| `donkey-balls.wav` | `selected` / `neutral` | -18.12 | -2.43 |
| `did-you-just-say-donkey-balls.wav` | `selected` / `neutral` | -18.02 | -3.16 |
| `debris-field-buckle-up.wav` | `order_issued` / `neutral` | -18.50 | -2.64 |
| `damn-straight-do-not-lose-that-ship.wav` | `attack_order_issued` / `smug` | -18.44 | -2.76 |
| `could-you-pass-me-the-drill.wav` | `selected` / `neutral` | -17.97 | -3.39 |

The pursuit line also joins the neutral attack pool. The two donkey-balls recordings are independent selection responses, not a guaranteed sequential exchange. Debris-field dialogue is a movement acknowledgement, not a new asteroid-detection event. The drill line is selection chatter, not a new repair trigger. No missing-word reconstruction, noise separation or subjective listening pass is claimed. Voice event timing/moods still need in-game listening.

## Scope, checks and reproducibility

Main owns `tools/build_update08.py`, the small reusable voice-helper extension, source-generator group fixes, `audit/update08` and this documentation. Existing game data, SDK, archives, model masters, installed mods and earlier ZIPs remain unchanged. Fleet supply, costs, weapons, hull/armor, movement, geometry and all existing ability combat values remain byte-identical or structurally identical except the intentional ability grouping. No Donnager, economy, faction or other balance work was added.

Each variant changes only seven preceding files: metadata, credits, English text, two unit ability-set lists, Rocinante dialogue bindings and boarding GUI fields. It adds12 sound/media files. Exact diff checks, known-field unit/skin/ability schema checks, supplemental native cloak checks, references for every now-coexisting ability, the boarding graph, decoded audio metrics, old-layout regression and ZIP/tree comparisons passed. No new schema fields were invented. Inherited corruption is still checked exactly against installed Cobalt; optional cloak coverage remains explicitly partial official coverage.62 pinned schemas and527 recorded game references still match.

Original audio: `assets/original/voice08`; editable normalized WAVs: `assets/derived/voice08/normalized-wav`; generated files: `build/voice08/game/sounds`. The existing local ffmpeg pipeline is reused without dependency updates. User-supplied audio provenance and unspecified license details are recorded separately from model permissions. Nothing was published.

```bash
cd '/run/media/haker/NVME 2/expanse-mod'
# Fresh audio derivative directories only:
python3 tools/build_update08.py --normalize
# Fresh complete package directories only:
python3 tools/build_update08.py
# Check already built packages without rewriting ZIPs/installations:
python3 tools/build_update08.py --validate-only
```

The builders refuse existing destinations and fail missing ignored dependencies explicitly. External provenance sidecars record source HEAD, uncommitted source hashes, original/editable/generated dependencies and package hashes. The supplied screenshot and read-only enabled setting are supporting user/runtime evidence; no executable instructions were taken from attachments.
