"""Create six editable yaw/pitch rig candidates; not installed gameplay assets."""
from common import *
import copy

a=Gltf(ROOT/'assets/derived/optimized-source/scene.gltf');g=a.g;trans=read(ROOT/'audit/derivative-transform.json');T=np.array(trans['matrix']).reshape(4,4).T
spheres=[445,493,541,589,637,685];barrels=[439,487,535,583,631,679]
ups=[[-1,0,0],[0,1,0],[0,-1,0],[1,0,0],[1,0,0],[-1,0,0]]
rigs=[]
for ri,(si,bi,up) in enumerate(zip(spheres,barrels,ups)):
    pivot=a.world[si][:3,3];node=g['nodes'][bi];p=g['meshes'][node['mesh']]['primitives'][0];v=a.positions(bi,p)
    forward=np.array([0.,0.,-1. if ri in [1,2] else 1.]);projection=v@forward;tip=v[projection>projection.max()-.1].mean(0)
    up=np.array(up,dtype=float);right=np.cross(up,forward);B=np.column_stack([right,up,forward]);world_pivot=pivot*T[0,0]+T[:3,3]
    local=np.eye(4);local[:3,:3]=B.T;local[:3,3]=-B.T@world_pivot
    rigs.append(dict(index=ri,sphere_source_node=si,barrel_source_node=bi,pivot=world_pivot.tolist(),source_pivot=pivot.tolist(),forward=forward.tolist(),up=up.tolist(),muzzle_local=((tip-pivot)*T[0,0]@B).tolist(),parts={'base':[],'barrel':[]},local_transform=local))
for i,n in enumerate(g['nodes']):
    if 'mesh' not in n or not n.get('name','').startswith('pdc_gun_'):continue
    v=np.concatenate([a.positions(i,p) for p in g['meshes'][n['mesh']]['primitives']]);mid=(v.min(0)+v.max(0))/2
    ri=int(np.argmin([np.linalg.norm(mid-np.array(r['source_pivot'])) for r in rigs]))
    kind='base' if any(w in n['name'] for w in ['swivel','sphere_holder','base_details']) else 'barrel'
    rigs[ri]['parts'][kind].append(i)
out=ROOT/'assets/derived/pdc-rigs';out.mkdir(parents=True,exist_ok=True)
for rig in rigs:
    for kind,ids in rig['parts'].items():
        assert ids
        d=copy.deepcopy(g);d['nodes']=[];d['scenes']=[{'nodes':[]}];d['scene']=0
        for ni in ids:
            n=copy.deepcopy(g['nodes'][ni]);n.pop('children',None)
            for k in ['translation','rotation','scale','matrix']:n.pop(k,None)
            n['matrix']=(rig['local_transform']@T@a.world[ni]).T.flatten().tolist()
            d['scenes'][0]['nodes'].append(len(d['nodes']));d['nodes'].append(n)
        d['buffers'][0]['uri']='../optimized-source/scene.bin'
        for im in d['images']:im['uri']='../optimized-source/'+im['uri']
        write(out/f'mcrn_pdc_{rig["index"]}_{kind}.gltf',d)
    del rig['local_transform']
write(ROOT/'audit/pdc-rig-candidates.json',{'status':'EDITABLE CANDIDATES; not runtime-tested or installed','pivot_method':'named sphere origins; verify yaw/pitch mechanical centers in editor','partition_method':'nearest PDC sphere for all pdc_gun_* parts; swivel/sphere_holder/base_details as yaw; others pitch; bay doors stay in hull','rigs':rigs,'caveats':['These glTF files use game-coordinate local frames, and still need compiler handedness compensation as in prepare_model.py.','Before mounting these rigs, remove exactly the listed moving nodes from a separate combat hull to prevent static duplicates.','Do not add 12 firing weapons: six physical assemblies each get one biaxial weapon entry.','Six barrel clusters are multi-barrel visual geometry; one cluster muzzle is estimated, not six independent budgets.']})
print('Prepared 12 editable glTF parts for six PDC rig candidates.')
