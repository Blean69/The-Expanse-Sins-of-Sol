from amun06_geometry_common import *
from collections import defaultdict
rows=[q for i in descendants(3) for q in arrays(i)];v=np.concatenate([r['v'] for r in rows]);idx=[];off=0
for r in rows:idx.extend(r['i']+off);off+=len(r['v'])
idx=np.array(idx);uv,remap=np.unique(np.round(v,5),axis=0,return_inverse=True);ii=remap[idx];parent=np.arange(len(uv))
def find(x):
 while parent[x]!=x:parent[x]=parent[parent[x]];x=parent[x]
 return x
for tri in ii:
 root=find(tri[0])
 for x in tri[1:]:parent[find(x)]=root
buckets=defaultdict(list)
for fi,tri in enumerate(ii):buckets[find(tri[0])].append(fi)
records=[]
for ids in buckets.values():
 vv=v[idx[ids]].reshape(-1,3);lo=vv.min(0);hi=vv.max(0);records.append({'triangles':len(ids),'min':lo.tolist(),'max':hi.tolist(),'center':((lo+hi)/2).tolist(),'indices':ids})
records.sort(key=lambda r:r['triangles'],reverse=True);write(AUDIT/'hull-components.json',records)
for i,r in enumerate(records[:35]):print(i,r['triangles'],np.round(r['min'],3),np.round(r['max'],3))
