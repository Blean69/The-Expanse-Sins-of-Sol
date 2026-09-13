from update12_scirocco_common import *
import ctypes as c
from scipy.spatial import ConvexHull
BUILD.mkdir(parents=True,exist_ok=True)
z=np.load(OUT/'source-components.npz');source=z['v'][z['i']];labels=z['triangle_components'];scent=source.mean(1)
lo=source.min((0,1));hi=source.max((0,1));center=(lo+hi)/2;scale=(200/46*105)/(hi[0]-lo[0]);R=np.array([[0,1,0],[0,0,1],[1,0,0]],float);assert np.linalg.det(R)==1
transform=lambda p:(np.array(p)-center)@R.T*scale
# Cut only the actual protruding source rail housing at its measured support plane.
upsource=np.array([0,-.866025403784,.5]);height=125.;d=source@upsource-height;region=(labels==89)&(scent[:,0]>-130)&(scent[:,0]<20);rail=[];hull=[];crossings=[]
def clip(q,dist,positive):
 out=[]
 for j in range(3):
  a=q[j];b=q[(j+1)%3];da=dist[j];db=dist[(j+1)%3];inside=da>=-1e-9 if positive else da<=1e-9
  if inside:out.append(a)
  if da*db<0:out.append(a+(b-a)*da/(da-db))
 return [np.array([out[0],out[j],out[j+1]])for j in range(1,len(out)-1)]
for k,q in enumerate(source):
 if not region[k] or d[k].max()<=0:hull.append(q);continue
 if d[k].min()>=0:rail.append(q);continue
 rail.extend(clip(q,d[k],True));hull.extend(clip(q,d[k],False))
 for i,j in [(0,1),(1,2),(2,0)]:
  if d[k,i]*d[k,j]<0:crossings.append(q[i]+(q[j]-q[i])*d[k,i]/(d[k,i]-d[k,j]))
crossings=np.unique(np.round(crossings,8),axis=0);right=np.cross(upsource,[1,0,0]);uv=np.column_stack([crossings[:,0],crossings@right]);boundary=crossings[ConvexHull(uv).vertices];pivot_source=(crossings.min(0)+crossings.max(0))/2
for i in range(len(boundary)):
 q=np.array([pivot_source,boundary[i],boundary[(i+1)%len(boundary)]]);
 if np.dot(np.cross(q[1]-q[0],q[2]-q[0]),upsource)<0:q=q[[0,2,1]]
 hull.append(q);rail.append(q[[0,2,1]])
hull=transform(hull);rail=transform(rail);railup=R@upsource;rail_clearance_offset=8.2;railpivot=transform(pivot_source)+railup*rail_clearance_offset;rail+=railup*rail_clearance_offset
# Quantified per-part reduction retains small features, especially the actual rail.
lib=c.CDLL(str(MAIN/'.tools/libmeshoptimizer.so'));u=c.POINTER(c.c_uint);f=c.POINTER(c.c_float);fn=lib.meshopt_simplify;fn.argtypes=[u,u,c.c_size_t,f,c.c_size_t,c.c_size_t,c.c_size_t,c.c_float,c.c_uint,f];fn.restype=c.c_size_t
optimization=[]
def reduce(tri,target,errorlimit):
 v,ii=np.unique(np.round(np.asarray(tri),6).reshape(-1,3),axis=0,return_inverse=True);pos=np.ascontiguousarray(v,dtype='float32');idx=np.ascontiguousarray(ii,dtype='uint32');dst=np.zeros_like(idx);err=c.c_float();nn=fn(dst.ctypes.data_as(u),idx.ctypes.data_as(u),len(idx),pos.ctypes.data_as(f),len(pos),12,target*3,errorlimit,0,c.byref(err));q=pos[dst[:nn].reshape(-1,3)].astype(float);cross=np.cross(q[:,1]-q[:,0],q[:,2]-q[:,0]);area=np.linalg.norm(cross,axis=1);edge=np.max(np.linalg.norm(q-np.roll(q,1,axis=1),axis=2),axis=1);valid=(area>1e-7)&(area/np.maximum(edge**2,1e-20)>1e-7);optimization.append({'source_triangles':len(tri),'retained_triangles':int(valid.sum()),'removed_slivers':int((~valid).sum()),'target':target,'error_limit':errorlimit,'measured_error':err.value});return q[valid]
