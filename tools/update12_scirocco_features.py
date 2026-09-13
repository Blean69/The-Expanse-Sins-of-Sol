"""Measured component feature views, not authored semantic labels."""
from pathlib import Path
import sys,json,numpy as np
sys.path.append('/run/media/haker/NVME 2/expanse-mod/tools')
from polish_ui import render,write
from scipy.sparse import coo_matrix
from scipy.sparse.csgraph import connected_components
R=Path(__file__).resolve().parents[1];O=R/'assets/derived/update12-b';A=R/'audit/update12-b';z=np.load(O/'source-welded.npz');v=z['v'];ii=z['i'];edges=np.concatenate([ii[:,[0,1]],ii[:,[1,2]],ii[:,[2,0]]]);_,lab=connected_components(coo_matrix((np.ones(len(edges)),(edges[:,0],edges[:,1])),shape=(len(v),len(v))),directed=False);tlab=lab[ii[:,0]];tri=v[ii];cent=tri.mean(1);np.savez(O/'source-components.npz',v=v,i=ii,triangle_components=tlab)
tex=np.full((1,1,4),255,np.uint8)
for name,lo,hi in [('side_assembly',[-120,-135,15],[25,-40,100]),('forward_hardware',[250,-90,-60],[310,90,60])]:
 mask=np.all((cent>lo)&(cent<hi),axis=1);mesh=[]
 for component in sorted(set(tlab[mask])):
  q=tri[mask&(tlab==component)];color=[.45,.5,.55,1] if component==89 else [[.9,.2,.1,1],[.2,.8,.2,1],[.2,.3,.9,1],[.8,.65,.2,1],[.6,.25,.8,1]][component%5];mesh.append((q,np.zeros((len(q),3,2)),tex,color,'OPAQUE'))
 for view,basis in [('top',[[1,0,0],[0,1,0],[0,0,1]]),('side',[[1,0,0],[0,0,1],[0,-1,0]]),('front',[[0,1,0],[0,0,1],[1,0,0]])]:render(mesh,(1200,800),np.array(basis),.8).save(A/(name+'-'+view+'.png'))
 print(name,sorted(set(tlab[mask])),flush=True)
