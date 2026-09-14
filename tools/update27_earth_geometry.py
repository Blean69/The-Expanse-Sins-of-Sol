"""Private Earth art: retain STL silhouette, replace static weapon tops, compile rigs."""
from pathlib import Path
import argparse,copy,ctypes as C,hashlib,json,subprocess
import numpy as np
from scipy.spatial.transform import Rotation
from scipy.spatial import cKDTree
from common import read,write,read_mesh
from update27_earth_intake import source
from update26_platform_common import load_parts,export,compile as compile_mesh
from update23_murphy_art import frames,cylinder,rayhit,WINE,SDK,ENV
from update14_pdc_arcs import Rays,sample,choose
ROOT=Path(__file__).resolve().parents[1];MAIN=Path('/run/media/haker/NVME 2/expanse-mod');BASE=MAIN/'build/experiments/expanse_update26';OUT=ROOT/'assets/derived/update27-earth';BUILD=ROOT/'build/update27-earth';GAME=BUILD/'game';AUD=ROOT/'audit/update27-earth';UNITS=104.9869586/46
IDS={'hale':'expanse27_nathan_hale','munroe':'expanse27_munroe'}
for p in[OUT,BUILD,AUD,GAME/'meshes',GAME/'mesh_materials',GAME/'textures',GAME/'effects']:p.mkdir(parents=True,exist_ok=True)
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def clip_top(tri,axis,sign,plane,zlo,zhi):
 """Local half-space surgery; cap actual intersection loops, not bounding boxes."""
 d=tri[:,:,axis]*sign-plane;bad=(d>1e-8).any(1);region=(tri[:,:,2].min(1)>=zlo)&(tri[:,:,2].max(1)<=zhi);selected=bad&region;removed=tri[selected];result=[tri[~selected]];cut=[];kept=[]
 for face in removed:
  polygon=[];crossings=[]
  for a,b in zip(face,np.roll(face,-1,axis=0)):
   da=a[axis]*sign-plane;db=b[axis]*sign-plane
   if da<=1e-8:polygon.append(a)
   if (da<0 and db>0)or(da>0 and db<0):
    p=a+(b-a)*da/(da-db);polygon.append(p);crossings.append(p)
  if len(polygon)>=3:
   for j in range(1,len(polygon)-1):kept.append([polygon[0],polygon[j],polygon[j+1]])
  if len(crossings)==2:cut.append(crossings)
 if kept:result.append(np.array(kept))
 assert cut,(axis,sign,plane,zlo,zhi)
 # The source is connected/watertight at each chosen turret bearing. Stitch loops.
 points=[];edges=[];lookup={}
 for line in cut:
  ids=[]
  for p in line:
   key=tuple(np.round(p,7))
   if key not in lookup:lookup[key]=len(points);points.append(p)
   ids.append(lookup[key])
  if ids[0]!=ids[1]:edges.append(ids)
 adj={j:[]for j in range(len(points))}
 for a,b in edges:adj[a].append(b);adj[b].append(a)
 assert all(len(v)==2 for v in adj.values()),(axis,sign,plane,zlo,zhi,[(j,len(v),points[j])for j,v in adj.items()if len(v)!=2][:5])
 unseen=set(adj);caps=[];loops=[];normal=np.eye(3)[axis]*sign
 while unseen:
  start=next(iter(unseen));loop=[start];previous=-1;current=start
  while True:
   choices=[v for v in adj[current]if v!=previous];nxt=choices[0]
   if nxt==start:break
   assert nxt not in loop;loop.append(nxt);previous,current=current,nxt
  unseen-=set(loop);p=np.array([points[j]for j in loop]);center=p.mean(0);loops.append({'center':center.tolist(),'vertices':len(p),'bounds':[p.min(0).tolist(),p.max(0).tolist()]})
  for a,b in zip(p,np.roll(p,-1,axis=0)):
   if np.dot(np.cross(a-center,b-center),normal)<0:a,b=b,a
   caps.append([center,a,b])
 result.append(np.array(caps));alltri=np.concatenate(result);q=np.cross(alltri[:,1]-alltri[:,0],alltri[:,2]-alltri[:,0]);alltri=alltri[np.linalg.norm(q,axis=1)>1e-8]
 return alltri,{'axis':axis,'sign':sign,'plane':plane,'source_z_window':[zlo,zhi],'source_faces_touched':int(selected.sum()),'cap_loops':loops}
