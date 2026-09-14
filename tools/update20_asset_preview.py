"""Offline source intake/geometry visualization; never installs or edits originals."""
import sys,json
from pathlib import Path
import numpy as np
from PIL import Image,ImageDraw
sys.path.insert(0,'tools');from common import Gltf
out=Path('audit/update20-assets'); root=Path('assets/derived/update20-intake')
models=[]
for f in ['1_part31behemoth.npz','2_gathering-storm-3d-print-whole.npz','3_unnipbmv2.npz','4_UNN_Murphy_Class_Destroyer.npz']:
 t=np.load(root/f)['tri'];models.append((f,t))
p=Path('/run/media/haker/NVME 2/expanse-extracted/UNN-Urshanabi/sdk-candidate/unn_urshanabi_wreck.gltf');g=Gltf(p);t=[]
for ni,n in enumerate(g.g['nodes']):
 if 'mesh' in n:
  for pr in g.g['meshes'][n['mesh']]['primitives']:t.append(g.positions(ni,pr)[g.accessor(pr['indices']).reshape(-1,3)])
models.append(('Urshanabi wreck assembly',np.concatenate(t)))
models.append(('UN One parts at exported coordinates',np.concatenate([np.load(p)['tri'] for p in root.glob('0_*.npz') if 'Stand' not in p.name])))
canvas=Image.new('RGB',(1500,1500),(16,21,29));d=ImageDraw.Draw(canvas)
for index,(name,t) in enumerate(models):
 dims=np.ptp(t.reshape(-1,3),axis=0);order=np.argsort(dims);t=t[:,:,order];t-= (t.min((0,1))+t.max((0,1)))/2
 B=np.array([[.2,.1,1],[.5,1,-.2],[1,-.5,-.15]]);q=t@B.T;coords=q[:,:,:2];coords[:,:,1]*=-1;coords*=min(680/np.ptp(coords[:,:,0]),650/np.ptp(coords[:,:,1]));coords-= (coords.min((0,1))+coords.max((0,1)))/2;coords+=[375+750*(index%2),390+500*(index//2)];coords[:,:,1]= (coords[:,:,1]-(390+500*(index//2)))*.61+(260+500*(index//2))
 ns=np.cross(t[:,1]-t[:,0],t[:,2]-t[:,0]);ns/=np.maximum(np.linalg.norm(ns,axis=1,keepdims=True),1e-12);shade=.3+.7*np.abs(ns@np.array([.3,.8,.5]));c=np.clip(shade[:,None]*np.array([165,180,195]),0,255).astype('uint8')
 for i in np.argsort(q[:,:,2].mean(1)):d.polygon([tuple(v) for v in coords[i]],fill=tuple(c[i]))
 d.text((20+750*(index%2),20+500*(index//2)),name,fill='white')
canvas.save(out/'geometry-intake-contact-sheet.png')
