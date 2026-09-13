# Final bounded review — passive ammo variant and hero tag registration

Read-only review of main `build/experiments/expanse_corvette_ammo03`, Worker A `build/combat03-a/persistent`, and the hero unit-tag candidate. No main/package/installed files were edited. Results and package hash are in `ammo-final-review.json`.

## Package and typed references

PASS: the ordinary unit differs from the timed 0.3 unit only by replacing its ability list with `expanse03_torpedo_magazine`. There is exactly one passive ability/buff/ADS set; the timed-cycle files and active launch actions are absent. The six working PDC definitions remain byte-identical. Buff/ADS/projectile JSON agrees with Worker A's candidate, and main's ability positions match the reviewed two launch apertures. Three changed definitions validate against pinned schemas; scalar values, float/unit memory variable IDs and target filter IDs resolve. `common_simulation_time_value` resolves through installed `uniforms/action.uniforms/common_action_values` with transform_type `simulation_time`. The inherited vanilla projectile skin and mesh dependencies resolve. ZIP contents match the package directory.

## Sequence review

Under the assumed immediate, ordered action evaluation, the sequence is coherent:

1. On first buff start: ammo 8; pair/reload deadlines zero.
2. Every 0.25s: refill only when empty and reload deadline reached; clear selected target.
3. If at least two rounds remain, pair deadline elapsed, fully built and weapon/missile permissions hold: select at most one nearest eligible detected same-well enemy within the authored radius.
4. Run two separate torpedo creates from sequential aperture positions, with selection/permission/ammo checks repeated. Ammo is still unchanged between these creates.
5. Subtract two once, advance pair deadline by 10s, and set reload deadline to now+120s only if the debit leaves zero.

The selected-target memory is cleared before every scan. Thus the later target-guarded deadline actions cannot keep extending reload during an empty-magazine poll: no selection occurs while ammo is zero. No target means no debit or new deadline. Continuous target availability authorizes pairs at approximately 0/10/20/30s and the next pair at 150s; these are intended timings, not measured game events. No definite arithmetic or duplicate-budget defect was found.

## Runtime boundaries

The schema cannot establish same-poll memory visibility, selector/operator ordering, or whether `max_target_count=1` is applied before or after `operators_constraint`. No installed exact combination of radius action + nearest sorting + target count + operator constraint was found in the bounded search. Test with a friendly ship closer than the nearest hostile ship to detect incorrect early limiting.

The two creates and subsequent debit do not receive an explicit creation-success result. A creation failure or state change between actions could consume ammunition without two projectiles. Source lifetime during death/disable/capture, permissions during phase travel, and buff memory/simulation-clock restoration across save/reload remain essential tests. In particular `only_if_owner_unit_operational:false` preserves the passive lifecycle; explicit firing permissions must be observed to stop launches when appropriate.

This variant autonomously selects the nearest detected eligible enemy; it does not follow the manual attack target, preserve the active ability's high/low-priority targeting, or prove torpedo standoff. Those differences are reflected in the package description. The Python state model is design evidence only.

## Hero unit-tag registration

The final inspected candidate now explicitly contains `overwrite_unit_tags:true`. Its unit_tags list preserves all 14 installed entries and appends exactly the private hero tag; item_access_tags are unchanged. The added localized-name key resolves. Matching unit-tag schema validation passes.

The pinned schema exposes overwrite_unit_tags as an optional boolean but documents neither its default nor detailed merge semantics. No explicit use of that flag or unit_tag mod example was found in the installed SDK examples. Therefore this review cannot assert that omission definitely fails or claim loader behavior was observed. For a full-list candidate, explicit true expresses the intended replacement while preserving the base entries, avoiding reliance on an undocumented default. Native tag loading and one-per-player limit behavior remain runtime checks, especially simultaneous factory queues, death/rebuild and capture.

All checks above are offline. No game test was run or marked passed.
