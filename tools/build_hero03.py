"""Assemble a separate Rocinante static-deployment combat/ability experiment.
Needs reviewed armed-hero geometry; never substitutes Tachi mounts or installs.
"""
from pathlib import Path
import argparse,copy,json,shutil,zipfile,math
import numpy as np
import jsonschema
from build_polish import write,cp
from build_combat03 import frozen,check_actions,set_pointer
from validate_experiments import read,require,sha256,Resolver,verify_zip,provenance,strings
from flight03_effects import scale_effect
ROOT=Path(__file__).resolve().parents[1];ID='expanse_rocinante03';HERO='expanse_rocinante_hero'

def ability_positions(mounts):
    out=[]
    for m in mounts:
        u=np.array(m['up']);f=np.array(m['forward']);require(abs(u@f)<1e-5,'Nonorthogonal launch basis')
        out.append({'position':m.get('muzzle_hull',m.get('weapon_position',m.get('position'))),'rotation':np.stack([np.cross(u,f),u,f]).flatten().tolist()})
    return out

def fixed_mount(m,weapon,point,yaw=15,pitch=5):
    pos=m.get('muzzle_hull',m.get('weapon_position',m.get('position')))
    return {'weapon':weapon,'mesh_point':point,'weapon_position':pos,'non_turret_muzzle_positions':[pos],
            'up':m['up'],'forward':m['forward'],'yaw_arc':{'min_angle':-yaw,'max_angle':yaw},'pitch_arc':{'min_angle':-pitch,'max_angle':pitch}}

def validate(out,game,sdk,metadata):
    unit=read(out/'entities'/f'{HERO}.unit');mounts=unit['weapons']['weapons']
    base=ROOT/'build/experiments/expanse_corvette_ammo03'
    for p in (base/'entities').iterdir():
        if p.suffix!='.entity_manifest':require(sha256(p)==sha256(out/'entities'/p.name),'Hero changed ordinary corvette/projectile behavior')
    for folder in ['meshes','mesh_materials','textures','brushes','effects']:
        for p in (base/folder).iterdir():require(sha256(p)==sha256(out/folder/p.name),'Hero changed ordinary asset '+str(p))
    require(len(mounts)==7 and len({m['weapon'] for m in mounts})==7,'Expected six hero PDC budgets plus railgun')
    for i,m in enumerate(mounts[:6]):
        w=read(out/'entities'/(m['weapon']+'.weapon'))
        require('turret' not in w and w['damage']==28 and w['cooldown_duration']==.25 and w['penetration']==0,'Wrong static PDC experiment budget')
        require(m==fixed_mount(metadata['pdc_mounts'][i],m['weapon'],f'weapon.pdc.{i}'),'Hero PDC not bound to actual model')
    rail=read(out/'entities/expanse03_hero_railgun.weapon')
    require(rail['damage']==2500 and rail['penetration']==1000 and rail['cooldown_duration']==10,'Wrong rail budget')
    require(unit['antimatter']=={'max_antimatter':350.0,'antimatter_restore_rate':1.0},'Missing hero antimatter')
    n=0
    types={'.unit':'unit','.unit_skin':'unit-skin','.weapon':'weapon','.ability':'ability','.buff':'buff','.action_data_source':'action-data-source','.player':'player','.brush':'brush'}
    for p in out.rglob('*'):
        if p.suffix in types:jsonschema.Draft7Validator(read(sdk/'json_schemas'/(types[p.suffix]+'-schema.json'))).validate(read(p));n+=1
    tags=read(out/'uniforms/unit_tag.uniforms')
    jsonschema.Draft7Validator(read(sdk/'json_schemas/unit-tag-uniforms-schema.json')).validate(tags)
    require(tags.pop('overwrite_unit_tags') is True,'Explicit full tag replacement missing')
    require(tags['unit_tags'].pop()=={'name':HERO,'localized_name':HERO+'_name'},'Wrong private tag')
    require(tags==read(game/'uniforms/unit_tag.uniforms'),'Unrelated vanilla tag change')
    for ident in ['trader_loyalist','trader_rebel','dlc_trader_loyalist']:
        player=read(out/'entities'/f'{ident}.player');stock=read(game/'entities'/f'{ident}.player');restored=copy.deepcopy(player)
        require(restored['buildable_units'].pop()==HERO,'Wrong hero build registration')
        require(restored['unit_limits']['global'].pop()=={'tag':HERO,'unit_limit':1},'Wrong private hero cap')
        require(restored==stock,'Unrelated player/faction change')
    for ext in ['weapon','ability','buff','action_data_source']:
        require(read(out/'entities'/f'{ext}.entity_manifest')['ids']==sorted(p.stem for p in (out/'entities').glob('*.'+ext)),f'{ext} manifest mismatch')
    require(read(out/'entities/unit.entity_manifest')['ids']==['expanse03_heavy_torpedo',HERO],'New unit manifest mismatch')
    require(read(out/'entities/unit_skin.entity_manifest')['ids']==[HERO],'Hero skin manifest mismatch')
    resolver=Resolver(out,game);resolver.unit('trader_light_frigate','ordinary corvette');resolver.unit(HERO,'hero root')
    actions=check_actions(out,resolver,HERO)
    hull=resolver.mesh(read(out/'entities'/f'{HERO}.unit_skin')['skin_stages'][0]['unit_mesh']['mesh'],'hero mount basis')
    for m in mounts:
        point=next(x for x in hull['meshpoints'] if x['name']==m['mesh_point']);r=np.array(point['rotation']).reshape(3,3)
        require(np.allclose(point['position'],m['weapon_position'],atol=2e-5) and np.allclose(r[1],m['up'],atol=2e-5) and np.allclose(r[2],m['forward'],atol=2e-5),'Hero compiled point differs from actual mount metadata')
    for p in (out/'effects').glob('*.particle_effect'):
        for ptr,v in strings(read(p)):
            if ptr[-1].endswith('texture') or ptr[-1] in {'texture_0','texture_1'}:resolver.resolve('textures/'+v+'.dds',p)
    return {'status':'PASS','schemas':n+1,'hero_mounts':7,'ability_graph':actions,'references':resolver.edges,'runtime':'NOT RUN','limitations':['Hero PDCs static deployed; no rotating mesh/animation binding in this experiment','Prototype added railgun/ports are not authenticated TV source geometry','Particle effects have no pinned schema','Queue limits, timer persistence, interception, damage and aura behavior need runtime tests']}