hull=reduce(hull,73500,.002);rail=reduce(rail,2800,.001);np.savez(OUT/'optimized-parts.npz',hull=hull,rail=rail);print('Reduced',len(hull),len(rail),flush=True)
# Efficient ray/hull checks in arbitrary mount directions.
projection_cache={}
def ray(origin,direction):
 o=np.array(origin,float);direction=np.array(direction,float);direction/=np.linalg.norm(direction);key=tuple(np.round(direction,8))
 if key not in projection_cache:
  a=np.eye(3)[np.argmin(abs(direction))];a-=direction*np.dot(a,direction);a/=np.linalg.norm(a);b=np.cross(direction,a);pr=np.stack([hull@a,hull@b],axis=-1);projection_cache[key]=(a,b,pr.min(1),pr.max(1))
 a,b,mn,mx=projection_cache[key];p=np.array([o@a,o@b]);mask=np.all((mn<=p+1e-7)&(mx>=p-1e-7),axis=1);q=hull[mask];e1=q[:,1]-q[:,0];e2=q[:,2]-q[:,0];h=np.cross(direction,e2);det=np.sum(e1*h,1);inv=np.divide(1,det,out=np.zeros_like(det),where=abs(det)>1e-10);s=o-q[:,0];uu=np.sum(s*h,1)*inv;qq=np.cross(s,e1);vv=qq@direction*inv;t=np.sum(e2*qq,1)*inv;ok=(abs(det)>1e-10)&(uu>=-1e-7)&(vv>=-1e-7)&(uu+vv<=1+1e-7)&(t>1e-5)
 if not ok.any():raise ValueError(('Ray misses source-derived hull',o.tolist(),direction.tolist()))
 j=np.where(ok)[0][np.argmin(t[ok])];return o+direction*t[j]
fixed={0:[hull],1:[],2:[]}
def add(q,mat=1):fixed[mat].append(np.array(q,float).reshape(-1,3,3))
def cyl(p0,p1,radius,segments=16):
 p0=np.array(p0);p1=np.array(p1);ax=p1-p0;ax/=np.linalg.norm(ax);a=np.eye(3)[np.argmin(abs(ax))];a-=ax*np.dot(a,ax);a/=np.linalg.norm(a);b=np.cross(ax,a);rr=radius*(np.cos(np.arange(segments)*2*np.pi/segments)[:,None]*a+np.sin(np.arange(segments)*2*np.pi/segments)[:,None]*b);aa=p0+rr;bb=p1+rr
 for i in range(segments):
  j=(i+1)%segments
  for q in [[aa[i],aa[j],bb[j]],[aa[i],bb[j],bb[i]],[p0,aa[j],aa[i]],[p1,bb[i],bb[j]]]:add(q)
# Existing complete donor PDCs: actual two-piece biaxial assembly, scale1.
donor=read(DONOR/'audit/polish-b/mount-metadata.json')['rigs'][0];off=np.array(donor['turret_override']['barrel_position']);muzzle=np.array(donor['turret_override']['muzzle_positions'][0]);donor_meshes={}
for part in ['base','barrel']:
 g=Gltf(DONOR/'assets/derived/polish-b'/f'expanse_polish_pdc_0_{part}.gltf');parts=[]
 for p in g.g['meshes'][0]['primitives']:
  v=g.accessor(p['attributes']['POSITION']);n=g.accessor(p['attributes']['NORMAL']);t=g.accessor(p['attributes']['TANGENT']);v[:,2]*=-1;n[:,2]*=-1;t[:,2]*=-1;t[:,3]*=-1;parts.append({'v':v,'n':n,'t':t,'uv':g.accessor(p['attributes']['TEXCOORD_0']),'i':g.accessor(p['indices']).reshape(-1,3),'material':'mcrn_tachi_material'})
 donor_meshes[part]=parts
