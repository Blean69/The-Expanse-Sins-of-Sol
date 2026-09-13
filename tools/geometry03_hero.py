"""Audit supplied hero, preserve archive/master, make stand-free editable/static derivative."""
from common import *
import copy,hashlib,ctypes as c,subprocess
from scipy.spatial.transform import Rotation,Slerp
from PIL import Image
source=Path('/run/media/haker/NVME 2/expanse-mod');root=ROOT/'assets/derived/geometry03-b';master=root/'hero-master';original=root/'hero-original/Rocinante_(The_Expanse).zip';out=root/'hero';out.mkdir(exist_ok=True);audit=ROOT/'audit/geometry03-b';a=Gltf(master/'Rocinante_(The_Expanse).gltf');g=a.g;an=g['animations'][0];tracks={};trackrecords=[]
for ch in an['channels']:
 ss=an['samplers'][ch['sampler']];times=a.accessor(ss['input']).flatten();values=a.accessor(ss['output']);tracks.setdefault(ch['target']['node'],{})[ch['target']['path']]=(times,values)
 trackrecords.append({'node':ch['target']['node'],'name':g['nodes'][ch['target']['node']]['name'],'path':ch['target']['path'],'keys':len(times),'time_min':float(times.min()),'time_max':float(times.max())})
def local(ni,time):
 n=g['nodes'][ni];vals={k:copy.deepcopy(v) for k,v in n.items() if k in ['rotation','translation','scale']}
 for path,(ts,vs) in tracks.get(ni,{}).items():
  if path=='rotation':value=Slerp(ts,Rotation.from_quat(vs))([min(max(time,float(ts[0])),float(ts[-1]))]).as_quat()[0]
  else:value=np.array([np.interp(time,ts,vs[:,i]) for i in range(vs.shape[1])])
  vals[path]=value
 if 'matrix' in n and not tracks.get(ni):return np.array(n['matrix']).reshape(4,4).T
 M=np.eye(4);M[:3,:3]=Rotation.from_quat(vals.get('rotation',[0,0,0,1])).as_matrix()@np.diag(vals.get('scale',[1,1,1]));M[:3,3]=vals.get('translation',[0,0,0]);return M
end=16.625;rootM=a.world[1];ref0=rootM@local(2,0);refend=rootM@local(2,end);remove_global=ref0@np.linalg.inv(refend);world={}
def walk(ni,parent):
 M=parent@local(ni,end);world[ni]=M
 for child in g['nodes'][ni].get('children',[]):walk(child,M)
