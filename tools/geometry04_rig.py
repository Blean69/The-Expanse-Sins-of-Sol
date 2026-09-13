"""Six explicit hero aiming rigs; retains complete source cannon assemblies.
Source deployment roll is not mislabelled as yaw/pitch. New support joints are
clearly derivative engineering geometry, centered on measured cannon blocks.
"""
from common import *
from scipy.spatial.transform import Rotation
from collections import defaultdict
import copy
out=ROOT/'assets/derived/geometry04-b';audit=ROOT/'audit/geometry04-b';data=np.load(out/'parts.npz');rows=read(audit/'parts.json');eq=read(audit/'equipment.json');norm=read(audit/'normalization.json');target=np.array(norm['target_center']);source=Gltf(ROOT/'assets/derived/geometry03-b/hero-master/Rocinante_(The_Expanse).gltf');parts={r['node']:r for r in rows if r['node']};shapes=defaultdict(list);frames={'hero_hull':{'basis':np.eye(3).tolist(),'origin':[0,0,0]}};rigs=[];ownership={};normalreports=[]
def descendants(i):
 result=[i]
 for c in source.g['nodes'][i].get('children',[]):result.extend(descendants(c))
 return result
# Each source assembly repeats the same named cannon+magazine+pins group.
wrappers=[(117,121,124,127,130,147,111),(180,184,187,190,193,207,174),(218,222,225,228,231,245,212),(256,260,263,266,269,283,250),(294,298,301,304,307,321,288),(332,336,339,342,345,359,326)]
def vgroup(root):return np.concatenate([data[parts[n]['key']+'_v'] for n in descendants(root) if n in parts])
def add_face(kind,points,mat=1):
 q=np.array(points);no=np.cross(q[1]-q[0],q[2]-q[0]);no/=np.linalg.norm(no);shapes[kind].append((mat,q,np.tile(no,(3,1))))
def cylinder(kind,p0,p1,radius,mat=1,segments=12,caps=True):
 p0=np.array(p0);p1=np.array(p1);axis=p1-p0;axis/=np.linalg.norm(axis);u=np.eye(3)[np.argmin(abs(axis))];u-=axis*np.dot(u,axis);u/=np.linalg.norm(u);v=np.cross(axis,u);angles=np.arange(segments)*2*np.pi/segments;r=radius*(np.cos(angles)[:,None]*u+np.sin(angles)[:,None]*v);a=p0+r;b=p1+r
 for i in range(segments):
  j=(i+1)%segments
  for q in [np.array([a[i],a[j],b[j]]),np.array([a[i],b[j],b[i]])]:
   no=np.cross(q[1]-q[0],q[2]-q[0]);mid=q.mean(0)-(p0+p1)/2;mid-=axis*np.dot(mid,axis)
   if np.dot(no,mid)<0:q=q[[0,2,1]]
   add_face(kind,q,mat)
  if caps:add_face(kind,np.array([p0,a[j],a[i]]),mat);add_face(kind,np.array([p1,b[i],b[j]]),mat)
