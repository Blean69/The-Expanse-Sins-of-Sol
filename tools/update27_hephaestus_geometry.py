"""Adyne's fan destroyer: source rail extraction and ten animated PDC replacements."""
from update27_mars_assets import *
NAME='expanse27_hephaestus';z=np.load(OUT/'source/hephaestus-components.npz');source=z['v'][z['i']];labels=z['labels'];count=np.bincount(labels);component=[]
for j in range(len(count)):
 t=source[labels==j];lo=t.min((0,1));hi=t.max((0,1));component.append((lo,hi,(lo+hi)/2))
anchors=[(333,[0,0,-1]),(334,[0,0,1]),(17,[-1,0,0]),(715,[1,0,0]),(137,[-.8660254,0,-.5]),(607,[.8660254,0,-.5]),(47,[-.70710678,0,-.70710678]),(48,[-.70710678,0,.70710678]),(677,[.70710678,0,-.70710678]),(678,[.70710678,0,.70710678])]
pdc_ids=set()
for key,_ in anchors:
 center=component[key][2]
 for j,(lo,hi,cnt)in enumerate(component):
  if np.max(hi-lo)<.72 and np.linalg.norm(cnt-center)<.38:pdc_ids.add(j)
rail_ids={j for j,(lo,hi,cen)in enumerate(component)if lo[1]>.6 and hi[1]<3.7 and lo[2]<-2.60 and hi[2]<-2.55 and np.max(np.abs([lo[0],hi[0]]))<.46}
assert len(rail_ids)>20
lo=source.min((0,1));hi=source.max((0,1));center=(lo+hi)/2;scale=270/(hi[1]-lo[1]);R=np.array([[-1,0,0],[0,0,1],[0,1,0.]])
transform=lambda x:(np.array(x)-center)@R.T*scale
hull=transform(source[~np.isin(labels,list(pdc_ids|rail_ids))]);rail=transform(source[np.isin(labels,list(rail_ids))]);hull,error=simplify(hull,115000,.001);rail,railerror=simplify(rail,6500,.0004)
# Exact source rail support plane and fixed native up axis. Turret housing lifted
# slightly onto a new pedestal so bounded yaw can clear the surrounding hull.
railup=np.array([0,-1.,0]);B=np.column_stack([np.cross(railup,[0,0,1]),railup,[0,0,1]]);pivot=transform([0,1.33,-2.58])+railup*1.5;rail+=railup*1.5;rail_local=(rail-pivot)@B;muzzle=rail_local.reshape(-1,3);tip=muzzle[muzzle[:,2]>muzzle[:,2].max()-.3];muzzle=(tip.min(0)+tip.max(0))/2+[0,0,.1]
positions=[(transform(component[j][2]),R@np.array(up))for j,up in anchors];rigs,points,support=pdc(hull,NAME,positions);support.append(cylinder(pivot+railup*-2.0,pivot,5.5));points.append({'name':'child.'+NAME+'_rail_0','translation':pivot.tolist(),'rotation':Rotation.from_matrix(B).as_quat().tolist()});rigs.append({'kind':'rail','mesh_point':points[-1]['name'],'position':pivot.tolist(),'up':railup.tolist(),'forward':[0,0,1],'yaw_arc':{'min_angle':-12.,'max_angle':12.},'pitch_arc':{'min_angle':-1.,'max_angle':1.},'turret_override':{'type':'gimbal','gimbal_mesh':NAME+'_rail_0','muzzle_positions':[muzzle.tolist()]}})
# Read actual bow tube centers from measured source geometry regions. Distinct
# small/medium origins have visible native holes; metadata keeps source locations.
ports={};extras=[]
# Bow view source has medium three upper apertures and five lower small tubes.
for kind,coords,radius in [('medium',[component[j][2]for j in [276,332,472]],1.6),('light',[component[j][2]for j in [286,301,325,446,459]],1.05)]:
 ports[kind]=[]
 for j,c in enumerate(coords):
  anchor=transform(c);surface=rayhit(hull,[anchor[0],anchor[1],200],[0,0,-1]);mouth=surface+[0,0,1.5];extras.append(cylinder(surface-[0,0,.4],mouth,radius,24,inner=radius*.72));point={'name':f'weapon.torpedo.{kind}.{j}','translation':mouth.tolist()};points.append(point);ports[kind].append({'position':mouth.tolist(),'mesh_point':point['name'],'up':[0,1,0],'forward':[0,0,1],'source_probe':list(c),'measured_surface':surface.tolist()})
