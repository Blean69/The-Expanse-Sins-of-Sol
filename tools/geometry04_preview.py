from common import *
from PIL import Image,ImageDraw
out=ROOT/'audit/geometry04-b';p=np.load(ROOT/'assets/derived/geometry04-b/parts.npz');records=read(out/'parts.json');target=np.array(read(out/'normalization.json')['target_center']);tris=[];norm=[];mats=[]
for r in records:
 k=r['key'];idx=p[k+'_i'];tris.extend(p[k+'_v'][idx]);norm.extend(p[k+'_n'][idx].mean(1));mats.extend([r['material']]*len(idx))
tri=np.array(tris);nn=np.array(norm);mi=np.array(mats);nn/=np.maximum(np.linalg.norm(nn,axis=1)[:,None],1e-9);camera=np.array([1.,.35,.12]);camera/=np.linalg.norm(camera);right=np.cross([0,1,0],camera);right/=np.linalg.norm(right);up=np.cross(camera,right);T=np.stack([right,up,camera]);colors=np.array([[85,88,91],[160,163,165],[180,90,25],[40,40,40]]);points=(tri-target)@T.T;depth=points[:,:,2].mean(1);im=Image.new('RGB',(1800,700),'#20252f');d=ImageDraw.Draw(im);shade=np.clip(.45+.55*abs(nn@np.array([.3,.7,.4])),.25,1);rgb=np.clip(colors[mi]*shade[:,None],0,255).astype(int)
for k in np.argsort(depth):
 if (nn[k]@camera)<0:continue
 q=points[k];d.polygon([(900+float(x)*13,350-float(y)*13) for x,y,z in q],fill=tuple(rgb[k]))
d.text((20,20),'0.4 CORRECTIVE DERIVATIVE / 90,356 TRIANGLES / AUTHORS NORMAL CULL / OFFLINE ONLY',fill='white');im.save(out/'corrective-preview.png')
