"""Actual reduced Donnager, two rail gimbals and sixteen supported donor PDCs."""
from donnager10_geometry_common import *
from scipy.spatial.transform import Rotation
from collections import defaultdict
import copy
z=np.load(OUT/'optimized.npz');rows=read(AUDIT/'optimized-parts.json')['parts'];layout=read(AUDIT/'layout-candidates.json');shapes=defaultdict(list);frames={'donnager_hull':{'basis':np.eye(3).tolist(),'origin':[0,0,0]}};ownership=[];rigs=[]
for r in rows:
 k=r['key'];v=z[k+'_v'];n=z[k+'_n'];uv=z[k+'_uv'];idx=z[k+'_i']
 if r['node'] not in [33,34,35,36]:groups=[('donnager_hull',np.ones(len(idx),dtype=bool))]
 else:groups=[(f'donnager_rail_{i}',np.mean(v[idx],axis=1)[:,0]*s>0) for i,s in enumerate([-1,1])]
 for kind,mask in groups:
  if not mask.any():continue
  ii=idx[mask];used,remap=np.unique(ii,return_inverse=True);shapes[kind].append({'v':v[used],'n':n[used],'uv':uv[used],'i':remap.reshape(-1,3),'material':r['material']});ownership.append({'node':r['node'],'material':r['material'],'part':kind,'retained_triangles':int(mask.sum()),'source_triangles_before_optimization':r['source_triangles']})
def face(points,mat=1):
 v=np.array(points,float);nn=np.cross(v[1]-v[0],v[2]-v[0]);nn/=np.linalg.norm(nn);shapes['donnager_hull'].append({'v':v,'n':np.tile(nn,(3,1)),'uv':np.array([[0,0],[1,0],[0,1.]]),'i':np.array([[0,1,2]]),'material':mat})
def cylinder(p0,p1,radius,segments=12):
 p0=np.array(p0);p1=np.array(p1);axis=p1-p0;axis/=np.linalg.norm(axis);u=np.eye(3)[np.argmin(abs(axis))];u-=axis*np.dot(u,axis);u/=np.linalg.norm(u);v=np.cross(axis,u);ang=np.arange(segments)*2*np.pi/segments;rr=radius*(np.cos(ang)[:,None]*u+np.sin(ang)[:,None]*v);a0=p0+rr;a1=p1+rr
 for i in range(segments):
  j=(i+1)%segments
  for q in [[a0[i],a0[j],a1[j]],[a0[i],a1[j],a1[i]],[p0,a0[j],a0[i]],[p1,a1[i],a1[j]]]:face(q)
def box(lo,hi):
 lo=np.array(lo);hi=np.array(hi);verts=np.array([[hi[j] if i&(1<<j) else lo[j] for j in range(3)] for i in range(8)])
 for inds in [[0,2,3,1],[4,5,7,6],[0,1,5,4],[2,6,7,3],[0,4,6,2],[1,3,7,5]]:
  for ii in [inds[:3],[inds[0],inds[2],inds[3]]]:face(verts[ii])
def alias(name):return {'mesh_alias_name':name,'mesh_definition':{'mesh':name,'shader':'ship','is_shadow_blocker':True}}
donor=read(ROOT/'audit/polish-b/mount-metadata.json')['rigs'][0]['turret_override'];pdcoffset=np.array(donor['barrel_position']);pdcmuzzle=np.array(donor['muzzle_positions'][0])
for kind,part in [('donnager_pdc_base','base'),('donnager_pdc_barrel','barrel')]:
 inp=Gltf(ROOT/'assets/derived/polish-b'/f'expanse_polish_pdc_0_{part}.gltf');frames[kind]={'basis':np.eye(3).tolist(),'origin':[0,0,0]}
 for p in inp.g['meshes'][0]['primitives']:
  v=inp.accessor(p['attributes']['POSITION']);n=inp.accessor(p['attributes']['NORMAL']);t=inp.accessor(p['attributes']['TANGENT']);v[:,2]*=-1;n[:,2]*=-1;t[:,2]*=-1;t[:,3]*=-1;ii=inp.accessor(p['indices']).flatten().reshape(-1,3);shapes[kind].append({'v':v,'n':n,'t':t,'uv':inp.accessor(p['attributes']['TEXCOORD_0']),'i':ii,'material':11})
