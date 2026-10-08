# Expanse: Sol at War 0.29.1

A hotfix for [0.29.0](https://github.com/Blean69/The-Expanse-Sins-of-Sol/releases/tag/v0.29.0) on **Sins of a Solar Empire II 2.1.x**. It changes the unit-tag list and six ship definitions and nothing else: art, audio, balance values, research and scenarios are byte-for-byte those of 0.29.0. The owner briefly tested the installed hotfix as MCRN and reported that it looked good.

## Fixed

- **MCRN can build Morrigans again.** 0.29.0 registered 31 unit tags, one more than the game reads. Sins II rejected the whole list while loading (`size overflow. key=unit_tags expected_size=30 actual_size=31`), so the Morrigan's 18-ship limit reported itself as already reached with none built. The list is now 27 entries; the 18-ship MCRN limit is unchanged.
- The same load error stopped the game from resolving built-in tags such as `starbase` and `corvette`, so other ship limits and tag-restricted equipment could misbehave in 0.29.0. Those tags now resolve.

## What was removed to make room

Four hull-identity tags that no limit, item or modifier read: Donnager, Murphy, and the MCRN and UNN support stations. The ships themselves are unchanged. Donnager is still limited by the titan cap, and both support stations still share the one-major-station cap and its equipment.

## Updating

Replace the 0.29.0 folder with this one, enable only one Expanse package, and start a fresh game. Saves made on 0.29.0 were created with the broken tag list and are not expected to carry over cleanly.

## Known limitations

- MCRN trade-ship escorts and most garrison ships are also Morrigans. Whether the game counts those toward the 18-ship limit has not been checked in a long match; please report it if the Morrigan count rises without you building any.
- Everything listed under known limitations in the [0.29.0 notes](release-notes-v0.29.0.md) still applies.
