"""Private Hephaestus and Laconian frigate definitions; shared access is separate."""
import copy,json
from pathlib import Path
from update20_fleet import ROOT,GAME
from validate_experiments import read,require
CONTRACTS=ROOT/'audit/update27-mars-laconia'

def changes(base,contracts=CONTRACTS):
    edits={};loc={};origins={};report={}
    def get(n,k):
        p=base/'entities'/f'{n}.{k}';return read(p if p.exists() else GAME/'entities'/p.name)
    def put(n,k,d,source):
        rel=f'entities/{n}.{k}';require(not (base/rel).exists(),'New hull overwrites accepted definition '+rel)
        edits[rel]=d;p=base/'entities'/f'{source}.{k}';origins[rel]=str(p if p.exists() else GAME/'entities'/p.name)
    def magazine(uid,old,ports,count,capacity,label,damage=None):
        name=uid+('_medium_magazine' if damage else '_light_magazine')
        for kind in ('ability','buff','action_data_source'):
            d=json.loads(json.dumps(get(old,kind)).replace(old,name))
            if kind=='ability':d['ability_positions']=[{'position':p['position'],'rotation':[1,0,0,0,1,0,0,0,1]} for p in ports]
            if kind=='buff':
                actions=d['time_actions'][0]['action_group']['actions']
                ix=[i for i,a in enumerate(actions) if any(o.get('operator_type')=='create_torpedo' for o in a.get('position_operators',[]))]
                require(bool(ix),'No native magazine shot operation')
                shots=[copy.deepcopy(actions[ix[i%len(ix)]]) for i in range(count)]
                d['time_actions'][0]['action_group']['actions']=[a for i,a in enumerate(actions[:ix[0]])]+shots+[a for i,a in enumerate(actions) if i>ix[0] and i not in ix]
            if kind=='action_data_source':
                vals={'heavy_torpedo_torpedo_count_value':capacity,'magazine_capacity_value':capacity,'magazine_pair_count_value':count,
                      'combat03_torpedoes_per_interval_value':count,'combat03_interval_count_value':capacity//count}
                for v in d['action_values']:
                    key=v['action_value_id'];av=v['action_value']
                    if key in vals:av['values']=[vals[key]]*len(av['values'])
                    if damage and key=='heavy_torpedo_damage_value':av['values']=[damage*x/av['values'][0] for x in av['values']]
            put(name,kind,d,old)
        loc.update({name+'.name':label,name+'.ammo_label':'Torpedoes remaining',name+'.description':
            f'{count} torpedoes per salvo; {capacity} rounds, then 120 seconds to reload. '+
            (f'{damage:g} base damage per medium torpedo; 20-second salvo interval, 1275 speed.' if damage else '1500 base damage per light torpedo; 10-second salvo interval, 2125 speed.')+
            ' Thirty-second fuel. Conventional interceptable torpedoes; existing magazine and research rules.'})
        return name
    for short in ('hephaestus','laconia'):
        spec=read(Path(contracts)/(short+'-integration.json'));uid='expanse27_hephaestus' if short=='hephaestus' else 'expanse27_laconia_frigate';heph=short=='hephaestus'
        u=get('expanse_mcrn_corvette','unit');u['spatial']=copy.deepcopy(spec['spatial'])
        u['skin_groups']=[{'skins':[uid]}];u['tags']=['cruiser' if heph else 'frigate',uid];u['target_filter_unit_type']='cruiser' if heph else 'frigate'
        u['build'].update(build_kind='cruiser' if heph else 'frigate',build_group_id='cruiser' if heph else 'frigate',build_time=150. if heph else 95.,supply_cost=180 if heph else 130,
                          price={'credits':6000. if heph else 4000.,'metal':1950. if heph else 1100.,'crystal':1000. if heph else 750.},
                          exotic_price=[{'exotic_type':'offense','count':1},{'exotic_type':'defense' if heph else 'utility','count':2 if heph else 1}],prerequisites=[[uid+'_procurement']])
        u['physics'].update(max_linear_speed=1600. if heph else 1550.,time_to_max_linear_speed=3. if heph else 4.,max_angular_speed=25.)
        u['health']['durability']=350. if heph else 250.;u['health']['levels'][0].update(max_hull_points=4000. if heph else 1500.,max_armor_points=2300. if heph else 800.,max_shield_points=0.)
        u['user_interface']['pip_type']='cruiser' if heph else 'frigate';u['ai_attack_target']['attack_target_type']='capital_supercapital_heavy' if heph else 'light'
        u['player_ai']['attack_ship_weight_scalar']=1.;u['weapons']={'weapons':[],'max_range_weapon_index':10 if heph else 0}
        u['attack']=get('expanse12_scirocco','unit')['attack'] if heph else u['attack']
        for i,rig in enumerate(spec['rigs']):
            rail=rig['kind']=='rail';name=uid+('_rail' if rail else '_pdc')+'_'+str(i)
            source='expanse12_scirocco_rail_0' if rail else 'expanse12_raptor_pdc_0'
            w=get(source,'weapon');w['name']=uid+('.rail.name' if rail else '.pdc.name');w['turret']=copy.deepcopy(rig['turret_override']);put(name,'weapon',w,source)
            mount={k:copy.deepcopy(rig[k]) for k in ('mesh_point','up','forward','yaw_arc','pitch_arc')};mount.update(weapon=name,weapon_position=rig['position']);u['weapons']['weapons'].append(mount)
        require(sum(r['kind']=='pdc' for r in spec['rigs'])==(10 if heph else 6),'Wrong requested PDC count')
        require(sum(r['kind']=='rail' for r in spec['rigs'])==(1 if heph else 0),'Wrong rail count')
        u['ai']['attack_target_type_groups_matching_weapon']=u['weapons']['weapons'][0]['weapon'];u['ai']['attack_target_type_groups']=copy.deepcopy(get('expanse12_raptor_pdc_0','weapon')['attack_target_type_groups'])
        mags=[magazine(uid,'expanse12_scirocco_light_magazine',spec['torpedo_ports']['light'],5 if heph else 2,20 if heph else 12,('Hephaestus' if heph else 'Laconian frigate')+' light torpedoes')]
        if heph:mags.append(magazine(uid,'expanse12_scirocco_heavy_magazine',spec['torpedo_ports']['medium'],3,12,'Hephaestus medium torpedoes',3000.))
        u['abilities']=[{'abilities':mags+['expanse11_no_shields']}];u['item_builds']=[];put(uid,'unit',u,'expanse_mcrn_corvette')
        skin=get('expanse12_raptor','unit_skin');st=skin['skin_stages'][0]
        st['unit_mesh']={'mesh':spec['hull_mesh'],'shader':'ship','is_shadow_blocker':True};st['min_camera_distance']=spec['spatial']['radius']*1.8
        aliases=set(spec['copied_meshes'])|{r['turret_override']['gimbal_mesh'] for r in spec['rigs'] if r['kind']=='rail'}
        st['child_mesh_alias_bindings']['map']=[{'mesh_alias_name':a,'mesh_definition':{'mesh':a,'shader':'ship','is_shadow_blocker':True}} for a in sorted(aliases)]
        st['gui'].update(name=uid+'.name',description=uid+'.description');st['gui'].pop('special_operation_names',None)
        st['effects']['hyperspace_effects']=get('trader_skirmisher_corvette_frigate','unit_skin')['skin_stages'][0]['effects']['hyperspace_effects']
        # Raptor idle plume is local to each exhaust.N compiled point, unlike
        # Scirocco's absolute multi-engine effect. Native exhaust instancing
        # therefore follows the four/one actual new nozzles.
        for key in ('flair_effects','level_up_effect','level_up_sound'):st['effects'].pop(key,None)
        st['sounds']['dialogue']['spawned']={'neutral':['expanse17_voice_mcrn_orders']};put(uid,'unit_skin',skin,'expanse12_raptor')
        loc.update({uid+'.name':'MCRN Hephaestus-class Destroyer' if heph else 'Laconian Procurement Frigate',uid+'.pdc.name':'Nariman Dynamics 40mm PDC' if heph else 'Laconian PDC',uid+'.rail.name':'Hephaestus light turreted railgun',
                    uid+'.description':('Mobile MCRN fan-design destroyer. Ten 117.6-DPS PDCs, one 2000-damage light railgun every 22.5 seconds, five light and three medium torpedo tubes. 4000 hull / 2300 armor. The small hangar and marine complement are visual/lore features, not extra fighters or a second capture system.' if heph else 'OPA late Laconian procurement adaptation in Martian livery. Six 117.6-DPS PDCs and two conventional light torpedo tubes; 1500 hull / 800 armor. Fast escort with no conventional shields, cloaking or railgun. Ordinary out-of-combat repairs apply.')})
        report[uid]={'source':spec['source'],'health':u['health'],'build':u['build'],'speed':u['physics']['max_linear_speed'],'rigs':spec['rigs'],'magazines':mags,'runtime':'NOT RUN','classification':'Mod balance and procurement adaptation; no claim of canonical numerical specifications.'}
    return edits,loc,origins,report