placements=[]
for sx in [175.,225.]:
 for sy in [-1,1]:placements.append(([sx,0,10],[0,sy,0],'bow side'))
for sx in [50.,135.]:placements.append(([sx,0,0],[0,0,-1],'ventral'))
for sy in [-1,1]:placements.append(([-140,0,4.2448],[0,sy,0],'behind side protrusion'))
for up in [[0,-1,0],[0,1,0],[0,0,-1],[0,0,1]]:placements.append(([-215,0,4.2448],up,'engine pod'))
rigs=[]
for i,(srcpos,srcup,role)in enumerate(placements):
 up=R@srcup;fw=np.array([0.,0,1]);right=np.cross(up,fw);B=np.column_stack([right,up,fw]);anchor=transform(srcpos);samples=[]
 for x,y in [(0,0),(-2.8,-2.8),(-2.8,2.8),(2.8,-2.8),(2.8,2.8)]:samples.append(ray(anchor+up*180+right*x+fw*y,-up))
 heights=np.array(samples)@up;top=heights.max()+.5;bottom=heights.min()-.6;pivot=anchor+up*(top-anchor@up);cyl(pivot+up*(bottom-top),pivot,3.)
 mount={'weapon':f'{PREFIX}_pdc_{i}','mesh_point':f'child.{PREFIX}_pdc_{i}','weapon_position':pivot.tolist(),'up':up.tolist(),'forward':fw.tolist(),'yaw_arc':{'min_angle':-180.,'max_angle':180.},'pitch_arc':{'min_angle':-85.,'max_angle':5.}}
 rigs.append({'index':i,'kind':'pdc','placement_role':role,'mount':mount,'basis_columns':B.tolist(),'yaw_pivot_hull':pivot.tolist(),'pitch_pivot_hull':(pivot+B@off).tolist(),'muzzle_hull':(pivot+B@(off+muzzle)).tolist(),'turret_override':{'type':'biaxial','biaxial_base_mesh':PREFIX+'_pdc_base','biaxial_barrel_mesh':PREFIX+'_pdc_barrel','barrel_position':off.tolist(),'muzzle_positions':[muzzle.tolist()]},'skin_alias_map':[{'mesh_alias_name':PREFIX+'_pdc_'+part,'mesh_definition':{'mesh':PREFIX+'_pdc_'+part,'shader':'ship','is_shadow_blocker':True}}for part in ['base','barrel']],'support':{'samples':np.array(samples).tolist(),'bottom':bottom,'top':top,'radius':3.},'runtime':'NOT RUN'})
