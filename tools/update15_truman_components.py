from pathlib import Path
import numpy as np,json
from scipy.sparse import coo_matrix
from scipy.sparse.csgraph import connected_components
from common import write
from polish_ui import render
from PIL import Image
R=Path(__file__).resolve().parents[1];D=R/'assets/derived/update15-truman';A=R/'audit/update15-truman';z=np.load(D/'source-parts.npz');raw=np.concatenate([z[f'{i}_v']for i in range(7)]);center=(raw.min(0)+raw.max(0))/2;scale=(376*105/46)/np.ptp(raw[:,2]);M=np.diag([-1,1,-1]);parts=[];start=0;allidx=[]
for i in range(7):
 p={k:z[f'{i}_{k}'].copy()for k in ['v','n','t','uv','i']};p['v']=(p['v']-center)@M*scale;p['n']=p['n']@M;p['t'][:,:3]=p['t'][:,:3]@M;parts.append(p);allidx.append(p['i']+start);start+=len(p['v'])
v=np.concatenate([p['v']for p in parts]);idx=np.concatenate(allidx);pos,ix=np.unique(np.round(v,4),axis=0,return_inverse=True);ii=ix[idx];edges=np.concatenate([ii[:,[0,1]],ii[:,[1,2]],ii[:,[2,0]]]);n,lab=connected_components(coo_matrix((np.ones(len(edges)),(edges[:,0],edges[:,1])),shape=(len(pos),len(pos))),directed=False);faces=lab[ii[:,0]];rows=[]
for k in range(n):
 q=v[idx[faces==k]];rows.append({'component':k,'triangles':len(q),'bounds':[q.min((0,1)).tolist(),q.max((0,1)).tolist()],'center':q.mean((0,1)).tolist()})
write(A/'components.json',{'center_source':center.tolist(),'scale':scale,'transform':M.tolist(),'components':sorted(rows,key=lambda x:-x['triangles'])});np.savez(D/'normalized.npz',v=v,n=np.concatenate([p['n']for p in parts]),t=np.concatenate([p['t']for p in parts]),uv=np.concatenate([p['uv']for p in parts]),i=idx,component=faces)
tex=np.array(Image.open(R/'assets/original/update15-truman/master/textures/material_baseColor.jpeg').convert('RGBA').resize((2048,2048)));meshes=[(p['v'][p['i']],p['uv'][p['i']],tex,[1,1,1,1],'OPAQUE')for p in parts]
for name,basis in [('side',[[0,0,1],[0,1,0],[-1,0,0]]),('top',[[0,0,1],[1,0,0],[0,1,0]]),('oblique',[[.36,0,.933],[.4,.903,-.154],[-.842,.429,.325]])]:render(meshes,(1800,900),np.array(basis)).save(A/(name+'.png'))
print(n, sum(r['triangles']for r in rows));print(json.dumps(sorted(rows,key=lambda x:-x['triangles'])[:15]))
