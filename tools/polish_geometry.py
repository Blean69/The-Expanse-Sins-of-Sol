"""Six PDC geometry polish; frozen model and SDK are read-only dependencies."""
from common import *
import argparse,copy,hashlib,subprocess,shutil
P=argparse.ArgumentParser();P.add_argument('--source-root',type=Path,required=True);P.add_argument('--sdk',type=Path,required=True);P.add_argument('--wine',type=Path);P.add_argument('--compile',action='store_true');args=P.parse_args()
src=args.source_root;out=ROOT/'assets/derived/polish-b';build=ROOT/'build/polish-b';audit=ROOT/'audit/polish-b'
for p in [out,build,audit]:p.mkdir(parents=True,exist_ok=True)
for p in [src/'assets/derived/baseline/mcrn_editable.gltf',src/'assets/derived/baseline/scene.bin',args.sdk/'MeshBuilder/bin/MeshBuilder.exe']:
 if not p.exists():raise SystemExit('MISSING DEPENDENCY: '+str(p))
a=Gltf(src/'assets/derived/baseline/mcrn_editable.gltf');g=a.g;old=read(src/'audit/pdc-rig-candidates.json')['rigs'];rigs=[];groups={'hull':[]};frames={'hull':(np.eye(3),np.zeros(3))};parts=[]
def ps(ni):return np.concatenate([a.positions(ni,p) for p in g['meshes'][g['nodes'][ni]['mesh']]['primitives']])
for r in old:
 i=r['index'];body=427+48*i;up=np.array(r['up']);fw=np.array(r['forward']);B=np.column_stack([np.cross(up,fw),up,fw]);yaw=a.world[body][:3,3].copy();pins=(ps(body+24)-yaw)@B;po=(pins.min(0)+pins.max(0))/2;po[0]=0;pitch=yaw+B@po;bar=(ps(body+12)-yaw)@B;tip=bar[bar[:,2]>bar[:,2].max()-.02184717777].mean(0);muzzle=tip-po
 rr={'index':i,'body':body,'B':B,'yaw':yaw,'pitch':pitch,'barrel_position':po,'muzzle':muzzle,'pitch_nodes':{body+j for j in [2,10,12,14,16,18,20]},'yaw_nodes':{body+22,body+24}}
 rigs.append(rr)
 for k,origin in [('base',yaw),('barrel',pitch)]:groups[f'pdc_{i}_{k}']=[];frames[f'pdc_{i}_{k}']=(B,origin)
for ni,n in enumerate(g['nodes']):
 if 'mesh' not in n or ni not in a.world:continue
 r=next((r for r in rigs if ni==r['body'] or ni in r['pitch_nodes'] or ni in r['yaw_nodes']),None)
 for pi,p in enumerate(g['meshes'][n['mesh']]['primitives']):
  idx=a.accessor(p['indices']).flatten().reshape(-1,3)
  if r and ni==r['body']:
   v=(a.positions(ni,p)-r['yaw'])@r['B'];yy=v[idx][:,:,1];lo=yy.max(1)<.65;hi=yy.min(1)>.65;assert np.all(lo|hi),(ni,'split crosses triangles');assign=[(f'pdc_{r["index"]}_base',idx[lo]),(f'pdc_{r["index"]}_barrel',idx[hi])]
  elif r:assign=[(f'pdc_{r["index"]}_'+('base' if ni in r['yaw_nodes'] else 'barrel'),idx)]
  else:assign=[('hull',idx)]
  for k,idxs in assign:
   if len(idxs):groups[k].append((ni,p,idxs));parts.append({'node':ni,'name':n['name'],'part':k,'triangles':len(idxs)})
