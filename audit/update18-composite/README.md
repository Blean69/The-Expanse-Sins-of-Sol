# ProtoTech Composite capability probe — milestone 0.18

Owner: worker C, isolated worktree `expanse-workers18/composite`. Source and installed references are read-only. This work does **not** add plating, composite production, a lab unlock, research knowledge or a mod to the playable 0.17 baseline.

## Result

A distinct exotic is structurally supported by the installed interfaces. `uniforms/exotic.uniforms` registers `{name, entity}` string pairs; `.exotic` definitions provide presentation and AI valuation. The corresponding schemas do not restrict registration to the five original names. Purchase-cost and reward references also accept string exotic IDs. Custom insufficient-resource sound slots already exist in native TEC player definitions.

This permits a genuine sixth identity, `expanse18_prototech_composite`. It does **not** prove the engine accepts, displays, persists, transfers or debits it correctly. All runtime gates remain **NOT RUN**. The native exotics HUD layout is designed around the existing entries; visibility of a sixth entry is an explicit test.

The inventory confirms no ProtoTech/plating entity exists in 0.17. The word `composite_and` in existing ability files denotes a condition expression and is unrelated to plating.

## Disabled deliverable

Run in this worktree:

```bash
python3 tools/update18_composite_probe.py --out 'build/laboratory/update18/composite/resource-probe-new'
```

The latest reviewed output is `build/laboratory/update18/composite/resource-probe-final/`. The generator refuses existing destinations and destinations outside this worker's laboratory directory. It creates no mod metadata, package, install action, enabled setting or script event registration.

Four entity fragments:

- `expanse18_prototech_composite.exotic`: the real new resource identity, with a clearly named native utility icon placeholder, independent green pip color and AI trade value 1,200.
- `expanse18_composite_probe_receive_one.research_subject`: one-time native research windfall of exactly one composite. Costs one credit and takes one second solely to exercise the currency path. It is **not** a containment study or production unlock.
- `expanse18_composite_probe_production_disabled.research_subject`: unlisted prerequisite used only to prevent optional factory-display registration from permitting fabrication. Never add this node to a test research list or grant it with a cheat.
- `expanse18_composite_probe_debit_one.unit_item`: inert defense-slot test component costing exactly one composite and one credit. No stats, abilities or shield effect. One per ship. Use another eligible empty-slot capital for the zero-balance denial test.

Integrator-owned merge fragments are under `merge/`:

- `uniforms/exotic.uniforms` contains the original five registrations unchanged plus the sixth. `overwrite_type_datas` is explicitly true; the integrator must merge any other deliberate exotic registrations rather than replacing them blindly.
- `manifest-additions.json` lists new IDs by type.
- `localization.json` provides ten strings; no vanilla resource is renamed.
- `player-fragments.json` describes test-only research/shop additions and an optional locked `buildable_exotics` display entry. This JSON is a **project merge recipe**, not an invented engine file.

The grant node reserves civilian-policy position `[1,0]`, vacant in the inspected 0.17 canonical tree. Check other milestone nodes before merging. Add the receive-one research and debit item only to explicit laboratory player wrappers. The production-disabled node is registered as an entity to resolve references but is excluded from research lists. The optional display entry remains locked. There is no starting stock, survey drop, market/contact giveaway or production trickle.

## Smallest ordered runtime test

Use a separate manually prepared laboratory package and a fresh game, with two eligible capitals and empty equipment slots. Do not run this over a valued save.

1. Open the exotics interface before receiving anything. Check that all five native exotic names/balances are unchanged and that ProtoTech Composite is independently represented. If a non-buildable resource is hidden, test the supplied locked display entry; do not substitute a different resource.
2. Purchase **LAB PROBE: receive one composite** once. Confirm the actual owner balance becomes one and other owners' balances remain zero. Research cannot be repeated normally.
3. Save/reload at balance one. Confirm the new identity and balance persist without re-granting the windfall.
4. Purchase **LAB PROBE: spend one composite** on the first capital. Confirm the native purchase consumes exactly one unit, leaving zero, and occupies one normal slot.
5. Try the same purchase on the second empty-slot capital. Confirm rejection specifically for insufficient composite, with native feedback. A denial on the already equipped first ship is not evidence: its one-copy limit would also reject the purchase.
6. Check purchase cancellation/refund, simultaneous queued purchases, capture and multiplayer owner isolation. Record whether a queued purchase reserves/debits at queue time and whether cancellation refunds once.
7. Save/reload at zero and during a queued item purchase. Check no duplicated resource, item or refund. Run on host and client with identical package hashes.

If any of these gates fails, keep production and plating disabled. Schema validation alone cannot replace them.

## Why study and plating remain gated

The installed Lua event documentation exposes per-instance state, simulation ticks, real-unit lookup, owner/location properties, cancellation/completion and `simulation:give_research`. It does not establish a paid ability/item commitment hook, an atomic debit tied to that commitment, or saved-operation deduplication. Operations worker B is probing actual object lifetime and notification reach separately. A timer attached to a cosmetic lab while ordinary empire research completes independently would violate the required interruption semantics; none is authored here.

Every eligible hull still carries `expanse11_no_shields`, which disables shield absorption, restoration and passive regeneration. Adding shield capacity as an item would therefore not produce functional plating. The installed permission definitions provide disabling mutations for these permissions, with no documented enable-override. Removing the guard globally would also expose ships without an item to inherited shields; this shortcut is not taken.

The candidate design uses fixed class-specific capacity around 12% of **unmodified base hull**, with regeneration at 1% of that capacity per second after a proposed 20-second delay. `inventory-and-shields.json` records the six eligible hulls and illustrative values. They are design calculations only. A later item must prove guard lifecycle, normal-slot eligibility, one-copy enforcement, installation/removal/capture/save behavior, no re-equipping refill, and owner-independent knowledge.

Native shield bypass/drain and shield-only damage still apply to a shield-backed layer. Whether hull damage that bypasses shields resets the intended recharge delay is untested. Native capacity/recharge/burst research, levels, auras and restoration abilities must remain audited. The baseline's removed/hidden shield research and zero burst percentages are preserved.

## Checks actually run

- PASS: five JSON schema checks against installed pinned schemas: exotic, two research subjects, unit item and exotic-uniform registration.
- PASS: original five exotic registration records preserved exactly.
- PASS: probe item has no modifiers/ability and costs one custom exotic; one-shot grant gives one of the same ID.
- PASS: eligible hull inventory finds the existing guard in every ability set; no plating entity exists in 0.17.
- PASS: Python source compilation.
- NOT RUN: game load, sixth-resource visibility, resource receipt/debit/save behavior, insufficient-resource feedback, lab interruption, plating or multiplayer.

Exact inspected sources and hashes are in `resource-probe.json` and `capability-and-interruption-audit.json`. The main integrator must continue to verify the project's pinned SDK revision and rollback hashes before packaging.
