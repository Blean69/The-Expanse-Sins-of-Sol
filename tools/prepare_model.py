"""Create an editable normalized glTF and a separate flattened compiler input.

The input is a separate optimized derivative. Source assets stay unchanged.
"""
from common import *
from PIL import Image
import copy, shutil

src=ROOT/'assets/derived/optimized-source';out=ROOT/'assets/derived/baseline';out.mkdir(parents=True,exist_ok=True)
a=Gltf(src/'scene.gltf');g=a.g;aud=read(ROOT/'audit/asset-audit.json');unit=read(GAME/'entities/trader_light_frigate.unit')
mins=np.array(aud['bounds_min']);maxs=np.array(aud['bounds_max']);origin=(mins+maxs)/2
scale=.95*min(2*np.array(unit['spatial']['box']['extents'])/(maxs-mins))
center=np.array(unit['spatial']['box']['center']);transform=np.eye(4);transform[:3,:3]*=scale;transform[:3,3]=center-scale*origin

# Editable derivative keeps all 714 source nodes and individually named parts.
editable=copy.deepcopy(g);editable['nodes'].append({'name':'MCRN_Cobalt_fit','matrix':transform.T.flatten().tolist(),'children':editable['scenes'][0]['nodes']});editable['scenes'][0]['nodes']=[len(editable['nodes'])-1]
shutil.copy2(src/'scene.bin',out/'scene.bin');shutil.copytree(src/'textures',out/'textures',dirs_exist_ok=True)
write(out/'mcrn_editable.gltf',editable)

# Compiler geometry: bake world matrices and combine by material ONLY here.
binary=bytearray();cg={'asset':{'version':'2.0','generator':'Expanse baseline preparation; source credit in ASSET-SOURCES.md'},'scene':0,'scenes':[{'nodes':[0]}],'nodes':[{'name':'mcrn_corvette_baseline','mesh':0,'children':[]}],'meshes':[{'name':'mcrn_corvette_baseline','primitives':[]}],'buffers':[],'bufferViews':[],'accessors':[],'materials':[]}
def access(v,kind,component=5126):
    v=np.asarray(v,dtype='<f4' if component==5126 else '<u4');binary.extend(b'\0'*((-len(binary))%4));off=len(binary);binary.extend(v.tobytes());vi=len(cg['bufferViews']);cg['bufferViews'].append({'buffer':0,'byteOffset':off,'byteLength':v.nbytes}); ac={'bufferView':vi,'componentType':component,'count':len(v),'type':kind}
    if kind=='VEC3':ac.update(min=v.min(0).tolist(),max=v.max(0).tolist())
    cg['accessors'].append(ac);return len(cg['accessors'])-1