# Single actual light rail: source-derived mounting plane, bounded one-axis gimbal.
B=np.column_stack([np.cross(railup,[0,0,1]),railup,[0,0,1]]);tip=rail.reshape(-1,3);tip=tip[tip[:,2]>tip[:,2].max()-.08];rail_muzzle=(tip.min(0)+tip.max(0))/2+np.array([0,0,.1]);cyl(railpivot-railup*(rail_clearance_offset+.5),railpivot-railup*.1,12.5)
mount={'weapon':PREFIX+'_rail_0','mesh_point':'child.'+PREFIX+'_rail_0','weapon_position':railpivot.tolist(),'up':railup.tolist(),'forward':[0,0,1],'yaw_arc':{'min_angle':-15.,'max_angle':15.},'pitch_arc':{'min_angle':0.,'max_angle':0.}}
rigs.append({'index':12,'kind':'rail','mount':mount,'basis_columns':B.tolist(),'yaw_pivot_hull':railpivot.tolist(),'pitch_pivot_hull':railpivot.tolist(),'muzzle_hull':rail_muzzle.tolist(),'turret_override':{'type':'gimbal','gimbal_mesh':PREFIX+'_rail_0','muzzle_positions':[((rail_muzzle-railpivot)@B).tolist()]},'skin_alias_map':[{'mesh_alias_name':PREFIX+'_rail_0','mesh_definition':{'mesh':PREFIX+'_rail_0','shader':'ship','is_shadow_blocker':True}}],'source_cut_plane':{'normal':upsource.tolist(),'height':height,'pivot_source':pivot_source.tolist(),'cap_vertices':boundary.tolist(),'housing_separated_from_source_component':89,'derivative_outward_clearance_offset':rail_clearance_offset},'runtime':'NOT RUN; rotation limited pending clearance check'})
# Ten custom launch collars, tied to measured actual bow surfaces: five per magazine.
ports={}
for kind,source_z,radius in [('light',-12.,1.5),('heavy',22.,2.)]:
 result=[]
 for i,source_y in enumerate([-48.,-24.,0.,24.,48.]):
  a=transform([0,source_y,source_z]);contact=ray([a[0],a[1],300],[0,0,-1]);foot=[ray([a[0]+dx,a[1]+dy,300],[0,0,-1])for dx,dy in [(0,0),(-radius*.7,-radius*.7),(-radius*.7,radius*.7),(radius*.7,-radius*.7),(radius*.7,radius*.7)]];end=max(q[2]for q in foot)+2.0;start=min(q[2]for q in foot)-.5;ring=np.column_stack([np.cos(np.arange(16)*2*np.pi/16),np.sin(np.arange(16)*2*np.pi/16)]);outer=ring*radius+contact[:2];inner=ring*radius*.7+contact[:2]
  for k in range(16):
   j=(k+1)%16
   for q in [[[*outer[k],start],[*outer[j],start],[*outer[j],end]],[[*outer[k],start],[*outer[j],end],[*outer[k],end]],[[*outer[k],end],[*outer[j],end],[*inner[j],end]],[[*outer[k],end],[*inner[j],end],[*inner[k],end]],[[*inner[k],start],[*inner[j],end],[*inner[j],start]],[[*inner[k],start],[*inner[k],end],[*inner[j],end]],[[*contact[:2],start+.02],[*inner[k],start+.02],[*inner[j],start+.02]]]:add(q,2)
  result.append({'position':[*contact[:2],end+.1],'up':[0,1,0],'forward':[0,0,1],'measured_surface':contact.tolist(),'custom_collar':True,'support_samples':np.array(foot).tolist(),'collar_start':start,'collar_end':end,'radius':radius,'source_semantics':'Prototype retrofit, not an authored tube identification'})
 ports[kind]=result
# Four actual isolated engine bells, components0–3, at their measured aft outlets.
exhausts=[]
for component in range(4):
 q=source[labels==component];lo=q.min((0,1));hi=q.max((0,1));p=(lo+hi)/2;p[0]=lo[0]-.1;exhausts.append({'position':transform(p).tolist(),'up':[0,1,0],'forward':[0,0,-1],'source_component':component,'source_bounds':[lo.tolist(),hi.tolist()]})
boarding_probe=transform([0,0,10]);boarding_contact=ray([200,boarding_probe[1],boarding_probe[2]],[-1,0,0]);boarding={'position':(boarding_contact+[20,0,0]).tolist(),'up':[0,1,0],'forward':[1,0,0],'measured_surface':boarding_contact.tolist(),'external_clearance':20.,'source_semantics':'Prototype boarding origin outside measured hull; no identified or animated source airlock claimed'}
points=[{'name':'center','translation':[0,0,0]},{'name':'above','translation':[0,90,0]},{'name':'aura','translation':[0,-90,0]}]
for r in rigs:points.append({'name':r['mount']['mesh_point'],'translation':r['yaw_pivot_hull'],'rotation':Rotation.from_matrix(r['basis_columns']).as_quat().tolist()})
for kind,pp in ports.items():
 for i,p in enumerate(pp):points.append({'name':f'weapon.{kind}_torpedo.{i}','translation':p['position']})
