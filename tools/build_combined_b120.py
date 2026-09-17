"""Optional fourth selectable Combined Fleet faction over frozen B120. No install."""
from pathlib import Path
from copy import deepcopy
import json, shutil
from common import ROOT, GAME, read, write
from doctrine_package import package, registries
from validate_experiments import require, sha256, file_hashes

BASE = ROOT/'build/experiments/expanse_balance28_B120'
OUT = ROOT/'build/experiments/expanse_balance28_B120_combined4'
AUD = ROOT/'audit/balance28_combined4'
DOC = ROOT/'docs/balance28_combined4.md'
ID = 'expanse28_combined_fleet'
FACTIONS = ('mcrn','unn','opa')
MOVES = {
 'expanse27_hephaestus_procurement': [7,4],
 'expanse27_laconia_frigate_procurement': [7,5],
 'expanse28_mcrn_orbital_defense': [4,4],
 'expanse28_opa_orbital_defense': [4,5],
}

def unique(seq): return list(dict.fromkeys(seq))
def main():
    require(BASE.with_suffix('.zip').is_file(), 'Missing frozen B120')
    require(not OUT.exists() and not OUT.with_suffix('.zip').exists(), 'Combined candidate already exists')
    players = {f:read(BASE/'entities'/f'expanse18_{f}.player') for f in FACTIONS}
    merged = deepcopy(players['mcrn'])
    keys = ('buildable_units','faction_buildable_units','buildable_strikecraft','structures','ship_components','planet_components')
    for key in keys: merged[key] = unique(v for faction in FACTIONS for v in players[faction][key])
    research = merged['research']
    for key in ('research_subjects','faction_research_subjects'):
        research[key] = unique(v for faction in FACTIONS for v in players[faction]['research'][key])
    # Built-in command and titan buckets: Truman at two, titans at one.
    caps = merged['unit_limits']['global']
    cmd = [c for c in caps if c['tag']=='super_capital_ship']
    require(len(cmd)==1, 'Unexpected command cap');cmd[0]['unit_limit']=2
    gui=merged['gui']
    for key in ('race_name','race_description','faction_name','faction_short_name','faction_description'):
        gui[key]=ID+'.'+key
    gui['faction_icon']='expanse_donnager_battleship_hud_icon'
    # Distinct combined faction inherits ordinary MCRN starts and economy.
    edits={f'entities/{ID}.player':merged};origins={f'entities/{ID}.player':str(BASE/'entities/expanse18_mcrn.player')}
    pu=read(BASE/'uniforms/player.uniforms');pu['pickable_players'].append(ID);edits['uniforms/player.uniforms']=pu
    picker=read(BASE/'gui/front_end_faction_picker_dialog.gui')
    picker['faction_portraits'].append({'faction':ID,'portrait':'player_portrait_trader_2_large'})
    picker['page_definitions'].append({'name':ID+'.picker_page','factions':[ID],'layout_gui':'faction_picker_page_layout_eidolon'})
    edits['gui/front_end_faction_picker_dialog.gui']=picker
    for p in sorted((BASE/'entities').glob('*start_mode.start_mode')):
        d=read(p);m=next(c for c in d['faction_configurations'] if c['player_definition_id']=='expanse18_mcrn')
        clone=deepcopy(m);clone['player_definition_id']=ID;d['faction_configurations'].append(clone)
        edits['entities/'+p.name]=d
    orbital=read(BASE/'entities/trader_orbital_cannon_structure.unit')
    template=next(row for row in orbital['abilities'] if row.get('required_player')=='expanse18_mcrn')
    row=deepcopy(template);row['required_player']=ID;orbital['abilities'].append(row)
    edits['entities/trader_orbital_cannon_structure.unit']=orbital
    # Relocate only four icon coordinates. All effects, costs and prereqs stay intact.
    for subject,coord in MOVES.items():
        rel=f'entities/{subject}.research_subject';d=read(BASE/rel);d['field_coord']=coord;edits[rel]=d
    loc=read(BASE/'localized_text/en.localized_text')
    loc.update({ID+'.race_name':'Combined Fleet',ID+'.race_description':'Martian, United Nations and Belt procurement under one TEC logistics framework.',ID+'.faction_name':'Combined Fleet Sandbox',ID+'.faction_short_name':'Combined Fleet',ID+'.faction_description':'Sandbox faction with the B120 fleet balance and access to the MCRN, UNN and OPA ship and research rosters. Uses the Martian starting fleet and one shared titan slot.',ID+'.picker_page':'COMBINED FLEET'})
    edits['localized_text/en.localized_text']=loc
    meta=read(BASE/'.mod_meta_data');meta.update(display_name='The Expanse — B120 Combined Fleet Fourth Faction',display_version='0.28-B120-C4',short_description='B120 combat candidate plus a fourth Combined Fleet sandbox faction.',long_description='Standalone B120 candidate. Adds a fourth TEC-derived faction with the union of MCRN, UNN and OPA ship, structure, component and research access. Existing three factions and combat values retained. Four shared technology icons are relocated to remove combined-tree overlap. Runtime not tested; fresh game recommended.')
    edits['.mod_meta_data']=meta
    # Every listed hull and research subject has a reachable prerequisite branch.
    tech=set(research['research_subjects'])
    def entity(name,kind):
        rel=f'entities/{name}.{kind}'
        return edits.get(rel) or read(BASE/rel if (BASE/rel).exists() else GAME/rel)
    for n in merged['buildable_units']:
        branches=entity(n,'unit').get('build',{}).get('prerequisites',[])
        require(not branches or any(set(b)<=tech for b in branches), 'Unreachable hull '+n)
    for n in tech:
        branches=entity(n,'research_subject').get('prerequisites',[])
        require(not branches or any(set(b)<=tech for b in branches), 'Unreachable research '+n)
    spots={}
    for n in tech:
        d=entity(n,'research_subject');key=(d.get('domain'),d.get('field'),d.get('tier'),tuple(d.get('field_coord',[])))
        require(key not in spots,'Overlapping combined research icons: '+n+' / '+spots.get(key,''));spots[key]=n
    # The three existing player definitions must remain byte-identical.
    source_hashes={p.name:sha256(p) for p in (BASE/'entities').glob('expanse18_*.player')}
    DOC.write_text('# B120 Combined Fleet fourth faction\n\nStandalone experiment over the frozen B120 combat candidate. Adds one selectable TEC-derived Combined Fleet faction with all 24 distinct buildable ships and all 216 research subjects from the three playable factions. It also exposes the union of their structures and equipment. The faction uses the existing Martian start and economy. Truman uses the native two-command limit; Donnager and Behemoth share the original one-titan limit. Four research icon positions change globally so the combined tree has no overlap; their costs, prerequisites and effects are identical to B120. All other faction player files, combat definitions, audio, art and menu scene remain unchanged.\n\nOffline checks verify JSON schemas, references, the 24 hull prerequisites, 216 research prerequisite branches, unique tree coordinates, all four starting-mode configurations and archive integrity. Runtime loading, UI layout, construction, research progression, save/reload and multiplayer have **NOT RUN**. Install or enable only after you choose to test it; use a fresh game. The original B120 ZIP is retained as rollback.\n')
    shutil.copytree(BASE,OUT,symlinks=True)
    for rel,d in edits.items(): write(OUT/rel,d)
    registries(OUT);shutil.copy2(DOC,OUT/'PLAYTEST-README.md')
    for name,h in source_hashes.items():require(sha256(OUT/'entities'/name)==h,'Original faction changed '+name)
    report=package(BASE,OUT,edits,origins,DOC,AUD,package_existing=True)
    write(AUD/'scope.json',{'base_sha256':sha256(BASE.with_suffix('.zip')),'combined_faction':ID,'ships':merged['buildable_units'],'research_subject_count':len(tech),'structures':len(merged['structures']),'ship_components':len(merged['ship_components']),'planet_components':len(merged['planet_components']),'relocated_icons':MOVES,'original_factions_byte_identical':True,'runtime':'NOT RUN','package':report})
    print(json.dumps(report))
if __name__=='__main__':main()