def simplify(tri,target,error=.00018):
 if len(tri)<=target:return tri,{'input_triangles':len(tri),'output_triangles':len(tri),'target_triangles':target,'simplified':False,'reason':'Removal of fused high-density static PDC tops already brings hull below budget; all remaining faces retained.'}
 v,inv=np.unique(tri.reshape(-1,3).astype('float32'),axis=0,return_inverse=True);idx=np.ascontiguousarray(inv,dtype='uint32');dest=np.empty_like(idx);v=np.ascontiguousarray(v);lib=C.CDLL(str(MAIN/'.tools/libmeshoptimizer.so'));U=C.POINTER(C.c_uint);F=C.POINTER(C.c_float);fn=lib.meshopt_simplify;fn.argtypes=[U,U,C.c_size_t,F,C.c_size_t,C.c_size_t,C.c_size_t,C.c_float,C.c_uint,F];fn.restype=C.c_size_t;err=C.c_float();count=fn(dest.ctypes.data_as(U),idx.ctypes.data_as(U),len(idx),v.ctypes.data_as(F),len(v),12,target*3,error,0,C.byref(err));out=v[dest[:count].reshape(-1,3)].astype(float)
 q=np.cross(out[:,1]-out[:,0],out[:,2]-out[:,0]);out=out[np.linalg.norm(q,axis=1)>1e-7]
 return out,{'input_triangles':len(tri),'output_triangles':len(out),'target_triangles':target,'relative_error_limit':error,'reported_relative_error':err.value,'bound_change':(out.max((0,1))-tri.max((0,1))).tolist(),'method':'meshopt_simplify positions, conservative source-relative error; retain all triangles if target cannot be reached within tolerance'}
