"""Conservative Sins channel translation of exported author material base layers."""
from pathlib import Path
import json,subprocess,os,hashlib
from common import write
R=Path(__file__).resolve().parents[1];D=R/'assets/derived/update19-haulers';B=R/'build/update19-haulers';A=R/'audit/update19-haulers';MAIN=Path('/run/media/haker/NVME 2/expanse-mod');wine=Path('/home/haker/.var/app/com.valvesoftware.Steam/.local/share/Steam/steamapps/common/Proton 10.0/files/bin/wine64');env=dict(os.environ,WINEPREFIX=str(B/'proton-prefix'),OMP_NUM_THREADS='2',MANGOHUD='0',WINEDEBUG='-all',DISPLAY='',WINEDLLOVERRIDES='mscoree,mshtml=');dest=B/'game/textures';dest.mkdir(parents=True,exist_ok=True)
materials=json.loads((A/'materials.json').read_text());aliases=sorted(set(m['alias']for m in materials));records=[]
for alias in aliases:
 for channel in ['clr','nrm','orm','msk']:
  inp=D/'textures'/(alias+'_'+channel+'.png');out=dest/('expanse19_hauler_'+inp.stem+'.dds');temporary=dest/(inp.stem+'.dds');digest=hashlib.sha256(inp.read_bytes()).hexdigest();stamp=B/(out.stem+'.source-sha256')
  if not out.exists()or not stamp.exists()or stamp.read_text()!=digest:
   cmd=[str(wine),str(MAIN/'.tools/texconv.exe'),'-f','BC5_SNORM'if channel=='nrm'else'BC7_UNORM','-y','-m','0','-nogpu','--single-proc','-o','Z:'+str(dest)]+(['--x2-bias']if channel=='nrm'else['-bc','q'])+['Z:'+str(inp)]
   with (B/'texture.log').open('a')as log:subprocess.run(cmd,env=env,stdout=log,stderr=subprocess.STDOUT,check=True,timeout=180)
   temporary.rename(out);stamp.write_text(digest)
  records.append({'file':out.name,'source_sha256':digest,'sha256':hashlib.sha256(out.read_bytes()).hexdigest()})
for jp in (B/'compiler-json').glob('*.mesh_json'):
 m=json.loads(jp.read_text())
 for alias in m['materials']:
  suffix='mat_'+alias.split('_mat_')[-1];assert suffix in aliases
  write(B/'game/mesh_materials'/(alias+'.mesh_material'),{'version':1,'base_color_texture':'expanse19_hauler_'+suffix+'_clr','normal_texture':'expanse19_hauler_'+suffix+'_nrm','occlusion_roughness_metallic_texture':'expanse19_hauler_'+suffix+'_orm','mask_texture':'expanse19_hauler_'+suffix+'_msk','emissive_factor':0.0})
# Processing checkpoints are source artifacts, never game resources.
for p in dest.glob('*.source-sha256'):p.rename(B/p.name)
write(A/'material-validation.json',{'status':'PASS OFFLINE DDS CONVERSION','normal_format':'BC5_SNORM','other_channels':'BC7_UNORM','mipmaps':'fullchain','maximum_source_dimension':1024,'materials':materials,'files':records,'limitations':'Unreal layered material effects approximated by one selected authored base-color/tint layer. No recovered full shader or verified runtime appearance claim.','runtime':'NOT RUN'})
print('MATERIALS COMPLETE',len(records),flush=True)
