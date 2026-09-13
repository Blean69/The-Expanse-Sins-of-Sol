"""Prepare one dorsal PDC from existing normalized/optimized assets. Never install.
Uses frozen master/baseline as read-only inputs; writes only worker-b outputs.
"""
from common import Gltf, read, write, read_mesh, ROOT
from pathlib import Path
import argparse, copy, hashlib, json, os, shutil, subprocess
import numpy as np
from PIL import Image, ImageDraw

P=argparse.ArgumentParser();P.add_argument('--source-root',type=Path,required=True);P.add_argument('--sdk',type=Path,required=True);P.add_argument('--wine',type=Path);P.add_argument('--compile',action='store_true');args=P.parse_args()
src=args.source_root.resolve();out=ROOT/'assets/derived/worker-b';build=ROOT/'build/worker-b';audit=ROOT/'audit/workers/b'
for d in [out,build,audit]:d.mkdir(parents=True,exist_ok=True)
required=[src/'assets/derived/baseline/mcrn_editable.gltf',src/'assets/derived/baseline/scene.bin',src/'assets/derived/pdc-rigs/mcrn_pdc_1_base.gltf',src/'assets/derived/pdc-rigs/mcrn_pdc_1_barrel.gltf',src/'audit/pdc-rig-candidates.json',args.sdk/'MeshBuilder/bin/MeshBuilder.exe']
for f in required:
 if not f.is_file():raise SystemExit('MISSING DEPENDENCY; NOT PASSED: '+str(f))
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
frozen={str(p):sha(p) for p in required}
a=Gltf(required[0]);g=a.g;rig=read(src/'audit/pdc-rig-candidates.json')['rigs'][1]
# Existing candidates are inspected, then corrected; their sources remain untouched.
for k in ['base','barrel']:Gltf(src/f'assets/derived/pdc-rigs/mcrn_pdc_1_{k}.gltf')
B=np.diag([-1.,1.,-1.]);yaw=a.world[475][:3,3].copy()
def points(ni):return np.concatenate([a.positions(ni,p) for p in g['meshes'][g['nodes'][ni]['mesh']]['primitives']])
pin=points(499);pitch=(pin.min(0)+pin.max(0))/2;pitch[0]=yaw[0]
bv=points(487);tip=bv[bv[:,2]<bv[:,2].min()+.021847177771839144].mean(0)
barrel_offset=(pitch-yaw)@B;muzzle=(tip-pitch)@B
pitch_nodes={491,477,485,487,489,493,495};yaw_nodes={497,499};fixed_nodes={6,513,515,517,519}
# pdc_gun_body has disconnected lower platform and upper housing. Split existing
# triangles only at y=2.5, across a verified empty gap: no new cut triangles.
groups={k:[] for k in ['hull','base','barrel']};parts=[];total=0
for ni,n in enumerate(g['nodes']):
 if 'mesh' not in n or ni not in a.world:continue
 for pi,p in enumerate(g['meshes'][n['mesh']]['primitives']):
  pos=a.positions(ni,p);idx=a.accessor(p['indices']).flatten().reshape(-1,3);total+=len(idx)
  if ni==475:
   yy=pos[idx][:,:,1];lo=yy.max(1)<2.5;hi=yy.min(1)>2.5
   assert np.all(lo|hi),'Body triangles cross mechanical split; manual review needed'
   partitions=[('base',idx[lo]),('barrel',idx[hi])]
  else:partitions=[('barrel' if ni in pitch_nodes else 'base' if ni in yaw_nodes else 'hull',idx)]
  for kind,inds in partitions:
   if len(inds):groups[kind].append((ni,p,inds));parts.append(dict(node=ni,name=n['name'],part=kind,triangles=len(inds)))
