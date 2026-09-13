"""Final higher-fidelity Donnager handoff with exact baseline preservation gates."""
from update11_donnager_common import *
import struct
import jsonschema
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
m=read(AUDIT/'mount-metadata.json');v=read(AUDIT/'output-validation.json');checks=read(AUDIT/'mount-preservation-checks.json');oldspec=read(FROZEN/'audit/donnager10-b/integration-spec.json')
assert v['status']=='PASS OFFLINE ONLY' and checks['status']=='PASS BOUNDED OFFLINE ONLY'
for path,digest in read(AUDIT/'preservation-before.json').items():assert sha(path)==digest,path
for path,digest in oldspec['source_hashes'].items():assert sha(path)==digest,path
for path,digest in old['source_dependencies'].items():assert sha(path)==digest,path
master=read(INTAKE/'preserved-source-hashes.json')
for key in ['supplied_archive','preserved_archive']:assert sha(master[key])==master['archive_sha256']
meshes=[];materials=[];textures=[];donors=[];game=BUILD/'game'
sdk=Path('/run/media/haker/NVME 2/SteamLibrary/steamapps/common/Sins of a Solar Empire II - Mod Tools')
assert not (sdk/'json_schemas/mesh_material-schema.json').exists() # No such schema in this pinned SDK; exact old values are validated instead.
for key,o in v['outputs'].items():
 p=Path(o['mesh']);assert sha(p)==o['sha256'];assert o['orthogonal_fallback_vertex_count']==o['opposed_winding_triangles']==0
 if key.startswith('donnager_pdc'):
  prior=FROZEN/'build/donnager10-b/game/meshes'/p.name
  assert sha(p)==sha(prior),(p,'unchanged donor binary differs')
  assert o['near_ambiguous_winding_triangles']==(3 if key.endswith('base') else 9)
  donors.append({'file':p.name,'sha256':sha(p),'exact_prior_binary_preserved':True})
 else:assert o['near_ambiguous_winding_triangles']==0 and o['minimum_face_normal_cosine']>.86
 for mat in o['materials']:assert (game/'mesh_materials'/(mat+'.mesh_material')).is_file(),mat
 meshes.append({'id':p.stem,'path':str(p),'sha256':sha(p),'triangles':o['triangles'],'materials':o['materials']})
for p in sorted((game/'mesh_materials').glob('*.mesh_material')):
 d=read(p);assert d==read(FROZEN/'build/donnager10-b/game/mesh_materials'/p.name.replace('expanse11_','expanse10_'))
 for key,val in d.items():
  if key.endswith('_texture'):assert (game/'textures'/(val+'.dds')).is_file(),val
 materials.append({'id':p.stem,'path':str(p),'sha256':sha(p)})
for p in sorted((game/'textures').glob('*.dds')):
 b=p.read_bytes();assert b[:4]==b'DDS ';h,w=struct.unpack_from('<II',b,12);assert (FROZEN/'build/donnager10-b/game/textures'/p.name).read_bytes()==b
 fourcc=b[84:88];assert fourcc in [b'DX10',b'BC5S'];fmt=struct.unpack_from('<I',b,128)[0] if fourcc==b'DX10' else 84;assert fmt==(84 if p.stem.endswith('_nrm') else 98)
 textures.append({'path':str(p),'sha256':sha(p),'dimensions':[w,h],'dxgi_format':fmt})
editable=Gltf(OUT/'update11_donnager_editable.gltf');count=sum(editable.g['accessors'][p['indices']]['count']//3 for n in editable.g['nodes'] if 'mesh' in n for p in editable.g['meshes'][n['mesh']]['primitives']);assert count==m['assembled_triangle_total']==194296
points=v['outputs']['donnager_hull']['meshpoints'];oldpts=oldspec['meshpoints'];assert points==oldpts,'Compiled mount/equipment points differ'
assert len(meshes)==5 and len(materials)==17 and len(textures)==27
spec={'status':'PASS OFFLINE ONLY','runtime':'NOT RUN FOR THIS NEW DERIVATIVE','game_directory':str(game),'hull_mesh':'expanse11_donnager_hull','rigs':m['rigs'],'ship_spatial':m['ship_spatial'],'spatial':m['ship_spatial'],'equipment':m['equipment'],'meshes':meshes,'materials':materials,'textures':textures,'unique_mesh_triangles':m['triangle_total'],'assembled_triangle_count':count,'pdc_count':16,'railgun_count':2,'count_is_prototype_not_canonical':True,'rail_yaw_speed_override':15.,'normalization':m['normalization'],'source_hashes':m['source_hashes'],'editable':str(OUT/'update11_donnager_editable.gltf'),'editable_compiler_z_reflected':False,'compiler_input_z_reflected':True,'meshpoints':points,'offline_checks':[str(AUDIT/n) for n in ['output-validation.json','mount-preservation-checks.json','silhouette-comparison.json','uv-frame-fallback.json','preservation-checks.json']],'ui_integration_spec':str(AUDIT/'ui-integration-spec.json'),'unchanged_donor_meshes':donors,'support_correction':read(AUDIT/'support-correction.json'),'runtime_limits':['New higher-fidelity derivative has not been loaded in game; user performance observation covers previous76299triangle version only','Inherited narrow rail yaw and gun arcs remain unchanged; sampledclearance is notcontinuous collision proof','Restored surfaces locally embed some fixed socketfeet by0.11–0.45gameunits; no gun transforms moved; inspectcloseup','Detailed shaders and higherpolygon performance require workstation observation'],'material_limitations':read(AUDIT/'material-resources.json')}
write(AUDIT/'integration-spec.json',spec)
write(AUDIT/'preservation-checks.json',{'status':'PASS','prior_files':len(read(AUDIT/'preservation-before.json')),'source_master_files':len(oldspec['source_hashes']),'source_archive_sha256':master['archive_sha256'],'donor_dependencies':len(old['source_dependencies']),'compiled_donor_meshes_exact':donors,'all18_compiled_mounts_and_equipment_points_exact':True,'fixed_support_only_change':read(AUDIT/'support-correction.json')})
write(AUDIT/'resource-checks.json',{'status':'PASS OFFLINE ONLY','meshes':5,'material_definitions_exactly_match_accepted_values':17,'mesh_material_schema':'Not present in pinned SDK; no schema pass claimed','byte_identical_dds_textures':27,'donor_binaries_exact':2,'assembled_triangles':count,'meshpoint_transform_arrays_exact':True,'runtime':'NOT RUN'})
print('PASS final higher-detail handoff',count,'triangles;',len(meshes),'meshes;',len(materials),'materials;',len(textures),'textures')
