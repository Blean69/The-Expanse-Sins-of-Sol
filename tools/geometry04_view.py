from common import *
from PIL import Image,ImageDraw
out=ROOT/'audit/geometry04-b';a=Gltf(ROOT/'assets/derived/geometry04-b/expanse04_hero_editable.gltf');meta=read(out/'mount-metadata.json');target=np.array(meta['normalization']['target_center']);tris=[];norm=[];mats=[]
for i,n in enumerate(a.g['nodes']):
 for p in a.g['meshes'][n['mesh']]['primitives']:
  v=a.positions(i,p);no=a.accessor(p['attributes']['NORMAL'])@np.linalg.inv(a.world[i][:3,:3]);idx=a.accessor(p['indices']).reshape(-1,3);tris.extend(v[idx]);norm.extend(no[idx].mean(1));mats.extend([p['material']]*len(idx))
tri=np.array(tris);nn=np.array(norm);mi=np.array(mats);nn/=np.maximum(np.linalg.norm(nn,axis=1)[:,None],1e-9);camera=np.array([-1.,.35,.12]);camera/=np.linalg.norm(camera);right=np.cross([0,1,0],camera);right/=np.linalg.norm(right);up=np.cross(camera,right);T=np.stack([right,up,camera]);colors=np.array([[85,88,91],[160,163,165],[180,90,25]]);im=Image.new('RGB',(1800,1100),'#20252f');d=ImageDraw.Draw(im);shade=np.clip(.45+.55*abs(nn@np.array([.3,.7,.4])),.25,1);rgb=np.clip(colors[mi]*shade[:,None],0,255).astype(int)
for panel,(center,s,cx,cy) in enumerate([(target,13,900,320),(np.array(meta['rigs'][0]['pitch_pivot_hull']),43,450,870)]):
 points=(tri-center)@T.T;depth=points[:,:,2].mean(1)
 for k in np.argsort(depth):
  if (nn[k]@camera)<0:continue
  if panel==1 and np.linalg.norm(tri[k].mean(0)-center)>9:continue
  q=points[k];xy=[(cx+float(x)*s,cy-float(y)*s) for x,y,z in q]
  if panel==1 and any(y<610 for x,y in xy):continue
  d.polygon(xy,fill=tuple(rgb[k]))
 if panel==1:
  r=meta['rigs'][0]
  for label,key,color in [('yaw socket','yaw_pivot_hull','#f581ef'),('pitch joint','pitch_pivot_hull','#6ee5ff'),('actual barrel muzzle','muzzle_hull','#ffe277')]:
   q=(np.array(r[key])-center)@T.T;x=cx+q[0]*s;y=cy-q[1]*s;d.ellipse((x-5,y-5,x+5,y+5),fill=color);d.text((x+10,y-15),label,fill=color)
d.text((20,20),'CORRECTED HERO / SIX INDEPENDENT AIMING RIGS / OFFLINE VIEW, RUNTIME NOT RUN',fill='white');d.text((940,720),'Geometry: complete source cannon1+cannon2 / magazines / pins',fill='white');d.text((940,750),'moves together as pitch assembly; new shaft and yoke yaw.',fill='white');d.text((940,790),'Fixed source slide/frame/cover remains in hull.',fill='white');d.text((940,830),'Source deployment roll is preserved in the baked pose.',fill='white');d.text((940,870),'Aiming pivots are explicit new mechanical joints.',fill='white');d.text((940,920),'Inspect clearance through full yaw/pitch arcs in game.',fill='white');im.save(out/'hero-aiming-rig-view.png')
