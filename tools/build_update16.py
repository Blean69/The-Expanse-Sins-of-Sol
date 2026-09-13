"""Focused0.16 balance/visual patch over frozen0.15; no install or enable operations."""
from pathlib import Path
import argparse,copy,json,shutil,zipfile
from build_polish import write,cp
from validate_experiments import read,require,sha256,file_hashes,compare_tree,verify_pins,verify_zip,provenance
from build_combat04 import binary_geometry
from amun06_validate_package import AmunResolver,check_action_values
from build_combat03 import check_actions
from update11_validate import schema_check
ROOT=Path(__file__).resolve().parents[1];BASE=ROOT/'build/experiments/expanse_update15';OUT=ROOT/'build/experiments/expanse_update16';AUD=ROOT/'audit/update16'
GAME=ROOT.parent/'SteamLibrary/steamapps/common/Sins2';SDK=GAME.parent/'Sins of a Solar Empire II - Mod Tools'
MAG='expanse10_donnager_light_magazine'

def preservation():
    c=read(AUD/'checkpoint.json');trees=[compare_tree(t)for t in c['trees']]
    for p,h in {**c['zips'],**c['originals']}.items():require(sha256(p)==h,'Frozen file changed '+p)
    return {'trees':trees,'pins':verify_pins(ROOT,GAME,SDK),'enabled_settings_unchanged':sha256(c['enabled_path'])==c['enabled_sha256'],'runtime':'User is testing concurrently; builder never writes installed mods/settings.'}

def expected():
    changes={}
    for prefix,count,before,after in [('expanse15_truman',18,4500.,6000.),('expanse10_donnager',16,6000.,8000.)]:
        for i in range(count):
            rel=f'entities/{prefix}_pdc_{i}.weapon';d=read(BASE/rel);require(d['range']==before,'Unexpected starting PDC range');d['range']=after;changes[rel]=d
    for i in range(2):
        rel=f'entities/expanse15_truman_rail_{i}.weapon';d=read(BASE/rel);require(d['cooldown_duration']==20.,'Unexpected rail cadence');d['cooldown_duration']=40.;changes[rel]=d
    rel='entities/'+MAG+'.action_data_source';d=read(BASE/rel)
    values={'heavy_torpedo_torpedo_count_value':48.,'magazine_capacity_value':48.,'combat03_torpedoes_per_interval_value':12.,'magazine_pair_count_value':12.}
    for v in d['action_values']:
        if v['action_value_id']in values:v['action_value']['values']=[values[v['action_value_id']]]*2
    changes[rel]=d
    rel='entities/'+MAG+'.buff';d=read(BASE/rel);a=d['time_actions'][0]['action_group']['actions']
    require([x['action_type']for x in a[5:7]]==['use_position_operators_on_single_position']*2,'Unexpected magazine launch layout')
    # Old saves may retain2/4/6/8rounds, below the new12round volley. Enter a
    # normal reload rather than leaving that partially loaded ship stuck forever.
    partial={'constraint_type':'composite_and','constraints':[{'constraint_type':'value_comparison','value_a':'magazine_ammo_value','comparison_type':'greater_than','value_b':'fixed_zero'},{'constraint_type':'value_comparison','value_a':'magazine_ammo_value','comparison_type':'less_than','value_b':'magazine_pair_count_value'}]}
    migrate=[{'action_type':'change_buff_memory_float_value','float_variable':'reload_ready','math_operators':[{'operator_type':'assign','operand_value':'common_simulation_time_value'},{'operator_type':'add','operand_value':'magazine_reload_duration_value'}],'constraint':copy.deepcopy(partial)},{'action_type':'change_buff_memory_float_value','float_variable':'ammo','math_operators':[{'operator_type':'assign','operand_value':'fixed_zero'}],'constraint':copy.deepcopy(partial)}]
    d['time_actions'][0]['action_group']['actions']=migrate+a[:5]+copy.deepcopy(a[5:7])*6+a[7:];changes[rel]=d
    rel='localized_text/en.localized_text';d=read(BASE/rel)
    d[MAG+'.description']='Twelve Martian light torpedoes per volley, every 10 seconds while a target is available. Four volleys per 48-round magazine; reloads 120 seconds after the final volley. Existing reactor reload acceleration applies.'
    changes[rel]=d
    rel='.mod_meta_data';d=read(BASE/rel);d.update(display_name='The Expanse — 0.16 BATTLESHIP BALANCE',display_version='0.16.0',short_description='Longer heavy-ship PDC range, slower UNN railguns, twelve-round Donnager volleys and slimmer Scirocco mounts.',long_description='Load alone as TEC Enclave. Full0.15 fleet/research/audio included. Offline checks pass; new balance, research transitions, save/reload and multiplayer require in-game testing.0.15rollback retained.');changes[rel]=d
    return changes

