"""Validate final compiled art contracts and emit exact dependency manifests."""
from update27_mars_assets import *
import jsonschema
import importlib.util
def local_module(name):
 spec=importlib.util.spec_from_file_location('_isolated_'+name,ROOT/'tools'/(name+'.py'));module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module);return module
changes=local_module('update27_storm_patch').changes

SDK=Path('/run/media/haker/NVME 2/SteamLibrary/steamapps/common/Sins of a Solar Empire II - Mod Tools/json_schemas')
def digest(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def artifact(key):
 meta=read(AUD/(key+'-integration.json'));assert meta['compiled']
 meshes=set(meta['compiled_meshes'])|set(meta['copied_meshes']);paths=set();materials=set()
 for name in sorted(meshes):
  p=GAME/'meshes'/(name+'.mesh');assert p.exists();paths.add(p)
  mi=read_mesh(p);materials.update(mi['materials'])
  if name==meta['hull_mesh']:
   points={p['name']:p for p in mi['meshpoints']}
   for pt in meta['meshpoints']:
    assert pt['name'] in points
    assert np.allclose(pt['translation'],points[pt['name']]['position'],atol=2e-4)
   if meta.get('epstein_drive_pass'):
    meshrows=local_module('update27_epstein_surface').meshrows
    rv,_=meshrows(p);center=np.array(meta['spatial']['box']['center']);extent=np.array(meta['spatial']['box']['extents'])
    assert (abs(rv[:,:3]-center)<=extent+2e-4).all(),'Hull/drive outside final spatial box'
    assert np.linalg.norm(rv[:,:3],axis=1).max()<=meta['spatial']['radius']+2e-4
    prior=read(BUILD/'pre-epstein'/(key+'-integration.json'))
    assert meta['spatial'].get('collision_rank')==prior['spatial'].get('collision_rank')
    old={r['mesh_point']:r for r in prior['rigs']}
    for r in meta['rigs']:
     assert r['position']==old[r['mesh_point']]['position'],'Weapon pivot moved in engine pass'
     assert r['turret_override']==old[r['mesh_point']]['turret_override'],'Turret changed in engine pass'
    if 'torpedo_ports'in prior:assert meta['torpedo_ports']==prior['torpedo_ports']
 for name in materials:
  p=GAME/'mesh_materials'/(name+'.mesh_material');assert p.exists();paths.add(p)
  for field,name in read(p).items():
   if field.endswith('_texture'):
    tex=GAME/'textures'/(name+'.dds');assert tex.exists(),tex;paths.add(tex)
    if name.startswith('expanse27_thermal_tiles_'):
     from PIL import Image
     dimensions=Image.open(tex).size;assert all(x%4==0 for x in dimensions),'BC7 dimensions must satisfy Direct3D block alignment'
     if name.endswith(('_clr','_nrm')):assert dimensions==(1024,1024)
 assert len(meta['rigs'])=={'storm':6,'laconia':6,'hephaestus':11}[key]
 assert len(meta['arc_checks'])==len(meta['rigs'])
 assert all(a['blocked']==0 for a in meta['arc_checks'])
 if key=='hephaestus':assert meta['rigs'][10]['kind']=='rail'
 rows=[]
 for p in sorted(paths):
  rel=p.relative_to(GAME);old=BASE/rel;sha=digest(p);previous=digest(old)if old.exists()else None
  rows.append({'path':str(rel),'bytes':p.stat().st_size,'sha256':sha,'previous_sha256':previous,'action':'reuse'if sha==previous else('replace'if previous else'add')})
 result={'ship':key,'artifact_root':str(GAME),'baseline':str(BASE),'contract':str(AUD/(key+'-integration.json')),'files':rows,'compiled_assembled_triangles':meta['compiled_assembled_triangles'],'sampled_clearance_rays':sum(a['rays']for a in meta['arc_checks']),'runtime':'NOT RUN'}
 write(AUD/(key+'-manifest.json'),result);return result

def storm_patch():
 edits,_,_,report=changes(BASE)
 for path,new in edits.items():
  suffix=Path(path).suffix[1:];schema=read(SDK/(suffix.replace('_','-')+'-schema.json'));jsonschema.Draft7Validator(schema).validate(new)
  old=read(BASE/path)
  if suffix=='weapon':
   assert {k:v for k,v in new.items()if k!='turret'}=={k:v for k,v in old.items()if k!='turret'}
   assert new['turret'].keys()==old['turret'].keys()
  elif suffix=='ability':
   assert {k:v for k,v in new.items()if k!='ability_positions'}=={k:v for k,v in old.items()if k!='ability_positions'}
  elif suffix=='unit':
   assert {k:v for k,v in new.items()if k not in ['spatial','weapons']}=={k:v for k,v in old.items()if k not in ['spatial','weapons']}
   for a,b in zip(old['weapons']['weapons'],new['weapons']['weapons']):
    assert {k:v for k,v in a.items()if k not in ['weapon_position','non_turret_muzzle_positions']}=={k:v for k,v in b.items()if k not in ['weapon_position','non_turret_muzzle_positions']}
 write(AUD/'storm-patch-validation.json',{'definitions':len(edits),'schemas':'PASS','nonspatial_field_guards':'PASS','report':report,'runtime':'NOT RUN'})

if __name__=='__main__':
 keys=sys.argv[1:]or['storm','laconia','hephaestus'];results=[artifact(k)for k in keys]
 if 'storm'in keys:storm_patch()
 print([(r['ship'],len(r['files']),r['sampled_clearance_rays'])for r in results])
