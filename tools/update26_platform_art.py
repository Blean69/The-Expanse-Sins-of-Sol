"""Rebuild Foehammer support as an open orbital kitbash; exact weapon rigs retained."""
from pathlib import Path
import argparse,copy,hashlib,json
import numpy as np
from scipy.spatial.transform import Rotation
from PIL import Image
from common import read,read_mesh,write
from update26_platform_common import load_parts,export,compile as compile_mesh
import update23_murphy_art as helper
ROOT=Path(__file__).resolve().parents[1];BASE=Path('/run/media/haker/NVME 2/expanse-mod/build/experiments/expanse_update25');NATIVE=Path('/run/media/haker/NVME 2/SteamLibrary/steamapps/common/Sins2');OUT=ROOT/'assets/derived/update26-platform';BUILD=ROOT/'build/update26-art/platform';GAME=ROOT/'build/update26-art/game';AUD=ROOT/'audit/update26-platform';NAME='expanse22_foehammer_support'
for p in[OUT,BUILD,AUD,GAME/'meshes',GAME/'mesh_materials',GAME/'textures']:p.mkdir(parents=True,exist_ok=True)
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def prepare():
 parts=[];donors=[];materials={}
 def donor(name,label,scale,position,R):
  path=NATIVE/'meshes'/(name+'.mesh');center=np.array(read_mesh(path)['box'][:3]);source=load_parts(path);count=0
  for j,p in enumerate(source):
   count+=len(p['i']);p['v']=(p['v']-center)@R.T*scale+position;p['n']=p['n']@R.T;p['t'][:,:3]=p['t'][:,:3]@R.T;mat=f'{label}_{j}';materials[mat]=str(NATIVE/'mesh_materials'/(p['material']+'.mesh_material'));p['material']=mat;parts.append(p)
  donors.append({'source':str(path),'sha256':sha(path),'triangles':count,'scale':scale,'centered_on_source_bounds':center.tolist(),'position':position,'rotation':R.tolist(),'material_label':label})
 donor('trader_research_lab_structure_component_habitat_ring','service_ring',.31,[0,-58,-22],Rotation.from_euler('x',90,degrees=True).as_matrix())
 for sign,label in[(-1,'port_machinery'),(1,'starboard_machinery')]:donor('trader_capital_ship_factory_structure_component_left',label,.08,[sign*33,-72,-13],Rotation.from_euler('y',180 if sign<0 else 0,degrees=True).as_matrix())
 # Recoil truss, circular service column, and supported PDC sockets. No solid block.
 frame=[]
 def tube(a,b,r,n=12,inner=None):frame.append(helper.cylinder(a,b,r,n,inner))
 tube([0,-62,-10],[0,-19,-10],8,32);tube([0,-61,-10],[0,-58,-10],12,32,9);tube([0,-34,-10],[0,-31,-10],10,32,8);tube([0,-22,-10],[0,-18.4,-10],9,32)
 for x in[-34,34]:
  for z in[-46,2]:tube([x,-52,z],[np.sign(x)*5,-25,-10+(-4 if z<0 else 4)],1.7)
  tube([x,-63,-44],[x,-65,18],1.4)
 for sign in[-1,1]:
  tube([sign*41,-54,-26],[sign*62,-31,-26],2.1);tube([sign*62,-31,-26],[sign*70.9,-31,-26],3.2,24);tube([sign*36,-56,-42],[sign*60,-33,-26],1.2);tube([sign*36,-56,-2],[sign*60,-33,-26],1.2)
 for z in[-46,2]:tube([-34,-52,z],[34,-52,z],1.4)
 for end in[[-42,-60,-22],[42,-60,-22],[0,-60,-70],[0,-60,26]]:tube([0,-60,-10],end,2)
 frame=np.concatenate(frame);p=helper.frames(frame);p['uv']=np.clip(p['uv'],0,1);p['material']='recoil_frame';parts.append(p);materials['recoil_frame']=str(BASE/'mesh_materials/expanse23_murphy_hull_machinery.mesh_material')
 old=read_mesh(BASE/'meshes'/(NAME+'.mesh'));points=[{'name':p['name'],'translation':p['position'],'rotation':Rotation.from_matrix(np.array(p['rotation']).reshape(3,3).T).as_quat().tolist()}for p in old['meshpoints']];export(NAME,parts,points,OUT)
 vertices=np.concatenate([p['v'][np.unique(p['i'])]for p in parts]);assert vertices[:,0].max()<71 and vertices[:,0].min()>-71;assert vertices[:,1].max()<=-18.39
 weapons=read(BASE/'entities/expanse22_foehammer_battery.unit')['weapons'];allverts=[vertices]
 for w in weapons['weapons']:
  definition=read(BASE/'entities'/(w['weapon']+'.weapon'));t=definition['turret'];B=np.column_stack([np.cross(w['up'],w['forward']),w['up'],w['forward']]);pos=np.array(w['weapon_position'])
  meshes=[(t['gimbal_mesh'],np.zeros(3))]if t['type']=='gimbal'else[(t['biaxial_base_mesh'],np.zeros(3)),(t['biaxial_barrel_mesh'],np.array(t['barrel_position']))]
  for name,offset in meshes:
   for p in load_parts(BASE/'meshes'/(name+'.mesh')):allverts.append((p['v'][np.unique(p['i'])]+offset)@B.T+pos)
 allverts=np.concatenate(allverts);lo=allverts.min(0);hi=allverts.max(0);oldsp=read(BASE/'entities/expanse22_foehammer_battery.unit')['spatial'];spatial={'box':{'center':((lo+hi)/2).tolist(),'extents':((hi-lo)/2).tolist()},'radius':float(np.linalg.norm(allverts-(lo+hi)/2,axis=1).max())}
 weapon_meshes=sorted({v for w in weapons['weapons']for k,v in read(BASE/'entities'/(w['weapon']+'.weapon'))['turret'].items()if k.endswith('_mesh')})
 write(AUD/'integration-spec.json',{'status':'PREPARED','base_reference':str(BASE),'game_output':str(GAME),'replacement_mesh':NAME,'materials':materials,'donors':donors,'meshpoints':points,'counts':{'support':sum(len(p['i'])for p in parts),'frame':len(frame),'rail_unchanged':8519,'two_pdcs_unchanged':1354,'assembled':sum(len(p['i'])for p in parts)+8519+1354},'spatial_patch_guidance':{'unit':'expanse22_foehammer_battery','old':oldsp,'new_art_bounds':spatial,'note':'Main owns unit.spatial update. Do not modify weapons, physics, cost or build time. Unit skin keeps same support mesh ID and unchanged child aliases.'},'source_weapon_records':weapons,'source_hashes':{str(p):sha(p)for p in[BASE/'meshes'/(NAME+'.mesh'),BASE/'entities/expanse22_foehammer_battery.unit',BASE/'entities/expanse22_foehammer_battery.unit_skin',*[BASE/'meshes'/(m+'.mesh')for m in weapon_meshes],*[BASE/'entities'/(w['weapon']+'.weapon')for w in weapons['weapons']]]},'clearance':{'support_x_min':float(vertices[:,0].min()),'support_x_max':float(vertices[:,0].max()),'support_y_max':float(vertices[:,1].max()),'pdcs_outward_plane_x':71,'rail_muzzle_height':0,'rail_fire_path_vertical_clearance':float(-vertices[:,1].max())},'runtime':'NOT RUN'})
 print('Prepared open orbital kitbash:',sum(len(p['i'])for p in parts),'support triangles',flush=True)
