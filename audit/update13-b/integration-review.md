# Main update13 integration review

Read-only review of main `tools/build_update13.py` before final Scirocco handoff/build. No main files changed.

Verified:

- Applying only the audio transformation to the frozen base modifies exactly eight intended armed skins: MCRN corvette, Donnager, Morrigan, Scirocco, Pella, Raptor, Rocinante and Amun-Ra. Scout dialogue/exhaust audio is unaffected.
- All nine hard-coded unit graph roots exist in the frozen package.
- Unit changes are reconstructed from frozen base plus spatial/mount metadata. Weapon changes are reconstructed from frozen base with only turret overrides permitted; fire rate, targeting, damage and other weapon fields are equality-checked.
- Worker resource directories cannot inject entity definitions, and duplicate worker asset paths must have identical hashes.
- Material/mesh/UV changes for worker B have independent compiled checks and exact overlay hashes.
- Short audio variants use only observed sound-profile fields; lack of verified concurrency/variant-selection semantics is documented rather than reported as a runtime pass.

Concrete low-priority issue reported to main: `--validate-only` still proceeds into unconditional ZIP verification and provenance generation. It therefore fails if used on an assembled candidate before the ZIP has been created, despite completing package validation. Return after writing the validation report in this mode, or condition subsequent archive-dependent operations on archive existence.

No blocking defect identified in current scope of reviewed skin/audio/asset integration. Final Scirocco contract and combined package results were not yet available during this review; their validation is the integrator's next step.