assert total==14622
moving={p['node'] for p in parts if p['part']!='hull'}
assert fixed_nodes.isdisjoint(moving)
assert all(p['node'] not in moving for p in parts if p['part']=='hull')
frames={'hull':(np.eye(3),np.zeros(3)),'base':(B,yaw),'barrel':(B,pitch)}
basepoints=read(src/'audit/derivative-transform.json')['meshpoints']
meshpoints={'hull':basepoints+[{'name':'child.pdturret_mount_0','translation':yaw.tolist(),'rotation':[0,1,0,0]}], 'base':[{'name':'child.pdturret_barrel_0','translation':barrel_offset.tolist()}], 'barrel':[{'name':'turret_muzzle.0','translation':muzzle.tolist()}]}
counts={};recompose_error=0;drawfaces={}
for kind,items in groups.items():
 name='expanse_tachi_one_pdc_'+kind;buf=bytearray();cg={'asset':{'version':'2.0','generator':'Expanse one-PDC experiment; attribution ASSET-SOURCES.md'},'scene':0,'scenes':[{'nodes':[0]}],'nodes':[{'name':name,'mesh':0,'children':[]}],'meshes':[{'name':name,'primitives':[]}],'buffers':[],'bufferViews':[],'accessors':[],'materials':[]}
 frame,origin=frames[kind];counts[kind]=sum(len(idx) for _,_,idx in items);drawfaces[kind]=[]
 def acc(v,typ,ct=5126):
  v=np.asarray(v,dtype='<f4' if ct==5126 else '<u4');buf.extend(b'\0'*((-len(buf))%4));start=len(buf);buf.extend(v.tobytes());cg['bufferViews'].append({'buffer':0,'byteOffset':start,'byteLength':v.nbytes});at={'bufferView':len(cg['bufferViews'])-1,'componentType':ct,'count':len(v),'type':typ}
  if typ=='VEC3':at.update(min=v.min(0).tolist(),max=v.max(0).tolist())
  cg['accessors'].append(at);return len(cg['accessors'])-1
 for mi,mat in enumerate(g['materials']):
  arrays={k:[] for k in ['POSITION','NORMAL','TANGENT','TEXCOORD_0']};indices=[];nv=0
  for ni,p,idx in items:
   if p['material']!=mi:continue
   # Preserve baseline vertex context; no new optimization/compaction pass.
   used=np.arange(len(a.accessor(p['attributes']['POSITION'])))
   world=a.positions(ni,p)[used];v=(world-origin)@frame
   recompose_error=max(recompose_error,float(np.max(np.abs(v@frame.T+origin-world))))
   drawfaces[kind].extend(world[idx].tolist());m=a.world[ni];norm=a.accessor(p['attributes']['NORMAL'])[used]@np.linalg.inv(m[:3,:3]);norm/=np.linalg.norm(norm,axis=1)[:,None];norm=norm@frame
   uv=a.accessor(p['attributes']['TEXCOORD_0'])[used]
   if 'TANGENT' in p['attributes']:
    tang=a.accessor(p['attributes']['TANGENT'])[used];tang[:,:3]=tang[:,:3]@m[:3,:3].T@frame;tang[:,:3]/=np.linalg.norm(tang[:,:3],axis=1)[:,None]
   else:
    i0,i1,i2=idx[0];e1=v[i1]-v[i0];e2=v[i2]-v[i0];d1=uv[i1]-uv[i0];d2=uv[i2]-uv[i0];den=d1[0]*d2[1]-d1[1]*d2[0];t=(e1*d2[1]-e2*d1[1])/den;t/=np.linalg.norm(t);bt=(e2*d1[0]-e1*d2[0])/den;tang=np.tile([*t,1 if np.dot(np.cross(norm[i0],t),bt)>0 else -1],(len(v),1))
   if np.linalg.det(m[:3,:3])<0:idx=idx[:,[0,2,1]];tang[:,3]*=-1
   # Compensate official MeshBuilder glTF Z reflection, including handedness.
   v[:,2]*=-1;norm[:,2]*=-1;tang[:,2]*=-1;tang[:,3]*=-1;idx=idx[:,[0,2,1]]
   for k,x in [('POSITION',v),('NORMAL',norm),('TANGENT',tang),('TEXCOORD_0',uv)]:arrays[k].append(x)
   indices.append(idx.flatten()+nv);nv+=len(v)
  if not indices:continue
  mindex=len(cg['materials']);cg['materials'].append({'name':'mcrn_tachi_'+mat['name'].lower(),'pbrMetallicRoughness':{'baseColorFactor':[1,1,1,1],'metallicFactor':1,'roughnessFactor':1}})
  cg['meshes'][0]['primitives'].append({'attributes':{k:acc(np.concatenate(vals),'VEC2' if k=='TEXCOORD_0' else 'VEC4' if k=='TANGENT' else 'VEC3') for k,vals in arrays.items()},'indices':acc(np.concatenate(indices),'SCALAR',5125),'material':mindex,'mode':4})
 for point in meshpoints[kind]:
  pp=copy.deepcopy(point);pp['translation'][2]*=-1;cg['nodes'][0]['children'].append(len(cg['nodes']));cg['nodes'].append(pp)
 cg['buffers']=[{'uri':name+'.bin','byteLength':len(buf)}];(out/(name+'.bin')).write_bytes(buf);write(out/(name+'.gltf'),cg)
 # Separate editable game-coordinate derivative. The original named normalized
 # model remains the master; audit records every triangle partition by node.
 editable=copy.deepcopy(cg);ebuf=bytearray(buf)
 for prim in editable['meshes'][0]['primitives']:
  for semantic in ['POSITION','NORMAL','TANGENT']:
   at=editable['accessors'][prim['attributes'][semantic]];view=editable['bufferViews'][at['bufferView']];width=4 if semantic=='TANGENT' else 3
   vv=np.ndarray((at['count'],width),dtype='<f4',buffer=ebuf,offset=view['byteOffset']);vv[:,2]*=-1
   if semantic=='TANGENT':vv[:,3]*=-1
   if semantic=='POSITION':at.update(min=vv.min(0).tolist(),max=vv.max(0).tolist())
  at=editable['accessors'][prim['indices']];view=editable['bufferViews'][at['bufferView']];ii=np.ndarray((at['count']//3,3),dtype='<u4',buffer=ebuf,offset=view['byteOffset']);ii[:]=ii[:,[0,2,1]]
 for node in editable['nodes'][1:]:node['translation'][2]*=-1
 editable['buffers'][0]['uri']=name+'_editable.bin';editable['asset']['generator']='Editable game-coordinate derivative; DO NOT feed directly to MeshBuilder'
 (out/(name+'_editable.bin')).write_bytes(ebuf);write(out/(name+'_editable.gltf'),editable)
assert sum(counts.values())==14622 and recompose_error<1e-10
# A source-pose side/front diagram based on the actual triangle geometry.
im=Image.new('RGB',(1400,880),'#151b24');d=ImageDraw.Draw(im);colors={'hull':'#697788','base':'#efb657','barrel':'#6cd1d8'}
for panel,axes in enumerate([(2,1),(0,1)]):
 xaxis,yaxis=axes;cx=350 if panel==0 else 1040;ctr=-19.6 if panel==0 else 0
 faces=[]
 for kind,fs in drawfaces.items():
  for q in fs:
   q=np.array(q)
   if np.max(np.abs(q[:,0]))>3.1 or q[:,1].max()<-.1 or q[:,1].min()>6 or q[:,2].min()<-24 or q[:,2].max()>-16:continue
   xy=[(float(cx+(p[xaxis]-ctr)*78),float(660-p[yaxis]*84)) for p in q];faces.append((q[:,0 if panel==0 else 2].mean(),xy,colors[kind]))
 for _,pts,c in sorted(faces):d.polygon(pts,fill=c,outline='#36414d')
 for label,p,col in [('YAW +Y',yaw,'#ffce7b'),('PITCH local +X',pitch,'#ffffff'),('MUZZLE +local Z',tip,'#ff7589')]:
  x=float(cx+(p[xaxis]-ctr)*78);y=float(660-p[yaxis]*84);d.ellipse((x-5,y-5,x+5,y+5),outline=col,width=2);d.text((x+8,y+8),label,fill=col)
d.text((35,20),'ONE DORSAL PDC / GEOMETRY CANDIDATE / RUNTIME NOT RUN',fill='white');d.text((35,46),'Side: aft-facing barrel points left. Front: viewed along ship Z. Gold yaw; cyan pitch; gray fixed deployment linkage.',fill='white');d.text((35,790),'Existing body node475 splits into 84 base triangles + 96 barrel triangles across empty y=2.5 gap.',fill='white');d.text((35,814),'Sphere node493 is above the gun: old sphere-origin rig rejected. Pivots below are geometric estimates for runtime inspection.',fill='white');im.save(audit/'one-pdc-annotated.png')
metadata={'status':'COMPILED OR EDITABLE CANDIDATE ONLY; SHADING GATE REQUIRED; RUNTIME NOT RUN','package_gate':'NOT CHECKED: run tachi_verify_compiler.py; compilation alone does not permit packaging','source_root':str(src),'source_commit':subprocess.check_output(['git','-C',str(src),'rev-parse','HEAD'],text=True).strip(),'representative_rig_index':1,'source_files_sha256':frozen,'counts':counts,'total_triangles':total,'rest_pose_recomposition_max_error':recompose_error,'coordinate_frame':{'game_forward':[0,0,1],'local_forward_in_hull':[0,0,-1],'local_up_in_hull':[0,1,0],'local_right_in_hull':[-1,0,0],'determinant':float(np.linalg.det(B))},'yaw_pivot_hull':yaw.tolist(),'pitch_pivot_hull':pitch.tolist(),'barrel_position':barrel_offset.tolist(),'muzzle_positions':[muzzle.tolist()],'muzzle_hull':tip.tolist(),'pivot_basis':'yaw named body lower-platform origin; pitch midpoint of holder-detail pin bounds, centered on body X; geometric estimates, not authored/engine-verified pivots','fixed_deployment_nodes':sorted(fixed_nodes),'geometry_partition':parts,'mount':{'weapon':'expanse_tachi_one_pdc_garda','mesh_point':'child.pdturret_mount_0','weapon_position':yaw.tolist(),'forward':[0,0,-1],'up':[0,1,0],'yaw_arc':{'min_angle':-45.0,'max_angle':45.0},'pitch_arc':{'min_angle':-20.0,'max_angle':0.0}},'arcs_status':'Conservative experiment limits only; sign and hull occlusion need runtime verification. No global coverage claim.','turret_override':{'type':'biaxial','biaxial_base_mesh':'pdturret_mount_0','biaxial_barrel_mesh':'pdturret_barrel_0','barrel_position':barrel_offset.tolist(),'muzzle_positions':[muzzle.tolist()]},'skin_alias_map':[{'mesh_alias_name':'pdturret_mount_0','mesh_definition':{'mesh':'expanse_tachi_one_pdc_base','shader':'ship','is_shadow_blocker':True}},{'mesh_alias_name':'pdturret_barrel_0','mesh_definition':{'mesh':'expanse_tachi_one_pdc_barrel','shader':'ship','is_shadow_blocker':True}}],'compiled':False,'checks':{'triangle_conservation':'PASS','no_static_moving_duplicates':'PASS','rest_pose_recomposition':'PASS','orthonormal_axes':'PASS','body_split_without_cutting':'PASS','runtime_rotation':'NOT RUN'}}
if args.compile:
 if args.wine and not args.wine.is_file():raise SystemExit('MISSING DEPENDENCY; compiler NOT PASSED: '+str(args.wine))
 env=dict(os.environ,OMP_NUM_THREADS='4',MANGOHUD='0',WINEDEBUG='-all',DISPLAY='',WINEDLLOVERRIDES='mscoree,mshtml=')
 if args.wine:
  prefix=build/'proton-prefix'
  if not prefix.exists():shutil.copytree(src/'.tools/proton-prefix',prefix,symlinks=True)
  env['WINEPREFIX']=str(prefix)
 def wp(p):return 'Z:'+str(p) if args.wine else str(p)
 outputs=[]
 for kind in groups:
  name='expanse_tachi_one_pdc_'+kind
  for fmt in ['json','binary']:
   dest=build/('compiler-'+fmt);dest.mkdir(exist_ok=True)
   cmd=([str(args.wine)] if args.wine else [])+[str(args.sdk/'MeshBuilder/bin/MeshBuilder.exe'),'--input_path='+wp(out/(name+'.gltf')),'--output_folder_path='+wp(dest),'--mesh_output_format='+fmt,'--fill_triangle_facing_grid']
   with (build/(name+'-'+fmt+'.log')).open('w') as log:subprocess.run(cmd,env=env,stdout=log,stderr=subprocess.STDOUT,check=True,timeout=300)
  mesh=build/'compiler-binary'/(name+'.mesh');info=read_mesh(mesh);assert info['triangles']==counts[kind]
  assert len(info['meshpoints'])==len(meshpoints[kind])
  for actual,point in zip(info['meshpoints'],meshpoints[kind]):
   assert actual['name']==point['name'] and np.allclose(actual['position'],point['translation'],atol=2e-5)
  outputs.append({'kind':kind,'mesh':str(mesh),'sha256':sha(mesh),'materials':info['materials'],'triangles':info['triangles'],'meshpoints':info['meshpoints']})
 metadata['compiled']=True;metadata['outputs']=outputs;metadata['checks']['official_json_and_binary_compilation']='PASS';metadata['checks']['compiled_triangle_and_meshpoint_checks']='PASS'
for p,h in frozen.items():assert sha(Path(p))==h,'Read-only dependency changed: '+p
metadata['checks']['read_only_input_hashes']='PASS';write(audit/'mount-metadata.json',metadata)
print(json.dumps({'counts':counts,'compiled':metadata['compiled'],'metadata':str(audit/'mount-metadata.json')}))
