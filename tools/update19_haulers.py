"""Private supplied Telltale hauler derivatives. Preserves source files; offline only."""
from pathlib import Path
import sys,json,ctypes as C,hashlib,copy
import numpy as np
from PIL import Image
from common import Gltf,write
import update12_scirocco_common as c
from polish_ui import render
R=Path(__file__).resolve().parents[1];MAIN=Path('/run/media/haker/NVME 2/expanse-mod');SRC=Path('/run/media/haker/NVME 2/expanse-extracted/Stations-and-Haulers');D=R/'assets/derived/update19-haulers';B=R/'build/update19-haulers';A=R/'audit/update19-haulers';RAW=SRC/'raw-export';SCALE=105/46
for p in [D,B,A,D/'textures']:p.mkdir(parents=True,exist_ok=True)
c.OUT=D
matpaths={p.stem:p for p in RAW.rglob('*.json')}
lib=C.CDLL(str(MAIN/'.tools/libmeshoptimizer.so'));U=C.POINTER(C.c_uint);F=C.POINTER(C.c_float)
fn=lib.meshopt_simplifyWithAttributes;fn.argtypes=[U,U,C.c_size_t,F,C.c_size_t,C.c_size_t,F,C.c_size_t,F,C.c_size_t,C.c_void_p,C.c_size_t,C.c_float,C.c_uint,F];fn.restype=C.c_size_t
matcache={};mater=[]
def material(name):
 if name in matcache:return matcache[name]
 data=json.loads(matpaths[name].read_text()) if name in matpaths else {};t=data.get('Textures',{});pr=data.get('Parameters',{});sc=pr.get('Scalars',{});co=pr.get('Colors',{});key=next((k for k in ['Base Color Texture','Base Color Texture R','Base Color Texture 0','PM_Diffuse'] if k in t),None)
 if not key:key=next((k for k in t if k.endswith('_BC') or k.endswith('_A')),None)
 src=RAW/(t[key].split('.')[0]+'.png') if key else None
 suffix=key.replace('Base Color Texture','') if key and key.startswith('Base Color Texture') else ''
 tint=co.get('Base Color Tint'+suffix,co.get('Base Color Tint',{'R':.45,'G':.45,'B':.45}))
 factor=np.array([tint.get(k,1) for k in ['R','G','B']]);factor=np.maximum(factor,0)**(1/2.2)
 im=Image.open(src).convert('RGBA') if src and src.exists() else Image.new('RGBA',(8,8),(255,255,255,255));im.thumbnail((1024,1024));a=np.array(im);a[:,:,:3]=np.rint(a[:,:,:3]*factor).clip(0,255).astype('uint8');a[:,:,3]=255
 alias='mat_'+hashlib.sha256(name.encode()).hexdigest()[:10];Image.fromarray(a).save(D/'textures'/(alias+'_clr.png'))
 normalkey=next((k for k in ['Normal Texture'+suffix,'Normal Texture','PM_Normals'] if k in t),None)
 nsrc=RAW/(t[normalkey].split('.')[0]+'.png') if normalkey else None
 ni=Image.open(nsrc).convert('RGB') if nsrc and nsrc.exists() else Image.new('RGB',(8,8),(128,128,255));ni.thumbnail((1024,1024));n=np.array(ni).astype(float)/127.5-1;n[:,:,1]*=-1;n[:,:,2]=np.sqrt(np.maximum(0,1-n[:,:,0]**2-n[:,:,1]**2));n/=np.maximum(np.linalg.norm(n,axis=2,keepdims=True),1e-8);Image.fromarray(np.rint((n+1)*127.5).clip(0,255).astype('uint8')).save(D/'textures'/(alias+'_nrm.png'))
 rough=float(np.clip(sc.get('Roughness Value'+suffix,sc.get('Roughness Value',.65)),.25,.9));metal=float(np.clip(sc.get('Metallic Value'+suffix,sc.get('Metallic Value',.3)),0,1));Image.new('RGBA',(8,8),(255,round(rough*255),round(metal*255),255)).save(D/'textures'/(alias+'_orm.png'));Image.new('RGBA',(8,8),(0,0,0,0)).save(D/'textures'/(alias+'_msk.png'))
 uvscale=[sc.get('TIle U'+suffix,sc.get('TIle U',1))*sc.get('Tile UV'+suffix,sc.get('Tile UV',1)),sc.get('Tile V'+suffix,sc.get('Tile V',1))*sc.get('Tile UV'+suffix,sc.get('Tile UV',1))]
 result={'alias':alias,'source_material':name,'source_json':str(matpaths.get(name,'')),'base_color_source':str(src),'normal_source':str(nsrc),'uv_scale':uvscale,'tint_linear':factor.tolist(),'approximation':'Selected base layer with authored tint/tile; vertex damage/layer blend and decals are not full Unreal shader reproduction. NormalY converted DirectX to glTF; roughness/metal scalar conservative; emission disabled pending source shader verification.'};mater.append(result);matcache[name]=result;return result
