"""Preserve supplied frigate wedge; add fitted drive, recessed ports and six PDCs."""
from update27_mars_assets import *
NAME='expanse27_laconia_frigate';raw=Path('/home/haker/Downloads/LaconiaFrigate.stl').read_bytes();t=np.frombuffer(raw[84:],dtype=[('n','<f4',3),('v','<f4',(3,3)),('a','<u2')])['v'].astype(float);lo=t.min((0,1));hi=t.max((0,1));center=(lo+hi)/2;scale=160/(hi[1]-lo[1]);R=np.array([[-1,0,0],[0,0,1],[0,1,0.]])
t=(t-center)@R.T*scale
# Clip exact planes instead of deleting large original triangles by centroid.
def cut(tri,z,positive):
 q=[]
 for j,a in enumerate(tri):
  b=tri[(j+1)%3];da=a[2]-z;db=b[2]-z
  if (da>=-1e-9)if positive else(da<=1e-9):q.append(a)
  if da*db<0:q.append(a+(b-a)*da/(da-db))
 return [[q[0],q[j],q[j+1]]for j in range(1,len(q)-1)]
# Remove the source's closed cylinder tip and replace it with a real open nozzle.
hull=np.array([r for q in t for r in cut(q,-62,True)])
for z in [-38,-31,30,37]:
 hull=np.array([r for q in hull for r in ((cut(q,z,True)+cut(q,z,False))if q[:,2].min()<z-1e-8 and q[:,2].max()>z+1e-8 else[q])])
area=np.linalg.norm(np.cross(hull[:,1]-hull[:,0],hull[:,2]-hull[:,0]),axis=1);hull=hull[area>1e-7]
positions=[([0,0,35],[1,0,0]),([0,0,35],[-1,0,0]),([0,0,-25],[1,0,0]),([0,0,-25],[-1,0,0]),([0,0,-2],[0,1,0]),([0,0,-2],[0,-1,0])];rigs,points,support=pdc(hull,NAME,positions)
# Source cylinder is round and centered; continuous two-ended drive shroud
# overlaps it at-61 and the native nozzle flange at-79.6.
a=np.arange(64)*2*np.pi/64;dirs=np.column_stack([np.cos(a),np.sin(a),np.zeros(64)]);root=[]
for d in dirs:root.append(rayhit(hull,d*100+[0,0,-60],-d))
root=np.array(root);outer=root+dirs*.3;inner=root-dirs*.6;lip=dirs*11.5+[0,0,-79.6];lipin=dirs*10.5+[0,0,-79.6];collar=np.concatenate([rings([lip,outer]),rings([inner,lipin]),rings([outer,inner]),rings([lipin,lip])]);drive=native_drive([0,0,-80],22)
ports=[];extras=[]
for j,x in enumerate([-5.,5.]):
 surface=rayhit(hull,[x,0,100],[0,0,-1]);mouth=surface+[0,0,1.2];extras.append(cylinder(surface-[0,0,.4],mouth,1.45,24,inner=1.05));pt={'name':f'weapon.torpedo.light.{j}','translation':mouth.tolist()};points.append(pt);ports.append({'position':mouth.tolist(),'mesh_point':pt['name'],'up':[0,1,0],'forward':[0,0,1],'measured_surface':surface.tolist()})
# Small fitted sensor ridges and heat-management strips visibly break up the
# low-detail printable surface without pretending to recover missing geometry.
for z in [-47,12,48]:
 surface=rayhit(hull,[0,100,z],[0,-1,0]);extras.append(box(surface+[-3,-.3,-3],surface+[3,1.3,3]))
for x in [-9.,9.]:
 for z in [-20,-15,-10,5,10,15]:
  surface=rayhit(hull,[x,100,z],[0,-1,0]);extras.append(box(surface+[-.6,-.2,-1.2],surface+[.6,.4,1.2]))
mid=hull.mean(1);labels=np.full(len(hull),'armor',dtype='<U8');labels[((mid[:,2]>30)&(mid[:,2]<37))|((mid[:,2]>-38)&(mid[:,2]<-31))]='orange';parts=[frames(hull[labels==k],k,40)for k in ['armor','orange']];parts+=[frames(np.concatenate(support+extras),'dark',35),frames(collar,'dark',55),drive]
points.extend([{'name':'exhaust.0','translation':[0,0,-80.4],'rotation':[0,1,0,0]},{'name':'center','translation':[0,0,0]},{'name':'above','translation':[0,35,0]}]);mesh=save(NAME+'_hull',parts,points);v=np.concatenate([p['v']for p in parts]);lo=v.min(0);hi=v.max(0)
meta={'id':'laconia','hull_mesh':NAME+'_hull','meshes':[mesh],'colors':{k:COLORS[k]for k in ['armor','orange','dark']},'native_materials':{'drive':'expanse24_storm_hull_storm_drive'},'copied_meshes':{NAME+'_pdc_'+k:'expanse24_storm_pdc_'+k for k in ['base','barrel']},'rigs':rigs,'meshpoints':points,'torpedo_ports':{'light':ports},'exhausts':[p for p in points if p['name'].startswith('exhaust')],'spatial':{'radius':float(np.linalg.norm(v,axis=1).max()),'box':{'center':((lo+hi)/2).tolist(),'extents':((hi-lo)/2).tolist()},'collision_rank':1},'source':{'path':'/home/haker/Downloads/LaconiaFrigate.stl','sha256':hashlib.sha256(raw).hexdigest(),'triangles':4294,'source_rotation':R.tolist(),'source_scale':scale,'original_center':center.tolist()},'counts':{'hull':mesh['triangles'],'pdcs':6},'runtime':'NOT RUN','adaptations':['Unnamed fan Laconian frigate; no unverified canonical class identity.','Exactly six native biaxial40mm PDC rigs; private Laconian label is a mod adaptation.','Scirocco-style charcoal/orange livery, original small sensor/heat-management details.','Source closed engine stub replaced with native machinery and continuous capped collar.']};write(AUD/'laconia-integration.json',meta);print('Laconia',mesh['triangles'],'triangles',flush=True)
