"""Freeze final handoff hashes and verify read-only dependencies are preserved."""
from common import *
import hashlib,subprocess
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest();audit=ROOT/'audit/geometry03-b';previous=read(ROOT/'audit/polish-b/source-preservation.json');checks=[]
for r in previous['frozen_dependency_hashes']:
 actual=sha(r['path']);assert actual==r['sha256'],r['path'];checks.append({'path':r['path'],'sha256':actual,'preserved':True})
hero=read(audit/'hero-asset-audit.json')
for p,h in hero['master_files'].items():assert sha(p)==h;checks.append({'path':p,'sha256':h,'preserved':True})
for p in [Path('/home/haker/Downloads/Rocinante_(The_Expanse).zip'),ROOT/'assets/derived/geometry03-b/hero-original/Rocinante_(The_Expanse).zip']:
 assert sha(p)==hero['archive_sha256'];checks.append({'path':str(p),'sha256':sha(p),'preserved':True})
for r in read(ROOT/'audit/polish-b/output-validation.json')['outputs'].values():
 assert sha(r['mesh'])==r['sha256'];checks.append({'path':r['mesh'],'sha256':r['sha256'],'preserved':True})
files=list((ROOT/'tools').glob('geometry03*.py'))
for variant in ['corvette','hero','hero-armed']:
 files.extend(p for p in (ROOT/'build/geometry03-b'/variant/'game').rglob('*') if p.is_file())
 files.extend(p for p in (ROOT/'assets/derived/geometry03-b'/variant).rglob('*') if p.is_file())
files.extend(p for p in audit.iterdir() if p.is_file() and p.name!='final-provenance.json')
record={'worker':'B','worker_head':subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),'status':'UNCOMMITTED LOCAL SOURCE AND GENERATED CANDIDATES; NO RUNTIME TEST CLAIM','preserved_inputs':checks,'files':{str(p):sha(p) for p in sorted(set(files))}}
write(audit/'final-provenance.json',record);print(json.dumps({'preserved_inputs':len(checks),'frozen_files':len(files),'corvette_hull':sha(ROOT/'build/geometry03-b/corvette/game/meshes/expanse03_hull.mesh'),'armed_hero':sha(ROOT/'build/geometry03-b/hero-armed/game/meshes/expanse03_hero_armed.mesh')}))
