"""Repairs derived from 0.27.1 log 496 and installed engine/SDK patterns."""
import copy, math
from pathlib import Path
from common import ROOT,GAME,read,write,read_mesh
from validate_experiments import require,sha256
from update27_1_runtime import get,audit_sockets
from update27_1_mesh_sockets import section,encode,IDENTITY

def gimbals(base):
    rows={}
    for p in (base/'entities').glob('*.unit'):
        u=read(p)
        for gr in u.get('skin_groups',[]):
            for sn in gr['skins']:
                for stage in get(base,'entities/'+sn+'.unit_skin')['skin_stages']:
                    aliases={a['mesh_alias_name']:a['mesh_definition']['mesh'] for a in stage.get('child_mesh_alias_bindings',{}).get('map',[])}
                    for mount in u.get('weapons',{}).get('weapons',[]):
                        turret=get(base,'entities/'+mount['weapon']+'.weapon').get('turret',{})
                        if turret.get('type')!='gimbal':continue
                        n=aliases.get(turret['gimbal_mesh'],turret['gimbal_mesh'])
                        if n in rows:require(rows[n]['muzzle_positions']==turret['muzzle_positions'],'Incompatible shared muzzle transforms '+n)
                        else:rows[n]={'muzzle_positions':turret['muzzle_positions'],'consumers':[]}
                        if p.stem not in rows[n]['consumers']:rows[n]['consumers'].append(p.stem)
    return rows

def changes(base,audit,artroot):
    edits={};art={};replacements={};levels={};report={'runtime':'NOT RUN','action_level_repairs':[],'gimbal_repairs':[]}
    for p in sorted((base/'entities').glob('*.action_data_source')):
        d=read(p);sizes={len(v['action_value']['values']) for v in d.get('action_values',[]) if 'values' in v['action_value']}
        if not sizes or sizes=={d.get('level_count',1)}:continue
        require(d.get('level_count',1)==1 and sizes in [{2},{1,2}],'Unknown action level mismatch '+p.name)
        consumers=[]
        for ap in (base/'entities').glob('*.ability'):
            a=read(ap)
            if a.get('action_data_source')==p.stem:
                require(a['level_source']=='research_prerequisites_per_level' and len(a['level_prerequisites'])==2,'Unverified source level consumer '+ap.name)
                consumers.append(ap.stem)
        require(consumers,'No two-level consumer '+p.name)
        rel='entities/'+p.name;d['level_count']=2;expanded=[]
        for v in d['action_values']:
            av=v['action_value']
            if 'values' in av and len(av['values'])==1:
                av['values']*=2;expanded.append(v['action_value_id'])
        edits[rel]=d
        if 'magazine' in rel:
            require(not expanded,'Magazine repair must be level declaration only')
            levels[rel]=sha256(p)
        report['action_level_repairs'].append({'file':rel,'consumers':consumers,'level_count':2,'constant_arrays_expanded':expanded,'existing_research_values_preserved':True})
    rel='entities/expanse24_behemoth.unit';d=get(base,rel);require(d['ship_roles']==['support_ship'],'Unexpected Behemoth role');d['ship_roles']=['attack_ship'];edits[rel]=d
    rel='entities/expanse26_tycho_recovery_component.unit_item';d=get(base,rel);require(d['is_finite'] and 'price' not in d,'Not an NPC reward item');d.pop('build_time');edits[rel]=d
    rel='localized_text/en.localized_text';d=get(base,rel);key='expanse26_tycho_recovery_component.description'
    require('Fitting takes the normal component build time.' in d[key],'Unexpected Tycho reward description')
    d[key]=d[key].replace(' Fitting takes the normal component build time.',' Fitted from the purchased finite inventory.');edits[rel]=d
    radii=[]
    for p in (base/'entities').glob('*.unit'):
        d=read(p);build=d.get('build',{});ext=d.get('spatial',{}).get('box',{}).get('extents')
        if 'build_radius' not in build or not ext:continue
        required=math.hypot(ext[0],ext[2])
        if required-build['build_radius']<=.001:continue # native float32 rounding
        require(p.stem=='expanse22_foehammer_battery','Unexpected substantial radius deficit '+p.name)
        before=build['build_radius'];build['build_radius']=math.ceil(required*100)/100;edits['entities/'+p.name]=d
        radii.append({'unit':p.stem,'before':before,'after':build['build_radius'],'required_xz_radius':required})
    report['placement_repairs']=radii
    proof=read(ROOT/'audit/update27_1/socket-repair.json')['official_compiler_proof']
    for label,key in [('without','without_sha256'),('with','with_sha256')]:
        require(sha256(ROOT/'build/update27_1-sockets/socket-proof'/label/'proof.mesh')==proof[key],'Compiler proof drift')
    report['socket_serializer_proof']=proof
    for n,record in gimbals(base).items():
        p=base/'meshes'/(n+'.mesh');p=p if p.exists() else GAME/'meshes'/p.name;old=read_mesh(p)
        if any(x['name'].startswith('turret_muzzle.') for x in old['meshpoints']):continue
        require(p.is_relative_to(base) and not old['meshpoints'],'Only empty custom gimbal socket tables')
        pts=[{'name':'turret_muzzle.'+str(i),'position':v,'rotation':IDENTITY,'bone_index':0} for i,v in enumerate(record['muzzle_positions'])]
        raw=p.read_bytes();start,end=section(raw);require(end-start==8,'Nonempty old socket table')
        revised=raw[:start]+encode(pts)+raw[end:];rel='meshes/'+p.name;dest=artroot/rel;dest.parent.mkdir(parents=True,exist_ok=True);dest.write_bytes(revised);new=read_mesh(dest)
        for k in ['vertices','triangles','box','sphere','materials','primitives']:require(old[k]==new[k],'Gimbal geometry changed '+k)
        require(raw[:start]==revised[:start] and raw[end:]==revised[start+len(encode(pts)):],'Bytes changed outside socket table')
        require(revised[new['parsed_prefix_bytes']:]==raw[old['parsed_prefix_bytes']:],'Acceleration trailer changed')
        art[rel]=dest;replacements[rel]=sha256(p)
        report['gimbal_repairs'].append({'file':rel,**record,'new_points':new['meshpoints'],'geometry_material_acceleration_unchanged':True})
    report['references']={str(GAME/'entities'/n):sha256(GAME/'entities'/n) for n in ['trader_robotics_cruiser_repair_droids.action_data_source','viturak_phase_shifter.unit_item']}
    write(audit/'load-repairs.json',report)
    return edits,art,replacements,levels

