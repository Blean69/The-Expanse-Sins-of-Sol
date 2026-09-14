"""Private 0.27 OPA mesh preparation helpers; no source or installed mutations."""
from pathlib import Path
import copy,ctypes as C,hashlib,json,math,struct,sys,subprocess
import numpy as np
from PIL import Image,ImageDraw,ImageFont
from scipy.spatial import cKDTree
from scipy.spatial.transform import Rotation
ROOT=Path(__file__).resolve().parents[1];MAIN=Path('/run/media/haker/NVME 2/expanse-mod');BASE=MAIN/'build/experiments/expanse_update26'
sys.path.insert(0,str(MAIN/'tools'))
from common import read,write,read_mesh,Gltf
import update12_scirocco_common as c
import update24_behemoth_compile as compiler
from flight03_effects import scale_effect,check_structure
from build_update12 import phase_effect
from polish_ui import render
BUILD=ROOT/'build/update27-opa';SOURCE=BUILD/'source';GAME=BUILD/'game';AUD=ROOT/'audit/update27-opa'
UNITS=104.987/46

def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def dirs():
 for p in [SOURCE,AUD,GAME/'meshes',GAME/'mesh_materials',GAME/'textures',GAME/'effects',BUILD/'gltf']:p.mkdir(parents=True,exist_ok=True)
def stl(name):
 b=(SOURCE/name).read_bytes();n=struct.unpack_from('<I',b,80)[0];assert len(b)==84+50*n;r=np.frombuffer(b,offset=84,count=n,dtype=[('n','<f4',(3,)),('v','<f4',(3,3)),('a','<u2')]);t=r['v'].astype(float);assert np.isfinite(t).all();return t

def simplify(t,target,tol):
 v,idx=np.unique(np.round(t.reshape(-1,3),5),axis=0,return_inverse=True);v=np.ascontiguousarray(v,dtype='float32');idx=np.ascontiguousarray(idx,dtype='uint32');dst=np.empty_like(idx)
 lib=C.CDLL(str(MAIN/'.tools/libmeshoptimizer.so'));u=C.POINTER(C.c_uint);f=C.POINTER(C.c_float);fn=lib.meshopt_simplify;fn.argtypes=[u,u,C.c_size_t,f,C.c_size_t,C.c_size_t,C.c_size_t,C.c_float,C.c_uint,f];fn.restype=C.c_size_t;error=C.c_float();count=fn(dst.ctypes.data_as(u),idx.ctypes.data_as(u),len(idx),v.ctypes.data_as(f),len(v),12,target*3,tol,0,C.byref(error));out=v[dst[:count].reshape(-1,3)].astype(float);q=np.cross(out[:,1]-out[:,0],out[:,2]-out[:,0]);valid=np.linalg.norm(q,axis=1)>1e-9;out=out[valid]
 return out,{'input_triangles':len(t),'output_triangles':len(out),'target':target,'relative_error':error.value,'error_limit':tol,'degenerate_faces_removed':int((~valid).sum()),'optimizer_sha256':sha(MAIN/'.tools/libmeshoptimizer.so')}

def frame(t,mat):
 p=c.frames(t,mat);v=p['v'];n=p['n'];low=v.min(0);extent=np.maximum(np.ptp(v,axis=0),1e-6);axes=np.argmax(abs(n),axis=1);uv=np.zeros((len(v),2));tangent=np.zeros((len(v),4));tangent[:,3]=1
 for ax in range(3):
  sel=axes==ax;a,b=[j for j in range(3)if j!=ax];uv[sel]=.01+.98*(v[sel][:,[a,b]]-low[[a,b]])/extent[[a,b]];tangent[sel,a]=1
 tangent[:,:3]-=n*(tangent[:,:3]*n).sum(1)[:,None];norm=np.linalg.norm(tangent[:,:3],axis=1);tangent[:,:3]/=np.maximum(norm[:,None],1e-9);bad=norm<1e-8;tangent[bad]=p['t'][bad]
 p['uv']=uv;p['t']=tangent;return p

