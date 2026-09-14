# 0.27.3 Menu Battle Preview

Standalone cumulative candidate over **regular 0.27.3 Load Repair**. Enable this package alone in place of 0.27.3; do not stack them. If the previous backdrop remains cached, restart the game after changing the enabled mod. The separate repair package remains available for comparison.

The main menu stages an MCRN-versus-UNN display battle:

- MCRN: Donnager, Scirocco, Hephaestus and Raptor, with two Tachi escorts crossing the foreground.
- UNN: Truman, Nathan Hale, Munroe and Murphy, with two Murphy escorts crossing the foreground.

Twelve ships replace the installed scene's twenty-eight. Existing camera, formation positions, patrol routes, opposing-player setup and 15-second wiped-side respawn logic are retained. The native backdrop's no-damage setting is retained where that API is available: this is a looping display battle, not a balance test.

Scene-only copies use the existing models, PDCs, railguns and torpedo magazines. Boarding, capture, free-ship launch and equipment access are omitted from those copies to prevent unwanted scene growth. Their mesh visibility distance is extended for the backdrop camera. The copies are absent from every faction's manufacturing and research lists; regular match units, models, balance, research, repair fixes and audio are byte-preserved from 0.27.3. No new unit tags are added.

**Offline passes:** real Lua 5.4 parse/execution with mocked existing engine APIs; distinct fleets even when both backdrop players share a race; twelve-ship initial setup; foreground movement; delayed respawn of only the wiped side; no native titan-item injection; unit/skin and ability references; unchanged original package files; ZIP integrity and hashes.

**Not observed yet:** actual menu framing, firing visuals, game performance, game-engine Lua execution and restart/cache behavior. Please confirm both fleets appear, escorts cross the foreground, weapon effects play and the menu stays responsive for a minute or two. The 0.27.3 crash repairs also still require their own runtime confirmation; the menu test does not establish save/reload or multiplayer stability.

No game launch, installation, enabled-mod change, save modification or publication was performed. Frozen 0.27.3 is retained unchanged.

Includes the 0.27.3 action-level, finite-item, role, placement and gimbal-socket repairs. The all-ships crash remains unconfirmed fixed; use the separate regular 0.27.3 control first to isolate stability from this optional scene. See the source release notes in `docs/update27_3.md`.
