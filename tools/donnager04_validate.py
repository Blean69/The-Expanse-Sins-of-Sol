"""Read-only derivative checks; writes only new worker audit/build results."""
from pathlib import Path
import hashlib,json,subprocess
import numpy as np
from common import Gltf
from donnager04_intake import ROOT,ASSETS,AUDIT,BUILD,meshes,sha,write

def main():
 required=[AUDIT/'preserved-source-hashes.json',AUDIT/'scale-and-pdc-donor.json',AUDIT/'railgun-geometry.json']
 for p in required:
  if not p.is_file():raise FileNotFoundError('Required intake output missing; dependency checks NOT RUN: '+str(p))
 lock,scaling,rails=[json.loads(p.read_text())for p in required];report={}
 assert sha(lock['supplied_archive'])==lock['archive_sha256']==sha(lock['preserved_archive'])
 assert lock['master_files']=={str(p.relative_to(ASSETS/'master')):sha(p)for p in sorted((ASSETS/'master').rglob('*'))if p.is_file()}
 for p,h in scaling['source_dependencies'].items():assert sha(p)==h,'Changed donor dependency: '+p
 for f in sorted(ASSETS.rglob('*.gltf')):
  g=Gltf(f);tri=0;vs=[]
  for i,pi,p,v,ix in meshes(g):
   assert np.isfinite(v).all()and ix.min()>=0 and ix.max()<len(v);tri+=len(ix);vs.append(v);normals=g.accessor(p['attributes']['NORMAL']);assert np.allclose(np.linalg.norm(normals,axis=1),1,atol=1e-4)
  allv=np.concatenate(vs);assert all((f.parent/im['uri']).is_file()for im in g.g.get('images',[]))
  if 'provisional'in f.name:assert np.isclose(np.ptp(allv,axis=0)[2],scaling['provisional_lore_scale']['Donnager_game_length'])
  if f.parent.name=='rail-assembly-preview':
   side=next(x for x in rails['sides']if x['editable_candidate']==str(f));assert tri==side['triangles'];assert np.allclose(allv.min(0),side['preview_bounds']['min'],atol=1e-5);assert np.allclose(allv.max(0),side['preview_bounds']['max'],atol=1e-5)
  else:assert tri==1804024
  report[str(f.relative_to(ASSETS))]={'triangles':tri,'dimensions':np.ptp(allv,axis=0).tolist(),'finite_positions':'PASS','indices':'PASS','unit_local_normals':'PASS','buffer_and_image_references':'PASS','sha256':sha(f)}
 write(AUDIT/'derivative-validation.json',{'status':'PASS','archive_and_master_preserved':'PASS','donor_dependencies_unchanged':'PASS','assets':report,'runtime':'NOT RUN','package_export':'NOT RUN; candidates deliberately incomplete for game export'})
 githead=subprocess.check_output(['git','-C',str(ROOT),'rev-parse','HEAD'],text=True).strip()
 manifest={'worker_checkout_head':githead,'source_tools':{str(p.relative_to(ROOT)):sha(p)for p in sorted((ROOT/'tools').glob('donnager04*.py'))},'unchanged_helper':{str(ROOT/'tools/common.py'):sha(ROOT/'tools/common.py')},'generated_asset_hashes':{str(p.relative_to(ASSETS)):sha(p)for p in sorted(ASSETS.rglob('*'))if p.is_file()},'audit_hashes':{str(p.relative_to(AUDIT)):sha(p)for p in sorted(AUDIT.rglob('*'))if p.is_file()},'installed_SDK_README_sha256':sha('/run/media/haker/NVME 2/SteamLibrary/steamapps/common/Sins of a Solar Empire II - Mod Tools/README.md'),'note':'Ignored intake/preparation artifacts only; no package or publishing. Root manifest is outside its own hash set.'}
 write(BUILD/'source-and-output-hashes.json',manifest);print(json.dumps({'status':'PASS','scenes_checked':len(report),'archive_master_donor_hashes':'PASS','runtime':'NOT RUN'}))
if __name__=='__main__':main()
