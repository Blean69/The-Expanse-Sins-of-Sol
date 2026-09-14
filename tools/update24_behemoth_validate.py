"""Read-only frozen-baseline validation through a disposable private overlay view."""
from pathlib import Path
import hashlib,json,os,sys
ROOT=Path(__file__).resolve().parents[1]
MAIN=Path('/run/media/haker/NVME 2/expanse-mod')
sys.path.insert(0,str(MAIN/'tools'))
from update11_validate import schema_check
from amun06_validate_package import AmunResolver,check_action_values
from build_combat03 import check_actions
from common import read,write,read_mesh
sys.path.insert(0,str(ROOT/'tools'))
from update24_behemoth_gameplay import changes,BASE,GAME,ID

def main():
    edits,loc,origins,report=changes();view=ROOT/'build/update24-behemoth/validation-view';view.mkdir(exist_ok=True)
    # Link each baseline file read-only in intent, then replace only owned new
    # resources and local registry/text copies. Never write through a symlink.
    for p in BASE.rglob('*'):
        if p.is_file():
            d=view/p.relative_to(BASE);d.parent.mkdir(parents=True,exist_ok=True)
            if not d.exists():d.symlink_to(p)
    for rel,d in edits.items():
        p=view/rel
        if p.is_symlink():p.unlink()
        write(p,d)
    for folder in [Path(report['art_directory']),ROOT/'build/update24-behemoth/gameplay-art']:
        for p in folder.rglob('*'):
            if not p.is_file():continue
            d=view/p.relative_to(folder);d.parent.mkdir(parents=True,exist_ok=True)
            if d.exists():assert d.read_bytes()==p.read_bytes()
            else:d.symlink_to(p)
    text=read(BASE/'localized_text/en.localized_text');text.update(loc);p=view/'localized_text/en.localized_text'
    if p.is_symlink():p.unlink()
    write(p,text)
    tags=read(BASE/'uniforms/unit_tag.uniforms');tags['unit_tags']+=report['unit_tag_entries_append'];p=view/'uniforms/unit_tag.uniforms'
    if p.is_symlink():p.unlink()
    write(p,tags)
    schemas=[]
    for rel in edits:
        r=schema_check(view/rel,Path(origins[rel])if rel in origins else None)
        if r:schemas.append(r)
    resolver=AmunResolver(view,GAME);unit=resolver.unit(ID,'Behemoth isolated audit')
    actions=check_actions(view,resolver,ID);action_values=check_action_values(view,GAME,resolver,unit)
    # Exact source values and no drift of pre-existing profiles.
    pdc=edits['entities/'+ID+'_pdc.weapon'];assert pdc['damage']/pdc['cooldown_duration']==85.
    assert len(unit['weapons']['weapons'])==8 and all(x['weapon']==ID+'_pdc'for x in unit['weapons']['weapons'])
    assert unit['tags']==['titan',ID]and unit['build']['build_kind']=='titan'and unit['target_filter_unit_type']=='titan'
    assert unit['items']==read(BASE/'entities/expanse_donnager_battleship.unit')['items']
    assert all(h['max_shield_points']==0 and 'shield_burst_restore'not in h for h in unit['health']['levels'])
    assert all('weapon_modifiers'not in x for x in unit['levels']['levels'])
    mag=edits['entities/'+ID+'_magazine.action_data_source'];assert mag==read(BASE/'entities/expanse19_europa_magazine.action_data_source')
    ability=edits['entities/'+ID+'_hospital.ability'];ads=edits['entities/'+ID+'_hospital.action_data_source'];vs={x['action_value_id']:x['action_value']['values'][0]for x in ads['action_values']}
    assert vs['repair_per_tick']*vs['repair_ticks']==800
    assert ability['active_actions']['auto_cast']['enabled_by_default_behavior']=='always'
    for target in ads['target_filters']:
        assert target['target_filter']['ownerships']==['self']
        assert any(c.get('constraint',{}).get('buff')=='expanse15_scirocco_engineering_teams'for c in target['target_filter']['constraints'])
    info=read_mesh(Path(report['art_directory'])/'meshes/expanse24_behemoth_hull.mesh');points={p['name']for p in info['meshpoints']}
    for weapon in unit['weapons']['weapons']:assert weapon['mesh_point']in points
    sourcehash={p:hashlib.sha256(Path(p).read_bytes()).hexdigest()for p in report['source_definitions_sha256']}
    assert sourcehash==report['source_definitions_sha256']
    result={'status':'PASS OFFLINE SCHEMA, REFERENCES, ACTION VALUES AND NUMERIC CONTRACTS','schemas':schemas,'actions':actions,'action_values':action_values,'checks':{'source_definitions_preserved':True,'shared_titan_kind_tag_and_type':True,'exact_native_titan_equipment_slots':True,'no_railguns':True,'pdc_dps':85,'pdc_count':8,'no_level_offensive_stat_drift':True,'shared_scirocco_repair_buff':True,'repair_cap':800,'owned_only_filters':True,'autocast_default_on':True,'magazine_ADS_unchanged_from_Europa':True,'all_weapon_meshpoints_exist':True,'art_file_hashes':{str(p.relative_to(Path(report['art_directory']))):hashlib.sha256(p.read_bytes()).hexdigest()for p in Path(report['art_directory']).rglob('*')if p.is_file()}},'integration_not_yet_applied':['OPA player access','priced titan research chain','new unit tag registry entry','final package manifests'],'runtime':{k:'NOT RUN'for k in report['untested']}}
    write(ROOT/'docs/audit/update24-behemoth/gameplay-validation.json',result);print(json.dumps({'status':result['status'],'schemas':len(schemas),'actions':actions,'values':action_values}))

if __name__=='__main__':main()
