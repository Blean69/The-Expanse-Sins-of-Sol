"""Shared hull foundations and generated faction access; no runtime Python."""
from pathlib import Path
import copy
from validate_experiments import read,require
from update20_fleet import ROOT,GAME
BASE=ROOT/'build/experiments/expanse_update20'
COMMAND='expanse21_opa_command'
PATROL='expanse21_contract_patrol'
FACTIONS={'mcrn':'expanse18_mcrn','unn':'expanse18_unn','opa':'expanse18_opa'}
WRAPPERS={'trader_loyalist':'mcrn','trader_rebel':'opa','dlc_trader_loyalist':'unn'}
CUSTOM={
 'mcrn':['trader_light_frigate','expanse_mcrn_corvette','expanse12_raptor','expanse12_scirocco','expanse_donnager_battleship','expanse19_artemis'],
 'unn':[PATROL,'expanse15_truman','expanse_amun_ra','expanse19_artemis'],
 'opa':[PATROL,'expanse19_europa_bane','expanse19_artemis','expanse_rocinante_hero','expanse12_pella',COMMAND]}

def foundations(base=BASE):
    edits={};loc={};origins={}
    def get(n,k='unit'):return read(base/'entities'/f'{n}.{k}')
    def put(n,k,d,source):
        rel=f'entities/{n}.{k}';edits[rel]=d;origins[rel]=str(base/'entities'/f'{source}.{k}')
    # Temporary contracted patrol hull uses existing art while Earth/Belt fleets
    # retain an affordable opening. Distinct identity, ordinary supply/costs.
    d=get('trader_light_frigate');d['skin_groups']=[{'skins':[PATROL]}]
    for idx,m in enumerate(d['weapons']['weapons']):
        source=m['weapon'];w=get(source,'weapon');ident=PATROL+f'_pdc_{idx}'
        w['damage']=85*w['cooldown_duration'];put(ident,'weapon',w,source);m['weapon']=ident
    d['ai']['attack_target_type_groups_matching_weapon']=d['weapons']['weapons'][0]['weapon']
    put(PATROL,'unit',d,'trader_light_frigate')
    skin=get('trader_light_frigate','unit_skin');gui=skin['skin_stages'][0]['gui']
    gui.update(name=PATROL+'.name',description=PATROL+'.description');gui.pop('special_operation_names',None)
    put(PATROL,'unit_skin',skin,'trader_light_frigate')
    loc[PATROL+'.name']='Contract Patrol Frigate'
    loc[PATROL+'.description']='Temporary Earth/Belt patrol refit using the Morrigan exterior. Two 85-DPS PDCs; surplus Martian light torpedo equipment. 40 supply. Shared placeholder, not a canonical UNN or OPA ship class.'
    # Expeditionary role is a separate capital, not a mutation of Europa frigate.
    d=get('expanse19_europa_bane');cap=get('expanse12_scirocco')
    for k in ['levels','items','antimatter','item_builds','capture_points','is_loot_collector']:
        d[k]=copy.deepcopy(cap[k])
    d['target_filter_unit_type']='capital_ship';d['tags']=['capital_ship',COMMAND]
    d['build'].update(build_kind='capital_ship',build_group_id='capital_ship',supply_cost=150,build_time=100.,price={'credits':3200.,'metal':650.,'crystal':400.})
    d['user_interface']=copy.deepcopy(cap['user_interface']);d['spatial']['collision_rank']=2
    d['ai_attack_target']['attack_target_type']='capital';d['formation']=copy.deepcopy(cap['formation'])
    d['skin_groups']=[{'skins':[COMMAND]}]
    first=copy.deepcopy(d['health']['levels'][0]);d['health']['levels']=[]
    for i in range(10):
        level=copy.deepcopy(first)
        level['max_hull_points']=first['max_hull_points']*(1+.03*i)
        level['max_armor_points']=first['max_armor_points']*(1+.03*i)
        level['experience_given_on_death']=cap['health']['levels'][i]['experience_given_on_death']
        d['health']['levels'].append(level)
    d['abilities'][0]['abilities'].insert(0,'expanse15_scirocco_engineering_teams')
    d['ship_roles']=['attack_ship'];put(COMMAND,'unit',d,'expanse19_europa_bane')
    skin=get('expanse19_europa_bane','unit_skin');skin['skin_stages'][0]['gui'].update(name=COMMAND+'.name',description=COMMAND+'.description')
    put(COMMAND,'unit_skin',skin,'expanse19_europa_bane')
    loc[COMMAND+'.name']='OPA Expeditionary Command Ship'
    loc[COMMAND+'.description']='Mod-original repeatable command refit using Europa’s Bane exterior. 150 supply; 2,500 hull and 1,500 armor at level 1. Colony equipment, bounded repair and separate local siege stores; no railgun or cloak. 3% hull/armor growth per level.'
    # Native cruiser production kind bypasses the first-free-capital entitlement,
    # while the ship remains a capital for combat, progression, and UI grouping.
    pella=get('expanse12_pella');pella['build']['build_kind']='cruiser'
    pella['build']['prerequisites']=[['expanse21_opa_surplus']];put('expanse12_pella','unit',pella,'expanse12_pella')
    amun=get('expanse_amun_ra');amun['build']['prerequisites']=[['expanse21_unn_black_budget']];put('expanse_amun_ra','unit',amun,'expanse_amun_ra')
    tags=read(base/'uniforms/unit_tag.uniforms')
    # Existing registry is a full deliberate overwrite; new hull selection uses
    # unit tags, never the bounded 32-entry weapon registry.
    require(COMMAND not in str(tags),'Command tag already exists')
    tags['unit_tags'].append({'name':COMMAND,'localized_name':COMMAND+'.name'});edits['uniforms/unit_tag.uniforms']=tags
    return edits,loc,origins