for r in layout['pdc_mounts']:
 i=r['index'];B=np.array(r['basis_columns']);pivot=np.array(r['yaw_pivot_hull']);up=B[:,1];s=r['support'];p0=pivot+up*(s['bottom']-s['top']);cylinder(p0,pivot,s['radius']);base='expanse10_donnager_pdc_base';bar='expanse10_donnager_pdc_barrel';mount={'weapon':f'expanse10_donnager_pdc_{i}','mesh_point':f'child.expanse10_donnager_pdc_{i}','weapon_position':pivot.tolist(),'up':up.tolist(),'forward':B[:,2].tolist(),'yaw_arc':{'min_angle':-180.,'max_angle':180.},'pitch_arc':{'min_angle':-85.,'max_angle':5.}}
 rigs.append({'index':i,'kind':'pdc','mount':mount,'basis_columns':B.tolist(),'yaw_pivot_hull':pivot.tolist(),'pitch_pivot_hull':(pivot+B@pdcoffset).tolist(),'muzzle_hull':(pivot+B@(pdcoffset+pdcmuzzle)).tolist(),'turret_override':{'type':'biaxial','biaxial_base_mesh':base,'biaxial_barrel_mesh':bar,'barrel_position':pdcoffset.tolist(),'muzzle_positions':[pdcmuzzle.tolist()]},'skin_alias_map':[alias(base),alias(bar)],'measured_support':r,'prototype_count_not_canonical':True,'donor_scale':1.0,'runtime':'NOT RUN'})
for r in layout['rails']:
 i=r['index'];p=np.array(r['pivot']);kind=f'donnager_rail_{i}';frames[kind]={'basis':np.eye(3).tolist(),'origin':p.tolist()};name='expanse10_'+kind
 for sup in r['supports']:
  start=np.array(sup['hull_contact']['position']);end=np.array(sup['end']);lo=np.minimum(start,end)-[.5,1.25,1.25];hi=np.maximum(start,end)+[.5,1.25,1.25];box(lo,hi)
 mount={'weapon':f'expanse10_donnager_rail_{i}','mesh_point':f'child.{name}','weapon_position':p.tolist(),'up':[0,1,0],'forward':[0,0,1],'yaw_arc':{'min_angle':-2.,'max_angle':2.},'pitch_arc':{'min_angle':0.,'max_angle':0.}}
 rigs.append({'index':16+i,'kind':'rail','mount':mount,'basis_columns':np.eye(3).tolist(),'yaw_pivot_hull':p.tolist(),'pitch_pivot_hull':p.tolist(),'muzzle_hull':r['muzzle'],'turret_override':{'type':'gimbal','gimbal_mesh':name,'muzzle_positions':[(np.array(r['muzzle'])-p).tolist()]},'skin_alias_map':[alias(name)],'measurement':r,'runtime':'NOT RUN; narrow yaw only, pitch disabled'})
# Actual blue emission geometry provides four complete nozzle surfaces.
eng=[r for r in source_parts() if r['node']==30][0]['v'];exhausts=[]
for sx,sy in [(-1,-1),(-1,1),(1,-1),(1,1)]:
 q=eng[(eng[:,0]*sx>0)&(eng[:,1]*sy>0)];lo=q.min(0);hi=q.max(0);pos=(lo+hi)/2;pos[2]=lo[2]-.1;exhausts.append({'position':pos.tolist(),'forward':[0,0,-1],'up':[0,1,0],'source':'Full actual source blue-emission nozzle surface bounds; four disjoint XY quadrants','source_node':30,'surface_bounds':[lo.tolist(),hi.tolist()]})
equipment={'railguns':[{'position':r['muzzle'],'up':[0,1,0],'forward':[0,0,1]} for r in layout['rails']],'exhausts':exhausts,'exhaust':exhausts[0]}
# Main integrator supplies separately measured source apertures, once reviewed.
equipment_input=AUDIT/'main-equipment.json'
if equipment_input.exists():
 equipment.update(read(equipment_input))
 for e in equipment['light_torpedo_ports']:
  c=e['custom_collar'];xy=np.array(c['center'][:2]);angles=np.arange(12)*2*np.pi/12;ring=np.column_stack([np.cos(angles),np.sin(angles)]);outer=xy+ring*c['outer_radius'];inner=xy+ring*c['inner_radius'];front=c['end_z'];back=c['start_z']
  for i in range(12):
   j=(i+1)%12
   for q in [[[ *outer[i],back],[ *outer[j],back],[ *outer[j],front]],[[ *outer[i],back],[ *outer[j],front],[ *outer[i],front]],[[ *inner[j],back],[ *inner[i],back],[ *inner[i],front]],[[ *inner[j],back],[ *inner[i],front],[ *inner[j],front]],[[ *outer[i],front],[ *outer[j],front],[ *inner[j],front]],[[ *outer[i],front],[ *inner[j],front],[ *inner[i],front]]]:face(q)
   face([[*xy,back+.02],[*inner[i],back+.02],[*inner[j],back+.02]],9)