def atlas(name,color,white=False):
 """Code-authored industrial panel maps with opaque color and emissive windows."""
 out=SOURCE/'textures';out.mkdir(exist_ok=True);w=h=1024;rng=np.random.default_rng(sum(name.encode()));im=Image.new('RGBA',(w,h),(*color,255));d=ImageDraw.Draw(im);mask=Image.new('RGBA',(w,h),(0,0,0,0));md=ImageDraw.Draw(mask)
 for y in range(0,h,16):
  for x in range(0,w,32):
   delta=int(rng.integers(-4,5)if white else rng.integers(-2,3));cc=tuple(int(np.clip(v+delta,0,255))for v in color);d.rectangle((x+1,y+1,x+30,y+14),fill=(*cc,255));line=tuple(max(0,v-(8 if white else 4))for v in cc);d.line((x,y,x+31,y),fill=(*line,255));d.line((x,y,x,y+15),fill=(*line,255))
   if rng.random()<.025:d.rectangle((x+4,y+6,x+9,y+7),fill=(125,166,183,255));md.rectangle((x+4,y+6,x+9,y+7),fill=(0,0,120,0))
 for y in [.2,.52,.78]:
  yy=int(h*y);d.rectangle((0,yy,w,yy+7),fill=(100,110,111,255)if white else(13,17,20,255))
 # No atlas text: repeated planar mapping would mirror or stretch lettering.
 for suffix,img in [('clr',im),('msk',mask),('orm',Image.new('RGBA',(w,h),(255,185 if white else 160,75 if white else 130,255))),('nrm',Image.new('RGBA',(w,h),(128,128,255,255)))]:img.save(out/(name+'_'+suffix+'.png'))
 return out

def cylinder(tlist,p0,p1,r,segments=32,cap=True,r2=None):
 p0=np.array(p0,float);p1=np.array(p1,float);axis=p1-p0;axis/=np.linalg.norm(axis);a=np.eye(3)[np.argmin(abs(axis))];a-=axis*np.dot(a,axis);a/=np.linalg.norm(a);b=np.cross(axis,a);ring=np.cos(np.arange(segments)*2*np.pi/segments)[:,None]*a+np.sin(np.arange(segments)*2*np.pi/segments)[:,None]*b;one=p0+ring*r;two=p1+ring*(r if r2 is None else r2)
 for j in range(segments):
  k=(j+1)%segments;tlist.extend([[one[j],one[k],two[k]],[one[j],two[k],two[j]]])
  if cap:tlist.extend([[p0,one[k],one[j]],[p1,two[j],two[k]]])

def ray(t,origin,direction):
 e1=t[:,1]-t[:,0];e2=t[:,2]-t[:,0];h=np.cross(np.broadcast_to(direction,e2.shape),e2);det=(e1*h).sum(1);inv=np.divide(1,det,out=np.zeros_like(det),where=abs(det)>1e-9);ss=np.asarray(origin)-t[:,0];u=(ss*h).sum(1)*inv;q=np.cross(ss,e1);v=(direction*q).sum(1)*inv;dist=(e2*q).sum(1)*inv;valid=(abs(det)>1e-9)&(u>=-1e-7)&(v>=-1e-7)&(u+v<=1.0000001)&(dist>1e-5)
 return None if not valid.any()else np.asarray(origin)+direction*dist[valid].min()

def rigs(t,specs,points,prefix,turret,standoff=2):
 out=[]
 for origin,up in specs:
  up=np.array(up,float);up/=np.linalg.norm(up);origin=np.array(origin,float);hit=ray(t,origin, -up);assert hit is not None
  pos=hit+up*standoff;forward=np.array([0,0,1.]);basis=np.column_stack([np.cross(up,forward),up,forward]);j=len(out);name=f'child.{prefix}_pdc_{j}'
  points.append({'name':name,'translation':pos.tolist(),'rotation':Rotation.from_matrix(basis).as_quat().tolist()});out.append({'mesh_point':name,'position':pos.tolist(),'up':up.tolist(),'forward':forward.tolist(),'basis':basis.tolist(),'yaw_arc':{'min_angle':-180.,'max_angle':180.},'pitch_arc':{'min_angle':-85.,'max_angle':-25.},'turret_override':copy.deepcopy(turret)})
 return out

def safety(t,mounts):
 count=0
 for r in mounts:
  basis=np.array(r['basis']);origin=np.array(r['position']);turret=r['turret_override']
  for yaw in np.linspace(r['yaw_arc']['min_angle'],r['yaw_arc']['max_angle'],17):
   for pitch in np.linspace(r['pitch_arc']['min_angle'],r['pitch_arc']['max_angle'],9):
    yy,pp=np.radians([yaw,pitch]);ry=Rotation.from_rotvec([0,yy,0]).as_matrix();rx=Rotation.from_rotvec([pp,0,0]).as_matrix();direction=basis@ry@rx@np.array([0.,0,1]);muzzle=origin+basis@ry@(np.array(turret['barrel_position'])+rx@np.array(turret['muzzle_positions'][0]));assert ray(t,muzzle,direction)is None,('blocked',r['mesh_point'],yaw,pitch);count+=1
 return count

