#!/usr/bin/env python3
"""Small TEC/Expanse shield policy overlay. apply(out, game) never edits game."""
import copy, hashlib, json, re
from pathlib import Path

GUARD='expanse11_no_shields'
MUTATIONS=['disable_can_shields_absorb_damage','disable_can_have_shields_restored','disable_can_passively_regenerate_shields']
SHIP_TYPES={'capital_ship','super_capital_ship','titan','starbase','frigate','cruiser','corvette','strikecraft','structure'}
HIDE_ITEMS={'trader_backup_shield_generator','trader_starbase_additional_shield_generator','trader_starbase_planetary_shield_array','trader_loyalist_titan_planetary_shield_array','trader_loyalist_titan_shield_array','dlc_ancient_starbase_planet_shield'}
HIDE_RESEARCH={'trader_shields_corvette','trader_shields_frigate','trader_shields_cruiser','trader_shields_0','trader_shields_1','trader_shield_burst_restore','trader_unlock_backup_shield_generator_unit_item','trader_upgrade_backup_shield_generator_unit_item','trader_unlock_loyalist_titan_shield_array_unit_item','trader_unlock_starbase_planetary_shield_array_unit_item'}
DISABLE_ABILITIES={'trader_loyalist_titan_shield_surge','trader_support_capital_ship_energy_transfer','trader_starbase_planetary_shield_array','trader_loyalist_titan_planetary_shield_array'}
PLANET_BUFFS={'trader_starbase_planetary_shield_array_on_self','trader_loyalist_titan_planetary_shield_array_on_self','trader_starbase_planetary_shield_array_shielding_on_planet','trader_loyalist_titan_planetary_shield_array_shielding_on_planet'}

def read(p): return json.loads(Path(p).read_text(encoding='utf-8-sig'))
def sha(p): return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def tec(n): return n.startswith('trader_') or re.match(r'^dlc\d*_trader_',n) is not None
def walk(x,path=''):
    if isinstance(x,dict):
        yield path,x
        for k,v in x.items(): yield from walk(v,path+'/'+k)
    elif isinstance(x,list):
        for i,v in enumerate(x):yield from walk(v,path+'/'+str(i))
def pointers(a,b,p=''):
    if type(a)!=type(b): return [p]
    if isinstance(a,dict):
        return [q for k in sorted(a.keys()|b.keys()) for q in ([p+'/'+k] if k not in a or k not in b else pointers(a[k],b[k],p+'/'+k))]
    if isinstance(a,list):
        if len(a)!=len(b): return [p]
        return [q for i,(x,y) in enumerate(zip(a,b))for q in pointers(x,y,p+'/'+str(i))]
    return [] if a==b else [p]
def remove_direct_shield_modifiers(x):
    if isinstance(x,dict):
        for k,v in list(x.items()):
            remove_direct_shield_modifiers(v)
            if k=='unit_modifiers' and isinstance(v,list):
                x[k]=[m for m in v if 'shield' not in m.get('modifier_type','') and not ('unit_modifiers'in m and not m['unit_modifiers'])]
    elif isinstance(x,list):
        for v in x:remove_direct_shield_modifiers(v)

