"""Menu-only Expanse backdrop over frozen 0.27.1; no installed-file writes."""
import copy,ctypes,ctypes.util,json,zipfile,shutil,math
from pathlib import Path
from common import ROOT,GAME,read,write
from validate_experiments import require,sha256,file_hashes
from doctrine_package import package,registries
BASE=ROOT/'build/experiments/expanse_update27_1'
OUT=ROOT/'build/experiments/expanse_update27_2_menu'
AUD=ROOT/'audit/menu27_2';ART=ROOT/'build/menu27_2-art'
FLEETS=[
 {'anchor':'expanse_donnager_battleship','high':'expanse12_scirocco','lead':'expanse27_hephaestus','low':'expanse12_raptor','wing':'expanse_mcrn_corvette'},
 {'anchor':'expanse15_truman','high':'expanse27_nathan_hale','lead':'expanse27_munroe','low':'expanse23_murphy','wing':'expanse23_murphy'},
]
def menu_id(n):return 'expanse_menu27_'+n.removeprefix('expanse_').removeprefix('trader_')

def lua_check(script, expected_counts=None):
    """Real Lua compilation + mocked existing scene API lifecycle, never the game."""
    lib=ctypes.CDLL(ctypes.util.find_library('lua5.4'))
    lib.luaL_newstate.restype=ctypes.c_void_p;lib.luaL_openlibs.argtypes=[ctypes.c_void_p]
    lib.luaL_loadbufferx.argtypes=[ctypes.c_void_p,ctypes.c_char_p,ctypes.c_size_t,ctypes.c_char_p,ctypes.c_char_p];lib.luaL_loadbufferx.restype=ctypes.c_int
    lib.lua_pcallk.argtypes=[ctypes.c_void_p,ctypes.c_int,ctypes.c_int,ctypes.c_int,ctypes.c_ssize_t,ctypes.c_void_p];lib.lua_pcallk.restype=ctypes.c_int
    lib.lua_tolstring.argtypes=[ctypes.c_void_p,ctypes.c_int,ctypes.POINTER(ctypes.c_size_t)];lib.lua_tolstring.restype=ctypes.c_char_p;lib.lua_close.argtypes=[ctypes.c_void_p]
    st=lib.luaL_newstate();lib.luaL_openlibs(st)
    mock='''
float3 = {new=function(self,x,y,z) return {x=x,y=y,z=z} end}
spawn_units_definition = {new=function(self) return {entries={}, add_required_units=function(self,n,c,o) table.insert(self.entries,{name=n,count=c,options=o}) end} end}
spawn_unit_options = {new=function(self) return {add_item=function() error("unexpected stock titan item") end} end}
local spawned, moves, holds, ai, damage = {},0,0,0,0
local alive={true,true}
local players={{race="trader_loyalist",index=1},{race="trader_loyalist",index=2}}
local sim={planets={},get_scenario_scene_gravity_well=function() return {} end,
 get_gravity_well_primary_fixture=function() return {} end,
 filter_playable_players=function() return {1,2} end,
 get_player_by_player_index=function(self,i) return players[i] end,
 set_player_ai_enabled=function(self,p,v) assert(v==false);ai=ai+1 end,
 set_player_can_units_receive_damage=function(self,p,v) assert(v==false);damage=damage+1 end,
 create_units=function(self,def,_,well,player,offset,flag,extra,dir)
  assert(math.abs(dir.x*dir.x+dir.y*dir.y+dir.z*dir.z-1)<1e-6)
  local units={}
  for _,e in ipairs(def.entries) do
   assert(e.options==nil)
   for i=1,e.count do local u={name=e.name,player=player.index};table.insert(units,u);table.insert(spawned,u) end
  end
  return units
 end,
 set_unit_auto_order_mode=function(self,u,m) assert(m=="hold_position");holds=holds+1 end,
 set_unit_return_to_gravity_well_enabled=function(self,u,v) assert(v==false) end,
 set_unit_ultimate_abilities_enabled=function(self,u,v) assert(v==false) end,
 issue_move_order=function(self,u,well,o) assert(o.ai_override=="never");moves=moves+1 end,
 is_unit_moving=function() return false end,
 does_gravity_well_contain_player_units=function(self,well,p) return alive[p.index] end}
'''
    tests='''
setup_scenario(sim)
assert(#spawned==12 and holds==8 and ai==2 and damage==2)
local expected=EXPECTED
local counts={}
for _,u in ipairs(spawned) do local k=u.player..":"..u.name;counts[k]=(counts[k] or 0)+1 end
for k,v in pairs(expected) do assert(counts[k]==v,k) end
local initial_moves=moves
on_update(sim,6)
assert(moves>initial_moves and #spawned==12)
alive[1]=false
on_update(sim,14)
assert(#spawned==12)
on_update(sim,1)
assert(#spawned==18)
for i=13,18 do assert(spawned[i].player==1) end
alive[1]=true
on_update(sim,30)
assert(#spawned==18)
'''
    expected={}
    for i,f in enumerate(FLEETS,1):
        for role,n in f.items():
            key=str(i)+':'+menu_id(n);expected[key]=expected.get(key,0)+(2 if role=='wing' else 1)
    if expected_counts is not None:expected=expected_counts
    literal='{'+','.join('['+json.dumps(k)+']='+str(v) for k,v in expected.items())+'}'
    code=(mock+script+tests.replace('EXPECTED',literal)).encode()
    try:
        result=lib.luaL_loadbufferx(st,code,len(code),b'menu27_2-test',None)
        if not result:result=lib.lua_pcallk(st,0,0,0,0,None)
        require(result==0,'Lua backdrop test: '+str(lib.lua_tolstring(st,-1,None)))
    finally:lib.lua_close(st)
    return {'status':'PASS Lua 5.4 / mocked engine API','initial_ships':12,'same_player_race_still_distinct_fleets':True,'foreground_patrol':'PASS','wiped_side_only_respawn_after_15s':'PASS','native_item_injection_absent':True,'engine_rendering':'NOT RUN'}

