"""Actual compiled hull orientation, bounds, points, and backface-culled review.
Six exterior ray grids judge winding independently of stored vertex normals.
"""
from pathlib import Path
import sys,json,numpy as np,hashlib
sys.path.insert(0,'/run/media/haker/NVME 2/expanse-mod/tools')
from common import Gltf,read_mesh
from polish_ui import write,render
from PIL import Image,ImageDraw
ROOT=Path(__file__).resolve().parents[1];BASE=Path('/run/media/haker/NVME 2/expanse-mod/build/experiments/expanse_update13')
def exterior(tri):
 rows=[];cross=np.cross(tri[:,1]-tri[:,0],tri[:,2]-tri[:,0]);center=tri.mean(1);bounds=np.array([tri.min((0,1)),tri.max((0,1))])
 for axis in range(3):
  xy=[q for q in range(3)if q!=axis];lo=tri[:,:,xy].min(1);hi=tri[:,:,xy].max(1)
  for sign in [-1,1]:
   hit=wrong=0;wrong_area=total_area=0;failures=[]
   for x in np.linspace(bounds[0,xy[0]],bounds[1,xy[0]],29)[1:-1]:
    for y in np.linspace(bounds[0,xy[1]],bounds[1,xy[1]],29)[1:-1]:
     pt=np.array([x,y]);sel=np.where((lo<=pt).all(1)&(hi>=pt).all(1)&(abs(cross[:,axis])>1e-10))[0]
     if not len(sel):continue
     q=tri[sel];a=q[:,0,xy];e=q[:,1,xy]-a;f=q[:,2,xy]-a;s=pt-a;det=e[:,0]*f[:,1]-e[:,1]*f[:,0];u=(s[:,0]*f[:,1]-s[:,1]*f[:,0])/det;v=(e[:,0]*s[:,1]-e[:,1]*s[:,0])/det;ok=(u>=-1e-7)&(v>=-1e-7)&(u+v<=1+1e-7)
     if not ok.any():continue
     depth=q[:,0,axis]+u*(q[:,1,axis]-q[:,0,axis])+v*(q[:,2,axis]-q[:,0,axis]);ids=np.where(ok)[0];k=ids[np.argmax(sign*depth[ids])];hit+=1;wrong+=int(cross[sel[k],axis]*sign<0)
     if cross[sel[k],axis]*sign<0:failures.append(dict(triangle_index=int(sel[k]),projected_xy=pt.tolist(),position_axis=float(depth[k]),normal=(cross[sel[k]]/np.linalg.norm(cross[sel[k]])).tolist(),triangle=tri[sel[k]].tolist()))
   rows.append(dict(axis=axis,side=sign,first_surface_hits=hit,inward_facing_first_surfaces=wrong,backface_hits=failures))
 return rows
for variant in ['raptor','pella']:
 p='expanse12_'+variant;out=ROOT/'audit/update14-hulls'/variant;build=ROOT/'build/update14-hulls'/variant;meta=json.loads((out/'integration-spec.json').read_text());mesh_json=build/'repaired-json'/(p+'_hull.mesh_json');mesh_json=mesh_json if mesh_json.exists()else build/'compiler-json'/(p+'_hull.mesh_json');m=json.loads(mesh_json.read_text());v=np.array([a['p']for a in m['non_skinned_vertices']]);idx=np.array(m['vertex_indices']).reshape(-1,3);tri=v[idx]
 unit=json.loads((BASE/'entities'/(p+'.unit')).read_text());spatial=unit['spatial'];print(spatial)
 exterior_rows=exterior(tri);write(out/'exterior-detail.json',exterior_rows)
 write(out/'exterior-check.json',{'runtime':'NOT RUN','six_sided_exterior_grid':exterior_rows,'compiled_signed_volume':float(np.einsum('ij,ij->i',tri[:,0],np.cross(tri[:,1],tri[:,2])).sum()/6),'compiled_bounds':[v.min(0).tolist(),v.max(0).tolist()],'old_spatial':spatial})
 # Backface-cull by geometric face winding before the existing software rasterizer.
 panels=[]
 for version,src in [('0.13',Path('/run/media/haker/NVME 2/expanse-workers/visual13-hulls/assets/derived/update13-b')/variant/(p+'_hull.gltf')),('0.14',ROOT/'assets/derived/update14-hulls'/variant/(p+'_hull.gltf'))]:
  g=Gltf(src)
  for view,basis in [('aft',np.array([[-1.,0,0],[0,1,0],[0,0,-1]])),('oblique',np.array([[.6,0,.8],[-.3,.927,.225],[-.7416,-.375,.5562]]))]:
   meshes=[]
   for pr in g.g['meshes'][0]['primitives']:
    vv=g.accessor(pr['attributes']['POSITION']);vv[:,2]*=-1;nn=g.accessor(pr['attributes']['NORMAL']);nn[:,2]*=-1;ii=g.accessor(pr['indices']).reshape(-1,3);t=vv[ii];cross=np.cross(t[:,1]-t[:,0],t[:,2]-t[:,0]);flip=(cross*nn[ii].mean(1)).sum(1)<0;t[flip]=t[flip][:,[0,2,1]];cross[flip]*=-1;sel=cross@basis[2]>0;mat=g.g['materials'][pr['material']]['pbrMetallicRoughness'];tex=np.full((1,1,4),255,np.uint8);uv=np.zeros((len(t),3,2))
    if 'baseColorTexture'in mat:
     texture=Path('/run/media/haker/NVME 2/expanse-workers/weapon-behavior/assets/derived/update12-a/pella/texture-sources/expanse12_pella_free_navy_clr.png');tex=np.array(Image.open(texture).convert('RGBA'));uv=g.accessor(pr['attributes']['TEXCOORD_0'])[ii];uv[flip]=uv[flip][:,[0,2,1]]
    meshes.append((t[sel],uv[sel],tex,mat.get('baseColorFactor',[.5,.5,.5,1]),'OPAQUE'))
   im=render(meshes,(850,650),basis);bg=Image.new('RGBA',im.size,(12,19,28,255));bg.alpha_composite(im);ImageDraw.Draw(bg).text((15,15),version+' '+variant+' '+view,fill='white');bg.save(out/(version+'-'+view+'.png'));panels.append(bg)
 sheet=Image.new('RGBA',(1700,1300),(12,19,28,255))
 for j,im in enumerate(panels):sheet.paste(im,((j//2)*850,(j%2)*650))
 sheet.save(out/'comparison.png')