def apply(out, game):
    out,game=Path(out).resolve(),Path(game).resolve()
    if out==game or out.is_relative_to(game) or game.is_relative_to(out):raise ValueError('Output must be separate from installed game')
    if not (out/'entities').is_dir():raise FileNotFoundError('Explicit new candidate entities directory required: '+str(out))
    if 'mods' in out.parts or 'original' in out.parts:raise ValueError('Refusing installed mod or original-asset destination')
    if (out/'entities'/(GUARD+'.ability')).exists():raise FileExistsError('Shield policy already applied; use a fresh candidate')
    sdk=game.parent/'Sins of a Solar Empire II - Mod Tools'
    import jsonschema
    schema=lambda n:read(sdk/'json_schemas'/(n+'-schema.json'))
    mutation_file=game/'uniforms/unit_mutation.uniforms';mut=read(mutation_file)
    permission_paths={}
    for path,obj in walk(mut):
        for name in MUTATIONS:
            if name in obj.get('disabling_mutations',[]):permission_paths[name]=path
    assert set(permission_paths)==set(MUTATIONS),'Required installed shield permission mutations missing'
    # All staging remains in memory until evidence and schema checks pass.
    loaded={}; originals={}; origins={}; installed_hashes={str(mutation_file):sha(mutation_file)}
    allowed={'.unit','.unit_item','.research_subject','.ability','.buff','.action_data_source','.player'}
    names={p.name for p in(game/'entities').iterdir()if p.is_file()and tec(p.stem)and p.suffix in allowed}
    names|={p.name for p in(out/'entities').iterdir()if p.is_file()and p.suffix in allowed and (tec(p.stem)or p.stem.startswith('expanse'))}
    def load(name):
        if name not in loaded:
            p=out/'entities'/name
            if not p.exists():p=game/'entities'/name
            if not p.is_file():raise FileNotFoundError('Missing exact shield policy dependency: '+str(p))
            originals[name]=read(p);loaded[name]=copy.deepcopy(originals[name]);origins[name]={'source':str(p),'sha256':sha(p)}
            if p.is_relative_to(game):installed_hashes[str(p)]=sha(p)
        return loaded[name]
    for name in names:load(name)
    # Validate shield-only names rather than silently replacing a missing source.
    for aid in DISABLE_ABILITIES:load(aid+'.ability')
    for bid in PLANET_BUFFS:load(bid+'.buff')
    for rid in HIDE_RESEARCH:load(rid+'.research_subject')
    for iid in HIDE_ITEMS-{'trader_loyalist_titan_shield_array'}:load(iid+'.unit_item')
    affected_units=[];removed_abilities={};zeroed_values=[]
    for name,d in loaded.items():
        if name.endswith('.unit'):
            # Projectiles are included in zero-capacity handling but not ship guard registration.
            for path,obj in walk(d.get('health',{})):
                for k,v in list(obj.items()):
                    if k in {'max_shield_points','shield_point_restore_rate','shield_point_restore_scalar_after_damage_taken'} and isinstance(v,(int,float)) and not isinstance(v,bool):obj[k]=0.0
                    if k=='shield_burst_restore' and isinstance(v,dict) and 'restore_percentage'in v:v['restore_percentage']=0.0
            remove_direct_shield_modifiers(d)
            unit_type=d.get('target_filter_unit_type')
            if 'health'in d and (unit_type in SHIP_TYPES or bool(SHIP_TYPES.intersection(d.get('tags',[])))):
                groups=d.setdefault('abilities',[])
                if not groups:groups.append({'abilities':[]})
                for group in groups:
                    assert isinstance(group.get('abilities'),list),'Unrecognized ability-set shape on '+name
                    removed=[x for x in group['abilities']if x in DISABLE_ABILITIES]
                    if removed:removed_abilities.setdefault(name,[]).extend(removed)
                    group['abilities']=[x for x in group['abilities']if x not in DISABLE_ABILITIES]
                    if GUARD not in group['abilities']:group['abilities'].append(GUARD)
                affected_units.append(name)
            if 'item_builds'in d:
                rows=[]
                for row in d['item_builds']:
                    row=copy.deepcopy(row)
                    if 'build_group'in row:row['build_group']=[x for x in row['build_group']if x not in HIDE_ITEMS]
                    if row.get('build_group'):rows.append(row)
                d['item_builds']=rows
        elif name.endswith(('.unit_item','.research_subject','.buff')):
            # Embedded shield-only entries are removed; hull/armor/AM entries survive verbatim.
            remove_direct_shield_modifiers(d)
        if name.endswith('.ability') and name[:-8] in DISABLE_ABILITIES:
            d.pop('active_actions',None);d.pop('passive_actions',None)
        if name.endswith('.buff') and name[:-5] in PLANET_BUFFS:
            # Only these TEC provider buffs become inert. Never modify a global planet definition.
            for k in ['time_actions','trigger_event_actions','planet_modifiers','unit_mutations']:d.pop(k,None)
            d.pop('gui',None)
        if name.endswith('.action_data_source'):
            vals={x['action_value_id']:x['action_value']for x in d.get('action_values',[])}
            for _,obj in walk(d):
                mt=obj.get('modifier_type','')
                if 'shield'in mt and obj.get('value_id')in vals:
                    v=vals[obj['value_id']]
                    # Preserve hostile shield-suppression penalties such as radiation bomb.
                    if v.get('values') and any(x>0 for x in v['values']):
                        v['values']=[0.0]*len(v['values']);zeroed_values.append({'file':name,'value_id':obj['value_id'],'modifier':mt})
    # Do not leave persistent enable mutations on already purchased shield-only gear/research.
    for bid in ['trader_backup_shield_generator_unit_item','trader_starbase_additional_shield_generator_unit_item','trader_unlock_backup_shield_generator']:
        d=load(bid+'.buff')
        if 'unit_mutations'in d:d['unit_mutations']=[m for m in d['unit_mutations']if m!='enable_can_have_shields_burst_restored']
    # Retain any research nodes genuinely required by a surviving system, rather than erase prerequisites.
    needed=set();dependents=[]
    player_research_checks=[]
    for name,d in loaded.items():
        if Path(name).stem in HIDE_RESEARCH or Path(name).stem in HIDE_ITEMS:continue
        for path,obj in walk(d):
            for k,v in obj.items():
                if 'prerequisite'in k and isinstance(v,list):
                    refs={x for row in v for x in(row if isinstance(row,list)else[row]) if isinstance(x,str)}
                    for ref in refs&HIDE_RESEARCH:needed.add(ref);dependents.append({'file':name,'path':path+'/'+k,'retained_research':ref})
    old=None
    while old!=needed:
        old=set(needed)
        for rid in list(needed):
            for row in loaded[rid+'.research_subject'].get('prerequisites',[]):needed.update(set(row)&HIDE_RESEARCH)
    hidden=HIDE_RESEARCH-needed
    for name,d in loaded.items():
        if not name.endswith('.player')or d.get('race')!='trader':continue
        if 'ship_components'in d:d['ship_components']=[x for x in d['ship_components']if x not in HIDE_ITEMS]
        research=d.get('research',{})
        for k in ['research_subjects','faction_research_subjects']:
            if k in research:
                # Installed faction arrays can contain conditional records; recurse only string lists.
                def strip(x):
                    if isinstance(x,list):return [strip(v)for v in x if not(isinstance(v,str)and v in hidden)]
                    if isinstance(x,dict):return {k:strip(v)for k,v in x.items()}
                    return x
                research[k]=strip(research[k])
                def string_values(x):
                    if isinstance(x,str):yield x
                    elif isinstance(x,list):
                        for v in x:yield from string_values(v)
                    elif isinstance(x,dict):
                        for v in x.values():yield from string_values(v)
                assert not hidden.intersection(string_values(research[k])), 'Hidden shield research remains in '+name+'/'+k
                player_research_checks.append({'file':name,'branch':'research/'+k,'hidden_nodes_remaining':[]})
    new={
        GUARD+'.ability':{'version':0,'action_data_source':GUARD,'level_source':'fixed_level_0','passive_actions':{'persistant_buff':GUARD,'only_if_owner_unit_operational':False}},
        GUARD+'.action_data_source':{'version':0},
        GUARD+'.buff':{'version':0,'stacking_limit':{'stacking_limit':'fixed_one','stacking_limit_met_behavior':'preserve_existing_buff'},'stacking_ownership_type':'for_all_players','restart_other_stacked_buffs_when_started':False,'unit_mutations':MUTATIONS},
    }
    changed={name:d for name,d in loaded.items()if d!=originals[name]};changed.update(new)
    mapping={'.ability':'ability','.buff':'buff','.action_data_source':'action-data-source','.research_subject':'research-subject','.unit_item':'unit-item','.player':'player'}
    checks=[]
    for name,d in changed.items():
        ext=Path(name).suffix
        if ext in mapping:
            # Players may carry installed post-pin fields. Validate only actual policy branches for those.
            if ext=='.player':continue
            jsonschema.Draft202012Validator(schema(mapping[ext])).validate(d);checks.append(name)
    for name in affected_units:
        d=changed.get(name,loaded[name]);assert all(GUARD in g['abilities']for g in d['abilities'])
        assert len(d['abilities'])==max(1,len(originals[name].get('abilities',[])))
    projectile_health_checks=[]
    for name,d in loaded.items():
        if name.endswith('.unit') and d.get('target_filter_unit_type')=='torpedo':
            assert d.get('health')==originals[name].get('health'), 'Projectile health changed: '+name
            assert name not in affected_units, 'Projectile received ship shield guard: '+name
            projectile_health_checks.append(name)
    for p,h in installed_hashes.items():assert sha(p)==h,'Installed dependency changed during policy: '+p
    changes=[]
    for name,d in sorted(changed.items()):
        dest=out/'entities'/name
        if dest.is_symlink():raise ValueError('Refusing candidate symlink '+str(dest))
        dest.write_text(json.dumps(d,indent=2)+'\n')
        changes.append({'file':'entities/'+name,'source':origins.get(name,{'source':'new private verified-schema definition'}),'changed_pointers':pointers(originals[name],d)if name in originals else['/'],'output_sha256':sha(dest)})
    return {'status':'PASS offline policy construction; runtime NOT RUN','guard_ability':GUARD,'new_entity_ids':{ext:[GUARD]for ext in ['ability','buff','action_data_source']},'guarded_unit_count':len(affected_units),'guarded_units':sorted(affected_units),'changes':changes,'strict_schema_checked':checks,'player_research_branch_checks':player_research_checks,'unchanged_projectile_health':projectile_health_checks,'unit_player_schema_boundary':'Main must validate complete integrated units/players and exact installed post-pin extensions; helper preserves unrelated fields.','permission_evidence':permission_paths,'source_hashes':installed_hashes,'hidden_shop_items':sorted(HIDE_ITEMS),'hidden_research':sorted(hidden),'retained_research_for_prerequisite_closure':sorted(needed),'retained_research_dependents':dependents,'removed_ship_abilities':removed_abilities,'zeroed_positive_shield_action_values':zeroed_values,'main_manifest_requirement':'Register GUARD in ability/buff/action_data_source manifests; register any copied unit/player/items per existing builder policy.','unresolved':['Policy is definition-scoped: captured TEC/Expanse hulls remain shieldless under any owner; captured foreign hulls retain their foreign shield behavior.','Foreign allied providers may add positive shield capacity visible on UI; verified guard disables absorption/restoration but does not prove all HUD bars vanish.','Existing saved buffs/health/research may need a new game or source ability reapplication; no destructive save migration is attempted.','TEC planetary provider buffs are disabled even if caster is captured; foreign planetary shielding is unchanged, including external allied providers. Ancient planet-shield item is hidden only from TEC shops; its shared definition and non-TEC shops stay unchanged.','Hidden shield-only items already present in saved inventories may occupy a slot; removal/refund is not automatic.','Shield-only native ability removal may leave unspent level-up points; no substitute ability or automatic level respec is invented.']}
