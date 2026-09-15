#!/usr/bin/env python3
"""Pure, frozen-input Stage B proposals. No files are written by changes().

base: candidate directory OR mapping of relative filenames to already edited JSON.
frozen: the immutable 27.5 package directory. Native fallback is read only.
Return (edits, origins, report); caller owns manifests, packaging and schema validation.
"""
from __future__ import annotations
from copy import deepcopy
from pathlib import Path
from collections import defaultdict
import hashlib
import json

GAME = Path('/run/media/haker/NVME 2/SteamLibrary/steamapps/common/Sins2')
HEAVY = {
    'expanse10_donnager_rail_0', 'expanse10_donnager_rail_1',
    'expanse15_truman_rail_0', 'expanse15_truman_rail_1',
    'expanse27_nathan_hale_rail_0', 'expanse27_nathan_hale_rail_1',
    'expanse22_foehammer_battery_0',
}
RECIPIENTS = {
    'expanse_mcrn_corvette': ['expanse03_torpedo_magazine'],
    'expanse28_mcrn_morrigan': ['expanse11_morrigan_magazine'],
    'expanse12_raptor': ['expanse12_raptor_light_magazine'],
    'expanse12_scirocco': ['expanse12_scirocco_light_magazine', 'expanse12_scirocco_heavy_magazine'],
    'expanse_donnager_battleship': ['expanse10_donnager_light_magazine', 'expanse10_donnager_heavy_magazine'],
    'expanse27_hephaestus': ['expanse27_hephaestus_light_magazine', 'expanse27_hephaestus_medium_magazine'],
}
TORPEDO_IDS = {'expanse04_light_torpedo': 'expanse28_mcrn_light_torpedo',
               'expanse10_donnager_heavy_torpedo': 'expanse28_mcrn_heavy_torpedo'}

def _walk(obj):
    if isinstance(obj, dict):
        yield obj
        for v in obj.values(): yield from _walk(v)
    elif isinstance(obj, list):
        for v in obj: yield from _walk(v)


def _replace(obj, mapping):
    if isinstance(obj, dict): return {k: _replace(v, mapping) for k, v in obj.items()}
    if isinstance(obj, list): return [_replace(v, mapping) for v in obj]
    return mapping.get(obj, obj) if isinstance(obj, str) else obj


def _diff(old, new, path=''):
    if type(old) != type(new): return [path]
    if isinstance(old, dict):
        out=[]
        for k in sorted(old.keys() | new.keys()):
            p=path+'/'+k.replace('~','~0').replace('/','~1')
            out += [p] if k not in old or k not in new else _diff(old[k],new[k],p)
        return out
    if isinstance(old, list):
        if len(old)!=len(new): return [path]
        return sum((_diff(a,b,path+'/'+str(i)) for i,(a,b) in enumerate(zip(old,new))),[])
    return [path] if old != new else []


