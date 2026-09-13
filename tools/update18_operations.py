"""Build disabled native operation probe and contact fragments; no package install."""
from __future__ import annotations
import argparse, copy, ctypes, ctypes.util, hashlib, json
from pathlib import Path
import jsonschema
ROOT = Path(__file__).resolve().parents[1]
DRIVE = Path('/run/media/haker/NVME 2')
GAME = DRIVE / 'SteamLibrary/steamapps/common/Sins2'
SDK = DRIVE / 'SteamLibrary/steamapps/common/Sins of a Solar Empire II - Mod Tools'
OUT = ROOT / 'build/laboratory/update18/operations'
AUDIT = ROOT / 'audit/update18-operations'

def read(p): return json.loads(p.read_text())
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def write(p, data):
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(data, indent=2) + '\n')

def lua_syntax(path):
    """Compile only with system liblua; never simulate game APIs or execute probe."""
    lib = ctypes.CDLL(ctypes.util.find_library('lua5.4'))
    lib.luaL_newstate.restype = ctypes.c_void_p
    lib.luaL_loadfilex.argtypes = [ctypes.c_void_p, ctypes.c_char_p, ctypes.c_char_p]
    lib.lua_tolstring.argtypes = [ctypes.c_void_p, ctypes.c_int, ctypes.c_void_p]
    lib.lua_tolstring.restype = ctypes.c_char_p
    lib.lua_close.argtypes = [ctypes.c_void_p]
    state = lib.luaL_newstate()
    try:
        result = lib.luaL_loadfilex(state, str(path).encode(), None)
        assert result == 0, lib.lua_tolstring(state, -1, None).decode()
    finally: lib.lua_close(state)
    return {'status':'PASS', 'scope':'Lua 5.4 syntax compile only; not game API binding/runtime validation'}

