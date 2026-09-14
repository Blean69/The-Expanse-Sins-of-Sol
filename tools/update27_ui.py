"""Native game-sized portraits rendered from reviewed compiled new geometry."""
from pathlib import Path
from PIL import Image,ImageFilter
from update20_fleet import ROOT,GAME
from validate_experiments import sha256
from build_polish import write
ROLES=['hud_icon','hud_picture','tooltip_picture','main_view_icon','main_view_icon_selected','main_view_icon_sub_selected']
def generate(source,out=None):
    source=Path(source);out=Path(out or ROOT/'build/update27-ui');art={};edits={}
    for key,uid in [('hephaestus','expanse27_hephaestus'),('laconia','expanse27_laconia_frigate'),('storm','expanse27_gathering_storm')]:
        portrait=Image.open(source/(key+'-oblique.png')).convert('RGBA');side=Image.open(source/(key+'-side.png')).convert('RGBA')
        # Crop to actual nontransparent silhouette so native icon sizes remain
        # legible without stretching the ship's proportions.
        portrait=portrait.crop(portrait.getbbox());side=side.crop(side.getbbox())
        for role in ROLES:
            edits[f'brushes/{uid}_{role}.brush']={'supported_dpis':[150,200],'normal_state':{'texture':uid+'_'+role}}
            for dpi in ('','150','200'):
                size=Image.open(GAME/'textures'/f'trader_light_frigate_{role}{dpi}.png').size
                if role.startswith('main_view_icon'):
                    p=side.copy();p.thumbnail(size,Image.Resampling.LANCZOS);mask=Image.new('L',size);mask.paste(p.getchannel('A'),((size[0]-p.width)//2,(size[1]-p.height)//2))
                    if role!='main_view_icon':mask=mask.filter(ImageFilter.MaxFilter(3))
                    img=Image.new('RGBA',size,(235,243,250,0));img.putalpha(mask)
                else:
                    p=portrait.copy();p.thumbnail(size,Image.Resampling.LANCZOS);img=Image.new('RGBA',size,(14,23,35,255) if role=='hud_picture' else (0,0,0,0));img.alpha_composite(p,((size[0]-p.width)//2,(size[1]-p.height)//2))
                rel=f'textures/{uid}_{role}{dpi}.png';path=out/rel;path.parent.mkdir(parents=True,exist_ok=True);img.save(path);art[rel]=path
    write(ROOT/'audit/update27/ui-manifest.json',{'files':{r:sha256(p) for r,p in art.items()},'source_previews':str(source),'output':str(out)})
    return edits,art

def apply_skin(skin,uid):
    for st in skin['skin_stages']:
        for k in ('hud_icon','hud_monochrome_icon','hud_picture','tooltip_picture'):st['gui'][k]=uid+'_'+('main_view_icon' if k=='hud_monochrome_icon' else k)
        for k,role in [('icon','main_view_icon'),('selected_icon','main_view_icon_selected'),('sub_selected_icon','main_view_icon_sub_selected')]:st['main_view_icon'][k]=uid+'_'+role
    return skin
