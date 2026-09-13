"""Assemble a separate 0.3 candidate; never install or alter the working 0.2.1.
Worker inputs and the pinned game are read-only. Missing inputs fail explicitly.
"""
from pathlib import Path
import argparse, copy, json, shutil, zipfile
import numpy as np
import jsonschema
from validate_experiments import read, require, sha256, file_hashes, compare_tree, verify_pins, verify_zip, provenance, Resolver, strings
from build_polish import write, cp
ROOT=Path(__file__).resolve().parents[1]
MOD_ID='expanse_corvette_combat03'

def set_pointer(data,pointer,value):
    parts=pointer.strip('/').split('/'); at=data
    for k in parts[:-1]: at=at[int(k)] if isinstance(at,list) else at[k]
    at[int(parts[-1]) if isinstance(at,list) else parts[-1]]=copy.deepcopy(value)

def frozen(game,sdk):
    snap=read(ROOT/'audit/combat03/checkpoint.json')
    for r in snap['trees']:compare_tree(r)
    for p,h in snap['packages'].items():require(sha256(p)==h,'Frozen ZIP changed: '+p)
    old=read(ROOT/'audit/experiments/checkpoint.json')
    for r in old['shared_read_only_inputs'].values():compare_tree(r)
    return verify_pins(ROOT,game,sdk)

def check_actions(mod, resolver, unit_id):
    """Resolve the authored ability->ADS->buff->torpedo chain in its owning skin.
    Installed effects and icons remain boundary references, not copied assets.
    """
    unit=read(mod/'entities'/f'{unit_id}.unit')
    skins=[resolver.skin(n,unit_id) for g in unit['skin_groups'] for n in g['skins']]
    aliases=[{x['alias_name'] for x in s['skin_stages'][0]['effects']['effect_alias_bindings']} for s in skins]
    loc=read(resolver.game/'localized_text/en.localized_text');loc.update(read(mod/'localized_text/en.localized_text'))
    counts={'abilities':0,'buffs':0,'torpedoes':0}
    for group in unit.get('abilities',[]):
        for name in group['abilities']:
            p=resolver.resolve(f'entities/{name}.ability',unit_id);ability=read(p)
            ads=read(resolver.resolve(f"entities/{ability['action_data_source']}.action_data_source",p))
            common=read(resolver.resolve('uniforms/action.uniforms',p))
            values={v['action_value_id'] for v in ads.get('action_values',[])}|{v for ptr,v in strings(common) if ptr[-1]=='action_value_id'}|{'fixed_zero','fixed_one'}
            filters={v['target_filter_id'] for v in ads.get('target_filters',[])}
            modifiers={v['buff_unit_modifier_id'] for v in ads.get('buff_unit_modifiers',[])}
            seen=set()
            def walk(d,source):
                if isinstance(d,list):
                    for v in d:walk(v,source)
                elif isinstance(d,dict):
                    if d.get('binding')=='unit_skin' and 'effect' in d:
                        require(all(d['effect'] in a for a in aliases),f'Unbound ability skin effect: {d["effect"]}')
                    for k,v in d.items():
                        if isinstance(v,str):
                            if k in {'buff','watched_buff','persistant_buff'}:
                                q=resolver.resolve(f'entities/{v}.buff',source)
                                # Existence queries do not execute another
                                # ability's buff with this ability's ADS.
                                if d.get('constraint_type')!='has_buff' and q not in seen:seen.add(q);counts['buffs']+=1;walk(read(q),q)
                            elif k=='torpedo_to_create':
                                t=resolver.unit(v,source);require(t['target_filter_unit_type']=='torpedo' and t['ai_attack_target']['attack_target_type']=='torpedo' and 'torpedo' in t,'Noninterceptable torpedo classification');counts['torpedoes']+=1
                            elif k in {'hud_icon','tooltip_icon','tooltip_picture'}:
                                rel=f'brushes/{v}.brush'
                                resolver.resolve(rel if rel.lower() in resolver.index else f'textures/{v}.png',source)
                            elif k in {'name','description'}:require(v in loc,f'Missing localized {v}')
                            elif k=='buff_unit_modifier_id':require(v in modifiers,'Unknown buff modifier '+v)
                            elif k in {'target_filter','target_filter_id'} or k=='target_filters' and isinstance(v,str):require(v in filters or v.startswith('uniforms_'),'Unknown target filter '+v)
                            elif k.endswith('_value') or k in {'value_id','cooldown_time','antimatter_cost','range','active_duration'}:
                                require(v in values,f'Unknown action value {v} in {source}')
                        else:
                            if k=='target_filters':
                                require(all(x in filters for x in v) if all(isinstance(x,str) for x in v) else True,'Unknown target filter in list')
                            walk(v,source)
            walk(ability,p);walk(ads,p);counts['abilities']+=1
    return counts