def compile():
 meta=read(AUD/'integration-spec.json');checks=compile_mesh(NAME,OUT,BUILD,GAME,meta['meshpoints']);source_hashes=meta['source_hashes'];files=[GAME/'meshes'/(NAME+'.mesh')]
 for alias in checks['materials']:
  key=alias.removeprefix(NAME+'_');source=Path(meta['materials'][key]);mat=read(source);dest=GAME/'mesh_materials'/(alias+'.mesh_material');write(dest,mat);files.append(dest);source_hashes[str(source)]=sha(source)
  for k,value in mat.items():
   if k.endswith('_texture'):
    src=source.parents[1]/'textures'/(value+'.dds');assert src.is_file()and not src.is_symlink();dest=GAME/'textures'/src.name;dest.write_bytes(src.read_bytes());source_hashes[str(src)]=sha(src);files.append(dest)
 meta['status']='OFFLINE COMPILED ART PASS; RUNTIME UNTESTED';meta['checks']=checks;meta['files']={str(p.relative_to(GAME)):sha(p)for p in sorted(set(files))};write(AUD/'integration-spec.json',meta);print(meta['status'],flush=True)
def preview():
 from polish_ui import render
 meta=read(AUD/'integration-spec.json');parts=[]
 def add(name,position,B=np.eye(3)):
  mesh=(GAME if(GAME/'meshes'/(name+'.mesh')).exists()else BASE)/'meshes'/(name+'.mesh')
  for p in load_parts(mesh):
   path=(GAME if(GAME/'mesh_materials'/(p['material']+'.mesh_material')).exists()else BASE)/'mesh_materials'/(p['material']+'.mesh_material');mat=read(path);texture=(GAME if(GAME/'textures'/(mat['base_color_texture']+'.dds')).exists()else BASE)/'textures'/(mat['base_color_texture']+'.dds');tex=np.asarray(Image.open(texture).convert('RGBA'));parts.append(((p['v']@B.T+position)[p['i']],p['uv'][p['i']],tex,[1,1,1,1],'OPAQUE'))
 add(NAME,[0,0,0])
 for w in meta['source_weapon_records']['weapons']:
  t=read(BASE/'entities'/(w['weapon']+'.weapon'))['turret'];B=np.column_stack([np.cross(w['up'],w['forward']),w['up'],w['forward']]);p=np.array(w['weapon_position'])
  if t['type']=='gimbal':add(t['gimbal_mesh'],p,B)
  else:add(t['biaxial_base_mesh'],p,B);add(t['biaxial_barrel_mesh'],p+B@np.array(t['barrel_position']),B)
 B=np.array([[.8,0,.6],[-.3,.866,.4],[.52,.5,-.693]]);render(parts,(1500,1050),B).save(AUD/'compiled-orbital-preview.png');render(parts,(1500,1050),B@np.diag([-1,1,-1])).save(AUD/'compiled-orbital-reverse-preview.png');print('Rendered actual compiled mesh and retained gun rigs; not game runtime.')
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('stage',choices=['prepare','compile','preview']);globals()[p.parse_args().stage]()
