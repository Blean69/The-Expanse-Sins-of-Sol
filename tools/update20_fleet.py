"""Stage1 supply and Morrigan-role overlay over frozen0.19; no historical multipliers."""
from pathlib import Path
import copy,json
from validate_experiments import read,require,sha256,strings
from build_polish import write
ROOT=Path(__file__).resolve().parents[1]
BASE=ROOT/'build/experiments/expanse_update19'
GAME=ROOT.parent/'SteamLibrary/steamapps/common/Sins2'
SUPPLY={'trader_light_frigate':40,'expanse_mcrn_corvette':95,'expanse19_europa_bane':95,'expanse15_truman':185,'expanse_donnager_battleship':500,'expanse_amun_ra':70,'expanse19_artemis':8}
NAMES={'trader_light_frigate':'Morrigan','expanse_mcrn_corvette':'Tachi','expanse19_europa_bane':"Europa's Bane",'expanse15_truman':'Truman','expanse_donnager_battleship':'Donnager','expanse_amun_ra':'Amun-Ra','expanse19_artemis':'Artemis','expanse12_scirocco':'Scirocco','expanse12_pella':'Pella','expanse12_raptor':'Raptor','expanse_rocinante_hero':'Rocinante','trader_scout_corvette':'Sunflare'}

def changes():
    out={};loc={};acquisition=[]
    for ident,supply in SUPPLY.items():
        d=read(BASE/'entities'/f'{ident}.unit');d['build']['supply_cost']=supply
        if ident=='expanse_mcrn_corvette':
            europa=read(BASE/'entities/expanse19_europa_bane.unit')['build']['price']['metal'];require(europa==350,'Review Tachi floor against changed Europa price')
            d['build']['price']['metal']=max(d['build']['price']['metal'],400.)
        out[f'entities/{ident}.unit']=d
    mounts=read(BASE/'entities/trader_light_frigate.unit')['weapons']['weapons']
    for mount in mounts:
        ident=mount['weapon'];p=BASE/'entities'/f'{ident}.weapon';d=read(p)
        require(d['penetration']==0 and abs(d['damage']/d['cooldown_duration']-117.6)<1e-8,'Morrigan fallback baseline changed')
        users=[q.stem for q in (BASE/'entities').glob('*.unit') if ident in [w['weapon'] for w in read(q).get('weapons',{}).get('weapons',[])]]
        require(users==['trader_light_frigate'],'Morrigan weapon unexpectedly shared')
        d['damage']=round(88.2*d['cooldown_duration'],6);out[f'entities/{ident}.weapon']=d
    for p in sorted((BASE/'entities').glob('*launch_corvette.action_data_source')):
        d=read(p)
        for v in d['action_values']:
            if v['action_value_id']=='launch_metal':v['action_value']['values']=[out['entities/expanse_mcrn_corvette.unit']['build']['price']['metal']]
            if v['action_value_id']=='pirate_mercenary_base_available_supply_value':v['action_value']['values']=[95.]
        out['entities/'+p.name]=d
        loc[p.stem+'.description']='Deploy one standard MCRN Tachi for 300 credits and 400 metal. Requires and consumes 95 ordinary fleet supply. Existing arrival delay and cooldown are unchanged.'
        acquisition.append({'path':p.stem,'supply':95,'metal':400,'mechanism':'spawn_units with owner supply constraint; ordinary unit, no reserve/special-operation exemption','refund':'Native action cost/payment behavior; no custom refund or reserve ledger'})
    # Explicit1x default preserves native lobby2x as an optional stress setting.
    d=read(BASE/'uniforms/player.uniforms');d['max_fleet_supply_scalar']=1.;out['uniforms/player.uniforms']=d
    loc['lobby_option_max_fleet_supply_scalar.name']='Fleet Supply Multiplier (1x doctrine balance)'
    loc['lobby_option_max_fleet_supply_scalar.description']='Use 1x for the supported 2,000-supply doctrine balance. 2x is a 4,000-supply stress test; comparison forces and balance targets assume 1x.'
    loc['expanse20.fleet.note']='Doctrine balance: Morrigan40 supply, Tachi95, Donnager500, Truman185. Morrigan PDCs88.2 base DPS per mount. Standard Tachi400 metal. Other combat performance is unchanged.'
    for ident in NAMES:
        skin=read(BASE/'entities'/f'{ident}.unit')['skin_groups'][0]['skins'][0]
        p=BASE/'entities'/f'{skin}.unit_skin'
        if not p.exists():p=GAME/'entities'/f'{skin}.unit_skin'
        key=read(p)['skin_stages'][0]['gui']['description']
        old=read(BASE/'localized_text/en.localized_text').get(key)
        if old is None:continue
        if ident=='trader_light_frigate':loc[key]='Fast Martian escort/patrol frigate. Two PDCs at 88.2 base DPS each and two bow tubes; fires one light torpedo every 10 seconds. 40 fleet supply. Interception and tracking unchanged.'
        if ident=='expanse_mcrn_corvette':loc[key]='Fast-attack torpedo frigate. Six PDCs and twin light torpedo launchers. 95 fleet supply; 300 credits and 400 metal; 20-second build.'
    acquisition.extend([{'path':'factory','unit':i,'supply':n,'mechanism':'normal build.supply_cost'} for i,n in SUPPLY.items()])
    # Native trade escorts and garrisons are deliberately separate local special
    # operations, not freely controllable ordinary launches. Do not double-charge.
    for p in sorted((BASE/'entities').glob('*.player')):
        d=read(p)
        if 'trade' not in d:continue
        for escort in d['trade'].get('trade_ship_escorts',[]):
            if escort['unit'] in SUPPLY:acquisition.append({'path':p.stem+'.trade','definition':escort,'policy':'Preserved native automatic trade_escort special operation; separate from ordinary fleet. No new controllable/free Tachi spawn path.'})
        if d.get('garrison'):acquisition.append({'path':p.stem+'.garrison','mechanism':'Native build_from_factory special_operation garrison, own local supply','policy':'Existing local garrison rules retained; unit supply changes affect its own budget, not double-charged ordinary fleet.'})
    refs=[]
    for p in sorted((BASE/'entities').iterdir()):
        if p.suffix not in ['.unit','.ability','.buff','.action_data_source','.npc_reward','.player','.start_mode']:continue
        d=read(p)
        hits=[{'path':'/'.join(map(str,path)),'unit':v} for path,v in strings(d) if v in ['expanse_mcrn_corvette','trader_light_frigate']]
        if hits:refs.append({'definition':p.name,'references':hits})
    return out,loc,{'acquisition_paths':acquisition,'all_matching_references':refs,'capture':'Existing per_build_or_virtual_supply target transforms read actual95 supply; no fixed Tachi capture price. Guarded resolution checked in ability overlay.','runtime':'NOT RUN'}

