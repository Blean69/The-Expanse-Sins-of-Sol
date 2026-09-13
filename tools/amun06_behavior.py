#!/usr/bin/env python3
"""Amun combat/boarding core plus isolated, evidence-checked optional cloak."""
import argparse,copy,hashlib,json
from pathlib import Path
import jsonschema

ROOT=Path(__file__).resolve().parents[1]
PIN='8e061033afe53b1393eaefd56617a3fd041eeb5f'
SCHEMAS={'.ability':'ability','.buff':'buff','.action_data_source':'action-data-source','.unit':'unit','.unit_skin':'unit-skin','.weapon':'weapon'}
def read(p):return json.loads(Path(p).read_text(encoding='utf-8-sig'))
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def write(p,d):p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(d,indent=2)+'\n')
def rename(x,mapping):
    if isinstance(x,dict):return {k:rename(v,mapping)for k,v in x.items()}
    if isinstance(x,list):return [rename(v,mapping)for v in x]
    if isinstance(x,str):
        for old,new in mapping.items():x=x.replace(old,new)
    return x
def walk(x,path=''):
    if isinstance(x,dict):
        for k,v in x.items():
            yield x,k,v,path+'/'+k
            yield from walk(v,path+'/'+k)
    elif isinstance(x,list):
        for i,v in enumerate(x):yield from walk(v,path+'/'+str(i))
def schema_check(name,d,sdk):jsonschema.Draft7Validator(read(sdk/'json_schemas'/(SCHEMAS[Path(name).suffix]+'-schema.json'))).validate(d)

def observed_cloak_check(entities,sdk,game):
    """No schema edits. Validate known remainder and exact installed extensions."""
    stock=read(game/'entities/dlc3_herald_cloak_frigate_cloak.buff')
    stock_degrade=read(game/'entities/dlc3_herald_cloak_frigate_cloak_damage_dealt_degrade.buff')
    records=[]
    for name in ['expanse06_amun_cloak.buff','expanse06_amun_revealed.buff']:
        value=copy.deepcopy(entities[name]);removed={}
        if name=='expanse06_amun_cloak.buff':
            for k in ['provides_cloak','required_product','cloak_alpha_value','cloak_fade_duration_value']:
                assert value[k]==stock[k],('Unobserved cloak extension',k,value[k])
                removed[k]=value.pop(k)
        modifiers=value.pop('unit_modifiers')
        assert len(modifiers)==1 and modifiers[0]['modifier_type']=='cloak_quality' and modifiers[0]['value_behavior']=='additive'
        source=stock if name=='expanse06_amun_cloak.buff' else stock_degrade
        assert source['unit_modifiers'][0]['modifier_type']=='cloak_quality' and source['unit_modifiers'][0]['value_behavior']=='additive'
        assert set(modifiers[0])=={'modifier_type','value_behavior','value_id'}
        schema_check(name,value,sdk)
        records.append({'file':name,'full_official_schema':'NOT PASS: pinned schema lacks cloak extensions','known_remainder':'PASS pinned schema after explicitly separating listed extensions','observed_extensions':removed,'observed_modifier':modifiers[0]})
    u=read(game/'entities/dlc3_herald_cloak_frigate.unit')
    assert u['cloak_ability']=='dlc3_herald_cloak_frigate_cloak'
    return {'status':'PASS source-evidence checks only; NOT full official schema validation','records':records,'unit_hook_evidence':{'source':'entities/dlc3_herald_cloak_frigate.unit','field':'cloak_ability','value_type':'ability ID string'},'runtime':'NOT RUN'}

