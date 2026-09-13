from amun06_geometry_common import *
from PIL import Image,ImageDraw
rows=[q for i in descendants(3) for q in arrays(i)];tex=np.array(Image.open(SRC/'images/DefaultMaterial_Base_Color.png').convert('RGB'));tris=[];no=[];color=[]
for r in rows:
 idx=r['i'];tris.extend(r['v'][idx]);no.extend(r['n'][idx].mean(1));uv=r['uv'][idx].mean(1);xy=np.clip(np.rint(uv*np.array([4095,4095])),0,4095).astype(int);color.extend(tex[xy[:,1],xy[:,0]])
tri=np.array(tris);no=np.array(no);color=np.array(color);im=Image.new('RGB',(1500,1300),'#141b25');d=ImageDraw.Draw(im)
for panel,(h,v,dep) in enumerate([(0,1,2),(2,1,0)]):
 light=np.clip(.5+.5*abs(no[:,dep]),.3,1);rgb=np.clip(color*light[:,None],0,255).astype(int)
 for k in np.argsort(tri[:,:,dep].mean(1)):
  if no[k,dep]<0:continue
  q=tri[k];d.polygon([(375+750*panel+float(p[h])*14,1180-float(p[v])*18) for p in q],fill=tuple(rgb[k]))
 d.text((20+750*panel,20),f'Central source hull; horizontal={h} vertical=+Y; camera+{dep}',fill='white')
for y in [-5,0,5,10,20,30,40,50,55]:d.text((20,1180-y*18),str(y),fill='white')
im.save(AUDIT/'source-hull-axes.png');print('Hull axes view written')