def check_package(mod,base,game,sdk,mode='timed'):
    unit=read(mod/'entities/trader_light_frigate.unit');old=read(base/'entities/trader_light_frigate.unit')
    restored=copy.deepcopy(unit);restored['attack']=old['attack'];restored.pop('abilities',None)
    require(restored==old,'Unintended ordinary unit change outside attack pattern and abilities')
    expected_attack=copy.deepcopy(old['attack']);expected_attack['attack_pattern']={'type':'circle_strafe','angle_range_off_gravity_well_plane':[-45.0,45.0]}
    require(unit['attack']==expected_attack,'Unexpected attack behavior change')
    require(unit['physics']==old['physics'] and unit['weapons']==old['weapons'],'Maneuverability or PDC budget changed')
    for p in (base/'entities').glob('*.weapon'):require(sha256(p)==sha256(mod/'entities'/p.name),'Working PDC definition changed')
    if mode=='timed':
        ability=read(mod/'entities/expanse03_torpedo_cycle.ability')
        ads=read(mod/'entities/expanse03_torpedo_cycle.action_data_source')
        buff=read(mod/'entities/expanse03_torpedo_cycle_on_self.buff')
        values={x['action_value_id']:x['action_value']['values'][0] for x in ads['action_values']}
        timed=buff['time_actions'][0]
        require(values[timed['executions_per_interval_value']]==2 and values[timed['execution_interval_count_value']]==4 and values[timed['execution_interval_value']]==10 and values[timed['first_action_delay_time_value']]==0,'Wrong paired launch schedule')
        require(values[ability['active_actions']['cooldown_time']]==120 and ability['active_actions']['cooldown_reset_type']=='on_spawned_buff_made_dead','Wrong reload contract')
        require(len(ability['ability_positions'])==2 and all(abs(x['position'][2])<30 for x in ability['ability_positions']),'Stock Ogrov launch coordinates leaked')
        require(timed['action_group']['actions'][0]['constraint']['target_filter_id']=='heavy_torpedo_target_filter','Missing launch-time target recheck')
        for f in ads['target_filters']:
            require(any(c['constraint_type']=='is_in_current_gravity_well' for c in f['target_filter']['constraints']),'Missing same-well filter')
        require(sorted(p.stem for p in (mod/'entities').glob('*.ability'))==['expanse03_torpedo_cycle'],'Hero/candidate ability leaked into corvette')
    else:
        require(sorted(p.stem for p in (mod/'entities').glob('*.ability'))==['expanse03_torpedo_magazine'],'Extra normal firing budget')
        ability=read(mod/'entities/expanse03_torpedo_magazine.ability')
        require('active_actions' not in ability and ability['passive_actions']['persistant_buff']=='expanse03_torpedo_magazine','Unexpected active magazine channel')
        require(len(ability['ability_positions'])==2,'Missing paired launch locations')
    require(sorted(p.stem for p in (mod/'entities').glob('*.weapon'))==sorted(p.stem for p in (base/'entities').glob('*.weapon')),'Unreviewed weapon leaked')
    oldskin=read(base/'entities/trader_light_frigate.unit_skin');newskin=read(mod/'entities/trader_light_frigate.unit_skin')
    restoredskin=copy.deepcopy(newskin);st=restoredskin['skin_stages'][0];os=oldskin['skin_stages'][0]
    st['unit_mesh']=os['unit_mesh'];st['child_mesh_alias_bindings']=os['child_mesh_alias_bindings']
    expectedaliases=os['effects']['effect_alias_bindings']+[next(x for x in read(game/'entities/trader_torpedo_cruiser.unit_skin')['skin_stages'][0]['effects']['effect_alias_bindings'] if x['alias_name']=='trader_torpedo_cruiser_torpedo_weapon_muzzle')]
    require(st['effects']['effect_alias_bindings']==expectedaliases,'Unexpected effect alias change')
    st['effects']['effect_alias_bindings']=os['effects']['effect_alias_bindings']
    for k in ['travel_effect','travel_effect_between_stars','travel_effect_destabilized']:
        require(st['effects']['hyperspace_effects'][k]=='mcrn03_corvette_phase_plume','Wrong phase effect')
        st['effects']['hyperspace_effects'][k]=os['effects']['hyperspace_effects'][k]
    require(restoredskin==oldskin,'Unrelated skin field changed')
    schemas=0
    types={'.unit':'unit','.unit_skin':'unit-skin','.weapon':'weapon','.ability':'ability','.buff':'buff','.action_data_source':'action-data-source','.brush':'brush'}
    for p in mod.rglob('*'):
        if p.suffix in types:
            jsonschema.Draft7Validator(read(sdk/'json_schemas'/(types[p.suffix]+'-schema.json'))).validate(read(p));schemas+=1
    for ext in ['ability','action_data_source','buff','weapon']:
        require(read(mod/'entities'/f'{ext}.entity_manifest')['ids']==sorted(p.stem for p in (mod/'entities').glob('*.'+ext)),f'{ext} manifest mismatch')
    newunits=sorted(p.stem for p in (mod/'entities').glob('*.unit') if p.stem!='trader_light_frigate')
    require(read(mod/'entities/unit.entity_manifest')['ids']==newunits,'Projectile manifest mismatch')
    resolver=Resolver(mod,game);resolver.unit('trader_light_frigate','combat03-root');actions=check_actions(mod,resolver,'trader_light_frigate')
    skin=read(mod/'entities/trader_light_frigate.unit_skin')
    for _,v in strings(skin['skin_stages'][0]['effects']['hyperspace_effects']):
        if v=='mcrn03_corvette_phase_plume':resolver.resolve('effects/'+v+'.particle_effect','phase hook')
    for p in (mod/'effects').glob('*.particle_effect'):
        for ptr,v in strings(read(p)):
            if ptr[-1].endswith('texture') or ptr[-1] in {'texture_0','texture_1'}:resolver.resolve('textures/'+v+'.dds',p)
    require(len(list((mod/'meshes').glob('*.mesh')))==13,'Stale or missing geometry meshes')
    return {'status':'PASS','schemas':schemas,'action_references':actions,'references':resolver.edges,'runtime':'NOT RUN','particle_schema':'NOT AVAILABLE; observed-field/texture checks only'}

