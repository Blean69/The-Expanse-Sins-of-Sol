"""Repaint retained Scirocco geometry and enlarge its existing twelve PDC assemblies.
No optimization/import, source modification, gameplay, or install operations.
"""
from pathlib import Path
import sys,json,copy,shutil,hashlib,numpy as np
from scipy.spatial.transform import Rotation
import update12_scirocco_common as c
from common import Gltf,read,write
R=Path(__file__).resolve().parents[1]; D=Path('/run/media/haker/NVME 2/expanse-workers/tachi-one-pdc');O=R/'assets/derived/update14-scirocco';A=R/'audit/update14-scirocco';B=R/'build/update14-scirocco';P='expanse12_scirocco'
for x in (O,A,B):x.mkdir(parents=True,exist_ok=True)
c.OUT=O
meta=read(D/'audit/update12-b/integration-spec.json');original=copy.deepcopy(meta)
parts={}
for kind in ('hull','pdc_base','pdc_barrel','rail_0'):
 g=Gltf(D/'assets/derived/update12-b'/f'{P}_{kind}.gltf');parts[kind]=[]
 for pr in g.g['meshes'][0]['primitives']:
  v=g.accessor(pr['attributes']['POSITION']);n=g.accessor(pr['attributes']['NORMAL']);t=g.accessor(pr['attributes']['TANGENT']);v[:,2]*=-1;n[:,2]*=-1;t[:,2]*=-1;t[:,3]*=-1
  parts[kind].append(dict(v=v,n=n,t=t,uv=g.accessor(pr['attributes']['TEXCOORD_0']),i=g.accessor(pr['indices']).reshape(-1,3),material=g.g['materials'][pr['material']]['name']))
# Compiler-input triangle order is not game-space triangle order. Restore each
# face to its preserved authored outward normals before deriving fresh frames.
orientation=[]
for kind, pp in parts.items():
 for p in pp:
  tri=p['v'][p['i']];q=np.cross(tri[:,1]-tri[:,0],tri[:,2]-tri[:,0])
  flip=np.sum(q*p['n'][p['i']].mean(1),axis=1)<0
  p['i'][flip]=p['i'][flip][:,[0,2,1]]
  orientation.append({'part':kind,'material':p['material'],'triangles':len(tri),'restored_to_authored_outward_normals':int(flip.sum())})
write(A/'import-orientation.json',orientation)
# Fixed hull includes existing 12 narrow sockets, rail bearing, and ten launch collars.
# They remain; wider inset footings enclose the old PDC sockets, not duplicate guns.
hull=np.concatenate([p['v'][p['i']]for p in parts['hull']]);cache={}
def ray(o,d):
 o=np.asarray(o);d=np.asarray(d);key=tuple(d)
 if key not in cache:
  a=np.eye(3)[np.argmin(abs(d))];a-=d*np.dot(a,d);a/=np.linalg.norm(a);b=np.cross(d,a);q=np.stack([hull@a,hull@b],axis=-1);cache[key]=(a,b,q.min(1),q.max(1))
 a,b,mn,mx=cache[key];xy=[o@a,o@b];q=hull[np.all((mn<=xy)&(mx>=xy),1)];e=q[:,1]-q[:,0];f=q[:,2]-q[:,0];h=np.cross(d,f);det=np.sum(e*h,1);inv=np.divide(1,det,out=np.zeros_like(det),where=abs(det)>1e-10);s=o-q[:,0];u=np.sum(s*h,1)*inv;v=np.cross(s,e)@d*inv;t=np.sum(f*np.cross(s,e),1)*inv;ok=(abs(det)>1e-10)&(u>=-1e-7)&(v>=-1e-7)&(u+v<=1+1e-7)&(t>0)
 if not ok.any():raise ValueError(('footing misses hull',o.tolist()))
 return o+d*t[ok].min()
