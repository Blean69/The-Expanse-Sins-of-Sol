"""Private portraits and brushes projected from the actual compiled hulls."""
from PIL import Image,ImageFilter
from update27_earth_geometry import GAME,AUD,IDS
from update27_earth_compile import sha
from common import read,write
from pathlib import Path
NATIVE=Path('/run/media/haker/NVME 2/SteamLibrary/steamapps/common/Sins2')
def main():
 for kind,ID in IDS.items():
  meta=read(AUD/(kind+'-integration.json'));portrait=Image.open(AUD/(kind+'-compiled-bow.png')).convert('RGBA')
  for role in ['hud_icon','hud_picture','tooltip_picture','main_view_icon','main_view_icon_selected','main_view_icon_sub_selected']:
   for suffix in ['','150','200']:
    size=Image.open(NATIVE/'textures'/('trader_light_frigate_'+role+suffix+'.png')).size
    if role.startswith('main_view_icon'):
     alpha=portrait.getchannel('A').resize(size,Image.Resampling.LANCZOS)
     if role!='main_view_icon':alpha=alpha.filter(ImageFilter.MaxFilter(3))
     img=Image.new('RGBA',size,(235,243,250,0));img.putalpha(alpha)
    else:
     p=portrait.copy();p.thumbnail(size,Image.Resampling.LANCZOS);img=Image.new('RGBA',size,(14,23,35,255)if role=='hud_picture'else(0,0,0,0));img.alpha_composite(p,((size[0]-p.width)//2,(size[1]-p.height)//2))
    rel='textures/'+ID+'_'+role+suffix+'.png';img.save(GAME/rel);meta['files'][rel]=sha(GAME/rel)
   rel='brushes/'+ID+'_'+role+'.brush';write(GAME/rel,{'supported_dpis':[150,200],'normal_state':{'texture':ID+'_'+role}});meta['files'][rel]=sha(GAME/rel)
  write(AUD/(kind+'-integration.json'),meta)
 print('UI: 36 textures and 12 native brushes')
if __name__=='__main__':main()
