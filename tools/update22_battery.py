"""One native stationary Foehammer installation with a private tag-based cap."""
from pathlib import Path
import copy,shutil
from validate_experiments import read,require,sha256
from update20_fleet import ROOT,GAME
ID='expanse22_foehammer_battery'
RESEARCH='expanse22_unn_orbital_defense'

def changes(base):
    spec=read(ROOT/'audit/update22-foehammer/integration-spec.json');edits={};origins={};loc={};art={}
    def get(ident,kind):
        p=base/'entities'/f'{ident}.{kind}';return read(p if p.exists() else GAME/'entities'/p.name)
    def put(ident,kind,d,source):
        rel=f'entities/{ident}.{kind}';edits[rel]=d
        p=base/'entities'/f'{source}.{kind}';origins[rel]=str(p if p.exists() else GAME/'entities'/p.name)
    artroot=Path(spec['output_game'])
    for rel,digest in spec['files'].items():
        require(sha256(artroot/rel)==digest,'Reviewed battery art changed '+rel)
        if (base/rel).exists():require(sha256(base/rel)==digest,'Donor asset collision '+rel)
        else:art[rel]=artroot/rel
    d=get('trader_gauss_defense_structure','unit')
    d['spatial'].update(copy.deepcopy(spec['spatial']))
    d['build'].update(price={'credits':2000.,'metal':500.,'crystal':350.},build_time=120.,build_radius=spec['spatial']['radius'],prerequisites=[[RESEARCH]])
    d['structure']['slots_required']=4
    d['tags']=['structure',ID];d['skin_groups']=[{'skins':[ID]}]
    d['abilities']=[{'abilities':['expanse11_no_shields']}]
    health=d['health']['levels'][0];health.update(max_hull_points=4000.,max_armor_points=3000.,armor_strength=75.)
    d['weapons']={'weapons':[],'max_range_weapon_index':0}
    for idx,rig in enumerate(spec['rigs']):
        source='expanse10_donnager_rail_0' if rig['kind']=='rail' else 'expanse10_donnager_pdc_0'
        name=ID+f'_{idx}';w=get(source,'weapon');w['turret']=copy.deepcopy(rig['turret_override'])
        put(name,'weapon',w,source)
        m={k:copy.deepcopy(rig[k]) for k in ['mesh_point','up','forward','yaw_arc','pitch_arc']}
        m.update(weapon=name,weapon_position=copy.deepcopy(rig['position']));d['weapons']['weapons'].append(m)
    rail=edits[f'entities/{ID}_0.weapon']
    d['ai']['attack_target_type_groups']=copy.deepcopy(rail['attack_target_type_groups'])
    d['ai']['attack_target_type_groups_matching_weapon']=ID+'_0'
    put(ID,'unit',d,'trader_gauss_defense_structure')
    skin=get('trader_gauss_defense_structure','unit_skin');stage=skin['skin_stages'][0]
    stage['unit_mesh']={'mesh':spec['base_mesh'],'shader':'ship','is_shadow_blocker':True}
    stage['gui'].update(name=ID+'.name',description=ID+'.description')
    stage['child_mesh_alias_bindings']={'map':[{'mesh_alias_name':n,'mesh_definition':{'mesh':n,'shader':'ship','is_shadow_blocker':True}} for n in spec['aliases'][1:]]}
    donor=get('expanse_donnager_battleship','unit_skin')['skin_stages'][0]['effects']['effect_alias_bindings']
    aliases=stage['effects'].setdefault('effect_alias_bindings',[]);existing={x['alias_name'] for x in aliases}
    aliases.extend(copy.deepcopy(x) for x in donor if x['alias_name'] not in existing)
    put(ID,'unit_skin',skin,'trader_gauss_defense_structure')
    node=get('trader_unlock_robotics_cruiser','research_subject');node.update(tier=2,field='military_engineering',field_coord=[6,8],
        prerequisites=[['trader_unlock_hangar_defense_structure']],name=RESEARCH+'.name',name_uppercase=RESEARCH+'.upper',description=RESEARCH+'.description',
        hud_icon='trader_gauss_defense_structure_hud_icon',tooltip_picture='trader_gauss_defense_structure_tooltip_picture')
    put(RESEARCH,'research_subject',node,'trader_unlock_robotics_cruiser')
    loc.update({ID+'.name':'Foehammer Orbital Battery',ID+'.description':'Mod-original stationary battery: one Foehammer, two PDCs, 4 military slots and a shared limit of 2 per gravity well. 4,000 hull / 3,000 armor. 2,000 credits, 500 metal, 350 crystal; 120 seconds. Needs screening against torpedoes and fast flanking ships.',
        RESEARCH+'.name':'Orbital Defense Command',RESEARCH+'.upper':'ORBITAL DEFENSE COMMAND',RESEARCH+'.description':'Unlocks the Foehammer Orbital Battery. Two per gravity well; 4 military infrastructure slots each. Separate defenses and fleets remain necessary.'})
    report={'status':'OFFLINE AUTHORED; RUNTIME NOT RUN','unit':ID,'research':RESEARCH,'art_files':len(art),
        'private_weapon_change':'turret alias only; all damage, cooldown, penetration, acquisition, tracking and range unchanged',
        'rail':{k:rail[k] for k in ['damage','cooldown_duration','penetration','range','pitch_speed','yaw_speed','target_acquired_duration_required_to_fire']},
        'station_rotation':'Native gauss stationary attack and 8-degree/second whole-structure rotation retained; no linear movement. Actual elevation/body alignment needs runtime test.',
        'limit':'Native player.unit_limits.planet private tag,2 across all aliases. Native queued/captured counting requires runtime verification. Excess captured property is retained; no deletion script; additional construction should remain blocked.',
        'research_limit_interaction':'Native gauss range/cooldown research targets native gauss weapon IDs, not this private gun; native starbase limit research targets starbase tag, not private battery tag.',
        'cost_basis':'Exactly half Truman ordinary resource investment; no exotic cost;120seconds;4militaryslots;no fleet supply.'}
    return edits,loc,origins,art,report