for mi,mat in enumerate(g['materials']):
    arrays={k:[] for k in ['POSITION','NORMAL','TANGENT','TEXCOORD_0']};indices=[];count=0
    for i,n in enumerate(g['nodes']):
        if 'mesh' not in n or i not in a.world:continue
        for p in g['meshes'][n['mesh']]['primitives']:
            if p['material']!=mi:continue
            assert p.get('mode',4)==4
            m=transform@a.world[i];v=a.accessor(p['attributes']['POSITION']);v=v@m[:3,:3].T+m[:3,3];arrays['POSITION'].append(v)
            normals=a.accessor(p['attributes']['NORMAL'])@np.linalg.inv(m[:3,:3]);normals/=np.linalg.norm(normals,axis=1)[:,None];arrays['NORMAL'].append(normals)
            if 'TANGENT' in p['attributes']:
                tang=a.accessor(p['attributes']['TANGENT']);tang[:,:3]=tang[:,:3]@m[:3,:3].T;tang[:,:3]/=np.linalg.norm(tang[:,:3],axis=1)[:,None]
            else:
                # Only six planar text quads lack tangents; they use flat normal maps.
                uv=a.accessor(p['attributes']['TEXCOORD_0']);tri=a.accessor(p['indices']).flatten()[:3];i0,i1,i2=tri;e1=v[i1]-v[i0];e2=v[i2]-v[i0];d1=uv[i1]-uv[i0];d2=uv[i2]-uv[i0];den=d1[0]*d2[1]-d1[1]*d2[0];t=(e1*d2[1]-e2*d1[1])/den;t/=np.linalg.norm(t);bt=(e2*d1[0]-e1*d2[0])/den;sign=1 if np.dot(np.cross(normals[i0],t),bt)>0 else -1;tang=np.tile([*t,sign],(len(v),1))
            idx=a.accessor(p['indices']).flatten()
            if np.linalg.det(m[:3,:3])<0:idx=idx.reshape(-1,3)[:,[0,2,1]].flatten();tang[:,3]*=-1
            arrays['TANGENT'].append(tang);arrays['TEXCOORD_0'].append(a.accessor(p['attributes']['TEXCOORD_0']));indices.append(idx+count);count+=len(v)
    name='mcrn_tachi_'+mat['name'].lower();cg['materials'].append({'name':name,'pbrMetallicRoughness':{'baseColorFactor':[1,1,1,1],'metallicFactor':1,'roughnessFactor':1}})
    # MeshBuilder's glTF importer reflects Z. Compensate in compiler input only,
    # including handedness/winding, so the actual mesh faces game +Z.
    for key in ['POSITION','NORMAL','TANGENT']:
        for values in arrays[key]: values[:,2]*=-1
    for values in arrays['TANGENT']:values[:,3]*=-1
    indices=[v.reshape(-1,3)[:,[0,2,1]].flatten() for v in indices]
    cg['meshes'][0]['primitives'].append({'attributes':{k:access(np.concatenate(v),{'POSITION':'VEC3','NORMAL':'VEC3','TANGENT':'VEC4','TEXCOORD_0':'VEC2'}[k]) for k,v in arrays.items()},'indices':access(np.concatenate(indices),'SCALAR',5125),'material':mi,'mode':4})
    # Build 2K source maps. Source ORM is already packed R=AO/G=rough/B=metal.
    tex=out/'game-textures';tex.mkdir(exist_ok=True);pbr=mat['pbrMetallicRoughness']
    def source_image(index):return Image.open(src/g['images'][g['textures'][index]['source']]['uri'])
    clr=source_image(pbr['baseColorTexture']['index']).convert('RGBA').resize((2048,2048),Image.Resampling.LANCZOS)
    clr.save(tex/(name+'_clr.png'))
    if 'metallicRoughnessTexture' in pbr:
        orm=source_image(pbr['metallicRoughnessTexture']['index']).convert('RGB').resize((2048,2048),Image.Resampling.LANCZOS);v=np.array(orm);v[:,:,1]=(v[:,:,1].astype(float)*pbr.get('roughnessFactor',1)).astype('uint8');orm=Image.fromarray(v)
    else:orm=Image.new('RGB',(4,4),(255,round(255*pbr.get('roughnessFactor',1)),round(255*pbr.get('metallicFactor',1))))
    orm.save(tex/(name+'_orm.png'))
    if 'normalTexture' in mat:
        normal=source_image(mat['normalTexture']['index']).convert('RGB').resize((2048,2048),Image.Resampling.LANCZOS)
        v=np.array(normal).astype(float)/127.5-1;v/=np.maximum(np.linalg.norm(v,axis=2,keepdims=True),1e-10);normal=Image.fromarray(np.clip((v+1)*127.5,0,255).astype('uint8'))
    else:normal=Image.new('RGB',(4,4),(128,128,255))
    normal.save(tex/(name+'_nrm.png'));Image.new('RGBA',(4,4),(0,0,0,0)).save(tex/(name+'_msk.png'))
    material={'version':1,'base_color_texture':name+'_clr','occlusion_roughness_metallic_texture':name+'_orm','normal_texture':name+'_nrm','mask_texture':name+'_msk','emissive_factor':1.0}
    write(out/'game-materials'/(name+'.mesh_material'),material)

# Attachment points: map forward-facing front PDC barrel tips, for fixed-gun
# baseline ONLY. These are geometric estimates, not verified turret mounts.
muzzles=[]
for ni in [631,679]:
    p=g['meshes'][g['nodes'][ni]['mesh']]['primitives'][0];v=a.positions(ni,p);tip=v[v[:,2]>v[:,2].max()-.1].mean(0);muzzles.append((tip*scale+transform[:3,3]).tolist())
points=[{'name':'weapon.0','translation':v} for v in muzzles]
points.extend([{'name':'exhaust.0','translation':[float(center[0]),float(center[1]),float((mins[2]-origin[2])*scale+center[2])],'rotation':[0,1,0,0]},{'name':'center','translation':center.tolist()},{'name':'above','translation':[0,float(center[1]+20),float(center[2])]},{'name':'aura','translation':[0,float(center[1]-22),float(center[2])]}])
for point in points:
    cg['nodes'][0]['children'].append(len(cg['nodes']));cp=copy.deepcopy(point);cp['translation'][2]*=-1;cg['nodes'].append(cp)
cg['buffers']=[{'uri':'mcrn_corvette_baseline.bin','byteLength':len(binary)}];(out/'mcrn_corvette_baseline.bin').write_bytes(binary);write(out/'mcrn_corvette_baseline.gltf',cg)
write(ROOT/'audit/derivative-transform.json',dict(scale=scale,source_center=origin.tolist(),destination_center=center.tolist(),matrix=transform.T.flatten().tolist(),muzzles=muzzles,meshpoints=points,triangles=read(ROOT/'audit/optimization.json')['output_triangles'],notes=['Source forward inferred +Z from named front hull and engine geometry.','Compiler input reflects Z to compensate for observed MeshBuilder handedness conversion.','All six PDC assemblies retained in supplied pose; no deployment animation added.','Muzzles estimated from front two barrel end vertices; confirm visually in SolarForge.','Simplified baseline; not certified for fleet performance.']))
print('Prepared editable and compiler glTF; uniform scale',scale,'muzzles',muzzles)
