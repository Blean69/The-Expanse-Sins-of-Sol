"""Validate isolated authored torpedo and preserved archive; no installed writes."""
import json,subprocess
import numpy as np
from amun05_intake import ROOT,ASSETS,AUDIT,BUILD,sha,write,geometry
from common import Gltf

def main():
 for p in [AUDIT/'source-hashes.json',AUDIT/'torpedo-extraction.json']:
  if not p.is_file():raise FileNotFoundError('Required intake dependency missing; checks NOT RUN: '+str(p))
 lock=json.loads((AUDIT/'source-hashes.json').read_text());meta=json.loads((AUDIT/'torpedo-extraction.json').read_text());master=ASSETS/'master'
 assert sha(lock['supplied_archive'])==lock['archive_sha256']==sha(lock['archive_copy'])
 assert lock['master_hashes']=={str(p.relative_to(master)):sha(p)for p in sorted(master.rglob('*'))if p.is_file()}
 assert all(sha(p)==h for p,h in meta['dependencies'].items());assert sha(meta['installed_size_reference']['path'])==meta['installed_size_reference']['sha256']
 original=Gltf(next(master.glob('*.gltf')));isolated=Gltf(meta['output_scene']);src=list(geometry(original,meta['selected_root']));out=list(geometry(isolated));assert len(src)==len(out)==2;tri=0;positions=[];attributes=[]
 for a,b in zip(src,out):
  _,_,sp,sv,si=a;_,_,op,ov,oi=b;assert np.array_equal(si,oi);assert np.allclose(ov,(sv-meta['source_local_center'])*meta['uniform_factor'],atol=1e-6)
  for key in sp['attributes']:
   if key=='POSITION':continue
   before=original.accessor(sp['attributes'][key]);after=isolated.accessor(op['attributes'][key]);assert np.array_equal(before,after),'Changed source attribute: '+key
   if key=='NORMAL':assert np.allclose(np.linalg.norm(after,axis=1),1,atol=1e-4)
  assert np.isfinite(ov).all()and oi.min()>=0 and oi.max()<len(ov);tri+=len(oi);positions.append(ov);attributes.append(list(op['attributes']))
 v=np.concatenate(positions);assert tri==1600;assert np.allclose(np.ptp(v,axis=0),meta['target_dimensions'],atol=1e-6);assert np.allclose((v.min(0)+v.max(0))/2,0,atol=1e-6);assert np.isclose(np.linalg.norm(v,axis=1).max(),meta['candidate_centered_vertex_radius'])
 assert all((isolated.path.parent/im['uri']).is_file()for im in isolated.g['images']);assert not list((ASSETS/'torpedo-editable').rglob('*.unit'))and not list((ASSETS/'torpedo-editable').rglob('*.unit_skin'))
 result={'status':'PASS','original_archive_and_master':'PASS','isolated_torpedo_dependencies':'PASS','installed_size_reference_unchanged':'PASS','exact_original_indices_and_nonposition_attributes':'PASS','position_uniform_scale_and_center':'PASS','finite_normals_indices':'PASS','triangles':tri,'dimensions':np.ptp(v,axis=0).tolist(),'source_attribute_sets':attributes,'candidate_vertex_radius':meta['candidate_centered_vertex_radius'],'stock_sphere_radius_delta':meta['stock_sphere_radius_delta'],'stock_sphere_fit':'Exceeds by about0.01308; main integration decision pending','projectile_entity_files_modified':False,'runtime':'NOT RUN','game_compilation':'NOT RUN'};write(AUDIT/'derivative-validation.json',result)
 manifest={'worker_checkout_head':subprocess.check_output(['git','-C',str(ROOT),'rev-parse','HEAD'],text=True).strip(),'source_tools':{str(p.relative_to(ROOT)):sha(p)for p in sorted((ROOT/'tools').glob('amun05*.py'))},'unchanged_helpers':{str(ROOT/'tools'/n):sha(ROOT/'tools'/n)for n in ['common.py','polish_ui.py']},'assets':{str(p.relative_to(ASSETS)):sha(p)for p in sorted(ASSETS.rglob('*'))if p.is_file()},'audits':{str(p.relative_to(AUDIT)):sha(p)for p in sorted(AUDIT.rglob('*'))if p.is_file()},'runtime':'NOT RUN','no_game_package':True};write(BUILD/'source-and-output-hashes.json',manifest);print(json.dumps(result))
if __name__=='__main__':main()