ships={}
for ship,source,rot in [('artemis','Artemis_Hauler/Full_Hull_Exterior',np.eye(3)),('le_guin','Le_Guin_Freighter/Exterior',np.array([[1,0,0],[0,0,1],[0,-1,0]]))]:
 g=Gltf(SRC/'models'/(source+'.gltf'));whole=np.concatenate([g.accessor(p['attributes']['POSITION']) for p in g.g['meshes'][0]['primitives']]);center=(whole.min(0)+whole.max(0))/2;parts=[];report=[];sourcefull=[]
 total=sum(g.g['accessors'][p['indices']]['count']//3 for p in g.g['meshes'][0]['primitives'])
 for pi,pr in enumerate(g.g['meshes'][0]['primitives']):
  orig=g.g['materials'][pr['material']]['name'];m=material(orig)
  if 'Decal' in orig:report.append({'material':orig,'omitted':'Separate decal overlay needs alpha-channel/shader baking; avoid opaque rectangular panels'});continue
  p={k:g.accessor(pr['attributes'][at]).astype(float) for k,at in [('v','POSITION'),('n','NORMAL'),('t','TANGENT'),('uv','TEXCOORD_0')]};p['i']=g.accessor(pr['indices']).reshape(-1,3).astype('uint32');p['v']=(p['v']-center)@rot.T*SCALE;p['n']=p['n']@rot.T;p['t'][:,:3]=p['t'][:,:3]@rot.T;p['uv']*=np.array(m['uv_scale']);p['material']=m['alias']
  # Exact attribute deduplication permits topological simplification without welding UV seams.
  packed=np.ascontiguousarray(np.column_stack([p[k] for k in ['v','n','t','uv']]),dtype='float32');unique,ii,inv=np.unique(packed,axis=0,return_index=True,return_inverse=True)
  for k in ['v','n','t','uv']:p[k]=p[k][ii]
  idx=np.ascontiguousarray(inv[p['i']].ravel(),dtype='uint32');v=np.ascontiguousarray(p['v'],dtype='float32');attrs=np.ascontiguousarray(np.column_stack([p['n'],p['uv']]),dtype='float32');weights=np.array([.015,.015,.015,.005,.005],dtype='float32');dest=np.empty_like(idx);err=C.c_float();target=max(60,round(len(idx)/3*75000/total))*3
  count=fn(dest.ctypes.data_as(U),idx.ctypes.data_as(U),len(idx),v.ctypes.data_as(F),len(v),12,attrs.ctypes.data_as(F),20,weights.ctypes.data_as(F),5,None,min(target,len(idx)),.006,32,C.byref(err))
  faces=dest[:count].reshape(-1,3);used,remap=np.unique(faces,return_inverse=True)
  for k in ['v','n','t','uv']:p[k]=p[k][used]
  p['i']=remap.reshape(-1,3);q=np.cross(p['v'][p['i'][:,1]]-p['v'][p['i'][:,0]],p['v'][p['i'][:,2]]-p['v'][p['i'][:,0]]);valid=np.linalg.norm(q,axis=1)>1e-6;p['i']=p['i'][valid]
  p['n']/=np.maximum(np.linalg.norm(p['n'],axis=1,keepdims=True),1e-9);p['t'][:,:3]-=p['n']*np.sum(p['n']*p['t'][:,:3],axis=1)[:,None];p['t'][:,:3]/=np.maximum(np.linalg.norm(p['t'][:,:3],axis=1,keepdims=True),1e-9);p['t'][:,3]=np.where(p['t'][:,3]<0,-1.,1.)
  parts.append(p);report.append({'material':orig,'source_triangles':len(idx)//3,'output_triangles':len(p['i']),'relative_error':err.value,'error_limit':.006,'attribute_weights':weights.tolist()});print(ship,orig,len(p['i']),err.value,flush=True)
 # Actual engine source material bounds guide exhaust positions; refined after preview.
 np.savez_compressed(D/(ship+'-parts.npz'),**{str(i)+'_'+k:np.asarray(v)for i,p in enumerate(parts)for k,v in p.items()});v=np.concatenate([p['v'] for p in parts]);lo=v.min(0);hi=v.max(0);name='expanse19_'+ship;points=[{'name':'center','translation':[0,0,0]},{'name':'above','translation':[0,float(hi[1]+5),0]},{'name':'aura','translation':[0,float(lo[1]-5),0]}]
 c.savegltf(name+'_editable',parts,points,compiler=False)
 eg=json.loads((D/(name+'_editable.gltf')).read_text());eg['images']=[];eg['textures']=[]
 for mm in eg['materials']:
  eg['images'].append({'uri':'textures/'+mm['name']+'_clr.png'});eg['textures'].append({'source':len(eg['images'])-1});mm['pbrMetallicRoughness']={'baseColorTexture':{'index':len(eg['textures'])-1},'baseColorFactor':[1,1,1,1]}
 write(D/(name+'_editable.gltf'),eg)
 meshes=[(p['v'][p['i']],p['uv'][p['i']],np.array(Image.open(D/'textures'/(p['material']+'_clr.png'))),[1,1,1,1],'OPAQUE')for p in parts]
 for label,view in [('oblique',[[.8,0,-.6],[-.3,.866,-.4],[.52,.5,.69]]),('side',[[0,0,1],[0,1,0],[-1,0,0]]),('aft',[[1,0,0],[0,1,0],[0,0,-1]])]:render(meshes,(950,700),np.array(view),fill=.85).save(A/(ship+'-'+label+'.png'))
 ships[ship]={'source':source,'source_center':center.tolist(),'source_to_game_rotation':rot.tolist(),'game_units_per_metre':SCALE,'counts':{'hull':sum(len(p['i'])for p in parts)},'hull_mesh':name+'_hull','ship_spatial':{'box':{'center':((lo+hi)/2).tolist(),'extents':((hi-lo)/2).tolist()},'radius':float(np.linalg.norm(v-(lo+hi)/2,axis=1).max()),'bounds_min':lo.tolist(),'bounds_max':hi.tolist()},'optimization':report,'editable_source':str(D/(name+'_editable.gltf'))}
write(A/'materials.json',mater);write(A/'integration-spec.json',{'status':'ART PREVIEW; COMPILATION PENDING','ships':ships,'game_directory':str(B/'game'),'runtime':'NOT RUN','excluded':{'Manitoba':'3752 triangle distant mesh unsuitable for close playable hull; detailed module level placement absent, no invented assembly.','Ceres':'Interior modules only, no exterior','Mausoleum':'Unverified multipart station assembly outside selected hauler scope'}})
