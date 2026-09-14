"""Dark Star and full-dimensional Behemoth bookmark conversion; private only."""
import copy,json,math,numpy as np
from scipy.spatial.transform import Rotation
import update27_opa_common as o

def saveparts(name,parts,points,report):
 z={}
 for j,p in enumerate(parts):
  for k,v in p.items():z[f'{j}_{k}']=v
 np.savez(o.SOURCE/(name+'-parts.npz'),**z);o.write(o.AUD/(name+'-geometry.json'),report)

def loadparts(name):
 z=np.load(o.SOURCE/(name+'-parts.npz'));parts=[]
 for j in range(len([k for k in z if k.endswith('_v')])):
  p={k:z[f'{j}_{k}']for k in ['v','n','t','uv','i']};p['material']=str(z[f'{j}_material']);parts.append(p)
 return parts

def darkstar():
 name='expanse27_dark_star';raw=o.stl('OPAS_Dark_Star_V1.1_Merged.stl');lo=raw.min((0,1));hi=raw.max((0,1));scale=90*o.UNITS/(hi[1]-lo[1]);center=np.array([0,(hi[1]+lo[1])/2,0]);tri=(raw-center)[:,:,[0,2,1]]*scale;tri=tri[:,[0,2,1]]
 tri,optimization=o.simplify(tri,180000,.00025);length=90*o.UNITS
 def world(p):return ((np.array(p)-center)[[0,2,1]]*scale)
 # Preserve major facets; classify subdued structural collar/end panels.
 centroid=tri.mean(1);trim=(centroid[:,2]<-length*.36)|(abs(centroid[:,0])>length*.145)
 mats=[name+'_charcoal',name+'_graphite'];o.atlas(mats[0],(35,39,43));o.atlas(mats[1],(22,26,30));parts=[o.frame(tri[~trim],mats[0]),o.frame(tri[trim],mats[1])]
 points=[{'name':'center','translation':[0,0,0]},{'name':'above','translation':[0,40,0]},{'name':'aura','translation':[0,-40,0]}]
 turret=copy.deepcopy(o.read(o.BASE/'entities/expanse06_amun_pdc_0.weapon')['turret']);turret.update(biaxial_base_mesh=name+'_pdc_base',biaxial_barrel_mesh=name+'_pdc_barrel')
 specs=[]
 for theta,z in [(math.pi/2,30),(-math.pi/2,0),(math.pi/2,-45)]:
  up=np.array([math.cos(theta),math.sin(theta),0]);specs.append((up*length+[0,0,z],up))
 mounts=o.rigs(tri,specs,points,name,turret,standoff=2.5)
 for r in mounts:r['pitch_arc']['max_angle']=-25.
 clear=o.safety(tri,mounts)
 # Single centered source engine at source-Y=-110.105; aft is game-Z negative.
 exhaust=world([0,lo[1]-.15,0]);engines=[{'position':exhaust.tolist(),'forward':[0,0,-1],'up':[0,1,0]}];points.append({'name':'exhaust.0','translation':exhaust.tolist(),'rotation':[0,1,0,0]})
 ports=[]
 for j,x in enumerate([-8.,8.]):
  origin=np.array([x,0,length]);hit=o.ray(tri,origin,np.array([0,0,-1.]));assert hit is not None;pos=hit+np.array([0,0,1]);points.append({'name':f'weapon.torpedo.{j}','translation':pos.tolist()});ports.append({'position':pos.tolist(),'rotation':[1,0,0,0,1,0,0,0,1]})
 rail=o.ray(tri,np.array([0.,-10.,length]),np.array([0,0,-1.]));assert rail is not None;rail+=np.array([0,0,1.]);points.append({'name':'weapon.rail.0','translation':rail.tolist()})
 boarding=o.ray(tri,np.array([length,0,0]),np.array([-1.,0,0]));assert boarding is not None;boarding+=np.array([1.,0,0]);points.append({'name':'weapon.boarding.0','translation':boarding.tolist(),'rotation':Rotation.from_euler('y',90,degrees=True).as_quat().tolist()})
 v=tri.reshape(-1,3);report={'id':name,'hull_mesh':name+'_hull','source_zip':'/home/haker/Downloads/The_Expanse_OPAS_Dark_Star_V1.1_Merged.zip','source_zip_sha256':o.sha('/home/haker/Downloads/The_Expanse_OPAS_Dark_Star_V1.1_Merged.zip'),'stl_sha256':o.sha(o.SOURCE/'OPAS_Dark_Star_V1.1_Merged.stl'),'source_triangles':len(raw),'optimization':optimization,'length_metres_mod_adaptation':90,'source_scale':scale,'source_center':center.tolist(),'source_rotation':'[X,Z,Y], compensate reflected triangle winding; source negativeY engine becomes game negativeZ','spatial':{'box':{'center':((v.max(0)+v.min(0))/2).tolist(),'extents':((v.max(0)-v.min(0))/2).tolist()},'radius':float(np.linalg.norm(v,axis=1).max()+10),'collision_rank':2},'meshpoints':points,'rigs':mounts,'torpedo_ports':ports,'rail_position':rail.tolist(),'exhausts':engines,'materials':mats,'checks':{'sampled_muzzle_rays_clear':clear,'sampled_yaw_angles':17,'sampled_pitch_angles':9},'notes':['Commissioned fan/RPG Belter salvage interpretation; not a canonical named ship.','Black/charcoal mod paint; original STL has no UV/material sources.','Three independent actual Amun PDC donor rigs; outward -25deg maximum elevation arc preserves hull clearance.','Local user-authorized paid-model derivative only; do not publish source or compiled art.']}
 saveparts(name,parts,points,report);return report

