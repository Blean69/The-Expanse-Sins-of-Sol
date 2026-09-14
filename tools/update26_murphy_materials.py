"""Murphy material-only refresh; preserve hull, large drive, rig and gameplay bytes."""
from pathlib import Path
import argparse,hashlib,subprocess
import numpy as np
from PIL import Image,ImageDraw,ImageFilter
from common import read,read_mesh,write
from update26_platform_common import load_parts,WINE,ENV
ROOT=Path(__file__).resolve().parents[1];BASE=Path('/run/media/haker/NVME 2/expanse-mod/build/experiments/expanse_update25');MAIN=Path('/run/media/haker/NVME 2/expanse-mod');OUT=ROOT/'assets/derived/update26-murphy';BUILD=ROOT/'build/update26-art/murphy';GAME=ROOT/'build/update26-art/game';AUD=ROOT/'audit/update26-murphy';SIZE=1024
for p in[OUT,BUILD,AUD,GAME/'mesh_materials',GAME/'textures']:p.mkdir(parents=True,exist_ok=True)
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def prepare():
 rng=np.random.default_rng(26);records={}
 for kind,basecolor in[('armor',(100,114,128)),('machinery',(36,44,53))]:
  a=np.empty((SIZE,SIZE,4),np.uint8);a[:,:,:3]=np.clip(np.array(basecolor)+rng.integers(-3,4,(SIZE,SIZE,1)),0,255);a[:,:,3]=255;clr=Image.fromarray(a);draw=ImageDraw.Draw(clr);height=Image.new('L',(SIZE,SIZE),128);hd=ImageDraw.Draw(height);orm=np.zeros((SIZE,SIZE,4),np.uint8);orm[:]=[255,105 if kind=='armor'else 128,195 if kind=='armor'else 205,255]
  # Rectangular panel fields are small finish changes, not artificial extra hull faces.
  for row,y in enumerate(range(0,SIZE,96)):
   for col,x in enumerate(range(-64 if row%2 else 0,SIZE,160)):
    if x<0:continue
    shade=int(rng.integers(-12,15));color=tuple(int(np.clip(c+shade,0,255))for c in basecolor);draw.rectangle((x+2,y+2,min(x+157,SIZE-1),min(y+93,SIZE-1)),fill=color);draw.line((x,y,x+160,y),fill=tuple(max(c-30,0)for c in basecolor),width=2);draw.line((x,y,x,min(y+96,SIZE-1)),fill=tuple(max(c-23,0)for c in basecolor),width=2);hd.line((x,y,x+160,y),fill=119,width=2);hd.line((x,y,x,min(y+96,SIZE-1)),fill=121,width=2);orm[y:min(y+96,SIZE),x:min(x+160,SIZE),1]=int(rng.integers(78,126)if kind=='armor'else rng.integers(112,158))
    for bx,by in[(x+7,y+7),(x+150,y+85)]:draw.ellipse((bx,by,bx+2,by+2),fill=(155,164,172)if kind=='armor'else(93,105,119));hd.ellipse((bx,by,bx+2,by+2),fill=139)
  if kind=='armor':
   for z in[72,-64]:
    x=int((z/240+.5)*SIZE);half=int(5/240*SIZE);draw.rectangle((x-half,0,x+half,SIZE),fill=(22,43,65));draw.line((x-half-3,0,x-half-3,SIZE),fill=(133,159,178),width=2);draw.line((x+half+3,0,x+half+3,SIZE),fill=(133,159,178),width=2);orm[:,x-half:x+half+1,1]=151;orm[:,x-half:x+half+1,2]=75
   draw.line((546,535,710,535),fill=(59,91,119),width=3)
   for x in[332,716]:
    draw.rectangle((x,448,x+23,454),fill=(185,137,59));draw.rectangle((x,550,x+23,556),fill=(185,137,59))
  else:
   for x in range(16,SIZE,64):draw.line((x,0,x,SIZE),fill=(25,32,40),width=4);hd.line((x,0,x,SIZE),fill=117,width=3)
  clr.putalpha(255);stem=f'expanse26_murphy_{kind}';clr.save(OUT/(stem+'_clr.png'))
  # Normal detail follows recessed seams; do not change mesh normals or silhouette.
  h=np.asarray(height.filter(ImageFilter.GaussianBlur(.65)),float)/255;dy,dx=np.gradient(h);n=np.stack([-dx*4,dy*4,np.ones_like(h)],axis=2);n/=np.linalg.norm(n,axis=2,keepdims=True);Image.fromarray(np.clip(np.rint((n+1)*127.5),0,255).astype(np.uint8)).save(OUT/(stem+'_nrm.png'));orm[:,:,0]=np.clip(255-np.maximum(.5-h,0)*350,225,255);Image.fromarray(orm).save(OUT/(stem+'_orm.png'));records[kind]={'roughness_byte_range':[int(orm[:,:,1].min()),int(orm[:,:,1].max())],'metallic_byte_range':[int(orm[:,:,2].min()),int(orm[:,:,2].max())],'maximum_normal_tilt_degrees':float(np.rad2deg(np.arccos(n[:,:,2].min())))}
 preserved=[BASE/'meshes/expanse23_murphy_hull.mesh',BASE/'meshes/expanse23_murphy_pdc_base.mesh',BASE/'meshes/expanse23_murphy_pdc_barrel.mesh',BASE/'effects/expanse23_murphy_idle_plume.particle_effect',BASE/'entities/expanse23_murphy.unit',BASE/'entities/expanse23_murphy.unit_skin',BASE/'entities/expanse23_murphy_pdc.weapon',BASE/'entities/expanse23_murphy_rail.weapon',BASE/'mesh_materials/expanse23_murphy_hull_nozzle.mesh_material'];opposed=0;triangles=0
 for p in load_parts(preserved[0]):
  t=p['v'][p['i']];q=np.cross(t[:,1]-t[:,0],t[:,2]-t[:,0]);opposed+=int((np.sum(q*p['n'][p['i']].mean(1),axis=1)<-1e-5).sum());triangles+=len(t)
 assert opposed==0 and triangles==9454;write(AUD/'integration-spec.json',{'status':'MATERIALS PREPARED','base_reference':str(BASE),'game_output':str(GAME),'material_changes':records,'preserved_files':{str(p):sha(p)for p in preserved},'checks':{'existing_hull_triangles':triangles,'existing_opposed_winding_triangles':opposed,'geometry_rebuild_needed':False},'skin_or_spatial_patch_required':False,'scope':'Only armor and machinery material bindings/textures; hull, rig, gun positions, plume and nozzle materials unchanged.','runtime':'NOT RUN'})
 print('Prepared material contrast; geometry normals checked and retained.')
