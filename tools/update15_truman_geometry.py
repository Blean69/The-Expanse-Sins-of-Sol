"""Retain full textured Truman geometry, separate its two modeled railgun assemblies, add measured PDC retrofits."""
from pathlib import Path
import copy,json,numpy as np
from scipy.spatial.transform import Rotation
from common import Gltf,write
import update12_scirocco_common as c
from update14_pdc_arcs import Rays,pose,sample,choose
R=Path(__file__).resolve().parents[1];D=R/'assets/derived/update15-truman';A=R/'audit/update15-truman';BUILD=R/'build/update15-truman';P='expanse15_truman';DONOR=Path('/run/media/haker/NVME 2/expanse-workers/tachi-one-pdc');c.OUT=D
z=np.load(D/'normalized.npz');src={k:z[k]for k in ['v','n','t','uv','i']};labels=z['component'];fv=src['v'].astype('float32').astype('float64');fi=src['i'];area=np.linalg.norm(np.cross(fv[fi[:,1]]-fv[fi[:,0]],fv[fi[:,2]]-fv[fi[:,0]]),axis=1);valid=area>=1e-4;write(A/'float32-sliver-audit.json',{'source_triangles':len(fi),'removed_float32_microslivers':int((~valid).sum()),'minimum_double_area':1e-4,'purpose':'Remove numerically collinear source faces whose sign is unstable between compiler JSON decimal serialization andbinaryfloat32'});src['i']=src['i'][valid];labels=labels[valid];comp=json.loads((A/'components.json').read_text())['components'];railids=[]
for sign in [1,-1]:railids.append([r['component']for r in comp if min(sign*r['bounds'][0][1],sign*r['bounds'][1][1])>125 and r['bounds'][0][2]>-140 and r['bounds'][1][2]<26])
def subset(mask):
 idx=src['i'][mask];used,remap=np.unique(idx,return_inverse=True);p={k:src[k][used].copy()for k in ['v','n','t','uv']};p['i']=remap.reshape(-1,3);p['material']='truman_material';return p
parts={'hull':[subset(~np.isin(labels,sum(railids,[])))]};rigs=[]
# Two actual source assemblies on their retained circular bearings, narrow yaw only.
for j,ids in enumerate(railids):
 sign=[1,-1][j];p=subset(np.isin(labels,ids));pivot=np.array([0,sign*126,-81.1756]);B=np.diag([sign,sign,1]);p['v']=(p['v']-pivot)@B;p['n']=p['n']@B;p['t'][:,:3]=p['t'][:,:3]@B;parts['rail_'+str(j)]=[p];m=[11,9,105.4];name=f'{P}_rail_{j}'
 rigs.append({'index':18+j,'kind':'rail','mount':{'weapon':name,'mesh_point':'child.'+name,'weapon_position':pivot.tolist(),'up':[0,sign,0],'forward':[0,0,1],'yaw_arc':{'min_angle':-12.,'max_angle':12.},'pitch_arc':{'min_angle':0.,'max_angle':0.}},'basis_columns':B.tolist(),'yaw_pivot_hull':pivot.tolist(),'pitch_pivot_hull':pivot.tolist(),'muzzle_hull':(pivot+B@np.array(m)).tolist(),'turret_override':{'type':'gimbal','gimbal_mesh':name,'muzzle_positions':[m,[-11,9,105.4]]},'skin_alias_map':[{'mesh_alias_name':name,'mesh_definition':{'mesh':name,'shader':'ship','is_shadow_blocker':True}}],'source_components':ids})
# The source mesh partitions do not identify usable independent PDC gun assemblies.
# Eighteen explicit surface retrofits represent three batteries around the six-sided hull.
tri=src['v'][src['i']];ray=Rays(tri,BUILD/'ray-check');donor=json.loads((DONOR/'audit/polish-b/mount-metadata.json').read_text())['rigs'][0];S=2.5;off=np.array(donor['turret_override']['barrel_position'])*S;mu=np.array(donor['turret_override']['muzzle_positions'][0])*S
for kind in ['base','barrel']:
 g=Gltf(DONOR/'assets/derived/polish-b'/f'expanse_polish_pdc_0_{kind}.gltf');pp=[]
 for pr in g.g['meshes'][0]['primitives']:
  p={k:g.accessor(pr['attributes'][at])for k,at in [('v','POSITION'),('n','NORMAL'),('t','TANGENT'),('uv','TEXCOORD_0')]};p['v'][:,2]*=-1;p['v']*=S;p['n'][:,2]*=-1;p['t'][:,2:4]*=-1;p.update(i=g.accessor(pr['indices']).reshape(-1,3),material='mcrn_tachi_material');pp.append(p)
 parts['pdc_'+kind]=pp