for i,roots in enumerate(wrappers):
 fw=np.array(eq['pdc_mounts'][i]['forward']);block=vgroup(roots[-2]);pitch=(block.min(0)+block.max(0))/2;radial=pitch-target;radial[2]=0;up=radial-fw*np.dot(radial,fw);up/=np.linalg.norm(up);right=np.cross(up,fw);B=np.column_stack([right,up,fw]);assert np.linalg.det(B)>.999999
 fixed=vgroup(roots[-1]);fixed_out=float(np.max(fixed@up));yaw=pitch-up*(float(np.dot(pitch,up))-fixed_out+.12);offset=(pitch-yaw)@B;assert .3<offset[1]<5,(i,offset);base=f'hero_pdc_{i}_base';barrel=f'hero_pdc_{i}_barrel';frames[base]={'basis':B.tolist(),'origin':yaw.tolist()};frames[barrel]={'basis':B.tolist(),'origin':pitch.tolist()}
 moving=set()
 for root in roots[:-1]:moving.update(n for n in descendants(root) if n in parts)
 for n in moving:assert n not in ownership;ownership[n]=barrel
 # Original cannon block remains with cannon/mags/pins in pitch assembly.
 # A fixed socket seats in the original deployed slide/frame; new yaw shaft
 # reaches the measured cannon-block center, with local-X trunnion/yokes.
 cylinder('hero_hull',yaw-up*.22,yaw+up*.10,.65)
 cylinder(base,yaw+up*.04,pitch-up*.38,.40)
 for side in [-1,1]:cylinder(base,pitch+right*(side*.95)-up*.50,pitch+right*(side*.95),.20)
 cylinder(base,pitch-right*1.08,pitch+right*1.08,.18)
 cylinder(barrel,pitch-right*.82,pitch+right*.82,.25)
 aliasbase=f'expanse04_hero_pdc_{i}_base';aliasbar=f'expanse04_hero_pdc_{i}_barrel';muzzle=(np.array(eq['pdc_mounts'][i]['muzzle_hull'])-pitch)@B;mount={'weapon':f'expanse_rocinante04_pdc_{i}','mesh_point':'child.'+aliasbase,'weapon_position':yaw.tolist(),'forward':fw.tolist(),'up':up.tolist(),'yaw_arc':{'min_angle':-90.,'max_angle':90.},'pitch_arc':{'min_angle':-65.,'max_angle':10.}}
 rigs.append({'index':i,'mount':mount,'basis_columns':B.tolist(),'yaw_pivot_hull':yaw.tolist(),'pitch_pivot_hull':pitch.tolist(),'muzzle_hull':eq['pdc_mounts'][i]['muzzle_hull'],'turret_override':{'type':'biaxial','biaxial_base_mesh':aliasbase,'biaxial_barrel_mesh':aliasbar,'barrel_position':offset.tolist(),'muzzle_positions':[muzzle.tolist()]},'skin_alias_map':[{'mesh_alias_name':aliasbase,'mesh_definition':{'mesh':aliasbase,'shader':'ship','is_shadow_blocker':True}},{'mesh_alias_name':aliasbar,'mesh_definition':{'mesh':aliasbar,'shader':'ship','is_shadow_blocker':True}}],'source_moving_nodes':sorted(moving),'fixed_source_housing_node':roots[-1],'pivot_evidence':'Pitch at deployed actual cannon2 mounting-block bounds center; yaw on matching deployed pdc1 outer surface. Added socket/shaft/yoke support connects both. These are authored aiming joints, not claimed source deployment joints.','runtime':'NOT RUN; arc/occlusion/clearance require workstation inspection'})
# Reconstruct geometric normals on the corrective topology with a30deg crease.
# Retained0.3 normals were interpolated across collapsed hard edges; recalculating
# from the actual faces avoids projecting that old shading error onto new faces.
def normals_for(v,idx,old):
 tri=v[idx];cross=np.cross(tri[:,1]-tri[:,0],tri[:,2]-tri[:,0]);area=np.linalg.norm(cross,axis=1);edge2=np.maximum.reduce([np.sum((tri[:,1]-tri[:,0])**2,axis=1),np.sum((tri[:,2]-tri[:,0])**2,axis=1),np.sum((tri[:,2]-tri[:,1])**2,axis=1)]);keep=(area>1e-7)&(area/np.maximum(edge2,1e-12)>1e-6);removed=int(sum(~keep));idx=idx[keep];tri=tri[keep];cross=cross[keep];area=area[keep];face=cross/np.maximum(area[:,None],1e-12);oldface=old[idx].mean(1);flip=np.sum(face*oldface,axis=1)<0;idx=idx.copy();idx[flip]=idx[flip][:,[0,2,1]];cross[flip]*=-1;face[flip]*=-1;tri=v[idx]
 rounded=np.round(v,5);_,inverse=np.unique(rounded,axis=0,return_inverse=True);adj=defaultdict(list)
 for fi,ids in enumerate(inverse[idx]):
  for vi in set(ids):adj[int(vi)].append(fi)
 N=np.empty((len(idx),3,3))
 for fi,ids in enumerate(inverse[idx]):
  for corner,vi in enumerate(ids):
   neighbors=adj[int(vi)];keep=[j for j in neighbors if np.dot(face[fi],face[j])>=.8660254];val=cross[keep].sum(0);ln=np.linalg.norm(val);N[fi,corner]=val/ln if ln>1e-12 else old[idx[fi,corner]]
 return tri,N,removed
for r in rows:
 key=r['key'];v=data[key+'_v'];old=data[key+'_n'];idx=data[key+'_i'];tri,N,deg=normals_for(v,idx,old);kind=ownership.get(r['node'],'hero_hull');normalreports.append({'source_node':r['node'],'triangles':len(tri),'removed_numerically_degenerate_triangles':deg,'assigned_to':kind});shapes[kind].append((r['material'],tri.reshape(-1,3),N.reshape(-1,3)))
# Existing rail/exhaust/ability anchor points transform rigidly with physical hull.
oldmeta=read(ROOT/'audit/geometry03-b/hero-armed-mount-metadata.json');R=np.array(norm['old_game_to_new_game_rotation']);points=[]
for p in oldmeta['meshpoints']['hero_armed']:
 if p['name'].startswith('weapon.pdc.'):continue
 q=copy.deepcopy(p);q['translation']=((np.array(q['translation'])-target)@R.T+target).tolist();rot=R@Rotation.from_quat(q.get('rotation',[0,0,0,1])).as_matrix();q['rotation']=Rotation.from_matrix(rot).as_quat().tolist();points.append(q)