def compile_parts(name,parts,points):
 out=BUILD/'gltf';c.OUT=out;c.savegltf(name,parts,points);compiler.NAME=name;compiler.OUT=out;compiler.BUILD=BUILD
 compiler.compile('json');m=read(BUILD/'compiler-json'/(name+'.mesh_json'));g=Gltf(out/(name+'.gltf'));buf=bytearray(g.buffers[0]);v=np.array([x['p']for x in m['non_skinned_vertices']]);n=np.array([x['n']for x in m['non_skinned_vertices']]);ids=np.array(m['vertex_indices']);flips=0
 for pr in m['primitives']:
  mat=m['materials'][pr['material_index']];p=next(x for x in g.g['meshes'][0]['primitives']if mat.endswith('_'+g.g['materials'][x['material']]['name']));ii=ids[pr['vertex_index_start']:pr['vertex_index_start']+pr['vertex_index_count']].reshape(-1,3);q=np.cross(v[ii[:,1]]-v[ii[:,0]],v[ii[:,2]]-v[ii[:,0]]);flip=(q*n[ii].mean(1)).sum(1)<0;ac=g.g['accessors'][p['indices']];bv=g.g['bufferViews'][ac['bufferView']];a=np.ndarray((ac['count']//3,3),dtype='<u4',buffer=buf,offset=bv.get('byteOffset',0)+ac.get('byteOffset',0));a[flip]=a[flip][:,[0,2,1]];flips+=int(flip.sum())
 if flips:(out/(name+'.bin')).write_bytes(buf);compiler.compile('json','-winding')
 compiler.compile('binary');bp=BUILD/'compiler-binary'/(name+'.mesh');original=bp.read_bytes();b=bytearray(original);count=struct.unpack_from('<Q',b,53)[0];off=61;rows=[];offsets=[]
 for _ in range(count):
  vals=struct.unpack_from('<12f?',b,off);rows.append(vals[:-1]);offsets.append(off+24);off+=49+(8 if vals[-1]else 0)
 a=np.array(rows);lookup=np.concatenate([np.column_stack([p['v'],p['n'],p['uv']])for p in parts]);ts=np.concatenate([p['t']for p in parts]);dist,match=cKDTree(lookup).query(np.column_stack([a[:,:6],a[:,10:12]]));assert dist.max()<.003,dist.max();t=ts[match].copy();n=a[:,3:6];t[:,:3]-=n*(t[:,:3]*n).sum(1)[:,None];norm=np.linalg.norm(t[:,:3],axis=1);assert norm.min()>1e-8;t[:,:3]/=norm[:,None];allowed=np.zeros(len(b),bool)
 for j,p in enumerate(offsets):struct.pack_into('<4f',b,p,*t[j]);allowed[p:p+16]=True
 assert np.all((np.frombuffer(original,np.uint8)==np.frombuffer(b,np.uint8))|allowed);info=read_mesh(bp);assert b[info['parsed_prefix_bytes']:]==original[info['parsed_prefix_bytes']:];m=read(BUILD/'compiler-json'/(name+'.mesh_json'));ii=np.array(m['vertex_indices']).reshape(-1,3);q=np.cross(a[ii[:,1],:3]-a[ii[:,0],:3],a[ii[:,2],:3]-a[ii[:,0],:3]);assert ((q*n[ii].mean(1)).sum(1)<-1e-4).sum()==0
 assert info['triangles']==sum(len(p['i'])for p in parts)
 for got,want in zip(info['meshpoints'],points,strict=True):
  assert got['name']==want['name']and np.allclose(got['position'],want['translation'],atol=.003);assert np.allclose(np.array(got['rotation']).reshape(3,3),Rotation.from_quat(want.get('rotation',[0,0,0,1])).as_matrix().T,atol=2e-5)
 (GAME/'meshes'/(name+'.mesh')).write_bytes(b)
 return {'name':name,'triangles':info['triangles'],'materials':info['materials'],'winding_flips':flips,'max_attribute_error':float(dist.max()),'checks':{'official_facing_grid':True,'tangent_only_patch':True,'winding_pass':True,'meshpoints_pass':True}}

def textures(names):
 for name in names:
  for ch in ['clr','nrm','orm','msk']:
   p=SOURCE/'textures'/(name+'_'+ch+'.png');out=GAME/'textures'/(p.stem+'.dds')
   cmd=[str(compiler.WINE),str(MAIN/'.tools/texconv.exe'),'-f','BC5_SNORM'if ch=='nrm'else'BC7_UNORM','-y','-m','0','-nogpu','--single-proc','-o','Z:'+str(GAME/'textures')]+(['--x2-bias']if ch=='nrm'else['-bc','q'])+['Z:'+str(p)]
   with (BUILD/'texture-conversion.log').open('a')as log:subprocess.run(cmd,env=compiler.ENV,stdout=log,stderr=subprocess.STDOUT,check=True,timeout=180)
   assert out.exists()

def materials(compiled,names):
 for name in names:
  mat=next(x for x in compiled['materials']if x.endswith('_'+name));write(GAME/'mesh_materials'/(mat+'.mesh_material'),{'version':1,'base_color_texture':name+'_clr','normal_texture':name+'_nrm','occlusion_roughness_metallic_texture':name+'_orm','mask_texture':name+'_msk','emissive_factor':.5})

def donor(old,new):
 p=BASE/'meshes'/(old+'.mesh');(GAME/'meshes'/(new+'.mesh')).write_bytes(p.read_bytes());return {'source':str(p),'sha256':sha(p),'new':new,'note':'Exact accepted compiled mesh; accepted materials/textures resolved from frozen baseline.'}

def plume(prefix,exhausts,width,length):
 source=compiler.INSTALLED/'effects/exhaust_tech_medium_01.particle_effect';fx=read(source);idle=scale_effect(fx,width,length,blue=True);phase=phase_effect(exhausts,width,length*2.5);write(GAME/'effects'/(prefix+'_idle_plume.particle_effect'),idle);write(GAME/'effects'/(prefix+'_phase_plume.particle_effect'),phase)
 return {'idle':prefix+'_idle_plume','phase':prefix+'_phase_plume','source':str(source),'source_sha256':sha(source),'nozzle_count':len(exhausts),'width_scalar':width,'length_scalar':length}

def preview(parts,riglist,name,donor_materials=None):
 textures={};meshes=[]
 for p in parts:
  mat=p['material']
  if mat not in textures:
   if mat in (donor_materials or {}):
    native=read(BASE/'mesh_materials'/(donor_materials[mat]+'.mesh_material'));source=BASE/'textures'/(native['base_color_texture']+'.dds')
   else:source=SOURCE/'textures'/(mat+'_clr.png')
   textures[mat]=np.array(Image.open(source).resize((512,512)).convert('RGBA'))
  meshes.append((p['v'][p['i']],p['uv'][p['i']],textures[mat],[1,1,1,1],'OPAQUE'))
 # The offline portrait checks assembled muzzle axes/placement; actual tracking
 # remains a runtime check. Donor base colors retain their accepted identities.
 from update26_command_art import unpack
 for r in riglist:
  turret=r['turret_override'];basis=np.array(r['basis']);position=np.array(r['position'])
  for key,off in [('biaxial_base_mesh',np.zeros(3)),('biaxial_barrel_mesh',np.array(turret['barrel_position']))]:
   path=GAME/'meshes'/(turret[key]+'.mesh');ps,_,_=unpack(path)
   for p in ps:
    m=read(BASE/'mesh_materials'/(p['old_material']+'.mesh_material'));tex=m['base_color_texture']
    if tex not in textures:textures[tex]=np.array(Image.open(BASE/'textures'/(tex+'.dds')).resize((512,512)).convert('RGBA'))
    v=(p['v']+off)@basis.T+position;meshes.append((v[p['i']],p['uv'][p['i']],textures[tex],[1,1,1,1],'OPAQUE'))
 for suffix,basis,size in [('oblique',np.array([[.8,0,-.6],[.24,.9165,.32],[.55,-.4,.733]]),(1400,950)),('side',np.array([[0,0,1],[0,1,0],[-1,0,0]]),(1500,800)),('aft',np.array([[1,0,0],[0,1,0],[0,0,-1]]),(1000,1000))]:render(meshes,size,basis).save(BUILD/(name+'-'+suffix+'.png'))
