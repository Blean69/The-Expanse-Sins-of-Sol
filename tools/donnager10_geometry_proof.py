from donnager10_geometry_common import *
from PIL import Image,ImageDraw
m=read(AUDIT/'mount-metadata.json');scene=Gltf(OUT/'donnager10_editable.gltf');tri=[];norm=[];colors=[]
for ni,node in enumerate(scene.g['nodes']):
 if 'mesh' not in node:continue
 M=scene.world[ni]
 for p in scene.g['meshes'][node['mesh']]['primitives']:
  v=scene.accessor(p['attributes']['POSITION'])@M[:3,:3].T+M[:3,3];n=scene.accessor(p['attributes']['NORMAL'])@np.linalg.inv(M[:3,:3]);ii=scene.accessor(p['indices']).flatten().reshape(-1,3);tri.extend(v[ii]);norm.extend(n[ii].mean(1));color=[72,196,208] if 'PDC' in node['name'] else [220,158,80] if 'rail' in node['name'] else [116,124,139];colors.extend([color]*len(ii))
tri=np.array(tri);norm=np.array(norm);colors=np.array(colors);im=Image.new('RGB',(1600,1100),'#101824');d=ImageDraw.Draw(im)
pdc=m['rigs'][0];rail=m['rigs'][16]
views=[(np.array(pdc['yaw_pivot_hull']),np.array([0,0,1.]),np.array([1.,.2,0]),32,'PDC0 actual donor + measured hull support',0,0),(np.array(rail['yaw_pivot_hull'])+[0,0,65],np.array([0,0,1.]),np.array([1.,0,0]),3.4,'Rail0 whole source assembly / measured drum & fixed yoke',800,0),(np.array(pdc['yaw_pivot_hull']),np.array([0.,1,0]),np.array([1.,0,0]),32,'PDC0 support front section',0,550),(np.array(rail['yaw_pivot_hull']),np.array([0,1.,0]),np.array([1.,0,0]),8,'Rail0 drum end bearing / source hull contact region',800,550)]
for origin,u,v,s,label,left,top in views:
 panel=Image.new('RGB',(800,550),'#101824');d=ImageDraw.Draw(panel);pl=left;pt=top;left=0;top=0;u/=np.linalg.norm(u);v-=u*np.dot(u,v);v/=np.linalg.norm(v);dep=np.cross(u,v);q=tri-origin;xx=q@u;yy=q@v;zz=q@dep;mask=(zz.min(1)<(15 if pl==0 else 30))&(zz.max(1)>(-15 if pl==0 else -30))&(xx.min(1)<350/s)&(xx.max(1)>-350/s)&(yy.min(1)<190/s)&(yy.max(1)>-190/s);ids=np.where(mask)[0];ids=ids[np.argsort(zz[ids].mean(1))]
 for i in ids:
  if np.dot(norm[i],dep)<0:continue
  shade=.4+.6*abs(np.dot(norm[i],dep));rgb=tuple(np.clip(colors[i]*shade,0,255).astype(int));d.polygon([(left+400+float(x)*s,top+270-float(y)*s) for x,y in zip(xx[i],yy[i])],fill=rgb)
 d.rectangle([left,top,left+800,top+550],outline='#31435b',width=3);d.text((left+15,top+15),label,fill='white');d.text((left+15,top+520),'Measured candidate; runtime rotation/clearance NOT RUN',fill='#f5c86c')
 point=np.array(pdc['yaw_pivot_hull'] if pl==0 else rail['yaw_pivot_hull'])-origin;x=left+400+np.dot(point,u)*s;y=top+270-np.dot(point,v)*s;d.ellipse((x-5,y-5,x+5,y+5),outline='#ffdf59',width=2);im.paste(panel,(pl,pt))
im.save(AUDIT/'first-mount-proof.png');print('First measured rail/PDC proof written')
