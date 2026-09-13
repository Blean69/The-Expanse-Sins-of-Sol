#!/usr/bin/env python3
"""Reviewable ability deltas; never writes a unit, skin, uniform or installed mod."""
import argparse, copy, hashlib, json
from pathlib import Path
import jsonschema

ROOT = Path(__file__).resolve().parents[1]
MAIN = ROOT if (ROOT / 'audit/schema-comparison.json').exists() and ROOT.name == 'expanse-mod' else ROOT.parent.parent / 'expanse-mod'
DRIVE = MAIN.parent
PIN = '8e061033afe53b1393eaefd56617a3fd041eeb5f'

def read(p): return json.loads(Path(p).read_text(encoding='utf-8-sig'))
def sha(p): return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def write(p, d):
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(d, indent=2) + '\n')
def walk(d):
    if isinstance(d, dict):
        for k,v in d.items():
            yield k,v
            yield from walk(v)
    elif isinstance(d,list):
        for v in d: yield from walk(v)
def rename(d, old, new):
    if isinstance(d,dict): return {k:rename(v,old,new) for k,v in d.items()}
    if isinstance(d,list): return [rename(v,old,new) for v in d]
    return d.replace(old,new) if isinstance(d,str) else d
def values(d): return {x['action_value_id']:x['action_value'] for x in d['action_values']}
def changed_paths(a,b,p=''):
    if type(a) is not type(b): return [p]
    if isinstance(a,dict):
        out=[]
        for k in sorted(a.keys()|b.keys()):
            out += [p+'/'+k] if k not in a or k not in b else changed_paths(a[k],b[k],p+'/'+k)
        return out
    if isinstance(a,list):
        if len(a)!=len(b): return [p]
        return [x for i,(u,v) in enumerate(zip(a,b)) for x in changed_paths(u,v,p+'/'+str(i))]
    return [] if a==b else [p]

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument('--base',type=Path,default=MAIN/'build/experiments/expanse_donnager10_pdc_audio')
    ap.add_argument('--game',type=Path,default=DRIVE/'SteamLibrary/steamapps/common/Sins2')
    ap.add_argument('--sdk',type=Path,default=DRIVE/'SteamLibrary/steamapps/common/Sins of a Solar Empire II - Mod Tools')
    ap.add_argument('--output',type=Path,default=ROOT/'build/update11-a/candidate')
    a=ap.parse_args(); audit=ROOT/'audit/update11-a'
    if a.output.exists(): raise SystemExit('Refusing existing candidate output '+str(a.output))
    if not a.output.resolve().is_relative_to(ROOT/'build/update11-a'): raise SystemExit('Output must stay in owned directory')
    pin=read(MAIN/'audit/schema-comparison.json'); assert pin['official_commit']==PIN
    for r in pin['files']:
        p=a.sdk/r['path']
        if not p.is_file(): raise SystemExit('MISSING pinned SDK dependency '+str(p))
        b=p.read_bytes(); assert hashlib.sha1(b'blob '+str(len(b)).encode()+b'\0'+b).hexdigest()==r['official_git_blob']
    baseline={str(p.relative_to(a.base)):sha(p) for p in a.base.rglob('*') if p.is_file()}
    assert baseline, 'Missing accepted package'
    files={}; local={}; evidence={}; deltas={}
    def source(name):
        p=a.base/'entities'/name
        if not p.is_file(): raise SystemExit('MISSING baseline definition '+str(p))
        evidence[str(p)] = sha(p)
        return read(p)
    launch='expanse10_donnager_launch_corvette'
    d=source(launch+'.ability'); before=copy.deepcopy(d)
    op=d['active_actions']['actions']['actions'][0]['operators'][0]
    assert op['operator_type']=='spawn_units'
    op['units']={'required_units':[{'unit':'expanse_mcrn_corvette','count':[1,1]}]}
    op['in_hyperspace']=True
    op['check_research_prerequisites']=False
    assert op['constrain_available_supply_to_owner_player'] is True
    d['gui']['hud_icon']='mcrn_corvette_hud_icon'
    d['gui']['tooltip_picture']='mcrn_corvette_tooltip_picture'
    d['gui']['tooltip_line_groups']=[{'lines':[{'rendering_type':'unit_icon_and_name','unit':'expanse_mcrn_corvette'},{'rendering_type':'single_value','label_text':'tooltip.supply_value_label','value_id':'pirate_mercenary_base_available_supply_value'}]}]
    files[launch+'.ability']=d; deltas[launch+'.ability']=changed_paths(before,d)
    d=source(launch+'.action_data_source'); before=copy.deepcopy(d)
    values(d)['pirate_mercenary_base_available_supply_value']['values']=[55.0]
    values(d)['pirate_mercenary_base_arrival_delay_value']['values']=[2.0]
    files[launch+'.action_data_source']=d; deltas[launch+'.action_data_source']=changed_paths(before,d)
    local[launch+'.description']='Deploy one MCRN Corvette-class as a reinforcement arriving after 2 seconds. Costs 300 credits and 55 metal; requires 55 free fleet supply. 20-second cooldown. Arrival placement is controlled by the engine.'
    for ident,chance,cooldown in [('expanse06_amun_boarding',.1,180),('expanse10_donnager_marines',.4,600)]:
        d=source(ident+'.action_data_source'); before=copy.deepcopy(d)
        assert d['target_filters'][0]['target_filter']['unit_types']==['capital_ship']
        d['target_filters'][0]['target_filter']['unit_types']=['capital_ship','super_capital_ship','titan']
        assert values(d)['capture_chance']['values']==[chance]
        assert values(d)['boarding_crew_cooldown_time_value']['values']==[float(cooldown)]
        files[ident+'.action_data_source']=d; deltas[ident+'.action_data_source']=changed_paths(before,d)
        local[ident+'.description']=f'Launch a boarding pod: one {int(chance*100)}% capture attempt after 3 seconds against a detected enemy capital ship, command ship or titan. Requires free fleet supply. {cooldown}-second cooldown. Rocinante is excluded. The timed visual cannot be intercepted. Captured titans may exceed the construction cap.'
    # Fresh magazine namespace: no changes to existing ship torpedo budgets.
    old='expanse03_torpedo_magazine'; new='expanse11_morrigan_magazine'
    for ext in ['ability','buff','action_data_source']:
        d=rename(source(old+'.'+ext),old,new)
        if ext=='ability':
            d.pop('ability_positions',None)  # Main supplies actual two tube frames.
        elif ext=='buff':
            actions=d['time_actions'][0]['action_group']['actions']; creation=[i for i,x in enumerate(actions) if any(k=='operator_type' and v=='create_torpedo' for k,v in walk(x))]
            assert len(creation)==2
            del actions[creation[1]]
        else:
            for k,n in {'magazine_capacity_value':4.,'magazine_pair_count_value':1.,'heavy_torpedo_torpedo_count_value':4.,'combat03_torpedoes_per_interval_value':1.}.items(): values(d)[k]['values']=[n]
        files[new+'.'+ext]=d
    local.update({new+'.name':'Morrigan light torpedoes',new+'.description':'Four Martian light torpedoes: one every 10 seconds, alternating between two bow tubes. Reloads 120 seconds after the fourth launch. Targets detected enemies in the same gravity well.',new+'.ammo_label':'Torpedoes remaining'})
    w=read(a.game/'uniforms/weapon.uniforms'); assert len(w['weapon_tags'])==19
    tag={'name':'expanse06_cloak_revealing_gun','localized_name':'expanse06_cloak_revealing_gun.name'}
    w['weapon_tags'].append(tag); local[tag['localized_name']]='Cloak-revealing gun'
    schema_names={'ability':'ability','buff':'buff','action_data_source':'action-data-source'}
    for name,d in files.items():
        schema=read(a.sdk/'json_schemas'/(schema_names[name.rsplit('.',1)[1]]+'-schema.json'))
        jsonschema.Draft7Validator(schema).validate(d); jsonschema.Draft202012Validator(schema).validate(d)
        write(a.output/'entities'/name,d)
    jsonschema.Draft202012Validator(read(a.sdk/'json_schemas/weapon-uniforms-schema.json')).validate(w)
    # Evaluate inherited concrete branch invariants, including delay-time supply recheck.
    for ident in ['expanse06_amun_boarding','expanse10_donnager_marines']:
        buff=source(ident+'.buff'); s=json.dumps(buff)
        assert 'player_has_available_supply' in s and 'capture_target_supply' in s and 'random_chance' in s
        constraints=files[ident+'.action_data_source']['target_filters'][0]['target_filter']['constraints']
        assert any(v=='expanse_rocinante_hero' for k,v in walk(constraints))
    m=values(files[new+'.action_data_source']); assert m['magazine_pair_interval_value']['values']==[10.] and m['magazine_reload_duration_value']['values']==[120.]
    assert sum(k=='operator_type' and v=='create_torpedo' for k,v in walk(files[new+'.buff']))==1
    assert any(k=='ability_position_picking_type' and v=='next_sequential' for k,v in walk(files[new+'.buff']))
    for rel in ['entities/trader_pirate_mercenary_base_unit_item.ability','entities/vasari_overseer_tower.ability','entities/dlc2_trader_loyalist_super_reserves.ability','entities/dlc2_trader_loyalist_super_capital_ship.unit','uniforms/weapon.uniforms']:
        p=a.game/rel; evidence[str(p)]=sha(p)
    assert 'super_capital_ship' in read(a.game/'entities/dlc2_trader_loyalist_super_capital_ship.unit')['tags']
    log=DRIVE/'SteamLibrary/steamapps/compatdata/1575940/pfx/drive_c/users/steamuser/AppData/Local/sins2/logs/sins2_log_318_[2026-09-13][06-34-54]_500.txt'
    excerpts=[]
    if log.is_file():
        lines=log.read_text(errors='replace').splitlines()
        for i,line in enumerate(lines):
            if 'unit_spawner] ASSERT(false)' in line or 'Found errors for' in line: excerpts.append('\n'.join(lines[max(0,i-3):i+6]))
        evidence[str(log)]=sha(log)
    write(audit/'runtime-log-evidence.json',{'log':str(log),'observed_excerpts':excerpts,'interpretation':'Engine asserts in unit_spawner immediately after use_ability. Wrong non-hyperspace path is a supported inference from stock patterns, not an observed fix.'})
    recipe={'status':'OFFLINE COMPONENTS PASS; main unit/skin integration and runtime tests required','files':list(files),'localization':local,'allowed_existing_deltas':deltas,'main_required_unit':'expanse_mcrn_corvette','main_required_unit_supply':55,'launch':{'in_hyperspace':True,'arrival_delay':2,'price':{'credits':300,'metal':55},'cooldown':20,'required_supply':55,'count':1,'runtime_unresolved':['Correct owner, arrival and location','Resource payment, full supply and simultaneous launch races','No unit_spawner assert']},'morrigan':{'ability':new,'ability_positions':'REQUIRED: main actual two bow tube position/frame records, not old Cobalt coordinates','firing':'one shot per10s;4rounds;120s empty reload;sequential tubes','projectile':'expanse04_light_torpedo','damage':750,'penetration':1000,'hull':50,'armor':100,'armor_strength':50},'main_unit_ai_fix':{'unit':'expanse_amun_ra','attack_target_type_groups_to_ignore':[],'reason':'Sole prior ignored group torpedo_strikecraft also appears in attack_target_type_groups and produces engine validation error'},'main_weapon_uniform':{'source':str(a.game/'uniforms/weapon.uniforms'),'source_sha256':sha(a.game/'uniforms/weapon.uniforms'),'append_weapon_tag':tag,'retain_other_fields':True,'expected_stock_tag_count':19},'boarding':{'target_types':['capital_ship','super_capital_ship','titan'],'Amun_chance':.1,'Amun_cooldown':180,'Donnager_chance':.4,'Donnager_cooldown':600,'capital_and_titan_supply_rechecks_preserved':True,'Rocinante_excluded':True,'capture_cap':'UNRESOLVED: change_owner_player has no cap field and action queries expose no global player tag count; captured titans may exceed construction cap. Test while already owning/queueing a titan. No shared construction cap is removed.'}}
    write(a.output/'integration-recipe.json',recipe); write(a.output/'localization.json',local)
    write(audit/'integration-recipe.json',recipe)
    assert baseline=={str(p.relative_to(a.base)):sha(p)for p in a.base.rglob('*')if p.is_file()}
    write(audit/'validation.json',{'status':'PASS candidate structural/schema checks; reference completeness depends on main private MCRN unit and Morrigan mount integration','runtime':'NOT RUN','official_pin':PIN,'schema_files_verified':len(pin['files']),'entity_schemas_passed':len(files),'main_uniform_contract_schema_passed':True,'accepted_files_unchanged':len(baseline),'candidate_sha256':{n:sha(a.output/'entities'/n)for n in files},'evidence_sha256':evidence,'pending_main_dependencies':['expanse_mcrn_corvette.unit with supply55','Morrigan ability_positions two actual frames','main weapon tag uniform append + localization','main Amun ignored group correction']})
    print('PASS',len(files),'candidate entity schemas and weapon uniform contract; runtime NOT RUN;',a.output)

if __name__=='__main__': main()
