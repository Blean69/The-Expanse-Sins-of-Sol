"""Independent archived 0.13 PDC ray reproduction; no package edits."""
from pathlib import Path
import json,hashlib,numpy as np
from update14_pdc_arcs import Rays,sample

ROOT=Path(__file__).resolve().parents[1]
MAIN=Path('/run/media/haker/NVME 2/expanse-mod')
SOURCE=Path('/run/media/haker/NVME 2/expanse-workers/visual13-hulls/build/update13-b')
BASE=MAIN/'build/experiments/expanse_update13'
report={'status':'OFFLINE REPRODUCTION: old arcs intersect own hull','entries':[],'runtime':'NOT RUN'}
for kind in ['raptor','pella']:
    name='expanse12_'+kind;mesh=BASE/'meshes'/(name+'_hull.mesh');worker_mesh=SOURCE/kind/'game/meshes'/mesh.name
    assert mesh.read_bytes()==worker_mesh.read_bytes()
    jp=SOURCE/kind/'repaired-json'/(name+'_hull.mesh_json');j=json.loads(jp.read_text())
    vertices=np.array([v['p']for v in j['non_skinned_vertices']]);tri=vertices[np.array(j['vertex_indices']).reshape(-1,3)]
    ray=Rays(tri,ROOT/'build/update14-arcs');u=json.loads((BASE/'entities'/(name+'.unit')).read_text());results=[]
    for mount in u['weapons']['weapons']:
        if '_pdc_' not in mount['weapon']:continue
        w=json.loads((BASE/'entities'/(mount['weapon']+'.weapon')).read_text());a,ex,ar=sample(ray,mount,w['turret'],np.arange(-180,181,2.),np.arange(-85,6,2.),0.)
        b,bex,br=sample(ray,mount,w['turret'],np.arange(-180,181,2.),np.arange(-85,6,2.),7.5)
        results.append({'weapon':mount['weapon'],'actual_muzzle_center_direction_blocked_poses':int(a.sum()),'including_original_tolerance_blocked_poses':int(b.sum()),'poses':int(a.size),'total_rays':ar+br,'example_centerline':ex,'example_tolerance':bex})
    ray.close();report['entries'].append({'identity':name,'mesh_sha256':hashlib.sha256(mesh.read_bytes()).hexdigest(),'repaired_json_sha256':hashlib.sha256(jp.read_bytes()).hexdigest(),'triangle_count':len(tri),'mounts':results})
    print(name,'centerline',sum(x['actual_muzzle_center_direction_blocked_poses']for x in results),'tolerance',sum(x['including_original_tolerance_blocked_poses']for x in results),flush=True)
(ROOT/'audit/update14-arcs/baseline-reproduction.json').write_text(json.dumps(report,indent=2)+'\n')
