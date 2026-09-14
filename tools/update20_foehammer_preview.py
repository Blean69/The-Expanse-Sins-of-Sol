"""Offline source intake/geometry visualization; never installs or edits originals."""
import sys,numpy as np
from pathlib import Path
from PIL import Image
sys.path.insert(0,'tools');from common import Gltf
from polish_ui import render
p=Path('assets/derived/update20-foehammer/foehammer_orbital_editable.gltf');g=Gltf(p);parts=[]
for ni,n in enumerate(g.g['nodes']):
 for pr in g.g['meshes'][n['mesh']]['primitives']:
  idx=g.accessor(pr['indices']).reshape(-1,3);pbr=g.g['materials'][pr['material']]['pbrMetallicRoughness'];tex=np.full((1,1,4),255,dtype='uint8')
  if 'baseColorTexture' in pbr:
   uri=g.g['images'][g.g['textures'][pbr['baseColorTexture']['index']]['source']]['uri'];tex=np.asarray(Image.open(p.parent/uri).convert('RGBA'))
  parts.append((g.positions(ni,pr)[idx],g.accessor(pr['attributes']['TEXCOORD_0'])[idx],tex,pbr.get('baseColorFactor',[1,1,1,1]),'OPAQUE'))
B=np.array([[.8,0,.6],[-.3,.866,.4],[.52,.5,-.693]])
render(parts,(1000,650),B).save('audit/update20-assets/foehammer-art-prototype.png')
