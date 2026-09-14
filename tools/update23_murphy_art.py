"""Build a Murphy art-only package from all 8,302 supplied STL faces.
Originals/installed game are read-only. The established Wine prefix is used in place.
Run prepare, then compile (local Wine IPC needs sandbox allowance), then preview.
"""
from pathlib import Path
import argparse,copy,hashlib,json,os,struct,subprocess,zipfile
from collections import defaultdict
import numpy as np
from scipy.spatial import cKDTree
from scipy.spatial.transform import Rotation
from PIL import Image,ImageDraw
from common import Gltf,read,read_mesh,write
ROOT=Path(__file__).resolve().parents[1];MAIN=Path('/run/media/haker/NVME 2/expanse-mod');BASE=MAIN/'build/experiments/expanse_update19'
OUT=ROOT/'assets/derived/update23-murphy';BUILD=ROOT/'build/update23-murphy';GAME=BUILD/'game';AUD=ROOT/'audit/update23-murphy';NAME='expanse23_murphy_hull';ZIP=Path('/home/haker/Downloads/UNN Murphy Class Destroyer - 7350801.zip')
WINE=Path('/home/haker/.var/app/com.valvesoftware.Steam/.local/share/Steam/steamapps/common/Proton 10.0/files/bin/wine64');PREFIX=Path('/run/media/haker/NVME 2/expanse-workers/tachi-one-pdc/build/polish-b/proton-prefix');SDK=Path('/run/media/haker/NVME 2/SteamLibrary/steamapps/common/Sins of a Solar Empire II - Mod Tools')
ENV=dict(os.environ,WINEPREFIX=str(PREFIX),OMP_NUM_THREADS='4',MANGOHUD='0',WINEDEBUG='-all',DISPLAY='',WINEDLLOVERRIDES='mscoree,mshtml=')
COLORS={'armor':(128,141,148),'navy':(25,48,67),'machinery':(39,45,49),'nozzle':(20,133,204)}
for p in [OUT,BUILD,AUD,GAME/'meshes',GAME/'mesh_materials',GAME/'textures']:p.mkdir(parents=True,exist_ok=True)
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def frames(tt):
 v=tt.reshape(-1,3);q=np.cross(tt[:,1]-tt[:,0],tt[:,2]-tt[:,0]);face=q/np.linalg.norm(q,axis=1)[:,None];n=np.repeat(face,3,axis=0);groups=defaultdict(list)
 for j,p in enumerate(np.round(v,5)):groups[tuple(p)].append(j)
 for ids in groups.values():
  ns=n[ids].copy();nn=(ns@ns.T>.8660254)@ns;nn/=np.linalg.norm(nn,axis=1)[:,None];n[ids]=nn
 uv=np.zeros((len(v),2));t=np.zeros((len(v),4));dominant=np.repeat(np.argmax(abs(face),axis=1),3)
 for axis,axes in [(0,(2,1)),(1,(2,0)),(2,(0,1))]:
  mask=dominant==axis;aa,bb=axes;uv[mask]=v[mask][:,[aa,bb]]/240+.5;t[mask,aa]=1;t[mask,:3]-=n[mask]*np.sum(n[mask]*t[mask,:3],axis=1)[:,None];t[mask,:3]/=np.linalg.norm(t[mask,:3],axis=1)[:,None];t[mask,3]=np.where(np.cross(n[mask],t[mask,:3])[:,bb]<0,-1,1)
 return {'v':v,'n':n,'t':t,'uv':uv,'i':np.arange(len(v),dtype=np.uint32).reshape(-1,3)}
