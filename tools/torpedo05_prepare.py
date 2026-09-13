"""Compile preparation from C's isolated1600-triangle torpedo; sources read-only."""
from common import *
from PIL import Image
import copy,hashlib
src=Path('/run/media/haker/NVME 2/expanse-workers/validation/assets/derived/amun05-c/torpedo-editable');a=Gltf(src/'amun05_torpedo.gltf');out=ROOT/'assets/derived/torpedo05-b';audit=ROOT/'audit/torpedo05-b';out.mkdir(exist_ok=True);audit.mkdir(exist_ok=True);tex=out/'texture-sources';tex.mkdir(exist_ok=True);arrays={k:[] for k in ['POSITION','NORMAL','TANGENT','TEXCOORD_0']};idxs=[];offset=0
for ni,n in enumerate(a.g['nodes']):
 if 'mesh' not in n:continue
 M=a.world[ni]
 for p in a.g['meshes'][n['mesh']]['primitives']:
  ii=a.accessor(p['indices']).flatten();used,remap=np.unique(ii,return_inverse=True);pos=a.positions(ni,p)[used];no=a.accessor(p['attributes']['NORMAL'])[used]@np.linalg.inv(M[:3,:3]);no/=np.linalg.norm(no,axis=1)[:,None];ta=a.accessor(p['attributes']['TANGENT'])[used];ta[:,:3]=ta[:,:3]@M[:3,:3].T;ta[:,:3]/=np.linalg.norm(ta[:,:3],axis=1)[:,None];uv=a.accessor(p['attributes']['TEXCOORD_0'])[used]
  for key,val in [('POSITION',pos),('NORMAL',no),('TANGENT',ta),('TEXCOORD_0',uv)]:arrays[key].append(val)
  idxs.extend(remap+offset);offset+=len(pos)
arrays={k:np.concatenate(v) for k,v in arrays.items()};idx=np.array(idxs,dtype=np.uint32);assert len(idx)//3==1600;v=arrays['POSITION'];lo=v.min(0);hi=v.max(0);mid=(lo+hi)/2;aft=v[v[:,2]<lo[2]+.01];exhaust=[float((aft[:,0].min()+aft[:,0].max())/2),float((aft[:,1].min()+aft[:,1].max())/2),float(lo[2]-.03)];points=[{'name':'center','translation':mid.tolist()},{'name':'above','translation':[float(mid[0]),float(hi[1]+.1),float(mid[2])]},{'name':'aura','translation':[float(mid[0]),float(lo[1]-.1),float(mid[2])]},{'name':'exhaust.0','translation':exhaust,'rotation':[0,1,0,0]}]
name='expanse05_amun_torpedo';matname='expanse05_amun_torpedo_surface';g={'asset':{'version':'2.0','generator':'1600tri private torpedo compiler input; explicit Z compensation'},'scene':0,'scenes':[{'nodes':[0]}],'nodes':[{'name':name,'mesh':0,'children':[]}],'meshes':[{'name':name,'primitives':[]}],'buffers':[],'bufferViews':[],'accessors':[],'materials':[{'name':matname,'pbrMetallicRoughness':{'baseColorFactor':[1,1,1,1],'metallicFactor':1,'roughnessFactor':1}}]};buf=bytearray();retained={'positions':arrays['POSITION'].tolist(),'normals':arrays['NORMAL'].tolist(),'tangents':arrays['TANGENT'].tolist(),'uv':arrays['TEXCOORD_0'].tolist()}
def acc(v,typ,ct=5126):
 v=np.asarray(v,dtype='<f4' if ct==5126 else '<u4');buf.extend(b'\0'*((-len(buf))%4));start=len(buf);buf.extend(v.tobytes());g['bufferViews'].append({'buffer':0,'byteOffset':start,'byteLength':v.nbytes});at={'bufferView':len(g['bufferViews'])-1,'componentType':ct,'count':len(v),'type':typ}
 if typ=='VEC3':at.update(min=v.min(0).tolist(),max=v.max(0).tolist())
 g['accessors'].append(at);return len(g['accessors'])-1
