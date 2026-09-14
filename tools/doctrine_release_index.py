"""Index existing frozen outputs; never rebuilds or mutates a candidate."""
from pathlib import Path
from validate_experiments import read,sha256,require
from update20_fleet import ROOT

def build():
    rows=[]
    for version in ['19','20','21','22_1','23_2','24','25','26','27']:
        for suffix in ['', '_sandbox']:
            folder=ROOT/'build/experiments'/f'expanse_update{version}{suffix}';z=folder.with_suffix('.zip')
            if not folder.exists() or not z.exists():continue
            meta=read(folder/'.mod_meta_data');digest=sha256(z)
            sidecar=folder.with_suffix('.sha256')
            if sidecar.exists():require(digest==sidecar.read_text().split()[0],'Frozen ZIP checksum drift')
            evidence='User reported 3-hour playtest' if version=='19' else ('User screenshots: menu/art issues; multiplayer unverified' if version=='25' else 'NOT RUN')
            rows.append({'version':meta['display_version'],'name':meta['display_name'],'file':z.name,'sha256':digest,'runtime':evidence})
    text=['# Fleet Doctrine — ordered local candidates','',
      'The confirmed three-hour session used **0.19 Fleet Balance**. Later user screenshots document0.25 menu/art problems; they are not multiplayer acceptance evidence.0.27 is the cumulative fleet expansion candidate, with0.26 retained as rollback. The user confirmed receiving and equipping the separate0.26 currency-probe item; save/reload and zero-balance rejection remain unconfirmed. All original packages are retained; each ZIP is standalone. Use one variant in a fresh game.','',
      'Test order:0.20 Stage1 (Normal Start only);0.21.1 Stage2 faction/colony/research;0.22.1 Stage3 defenses.0.23.2+ are separate new-hull prototypes over those foundations, not claims that Stage4/5 is implemented. The combined sandbox grants the full roster for comparisons; asymmetric variants enforce manufacturer/faction access.0.22.0 and0.23.1 are retained but superseded because of the corrected constructor list.','',
      '| Version / candidate | Package | Runtime evidence |','|---|---|---|']
    for r in rows:text.append(f"| {r['version']} — {r['name']} | [{r['file']}]({r['file']}) | {r['runtime']} |")
    text+=['','## SHA-256','']
    text+=['- `'+r['sha256']+'` — '+r['file'] for r in rows]
    text+=['','## First test','',
      'Use identical hashes for a short three-player session before another long FFA. Check load, ordinary faction opening, existing/new research behavior, capital colony modules, local siege, station equipment and source-loss/capture cleanup, then save/reload during a reload or construction. Compare new hulls separately. Record actual elapsed time/errors/casualties; offline checks are not combat results.','',
      '0.27 adds five faction-specific hulls and replaces Behemoth art, moves Gathering Storm to OPA and repairs three diagnosed log assertions. New0.27 runtime/MP NOT RUN.', '',
      '0.26 adds compact military research, direct OPA command colonization, model polish and actual paid NPC services. Use Sol — Three Homes / Contacts for guaranteed Tycho and Ceres menus. Civilian research is preserved.','',
      'Stage4 exclusive recovery/global announcements and Stage5 interruptible ProtoTech/plating remain absent at documented capability gates. IPBM visuals do not prove interception. No installation, game launch, remote push or publication was performed.','']
    probe=ROOT/'build/experiments/expanse_update26_composite_probe.zip'
    if probe.exists():
        text+=['## Separate optional currency test','',
          '[0.26 Composite currency probe](expanse_update26_composite_probe.zip) — laboratory only, enable alone. Tests receive1/save/spend1/reject0 using a distinct native exotic and an inert item; no plating. User reported receive/equip PASS; save/reload and reject-zero UNCONFIRMED. Combined roster is intentional in this laboratory.',
          '', '`'+sha256(probe)+'`', '']
    target=ROOT/'build/experiments/FLEET-DOCTRINE-CANDIDATES.md';target.write_text('\n'.join(text));return target

if __name__=='__main__':print(build())
