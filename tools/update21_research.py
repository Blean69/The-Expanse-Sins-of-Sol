"""Owner-scoped Stage 2 specialty research. New definitions only; merges returned for integrator."""
from __future__ import annotations
import copy,json
from pathlib import Path
BASE=Path('/run/media/haker/NVME 2/expanse-mod/build/experiments/expanse_update20')
GAME=Path('/run/media/haker/NVME 2/SteamLibrary/steamapps/common/Sins2')
FACTIONS={x:'expanse18_'+x for x in ['mcrn','unn','opa']}

def changes(base=BASE):
    base=Path(base);edits={};strings={};patches={x:{'research_subjects':[],'ship_components':[],'planet_components':[]} for x in FACTIONS};report={'mapping':[],'shared_definition_merges':[],'deferred':[],'runtime':'NOT RUN'}
    def read(n,ext):
        p=base/'entities'/f'{n}.{ext}';return json.loads((p if p.exists() else GAME/'entities'/f'{n}.{ext}').read_text())
    def put(n,ext,d):edits[f'entities/{n}.{ext}']=d
    def labels(n,name,desc):
        strings[n+'.name']=name;strings[n+'.name_uppercase']=name.upper();strings[n+'.description']=desc
        return {'name':n+'.name','name_uppercase':n+'.name_uppercase','description':n+'.description'}
    def research(faction,slug,name,desc,template,prereqs=None):
        n=f'expanse21_{faction}_{slug}';src=read(template,'research_subject')
        d={k:copy.deepcopy(src[k]) for k in ['version','domain','tier','field','research_time','price','exotic_price','hud_icon','tooltip_picture'] if k in src}
        # A separate row below the inherited TEC graph avoids overlapping or moving native nodes.
        i=len(patches[faction]['research_subjects']);d['field_coord']=[2*d['tier']+(i%2),14+4*list(FACTIONS).index(faction)+i//2]
        if prereqs:d['prerequisites']=[prereqs]
        d.update(labels(n,name,desc));put(n,'research_subject',d);patches[faction]['research_subjects'].append(n)
        report['mapping'].append({'id':n,'faction':FACTIONS[faction],'name':name,'description':desc,'template':template,
            'tier':d['tier'],'domain':d['domain'],'price':d['price'],'research_time':d['research_time'],'prerequisites':prereqs or []})
        return n,d
    def passive(n,kind,modifier,value):
        put(n,'action_data_source',{'version':0,'action_values':[{'action_value_id':'bonus','action_value':{'values':[value]}}]})
        put(n,'buff',{'version':0,'stacking_limit':{'stacking_limit':'fixed_one','stacking_limit_met_behavior':'preserve_existing_buff'},
            'stacking_ownership_type':'for_all_players','restart_other_stacked_buffs_when_started':False,
            kind:[{'modifier_type':modifier,'value_behavior':'scalar','value_id':'bonus'}]})
        put(n,'ability',{'version':0,'action_data_source':n,'level_source':'fixed_level_0','passive_actions':{'persistant_buff':n}})
    def item(n,name,desc,template,gate,category):
        d=read(template,'unit_item')
        for k in ['item_level_count','item_level_source','item_level_prerequisites','unit_modifiers','ability','other_item_requirements']:d.pop(k,None)
        d.update({k:v for k,v in labels(n,name,desc).items() if k!='name_uppercase'})
        d['max_count_on_unit']=1
        if category=='planet_components':
            for group in d['planet_type_groups']:group['build_prerequisites']=[[gate]]
            d['other_item_requirements']={'mutually_exclusive_items':[template]}
        else:d['build_prerequisites']=[[gate]]
        put(n,'unit_item',d);return d
    def symmetric_exclusion(source, derivative):
        original=read(source,'unit_item');requirements=copy.deepcopy(original.get('other_item_requirements',{}))
        key=f'entities/{source}.unit_item'
        previous=next((x for x in report['shared_definition_merges'] if x['file']==key),None)
        if previous:requirements=copy.deepcopy(previous['set_fields']['other_item_requirements'])
        requirements.setdefault('mutually_exclusive_items',[]).append(derivative)
        if previous:previous['set_fields']['other_item_requirements']=requirements
        else:report['shared_definition_merges'].append({'file':key,'set_fields':{'other_item_requirements':requirements}})
    # MCRN civilian: a paid installed planet component is the explicit local investment.
    n,d=research('mcrn','terraforming_bonds','Terraforming Directorate Bonds',
        'Unlocks a paid Directorate Bonds planet component on developed colonies. While fitted: +10% local commerce income; one slot. No empire-wide income bonus.',
        'trader_unlock_commercial_district_unit_item',['trader_unlock_commercial_district_unit_item'])
    it=n+'_module';m=item(it,'Directorate Bonds Office','Paid local economic investment: +10% commerce income while fitted. Requires a level-5 developed colony; one planet component slot.', 'trader_commercial_district',n,'planet_components')
    m['other_item_requirements']['mutually_exclusive_items'] += ['trader_industrial_complex','trader_high_density_district'];symmetric_exclusion('trader_commercial_district',it);m['ability']=it;passive(it,'planet_modifiers','commerce_track_credit_income_rate',.1);patches['mcrn']['planet_components'].append(it)
    n,d=research('mcrn','closed_loop','Closed-Loop Habitat Engineering','Reduces civilian colony development-track build times by 10%. Does not alter ship production.', 'trader_planet_track_upgrade_rate')
    d['planet_modifiers']=[{'modifier_type':'any_development_track_build_time','value_behavior':'scalar','value':-.1}]
    n,d=research('mcrn','precision_manufacturing','Precision Manufacturing','Unlocks two discounted equipment supply contracts: Combat Repair System and Antimatter Engine, each 10% cheaper in ordinary resources. Their native effects and exotic costs are unchanged.', 'trader_trade_port_income_rate_0',['trader_unlock_combat_repair_system_unit_item'])
    for source in ['trader_combat_repair_system','trader_antimatter_engine']:
        it='expanse21_mcrn_precision_'+source.removeprefix('trader_');m=read(source,'unit_item')
        m['price']={k:round(v*.9,4) for k,v in m['price'].items()}
        for group in m.setdefault('build_prerequisites',[[]]):group.append(n)
        m['other_item_requirements']={'mutually_exclusive_items':[source]}
        m.update({k:v for k,v in labels(it,'Precision Contract: '+source.removeprefix('trader_').replace('_',' ').title(),
            '10% ordinary-resource discount. Same native equipment effect and exotic cost; incompatible with its standard counterpart.').items() if k!='name_uppercase'})
        put(it,'unit_item',m);symmetric_exclusion(source,it);patches['mcrn']['ship_components'].append(it)
    # MCRN military: extend existing bounded disruption, never capture chance.
    n,d=research('mcrn','mmc_certification','MMC Assault Certification','Adds one second to trained Scirocco Marine Breaching Teams disruption (13 to 14 seconds). Movement/firing penalties, protection and capture probabilities are unchanged.', 'trader_upgrade_experience_gain_0',['trader_upgrade_experience_gain_0'])
    ads=read('expanse15_scirocco_breaching_teams','action_data_source');ads['level_count']=3
    for row in ads['action_values']:
        a=row['action_value'];a['values'].append(a['values'][-1]+1 if row['action_value_id']=='duration' else a['values'][-1])
    put(n+'_support','action_data_source',ads)
    old=read('expanse15_scirocco_breaching_teams','ability')
    report['shared_definition_merges'].append({'file':'entities/expanse15_scirocco_breaching_teams.ability','set_fields':{
        'action_data_source':n+'_support','level_prerequisites':old['level_prerequisites']+[[[n]]]}})
    n,d=research('mcrn','redundant_command','Redundant Command Systems','Unlocks a paid capital/command component providing +15% antimatter capacity. No damage, shield, reload or regeneration bonus.', 'trader_unlock_antimatter_engine_unit_item')
    it=n+'_module';m=item(it,'Redundant Command Reserve','Adds 15% antimatter capacity. One equipment slot; no active reactor boost or regeneration bonus.', 'trader_antimatter_engine',n,'ship_components')
    m['required_unit_tags']=['capital_ship','super_capital_ship'];m['unit_modifiers']=[{'modifier_type':'max_antimatter','value_behavior':'scalar','values':[.15]}];patches['mcrn']['ship_components'].append(it)
    # UNN civilian: developed-colony module is local and always paid; exact +10% rate = -1/11 time.
    n,d=research('unn','lunar_procurement','Lunar Procurement Offices','Unlocks a paid developed-colony procurement office. While fitted it increases local factory production rate by 10% (build time divided by 1.10).', 'trader_unlock_industrial_complex_unit_item')
    it=n+'_module';m=item(it,'Lunar Procurement Office','Paid local shipyard infrastructure: +10% factory production rate while fitted, equivalent to 9.09% shorter build time. Requires planet level 5.', 'trader_industrial_complex',n,'planet_components')
    m['other_item_requirements']['mutually_exclusive_items'] += ['trader_commercial_district','trader_high_density_district'];symmetric_exclusion('trader_industrial_complex',it);m['ability']=it;passive(it,'planet_modifiers','factory_unit_build_time',-1/11);patches['unn']['planet_components'].append(it)
    lunar_module=it; lunar_gate=n
    n,d=research('unn','emergency_appropriations','Emergency Appropriations','Unlocks a paid local mobilization office. Manual activation costs 300 credits, 100 metal and 50 crystal for +20% local shipbuilding rate for 30 seconds; 180-second cooldown. Incompatible with passive Lunar Procurement on the same planet.', 'trader_trade_port_income_rate_0',[lunar_gate])
    it=n+'_module';m=item(it,'Emergency Mobilization Office','Manual mobilization: pay 300 credits / 100 metal / 50 crystal for +20% factory production rate for 30 seconds. 180-second cooldown; requires developed planet level 5. Incompatible with passive Lunar Procurement.', 'trader_industrial_complex',n,'planet_components')
    m['other_item_requirements']['mutually_exclusive_items'] += [lunar_module,'trader_commercial_district','trader_high_density_district']
    edits[f'entities/{lunar_module}.unit_item']['other_item_requirements']['mutually_exclusive_items'].append(it)
    symmetric_exclusion('trader_industrial_complex',it);m['ability']=it;patches['unn']['planet_components'].append(it)
    put(it,'action_data_source',{'version':0,'action_values':[{'action_value_id':key,'action_value':{'values':[value]}} for key,value in [('credits',300),('metal',100),('crystal',50),('duration',30),('cooldown',180),('time_bonus',-1/6)]]})
    put(it,'buff',{'version':0,'active_duration':'duration','stacking_limit':{'stacking_limit':'fixed_one','stacking_limit_met_behavior':'preserve_existing_buff'},'stacking_ownership_type':'for_all_players','restart_other_stacked_buffs_when_started':False,'make_dead_on_current_spawner_ownership_changed_from_buff_ownership':True,'planet_modifiers':[{'modifier_type':'factory_unit_build_time','value_behavior':'scalar','value_id':'time_bonus'}]})
    put(it,'ability',{'version':0,'action_data_source':it,'level_source':'fixed_level_0','active_actions':{'cooldown_time':'cooldown','credits_cost':'credits','metal_cost':'metal','crystal_cost':'crystal','actions':{'actions':[{'action_type':'use_unit_operators_on_single_unit','destination_unit':{'unit_type':'current_spawner'},'operators':[{'operator_type':'apply_buff','buff':it}]}]}},'gui':{'name':it+'.name','description':it+'.description','hud_icon':m['hud_icon']}})
    n,d=research('unn','shipping_requisition','Civilian Shipping Requisition','Increases ordinary trade credit, metal and crystal income by 5%. Preserves existing trade shipping; grants no combat escorts or free ships.', 'trader_trade_port_income_rate_0',['trader_unlock_trade_port'])
    d['empire_modifiers']=[{'modifier_type':f'trade_{r}_income_rate','value_behavior':'scalar','value':.05} for r in ['credits','metal','crystal']]
    n,d=research('unn','black_budget','Black-Budget Procurement','Authorizes paid Amun-Ra construction. Normal 4,000 credits / 750 metal / 500 crystal, 90-second build time and 70 supply remain; maximum six owned hulls. Grants no free ship.', 'trader_unlock_heavy_gauss_slugs_unit_item')
    # Template costs/tier retained but no unrelated railgun prerequisite or reward.
    n,d=research('unn','fleet_train','Fleet Train Organization','Unlocks a paid targeted repair component for capitals and command ships. 200 hull maximum over 20 seconds within 2,000 range; same-effect repair cannot stack with Scirocco teams. No reload reset.', 'trader_unlock_robotics_cruiser',['trader_unlock_retrofit_bay_repair_ability'])
    it=n+'_module';m=item(it,'Fleet Train Repair Equipment','Repairs one nearby owned ship for 10 hull/second for 20 seconds (200 maximum). Range 2,000; costs 50 antimatter; cooldown 60 seconds. Shares Scirocco repair stacking exclusion.', 'trader_antimatter_engine',n,'ship_components');m['required_unit_tags']=['capital_ship','super_capital_ship'];m['ability']=it;patches['unn']['ship_components'].append(it)
    ability=read('expanse15_scirocco_engineering_teams','ability');ability['action_data_source']=it;ability['gui']={'name':it+'.name','description':it+'.description','hud_icon':m['hud_icon']}
    ads=read('expanse15_scirocco_engineering_teams','action_data_source')
    for row in ads['action_values']:
        if row['action_value_id']=='range':row['action_value']['values']=[2000.0]
        if row['action_value_id']=='repair_per_tick':row['action_value']['values']=[10.0]
    for row in ads['target_filters']:row['target_filter']['ownerships']=['self']
    put(it,'ability',ability);put(it,'action_data_source',ads)
    # OPA civilian: narrow infrastructure economy; no global structure discount.
    n,d=research('opa','recovery_cooperatives','Volatile Recovery Cooperatives','Adds 15% metal and crystal income from orbital extractors. Does not multiply mining-track income, market transactions or salvage rewards.', 'trader_orbital_extraction_crystal_rate_0',['trader_unlock_resource_extractor_structures'])
    d['planet_modifiers']=[{'modifier_type':f'orbital_extraction_{r}_income_rate','value_behavior':'scalar','value':.15} for r in ['metal','crystal']]
    n,d=research('opa','spin_habitat','Spin-Habitat Construction','Reduces logistics-track development time by 10% on asteroid and ice-asteroid colonies. Does not discount ships, rail batteries or other orbital structures.', 'trader_planet_track_upgrade_rate')
    d['planet_modifiers']=[{'modifier_type':'logistics_track_build_time','value_behavior':'scalar','value':-.1,'planet_types':['asteroid','ice_asteroid']}]
    n,d=research('opa','override_codes','Override-Code Libraries','Increases the existing Amun/Europa guarded boarding range by 5% (6,000 to 6,300). Requires ownership of a compatible hull; no capture-probability, health-threshold or protection change.', 'trader_upgrade_experience_gain_0')
    # Main applies this recipe to the Stage 1 shared ability; private ADS retains all lock guards.
    ads=read('expanse06_amun_boarding','action_data_source');ads['level_count']=2
    for row in ads['action_values']:
        a=row['action_value'];a['values']=[a['values'][0],a['values'][0]*1.05 if row['action_value_id']=='boarding_crew_range_value' else a['values'][0]]
    put(n+'_boarding','action_data_source',ads)
    report['shared_definition_merges'].append({'file':'entities/expanse06_amun_boarding.ability','set_fields':{
        'action_data_source':n+'_boarding','level_source':'research_prerequisites_per_level','level_prerequisites':[[],[[n]]]}})
    n,d=research('opa','surplus','Diverted Martian Surplus','Authorizes one paid Pella command capital per player. Full ordinary/exotic prices, construction time and 200 supply remain. Does not unlock the MCRN production tree.', 'trader_unlock_heavy_gauss_slugs_unit_item')
    # Facilities/contested salvage are delivered in later stages, not sold as dead unlocks here.
    report['deferred']=[{'faction':'mcrn','name':'Naval Readiness Program','stage':3,'reason':'Requires an operational local naval anchorage.'},
      {'faction':'unn','name':'Orbital Defense Command','stage':3,'reason':'Requires the actual heavy orbital battery.'},
      {'faction':'opa','name':'Dockworker Damage Control','stage':3,'reason':'Requires bounded local tender/engineering equipment; no free Artemis aura or empire heal.'},
      {'faction':'opa','name':'Salvage Arbitration','stage':4,'reason':'Requires reward-specific ordinary material adjustment excluding rare samples/scuttle rewards.'}]
    report['acquisition_gates']={'expanse_amun_ra':'expanse21_unn_black_budget','expanse12_pella':'expanse21_opa_surplus'}
    report['stage1_dependency']='Call changes() against the integrated Stage 1 package, so private boarding/repair ADS inherit its new target lock and autocast filters.'
    report['research_owner_scoping']='Only add each faction research list to that owner player; effects use native per-player research state. Captured foreign hulls gain no production access.'
    report['origins'] = {}  # Every authored definition validates without installed-extension exemptions.
    return edits,strings,{'research':{k:v['research_subjects'] for k,v in patches.items()},'items':{k:v['ship_components'] for k,v in patches.items()},'planet_items':{k:v['planet_components'] for k,v in patches.items()}},report