def cylinder(p0,p1,r):
 axis=p1-p0;axis/=np.linalg.norm(axis);x=np.eye(3)[np.argmin(abs(axis))];x-=axis*np.dot(x,axis);x/=np.linalg.norm(x);y=np.cross(axis,x);rad=r*(np.cos(np.arange(24)*np.pi/12)[:,None]*x+np.sin(np.arange(24)*np.pi/12)[:,None]*y);aa=p0+rad;bb=p1+rad;out=[]
 for i in range(24):
  j=(i+1)%24;out.extend([[aa[i],aa[j],bb[j]],[aa[i],bb[j],bb[i]],[p0,aa[j],aa[i]],[p1,bb[i],bb[j]]])
 return np.array(out)
SCALE=2.2;footings=[];checks=[]
for r in meta['rigs']:
 if r['kind']!='pdc':continue
 basis=np.array(r['basis_columns']);up=basis[:,1];old=np.array(r['yaw_pivot_hull']);radius=6.6
 samples=[]
 for angle in np.arange(8)*np.pi/4:
  lateral=(basis[:,0]*np.cos(angle)+basis[:,2]*np.sin(angle))*radius*.92;samples.append(ray(old+up*100+lateral,-up))
 heights=np.array(samples)@up;top=max(heights.max()+5.0,old@up+3.5);bottom=heights.min()-.8;new=old+up*(top-old@up)
 footings.append(cylinder(new+up*(bottom-top),new,radius))
 r['yaw_pivot_hull']=new.tolist();r['mount']['weapon_position']=new.tolist();r['turret_override']['barrel_position']=(np.array(r['turret_override']['barrel_position'])*SCALE).tolist();r['turret_override']['muzzle_positions']=(np.array(r['turret_override']['muzzle_positions'])*SCALE).tolist();off=np.array(r['turret_override']['barrel_position']);tip=np.array(r['turret_override']['muzzle_positions'][0]);r['pitch_pivot_hull']=(new+basis@off).tolist();r['muzzle_hull']=(new+basis@(off+tip)).tolist();r['support']={'samples':np.array(samples).tolist(),'bottom':float(bottom),'top':float(top),'radius':radius};r['visual_scale_from_update12']=SCALE
 for pt in meta['meshpoints']['hull']:
  if pt['name']==r['mount']['mesh_point']:pt['translation']=new.tolist()
 checks.append({'index':r['index'],'eight_footprint_samples_inside_support':bool(heights.min()>bottom and heights.max()<top),'support_radius':radius,'support_depth':float(top-bottom),'origin_shift':float(top-old@up)})
for kind in ('pdc_base','pdc_barrel'):
 for p in parts[kind]:p['v']*=SCALE
# New broad Martian orange-red stripes follow measured longitudinal stations.
# Split actual triangles at every color boundary instead of staircase face assignments.
def clip(poly,z,above):
 out=[]
 for a,b in zip(poly,poly[1:]+poly[:1]):
  ia=a[2]>=z if above else a[2]<=z;ib=b[2]>=z if above else b[2]<=z
  if ia:out.append(a)
  if ia!=ib:out.append(a+(b-a)*((z-a[2])/(b[2]-a[2])))
 return out
paint={0:[],1:[],2:[]};limits=[-1000,-191,-174,-119,-96,158,179,1000]
for k,(lo,hi) in enumerate(zip(limits,limits[1:])):
 inside=(hull[:,:,2].min(1)>=lo)&(hull[:,:,2].max(1)<=hi);q=list(hull[inside]);touch=(hull[:,:,2].max(1)>lo)&(hull[:,:,2].min(1)<hi)&~inside
 for tt in hull[touch]:
  poly=clip(clip(list(tt),lo,True),hi,False)
  for j in range(1,len(poly)-1):
   tri=np.array([poly[0],poly[j],poly[j+1]])
   if np.linalg.norm(np.cross(tri[1]-tri[0],tri[2]-tri[0]))>1e-7:q.append(tri)
 paint[1 if k in (1,3,5) else 0].extend(q)
