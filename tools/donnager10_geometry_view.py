from donnager10_geometry_common import *
from PIL import Image,ImageDraw
r=read(AUDIT/'optimization-probe.json');z=np.load(OUT/'probe.npz');tri=[];col=[];ns=[]
for p in r['parts']:
 k=p['key'];ii=z[k+'_i'];v=z[k+'_v'];no=z[k+'_n'];uv=z[k+'_uv'];mat=a.g['materials'][p['material']];pbr=mat['pbrMetallicRoughness'];base=np.array(pbr.get('baseColorFactor',[1]*4))[:3]
 if 'baseColorTexture' in pbr:
  ip=a.g['images'][a.g['textures'][pbr['baseColorTexture']['index']]['source']]['uri'];tex=np.array(Image.open(SRC/ip).convert('RGB'));uvc=uv[ii].mean(1)%1;xy=np.minimum((uvc*np.array(tex.shape[1::-1])).astype(int),np.array(tex.shape[1::-1])-1);rgb=tex[xy[:,1],xy[:,0]]*base
 else:rgb=np.tile(base*255,(len(ii),1))
 tri.extend(v[ii]);ns.extend(no[ii].mean(1));col.extend(rgb)
tri=np.array(tri);ns=np.array(ns);col=np.array(col);im=Image.new('RGB',(1800,1500),'#111827');d=ImageDraw.Draw(im)
for panel,(h,v,dep) in enumerate([(2,1,0),(2,0,1),(0,1,2)]):
 left=0;top=panel*500;s=.73 if panel<2 else .95;cx=900 if panel<2 else 900;cy=top+255;light=np.clip(.45+.55*abs(ns[:,dep]),.3,1);rgb=np.clip(col*light[:,None],0,255).astype(int)
 for k in np.argsort(tri[:,:,dep].mean(1)):
  if ns[k,dep]<0:continue
  d.polygon([(cx+float(p[h])*s,cy-float(p[v])*s) for p in tri[k]],fill=tuple(rgb[k]))
 d.text((20,top+20),f'Donnager actual reduced source: horizontal axis{h}, vertical{v}, camera+{dep}; {len(tri)}tri',fill='white')
im.save(AUDIT/'optimization-preview.png')
