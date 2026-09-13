"""Integrate Gate 1 only over frozen 0.17. Never installs, enables or pushes.

Run update18_scenario.py first, then this builder. Later laboratory outputs are
deliberately absent from the package, pending the milestone's runtime gates.
"""
from pathlib import Path
import argparse, copy, json, shutil, zipfile
import jsonschema
from build_polish import write
from validate_experiments import read, require, sha256, file_hashes, tree_hash, verify_zip, verify_pins, provenance
from update18_scenario import gameplay, schema_check

ROOT=Path(__file__).resolve().parents[1]
BASE=ROOT/'build/experiments/expanse_update17'
OUT=ROOT/'build/experiments/expanse_update18'
LAB=ROOT/'build/laboratory/update18/scenario'
AUD=ROOT/'audit/update18'
GAME=ROOT.parent/'SteamLibrary/steamapps/common/Sins2'
SDK=GAME.parent/'Sins of a Solar Empire II - Mod Tools'
IDS=['expanse18_unn','expanse18_mcrn','expanse18_opa']

def source(rel):
    return BASE/rel if (BASE/rel).exists() else GAME/rel

def preservation():
    c=read(AUD/'checkpoint.json')
    require(tree_hash(file_hashes(BASE))==c['tree_sha256'],'Frozen 0.17 tree changed')
    require(sha256(BASE.with_suffix('.zip'))==c['zip_sha256'],'Frozen 0.17 ZIP changed')
    return {'baseline_tree_sha256':c['tree_sha256'],'baseline_zip_sha256':c['zip_sha256'],
            'pins':verify_pins(ROOT,GAME,SDK)}

def changes():
    f=read(LAB/'fragments/registrations.json');result={}
    for kind in ['player','unit']:
        rel=f'entities/{kind}.entity_manifest';d=read(source(rel))
        additions=f[kind+'.entity_manifest']['append_ids']
        require(not set(d['ids'])&set(additions),'Already registered '+kind)
        d['ids']+=additions;result[rel]=d
    for rel,key,fragkey in [('uniforms/player.uniforms','pickable_players','append_pickable_players'),
                            ('uniforms/scenario.uniforms','scenarios','append_scenarios')]:
        d=read(source(rel));require(not set(d[key])&set(f[rel][fragkey]),'Already registered '+key)
        d[key]+=f[rel][fragkey];result[rel]=d
    rel='gui/front_end_faction_picker_dialog.gui';require(sha256(source(rel))==f[rel]['source_sha256'],'Picker source drift')
    d=read(source(rel))
    for key in ['page_definitions','faction_portraits']:d[key]+=f[rel]['append_'+key]
    result[rel]=d
    for patch in f['shared_definition_patches']:
        rel=patch['file'];require(sha256(source(rel))==patch['source_sha256'],'Shared source drift')
        d=read(source(rel));d['abilities']+=patch['append_to_abilities'];result[rel]=d
    rel='localized_text/en.localized_text';d=read(BASE/rel)
    require(not set(d)&set(f['localizations']),'Localization collision')
    d.update(f['localizations']);result[rel]=d
    d=read(BASE/'.mod_meta_data')
    d.update(display_name='The Expanse — 0.18 SOL GATE 1',display_version='0.18.0',
        short_description='Three shared faction identities and a small fixed-home Sol test map.',
        long_description='GATE 1 CANDIDATE: full 0.17 fleet preserved. UNN, MCRN and OPA share gameplay. Sol — Three Homes: Normal start, slot 1 UNN/Earth, slot 2 MCRN/Mars, slot 3 OPA/Jovian Habitats. Load alone with the same package on every client. Offline checks pass; editor, game and multiplayer tests pending. Full Sol, Tycho, salvage and composite progression are not included.')
    result['.mod_meta_data']=d
    return result

def build():
    preservation();require(not OUT.exists() and not OUT.with_suffix('.zip').exists(),'Refusing existing 0.18 output')
    require(read(ROOT/'audit/update18-scenario/report.json')['scenario']['sha256']==sha256(LAB/'overlay/scenarios/expanse18_sol_three_homes.scenario'),'Scenario differs from reviewed output')
    shutil.copytree(BASE,OUT)
    for p in sorted((LAB/'overlay').rglob('*')):
        if p.is_file():
            dest=OUT/p.relative_to(LAB/'overlay');require(not dest.exists(),'Overlay unexpectedly overwrites baseline')
            dest.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(p,dest)
    for rel,d in changes().items():write(OUT/rel,d)
    shutil.copy2(ROOT/'docs/update18.md',OUT/'GATE-1-README.md')

