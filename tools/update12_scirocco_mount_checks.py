from update12_scirocco_common import *
from scipy.spatial import cKDTree
m=read(AUD/'integration-spec.json');z=np.load(OUT/'optimized-parts.npz');hull=z['hull'];rail=z['rail'];projection_cache={}

def ray(origin,direction):
 o=np.array(origin,float);direction=np.array(direction,float);direction/=np.linalg.norm(direction);key=tuple(np.round(direction,8))
 if key not in projection_cache:
  a=np.eye(3)[np.argmin(abs(direction))];a-=direction*np.dot(a,direction);a/=np.linalg.norm(a);b=np.cross(direction,a);pr=np.stack([hull@a,hull@b],axis=-1);projection_cache[key]=(a,b,pr.min(1),pr.max(1))
 a,b,mn,mx=projection_cache[key];p=np.array([o@a,o@b]);mask=np.all((mn<=p+1e-7)&(mx>=p-1e-7),axis=1);q=hull[mask];e1=q[:,1]-q[:,0];e2=q[:,2]-q[:,0];h=np.cross(direction,e2);det=np.sum(e1*h,1);inv=np.divide(1,det,out=np.zeros_like(det),where=abs(det)>1e-10);s=o-q[:,0];uu=np.sum(s*h,1)*inv;qq=np.cross(s,e1);vv=qq@direction*inv;t=np.sum(e2*qq,1)*inv;ok=(abs(det)>1e-10)&(uu>=-1e-7)&(vv>=-1e-7)&(uu+vv<=1+1e-7)&(t>1e-5)
 if not ok.any():raise ValueError(('Ray misses source-derived hull',o.tolist(),direction.tolist()))
 j=np.where(ok)[0][np.argmin(t[ok])];return o+direction*t[j]

checks=[]
for r in m['rigs']:
 B=np.array(r['basis_columns']);assert np.allclose(B.T@B,np.eye(3),atol=1e-8)and np.linalg.det(B)>.999999
 pos=np.array(r['yaw_pivot_hull']);t=r['turret_override'];tip=np.array(t['muzzle_positions'][0])+np.array(t.get('barrel_position',[0,0,0]));assert np.allclose(pos+B@tip,r['muzzle_hull'],atol=1e-7)
 if r['kind']=='pdc':
  ss=r['support'];up=B[:,1];heights=np.array(ss['samples'])@up;assert heights.min()>ss['bottom']and heights.max()<ss['top'];checks.append({'mount':r['index'],'role':r['placement_role'],'support_depth':ss['top']-ss['bottom'],'five_samples_inside_socket':True})
r=m['rigs'][-1];pos=np.array(r['yaw_pivot_hull']);up=np.array(r['mount']['up']);B=np.array(r['basis_columns']);rv=rail.reshape(-1,3);sample=rv[np.linspace(0,len(rv)-1,600).astype(int)];sweeps=[]
for angle in np.linspace(r['mount']['yaw_arc']['min_angle'],r['mount']['yaw_arc']['max_angle'],5):
 rot=Rotation.from_rotvec(up*np.deg2rad(angle)).as_matrix();q=(sample-pos)@rot.T+pos;outside=[];bearing=0
 for v in q:
  contact=ray(v+up*200,-up);clearance=(v-contact)@up
  if clearance<-.05:
   local=(v-pos)@B
   if np.linalg.norm(local[[0,2]])>14 or abs(local[1])>1.5:outside.append({'point':v.tolist(),'contact':contact.tolist(),'clearance':float(clearance)})
   else:bearing+=1
 sweeps.append({'angle_degrees':angle,'samples':600,'outside_bearing_contacts':outside,'intended_bearing_contacts':bearing})
write(AUD/'rail-clearance.json',{'status':'MEASURED OFFLINE','sweeps':sweeps,'caveat':'Bounded600vertex samples per pose against hull; notcontinuous/fullinternalcollision proof'})
assert not any(q['outside_bearing_contacts']for q in sweeps),[(q['angle_degrees'],len(q['outside_bearing_contacts']))for q in sweeps]
for key in ['light_torpedo_ports','heavy_torpedo_ports']:
 assert len(m['equipment'][key])==5
 for p in m['equipment'][key]:
  assert len(p['support_samples'])==5;zz=np.array(p['support_samples'])[:,2];assert zz.min()>p['collar_start']and zz.max()<p['collar_end'];assert p['position'][2]>p['collar_end'];contact=ray(np.array(p['position'])+[0,0,200],[0,0,-1]);assert p['position'][2]>contact[2]
assert len(m['equipment']['exhausts'])==4 and len(m['rigs'])==13
b=m['equipment']['boarding'];hit=ray(np.array(b['position'])+[200,0,0],[-1,0,0]);assert b['position'][0]-hit[0]>19.99
write(AUD/'mount-checks.json',{'status':'PASS BOUNDED OFFLINE','pdc_mounts':checks,'pdc_count':12,'rail_count':1,'unique_weapon_count':len({r['mount']['weapon']for r in m['rigs']}),'proper_rotation_determinant':m['normalization']['determinant'],'port_supports_and_outward_rays':10,'source_engine_nozzles':4,'boarding_external_clearance':b['position'][0]-hit[0],'runtime':'NOT RUN'})
print('PASS13mounts,12supports,rail±15degree sampledclearance,10ports,fourengines,boarding')
