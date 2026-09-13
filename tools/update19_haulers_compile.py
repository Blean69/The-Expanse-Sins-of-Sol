"""Compile hauler geometry using pinned MeshBuilder, retaining official facing-grid trailer."""
from pathlib import Path
import os,sys,subprocess,shutil,json,struct,hashlib
import numpy as np
from scipy.spatial import cKDTree
from common import Gltf,read_mesh,write
import update12_scirocco_common as c
R=Path(__file__).resolve().parents[1];D=R/'assets/derived/update19-haulers';B=R/'build/update19-haulers';A=R/'audit/update19-haulers';MAIN=Path('/run/media/haker/NVME 2/expanse-mod');SDK=Path('/run/media/haker/NVME 2/SteamLibrary/steamapps/common/Sins of a Solar Empire II - Mod Tools');wine=Path('/home/haker/.var/app/com.valvesoftware.Steam/.local/share/Steam/steamapps/common/Proton 10.0/files/bin/wine64');prefix=B/'proton-prefix'
if not prefix.exists():shutil.copytree(Path('/run/media/haker/NVME 2/expanse-workers/tachi-one-pdc/build/polish-b/proton-prefix'),prefix,symlinks=True)
env=dict(os.environ,WINEPREFIX=str(prefix),OMP_NUM_THREADS='4',MANGOHUD='0',WINEDEBUG='-all',DISPLAY='',WINEDLLOVERRIDES='mscoree,mshtml=')
c.OUT=D;meta=json.loads((A/'integration-spec.json').read_text());records=[]
for ship,sm in meta['ships'].items():
 z=np.load(D/(ship+'-parts.npz'));parts=[];repairs=0
 for j in range(len([k for k in z if k.endswith('_v')])):
  p={k:z[str(j)+'_'+k].copy()for k in ['v','n','t','uv','i']};p['material']=str(z[str(j)+'_material']);p['v']=p['v'].astype('float32').astype('float64');ii=p['i'];qq=np.cross(p['v'][ii[:,1]]-p['v'][ii[:,0]],p['v'][ii[:,2]]-p['v'][ii[:,0]]);p['i']=ii[np.linalg.norm(qq,axis=1)>1e-3];i=p['i'];q=np.cross(p['v'][i[:,1]]-p['v'][i[:,0]],p['v'][i[:,2]]-p['v'][i[:,0]]);nn=p['n'][i].mean(1);cos=np.sum(q*nn,axis=1)/np.maximum(np.linalg.norm(q,axis=1)*np.linalg.norm(nn,axis=1),1e-15);bad=abs(cos)<.5
  # Attribute simplification occasionally collapses bevels onto a face with invalid smooth normals.
  # Split only those triangles and rebuild an explicit geometric tangent basis.
  if bad.any():
   idx=i[bad];vv=p['v'][idx].reshape(-1,3);uv=p['uv'][idx].reshape(-1,2);face=q[bad];face*=np.where(cos[bad]<0,-1,1)[:,None];face/=np.linalg.norm(face,axis=1)[:,None];norm=np.repeat(face,3,axis=0);tan=[]
   for tri,tu,n in zip(vv.reshape(-1,3,3),uv.reshape(-1,3,2),face):
    du=tu[1]-tu[0];dv=tu[2]-tu[0];det=du[0]*dv[1]-dv[0]*du[1];t=((tri[1]-tri[0])*dv[1]-(tri[2]-tri[0])*du[1])/det if abs(det)>1e-8 else tri[1]-tri[0];t-=n*np.dot(t,n)
    if np.linalg.norm(t)<1e-8:t=np.cross(n,np.eye(3)[np.argmin(abs(n))])
    t/=np.linalg.norm(t);tan.extend([[*t,1.]]*3)
   start=len(p['v']);p['v']=np.concatenate([p['v'],vv]);p['n']=np.concatenate([p['n'],norm]);p['t']=np.concatenate([p['t'],tan]);p['uv']=np.concatenate([p['uv'],uv]);p['i'][bad]=np.arange(start,len(p['v'])).reshape(-1,3);repairs+=int(bad.sum())
  parts.append(p)
 merged={}
 for p in parts:
  key=p['material']
  if key not in merged:merged[key]=p
  else:
   prev=merged[key];offset=len(prev['v']);prev['i']=np.concatenate([prev['i'],p['i']+offset])
   for k in ['v','n','t','uv']:prev[k]=np.concatenate([prev[k],p[k]])
 parts=list(merged.values())
 sm['counts']['hull']=sum(len(p['i'])for p in parts)
 name=sm['hull_mesh'];lo=np.array(sm['ship_spatial']['bounds_min']);hi=np.array(sm['ship_spatial']['bounds_max']);center=np.array(sm['source_center']);rot=np.array(sm['source_to_game_rotation']);scale=sm['game_units_per_metre']
 # Source-engine apertures: Artemis fullhull aft is -Z. LeGuin is provisional derelict art only.
 source_exhausts=([[-10.09944,.46667,-61.75],[.33870,.46667,-61.75],[10.77684,.46667,-61.75]] if ship=='artemis' else [])
 points=[{'name':'center','translation':[0,0,0]},{'name':'above','translation':[0,float(hi[1]+5),0]},{'name':'aura','translation':[0,float(lo[1]-5),0]}];exhausts=[]
 for j,sp in enumerate(source_exhausts):
  pos=(np.array(sp)-center)@rot.T*scale;points.append({'name':f'exhaust.{j}','translation':pos.tolist(),'rotation':[0,1,0,0]});exhausts.append({'position':pos.tolist(),'forward':[0,0,-1],'up':[0,1,0],'source_position_metres':sp,'placement':'Three measured circular aft engine mouth centers, verify plume alignment in game'})
 c.savegltf(name,parts,points);c.savegltf(name.replace('_hull','_editable'),parts,points,compiler=False)
 # Add editable textures after save; game aliases are resolved from actual compiler materials below.
 eg=json.loads((D/(name.replace('_hull','_editable')+'.gltf')).read_text());eg['images']=[];eg['textures']=[]
 for mm in eg['materials']:
  eg['images'].append({'uri':'textures/'+mm['name']+'_clr.png'});eg['textures'].append({'source':len(eg['images'])-1});mm['pbrMetallicRoughness']={'baseColorTexture':{'index':len(eg['textures'])-1},'baseColorFactor':[1,1,1,1]}
 write(D/(name.replace('_hull','_editable')+'.gltf'),eg)
 for fmt in ['json','binary']:
  dest=B/('compiler-'+fmt);dest.mkdir(exist_ok=True)
  with (B/(name+'-'+fmt+'.log')).open('w')as log:subprocess.run([str(wine),str(SDK/'MeshBuilder/bin/MeshBuilder.exe'),'--input_path=Z:'+str(D/(name+'.gltf')),'--output_folder_path=Z:'+str(dest),'--mesh_output_format='+fmt,'--fill_triangle_facing_grid'],env=env,stdout=log,stderr=subprocess.STDOUT,check=True,timeout=300)
 bp=B/'compiler-binary'/(name+'.mesh');jp=B/'compiler-json'/(name+'.mesh_json');m=json.loads(jp.read_text());gv=Gltf(D/(name+'.gltf'));buf=bytearray(gv.buffers[0]);v=np.array([q['p']for q in m['non_skinned_vertices']]);n=np.array([q['n']for q in m['non_skinned_vertices']]);allidx=np.array(m['vertex_indices']);flipped=0
 for mp in m['primitives']:
  material=m['materials'][mp['material_index']];matches=[p for p in gv.g['meshes'][0]['primitives']if material.endswith('_'+gv.g['materials'][p['material']]['name'])];assert len(matches)==1;pr=matches[0]
  i=allidx[mp['vertex_index_start']:mp['vertex_index_start']+mp['vertex_index_count']].reshape(-1,3);q=np.cross(v[i[:,1]]-v[i[:,0]],v[i[:,2]]-v[i[:,0]]);cos=(q*n[i].mean(1)).sum(1);flip=cos< -1e-8;ac=gv.g['accessors'][pr['indices']];bv=gv.g['bufferViews'][ac['bufferView']];arr=np.ndarray((ac['count']//3,3),dtype='<u4',buffer=buf,offset=bv.get('byteOffset',0)+ac.get('byteOffset',0));assert len(arr)==len(i);arr[flip]=arr[flip][:,[0,2,1]];flipped+=int(flip.sum())
 if flipped:
  (D/(name+'.bin')).write_bytes(buf)
  for fmt in ['json','binary']:
   with (B/(name+'-winding-'+fmt+'.log')).open('w')as log:subprocess.run([str(wine),str(SDK/'MeshBuilder/bin/MeshBuilder.exe'),'--input_path=Z:'+str(D/(name+'.gltf')),'--output_folder_path=Z:'+str(B/('compiler-'+fmt)),'--mesh_output_format='+fmt,'--fill_triangle_facing_grid'],env=env,stdout=log,stderr=subprocess.STDOUT,check=True,timeout=300)
 original=bp.read_bytes();b=bytearray(original);m=json.loads(jp.read_text());count=struct.unpack_from('<Q',b,53)[0];offset=61;binary=[];offsets=[]
 for _ in range(count):
  vals=struct.unpack_from('<12f?',b,offset);binary.append(vals[:-1]);offsets.append(offset+24);offset+=49+(8 if vals[-1]else 0)
 binary=np.array(binary);lookup=np.concatenate([np.column_stack([p['v'],p['n'],p['uv']])for p in parts]);st=np.concatenate([p['t']for p in parts]);dist,ids=cKDTree(lookup).query(np.column_stack([binary[:,:6],binary[:,10:12]]));assert dist.max()<3e-4,(ship,dist.max());t=st[ids].copy();n=binary[:,3:6];t[:,:3]-=n*(t[:,:3]*n).sum(1)[:,None];norm=np.linalg.norm(t[:,:3],axis=1);assert norm.min()>1e-8;t[:,:3]/=norm[:,None];t[:,3]=np.where(t[:,3]<0,-1,1);allowed=np.zeros(len(b),bool)
 for j,off in enumerate(offsets):struct.pack_into('<4f',b,off,*t[j]);allowed[off:off+16]=True
 assert np.all((np.frombuffer(original,np.uint8)==np.frombuffer(b,np.uint8))|allowed);parsed=read_mesh(bp)['parsed_prefix_bytes'];assert b[parsed:]==original[parsed:];i=np.array(m['vertex_indices']).reshape(-1,3);v=binary[:,:3];q=np.cross(v[i[:,1]]-v[i[:,0]],v[i[:,2]]-v[i[:,0]]);cos=(q*n[i].mean(1)).sum(1)/np.maximum(np.linalg.norm(q,axis=1)*np.linalg.norm(n[i].mean(1),axis=1),1e-15);assert (cos< -1e-5).sum()==0,(ship,(cos< -1e-5).sum())
 (B/'game/meshes').mkdir(parents=True,exist_ok=True);out=B/'game/meshes'/(name+'.mesh');out.write_bytes(b);sm['equipment']={'exhausts':exhausts,'exhaust':exhausts[0]if exhausts else None};sm['meshpoints']={'hull':points};sm['materials']=m['materials'];sm['runtime_role_restriction']='None'if ship=='artemis'else 'Source wreck exterior; stationary derelict/prototype only. No verified propulsion assembly.';sm['compile_sha256']=hashlib.sha256(b).hexdigest();records.append({'ship':ship,'triangles':len(i),'sha256':sm['compile_sha256'],'near_perpendicular_faces_reframed':repairs,'only_tangent_bytes_patched':True,'official_trailer_unchanged':True,'tangent_match_max_error':float(dist.max()),'opposed_winding_triangles':0});print(ship,'COMPILED',flush=True)
meta['status']='OFFLINE GEOMETRY PASS; MATERIAL CONVERSION PENDING';write(A/'integration-spec.json',meta);write(A/'mesh-validation.json',{'status':'PASS OFFLINE','records':records,'runtime':'NOT RUN'})