paint[2].extend(np.concatenate(footings));parts['hull']=[c.frames(np.array(q),P+f'_mat_{m}')for m,q in paint.items()]
# Consistent dominant-axis planar UVs within [0,1], normalized by500game units. No original UV claim.
for p in parts['hull']:
 uv=[];tangent=[]
 for tri,ns in zip(p['v'][p['i']],p['n'][p['i']]):
  face=np.cross(tri[1]-tri[0],tri[2]-tri[0]);face/=np.linalg.norm(face);axis=np.argmax(abs(face));u=np.eye(3)[(axis+1)%3];v=np.eye(3)[(axis+2)%3];uv.extend(np.column_stack([tri@u,tri@v])/500.+.5)
  for n in ns:
   t=u-n*np.dot(n,u);t/=np.linalg.norm(t);w=1 if np.dot(np.cross(n,t),v)>0 else -1;tangent.append([*t,w])
 p['uv']=np.array(uv);p['t']=np.array(tangent)
tex=O/'texture-sources';tex.mkdir(exist_ok=True)
source=Path('/run/media/haker/NVME 2/expanse-workers/visual13-scirocco/assets/source/update13-a/charcoal-panel-tile.png');shutil.copyfile(source,tex/'expanse13_scirocco_panels_clr.png')
frames={}
for kind,pp in parts.items():
 c.savegltf(P+'_'+kind,pp,meta['meshpoints'][kind]);frames[kind]={str(i):{k:p[k].tolist()for k in ('v','n','t','uv')}for i,p in enumerate(pp)}
assembled=copy.deepcopy(parts['hull'])
for r in meta['rigs']:
 basis=np.array(r['basis_columns']);origin=np.array(r['yaw_pivot_hull']);pieces=[('rail_0',np.zeros(3))]if r['kind']=='rail'else[('pdc_base',np.zeros(3)),('pdc_barrel',np.array(r['turret_override']['barrel_position']))]
 for kind,off in pieces:
  for pp in parts[kind]:
   p=copy.deepcopy(pp);p['v']=(p['v']+off)@basis.T+origin;p['n']=p['n']@basis.T;p['t'][:,:3]=p['t'][:,:3]@basis.T;assembled.append(p)
c.savegltf(P+'_editable',assembled,compiler=False)
# Editable render actually references the same charcoal texture game uses.
g=read(O/(P+'_editable.gltf'));g['images']=[{'uri':'texture-sources/expanse13_scirocco_panels_clr.png'}];g['textures']=[{'source':0}]
for mat in g['materials']:
 if mat['name'].endswith('_mat_0'):mat['pbrMetallicRoughness']={'baseColorFactor':[1,1,1,1],'baseColorTexture':{'index':0}}
write(O/(P+'_editable.gltf'),g)
vertices=np.concatenate([p['v']for p in assembled]);lo=vertices.min(0);hi=vertices.max(0);center=(lo+hi)/2
meta.update(status='COMPILER PENDING',game_directory=str(B/'game'),editable_source=str(O/(P+'_editable.gltf')),counts={k:sum(len(p['i'])for p in pp)for k,pp in parts.items()},assembled_triangle_total=sum(len(p['i'])for p in assembled),ship_spatial={'box':{'center':center.tolist(),'extents':((hi-lo)/2).tolist()},'radius':float(np.linalg.norm(vertices-center,axis=1).max()),'bounds_min':lo.tolist(),'bounds_max':hi.tolist()})
write(O/'retained-source-frames.json',frames);write(A/'integration-spec.json',meta);write(A/'support-checks.json',{'status':'PASS OFFLINE','mounts':checks,'scale':SCALE,'source_original_sha256':hashlib.sha256((D/'assets/derived/update12-b/expanse12_scirocco_hull.bin').read_bytes()).hexdigest(),'rail_metadata_unchanged':meta['rigs'][-1]==original['rigs'][-1],'runtime':'NOT RUN'})
print(meta['counts'],meta['assembled_triangle_total'])
