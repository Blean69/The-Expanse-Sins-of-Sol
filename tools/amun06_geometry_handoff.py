"""Validate staged resource linkage and emit frozen integrator contract."""
from amun06_geometry_common import *
import hashlib, struct
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
m=read(AUDIT/'mount-metadata.json');v=read(AUDIT/'output-validation.json');checks=read(AUDIT/'independent-checks.json');assert v['status'].startswith('PASS') and checks['status'].startswith('PASS')
game=ROOT/'build/amun06-b/game';textures=[]
for p in sorted((game/'textures').glob('*.dds')):
 data=p.read_bytes();assert data[:4]==b'DDS ';h,w=struct.unpack_from('<II',data,12);assert (w,h)==(2048,2048);fourcc=data[84:88];assert fourcc in [b'DX10',b'BC5S'];fmt=struct.unpack_from('<I',data,128)[0] if fourcc==b'DX10' else 84;assert fmt==(84 if p.stem.endswith('_nrm') else 98);textures.append({'path':str(p),'sha256':sha(p),'width':w,'height':h,'dxgi_format':fmt,'fourcc':fourcc.decode()})
assert len(textures)==4
materials=[]
for p in sorted((game/'mesh_materials').glob('*.mesh_material')):
 d=read(p)
 for key,value in d.items():
  if key.endswith('_texture') and isinstance(value,str):assert (game/'textures'/(value+'.dds')).is_file(),(p,key,value)
 materials.append({'id':p.stem,'path':str(p),'sha256':sha(p)})
meshes=[]
for key,o in v['outputs'].items():
 assert sha(o['mesh'])==o['sha256']
 for name in o['materials']:assert any(q['id']==name for q in materials),name
 meshes.append({'id':Path(o['mesh']).stem,'path':o['mesh'],'sha256':o['sha256'],'triangles':o['triangles'],'materials':o['materials']})
assert len(meshes)==8 and len(materials)==8
spec={'status':'PASS OFFLINE ONLY','runtime':'NOT RUN','game_directory':str(game),'hull_mesh':'expanse06_amun_hull','pod_mesh':'expanse06_amun_boarding_pod','rigs':m['rigs'],'spatial':m['ship_spatial'],'equipment':m['equipment'],'normalization':m['normalization'],'selection':m['selection'],'meshes':meshes,'materials':materials,'textures':textures,'ship_triangle_count':m['ship_triangle_total'],'pod_triangle_count':m['pod_triangle_total'],'pod_meshpoints':v['outputs']['amun_boarding_pod']['meshpoints'],'editable_ship':str(OUT/'expanse06_amun_editable.gltf'),'editable_pod':str(OUT/'expanse06_pod_editable.gltf'),'compiler_input_is_z_reflected':True,'editable_is_z_reflected':False,'mesh_compiler_applies_z_reflection':True,'material_limitations':read(AUDIT/'material-resources.json'),'source_hashes':m['source_hashes'],'offline_validation':str(AUDIT/'output-validation.json'),'independent_checks':str(AUDIT/'independent-checks.json')}
write(AUDIT/'integration-spec.json',spec);write(AUDIT/'resource-checks.json',{'status':'PASS OFFLINE ONLY','meshes':len(meshes),'materials':len(materials),'textures':textures,'all_mesh_material_and_texture_references_resolved':True});print('PASS: staged eight meshes, eight materials, four DDS; integration-spec ready')