def build():
    sources = ['scripts/event_metadata.lua','scripts/pirate_incursion.lua',
        'entities/derelict_loot_2.unit','entities/trader_derelict_specialist.unit_item',
        'entities/pranast_united_npc.player','entities/jiskun_force_npc.player',
        'entities/jiskun_share_vision.npc_reward','entities/jiskun_share_vision.ability',
        'entities/jiskun_share_vision.action_data_source','entities/jiskun_share_vision_on_scout.buff',
        'entities/jiskun_share_vision_on_node.buff','entities/jiskun_crystal_stockpile_0.npc_reward',
        'entities/pirate_looting_crew.npc_reward','entities/advent_unity_conversion_on_planet.buff',
        'uniforms/notification.uniforms','uniforms/loot.uniforms']
    rows = [{'path':str(GAME/s), 'sha256':sha(GAME/s)} for s in sources]
    schema_names = ['npc-reward-schema.json','unit-item-schema.json','action-data-source-schema.json','notification-uniforms-schema.json','loot-uniforms-schema.json']
    schema_rows = [{'path':str(SDK/'json_schemas'/s),'sha256':sha(SDK/'json_schemas'/s)} for s in schema_names]
    action = read(SDK/'json_schemas/action-data-source-schema.json')
    branch = next(x['then'] for x in action['$defs']['action']['anyOf'] if x.get('if',{}).get('properties',{}).get('action_type',{}).get('const') == 'add_notification')
    notif = read(SDK/'json_schemas/notification-uniforms-schema.json')
    assert branch['properties']['notification_type']['enum'] == ['planet_conversion_started','planet_conversion_colonized']
    assert notif['properties']['types']['unevaluatedProperties'] is False
    item_id = 'expanse18_tycho_recovery_component'
    item = read(GAME/'entities/trader_derelict_specialist.unit_item')
    item.update(name=item_id+'.name',description=item_id+'.description')
    item['unit_modifiers'] = [{'modifier_type':'unit_capture_points','value_behavior':'scalar','values':[1.15]}]
    # Service-supplied only: own clone is not put in any factory's item inventory.
    # Existing native prerequisite is preserved, not a competing research node.
    reward = {'version':0,'gui':{'hud_icon':item['hud_icon'],'name':item_id+'.name','description':item_id+'.description'},'type':'ship_component','item':item_id}
    cache = {'version':0,'gui':{'hud_icon':'jiskun_crystal_stockpile_0_hud_icon','name':'expanse18_ceres_materials.name','description':'expanse18_ceres_materials.description'},'type':'assets','assets':{'metal':300.0}}
    registry = read(GAME/'entities/jiskun_share_vision.npc_reward')
    registry['gui'].update(name='expanse18_ceres_registry.name',description='expanse18_ceres_registry.description')
    definitions = {item_id+'.unit_item':item,item_id+'.npc_reward':reward,
        'expanse18_ceres_materials.npc_reward':cache,'expanse18_ceres_registry.npc_reward':registry}
    checks=[]
    for name, data in definitions.items():
        path=OUT/'entities'/name;write(path,data)
        schema='unit-item-schema.json' if name.endswith('.unit_item') else 'npc-reward-schema.json'
        jsonschema.Draft202012Validator(read(SDK/'json_schemas'/schema)).validate(data)
        checks.append({'file':str(path.relative_to(OUT)),'schema':schema,'status':'PASS'})
    # These are explicit PROJECT fragments, not loadable .player files; shared NPC
    # registration, scenario placement, localization merge belong to the integrator.
    contacts={
      'format':'project fragment, NOT engine configuration file',
      'status':'DISABLED_PENDING_CONTACT_RUNTIME_TEST',
      'expanse18_tycho_bureau':{
        'native_player_reference':'pranast_united_npc',
        'reputation_rewards':[{'reward':item_id,'required_reputation_level':2,'influence_point_cost':4,'cooldown_duration':360}],
        'late_sample_authorization':'GATED; no substitute reward',
        'neutrality':'Native reference starts allied to playable players; contact is not owned by service buyer or OPA.',
        'placement':'Tycho Roadstead only; separate from buildable expanse18_tycho_arsenal',
        'free_visiting_buffs':'No new aura/repair or visit-triggered benefit authored. Native NPC support-fleet interactions require review before cloning a full player.'},
      'expanse18_ceres_exchange':{
        'native_player_reference':'jiskun_force_npc',
        'reputation_rewards':[{'reward':'expanse18_ceres_materials','required_reputation_level':0,'influence_point_cost':2,'cooldown_duration':240},
          {'reward':'expanse18_ceres_registry','required_reputation_level':1,'influence_point_cost':4,'cooldown_duration':600}],
        'placement':'Ceres Freeport separate from colonizable Ceres',
        'finite_service':'360 seconds of existing NPC scout vision; ordinary vision, NOT stealth detection; no permanent map reveal authored.'},
      'faction_access':['expanse18_unn','expanse18_mcrn','expanse18_opa']}
    write(OUT/'contact-fragments.json',contacts)
    write(OUT/'localization-fragment.json',{
      'expanse18_tycho_bureau.name':'Tycho Engineering Bureau',
      'expanse18_ceres_exchange.name':'Ceres Shipping Exchange',
      item_id+'.name':'Tycho Recovery Component',
      item_id+'.description':'A normal capital-ship component providing 15% more native capture points. One per ship; occupies an equipment slot. Does not grant research, resources, boarding capture abilities or exclusive recovery claims.',
      'expanse18_ceres_materials.name':'Bonded Material Shipment',
      'expanse18_ceres_materials.description':'Receive 300 metal once per purchase. Costs Influence and has a service cooldown.',
      'expanse18_ceres_registry.name':'Temporary Shipping Registry Access',
      'expanse18_ceres_registry.description':'Shares the contact\'s native scout vision for 360 seconds. Reveals what those scouts can normally see; does not detect stealth.'})
    probe=OUT/'scripts/expanse18_operations_native_probe.lua'
    probe.parent.mkdir(parents=True,exist_ok=True)
    probe.write_bytes((ROOT/'tools/update18_operations_probe.lua').read_bytes())
    syntax=lua_syntax(probe)
    assert 'local PROBE_ENABLED = false' in probe.read_text()
    assert not any(x in probe.read_text() for x in ['simulation:give_research','math.random','os.time','io.open'])
    capability={
      'status':'GLOBAL_OPERATION_GATE_UNRESOLVED', 'runtime_status':'NOT RUN',
      'native_lua_api_version':0.6,
      'verified_source_structure':{
        'event_callbacks':['on_start','on_update','on_complete','on_cancel','on_teardown'],
        'state':'Documented context.instance/shared survives event callbacks; save/reload behavior not documented or observed.',
        'physical_checks':['unit existence','unit owner id','current gravity-well id','position within range','owner defeated'],
        'notification_action_enum':branch['properties']['notification_type']['enum'],
        'custom_notification_types_rejected_by_pinned_schema':True,
        'native_lua_notification_examples':['NOTIFY_PIRATE_INCURSION_STARTED: {}','NOTIFY_PIRATE_KING_ARRIVED: gravity_well_id + target_player_index'],
        'loot':'Native capture_points_total + destroy_on_capture, per-level collection duration/range; no exclusive-claim API identified.'},
      'not_verified':['global delivery to enemy without local vision','arbitrary event identity + actor + actual sector text','ability/payment commitment callback','exclusive one-claimant capture ownership','claim cancellation on departure/capture/death in native loot','reward exactly once under save/reload','runtime Lua loading/bindings in retail build','disconnect/defeat behavior','owner-only fixed industrial reward per placed site'],
      'excluded_from_supported_candidate':['major salvage','containment sample authorization','paid study','salvage-generated research','second capture system'],
      'contact_outputs':'4 native-schema-valid item/reward definitions plus project integration/localization fragments; no .player or manifest, not enabled',
      'sound':'Probe retains native pirate notifications/sounds and labels; no fake custom traffic voice',
      'duration_target_seconds':90,
      'sources':rows,'schemas':schema_rows}
    write(AUDIT/'capability-report.json',capability)
    write(AUDIT/'offline-validation.json',{'status':'PASS','definition_checks':checks,'lua':syntax,'runtime_status':'NOT RUN','engine_tests_observed':0,'disabled_register':True,'source_integrity_unchanged':all(sha(Path(r['path']))==r['sha256'] for r in rows)})
    write(OUT/'integration-record.json',{'supported_package_files':[],'experimental_only':list(definitions),'project_fragments':['contact-fragments.json','localization-fragment.json'], 'lua_probe':'scripts/expanse18_operations_native_probe.lua','must_not_merge_into_playtest_scripts':True,'manifest_owner':'integrator','major_operations':'gated'})
    print(json.dumps({'output':str(OUT),'definitions':len(definitions),'lua_syntax':syntax['status'],'runtime':'NOT RUN','gate':'unresolved'}))

if __name__ == '__main__': build()
