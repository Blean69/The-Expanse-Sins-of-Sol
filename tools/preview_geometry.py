"""Offline geometry QA: orthographic silhouettes and shaded comparison.
This is a CPU diagnostic render, not a screenshot of the game.
"""
from common import *
from PIL import Image, ImageDraw

def geometry(path):
    a=Gltf(path);vertices=[];colors=[]
    for i,n in enumerate(a.g['nodes']):
        if 'mesh' not in n:continue
        for p in a.g['meshes'][n['mesh']]['primitives']:
            v=a.positions(i,p);idx=a.accessor(p['indices']).reshape(-1,3);tri=v[idx];vertices.append(tri)
            mat=a.g['materials'][p['material']];ti=mat['pbrMetallicRoughness']['baseColorTexture']['index'];uri=a.g['images'][a.g['textures'][ti]['source']]['uri'];tex=np.array(Image.open(a.path.parent/uri).convert('RGBA'));uv=a.accessor(p['attributes']['TEXCOORD_0'])[idx].mean(1)%1
            px=(uv[:,0]*(tex.shape[1]-1)).astype(int);py=(uv[:,1]*(tex.shape[0]-1)).astype(int);c=tex[py,px].astype(float);normal=np.cross(tri[:,1]-tri[:,0],tri[:,2]-tri[:,0]);normal/=np.maximum(np.linalg.norm(normal,axis=1)[:,None],1e-10);shade=.4+.6*np.abs(normal@np.array([.3,.5,.8124]));c[:,:3]*=shade[:,None];colors.append(np.clip(c,0,255).astype('uint8'))
    return np.concatenate(vertices),np.concatenate(colors)

source=geometry(ROOT/'assets/source/tachi/scene.gltf');deriv=geometry(ROOT/'assets/derived/optimized-source/scene.gltf')
canvas=Image.new('RGB',(1500,1080),'#111923');draw=ImageDraw.Draw(canvas);report={}
views=[('Top / six PDC locations',np.array([[0,0,1],[1,0,0],[0,1,0]])),('Side',np.array([[0,0,1],[0,1,0],[1,0,0]])),('Oblique',np.array([[.8,0,.6],[-.3,.866,.4],[-.52,-.5,.693]]))]
for row,(name,basis) in enumerate(views):
    xyz=source[0]@basis.T;lo=xyz[:,:,:2].min((0,1));hi=xyz[:,:,:2].max((0,1));scale=min(650/(hi[0]-lo[0]),265/(hi[1]-lo[1]));masks=[]
    for col,(tris,colors) in enumerate([source,deriv]):
        im=Image.new('RGB',(740,320),'#17232e');mask=Image.new('1',im.size);d=ImageDraw.Draw(im);md=ImageDraw.Draw(mask);v=tris@basis.T
        p=(v[:,:,:2]-(lo+hi)/2)*scale;p[:,:,1]*=-1;p+=np.array([370,170])
        for k in np.argsort(v[:,:,2].mean(1)):
            if colors[k,3]<128:continue
            poly=[tuple(x) for x in p[k]];d.polygon(poly,fill=tuple(colors[k,:3]));md.polygon(poly,fill=1)
        d.text((14,12),('SOURCE 140,863 tris' if col==0 else 'DERIVATIVE 14,622 tris')+' | '+name,fill='white');canvas.paste(im,(col*750,row*350+30));masks.append(np.array(mask,dtype=bool))
    report[name]={'silhouette_iou':float((masks[0]&masks[1]).sum()/(masks[0]|masks[1]).sum()),'source_pixels':int(masks[0].sum()),'derivative_pixels':int(masks[1].sum())}
draw.text((16,8),'Offline source/derivative comparison. No game rendering or runtime test performed.',fill='white');canvas.save(ROOT/'audit/geometry-comparison.png');write(ROOT/'audit/silhouette-comparison.json',report);print(report)
