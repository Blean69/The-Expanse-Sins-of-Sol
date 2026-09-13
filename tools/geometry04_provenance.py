from common import *
import hashlib,subprocess
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest();audit=ROOT/'audit/geometry04-b';previous=read(ROOT/'audit/geometry03-b/final-provenance.json');preserved=[]
for p,h in previous['files'].items():assert sha(p)==h;preserved.append({'path':p,'sha256':h})
for r in previous['preserved_inputs']:assert sha(r['path'])==r['sha256'];preserved.append({'path':r['path'],'sha256':r['sha256']})
files=list((ROOT/'tools').glob('geometry04*.py'))
for directory in [ROOT/'assets/derived/geometry04-b',ROOT/'build/geometry04-b/game',audit]:files.extend(p for p in directory.rglob('*') if p.is_file() and p.name!='final-provenance.json')
write(audit/'final-provenance.json',{'worker':'B','source_head':subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),'source_status':'UNCOMMITTED ISOLATED WORKTREE; exact script hashes below','preserved_inputs':preserved,'files':{str(p):sha(p) for p in sorted(set(files))},'runtime':'NOT RUN'});print(json.dumps({'preserved_files':len(preserved),'frozen_files':len(files),'hull_sha256':sha(ROOT/'build/geometry04-b/game/meshes/expanse04_hero_hull.mesh')}))
