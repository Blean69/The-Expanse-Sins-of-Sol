#!/usr/bin/env python3
"""Deterministic, isolated gate-1 faction/scenario fragment builder. Never installs.

Example: python3 tools/update18_scenario.py
The output is an overlay plus integration fragments, NOT a standalone mod.
"""
from pathlib import Path
import argparse, copy, hashlib, json, math, zipfile
import jsonschema

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_DRIVE = Path('/run/media/haker/NVME 2')
DEFAULT_MAIN = DEFAULT_DRIVE / 'expanse-mod'

def read(p): return json.loads(Path(p).read_text(encoding='utf-8-sig'))
def encoded(d): return (json.dumps(d, indent=2, ensure_ascii=False)+'\n').encode()
def write(p,d): p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(encoded(d))
def sha(p): return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def digest(d): return hashlib.sha256(json.dumps(d,sort_keys=True,separators=(',',':')).encode()).hexdigest()
def require(v,s):
    if not v: raise ValueError(s)

def schema_check(data, schema, original=None):
    """Validate both schema drafts; unchanged installed unknowns are recorded.
    Does not silently accept altered unknown fields or invent new schema keys.
    """
    value=copy.deepcopy(data);schema=copy.deepcopy(schema);extensions=[]
    for _ in range(40):
        errors=list(jsonschema.Draft202012Validator(schema).iter_errors(value))
        if not errors: break
        progress=False
        for e in errors:
            target=value;source=original
            for k in e.path:
                target=target[k]
                source=source[k] if source is not None else None
            if e.validator=='enum' and source is not None and source==e.instance:
                e.schema['enum'].append(e.instance);extensions.append({'path':list(e.path),'unchanged_enum':e.instance});progress=True
            elif e.validator in ['unevaluatedProperties','additionalProperties'] and isinstance(target,dict) and e.schema.get('properties'):
                for k in sorted(set(target)-set(e.schema['properties'])):
                    require(source is not None and k in source and source[k]==target[k],f'New unknown field: {list(e.path)+[k]}')
                    extensions.append({'path':list(e.path)+[k],'unchanged_installed_extension':True});del target[k];progress=True
        require(progress,'Schema error: '+str(errors[0]))
    jsonschema.Draft7Validator(schema).validate(value)
    jsonschema.Draft202012Validator(schema).validate(value)
    return extensions

def gameplay(player):
    p=copy.deepcopy(player)
    for k in ['race_name','race_description','faction_name','faction_short_name','faction_description','faction_icon']:
        p['gui'].pop(k,None)
    return p

def scalar_occurrences(x, needle, path=''):
    if isinstance(x,dict):
        return [r for k,v in x.items() for r in scalar_occurrences(v,needle,path+'/'+str(k))]
    if isinstance(x,list):
        return [r for k,v in enumerate(x) for r in scalar_occurrences(v,needle,path+'/'+str(k))]
    return [path] if x==needle else []

