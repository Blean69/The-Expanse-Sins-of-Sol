#!/usr/bin/env python3
"""Private Donnager10 weapons/abilities; game, SDK, accepted package read-only."""
import argparse,copy,hashlib,json
from pathlib import Path
import jsonschema
ROOT=Path(__file__).resolve().parents[1]
PIN='8e061033afe53b1393eaefd56617a3fd041eeb5f'
PREFIX='expanse10_donnager'
SCHEMA={'.weapon':'weapon','.unit':'unit','.ability':'ability','.buff':'buff','.action_data_source':'action-data-source'}
def read(p):return json.loads(Path(p).read_text(encoding='utf-8-sig'))
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def write(p,d):p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(d,indent=2)+'\n')
def renamed(x,old,new):
    if isinstance(x,dict):return {k:renamed(v,old,new)for k,v in x.items()}
    if isinstance(x,list):return [renamed(v,old,new)for v in x]
    return x.replace(old,new) if isinstance(x,str) else x
def vals(d):return {x['action_value_id']:x['action_value']for x in d['action_values']}
def setvals(d,mapping):
    v=vals(d)
    for k,n in mapping.items():v[k]['values']=[n]
def av(k,n):return {'action_value_id':k,'action_value':{'values':[n]}}
def actor(t='current_spawner'):return {'unit_type':t}
def walk(d,path=''):
    if isinstance(d,dict):
        for k,v in d.items():
            yield k,v,path+'/'+k
            yield from walk(v,path+'/'+k)
    elif isinstance(d,list):
        for i,v in enumerate(d):yield from walk(v,path+'/'+str(i))