def changes(base, frozen, game=GAME, *, tachi_supply=120, heavy_tracking=True,
            donnager_cadence=False, include_torpedoes=True):
    """Derive every multiplier from frozen; repeated calls cannot compound values.

    tachi_supply=95 gives the explicit supply control. heavy_tracking=False gives
    the tracking control. donnager_cadence=True is OPTIONAL, never the default.
    """
    if tachi_supply not in (95,120): raise ValueError('Only reviewed Tachi 95/120 variants supported')
    frozen,game=Path(frozen),Path(game)
    overlay=base if isinstance(base,dict) else None
    root=Path(base) if overlay is None else frozen
    edits={};origins={};originals={}
    def source(rel):
        p=frozen/rel
        if not p.is_file():p=game/rel
        if not p.is_file():raise FileNotFoundError(f'Required frozen/native definition missing: {rel}')
        return p
    def frozen_read(rel):return json.loads(source(rel).read_text())
    def current(rel):
        if rel in edits:return deepcopy(edits[rel])
        if overlay is not None and rel in overlay:return deepcopy(overlay[rel])
        p=root/rel
        return json.loads(p.read_text()) if p.exists() else frozen_read(rel)
    def save(rel,data,source_rel=None):
        sr=source_rel or rel;p=source(sr)
        originals[rel]=frozen_read(sr)
        edits[rel]=deepcopy(data)
        origins[rel]={'source':str(p),'source_relative':sr,'sha256':hashlib.sha256(p.read_bytes()).hexdigest()}
    def ent(n,e):return f'entities/{n}.{e}'
    report={'runtime':'NOT RUN','variant':{'tachi_supply':tachi_supply,'heavy_tracking':heavy_tracking,'optional_donnager_cadence':donnager_cadence},
            'pdc_ranges':[],'railguns':[],'torpedoes':[],'magazines':[],'recipients':RECIPIENTS if include_torpedoes else {},'unresolved':[]}
    # Tag-based custom PDC scope, plus native weapons actually mounted by custom hulls.
    pdc=set(); units={}; weapon_hosts=defaultdict(set)
    for p in sorted((frozen/'entities').glob('*.weapon')):
        d=json.loads(p.read_text())
        if 'point_defense' in d.get('tags',[]):pdc.add(p.stem)
    for p in sorted((frozen/'entities').glob('*.unit')):
        if p.stem.startswith('expanse_menu'):continue
        if not (p.stem.startswith('expanse') or p.stem=='trader_light_frigate'):continue
        d=json.loads(p.read_text());units[p.stem]=d
        for w in d.get('weapons',{}).get('weapons',[]):
            name=w['weapon'];weapon_hosts[name].add(p.stem)
            wd=frozen_read(ent(name,'weapon'))
            if 'point_defense' in wd.get('tags',[]):pdc.add(name)
    for name in sorted(pdc):
        rel=ent(name,'weapon');old=frozen_read(rel);d=current(rel);d['range']=round(old['range']*1.3,6);save(rel,d)
        report['pdc_ranges'].append({'weapon':name,'before':old['range'],'after':d['range'],'hosts':sorted(weapon_hosts[name])})
    host_ranges={}
    for name,d in units.items():
        ranges={edits[ent(w['weapon'],'weapon')]['range'] for w in d.get('weapons',{}).get('weapons',[]) if w['weapon'] in pdc}
        if len(ranges)>1:raise ValueError(f'Host {name} has heterogeneous PDC range: {ranges}; explicit policy required')
        if ranges:host_ranges[name]=ranges.pop()
    for name,hosts in sorted(weapon_hosts.items()):
        rel=ent(name,'weapon');old=frozen_read(rel)
        if 'rail_gun' not in old.get('tags',[]):continue
        if name=='expanse22_foehammer_battery_0':ranges={3*host_ranges['expanse_donnager_battleship']}
        else:ranges={host_ranges[h] for h in hosts if h in host_ranges}
        if len(ranges)!=1:raise ValueError(f'Rail {name} needs private host aliases; host PDC ranges {ranges}')
        d=current(rel);d['range']=ranges.pop()
        if heavy_tracking and name in HEAVY:
            if old.get('turret',{}).get('type') not in ('gimbal','biaxial'):raise ValueError(f'Heavy rail is not a verified turret: {name}')
            for key in ('pitch_speed','yaw_speed'):d[key]=round(old[key]*.6,6)
            for key in ('pitch_firing_tolerance','yaw_firing_tolerance'):
                if key in old:d[key]=min(old[key],1.0)
        if name=='expanse22_foehammer_battery_0':d['firing']['charge_duration']=60.0
        if donnager_cadence and name.startswith('expanse10_donnager_rail_'):d['cooldown_duration']=round(old['cooldown_duration']*.8,6)
        save(rel,d)
        report['railguns'].append({'weapon':name,'hosts':sorted(hosts),'heavy_tracking':heavy_tracking and name in HEAVY,
             'mount':old.get('turret',{}).get('type'),'range_before':old['range'],'range_after':d['range'],
             'damage':d['damage'],'penetration':d.get('penetration'),'cooldown':d['cooldown_duration'],
             'charge':d.get('firing',{}).get('charge_duration',0),'acquisition_unchanged':old.get('target_acquired_duration_required_to_fire'),
             'pitch_before':old.get('pitch_speed'),'pitch_after':d.get('pitch_speed'),'yaw_before':old.get('yaw_speed'),'yaw_after':d.get('yaw_speed'),
             'muzzles_per_instance':len(old.get('turret',{}).get('muzzle_positions',[])),
             'instances':sum(sum(w['weapon']==name for w in units[h].get('weapons',{}).get('weapons',[]))for h in hosts)})
    tachi='expanse_mcrn_corvette';rel=ent(tachi,'unit');old=frozen_read(rel);d=current(rel)
    d['build']['supply_cost']=tachi_supply
    d['physics']['time_to_max_linear_speed']=old['physics']['time_to_max_linear_speed']*.8
    d['physics']['max_angular_speed']=old['physics']['max_angular_speed']*1.15
    save(rel,d)
    report['tachi']={'supply_before':old['build']['supply_cost'],'supply_after':tachi_supply,
      'physics_before':old['physics'],'physics_after':d['physics'],
      'angular_ramp':'Existing 1.25-second angular ramp preserved: acceleration increases from 20 to 23 degrees/s^2.',
      'menu_aliases':'Display-unit hull stats untouched; main integrator owns any display synchronization.'}
    for p in sorted((frozen/'entities').glob('*launch_corvette.action_data_source')):
        rel='entities/'+p.name;d=current(rel);count=0
        for v in d.get('action_values',[]):
            if v['action_value_id']=='pirate_mercenary_base_available_supply_value':
                v['action_value']['values']=[float(tachi_supply)]*len(v['action_value']['values']);count+=1
        if count:save(rel,d)
    if include_torpedoes:
        morrigan_rel=ent('expanse28_mcrn_morrigan','unit')
        save(morrigan_rel,current(ent('trader_light_frigate','unit')),ent('trader_light_frigate','unit'))
        # MCRN identity and its TEC Loyalist gameplay alias only. Shared NPC/OPA/UNN
        # hull and launch chains remain untouched. Existing skin_groups deliberately
        # reference the original Morrigan skin and art.
        report['morrigan_acquisition']={}
        for player in ('expanse18_mcrn','trader_loyalist'):
            rel=ent(player,'player');old=current(rel)
            d=_replace(old,{'trader_light_frigate':'expanse28_mcrn_morrigan'})
            save(rel,d)
            report['morrigan_acquisition'][rel]=_diff(old,d)
        report['morrigan_start_modes']={}
        for path in sorted((frozen/'entities').glob('*.start_mode')):
            rel='entities/'+path.name;old=current(rel);d=deepcopy(old)
            for i,config in enumerate(d.get('faction_configurations',[])):
                if config.get('player_definition_id') in ('expanse18_mcrn','trader_loyalist'):
                    d['faction_configurations'][i]=_replace(config,{'trader_light_frigate':'expanse28_mcrn_morrigan'})
            if d!=frozen_read(rel):
                save(rel,d);report['morrigan_start_modes'][rel]=_diff(frozen_read(rel),d)
        report['morrigan_research_scope']={
          'explicit_unit_filter_consumers':[],
          'display_only_reference':'trader_unlock_trade_escorts_0.research_subject /arbitary_research_line/units_listing; original skin/name identical, retained shared display reference',
          'retained_upgrade_contract':'No exact trader_light_frigate references occur in installed or mod research unit filters/ADS/buffs/items. Autocannon and missile research use weapon tags (point_defense/missile); original tags, skin, target_filter_unit_type and ship roles are retained.',
          'foreign_spawn_exception':'Native eivonns_light_ships creates the original hull; deliberately unchanged foreign ability.'}
        for old_id,new_id in TORPEDO_IDS.items():
            old_rel=ent(old_id,'unit');d=frozen_read(old_rel);before=d['physics']['max_linear_speed']
            d['physics']['max_linear_speed']=round(before*1.2,6);save(ent(new_id,'unit'),d,old_rel)
            report['torpedoes'].append({'source':old_id,'private':new_id,'speed_before':before,'speed_after':d['physics']['max_linear_speed'],'changed_pointer':'/physics/max_linear_speed'})
        for host,abilities in RECIPIENTS.items():
            rel=ent(host,'unit');unit=current(rel)
            for old_id in abilities:
                new_id='expanse28_mcrn_'+old_id.removeprefix('expanse')
                mapping={old_id:new_id,**TORPEDO_IDS}
                for ext in ('ability','buff','action_data_source'):
                    old_rel=ent(old_id,ext);d=_replace(frozen_read(old_rel),mapping)
                    if ext=='action_data_source':
                        for v in d.get('action_values',[]):
                            if v['action_value_id']=='heavy_torpedo_torpedo_speed_value':
                                v['action_value']['values']=[round(x*1.2,6)for x in v['action_value']['values']]
                    if ext=='action_data_source':
                        values={v['action_value_id']:v['action_value'].get('values') for v in d.get('action_values',[])}
                        report['magazines'].append({'host':host,'private':new_id,'fuel':values.get('heavy_torpedo_torpedo_lifetime_value'),
                          'speed':values.get('heavy_torpedo_torpedo_speed_value'),'capacity':values.get('magazine_capacity_value'),
                          'rounds_per_interval':values.get('magazine_pair_count_value'),'interval':values.get('magazine_pair_interval_value'),
                          'empty_reload':values.get('magazine_reload_duration_value')})
                    save(ent(new_id,ext),d,old_rel)
                found=0
                for group in unit.get('abilities',[]):
                    group['abilities']=[new_id if a==old_id else a for a in group['abilities']]
                    found+=new_id in group['abilities']
                if found!=1:raise ValueError(f'Expected one magazine {old_id} on {host}; got {found}')
            save(rel,unit,ent('trader_light_frigate','unit') if host=='expanse28_mcrn_morrigan' else None)
    report['unresolved']=[
      'Acquisition field has no verified continuous-lock or reset semantics in pinned schema; unchanged, not raised to 2.5.',
      'Native firing.charge_duration exists and stock Vasari projectile weapons use it with cooldown. 60-second orbital charge versus 30-second reload is configured; actual combined cycle, interruption and target-switch behavior require runtime timing.',
      'Fixed/spinal rail host turn rates remain unchanged; damage application is not proof of a dodge mechanic.',
      'Muzzle arrays route effects; no offline claim that extra muzzle entries multiply damage applications.',
      'MCRN player and trader_loyalist alias build/garrison/escort/preview references use a private Morrigan. Shared original trader_light_frigate and contract patrol preserve original torpedoes for foreign/NPC users.',
      'Capturing an upgraded MCRN hull retains fitted private torpedoes; this is equipment scope, not a faction-wide owner modifier.',
      'OPA Pella launches the same standard expanse_mcrn_corvette: these Tachi hulls retain hardware-origin private premium torpedoes and 120 supply; Pella own magazine remains baseline.',
      'Private projectile max speed increases 20 percent with unchanged acceleration ramp, steering, health and 30-second lifetime; practical pursuit distance also increases.',
      'Menu-only display hull stats remain frozen. All PDC range changes intentionally include shared custom OPA/UNN PDC weapons under the latest ALL PDC override.',
      'Runtime tests NOT RUN: close orbit dodge, still-target hit, interception under attack order, first volley, magazine counts/fuel, new-save/save-reload.'
    ]
    report['changed_pointers']={rel:_diff(originals[rel],d)for rel,d in sorted(edits.items())}
    report['protected_file_changes']=sorted(rel for rel in edits if (frozen/rel).is_file())
    report['new_files']=sorted(rel for rel in edits if not (frozen/rel).is_file())
    report['native_charge_evidence']='entities/vasari_heavy_cruiser_medium_wave_cannon.weapon: firing.charge_duration=1, cooldown_duration=4, firing_type=projectile'
    report['schema_evidence']='Pinned weapon-schema.json supports firing.charge_duration, pitch_speed, yaw_speed, pitch_firing_tolerance, yaw_firing_tolerance; acquisition field numeric only.'
    # No weapon damage or projectile health/capacity mutation is allowed by this helper.
    for rel,d in edits.items():
        old=originals[rel]
        if rel.endswith('.weapon'):
            for key in ('damage','penetration','damage_affect_type','effects','turret'):
                assert d.get(key)==old.get(key),(rel,key)
        if rel in (ent(n,'unit')for n in TORPEDO_IDS.values()):
            assert _diff(old,d)==['/physics/max_linear_speed'],rel
    return edits,origins,report
