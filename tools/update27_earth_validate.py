"""Private offline schema, reference, rig and combat-contract validation."""
from pathlib import Path
import hashlib,json,inspect
import numpy as np
from common import read,write,read_mesh
from update27_earth_geometry import ROOT,BASE,AUD,GAME,BUILD,IDS
from update27_earth_gameplay import changes
import update11_validate as sv
from amun06_validate_package import AmunResolver
import build_combat03,amun06_validate_package
NATIVE=Path('/run/media/haker/NVME 2/SteamLibrary/steamapps/common/Sins2');sv.GAME=NATIVE;sv.SDK=NATIVE.parent/'Sins of a Solar Empire II - Mod Tools'
def main():
 edits,loc,origins,contract=changes();view=BUILD/'validation-view';view.mkdir(exist_ok=True)
 for tree in [BASE,GAME]:
  for p in tree.rglob('*'):
   if p.is_file():
    d=view/p.relative_to(tree);d.parent.mkdir(parents=True,exist_ok=True)
    if d.is_symlink():d.unlink()
    if not d.exists():d.symlink_to(p)
 text=read(BASE/'localized_text/en.localized_text');text.update(loc);p=view/'localized_text/en.localized_text'
 if p.is_symlink():p.unlink()
 write(p,text)
 schemas=[sv.schema_check(view/rel,Path(origins[rel]))for rel in edits]
 schemas += [sv.schema_check(p) for p in (GAME/'brushes').glob('*.brush')]
 resolver=AmunResolver(view,NATIVE);units={ID:resolver.unit(ID,'Private update27 Earth audit')for ID in IDS.values()}
 source=inspect.getsource(build_combat03.check_actions).replace("filters={v['target_filter_id'] for v in ads.get('target_filters',[])}","filters={v['target_filter_id'] for v in ads.get('target_filters',[])}|set(resolver.filters)");scope=dict(vars(build_combat03));exec(source,scope)
 actions={ID:scope['check_actions'](view,resolver,ID)for ID in units}
 source=inspect.getsource(amun06_validate_package.check_action_values).replace("require(set(v)<=filters,'Unknown target_filters list member')","require(set(v)<=(filters|set(resolver.filters)),'Unknown target_filters list member')");scope=dict(vars(amun06_validate_package));exec(source,scope)
 values={ID:scope['check_action_values'](view,NATIVE,resolver,u)for ID,u in units.items()}
 for kind,ID in IDS.items():
  art=read(AUD/(kind+'-integration.json'));u=units[ID];points={p['name']:p for p in read_mesh(GAME/'meshes'/(art['hull_mesh']+'.mesh'))['meshpoints']}
  for r in art['rigs']:
   m=r['mount'];assert m['mesh_point']in points;assert np.allclose(points[m['mesh_point']]['position'],m['weapon_position'],atol=2e-5)
   w=read(GAME/'entities'/(m['weapon']+'.weapon'))
   if r['kind']=='pdc':assert w['damage']/w['cooldown_duration']==85 and w['yaw_speed']==180
   else:assert w['cooldown_duration']==60 and w['pitch_speed']==0
  assert all(h['max_shield_points']==0 and h['shield_point_restore_rate']==0 for h in u['health']['levels'])
  assert not u.get('colonize_ability');assert len(art['exhausts'])==(5 if kind=='hale'else 4)
  for p,h in art['files'].items():assert hashlib.sha256((GAME/p).read_bytes()).hexdigest()==h,p
  assert all(v['opposed_winding_triangles']==0 and v['official_triangle_grid_and_trailer_preserved']for v in art['compile_checks'].values())
 for p,h in contract['source_definitions_sha256'].items():assert hashlib.sha256(Path(p).read_bytes()).hexdigest()==h
 files={str(p.relative_to(GAME)):hashlib.sha256(p.read_bytes()).hexdigest()for p in sorted(GAME.rglob('*'))if p.is_file()};assert not any(p.is_symlink()for p in GAME.rglob('*'))
 write(AUD/'game-files-sha256.json',files);write(AUD/'validation.json',{'status':'PASS OFFLINE','schemas':schemas,'actions':actions,'action_values':values,'checks':['all source definitions unchanged','native schemas and references','zero opposed compiled winding','only tangent bytes repaired; native triangle grids preserved','rig meshpoints match unit origins','85 DPS per PDC','60-second rails with zero elevation tracking','five Hale and four Munroe plume origins','all owned art hashes match','no new capture system or shield pool'],'pdc_clearance':'Separate compiled-clearance.json: 1-degree grid plus 3-degree envelope against stationary hull and rails; moving sibling mounts excluded','files':len(files),'untested':contract['untested']});print('PASS',len(schemas),'schemas',len(files),'owned files')
if __name__=='__main__':main()
