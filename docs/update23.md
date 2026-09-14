# 0.23.2 — Murphy hull prototype

Supersedes0.23.1 by inheriting0.22.1's corrected station constructor list. Murphy combat mechanics are unchanged. Use the corrected package for testing; old files are retained.

This separate new-hull experiment follows frozen0.22 Stage3; it is **not Stage4 or Stage5**. Only UNN can manufacture the Murphy in asymmetric play. The combined sandbox exposes it to every owner. Existing fleets, defenses, economy, research, audio and ordnance remain unchanged. Retain0.22 for direct comparisons. Fresh game, one intended package only; no implicit save migration.

The supplied fan-made Murphy hull retains all8302original triangles,12162assembled with mounts and tubes. It uses authored gray/navy materials, four rotating physical PDCs with outward-only arcs, and a blue drive plume. Scale102m is a provisional RPG class reference applied to fan geometry; its single modeled nozzle differs from the RPG two-drive description. This is an explicitly approximate interpretation. See `docs/update20-asset-intake.md` for sources and `audit/update23-murphy` for actual geometry evidence.

| Property | Prototype value |
|---|---|
| Supply and price |95;1200credits/450metal/150crystal |
| Build |60seconds; native antiarmor-frigate research prerequisite |
| Endurance |1400hull,1000armor,150durability,50armor strength; shieldless |
| Movement |1350speed,25degree/s turn,5seconds acceleration; inherited corvette orbit behavior |
| PDCs |4×85rawDPS; accepted Earth tracking/range/interception profile |
| Light rails |750damage,800pierce,30second interval each; fixed fore/aft,5degree yaw,zero pitch;1.5second acquisition |
| Torpedoes |2UNN light per10seconds,8rounds,120second reload after last pair;750base damage,2125speed,30second fuel |

Fore/aft rail origins are hull-integrated approximations, with no separate modeled rotating rail guns. Their opposed arcs prevent both rails concentrating straight ahead. Rail performance is a new modest escort profile, not another rebalance of existing ships. Larger HP than Tachi is offset by four slower Earth PDCs instead of six Martian PDCs, lower torpedo damage, higher price/build time and a vulnerable150durability hull. These are design comparisons, not observed combat outcomes. No colony, siege, capture, cloak or hero limit. Generic UNN crew reused; ordinary native jump effects remain until private phase art is authored.

Offline evidence: unchanged source triangles and donor files, compiled SDK mesh/frame/tangent checks,5256outward gun samples, graph/schema/reference checks, eight-round/two-shot authored memory magazine, exact inherited research and torpedo values. Runtime NOT RUN: model/textures/scale, turret coverage, actual rail origins and aft aiming during orbit, torpedo pair/reload/save behavior, faction factories/prerequisite, combat balance, multiplayer. No automatic installation, launch or remote push.