def prepare(kind):
 ID=IDS[kind];D=OUT/kind;D.mkdir(exist_ok=True);tt,src=source(kind);surgeries=[];length=270 if kind=='hale'else 200;srcmid=(tt.min((0,1))+tt.max((0,1)))/2;scale=length*UNITS/(tt[:,:,2].max()-tt[:,:,2].min());original=tt.copy()
 # Replace the connected, static gun tops at measured pedestal planes.
 if kind=='hale':
  for sign in[-1,1]:tt,cut=clip_top(tt,1,sign,5.01,7.8,15.4);surgeries.append(cut)
 else:
  for axis,sign,plane,zlo,zhi in[(1,1,45,40,90),(1,-1,45,40,90),(0,1,39,30,125),(0,-1,39,30,125),(1,1,41.037,202,255),(1,-1,41.037,202,255),(0,1,39,258,345),(0,-1,54,231,278)]:
   tt,cut=clip_top(tt,axis,sign,plane,zlo,zhi);surgeries.append(cut)
 opt={'simplified':False}
 if kind=='munroe':tt,opt=simplify(tt,260000)
 tt=(tt-srcmid)*scale;original=(original-srcmid)*scale;lo=tt.min((0,1));hi=tt.max((0,1));centre=tt.mean(1);q=np.cross(tt[:,1]-tt[:,0],tt[:,2]-tt[:,0]);face=q/np.linalg.norm(q,axis=1)[:,None]
 # Spatially assigned livery holds across projection seams. Blue UNN bands are
 # defined in hull space; subtle panel maps are reused from accepted Murphy art.
 mat=np.full(len(tt),'armor',dtype='<U16');mat[(centre[:,2]<lo[2]+length*UNITS*.19)]='machinery';bands=[-.20,.22]if kind=='hale'else[-.22,.16]
 for band in bands:mat[abs(centre[:,2]-band*length*UNITS)<length*UNITS*.024]='navy'
 mat[(abs(face[:,2])<.18)&(abs(centre[:,0])<hi[0]*.3)&(centre[:,2]>0)]='steel'
 parts=[]
 for material in['armor','machinery','navy','steel']:
  mask=mat==material
  if mask.any():p=frames(tt[mask]);p['material']=material;parts.append(p)
 extras=[];rigs=[];points=[{'name':'center','translation':[0,0,0]},{'name':'above','translation':[0,float(hi[1]+15),0]},{'name':'aura','translation':[0,float(lo[1]-15),0]}];donors={};pdc_scale=.65 if kind=='hale'else.55
 pdc_t=read(BASE/'entities/expanse15_truman_pdc_0.weapon')['turret'];pdc_t=copy.deepcopy(pdc_t)
 for key in['barrel_position','muzzle_positions']:pdc_t[key]=(np.array(pdc_t[key])*pdc_scale).tolist()
 for k in['base','barrel']:
  name=ID+'_pdc_'+k;srcpath=BASE/'meshes'/('expanse15_truman_pdc_'+k+'.mesh');pp=load_parts(srcpath)
  for p in pp:p['v']*=pdc_scale
  export(name,pp,[],D/name);donors[name]={'source':str(srcpath),'sha256':sha(srcpath),'scale':pdc_scale,'materials':[p['material']for p in pp]};pdc_t['biaxial_'+k+'_mesh']=name
 if kind=='hale':
  mountsites=[]
  # Twelve representative PDC batteries, in exterior hull quadrants.
  for z in[-.28,.02,.28]:
   for axis,sign in[(0,-1),(0,1),(1,-1),(1,1)]:
    p=np.array([sign*33. if axis==1 and z==.02 else 0.,0.,z*length*UNITS]);p[axis]=(hi[axis]if sign>0 else lo[axis])+sign*80;up=np.eye(3)[axis]*sign;hit=rayhit(tt,p,-up);mountsites.append((hit+up*4,up,hit))
 else:
  mountsites=[]
  for cut in surgeries:
   axis,sign=cut['axis'],cut['sign'];loop=max(cut['cap_loops'],key=lambda x:x['vertices']);p=(np.array(loop['center'])-srcmid)*scale;up=np.eye(3)[axis]*sign;mountsites.append((p+up*1.2,up,p))
 for j,(pos,up,contact)in enumerate(mountsites):
  extras.append(cylinder(contact-up*.4,pos,2.8 if kind=='hale'else 2.1,24));B=np.column_stack([np.cross(up,[0,0,1]),up,[0,0,1]]);name=ID+'_pdc_'+str(j);mount={'weapon':name,'mesh_point':'child.'+name,'weapon_position':pos.tolist(),'up':up.tolist(),'forward':[0,0,1],'yaw_arc':{'min_angle':-180.,'max_angle':180.},'pitch_arc':{'min_angle':-85.,'max_angle':-25.}};rigs.append({'kind':'pdc','mount':mount,'turret':pdc_t,'contact':contact.tolist()});points.append({'name':mount['mesh_point'],'translation':pos.tolist(),'rotation':Rotation.from_matrix(B).as_quat().tolist()})
 if kind=='hale':
  rail_scale=.75;rail_source=BASE/'meshes/expanse15_truman_rail_0.mesh';name=ID+'_rail_mesh';pp=load_parts(rail_source)
  for p in pp:p['v']*=rail_scale
  export(name,pp,[],D/name);donors[name]={'source':str(rail_source),'sha256':sha(rail_source),'scale':rail_scale,'materials':[p['material']for p in pp]};rt=copy.deepcopy(read(BASE/'entities/expanse15_truman_rail_0.weapon')['turret']);rt['gimbal_mesh']=name;rt['muzzle_positions']=(np.array(rt['muzzle_positions'])*rail_scale).tolist()
  for j,cut in enumerate(surgeries):
   sign=cut['sign'];c=max(cut['cap_loops'],key=lambda x:x['vertices'])['center'];pos=(np.array(c)-srcmid)*scale;up=np.array([0,sign,0]);B=np.diag([sign,sign,1]);name=ID+'_rail_'+str(j);mount={'weapon':name,'mesh_point':'child.'+name,'weapon_position':pos.tolist(),'up':up.tolist(),'forward':[0,0,1],'yaw_arc':{'min_angle':-12.,'max_angle':12.},'pitch_arc':{'min_angle':0.,'max_angle':0.}};rigs.append({'kind':'rail','mount':mount,'turret':rt});points.append({'name':mount['mesh_point'],'translation':pos.tolist(),'rotation':Rotation.from_matrix(B).as_quat().tolist()})
 else:
  # Source keel assembly is fixed. Actual foremost barrel endpoints, no turret.
  nose=tt.reshape(-1,3);nose=nose[nose[:,2]>hi[2]-4];pos=nose.mean(0);pos[2]=hi[2]+.3;name=ID+'_rail_0';mount={'weapon':name,'mesh_point':'weapon.keel_rail.0','weapon_position':pos.tolist(),'up':[0,1,0],'forward':[0,0,1],'yaw_arc':{'min_angle':-2.,'max_angle':2.},'pitch_arc':{'min_angle':-2.,'max_angle':2.}};rigs.append({'kind':'rail','mount':mount,'turret':None});points.append({'name':mount['mesh_point'],'translation':pos.tolist()})
 # Exhaust centers measured on source mouths; source geometry is not a drive count inference from screenshots.
 if kind=='hale':engines=[[-2.15061316,-.69877658,.0851],[2.15061316,-.69877658,.0851],[-1.32915203,1.82942082,.0851],[1.32915203,1.82942082,.0851],[0,-2.2612885,.0851]];radius=12
 else:engines=[[-22.4469,.0124,.342],[22.4389,.0125,.342],[-.0017,-23.1590,.342],[-.0061,23.1791,.342]];radius=12
 exhaust=[]
 for j,e in enumerate(engines):
  p=(np.array(e)-srcmid)*scale;p[2]-=.15;exhaust.append({'position':p.tolist(),'forward':[0,0,-1],'up':[0,1,0]});points.append({'name':'exhaust.'+str(j),'translation':p.tolist(),'rotation':[0,1,0,0]})
 ports=[]
 sites=[(2,1,[-.12,0,.38]),(2,1,[.12,0,.38]),(1,1,[-.10,.5,.05]),(1,1,[.10,.5,.05]),(1,-1,[-.10,-.5,.05]),(1,-1,[.10,-.5,.05])]
 for j,(axis,sign,f)in enumerate(sites):
  p=np.array(f)*np.array([hi[0]-lo[0],hi[1]-lo[1],hi[2]-lo[2]]);p[axis]=(hi[axis]+30)if sign>0 else(lo[axis]-30);direction=np.eye(3)[axis]*sign;hit=rayhit(tt,p,-direction);mouth=hit+direction*1.1;ports.append({'position':mouth.tolist(),'forward':direction.tolist(),'up':([0,1,0]if axis==2 else[0,0,1])});points.append({'name':'weapon.torpedo.'+str(j),'translation':mouth.tolist()})
 if extras:p=frames(np.concatenate(extras));p['material']='machinery';parts.append(p)
 # Compile one hull; donor rigs use their accepted material definitions.
 grouped={}
 for p in parts:
  key=p['material']
  if key not in grouped:grouped[key]=p
  else:
   dst=grouped[key];offset=len(dst['v']);dst['i']=np.concatenate([dst['i'],p['i']+offset])
   for attr in['v','n','t','uv']:dst[attr]=np.concatenate([dst[attr],p[attr]])
 parts=list(grouped.values())
 export(ID+'_hull',parts,points,D/(ID+'_hull'));htri=np.concatenate([p['v'][p['i']]for p in parts]);alltri=[htri];obstacles=[htri]
 for r in rigs:
  if not r['turret']:continue
  mount=r['mount'];B=np.column_stack([np.cross(mount['up'],mount['forward']),mount['up'],mount['forward']]);pos=np.array(mount['weapon_position']);t=r['turret'];names=[(t['gimbal_mesh'],np.zeros(3))]if t['type']=='gimbal'else[(t['biaxial_base_mesh'],np.zeros(3)),(t['biaxial_barrel_mesh'],np.array(t['barrel_position']))]
  for name,offset in names:
   donor=donors[name]
   for p in load_parts(Path(donor['source'])):
    transformed=(p['v'][p['i']]*donor['scale']+offset)@B.T+pos;alltri.append(transformed)
    if r['kind']=='rail':obstacles.append(transformed)
 alltri=np.concatenate(alltri);ray=Rays(np.concatenate(obstacles),BUILD/(kind+'-rays'));arc=[]
 for r in rigs:
  if r['kind']!='pdc':continue
  # Obstructions from own housing are excluded by origins at muzzle; stationary rail silhouettes are included. Moving PDC silhouettes are excluded. Narrow rectangles selected analytically.
  mask,_,_=sample(ray,r['mount'],r['turret'],np.arange(-180,181,4),np.arange(-85,-4,2),3);arcs,area=choose(mask,np.arange(-180,181,4),np.arange(-85,-4,2));r['mount'].update(arcs);aa=arcs['yaw_arc'];bb=arcs['pitch_arc'];blocked,example,n=sample(ray,r['mount'],r['turret'],np.arange(aa['min_angle'],aa['max_angle']+.01,2),np.arange(bb['min_angle'],bb['max_angle']+.01,2),3);assert not blocked.any(),example;arc.append({'weapon':r['mount']['weapon'],'arcs':arcs,'samples':n,'blocked':0});print(kind,r['mount']['weapon'],arcs,flush=True)
 ray.close();v=alltri.reshape(-1,3);lo2=v.min(0);hi2=v.max(0);mid=(lo2+hi2)/2
 meta={'status':'PREPARED','ID':ID,'game_output':str(GAME),'source':src,'source_to_game':{'center':srcmid.tolist(),'scale':scale,'length_metres':length,'units_per_metre':UNITS,'axis':'source +Z bow, +Y up; original silhouette preserved'},'surgeries':surgeries,'optimization':opt,'donors':donors,'hull_mesh':ID+'_hull','hull_materials':[p['material']for p in parts],'meshpoints':points,'rigs':rigs,'ports':ports,'exhausts':exhaust,'spatial':{'box':{'center':mid.tolist(),'extents':((hi2-lo2)/2).tolist()},'radius':float(np.linalg.norm(v-mid,axis=1).max())},'counts':{'hull':len(htri),'assembled':len(alltri),'pdc_count':len(mountsites),'rail_count':sum(r['kind']=='rail'for r in rigs)},'arc_checks':arc,'runtime':'NOT RUN'};write(AUD/(kind+'-integration.json'),meta);np.savez_compressed(D/'hull-triangles.npz',tri=htri);print('PREPARED',kind,meta['counts'],flush=True)
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('kind',choices=IDS);prepare(p.parse_args().kind)