support=[]
def cylinder(a,b,r=3.8):
 axis=b-a;axis/=np.linalg.norm(axis);u=np.cross(axis,[0,0,1]);u/=np.linalg.norm(u);w=np.cross(axis,u);v=np.cos(np.arange(24)*np.pi/12)[:,None]*u*r+np.sin(np.arange(24)*np.pi/12)[:,None]*w*r
 for i in range(24):
  j=(i+1)%24;support.extend([[a+v[i],a+v[j],b+v[j]],[a+v[i],b+v[j],b+v[i]],[a,a+v[j],a+v[i]],[b,b+v[i],b+v[j]]])
for zz in [-260.,65.,365.]:
 for angle in [30,90,150,210,270,330]:
  i=len([r for r in rigs if r['kind']=='pdc']);up=np.array([np.cos(np.radians(angle)),np.sin(np.radians(angle)),0]);origin=up*350+[0,0,zz];distance=ray([origin],[-up],1000)[0];assert distance>0;contact=origin-distance*up;side=np.cross(up,[0,0,1]);foot=(abs(src['v']@side)<7)&(abs(src['v'][:,2]-zz)<7)&(src['v']@up>0);outer=max(float(contact@up),float((src['v'][foot]@up).max()));pivot=contact+up*(outer-float(contact@up)+6);B=np.column_stack([np.cross(up,[0,0,1]),up,[0,0,1]]);cylinder(contact-up,pivot)
  name=f'{P}_pdc_{i}';mount={'weapon':name,'mesh_point':'child.'+name,'weapon_position':pivot.tolist(),'up':up.tolist(),'forward':[0,0,1],'yaw_arc':{'min_angle':-180.,'max_angle':180.},'pitch_arc':{'min_angle':-85.,'max_angle':-25.}};turret={'type':'biaxial','biaxial_base_mesh':P+'_pdc_base','biaxial_barrel_mesh':P+'_pdc_barrel','barrel_position':off.tolist(),'muzzle_positions':[mu.tolist()]}
  rigs.append({'index':i,'kind':'pdc','mount':mount,'basis_columns':B.tolist(),'yaw_pivot_hull':pivot.tolist(),'pitch_pivot_hull':(pivot+B@off).tolist(),'muzzle_hull':(pivot+B@(off+mu)).tolist(),'turret_override':turret,'skin_alias_map':[{'mesh_alias_name':P+'_pdc_'+k,'mesh_definition':{'mesh':P+'_pdc_'+k,'shader':'ship','is_shadow_blocker':True}}for k in ['base','barrel']],'measured_contact':contact.tolist(),'source':'Derivative retrofit measured from actual hull; battery representation, not42individualsourcePDCidentifications'})
parts['hull'].append(c.frames(np.array(support),'truman_support'));rigs.sort(key=lambda r:r['index'])
# Measured source apertures at the bow: four separated launcher origins.
ports=[]
for x,y in [(-35,0),(35,0),(-16,-30),(16,-30)]:
 origin=np.array([x,y,500.]);hit=ray([origin],[[0,0,-1]],1000)[0];assert hit>0;contact=origin-[0,0,hit];ports.append({'position':(contact+[0,0,.7]).tolist(),'forward':[0,0,1],'up':[0,1,0],'measured_surface':contact.tolist(),'source':'Measured bow launch origin; exact screen tube correspondence unverified'})
exhausts=[]
for ci in [185,186,1778,1779,3702,3703]:
 r=next(r for r in comp if r['component']==ci);lo,hi=np.array(r['bounds']);v=(lo+hi)/2;v[2]=lo[2]-.25;exhausts.append({'position':v.tolist(),'forward':[0,0,-1],'up':[0,1,0],'source_component':ci})