points=[{'name':'center','translation':[0,0,0]},{'name':'above','translation':[0,215,0]},{'name':'aura','translation':[0,-215,0]}]
for r in rigs:points.append({'name':r['mount']['mesh_point'],'translation':r['yaw_pivot_hull'],'rotation':Rotation.from_matrix(r['basis_columns']).as_quat().tolist()})
for i,e in enumerate(exhausts):points.append({'name':f'exhaust.{i}','translation':e['position'],'rotation':[0,1,0,0]})
for name,key in [('hangar.0','hangar'),('weapon.light_torpedo.0','light_torpedo_port'),('weapon.heavy_torpedo.0','heavy_torpedo_port')]:
 if key in equipment:
  e=equipment[key];B=np.column_stack([np.cross(e['up'],e['forward']),e['up'],e['forward']]);points.append({'name':name,'translation':e['position'],'rotation':Rotation.from_matrix(B).as_quat().tolist()})
if 'hangar' in equipment:points.append({'name':'weapon.boarding.0','translation':equipment['hangar']['position'],'rotation':[0,1,0,0]})
meshpoints={'donnager_hull':points};materialspec=[{'name':f'expanse10_donnager_mat_{i}','original':copy.deepcopy(mat)} for i,mat in enumerate(a.g['materials'])];materialspec.append({'name':'mcrn_tachi_material','original':{'pbrMetallicRoughness':{'baseColorTexture':{'index':2}}}});counts={};sourceframes={};flatfallback=0
for kind,frame in frames.items():
 B=np.array(frame['basis']);origin=np.array(frame['origin']);name='expanse10_'+kind;g={'asset':{'version':'2.0','generator':'Measured Donnager prototype; official compiler Z compensation'},'scene':0,'scenes':[{'nodes':[0]}],'nodes':[{'name':name,'mesh':0,'children':[]}],'meshes':[{'name':name,'primitives':[]}],'buffers':[],'bufferViews':[],'accessors':[],'materials':[]};buf=bytearray();sourceframes[kind]={};counts[kind]=0
 def acc(value,typ,ct=5126):
  value=np.asarray(value,dtype='<f4' if ct==5126 else '<u4');buf.extend(b'\0'*((-len(buf))%4));start=len(buf);buf.extend(value.tobytes());g['bufferViews'].append({'buffer':0,'byteOffset':start,'byteLength':value.nbytes});at={'bufferView':len(g['bufferViews'])-1,'componentType':ct,'count':len(value),'type':typ}
  if typ=='VEC3':at.update(min=value.min(0).tolist(),max=value.max(0).tolist())
  g['accessors'].append(at);return len(g['accessors'])-1
 for material in sorted({r['material'] for r in shapes[kind]}):
  rr=[r for r in shapes[kind] if r['material']==material];v=np.concatenate([(r['v']-origin)@B for r in rr]);n=np.concatenate([r['n']@B for r in rr]);uv=np.concatenate([r['uv'] for r in rr]);ids=[];offset=0
  for r in rr:ids.extend(r['i'].flatten()+offset);offset+=len(r['v'])
  idx=np.array(ids,dtype=np.uint32).reshape(-1,3);tri=v[idx];q=np.cross(tri[:,1]-tri[:,0],tri[:,2]-tri[:,0]);flip=np.sum(q*n[idx].mean(1),axis=1)<0;idx[flip]=idx[flip][:,[0,2,1]]
  if all('t' in r for r in rr):t=np.concatenate([r['t'] for r in rr]);t[:,:3]=t[:,:3]@B
  else:
   # Flat normal maps on Donnager source materials; construct valid UV frame.
   ta=np.zeros_like(v);bit=np.zeros_like(v);tri=v[idx];du=uv[idx[:,1]]-uv[idx[:,0]];dv=uv[idx[:,2]]-uv[idx[:,0]];det=du[:,0]*dv[:,1]-du[:,1]*dv[:,0];valid=abs(det)>1e-12;inv=np.divide(1,det,out=np.zeros_like(det),where=valid);e1=tri[:,1]-tri[:,0];e2=tri[:,2]-tri[:,0];tt=(e1*dv[:,1,None]-e2*du[:,1,None])*inv[:,None];bb=(e2*du[:,0,None]-e1*dv[:,0,None])*inv[:,None]
   for ci in range(3):np.add.at(ta,idx[:,ci],tt);np.add.at(bit,idx[:,ci],bb)
   ta-=n*np.sum(ta*n,axis=1)[:,None];ln=np.linalg.norm(ta,axis=1);bad=ln<1e-10;flatfallback+=int(bad.sum())
   for j in np.where(bad)[0]:axis=np.eye(3)[np.argmin(abs(n[j]))];ta[j]=axis-n[j]*np.dot(axis,n[j])
   ta/=np.linalg.norm(ta,axis=1)[:,None];hand=np.where(np.sum(np.cross(n,ta)*bit,axis=1)<0,-1.,1.);t=np.column_stack([ta,hand])
  mi=len(g['materials']);g['materials'].append({'name':materialspec[material]['name'],'pbrMetallicRoughness':{'baseColorFactor':[1,1,1,1]}});sourceframes[kind][str(mi)]={'positions':v.tolist(),'normals':n.tolist(),'tangents':t.tolist(),'uv':uv.tolist()};counts[kind]+=len(idx)
  for value in [v,n,t]:value[:,2]*=-1
  t[:,3]*=-1;g['meshes'][0]['primitives'].append({'mode':4,'material':mi,'indices':acc(idx.flatten(),'SCALAR',5125),'attributes':{'POSITION':acc(v,'VEC3'),'NORMAL':acc(n,'VEC3'),'TANGENT':acc(t,'VEC4'),'TEXCOORD_0':acc(uv,'VEC2')}})
 for p in meshpoints.setdefault(kind,[]):
  q=copy.deepcopy(p);q['translation'][2]*=-1
  if 'rotation' in q:q['rotation'][0]*=-1;q['rotation'][1]*=-1
  g['nodes'][0]['children'].append(len(g['nodes']));g['nodes'].append(q)
 g['buffers']=[{'uri':name+'.bin','byteLength':len(buf)}];(OUT/(name+'.bin')).write_bytes(buf);write(OUT/(name+'.gltf'),g)
