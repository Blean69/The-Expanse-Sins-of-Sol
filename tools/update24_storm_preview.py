"""Actual compiled meshes/materials plus offline hull-ray arc audit."""
from pathlib import Path
import struct,sys
import numpy as np
from PIL import Image
MAIN=Path('/run/media/haker/NVME 2/expanse-mod');sys.path.insert(0,str(MAIN/'tools'))
from common import read,read_mesh,write,Gltf
from polish_ui import render
from update14_pdc_arcs import Rays,sample,choose
ROOT=Path(__file__).resolve().parents[1];GAME=ROOT/'build/update24-storm/game';AUD=ROOT/'audit/update24-storm';meta=read(AUD/'integration-spec.json');parts=[]
def add(name,position,B=np.eye(3),barrel=False):
 b=(GAME/'meshes'/(name+'.mesh')).read_bytes();count=struct.unpack_from('<Q',b,53)[0];off=61;rows=[]
 for _ in range(count):
  vals=struct.unpack_from('<12f?',b,off);rows.append(vals[:-1]);off+=49+(8 if vals[-1]else 0)
 rows=np.array(rows);ic=struct.unpack_from('<Q',b,off)[0];off+=8;idx=np.frombuffer(b,dtype='<u4',count=ic,offset=off);v=rows[:,:3]@B.T+position;uv=rows[:,10:12];info=read_mesh(GAME/'meshes'/(name+'.mesh'))
 for pr in info['primitives']:
  ii=idx[pr['vertex_index_start']:pr['vertex_index_start']+pr['vertex_index_count']].reshape(-1,3);m=read(GAME/'mesh_materials'/(info['materials'][pr['material_index']]+'.mesh_material'));tex=np.asarray(Image.open(GAME/'textures'/(m['base_color_texture']+'.dds')).convert('RGBA'));parts.append((v[ii],uv[ii],tex,[1,1,1,1],'OPAQUE'))
add(meta['hull_mesh'],[0,0,0]);hull=np.concatenate([p[0]for p in parts]);ray=Rays(hull,ROOT/'build/update24-storm/rays');checks=[]
for rig in meta['rigs']:
 mount={**rig,'weapon_position':rig['position']};arcs=rig['yaw_arc'],rig['pitch_arc'];ys=np.arange(-180,181,4.);ps=np.arange(-85,-14,2.);mask,_,_=sample(ray,mount,rig['turret_override'],ys,ps,3.);safe,_=choose(mask,ys,ps);rig.update(safe);mount.update(safe)
 ys=np.arange(safe['yaw_arc']['min_angle'],safe['yaw_arc']['max_angle']+.01,1);ps=np.arange(-85,safe['pitch_arc']['max_angle']+.01,1);blocked,ex,count=sample(ray,mount,rig['turret_override'],ys,ps,3.);assert not blocked.any(),ex;checks.append({'mesh_point':rig['mesh_point'],'rays':count,'blocked':0,'step_degrees':1,'aim_envelope':3,'arcs':safe})
 B=np.column_stack([np.cross(rig['up'],rig['forward']),rig['up'],rig['forward']]);p=np.array(rig['position']);t=rig['turret_override'];add(t['biaxial_base_mesh'],p,B);add(t['biaxial_barrel_mesh'],p+B@np.array(t['barrel_position']),B)
ray.close()
for label,B in [('oblique',[[.65,0,.76],[-.3,.92,.26],[-.7,-.39,.60]]),('side',[[0,0,1],[0,1,0],[-1,0,0]]),('top',[[0,0,1],[1,0,0],[0,1,0]])]:render(parts,(1400,800),np.array(B),fill=.86).save(AUD/(label+'.png'))
meta['arc_checks']=checks;meta['assembled_triangles']=len(hull)+6*(read_mesh(GAME/'meshes/expanse24_storm_pdc_base.mesh')['triangles']+read_mesh(GAME/'meshes/expanse24_storm_pdc_barrel.mesh')['triangles']);meta['adaptations'].append('Outward arc rectangles refined by 1-degree samples and a 3-degree outgoing direction envelope. Static hull checks do not prove swept turret-mesh or runtime targeting clearance.');write(AUD/'integration-spec.json',meta);print('PASS arcs',sum(x['rays']for x in checks),'rays; actual compiled preview')
