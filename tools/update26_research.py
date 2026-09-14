"""Conservative roster cleanup and compact military-only research layout.
Civilian definitions/domain/list ordering are invariant. Installed entities remain
on disk for old saves and native NPCs, but obsolete player production is removed.
"""
import copy,json,collections
from pathlib import Path
from update20_fleet import GAME
from update21_factions import FACTIONS,WRAPPERS
from validate_experiments import read,require

OBSOLETE_SHIPS={
 'trader_skirmisher_corvette_frigate','trader_missile_corvette','trader_siege_frigate',
 'trader_carrier_cruiser','trader_antifighter_frigate','trader_antiarmor_frigate',
 'trader_robotics_cruiser','trader_long_range_cruiser','trader_heavy_cruiser','trader_torpedo_cruiser',
 'trader_battle_capital_ship','trader_carrier_capital_ship','trader_colony_capital_ship',
 'trader_planet_destroyer_capital_ship','trader_support_capital_ship','trader_loyalist_titan','trader_rebel_titan',
 'dlc2_trader_loyalist_super_capital_ship','dlc2_trader_rebel_super_capital_ship'}
# Native starbases/infrastructure remain supported. Native Titan-specific equipment
# has no matching access tag on our ships; it must not occupy research/menu space.
OBSOLETE_ITEM_PREFIXES=('trader_loyalist_titan_','trader_rebel_titan_','dlc2_trader_loyalist_super_capital_ship_','dlc2_trader_rebel_super_capital_ship_')
GRAPH_KINDS=('unit','weapon','ability','buff','action_data_source','unit_item')
SKIP_KEYS={'gui','user_interface','skin_groups','sounds','sound','effects','item_builds','player_ai','ai','ai_attack_target'}

def strings(obj):
 if isinstance(obj,str):yield obj
 elif isinstance(obj,list):
  for v in obj:yield from strings(v)
 elif isinstance(obj,dict):
  for k,v in obj.items():
   if k not in SKIP_KEYS:yield from strings(v)

