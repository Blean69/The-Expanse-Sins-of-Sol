# Update26: enlarged OPA command cruiser

Private derivative of the frozen `expanse_update25` package. This fragment upgrades
`expanse21_opa_command`; regular Europa’s Bane definitions, models and materials are
untouched. Main owns final player menus, registries, localization and packaging.

## Delivered changes

- Uniform visual scale **1.361384581046304**: length **456.521728515625** game units,
  equal to the accepted Scirocco bounding-box length. Regular Europa remains
  **335.33634424209594** units. This is a gameplay command refit, not a new lore
  assertion about Europa’s actual length.
- Retains all **100,867 hull triangles**, plus **138 base + 539 barrel triangles**
  per PDC; six assembled guns total **104,929 triangles**. No decimation or
  subdivision; source UVs, colors and PBR maps remain intact.
- Private hull, PDC base/barrel and exhaust aliases. Positions, turret offsets,
  child attachments, boarding/colony launch points, torpedo launch positions and
  bombardment muzzles scale together. Native MeshBuilder rebuilt facing grids.
- Base **5,000 hull / 3,000 armor**, twice regular Europa’s Bane. Existing command
  level progression is retained by doubling each existing level's hull/armor.
  Durability, armor strength, regeneration, movement and shieldless baseline stay
  unchanged.
- Price **4,800 credits / 975 metal / 600 crystal**, +50% over the command ship.
  **100-second construction and 150 supply** stay unchanged.
- Direct native **Colonize** on the ordinary ability bar. Reuses the already
  shipped `expanse21_opa_command_colony_module.ability` and ADS without changes:
  120 antimatter, 120-second cooldown, 5,000 range, native colony shuttle and
  existing planet-development grant. No new capture or colony action program.
- Existing repair, guarded boarding, PDC damage/targeting/arcs and magazine combat
  behavior remain exact. The magazine has a private ability/buff/ADS derivation
  solely so its launch positions can scale; its timing, damage, speed, fuel,
  capacity, filters, research progression and buff-memory logic match the source.

## Integration contract

Run `tools/update26_command_gameplay.py:changes(base)` to obtain
`(edits, localization, origins, report)`. Eleven entity edits consist of the
existing command unit/skin, six private PDC definitions and three private magazine
files. Copy the nineteen private art files listed by `report.art_files`; each hash
is recorded in `audit/update26-command/art-contract.json`. Reuse existing source
DDS aliases; their hashes are recorded as dependencies, not copied or rewritten.

Remove `expanse21_opa_command_colony_module` from **every player’s purchasable ship
components** and recommendations. The command's own recommendation is removed
in this fragment. **Keep the ability, ADS and old item definition**: the direct
ability depends on the first two, and preserving the old item definition avoids
breaking saved references. The only colony ability appended is the existing ID.
Fresh builds have one direct acquisition path. A saved ship already carrying the
old fitted item may retain that previous path; do not claim migration behavior
has been tested.

No player, research, registry or final localization files were edited here.

## Checks and evidence

`audit/update26-command/validation.json` records eleven inherited-schema checks,
complete ability/buff/projectile/effect references, typed action-value resolution,
exact source-preservation comparisons, numeric contracts, all weapon attachment
names, and colony/boarding launch-point existence. The art contract records exact
source triangle counts, attribute error, matching meshpoint rotations/translations,
fresh official facing grids, tangent-only postcompile repair and texture aliases.

The old shared action validators treated native filter strings and lists
inconsistently. The direct native colonize action uses
`uniforms_colonizable_planets` in a list, which is declared in installed
`uniforms/target_filter.uniforms`. The private validator extends only its local
check scope with actual `resolver.filters` IDs. It does not invent gameplay keys
or bypass unknown filter errors. Main was notified to fix both shared validators.

Offline previews:

- `build/update26-command/command-scale-comparison.png`: shared-camera comparison;
  Europa left, enlarged command center, Scirocco right. Hulls only for scale.
- `build/update26-command/command-oblique.png`: assembled command and six PDCs.

The preview renderer uses downsampled color maps and double-sided rasterization;
these images are not evidence of in-engine culling, materials, plume brightness,
tracking or firing. Native mesh winding is checked separately. Game loading,
command-bar placement, actual colonization, inherited-save item handling,
save/reload and multiplayer are **not run**. No installation or publication.

## Rebuild

Use the existing project Python runtime to run, in order:

1. `tools/update26_command_art.py` (pinned local SDK MeshBuilder under Wine).
2. `tools/update26_command_gameplay.py` (private overlay and merge contracts).
3. `tools/update26_command_validate.py` (private read-only-baseline view).

Art generation uses accepted compiled meshes as its pinned source, not ignored
original glTF paths. Its native compiler wrapper is the existing
`update24_behemoth_compile.py`; common import/export helpers are pinned by the
project. No additional modeling packages or external downloads are needed.
