"""Independent candidate checks against frozen0.25 and installed native data."""
import copy, json, zipfile
from update20_fleet import ROOT, GAME
from update21_factions import FACTIONS, WRAPPERS
from update26_research import OBSOLETE_SHIPS
from validate_experiments import read, require, sha256
from build_polish import write
from check_doctrine_acquisition import run as acquisition

UI = {'name', 'name_uppercase', 'description', 'hud_icon', 'tooltip_picture',
      'tooltip_icon', 'field_coord'}

def run(suffix=''):
    old = ROOT/'build/experiments'/('expanse_update25'+suffix)
    new = ROOT/'build/experiments'/('expanse_update26'+suffix)
    def path(base, name, kind):
        p = base/'entities'/f'{name}.{kind}'
        return p if p.exists() else GAME/'entities'/p.name
    def get(base, name, kind): return read(path(base, name, kind))
    rows = []
    for owner in [*FACTIONS.values(), *WRAPPERS]:
        a, b = (get(base, owner, 'player') for base in (old, new))
        require(a['research']['research_domains'] == b['research']['research_domains'], 'Domain/tier drift '+owner)
        listed = set(b['research']['research_subjects'] + b['research']['faction_research_subjects'])
        cells = {}; civilian_count = 0
        for key in ('research_subjects', 'faction_research_subjects'):
            def civilian(base, player):
                return [n for n in player['research'][key] if get(base,n,'research_subject')['domain']=='civilian']
            require(civilian(old,a)==civilian(new,b), 'Civilian membership/order drift '+owner)
        for n in listed:
            before, after = (get(base,n,'research_subject') for base in (old,new))
            require({k:v for k,v in before.items() if k not in UI} ==
                    {k:v for k,v in after.items() if k not in UI}, 'Research mechanics changed '+n)
            if after['domain']=='civilian':
                require(path(old,n,'research_subject').read_bytes()==path(new,n,'research_subject').read_bytes(), 'Civilian bytes changed '+n)
                civilian_count += 1
            else:
                cell = (after['field'], *after['field_coord'])
                require(cell not in cells, 'Research collision '+n+' '+cells.get(cell,''))
                cells[cell] = n
                require(0 <= after['field_coord'][1] <= (9 if suffix else 7), 'Sparse military row '+n)
            groups = after.get('prerequisites',[])
            # Outer groups are alternative routes; the combined sandbox keeps
            # both native Titan routes while each owner needs only its own.
            require(not groups or any(set(group)<=listed for group in groups),
                    'No reachable prerequisite route '+owner+' '+n)
        routes = set(b['buildable_units']) | set(b['theme_picker_mesh_preview_units'])
        routes.update(x['unit'] for x in b['garrison']['units']['random_units'])
        routes.update(x['unit'] for x in b['trade']['trade_ship_escorts'])
        require(not routes & OBSOLETE_SHIPS, 'Obsolete player acquisition '+owner)
        require('expanse21_opa_command_colony_module' not in b['ship_components'], 'Paid command module still listed')
        rows.append({'owner':owner,'civilian_subjects_unchanged':civilian_count,'military_cells':len(cells)})

    command = get(new,'expanse21_opa_command','unit')
    prior = get(old,'expanse21_opa_command','unit')
    europa = get(new,'expanse19_europa_bane','unit')
    for k in ('max_hull_points','max_armor_points'):
        require(command['health']['levels'][0][k] == 2*europa['health']['levels'][0][k], 'Command health ratio '+k)
    require(command['physics']==prior['physics'] and command['hyperspace']==prior['hyperspace'], 'Command movement drift')
    require(command['build']['price']=={'credits':4800.,'metal':975.,'crystal':600.}, 'Command price')
    for k in ('build_time','supply_cost'): require(command['build'][k]==prior['build'][k], 'Command '+k)
    require(command['colonize_ability'] in command['abilities'][0]['abilities'], 'Direct colony unavailable')
    require(path(old,'expanse19_europa_bane','unit').read_bytes()==path(new,'expanse19_europa_bane','unit').read_bytes(), 'Regular Europa changed')

    item = get(new,'expanse26_tycho_recovery_component','unit_item')
    require(item['is_finite'] and item['always_show_in_shop'] and 'price' not in item, 'NPC inventory bypass')
    require(item['max_count_on_unit']==1, 'Recovery stacking')
    require(item['unit_modifiers']==[{'modifier_type':'unit_capture_points','value_behavior':'scalar','values':[.15]}], 'Recovery effect')
    reward_ids = read(new/'entities/npc_reward.entity_manifest')['ids']
    item_ids = read(new/'entities/unit_item.entity_manifest')['ids']
    require('expanse26_tycho_recovery_component' in item_ids, 'Unregistered reward item')
    for owner in ('pranast_united_npc','jiskun_force_npc'):
        native = get(GAME,owner,'player'); p = get(new,owner,'player')
        for reward in p['npc']['reputation']['rewards']:
            require(reward['reward'] in reward_ids, 'Unregistered paid service')
            require(reward['influence_point_cost']>0 and reward['cooldown_duration']>0, 'Free/unbounded service')
        p['npc']['visuals'] = native['npc']['visuals']
        p['npc']['reputation']['rewards'] = native['npc']['reputation']['rewards']
        require(p==native, 'Unrelated NPC behavior changed')
    with zipfile.ZipFile(old/'scenarios/expanse18_sol_three_homes.scenario') as a, zipfile.ZipFile(new/'scenarios/expanse26_sol_three_homes.scenario') as b:
        require(b.testzip() is None, 'Scenario CRC')
        before=json.loads(a.read('galaxy_chart.json'));after=json.loads(b.read('galaxy_chart.json'))
        for ar,br in zip(before['root_nodes'],after['root_nodes']):
            for an,bn in zip(ar.get('child_nodes',[]),br.get('child_nodes',[])):
                if an['id'] in (5,6):
                    bn['primary_fixture_override_name']=an['primary_fixture_override_name']
                    bn['ownership']=an['ownership']
        require(before==after, 'Scenario topology changed')
        for name in a.namelist():
            if name not in ('galaxy_chart.json','scenario_info.json'):require(a.read(name)==b.read(name),'Scenario member drift '+name)
    require(not (new/'entities/expanse18_prototech_composite.exotic').exists(), 'Lab resource leaked into gameplay')
    frozen=read(ROOT/'audit/update26/checkpoint.json')['preserved_packages'][old.name]
    require(sha256(old.with_suffix('.zip'))==frozen['zip_sha256'], 'Rollback mutated')
    acquisition(new)
    result={'status':'PASS OFFLINE','players':rows,'npc_and_colony_routes':'PASS static wiring',
            'rollback_zip_unchanged':True,'runtime':'NOT RUN'}
    write(ROOT/'audit'/('update26'+suffix)/'acceptance-check.json',result)
    return result

if __name__=='__main__':
    for suffix in ('','_sandbox'):print(json.dumps(run(suffix),indent=2))
