"""Add explicitly custom prototype weapons to the separate static hero derivative.
These are new fittings, not claims about the source asset's antenna identities.
"""
from common import *
import copy
src=ROOT/'assets/derived/geometry03-b/hero';out=ROOT/'assets/derived/geometry03-b/hero-armed';out.mkdir(exist_ok=True);audit=ROOT/'audit/geometry03-b';cg=read(src/'expanse03_hero_static.gltf');a=Gltf(src/'expanse03_hero_static.gltf');buf=bytearray(a.buffers[0]);meta=read(audit/'hero-mount-metadata.json');equipment=read(audit/'hero-equipment-mounts.json');frames=read(src/'retained-source-frames.json')['hero_static'];cloud=np.concatenate([np.array(r['positions']) for r in frames.values()]);geometry=[]
def face(points,mat=1):
 q=np.array(points,dtype=float);n=np.cross(q[1]-q[0],q[2]-q[0]);n/=np.linalg.norm(n);axis=np.eye(3)[np.argmin(abs(n))];t=axis-n*np.dot(axis,n);t/=np.linalg.norm(t);geometry.append((mat,q,np.tile(n,(3,1)),np.tile([*t,1.],(3,1)),np.zeros((3,2))))
def box(lo,hi,mat=1):
 lo=np.minimum(lo,hi);hi=np.maximum(lo,hi);v=np.array([[x,y,z] for x in [lo[0],hi[0]] for y in [lo[1],hi[1]] for z in [lo[2],hi[2]]]);center=(lo+hi)/2
 for ids in [[0,1,3,2],[4,6,7,5],[0,4,5,1],[2,3,7,6],[0,2,6,4],[1,5,7,3]]:
  q=v[ids];n=np.cross(q[1]-q[0],q[2]-q[0]);q=q if np.dot(n,q.mean(0)-center)>0 else q[::-1];face(q[[0,1,2]],mat);face(q[[0,2,3]],mat)
def tube(center,radius,length,segments=8):
 center=np.array(center);front=center+[0,0,length/2];back=center-[0,0,length/2];dirs=np.array([[np.cos(t),np.sin(t),0] for t in np.arange(segments)*2*np.pi/segments]);outer=[back+radius*dirs,front+radius*dirs];inner=[back+radius*.62*dirs,front+radius*.62*dirs]
 for j in range(segments):
  k=(j+1)%segments
  # Outer/inner surfaces and annular open muzzle; rear dark cap is recessed.
  for q,mat in [(np.array([outer[0][j],outer[0][k],outer[1][k],outer[1][j]]),1),(np.array([inner[0][k],inner[0][j],inner[1][j],inner[1][k]]),0),(np.array([outer[1][j],outer[1][k],inner[1][k],inner[1][j]]),1)]:face(q[[0,1,2]],mat);face(q[[0,2,3]],mat)
  face(np.array([back,inner[0][k],inner[0][j]]),0)
def surface(x,z,top):
 zone=cloud[(abs(cloud[:,0]-x)<2)&(abs(cloud[:,2]-z)<3)];assert len(zone)>10,(x,z,'no local hull samples');return float(zone[:,1].max() if top else zone[:,1].min())
# Fit the rail to actual fore-keel samples; two pylons connect the housing.
rail_y=min(surface(0,20,False),surface(0,28,False))-1.0;rail_center=[0,rail_y,31.];tube(rail_center,.5,18.,8);box([-1.0,rail_y-.7,19.],[1.0,rail_y+.7,25.])
for z in [21.,27.]:
 sy=surface(0,z,False);lo=np.array([-.45,min(rail_y+.35,sy)-.05,z-.7]);hi=np.array([.45,max(rail_y+.35,sy)+.2,z+.7]);box(lo,hi)
rail={'position':[0,rail_y,40.12],'forward':[0,0,1],'up':[0,1,0],'mesh_point':'weapon.rail.0','source':'CUSTOM prototype keel railgun added to hero derivative; not a relabelled source antenna','mount_hull_surface_samples':[surface(0,20,False),surface(0,28,False)]}
ports=[]
for label,x,top in [('dorsal',0.,True),('ventral',3.,False)]:
 z=12.;sy=surface(x,z,top);cy=sy+(.8 if top else -.8);tube([x,cy,z],.72,2.0,8);box([x-.85,min(sy,cy)-.1,z-.9],[x+.85,max(sy,cy)+.1,z+.4]);ports.append({'name':label,'position':[x,cy,z+1.12],'forward':[0,0,1],'up':[0,1,0],'source':'CUSTOM prototype launch fitting on measured hero forebody surface','hull_surface_y':sy,'nearest_PDC_muzzle_distance':float(min(np.linalg.norm(np.array([x,cy,z])-r['muzzle_hull']) for r in equipment['pdc_mounts']))})