def has_creation(action):return any(k=='operator_type' and v=='create_torpedo' for k,v,_ in walk(action))

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--base',type=Path,required=True);ap.add_argument('--game',type=Path,required=True);ap.add_argument('--sdk',type=Path,required=True);ap.add_argument('--source-root',type=Path,default=Path('/run/media/haker/NVME 2/expanse-mod'));ap.add_argument('--output',type=Path,default=ROOT/'build/donnager10-a/final');a=ap.parse_args()
    assert a.output.resolve().is_relative_to(ROOT/'build/donnager10-a') and not a.output.exists(),'Fresh owned output required'
    snap=read(a.source_root/'audit/schema-comparison.json');assert snap['official_commit']==PIN
    for r in snap['files']:
        b=(a.sdk/r['path']).read_bytes();assert hashlib.sha1(b'blob '+str(len(b)).encode()+b'\0'+b).hexdigest()==r['official_git_blob']
    frozen={str(p.relative_to(a.base)):sha(p)for p in a.base.rglob('*')if p.is_file()};evidence={}
    def base(rel):
        p=a.game/rel
        if not p.is_file():raise SystemExit('BLOCKED missing installed dependency '+str(p))
        evidence[rel]={'sha256':sha(p),'bytes':p.stat().st_size};return read(p)
    ank=base('entities/trader_loyalist_titan.unit');ragnarov=base('entities/trader_rebel_titan_rail_gun.weapon');starbase=base('entities/trader_starbase_self_destruct_on_self.buff');explosionADS=base('entities/trader_starbase_self_destruct.action_data_source')
    for n in ['vasari_battle_capital_ship_volatile_nanites_on_target.buff','trader_rapid_autoloader_unit_item.action_data_source','trader_pirate_mercenary_base_unit_item.ability','vasari_overseer_tower.ability','trader_radiation_bomb.unit_item','trader_flak_burst.unit_item','trader_salvage_kit.unit_item','trader_combat_repair_system.unit_item','trader_loyalist_titan_hull_plating_0.unit_item']:
        base('entities/'+n)
    staged={};localization={};light=PREFIX+'_light_magazine';heavy=PREFIX+'_heavy_magazine';heavyunit=PREFIX+'_heavy_torpedo';reactor=PREFIX+'_reactor';launch=PREFIX+'_launch_corvette';boarding=PREFIX+'_marines';death=PREFIX+'_reactor_breach'
    # Exactly sixteen independent physical PDC budgets, four stations per sector.
    pdcsource=read(a.base/'entities/expanse_polish_pdc_0.weapon')
    for i in range(16):
        w=copy.deepcopy(pdcsource);w.pop('turret');w['damage']=14.;w['name']=PREFIX+'.pdc.name';assert w['cooldown_duration']==.25 and w['penetration']==0;staged[f'{PREFIX}_pdc_{i}.weapon']=w
    railsource=read(a.base/'entities/expanse03_hero_railgun.weapon')
    for i in range(2):
        w=copy.deepcopy(railsource);w.update(damage=5000.,penetration=1500.,cooldown_duration=20.,name=PREFIX+'.rail.name');staged[f'{PREFIX}_rail_{i}.weapon']=w
    localization.update({PREFIX+'.pdc.name':'Donnager PDC',PREFIX+'.rail.name':'Donnager heavy railgun'})
    base('entities/trader_torpedo_cruiser_torpedo.unit') # Retain installed benchmark evidence only.
    projectile=read(a.base/'entities/expanse04_light_torpedo.unit');projectile['physics']['max_linear_speed']=750.;projectile['ai']['attack_target_type_groups']=['defense_starbase_titan'];staged[heavyunit+'.unit']=projectile
    assert projectile['health']['levels'][0]=={'max_hull_points':50.,'max_armor_points':100.,'armor_strength':50.}
    magazine_source='expanse03_torpedo_magazine'
    boost_actions=[]
    for memory,deadline in [('next_pair_ready','magazine_next_pair_ready_value'),('reload_ready','magazine_reload_ready_value')]:
        boost_actions.append({'action_type':'change_buff_memory_float_value','float_variable':memory,'math_operators':[{'operator_type':'subtract','operand_value':'donnager_reactor_extra_progress_tick'}],'constraint':{'constraint_type':'composite_and','constraints':[{'constraint_type':'unit_passes_unit_constraint','unit':actor(),'unit_constraint':{'constraint_type':'has_buff','buff':reactor,'include_pending_buffs':False}},{'constraint_type':'value_comparison','value_a':deadline,'comparison_type':'greater_than','value_b':'common_simulation_time_value'}]}})
    for ident,is_heavy in [(light,False),(heavy,True)]:
        for ext in ['ability','buff','action_data_source']:
            d=renamed(read(a.base/'entities'/(magazine_source+'.'+ext)),magazine_source,ident)
            if ext=='ability':
                d.pop('ability_positions',None);d['gui'].update(name=ident+'.name',description=ident+'.description')
            elif ext=='buff':
                actions=d['time_actions'][0]['action_group']['actions']
                if is_heavy:
                    found=False;kept=[]
                    for action in actions:
                        if has_creation(action):
                            if found:continue
                            found=True
                            action=renamed(action,'expanse04_light_torpedo',heavyunit)
                            action=renamed(action,'expanse04_light_torpedo_muzzle','trader_torpedo_cruiser_torpedo_weapon_muzzle')
                            # Replacement ordering above may have changed alias prefix too.
                            action=renamed(action,heavyunit+'_muzzle','trader_torpedo_cruiser_torpedo_weapon_muzzle')
                        kept.append(action)
                    actions[:]=kept
                actions[:0]=copy.deepcopy(boost_actions)
            else:
                d['action_values'].append(av('donnager_reactor_extra_progress_tick',.125))
                assert vals(d)['magazine_poll_interval_value']['values']==[.25]
                if is_heavy:
                    setvals(d,{'heavy_torpedo_damage_value':4000.,'heavy_torpedo_armor_penetration_value':1500.,'heavy_torpedo_torpedo_speed_value':750.,'heavy_torpedo_torpedo_hull_value':50.,'heavy_torpedo_torpedo_armor_value':100.,'heavy_torpedo_torpedo_count_value':4.,'heavy_torpedo_torpedo_lifetime_value':300.,'combat03_torpedoes_per_interval_value':1.,'combat03_interval_count_value':4.,'combat03_interval_value':15.,'magazine_capacity_value':4.,'magazine_pair_count_value':1.,'magazine_pair_interval_value':15.})
                    for f in d['target_filters']:f['target_filter']['unit_types']=['starbase','titan']
            staged[ident+'.'+ext]=d
        localization[ident+'.ammo_label']='Torpedoes remaining'
        localization[ident+'.name']='Heavy torpedo magazine' if is_heavy else 'Martian light torpedoes'
        localization[ident+'.description']=('Four heavy torpedoes, one every 15 seconds at a detected enemy starbase or titan in this well; 120-second reload after empty.' if is_heavy else 'Eight Martian torpedoes, two every 10 seconds at detected enemies in this well; 120-second reload after empty.')+' Reactor overdrive accelerates firing and reload progress by 50% while active.'
    # Instant activation: 30 active + 120 recovery =150 activation-to-activation.
    ra=read(a.base/'entities/expanse_roci_overcharged_reactor.ability');ra=renamed(ra,'expanse_roci_overcharged_reactor',reactor);ra['active_actions'].update(cooldown_reset_type='on_start_use_ability',execute_time=0.,stop_time=0.,stop_use_type='on_stop_time_elapsed');ra['gui'].update(name=reactor+'.name',description=reactor+'.description');staged[reactor+'.ability']=ra
    rb=read(a.base/'entities/expanse_roci_overcharged_reactor.buff');rb['weapon_modifiers']=[{'buff_weapon_modifier_id':'reload_rate'}];staged[reactor+'.buff']=rb
    rd=read(a.base/'entities/expanse_roci_overcharged_reactor.action_data_source');setvals(rd,{'cooldown':150.,'duration':30.,'antimatter':100.,'speed':.5});rd['action_values'].append(av('reload_duration_scalar',-1/3));rd['buff_weapon_modifiers']=[{'buff_weapon_modifier_id':'reload_rate','buff_weapon_modifier':{'modifier_type':'cooldown_duration','value_behavior':'scalar','value_id':'reload_duration_scalar','tags':['physical']}}];staged[reactor+'.action_data_source']=rd
    localization.update({reactor+'.name':'Reactor overdrive',reactor+'.description':'For 30 seconds: +50% maximum speed and 50% faster weapon and torpedo-magazine progress. Then 120 seconds of recovery. Costs 100 antimatter.'})
    # Paid, one exact corvette; no factory build_kind roster expansion.
    la=base('entities/trader_pirate_mercenary_base_unit_item.ability');la['action_data_source']=launch;la['level_source']='fixed_level_0';la['active_actions']['metal_cost']='launch_metal';op=la['active_actions']['actions']['actions'][0]['operators'][0];op['units']={'required_units':[{'unit':'trader_light_frigate','count':[1,1]}]};op['in_hyperspace']=False;op['check_research_prerequisites']=True
    la['gui']={'hud_icon':'trader_light_frigate_hud_icon','name':launch+'.name','description':launch+'.description'};staged[launch+'.ability']=la
    cobalt=read(a.base/'entities/trader_light_frigate.unit')['build'];staged[launch+'.action_data_source']={'version':0,'action_values':[av('pirate_mercenary_base_cooldown_time_value',20.),av('pirate_mercenary_base_credits_cost_value',cobalt['price']['credits']),av('launch_metal',cobalt['price']['metal']),av('pirate_mercenary_base_available_supply_value',cobalt['supply_cost']),av('pirate_mercenary_base_arrival_delay_value',0.)]}
    localization.update({launch+'.name':'Launch MCRN corvette',launch+'.description':'Deploy one MCRN Corvette-class near the Donnager for 300 credits and 55 metal. Requires 5 free supply. 20-second cooldown. Deployment placement is controlled by the engine.'})
    for ext in ['ability','buff','action_data_source']:
        d=renamed(read(a.base/'entities'/('expanse06_amun_boarding.'+ext)),'expanse06_amun_boarding',boarding)
        if ext=='ability':d['gui'].update(name=boarding+'.name',description=boarding+'.description')
        if ext=='action_data_source':setvals(d,{'capture_chance':.4,'boarding_crew_cooldown_time_value':600.})
        staged[boarding+'.'+ext]=d
    localization.update({boarding+'.name':'Launch marine boarding pod',boarding+'.description':'Launch a modeled pod: one 40% capture attempt after a 3-second delay against a valid enemy capital ship. Requires free fleet supply. 10-minute cooldown. The timed pod visual cannot be intercepted.',boarding+'.chance':'Capture chance per attempt'})
    # Actual death trigger, not a low-health self-destruct active ability.
    ea=base('entities/trader_starbase_self_destruct.ability');ea.pop('active_actions');ea['action_data_source']=death;ea['level_source']='fixed_level_0';ea['passive_actions']={'persistant_buff':death,'only_if_owner_unit_operational':False};ea['gui']={'hud_icon':ea['gui']['hud_icon'],'name':death+'.name','description':death+'.description'};staged[death+'.ability']=ea
    actions=copy.deepcopy(starbase['time_actions'][0]['action_group']['actions']);actions[0]['include_radius_origin_unit']=False;actions[0]['include_y_axis_in_radius_check']=True;actions[1]['operators']=[x for x in actions[1]['operators']if x['operator_type']!='make_dead'];actions.append({'action_type':'make_buff_dead'})
    eb={'version':0,'make_dead_on_current_spawner_made_dead':False,'make_dead_on_source_ability_released':False,'stacking_limit':{'stacking_limit':'fixed_one','stacking_limit_met_behavior':'preserve_existing_buff'},'stacking_ownership_type':'for_all_players','restart_other_stacked_buffs_when_started':False,'trigger_event_actions':[{'trigger_event_type':'on_current_spawner_made_dead','action_group':{'actions':actions}}]};staged[death+'.buff']=eb
    ed=copy.deepcopy(explosionADS);ed['target_filters']=[ed['target_filters'][0]];ed['target_filters'][0]['target_filter']['ownerships']=['self','ally','friendly','enemy'];ed['target_filters'][0]['target_filter']['respect_can_be_targeted_permissions']=False;ed['effect_alias_bindings']=[ed['effect_alias_bindings'][0]];staged[death+'.action_data_source']=ed
    localization.update({death+'.name':'Catastrophic reactor breach',death+'.description':'On destruction, a reactor blast deals 10,000 damage with 1,000 penetration within 10,000 range to friendly, allied and enemy ships, strikecraft, torpedoes and structures. Keep your fleet clear.'})
    # Resolve exact ship-side weapon aliases without copying vanilla effects.
    aliases={}
    for path in [a.base/'entities/trader_light_frigate.unit_skin',a.base/'entities/expanse_rocinante_hero.unit_skin',a.game/'entities/trader_torpedo_cruiser.unit_skin']:
        for binding in read(path)['skin_stages'][0]['effects']['effect_alias_bindings']:aliases[binding['alias_name']]=binding
    needed={'expanse04_light_torpedo_muzzle','trader_torpedo_cruiser_torpedo_weapon_muzzle'}
    for name,w in staged.items():
        if name.endswith('.weapon'):needed.update(v for k,v in w['effects'].items()if isinstance(v,str)and k.endswith('_effect'))
    for name,d in staged.items():
        schema=read(a.sdk/'json_schemas'/(SCHEMA[Path(name).suffix]+'-schema.json'))
        jsonschema.Draft7Validator(schema).validate(d)
        error=next(jsonschema.Draft202012Validator(schema).iter_errors(d),None)
        if error:raise AssertionError(name+': '+error.message)
    # Budget/cadence invariants independent of the unknown hull mount integration.
    assert sum(w['damage']/w['cooldown_duration']for n,w in staged.items()if '_pdc_'in n)==896
    for ident,count in [(light,2),(heavy,1)]:
        assert sum(k=='operator_type' and v=='create_torpedo'for k,v,_ in walk(staged[ident+'.buff']))==count
    assert vals(staged[boarding+'.action_data_source'])['capture_chance']['values']==[.4]
    for name,d in staged.items():write(a.output/'entities'/name,d)
    write(a.output/'localization.json',localization);write(a.output/'ship-effect-aliases.json',[aliases[n]for n in sorted(needed)])
    items={}
    for n in ['trader_radiation_bomb','trader_flak_burst','trader_salvage_kit','trader_combat_repair_system','trader_loyalist_titan_hull_plating_0']:
        d=read(a.game/'entities'/(n+'.unit_item'));items[n]={k:d[k]for k in ['item_type','required_unit_tags','required_item_access_tags','consumable_stack_count','build_group_id','build_prerequisites']if k in d}
    evidence_doc={'Ankylon':{k:ank[k]for k in ['physics','health','items','tags','item_access_tags','build']},'rail_benchmark':ragnarov,'item_examples':items,'whole_ship_PDC':{'guns':16,'damage':14,'cooldown':.25,'raw_per_gun':56,'raw_all':896,'four_gun_sector':224,'eight_gun_overlap':448,'source_filter':pdcsource['uniforms_target_filter_id'],'source_groups':pdcsource['attack_target_type_groups']},'installed_source_files':evidence}
    write(a.output/'source-evidence.json',evidence_doc)
    abilities=[light,heavy,launch,reactor,boarding,death]
    recipe={'status':'OFFLINE PRIVATE COMPONENT CANDIDATE; no unit/mount/package/runtime claim','core_abilities':abilities,'unit_ability_sets':[{'abilities':abilities}],'pdc_ids':[f'{PREFIX}_pdc_{i}'for i in range(16)],'rail_ids':[f'{PREFIX}_rail_{i}'for i in range(2)],'light_projectile':'expanse04_light_torpedo','heavy_projectile':heavyunit,'magazines':{'light':{'ability':light,'positions':'Main/B actual front mounts','capacity':8,'count_per_event':2,'event_seconds':10,'reload':120,'damage':750,'penetration':1000,'speed':1250},'heavy':{'ability':heavy,'positions':'Main/B actual rear mounts','capacity':4,'count_per_event':1,'event_seconds':15,'reload':120,'damage':4000,'penetration':1500,'speed':750,'lifetime':300,'targets':['starbase','titan'],'hull':50,'armor':100,'armor_strength':50}},'reactor':{'ability':reactor,'duration':30,'activation_cooldown':150,'recovery_after_duration':120,'speed_scalar':.5,'weapon_cooldown_scalar':-1/3,'rate_multiplier':1.5,'private_magazine_deadline_extra_progress_per_0_25s_tick':.125,'AM_cost':100,'notes':'Instant activation with on_start_use cooldown; no watched buff/channel; private magazine clocks accelerated in addition to PDC/rail. No ability cooldown acceleration.'},'launch':{'ability':launch,'unit':'trader_light_frigate','count':1,'credits':300,'metal':55,'supply':5,'cooldown':20,'in_hyperspace':False,'placement':'At caster via spawn_units, engine-controlled location; no invented hangar offset. Not a native production queue.','runtime_gates':['Spawn placement and correct owner','Insufficient resources/supply and concurrent actions','Costs/refund if engine refuses spawn']},'boarding':{'ability':boarding,'chance':.4,'cooldown':600,'delay':3,'source':'working Amun09 boarding','visual':'existing expanse06_boarding_pod_visual, stock-derived timed model; main binds Donnager actual point','patchable_visual_fields':['play_weapon_effects.mesh_point','ADS alias particle_effect']},'death':{'ability':death,'event':'on_current_spawner_made_dead','radius':10000,'damage':10000,'penetration':1000,'wave_speed':5000,'delay_before_damage_schedule':0,'max_wave_travel_seconds':2,'owner_filter':['self','ally','friendly','enemy'],'include_radius_origin_unit':False,'respect_target_permissions':False,'runtime_gates':['Own and allied targets actually take damage','Travel-delayed damage survives source/buff death','Multiple nearby reactor chain explosions and performance','Phase-space/scuttle/ownership/context behavior']},'unit_fields_from_Ankylon':{'physics':ank['physics'],'health':ank['health'],'items':ank['items']},'item_scope':{'recommended_tags':['capital_ship','expanse_donnager'],'items':ank['items'],'avoid_titan_tag':'Would share existing player titan count cap','generic_consumables':'They are ship_component items accepting capital_ship;8slots suffice','Ankylon_exclusive_items':'Require titan tag +trader_loyalist_titan access; not necessary for generic consumables, do not silently grant'},'integration_requirements':['One outer abilities set with all6 coexisting abilities','Actual16PDC/2rail mounts, turret frames and2magazine position arrays by B/main','Main ship uses user-confirmed shared vanilla titan limit, titan build route and8itemslots','Main add namespaced manifests and resolve aliases including inherited private light projectile/boarding model','Do not modify any existing ship/weapon/magazine/ability'], 'all_entity_files':list(staged)}
    recipe['heavy_visual']={'source':'accepted expanse04_light_torpedo private visual/spatial data','length':16.510756,'beam':2.936114,'reason':'Fits measured6.3-diameter aft tubes; heavy differs by damage, speed, launch position, cadence and label','older_Ogrov_candidate':'Preserved in final-reviewed; do not package that wider hull'}
    recipe['ship_id']='expanse_donnager_battleship';recipe['mod_id']='expanse_donnager10'
    recipe['shared_titan_limit']={'confirmed_user_choice':True,'tags':['titan','expanse_donnager_battleship'],'build_kind':'titan','rule':'Participates in existing titan cap; no independent private cap or original titan limit edit'}
    recipe['item_scope']={'recommended_tags':['titan','expanse_donnager_battleship'],'items':ank['items'],'generic_consumables':'ship_component consumables accepting titan;8slots shared with other ship components','Ankylon_exclusive_items':'Do not add trader_loyalist_titan item_access_tag; preserve proprietary upgrade exclusion'}
    write(a.output/'integration-recipe.json',recipe)
    assert frozen=={str(p.relative_to(a.base)):sha(p)for p in a.base.rglob('*')if p.is_file()},'Accepted base changed'
    write(a.output/'offline-validation.json',{'status':'PASS candidate schemas and structural budgets; runtime NOT RUN','pinned_schema_count':len(snap['files']),'entity_schema_count':len(staged),'source_files_unchanged':len(frozen),'source_hashes':frozen,'candidate_sha256':{p.name:sha(p)for p in sorted((a.output/'entities').iterdir())}})
    print(f'PASS {len(staged)} candidate schemas; {len(frozen)} accepted base files unchanged. '+str(a.output))
if __name__=='__main__':main()
