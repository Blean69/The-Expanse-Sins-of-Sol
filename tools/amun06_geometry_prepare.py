"""Seven-part Amun plus separate compact boarding-pod appearance.
No source optimization. Exact source yaw/pitch joints; explicit three-gun selection.
"""
from amun06_geometry_common import *
from scipy.spatial.transform import Rotation
from PIL import Image
import copy,hashlib
from collections import defaultdict
for d in [OUT,AUDIT,BUILD]:d.mkdir(exist_ok=True)
C=np.array([[-1.,0,0],[0,0,1],[0,1,0]]);central=[r for i in descendants(3) for r in arrays(i)];vv=np.concatenate([r['v'] for r in central]);lo=vv.min(0);hi=vv.max(0);center=(lo+hi)/2;target_length=104.986959*61.5/46;factor=target_length/(hi[1]-lo[1]);target=np.array([0.,-10.112395,3.162117]);
def point(p):return (np.asarray(p)-center)@C.T*factor+target
def direction(p):return C@np.asarray(p)
def normalized(M):
 R=M[:3,:3].copy();R/=np.linalg.norm(R,axis=0);return R
shapes=defaultdict(list);frames={'amun_hull':{'basis':np.eye(3).tolist(),'origin':[0,0,0]}};selected=[892,910,946];omitted=928;rigs=[];ownership=[]
def add(kind,r,custom_v=None,custom_n=None,custom_t=None):
 v=point(r['v']) if custom_v is None else custom_v;n=r['n']@C.T if custom_n is None else custom_n;t=r['t'].copy() if custom_t is None else custom_t.copy()
 if custom_t is None:t[:,:3]=t[:,:3]@C.T
 shapes[kind].append({'v':v,'n':n,'t':t,'uv':r['uv'],'i':r['i'],'node':r['node']});ownership.append({'node':r['node'],'part':kind,'triangles':len(r['i'])})
# Central hull and all actual fixed source door groups. Floating posed equipment
# and the fourth PDC are excluded, not baked into ship bounds.
for root in [3,7,12,17,20,23,26,29,32,35,38,41,44]:
 for ni in descendants(root):
  for r in arrays(ni):add('amun_hull',r)
for i,root in enumerate(selected):
 yawnode=root+3;pitchnode=root+8;barrelnode=root+13;padnode=root+2;basemeshroot=root+4;YM=matrix(yawnode);PM=matrix(pitchnode);YR=normalized(YM);yaw=point(YM[:3,3]);pitch=point(PM[:3,3]);# Source yaw is localZ, pitch localX. Game localY is yaw axis.
 B=C@YR@np.array([[1.,0,0],[0,0,-1],[0,1,0]]);up=B[:,1];fw=B[:,2];base=f'amun_pdc_{i}_base';barrel=f'amun_pdc_{i}_barrel';frames[base]={'basis':B.tolist(),'origin':yaw.tolist()};frames[barrel]={'basis':B.tolist(),'origin':pitch.tolist()}
 for r in arrays(padnode):add('amun_hull',r)
 for ni in descendants(basemeshroot):
  for r in arrays(ni):add(base,r)
 localrows=[q for ni in descendants(pitchnode) for q in arrays(ni,np.linalg.inv(a.world[pitchnode]))]
 for r in localrows:
  v=r['v']@B.T*factor+pitch;n=r['n']@B.T;t=r['t'].copy();t[:,:3]=t[:,:3]@B.T;add(barrel,r,v,n,t)
 # Full muzzle ring in source pitch frame at actual barrel extremum.
 muzzlelocal=np.concatenate([r['v'] for ni in descendants(barrelnode) for r in arrays(ni,np.linalg.inv(a.world[pitchnode]))]);tip=muzzlelocal[muzzlelocal[:,2]>muzzlelocal[:,2].max()-.0001];mc=(tip.min(0)+tip.max(0))/2;mc[2]+=.015;muzzle=pitch+B@(mc*factor);offset=(pitch-yaw)@B;aliasbase='expanse06_'+base;aliasbarrel='expanse06_'+barrel
 mount={'weapon':f'expanse06_amun_pdc_{i}','mesh_point':'child.'+aliasbase,'weapon_position':yaw.tolist(),'up':up.tolist(),'forward':fw.tolist(),'yaw_arc':{'min_angle':-180.,'max_angle':180.},'pitch_arc':{'min_angle':-85.,'max_angle':5.}}
 rigs.append({'index':i,'source_pad_root':root,'source_yaw_node':yawnode,'source_pitch_node':pitchnode,'source_barrel_node':barrelnode,'source_pad_mesh':padnode,'mount':mount,'basis_columns':B.tolist(),'yaw_pivot_hull':yaw.tolist(),'pitch_pivot_hull':pitch.tolist(),'muzzle_hull':muzzle.tolist(),'turret_override':{'type':'biaxial','biaxial_base_mesh':aliasbase,'biaxial_barrel_mesh':aliasbarrel,'barrel_position':offset.tolist(),'muzzle_positions':[(mc*factor).tolist()]},'skin_alias_map':[{'mesh_alias_name':aliasbase,'mesh_definition':{'mesh':aliasbase,'shader':'ship','is_shadow_blocker':True}},{'mesh_alias_name':aliasbarrel,'mesh_definition':{'mesh':aliasbarrel,'shader':'ship','is_shadow_blocker':True}}],'neutral_pose':'Original yaw retained. Source pitch pose removed at exact source pitch pivot and placed horizontal in game neutral; source barrel+Z becomes game local+Z, pad+Z becomes game local+Y. No geometry deformation.','runtime':'NOT RUN; source joint axes verified, aiming/clearance require game'})