def changes(base,sandbox=False):
 base=Path(base);edits={};loc={};cache={};report={'players':{},'mapping':{},'civilian':'unchanged','runtime':'NOT RUN'}
 def get(n,kind):
  rel=f'entities/{n}.{kind}'
  if rel in edits:return edits[rel]
  if rel not in cache:cache[rel]=read(base/rel if (base/rel).exists() else GAME/rel)
  return cache[rel]
 all_research={p.stem for root in (GAME,base) for p in (root/'entities').glob('*.research_subject')}
 entity_index=collections.defaultdict(list)
 for root in (GAME,base):
  for kind in GRAPH_KINDS:
   for p in (root/'entities').glob('*.'+kind):
    if kind not in entity_index[p.stem]:entity_index[p.stem].append(kind)
 def graph(seeds):
  seen=set();refs=set();todo=list(seeds)
  while todo:
   n,k=todo.pop()
   if (n,k) in seen:continue
   seen.add((n,k));d=get(n,k)
   for value in strings(d):
    if value in all_research:refs.add(value)
    for kind in entity_index.get(value,[]):
     if (value,kind) not in seen:todo.append((value,kind))
  return seen,refs
 owners={**{v:k for k,v in FACTIONS.items()},**WRAPPERS};plans={}
 for owner,faction in owners.items():
  p=copy.deepcopy(get(owner,'player'));old=copy.deepcopy(p)
  p['buildable_units']=[n for n in p['buildable_units'] if n not in OBSOLETE_SHIPS]
  # Actual themed Sunflare/scout and civilian colony transport use native IDs.
  patrol='trader_light_frigate' if faction=='mcrn' else 'expanse21_contract_patrol'
  heavy={'mcrn':'expanse_mcrn_corvette','unn':'expanse23_murphy','opa':'expanse19_europa_bane'}[faction]
  p['garrison']['units']['random_units']=[{'unit':patrol,'weight':70.0},{'unit':heavy,'weight':30.0}]
  for escort in p['trade']['trade_ship_escorts']:
   if escort['unit'] in OBSOLETE_SHIPS:escort['unit']=heavy
  p['ship_components']=[n for n in p['ship_components'] if not n.startswith(OBSOLETE_ITEM_PREFIXES) and n!='expanse21_opa_command_colony_module']
  # UI preview roster also must not advertise removed capital hulls.
  p['theme_picker_mesh_preview_units']=[n for n in p.get('theme_picker_mesh_preview_units',[]) if n not in OBSOLETE_SHIPS]
  p['theme_picker_mesh_preview_units']+= [n for n in p['buildable_units'] if n.startswith('expanse') and n not in p['theme_picker_mesh_preview_units']][:4]
  seeds=[(n,'unit') for n in p['buildable_units']+p['structures']+p.get('ability_created_units',[])]+[(n,'unit_item') for n in p['ship_components']+p['planet_components']]
  reachable,refs=graph(seeds)
  # Preserve owner research affecting native engine systems such as supply,
  # garrison, scouting and structure modifiers, as well as tangible equipment.
  refs.update(v for v in strings({k:value for k,value in p.items() if k!='research'}) if v in all_research)
  listed=p['research']['research_subjects']+p['research'].get('faction_research_subjects',[])
  keep=set()
  for n in listed:
   d=get(n,'research_subject')
   if d['domain']!='military' or n.startswith('expanse') or n in refs or any(k.endswith('_modifiers') or k in {'buff_providers','bonus_unit_limits','windfall'} for k in d):keep.add(n)
   if n.startswith(('trader_max_supply_','trader_capital_ship_starting_level_','trader_garrison_max_supply','trader_loyalist_garrison_max_supply','trader_defense_structure_culture_resistance','trader_structure_hull','trader_twin_fortresses','trader_upgrade_consumables_')):keep.add(n)
  # References from unchanged civilian research are mandatory even when they
  # cross into a military prerequisite. Retain full prerequisite closure.
  changed=True
  while changed:
   previous=set(keep)
   for n in list(keep):
    for v in strings(get(n,'research_subject').get('prerequisites',[])):
     if v in listed:keep.add(v)
   changed=keep!=previous
  for key in ('research_subjects','faction_research_subjects'):
   if key in p['research']:p['research'][key]=[n for n in p['research'][key] if n in keep]
  require(p['research']['research_domains']['civilian']==old['research']['research_domains']['civilian'],'Civilian domain drift')
  for key in ('research_subjects','faction_research_subjects'):
   require([n for n in p['research'].get(key,[]) if get(n,'research_subject')['domain']=='civilian']==[n for n in old['research'].get(key,[]) if get(n,'research_subject')['domain']=='civilian'],'Civilian list changed')
  plans[owner]=(p,keep,reachable,refs)
  report['players'][owner]={'removed_ships':sorted(set(old['buildable_units'])-set(p['buildable_units'])),'removed_items':sorted(set(old['ship_components'])-set(p['ship_components'])),'removed_research':sorted(set(listed)-keep),'garrison':[patrol,heavy],'heavy_trade_escort':heavy,'retained_military':sorted(n for n in keep if get(n,'research_subject')['domain']=='military')}
 # Allocate shared coordinates once across the union so sandbox and faction
 # aliases see identical definitions. Tier-column and chain row order retained.
 military=sorted({n for _,keep,_,_ in plans.values() for n in keep if get(n,'research_subject')['domain']=='military'})
 rows={};occupied=collections.defaultdict(set)
 for n in sorted(military,key=lambda n:(get(n,'research_subject')['field'],get(n,'research_subject')['tier'],get(n,'research_subject')['field_coord'][1],n)):
  d=copy.deepcopy(get(n,'research_subject'));field=d['field'];tier=d['tier'];x=d['field_coord'][0]
  # Valid native columns are 2*tier or2*tier+1. Repack empty rows only.
  x=2*tier+(x%2)
  parents=[rows[v] for v in strings(d.get('prerequisites',[])) if v in rows and get(v,'research_subject')['field']==field]
  preferred=min(parents) if parents else 0
  y=preferred
  while (x,y) in occupied[field]:y+=1
  occupied[field].add((x,y));rows[n]=y;d['field_coord']=[x,y]
  # Explicit existing mod brush assets avoid contextual skin-only aliases.
  art={'expanse22_unn_orbital_defense':'expanse15_truman','expanse22_mcrn_naval_readiness':'expanse12_scirocco','expanse22_opa_dockworker_damage_control':'expanse19_europa','expanse21_unn_fleet_train':'expanse15_truman','expanse24_gathering_storm_procurement':'expanse12_raptor','expanse24_behemoth_refit':'expanse24_behemoth','expanse21_unn_black_budget':'expanse06_amun','expanse21_opa_surplus':'expanse12_pella'}
  if n in art:
   for fieldname,suffix in [('hud_icon','hud_icon'),('tooltip_picture','tooltip_picture')]:
    brush=art[n]+'_'+suffix
    require((base/'brushes'/f'{brush}.brush').exists(),'Missing concrete research brush '+brush)
    d[fieldname]=brush
   d['tooltip_icon']=d['hud_icon']
  edits[f'entities/{n}.research_subject']=d
  report['mapping'][n]={'field':field,'old_coord':cache[f'entities/{n}.research_subject']['field_coord'],'coord':[x,y], 'direct_definition_references':sorted({f'{a}.{k}' for _,_,reachable,_ in plans.values() for a,k in reachable if n in set(strings(get(a,k)))}),'modifiers':{k:v for k,v in d.items() if k.endswith('_modifiers')},'prerequisites':d.get('prerequisites',[])}
 for owner,(p,keep,_,_) in plans.items():edits[f'entities/{owner}.player']=p
 # Retained native procurement gates now describe the actual custom hull.
 labels={'trader_unlock_antiarmor_frigate':('Murphy Destroyer Construction','Authorizes the UNN Murphy light destroyer. Native cost, tier and research time are retained.'),
 'trader_unlock_loyalist_titan':('Donnager Battleship Construction','Authorizes the MCRN Donnager battleship and satisfies its late procurement prerequisites. Uses the shared titan limit.'),
 'trader_unlock_rebel_titan':('Heavy Battleship Commissioning','Alternative shipyard commissioning route for Donnager procurement in the combined sandbox. Uses the shared titan limit.')}
 for n,(name,desc) in labels.items():
  if n in military:
   d=edits[f'entities/{n}.research_subject'];loc[d['name']]=name;loc[d['name_uppercase']]=name.upper()
   d['description']=n+'_expanse26_description';loc[d['description']]=desc
   prefix='expanse15_truman' if 'antiarmor' in n else 'expanse11_donnager'
   d['hud_icon']=prefix+'_hud_icon';d['tooltip_picture']=prefix+'_tooltip_picture';d['tooltip_icon']=d['hud_icon']
 # Canonical display aliases also cover native tooltips deriving their ID.
 text=read(base/'localized_text/en.localized_text')
 for n in military:
  d=edits[f'entities/{n}.research_subject']
  if n.startswith('expanse'):
   name=text[d['name']];loc[n]=name;loc[n+'_research_subject_name']=name;loc[n+'_research_subject_name_uppercase']=name.upper()
   d['name']=n+'_research_subject_name';d['name_uppercase']=n+'_research_subject_name_uppercase'
 report['maximum_military_rows']={f:max(y for x,y in cells)+1 for f,cells in occupied.items()}
 return edits,loc,report
