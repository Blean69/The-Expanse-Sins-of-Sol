from donnager10_geometry_common import *
from PIL import Image,ImageDraw
from scipy.ndimage import binary_dilation
original=np.concatenate([r['v'][r['i']] for r in source_parts()]);z=np.load(OUT/'optimized.npz');rows=read(AUDIT/'optimized-parts.json')['parts'];reduced=np.concatenate([z[r['key']+'_v'][z[r['key']+'_i']] for r in rows]);records=[];contact=Image.new('RGB',(1200,1350),'#111827')
for vi,(h,v) in enumerate([(2,0),(2,1),(0,1)]):
 masks=[];s=.92 if h==2 else .75
 for tris in [original,reduced]:
  im=Image.new('1',(1200,450));d=ImageDraw.Draw(im)
  for q in tris:d.polygon([(600+float(p[h])*s,225-float(p[v])*s) for p in q],fill=1)
  masks.append(np.array(im,dtype=bool))
 o,r=masks;iou=float((o&r).sum()/(o|r).sum());missing=int((o&~binary_dilation(r,iterations=2)).sum());added=int((r&~binary_dilation(o,iterations=2)).sum());record={'axes':[h,v],'pixels_per_game_unit':s,'source_pixels':int(o.sum()),'reduced_pixels':int(r.sum()),'intersection_over_union':iou,'source_pixels_missing_beyond_two_pixel_tolerance':missing,'derivative_pixels_added_beyond_two_pixel_tolerance':added};records.append(record);rgb=np.zeros((*o.shape,3),dtype=np.uint8);rgb[o]=[190,82,88];rgb[r]=[74,186,193];rgb[o&r]=[152,165,183];contact.paste(Image.fromarray(rgb),(0,450*vi));print(record,flush=True)
contact.save(AUDIT/'silhouette-comparison.png');write(AUDIT/'silhouette-comparison.json',{'status':'MEASURED OFFLINE; visual quality requires runtime','purpose':'Original and optimized source only, before donor/support/collar additions. Binary projected masks, not a shading/UV proof','views':records})
