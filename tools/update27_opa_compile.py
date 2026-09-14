"""Compile OPA hulls, exact native donor turrets, textures and engine effects."""
from pathlib import Path
import json,sys,numpy as np
import update27_opa_common as o
from update27_opa_geometry import loadparts

def ui(name):
 from PIL import Image,ImageFilter
 out=o.BUILD/'ui';out.mkdir(exist_ok=True);portrait=Image.open(o.BUILD/(name+'-oblique.png')).convert('RGBA');mask=Image.open(o.BUILD/(name+'-side.png')).getchannel('A')
 for role in ['hud_icon','hud_picture','tooltip_picture','main_view_icon','main_view_icon_selected','main_view_icon_sub_selected']:
  for dpi,suffix in [(100,''),(150,'150'),(200,'200')]:
   size=Image.open(o.compiler.INSTALLED/'textures'/('trader_light_frigate_'+role+suffix+'.png')).size
   if role.startswith('main_view_icon'):
    alpha=mask.resize(size,Image.Resampling.LANCZOS)
    if role!='main_view_icon':alpha=alpha.filter(ImageFilter.MaxFilter(3))
    im=Image.new('RGBA',size,(235,243,250,0));im.putalpha(alpha)
   else:
    p=portrait.copy();p.thumbnail(size,Image.Resampling.LANCZOS);im=Image.new('RGBA',size,(14,23,35,255)if role=='hud_picture'else(0,0,0,0));im.alpha_composite(p,((size[0]-p.width)//2,(size[1]-p.height)//2))
   im.save(out/(name+'_'+role+suffix+'.png'))

def main():
 o.dirs();reports=[]
 for name,base in [('expanse27_dark_star','expanse06_amun_pdc_0'),('expanse27_behemoth','expanse24_behemoth_pdc')]:
  if len(sys.argv)>1 and sys.argv[1]!=name:continue
  r=o.read(o.AUD/(name+'-geometry.json'));parts=loadparts(name);compiled=o.compile_parts(r['hull_mesh'],parts,r['meshpoints']);r['compiled']=compiled
  o.textures(r['materials']);o.materials(compiled,r['materials'])
  for alias,native in r.get('donor_materials',{}).items():
   name_mat=next(x for x in compiled['materials']if x.endswith('_'+alias));o.write(o.GAME/'mesh_materials'/(name_mat+'.mesh_material'),o.read(o.BASE/'mesh_materials'/(native+'.mesh_material')))
  r['donors']=[]
  for role in ['base','barrel']:r['donors'].append(o.donor(base+'_'+role,name+'_pdc_'+role))
  if name.endswith('dark_star'):r['plumes']=o.plume(name,r['exhausts'],1.25,2.5)
  else:r['plumes']=o.plume(name,r['exhausts'],9.,18.)
  o.preview(parts,r['rigs'],name,r.get('donor_materials'));ui(name)
  r['status']='PASS OFFLINE COMPILED ART; NO RUNTIME TEST';r['output_game']=str(o.GAME)
  r['art_files']={str(p.relative_to(o.GAME)):o.sha(p)for p in sorted(o.GAME.rglob('*'))if p.is_file()and name in p.name}
  r['previews']=[str(o.BUILD/(name+'-'+x+'.png'))for x in ['oblique','side','aft','epstein-closeup']if(o.BUILD/(name+'-'+x+'.png')).exists()];r['preview_sha256']={p:o.sha(p)for p in r['previews']}
  r['tool_sources_sha256']={str(p):o.sha(p)for p in [o.compiler.SDK/'MeshBuilder/bin/MeshBuilder.exe',o.MAIN/'.tools/texconv.exe',o.MAIN/'.tools/libmeshoptimizer.so',o.MAIN/'tools/update12_scirocco_common.py',o.MAIN/'tools/common.py']}
  o.write(o.AUD/(name+'-art.json'),r);reports.append({'id':name,'triangles':compiled['triangles'],'art_files':len(r['art_files'])});print(json.dumps(reports[-1]),flush=True)
 o.write(o.AUD/'compiled-art-manifest.json',{'base':str(o.BASE),'files':{str(p.relative_to(o.GAME)):o.sha(p)for p in sorted(o.GAME.rglob('*'))if p.is_file()},'ui_files':{'textures/'+p.name:o.sha(p) for p in sorted((o.BUILD/'ui').glob('*.png'))},'source_files_not_packaged':True,'distribution':'LOCAL USER GAME DERIVATIVE ONLY; no publication authorized'})
if __name__=='__main__':main()