points.append({'name':'weapon.boarding.0','translation':boarding['position'],'rotation':Rotation.from_matrix(np.column_stack([np.cross(boarding['up'],boarding['forward']),boarding['up'],boarding['forward']])).as_quat().tolist()})
for i,e in enumerate(exhausts):points.append({'name':f'exhaust.{i}','translation':e['position'],'rotation':[0,1,0,0]})
# Generate final meshes and full editable assembled scene.
allparts={'hull':[frames(np.concatenate(parts),PREFIX+f'_mat_{mat}')for mat,parts in fixed.items()if parts],'rail_0':[frames((rail-railpivot)@B,PREFIX+'_mat_0')]};allparts.update({'pdc_'+k:p for k,p in donor_meshes.items()});meshpoints={k:points if k=='hull'else[]for k in allparts};sourceframes={}
for kind,parts in allparts.items():savegltf(PREFIX+'_'+kind,parts,meshpoints[kind]);sourceframes[kind]={str(i):{k:p[k].tolist()for k in ['v','n','t','uv']}for i,p in enumerate(parts)}
assembled=copy.deepcopy(allparts['hull'])
for r in rigs:
 B=np.array(r['basis_columns']);origin=np.array(r['yaw_pivot_hull']);pieces=[('rail_0',np.zeros(3))]if r['kind']=='rail'else[('pdc_base',np.zeros(3)),('pdc_barrel',off)]
 for name,offset in pieces:
  for pp in allparts[name]:
   p=copy.deepcopy(pp);p['v']=(p['v']+offset)@B.T+origin;p['n']=p['n']@B.T;p['t'][:,:3]=p['t'][:,:3]@B.T;assembled.append(p)
savegltf(PREFIX+'_editable',assembled,compiler=False);vv=np.concatenate([p['v']for p in assembled]);lo=vv.min(0);hi=vv.max(0);bc=(lo+hi)/2;counts={k:sum(len(p['i'])for p in pp)for k,pp in allparts.items()};total=sum(len(p['i'])for p in assembled);spatial={'box':{'center':bc.tolist(),'extents':((hi-lo)/2).tolist()},'radius':float(np.linalg.norm(vv-bc,axis=1).max()),'bounds_min':lo.tolist(),'bounds_max':hi.tolist()}
write(OUT/'retained-source-frames.json',sourceframes);write(AUD/'integration-spec.json',{'status':'COMPILER PENDING','game_directory':str(BUILD/'game'),'hull_mesh':PREFIX+'_hull','rigs':rigs,'ship_spatial':spatial,'equipment':{'light_torpedo_ports':ports['light'],'light_torpedo_port':ports['light'][0],'heavy_torpedo_ports':ports['heavy'],'heavy_torpedo_port':ports['heavy'][0],'exhausts':exhausts,'exhaust':exhausts[0],'boarding':boarding},'counts':counts,'assembled_triangle_total':total,'meshpoints':meshpoints,'editable_source':str(OUT/(PREFIX+'_editable.gltf')),'normalization':{'source_center':center.tolist(),'source_to_game_rotation':R.tolist(),'determinant':1.,'scale':scale,'source_length':float(np.ptp(source[:,:,0])),'provisional_game_length':200/46*105,'lore_length_meters':200,'source_gun_side_preserved':True},'runtime':'NOT RUN'})
write(AUD/'optimization.json',{'parts':optimization,'assembled_triangles':total,'source_triangles':len(source),'separation_boundary_vertices':len(boundary),'source_rail_cut_no_duplicate_geometry':True,'runtime':'NOT RUN'});print('Assembled',total,counts,flush=True)