for r in rigs:points.append({'name':r['mount']['mesh_point'],'translation':r['yaw_pivot_hull'],'rotation':Rotation.from_matrix(r['basis_columns']).as_quat().tolist()})
meshpoints={'hero_hull':points};counts={};sourceframes={};matmaster=read(ROOT/'audit/geometry03-b/hero-mount-metadata.json')['materialspec']
for kind,frame in frames.items():
 B=np.array(frame['basis']);origin=np.array(frame['origin']);name='expanse04_'+kind;g={'asset':{'version':'2.0','generator':'Hero04 explicit aiming derivative; compiler Z compensation'},'scene':0,'scenes':[{'nodes':[0]}],'nodes':[{'name':name,'mesh':0,'children':[]}],'meshes':[{'name':name,'primitives':[]}],'buffers':[],'bufferViews':[],'accessors':[],'materials':[]};buf=bytearray();sourceframes[kind]={};count=0
 def acc(v,typ,ct=5126):
  v=np.asarray(v,dtype='<f4' if ct==5126 else '<u4');buf.extend(b'\0'*((-len(buf))%4));start=len(buf);buf.extend(v.tobytes());g['bufferViews'].append({'buffer':0,'byteOffset':start,'byteLength':v.nbytes});at={'bufferView':len(g['bufferViews'])-1,'componentType':ct,'count':len(v),'type':typ}
  if typ=='VEC3':at.update(min=v.min(0).tolist(),max=v.max(0).tolist())
  g['accessors'].append(at);return len(g['accessors'])-1
 usedmats=sorted(set(q[0] for q in shapes[kind]))
 for localmat,mat in enumerate(usedmats):
  vv=np.concatenate([q[1] for q in shapes[kind] if q[0]==mat]);nn=np.concatenate([q[2] for q in shapes[kind] if q[0]==mat]);pos=(vv-origin)@B;no=nn@B;no/=np.linalg.norm(no,axis=1)[:,None];axis=np.eye(3)[np.argmin(abs(no),axis=1)];t=axis-no*np.sum(axis*no,axis=1)[:,None];t/=np.linalg.norm(t,axis=1)[:,None];tang=np.column_stack([t,np.ones(len(t))]);uv=np.zeros((len(pos),2));idx=np.arange(len(pos),dtype=np.uint32);count+=len(pos)//3;sourceframes[kind][str(localmat)]={'positions':pos.tolist(),'normals':no.tolist(),'tangents':tang.tolist(),'uv':uv.tolist()}
  for ar in [pos,no,tang]:ar[:,2]*=-1
  tang[:,3]*=-1;g['materials'].append({'name':f'expanse03_hero_mat_{mat}','pbrMetallicRoughness':{'baseColorFactor':[1,1,1,1],'metallicFactor':1,'roughnessFactor':1}});g['meshes'][0]['primitives'].append({'attributes':{'POSITION':acc(pos,'VEC3'),'NORMAL':acc(no,'VEC3'),'TANGENT':acc(tang,'VEC4'),'TEXCOORD_0':acc(uv,'VEC2')},'indices':acc(idx,'SCALAR',5125),'material':localmat,'mode':4})
 meshpoints.setdefault(kind,[])
 for p in meshpoints[kind]:
  cp=copy.deepcopy(p);cp['translation'][2]*=-1
  if 'rotation' in cp:cp['rotation'][0]*=-1;cp['rotation'][1]*=-1
  g['nodes'][0]['children'].append(len(g['nodes']));g['nodes'].append(cp)
 g['buffers']=[{'uri':name+'.bin','byteLength':len(buf)}];(out/(name+'.bin')).write_bytes(buf);write(out/(name+'.gltf'),g);counts[kind]=count
write(out/'retained-source-frames.json',sourceframes);write(audit/'normal-repair.json',normalreports);write(audit/'mount-metadata.json',{'status':'GENERATED CANDIDATE; COMPILER CHECKS PENDING','rigs':rigs,'frames':frames,'meshpoints':meshpoints,'counts':counts,'triangle_total':sum(counts.values()),'normalization':norm,'equipment':eq,'custom_railgun':eq['railgun'],'exhaust_geometry':eq['exhaust'],'materialspec':matmaster,'source_assignment':normalreports,'aiming_vs_deployment':'Source animation30deg rotates around barrel direction, not a suitable aiming pivot. New explicit aiming joints centered on measured blocks and supported by added geometry; source cannon+magazine+pin group stays intact.'});print('Generated13 meshes',sum(counts.values()),counts,flush=True)
