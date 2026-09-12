"""Reproduce intake facts before conversion; no mesh edits."""
from common import *
from PIL import Image
import hashlib

a=Gltf(ROOT/'assets/source/tachi/scene.gltf'); g=a.g; rows=[]; allp=[]
for i,n in enumerate(g['nodes']):
    row=dict(index=i,name=n.get('name'),parent=a.parents.get(i),children=n.get('children',[]),active=i in a.world,mesh=n.get('mesh'),local_matrix=n.get('matrix'),translation=n.get('translation'),rotation=n.get('rotation'),scale=n.get('scale'))
    if i in a.world: row['world_origin']=a.world[i][:3,3].tolist()
    if 'mesh' in n and i in a.world:
        prims=g['meshes'][n['mesh']]['primitives'];p=np.concatenate([a.positions(i,x) for x in prims]);allp.append(p)
        row.update(triangles=sum(len(a.accessor(x['indices']))//3 for x in prims),materials=[g['materials'][x['material']]['name'] for x in prims],bounds_min=p.min(0).tolist(),bounds_max=p.max(0).tolist(),has_tangents=all('TANGENT' in x['attributes'] for x in prims))
    rows.append(row)
p=np.concatenate(allp); textures=[]
for im in g['images']:
    f=a.path.parent/im['uri']
    with Image.open(f) as img: textures.append(dict(path=im['uri'],size=list(img.size),mode=img.mode,bytes=f.stat().st_size))
data=dict(asset=g['asset'],node_count=len(g['nodes']),mesh_count=len(g['meshes']),triangles=sum(r.get('triangles',0) for r in rows),materials=g['materials'],textures=textures,animations=len(g.get('animations',[])),skins=len(g.get('skins',[])),bounds_min=p.min(0).tolist(),bounds_max=p.max(0).tolist(),dimensions=np.ptp(p,axis=0).tolist(),nodes=rows)
write(ROOT/'audit/asset-audit.json',data)
master=ROOT/'assets/original/mcrn_tachi_expanse_tv_show.zip'
write(ROOT/'audit/source-checksums.json',{'archive_sha256':hashlib.sha256(master.read_bytes()).hexdigest(),'files':{str(f.relative_to(a.path.parent)):hashlib.sha256(f.read_bytes()).hexdigest() for f in sorted(a.path.parent.rglob('*')) if f.is_file()}})
mesh=read_mesh(GAME/'meshes/trader_light_frigate.mesh');write(ROOT/'audit/cobalt-mesh.json',mesh)
print(json.dumps({k:v for k,v in data.items() if k not in ['nodes','materials','asset']},indent=2));print('Cobalt mesh',mesh)
