"""Stage only existing generated hero maps and required private material aliases."""
from common import *
import hashlib,shutil,re
build=ROOT/'build/geometry04-b';dest=build/'game';(dest/'mesh_materials').mkdir(parents=True,exist_ok=True);(dest/'textures').mkdir(exist_ok=True);src=ROOT/'assets/derived/geometry03-b/hero/materials';records={}
for path in sorted((build/'compiler-json').glob('*.mesh_json')):
 for name in read(path)['materials']:
  alias=re.search(r'expanse03_hero_mat_\d+$',name).group(0);inp=src/(alias+'.mesh_material');shutil.copy2(inp,dest/'mesh_materials'/(name+'.mesh_material'));records[name]=str(inp)
for path in sorted((ROOT/'build/geometry03-b/hero/game/textures').glob('*.dds')):assert path.read_bytes()[:4]==b'DDS ';shutil.copy2(path,dest/'textures'/path.name)
write(ROOT/'audit/geometry04-b/material-resources.json',{'aliases':records,'files':{str(p):hashlib.sha256(p.read_bytes()).hexdigest() for folder in ['mesh_materials','textures'] for p in sorted((dest/folder).iterdir())}});print(len(records),'material aliases;12 existing DDS maps reused')