for ni in g['scenes'][g.get('scene',0)]['nodes']:walk(ni,np.eye(4))
world={ni:remove_global@M for ni,M in world.items()};stand={65,66,67,68};sourceparts=[];tris_before=0;tris_removed=0
for ni,n in enumerate(g['nodes']):
 if 'mesh' not in n:continue
 tris=sum(a.accessor(p['indices']).size//3 for p in g['meshes'][n['mesh']]['primitives']);tris_before+=tris
 if ni in stand:tris_removed+=tris
 sourceparts.append({'node':ni,'name':n['name'],'parent_name':g['nodes'][a.parents[ni]]['name'],'triangles':tris,'stand_removed':ni in stand})
# Preserve animation intact except channels targeting excluded stand nodes.
editable=copy.deepcopy(g);editable['nodes'][1]['children']=[i for i in editable['nodes'][1]['children'] if i not in stand]
for ni in stand:editable['nodes'][ni].pop('mesh',None)
for aa in editable['animations']:aa['channels']=[ch for ch in aa['channels'] if ch['target']['node'] not in stand]
for buffer in editable['buffers']:buffer['uri']=str(master/buffer['uri'])
write(out/'rocinante_stand_free_animated.gltf',editable)
# Analyze relative motion independent of baked global presentation transform.
motion=[]
for ni in [111,114,117,133,140,147,174,196,212,234,250,272,288,310,326,348]:
 base_rel=np.linalg.inv(local(2,0))@local(ni,0);delta=np.linalg.inv(local(2,end))@local(ni,end)@np.linalg.inv(base_rel);motion.append({'node':ni,'name':g['nodes'][ni]['name'],'relative_translation':delta[:3,3].tolist(),'relative_rotation_degrees':float(Rotation.from_matrix(delta[:3,:3]).magnitude()*180/np.pi)})
# Separate optimized topology, per source primitive, using existing pinned library.
libpath=Path('/run/media/haker/NVME 2/expanse-mod/.tools/libmeshoptimizer.so');assert libpath.is_file();lib=c.CDLL(str(libpath));u=c.POINTER(c.c_uint);f=c.POINTER(c.c_float);fn=lib.meshopt_simplifyWithAttributes;fn.argtypes=[u,u,c.c_size_t,f,c.c_size_t,c.c_size_t,f,c.c_size_t,f,c.c_size_t,c.POINTER(c.c_ubyte),c.c_size_t,c.c_float,c.c_uint,f];fn.restype=c.c_size_t
parts=[];allv=[];optimization=[]
for ni,n in enumerate(g['nodes']):
 if 'mesh' not in n or ni in stand:continue
 M=world[ni]
 for pi,p in enumerate(g['meshes'][n['mesh']]['primitives']):
  pos=np.ascontiguousarray(a.accessor(p['attributes']['POSITION']),dtype='float32');normal=np.ascontiguousarray(a.accessor(p['attributes']['NORMAL']),dtype='float32');idx=np.ascontiguousarray(a.accessor(p['indices']).flatten(),dtype='uint32');dst=np.zeros_like(idx);weights=np.array([.1,.1,.1],dtype='float32');err=c.c_float();target=max(12,len(idx)//60*3);nn=fn(dst.ctypes.data_as(u),idx.ctypes.data_as(u),len(idx),pos.ctypes.data_as(f),len(pos),12,normal.ctypes.data_as(f),12,weights.ctypes.data_as(f),3,None,target,.04,32,c.byref(err));assert nn>0 and nn%3==0;ii=dst[:nn].reshape(-1,3);used=np.unique(ii);wp=pos@M[:3,:3].T+M[:3,3];wn=normal@np.linalg.inv(M[:3,:3]);wn/=np.linalg.norm(wn,axis=1)[:,None];allv.append(wp[used]);parts.append((ni,p['material'],wp,wn,ii));optimization.append({'node':ni,'name':n['name'],'parent_name':g['nodes'][a.parents[ni]]['name'],'input_triangles':len(idx)//3,'output_triangles':nn//3,'simplifier_error':float(err.value)})
# Source nose is +X (s1), engine -X (s3); source +Y maps to game +Y.
cloud=np.concatenate(allv);_,_,basis=np.linalg.svd(cloud-cloud.mean(0),full_matrices=False);forward=basis[0];forward=forward if forward[0]>0 else -forward;up=np.array([0.,1.,0.]);up-=forward*np.dot(up,forward);up/=np.linalg.norm(up);right=np.cross(up,forward);C=np.stack([right,up,forward]);v=cloud@C.T;mi=v.min(0);ma=v.max(0);center=(mi+ma)/2;stock=read('/run/media/haker/NVME 2/SteamLibrary/steamapps/common/Sins2/entities/trader_light_frigate.unit');targetcenter=np.array(stock['spatial']['box']['center']);targetext=np.array(stock['spatial']['box']['extents']);scale=.95*min(2*targetext/(ma-mi));# separate normalized source transform; do not alter gameplay extents
buf=bytearray();name='expanse03_hero_static';cg={'asset':{'version':'2.0','generator':'Static deployed Rocinante derivative; source attribution pending exact metadata'},'scene':0,'scenes':[{'nodes':[0]}],'nodes':[{'name':name,'mesh':0,'children':[]}],'meshes':[{'name':name,'primitives':[]}],'buffers':[],'bufferViews':[],'accessors':[],'materials':[]};sourceframes={};total=0
# Use observed baseline attachment names as placeholders; hero effect positions need main review.
points=[{'name':'center','translation':targetcenter.tolist()},{'name':'exhaust.0','translation':[0,targetcenter[1],float((mi[2]-center[2])*scale+targetcenter[2])],'rotation':[0,1,0,0]},{'name':'above','translation':[0,float(targetcenter[1]+20),targetcenter[2]]},{'name':'aura','translation':[0,float(targetcenter[1]-22),targetcenter[2]]}]
def acc(v,typ,ct=5126):
 v=np.asarray(v,dtype='<f4' if ct==5126 else '<u4');buf.extend(b'\0'*((-len(buf))%4));start=len(buf);buf.extend(v.tobytes());cg['bufferViews'].append({'buffer':0,'byteOffset':start,'byteLength':v.nbytes});at={'bufferView':len(cg['bufferViews'])-1,'componentType':ct,'count':len(v),'type':typ}
 if typ=='VEC3':at.update(min=v.min(0).tolist(),max=v.max(0).tolist())
 cg['accessors'].append(at);return len(cg['accessors'])-1
materialspec=[]
for mat_i,mat in enumerate(g['materials']):
 vv=[];nn=[];ii=[];offset=0
 for ni,mm,pos,norm,idx in parts:
  if mm!=mat_i:continue
  used,remap=np.unique(idx,return_inverse=True);pos=((pos[used]@C.T)-center)*scale+targetcenter;norm=norm[used]@C.T;idx=remap.reshape(-1,3);q=pos[idx];dot=np.sum(np.cross(q[:,1]-q[:,0],q[:,2]-q[:,0])*norm[idx].mean(1),axis=1);idx[dot<0]=idx[dot<0][:,[0,2,1]];vv.append(pos);nn.append(norm);ii.append(idx.flatten()+offset);offset+=len(pos)
 if not vv:continue
 pos=np.concatenate(vv);norm=np.concatenate(nn);idx=np.concatenate(ii);total+=len(idx)//3;axis=np.eye(3)[np.argmin(abs(norm),axis=1)];t=axis-norm*np.sum(axis*norm,axis=1)[:,None];t/=np.linalg.norm(t,axis=1)[:,None];tang=np.column_stack([t,np.ones(len(t))]);uv=np.zeros((len(pos),2));sourceframes[str(mat_i)]={'positions':pos.tolist(),'normals':norm.tolist(),'tangents':tang.tolist(),'uv':uv.tolist()}
 for ar in [pos,norm,tang]:ar[:,2]*=-1
 tang[:,3]*=-1;matname=f'expanse03_hero_mat_{mat_i}';cg['materials'].append({'name':matname,'pbrMetallicRoughness':{'baseColorFactor':[1,1,1,1],'metallicFactor':1,'roughnessFactor':1}});cg['meshes'][0]['primitives'].append({'attributes':{'POSITION':acc(pos,'VEC3'),'NORMAL':acc(norm,'VEC3'),'TANGENT':acc(tang,'VEC4'),'TEXCOORD_0':acc(uv,'VEC2')},'indices':acc(idx,'SCALAR',5125),'material':mat_i,'mode':4})
 pbr=mat['pbrMetallicRoughness'];linear=np.array(pbr['baseColorFactor'][:3]);srgb=np.where(linear<=.0031308,linear*12.92,1.055*linear**(1/2.4)-.055);rgb=np.clip(np.rint(srgb*255),0,255).astype(int).tolist();texdir=out/'texture-sources';texdir.mkdir(exist_ok=True)
 for suffix,color in [('clr',(*rgb,255)),('orm',(255,round(pbr.get('roughnessFactor',1)*255),round(pbr.get('metallicFactor',1)*255),255)),('nrm',(128,128,255,255)),('msk',(0,0,0,0))]:Image.new('RGBA',(4,4),color).save(texdir/(matname+'_'+suffix+'.png'))
 material={'version':1,'base_color_texture':matname+'_clr','occlusion_roughness_metallic_texture':matname+'_orm','normal_texture':matname+'_nrm','mask_texture':matname+'_msk','emissive_factor':0.0};write(out/'materials'/(matname+'.mesh_material'),material);materialspec.append({'name':matname,'original':mat,'srgb_texture_color':rgb,'material_file':str(out/'materials'/(matname+'.mesh_material'))})
for p in points:
 pp=copy.deepcopy(p);pp['translation'][2]*=-1;cg['nodes'][0]['children'].append(len(cg['nodes']));cg['nodes'].append(pp)
cg['buffers']=[{'uri':name+'.bin','byteLength':len(buf)}];(out/(name+'.bin')).write_bytes(buf);write(out/(name+'.gltf'),cg);write(out/'retained-source-frames.json',{'hero_static':sourceframes});write(audit/'hero-mount-metadata.json',{'source_root':str(source),'status':'STATIC DEPLOYED HERO VISUAL CANDIDATE; no weapon mounts or deployment integration','counts':{'hero_static':total},'triangle_total':total,'frames':{'hero_static':{'basis':np.eye(3).tolist(),'origin':[0,0,0]}},'rigs':[],'meshpoints':{'hero_static':points},'materialspec':materialspec,'normalization':{'scale':scale,'source_to_game_rotation':C.tolist(),'source_rotated_center':center.tolist(),'target_center':targetcenter.tolist()}})
# Keep a high-resolution static deployed editable pose with global presentation removed.
deployed=copy.deepcopy(editable);deployed.pop('animations',None);deployed['nodes']=[];deployed['scenes']=[{'nodes':[]}];deployed['scene']=0
for ni,n in enumerate(g['nodes']):
 if 'mesh' not in n or ni in stand:continue
 node={'name':n['name'],'mesh':n['mesh'],'matrix':world[ni].T.flatten().tolist()};deployed['scenes'][0]['nodes'].append(len(deployed['nodes']));deployed['nodes'].append(node)
write(out/'rocinante_stand_free_deployed.gltf',deployed)
record={'permission':'User states permission granted to use this asset; creator/source URL/exact license terms not supplied','archive_sha256':hashlib.sha256(original.read_bytes()).hexdigest(),'master_files':{str(p):hashlib.sha256(p.read_bytes()).hexdigest() for p in master.iterdir()},'source_triangles':tris_before,'stand_removed_triangles':tris_removed,'stand_free_triangles':tris_before-tris_removed,'stand_nodes':sorted(stand),'source_mesh_nodes':163,'remaining_mesh_nodes':161,'optimized_static_triangles':total,'source_materials':g['materials'],'texture_images':0,'UV_sets':0,'background_jpeg':'Archive background.jpeg is not referenced by glTF model','animations':{'count':1,'name':an['name'],'channel_count':len(an['channels']),'duration_seconds':end,'relative_PDC_motion':motion,'interpretation':'Includes global presentation movement and real PDC covering/housing/cannon relative movement. Engine deployment integration NOT IMPLEMENTED.'},'optimization':{'library':str(libpath),'library_sha256':hashlib.sha256(libpath.read_bytes()).hexdigest(),'pinned_source_commit':'bba256eaa24039b6f93c773063ff7c20143ae0db','target_ratio':1/20,'error_limit':.04,'records':optimization},'parts':sourceparts,'animation_tracks':trackrecords,'runtime':'NOT RUN'};write(audit/'hero-asset-audit.json',record);print(json.dumps({'original':tris_before,'stand_removed':tris_removed,'stand_free':tris_before-tris_removed,'optimized_static':total,'remaining_parts':161,'actual_animation_channels':len(an['channels'])}))
