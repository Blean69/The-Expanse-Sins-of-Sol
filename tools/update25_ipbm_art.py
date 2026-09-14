"""Compile the supplied UN IPBM v2 as a local-bombardment cosmetic mesh.
No unit, damage, health, global launch, or interception mechanics are authored.
"""
from pathlib import Path
import argparse,copy,ctypes as C,hashlib,json,struct,subprocess,zipfile
import numpy as np
from scipy.spatial import cKDTree
from scipy.spatial.transform import Rotation
from PIL import Image,ImageDraw,ImageFont
from common import Gltf,read,read_mesh,write
import update23_murphy_art as helper
ROOT=Path(__file__).resolve().parents[1];MAIN=Path('/run/media/haker/NVME 2/expanse-mod');BASE=MAIN/'build/experiments/expanse_update19';NATIVE=Path('/run/media/haker/NVME 2/SteamLibrary/steamapps/common/Sins2');OUT=ROOT/'assets/derived/update25-ipbm';BUILD=ROOT/'build/update25-ipbm';GAME=BUILD/'game';AUD=ROOT/'audit/update25-ipbm';NAME='expanse25_un_ipbm';ZIP=Path('/home/haker/Downloads/UN IPBM from The Expanse - 2639049.zip');ENV=helper.ENV;WINE=helper.WINE;SDK=helper.SDK
for p in[OUT,BUILD,AUD,GAME/'meshes',GAME/'mesh_materials',GAME/'textures',GAME/'effects']:p.mkdir(parents=True,exist_ok=True)
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def prepare():
 archive=zipfile.ZipFile(ZIP);raw=archive.read('files/unnipbmv2.stl');data=np.frombuffer(raw[84:],dtype=[('n','<f4',3),('v','<f4',(3,3)),('a','<u2')]);source=data['v'].astype(float);cross=np.cross(source[:,1]-source[:,0],source[:,2]-source[:,0]);area=np.linalg.norm(cross,axis=1);exact=int((area==0).sum());small=int(((area>0)&(area<=1e-10)).sum());source=source[area>1e-10];lo=source.reshape(-1,3).min(0);hi=source.reshape(-1,3).max(0);center=(lo+hi)/2;reference=BASE/'meshes/expanse05_amun_torpedo.mesh';length=read_mesh(reference)['box'][5]*2;scale=length/(hi[2]-lo[2]);v,inv=np.unique(source.reshape(-1,3),axis=0,return_inverse=True);v=np.ascontiguousarray((v-center)*scale,dtype='f4');idx=np.ascontiguousarray(inv,dtype='u4');dst=np.empty_like(idx)
 libpath=MAIN/'.tools/libmeshoptimizer.so';lib=C.CDLL(str(libpath));u=C.POINTER(C.c_uint);f=C.POINTER(C.c_float);fn=lib.meshopt_simplify;fn.argtypes=[u,u,C.c_size_t,f,C.c_size_t,C.c_size_t,C.c_size_t,C.c_float,C.c_uint,f];fn.restype=C.c_size_t;error=C.c_float();count=fn(dst.ctypes.data_as(u),idx.ctypes.data_as(u),len(idx),v.ctypes.data_as(f),len(v),12,6000*3,.0007,0,C.byref(error));tt=v[dst[:count].reshape(-1,3)].astype(float);q=np.cross(tt[:,1]-tt[:,0],tt[:,2]-tt[:,0]);valid=np.linalg.norm(q,axis=1)>1e-10;slivers=int((~valid).sum());tt=tt[valid];axis=(-center*scale)[:2]
 oldframes=helper.frames
 def missileframes(tri):
  p=oldframes(tri);v=p['v'];n=p['n'];theta=np.arctan2(v[:,1]-axis[1],v[:,0]-axis[0]);uv=np.column_stack([(theta+np.pi)/(2*np.pi),(v[:,2]+length/2)/length]);uvtri=uv.reshape(-1,3,2)
  for a in uvtri:
   if np.ptp(a[:,0])>.5:a[a[:,0]<.5,0]+=1
  face=np.cross(tri[:,1]-tri[:,0],tri[:,2]-tri[:,0]);cap=np.repeat(abs(face[:,2])>np.linalg.norm(face[:,:2],axis=1)*2,3);uv[cap,0]=(v[cap,0]-v[:,0].min())/np.ptp(v[:,0]);uv[cap,1]=(v[cap,1]-v[:,1].min())/np.ptp(v[:,1]);t=np.column_stack([-np.sin(theta),np.cos(theta),np.zeros(len(v)),np.ones(len(v))]);t[cap,:3]=[1,0,0];t[:,:3]-=n*np.sum(n*t[:,:3],axis=1)[:,None];bad=np.linalg.norm(t[:,:3],axis=1)<1e-8;t[bad,:3]=p['t'][bad,:3];t[:,:3]/=np.linalg.norm(t[:,:3],axis=1)[:,None];bit=np.where(cap[:,None],[0,1,0],[0,0,1]);t[:,3]=np.where(np.sum(np.cross(n,t[:,:3])*bit,axis=1)<0,-1,1);uv[:,0]*=.5;p.update(uv=uv,t=t);return p
 helper.NAME=NAME;helper.OUT=OUT;helper.frames=missileframes;points=[{'name':'center','translation':[0,0,0]},{'name':'exhaust.0','translation':[float(axis[0]),float(axis[1]),-length/2],'rotation':[0,1,0,0]}];helper.save({'shell':tt},points);helper.frames=oldframes
 tex=OUT/'texture-sources';tex.mkdir(exist_ok=True);size=1024;image=Image.new('RGBA',(size,size),(173,179,180,255));draw=ImageDraw.Draw(image)
 # Cylindrical UVs preserve straight axial lettering and circumferential bands.
 draw.rectangle((0,0,size,200),fill=(49,57,65));draw.rectangle((0,235,size,270),fill=(52,74,96));draw.rectangle((0,865,size,size),fill=(128,140,150))
 for y in[210,300,535,790]:draw.line((0,y,size,y),fill=(113,122,129),width=3)
 try:font=ImageFont.truetype('/usr/share/fonts/TTF/DejaVuSans.ttf',65)
 except OSError:font=ImageFont.load_default(size=65)
 for x in[64,576]:draw.text((x,540),'UNN',font=font,fill=(31,58,83));draw.rectangle((x,510,x+140,518),fill=(48,82,110))
 image.putalpha(255);half=image.resize((size//2,size),Image.Resampling.LANCZOS);image.paste(half,(0,0));image.paste(half,(size//2,0));image.putalpha(255);image.save(tex/'expanse25_ipbm_clr.png');Image.new('RGBA',(16,16),(255,173,115,255)).save(tex/'expanse25_ipbm_orm.png');Image.new('RGBA',(16,16),(0,0,0,0)).save(tex/'expanse25_ipbm_msk.png');bounds=tt.reshape(-1,3);write(AUD/'integration-spec.json',{'status':'PREPARED','output_game':str(GAME),'base_mesh':NAME,'source':{'archive':str(ZIP),'zip_sha256':sha(ZIP),'member':'files/unnipbmv2.stl','stl_sha256':hashlib.sha256(raw).hexdigest(),'author':'trehn','url':'https://www.thingiverse.com/thing:2639049','license':archive.read('LICENSE.txt').decode(),'description':archive.read('README.txt').decode(),'original_triangles':39960,'exact_zero_area_removed':exact,'numerical_slivers_removed':small,'clean_source_triangles':len(source),'bounds':[lo.tolist(),hi.tolist()]},'optimization':{'target':6000,'relative_error':error.value,'relative_error_limit':.0007,'post_simplification_degenerates_removed':slivers,'library':str(libpath),'library_sha256':sha(libpath)},'scale':{'policy':'Match accepted Expanse torpedo visual length; never use print units directly. Not a canonical metric-size claim.','reference':str(reference),'reference_sha256':sha(reference),'reference_length':length,'game_length':float(np.ptp(bounds[:,2])),'source_to_game':scale},'counts':{'hull':len(tt),'source':39960},'spatial':{'box':{'center':((bounds.min(0)+bounds.max(0))/2).tolist(),'extents':((bounds.max(0)-bounds.min(0))/2).tolist()},'radius':float(np.linalg.norm(bounds,axis=1).max())},'meshpoints':points,'scope':'LOCAL NATIVE PLANET_BOMBING COSMETIC ONLY. No actual unit, damage, health, global firing or interception.','checks':{'no_stands_present':True,'original_shape_and_ribs_retained_with_bounded_simplification':True},'runtime':'NOT RUN'});print('Prepared',len(tt),'triangles; removed',exact,'zero-area and',small,'numerical slivers; error',error.value,flush=True)

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
 for p in(OUT/'texture-sources').glob('*.png'):
  with(BUILD/('texture-'+p.stem+'.log')).open('w')as log:subprocess.run([str(WINE),str(MAIN/'.tools/texconv.exe'),'-f','BC7_UNORM','-y','-m','0','-nogpu','--single-proc','-o','Z:'+str(GAME/'textures'),'-bc','q','Z:'+str(p)],env=ENV,stdout=log,stderr=subprocess.STDOUT,check=True,timeout=300)
 assert len(m['materials'])==1;write(GAME/'mesh_materials'/(m['materials'][0]+'.mesh_material'),{'version':1,'base_color_texture':'expanse25_ipbm_clr','occlusion_roughness_metallic_texture':'expanse25_ipbm_orm','normal_texture':'expanse10_donnager_flat_nrm','mask_texture':'expanse25_ipbm_msk','emissive_factor':0.0});normal=BASE/'textures/expanse10_donnager_flat_nrm.dds';(GAME/'textures'/normal.name).write_bytes(normal.read_bytes())
 donor=NATIVE/'effects/Weapon_TechFrigatePlanetBombing_Travel.particle_effect';effect=read(donor);mesh_emitter=next(e for e in effect['emitters']if e['particle']['type']=='mesh');assert mesh_emitter['particle']['mesh']['mesh']=='weapon_trader_missile_nuke';mesh_emitter['particle']['mesh']['mesh']=NAME
 # The stock visual is tail-origin: its mesh center is shifted forward. Keep
 # that convention while replacing the native nuke with the centered IPBM mesh.
 node_id=next(a['attachee_id']for a in effect['emitter_to_node_attachments']if a['attacher_id']==mesh_emitter['id']);node=next(n for n in effect['nodes']if n['id']==node_id);node['z']=[meta['scale']['reference_length']/2]*2;write(GAME/'effects/expanse25_ipbm_local_bombardment_travel.particle_effect',effect)
 native_skin=NATIVE/'entities/trader_siege_frigate.unit_skin';native_weapon=NATIVE/'entities/trader_siege_frigate_planet_bombing.weapon';alias={'alias_name':'trader_siege_frigate_planet_bombing_weapon_projectile_travel','alias_binding':{'particle_effect':'expanse25_ipbm_local_bombardment_travel'}}
 meta['effect_fragment']={'native_unit_skin_path':'skin_stages[].effects.effect_alias_bindings[]','entry':alias,'integration_note':'Use the actual local bombardment weapon travel alias on each selected ship skin. Do not replace the whole alias list. Preserve weapon_type planet_bombing, firing, damage, filters, range and cooldown. This changes only an already native mesh-particle travel effect.'};meta['source_game_hashes']={str(p):sha(p)for p in[normal,donor,native_skin,native_weapon]};meta['status']='OFFLINE COMPILED LOCAL BOMBARDMENT VISUAL PASS; RUNTIME UNTESTED';meta['checks'].update(meshpoint_transforms_exact=True,source_frame_error=float(distance.max()),opposed_winding_triangles=opposed,initial_winding_flips=flips,only_tangent_bytes_repaired=True,official_triangle_grid_and_trailer_preserved=True);meta['files']={str(p.relative_to(GAME)):sha(p)for p in sorted(GAME.rglob('*'))if p.is_file()};meta['wine_prefix_copied']=False;write(AUD/'integration-spec.json',meta);print(meta['status'],flush=True)
def preview():
 # Reuse the existing packaged-mesh/DDS renderer without importing gameplay.
 import update25_unone_art as renderer
 renderer.GAME=GAME;renderer.AUD=AUD;renderer.NAME=NAME;renderer.preview()
if __name__=='__main__':
 parser=argparse.ArgumentParser();parser.add_argument('stage',choices=['prepare','compile','preview']);args=parser.parse_args();globals()[args.stage]()
