"""Copy generated hero DDS maps and remap emitted armed material IDs only."""
from common import *
import shutil,hashlib
src=ROOT/'assets/derived/geometry03-b/hero';build=ROOT/'build/geometry03-b';armed=build/'hero-armed/game';materials=read(build/'hero-armed/compiler-json/expanse03_hero_armed.mesh_json')['materials'];(armed/'mesh_materials').mkdir(parents=True,exist_ok=True);(armed/'textures').mkdir(exist_ok=True)
for name in materials:
 source=name.removeprefix('expanse03_hero_armed_');shutil.copy2(src/'materials'/(source+'.mesh_material'),armed/'mesh_materials'/(name+'.mesh_material'))
for source in sorted((build/'hero/game/textures').glob('*.dds')):
 assert source.read_bytes()[:4]==b'DDS ';shutil.copy2(source,armed/'textures'/source.name)
assert len(list((armed/'textures').glob('*.dds')))==12
write(ROOT/'audit/geometry03-b/hero-armed-resources.json',{'materials':materials,'files':{str(p):hashlib.sha256(p.read_bytes()).hexdigest() for sub in ['mesh_materials','textures'] for p in sorted((armed/sub).iterdir())},'source_colors':'Preserved supplied flat-color factors converted to tiny constant maps. No original surface image textures existed.'})