def cylinder(a,b,r,segments=24,inner=None):
 a=np.array(a,float);b=np.array(b,float);up=(b-a)/np.linalg.norm(b-a);right=np.eye(3)[np.argmin(abs(up))];right-=up*np.dot(right,up);right/=np.linalg.norm(right);fwd=np.cross(up,right);ring=np.array([right*np.cos(i*2*np.pi/segments)+fwd*np.sin(i*2*np.pi/segments) for i in range(segments)]);tri=[]
 def face(x,y,z,outward):
  if np.dot(np.cross(y-x,z-x),outward)<0:y,z=z,y
  tri.append([x,y,z])
 for i in range(segments):
  j=(i+1)%segments;aa=a+r*ring[i];ab=a+r*ring[j];ba=b+r*ring[i];bb=b+r*ring[j];side=ring[i]+ring[j];face(aa,ab,bb,side);face(aa,bb,ba,side)
  if inner is None:face(a,aa,ab,-up);face(b,ba,bb,up)
  else:
   ia=a+inner*ring[i];ib=a+inner*ring[j];ja=b+inner*ring[i];jb=b+inner*ring[j];face(ia,jb,ib,-side);face(ia,ja,jb,-side);face(aa,ia,ib,-up);face(aa,ib,ab,-up);face(ba,bb,jb,up);face(ba,jb,ja,up)
 return np.array(tri)
def rayhit(tt,origin,direction):
 # First actual hull intersection, vectorized Moller-Trumbore.
 o=np.array(origin);d=np.array(direction);e1=tt[:,1]-tt[:,0];e2=tt[:,2]-tt[:,0];h=np.cross(np.broadcast_to(d,e2.shape),e2);det=np.sum(e1*h,axis=1);inv=np.divide(1,det,out=np.zeros_like(det),where=abs(det)>1e-9);s=o-tt[:,0];u=inv*np.sum(s*h,axis=1);q=np.cross(s,e1);v=inv*np.sum(d*q,axis=1);t=inv*np.sum(e2*q,axis=1);ok=(abs(det)>1e-9)&(u>=-1e-8)&(v>=-1e-8)&(u+v<=1+1e-8)&(t>0);assert ok.any(),(origin,direction);return o+d*t[ok].min()
def save(parts,points):
 g={'asset':{'version':'2.0','generator':'Murphy full-resolution fan STL plus original support geometry; official SDK Z compensation'},'scene':0,'scenes':[{'nodes':[0]}],'nodes':[{'name':NAME,'mesh':0,'children':[]}],'meshes':[{'name':NAME,'primitives':[]}],'materials':[],'buffers':[],'bufferViews':[],'accessors':[]};buf=bytearray()
 def acc(x,typ,ct=5126):
  x=np.asarray(x,dtype='<u4'if ct==5125 else'<f4');buf.extend(b'\0'*((-len(buf))%4));off=len(buf);buf.extend(x.tobytes());g['bufferViews'].append({'buffer':0,'byteOffset':off,'byteLength':x.nbytes});a={'bufferView':len(g['bufferViews'])-1,'componentType':ct,'count':len(x),'type':typ}
  if typ=='VEC3':a.update(min=x.min(0).tolist(),max=x.max(0).tolist())
  g['accessors'].append(a);return len(g['accessors'])-1
 references={}
 for mat,tri in parts.items():
  p=frames(tri);references[mat]={k:v.tolist()for k,v in p.items()if k!='i'};v,n,t=[p[k].copy()for k in ['v','n','t']]
  for a in [v,n,t]:a[:,2]*=-1
  t[:,3]*=-1;g['materials'].append({'name':mat,'pbrMetallicRoughness':{'baseColorFactor':[1,1,1,1]}});g['meshes'][0]['primitives'].append({'mode':4,'material':len(g['materials'])-1,'indices':acc(p['i'].ravel(),'SCALAR',5125),'attributes':{'POSITION':acc(v,'VEC3'),'NORMAL':acc(n,'VEC3'),'TANGENT':acc(t,'VEC4'),'TEXCOORD_0':acc(p['uv'],'VEC2')}})
 for pt in points:
  q=copy.deepcopy(pt);q['translation'][2]*=-1
  if 'rotation'in q:q['rotation'][0]*=-1;q['rotation'][1]*=-1
  g['nodes'][0]['children'].append(len(g['nodes']));g['nodes'].append(q)
 g['buffers']=[{'uri':NAME+'.bin','byteLength':len(buf)}];write(OUT/(NAME+'.gltf'),g);(OUT/(NAME+'.bin')).write_bytes(buf);write(OUT/'source-frames.json',references)