points=[{'name':'center','translation':[0,0,0]},{'name':'above','translation':[0,180,0]},{'name':'aura','translation':[0,-180,0]}]
for r in rigs:points.append({'name':r['mount']['mesh_point'],'translation':r['yaw_pivot_hull'],'rotation':Rotation.from_matrix(r['basis_columns']).as_quat().tolist()})
for i,p in enumerate(ports):points.append({'name':f'weapon.torpedo.{i}','translation':p['position']})
for i,p in enumerate(exhausts):points.append({'name':f'exhaust.{i}','translation':p['position'],'rotation':[0,1,0,0]})
# Strict outward arcs sampled against full source hull including both stationary rail silhouettes.
arc_results=[]
for r in rigs:
 if r['kind']!='pdc':continue
 mount=r['mount'];turret=r['turret_override'];ya=np.arange(-180,181,4.);pa=np.arange(-85,-4,2.);mask,_,_=sample(ray,mount,turret,ya,pa,3.);arcs,area=choose(mask,ya,pa);mount.update(arcs);yy=arcs['yaw_arc'];pp=arcs['pitch_arc'];blocked,ex,n=sample(ray,mount,turret,np.arange(yy['min_angle'],yy['max_angle']+.01,1),np.arange(pp['min_angle'],pp['max_angle']+.01,1),3.);assert not blocked.any(),ex;arc_results.append({'weapon':mount['weapon'],'arcs':arcs,'rays':n,'blocked':0,'firing_tolerance':1.});print(mount['weapon'],arcs,flush=True)
ray.close();write(A/'arc-validation.json',{'status':'PASS OFFLINE SAMPLED RAYS','entries':arc_results,'limitations':'Sampled1degreepositions/+/-3degreeaimenvelope; stationaryhullandrail silhouettes. Engine and movingneighbor turrets NOT RUN.'})
sourceframes={};assembled=copy.deepcopy(parts['hull'])
for kind,pp in parts.items():
 c.savegltf(P+'_'+kind,pp,points if kind=='hull'else[]);sourceframes[kind]={str(i):{k:p[k].tolist()for k in ['v','n','t','uv']}for i,p in enumerate(pp)}
for r in rigs:
 B=np.array(r['basis_columns']);origin=np.array(r['yaw_pivot_hull']);kinds=[('pdc_base',np.zeros(3)),('pdc_barrel',off)]if r['kind']=='pdc'else[('rail_'+str(r['index']-18),np.zeros(3))]
 for kind,offset in kinds:
  for pp in parts[kind]:
   p=copy.deepcopy(pp);p['v']=(p['v']+offset)@B.T+origin;p['n']=p['n']@B.T;p['t'][:,:3]=p['t'][:,:3]@B.T;assembled.append(p)
c.savegltf(P+'_editable',assembled,compiler=False);v=np.concatenate([p['v']for p in assembled]);lo=v.min(0);hi=v.max(0);bc=(lo+hi)/2
meta={'status':'COMPILER PENDING','game_directory':str(BUILD/'game'),'hull_mesh':P+'_hull','rigs':rigs,'ship_spatial':{'box':{'center':bc.tolist(),'extents':((hi-lo)/2).tolist()},'radius':float(np.linalg.norm(v-bc,axis=1).max()),'bounds_min':lo.tolist(),'bounds_max':hi.tolist()},'equipment':{'light_torpedo_ports':ports,'light_torpedo_port':ports[0],'torpedo_ports':ports,'exhaust':exhausts[0],'exhausts':exhausts},'counts':{k:sum(len(p['i'])for p in pp)for k,pp in parts.items()},'assembled_triangle_total':sum(len(p['i'])for p in assembled),'meshpoints':{k:points if k=='hull'else[]for k in parts},'editable_source':str(D/(P+'_editable.gltf')),'runtime':'NOT RUN'}
write(D/'retained-source-frames.json',sourceframes);write(A/'integration-spec.json',meta);np.savez(D/'assembled.npz',v=v);print(meta['assembled_triangle_total'])