def validate():
    before,after=file_hashes(BASE),file_hashes(OUT);expected=changes()
    overlay=file_hashes(LAB/'overlay');added=set(after)-set(before)
    require(set(before)<=set(after),'Deleted baseline file')
    require(added==set(overlay)|(set(expected)-set(before))|{'GATE-1-README.md'},'Unexpected new package files')
    changed=sorted(p for p,h in before.items() if after[p]!=h)
    require(set(changed)<=set(expected),'Unrelated fleet definition changed')
    for rel,d in expected.items():require(read(OUT/rel)==d,'Shared merge mismatch '+rel)
    for rel,h in overlay.items():require(after[rel]==h,'Overlay mismatch '+rel)
    require(after['GATE-1-README.md']==sha256(ROOT/'docs/update18.md'),'Handoff mismatch')
    require(not any(p.startswith(('scripts/','exotics/')) or 'expanse18_tycho' in p or 'expanse18_composite' in p or 'expanse18_prototech' in p for p in added),'Later prototype leaked into Gate 1')
    canonical=read(BASE/'entities/trader_loyalist.player');schema_rows=[]
    for ident in IDS:
        d=read(OUT/f'entities/{ident}.player')
        require(gameplay(d)==gameplay(canonical),'Gameplay parity drift '+ident)
        schema_rows.append({'file':ident+'.player','unchanged_extensions':schema_check(d,read(SDK/'json_schemas/player-schema.json'),canonical)})
        for key in ['buildable_units','structures','ship_components','planet_components','research','unit_limits','buildable_exotics']:
            require(d[key]==canonical[key],'Owner availability drift '+key)
    for rel,kind,key in [('uniforms/player.uniforms','player-uniforms','pickable_players'),('uniforms/scenario.uniforms','scenario-uniforms','scenarios')]:
        native=read(source(rel));data=read(OUT/rel);schema=read(SDK/f'json_schemas/{kind}-schema.json')
        require({k:v for k,v in data.items() if k!=key}=={k:v for k,v in native.items() if k!=key},'Unrelated uniform change')
        # Installed player.uniforms itself lacks the pinned schema's legacy
        # dlc_only_pickable_players. Do not invent that field or claim a full
        # schema pass. Validate the sole changed property, preserve all others.
        partial={'type':'object','properties':{key:schema['properties'][key]},'required':[key],'additionalProperties':False,'$defs':schema.get('$defs',{})}
        schema_check({key:data[key]},partial)
        native_errors=[{'path':list(e.path),'validator':e.validator,'message':e.message} for e in jsonschema.Draft202012Validator(schema).iter_errors(native)]
        schema_rows.append({'file':rel,'status':'PASS changed-property schema and exact unchanged installed remainder','validated_property':key,'installed_full_schema_mismatches':native_errors})
    for rel,kind,original in [('entities/expanse18_equal_home.unit','unit',GAME/'entities/terran_planet.unit'),
         ('entities/trader_orbital_cannon_structure.unit','unit',BASE/'entities/trader_orbital_cannon_structure.unit')]:
        schema_rows.append({'file':rel,'unchanged_extensions':schema_check(read(OUT/rel),read(SDK/f'json_schemas/{kind}-schema.json'),read(original))})
    frag=read(LAB/'fragments/registrations.json')['gui/front_end_faction_picker_dialog.gui']
    sp=SDK/'json_schemas/faction-picker-pages-schema.json';raw=sp.read_text()
    bad='(e.g. "capital_ships")';require(raw.count(bad)==1,'Unexpected picker schema text')
    # The installed schema has one unescaped quote in a description, not a
    # validation rule. Repair that documentation string in memory only.
    picker_schema=json.loads(raw.replace(bad,'(e.g. capital_ships)'))
    schema_check({'pages':frag['append_page_definitions'],'faction_portraits':frag['append_faction_portraits']},picker_schema)
    schema_rows.append({'file':'gui/front_end_faction_picker_dialog.gui','status':'PASS added page/portrait structures plus exact installed template remainder','schema_source_sha256':sha256(sp),'schema_note':'Installed schema line 153 has unescaped capital_ships quotes in description; removed only those two description quotes in memory, no SDK file edits or validation-rule changes'})
    for kind in ['player','unit']:
        values=read(OUT/f'entities/{kind}.entity_manifest')['ids'];require(len(values)==len(set(values)),'Duplicate manifest ID')
        for v in values:require((OUT/f'entities/{v}.{kind}').exists() or (GAME/f'entities/{v}.{kind}').exists(),'Missing manifest definition '+v)
    # All four native start modes keep their old entries and add the three exact
    # Enclave copies. This format has no entity schema in the pinned SDK.
    for p in sorted((OUT/'entities').glob('*.start_mode')):
        old=read(GAME/'entities'/p.name);d=read(p)
        native=next(x for x in old['faction_configurations'] if x['player_definition_id']=='trader_loyalist')
        require(d['faction_configurations'][:-3]==old['faction_configurations'],'Native start drift')
        for ident,x in zip(IDS,d['faction_configurations'][-3:]):
            want=copy.deepcopy(native);want['player_definition_id']=ident;require(x==want,'Unequal start')
    path=OUT/'scenarios/expanse18_sol_three_homes.scenario'
    with zipfile.ZipFile(path) as z:
        require(z.testzip() is None,'Scenario CRC')
        require(set(z.namelist())=={'galaxy_chart.json','galaxy_chart_fillings.json','scenario_info.json','picture.png'},'Unexpected scenario members')
        chart=json.loads(z.read('galaxy_chart.json'))
        schema_check(chart,read(SDK/'json_schemas/galaxy-chart-schema.json'))
    # All original combat, research, voices, textures and meshes remain exact;
    # only cannon owner-gate groups expand to support clone owners.
    return {'status':'PASS OFFLINE ONLY','gate':1,'schemas':schema_rows,
        'changed_baseline_files':changed,'new_files':sorted(added),'file_count':len(after),
        'preserved_baseline_files':len(before)-len(changed),'clone_gameplay_parity':True,
        'research_weapons_hull_stats_audio_meshes_unchanged':True,
        'review':'Independent read-only worker review found no concrete source defect; not a runtime pass',
        'runtime':{'SolarForge':'NOT RUN','game_load':'NOT RUN','home_economy_precedence':'NOT RUN','construction_victory':'NOT RUN','owner_research_limits':'NOT RUN','save_reload':'NOT RUN','multiplayer_minutes':0},
        'preservation':preservation()}

