"""Separate visual/audio polish overlay on the frozen 0.12 fleet."""
from pathlib import Path
import argparse,copy,json,shutil,zipfile
import numpy as np
from validate_experiments import read,require,sha256,file_hashes,compare_tree,verify_pins,verify_zip,provenance
from build_polish import write,cp
from build_update11 import aliases,spatial
from build_update12 import phase_effect
from build_amun06 import patch_pointer
from update11_validate import schema_check
from build_combat04 import binary_geometry
from amun06_validate_package import AmunResolver,check_action_values
from build_combat03 import check_actions
ROOT=Path(__file__).resolve().parents[1];BASE=ROOT/'build/experiments/expanse_update12';OUT=ROOT/'build/experiments/expanse_update13';AUD=ROOT/'audit/update13';GAME=ROOT.parent/'SteamLibrary/steamapps/common/Sins2';SDK=GAME.parent/'Sins of a Solar Empire II - Mod Tools'
ALIAS='trader_antifighter_frigate_point_defense_autocannon_weapon_muzzle'

def preservation():
 d=read(AUD/'checkpoint.json');trees=[compare_tree(t)for t in d['trees']]
 for p,h in {**d['zips'],**d['originals'],d['enabled_path']:d['enabled_sha256']}.items():require(sha256(p)==h,'Frozen file changed: '+p)
 return {'trees':trees,'zips':len(d['zips']),'originals':len(d['originals']),'pins':verify_pins(ROOT,GAME,SDK),'enabled_settings_unchanged':True}

def contracts():
 p=AUD/'integration-inputs.json';require(p.exists(),'Missing reviewed asset contract: '+str(p));c=read(p)
 for p,h in read(AUD/'reviewed-inputs.json').items():require(Path(p).is_file() and sha256(p)==h,'Ignored asset/SDK handoff missing or changed: '+p)
 require(set(c['ui'])=={'trader_light_frigate','expanse12_scirocco','trader_scout_corvette'},'Incomplete model UI inputs')
 require(set(c['geometry'])=={'expanse12_scirocco','trader_scout_corvette'},'Incomplete geometry inputs')
 return c

def updated_unit(name,m):
 u=read(BASE/'entities'/(name+'.unit'));spatial(u,m)
 if m.get('rigs'):u['weapons']['weapons']=[r['mount']for r in m['rigs']]
 return u

def updated_skin(name,c):
 s=read(BASE/'entities'/(name+'.unit_skin'))
 for stage in s['skin_stages']:
  for row in stage.get('effects',{}).get('effect_alias_bindings',[]):
   if row['alias_name']==ALIAS and row['alias_binding'].get('sounds')==['expanse10_pdc_burst']:
    row['alias_binding']['sounds']=['expanse13_pdc_report_'+str(i)for i in range(4)]
 if name in c['ui']:
  for patch in read(c['ui'][name])['skin_patches']:patch_pointer(s,patch['pointer'],patch['value'])
 if name in c['geometry']:
  m=read(c['geometry'][name]);st=s['skin_stages'][0];st['unit_mesh']['mesh']=m['hull_mesh']
  if m.get('rigs'):st['child_mesh_alias_bindings']=aliases(m)
 return s

def assets(c):
 result={}
 for directory in c['resource_directories']:
  for p,h in file_hashes(directory).items():
   require(Path(p).parts[0] in {'meshes','mesh_materials','textures','brushes','sounds'} or p.endswith('_logo.png'),'Asset worker attempted shared definition: '+p)
   if p in result:require(result[p][1]==h,'Worker resource collision: '+p)
   result[p]=(str(Path(directory)/p),h)
 return result

def build(c):
 require(not OUT.exists() and not OUT.with_suffix('.zip').exists(),'Refusing existing polish package');shutil.copytree(BASE,OUT)
 for rel,(src,h)in assets(c).items():cp(Path(src),OUT/rel)
 for name,src in c['geometry'].items():
  m=read(src);require(m['status'].startswith('PASS'),'Incomplete geometry: '+name);write(OUT/'entities'/(name+'.unit'),updated_unit(name,m))
  for rig in m.get('rigs',[]):
   wname=rig['mount']['weapon'];w=read(BASE/'entities'/(wname+'.weapon'));w['turret']=rig['turret_override'];write(OUT/'entities'/(wname+'.weapon'),w)
 for p in (BASE/'entities').glob('*.unit_skin'):
  s=updated_skin(p.stem,c)
  if s!=read(p):write(OUT/'entities'/p.name,s)
 sun=read(c['geometry']['trader_scout_corvette']);write(OUT/'effects/expanse12_sunflare_phase_plume.particle_effect',phase_effect(sun['equipment']['exhausts'],.35,2.4))
 meta=read(BASE/'.mod_meta_data');meta.update(display_name='The Expanse — 0.13 MODEL & AUDIO POLISH',display_version='0.13.0',short_description='Martian livery, clearer Scirocco PDCs, corrected scout presentation and shorter PDC reports.',long_description='Load alone. Includes complete 0.12 fleet. Visual orientation and sound-mix changes require workstation confirmation; gameplay budgets remain unchanged.');write(OUT/'.mod_meta_data',meta)
 (OUT/'ASSET-SOURCES.md').write_text((ROOT/'ASSET-SOURCES.md').read_text())

