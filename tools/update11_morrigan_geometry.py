"""Local Morrigan STL derivative; originals and shared game assets are read-only."""
from pathlib import Path
import numpy as np,ctypes as c,json,hashlib,copy,shutil,struct,os,subprocess
from scipy.sparse import coo_matrix
from scipy.sparse.csgraph import connected_components
from scipy.spatial.transform import Rotation
from polish_ui import write,render
from common import Gltf
ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'assets/derived/update11-c';AUD=ROOT/'audit/update11-c';BUILD=ROOT/'build/update11-c';MAIN=Path('/run/media/haker/NVME 2/expanse-mod');DONOR=Path('/run/media/haker/NVME 2/expanse-workers/tachi-one-pdc');PREFIX='expanse11_morrigan'
BUILD.mkdir(parents=True,exist_ok=True)
z=np.load(OUT/'source-welded.npz');v=z['v'];idx=z['i'];edges=np.concatenate([idx[:,[0,1]],idx[:,[1,2]],idx[:,[2,0]]]);_,lab=connected_components(coo_matrix((np.ones(len(edges)),(edges[:,0],edges[:,1])),shape=(len(v),len(v))),directed=False)
# Both static guns, including disjoint end caps and pivot pins, are derivative-only removals.
removed=[20,21,27,29,30,31,32,33];idx=idx[~np.isin(lab[idx[:,0]],removed)]
lo=v.min(0);hi=v.max(0);center=(lo+hi)/2;scale=78.75/(hi[0]-lo[0]);R=np.array([[0,-1,0],[0,0,1],[-1,0,0]]) # source-X bow becomes game+Z; source+Z up
v=(v-center)@R.T*scale
lib=c.CDLL(str(MAIN/'.tools/libmeshoptimizer.so'));u=c.POINTER(c.c_uint);f=c.POINTER(c.c_float);fn=lib.meshopt_simplify;fn.argtypes=[u,u,c.c_size_t,f,c.c_size_t,c.c_size_t,c.c_size_t,c.c_float,c.c_uint,f];fn.restype=c.c_size_t
pos=np.ascontiguousarray(v,dtype='float32');ii=np.ascontiguousarray(idx.ravel(),dtype='uint32');dst=np.empty_like(ii);error=c.c_float();nn=fn(dst.ctypes.data_as(u),ii.ctypes.data_as(u),len(ii),pos.ctypes.data_as(f),len(pos),12,28500*3,.004,0,c.byref(error));ii=dst[:nn].reshape(-1,3);tri=pos[ii].astype(float);cross=np.cross(tri[:,1]-tri[:,0],tri[:,2]-tri[:,0]);area=np.linalg.norm(cross,axis=1);edge=np.max(np.linalg.norm(tri-np.roll(tri,1,axis=1),axis=2),axis=1);valid=(area>1e-7)&(area/np.maximum(edge**2,1e-20)>1e-6);tri=tri[valid]
# STL triangle winding, not unreliable STL facet normals, defines authored faces.
# Negative source transform determinant is compensated once.
if np.linalg.det(R)<0:tri=tri[:,[0,2,1]]
np.savez(OUT/'optimized-hull.npz',tri=tri)
tex=np.full((1,1,4),255,np.uint8);uv=np.zeros((len(tri),3,2));meshes=[(tri,uv,tex,[.38,.42,.46,1],'OPAQUE')]
for name,basis in [('top',[[0,0,1],[1,0,0],[0,1,0]]),('side',[[0,0,1],[0,1,0],[-1,0,0]]),('front',[[1,0,0],[0,1,0],[0,0,1]]),('rear',[[-1,0,0],[0,1,0],[0,0,-1]]),('oblique',[[.6,0,.8],[-.3,.927,.225],[-.7416,-.375,.5562]])]:render(meshes,(1400,600),np.array(basis)).save(AUD/('optimized-'+name+'.png'))
write(AUD/'optimization.json',{'source_triangles':306518,'removed_static_gun_components':removed,'triangles_after_gun_removal':len(idx),'optimized_hull_triangles':len(tri),'degenerates_removed':int((~valid).sum()),'meshoptimizer_relative_error':error.value,'target':28500,'error_limit':.004,'source_center':center.tolist(),'source_to_game_rotation':R.tolist(),'uniform_scale':scale,'provisional_length':78.75,'source_format':'STL: no UV/material/animation source','runtime':'NOT RUN'})
print(len(tri),error.value,flush=True)
# Measured ray/surface attachment on the reduced derivative.
def ray(origin,direction):
 origin=np.array(origin,float);direction=np.array(direction,float);direction/=np.linalg.norm(direction);e1=tri[:,1]-tri[:,0];e2=tri[:,2]-tri[:,0];p=np.cross(direction,e2);det=np.sum(e1*p,axis=1);inv=np.divide(1,det,out=np.zeros_like(det),where=abs(det)>1e-10);s=origin-tri[:,0];u0=np.sum(s*p,axis=1)*inv;q=np.cross(s,e1);v0=q@direction*inv;t=np.sum(e2*q,axis=1)*inv;ok=(abs(det)>1e-10)&(u0>=-1e-8)&(v0>=-1e-8)&(u0+v0<=1+1e-8)&(t>1e-5)
 if not ok.any():raise ValueError(('ray misses actual hull',origin.tolist(),direction.tolist()))
 k=np.where(ok)[0][np.argmin(t[ok])];return origin+direction*t[k]