def check(base):
    roles={r for p in (GAME/'entities').glob('*.unit') for r in read(p).get('ship_roles',[])}
    for p in (base/'entities').glob('*.unit'):
        d=read(p);require(set(d.get('ship_roles',[]))<=roles,'Invalid ship role '+p.name)
        for group in d.get('skin_groups',[]):
            for sn in group['skins']:
                for stage in get(base,'entities/'+sn+'.unit_skin')['skin_stages']:
                    require(stage.get('gui'),'Missing skin GUI '+sn)
        br=d.get('build',{}).get('build_radius');e=d.get('spatial',{}).get('box',{}).get('extents')
        if br is not None and e:require(br+.001>=math.hypot(e[0],e[2]),'Invalid build clearance '+p.name)
    count=0
    for p in (base/'entities').glob('*.action_data_source'):
        d=read(p)
        for v in d.get('action_values',[]):
            if 'values' in v['action_value']:require(len(v['action_value']['values'])==d.get('level_count',1),'Static array level mismatch '+p.name)
        count+=1
    biaxial=audit_sockets(base);gimbal=gimbals(base)
    for n in gimbal:
        p=base/'meshes'/(n+'.mesh');p=p if p.exists() else GAME/'meshes'/p.name
        require(any(x['name'].startswith('turret_muzzle.') for x in read_mesh(p)['meshpoints']),'Missing gimbal muzzle '+n)
    return {'status':'PASS OFFLINE','action_sources_checked':count,'gimbal_meshes_checked':len(gimbal),'biaxial_pairs_checked':len(biaxial),'roles_and_build_radii':'PASS','all_unit_skin_gui_objects_present':'PASS','crash_reproduction':'NOT RUN; last Scirocco empty-resource fault remains unlocalized'}
