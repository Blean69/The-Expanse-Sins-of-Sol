"""Incremental0.3 geometry: targeted shell interiors and physical turret supports.
Prior polish meshes and shared sources remain read-only.
"""
from common import *
import copy,shutil,json
old=ROOT/'assets/derived/polish-b';out=ROOT/'assets/derived/geometry03-b/corvette';out.mkdir(parents=True,exist_ok=True);audit=ROOT/'audit/geometry03-b';audit.mkdir(exist_ok=True);meta=read(ROOT/'audit/polish-b/mount-metadata.json');source=Path(meta['source_root']);a=Gltf(source/'assets/derived/baseline/mcrn_editable.gltf');frames=read(old/'retained-source-frames.json');newmeta=copy.deepcopy(meta);newmeta.pop('outputs',None);newmeta['status']='CANDIDATE awaiting03 compile';counts=copy.deepcopy(meta['counts']);changes={};uv=np.array([.4906005859375,.4942626953125]);groups={k:[] for k in counts}
# Each generated triangle has independent vertices and a valid authored frame.
def addtri(kind,points,norm=None,mat=0,uvs=None,tang=None):
 p=np.asarray(points,dtype=float);n=np.cross(p[1]-p[0],p[2]-p[0]) if norm is None else np.asarray(norm,dtype=float);n=n/np.linalg.norm(n);n=np.tile(n,(3,1)) if n.ndim==1 else n
 if tang is None:
  axis=np.eye(3)[np.argmin(abs(n[0]))];t=axis-n[0]*np.dot(axis,n[0]);t/=np.linalg.norm(t);t=np.tile([*t,1],(3,1))
 else:t=np.asarray(tang)
 groups[kind].append((mat,p,n,t,np.tile(uv,(3,1)) if uvs is None else np.asarray(uvs)))
def box(kind,lo,hi,transform=None):
 lo=np.array(lo);hi=np.array(hi);v=np.array([[x,y,z] for x in [lo[0],hi[0]] for y in [lo[1],hi[1]] for z in [lo[2],hi[2]]]);center=(lo+hi)/2
 for ids in [[0,1,3,2],[4,6,7,5],[0,4,5,1],[2,3,7,6],[0,2,6,4],[1,5,7,3]]:
  q=v[ids];normal=np.cross(q[1]-q[0],q[2]-q[0]);
  if np.dot(normal,q.mean(0)-center)<0:q=q[::-1]
  if transform:q=q@transform[0].T+transform[1]
  addtri(kind,q[[0,1,2]]);addtri(kind,q[[0,2,3]])
def cylinder(kind,center,axis,radius,length,segments=8,transform=None):
 center=np.array(center);axis=np.array(axis,dtype=float);axis/=np.linalg.norm(axis);u=np.eye(3)[np.argmin(abs(axis))];u=np.cross(axis,u);u/=np.linalg.norm(u);v=np.cross(axis,u);rings=[np.array([center+axis*h+radius*(u*np.cos(t)+v*np.sin(t)) for t in np.arange(segments)*2*np.pi/segments]) for h in [-length/2,length/2]]
 for j in range(segments):
  k=(j+1)%segments
  for pp in [np.array([rings[0][j],rings[0][k],rings[1][k]]),np.array([rings[0][j],rings[1][k],rings[1][j]]),np.array([center-axis*length/2,rings[0][k],rings[0][j]]),np.array([center+axis*length/2,rings[1][j],rings[1][k]])]:
   if transform:pp=pp@transform[0].T+transform[1]
   addtri(kind,pp)