def prepare():
    edits={};origins={};units={};skins={};loc=read(BASE/'localized_text/en.localized_text');sources=sorted({n for f in FLEETS for n in f.values()})
    for n in sources:
        rel='entities/'+n+'.unit';u=read(BASE/rel);ident=menu_id(n);u=copy.deepcopy(u)
        # Scene-only copies: no player acquisition lists or extra identity tags.
        u['abilities']=[{'abilities':[a for group in u.get('abilities',[]) for a in group['abilities'] if 'magazine' in a or a=='expanse11_no_shields']}]
        for k in ['items','item_builds','colonize_ability','cloak_ability']:u.pop(k,None)
        newgroups=[]
        for gr in u['skin_groups']:
            group=copy.deepcopy(gr);group['skins']=[]
            for sn in gr['skins']:
                sr='entities/'+sn+'.unit_skin';sp=BASE/sr if (BASE/sr).exists() else GAME/sr;sk=read(sp);sid=ident+'_skin';group['skins'].append(sid)
                for stage in sk['skin_stages']:stage['is_main_view_icon_visible_camera_distance']=60000.
                edits['entities/'+sid+'.unit_skin']=sk;origins['entities/'+sid+'.unit_skin']=str(sp);skins[sid]=sn
            newgroups.append(group)
        u['skin_groups']=newgroups;edits['entities/'+ident+'.unit']=u;origins['entities/'+ident+'.unit']=str(BASE/rel);units[ident]=n
    source=GAME/'scenarios/front_end.scenario';pin=read(ROOT/'audit/update27_1/menu-backdrop-followup.json');require(sha256(source)==pin['sha256'],'Menu source changed since inspected baseline')
    with zipfile.ZipFile(source) as z:members={n:z.read(n) for n in z.namelist()}
    before=members['scenario.lua'].decode();start=before.index('local function get_fleet_for_race(race)');end=before.index('\n-- every titan spawns',start)
    tables=[]
    for f in FLEETS:tables.append('{'+','.join(k+'='+json.dumps(menu_id(v)) for k,v in f.items())+'}')
    replacement='''local function get_fleet_for_race(side_index)
    -- Menu-only MCRN / UNN display copies; bounded to six ships per side.
    local fleets = {FLEETS}
    local ships = fleets[side_index] or fleets[1]
    local main = {{unit=ships.anchor,count=1,forward=0,up=0,toward_camera=0}}
    for _, pair in ipairs({{"high","cap_high"},{"lead","cap_lead"},{"low","cap_low"}}) do
        local slot = formation_slots[pair[2]]
        table.insert(main,{unit=ships[pair[1]],count=1,forward=slot.forward,up=slot.up,toward_camera=slot.toward_camera})
    end
    return {main=main,wing={{unit=ships.wing,count=2}}}
end
'''.replace('FLEETS',','.join(tables))
    script=before[:start]+replacement+before[end:];oldcall='get_fleet_for_race(battle_player.player.race)';newcall='get_fleet_for_race(battle_player.wing_route_index)';require(script.count(oldcall)==1,'Changed menu dispatch');script=script.replace(oldcall,newcall)
    require(script[:start]==before[:start] and script[script.index('\n-- every titan spawns'):].replace(newcall,oldcall)==before[end:],'Unexpected menu loop/camera mutation')
    lifecycle=lua_check(script);members['scenario.lua']=script.encode();dest=ART/'scenarios/front_end.scenario';dest.parent.mkdir(parents=True,exist_ok=True)
    with zipfile.ZipFile(dest,'w',zipfile.ZIP_DEFLATED) as z:
        for n,data in members.items():z.writestr(n,data)
    with zipfile.ZipFile(source) as a,zipfile.ZipFile(dest) as b:
        require(a.namelist()==b.namelist(),'Scenario member list drift')
        for n in a.namelist():
            if n!='scenario.lua':require(a.read(n)==b.read(n),'Backdrop camera/configuration changed')
    meta=read(BASE/'.mod_meta_data');meta.update(display_version='0.27.2',display_name='The Expanse — 0.27.2 MENU BATTLE PREVIEW',short_description='0.27.1 repairs plus an isolated MCRN-versus-UNN menu display battle.',long_description='Standalone cumulative menu preview over regular 0.27.1. Twelve display ships, existing camera/patrol/respawn logic, no player build access for scene copies, no boarding or ship-launch abilities in the scene. Existing match definitions/art/audio remain unchanged. Menu visuals and runtime require user confirmation. Enable alone; restart after changing mods if the backdrop is cached.')
    edits['.mod_meta_data']=meta
    write(AUD/'scene-audit.json',{'source':str(source),'source_sha256':sha256(source),'scenario_sha256':sha256(dest),'fleets':FLEETS,'private_units':units,'private_skins':skins,'lua_lifecycle':lifecycle,'camera':'Native scene camera, positions, directions and waypoint routes byte-preserved; all menu skins render meshes to 60000 units. Scene staging is within 12000 units of camera.','abilities':'Only existing torpedo magazines and shieldless helper. No boarding/capture, free ship launch or equipment.','visuals':'NOT RUN'})
    return edits,origins,{'scenarios/front_end.scenario':dest}