points={'hull':read(src/'audit/derivative-transform.json')['meshpoints']};metadata=[]
for r in rigs:
 i=r['index'];aliasbase=f'expanse_pdc_{i}_base';aliasbar=f'expanse_pdc_{i}_barrel';B=r['B'];# rotation quaternion from exact signed-permutation basis
 tr=np.trace(B)
 if tr>0:q=np.array([B[2,1]-B[1,2],B[0,2]-B[2,0],B[1,0]-B[0,1],1+tr]);q/=np.linalg.norm(q)
 else:
  from scipy.spatial.transform import Rotation
  q=Rotation.from_matrix(B).as_quat()
 points['hull'].append({'name':'child.'+aliasbase,'translation':r['yaw'].tolist(),'rotation':q.tolist()});points[f'pdc_{i}_base']=[{'name':'child.'+aliasbar,'translation':r['barrel_position'].tolist()}];points[f'pdc_{i}_barrel']=[{'name':'turret_muzzle.0','translation':r['muzzle'].tolist()}]
 metadata.append({'index':i,'pivot_basis':'Body lower-platform origin / actual holder-detail pin bounds; geometry estimates awaiting runtime','yaw_pivot_hull':r['yaw'].tolist(),'pitch_pivot_hull':r['pitch'].tolist(),'basis_columns':B.tolist(),'mount':{'weapon':f'expanse_polish_pdc_{i}','mesh_point':'child.'+aliasbase,'weapon_position':r['yaw'].tolist(),'forward':B[:,2].tolist(),'up':B[:,1].tolist(),'yaw_arc':{'min_angle':-100.0,'max_angle':100.0},'pitch_arc':{'min_angle':-75.0,'max_angle':5.0}},'turret_override':{'type':'biaxial','biaxial_base_mesh':aliasbase,'biaxial_barrel_mesh':aliasbar,'barrel_position':r['barrel_position'].tolist(),'muzzle_positions':[r['muzzle'].tolist()]},'skin_alias_map':[{'mesh_alias_name':alias,'mesh_definition':{'mesh':f'expanse_polish_pdc_{i}_{kind}','shader':'ship','is_shadow_blocker':True}} for alias,kind in [(aliasbase,'base'),(aliasbar,'barrel')]]})
counts={};inputchecks={};sources={}
for kind,items in groups.items():
 name='expanse_polish_'+kind;B,origin=frames[kind];buf=bytearray();cg={'asset':{'version':'2.0','generator':'Expanse six-PDC polish derivative'},'scene':0,'scenes':[{'nodes':[0]}],'nodes':[{'name':name,'mesh':0,'children':[]}],'meshes':[{'name':name,'primitives':[]}],'buffers':[],'bufferViews':[],'accessors':[],'materials':[]};sources[kind]={};counts[kind]=sum(len(idx) for _,_,idx in items)
 def acc(v,typ,ct=5126):
  v=np.asarray(v,dtype='<f4' if ct==5126 else '<u4');buf.extend(b'\0'*((-len(buf))%4));start=len(buf);buf.extend(v.tobytes());cg['bufferViews'].append({'buffer':0,'byteOffset':start,'byteLength':v.nbytes});at={'bufferView':len(cg['bufferViews'])-1,'componentType':ct,'count':len(v),'type':typ}
  if typ=='VEC3':at.update(min=v.min(0).tolist(),max=v.max(0).tolist())
  cg['accessors'].append(at);return len(cg['accessors'])-1
 flips=0
 for mi,mat in enumerate(g['materials']):
  vals={k:[] for k in ['POSITION','NORMAL','TANGENT','TEXCOORD_0']};inds=[];nv=0
  for ni,p,idx in items:
   if p['material']!=mi:continue
   m=a.world[ni];v=(a.positions(ni,p)-origin)@B;n=a.accessor(p['attributes']['NORMAL'])@np.linalg.inv(m[:3,:3]);n/=np.linalg.norm(n,axis=1)[:,None];n=n@B;uv=a.accessor(p['attributes']['TEXCOORD_0'])
   if 'TANGENT' in p['attributes']:
    t=a.accessor(p['attributes']['TANGENT']);t[:,:3]=t[:,:3]@m[:3,:3].T@B;t[:,:3]/=np.maximum(np.linalg.norm(t[:,:3],axis=1)[:,None],1e-15)
    if np.linalg.det(m[:3,:3])<0:t[:,3]*=-1
   else:
    tri=idx[0];q=v[tri];u=uv[tri];e1=q[1]-q[0];e2=q[2]-q[0];d1=u[1]-u[0];d2=u[2]-u[0];den=np.linalg.det(np.stack([d1,d2]));tt=(e1*d2[1]-e2*d1[1])/den;tt/=np.linalg.norm(tt);bt=(e2*d1[0]-e1*d2[0])/den;t=np.tile([*tt,1 if np.dot(np.cross(n[tri[0]],tt),bt)>0 else -1],(len(v),1))
   for key,val in [('POSITION',v),('NORMAL',n),('TANGENT',t),('TEXCOORD_0',uv)]:vals[key].append(val)
   inds.append(idx.flatten()+nv);nv+=len(v)
  if not inds:continue
  vals={k:np.concatenate(v) for k,v in vals.items()};idx=np.concatenate(inds).reshape(-1,3);vi=vals['POSITION'][idx];dot=np.sum(np.cross(vi[:,1]-vi[:,0],vi[:,2]-vi[:,0])*vals['NORMAL'][idx].mean(1),axis=1);negative=dot<0;idx[negative]=idx[negative][:,[0,2,1]];flips+=int(negative.sum())
  # Save exact source frames before official importer tangent generation.
  sources[kind][mi]={'positions':vals['POSITION'].tolist(),'normals':vals['NORMAL'].tolist(),'tangents':vals['TANGENT'].tolist(),'uv':vals['TEXCOORD_0'].tolist()}
  # Reflect vertices only. An outward game face becomes negative in importer
  # coordinates; the importer geometry reflection should restore outward sign.
  for key in ['POSITION','NORMAL','TANGENT']:vals[key][:,2]*=-1
  vals['TANGENT'][:,3]*=-1
  mid=len(cg['materials']);cg['materials'].append({'name':'mcrn_tachi_'+mat['name'].lower(),'pbrMetallicRoughness':{'baseColorFactor':[1,1,1,1],'metallicFactor':1,'roughnessFactor':1}})
  cg['meshes'][0]['primitives'].append({'attributes':{k:acc(v,'VEC4' if k=='TANGENT' else 'VEC2' if k=='TEXCOORD_0' else 'VEC3') for k,v in vals.items()},'indices':acc(idx.flatten(),'SCALAR',5125),'material':mid,'mode':4})
 for p in points[kind]:
  cp=copy.deepcopy(p);cp['translation'][2]*=-1
  if 'rotation' in cp:cp['rotation'][0]*=-1;cp['rotation'][1]*=-1
  cg['nodes'][0]['children'].append(len(cg['nodes']));cg['nodes'].append(cp)
 cg['buffers']=[{'uri':name+'.bin','byteLength':len(buf)}];(out/(name+'.bin')).write_bytes(buf);write(out/(name+'.gltf'),cg);inputchecks[kind]={'triangles':counts[kind],'source_winding_corrections':flips}