def build(args):
    base=args.baseline;game=args.game;sdk=args.sdk;out=args.output;payload=out/'overlay';audit=args.audit
    require(base.is_dir(),'Missing readonly baseline')
    require(not out.exists(),'Refusing to overwrite output; use a fresh --output')
    source=read(args.source);factions=source['factions'];ids=[x['id'] for x in factions]
    baseline_player=read(base/'entities/trader_loyalist.player')
    sources=[base/'entities/trader_loyalist.player',game/'uniforms/player.uniforms',game/'uniforms/scenario.uniforms',game/'uniforms/galaxy_generator.uniforms',game/'entities/terran_planet.unit']
    source_hashes={str(p):sha(p) for p in sources}
    localizations={};validation=[];availability={}
    for faction in factions:
        p=copy.deepcopy(baseline_player);fid=faction['id'];g=p['gui']
        for key in ['race_name','faction_name','faction_short_name','race_description','faction_description']:
            g[key]=f'{fid}.{key}'
        g['faction_icon']=faction['icon']
        localizations.update({g['race_name']:'Sins of Sol',g['faction_name']:faction['name'],g['faction_short_name']:faction['short'],g['race_description']:'Three identities share the same fleet, technology and economy.',g['faction_description']:f"{faction['name']}: shared TEC-derived gameplay. Sol gate 1 requires slot {ids.index(fid)+1} / {faction['home'].replace('_',' ').title()}. No faction bonuses or exclusive ships."})
        require(gameplay(p)==gameplay(baseline_player),'Faction gameplay drift')
        brush=base/'brushes'/f"{faction['icon']}.brush";require(brush.is_file(),'Missing existing faction silhouette icon')
        extensions=schema_check(p,read(sdk/'json_schemas/player-schema.json'),baseline_player)
        validation.append({'file':f'{fid}.player','status':'PASS offline schema/source equality','unchanged_extensions':extensions})
        write(payload/'entities'/f'{fid}.player',p)
        availability[fid]={k:copy.deepcopy(p[k]) for k in ['buildable_units','structures','ship_components','planet_components','research','unit_limits','buildable_exotics']}
    # All installed start modes are keyed by exact player definition, not race.
    # Preserve original entries byte-semantically and append clones of Enclave.
    starts={}
    for p in sorted((game/'entities').glob('*.start_mode')):
        native=read(p);config=next(r for r in native['faction_configurations'] if r['player_definition_id']=='trader_loyalist')
        data=copy.deepcopy(native)
        for fid in ids:
            r=copy.deepcopy(config);r['player_definition_id']=fid;data['faction_configurations'].append(r)
        require(data['faction_configurations'][:-3]==native['faction_configurations'],'Original start modes changed')
        for r in data['faction_configurations'][-3:]:
            check=copy.deepcopy(r);check['player_definition_id']='trader_loyalist';require(check==config,'Unequal start configuration')
        starts[p.name]={'source_sha256':sha(p),'configuration':config,'verification':'Exact installed template clone; no start-mode entity schema in pinned SDK'}
        source_hashes[str(p)]=sha(p);write(payload/'entities'/p.name,data)
    # Local scenario override targets only player home filling; no global planet reskin.
    home=read(game/'entities/terran_planet.unit');native_home=copy.deepcopy(home)
    for kind in ['random_metal_asteroids','random_crystal_asteroids']:
        for tier in home['planet'][kind]['tiers']:tier['count']=[0,0]
    home['skin_groups']=[{'skins':['terran_planet_0']}]
    validation.append({'file':'expanse18_equal_home.unit','status':'PASS offline schema','unchanged_extensions':schema_check(home,read(sdk/'json_schemas/unit-schema.json'),native_home)})
    write(payload/'entities/expanse18_equal_home.unit',home)
    # The fixture selection override is scenario-local. Test actual home choice in game.
    fillings={'version':1,'fixture_fillings':[{'name':'expanse18_equal_home_fixture','filling':{'entity_definition':'expanse18_equal_home','militia_supply':[0,0]}}], 'random_fixture_fillings':[{'name':'random_terran_home_planet','filling':{'items':[{'name':'expanse18_equal_home_fixture','probability':1}]}}]}
    gs=read(sdk/'json_schemas/galaxy-generator-uniforms-schema.json')
    fs=copy.deepcopy(gs['$defs']['galaxy_chart_fillings']);fs['$defs']=gs['$defs']
    require(fillings['version']==1,'Fixture version')
    schema_check({k:v for k,v in fillings.items() if k!='version'},fs)
    native_fillings=read(game/'uniforms/galaxy_generator.uniforms')['fillings']
    filling_names={r['name'] for r in native_fillings['node_fillings']}
    npc_names={r['name'] for r in native_fillings['npc_fillings']}
    nodes=source['nodes'];bykey={r['key']:r for r in nodes};nodeids={r['id'] for r in nodes}
    require(len(nodes)==len(bykey)==len(nodeids),'Duplicate node ID/key')
    require([r.get('slot') for r in nodes if 'slot' in r]==[0,1,2],'Exactly three home slots required')
    chart={'version':1,'skybox':'skybox_cloud_16','root_nodes':[],'phase_lanes':[],'recommended_team_count':0}
    made={};min_separation=float('inf')
    for r in nodes:
        require(r['filling'] in filling_names,'Unknown filling '+r['filling'])
        p={'id':r['id'],'design_name':r['key'],'primary_fixture_override_name':f"expanse18.node.{r['key']}",'filling_name':r['filling'],'position':r['position'],'orbit_speed_scalar':0.0,'chance_of_retrograde_orbit':0.0,'chance_of_loot':0.0,'chance_of_first_planet_bonus':0.0,'chance_of_second_planet_bonus':0.0}
        localizations[p['primary_fixture_override_name']]=r['name']
        if 'slot' in r:p['ownership']={'player_index':r['slot']}
        if 'npc' in r:
            require(r['npc'] in npc_names,'Unknown NPC');p['ownership']={'npc_filling_name':r['npc']}
        made[r['key']]=p
    for r in nodes:
        ancestors=set();cursor=r
        while 'parent' in cursor:
            require(cursor['parent'] in bykey,'Missing parent')
            require(cursor['parent'] not in ancestors,'Cyclic parent hierarchy')
            ancestors.add(cursor['parent']);cursor=bykey[cursor['parent']]
    for r in nodes:
        if 'parent' in r:
            require(r['parent'] in made and r['parent']!=r['key'],'Invalid parent')
            made[r['parent']].setdefault('child_nodes',[]).append(made[r['key']])
        else:chart['root_nodes'].append(made[r['key']])
    require(len(chart['root_nodes'])==1 and chart['root_nodes'][0]['id']==0,'Exactly one Sol root')
    adjacency={k:set() for k in bykey};edges=set()
    for i,(a,b) in enumerate(source['lanes']):
        require(a in bykey and b in bykey and a!=b,'Bad lane endpoint')
        pair=tuple(sorted((a,b)));require(pair not in edges,'Duplicate lane');edges.add(pair)
        adjacency[a].add(b);adjacency[b].add(a)
        chart['phase_lanes'].append({'id':100+i,'node_a':bykey[a]['id'],'node_b':bykey[b]['id']})
    seen=set();todo=['sol']
    while todo:
        k=todo.pop()
        if k not in seen:seen.add(k);todo.extend(adjacency[k]-seen)
    require(seen==set(bykey),'Disconnected or orphan node')
    for i,a in enumerate(nodes):
        for b in nodes[i+1:]:min_separation=min(min_separation,math.dist(a['position'],b['position']))
    require(min_separation>=250,'Overlapping chart centers (conservative map-unit check)')
    for fid in factions:require(len(adjacency[fid['home']])>=2,'Home needs two outbound routes')
    schema_check(chart,read(sdk/'json_schemas/galaxy-chart-schema.json'))
    # Existing three-player fixed archive supplies compatible ZIP members/metadata.
    seed=game/'scenarios/public_balance_of_power.scenario';source_hashes[str(seed)]=sha(seed)
    with zipfile.ZipFile(seed) as z:
        info=json.loads(z.read('scenario_info.json'));members={n:z.read(n) for n in z.namelist()}
    info.update(name=':'+source['title'],description=':GATE 1 TEST ONLY. Normal start. Slot 1 UNN/Earth; slot 2 MCRN/Mars; slot 3 OPA/Jovian Habitats. Static, no randomized starts. Three equal placeholder homes; full Sol expansion map pending runtime validation.',planet_counts=[6,6],star_counts=[1,1],has_npcs=True,are_player_slots_randomized=False,can_gravity_wells_move=False)
    info['desired_player_slots_configuration']={'player_count':3,'team_count':0}
    # New metadata keys are observed in the installed static scenario.
    static=game/'scenarios/public_scorched_space.scenario';source_hashes[str(static)]=sha(static)
    with zipfile.ZipFile(static) as z:static_info=json.loads(z.read('scenario_info.json'))
    for key in ['are_player_slots_randomized','can_gravity_wells_move']:require(info[key]==static_info[key],'Unverified static metadata')
    members.update({'galaxy_chart.json':encoded(chart),'galaxy_chart_fillings.json':encoded(fillings),'scenario_info.json':encoded(info)})
    # Keep installed seed preview as an explicitly temporary thumbnail, metadata intact.
    path=payload/'scenarios'/f"{source['scenario_id']}.scenario";path.parent.mkdir(parents=True,exist_ok=True)
    with zipfile.ZipFile(path,'w',zipfile.ZIP_DEFLATED,compresslevel=9) as z:
        for name,data in sorted(members.items()):
            zi=zipfile.ZipInfo(name,(2026,9,13,0,0,0));zi.compress_type=zipfile.ZIP_DEFLATED;zi.external_attr=0o644<<16;z.writestr(zi,data)
    with zipfile.ZipFile(path) as z:
        require(z.testzip() is None,'ZIP CRC');require(set(z.namelist())==set(members),'Scenario member drift')
        require(json.loads(z.read('galaxy_chart.json'))==chart,'ZIP chart roundtrip')
    write(out/'editable/galaxy_chart.json',chart);write(out/'editable/galaxy_chart_fillings.json',fillings);write(out/'editable/scenario_info.json',info)
    # Integrator explicitly owns the real shared files; these are project fragments.
    fragments={'format':'PROJECT MERGE INSTRUCTIONS, not engine configuration','player.entity_manifest':{'append_ids':ids},'unit.entity_manifest':{'append_ids':['expanse18_equal_home']},'uniforms/player.uniforms':{'append_pickable_players':ids,'preserve_existing_entries':True},'uniforms/scenario.uniforms':{'append_scenarios':[source['scenario_id']],'preserve_existing_entries':True},'localizations':localizations}
    cannon=read(base/'entities/trader_orbital_cannon_structure.unit')
    native_group=next(g for g in cannon['abilities'] if g.get('required_player')=='trader_loyalist')
    clones=[]
    for fid in ids:
        group=copy.deepcopy(native_group);group['required_player']=fid;clones.append(group)
    fragments['shared_definition_patches']=[{'file':'entities/trader_orbital_cannon_structure.unit','source_sha256':sha(base/'entities/trader_orbital_cannon_structure.unit'),'operation':'append exact Enclave ability groups for clone owners','append_to_abilities':clones}]
    picker_path=game/'gui/front_end_faction_picker_dialog.gui'
    picker=read(picker_path)
    source_hashes[str(picker_path)]=sha(picker_path)
    single_template=next(p for p in picker['page_definitions'] if len(p['factions'])==1)
    pages=[];portraits=[]
    for index,faction in enumerate(factions):
        page=copy.deepcopy(single_template);page['name']=f"{faction['id']}.picker_page";page['factions']=[faction['id']]
        localizations[page['name']]=faction['name']+' / '+faction['short'];pages.append(page)
        portraits.append({'faction':faction['id'],'portrait':picker['faction_portraits'][index%2]['portrait']})
    fragments['gui/front_end_faction_picker_dialog.gui']={'source_sha256':sha(picker_path),'append_page_definitions':pages,'append_faction_portraits':portraits,'preserve_existing_fields':True,'layout_note':'Reuses installed single-faction page/layout pattern, not an invented three-column page. Portraits are native TEC placeholders.'}
    write(out/'fragments/registrations.json',fragments)
    write(out/'fragments/availability.json',availability)
    # Audit exact hardcoded player references in the shared reachable definitions.
    refs=[]
    for p in sorted((base/'entities').iterdir()):
        if p.suffix not in ['.research_subject','.unit','.ability','.buff','.unit_item']:continue
        try:d=read(p)
        except (ValueError,UnicodeError):continue
        for needle in ['trader_loyalist','trader_rebel',*ids]:
            paths=scalar_occurrences(d,needle)
            if paths:refs.append({'definition':p.name,'literal':needle,'paths':paths})
    audit.mkdir(parents=True,exist_ok=True)
    report={'status':'PASS OFFLINE ONLY; runtime gate NOT RUN','baseline_player_sha256':sha(base/'entities/trader_loyalist.player'),'faction_ids':ids,'shared_gameplay_sha256':digest(gameplay(baseline_player)),'player_definitions_identical_except_presentation':True,'start_modes':starts,'unit_limits':baseline_player['unit_limits'],'inherited_defaults':{k:baseline_player[k] for k in ['race','home_planet','culture','trade','garrison','max_supply','factional_victory','default_starting_assets','unit_starting_experience']},'research_tier_bonuses':{k:v['research_tiers'] for k,v in baseline_player['research']['research_domains'].items()},'exact_player_id_references_in_baseline_mechanics':refs,'scenario':{'sha256':sha(path),'nodes':len(nodes),'home_nodes':3,'minimum_center_separation_map_units':min_separation,'lanes':len(edges),'all_nodes_reachable':True,'no_generator_params_member':True,'fixed_slots':True,'faction_aware_assignment':'NOT SUPPORTED by inspected schema; deterministic slot instructions only','layout_note':source['layout_note'],'home_equalization':'Scenario-local random_terran_home_planet override selects fixed expanse18_equal_home: 2 metal, 1 crystal, zero random extra asteroids; home selection precedence still requires runtime proof','markets':['pranast_united','viturak_cabal'],'preview':'Unmodified installed Balance of Power thumbnail placeholder; not a rendered Sol preview'},'validation':validation,'source_hashes':source_hashes,'runtime':{'SolarForge_open_save_roundtrip':'NOT RUN','game_load':'NOT RUN','construction_and_victory':'NOT RUN','host_slot_permutations':'NOT RUN','independent_owner_research_and_hero_limits':'NOT RUN','save_reload':'NOT RUN','multiplayer_duration_seconds':0},'blocker':'No supported headless SolarForge/game validation command found. Candidate archive requires one SolarForge open/save and in-game gate-1 session; installed seed is available, so no user-created seed is necessary.'}
    write(audit/'report.json',report);write(audit/'node-report.json',{'nodes':nodes,'adjacency':{k:sorted(v) for k,v in adjacency.items()},'layout_note':source['layout_note']})
    for p,h in source_hashes.items():require(sha(p)==h,'Readonly dependency changed')
    write(out/'artifact-manifest.json',{'files':{str(p.relative_to(out)):sha(p) for p in sorted(out.rglob('*')) if p.is_file()},'runtime':'NOT RUN'})
    print(json.dumps({'output':str(out),'scenario_sha256':sha(path),'factions':ids,'status':report['status']},indent=2))

if __name__=='__main__':
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--baseline',type=Path,default=DEFAULT_MAIN/'build/experiments/expanse_update17')
    ap.add_argument('--game',type=Path,default=DEFAULT_DRIVE/'SteamLibrary/steamapps/common/Sins2')
    ap.add_argument('--sdk',type=Path,default=DEFAULT_DRIVE/'SteamLibrary/steamapps/common/Sins of a Solar Empire II - Mod Tools')
    ap.add_argument('--output',type=Path,default=ROOT/'build/laboratory/update18/scenario')
    ap.add_argument('--audit',type=Path,default=ROOT/'audit/update18-scenario')
    ap.add_argument('--source',type=Path,default=Path(__file__).with_name('update18_scenario_source.json'))
    build(ap.parse_args())