# A single actual compact pod (root122), not the deployed/showcase root47.
podroot=122;podrows=[q for ni in descendants(podroot) for q in arrays(ni,np.linalg.inv(a.world[podroot]))];pv=np.concatenate([r['v'] for r in podrows]);pc=(pv.min(0)+pv.max(0))/2;frames['amun_boarding_pod']={'basis':np.eye(3).tolist(),'origin':[0,0,0]}
for r in podrows:add('amun_boarding_pod',r,(r['v']-pc)*factor,r['n'],r['t'])
podbounds=np.concatenate([r['v'] for r in shapes['amun_boarding_pod']]);podex=[0.,0.,float(podbounds[:,2].min()-.03)]
# Rail: actual paired forward machined rail components9/10 from audited welded
# component decomposition. Their midpoint has a clear+Y ray through the nose.
components=read(AUDIT/'hull-components.json');alltri=np.concatenate([r['v'][r['i']] for r in central]);railverts=np.concatenate([alltri[components[j]['indices']].reshape(-1,3) for j in [9,10]]);railcap=railverts[railverts[:,1]>railverts[:,1].max()-.006];rc=(railcap.min(0)+railcap.max(0))/2;rc[1]=railverts[:,1].max()+.02;rail={'position':point(rc).tolist(),'forward':[0,0,1],'up':[0,1,0],'mesh_point':'weapon.rail.0','source':'Actual paired forward rail components9/10 in source hull, full terminal cap bounds midpoint; +Y ray clearance checked','source_position':rc.tolist()}
# Measured circular aft nozzle opening: separate inner/outer rim radii.
rim=np.unique(np.round(vv[vv[:,1]<lo[1]+.0001],6),axis=0);p=rim[:,[0,2]];guess=(p.min(0)+p.max(0))/2;radius=np.linalg.norm(p-guess,axis=1);ordered=np.sort(radius);gi=np.argmax(np.diff(ordered));cut=(ordered[gi]+ordered[gi+1])/2;inner=p[radius<cut];fit=np.linalg.lstsq(np.column_stack([2*inner,np.ones(len(inner))]),(inner*inner).sum(1),rcond=None)[0];rad=np.sqrt(fit[2]+sum(fit[:2]**2));res=float(max(abs(np.linalg.norm(inner-fit[:2],axis=1)-rad)));assert len(inner)>=8 and res<.01;ec=np.array([fit[0],rim[:,1].mean()-.03,fit[1]]);exhaust={'position':point(ec).tolist(),'up':[0,1,0],'forward':[0,0,-1],'source':'Fitted actual aft nozzle inner rim; full circumference, not whole-hull min slice center','inner_rim_vertices':len(inner),'source_inner_radius':float(rad),'source_fit_residual':res,'source_position':ec.tolist()}
def door_port(root,name):
 localrows=[q for ni in descendants(root) for q in arrays(ni,np.linalg.inv(a.world[root]))];v=np.concatenate([r['v'] for r in localrows]);mid=(v.min(0)+v.max(0))/2;extent=np.ptp(v,axis=0);normal_axis=int(np.argmin(extent));M=matrix(root);R=normalized(M);pos=M[:3,:3]@mid+M[:3,3];normal=R[:,normal_axis];radial=pos-center;radial[1]=0
 if np.dot(normal,radial)<0:normal=-normal
 tangent=R[:,int(np.argmax(extent))];tangent-=normal*np.dot(tangent,normal);tangent/=np.linalg.norm(tangent);pos+=normal*.06;return {'name':name,'position':point(pos).tolist(),'forward':direction(normal).tolist(),'up':direction(tangent).tolist(),'source_root':root,'source_position':pos.tolist(),'source':'Measured named source door center/normal plus0.06 outward clearance; static door pose; launch aperture/door-clearance runtime NOT RUN'}