def players(base,edits,loc,research,items,planet_items,sandbox=False):
    report={}
    common=[x for x in read(base/'entities/expanse18_mcrn.player')['buildable_units'] if not x.startswith('expanse') and x!='trader_light_frigate']
    # Existing TEC escorts/support remain named transitional models. Native
    # capital/titan roster remains accessible only in the combined sandbox.
    essential=[x for x in common if 'capital_ship' not in x and 'titan' not in x]
    native_all=read(base/'entities/expanse18_mcrn.player')['buildable_units']
    owners={**{v:k for k,v in FACTIONS.items()},**WRAPPERS}
    for ident,faction in owners.items():
        d=read(base/'entities'/f'{ident}.player')
        roster=list(dict.fromkeys(native_all+[PATROL,COMMAND])) if sandbox else essential+CUSTOM[faction]
        d['buildable_units']=roster
        if not sandbox:d['faction_buildable_units']=[x for x in d['faction_buildable_units'] if x in roster]
        available_research=list(dict.fromkeys(sum(research.values(),[]))) if sandbox else research[faction]
        d['research']['research_subjects']+=available_research
        available_items=list(dict.fromkeys(sum(items.values(),[]))) if sandbox else items[faction]
        d['ship_components']=list(dict.fromkeys(d['ship_components']+available_items))
        pi=list(dict.fromkeys(sum(planet_items.values(),[]))) if sandbox else planet_items[faction]
        d['planet_components']=list(dict.fromkeys(d['planet_components']+pi))
        if not sandbox:
            obsolete={'dlc2_trader_unlock_loyalist_super_capital_ship','dlc2_trader_upgrade_loyalist_super_limit_0','dlc2_trader_upgrade_loyalist_super_limit_1'}
            d['research']['research_subjects']=[n for n in d['research']['research_subjects'] if n not in obsolete]
            d['research']['faction_research_subjects']=[n for n in d['research'].get('faction_research_subjects',[]) if n not in obsolete]
            replacement='trader_light_frigate' if faction=='mcrn' else PATROL
            for escort in d['trade']['trade_ship_escorts']:
                if faction!='mcrn':escort['unit']=PATROL if escort['unit']=='trader_light_frigate' else 'trader_antiarmor_frigate'
            for item in d['garrison']['units']['random_units']:
                if item['unit']=='trader_light_frigate':item['unit']=replacement
        edits[f'entities/{ident}.player']=d
        if ident in FACTIONS.values():
            key=d['gui']['faction_description']
            loc[key]=('Combined Fleet Sandbox: all Expanse and transitional TEC hulls; shared sources, full prices and ordinary supply.' if sandbox else {
                'mcrn':'MCRN: Morrigan, Tachi, Raptor, Scirocco and Donnager. Quality, coordination and recovery. Shared TEC support remains during conversion.',
                'unn':'UNN: Truman, contracted patrols and transitional TEC escorts. Amun-Ra requires Black-Budget Procurement. Logistics and territorial defense.',
                'opa':'OPA: Europa’s Bane, Artemis, repeatable expeditionary command and Rocinante. Pella requires paid Diverted Martian Surplus. Contract patrols cover the opening.'}[faction])
        report[ident]={'faction':faction,'roster':roster,'research':available_research,'items':available_items,'planet_items':pi,'trade_escorts':d['trade']['trade_ship_escorts'],'garrison':d['garrison']['units']}
    if True:
        for p in (base/'entities').glob('*.start_mode'):
            d=read(p)
            def replace(o,old,new):
                if isinstance(o,list):
                    for v in o:replace(v,old,new)
                elif isinstance(o,dict):
                    if o.get('unit')==old:o['unit']=new
                    for v in o.values():replace(v,old,new)
            for cfg in d.get('faction_configurations',[]):
                faction=owners.get(cfg['player_definition_id'])
                if faction and faction!='mcrn' and not sandbox:replace(cfg,'trader_light_frigate',PATROL)
                if faction and p.name=='quick_start_mode.start_mode':
                    for formation in cfg['home_planet'].get('starting_units_in_formations',[]):
                        for row in formation.get('required_units',[]):
                            if row['unit'] in ['trader_light_frigate',PATROL]:row['count']=[6,6]
                            if row['unit']=='trader_scout_corvette':row['count']=[2,2]
                if faction and p.name=='advanced_start_mode.start_mode':
                    for formation in cfg['home_planet'].get('starting_units_in_formations',[]):
                        for row in formation.get('required_units',[]):
                            if row['unit'] in ['trader_light_frigate',PATROL]:row['count']=[10,10]
                    def smaller_grants(o):
                        if isinstance(o,dict):
                            if o.get('unit') in ['trader_light_frigate',PATROL]:o['count']=[2,2]
                            for v in o.values():smaller_grants(v)
                        elif isinstance(o,list):
                            for v in o:smaller_grants(v)
                    smaller_grants(cfg.get('additional_starting_planets',{}).get('granted_planets_units_in_formations',[]))
            edits['entities/'+p.name]=d
    return report
