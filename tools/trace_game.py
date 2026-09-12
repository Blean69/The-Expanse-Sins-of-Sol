"""Record paths and JSON-pointer relationships; ambiguous matches stay explicit."""
from common import *
import hashlib, collections, csv, re

files=[f for f in GAME.rglob('*') if f.is_file()]
index=collections.defaultdict(list)
for f in files: index[f.stem.lower()].append(f)
localization=read(GAME/'localized_text/en.localized_text')
def strings(x,p=''):
    if isinstance(x,dict):
        for k,v in x.items(): yield from strings(v,p+'/'+k.replace('~','~0').replace('/','~1'))
    elif isinstance(x,list):
        for i,v in enumerate(x): yield from strings(v,p+'/'+str(i))
    elif isinstance(x,str): yield p,x

roots=['entities/trader_light_frigate.unit','entities/trader_light_frigate.unit_skin','entities/trader_torpedo_cruiser.unit','entities/trader_torpedo_cruiser_torpedo.weapon','entities/trader_antifighter_frigate.unit','uniforms/target_filter.uniforms','uniforms/attack_target_type_group.uniforms','uniforms/attack_target_type.uniforms','uniforms/weapon.uniforms','uniforms/debris.uniforms']
def expected(ptr, source):
    parts=[v for v in ptr.split('/') if v and not v.isdigit()];key=parts[-1] if parts else ''
    if source.suffix=='.mesh':return ['.mesh_material']
    if 'dialogue' in parts or any(v in parts for v in ['sounds','move_sounds']) or key.endswith('_sound'):return ['.sound']
    if key in ['weapon','attack_target_type_groups_matching_weapon']:return ['.weapon']
    if key=='skins':return ['.unit_skin']
    if key=='spawned_unit':return ['.unit']
    if key in ['death_sequence_group','death_sequences']:return ['.death_sequence_group'] if key.endswith('group') else ['.death_sequence']
    if key=='shield_effect':return ['.shield_effect']
    if 'mesh'==key or key.endswith('_mesh'):return ['.mesh']
    if 'texture' in key and 'frame' not in key:return ['.dds','.png','.texture_animation']
    if 'effect' in key:return ['.particle_effect','.beam_effect','.effect_alias']
    if 'icon' in key or 'picture' in key:return ['.brush','.png']
    return []
edges=[]; seen=set(); q=collections.deque(GAME/r for r in roots); unresolved=[]
while q:
    f=q.popleft()
    if f in seen: continue
    seen.add(f); rel=str(f.relative_to(GAME)); values=[]
    try:
        if f.suffix=='.mesh':
            d=read_mesh(f); values=[('/materials/'+str(i),m) for i,m in enumerate(d['materials'])]
        elif f.suffix not in ['.dds','.ogg','.png','.fxc','.ttf','.otf']:
            values=list(strings(read(f)))
    except (ValueError,UnicodeError,AssertionError,KeyError,struct.error): continue
    for ptr,value in values:
        if value in localization:
            edges.append([rel,ptr,value,'localized_text/en.localized_text#/'+value,'localization'])
        allowed=expected(ptr,f)
        matches=[p for p in index.get(value.lower(),[]) if p.suffix in allowed]
        for target in matches:
            if target==f: continue
            edges.append([rel,ptr,value,str(target.relative_to(GAME)),'exact_stem' if value==target.stem else 'casefold_stem'])
            q.append(target)
        if not matches and value not in localization:
            if allowed:unresolved.append(dict(file=rel,pointer=ptr,value=value))
    if f.suffix=='.sound':
        for target in index[f.stem.lower()]:
            if target.suffix=='.ogg':edges.append([rel,'(implicit same basename)',f.stem,str(target.relative_to(GAME)),'sound_audio']);q.append(target)

# Effect IDs can refer to skin-local aliases, not standalone files.
for skin in [f for f in seen if f.suffix=='.unit_skin']:
    for si,stage in enumerate(read(skin).get('skin_stages',[])):
        for ai,alias in enumerate(stage.get('effects',{}).get('effect_alias_bindings',[])):
            for u in unresolved:
                if u['value']==alias['alias_name']:
                    edges.append([u['file'],u['pointer'],u['value'],str(skin.relative_to(GAME))+f'#/skin_stages/{si}/effects/effect_alias_bindings/{ai}','skin_local_alias'])

out=ROOT/'audit'
with (out/'reference-edges.csv').open('w',newline='') as h:
    w=csv.writer(h);w.writerow(['source','json_pointer','id','target','resolution']);w.writerows(sorted(edges))
write(out/'unresolved-strings.json',unresolved)
manifest={str(f.relative_to(GAME)):{'bytes':f.stat().st_size,'sha256':hashlib.sha256(f.read_bytes()).hexdigest()} for f in sorted(seen)}
write(out/'installed-file-hashes.json',manifest)
steamapps=GAME.parents[1]
def build_id(app):
    manifest=(steamapps/f'appmanifest_{app}.acf').read_text()
    return re.search(r'"buildid"\s+"([^"]+)"',manifest).group(1)
logs=steamapps/'compatdata/1575940/pfx/drive_c/users/steamuser/AppData/Local/sins2/logs'
version='Not established from logs';version_log=None
for log in sorted(logs.glob('*.txt'),key=lambda p:p.stat().st_mtime,reverse=True):
    m=re.search(r'Version = ([^\r\n]+)',log.read_text(errors='replace'))
    if m:version=m.group(1);version_log=str(log);break
write(out/'environment.json',dict(game_path=str(GAME),sdk_path=str(SDK),game_version=version,version_log=version_log,game_steam_build=build_id(1575940),sdk_steam_build=build_id(3172890),official_schema_commit=read(out/'schema-comparison.json')['official_commit'],scope='Static inspection; game has not been launched for this project',root_files=roots))
print('Recorded',len(seen),'files,',len(edges),'relationships. Unresolved strings include enums and symbolic IDs; see trace caveats.')