ports=[door_port(7,'torpedo_bay_002'),door_port(12,'torpedo_bay_003')];boarding=door_port(41,'boarding_shuttle_bay');boarding['mesh_point']='weapon.boarding.0';equipment={'railgun':rail,'torpedo_ports':ports,'exhaust':exhaust,'boarding_port':boarding}
points=[{'name':'center','translation':target.tolist()},{'name':'above','translation':[target[0],float(point(hi)[1]+3),target[2]]},{'name':'aura','translation':[target[0],float(point(lo)[1]-3),target[2]]}]
for name,e in [('weapon.rail.0',rail),('exhaust.0',exhaust),('weapon.boarding.0',boarding)]:points.append({'name':name,'translation':e['position'],'rotation':Rotation.from_matrix(np.column_stack([np.cross(e['up'],e['forward']),e['up'],e['forward']])).as_quat().tolist()})
for r in rigs:points.append({'name':r['mount']['mesh_point'],'translation':r['yaw_pivot_hull'],'rotation':Rotation.from_matrix(r['basis_columns']).as_quat().tolist()})
meshpoints={'amun_hull':points,'amun_boarding_pod':[{'name':'center','translation':[0,0,0]},{'name':'exhaust.0','translation':podex,'rotation':[0,1,0,0]}]};counts={};sourceframes={};materialname='expanse06_amun_surface'
for kind,frame in frames.items():
 B=np.array(frame['basis']);origin=np.array(frame['origin']);name='expanse06_'+kind;g={'asset':{'version':'2.0','generator':'Actual Amun source geometry; compiler-Z compensated'},'scene':0,'scenes':[{'nodes':[0]}],'nodes':[{'name':name,'mesh':0,'children':[]}],'meshes':[{'name':name,'primitives':[]}],'buffers':[],'bufferViews':[],'accessors':[],'materials':[{'name':materialname,'pbrMetallicRoughness':{'baseColorFactor':[1,1,1,1],'roughnessFactor':1,'metallicFactor':1}}]};buf=bytearray();vs=[];ns=[];ts=[];uvs=[];ids=[];offset=0
 for r in shapes[kind]:
  vs.append((r['v']-origin)@B);ns.append(r['n']@B);t=r['t'].copy();t[:,:3]=t[:,:3]@B;ts.append(t);uvs.append(r['uv']);ids.extend(r['i'].flatten()+offset);offset+=len(r['v'])
 v=np.concatenate(vs);n=np.concatenate(ns);t=np.concatenate(ts);uv=np.concatenate(uvs);idx=np.array(ids,dtype=np.uint32);sourceframes[kind]={'0':{'positions':v.tolist(),'normals':n.tolist(),'tangents':t.tolist(),'uv':uv.tolist()}};counts[kind]=len(idx)//3
 def acc(v,typ,ct=5126):
  v=np.asarray(v,dtype='<f4' if ct==5126 else '<u4');buf.extend(b'\0'*((-len(buf))%4));start=len(buf);buf.extend(v.tobytes());g['bufferViews'].append({'buffer':0,'byteOffset':start,'byteLength':v.nbytes});at={'bufferView':len(g['bufferViews'])-1,'componentType':ct,'count':len(v),'type':typ}
  if typ=='VEC3':at.update(min=v.min(0).tolist(),max=v.max(0).tolist())
  g['accessors'].append(at);return len(g['accessors'])-1
 for ar in [v,n,t]:ar[:,2]*=-1
 t[:,3]*=-1;g['meshes'][0]['primitives']=[{'mode':4,'material':0,'indices':acc(idx,'SCALAR',5125),'attributes':{'POSITION':acc(v,'VEC3'),'NORMAL':acc(n,'VEC3'),'TANGENT':acc(t,'VEC4'),'TEXCOORD_0':acc(uv,'VEC2')}}]
 meshpoints.setdefault(kind,[])
 for p in meshpoints[kind]:
  q=copy.deepcopy(p);q['translation'][2]*=-1
  if 'rotation' in q:q['rotation'][0]*=-1;q['rotation'][1]*=-1
  g['nodes'][0]['children'].append(len(g['nodes']));g['nodes'].append(q)
 g['buffers']=[{'uri':name+'.bin','byteLength':len(buf)}];(OUT/(name+'.bin')).write_bytes(buf);write(OUT/(name+'.gltf'),g)
