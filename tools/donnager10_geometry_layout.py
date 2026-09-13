from donnager10_geometry_common import *
from scipy.spatial.transform import Rotation
from PIL import Image,ImageDraw
z=np.load(OUT/'probe.npz');rows=read(AUDIT/'optimization-probe.json')['parts'];hull=np.concatenate([z[r['key']+'_v'][z[r['key']+'_i']] for r in rows if r['node'] not in [33,34,35,36]]);hullnodes=np.concatenate([np.full(len(z[r['key']+'_i']),r['node']) for r in rows if r['node'] not in [33,34,35,36]])
def rayhit(origin,direction):
 o=np.array(origin);d=np.array(direction);axis=int(np.argmax(abs(d)));other=[j for j in range(3) if j!=axis];mask=np.all((hull.min(1)[:,other]<=o[other]+1e-7)&(hull.max(1)[:,other]>=o[other]-1e-7),axis=1);which=np.where(mask)[0];ht=hull[mask];e1=ht[:,1]-ht[:,0];e2=ht[:,2]-ht[:,0];h=np.cross(d,e2);det=np.sum(e1*h,1);valid=abs(det)>1e-10;inv=np.divide(1,det,out=np.zeros_like(det),where=valid);s=o-ht[:,0];u=inv*np.sum(s*h,1);q=np.cross(s,e1);v=inv*np.sum(d*q,1);t=inv*np.sum(e2*q,1);good=np.where(valid&(u>=-1e-8)&(v>=-1e-8)&(u+v<=1+1e-8)&(t>=0))[0]
 if not len(good):return None
 j=good[np.argmin(t[good])];normal=np.cross(e1[j],e2[j]);normal/=np.linalg.norm(normal)
 if np.dot(normal,d)>0:normal=-normal
 return {'position':(o+d*t[j]).tolist(),'normal':normal.tolist(),'node':int(hullnodes[which[j]]),'triangle':int(which[j])}
mounts=[]
for station,long in enumerate([-370.,-150.,50.,240.]):
 for sector,up in enumerate([[1.,0,0],[0,1.,0],[-1.,0,0],[0,-1.,0]]):
  up=np.array(up);fw=np.array([0.,0,1]);right=np.cross(up,fw);samples=[]
  for x,y in [(0,0),(-2.8,-2.8),(-2.8,2.8),(2.8,-2.8),(2.8,2.8)]:
   hit=rayhit(up*260+fw*(long+y)+right*x,-up);assert hit is not None,(station,sector);samples.append(hit)
  heights=[np.dot(s['position'],up) for s in samples];top=max(heights)+.6;bottom=min(heights)-.5;origin=up*top+fw*long;mounts.append({'index':len(mounts),'station':station,'sector':sector,'yaw_pivot_hull':origin.tolist(),'basis_columns':np.column_stack([right,up,fw]).tolist(),'support':{'radius':3.0,'bottom':bottom,'top':top,'foot_samples':samples,'penetration_clearance':.5},'source_surface_normal_dot_up':float(np.dot(samples[0]['normal'],up))})
rails=[]
for ri,side in enumerate(read(INTAKE/'railgun-geometry.json')['sides']):
 pivot=(np.array(side['estimated_drum_center_world'])-center)*scale;sign=-1 if ri==0 else 1;rv=[]
 for r in rows:
  if r['node'] not in [33,34,35,36]:continue
  v=z[r['key']+'_v'];ii=z[r['key']+'_i'];mask=np.mean(v[ii],axis=1)[:,0]*sign>0;rv.extend(v[ii[mask]].reshape(-1,3))
 rv=np.array(rv);tip=rv[rv[:,2]>rv[:,2].max()-.06];muzzle=(tip.min(0)+tip.max(0))/2;muzzle[2]+=.1
 supports=[]
 for y in [-20.0,20.0]:
  hit=rayhit([sign*260,y,pivot[2]],[-sign,0,0]);assert hit;supports.append({'hull_contact':hit,'end':[pivot[0],y,pivot[2]],'thickness':2.5})
 # Sample hull radial boundary at every rail vertex in five narrow yaw poses.
 # Each outward half-ship radial ray provides an actual surface sample; only
 # intended central drum/bearing zone is allowed to contact its fixed yoke.
 checks=[]
 for angle in [-2.,-1.,0.,1.,2.]:
  R=Rotation.from_euler('y',angle,degrees=True).as_matrix();moved=(rv-pivot)@R.T+pivot;clear=[];hits=0;bad=[]
  sample=moved[np.linspace(0,len(moved)-1,min(400,len(moved))).astype(int)]
  for p in sample:
   hit=rayhit([sign*260,p[1],p[2]],[-sign,0,0])
   if hit is not None:clear.append(sign*(p[0]-hit['position'][0]));hits+=1
   if hit is not None and clear[-1]<-.05:bad.append({'point':p.tolist(),'hull':hit,'drum_distance_xz':float(np.linalg.norm((p-pivot)[[0,2]]))})
  checks.append({'angle_degrees':angle,'sampled_vertices':len(sample),'hull_surface_hits':hits,'minimum_radial_clearance':min(clear) if clear else None,'penetrating_samples':int(sum(c<-.05 for c in clear)),'contact_samples':bad})
 rails.append({'index':ri,'pivot':pivot.tolist(),'forward':[0,0,1],'up':[0,1,0],'muzzle':muzzle.tolist(),'muzzle_method':'Terminal forward source rail structure bounds center; front cap bore inspection pending','supports':supports,'sweep':checks,'source_side':side['side']})
write(AUDIT/'layout-candidates.json',{'status':'MEASURED CANDIDATE; support and bore visual review pending','pdc_mounts':mounts,'rails':rails});print(json.dumps({'pdc_count':len(mounts),'supports_height_ranges':[[r['support']['bottom'],r['support']['top']] for r in mounts],'rails':rails},indent=2))