def build():
    preservation();require(not OUT.exists() and not OUT.with_suffix('.zip').exists(),'Refusing existing0.16')
    m=read(AUD/'mount-validation.json');require(m['status']=='PASS OFFLINE','Mount candidate incomplete')
    shutil.copytree(BASE,OUT)
    for rel,d in expected().items():write(OUT/rel,d)
    for rel,p in m['resources'].items():cp(Path(p),OUT/rel)
    (OUT/'ASSET-SOURCES.md').write_text((ROOT/'ASSET-SOURCES.md').read_text())
    write(AUD/'reviewed-inputs.json',{p:sha256(p)for p in m['resources'].values()})

def walk(x):
    if isinstance(x,dict):
        yield x
        for v in x.values():yield from walk(v)
    elif isinstance(x,list):
        for v in x:yield from walk(v)

def validate():
    before,after=file_hashes(BASE),file_hashes(OUT);m=read(AUD/'mount-validation.json');edits=expected()
    allowed=set(edits)|set(m['resources'])|{'ASSET-SOURCES.md'}
    require(before.keys()==after.keys(),'Unexpected file addition/deletion')
    for p,h in before.items():require(after[p]==h or p in allowed,'Unrelated baseline change '+p)
    for p,d in edits.items():require(read(OUT/p)==d,'Unexpected gameplay/UI delta '+p)
    for rel,p in m['resources'].items():require(after[rel]==sha256(p)==read(AUD/'reviewed-inputs.json')[p],'Mesh/material differs from reviewed candidate')
    require(m['source_mesh_sha256']==before['meshes/expanse12_scirocco_hull.mesh'],'Wrong preserved mesh')
    geometry=binary_geometry(OUT/'meshes/expanse12_scirocco_hull.mesh')
    schemas=[s for rel in edits if (s:=schema_check(OUT/rel,BASE/rel))]
    # Exact launch operators, counter debit and both researched/unresearched clocks.
    d=read(OUT/'entities'/(MAG+'.buff'));launches=[x for x in walk(d)if x.get('operator_type')=='create_torpedo']
    require(len(launches)==12,'Must launch twelve real torpedo objects')
    old=read(BASE/'entities'/(MAG+'.buff'));source=[x for x in walk(old)if x.get('operator_type')=='create_torpedo']
    require(all(x==source[0]for x in launches),'Changed damage/targeting bindings')
    values={x['action_value_id']:x['action_value'].get('values')for x in read(OUT/'entities'/(MAG+'.action_data_source'))['action_values']}
    require(values['magazine_capacity_value']==[48,48] and values['magazine_pair_count_value']==[12,12],'Both research levels must agree on ammo')
    require(values['magazine_pair_interval_value']==[10,10] and values['magazine_reload_duration_value']==[120,120],'Reload cadence changed')
    require(values['heavy_torpedo_damage_value']==[750.,787.5],'Light torpedo damage changed')
    # Emulate supported magazine action operators to test the actual altered graph.
    from update16_magazine_check import check_magazine
    magazine=check_magazine(OUT,BASE)
    resolver=AmunResolver(OUT,GAME);graphs={}
    for n in ['expanse12_scirocco','expanse15_truman','expanse_donnager_battleship']:
        unit=resolver.unit(n,'0.16 focused patch');graphs[n]={'graph':check_actions(OUT,resolver,n),'typed':check_action_values(OUT,GAME,resolver,unit)}
    return {'status':'PASS OFFLINE ONLY','runtime':'NOT RUN for0.16','schemas':schemas,'references':resolver.edges,'graphs':graphs,'geometry':geometry,'magazine_contract':magazine,'changed_files':sorted(p for p in before if before[p]!=after[p]),'all_existing_units_byte_identical':True,'unrelated_weapons_research_audio_textures_byte_identical':True,'preservation':preservation()}

def main(a):
    if not(a.validate_only or a.package_existing):build()
    write(AUD/'package-validation.json',validate())
    if a.validate_only:print('PASS OFFLINE0.16');return
    archive=OUT.with_suffix('.zip');require(not archive.exists(),'Existing archive')
    with zipfile.ZipFile(archive,'w',zipfile.ZIP_DEFLATED)as z:
        for p in sorted(OUT.rglob('*')):
            if p.is_file():
                zi=zipfile.ZipInfo(p.relative_to(OUT).as_posix(),(2026,9,13,0,0,0));zi.compress_type=zipfile.ZIP_DEFLATED;zi.external_attr=0o100644<<16;z.writestr(zi,p.read_bytes())
    result={'mod_id':OUT.name,**verify_zip(archive,OUT),'installed':False,'runtime':'NOT RUN'};write(AUD/'package-summary.json',result)
    OUT.with_suffix('.sha256').write_text(result['zip_sha256']+'  '+archive.name+'\n')
    deps=[BASE,AUD/'reviewed-inputs.json',AUD/'mount-validation.json'];write(OUT.with_suffix('.dependencies.json'),list(map(str,deps)));write(OUT.with_suffix('.provenance.json'),provenance(archive,ROOT,deps));print(json.dumps(result,indent=2))
if __name__=='__main__':
    p=argparse.ArgumentParser();g=p.add_mutually_exclusive_group();g.add_argument('--validate-only',action='store_true');g.add_argument('--package-existing',action='store_true');main(p.parse_args())