def validate_components(package,candidate,sdk,*,cloak=False,boarding_model=False):
    """Validate private components; excludes main-owned mounts/ship/manifest checks."""
    package,candidate,sdk=map(Path,[package,candidate,sdk]);core=candidate/'core/entities';count=0
    for p in core.iterdir():
        expected=read(p);actual=read(package/'entities'/p.name)
        if p.suffix=='.weapon' and '_pdc_' in p.name:
            actual=copy.deepcopy(actual);actual.pop('turret',None)
        if p.name=='expanse06_amun_magazine.ability':
            actual=copy.deepcopy(actual);positions=actual.pop('ability_positions',None)
            assert isinstance(positions,list) and positions,'Main must bind actual Amun launch positions'
        if boarding_model and p.name=='expanse06_amun_boarding.ability':
            expected['active_actions']['actions']['actions'][0]['operators'][1]['mesh_point']='weapon.boarding.0'
        if boarding_model and p.name=='expanse06_amun_boarding.action_data_source':
            expected['effect_alias_bindings'][0]['alias_binding']['particle_effect']='expanse06_boarding_pod_visual'
        assert actual==expected, 'Unapproved component change '+p.name
        schema_check(p.name,read(package/'entities'/p.name),sdk);count+=1
    optional_ids={p.name for p in (candidate/'cloak/entities').iterdir()}
    if not cloak:
        assert not any((package/'entities'/n).exists() for n in optional_ids),'Optional cloak leaked into official-schema core'
        ship=package/'entities/expanse_amun_ra.unit'
        if ship.exists():assert 'cloak_ability' not in read(ship),'Unvalidated cloak unit hook leaked into core'
    else:
        for name in optional_ids:assert read(package/'entities'/name)==read(candidate/'cloak/entities'/name),name
    return {'status':'PASS private core invariants and pinned schemas','schema_count':count,'optional_cloak_present':cloak,'official_cloak_validation':'NOT CLAIMED','runtime':'NOT RUN','scope':'Main still verifies final meshes/mounts/effects/ownership limits/manifests and source preservation'}

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--base',type=Path,required=True);ap.add_argument('--game',type=Path,required=True);ap.add_argument('--sdk',type=Path,required=True);ap.add_argument('--source-root',type=Path,default=Path('/run/media/haker/NVME 2/expanse-mod'));ap.add_argument('--torpedo-worker',type=Path,required=True);ap.add_argument('--output',type=Path,default=ROOT/'build/amun06-a/final');a=ap.parse_args()
    assert a.output.resolve().is_relative_to(ROOT/'build/amun06-a') and not a.output.exists(),'Fresh owned output required'
    snap=read(a.source_root/'audit/schema-comparison.json');assert snap['official_commit']==PIN
    for rec in snap['files']:
        p=a.sdk/rec['path'];b=p.read_bytes();assert hashlib.sha1(b'blob '+str(len(b)).encode()+b'\0'+b).hexdigest()==rec['official_git_blob']
    frozen={str(p.relative_to(a.base)):sha(p)for p in a.base.rglob('*')if p.is_file()}
    spec=read(a.torpedo_worker/'audit/torpedo05-b/integration-spec.json')
    assert sha(spec['mesh'])==spec['sha256'];assert sha(spec['material']['path'])==spec['material']['sha256']
    for t in spec['textures']:assert sha(t['path'])==t['sha256']
    inputs=[ROOT/'build/stealth05-a/combat/entities',ROOT/'build/stealth05-a/probes/entities']
    for p in inputs:
        if not p.is_dir():raise SystemExit('BLOCKED missing reviewed candidate input '+str(p))
    mapping={'expanse05_amun':'expanse06_amun','expanse05_cloak_revealing_gun':'expanse06_cloak_revealing_gun'}
    core={rename(p.name,mapping):rename(read(p),mapping)for p in inputs[0].iterdir()}
    # Actual custom torpedo appearance and bounding sphere come from reviewed0.4.1.
    unit=core['expanse06_amun_torpedo.unit'];unit['spatial']=read(a.base/'entities/expanse04_light_torpedo.unit')['spatial']
    skin=read(a.base/'entities/expanse04_light_torpedo.unit_skin');skin['skin_stages'][0]['gui'].update(name='expanse06_amun_torpedo.name',description='expanse06_amun_torpedo.description');assert skin['skin_stages'][0]['unit_mesh']['mesh']==spec['mesh_id'];core['expanse06_amun_torpedo.unit_skin']=skin
    coreloc=rename(read(ROOT/'build/stealth05-a/combat/localization.json'),mapping)
    # rename() intentionally never alters dict keys; normalize localization keys.
    coreloc={rename(k,mapping):v for k,v in coreloc.items()}
    board='expanse06_amun_boarding'
    for p in inputs[1].glob('expanse05_boarding_probe.*'):
        d=rename(read(p),{'expanse05_boarding_probe':board})
        if p.suffix=='.ability':
            d['gui'].update(name=board+'.name',description=board+'.description')
            d['gui']['tooltip_line_groups'][0]['lines'][0]['label_text']=board+'.chance'
        core[board+p.suffix]=d
    coreloc.update({board+'.name':'Boarding shuttles',board+'.description':'Launch a modeled boarding shuttle at an enemy capital ship. After a 3-second delay, one eligible attempt has a 10% capture chance. Requires free fleet supply. The shuttle effect cannot be intercepted.',board+'.chance':'Capture chance per attempt'})
    # Ship-skin effect aliases are existing definitions, passed to main explicitly.
    all_aliases={}
    for ident in ['trader_light_frigate','expanse_rocinante_hero']:
        for e in read(a.base/'entities'/(ident+'.unit_skin'))['skin_stages'][0]['effects']['effect_alias_bindings']:all_aliases[e['alias_name']]=e
    alias_names={'expanse04_light_torpedo_muzzle'}
    for name,d in core.items():
        if name.endswith('.weapon'):
            alias_names.update(v for k,v in d['effects'].items() if isinstance(v,str) and k.endswith('_effect'))
    required_aliases=[all_aliases[k]for k in sorted(alias_names)]
    # Isolate optional controller/manual cloak/reveal definitions from core files.
    cloakid='expanse06_amun_cloak';controller=cloakid+'_controller';reveal='expanse06_amun_revealed';optional={}
    counter=read(inputs[1]/'expanse05_launch_probe.buff')
    counter=rename(counter,{'expanse05_cloak_revealing_gun':'expanse06_cloak_revealing_gun','trader_torpedo_cruiser_torpedo':'expanse06_amun_torpedo'})
    has_cloak={'constraint_type':'unit_passes_unit_constraint','unit':{'unit_type':'current_spawner'},'unit_constraint':{'constraint_type':'has_buff','buff':cloakid,'include_pending_buffs':False}}
    apply_reveal={'action_type':'use_unit_operators_on_single_unit','destination_unit':{'unit_type':'current_spawner'},'operators':[{'operator_type':'apply_buff','buff':reveal}]}
    for event in counter['trigger_event_actions']:
        if event['trigger_event_type']!='on_buff_started':event['action_group']['constraint']['constraints'].append(copy.deepcopy(has_cloak))
        if event['trigger_event_type']=='on_current_spawner_spawned_torpedo':
            action=copy.deepcopy(apply_reveal);action['constraint']=copy.deepcopy(event['action_group']['actions'][1]['constraint']);event['action_group']['actions'].insert(2,action)
        if event['trigger_event_type']=='on_unit_damaged_by_current_spawner':event['action_group']['actions'].insert(1,copy.deepcopy(apply_reveal))
    counter['gui']['name']=controller+'.name'
    for line in counter['gui']['tooltip_line_groups'][0]['lines']:
        line['label_text']=controller+('.count' if line['value_id']=='launch_count_memory' else '.deadline')
    optional[controller+'.buff']=counter
    ca=read(inputs[1]/'expanse05_launch_probe.ability');ca['action_data_source']=cloakid;ca['passive_actions']['persistant_buff']=controller;ca['gui'].update(name=controller+'.name',description=controller+'.description');optional[controller+'.ability']=ca
    ads=read(inputs[1]/'expanse05_launch_probe.action_data_source')
    ads['action_values'] += [{'action_value_id':k,'action_value':{'values':[n]}} for k,n in [('cloak_alpha_value',.3),('cloak_fade_duration_value',3.),('amun_cloak_quality',4.),('amun_reveal_quality',-5.),('cooldown_time_value',30.)]]
    optional[cloakid+'.action_data_source']=ads
    source_cloak=read(a.game/'entities/dlc3_herald_cloak_frigate_cloak.buff');source_ability=read(a.game/'entities/dlc3_herald_cloak_frigate_cloak.ability')
    cb={k:copy.deepcopy(source_cloak[k])for k in ['version','provides_cloak','required_product','cloak_alpha_value','cloak_fade_duration_value','stacking_limit','stacking_ownership_type','gui']}
    cb['unit_modifiers']=[{'modifier_type':'cloak_quality','value_behavior':'additive','value_id':'amun_cloak_quality'}];cb['restart_other_stacked_buffs_when_started']=False;cb['stacking_limit']['stacking_limit_met_behavior']='preserve_existing_buff';cb['gui']['name']=cloakid+'.name';optional[cloakid+'.buff']=cb
    active=copy.deepcopy(source_ability);active['level_source']='fixed_level_0';active.pop('level_prerequisites');active['action_data_source']=cloakid;active['active_actions'].pop('ai_only_auto_cast')
    active['active_actions']['actions']['actions'][0]['operators']=[{'operator_type':'apply_buff','buff':cloakid}]
    active['gui'].update(name=cloakid+'.name',description=cloakid+'.description');optional[cloakid+'.ability']=active
    rb=read(a.game/'entities/dlc3_herald_cloak_frigate_cloak_damage_dealt_degrade.buff');rb['active_duration']='reveal_seconds';rb['unit_modifiers'][0]['value_id']='amun_reveal_quality';rb['stacking_limit']['stacking_limit_met_behavior']='preserve_existing_buff';rb['gui']['name']=reveal+'.name'
    rb['gui']['tooltip_line_groups'][0]['lines'][0]['value_id']='amun_reveal_quality';optional[reveal+'.buff']=rb
    cloakloc={cloakid+'.name':'Cloak',cloakid+'.description':'Experimental Eidolon cloak. Three individual Amun torpedo launches are allowed before the fourth starts a fixed 60-second reveal window. A successful PDC or railgun hit also reveals; missed shots are not detected. Enemy cloak detectors still apply.',controller+'.name':'Cloak launch controller',controller+'.description':'Tracks launches independently of manual cloak toggles. A paired magazine reveals during its second pair. Counter and visibility persistence require runtime testing.',controller+'.count':'Counted individual launches',controller+'.deadline':'Reveal deadline (simulation seconds)',reveal+'.name':'Weapon signature revealed'}
    count=0
    for name,d in core.items():schema_check(name,d,a.sdk);count+=1
    optional_known=[]
    for name,d in optional.items():
        if name not in [cloakid+'.buff',reveal+'.buff']:schema_check(name,d,a.sdk);optional_known.append(name)
    observed=observed_cloak_check(optional,a.sdk,a.game)
    assert core['expanse06_amun_torpedo.unit']['health']['levels'][0]['armor_strength']==50
    assert not any('cloak' in k for k in core['expanse06_amun_torpedo.unit'])
    for name,d in core.items():write(a.output/'core/entities'/name,d)
    for name,d in optional.items():write(a.output/'cloak/entities'/name,d)
    write(a.output/'core/localization.json',coreloc);write(a.output/'cloak/localization.json',cloakloc)
    write(a.output/'core/ship-effect-aliases.json',required_aliases)
    recipe={'core_status':'READY FOR MAIN GEOMETRY/SHIP INTEGRATION; official component schemas PASS; runtime NOT RUN','core_files':list(core),'ship_id':'expanse_amun_ra','core_ship_abilities':['expanse06_amun_magazine',board],'private_weapons':[f'expanse06_amun_pdc_{i}'for i in range(3)]+['expanse06_amun_railgun'],'torpedo':{'unit':'expanse06_amun_torpedo','skin':'expanse06_amun_torpedo','mesh':spec['mesh_id'],'generated_assets':spec['game_directory'],'damage':900,'speed':1500,'penetration':1000,'hull':25,'armor':50,'armor_strength':50,'range':200000,'life':240},'mount_requirements':['Bind three actual PDC turrets and unit mounts; exactly one budget per physical assembly','Bind heavy railgun actual muzzle; definition damage3750/pen1000/10seconds','Add actual torpedo ability_positions to expanse06_amun_magazine.ability; no copied Tachi points','Bind ship-effect-aliases.json in Amun ship skin; boarding alias lives in boarding ADS and uses implicit center'], 'magazine':{'capacity':8,'per_pair':2,'pair_interval':10,'empty_reload':120,'three_individual_allowance':'Fourth individual projectile occurs within the second pair, normally t10. One-per5seconds was not substituted.'},'boarding':{'ability':board,'chance':.1,'delay':3,'range':6000,'cooldown':180,'semantics':'Accepted modeled shuttle with fixed delay; no physical arrival or interceptable pod','targets':'enemy capital_ship, fully built, detected, same well; named Rocinante excluded; other mod heroes need explicit exclusions','supply':'dynamic target supply at cast and rechecked at delayed attempt; queue/concurrent-transfer behavior runtime'},'optional_cloak':{'status':'ISOLATED CANDIDATE ONLY — NO ZIP; NOT FULL OFFICIAL SCHEMA PASS','files':list(optional),'append_ship_abilities':[controller,cloakid],'unit_hook':{'cloak_ability':cloakid},'unit_hook_source':'entities/dlc3_herald_cloak_frigate.unit','product_gate':source_cloak['required_product'],'cloak_quality':4,'reveal_quality_modifier':-5,'duration':60,'controller_independence':'Passive controller owns memory and reveal child. Cloak/decloak does not intentionally reset controller or remove reveal child. Engine lifecycle/save behavior untested.','damage_policy':'Only private tagged PDC/rail successful hits trigger reveal; torpedo impacts excluded. Misses do not reveal. No copied stock generic damage-dealt degradation, shield or auto-acquisition mutation.','continued_events':'Do not extend reveal deadline; count restarts after60s. Manual cloak is optional and no auto-cloak cast is added.'},'unit_limit':{'tag':'expanse_amun_ra','unit_limit':6,'semantics':'per player empire, not all players sharing faction'},'validation':'validate_components(package, candidate, sdk, cloak=False) supplements main whole-package checks; never use observed extension checks as official schema PASS'}
    recipe.update(core_abilities=recipe['core_ship_abilities'],railgun='expanse06_amun_railgun',pdcs=[f'expanse06_amun_pdc_{i}'for i in range(3)],boarding_model_override={'ability_mesh_point':'weapon.boarding.0','ADS_alias_particle':'expanse06_boarding_pod_visual','scope':'Only these2 exact fields; delay/chance/filter/supply untouched; enable validator boarding_model=True'})
    write(a.output/'integration-recipe.json',recipe)
    assert frozen=={str(p.relative_to(a.base)):sha(p)for p in a.base.rglob('*')if p.is_file()},'Frozen0.4.1 changed'
    write(a.output/'offline-validation.json',{'status':'PASS core components; optional cloak only separately evidence-checked','runtime':'NOT RUN','official_schema_pin':PIN,'pinned_schema_count':len(snap['files']),'core_official_schema_count':count,'optional_known_schema_files':optional_known,'optional_cloak_observed_validation':observed,'unchanged_source_file_count':len(frozen),'source_sha256':frozen,'candidate_sha256':{str(p.relative_to(a.output)):sha(p)for p in sorted(a.output.rglob('*'))if p.is_file()},'torpedo_compiler_spec_sha256':sha(a.torpedo_worker/'audit/torpedo05-b/integration-spec.json')})
    print(f'PASS {count} core schemas; optional cloak isolated with explicit observed extension checks. {len(frozen)} old files unchanged. '+str(a.output))
if __name__=='__main__':main()
