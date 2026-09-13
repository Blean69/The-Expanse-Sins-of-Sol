from pathlib import Path
import numpy as np
from PIL import Image,ImageDraw
from polish_ui import geometry,render
R=Path(__file__).resolve().parents[1]
meshes,_,_=geometry(Path('/run/media/haker/NVME 2/expanse-workers/validation/assets/derived/update12-c/expanse12_sunflare_editable.gltf'))
canvas=Image.new('RGBA',(1600,1200),(12,19,28,255));d=ImageDraw.Draw(canvas)
basis=np.array([[0,0,-1],[0,1,0],[1,0,0.]])
for k,angle in enumerate([0,60,120,180,240,300]):
 a=np.radians(angle);Q=np.array([[np.cos(a),-np.sin(a),0],[np.sin(a),np.cos(a),0],[0,0,1.]])
 mm=[(m[0]@Q.T,*m[1:])for m in meshes]
 im=render(mm,(800,380),basis)
 canvas.alpha_composite(im,((k%2)*800,(k//2)*400));d.text(((k%2)*800+20,(k//2)*400+12),f'Game longitudinal roll {angle}; bow left; viewing from +X',fill='white')
canvas.save(R/'audit/update13-c/roll-probe.png')
