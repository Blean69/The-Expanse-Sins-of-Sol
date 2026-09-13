"""Render actual derivative hull UI and emit standalone skins; no gameplay changes."""
from pathlib import Path
import json,copy,hashlib
import numpy as np
from PIL import Image,ImageFilter
import jsonschema
from common import Gltf,write
from polish_ui import render,silhouette,ROLES
R=Path(__file__).resolve().parents[1];D=R/'assets/derived/update19-haulers';B=R/'build/update19-haulers';A=R/'audit/update19-haulers';GAME=Path('/run/media/haker/NVME 2/SteamLibrary/steamapps/common/Sins2');SDK=GAME.parent/'Sins of a Solar Empire II - Mod Tools';BASE=Path('/run/media/haker/NVME 2/expanse-mod/build/experiments/expanse_update18');records=[];meta=json.loads((A/'integration-spec.json').read_text())
for ship,sm in meta['ships'].items():
 name='expanse19_'+ship;g=Gltf(D/(name+'_editable.gltf'));meshes=[]
 for p in g.g['meshes'][0]['primitives']:
  mat=g.g['materials'][p['material']];tex=g.g['textures'][mat['pbrMetallicRoughness']['baseColorTexture']['index']];im=g.g['images'][tex['source']];v=g.accessor(p['attributes']['POSITION']);uv=g.accessor(p['attributes']['TEXCOORD_0']);i=g.accessor(p['indices']).reshape(-1,3);meshes.append((v[i],uv[i],np.array(Image.open(D/im['uri']).convert('RGBA')),[1,1,1,1],'OPAQUE'))
 basis=np.array([[.78,0,.625],[.24,.925,-.3],[0,0,1.]]);basis[0]/=np.linalg.norm(basis[0]);basis[1]-=basis[0]*np.dot(basis[0],basis[1]);basis[1]/=np.linalg.norm(basis[1]);basis[2]=np.cross(basis[0],basis[1]);portrait=render(meshes,(1400,800),basis,fill=.88);portrait.save(A/(ship+'-final.png'));mask,_=silhouette(meshes,(1000,500));mask.save(A/(ship+'-silhouette.png'))
 flat=[(m[0],np.zeros_like(m[1]),np.full((1,1,4),255,np.uint8),[.35,.4,.45,1],'OPAQUE')for m in meshes];render(flat,(1100,700),basis,fill=.88).save(A/(ship+'-geometry-control.png'))
 for role in ROLES:
  brush={'supported_dpis':[150,200],'normal_state':{'texture':name+'_'+role}};jsonschema.Draft7Validator(json.loads((SDK/'json_schemas/brush-schema.json').read_text())).validate(brush);write(B/'game/brushes'/(name+'_'+role+'.brush'),brush)
  for dpi,suffix in [(100,''),(150,'150'),(200,'200')]:
   size=Image.open(GAME/'textures'/('trader_light_frigate_'+role+suffix+'.png')).size
   if role.startswith('main_view_icon'):
    icon=mask.resize(size,Image.Resampling.LANCZOS)
    if role!='main_view_icon':icon=icon.filter(ImageFilter.MaxFilter(3))
    out=Image.new('RGBA',size,(235,243,250,0));out.putalpha(icon)
   else:
    im=portrait.copy();im.thumbnail(size,Image.Resampling.LANCZOS);out=Image.new('RGBA',size,(14,23,35,255)if role=='hud_picture'else(0,0,0,0));out.alpha_composite(im,((size[0]-im.width)//2,(size[1]-im.height)//2))
   dest=B/'game/textures'/(name+'_'+role+suffix+'.png');dest.parent.mkdir(parents=True,exist_ok=True);out.save(dest)
 skin=json.loads((GAME/'entities'/('trader_trade_ship.unit_skin'if ship=='artemis'else'derelict_loot_0.unit_skin')).read_text());stage=skin['skin_stages'][0];stage['unit_mesh']['mesh']=sm['hull_mesh'];stage['min_camera_distance']=max(100,sm['ship_spatial']['radius']*1.35)
 for key,role in [('hud_icon','hud_icon'),('hud_monochrome_icon','main_view_icon'),('hud_picture','hud_picture'),('tooltip_picture','tooltip_picture')]:stage['gui'][key]=name+'_'+role
 stage['gui']['name']=name+'.name';stage['gui']['description']=name+'.description'
 for key,role in [('icon','main_view_icon'),('selected_icon','main_view_icon_selected'),('sub_selected_icon','main_view_icon_sub_selected')]:stage['main_view_icon'][key]=name+'_'+role
 if ship=='artemis':
  stage['effects']['exhaust_effects']={'particle_effects':[{'particle_effect':'expanse03_roci_idle_plume'}]};h=stage['effects']['hyperspace_effects']
  for k in ['travel_effect','travel_effect_between_stars','travel_effect_destabilized']:h[k]='expanse03_roci_phase_plume'
 jsonschema.Draft7Validator(json.loads((SDK/'json_schemas/unit-skin-schema.json').read_text())).validate(skin);write(B/'game/entities'/(name+'.unit_skin'),skin);sm['unit_skin']=name;sm['gui_brush_prefix']=name;records.append({'ship':ship,'skin_schema':'PASS','brush_count':len(ROLES),'PNG_count':len(ROLES)*3,'derivative_triangles':sum(len(m[0])for m in meshes),'preview':str(A/(ship+'-final.png'))})
meta['status']='PASS OFFLINE ASSET PIPELINE; GAME VALIDATION REQUIRED';meta['integration_notes']={'artemis':'Full source148m hull replaces compact78m selection because compact lacks aft thruster section.3measured aftengineorigins, native collector/trade mechanics owned by integrator.','le_guin':'Damaged source wreck, only native derelict visual. center point retained fornative scanning flair. Noexhaust.','material_fidelity':'Author base textures/tints/UVs mapped, layeredUnrealshader approximated. This is not a complete PBRshaderport.'};write(A/'integration-spec.json',meta);write(A/'ui-validation.json',{'status':'PASS OFFLINE','records':records,'runtime':'NOT RUN'})