shipverts=[r['v'] for k in shapes if not k.startswith('donnager_pdc') for r in shapes[k]]
for r in rigs[:16]:
 B=np.array(r['basis_columns']);origin=np.array(r['yaw_pivot_hull'])
 for kind,offset in [('donnager_pdc_base',np.zeros(3)),('donnager_pdc_barrel',pdcoffset)]:shipverts.extend([(q['v']+offset)@B.T+origin for q in shapes[kind]])
v=np.concatenate(shipverts);lo=v.min(0);hi=v.max(0);bc=(lo+hi)/2;spatial={'box':{'center':bc.tolist(),'extents':((hi-lo)/2).tolist()},'radius':float(np.linalg.norm(v-bc,axis=1).max()),'bounds_min':lo.tolist(),'bounds_max':hi.tolist()};assembled=counts['donnager_hull']+sum(counts[f'donnager_rail_{i}'] for i in range(2))+16*(counts['donnager_pdc_base']+counts['donnager_pdc_barrel']);write(OUT/'retained-source-frames.json',sourceframes);write(AUDIT/'mount-metadata.json',{'status':'COMPILER CHECKS PENDING','rigs':rigs,'frames':frames,'meshpoints':meshpoints,'counts':counts,'triangle_total':sum(counts.values()),'assembled_triangle_total':assembled,'ship_spatial':spatial,'equipment':equipment,'exhaust_geometry':exhausts[0],'materialspec':materialspec,'source_ownership':ownership,'source_hashes':{str(p):hashlib.sha256(p.read_bytes()).hexdigest() for p in SRC.rglob('*') if p.is_file()},'normalization':{'scale':scale,'source_world_center':center.tolist(),'source_to_game_rotation':np.eye(3).tolist(),'target_center':[0,0,0],'provisional_meters':[475.5,46]},'uv_frame_fallback_corners_flat_materials':flatfallback});print('Assembled',assembled,'unique',sum(counts.values()),'counts',counts,flush=True)
