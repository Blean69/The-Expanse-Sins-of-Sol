"""Compile private Earth game art, dependencies and previews. No installation."""
import argparse,copy,hashlib,subprocess
from pathlib import Path
import numpy as np
from PIL import Image,ImageDraw
from common import read,write,read_mesh
from update26_platform_common import compile as compile_mesh,load_parts
from update27_earth_geometry import ROOT,MAIN,BASE,OUT,BUILD,GAME,AUD,IDS,WINE,ENV
from flight03_effects import scale_effect
import build_update12
build_update12.GAME=Path("/run/media/haker/NVME 2/SteamLibrary/steamapps/common/Sins2")
from build_update12 import phase_effect
PALETTE={'armor':((94,108,122),105,198),'machinery':((30,40,51),135,205),'navy':((20,53,87),145,90),'steel':((151,160,168),85,220)}
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def textures():
 D=OUT/'texture-sources';D.mkdir(exist_ok=True)
 for name,(color,rough,metal)in PALETTE.items():
  rng=np.random.default_rng(2700+len(name));a=np.zeros((512,512,4),np.uint8);a[:,:,:3]=np.clip(np.array(color)+rng.integers(-3,4,(512,512,1)),0,255);a[:,:,3]=255;im=Image.fromarray(a);dr=ImageDraw.Draw(im)
  for row,y in enumerate(range(0,512,64)):
   for x in range(0,512,96):
    shade=int(rng.integers(-9,10));dr.rectangle((x+2,y+2,min(x+93,511),min(y+61,511)),fill=tuple(int(np.clip(c+shade,0,255))for c in color));dr.line((x,y,x+96,y),fill=tuple(max(c-24,0)for c in color),width=2)
    for xx,yy in[(x+6,y+6),(x+87,y+54)]:dr.rectangle((xx,yy,xx+1,yy+1),fill=tuple(min(c+34,255)for c in color))
  stem='expanse27_unn_'+name;im.save(D/(stem+'_clr.png'));Image.new('RGBA',(8,8),(255,rough,metal,255)).save(D/(stem+'_orm.png'))
 for p in D.glob('*.png'):
  dest=GAME/'textures'/(p.stem+'.dds')
  with(BUILD/(p.stem+'.log')).open('w')as log:subprocess.run([str(WINE),str(MAIN/'.tools/texconv.exe'),'-f','BC7_UNORM','-y','-m','0','-nogpu','--single-proc','-bc','q','-o','Z:'+str(GAME/'textures'),'Z:'+str(p)],env=ENV,stdout=log,stderr=subprocess.STDOUT,check=True,timeout=300)
def compile(kind):
 meta=read(AUD/(kind+'-integration.json'));ID=meta['ID'];D=OUT/kind;B=BUILD/kind;B.mkdir(exist_ok=True);names=[meta['hull_mesh']]+list(meta['donors']);checks={};files=set();sources={}
 for name in names:
  (B/name).mkdir(parents=True,exist_ok=True)
  checks[name]=compile_mesh(name,D/name,B/name,GAME,meta['meshpoints']if name==meta['hull_mesh']else[]);files.add('meshes/'+name+'.mesh')
  for alias in checks[name]['materials']:
   if name==meta['hull_mesh']:
    material=next(k for k in PALETTE if alias.removeprefix(name+'_').startswith(k));stem='expanse27_unn_'+material;data={'version':1,'base_color_texture':stem+'_clr','occlusion_roughness_metallic_texture':stem+'_orm','normal_texture':'expanse26_murphy_'+('machinery'if material=='machinery'else'armor')+'_nrm','mask_texture':'expanse23_murphy_msk','emissive_factor':1.}
   else:
    original=next(m for m in meta['donors'][name]['materials']if alias.endswith('_'+m));source=BASE/'mesh_materials'/(original+'.mesh_material');data=read(source);sources[str(source)]=sha(source)
   dest=GAME/'mesh_materials'/(alias+'.mesh_material');write(dest,data);files.add(str(dest.relative_to(GAME)))
   for key,value in data.items():
    if key.endswith('_texture'):
     dest=GAME/'textures'/(value+'.dds')
     if not dest.exists():
      source=BASE/'textures'/dest.name;assert source.is_file()and not source.is_symlink();dest.write_bytes(source.read_bytes());sources[str(source)]=sha(source)
     files.add(str(dest.relative_to(GAME)))
 # One attachment-local blue plume per actual exhaust point. Existing native
 # phase builder creates the corresponding explicit multi-nozzle travel effect.
 source=BASE/'effects/expanse15_truman_idle_plume.particle_effect';spatial=.65 if kind=='hale'else .42;plume=copy.deepcopy(read(source))
 for node in plume['nodes']:
  for key in['x','y','z']:
   if key in node:node[key]=[v*spatial for v in node[key]]
 for emitter in plume['emitters']:
  if 'forward_velocity'in emitter:emitter['forward_velocity']=[v*spatial for v in emitter['forward_velocity']]
  billboard=emitter['particle'].get('billboard',{})
  for key in['width','height']:
   if key in billboard:billboard[key]=[v*spatial for v in billboard[key]]
 path=GAME/'effects'/(ID+'_idle_plume.particle_effect');write(path,plume);files.add(str(path.relative_to(GAME)));sources[str(source)]=sha(source)
 path=GAME/'effects'/(ID+'_phase_plume.particle_effect');write(path,phase_effect(meta['exhausts'],1.15 if kind=='hale'else .75,7.));files.add(str(path.relative_to(GAME)))
 meta.update(status='COMPILED PRIVATE ART; RUNTIME UNTESTED',compile_checks=checks,source_dependency_hashes=sources,files={rel:sha(GAME/rel)for rel in sorted(files)});write(AUD/(kind+'-integration.json'),meta);print('COMPILED',kind,len(files),'files',flush=True)
def preview(kind):
 from polish_ui import render
 meta=read(AUD/(kind+'-integration.json'));parts=[]
 def add(name,position,B=np.eye(3)):
  for p in load_parts(GAME/'meshes'/(name+'.mesh')):
   mat=read(GAME/'mesh_materials'/(p['material']+'.mesh_material'));tex=np.asarray(Image.open(GAME/'textures'/(mat['base_color_texture']+'.dds')).convert('RGBA'));parts.append(((p['v']@B.T+position)[p['i']],p['uv'][p['i']],tex,[1,1,1,1],'OPAQUE'))
 add(meta['hull_mesh'],[0,0,0])
 for r in meta['rigs']:
  if not r['turret']:continue
  w=r['mount'];t=r['turret'];B=np.column_stack([np.cross(w['up'],w['forward']),w['up'],w['forward']]);p=np.array(w['weapon_position'])
  if t['type']=='gimbal':add(t['gimbal_mesh'],p,B)
  else:add(t['biaxial_base_mesh'],p,B);add(t['biaxial_barrel_mesh'],p+B@np.array(t['barrel_position']),B)
 B=np.array([[.8,0,.6],[-.3,.866,.4],[.52,.5,-.693]])
 for label,M in [('aft',B),('bow',B@np.diag([-1,1,-1]))]:render(parts,(1500,1050),M).save(AUD/(kind+'-compiled-'+label+'.png'))
 print('PREVIEW',kind,flush=True)
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('stage',choices=['textures','compile','preview']);p.add_argument('kind',nargs='?',choices=IDS);a=p.parse_args();globals()[a.stage]()if a.stage=='textures'else globals()[a.stage](a.kind)
