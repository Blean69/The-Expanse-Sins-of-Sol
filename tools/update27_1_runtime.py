"""Runtime constraints discovered from the 0.27 crash log; no balance changes."""
import copy,json
from pathlib import Path
from common import ROOT,GAME,read,read_mesh,write
from validate_experiments import require,sha256
IDENTITY_TAGS={'expanse27_nathan_hale','expanse27_munroe','expanse27_hephaestus','expanse27_laconia_frigate','expanse27_dark_star'}
UNIT_TAG_LIMIT=30 # engine 2.0.3 (318): expected_size=30 actual_size=35

def get(base,rel):
    p=base/rel;return read(p if p.exists() else GAME/rel)

def tag_consumers(base,names):
    found=[]
    def walk(v,path):
        if isinstance(v,dict):
            for k,x in v.items():yield from walk(x,path+'/'+k)
        elif isinstance(v,list):
            for i,x in enumerate(v):yield from walk(x,path+'/'+str(i))
        elif isinstance(v,str) and v in names and 'tag' in path:yield path,v
    for folder in ['entities','uniforms']:
        for p in (base/folder).iterdir():
            try:d=read(p)
            except (UnicodeDecodeError,json.JSONDecodeError):continue
            for path,value in walk(d,''):
                if p.suffix=='.unit' and path.startswith('/tags/'):continue
                if p.name=='unit_tag.uniforms' and path.startswith('/unit_tags/'):continue
                found.append({'file':str(p.relative_to(base)),'path':path,'value':value})
    return found

def changes(base):
    base=Path(base);edits={};origins={}
    require(not tag_consumers(base,IDENTITY_TAGS),'New identity tag actually controls a mechanic')
    rel='uniforms/unit_tag.uniforms';d=get(base,rel);d['unit_tags']=[t for t in d['unit_tags'] if t['name'] not in IDENTITY_TAGS];require(len(d['unit_tags'])<=UNIT_TAG_LIMIT,'Unit tag registry remains oversized');edits[rel]=d
    for n in sorted(IDENTITY_TAGS):
        rel='entities/'+n+'.unit';d=get(base,rel);d['tags']=[t for t in d['tags'] if t not in IDENTITY_TAGS];require(d['tags'],'Lost ship classification');edits[rel]=d
    # Copy the installed, already-used effect/sound pair. No experience or hull
    # progression changes and no invented hidden-ability flags.
    donor=get(base,'entities/expanse15_truman.unit_skin')['skin_stages'][0]['effects']
    repaired=[]
    for p in (base/'entities').glob('*.unit'):
        u=read(p)
        if u.get('levels',{}).get('type')!='experience':continue
        for group in u.get('skin_groups',[]):
            for n in group['skins']:
                rel='entities/'+n+'.unit_skin';skin=copy.deepcopy(edits.get(rel,get(base,rel)));changed=False
                for stage in skin['skin_stages']:
                    effects=stage.setdefault('effects',{})
                    for key in ['level_up_effect','level_up_sound']:
                        if not effects.get(key):effects[key]=donor[key];changed=True
                if changed:edits[rel]=skin;repaired.append(n)
    return edits,origins,{'unit_tag_count_before':len(get(base,'uniforms/unit_tag.uniforms')['unit_tags']),'unit_tag_count_after':len(edits['uniforms/unit_tag.uniforms']['unit_tags']),'removed_unused_identity_tags':sorted(IDENTITY_TAGS),'level_up_skins_repaired':repaired,'equipment':'Existing required_unit_tags filters preserved; no starbase/capital tags removed.','runtime':'NOT RUN'}

def audit_sockets(base):
    rows=[];seen=set()
    for p in (base/'entities').glob('*.unit'):
        u=read(p)
        for group in u.get('skin_groups',[]):
            for sn in group['skins']:
                for st in get(base,'entities/'+sn+'.unit_skin')['skin_stages']:
                    aliases={a['mesh_alias_name']:a['mesh_definition']['mesh'] for a in st.get('child_mesh_alias_bindings',{}).get('map',[])}
                    for mount in u.get('weapons',{}).get('weapons',[]):
                        w=get(base,'entities/'+mount['weapon']+'.weapon');turret=w.get('turret',{})
                        if turret.get('type')!='biaxial':continue
                        bn=aliases.get(turret['biaxial_base_mesh'],turret['biaxial_base_mesh']);an=aliases.get(turret['biaxial_barrel_mesh'],turret['biaxial_barrel_mesh']);key=(bn,an)
                        if key in seen:continue
                        seen.add(key);points=[]
                        for n in key:
                            f=base/'meshes'/(n+'.mesh');f=f if f.exists() else GAME/'meshes'/f.name;points.append(read_mesh(f)['meshpoints'])
                        require(any(x['name'].startswith('child.') for x in points[0]),'No turret barrel socket '+bn)
                        require(any(x['name'].startswith('turret_muzzle.') for x in points[1]),'No turret muzzle socket '+an)
                        rows.append({'base':bn,'barrel':an,'status':'PASS native socket types'})
    return rows

