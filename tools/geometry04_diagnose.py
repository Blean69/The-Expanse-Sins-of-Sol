"""Read-only 0.3 source-pose and topology diagnostic; no rebuilding."""
from common import *
from scipy.spatial.transform import Rotation,Slerp
import copy
out=ROOT/'audit/geometry04-b';out.mkdir(exist_ok=True);a=Gltf(ROOT/'assets/derived/geometry03-b/hero-master/Rocinante_(The_Expanse).gltf');g=a.g;an=g['animations'][0];tracks={}
for ch in an['channels']:
 ss=an['samplers'][ch['sampler']];tracks.setdefault(ch['target']['node'],{})[ch['target']['path']]=(a.accessor(ss['input']).flatten(),a.accessor(ss['output']))
def local(ni,time):
 n=g['nodes'][ni];vals={k:copy.deepcopy(v) for k,v in n.items() if k in ['rotation','translation','scale']}
 for path,(ts,vs) in tracks.get(ni,{}).items():
  vals[path]=Slerp(ts,Rotation.from_quat(vs))([np.clip(time,ts[0],ts[-1])]).as_quat()[0] if path=='rotation' else np.array([np.interp(time,ts,vs[:,i]) for i in range(vs.shape[1])])
 if 'matrix' in n and not tracks.get(ni):return np.array(n['matrix']).reshape(4,4).T
 M=np.eye(4);M[:3,:3]=Rotation.from_quat(vals.get('rotation',[0,0,0,1])).as_matrix()@np.diag(vals.get('scale',[1,1,1]));M[:3,3]=vals.get('translation',[0,0,0]);return M
records=[]
for ni in g['nodes'][1]['children']:
 d=np.linalg.inv(local(2,16.625))@local(ni,16.625)@np.linalg.inv(np.linalg.inv(local(2,0))@local(ni,0));records.append({'node':ni,'name':g['nodes'][ni]['name'],'relative_translation':d[:3,3].tolist(),'relative_rotation_degrees':float(np.degrees(Rotation.from_matrix(d[:3,:3]).magnitude())),'relative_scale':np.linalg.svd(d[:3,:3])[1].tolist()})
write(out/'source-pose.json',{'root_nodes':g['nodes'][:2],'hull_relative_motion':records,'prior_normalization':read(ROOT/'audit/geometry03-b/hero-mount-metadata.json')['normalization']})
for r in records:
 if r['node']<111 and (r['relative_rotation_degrees']>.001 or np.linalg.norm(r['relative_translation'])>.00001):print(r)
# Check whether optimized triangles have newly unmatched geometric edges.
def topology(pos,idx):
 p=np.round(pos,6);_,remap=np.unique(p,axis=0,return_inverse=True);tri=remap[idx];edge=np.sort(np.concatenate([tri[:,[0,1]],tri[:,[1,2]],tri[:,[2,0]]]),axis=1);u,c=np.unique(edge,axis=0,return_counts=True);return {'triangles':len(idx),'boundary_edges':int(sum(c==1)),'nonmanifold_edges':int(sum(c>2))}
source=[]
for ni,n in enumerate(g['nodes']):
 if 'mesh' not in n or ni in [67,68]:continue
 for p in g['meshes'][n['mesh']]['primitives']:
  source.append({'node':ni,'parent':g['nodes'][a.parents[ni]]['name'],**topology(a.accessor(p['attributes']['POSITION']),a.accessor(p['indices']).reshape(-1,3))})
write(out/'source-topology.json',source)
print('Source pose/topology recorded')