def cap_blade(raw):
 keep=raw[:,:,0].max(1)<=.5;tri=raw[keep];v,idx=np.unique(np.round(tri.reshape(-1,3),5),axis=0,return_inverse=True);idx=idx.reshape(-1,3);tri=v[idx];edges=np.concatenate([idx[:,[0,1]],idx[:,[1,2]],idx[:,[2,0]]]);und,cnt=np.unique(np.sort(edges,axis=1),axis=0,return_counts=True);boundary=und[cnt==1];neighbors={}
 for a,b in boundary:neighbors.setdefault(a,[]).append(b);neighbors.setdefault(b,[]).append(a)
 assert all(len(x)==2 for x in neighbors.values());remaining=set(neighbors);caps=[];loops=[]
 while remaining:
  start=min(remaining);order=[start];prev=None;cur=start
  while True:
   nxt=next(x for x in neighbors[cur]if x!=prev)
   if nxt==start:break
   order.append(nxt);prev,cur=cur,nxt
  remaining.difference_update(order);points=v[order];middle=points.mean(0);loop=[]
  for a,b in zip(points,np.roll(points,-1,axis=0)):
   t=np.array([a,b,middle]);n=np.cross(t[1]-t[0],t[2]-t[0]);
   if n[0]<0:t=t[[0,2,1]]
   loop.append(t)
  caps+=loop;loops.append({'edges':len(order),'bounds':[points.min(0).tolist(),points.max(0).tolist()]})
 tri=np.concatenate([tri,np.array(caps)]);v,idx=np.unique(np.round(tri.reshape(-1,3),5),axis=0,return_inverse=True);idx=idx.reshape(-1,3);edges=np.concatenate([idx[:,[0,1]],idx[:,[1,2]],idx[:,[2,0]]]);_,counts=np.unique(np.sort(edges,axis=1),axis=0,return_counts=True);assert not (counts==1).any()
 return tri,{'removed_blade_triangles':int((~keep).sum()),'retained_source_triangles':int(keep.sum()),'caps_added':len(caps),'boundary_loops':loops,'remaining_open_edges':int((counts==1).sum()),'rule':'Remove triangles extending beyond X=0.5; source full hull maxX0.491. Cap narrow attachment loops; no broad silhouette clipping.'}

