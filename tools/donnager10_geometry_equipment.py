from donnager10_geometry_common import *
z=np.load(OUT/'optimized.npz');rows=read(AUDIT/'optimized-parts.json')['parts'];tri=np.concatenate([z[r['key']+'_v'][z[r['key']+'_i']] for r in rows if r['node'] not in [33,34,35,36]]);lo=tri.min(1);hi=tri.max(1)
def zhit(x,y,positive=True):
 mask=(lo[:,0]<=x)&(hi[:,0]>=x)&(lo[:,1]<=y)&(hi[:,1]>=y);tt=tri[mask];xy=tt[:,:,:2];p=np.array([x,y]);e1=xy[:,1]-xy[:,0];e2=xy[:,2]-xy[:,0];d=p-xy[:,0];det=e1[:,0]*e2[:,1]-e1[:,1]*e2[:,0];valid=abs(det)>1e-12;u=np.divide(d[:,0]*e2[:,1]-d[:,1]*e2[:,0],det,out=np.zeros(len(tt)),where=valid);v=np.divide(e1[:,0]*d[:,1]-e1[:,1]*d[:,0],det,out=np.zeros(len(tt)),where=valid);good=valid&(u>=0)&(v>=0)&(u+v<=1);depth=tt[:,0,2]+u*(tt[:,1,2]-tt[:,0,2])+v*(tt[:,2,2]-tt[:,0,2]);return float(np.max(depth[good]) if positive else np.min(depth[good])) if good.any() else None
# Main's actual source aperture-component measurements, read-only.
comp=read(Path('/run/media/haker/NVME 2/expanse-mod/audit/donnager10/aperture-components.json'));heavy=[]
for c in comp:
 if c['node']==60 and 6.8<c['dimensions'][0]<7 and abs(c['center'][0])>70:
  p=(np.array(c['center'])-center)*scale;p[2]-=.2;back=zhit(p[0],p[1],False);heavy.append({'position':p.tolist(),'up':[0,1,0],'forward':[0,0,-1],'source_component':c,'outward_axis_first_surface':back,'axis_clearance':None if back is None else p[2]-back,'classification':'Measured actual aft circular dark aperture, assigned heavy launcher for prototype; source weapon label absent'})
assert len(heavy)==4
# Forebody has no separately identified source tubes. Add two modest short
# collars on actual extreme bow surfaces at ±X, keeping original hull intact.
light=[]
for x in [-18.,18.]:
 y=0.;samples=[zhit(x+dx,y+dy,True) for dx,dy in [(0,0),(-2.4,-2.4),(-2.4,2.4),(2.4,-2.4),(2.4,2.4)]]
 if any(p is None for p in samples):
  y=24.;samples=[zhit(x+dx,y+dy,True) for dx,dy in [(0,0),(-2.4,-2.4),(-2.4,2.4),(2.4,-2.4),(2.4,2.4)]]
 assert all(p is not None for p in samples),(x,y,samples);end=max(samples)+3.;light.append({'position':[x,y,end+.1],'up':[0,1,0],'forward':[0,0,1],'custom_collar':{'center':[x,y,end],'start_z':min(samples)-.3,'end_z':end,'outer_radius':2.4,'inner_radius':1.8,'support_sample_z':samples},'classification':'New short prototype light tube on measured bow surface, not claimed canonical source aperture'})
hatch=next(c for c in comp if c['node']==65 and c['dimensions'][0]>90);hp=(np.array(hatch['center'])-center)*scale;surface=zhit(hp[0],hp[1],False);assert surface is not None;hp[2]=surface-60.;hangar={'position':hp.tolist(),'forward':[0,0,-1],'up':[0,1,0],'mouth_position':[float(hp[0]),float(hp[1]),surface-.1],'source_hatch':hatch,'clearance_from_static_hatch':60.0,'classification':'Actual central aft99-source-unit hatch reference; corvette spawn outside closed static hatch, no door animation or open passage claimed'}
write(AUDIT/'main-equipment.json',{'light_torpedo_ports':light,'heavy_torpedo_ports':heavy,'hangar':hangar});print('Measured front2 customcollars, aft4actualapertures, centralhatch:',json.dumps({'light':light,'heavy_axis_clearance':[h['axis_clearance'] for h in heavy],'hangar':hangar},indent=2))
