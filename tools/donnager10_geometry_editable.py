from donnager10_geometry_common import *
import copy
from scipy.spatial.transform import Rotation
m=read(AUDIT/'mount-metadata.json');ss=read(OUT/'retained-source-frames.json');g={'asset':{'version':'2.0','generator':'Donnager10 editable assembled game-space scene, no compiler Z reflection'},'scene':0,'scenes':[{'nodes':[]}],'nodes':[],'meshes':[],'buffers':[],'bufferViews':[],'accessors':[],'materials':copy.deepcopy(a.g['materials']),'images':[],'textures':[]};donor=Path('/run/media/haker/NVME 2/expanse-mod/assets/derived/baseline');dg=read(donor/'mcrn_editable.gltf')
for image in a.g['images']:g['images'].append({'uri':os.path.relpath(SRC/image['uri'],OUT)})
for image in dg['images'][:3]:g['images'].append({'uri':os.path.relpath(donor/image['uri'],OUT)})
g['textures']=[{'source':i} for i in range(len(g['images']))];dm=copy.deepcopy(dg['materials'][0]);dm['pbrMetallicRoughness']['baseColorTexture']['index']=2;dm['pbrMetallicRoughness']['metallicRoughnessTexture']['index']=3;dm['normalTexture']['index']=4;dm['occlusionTexture']['index']=3;g['materials'].append(dm);buf=bytearray();meshids={}
def acc(value,typ,ct=5126):
 value=np.asarray(value,dtype='<f4' if ct==5126 else '<u4');buf.extend(b'\0'*((-len(buf))%4));off=len(buf);buf.extend(value.tobytes());g['bufferViews'].append({'buffer':0,'byteOffset':off,'byteLength':value.nbytes});at={'bufferView':len(g['bufferViews'])-1,'componentType':ct,'count':len(value),'type':typ}
 if typ=='VEC3':at.update(min=value.min(0).tolist(),max=value.max(0).tolist())
 g['accessors'].append(at);return len(g['accessors'])-1
for kind,parts in ss.items():
 mesh={'name':kind,'primitives':[]};inp=read(OUT/('expanse10_'+kind+'.gltf'));aa=Gltf(OUT/('expanse10_'+kind+'.gltf'))
 for mi,part in parts.items():
  mi=int(mi);name=inp['materials'][mi]['name'];mat=11 if name=='mcrn_tachi_material' else int(name.rsplit('_',1)[1]);idx=aa.accessor(inp['meshes'][0]['primitives'][mi]['indices']).flatten().reshape(-1,3);v=np.array(part['positions']);n=np.array(part['normals']);cross=np.cross(v[idx[:,1]]-v[idx[:,0]],v[idx[:,2]]-v[idx[:,0]]);flip=np.sum(cross*n[idx].mean(1),axis=1)<0;idx[flip]=idx[flip][:,[0,2,1]];mesh['primitives'].append({'material':mat,'mode':4,'indices':acc(idx.flatten(),'SCALAR',5125),'attributes':{'POSITION':acc(v,'VEC3'),'NORMAL':acc(n,'VEC3'),'TANGENT':acc(part['tangents'],'VEC4'),'TEXCOORD_0':acc(part['uv'],'VEC2')}})
 meshids[kind]=len(g['meshes']);g['meshes'].append(mesh)
def node(kind,p,B=np.eye(3),name=None):
 g['scenes'][0]['nodes'].append(len(g['nodes']));g['nodes'].append({'name':name or kind,'mesh':meshids[kind],'translation':list(p),'rotation':Rotation.from_matrix(B).as_quat().tolist()})
node('donnager_hull',[0,0,0])
for r in m['rigs']:
 if r['kind']=='rail':node('donnager_rail_'+str(r['index']-16),r['yaw_pivot_hull'])
 else:
  B=np.array(r['basis_columns']);node('donnager_pdc_base',r['yaw_pivot_hull'],B,'PDC '+str(r['index'])+' yaw');node('donnager_pdc_barrel',r['pitch_pivot_hull'],B,'PDC '+str(r['index'])+' pitch')
g['buffers']=[{'uri':'donnager10_editable.bin','byteLength':len(buf)}];(OUT/'donnager10_editable.bin').write_bytes(buf);write(OUT/'donnager10_editable.gltf',g);write(AUDIT/'editable-contract.json',{'path':str(OUT/'donnager10_editable.gltf'),'active_nodes':len(g['nodes']),'unique_meshes':len(g['meshes']),'triangles':m['assembled_triangle_total'],'compiler_z_reflected':False,'coordinate_convention':'+Z bow,+Y up; centered actual source scaled uniformly475.5/46Tachi reference','source_image_dependencies':[str((OUT/i['uri']).resolve()) for i in g['images']]});print('Editable',len(g['nodes']),'nodes',m['assembled_triangle_total'],'triangles')
