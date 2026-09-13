"""Render a close-up from actual compiled geometry and diffuse textures."""
from pathlib import Path
import numpy as np
from PIL import Image,ImageDraw
from update16_scirocco_mounts import decode,BASE,AUD,ROOT
from validate_experiments import read
from common import read_mesh
from polish_ui import render
OUT=ROOT/'build/experiments/expanse_update16'
r=next(r for r in read(ROOT/'audit/update14-scirocco/integration-spec.json')['rigs']if r['kind']=='pdc')
origin=np.array(r['yaw_pivot_hull']);basis=np.array(r['basis_columns'])
cam=np.array([-1.,.15,.55]);cam/=np.linalg.norm(cam);right=np.cross([0,1,0],cam);right/=np.linalg.norm(right);up=np.cross(cam,right);view=np.array([right,up,cam])
images=[]
for source,label in [(BASE,'0.15 — oversized collar'),(OUT,'0.16 — narrower, hull finish')]:
    meshes=[]
    for name,off,rot in [('expanse12_scirocco_hull',np.zeros(3),np.eye(3)),('expanse12_scirocco_pdc_base',origin,basis),('expanse12_scirocco_pdc_barrel',origin+basis@np.array(r['turret_override']['barrel_position']),basis)]:
        p=source/'meshes'/(name+'.mesh');_,v,i,_=decode(p);m=read_mesh(p)
        for pr in m['primitives']:
            a=pr['vertex_index_start']//3;b=a+pr['vertex_index_count']//3;ids=i[a:b];tri=v[:,:3][ids]@rot.T+off
            keep=np.linalg.norm(tri.mean(1)-origin,axis=1)<24
            if not keep.any():continue
            mat=read(source/'mesh_materials'/(m['materials'][pr['material_index']]+'.mesh_material'))
            tex=np.asarray(Image.open(source/'textures'/(mat['base_color_texture']+'.dds')).convert('RGBA'))
            meshes.append((tri[keep],v[:,10:12][ids][keep],tex,[1,1,1,1],'OPAQUE'))
    image=render(meshes,(640,520),view,fill=.88);bg=Image.new('RGBA',image.size,(29,34,42,255));bg.alpha_composite(image);ImageDraw.Draw(bg).text((16,15),label,fill='white');images.append(bg)
canvas=Image.new('RGBA',(1280,520));canvas.paste(images[0],(0,0));canvas.paste(images[1],(640,0));canvas.save(AUD/'mount-comparison.png')
print(AUD/'mount-comparison.png')