def main(a):
    if not (a.validate_only or a.package_existing):build()
    write(AUD/'package-validation.json',validate())
    if a.validate_only:print('PASS OFFLINE 0.18 Gate 1');return
    archive=OUT.with_suffix('.zip');require(not archive.exists(),'Existing 0.18 ZIP')
    with zipfile.ZipFile(archive,'w',zipfile.ZIP_DEFLATED,compresslevel=9) as z:
        for p in sorted(OUT.rglob('*')):
            if p.is_file():
                zi=zipfile.ZipInfo(p.relative_to(OUT).as_posix(),(2026,9,13,0,0,0));zi.compress_type=zipfile.ZIP_DEFLATED;zi.external_attr=0o100644<<16;z.writestr(zi,p.read_bytes())
    result={'mod_id':OUT.name,'version':'0.18.0','gate':1,**verify_zip(archive,OUT),'installed':False,'runtime':'NOT RUN'}
    write(AUD/'package-summary.json',result);OUT.with_suffix('.sha256').write_text(result['zip_sha256']+'  '+archive.name+'\n')
    deps=[BASE,LAB,ROOT/'docs/update18.md'];write(OUT.with_suffix('.dependencies.json'),list(map(str,deps)))
    write(OUT.with_suffix('.provenance.json'),provenance(archive,ROOT,deps));print(json.dumps(result,indent=2))

if __name__=='__main__':
    p=argparse.ArgumentParser();g=p.add_mutually_exclusive_group();g.add_argument('--validate-only',action='store_true');g.add_argument('--package-existing',action='store_true');main(p.parse_args())
