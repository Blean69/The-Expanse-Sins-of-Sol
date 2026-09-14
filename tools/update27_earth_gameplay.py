"""Private Earth additions only; main owns player access, registry, research and text merge."""
from pathlib import Path
from copy import deepcopy as cp
import hashlib,json
import numpy as np
from common import read,write
from update27_earth_geometry import ROOT,BASE,AUD,GAME,IDS
from build_hero03 import ability_positions

def rename(x,a,b):
 if isinstance(x,str):return x.replace(a,b)
 if isinstance(x,list):return[rename(v,a,b)for v in x]
 if isinstance(x,dict):return{k:rename(v,a,b)for k,v in x.items()}
 return x

def changes(base=BASE):
 base=Path(base);edits={};loc={};origins={};sources={};reports={};artfiles={}
 def load(name):
  p=base/'entities'/name;sources[str(p)]=hashlib.sha256(p.read_bytes()).hexdigest();return read(p)
 def put(name,d,origin):edits['entities/'+name]=d;origins['entities/'+name]=str(base/'entities'/origin)
 for kind,ID in IDS.items():
  art=read(AUD/(kind+'-integration.json'));artfiles.update({rel:str(Path(art['game_output'])/rel)for rel in art['files']});oldid='expanse15_truman'if kind=='hale'else'expanse23_murphy';u=load(oldid+'.unit');before=cp(u);capital=kind=='hale';hull=10000 if capital else 5200;armor=3800 if capital else 2400;supply=155 if capital else 125;speed=800 if capital else 950;price={'credits':3200. if capital else 2600.,'metal':800. if capital else 750.,'crystal':500. if capital else 400.}
  u['spatial'].update(cp(art['spatial']));u['skin_groups']=[{'skins':[ID]}];typ='capital_ship'if capital else'cruiser';u['tags']=[typ,ID];u['target_filter_unit_type']=typ;u['ship_roles']=['attack_ship'];u.pop('colonize_ability',None);u['build'].update(build_time=90. if capital else 80.,price=price,supply_cost=supply,build_kind=typ,build_group_id=typ);u['build'].pop('prerequisites',None)
  # Integration chooses a priced unlock; no unverified or free local unlock here.
  if capital:u['build']['exotic_price']=[{'exotic_type':'offense','count':1},{'exotic_type':'defense','count':1}]
  u['physics'].update(max_linear_speed=float(speed),time_to_max_linear_speed=8. if capital else 6.,max_angular_speed=16. if capital else 20.,max_bank_angle=20.)
  first=before['health']['levels'][0]
  for h in u['health']['levels']:
   h['max_hull_points']*=hull/first['max_hull_points'];h['max_armor_points']*=armor/first['max_armor_points'];h['max_shield_points']=0.;h['shield_point_restore_rate']=0.
   for k in list(h):
    if k.startswith('shield_burst'):h.pop(k)
  for lv in u.get('levels',{}).get('levels',[]):lv.pop('weapon_modifiers',None)
  u['user_interface']['pip_type']=typ;u['weapons']={'weapons':[cp(r['mount'])for r in art['rigs']],'max_range_weapon_index':len(art['rigs'])-1};u['ai']['attack_target_type_groups_matching_weapon']=ID+'_rail_0';u['ai']['attack_target_type_groups_to_ignore']=[]
  for r in art['rigs']:
   is_pdc=r['kind']=='pdc';source='expanse15_truman_pdc_0'if is_pdc else'expanse15_truman_rail_0';w=load(source+'.weapon');w['name']=ID+('.pdc.name'if is_pdc else'.rail.name');w.update(pitch_firing_tolerance=1.,yaw_firing_tolerance=1.)
   if r['turret']:w['turret']=cp(r['turret'])
   else:w.pop('turret',None)
   if is_pdc:w.update(damage=21.25,cooldown_duration=.25,pitch_speed=180.,yaw_speed=180.)
   else:
    w.update(damage=2400. if capital else 1800.,cooldown_duration=60.,penetration=1100. if capital else 1000.,target_acquired_duration_required_to_fire=1.5,pitch_speed=0.,yaw_speed=20. if capital else 0.)
    u['ai']['attack_target_type_groups']=cp(w['attack_target_type_groups'])
   put(r['mount']['weapon']+'.weapon',w,source+'.weapon')
  # The accepted UNN torpedo program is derived privately: same target guards,
  # destroyable torpedo entity, damage/research, fuel and reload semantics.
  mag=ID+'_magazine';oldmag='expanse15_truman_light_magazine';salvo=4 if capital else 6;capacity=24 if capital else 36;interval=10. if capital else 12.
  for ext in['ability','buff','action_data_source']:
   d=rename(load(oldmag+'.'+ext),oldmag,mag)
   if ext=='ability':d['ability_positions']=ability_positions(art['ports'])
   if ext=='buff':
    actions=d['time_actions'][0]['action_group']['actions'];launches=[a for a in actions if a.get('action_type')=='use_position_operators_on_single_position'];assert len(launches)==6;start=next(i for i,a in enumerate(actions)if a in launches);finish=start+6;assert actions[start:finish]==launches;d['time_actions'][0]['action_group']['actions']=actions[:start]+cp(launches[:salvo])+actions[finish:]
   if ext=='action_data_source':
    replacements={'heavy_torpedo_torpedo_count_value':capacity,'magazine_capacity_value':capacity,'magazine_pair_count_value':salvo,'combat03_torpedoes_per_interval_value':salvo,'combat03_interval_count_value':capacity//salvo,'combat03_interval_value':interval,'magazine_pair_interval_value':interval}
    for a in d['action_values']:
     if a['action_value_id']in replacements:a['action_value']['values']=[replacements[a['action_value_id']]]*len(a['action_value']['values'])
   put(mag+'.'+ext,d,oldmag+'.'+ext)
  u['abilities']=[{'abilities':[mag,'expanse11_no_shields']}]
  if 'spawn_loot'in u.get('spawn_debris',{}):u['spawn_debris']['spawn_loot']['loot_name']=ID+'.loot'
  put(ID+'.unit',u,oldid+'.unit');skin=load(oldid+'.unit_skin')
  for st in skin['skin_stages']:
   st['unit_mesh']['mesh']=art['hull_mesh'];st['min_camera_distance']=art['spatial']['radius']*2;st['gui'].update(name=ID+'.name',description=ID+'.description');st['child_mesh_alias_bindings']={'map':[{'mesh_alias_name':name,'mesh_definition':{'mesh':name,'shader':'ship','is_shadow_blocker':True}}for name in art['donors']]};st['effects']['exhaust_effects']={'particle_effects':[{'particle_effect':ID+'_idle_plume'}]}
   for key in['travel_effect','travel_effect_between_stars','travel_effect_destabilized']:st['effects']['hyperspace_effects'][key]=ID+'_phase_plume'
   for k in['hud_icon','hud_monochrome_icon','hud_picture','tooltip_picture']:st['gui'][k]=ID+'_'+('main_view_icon'if k=='hud_monochrome_icon'else k)
   for k,suffix in[('icon','main_view_icon'),('selected_icon','main_view_icon_selected'),('sub_selected_icon','main_view_icon_sub_selected')]:st['main_view_icon'][k]=ID+'_'+suffix
  put(ID+'.unit_skin',skin,oldid+'.unit_skin')
  title='UNN Nathan Hale — Leonidas-class'if capital else'UNN Munroe-class cruiser';desc=('An older UNN battleship: two slow medium railgun turrets, twelve defensive batteries and a four-torpedo volley. Durable but slow; narrow rail tracking rewards flanking.'if capital else'A detailed UNN line cruiser with eight defensive batteries, a fixed forward keel railgun and six-torpedo volleys. Thick armor favors formation combat; the keel gun requires the ship to face its target.')
  loc.update({ID+'.name':title,ID+'.description':desc,ID+'.loot':('Leonidas'if capital else'Munroe')+' wreckage',ID+'.pdc.name':'UNN defensive cannon battery',ID+'.rail.name':'UNN medium railgun'if capital else'UNN keel railgun',mag+'.name':'UNN light torpedo magazine',mag+'.description':f'{salvo} UNN light torpedoes every {int(interval)} seconds while an eligible enemy is available. {capacity}-round magazine; reloads 120 seconds after the last volley. Torpedoes expire after 30 seconds.',mag+'.ammo_label':'Torpedoes remaining'})
  reports[ID]={'role':typ,'lore_class':'TV Leonidas-class battleship'if capital else'RPG Munroe-class light destroyer; cruiser is requested mod classification','stats':{'hull':hull,'armor':armor,'supply':supply,'speed':speed,'price':price,'build_time':u['build']['build_time'],'pdc_count':art['counts']['pdc_count'],'pdc_dps_each':85.,'rail_count':art['counts']['rail_count'],'rail_damage':2400 if capital else 1800,'rail_cooldown':60.,'salvo':salvo,'interval':interval,'magazine':capacity,'reload':120.},'art':str(AUD/(kind+'-integration.json')),'new_private_ids':[r['mount']['weapon']for r in art['rigs']]+[ID,mag]}
 report={'status':'PRIVATE EARTH DEFINITIONS; MAIN INTEGRATION REQUIRED','base':str(base),'art_directory':str(Path(art['game_output'])),'art_files':artfiles,'ships':reports,'unit_tag_entries_append':list(IDS.values()),'source_definitions_sha256':sources,'integration_needed':['priced research unlock and prerequisites','Earth player build availability only','unit tag registry and manifest registration','localization merge','main shared no_shields GUI visibility fix'],'preserved':['all pre-existing hull definitions and shared weapons','accepted UNN torpedo damage, hull, speed, fuel and target guards','no second capture system or special boarding ability','no free colony capability inherited from Truman'],'untested':['game load and research/build access','live PDC/rail acquisition and rig interpolation','actual plume orientation/scale and shader appearance','save/reload','multiplayer']}
 return edits,loc,origins,report

def main():
 edits,loc,origins,report=changes()
 for rel,d in edits.items():write(GAME/rel,d)
 for name,d in[('localization',loc),('origins',origins),('gameplay-contract',report)]:write(AUD/(name+'.json'),d)
 print('PRIVATE DEFS',len(edits),'ship stats',json.dumps({k:v['stats']for k,v in report['ships'].items()}))
if __name__=='__main__':main()