write(out/'retained-source-frames.json',sources)
assert sum(counts.values())==14622
write(audit/'mount-metadata.json',{'source_root':str(src),'source_commit':subprocess.check_output(['git','-C',str(src),'rev-parse','HEAD'],text=True).strip(),'status':'CANDIDATE; awaiting output validation; runtime NOT RUN','rigs':metadata,'counts':counts,'triangle_total':sum(counts.values()),'parts':parts,'meshpoints':points,'frames':{k:{'basis':B.tolist(),'origin':origin.tolist()} for k,(B,origin) in frames.items()},'input_checks':inputchecks})
if args.compile:
 env=dict(os.environ,OMP_NUM_THREADS='4',MANGOHUD='0',WINEDEBUG='-all',DISPLAY='',WINEDLLOVERRIDES='mscoree,mshtml=')
 if args.wine:
  pref=build/'proton-prefix'
  if not pref.exists():shutil.copytree(ROOT/'build/worker-b/proton-prefix',pref,symlinks=True)
  env['WINEPREFIX']=str(pref)
 for kind in groups:
  name='expanse_polish_'+kind
  for fmt in ['json','binary']:
   dest=build/('compiler-'+fmt);dest.mkdir(exist_ok=True);wp=lambda p:'Z:'+str(p) if args.wine else str(p);cmd=([str(args.wine)] if args.wine else [])+[str(args.sdk/'MeshBuilder/bin/MeshBuilder.exe'),'--input_path='+wp(out/(name+'.gltf')),'--output_folder_path='+wp(dest),'--mesh_output_format='+fmt,'--fill_triangle_facing_grid']
   with (build/(name+'-'+fmt+'.log')).open('w') as log:subprocess.run(cmd,env=env,stdout=log,stderr=subprocess.STDOUT,check=True,timeout=300)
  print('compiled',kind,flush=True)
print(counts)