def behemoth():
 name='expanse27_behemoth';raw=o.stl('Nauvoo_Bookmark.stl');tri,cleanup=cap_blade(raw);lo=tri.min((0,1));hi=tri.max((0,1));center=np.array([-11.38,-24.24,(hi[2]+lo[2])/2]);scale=2000*o.UNITS/(hi[2]-lo[2]);tri=(tri-center)*scale;tri,optimization=o.simplify(tri,145000,.0001)
 # The source's lower cylinders are solid print pegs. Replace only below source
 # Z=8.0 with open, tapered nozzle bells at their measured circular centers.
 cutoff=(8.-center[2])*scale;peg=tri[:,:,2].min(1)<cutoff;kept=list(tri[~peg])
 for t in tri[peg]:
  poly=[]
  for a,b in zip(t,np.roll(t,-1,axis=0)):
   ia=a[2]>=cutoff;ib=b[2]>=cutoff
   if ia:poly.append(a)
   if ia!=ib:poly.append(a+(b-a)*((cutoff-a[2])/(b[2]-a[2])))
  for j in range(1,len(poly)-1):kept.append(np.array([poly[0],poly[j],poly[j+1]]))
 retained=np.array(kept)
 source_v=np.unique(raw.reshape(-1,3),axis=0);mouth=source_v[(source_v[:,2]<.0001)&(source_v[:,0]<=.5)];xy=mouth[:,:2];from scipy.cluster.vq import kmeans2
 # Eight clusters initialized evenly about measured source engine-axis center.
 angles=np.linspace(0,2*np.pi,8,endpoint=False);guess=center[:2]+np.column_stack([np.cos(angles),np.sin(angles)])*7.2;means,labels=kmeans2(xy,guess,minit='matrix',iter=40);assert len(set(labels))==8
 assert np.max(np.linalg.norm(means-center[:2],axis=1))<10.,'Bookmark vertices leaked into drive centers'
 engines=[];engine_tri=[];inner=[]
 for j,xy0 in enumerate(means):
  pos=(np.r_[xy0,0]-center)*scale;top=pos.copy();top[2]=cutoff+scale*.2;bottom=pos.copy();bottom[2]-=scale*.5
  radius=float(np.linalg.norm(xy[labels==j]-xy0,axis=1).mean())*scale
  # 48-sided tapered outer/inner bells give an actual open throat, not capped pegs.
  o.cylinder(engine_tri,top,bottom,radius,segments=48,cap=False,r2=radius*1.35)
  throat=bottom.copy();throat[2]+=radius*1.25;o.cylinder(inner,bottom,throat,radius*1.22,segments=48,cap=False,r2=radius*.4)
  engines.append({'position':bottom.tolist(),'forward':[0,0,-1],'up':[0,1,0],'source_xy_center':xy0.tolist(),'aperture_radius':radius*1.22})
 mats=[name+'_ivory',name+'_framework',name+'_nozzle'];o.atlas(mats[0],(197,200,193),white=True);o.atlas(mats[1],(125,137,140),white=True);o.atlas(mats[2],(24,32,40))
 centroid=retained.mean(1);radial=np.linalg.norm(centroid[:,:2],axis=1);trim=radial>11.3*scale;parts=[o.frame(retained[~trim],mats[0]),o.frame(retained[trim],mats[1]),o.frame(np.concatenate([engine_tri,inner]),mats[2])]
 hull=np.concatenate([retained,np.array(engine_tri),np.array(inner)]);points=[{'name':'center','translation':[0,0,0]},{'name':'above','translation':[0,1000,0]},{'name':'aura','translation':[0,-1000,0]}]
 for j,e in enumerate(engines):points.append({'name':f'exhaust.{j}','translation':e['position'],'rotation':[0,1,0,0]})
 turret=copy.deepcopy(o.read(o.BASE/'entities/expanse24_behemoth_pdc.weapon')['turret']);turret.update(biaxial_base_mesh=name+'_pdc_base',biaxial_barrel_mesh=name+'_pdc_barrel');specs=[]
 for zlow,zhigh in [(11.,24.),(37.,46.)]:
  for a in np.pi/4+np.arange(4)*np.pi/2:
   up=np.array([math.cos(a),math.sin(a),0.]);contacts=[]
   for srcz in np.linspace(zlow,zhigh,65):
    origin=up*2000+[0,0,(srcz-center[2])*scale];hit=o.ray(hull,origin,-up)
    if hit is not None:contacts.append(hit)
   hit=max(contacts,key=lambda p:float(p@up));specs.append((up*2000+[0,0,hit[2]],up))
 mounts=o.rigs(hull,specs,points,name,turret,standoff=15.)
 clear=o.safety(hull,mounts)
 ports=[]
 for j,x in enumerate([-250.,250.]):
  hit=o.ray(hull,np.array([x,0,3000.]),np.array([0,0,-1.]));assert hit is not None;pos=hit+np.array([0,0,12.]);points.append({'name':f'weapon.torpedo.{j}','translation':pos.tolist()});ports.append({'position':pos.tolist(),'rotation':[1,0,0,0,1,0,0,0,1]})
 v=hull.reshape(-1,3);report={'id':name,'existing_unit_id':'expanse24_behemoth','hull_mesh':name+'_hull','source_zip':'/home/haker/Downloads/Nauvoo _ Behemoth _ Medina Station Bookmark from the Expanse - 5977410.zip','source_zip_sha256':o.sha('/home/haker/Downloads/Nauvoo _ Behemoth _ Medina Station Bookmark from the Expanse - 5977410.zip'),'stl_sha256':o.sha(o.SOURCE/'Nauvoo_Bookmark.stl'),'source_triangles':len(raw),'cleanup':cleanup,'optimization':optimization,'engine_reconstruction':{'print_peg_faces_removed':int(peg.sum()),'bell_faces_added':len(engine_tri)+len(inner),'engine_count':8,'method':'Eight source-Z0 circle groups; replace solid peg ends with48-sided open tapered bells and dark throats'},'length_metres':2000,'source_scale':scale,'source_center':center.tolist(),'spatial':{'box':{'center':((v.min(0)+v.max(0))/2).tolist(),'extents':((v.max(0)-v.min(0))/2).tolist()},'radius':float(np.linalg.norm(v,axis=1).max()+40),'collision_rank':3},'meshpoints':points,'rigs':mounts,'torpedo_ports':ports,'exhausts':engines,'materials':mats,'checks':{'sampled_muzzle_rays_clear':clear,'sampled_yaw_angles':17,'sampled_pitch_angles':9},'notes':['Full round3D source hull retained; no flattened bookmark exported.','Blade removed and attachment capped; no separate exterior source lettering identified. Interior detail is retained rather than misclassified as print supports.','White/ivory industrial panel paint and emissive windows; inherited support-oriented combat/health remain unchanged.','CC BY-NC archive attribution: Brendch06, Thingiverse5977410. Local derivative only.']}
 saveparts(name,parts,points,report);return report

def main():
 o.dirs()
 for fun in [darkstar,behemoth]:
  r=fun();print(json.dumps({'id':r['id'],'optimization':r['optimization'],'clear_rays':r['checks']['sampled_muzzle_rays_clear']}),flush=True)
if __name__=='__main__':main()