def main(a):
    frozen(a.game,a.sdk);out=ROOT/'build/experiments'/ID
    require(not out.exists() and not out.with_suffix('.zip').exists(),'Refusing existing hero output')
    meta=read(a.hero_metadata);spec=read(a.hero_spec)
    meta['torpedo_mounts']=meta['torpedo_ports'];meta['railgun_mount']=meta['railgun']
    require(spec['status'].startswith('PASS'),'Hero geometry offline gates incomplete')
    require(len(meta['pdc_mounts'])==6 and len(meta['torpedo_mounts'])==2 and 'railgun_mount' in meta,'Incomplete actual hero hardpoints')
    base=ROOT/'build/experiments/expanse_corvette_ammo03';shutil.copytree(base,out)
    for root in [a.hero_abilities/'generated',a.hero_abilities/'unit-candidate']:
        for p in root.rglob('*'):
            if p.is_file() and p.name!='candidate-status.json' and 'localized_text' not in p.parts:cp(p,out/p.relative_to(root))
    for p in (a.hero_game).rglob('*'):
        if p.is_file():cp(p,out/p.relative_to(a.hero_game))
    ui=read(a.ui/'integration-spec.json')
    for p in (a.ui/'generated').rglob('*'):
        if p.is_file():cp(p,out/p.relative_to(a.ui/'generated'))
    unit=read(out/'entities'/f'{HERO}.unit');skin=read(base/'entities/trader_light_frigate.unit_skin');stage=skin['skin_stages'][0]
    stage['unit_mesh']['mesh']=spec['mesh_id'];stage.pop('child_mesh_alias_bindings',None)
    stage['gui']['name']=HERO+'_name';stage['gui']['description']=HERO+'_description';stage['gui'].pop('special_operation_names',None)
    for edit in ui['hero_skin_patches']:set_pointer(skin,edit['pointer'],edit['value'])
    for k in ['travel_effect','travel_effect_between_stars','travel_effect_destabilized']:stage['effects']['hyperspace_effects'][k]='expanse03_roci_phase_plume'
    stage['effects']['exhaust_effects']['particle_effects']=[{'particle_effect':'expanse03_roci_idle_plume'}]
    ordinary=read(a.game/'effects/exhaust_tech_medium_01.particle_effect')
    # Hero nozzle metadata uses the normalized hull's aft (-Z) convention.
    nozzle=meta['exhaust'];f=np.array(nozzle['forward'],dtype=float);f=f/np.linalg.norm(f)
    require(f[2]<-.99,'Unexpected hero nozzle direction')
    write(out/'effects/expanse03_roci_idle_plume.particle_effect',scale_effect(ordinary,1.5,1.5,blue=True))
    phase=scale_effect(ordinary,1.5,6.0,blue=True)
    yaw=math.atan2(f[0],f[2]);pitch=-math.asin(f[1])
    for node in phase['nodes']:
        require(node['x']==[0,0] and node['y']==[0,0] and all(node[k]==[0,0] for k in ['yaw','pitch','roll']),'Unsupported nonaxial plume node')
        positions=[np.array(nozzle['position'])+z*f for z in node['z']]
        for axis,index in [('x',0),('y',1),('z',2)]:node[axis]=sorted(float(p[index]) for p in positions)
        node['yaw']=[yaw,yaw];node['pitch']=[pitch,pitch]
    write(out/'effects/expanse03_roci_phase_plume.particle_effect',phase)
    mounts=[]
    for i,m in enumerate(meta['pdc_mounts']):
        ident=f'expanse03_roci_pdc_{i}';w=read(base/'entities'/f'expanse_polish_pdc_{i}.weapon');w.pop('turret')
        write(out/'entities'/(ident+'.weapon'),w);mounts.append(fixed_mount(m,ident,f'weapon.pdc.{i}'))
    cp(a.combat/'entities/expanse03_hero_railgun.weapon',out/'entities/expanse03_hero_railgun.weapon')
    mounts.append(fixed_mount(meta['railgun_mount'],'expanse03_hero_railgun','weapon.rail.0',10,10))
    unit['weapons']={'weapons':mounts,'max_range_weapon_index':6}
    unit['ai']['attack_target_type_groups_matching_weapon']=mounts[0]['weapon'];unit['ai']['attack_target_type_groups']=read(out/'entities'/f"{mounts[0]['weapon']}.weapon")['attack_target_type_groups']
    # Coordinates are per ability definition, so hero normal needs its own ID.
    normal=read(base/'entities/expanse03_torpedo_magazine.ability');normal['ability_positions']=ability_positions(meta['torpedo_mounts'])
    write(out/'entities/expanse03_roci_torpedo_magazine.ability',normal)
    for g in unit['abilities']:
        g['abilities']=['expanse03_roci_torpedo_magazine' if x=='expanse03_torpedo_cycle' else x for x in g['abilities']]
    for ext in ['ability','buff','action_data_source']:
        ident='expanse03_hero_torpedo_salvo'+('_on_self' if ext=='buff' else '')
        cp(a.combat/'entities'/f'{ident}.{ext}',out/'entities'/f'{ident}.{ext}')
    salvo=read(out/'entities/expanse03_hero_torpedo_salvo.ability');salvo['ability_positions']=ability_positions(meta['torpedo_mounts']);write(out/'entities/expanse03_hero_torpedo_salvo.ability',salvo)
    recipe=read(a.combat/'integration-recipe.json');existing={x['alias_name'] for x in stage['effects']['effect_alias_bindings']}
    stage['effects']['effect_alias_bindings'] += [x for x in recipe['required_skin_effect_alias_bindings'] if x['alias_name'] not in existing]
    write(out/'entities'/f'{HERO}.unit',unit);write(out/'entities'/f'{HERO}.unit_skin',skin)
    for ext in ['weapon','ability','buff','action_data_source']:write(out/'entities'/f'{ext}.entity_manifest',{'ids':sorted(p.stem for p in (out/'entities').glob('*.'+ext))})
    write(out/'entities/unit.entity_manifest',{'ids':['expanse03_heavy_torpedo',HERO]});write(out/'entities/unit_skin.entity_manifest',{'ids':[HERO]})
    loc=read(out/'localized_text/en.localized_text')
    for p in [a.hero_abilities/'generated/localized_text/en.localized_text',a.hero_abilities/'unit-candidate/localized_text/en.localized_text']:loc.update(read(p))
    loc.update(recipe['localization_additions']);write(out/'localized_text/en.localized_text',loc)
    metadata=read(out/'.mod_meta_data');metadata.update(logos=ui['optional_root_logos'],display_name='The Expanse — Rocinante 0.3 STATIC RIG EXPERIMENT',short_description='Rocinante hero with prototype hardpoints and crew abilities.',long_description='New stand-free Rocinante model in a baked deployed pose. Six static PDC mounts, added prototype railgun/launch ports, separate salvo and crew abilities. Rotation/deployment animation is not bound. Runtime tests pending.')
    write(out/'.mod_meta_data',metadata);cp(ROOT/'ASSET-SOURCES.md',out/'ASSET-SOURCES.md')
    checks=validate(out,a.game,a.sdk,meta);write(ROOT/'audit/combat03/hero-package-validation.json',checks)
    with zipfile.ZipFile(out.with_suffix('.zip'),'w',zipfile.ZIP_DEFLATED) as z:
        for p in sorted(out.rglob('*')):
            if p.is_file():
                i=zipfile.ZipInfo(p.relative_to(out).as_posix(),(2026,9,12,0,0,0));i.compress_type=zipfile.ZIP_DEFLATED;i.external_attr=0o100644<<16;z.writestr(i,p.read_bytes())
    deps=[a.hero_spec,a.hero_metadata,a.hero_game,a.ui,a.combat,a.hero_abilities]
    write(out.with_suffix('.dependencies.json'),[str(p.resolve()) for p in deps]);write(out.with_suffix('.provenance.json'),provenance(out.with_suffix('.zip'),ROOT,deps))
    summary={'mod_id':ID,**verify_zip(out.with_suffix('.zip'),out),'runtime':'NOT RUN','installed':False};write(ROOT/'audit/combat03/hero-package-summary.json',summary);frozen(a.game,a.sdk);print(json.dumps(summary,indent=2))

if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__)
    for k in ['game','sdk','hero-metadata','hero-spec','hero-game','ui','combat','hero-abilities']:p.add_argument('--'+k,type=Path,required=True)
    main(p.parse_args())
