"""Restore source Raptor/Pella detail with explicit engine budgets and frozen mounts.
Original STL, source intake, previous packages, and shared game assets are read-only.
"""
from pathlib import Path
import numpy as np,ctypes as c,json,hashlib,copy,shutil,struct,os,subprocess
from scipy.sparse import coo_matrix
from scipy.sparse.csgraph import connected_components
from scipy.spatial.transform import Rotation
import sys
sys.path.insert(0,'/run/media/haker/NVME 2/expanse-mod/tools')
from polish_ui import write,render
from common import Gltf
import argparse
ap=argparse.ArgumentParser();ap.add_argument('--variant',choices=['raptor','pella'],default='raptor');args=ap.parse_args();VARIANT=args.variant
ROOT=Path(__file__).resolve().parents[1];INTAKE=Path('/run/media/haker/NVME 2/expanse-workers/weapon-behavior/assets/derived/update12-a');OUT=ROOT/'assets/derived/update14-hulls'/VARIANT;AUD=ROOT/'audit/update14-hulls'/VARIANT;BUILD=ROOT/'build/update14-hulls'/VARIANT;MAIN=Path('/run/media/haker/NVME 2/expanse-mod');DONOR=Path('/run/media/haker/NVME 2/expanse-workers/tachi-one-pdc');PREFIX='expanse12_'+VARIANT
OUT.mkdir(parents=True,exist_ok=True);AUD.mkdir(parents=True,exist_ok=True)
BUILD.mkdir(parents=True,exist_ok=True)
original=Path('/home/haker/Downloads/xxx_-_raptor_whole.stl');assert hashlib.sha256(original.read_bytes()).hexdigest()=='c06878f57e5b9f04043793226f8c6a06b082848273ea6fc9e9369f474c8dedd6'
z=np.load(INTAKE/'source-welded.npz');v=z['v'];idx=z['i'];edges=np.concatenate([idx[:,[0,1]],idx[:,[1,2]],idx[:,[2,0]]]);_,lab=connected_components(coo_matrix((np.ones(len(edges)),(edges[:,0],edges[:,1])),shape=(len(v),len(v))),directed=False)
# Exact source components: retain nine bay housings; remove stowed gun/door/latch/brace parts only.
clusters=[{'body':77,'housing':69,'other':[67,72,74,76]}, {'body':78,'housing':68,'other':[66,71,73,75]}, {'body':129,'housing':123,'other':[122,126,127,128]}, {'body':155,'housing':148,'other':[145,150,152,154]}, {'body':156,'housing':147,'other':[144,149,151,153]}, {'body':255,'housing':236,'other':[240,244,248,250]}, {'body':256,'housing':235,'other':[239,243,247,249]}, {'body':257,'housing':238,'other':[242,246,252,254]}, {'body':258,'housing':237,'other':[241,245,251,253]}]
removed=[c['body'] for c in clusters]+[k for c in clusters for k in c['other']]
source_v=v.copy();source_idx=idx.copy();idx=idx[~np.isin(lab[idx[:,0]],removed)]
lo=v.min(0);hi=v.max(0);center=(lo+hi)/2;scale=(89/46*105)/(hi[0]-lo[0]);R=np.array([[0,0,1],[0,1,0],[-1,0,0]]) # source-X bow ->game+Z; source+Yup, proper rotation
v=(v-center)@R.T*scale
lib=c.CDLL(str(MAIN/'.tools/libmeshoptimizer.so'));u=c.POINTER(c.c_uint);f=c.POINTER(c.c_float);fn=lib.meshopt_simplify;fn.argtypes=[u,u,c.c_size_t,f,c.c_size_t,c.c_size_t,c.c_size_t,c.c_float,c.c_uint,f];fn.restype=c.c_size_t
# Restore real source detail. Separate engine budgets keep their circular rims intact.
pos=np.ascontiguousarray(v,dtype='float32'); engine_ids=[287,288,289,290]
component=lab[idx[:,0]];records=[];pieces=[]
for label,selection,target,tolerance in [('hull',~np.isin(component,engine_ids),180000,.0007)]+[(str(c0),component==c0,16000,.00015)for c0 in engine_ids]:
 ii=np.ascontiguousarray(idx[selection].ravel(),dtype='uint32');dst=np.empty_like(ii);error=c.c_float()
 nn=fn(dst.ctypes.data_as(u),ii.ctypes.data_as(u),len(ii),pos.ctypes.data_as(f),len(pos),12,target*3,tolerance,0,c.byref(error))
 q=pos[dst[:nn].reshape(-1,3)].astype(float);cross=np.cross(q[:,1]-q[:,0],q[:,2]-q[:,0]);area=np.linalg.norm(cross,axis=1);edge=np.max(np.linalg.norm(q-np.roll(q,1,axis=1),axis=2),axis=1);valid=(area>1e-7)&(area/np.maximum(edge**2,1e-20)>1e-6);pieces.append(q[valid]);records.append(dict(component=label,source_triangles=len(ii)//3,target=target,triangles=int(valid.sum()),relative_error=error.value,error_limit=tolerance,degenerates_removed=int((~valid).sum())))
tri=np.concatenate(pieces)
# STL triangle winding, not unreliable STL facet normals, defines authored faces.
# Negative source transform determinant is compensated once.
if np.linalg.det(R)<0:tri=tri[:,[0,2,1]]
np.savez(OUT/'optimized-hull.npz',tri=tri)
write(AUD/'optimization.json',{'source_triangles':1513390,'removed_static_gun_components':removed,'triangles_after_gun_removal':len(idx),'optimized_hull_triangles':len(tri),'component_budgets':records,'source_center':center.tolist(),'source_to_game_rotation':R.tolist(),'uniform_scale':scale,'provisional_length':89/46*105,'source_format':'STL: no UV/material/animation source','original_sha256':hashlib.sha256(original.read_bytes()).hexdigest(),'source_welded_sha256':hashlib.sha256((INTAKE/'source-welded.npz').read_bytes()).hexdigest(),'runtime':'NOT RUN'})
print(len(tri),error.value,flush=True)
# Measured ray/surface attachment on the reduced derivative.
# All established attachment coordinates remain exact. They are not resampled after reduction.
old=json.loads((Path('/run/media/haker/NVME 2/expanse-workers/weapon-behavior/audit/update12-a')/VARIANT/'integration-spec.json').read_text())
contacts=iter([r['measured_contact']for r in old['rigs']]+[p['measured_surface']for p in old['equipment']['torpedo_ports']]+[old['equipment']['boarding']['measured_surface']])
def ray(origin,direction):return np.array(next(contacts),float)
shapes={'hull':[]};colors=([[.24,.28,.31,1],[.65,.16,.055,1],[.075,.085,.095,1],[.07,.35,.8,1]] if VARIANT=='raptor' else [[.67,.70,.73,1],[.39,.43,.47,1],[.055,.065,.075,1],[.07,.35,.8,1]])
def addtri(t,material=0):shapes['hull'].append((np.asarray(t,float).reshape(-1,3,3),material))
# Procedural matte grey hull with orange support collars. Source had no colors.
# Geometrically split paint boundaries so material stripes stay straight across large triangles.
limits=[-1e6,-61.,-55.,37.,43.,1e6]
def clip(poly,z,above):
 out=[]
 for a,b in zip(poly,poly[1:]+poly[:1]):
  ia=(a[2]>=z) if above else (a[2]<=z);ib=(b[2]>=z) if above else (b[2]<=z)
  if ia:out.append(a)
  if ia!=ib:out.append(a+(b-a)*((z-a[2])/(b[2]-a[2])))
 return out
for k,(low,high) in enumerate(zip(limits,limits[1:])):
 allin=(tri[:,:,2].min(1)>=low)&(tri[:,:,2].max(1)<=high);pieces=list(tri[allin])
 touch=(tri[:,:,2].max(1)>low)&(tri[:,:,2].min(1)<high)&~allin
 for t0 in tri[touch]:
  poly=clip(clip(list(t0),low,True),high,False)
  for j in range(1,len(poly)-1):
   q=np.array([poly[0],poly[j],poly[j+1]])
   if np.linalg.norm(np.cross(q[1]-q[0],q[2]-q[0]))>1e-7:pieces.append(q)
 if pieces:addtri(pieces,1 if k in [1,3] else 0)

def cyl(p0,p1,radius,segments=16):
 p0=np.array(p0);p1=np.array(p1);ax=p1-p0;ax/=np.linalg.norm(ax);u=np.eye(3)[np.argmin(abs(ax))];u-=ax*np.dot(ax,u);u/=np.linalg.norm(u);w=np.cross(ax,u);r=radius*(np.cos(np.arange(segments)*2*np.pi/segments)[:,None]*u+np.sin(np.arange(segments)*2*np.pi/segments)[:,None]*w);a=p0+r;b=p1+r
 for i in range(segments):
  j=(i+1)%segments;addtri([a[i],a[j],b[j]],1);addtri([a[i],b[j],b[i]],1);addtri([p0,a[j],a[i]],2);addtri([p1,b[i],b[j]],2)
rigs=[];donor=json.loads((DONOR/'audit/polish-b/mount-metadata.json').read_text())['rigs'][0];off=np.array(donor['turret_override']['barrel_position']);muzzle=np.array(donor['turret_override']['muzzle_positions'][0]);donor_meshes={}
for part in ['base','barrel']:
 source=DONOR/'assets/derived/polish-b'/f'expanse_polish_pdc_0_{part}.gltf';g=Gltf(source);parts=[]
 for p in g.g['meshes'][0]['primitives']:
  vv=g.accessor(p['attributes']['POSITION']);nn=g.accessor(p['attributes']['NORMAL']);tt=g.accessor(p['attributes']['TANGENT']);vv[:,2]*=-1;nn[:,2]*=-1;tt[:,2]*=-1;tt[:,3]*=-1;parts.append({'v':vv,'n':nn,'t':tt,'uv':g.accessor(p['attributes']['TEXCOORD_0']),'i':g.accessor(p['indices']).reshape(-1,3),'material':'mcrn_tachi_material'})
 donor_meshes[part]=parts
for i,c0 in enumerate(clusters):
 body=source_v[source_idx[lab[source_idx[:,0]]==c0['body']]].reshape(-1,3);housing=source_v[source_idx[lab[source_idx[:,0]]==c0['housing']]].reshape(-1,3)
 # Closed doors are two1036-triangle components; fit their outward normal rather than assume radial orientation.
 door_ids=[q for q in c0['other'] if int((lab[source_idx[:,0]]==q).sum())==1036]
 doors=source_v[source_idx[np.isin(lab[source_idx[:,0]],door_ids)]].reshape(-1,3);cov=np.cov(doors.T);evals,axes=np.linalg.eigh(cov);su=axes[:,0];su[0]=0;su/=np.linalg.norm(su)
 if np.dot(su,doors.mean(0)-body.mean(0))<0:su=-su
 up=R@su;B=np.column_stack([np.cross(up,[0,0,1]),up,[0,0,1]])
 anchor=(body.min(0)+body.max(0))/2;anchor[0]=body[:,0].max()-2.0;probe=(anchor-center)@R.T*scale
 contact=ray(probe+up*20,-up);hg=(housing-center)@R.T*scale;outer=float(np.max(hg@up));pivot=contact+up*max(.45,outer-np.dot(contact,up)+.15);cyl(contact-up*.5,pivot,1.22)
 mount={'weapon':f'{PREFIX}_pdc_{i}','mesh_point':f'child.{PREFIX}_pdc_{i}','weapon_position':pivot.tolist(),'up':up.tolist(),'forward':[0,0,1],'yaw_arc':{'min_angle':-180.,'max_angle':180.},'pitch_arc':{'min_angle':-85.,'max_angle':5.}}
 rigs.append({'index':i,'kind':'pdc','mount':mount,'basis_columns':B.tolist(),'yaw_pivot_hull':pivot.tolist(),'pitch_pivot_hull':(pivot+B@off).tolist(),'muzzle_hull':(pivot+B@(off+muzzle)).tolist(),'turret_override':{'type':'biaxial','biaxial_base_mesh':PREFIX+'_pdc_base','biaxial_barrel_mesh':PREFIX+'_pdc_barrel','barrel_position':off.tolist(),'muzzle_positions':[muzzle.tolist()]},'skin_alias_map':[{'mesh_alias_name':PREFIX+'_pdc_'+part,'mesh_definition':{'mesh':PREFIX+'_pdc_'+part,'shader':'ship','is_shadow_blocker':True}} for part in ['base','barrel']],'measured_contact':contact.tolist(),'support_embed_depth':.5,'source_cluster':c0,'source_door_normal':su.tolist(),'support_height':float(np.linalg.norm(pivot-contact)),'runtime':'NOT RUN'})
ports=[]
# Nine authored forward collars on measured surfaces: four outer, two middle and three lower.
# Source bay/aperture identity is not supplied; these are explicit retrofits, not nine proven canonical tubes.
layout=[(95,-65),(95,65),(30,-70),(30,70),(60,-30),(60,30),(10,-30),(10,0),(10,30)]
for sy,sz in layout:
 probe=(np.array([-900,sy,sz])-center)@R.T*scale;contact=ray(probe,[0,0,-1]);x,y=contact[:2];z0=contact[2]-.25;z1=contact[2]+1.35;r0=1.85;r1=1.6;angles=np.arange(16)*2*np.pi/16;ring=np.column_stack([np.cos(angles),np.sin(angles)]);oo=ring*r0+[x,y];inn=ring*r1+[x,y]
 for i in range(16):
  j=(i+1)%16
  for q in [[[ *oo[i],z0],[ *oo[j],z0],[ *oo[j],z1]],[[ *oo[i],z0],[ *oo[j],z1],[ *oo[i],z1]],[[ *oo[i],z1],[ *oo[j],z1],[ *inn[j],z1]],[[ *oo[i],z1],[ *inn[j],z1],[ *inn[i],z1]],[[*inn[i],z0],[*inn[j],z1],[*inn[j],z0]],[[*inn[i],z0],[*inn[i],z1],[*inn[j],z1]]]:addtri(q,2)
  addtri([[x,y,z0+.01],[*inn[i],z0+.01],[*inn[j],z0+.01]],2)
 ports.append({'position':[x,y,z1+.05],'up':[0,1,0],'forward':[0,0,1],'measured_surface':contact.tolist(),'new_collar':True,'inner_diameter':3.2,'source':'Authored retrofit on measured forward surface; exact screen port correspondence unverified'})
exhausts=[]
for component in [287,288,289,290]:
 bell=source_v[source_idx[lab[source_idx[:,0]]==component]].reshape(-1,3);es=(bell.min(0)+bell.max(0))/2;es[0]=bell[:,0].max()+.5;ep=(es-center)@R.T*scale;exhausts.append({'position':ep.tolist(),'forward':[0,0,-1],'up':[0,1,0],'source_component':component,'source':'Actual source engine-bell aftmost outlet plane, centered on measured Y/Z bounds'})
exhaust=exhausts[0]
boarding_contact=ray([100,0,0],[-1,0,0]);boarding={'position':(boarding_contact+np.array([.5,0,0])).tolist(),'forward':[1,0,0],'up':[0,1,0],'measured_surface':boarding_contact.tolist(),'source':'Measured external starboard surface; prototype pod origin, source airlock identity unverified'}
points=[{'name':'center','translation':[0,0,0]},{'name':'above','translation':[0,40,0]},{'name':'aura','translation':[0,-40,0]}]
points.append({'name':'weapon.boarding.0','translation':boarding['position'],'rotation':Rotation.from_matrix(np.array([[0,0,1],[0,1,0],[-1,0,0]])).as_quat().tolist()})
for r in rigs:points.append({'name':r['mount']['mesh_point'],'translation':r['yaw_pivot_hull'],'rotation':Rotation.from_matrix(r['basis_columns']).as_quat().tolist()})
for i,p in enumerate(ports):points.append({'name':f'weapon.torpedo.{i}','translation':p['position']})
for i,p in enumerate(exhausts):points.append({'name':f'exhaust.{i}','translation':p['position'],'rotation':[0,1,0,0]})
# Authored per-face projection gives valid UV derivatives. Average only similar normals at coincident vertices.
from collections import defaultdict
allparts={};sourceframes={}
for material in range(3):
 tt=np.concatenate([t for t,m in shapes['hull'] if m==material]);vv=tt.reshape(-1,3);face=np.cross(tt[:,1]-tt[:,0],tt[:,2]-tt[:,0]);face/=np.linalg.norm(face,axis=1)[:,None];norm=np.repeat(face,3,axis=0);corner_weights=np.linalg.norm(np.cross(tt[:,1]-tt[:,0],tt[:,2]-tt[:,0]),axis=1).repeat(3);groups=defaultdict(list)
 for j,p in enumerate(np.round(vv,5)):groups[tuple(p)].append(j)
 for ids in groups.values():
  ns=norm[ids].copy();matches=ns@ns.T>np.cos(np.deg2rad(25));weights=corner_weights[ids];nn=matches@(ns*weights[:,None]);nn/=np.linalg.norm(nn,axis=1)[:,None];norm[ids]=nn
 uv=[];tan=[]
 for k,nn in enumerate(face):
  axis=np.eye(3)[np.argmin(abs(nn))];axis-=nn*np.dot(axis,nn);axis/=np.linalg.norm(axis);bit=np.cross(nn,axis);uv.extend(np.column_stack([tt[k]@axis,tt[k]@bit])*.05)
  for n in norm[k*3:k*3+3]:t=axis-n*np.dot(axis,n);t/=np.linalg.norm(t);tan.append([*t,1.])
 uv=np.array(uv);uv=.05+.9*(uv-uv.min(0))/np.maximum(np.ptp(uv,axis=0),1e-9)
 allparts.setdefault('hull',[]).append({'v':vv,'n':norm,'t':np.array(tan),'uv':np.array(uv),'i':np.arange(len(vv)).reshape(-1,3),'material':PREFIX+f'_mat_{material}'})
allparts.update({'pdc_'+k:p for k,p in donor_meshes.items()})
def savegltf(name,parts,meshpoints=[],compiler=True):
 g={'asset':{'version':'2.0','generator':'Raptor/Pella procedural STL derivative; source unchanged'},'scene':0,'scenes':[{'nodes':[0]}],'nodes':[{'mesh':0,'name':name,'children':[]}],'meshes':[{'primitives':[]}],'materials':[],'buffers':[],'bufferViews':[],'accessors':[]};buf=bytearray()
 def acc(a,typ,ct=5126):
  a=np.asarray(a,dtype='<f4' if ct==5126 else '<u4');buf.extend(b'\0'*((-len(buf))%4));start=len(buf);buf.extend(a.tobytes());g['bufferViews'].append({'buffer':0,'byteOffset':start,'byteLength':a.nbytes});x={'bufferView':len(g['bufferViews'])-1,'componentType':ct,'count':len(a),'type':typ}
  if typ=='VEC3':x.update(min=a.min(0).tolist(),max=a.max(0).tolist())
  g['accessors'].append(x);return len(g['accessors'])-1
 for p in parts:
  vv=p['v'].copy();nn=p['n'].copy();tt=p['t'].copy();idx=p['i'].copy();q=np.cross(vv[idx[:,1]]-vv[idx[:,0]],vv[idx[:,2]]-vv[idx[:,0]]);flip=np.sum(q*nn[idx].mean(1),axis=1)<0;idx[flip]=idx[flip][:,[0,2,1]]
  if compiler:vv[:,2]*=-1;nn[:,2]*=-1;tt[:,2]*=-1;tt[:,3]*=-1
  mat=p['material'];factor=colors[int(mat[-1])] if '_mat_'in mat else [.18,.2,.22,1];mi=len(g['materials']);g['materials'].append({'name':mat,'pbrMetallicRoughness':{'baseColorFactor':factor,'metallicFactor':.82 if VARIANT=='pella' else .4,'roughnessFactor':.3 if VARIANT=='pella' else .7}});g['meshes'][0]['primitives'].append({'mode':4,'material':mi,'indices':acc(idx.ravel(),'SCALAR',5125),'attributes':{'POSITION':acc(vv,'VEC3'),'NORMAL':acc(nn,'VEC3'),'TANGENT':acc(tt,'VEC4'),'TEXCOORD_0':acc(p['uv'],'VEC2')}})
 for p in meshpoints:
  p=copy.deepcopy(p)
  if compiler:
   p['translation'][2]*=-1
   if 'rotation'in p:p['rotation'][0]*=-1;p['rotation'][1]*=-1
  g['nodes'][0]['children'].append(len(g['nodes']));g['nodes'].append(p)
 g['buffers']=[{'uri':name+'.bin','byteLength':len(buf)}];(OUT/(name+'.bin')).write_bytes(buf);write(OUT/(name+'.gltf'),g)
for kind,parts in allparts.items():
 savegltf(PREFIX+'_'+kind,parts,points if kind=='hull'else[]);sourceframes[kind]={str(i):{k:part[k].tolist() for k in ['v','n','t','uv']} for i,part in enumerate(parts)}
assembled=copy.deepcopy(allparts['hull'])
for r in rigs:
 B=np.array(r['basis_columns']);origin=np.array(r['yaw_pivot_hull'])
 for part,offset in [('base',np.zeros(3)),('barrel',off)]:
  for pp in donor_meshes[part]:
   p=copy.deepcopy(pp);p['v']=(p['v']+offset)@B.T+origin;p['n']=p['n']@B.T;p['t'][:,:3]=p['t'][:,:3]@B.T;assembled.append(p)
savegltf(PREFIX+'_editable',assembled,compiler=False)
vall=np.concatenate([p['v']for p in assembled]);lo=vall.min(0);hi=vall.max(0);bc=(lo+hi)/2;spatial={'box':{'center':bc.tolist(),'extents':((hi-lo)/2).tolist()},'radius':float(np.linalg.norm(vall-bc,axis=1).max()),'bounds_min':lo.tolist(),'bounds_max':hi.tolist()};counts={k:sum(len(p['i']) for p in parts)for k,parts in allparts.items()};total=sum(len(p['i'])for p in assembled)
write(OUT/'retained-source-frames.json',sourceframes);meta={'status':'COMPILER PENDING','game_directory':str(BUILD/'game'),'hull_mesh':PREFIX+'_hull','rigs':rigs,'ship_spatial':spatial,'equipment':{'light_torpedo_ports':ports,'light_torpedo_port':ports[0],'torpedo_ports':ports,'exhaust':exhaust,'exhausts':exhausts,'boarding':boarding},'exhaust_geometry':exhaust,'counts':counts,'assembled_triangle_total':total,'meshpoints':{'hull':points,'pdc_base':[],'pdc_barrel':[]},'editable_source':str(OUT/(PREFIX+'_editable.gltf')),'runtime':'NOT RUN'};write(AUD/'integration-spec.json',meta);print('Assembled',total,flush=True)

np.savez_compressed(OUT/'hull-ray.npz',tri=np.concatenate([p['v'][p['i']]for p in allparts['hull']]))
assert meta['meshpoints']==old['meshpoints']
assert meta['rigs']==old['rigs']