def compile():
 meta=read(AUD/'integration-spec.json');files=[]
 for p in OUT.glob('*.png'):
  normal=p.stem.endswith('_nrm');cmd=[str(WINE),str(MAIN/'.tools/texconv.exe'),'-f','BC5_SNORM'if normal else'BC7_UNORM','-y','-m','0','-nogpu','--single-proc','-o','Z:'+str(GAME/'textures')]+(['--x2-bias']if normal else['-bc','q'])+['Z:'+str(p)]
  with(BUILD/(p.stem+'.log')).open('w')as log:subprocess.run(cmd,env=ENV,stdout=log,stderr=subprocess.STDOUT,check=True,timeout=300)
  files.append(GAME/'textures'/(p.stem+'.dds'))
 for kind in['armor','machinery']:
  source=BASE/'mesh_materials'/('expanse23_murphy_hull_'+kind+'.mesh_material');m=read(source);stem='expanse26_murphy_'+kind;m.update(base_color_texture=stem+'_clr',occlusion_roughness_metallic_texture=stem+'_orm',normal_texture=stem+'_nrm');dest=GAME/'mesh_materials'/source.name;write(dest,m);files.append(dest);meta.setdefault('source_material_hashes',{})[str(source)]=sha(source)
 meta['files']={str(p.relative_to(GAME)):sha(p)for p in files};meta['status']='OFFLINE MATERIAL PACKAGE PASS; RUNTIME UNTESTED';write(AUD/'integration-spec.json',meta);print(meta['status'])
def preview():
 from polish_ui import render
 meta=read(AUD/'integration-spec.json');parts=[]
 def add(name,position,B=np.eye(3)):
  for p in load_parts(BASE/'meshes'/(name+'.mesh')):
   path=(GAME if(GAME/'mesh_materials'/(p['material']+'.mesh_material')).exists()else BASE)/'mesh_materials'/(p['material']+'.mesh_material');mat=read(path);texture=(GAME if(GAME/'textures'/(mat['base_color_texture']+'.dds')).exists()else BASE)/'textures'/(mat['base_color_texture']+'.dds');tex=np.asarray(Image.open(texture).convert('RGBA'));parts.append(((p['v']@B.T+position)[p['i']],p['uv'][p['i']],tex,[1,1,1,1],'OPAQUE'))
 add('expanse23_murphy_hull',[0,0,0]);unit=read(BASE/'entities/expanse23_murphy.unit')
 for w in unit['weapons']['weapons']:
  definition=read(BASE/'entities'/(w['weapon']+'.weapon'));t=definition.get('turret')
  if not t or t['type']!='biaxial':continue
  B=np.column_stack([np.cross(w['up'],w['forward']),w['up'],w['forward']]);p=np.array(w['weapon_position']);add(t['biaxial_base_mesh'],p,B);add(t['biaxial_barrel_mesh'],p+B@np.array(t['barrel_position']),B)
 B=np.array([[.8,0,.6],[-.3,.866,.4],[.52,.5,-.693]]);render(parts,(1400,900),B).save(AUD/'compiled-material-aft-preview.png');render(parts,(1400,900),B@np.diag([-1,1,-1])).save(AUD/'compiled-material-bow-preview.png');print('Preview shows retained game geometry and new color maps; PBR response still needs in-game check.')
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('stage',choices=['prepare','compile','preview']);globals()[p.parse_args().stage]()