def check(base,old):
    from update21_factions import FACTIONS,WRAPPERS
    tags=get(base,'uniforms/unit_tag.uniforms');names=[t['name'] for t in tags['unit_tags']];native=get(GAME,'uniforms/unit_tag.uniforms')['unit_tags'];require(tags['overwrite_unit_tags'] is True,'Unverified unit tag merge');require(len(names)<=UNIT_TAG_LIMIT and len(names)==len(set(names)),'Unit tag overflow / duplicate');require(tags['unit_tags'][:len(native)]==native,'Native unit tags/order lost')
    for p in (base/'entities').glob('*.unit'):
        u=read(p);require(set(u.get('tags',[]))<=set(names),'Unknown unit tag '+p.name)
        if u.get('levels',{}).get('type')=='experience':
            for group in u['skin_groups']:
                for sn in group['skins']:
                    for st in get(base,'entities/'+sn+'.unit_skin')['skin_stages']:
                        require(all(st.get('effects',{}).get(k) for k in ['level_up_effect','level_up_sound']),'Missing experience effects '+sn)
    # Test actual player inventories against every mobile, item-capable hull.
    # Native required_unit_tags is an any-of selector (capital OR titan etc.).
    equipment=[]
    for owner in {**{v:k for k,v in FACTIONS.items()},**WRAPPERS}:
        player=get(base,'entities/'+owner+'.player');require(player==get(old,'entities/'+owner+'.player'),'Faction/research list changed')
        items={n:get(base,'entities/'+n+'.unit_item') for n in player['ship_components']};station_only={n:d for n,d in items.items() if d.get('required_unit_tags') and set(d['required_unit_tags'])<= {'starbase','dlc_ancient_starbase','expanse22_major_support_station','expanse22_mcrn_support_station','expanse22_unn_support_station','expanse22_opa_support_station'}}
        for item,d in items.items():require(set(d.get('required_unit_tags',[]))<=set(names),'Unresolved item tag '+item)
        mobile=[];positive=[]
        for n in player['buildable_units']+player['structures']:
            u=get(base,'entities/'+n+'.unit');ut=set(u.get('tags',[]));eligible={item for item,d in items.items() if not d.get('required_unit_tags') or ut&set(d['required_unit_tags'])}
            if u.get('physics',{}).get('can_move_linear') and u.get('items'):
                require(not (eligible&station_only.keys()),'Station item allowed on '+n);mobile.append(n)
                if 'capital_ship' in ut:require('trader_heavy_armor' in eligible,'Capital equipment lost '+n)
            if 'starbase' in ut:
                require('trader_starbase_docking_booms' in eligible,'Native station equipment lost '+n);positive.append(n)
        require(positive,'No positive station control '+owner)
        equipment.append({'player':owner,'station_only_items_rejected':sorted(station_only),'mobile_hulls_checked':mobile,'starbase_positive_controls':positive})
    # Every existing cost, health, movement, gun/torpedo/ability program remains.
    for p in (old/'entities').iterdir():
        if p.suffix in ['.weapon','.ability','.buff','.action_data_source','.unit_item','.research_subject']:
            require((base/'entities'/p.name).read_bytes()==p.read_bytes(),'Unrequested gameplay mutation '+p.name)
        if p.suffix=='.unit':
            a,b=read(p),get(base,'entities/'+p.name);a.pop('tags',None);b.pop('tags',None);require(a==b,'Unrequested hull change '+p.name)
    return {'status':'PASS OFFLINE','unit_tag_count':len(names),'unit_tag_capacity':UNIT_TAG_LIMIT,'native_tags_preserved':len(native),'equipment_matrix':equipment,'turret_sockets':audit_sockets(base),'baseline_gameplay_preserved':True,'runtime':'NOT RUN','crash_status':'Tag overflow and missing sockets repaired. No post-fix runtime reproduction; secondary index/formation assertions remain unconfirmed.'}
