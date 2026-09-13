from common import *
from PIL import Image,ImageDraw
out=ROOT/'audit/geometry04-b';m=read(ROOT/'audit/geometry03-b/hero-mount-metadata.json')['normalization'];C=np.array(m['source_to_game_rotation']);center=np.array(m['source_rotated_center']);target=np.array(m['target_center']);scale=m['scale'];a=Gltf(ROOT/'assets/derived/geometry03-b/hero/rocinante_stand_free_deployed.gltf');tris=[];norm=[];mats=[]
for i,n in enumerate(a.g['nodes']):
 for p in a.g['meshes'][n['mesh']]['primitives']:
  v=(a.positions(i,p)@C.T-center)*scale+target;no=a.accessor(p['attributes']['NORMAL'])@np.linalg.inv(a.world[i][:3,:3])@C.T;idx=a.accessor(p['indices']).reshape(-1,3);tris.extend(v[idx]);norm.extend(no[idx].mean(1));mats.extend([p['material']]*len(idx))
source=(np.array(tris),np.array(norm),np.array(mats));b=Gltf(ROOT/'assets/derived/geometry03-b/hero/expanse03_hero_static.gltf');tris=[];norm=[];mats=[]
for p in b.g['meshes'][0]['primitives']:
 v=b.accessor(p['attributes']['POSITION']);v[:,2]*=-1;no=b.accessor(p['attributes']['NORMAL']);no[:,2]*=-1;idx=b.accessor(p['indices']).reshape(-1,3);tris.extend(v[idx]);norm.extend(no[idx].mean(1));mats.extend([p['material']]*len(idx))
optimized=(np.array(tris),np.array(norm),np.array(mats));camera=np.array([1.,.35,.12]);camera/=np.linalg.norm(camera);right=np.cross([0,1,0],camera);right/=np.linalg.norm(right);up=np.cross(camera,right);T=np.stack([right,up,camera]);colors=np.array([[85,88,91],[160,163,165],[180,90,25],[40,40,40]])
im=Image.new('RGB',(1800,1100),'#20252f');d=ImageDraw.Draw(im)
for row,(tri,nn,mi) in enumerate([source,optimized]):
 nlen=np.linalg.norm(nn,axis=1);nn/=np.maximum(nlen[:,None],1e-9);p=(tri-target)@T.T;depth=p[:,:,2].mean(1);normal_camera=nn@camera
 for col,cull in enumerate([False,True]):
  shade=np.clip(.45+.55*abs(nn@np.array([.3,.7,.4])),.25,1);rgb=np.clip(colors[mi]*shade[:,None],0,255).astype(int)
  for k in np.argsort(depth):
   if cull and normal_camera[k]<0:continue
   q=p[k];d.polygon([(900*col+450+float(x)*6,550*row+270-float(y)*6) for x,y,z in q],fill=tuple(rgb[k]))
  d.text((900*col+20,550*row+20),('FULL SOURCE' if row==0 else '0.3 OPTIMIZED')+(' CULL TO AUTHOR NORMALS' if cull else 'BOTH SIDES'),fill='white')
im.save(out/'source-v-optimized.png')
