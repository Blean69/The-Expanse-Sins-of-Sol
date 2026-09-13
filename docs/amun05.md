# Amun-Ra intake and mechanics candidates

The supplied archive is `/home/haker/Downloads/Amun-Ra_Class_Stealth_Ship_[The_Expanse].zip`. The user explicitly attests permission to use it. Its original package and extracted master remain unchanged; no license from another model is substituted. Editable and generated work uses separate `amun05` paths. This study extends the active request without changing the completed Martian damage/health or the frozen installed packages.

The fourth faction is **Eidolon**, introduced with Harbinger. The developer describes real cloaking/detection systems in the [official expansion release](https://www.sinsofasolarempire2.com/article/542267/sins-of-a-solar-empire-ii-harbinger-is-available-now). Mechanics evidence comes from the installed `dlc3_herald` definitions, not from a guessed stealth flag.

## Requested behavior and interpretation

- Three independently aiming PDCs with one firing budget each. The source actually contains four complete turret hierarchies; the final three-gun derivative needs an explicit layout choice, with the fourth source assembly retained in the master.
- Six Amun-Ra ships per player is the existing-cap implementation path; the user was asked whether the intended limit instead spans every player of a faction. No faction-wide cap is claimed from a per-player limit.
- Three **individual torpedo launches**, not three multi-torpedo salvos, may remain concealed. The fourth should reveal the ship for60 seconds. Counter persistence, re-cloaking and interaction with detectors are runtime gates.
- Amun torpedoes should hit harder and travel faster than the Martian750damage/1250speed candidate, while being easier to intercept. Martian50hull/100armor/50armor-strength stays unchanged. A new private projectile class must hold Amun tuning; changing a shared Martian definition is prohibited.
- A powerful private Amun railgun must not alter the accepted Rocinante2500damage/1000penetration/10-second definition. Final Amun damage/cadence requires a controlled target test, not a claimed one-shot guarantee across all defenses.
- Boarding should make one10%ownership attempt against a valid enemy capital after the modeled pod reaches it. Ten percent is per valid boarding attempt, not per frame or per pod mesh. A flying visual alone is not proof of arrival, successful boarding or ownership transfer.

## Asset evidence

The named `Torpedo_LP.004`–`.007` subtrees provide real torpedo geometry:1,600triangles per instance, with identical local dimensions approximately1.29107×1.29107×12.67893. A separate editable extraction is being uniformly sized to the installed Javelis's16.510756game-unit length. UV/atlas dependencies stay attached. This enables a later custom appearance without altering the current Martian projectile health.

Four `Turret_Pad` hierarchies each contain pad/base/barrel-base/barrel geometry,1,230triangles per assembly. Fifteen breaching-pod subtrees are present. Several pods are displayed away from the hull; whole-scene bounds therefore must not be used as ship dimensions. Named moving parts are not proof that their pivots, axes and game animations already work.

## Verified constraint before packaging

Installed Eidolon cloak buffs use `provides_cloak`, `cloak_alpha_value`, `cloak_fade_duration_value` and product gating. Those fields are absent from the pinned buff schema. The installed examples are evidence that the engine uses them, but the current matching-schema requirement cannot be satisfied by calling an incomplete Draft7 check a pass. The pinned dependencies were not replaced or updated. Full cloak work remains a clearly labeled candidate until this discrepancy is resolved.

Do not blindly copy the stock cloak buff: its weapon-acquisition and shield behavior would change the requested defensive role. Its damage-triggered degradation also differs from a launch counter. The installed pirate king MAG missile buff provides a real `on_current_spawner_spawned_torpedo` event and filters the spawned unit by definition; that is the promising counter hook for **only** the private Amun torpedo. Exclude rail/PDC/pod events and investigate their own reveal policy explicitly. Detector-based visibility must continue to work; a scripted cloak is not unconditional invisibility.

Ownership transfer must preserve engine ownership/team/supply semantics and exclude inappropriate targets. A schema probability field alone does not establish a correct10%capture chance after pod arrival. Do not release a boarding effect that repeatedly rerolls until success, treats launch as arrival, or silently captures heroes/titans/stations when the requested target is a capital ship.

The worker evidence reports will distinguish supported candidate operators from unresolved trigger, schema, targeting and runtime behavior. No Amun-Ra game package or tested stealth/boarding behavior is claimed by this document.

## Completed candidates and precise remaining work

`audit/amun05-c/report.md` records the full inspected scene: 102,371 triangles, 382 meshes, 965 nodes, one material and four 4096² atlases, with no animation channels or skins. The central hull itself is 23,556 triangles. Moving parts are separately modeled, but there is no supplied animation rig. The extracted torpedo has verified source UVs/attributes and a maximum radius of 8.287339; matching Javelis length does not imply identical collision bounds.

Weapon candidates are in `/run/media/haker/NVME 2/expanse-workers/weapon-behavior/build/stealth05-a/combat/`. Provisional values are explicit:

| Candidate | Values |
|---|---|
| Amun torpedo | 900 damage, 1000 penetration, 1500 speed; 25 hull / 50 armor / 50 armor strength |
| Amun railgun | 3750 damage, 1000 penetration, 10-second cooldown |
| Three Amun PDCs | 28 damage / 0.25 seconds / 0 penetration each; 336 aggregate raw DPS when all bear |

These are private definitions. No old ship/weapon/projectile is rebalanced. The normal magazine retains the existing 8-round / two per 10 seconds / 120-second reload candidate pattern. None of these files is a complete ship: actual hardpoints, skin aliases, private build registration/limit and a cloak implementation remain unbound. The Martian appearance variant does **not** use these stronger/weaker Amun statistics.

Six additional definitions in sibling `probes/` provide concrete isolated experiments. The launch probe has **no cloaking behavior**: it records events from an installed Ogrov projectile so the counter can be checked on a stock hull. The fourth individual projectile starts a fixed 60-second deadline; further events during the deadline do not extend it. A private weapon tag permits successful Amun rail/PDC hits to start the same window, excluding torpedo damage. Misses are not observed, and hit-time reveal is not immediate firing-time reveal. For later Amun integration, change the probe's projectile filter to the private Amun torpedo ID.

The boarding probe uses a real installed modeled shuttle effect and the stock three-second delayed-action pattern. It rolls once using `random_chance: 0.1`, then uses `change_owner_player`. This is a **scheduled-delay experiment**, not an actual pod-collision callback or interceptable projectile. The target filter is an enemy, fully built, detected capital ship in the same well, explicitly excluding Rocinante; titans are outside the selected target type. Other mods' capital heroes need their own exclusions. Supply is checked at cast and before transfer; concurrent ownership/supply races still need testing. No damage or death-prevention effect is added. Six independent 10% attempts have about 46.9% chance of at least one success; the fleet must not be described as having a combined 10% chance.

Passed offline: 15 candidate schemas, 62 pinned schema hashes, the intended counter state model, single-roll boarding structure and preservation of all 198 files in the completed 0.4 package. The actual stock cloak's schema failures are recorded as failures separately. A Python state model does not demonstrate engine memory persistence, detector behavior, ownership transfer or multiplayer randomness.

Reproduction and exact installed references: `audit/stealth05-a/worker-report.md`, `integration-recipe.json`, `tools/stealth05_stage.py` and `tools/stealth05_combat.py`. These generators write candidates only. The integrated stealth ship remains incomplete because cloak fields are outside the pinned schema, real Amun mounts/build limits are not integrated, and boarding arrival is currently a timed visual rather than a proven physical event. No installable stealth ship was advertised or built.
