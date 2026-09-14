"""Independent0.27 acquisition, research, armament and log-regression checks."""
import copy,json
from pathlib import Path
import jsonschema
from update20_fleet import ROOT,GAME
from update21_factions import FACTIONS,WRAPPERS
from update27_access import SHIPS,STORM,STORM_RESEARCH
from update26_research import OBSOLETE_SHIPS
from validate_experiments import read,require,sha256
from build_polish import write

def run(suffix=''):
    old=ROOT/'build/experiments'/('expanse_update26'+suffix);new=ROOT/'build/experiments'/('expanse_update27'+suffix)
    def get(base,n,k):
        p=base/'entities'/f'{n}.{k}';return read(p if p.exists() else GAME/'entities'/p.name)
    players=[]
    for owner,faction in {**{v:k for k,v in FACTIONS.items()},**WRAPPERS}.items():
        a,b=(get(base,owner,'player') for base in (old,new));listed=set(b['research']['research_subjects']+b['research']['faction_research_subjects'])
        require(a['research']['research_domains']==b['research']['research_domains'],'Research domains/tier drift')
        civilian=[];cells={};factories=set()
        for n in b['structures']:factories.update(get(new,n,'unit').get('unit_factory',{}).get('build_kinds',[]))
        for key in ('research_subjects','faction_research_subjects'):
            left=[n for n in a['research'][key] if get(old,n,'research_subject')['domain']=='civilian']
            right=[n for n in b['research'][key] if get(new,n,'research_subject')['domain']=='civilian']
            require(left==right,'Civilian list drift '+owner);civilian+=left
        for n in listed:
            d=get(new,n,'research_subject')
            if n in civilian:require(d==get(old,n,'research_subject'),'Civilian mechanics drift '+n)
            else:
                cell=(d['field'],*d['field_coord']);require(cell not in cells,'Research cell collision '+n+' '+cells.get(cell,''));cells[cell]=n
            routes=d.get('prerequisites',[]);require(not routes or any(set(g)<=listed for g in routes),'Research inaccessible '+owner+' '+n)
        for n in b['buildable_units']:
            u=get(new,n,'unit');require(u['build']['build_kind'] in factories,'No factory '+owner+' '+n)
            routes=u['build'].get('prerequisites',[]);require(not routes or any(set(g)<=listed for g in routes),'Build research inaccessible '+owner+' '+n)
        for n,(assigned,*_) in SHIPS.items():
            allowed=bool(suffix) or assigned==faction
            require((n in b['buildable_units'])==allowed,'Faction hull leak/missing '+owner+' '+n)
            require((n+'_procurement' in listed)==allowed,'Faction research leak/missing '+owner+' '+n)
        allowed=bool(suffix) or faction=='opa'
        require((STORM in b['buildable_units'])==allowed and (STORM_RESEARCH in listed)==allowed,'Storm ownership '+owner)
        caps={x['tag']:x['unit_limit'] for x in b['unit_limits']['global']};require(caps['titan']==1 and caps[STORM]==1,'Unique caps drift')
        acquisition=set(b['buildable_units'])|set(b['theme_picker_mesh_preview_units'])
        acquisition.update(x['unit'] for x in b['garrison']['units']['random_units']);acquisition.update(x['unit'] for x in b['trade']['trade_ship_escorts'])
        require(not acquisition&OBSOLETE_SHIPS,'Obsolete ship route')
        players.append({'owner':owner,'faction':faction,'civilian_subjects_unchanged':len(civilian),'research_cells':len(cells),'factory_kinds':sorted(factories),'ships':b['buildable_units']})
    # Primary runtime assertions: validate full required-key schema, GUI and
    # every static axis on exported weapon mounts, not only the reported Scirocco.
    schema=read(GAME.parent/'Sins of a Solar Empire II - Mod Tools/json_schemas/scenario-uniforms-schema.json')
    scenario=read(new/'uniforms/scenario.uniforms');jsonschema.Draft202012Validator(schema).validate(scenario)
    ability=get(new,'expanse11_no_shields','ability');before=get(old,'expanse11_no_shields','ability');ability.pop('gui');before.pop('gui',None);require(ability==before,'Shieldless helper mechanics changed')
    require((GAME/'textures/unit_analysis_defense_icon.png').is_file(),'Missing helper HUD icon')
    arc_count=0
    for p in (new/'entities').glob('expanse*.unit'):
        u=read(p)
        for level in u.get('health',{}).get('levels',[]):require(level.get('max_shield_points',0)==0,'Unexpected shield pool')
        for m in u.get('weapons',{}).get('weapons',[]):
            w=get(new,m['weapon'],'weapon')
            for axis in ('pitch','yaw'):
                if axis+'_arc' in m and w.get(axis+'_speed',0)<=0:
                    arc=m[axis+'_arc'];require(arc['max_angle']>arc['min_angle'],'Zero fixed arc '+p.name);arc_count+=1
    command=get(new,'expanse21_opa_command','unit');require(command['abilities'][0]['abilities'][0]==command['colonize_ability'],'Colony outside first button')
    # New weapons keep the requested counts and inherited torpedo fuel/speeds.
    gun_rows=[]
    for n in SHIPS:
        u=get(new,n,'unit');weapons=[get(new,m['weapon'],'weapon') for m in u['weapons']['weapons']]
        pdc=[w for m,w in zip(u['weapons']['weapons'],weapons) if 'pdc' in m['weapon']]
        if n.endswith('hephaestus'):require(len(pdc)==10,'Hephaestus PDC count')
        if n.endswith('laconia_frigate'):require(len(pdc)==6,'Frigate PDC count')
        gun_rows.append({'unit':n,'weapon_count':len(weapons),'pdc_count':len(pdc),'pdc_dps':[w['damage']/w['cooldown_duration'] for w in pdc]})
    for p in (new/'entities').glob('expanse27*magazine.action_data_source'):
        vals={x['action_value_id']:x['action_value']['values'][0] for x in read(p)['action_values']}
        buff=get(new,p.stem,'buff');actions=buff['time_actions'][0]['action_group']['actions']
        count=sum(any(o.get('operator_type')=='create_torpedo' for o in a.get('position_operators',[])) for a in actions)
        require(count==vals['magazine_pair_count_value'],'Salvo action/count mismatch '+p.name)
        require(vals['magazine_capacity_value']%count==0,'Partial magazine '+p.name)
        require(vals['heavy_torpedo_torpedo_lifetime_value']==30,'Fuel drift '+p.name)
        if p.stem=='expanse27_dark_star_magazine':
            donor=get(old,'expanse06_amun_magazine','action_data_source')
            expected=next(a['action_value']['values'][0] for a in donor['action_values'] if a['action_value_id']=='heavy_torpedo_torpedo_speed_value')
            require(vals['heavy_torpedo_torpedo_speed_value']==expected,'Amun torpedo speed drift '+p.name)
        else:require(vals['heavy_torpedo_torpedo_speed_value'] in (1275,2125),'Torpedo speed drift '+p.name)
    # All accepted normal weapon mechanics remain exact. Only the Storm's
    # scaled decorative turret geometry may change in old weapon definitions.
    for p in (old/'entities').glob('*.weapon'):
        a,b=read(p),read(new/'entities'/p.name)
        if p.stem.startswith(STORM+'_pdc_'):
            a.pop('turret',None);b.pop('turret',None)
        require(a==b,'Existing weapon mechanics drift '+p.name)
    text=read(new/'localized_text/en.localized_text')
    for n in SHIPS:
        u=get(new,n,'unit');skin=get(new,n,'unit_skin')
        for st in skin['skin_stages']:
            for k in ('name','description'):require(st['gui'][k] in text,'Missing ship localization '+n+' '+k)
        for m in u['weapons']['weapons']:require(get(new,m['weapon'],'weapon')['name'] in text,'Missing weapon localization')
    for n in ('expanse24_behemoth','expanse21_opa_command'):
        a,b=(get(base,n,'unit') for base in (old,new))
        for k in ('health','physics','hyperspace','build'):require(a[k]==b[k],'Unrequested existing hull balance '+n+' '+k)
    require(not (new/'entities/expanse18_prototech_composite.exotic').exists(),'Probe resource leaked')
    result={'status':'PASS OFFLINE','players':players,'weapons':gun_rows,'positive_static_arcs_checked':arc_count,'scenario_full_schema':'PASS','runtime':'NOT RUN','unresolved_runtime_error':'Unattributed inplace_vector assertion requires a new log after this candidate.'}
    write(ROOT/'audit'/('update27'+suffix)/'acceptance-check.json',result);return result

if __name__=='__main__':
    for suffix in ('','_sandbox'):print(json.dumps(run(suffix),indent=2))
