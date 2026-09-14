"""Render the compiled battery game meshes with packaged DDS base color maps."""
from pathlib import Path
import struct
import numpy as np
from PIL import Image
from scipy.spatial.transform import Rotation
from common import read,read_mesh
from polish_ui import render
ROOT=Path(__file__).resolve().parents[1];GAME=ROOT/'build/update22-foehammer/game';AUD=ROOT/'audit/update22-foehammer';meta=read(AUD/'integration-spec.json');parts=[]
def add(name,position,B=np.eye(3)):
 p=GAME/'meshes'/(name+'.mesh');b=p.read_bytes();count=struct.unpack_from('<Q',b,53)[0];off=61;rows=[]
 for _ in range(count):
  vals=struct.unpack_from('<12f?',b,off);rows.append(vals[:-1]);off+=49+(8 if vals[-1] else 0)
 rows=np.array(rows);ic=struct.unpack_from('<Q',b,off)[0];off+=8;indices=np.frombuffer(b,dtype='<u4',count=ic,offset=off);v=rows[:,:3]@B.T+position;uv=rows[:,10:12];info=read_mesh(p)
 for prim in info['primitives']:
  idx=indices[prim['vertex_index_start']:prim['vertex_index_start']+prim['vertex_index_count']].reshape(-1,3);material=read(GAME/'mesh_materials'/(info['materials'][prim['material_index']]+'.mesh_material'));tex=np.asarray(Image.open(GAME/'textures'/(material['base_color_texture']+'.dds')).convert('RGBA'));parts.append((v[idx],uv[idx],tex,[1,1,1,1],'OPAQUE'))
add(meta['base_mesh'],[0,0,0])
for rig in meta['rigs']:
 B=np.column_stack([np.cross(rig['up'],rig['forward']),rig['up'],rig['forward']]);p=np.array(rig['position']);t=rig['turret_override']
 if rig['kind']=='rail':add(t['gimbal_mesh'],p,B)
 else:add(t['biaxial_base_mesh'],p,B);add(t['biaxial_barrel_mesh'],p+B@np.array(t['barrel_position']),B)
B=np.array([[.8,0,.6],[-.3,.866,.4],[.52,.5,-.693]]);render(parts,(1200,800),B).save(AUD/'compiled-game-preview.png');print('Rendered actual packaged mesh + DDS files, not game runtime.')