shipv=np.concatenate([r['v'] for kind in shapes if kind!='amun_boarding_pod' for r in shapes[kind]]);sl=shipv.min(0);sh=shipv.max(0);bc=(sl+sh)/2;spatial={'box':{'center':bc.tolist(),'extents':((sh-sl)/2).tolist()},'radius':float(np.linalg.norm(shipv-bc,axis=1).max()),'bounds_min':sl.tolist(),'bounds_max':sh.tolist(),'includes':'Real central hull, fixed doors, three selected pads and neutral yaw/pitch geometry only; pod excluded'}
write(OUT/'retained-source-frames.json',sourceframes);write(AUDIT/'equipment.json',equipment);write(AUDIT/'mount-metadata.json',{'status':'COMPILER CHECKS PENDING','rigs':rigs,'frames':frames,'meshpoints':meshpoints,'counts':counts,'triangle_total':sum(counts.values()),'ship_triangle_total':sum(v for k,v in counts.items() if k!='amun_boarding_pod'),'pod_triangle_total':counts['amun_boarding_pod'],'equipment':equipment,'exhaust_geometry':exhaust,'custom_railgun':rail,'ship_spatial':spatial,'normalization':{'source_to_game_rotation':C.tolist(),'source_center':center.tolist(),'scale':factor,'target_center':target.tolist(),'central_hull_length':target_length,'scale_status':'Provisional61.5m Amun /46m Tachi, based on secondary size reference supplied by main; not primary-verified','source_reference':str(SOURCE),'presentation_cancel_matrix':cancel.tolist()},'selection':{'selected_pdc_roots':selected,'omitted_pdc_root':omitted,'reason':'Requested three guns: dorsal/ventral opposition plus starboard-forward reinforcement; source has four, this is an explicit non-canonical prototype choice','excluded_detached_torpedoes':[102,107,112,117],'excluded_detached_pods':[47,122,177,232,287,342,397,452,507,562,617,672,727,782,837],'separate_pod_source_root':podroot,'no_fourth_static_gun':True},'source_ownership':ownership,'source_hashes':{str(p):hashlib.sha256(p.read_bytes()).hexdigest() for p in SRC.rglob('*') if p.is_file()},'materialspec':[{'name':materialname,'original':a.g['materials'][0]}]});print(json.dumps({'ship_triangles':sum(v for k,v in counts.items() if k!='amun_boarding_pod'),'pod_triangles':counts['amun_boarding_pod'],'counts':counts,'source_to_game_scale':factor,'length':target_length}),flush=True)
