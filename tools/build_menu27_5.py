"""Finished-model backdrop over tested 0.27.4; zero match definition edits."""
import copy,json,zipfile
from common import ROOT,GAME,read,write
from validate_experiments import require,sha256,file_hashes
from doctrine_package import package
from build_update27_3 import stage
from update27_3_loadfixes import check
import build_menu27_2 as scene
BASE=ROOT/'build/experiments/expanse_update27_4';OUT=ROOT/'build/experiments/expanse_update27_5_menu';AUD=ROOT/'audit/menu27_5';ART=ROOT/'build/menu27_5-art';DOC=ROOT/'docs/menu27_5.md'
FLEETS=[
 {'anchor':'expanse_donnager_battleship','high':'expanse12_scirocco','lead':'expanse27_hephaestus','low':'expanse12_raptor','wing':'expanse_mcrn_corvette'},
 {'anchor':'expanse15_truman','high':'expanse27_munroe','lead':'expanse24_gathering_storm','low':'expanse_amun_ra','wing':'trader_light_frigate'}]

def build():
    require(not OUT.with_suffix('.zip').exists(),'Menu already frozen')
    scene.BASE=BASE;scene.AUD=AUD;scene.ART=ART;scene.FLEETS=FLEETS
    edits,origins,art=scene.prepare();audit=read(AUD/'scene-audit.json');private=set(audit['private_units']);ability_map={}
    for ident in private:
        u=edits['entities/'+ident+'.unit'];u.get('build',{}).pop('prerequisites',None)
        # Display units cannot depend on whichever random faction the native
        # backdrop chooses. Private fixed-level abilities use unchanged ADS/buffs.
        for group in u['abilities']:
            result=[]
            for aid in group['abilities']:
                if aid not in ability_map:
                    source=BASE/'entities'/(aid+'.ability');a=read(source)
                    if a['level_source']=='fixed_level_0':ability_map[aid]=aid
                    else:
                        require(a['level_source']=='research_prerequisites_per_level','Unreviewed scene ability level source')
                        new='expanse_menu27_5_'+aid.removeprefix('expanse_');a['level_source']='fixed_level_0';a.pop('level_prerequisites',None)
                        edits['entities/'+new+'.ability']=a;origins['entities/'+new+'.ability']=str(source);ability_map[aid]=new
                result.append(ability_map[aid])
            group['abilities']=result
    scenario=art['scenarios/front_end.scenario']
    with zipfile.ZipFile(scenario)as z:members={n:z.read(n)for n in z.namelist()}
    script=members['scenario.lua'].decode();old='return {main=main,wing={{unit=ships.wing,count=2}}}'
    require(script.count(old)==1,'Unexpected scene roster template')
    morrigan=scene.menu_id('trader_light_frigate');tachi=scene.menu_id('expanse_mcrn_corvette');amun=scene.menu_id('expanse_amun_ra')
    replacement='local wing = side_index == 1 and {{unit='+json.dumps(tachi)+',count=1},{unit='+json.dumps(morrigan)+',count=1}} or {{unit='+json.dumps(amun)+',count=2}}\n    return {main=main,wing=wing}'
    script=script.replace(old,replacement);expected={}
    for i,f in enumerate(FLEETS,1):
        for k,n in f.items():
            if k=='wing':continue
            key=str(i)+':'+scene.menu_id(n);expected[key]=expected.get(key,0)+1
    expected['1:'+tachi]=1;expected['1:'+morrigan]=1;expected['2:'+amun]+=2
    lifecycle=scene.lua_check(script,expected);members['scenario.lua']=script.encode()
    with zipfile.ZipFile(scenario,'w',zipfile.ZIP_DEFLATED)as z:
        for n,data in members.items():z.writestr(n,data)
    meta=read(BASE/'.mod_meta_data');meta.update(display_version='0.27.5',display_name='The Expanse — 0.27.5 Finished Fleet Menu',short_description='0.27.4 repairs plus a finished-model menu battle with no scene research dependencies.',long_description='Standalone cumulative menu candidate. MCRN line: Donnager, Scirocco, Hephaestus, Raptor, Tachi and Morrigan. Opposing showcase: Truman, Munroe, Gathering Storm and Amun-Ra. Private display copies have no procurement or ability research requirements, cloak, boarding or ship launch. Match files unchanged. Pella GUI prompt remains unresolved; plating not included. Enable alone; restart.')
    edits['.mod_meta_data']=meta;stage(BASE,OUT,edits,art,DOC)
    before=file_hashes(BASE);after=file_hashes(OUT);unchanged=[]
    for rel,h in before.items():
        if rel in ['.mod_meta_data','PLAYTEST-README.md']or rel.endswith('.entity_manifest'):continue
        require(after[rel]==h,'Regular game changed '+rel);unchanged.append(rel)
    for ident in private:
        u=read(OUT/'entities'/(ident+'.unit'));require(not u.get('build',{}).get('prerequisites'),'Scene procurement prerequisite')
        require(not any(k in u for k in ['carrier','unit_factory','items','item_builds','cloak_ability','colonize_ability']),'Unexpected scene spawner/equipment hook')
        for gr in u['abilities']:
            for aid in gr['abilities']:
                a=read(OUT/'entities'/(aid+'.ability'));require(a['level_source']=='fixed_level_0' and not a.get('level_prerequisites'),'Scene research level dependency')
    for p in (OUT/'entities').glob('*.player'):
        require(not any('"'+n+'"'in p.read_text()for n in private),'Menu ship acquired by normal player')
    # Explicitly test a faction with no technology knowledge; all direct scene
    # procurement/ability queries must be satisfiable without any research IDs.
    require(all(not read(OUT/'entities'/(n+'.unit')).get('build',{}).get('prerequisites') for n in private),'Empty-research owner failed')
    audit.update(scenario_sha256=sha256(scenario),actual_spawn_counts=expected,private_ability_sources=ability_map,lua_lifecycle=lifecycle,abilities='Fixed level zero private torpedo-magazine abilities + existing shieldless helper. No owner research, cloak, capture, free ships or items.',previous_failure_prevention=['Hephaestus native heavy target type inherited from 0.27.4','No rebel-titan or other procurement prerequisites on any display copy','Private magazine levels require no owner research'],user_evidence='0.27.4 user reports no crash observed; Pella prompt remains. This does not validate the new menu.',plating='Not included: existing Composite item is inert; shield-disable exception and production/study behavior not implemented.')
    write(AUD/'scene-audit.json',audit);write(AUD/'acceptance-check.json',{**check(OUT),'crash_reproduction':'New menu NOT RUN; user observed no crash in 0.27.4 test, with Pella GUI prompt unresolved','existing_game_files_unchanged':len(unchanged),'empty_research_owner_check':'PASS','private_units':len(private),'private_research_free_abilities':len([a for a,b in ability_map.items()if a!=b]),'lua_lifecycle':lifecycle,'runtime_menu':'NOT RUN','plating':'NOT INCLUDED'})
    print(json.dumps(package(BASE,OUT,edits,origins,DOC,AUD,art,package_existing=True),indent=2))
if __name__=='__main__':build()