# Assembly is defined below once reviewed worker metadata has been loaded.

def assemble(a):
    frozen(a.game,a.sdk)
    base=ROOT/'build/experiments/expanse_corvette_polish';out=ROOT/'build/experiments'/MOD_ID
    geometry=read(a.geometry/'integration-spec.json');flight=read(a.flight/'integration-spec.json')
    require(geometry['status']=='PASS','Geometry gates incomplete')
    require(not out.exists() and not out.with_suffix('.zip').exists(),'Refusing existing 0.3 output')
    # Explicit ordinary set: no hero railgun/abilities or old combat candidates.
    filenames=['expanse03_heavy_torpedo.unit','expanse03_torpedo_cycle.ability','expanse03_torpedo_cycle_on_self.buff','expanse03_torpedo_cycle.action_data_source']
    for n in filenames:require((a.combat/'entities'/n).is_file(),'Missing ignored combat dependency: '+n)
    shutil.copytree(base,out)
    for directory in ['meshes','mesh_materials']:
        shutil.rmtree(out/directory);(out/directory).mkdir()
    for m in geometry['meshes']:
        require(sha256(m['path'])==m['sha256'],'Geometry drift');cp(Path(m['path']),out/'meshes'/Path(m['path']).name)
        for ident,source in m['material_sources'].items():cp(Path(source),out/'mesh_materials'/(ident+'.mesh_material'))
    unit=read(out/'entities/trader_light_frigate.unit');skin=read(out/'entities/trader_light_frigate.unit_skin')
    require(unit['weapons']['weapons']==geometry['mounts'],'Working mounts changed by geometry')
    for p in flight['unit_patches']:set_pointer(unit,p['pointer'],p['value'])
    unit['abilities']=[{'abilities':['expanse03_torpedo_cycle']}]
    stage=skin['skin_stages'][0];stage['unit_mesh']['mesh']=geometry['hull_mesh']
    for row in stage['child_mesh_alias_bindings']['map']:
        row['mesh_definition']['mesh']=row['mesh_definition']['mesh'].replace('expanse_polish_','expanse03_')
    for p in flight['skin_patches_by_role']['corvette']:set_pointer(skin,p['pointer'],p['value'])
    ogrov=read(a.game/'entities/trader_torpedo_cruiser.unit_skin')
    alias=next(x for x in ogrov['skin_stages'][0]['effects']['effect_alias_bindings'] if x['alias_name']=='trader_torpedo_cruiser_torpedo_weapon_muzzle')
    stage['effects']['effect_alias_bindings'].append(copy.deepcopy(alias))
    write(out/'entities/trader_light_frigate.unit',unit);write(out/'entities/trader_light_frigate.unit_skin',skin)
    for n in filenames:cp(a.combat/'entities'/n,out/'entities'/n)
    torps=read(a.torpedo_mounts)['mounts'];positions=[]
    for m in torps:
        up=np.array(m['up']);forward=np.array(m['forward']);require(abs(np.dot(up,forward))<1e-7,'Nonorthogonal torpedo basis')
        positions.append({'position':m['weapon_position'],'rotation':np.stack([np.cross(up,forward),up,forward]).flatten().tolist()})
    ability=read(out/'entities/expanse03_torpedo_cycle.ability');ability['ability_positions']=positions
    write(out/'entities/expanse03_torpedo_cycle.ability',ability)
    cp(a.flight/'generated/effects/mcrn03_corvette_phase_plume.particle_effect',out/'effects/mcrn03_corvette_phase_plume.particle_effect')
    for ext in ['ability','action_data_source','buff','weapon']:
        write(out/'entities'/f'{ext}.entity_manifest',{'ids':sorted(p.stem for p in (out/'entities').glob('*.'+ext))})
    write(out/'entities/unit.entity_manifest',{'ids':['expanse03_heavy_torpedo']})
    loc=read(out/'localized_text/en.localized_text')
    # Worker writes only new ability-localized keys; no vanilla scope expansion.
    recipe=read(a.combat/'integration-recipe.json')
    names={ability['gui']['name'],ability['gui']['description']}
    loc.update({k:v for k,v in recipe['localization_additions'].items() if k in names})
    loc['trader_light_frigate_description']='Fast-attack corvette with six dual-purpose PDCs and an experimental eight-torpedo launch cycle.'
    write(out/'localized_text/en.localized_text',loc)
    meta=read(out/'.mod_meta_data');meta.update(display_name='The Expanse — Corvette Combat 0.3 EXPERIMENT',display_version='0.3.0',short_description='Supported PDCs, heavy torpedo cycle, orbiting combat and blue phase plume.',long_description='Experimental timed torpedo cycle: pairs at 0/10/20/30 seconds, then 120 seconds reload. Cancellation, interception, save/reload and movement require runtime testing. Includes all corvette model and UI assets; load alone.')
    write(out/'.mod_meta_data',meta);cp(ROOT/'ASSET-SOURCES.md',out/'ASSET-SOURCES.md')
    checks=check_package(out,base,a.game,a.sdk)
    write(ROOT/'audit/combat03/package-validation.json',checks)
    with zipfile.ZipFile(out.with_suffix('.zip'),'w',zipfile.ZIP_DEFLATED) as z:
        for p in sorted(out.rglob('*')):
            if p.is_file():
                info=zipfile.ZipInfo(p.relative_to(out).as_posix(),(2026,9,12,0,0,0));info.compress_type=zipfile.ZIP_DEFLATED;info.external_attr=0o100644<<16;z.writestr(info,p.read_bytes())
    deps=[a.combat,a.geometry/'integration-spec.json',a.flight,a.torpedo_mounts]+[Path(m['path']) for m in geometry['meshes']]
    write(out.with_suffix('.dependencies.json'),[str(p.resolve()) for p in deps])
    write(out.with_suffix('.provenance.json'),provenance(out.with_suffix('.zip'),ROOT,deps))
    summary={'mod_id':MOD_ID,**verify_zip(out.with_suffix('.zip'),out),'installed':False,'runtime':'NOT RUN'}
    write(ROOT/'audit/combat03/package-summary.json',summary);frozen(a.game,a.sdk);print(json.dumps(summary,indent=2))

if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__)
    for k in ['game','sdk','combat','geometry','flight','torpedo-mounts']:p.add_argument('--'+k,type=Path,required=True)
    p.add_argument('--validate-only',action='store_true');a=p.parse_args()
    if a.validate_only:
        frozen(a.game,a.sdk);out=ROOT/'build/experiments'/MOD_ID
        print(json.dumps({'validation':check_package(out,ROOT/'build/experiments/expanse_corvette_polish',a.game,a.sdk)['status'],**verify_zip(out.with_suffix('.zip'),out)},indent=2))
    else:assemble(a)