shapes={'hull':[]};colors=[[.24,.28,.31,1],[.65,.16,.055,1],[.075,.085,.095,1],[.07,.35,.8,1]]
def addtri(t,material=0):shapes['hull'].append((np.asarray(t,float).reshape(-1,3,3),material))
# Procedural matte grey hull with orange support collars. Source had no colors.
cent=tri.mean(1);orange=np.zeros(len(tri),dtype=bool);dark=np.zeros(len(tri),dtype=bool);addtri(tri[~orange&~dark],0);addtri(tri[orange&~dark],1);addtri(tri[dark],2)
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
for i,sign in enumerate([-1,1]):
 up=np.array([sign*.866025403784,.5,0]);up/=np.linalg.norm(up);B=np.column_stack([np.cross(up,[0,0,1]),up,[0,0,1]]);probe=(np.array([16.175,-sign*50,26])-center)@R.T*scale;contact=ray(probe+up*10,-up);pivot=contact+up*.45;cyl(contact-up*.65,pivot,1.18)
 mount={'weapon':f'{PREFIX}_pdc_{i}','mesh_point':f'child.{PREFIX}_pdc_{i}','weapon_position':pivot.tolist(),'up':up.tolist(),'forward':[0,0,1],'yaw_arc':{'min_angle':-180.,'max_angle':180.},'pitch_arc':{'min_angle':-85.,'max_angle':5.}}
 rigs.append({'index':i,'kind':'pdc','mount':mount,'basis_columns':B.tolist(),'yaw_pivot_hull':pivot.tolist(),'pitch_pivot_hull':(pivot+B@off).tolist(),'muzzle_hull':(pivot+B@(off+muzzle)).tolist(),'turret_override':{'type':'biaxial','biaxial_base_mesh':PREFIX+'_pdc_base','biaxial_barrel_mesh':PREFIX+'_pdc_barrel','barrel_position':off.tolist(),'muzzle_positions':[muzzle.tolist()]},'skin_alias_map':[{'mesh_alias_name':PREFIX+'_pdc_'+part,'mesh_definition':{'mesh':PREFIX+'_pdc_'+part,'shader':'ship','is_shadow_blocker':True}} for part in ['base','barrel']],'measured_contact':contact.tolist(),'support_embed_depth':.65,'runtime':'NOT RUN'})
ports=[]
for x in [-3.,3.]:
 contact=ray([x,0,100],[0,0,-1]);z0=contact[2]-.2;z1=contact[2]+1.15;r0=.85;r1=.6;angles=np.arange(16)*2*np.pi/16;ring=np.column_stack([np.cos(angles),np.sin(angles)]);oo=ring*r0+[x,0];inn=ring*r1+[x,0]
 for i in range(16):
  j=(i+1)%16
  for q in [[[ *oo[i],z0],[ *oo[j],z0],[ *oo[j],z1]],[[ *oo[i],z0],[ *oo[j],z1],[ *oo[i],z1]],[[ *oo[i],z1],[ *oo[j],z1],[ *inn[j],z1]],[[ *oo[i],z1],[ *inn[j],z1],[ *inn[i],z1]],[[*inn[i],z0],[*inn[j],z1],[*inn[j],z0]],[[*inn[i],z0],[*inn[i],z1],[*inn[j],z1]]]:addtri(q,2)
  addtri([[x,0,z0+.01],[*inn[i],z0+.01],[*inn[j],z0+.01]],2)
 ports.append({'position':[x,0,z1+.05],'up':[0,1,0],'forward':[0,0,1],'measured_surface':contact.tolist(),'new_collar':True})
