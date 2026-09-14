"""Compiled DDS/mesh previews and bounded outgoing-ray checks; no game runtime."""
from update27_mars_assets import *
from polish_ui import render
from update14_pdc_arcs import Rays,sample,choose
from PIL import Image
import argparse

def preview(key):
 meta=read(AUD/(key+'-integration.json'));parts=[]
 def add(name,pos,B=np.eye(3)):
  b=(GAME/'meshes'/(name+'.mesh')).read_bytes();count=struct.unpack_from('<Q',b,53)[0];off=61;rows=[]
  for _ in range(count):
   r=struct.unpack_from('<12f?',b,off);rows.append(r[:-1]);off+=49+(8 if r[-1]else 0)
  rows=np.array(rows);ic=struct.unpack_from('<Q',b,off)[0];idx=np.frombuffer(b,'<u4',ic,off+8);info=read_mesh(GAME/'meshes'/(name+'.mesh'));v=rows[:,:3]@B.T+pos
  for p in info['primitives']:
   ii=idx[p['vertex_index_start']:p['vertex_index_start']+p['vertex_index_count']].reshape(-1,3);mat=read(GAME/'mesh_materials'/(info['materials'][p['material_index']]+'.mesh_material'));tex=np.array(Image.open(GAME/'textures'/(mat['base_color_texture']+'.dds')).convert('RGBA'));parts.append((v[ii],rows[ii,10:12],tex,mat.get('base_color_factor',[1,1,1,1]),'OPAQUE'))
 add(meta['hull_mesh'],[0,0,0]);hull=np.concatenate([p[0]for p in parts]);ray=Rays(hull,BUILD/'rays');obstacles=[hull]
 for r in meta['rigs']:
  if r['kind']!='rail':continue
  path=GAME/'meshes'/(r['turret_override']['gimbal_mesh']+'.mesh');b=path.read_bytes();cnt=struct.unpack_from('<Q',b,53)[0];off=61;verts=[]
  for _ in range(cnt):
   row=struct.unpack_from('<12f?',b,off);verts.append(row[:3]);off+=49+(8 if row[-1]else 0)
  ic=struct.unpack_from('<Q',b,off)[0];ix=np.frombuffer(b,'<u4',ic,off+8).reshape(-1,3);verts=np.array(verts);basis=np.column_stack([np.cross(r['up'],r['forward']),r['up'],r['forward']]);root=np.array(r['position'])
  for yaw in [r['yaw_arc']['min_angle'],0,r['yaw_arc']['max_angle']]:
   rot=Rotation.from_euler('y',yaw,degrees=True).as_matrix();posed=verts@rot.T@basis.T+root;obstacles.append(posed[ix])
 pdc_ray=Rays(np.concatenate(obstacles),BUILD/'rays');checks=[]
 for rig in meta['rigs']:
  B=np.column_stack([np.cross(rig['up'],rig['forward']),rig['up'],rig['forward']]);pos=np.array(rig['position']);turret=rig['turret_override'];mount={**rig,'weapon_position':rig['position']}
  if rig['kind']=='pdc':
   if key!='storm':
    ys=np.arange(-180,181,2);ps=np.arange(-85,6,2);mask,_,_=sample(pdc_ray,mount,turret,ys,ps,3.);safe,_=choose(mask,ys,ps);rig.update(safe)
   ys=np.arange(rig['yaw_arc']['min_angle'],rig['yaw_arc']['max_angle']+.01,1);ps=np.arange(rig['pitch_arc']['min_angle'],rig['pitch_arc']['max_angle']+.01,1);blocked,ex,count=sample(pdc_ray,mount,turret,ys,ps,3.);assert not blocked.any(),(rig['mesh_point'],ex);add(turret['biaxial_base_mesh'],pos,B);add(turret['biaxial_barrel_mesh'],pos+B@np.array(turret['barrel_position']),B)
  else:
   fake={'barrel_position':[0,0,0],'muzzle_positions':turret['muzzle_positions']};ys=np.arange(rig['yaw_arc']['min_angle'],rig['yaw_arc']['max_angle']+.01,.5);ps=np.arange(rig['pitch_arc']['min_angle'],rig['pitch_arc']['max_angle']+.01,.5);blocked,ex,count=sample(ray,mount,fake,ys,ps,1.);assert not blocked.any(),(rig['mesh_point'],ex);add(turret['gimbal_mesh'],pos,B)
  checks.append({'mesh_point':rig['mesh_point'],'rays':count,'blocked':0,'yaw_arc':rig['yaw_arc'],'pitch_arc':rig['pitch_arc']})
 ray.close();pdc_ray.close()
 for name,B in [('oblique',[[.65,0,.76],[-.3,.92,.26],[-.7,-.39,.60]]),('side',[[0,0,1],[0,1,0],[-1,0,0]]),('top',[[0,0,1],[1,0,0],[0,1,0]]),('stern',[[1,0,0],[0,1,0],[0,0,-1]]),('bow',[[1,0,0],[0,1,0],[0,0,1]])]:render(parts,(1400,850),np.array(B),fill=.86).save(AUD/(key+'-'+name+'.png'))
 meta['arc_checks']=checks;meta['compiled_assembled_triangles']=sum(len(p[0])for p in parts);meta['preview_scope']='Actual compiled mesh and DDS; diffuse software render. Specular lighting, animated targeting and gameplay not tested.'
 if meta.get('epstein_drive_pass'):
  meta['epstein_drive_pass']['stage']='compiled; offline ray checks and diffuse previews complete'
  meta['preview_texture_limit']='Actual tile grain/fasteners and native Tachi orange drive flecks are present in textures; nearest-neighbor CPU sampling exaggerates speckles. Game filtering, normal response and specular appearance remain untested.'
 aliases=[]
 for r in meta['rigs']:
  t=r['turret_override']
  for field in ['biaxial_base_mesh','biaxial_barrel_mesh','gimbal_mesh']:
   if field in t and t[field]not in [a['mesh_alias_name']for a in aliases]:aliases.append({'mesh_alias_name':t[field],'mesh_definition':{'mesh':t[field],'shader':'ship','is_shadow_blocker':True}})
 meta['skin_contract']={'unit_mesh':{'mesh':meta['hull_mesh'],'shader':'ship','is_shadow_blocker':True},'child_mesh_alias_bindings':{'map':aliases},'exhaust_effects':{'particle_effects':[{'particle_effect':'expanse12_raptor_idle_plume'}]},'phase_note':'Use ordinary native hyperspace effects; no absolute multi-nozzle phase effect.'}
 meta['weapon_mounts']=[{'mesh_point':r['mesh_point'],'weapon_position':r['position'],'up':r['up'],'forward':r['forward'],'yaw_arc':r['yaw_arc'],'pitch_arc':r['pitch_arc']}for r in meta['rigs']]
 write(AUD/(key+'-integration.json'),meta);print(key,'PASS',sum(c['rays']for c in checks),'rays',flush=True)
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('key');a=p.parse_args();preview(a.key)