def balance_report(edits):
    def unit(ident):return edits.get(f'entities/{ident}.unit',read(BASE/'entities'/f'{ident}.unit'))
    scalar=read(GAME/'uniforms/unit.uniforms')['damage_scalar_per_additive_defensive_value']
    targets=['trader_light_frigate','expanse_mcrn_corvette','expanse12_pella','expanse15_truman','expanse_donnager_battleship']
    rows=[]
    for ident,name in NAMES.items():
        old=read(BASE/'entities'/f'{ident}.unit');d=unit(ident);mounts=[];raw=0
        for m in d.get('weapons',{}).get('weapons',[]):
            w=edits.get('entities/'+m['weapon']+'.weapon',read(BASE/'entities'/(m['weapon']+'.weapon')))
            if 'point_defense' not in w.get('tags',[]):continue
            require('burst_pattern' not in w,'Unexpected mechanical burst')
            dps=w['damage']/w['cooldown_duration'];raw+=dps
            mounts.append({'weapon':m['weapon'],'damage':w['damage'],'cooldown':w['cooldown_duration'],'raw_dps':dps,'penetration':w['penetration']})
        effective=[]
        for t in targets:
            v=unit(t);dur=v['health']['durability'];armor=v['health']['levels'][0].get('armor_strength',0)
            hull=sum(w['raw_dps']/(1+max(dur-w['penetration'],0)*scalar) for w in mounts)
            effective.append({'target':NAMES[t],'exposed_hull_dps_all_mounts':hull,'armor_layer_dps_all_mounts':hull/(1+armor*scalar),'with_fire_control_hull_dps':hull*1.05})
        rows.append({'unit':ident,'name':name,'supply_before':old['build']['supply_cost'],'supply':d['build']['supply_cost'],'resources':d['build']['price'],'exotic_price':d['build'].get('exotic_price',[]),'build_seconds':d['build']['build_time'],'hull':d['health']['levels'][0]['max_hull_points'],'armor':d['health']['levels'][0].get('max_armor_points',0),'durability':d['health']['durability'],'armor_strength':d['health']['levels'][0].get('armor_strength',0),'mounts':mounts,'raw_pdc_dps_per_hull':raw,'raw_pdc_dps_per_supply':raw/d['build']['supply_cost'],'effective':effective})
    return {'status':'CALCULATED, NOT OBSERVED','damage_scalar_per_additive_defensive_value':scalar,'formula_reference':'https://www.sinsofasolarempire2.com/article/525851/the-art-of-war-update---sins-of-a-solar-empire-ii','rows':rows,'limits':['Nominal continuous all-mount PDC envelope; actual arcs, target allocation, interception, overkill, reloads, movement, research and cripple states affect observed results.','Exposed hull and armor layer reported separately; no invented target-class multiplier. Penetration offsets durability but not armor strength.','PDC numbers exclude railguns and torpedoes; those definitions and schedules remain byte-identical.','No casualty, torpedo-leakage or winner claims without runtime trials.']}

if __name__=='__main__':
    edits,loc,audit=changes()
    for rel,d in edits.items():write(ROOT/'build/laboratory/update20/fleet'/rel,d)
    write(ROOT/'audit/update20/fleet-localization.json',loc);write(ROOT/'audit/update20/acquisition.json',audit);write(ROOT/'audit/update20/fleet-arithmetic.json',balance_report(edits))
    print('Stage1fleet definitions',len(edits))
