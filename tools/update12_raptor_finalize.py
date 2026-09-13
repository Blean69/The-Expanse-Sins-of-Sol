"""Small final asset contract check; no game or installed package writes."""
from pathlib import Path
import hashlib,json,struct,sys
sys.path.insert(0,'/run/media/haker/NVME 2/expanse-mod/tools')
from polish_ui import write
ROOT=Path(__file__).resolve().parents[1]
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
rows=[]
for variant in ['raptor','pella']:
 aud=ROOT/'audit/update12-a'/variant;build=ROOT/'build/update12-a'/variant;game=build/'game';meta=json.loads((aud/'integration-spec.json').read_text());mesh=json.loads((aud/'mesh-validation.json').read_text());mount=json.loads((aud/'mount-validation.json').read_text());ui=json.loads((aud/'ui-validation.json').read_text());assert ui['status']=='PASS' and mount['sampled_obstructions']==0
 expected={meta['hull_mesh']:meta['counts']['hull'],f'expanse12_{variant}_pdc_base':138,f'expanse12_{variant}_pdc_barrel':539}
 for record in mesh['meshes']:
  p=game/'meshes'/(record['mesh']+'.mesh');assert sha(p)==record['sha256'];assert record['triangles']==expected[record['mesh']];assert record['tangent_fallbacks']==0 and record['opposed_winding_triangles']==0 and record['only_tangent_bytes_changed'] and record['official_trailer_preserved']
 materials=[];textures=[]
 for p in (game/'mesh_materials').glob('*.mesh_material'):
  d=json.loads(p.read_text());assert set(d)=={'version','base_color_texture','occlusion_roughness_metallic_texture','normal_texture','mask_texture','emissive_factor'}
  for k,v in d.items():
   if k.endswith('_texture'):assert (game/'textures'/(v+'.dds')).is_file(),(p,k,v)
  materials.append(p.name)
 for p in (game/'textures').glob('*.dds'):
  b=p.read_bytes();assert b[:4]==b'DDS ';h,w=struct.unpack_from('<II',b,12);assert w%4==0 and h%4==0,(p,w,h);textures.append({'name':p.name,'size':[w,h],'sha256':sha(p)})
 for rec in ui['png_checks']:assert sha(Path(rec['file']))==rec['sha256']
 meta['status']='PASS OFFLINE MESH, MATERIAL, MOUNT AND UI CHECKS';meta['files']={str(p.relative_to(game)):sha(p)for p in game.rglob('*')if p.is_file()};meta['ui_files']={str(p.relative_to(build/'ui/generated')):sha(p)for p in (build/'ui/generated').rglob('*')if p.is_file()};meta['ui_game_directory']=str(build/'ui/generated');meta['runtime']='NOT RUN';write(aud/'integration-spec.json',meta)
 material_report=json.loads((aud/'material-validation.json').read_text());material_report['textures']={r['name']:r['sha256']for r in textures};material_report['dimensions_checked_for_block_compression']=textures;material_report['authored']='Procedural gray/orange for Raptor; procedural silver for Pella plus reference-guided Free Navy emblem paint. Source STL contains no authored materials.';write(aud/'material-validation.json',material_report)
 rows.append({'variant':variant,'status':'PASS OFFLINE','assembled_triangles':meta['assembled_triangle_total'],'game_files':len(meta['files']),'ui_files':len(meta['ui_files']),'material_references':len(materials),'textures':textures,'integration_spec_sha256':sha(aud/'integration-spec.json')})
write(ROOT/'audit/update12-a/final-validation.json',{'status':'PASS OFFLINE','variants':rows,'runtime':'NOT RUN'});print(json.dumps(rows,indent=2))
