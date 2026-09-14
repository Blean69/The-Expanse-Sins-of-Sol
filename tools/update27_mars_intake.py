"""Reproducible local intake of user-supplied fan assets. Does not modify originals."""
from update27_mars_assets import *
import zipfile
from scipy.sparse.csgraph import connected_components
out=OUT/'source';out.mkdir(exist_ok=True)
p=Path('/home/haker/Downloads/mcrn_hephaestus-class_destroyer_printable.zip')
with zipfile.ZipFile(p)as z:
 for n in ['scene.gltf','scene.bin','license.txt']:(out/n).write_bytes(z.read(n))
g=Gltf(out/'scene.gltf');parts=[]
for j,n in enumerate(g.g['nodes']):
 if 'mesh'in n:
  for pr in g.g['meshes'][n['mesh']]['primitives']:parts.append(g.positions(j,pr)[g.accessor(pr['indices']).reshape(-1,3)])
t=np.concatenate(parts);v,inv=np.unique(np.round(t,6).reshape(-1,3),axis=0,return_inverse=True);ii=inv.reshape(-1,3);e=np.concatenate([ii[:,[0,1]],ii[:,[1,2]],ii[:,[0,2]]]);count,lab=connected_components(coo_matrix((np.ones(len(e)),(e[:,0],e[:,1])),shape=(len(v),len(v))),directed=False);np.savez_compressed(out/'hephaestus-components.npz',v=v,i=ii,labels=lab[ii[:,0]])
report={'hephaestus':{'source':str(p),'sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'triangles':len(t),'connected_components':count,'creator':'Adyne','license':'CC-BY-4.0','primary_source':'https://sketchfab.com/3d-models/mcrn-hephaestus-class-destroyer-printable-8774ee0a3a8e41a39c677dbeb6d979bc','canon_status':'Creator explicitly identifies fanart, not canon.'},'laconia':{'source':'/home/haker/Downloads/LaconiaFrigate.stl','sha256':hashlib.sha256(Path('/home/haker/Downloads/LaconiaFrigate.stl').read_bytes()).hexdigest(),'triangles':4294,'creator':'Not embedded in supplied STL','canon_status':'Unnamed fan frigate; no unsupported canonical identity assigned.'}}
write(AUD/'source-intake.json',report);print('Hephaestus',len(t),'triangles',count,'components')