# Targeted double-sided surface semantics only for these seven source shells.
shells=[18,22,78,110,192,410,412];shellcounts=[]
for ni in shells:
 n=a.g['nodes'][ni];total=0
 for p in a.g['meshes'][n['mesh']]['primitives']:
  mi=p['material'];assert a.g['materials'][mi].get('doubleSided') is True
  pos=a.positions(ni,p);m=a.world[ni];normal=a.accessor(p['attributes']['NORMAL'])@np.linalg.inv(m[:3,:3]);normal/=np.linalg.norm(normal,axis=1)[:,None];uv0=a.accessor(p['attributes']['TEXCOORD_0']);t=a.accessor(p['attributes']['TANGENT']);t[:,:3]=t[:,:3]@m[:3,:3].T;t[:,:3]/=np.linalg.norm(t[:,:3],axis=1)[:,None]
  if np.linalg.det(m[:3,:3])<0:t[:,3]*=-1
  idx=a.accessor(p['indices']).flatten().reshape(-1,3)
  for ii in idx:
   q=pos[ii];nn=-normal[ii];tt=t[ii].copy();tt[:,3]*=-1;groups['hull'].append((mi,q,nn,tt,uv0[ii]));total+=1
 shellcounts.append({'node':ni,'name':n['name'],'interior_triangles':total,'source_double_sided':True})
for r in meta['rigs']:
 i=r['index'];k=f'pdc_{i}_base';po=np.array(r['turret_override']['barrel_position']);B=np.array(r['basis_columns']);origin=np.array(r['yaw_pivot_hull']);
 # Fixed hull socket and yaw pedestal overlap at the same mechanical origin.
 cylinder('hull',[0,-.33,0],[0,1,0],1.25,.7,transform=(B,origin));cylinder(k,[0,-.02,0],[0,1,0],1.15,.4)
 for x in [-1.16,1.16]:box(k,[x-.16,-.1,po[2]-.19],[x+.16,po[1]+.16,po[2]+.19])
 cylinder(k,po,[1,0,0],.32,2.65);cylinder(f'pdc_{i}_barrel',[0,0,0],[1,0,0],.25,2.3)
for kind,additions in groups.items():
 oldname='expanse_polish_'+kind;name='expanse03_'+kind;cg=read(old/(oldname+'.gltf'));buf=bytearray((old/(oldname+'.bin')).read_bytes());cg['nodes'][0]['name']=name;cg['meshes'][0]['name']=name;newmeta['counts'][kind]+=len(additions);changes[kind]={'added_triangles':len(additions)}
 def acc(v,typ,ct=5126):
  v=np.asarray(v,dtype='<f4' if ct==5126 else '<u4');buf.extend(b'\0'*((-len(buf))%4));start=len(buf);buf.extend(v.tobytes());cg['bufferViews'].append({'buffer':0,'byteOffset':start,'byteLength':v.nbytes});at={'bufferView':len(cg['bufferViews'])-1,'componentType':ct,'count':len(v),'type':typ}
  if typ=='VEC3':at.update(min=v.min(0).tolist(),max=v.max(0).tolist())
  cg['accessors'].append(at);return len(cg['accessors'])-1
 # Append distinct primitives; repeated material IDs are supported by compiler.
 for mi in sorted(set(x[0] for x in additions)):
  chosen=[x for x in additions if x[0]==mi];pos=np.concatenate([x[1] for x in chosen]);normal=np.concatenate([x[2] for x in chosen]);tang=np.concatenate([x[3] for x in chosen]);uvs=np.concatenate([x[4] for x in chosen]);idx=np.arange(len(pos)).reshape(-1,3);q=pos[idx];dot=np.sum(np.cross(q[:,1]-q[:,0],q[:,2]-q[:,0])*normal[idx].mean(1),axis=1);flip=dot<0;idx[flip]=idx[flip][:,[0,2,1]]
  # Preserve source frames for final tangent repair (game coordinates).
  existing=frames[kind].setdefault(str(mi),{'positions':[],'normals':[],'tangents':[],'uv':[]})
  for key,arr in [('positions',pos),('normals',normal),('tangents',tang),('uv',uvs)]:existing[key].extend(arr.tolist())
  for arr in [pos,normal,tang]:arr[:,2]*=-1
  tang[:,3]*=-1
  cg['meshes'][0]['primitives'].append({'attributes':{'POSITION':acc(pos,'VEC3'),'NORMAL':acc(normal,'VEC3'),'TANGENT':acc(tang,'VEC4'),'TEXCOORD_0':acc(uvs,'VEC2')},'indices':acc(idx.flatten(),'SCALAR',5125),'material':mi,'mode':4})
 # Make one primitive per material, preserving original triangles and authored
 # attributes. This keeps the already verified per-material compiler mapping.
 cg['buffers'][0]={'uri':name+'.bin','byteLength':len(buf)};(out/(name+'.bin')).write_bytes(buf);write(out/(name+'.gltf'),cg)
 # Merge duplicates only in compiler derivative by material (not source master).
 aa=Gltf(out/(name+'.gltf'));oldpr=cg['meshes'][0]['primitives'];cg['meshes'][0]['primitives']=[]
 for mi in sorted(set(p['material'] for p in oldpr)):
  pp=[p for p in oldpr if p['material']==mi];vals={key:[] for key in ['POSITION','NORMAL','TANGENT','TEXCOORD_0']};ii=[];offset=0
  for p in pp:
   for key in vals:vals[key].append(aa.accessor(p['attributes'][key]))
   ii.append(aa.accessor(p['indices']).flatten()+offset);offset+=len(vals['POSITION'][-1])
  cg['meshes'][0]['primitives'].append({'attributes':{key:acc(np.concatenate(v),'VEC4' if key=='TANGENT' else 'VEC2' if key=='TEXCOORD_0' else 'VEC3') for key,v in vals.items()},'indices':acc(np.concatenate(ii),'SCALAR',5125),'material':mi,'mode':4})
 cg['buffers'][0]['byteLength']=len(buf);(out/(name+'.bin')).write_bytes(buf);write(out/(name+'.gltf'),cg)