for key in ['POSITION','NORMAL','TANGENT']:arrays[key][:,2]*=-1
arrays['TANGENT'][:,3]*=-1;g['meshes'][0]['primitives']=[{'attributes':{k:acc(ar,'VEC4' if k=='TANGENT' else 'VEC2' if k=='TEXCOORD_0' else 'VEC3') for k,ar in arrays.items()},'indices':acc(idx,'SCALAR',5125),'material':0,'mode':4}]
for point in points:
 q=copy.deepcopy(point);q['translation'][2]*=-1
 if 'rotation' in q:q['rotation'][0]*=-1;q['rotation'][1]*=-1
 g['nodes'][0]['children'].append(len(g['nodes']));g['nodes'].append(q)
g['buffers']=[{'uri':name+'.bin','byteLength':len(buf)}];(out/(name+'.bin')).write_bytes(buf);write(out/(name+'.gltf'),g);write(out/'retained-source-frames.json',{'amun_torpedo':{'0':retained}})
# Referenced glTF semantics: G roughness/B metallic, no AO texture; sourceR is0
# and must not become black occlusion. Emissive mask uses observed shaderB.
mat=a.g['materials'][0];pbr=mat['pbrMetallicRoughness']
def img(texture):
 uri=a.g['images'][a.g['textures'][texture]['source']]['uri'];return Image.open(src/uri).convert('RGBA').resize((1024,1024),Image.Resampling.LANCZOS)
clr=img(pbr['baseColorTexture']['index']);clr.save(tex/(matname+'_clr.png'));orm=np.array(img(pbr['metallicRoughnessTexture']['index']));orm[:,:,0]=255;orm[:,:,3]=255;Image.fromarray(orm).save(tex/(matname+'_orm.png'));normal=np.array(img(mat['normalTexture']['index'])).astype(float)[:,:,:3]/127.5-1;normal/=np.maximum(np.linalg.norm(normal,axis=2,keepdims=True),1e-10);Image.fromarray(np.clip(np.rint((normal+1)*127.5),0,255).astype('uint8')).save(tex/(matname+'_nrm.png'));em=np.array(img(mat['emissiveTexture']['index']));mask=np.zeros_like(em);mask[:,:,2]=em[:,:,:3].max(2);Image.fromarray(mask).save(tex/(matname+'_msk.png'));material={'version':1,'base_color_texture':matname+'_clr','occlusion_roughness_metallic_texture':matname+'_orm','normal_texture':matname+'_nrm','mask_texture':matname+'_msk','emissive_factor':1.0};write(out/'materials'/(matname+'.mesh_material'),material)
sourcehashes={str(p):hashlib.sha256(p.read_bytes()).hexdigest() for p in src.rglob('*') if p.is_file()};write(audit/'mount-metadata.json',{'status':'COMPILER CHECKS PENDING','source_hashes':sourcehashes,'source_scene':str(src/'amun05_torpedo.gltf'),'frames':{'amun_torpedo':{'basis':np.eye(3).tolist(),'origin':[0,0,0]}},'rigs':[],'meshpoints':{'amun_torpedo':points},'counts':{'amun_torpedo':1600},'triangle_total':1600,'exhaust_geometry':{'position':exhaust,'up':[0,1,0],'forward':[0,0,-1],'source':'Full actual aft-most body slice0.01 gameunits; center of XY bounds;0.03 outward clearance'},'bounds':{'min':lo.tolist(),'max':hi.tolist(),'dimensions':(hi-lo).tolist(),'vertex_radius':float(np.linalg.norm(v,axis=1).max())},'material_source':str(out/'materials'/(matname+'.mesh_material')),'texture_conversion':{'dimensions':[1024,1024],'source_dimensions':[4096,4096],'ORM':'R=255 because no AO texture;G/B copied from glTF metallicRoughness','MSK':'R/G/A0;B=max source emissiveRGB; game emissive uses base-color tint','normal':'Referenced glTF normal preserved; source filename DirectX conflicts with glTF naming expectation; no unverified green-channel inversion. Inspect bumps in game.'},'gameplay_changes':[]});print('Prepared1600tri torpedo, four1K maps, four stock-observed meshpoint names')