# Four actual engine mouths; all source geometry retained at controlled detail.
exhausts=[]
for c in [103,104,485,486]:
 a,b,_=component[c];p=(a+b)/2;p[1]=a[1]-.03;pos=transform(p);pt={'name':'exhaust.'+str(len(exhausts)),'translation':pos.tolist(),'rotation':[0,1,0,0]};points.append(pt);exhausts.append(pt)
# Cut color boundaries through large triangles so livery has straight edges.
def cut(tri,z,positive):
 q=[]
 for j,a in enumerate(tri):
  b=tri[(j+1)%3];da=a[2]-z;db=b[2]-z
  if (da>=-1e-9)if positive else(da<=1e-9):q.append(a)
  if da*db<0:q.append(a+(b-a)*da/(da-db))
 return [[q[0],q[j],q[j+1]]for j in range(1,len(q)-1)]
for z in [-86,-73,55,67]:
 hull=np.array([r for q in hull for r in ((cut(q,z,True)+cut(q,z,False))if q[:,2].min()<z-1e-8 and q[:,2].max()>z+1e-8 else[q])])
hull=hull[np.linalg.norm(np.cross(hull[:,1]-hull[:,0],hull[:,2]-hull[:,0]),axis=1)>1e-7]
cent=hull.mean(1);material=np.full(len(hull),'armor',dtype='<U8');material[(cent[:,2]>55)&(cent[:,2]<67)]='orange';material[(cent[:,2]<-73)&(cent[:,2]>-86)]='orange';material[(np.abs(cent[:,0])<8)&(cent[:,2]<-10)&(material!='orange')]='dark'
parts=[frames(hull[material==k],k,40)for k in ['armor','orange','dark']if(material==k).any()];parts.append(frames(np.concatenate(support+extras),'dark',35));meshes=[save(NAME+'_hull',parts,points),save(NAME+'_rail_0',[frames(rail_local,'armor',35)])];vv=np.concatenate([p['v']for p in parts]+[rail.reshape(-1,3)]);lo=vv.min(0);hi=vv.max(0)
meta={'id':'hephaestus','hull_mesh':NAME+'_hull','meshes':meshes,'colors':{k:COLORS[k]for k in ['armor','orange','dark']},'native_materials':{},'copied_meshes':{NAME+'_pdc_'+k:'expanse24_storm_pdc_'+k for k in ['base','barrel']},'rigs':rigs,'meshpoints':points,'torpedo_ports':ports,'exhausts':exhausts,'spatial':{'radius':float(np.linalg.norm(vv,axis=1).max()),'box':{'center':((lo+hi)/2).tolist(),'extents':((hi-lo)/2).tolist()},'collision_rank':2},'source':{'triangles':len(source),'removed_static_pdc_components':sorted(pdc_ids),'rail_components':sorted(rail_ids),'source_scale':scale,'source_center':center.tolist(),'rotation':R.tolist(),'normalized_simplification_error':error,'rail_error':railerror,'hull_triangles':len(hull),'rail_triangles':len(rail),'zip':'/home/haker/Downloads/mcrn_hephaestus-class_destroyer_printable.zip','sha256':hashlib.sha256(Path('/home/haker/Downloads/mcrn_hephaestus-class_destroyer_printable.zip').read_bytes()).hexdigest()},'runtime':'NOT RUN','adaptations':['Adyne fan model; not canonical.','270gameunit design length; native engine/panel detail preserved.','Ten static PDC clusters removed and replaced by native rotating40mm assemblies.','One source-derived gimbal rail; limited mechanical arc.','Scirocco-inspired charcoal/orange livery.']};write(AUD/'hephaestus-integration.json',meta);print('Hephaestus hull',len(hull),'rail',len(rail),'staticPDCcomponents',len(pdc_ids),flush=True)
