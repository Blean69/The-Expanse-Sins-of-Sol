from update11_donnager_common import *
from scipy.spatial.transform import Rotation
from PIL import Image,ImageDraw
z=np.load(OUT/'optimized.npz');rows=read(AUDIT/'optimized-parts.json')['parts'];hull=np.concatenate([z[r['key']+'_v'][z[r['key']+'_i']] for r in rows if r['node'] not in [33,34,35,36]]);hullnodes=np.concatenate([np.full(len(z[r['key']+'_i']),r['node']) for r in rows if r['node'] not in [33,34,35,36]])
hull_min=hull.min(1);hull_max=hull.max(1)
def rayhit(origin,direction):
 o=np.array(origin);d=np.array(direction);axis=int(np.argmax(abs(d)));other=[j for j in range(3) if j!=axis];mask=np.all((hull_min[:,other]<=o[other]+1e-7)&(hull_max[:,other]>=o[other]-1e-7),axis=1);which=np.where(mask)[0];ht=hull[mask];e1=ht[:,1]-ht[:,0];e2=ht[:,2]-ht[:,0];h=np.cross(d,e2);det=np.sum(e1*h,1);valid=abs(det)>1e-10;inv=np.divide(1,det,out=np.zeros_like(det),where=valid);s=o-ht[:,0];u=inv*np.sum(s*h,1);q=np.cross(s,e1);v=inv*np.sum(d*q,1);t=inv*np.sum(e2*q,1);good=np.where(valid&(u>=-1e-8)&(v>=-1e-8)&(u+v<=1+1e-8)&(t>=0))[0]
 if not len(good):return None
 j=good[np.argmin(t[good])];normal=np.cross(e1[j],e2[j]);normal/=np.linalg.norm(normal)
 if np.dot(normal,d)>0:normal=-normal
 return {'position':(o+d*t[j]).tolist(),'normal':normal.tolist(),'node':int(hullnodes[which[j]]),'triangle':int(which[j])}

# Validate frozen supports and pivots against the new higher fidelity hull.
m=read(AUDIT/'mount-metadata.json'); old_meta=read(FROZEN/'audit/donnager10-b/mount-metadata.json'); support_checks=[]; rail_checks=[]
for cur,prior in zip(m['rigs'],old_meta['rigs']):
 for key in ['yaw_pivot_hull','pitch_pivot_hull','muzzle_hull','basis_columns']:
  assert cur[key]==prior[key],(cur['index'],key)
 assert cur['mount']==prior['mount'],cur['index']
 if cur['kind']!='pdc':continue
 B=np.array(cur['basis_columns']);up=B[:,1];right=B[:,0];fw=B[:,2];p=np.array(cur['yaw_pivot_hull']);s=cur['measured_support']['support']; heights=[]
 for x,y in [(0,0),(-2.8,-2.8),(-2.8,2.8),(2.8,-2.8),(2.8,2.8)]:
  hit=rayhit(p+up*100+right*x+fw*y,-up);assert hit is not None; heights.append(float(np.dot(hit['position'],up)))
 assert min(heights)>s['bottom']-.05,(cur['index'],'socket gap',min(heights),s['bottom'])
 assert max(heights)<s['top']+1.0,(cur['index'],'greater than 1 unit source surface restoration at frozen socket',max(heights),s['top'])
 support_checks.append({'mount':cur['index'],'frozen_socket_bottom_top':[s['bottom'],s['top']],'new_surface_heights':heights,'maximum_local_hull_above_socket_top':max(0,max(heights)-s['top']),'maximum_socket_bottom_gap':max(0,s['bottom']-min(heights))})
for r in m['rigs'][16:]:
 ri=r['index']-16;sign=-1 if ri==0 else 1;p=np.array(r['yaw_pivot_hull']);rv=[]
 for row in rows:
  if row['node'] not in [33,34,35,36]:continue
  vv=z[row['key']+'_v'];ii=z[row['key']+'_i'];mask=vv[ii].mean(1)[:,0]*sign>0;rv.extend(vv[ii[mask]].reshape(-1,3))
 rv=np.array(rv);sample=rv[np.linspace(0,len(rv)-1,400).astype(int)]
 for angle in [-2,-1,0,1,2]:
  R=Rotation.from_euler('y',angle,degrees=True).as_matrix();moved=(sample-p)@R.T+p;outside=[];inside=[]
  for q in moved:
   hit=rayhit([sign*260,q[1],q[2]],[-sign,0,0])
   if hit and sign*(q[0]-hit['position'][0])<-.05:
    datum={'point':q.tolist(),'hull':hit['position']}
    if np.linalg.norm((q-p)[[0,2]])>11.2 or abs(q[1]-p[1])>19:outside.append(datum)
    else:inside.append(datum)
  rail_checks.append({'rail':ri,'angle_degrees':angle,'sampled_vertices':400,'contacts_outside_original_bearing_envelope':outside,'contacts_within_intended_bearing':len(inside)})
  assert len(outside)==0,(ri,angle,outside)
assert m['equipment']==old_meta['equipment'];assert m['normalization']==old_meta['normalization'];assert max(abs(np.array(m['ship_spatial']['bounds_min'])-old_meta['ship_spatial']['bounds_min']))<1.;assert max(abs(np.array(m['ship_spatial']['bounds_max'])-old_meta['ship_spatial']['bounds_max']))<1.
write(AUDIT/'mount-preservation-checks.json',{'status':'PASS BOUNDED OFFLINE ONLY','all18_mount_transform_dicts_exact':True,'equipment_exact':True,'normalization_exact':True,'spatial_restored_detail_under_one_unit_delta':True,'old_spatial':old_meta['ship_spatial'],'new_spatial':m['ship_spatial'],'support_checks':support_checks,'rail_checks':rail_checks,'caveat':'400 sampled vertices at five poses per rail; full continuous or internal collision not proven. Runtime not run.'})
print('PASS 18 exact mounts, 16 supported sockets, equipment, spatial and bounded rail sweep')
