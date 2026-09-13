"""Reuse the accepted texture content and material values with new compiled aliases.
No source images are altered and no texture recompression is needed.
"""
from update11_donnager_common import *
import shutil
prior=FROZEN/'build/donnager10-b/game';dest=BUILD/'game';records=[];textures=set()
for jp in sorted((BUILD/'compiler-json').glob('*.mesh_json')):
 for name in read(jp)['materials']:
  old_name=name.replace('expanse11_','expanse10_');src=prior/'mesh_materials'/(old_name+'.mesh_material');assert src.is_file(),src
  output=dest/'mesh_materials'/(name+'.mesh_material');output.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(src,output)
  for key,value in read(src).items():
   if key.endswith('_texture'):textures.add(value)
  records.append({'new_material':name,'source':str(src),'source_sha256':hashlib.sha256(src.read_bytes()).hexdigest(),'definition_values_exactly_preserved':True})
for name in sorted(textures):
 src=prior/'textures'/(name+'.dds');assert src.is_file();out=dest/'textures'/src.name;out.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(src,out)
write(AUDIT/'material-resources.json',{'status':'PASS EXACT ACCEPTED TEXTURE/MATERIAL REUSE','aliases':records,'textures':{name:hashlib.sha256((dest/'textures'/(name+'.dds')).read_bytes()).hexdigest() for name in sorted(textures)},'source_normal_maps':'Original Donnager has no detail normal maps; original flat normal derivative preserved; source color atlases remain2048x2048'})
print('PASS',len(records),'material aliases and',len(textures),'byte-identical DDS maps')