# Aft engine is the isolated source bell, component56. Locate its aftmost outlet.
engine_source=np.array([196.805328369,-0.,-3.5]);ep=(engine_source-center)@R.T*scale;ep[2]-=.1;exhaust={'position':ep.tolist(),'forward':[0,0,-1],'up':[0,1,0],'source':'Source engine-bell component56 aftmost plane; centered on measured bell Y/Z bounds'}
points=[{'name':'center','translation':[0,0,0]},{'name':'above','translation':[0,15,0]},{'name':'aura','translation':[0,-15,0]}]
for r in rigs:points.append({'name':r['mount']['mesh_point'],'translation':r['yaw_pivot_hull'],'rotation':Rotation.from_matrix(r['basis_columns']).as_quat().tolist()})
for i,p in enumerate(ports):points.append({'name':f'weapon.torpedo.{i}','translation':p['position']})
points.append({'name':'exhaust.0','translation':ep.tolist(),'rotation':[0,1,0,0]})
# Authored per-face projection gives valid UV derivatives. Average only similar normals at coincident vertices.
from collections import defaultdict
allparts={};sourceframes={}
for material in range(3):
 tt=np.concatenate([t for t,m in shapes['hull'] if m==material]);vv=tt.reshape(-1,3);face=np.cross(tt[:,1]-tt[:,0],tt[:,2]-tt[:,0]);face/=np.linalg.norm(face,axis=1)[:,None];norm=np.repeat(face,3,axis=0);groups=defaultdict(list)
 for j,p in enumerate(np.round(vv,5)):groups[tuple(p)].append(j)
 for ids in groups.values():
  ns=norm[ids].copy();matches=ns@ns.T>.70710678;nn=matches@ns;nn/=np.linalg.norm(nn,axis=1)[:,None];norm[ids]=nn
 uv=[];tan=[]
 for k,nn in enumerate(face):
  axis=np.eye(3)[np.argmin(abs(nn))];axis-=nn*np.dot(axis,nn);axis/=np.linalg.norm(axis);bit=np.cross(nn,axis);uv.extend(np.column_stack([tt[k]@axis,tt[k]@bit])*.05)
  for n in norm[k*3:k*3+3]:t=axis-n*np.dot(axis,n);t/=np.linalg.norm(t);tan.append([*t,1.])
 uv=np.array(uv);uv=.05+.9*(uv-uv.min(0))/np.maximum(np.ptp(uv,axis=0),1e-9)
 allparts.setdefault('hull',[]).append({'v':vv,'n':norm,'t':np.array(tan),'uv':np.array(uv),'i':np.arange(len(vv)).reshape(-1,3),'material':PREFIX+f'_mat_{material}'})
allparts.update({'pdc_'+k:p for k,p in donor_meshes.items()})
def savegltf(name,parts,meshpoints=[],compiler=True):
 g={'asset':{'version':'2.0','generator':'Morrigan STL derivative; source unchanged'},'scene':0,'scenes':[{'nodes':[0]}],'nodes':[{'mesh':0,'name':name,'children':[]}],'meshes':[{'primitives':[]}],'materials':[],'buffers':[],'bufferViews':[],'accessors':[]};buf=bytearray()
 def acc(a,typ,ct=5126):
  a=np.asarray(a,dtype='<f4' if ct==5126 else '<u4');buf.extend(b'\0'*((-len(buf))%4));start=len(buf);buf.extend(a.tobytes());g['bufferViews'].append({'buffer':0,'byteOffset':start,'byteLength':a.nbytes});x={'bufferView':len(g['bufferViews'])-1,'componentType':ct,'count':len(a),'type':typ}
  if typ=='VEC3':x.update(min=a.min(0).tolist(),max=a.max(0).tolist())
  g['accessors'].append(x);return len(g['accessors'])-1
 for p in parts:
  vv=p['v'].copy();nn=p['n'].copy();tt=p['t'].copy();idx=p['i'].copy();q=np.cross(vv[idx[:,1]]-vv[idx[:,0]],vv[idx[:,2]]-vv[idx[:,0]]);flip=np.sum(q*nn[idx].mean(1),axis=1)<0;idx[flip]=idx[flip][:,[0,2,1]]
  if compiler:vv[:,2]*=-1;nn[:,2]*=-1;tt[:,2]*=-1;tt[:,3]*=-1
  mat=p['material'];factor=colors[int(mat[-1])] if '_mat_'in mat else [.18,.2,.22,1];mi=len(g['materials']);g['materials'].append({'name':mat,'pbrMetallicRoughness':{'baseColorFactor':factor}});g['meshes'][0]['primitives'].append({'mode':4,'material':mi,'indices':acc(idx.ravel(),'SCALAR',5125),'attributes':{'POSITION':acc(vv,'VEC3'),'NORMAL':acc(nn,'VEC3'),'TANGENT':acc(tt,'VEC4'),'TEXCOORD_0':acc(p['uv'],'VEC2')}})
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
write(OUT/'retained-source-frames.json',sourceframes);meta={'status':'COMPILER PENDING','game_directory':str(BUILD/'game'),'hull_mesh':PREFIX+'_hull','rigs':rigs,'ship_spatial':spatial,'equipment':{'light_torpedo_ports':ports,'light_torpedo_port':ports[0],'torpedo_ports':ports,'exhaust':exhaust,'exhausts':[exhaust]},'exhaust_geometry':exhaust,'counts':counts,'assembled_triangle_total':total,'meshpoints':{'hull':points,'pdc_base':[],'pdc_barrel':[]},'editable_source':str(OUT/(PREFIX+'_editable.gltf')),'runtime':'NOT RUN'};write(AUD/'integration-spec.json',meta);print('Assembled',total,flush=True)