name='expanse03_hero_armed';cg['nodes'][0]['name']=name;cg['meshes'][0]['name']=name
# Append and then group compiler primitives by material; source UVs untouched.
def acc(v,typ,ct=5126):
 v=np.asarray(v,dtype='<f4' if ct==5126 else '<u4');buf.extend(b'\0'*((-len(buf))%4));start=len(buf);buf.extend(v.tobytes());cg['bufferViews'].append({'buffer':0,'byteOffset':start,'byteLength':v.nbytes});at={'bufferView':len(cg['bufferViews'])-1,'componentType':ct,'count':len(v),'type':typ}
 if typ=='VEC3':at.update(min=v.min(0).tolist(),max=v.max(0).tolist())
 cg['accessors'].append(at);return len(cg['accessors'])-1
for mi in sorted(set(q[0] for q in geometry)):
 chosen=[q for q in geometry if q[0]==mi];pos=np.concatenate([q[1] for q in chosen]);norm=np.concatenate([q[2] for q in chosen]);tang=np.concatenate([q[3] for q in chosen]);uv=np.concatenate([q[4] for q in chosen]);idx=np.arange(len(pos),dtype=np.uint32)
 for key,v in [('positions',pos),('normals',norm),('tangents',tang),('uv',uv)]:frames[str(mi)][key].extend(v.tolist())
 for ar in [pos,norm,tang]:ar[:,2]*=-1
 tang[:,3]*=-1;cg['meshes'][0]['primitives'].append({'attributes':{'POSITION':acc(pos,'VEC3'),'NORMAL':acc(norm,'VEC3'),'TANGENT':acc(tang,'VEC4'),'TEXCOORD_0':acc(uv,'VEC2')},'indices':acc(idx,'SCALAR',5125),'material':mi,'mode':4})
cg['buffers']=[{'uri':name+'.bin','byteLength':len(buf)}];(out/(name+'.bin')).write_bytes(buf);write(out/(name+'.gltf'),cg);aa=Gltf(out/(name+'.gltf'));oldpr=cg['meshes'][0]['primitives'];cg['meshes'][0]['primitives']=[]
for mi in sorted(set(p['material'] for p in oldpr)):
 vals={key:[] for key in ['POSITION','NORMAL','TANGENT','TEXCOORD_0']};indices=[];offset=0
 for p in [p for p in oldpr if p['material']==mi]:
  for key in vals:vals[key].append(aa.accessor(p['attributes'][key]))
  indices.append(aa.accessor(p['indices']).flatten()+offset);offset+=len(vals['POSITION'][-1])
 cg['meshes'][0]['primitives'].append({'attributes':{key:acc(np.concatenate(v),'VEC4' if key=='TANGENT' else 'VEC2' if key=='TEXCOORD_0' else 'VEC3') for key,v in vals.items()},'indices':acc(np.concatenate(indices),'SCALAR',5125),'material':mi,'mode':4})
points=copy.deepcopy(meta['meshpoints']['hero_static'])
for point in points:
 if point['name'].startswith('weapon.hero_pdc_'):point['name']=point['name'].replace('weapon.hero_pdc_','weapon.pdc.')
points.append({'name':'weapon.rail.0','translation':rail['position']});cg['nodes']=cg['nodes'][:1];cg['nodes'][0]['children']=[]
for point in points:
 cp=copy.deepcopy(point);cp['translation'][2]*=-1
 if 'rotation' in cp:cp['rotation'][0]*=-1;cp['rotation'][1]*=-1
 cg['nodes'][0]['children'].append(len(cg['nodes']));cg['nodes'].append(cp)
cg['buffers'][0]['byteLength']=len(buf);(out/(name+'.bin')).write_bytes(buf);write(out/(name+'.gltf'),cg);write(out/'retained-source-frames.json',{'hero_armed':frames});new=copy.deepcopy(meta);new.pop('outputs',None);new['status']='ARMED HERO STATIC VISUAL CANDIDATE; custom prototype fittings; runtime NOT RUN';new['counts']={'hero_armed':meta['triangle_total']+len(geometry)};new['triangle_total']=sum(new['counts'].values());new['frames']={'hero_armed':{'basis':np.eye(3).tolist(),'origin':[0,0,0]}};new['meshpoints']={'hero_armed':points};new['custom_railgun']=rail;new['custom_torpedo_ports']=ports;new['custom_added_triangles']=len(geometry)
for r in new['measured_static_weapon_mounts']:r['mesh_point']=f'weapon.pdc.{r["index"]}'
write(audit/'hero-armed-mount-metadata.json',new);write(audit/'hero-armed-equipment.json',{'pdc_mounts':new['measured_static_weapon_mounts'],'railgun':rail,'torpedo_ports':ports,'exhaust':equipment['exhaust'],'runtime':'NOT RUN','custom_fittings_not_screen_accuracy_claim':True});print('Armed hero',new['triangle_total'],'triangles; new custom fitting triangles',len(geometry))
