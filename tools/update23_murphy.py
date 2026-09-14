"""Private UNN escort prototype; never rewrites accepted fleet definitions."""
import copy
from pathlib import Path
from update20_fleet import ROOT,GAME
from validate_experiments import read,require,sha256
ID='expanse23_murphy'

def changes(base):
    spec=read(ROOT/'audit/update23-murphy/integration-spec.json');edits={};origins={};loc={};art={}
    def get(n,k):
        p=base/'entities'/f'{n}.{k}';return read(p if p.exists() else GAME/'entities'/p.name)
    def put(n,k,d,source):
        rel=f'entities/{n}.{k}';edits[rel]=d;p=base/'entities'/f'{source}.{k}';origins[rel]=str(p if p.exists() else GAME/'entities'/p.name)
    for rel,h in spec['files'].items():
        p=Path(spec['output_game'])/rel;require(sha256(p)==h,'Unreviewed Murphy asset '+rel)
        if (base/rel).exists():require(sha256(base/rel)==h,'Murphy art collision '+rel)
        else:art[rel]=p
    u=get('expanse_mcrn_corvette','unit');u['spatial'].update(copy.deepcopy(spec['spatial']))
    u['build'].update(build_time=60.,price={'credits':1200.,'metal':450.,'crystal':150.},supply_cost=95,prerequisites=[['trader_unlock_antiarmor_frigate']])
    u['physics'].update(max_linear_speed=1350.,max_angular_speed=25.,time_to_max_linear_speed=5.)
    u['health']['durability']=150.;h=u['health']['levels'][0];h.update(max_hull_points=1400.,max_armor_points=1000.,armor_strength=50.,max_shield_points=0.)
    u['tags']=['frigate',ID];u['skin_groups']=[{'skins':[ID]}];u['item_builds']=[]
    u['weapons']={'weapons':[],'max_range_weapon_index':4}
    pdc=ID+'_pdc';w=get('expanse15_truman_pdc_0','weapon');w['name']=pdc+'.name';w['turret']=copy.deepcopy(spec['rigs'][0]['turret_override']);put(pdc,'weapon',w,'expanse15_truman_pdc_0')
    for rig in spec['rigs']:
        m={k:copy.deepcopy(rig[k]) for k in ['mesh_point','up','forward','yaw_arc','pitch_arc']};m.update(weapon=pdc,weapon_position=rig['position']);u['weapons']['weapons'].append(m)
    rail=ID+'_rail';w=get('expanse06_amun_railgun','weapon');w.update(name=rail+'.name',damage=750.,penetration=800.,cooldown_duration=30.,tags=['rail_gun','physical'])
    put(rail,'weapon',w,'expanse06_amun_railgun')
    for i in range(2):
        point=next(x for x in spec['meshpoints'] if x['name']=='weapon.rail.'+str(i))
        u['weapons']['weapons'].append({'weapon':rail,'mesh_point':point['name'],'weapon_position':point['translation'],'non_turret_muzzle_positions':[point['translation']],
            'forward':[0,0,1 if i==0 else -1],'up':[0,1,0],'yaw_arc':{'min_angle':-5.,'max_angle':5.},'pitch_arc':{'min_angle':0.,'max_angle':0.}})
    u['ai']['attack_target_type_groups_matching_weapon']=pdc
    u['ai']['attack_target_type_groups']=copy.deepcopy(edits['entities/'+pdc+'.weapon']['attack_target_type_groups'])
    mag=ID+'_light_magazine';old='expanse15_truman_light_magazine'
    for kind in ['ability','buff','action_data_source']:
        d=get(old,kind)
        # Exact identifier substitution, including local GUI keys, is private.
        def replace(o):
            if isinstance(o,str):return o.replace(old,mag)
            if isinstance(o,list):return [replace(x) for x in o]
            if isinstance(o,dict):return {k:replace(v) for k,v in o.items()}
            return o
        d=replace(d)
        if kind=='ability':d['ability_positions']=[{'position':v,'rotation':[1,0,0,0,1,0,0,0,1]} for v in spec['torpedo_ports']]
        if kind=='buff':
            actions=d['time_actions'][0]['action_group']['actions'];shots=[x for x in actions if any(y.get('operator_type')=='create_torpedo' for y in x.get('position_operators',[]))]
            require(len(shots)==6,'Unexpected Truman magazine implementation')
            # Repeated shot dictionaries compare equal: select by position,
            # never by dict equality, or all six operations disappear.
            shot_indices=[i for i,x in enumerate(actions) if any(y.get('operator_type')=='create_torpedo' for y in x.get('position_operators',[]))]
            d['time_actions'][0]['action_group']['actions']=[x for i,x in enumerate(actions) if i not in shot_indices[2:]]
            require(sum(any(y.get('operator_type')=='create_torpedo' for y in x.get('position_operators',[])) for x in d['time_actions'][0]['action_group']['actions'])==2,'Murphy must create exactly two torpedoes per launch')
        if kind=='action_data_source':
            numbers={'heavy_torpedo_torpedo_count_value':8,'magazine_capacity_value':8,'magazine_pair_count_value':2,'combat03_torpedoes_per_interval_value':2,'combat03_interval_count_value':4}
            for v in d['action_values']:
                if v['action_value_id'] in numbers:v['action_value']['values']=[numbers[v['action_value_id']]]*len(v['action_value']['values'])
        put(mag,kind,d,old)
    u['abilities']=[{'abilities':[mag,'expanse11_no_shields']}];put(ID,'unit',u,'expanse_mcrn_corvette')
    skin=get('expanse15_truman','unit_skin');skin.pop('name',None)
    st=skin['skin_stages'][0];st['unit_mesh']=spec['skin_contract']['unit_mesh'];st['child_mesh_alias_bindings']=spec['skin_contract']['child_mesh_alias_bindings']
    st['gui'].update(name=ID+'.name',description=ID+'.description');st['gui'].pop('special_operation_names',None)
    effects=st['effects'];effects['exhaust_effects']=spec['skin_contract']['exhaust_effects']
    effects['hyperspace_effects']=get('trader_skirmisher_corvette_frigate','unit_skin')['skin_stages'][0]['effects']['hyperspace_effects']
    effects.pop('flair_effects',None);effects.pop('level_up_effect',None);effects.pop('level_up_sound',None)
    put(ID,'unit_skin',skin,'expanse15_truman')
    loc.update({ID+'.name':'UNN Murphy-class Destroyer',ID+'.description':'UNN light escort using a fan interpretation of the RPG class. 95supply,1400hull/1000armor,1350speed. Four85DPS PDCs; two fixed fore/aft light rails,750damage/30seconds each. Two light torpedoes per10seconds,8round magazine,120second reload. No colony, siege, cloak or boarding system.',
        pdc+'.name':'UNN escort PDC',rail+'.name':'UNN light spinal railgun',mag+'.name':'Murphy light torpedo magazine',mag+'.description':'Two UNN light torpedoes every10seconds;8total, then120seconds to reload after the final pair.750base damage each,2125speed,30second fuel; normal UNN research and interception rules.',mag+'.ammo_label':'Torpedoes remaining'})
    report={'unit':ID,'factions':['unn'],'source_art':spec['source'],'stats':{'supply':95,'cost':u['build']['price'],'seconds':60,'hull':1400,'armor':1000,'speed':1350,'pdc_count':4,'pdc_dps_per_mount':85,'rail_damage':750,'rail_interval':30,'rail_pierce':800,'rail_arcs':'fixed fore/aft,5degrees yaw,0pitch','torpedoes_per_pair':2,'magazine':8,'pair_seconds':10,'reload_seconds':120},
        'adaptation':'Fan hull, provisional102m scale; four PDC and fixed rail locations are mod interpretations. Reserved hull-integrated rail origins have no additional animated gun mesh. Two opposed rails cannot both concentrate straight ahead. Native orbit behavior fromTachi, ordinary native hyperspace effect until private phase art is authored.',
        'runtime':'NOT RUN','unit_tag_entries_append':[{'name':ID,'localized_name':ID+'.name'}]}
    return edits,loc,origins,art,report