def prepare():
 z=zipfile.ZipFile(ZIP);raw=z.read('files/UNN_Murphy_Class_Destroyer.stl');stl=np.frombuffer(raw[84:],dtype=[('n','<f4',3),('v','<f4',(3,3)),('a','<u2')]);source=stl['v'].astype(float);assert len(source)==8302
 lo=source.reshape(-1,3).min(0);hi=source.reshape(-1,3).max(0);scale=102*(104.9869586/46)/61;tt=(source-(lo+hi)/2)*scale;tt=tt[:,:,[0,2,1]];tt[:,:,2]*=-1;center=tt.mean(1);hlo=tt.reshape(-1,3).min(0);hhi=tt.reshape(-1,3).max(0)
 q=np.cross(tt[:,1]-tt[:,0],tt[:,2]-tt[:,0]);assert np.linalg.norm(q,axis=1).min()>1e-8
 # UNN gray armor with navy structural bands; the aft machinery is intentionally dark.
 assignment=np.full(len(tt),'armor',dtype='<U12');assignment[center[:,2]<-90]='machinery';parts={k:tt[assignment==k]for k in ['armor','machinery']};extras=[];mounts=[];points=[{'name':'center','translation':[0,0,0]},{'name':'above','translation':[0,float(hhi[1]+15),0]},{'name':'aura','translation':[0,float(hlo[1]-10),0]}]
 # Four mounts beyond the full hull bounding planes. Outward hemispheres cannot enter the hull.
 for j,(axis,sign,longitudinal)in enumerate([(0,1,22),(0,-1,22),(1,1,-18),(1,-1,-18)]):
  up=np.eye(3)[axis]*sign;p=np.array([0.,-10. if axis==0 else 0.,float(longitudinal)]);p[axis]=(hhi[axis]+2.8)if sign>0 else(hlo[axis]-2.8);surface=rayhit(tt,p,-up);foot=surface-up*.45;extras.append(cylinder(foot,p,2.5));B=np.column_stack([np.cross(up,[0,0,1]),up,[0,0,1]]);pt={'name':f'child.expanse23_murphy_pdc_{j}','translation':p.tolist(),'rotation':Rotation.from_matrix(B).as_quat().tolist()};points.append(pt);mounts.append({'kind':'pdc','mesh_point':pt['name'],'position':p.tolist(),'up':up.tolist(),'forward':[0,0,1],'support_surface':surface.tolist(),'support_length':float(np.linalg.norm(p-foot)),'outward_hull_plane_clearance':2.8,'yaw_arc':{'min_angle':-180.,'max_angle':180.},'pitch_arc':{'min_angle':-85.,'max_angle':0.}})
 ports=[]
 for j,x in enumerate([-8.,8.]):
  p=np.array([x,9.,hhi[2]+6]);surface=rayhit(tt,p,[0,0,-1]);mouth=surface+[0,0,3];extras.append(cylinder(surface-[0,0,.4],mouth,2.15,24,inner=1.5));points.append({'name':f'weapon.torpedo.{j}','translation':mouth.tolist()});ports.append(mouth.tolist())
 parts['machinery']=np.concatenate([parts['machinery'],*extras]);engine=np.array([(5.5-(lo[0]+hi[0])/2)*scale,(6.5-(lo[2]+hi[2])/2)*scale,hlo[2]-.2]);parts['nozzle']=cylinder(engine+[0,0,.05],engine-[0,0,.2],17,48,inner=15.8);points.append({'name':'exhaust.0','translation':engine.tolist(),'rotation':[0,1,0,0]})
 # Reserved attachment origins only; no additional rail weapon or geometry implied.
 points.extend([{'name':'weapon.rail.0','translation':[0,16,float(hhi[2]+.2)]},{'name':'weapon.rail.1','translation':(engine+[0,-20,0]).tolist(),'rotation':[0,1,0,0]}]);save(parts,points)
 tex=OUT/'texture-sources';tex.mkdir(exist_ok=True)
 for name,color in COLORS.items():
  a=np.empty((512,512,4),np.uint8);rng=np.random.default_rng(23);variation=rng.integers(-4,5,(512,512,1));a[:,:,:3]=np.clip(np.array(color)+variation,0,255);a[:,:,3]=255
  if name=='armor':
   world_z=(np.arange(512)/511-.5)*240;stripe=(abs(world_z-72)<5)|(abs(world_z+64)<5);a[:,stripe,:3]=np.clip(np.array(COLORS['navy'])+variation[:,stripe],0,255)
  im=Image.fromarray(a);draw=ImageDraw.Draw(im)
  if name!='nozzle':
   for y in range(0,512,64):
    draw.line((0,y,511,y),fill=tuple(max(0,c-16)for c in color),width=2)
    for x in range((y//64%2)*32,512,96):draw.line((x,y,x,min(y+64,511)),fill=tuple(max(0,c-12)for c in color),width=1)
  im.save(tex/(f'expanse23_murphy_{name}_clr.png'))
 Image.new('RGBA',(16,16),(255,175,115,255)).save(tex/'expanse23_murphy_orm.png');Image.new('RGBA',(16,16),(0,0,0,0)).save(tex/'expanse23_murphy_msk.png');Image.new('RGBA',(16,16),(0,0,150,0)).save(tex/'expanse23_murphy_glow_msk.png')
 bounds=np.concatenate(list(parts.values())).reshape(-1,3);counts={k:len(v)for k,v in parts.items()};write(AUD/'integration-spec.json',{'status':'PREPARED; COMPILE PENDING','output_game':str(GAME),'base_mesh':NAME,'source':{'zip':str(ZIP),'zip_sha256':sha(ZIP),'member':'files/UNN_Murphy_Class_Destroyer.stl','stl_sha256':hashlib.sha256(raw).hexdigest(),'author':'Qwerty1998','url':'https://www.thingiverse.com/thing:7350801','license':z.read('LICENSE.txt').decode()if'LICENSE.txt'in z.namelist()else'CC BY-SA (version unspecified in supplied package)','author_description':'a made up UNN ship from the Expanse','source_triangles':8302,'retained_triangles':8302,'decimation':False,'source_bounds':[lo.tolist(),hi.tolist()]},'scale':{'length_metres_provisional':102,'game_units_per_metre':104.9869586/46,'source_to_game':scale,'transform':'center bounding box then [X,Z,-Y]; positive Z bow; positive Y dorsal','lore_caveat':'102 m is the RPG class reference applied to a fan-made geometry; one modeled drive differs from the RPG two-drive description.'},'counts':{'hull':sum(counts.values()),'material_triangles':counts,'source':8302,'added_geometry':sum(counts.values())-8302,'pdc_base':138,'pdc_barrel':539,'assembled':sum(counts.values())+4*(138+539)},'spatial':{'box':{'center':((bounds.max(0)+bounds.min(0))/2).tolist(),'extents':((bounds.max(0)-bounds.min(0))/2).tolist()},'radius':float(np.linalg.norm(bounds,axis=1).max()+5)},'meshpoints':points,'rigs':mounts,'torpedo_ports':ports,'exhaust_point':engine.tolist(),'reserved_rail_points':['weapon.rail.0','weapon.rail.1'],'adaptations':['Four visible PDC mounts and their exact locations are mod adaptations; canon does not specify this count.','Two forward torpedo tubes follow the RPG role; collars are original added geometry.','Reserved rail points are optional integration origins, not additional modeled guns.','Blue nozzle annulus and UNN gray/navy panel materials are original mod art.'],'checks':{'all_source_faces_retained':True,'source_degenerate_faces':0,'support_first_hit_rays':True},'runtime':'NOT RUN'})
 print('Prepared',counts,flush=True)
def compile():
 def run(fmt,suffix=''):
  dest=BUILD/('compiler-'+fmt);dest.mkdir(exist_ok=True)
  with(BUILD/(NAME+suffix+'-'+fmt+'.log')).open('w')as log:subprocess.run([str(WINE),str(SDK/'MeshBuilder/bin/MeshBuilder.exe'),'--input_path=Z:'+str(OUT/(NAME+'.gltf')),'--output_folder_path=Z:'+str(dest),'--mesh_output_format='+fmt,'--fill_triangle_facing_grid'],env=ENV,stdout=log,stderr=subprocess.STDOUT,check=True,timeout=300)
 run('json');m=read(BUILD/'compiler-json'/(NAME+'.mesh_json'));asset=Gltf(OUT/(NAME+'.gltf'));buf=bytearray(asset.buffers[0]);v=np.array([x['p']for x in m['non_skinned_vertices']]);n=np.array([x['n']for x in m['non_skinned_vertices']]);allidx=np.array(m['vertex_indices']);flips=0
 for prim in m['primitives']:
  mat=m['materials'][prim['material_index']];p=next(p for p in asset.g['meshes'][0]['primitives']if mat.endswith('_'+asset.g['materials'][p['material']]['name']));ii=allidx[prim['vertex_index_start']:prim['vertex_index_start']+prim['vertex_index_count']].reshape(-1,3);q=np.cross(v[ii[:,1]]-v[ii[:,0]],v[ii[:,2]]-v[ii[:,0]]);flip=np.sum(q*n[ii].mean(1),axis=1)<-1e-5;acc=asset.g['accessors'][p['indices']];view=asset.g['bufferViews'][acc['bufferView']];arr=np.ndarray((acc['count']//3,3),dtype='<u4',buffer=buf,offset=view['byteOffset']);expected=asset.accessor(p['attributes']['POSITION']);expected[:,2]*=-1;assert np.allclose(np.sort(expected[arr],axis=1),np.sort(v[ii],axis=1),atol=4e-5);arr[flip]=arr[flip][:,[0,2,1]];flips+=int(flip.sum())
 if flips:(OUT/(NAME+'.bin')).write_bytes(buf);run('json','-winding')
 run('binary');m=read(BUILD/'compiler-json'/(NAME+'.mesh_json'));bp=BUILD/'compiler-binary'/(NAME+'.mesh');original=bp.read_bytes();b=bytearray(original);count=struct.unpack_from('<Q',b,53)[0];off=61;rows=[];offsets=[]
 for _ in range(count):
  vals=struct.unpack_from('<12f?',b,off);rows.append(vals[:-1]);offsets.append(off+24);off+=49+(8 if vals[-1]else 0)
 rows=np.array(rows);ref=read(OUT/'source-frames.json');lookup=np.concatenate([np.concatenate([r['v'],r['n'],r['uv']],axis=1)for r in ref.values()]);distance,match=cKDTree(lookup).query(np.concatenate([rows[:,:6],rows[:,10:12]],axis=1));assert distance.max()<2e-4;t=np.concatenate([r['t']for r in ref.values()])[match];n=rows[:,3:6];t[:,:3]-=n*np.sum(n*t[:,:3],axis=1)[:,None];t[:,:3]/=np.linalg.norm(t[:,:3],axis=1)[:,None];allowed=np.zeros(len(b),bool)
 for i,pos in enumerate(offsets):struct.pack_into('<4f',b,pos,*t[i]);allowed[pos:pos+16]=True
 assert np.all((np.frombuffer(original,np.uint8)==np.frombuffer(b,np.uint8))|allowed);info=read_mesh(bp);prefix=info['parsed_prefix_bytes'];assert original[prefix:]==b[prefix:];idx=np.array(m['vertex_indices']).reshape(-1,3);q=np.cross(rows[idx[:,1],:3]-rows[idx[:,0],:3],rows[idx[:,2],:3]-rows[idx[:,0],:3]);opposed=int((np.sum(q*n[idx].mean(1),axis=1)<-1e-5).sum());assert opposed==0;(GAME/'meshes'/(NAME+'.mesh')).write_bytes(b)
 meta=read(AUD/'integration-spec.json');assert len(idx)==meta['counts']['hull']
 for got,want in zip(info['meshpoints'],meta['meshpoints']):
  assert got['name']==want['name']and np.allclose(got['position'],want['translation'],atol=2e-5);assert np.allclose(np.array(got['rotation']).reshape(3,3),Rotation.from_quat(want.get('rotation',[0,0,0,1])).as_matrix().T,atol=2e-5)
 source_hashes={};materials=set()
 # One-engine idle plume cloned from the accepted blue Truman exhaust. The phase
 # effect is deliberately not reused: it contains six absolute engine assemblies.
 plume_source=BASE/'effects/expanse15_truman_idle_plume.particle_effect';plume=read(plume_source)
 for node in plume['nodes']:
  for key in ['x','y','z']:
   if key in node:node[key]=[v*.5 for v in node[key]]
 for emitter in plume['emitters']:
  if 'forward_velocity'in emitter:emitter['forward_velocity']=[v*.5 for v in emitter['forward_velocity']]
  billboard=emitter['particle'].get('billboard',{})
  for key in ['width','height']:
   if key in billboard:billboard[key]=[v*.5 for v in billboard[key]]
 (GAME/'effects').mkdir(exist_ok=True);write(GAME/'effects/expanse23_murphy_idle_plume.particle_effect',plume);source_hashes[str(plume_source)]=sha(plume_source)
 meta['skin_contract']={'unit_mesh':{'mesh':NAME,'shader':'ship','is_shadow_blocker':True},'child_mesh_alias_bindings':{'map':[{'mesh_alias_name':f'expanse23_murphy_pdc_{kind}','mesh_definition':{'mesh':f'expanse23_murphy_pdc_{kind}','shader':'ship','is_shadow_blocker':True}}for kind in ['base','barrel']]},'exhaust_effects':{'particle_effects':[{'particle_effect':'expanse23_murphy_idle_plume'}]},'exhaust_notes':'One exhaust.0 with accepted Truman rotation; private blue idle effect at 0.5 spatial scale. No six-engine absolute phase effect reused; use ordinary hyperspace effects until a custom phase plume is authored.'}

 for kind in ['base','barrel']:
  source=BASE/'meshes'/('expanse11_morrigan_pdc_'+kind+'.mesh');dest=GAME/'meshes'/('expanse23_murphy_pdc_'+kind+'.mesh');assert source.is_file()and not source.is_symlink();dest.write_bytes(source.read_bytes());source_hashes[str(source)]=sha(source);materials.update(read_mesh(source)['materials'])
 for mat in materials:
  source=BASE/'mesh_materials'/(mat+'.mesh_material');(GAME/'mesh_materials'/source.name).write_bytes(source.read_bytes());source_hashes[str(source)]=sha(source)
 for p in (OUT/'texture-sources').glob('*.png'):
  with(BUILD/('texture-'+p.stem+'.log')).open('w')as log:subprocess.run([str(WINE),str(MAIN/'.tools/texconv.exe'),'-f','BC7_UNORM','-y','-m','0','-nogpu','--single-proc','-o','Z:'+str(GAME/'textures'),'-bc','q','Z:'+str(p)],env=ENV,stdout=log,stderr=subprocess.STDOUT,check=True,timeout=300)
 for mat in m['materials']:
  name=next(k for k in COLORS if mat.endswith('_'+k));write(GAME/'mesh_materials'/(mat+'.mesh_material'),{'version':1,'base_color_texture':'expanse23_murphy_'+name+'_clr','occlusion_roughness_metallic_texture':'expanse23_murphy_orm','normal_texture':'expanse10_donnager_flat_nrm','mask_texture':'expanse23_murphy_glow_msk'if name=='nozzle'else'expanse23_murphy_msk','emissive_factor':1.0})
 for mat in(GAME/'mesh_materials').glob('*.mesh_material'):
  for key,value in read(mat).items():
   if key.endswith('_texture')and not(GAME/'textures'/(value+'.dds')).exists():
    source=BASE/'textures'/(value+'.dds');assert source.is_file()and not source.is_symlink();(GAME/'textures'/source.name).write_bytes(source.read_bytes());source_hashes[str(source)]=sha(source)
 # Remove only stale private build products from earlier iterations of this tool.
 used_materials=set(m['materials'])|materials
 for p in(GAME/'mesh_materials').glob('*.mesh_material'):
  if p.stem not in used_materials:p.unlink()
 used_textures={value for p in(GAME/'mesh_materials').glob('*.mesh_material')for key,value in read(p).items()if key.endswith('_texture')}
 for p in(GAME/'textures').glob('*.dds'):
  if p.stem not in used_textures:p.unlink()
 turret=read(BASE/'entities/expanse11_morrigan_pdc_0.weapon')['turret'];turret.update(biaxial_base_mesh='expanse23_murphy_pdc_base',biaxial_barrel_mesh='expanse23_murphy_pdc_barrel')
 for rig in meta['rigs']:rig['turret_override']=turret
 meta['status']='OFFLINE COMPILED ART PASS; RUNTIME UNTESTED';meta['checks'].update(meshpoint_transforms_exact=True,source_frame_error=float(distance.max()),opposed_winding_triangles=opposed,initial_winding_flips=flips,only_tangent_bytes_repaired=True,official_triangle_grid_and_trailer_preserved=True,donor_game_bytes_unchanged=True);meta['source_game_hashes']=source_hashes;meta['files']={str(p.relative_to(GAME)):sha(p)for p in sorted(GAME.rglob('*'))if p.is_file()};meta['wine_prefix_used_in_place']=str(PREFIX);meta['wine_prefix_copied']=False;write(AUD/'integration-spec.json',meta);print(meta['status'],flush=True)
def preview():
 from polish_ui import render
 meta=read(AUD/'integration-spec.json');parts=[]
 def add(name,position,B=np.eye(3)):
  path=GAME/'meshes'/(name+'.mesh');b=path.read_bytes();count=struct.unpack_from('<Q',b,53)[0];off=61;rows=[]
  for _ in range(count):
   vals=struct.unpack_from('<12f?',b,off);rows.append(vals[:-1]);off+=49+(8 if vals[-1]else 0)
  rows=np.array(rows);ic=struct.unpack_from('<Q',b,off)[0];off+=8;indices=np.frombuffer(b,dtype='<u4',count=ic,offset=off);v=rows[:,:3]@B.T+position;uv=rows[:,10:12];info=read_mesh(path)
  for p in info['primitives']:
   idx=indices[p['vertex_index_start']:p['vertex_index_start']+p['vertex_index_count']].reshape(-1,3);mat=read(GAME/'mesh_materials'/(info['materials'][p['material_index']]+'.mesh_material'));tex=np.asarray(Image.open(GAME/'textures'/(mat['base_color_texture']+'.dds')).convert('RGBA'));parts.append((v[idx],uv[idx],tex,[1,1,1,1],'OPAQUE'))
 add(NAME,[0,0,0])
 for rig in meta['rigs']:
  B=np.column_stack([np.cross(rig['up'],rig['forward']),rig['up'],rig['forward']]);p=np.array(rig['position']);t=rig['turret_override'];add(t['biaxial_base_mesh'],p,B);add(t['biaxial_barrel_mesh'],p+B@np.array(t['barrel_position']),B)
 B=np.array([[.8,0,.6],[-.3,.866,.4],[.52,.5,-.693]]);render(parts,(1400,850),B).save(AUD/'compiled-game-preview.png');render(parts,(1400,850),B@np.diag([-1,1,-1])).save(AUD/'compiled-game-bow-preview.png');print('Preview uses packaged mesh and DDS; not game runtime.')
if __name__=='__main__':
 parser=argparse.ArgumentParser();parser.add_argument('stage',choices=['prepare','compile','preview']);args=parser.parse_args();globals()[args.stage]()
