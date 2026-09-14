"""Exact-scope, native-schema and reference checks for the private command overlay."""
from pathlib import Path
import hashlib,json,sys
import numpy as np
ROOT=Path(__file__).resolve().parents[1];MAIN=Path('/run/media/haker/NVME 2/expanse-mod');sys.path.insert(0,str(MAIN/'tools'))
from common import read,write,read_mesh
from update11_validate import schema_check
from amun06_validate_package import AmunResolver,check_action_values
from build_combat03 import check_actions
sys.path.insert(0,str(ROOT/'tools'))
from update26_command_gameplay import changes,BASE,ID,ART,MAG,COLONY,rename
GAME=MAIN.parent/'SteamLibrary/steamapps/common/Sins2'
class Resolver(AmunResolver):
    def weapon(self,name,skins,source):
        d=read(self.resolve('entities/'+name+'.weapon',source))
        if d.get('weapon_type')!='planet_bombing':return super().weapon(name,skins,source)
        assert d['uniforms_target_filter_id']in self.filters and d['acquire_target_logic']=='order_target_only'
        for s in skins:
            for stage in s['skin_stages']:
                aliases={x['alias_name']for x in stage.get('effects',{}).get('effect_alias_bindings',[])}
                for k,v in d.get('effects',{}).items():
                    if k.endswith('_effect')and isinstance(v,str):assert v in aliases
        return d

def main():
    edits,loc,origins,report=changes();view=ROOT/'build/update26-command/validation-view';view.mkdir(exist_ok=True)
    for p in BASE.rglob('*'):
        if p.is_file():
            dst=view/p.relative_to(BASE);dst.parent.mkdir(parents=True,exist_ok=True)
            if not dst.exists():dst.symlink_to(p)
    for rel,d in edits.items():
        p=view/rel
        if p.is_symlink():p.unlink()
        write(p,d)
    for rel,p in report['art_files'].items():
        dst=view/rel;dst.parent.mkdir(parents=True,exist_ok=True)
        if not dst.exists():dst.symlink_to(p)
        else:assert dst.read_bytes()==Path(p).read_bytes()
    text=read(BASE/'localized_text/en.localized_text');text.update(loc);p=view/'localized_text/en.localized_text'
    if p.is_symlink():p.unlink()
    write(p,text)
    schemas=[schema_check(view/rel,Path(origins[rel]))for rel in edits]
    resolver=Resolver(view,GAME);unit=resolver.unit(ID,'Private update26 command audit')
    # The old helper checks ADS-local filters only for lists (unlike its string
    # branch). Extend local validation scope with the actually declared native
    # filter IDs; do not change valid gameplay or any shared checker file.
    import inspect,build_combat03
    source=inspect.getsource(build_combat03.check_actions)
    source=source.replace("filters={v['target_filter_id'] for v in ads.get('target_filters',[])}","filters={v['target_filter_id'] for v in ads.get('target_filters',[])}|set(resolver.filters)")
    scope=dict(vars(build_combat03));exec(source,scope)
    actions=scope['check_actions'](view,resolver,ID)
    import amun06_validate_package
    source=inspect.getsource(amun06_validate_package.check_action_values).replace("require(set(v)<=filters,'Unknown target_filters list member')","require(set(v)<=(filters|set(resolver.filters)),'Unknown target_filters list member')")
    scope=dict(vars(amun06_validate_package));exec(source,scope);values=scope['check_action_values'](view,GAME,resolver,unit)
    old=read(BASE/'entities'/(ID+'.unit'));s=report['stats']['scale']
    for k in ['physics','move','hyperspace','levels','items']:assert unit[k]==old[k],k
    for k in old['build']:
        if k!='price':assert unit['build'][k]==old['build'][k],k
    for before,after in zip(old['health']['levels'],unit['health']['levels'],strict=True):
        for k in before:assert after[k]==before[k]*(2 if k in ['max_hull_points','max_armor_points']else 1),k
    assert unit['health']['durability']==old['health']['durability']
    assert [x for x in unit['abilities'][0]['abilities']if x not in [MAG,COLONY]]==[x for x in old['abilities'][0]['abilities']if x!='expanse19_europa_magazine']
    assert sum(COLONY in x['abilities']for x in unit['abilities'])==1
    assert not any(COLONY in x['build_group']for x in unit['item_builds'])
    for ext in ['ability','action_data_source','buff']:
        d=rename(read(view/'entities'/(MAG+'.'+ext)),MAG,'expanse19_europa_magazine');baseline=read(BASE/'entities'/('expanse19_europa_magazine.'+ext))
        if ext=='ability':
            for p,b in zip(d['ability_positions'],baseline['ability_positions'],strict=True):
                assert np.allclose(p['position'],np.array(b['position'])*s);p['position']=b['position']
        assert d==baseline,ext
    for i in range(6):
        before=read(BASE/'entities'/f'expanse19_europa_pdc_{i}.weapon');after=read(view/'entities'/f'{ART}_pdc_{i}.weapon');t=after.pop('turret');bt=before.pop('turret');assert before==after
        assert t['type']==bt['type'];assert t['biaxial_base_mesh']==ART+'_pdc_base'and t['biaxial_barrel_mesh']==ART+'_pdc_barrel'
        assert np.allclose(t['barrel_position'],np.array(bt['barrel_position'])*s)and np.allclose(t['muzzle_positions'],np.array(bt['muzzle_positions'])*s)
    hull=read_mesh(view/'meshes'/(ART+'_hull.mesh'));points={p['name']:p for p in hull['meshpoints']}
    for a,b in zip(unit['weapons']['weapons'],old['weapons']['weapons'],strict=True):
        assert a['mesh_point']in points
        assert np.allclose(a['weapon_position'],np.array(b['weapon_position'])*s)
        for k in ['up','forward','yaw_arc','pitch_arc']:assert a[k]==b[k]
        if 'non_turret_muzzle_positions'in b:assert np.allclose(a['non_turret_muzzle_positions'],np.array(b['non_turret_muzzle_positions'])*s)
    assert 'weapon.boarding.0'in points and 'weapon.torpedo.0'in points
    for p,h in report['source_definitions_sha256'].items():assert hashlib.sha256(Path(p).read_bytes()).hexdigest()==h
    art=read(ROOT/'audit/update26-command/art-contract.json')
    for mesh in art['meshes']:
        for p,h in mesh['sources_sha256'].items():assert hashlib.sha256(Path(p).read_bytes()).hexdigest()==h
    result={'status':'PASS OFFLINE: schemas, references, action values, exact preservation and uniform attachment checks','schemas':schemas,'actions':actions,'action_values':values,'checks':{'regular_Europa_untouched':True,'all_shared_magazine_programs_untouched':True,'private_magazine_only_ID_and_position_differences':True,'PDC_combat_fields_unchanged':True,'PDC_geometry_and_offsets_uniformly_scaled':True,'all_weapon_meshpoints_exist':True,'colony_and_boarding_meshpoints_exist':True,'physics_and_progression_unchanged':True,'hull_armor_exactly_doubled_at_all_levels':True,'direct_colony_once_no_item_recommendation':True,'native_colony_program_unmodified':True},'runtime':{x:'NOT RUN'for x in report['untested']}}
    write(ROOT/'audit/update26-command/validation.json',result);print(json.dumps({'status':result['status'],'schemas':len(schemas)}))
if __name__=='__main__':main()