def build():
    require(not OUT.with_suffix('.zip').exists(),'Menu candidate already frozen')
    edits,origins,art=prepare()
    if not OUT.exists():shutil.copytree(BASE,OUT,symlinks=True)
    for rel,d in edits.items():write(OUT/rel,d)
    for rel,src in art.items():(OUT/rel).parent.mkdir(parents=True,exist_ok=True);shutil.copy2(src,OUT/rel)
    registries(OUT);shutil.copy2(ROOT/'docs/menu27_2.md',OUT/'PLAYTEST-README.md')
    # All original game definitions, models and sound must be identical.
    preserved=file_hashes(BASE)
    for rel,h in preserved.items():
        if rel not in ['.mod_meta_data','PLAYTEST-README.md'] and not rel.endswith('.entity_manifest'):require(sha256(OUT/rel)==h,'Existing gameplay/art changed '+rel)
    clones=set(read(AUD/'scene-audit.json')['private_units'])
    for p in (OUT/'entities').glob('*.player'):
        data=p.read_text();require(not any('"'+n+'"' in data for n in clones),'Scene ship leaked into player lists')
    report=package(BASE,OUT,edits,origins,ROOT/'docs/menu27_2.md',AUD,art,package_existing=True)
    write(AUD/'acceptance-check.json',{'status':'PASS OFFLINE','base_zip_sha256':sha256(BASE.with_suffix('.zip')),'existing_files_unchanged':len(preserved)-4,'private_units_unavailable_to_players':len(clones),'regular_match_art_audio_and_balance':'UNCHANGED','runtime_menu':'NOT RUN'})
    return report
if __name__=='__main__':print(json.dumps(build(),indent=2))