def validate(c):
 before=file_hashes(BASE);after=file_hashes(OUT);resource=assets(c);allowed=set(resource)|{'.mod_meta_data','ASSET-SOURCES.md','effects/expanse12_sunflare_phase_plume.particle_effect'}
 for name,src in c['geometry'].items():
  m=read(src);p='entities/'+name+'.unit';require(read(OUT/p)==updated_unit(name,m),'Unit gameplay drift: '+name);allowed.add(p)
  for rig in m.get('rigs',[]):
   p='entities/'+rig['mount']['weapon']+'.weapon';w=read(BASE/p);w['turret']=rig['turret_override'];require(read(OUT/p)==w,'Weapon firing budget or targeting changed: '+p);allowed.add(p)
 for p in (BASE/'entities').glob('*.unit_skin'):
  expected=updated_skin(p.stem,c);require(read(OUT/'entities'/p.name)==expected,'Unexpected skin change: '+p.name)
  if expected!=read(p):allowed.add('entities/'+p.name)
 require(not set(before)-set(after),'Prior package file removed')
 for p,h in before.items():require(after[p]==h or p in allowed,'Unexpected baseline content changed: '+p)
 require(set(after)-set(before)<=allowed,'Unreviewed added file')
 for p,(src,h)in resource.items():require(after[p]==h,'Resource differs from reviewed worker input: '+p)
 schemas=[]
 for p,h in after.items():
  if before.get(p)!=h:
   r=schema_check(OUT/p,BASE/p if p.endswith('.unit') else None)
   if r:schemas.append(r)
 meshes=[binary_geometry(OUT/p)for p in resource if p.endswith('.mesh')]
 resolver=AmunResolver(OUT,GAME);graphs={};frames=[]
 names=['trader_light_frigate','expanse12_raptor','expanse12_pella','expanse12_scirocco','trader_scout_corvette','expanse_donnager_battleship','expanse_mcrn_corvette','expanse_rocinante_hero','expanse_amun_ra']
 for n in names:
  u=resolver.unit(n,'0.13 integrated ship');graphs[n]={'graph':check_actions(OUT,resolver,n),'typed':check_action_values(OUT,GAME,resolver,u)}
 for name,src in c['geometry'].items():
  m=read(src);hull=resolver.mesh(m['hull_mesh'],name);points={p['name']:p for p in hull['meshpoints']}
  for rig in m.get('rigs',[]):
   mount=rig['mount'];point=points[mount['mesh_point']];rot=np.array(point['rotation']).reshape(3,3)
   require(np.allclose(point['position'],mount['weapon_position'],atol=4e-5) and np.allclose(rot[1],mount['up'],atol=4e-5) and np.allclose(rot[2],mount['forward'],atol=4e-5),'Bad compiled mountframe')
   frames.append(mount['weapon'])
  for noz in m['equipment']['exhausts']:require(any(np.allclose(noz['position'],p['position'],atol=4e-5)for k,p in points.items()if k.startswith('exhaust.')),'Exhaust transform mismatch')
 require(read(OUT/'effects/expanse12_sunflare_phase_plume.particle_effect')==phase_effect(read(c['geometry']['trader_scout_corvette'])['equipment']['exhausts'],.35,2.4),'Scout phase effect did not follow nozzle')
 audio=read(AUD/'audio.json');require(audio['status'].startswith('PASS'),'Audio incomplete');bound=[]
 for p in (OUT/'entities').glob('*.unit_skin'):
  if 'expanse13_pdc_report_' in p.read_text():bound.append(p.stem)
 require(len(bound)==8,'PDC audio did not reach all eight Expanse armed skins')
 for row in audio['reports']:
  sound=read(OUT/'sounds'/(row['id']+'.sound'));require(sound==audio['sound_profile'],'Unexpected sound configuration');require(sha256(OUT/'sounds'/(row['id']+'.ogg'))==row['ogg_sha256'],'Wrong audio variant')
 return {'status':'PASS OFFLINE ONLY','runtime':'NOT RUN','schemas':schemas,'meshes':meshes,'compiled_mounts':frames,'references':resolver.edges,'ability_graphs':graphs,'audio_ships':bound,'preservation':preservation(),'changed_existing_files':[p for p in before if before[p]!=after[p]],'added_files':sorted(set(after)-set(before))}

def main(a):
 preservation();c=contracts()
 if not(a.validate_only or a.package_existing):build(c)
 write(AUD/'package-validation.json',validate(c))
 if a.validate_only:
  print(json.dumps({'status':'PASS OFFLINE PACKAGE TREE','runtime':'NOT RUN','archive_check':'Not requested by --validate-only'},indent=2));return
 if not a.validate_only:
  require(not OUT.with_suffix('.zip').exists(),'Refusing existing ZIP')
  with zipfile.ZipFile(OUT.with_suffix('.zip'),'w',zipfile.ZIP_DEFLATED)as z:
   for p in sorted(OUT.rglob('*')):
    if p.is_file():
     zi=zipfile.ZipInfo(p.relative_to(OUT).as_posix(),(2026,9,13,0,0,0));zi.compress_type=zipfile.ZIP_DEFLATED;zi.external_attr=0o100644<<16;z.writestr(zi,p.read_bytes())
 summary={'mod_id':OUT.name,**verify_zip(OUT.with_suffix('.zip'),OUT),'installed':False,'runtime':'NOT RUN'};write(AUD/'package-summary.json',summary)
 deps=[BASE,AUD/'integration-inputs.json',AUD/'reviewed-inputs.json']+[Path(p)for p in c['resource_directories']];write(OUT.with_suffix('.dependencies.json'),list(map(str,deps)));write(OUT.with_suffix('.provenance.json'),provenance(OUT.with_suffix('.zip'),ROOT,deps));print(json.dumps(summary,indent=2))
if __name__=='__main__':
 p=argparse.ArgumentParser(description=__doc__);g=p.add_mutually_exclusive_group();g.add_argument('--validate-only',action='store_true');g.add_argument('--package-existing',action='store_true');main(p.parse_args())