for r in newmeta['rigs']:
 for binding in r['skin_alias_map']:binding['mesh_definition']['mesh']=binding['mesh_definition']['mesh'].replace('expanse_polish_','expanse03_')
newmeta['triangle_total']=sum(newmeta['counts'].values());newmeta['changes03']=changes;newmeta['targeted_shell_backings']=shellcounts;newmeta['support_uv']={'uv':uv.tolist(),'source_color_rgb':[32,33,35],'source_normal_rgb':[128,127,255],'material':'mcrn_tachi_material'};newmeta['previous_runtime_observation']='User reports06polish PDCs track and tracers look good; pivots/muzzle offsets unchanged by03';newmeta['corvette_original_triangles']=14622;write(out/'retained-source-frames.json',frames);write(audit/'mount-metadata.json',newmeta)
# Two doors/front planes in actual named torpedo bay: dorsal and ventral.
front=[]
for top in [True,False]:
 p=a.g['meshes'][a.g['nodes'][192]['mesh']]['primitives'][0];v=a.positions(192,p);v=v[v[:,1]>-10] if top else v[v[:,1]<-10];center=(v.min(0)+v.max(0))/2;normal=np.array([0,1 if top else -1,1.164754]);normal/=np.linalg.norm(normal);center+=normal*.2;front.append({'name':'dorsal' if top else 'ventral','weapon_position':center.tolist(),'forward':normal.tolist(),'up':np.cross(normal,[1,0,0]).tolist(),'source_nodes':[22,192,194,196,198,200],'status':'Named bay front-plane center estimate; closed hatch geometry, not verified open throat'})
write(audit/'torpedo-mounts.json',{'mounts':front,'source_geometry':'hull_middle_torpedo_bay / hull_middle_torpedo_bay_front','runtime':'NOT RUN','note':'Model contains front/hatch surfaces; launch-clearance and projectile/effect alignment require runtime verification.'})
print('03 total',newmeta['triangle_total'],'additions',newmeta['triangle_total']-14622)
