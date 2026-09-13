"""Private, full-silhouette Europa's Bane derivative with proven articulated PDCs.
Read-only extracted source; Unreal layered material response approximated explicitly.
"""
from pathlib import Path
import json,copy,hashlib,numpy as np
from PIL import Image
from scipy.spatial.transform import Rotation
from common import Gltf,write
import update12_scirocco_common as c
from update14_pdc_arcs import Rays,sample,choose
R=Path(__file__).resolve().parents[1];D=R/'assets/derived/update19-europa';A=R/'audit/update19-europa';B=R/'build/update19-europa';S=Path('/run/media/haker/NVME 2/expanse-extracted/OPA-pirate-ships');MAIN=Path('/run/media/haker/NVME 2/expanse-mod');DONOR=Path('/run/media/haker/NVME 2/expanse-workers/tachi-one-pdc');P='expanse19_europa';c.OUT=D
for p in [D,A,B,D/'texture-sources']:p.mkdir(parents=True,exist_ok=True)
g=Gltf(S/'meshes/Europa_Bane_Exterior_A.gltf');mm={p.stem.lower():(p,json.loads(p.read_text()))for p in (S/'raw-export').rglob('*.json')};allv=np.concatenate([g.accessor(p['attributes']['POSITION'])for p in g.g['meshes'][0]['primitives']]);center=(allv.min(0)+allv.max(0))/2;rot=np.diag([-1.,1.,-1.]);scale=1.875
parts={'hull':[]};mats={};omitted=[];deps={}
def cv(v):return (np.asarray(v)-center)@rot*scale
def rgba(im,size):return np.asarray(im.convert('RGBA').resize(size,Image.Resampling.LANCZOS)).copy()
def readtex(mat,key):
 q=mat.get('Textures',{}).get(key)
 if not q:return None
 p=S/'raw-export'/(q.split('.')[0]+'.png');deps[str(p)]=hashlib.sha256(p.read_bytes()).hexdigest();return Image.open(p)
def factor(d,key,default):
 color=d.get('Parameters',{}).get('Colors',{}).get(key)
 return np.array([color[k]for k in ['R','G','B']])if color else np.array(default)
for j,pr in enumerate(g.g['meshes'][0]['primitives']):
 name=g.g['materials'][pr['material']]['name'];idx=g.accessor(pr['indices']).reshape(-1,3)
 if 'PDC01' in name or 'Decal' in name:
  omitted.append({'material':name,'triangles':len(idx),'reason':'static weapons replaced with articulated retrofit'if'PDC01'in name else'Unreal decal shader excluded; avoids opaque floating decal cards'});continue
 pp={k:g.accessor(pr['attributes'][at]).astype(float)for k,at in [('v','POSITION'),('n','NORMAL'),('t','TANGENT'),('uv','TEXCOORD_0')]};pp['v']=cv(pp['v']);pp['n']=pp['n']@rot;pp['n']/=np.linalg.norm(pp['n'],axis=1)[:,None];pp['t'][:,:3]=pp['t'][:,:3]@rot;pp['t'][:,:3]-=pp['n']*np.sum(pp['t'][:,:3]*pp['n'],axis=1)[:,None];ln=np.linalg.norm(pp['t'][:,:3],axis=1);assert ln.min()>1e-7;pp['t'][:,:3]/=ln[:,None];pp['t'][:,3]=np.where(pp['t'][:,3]<0,-1,1)
 # Drop only float32-collapsed microslivers, retaining every meaningful hull face.
 vv=pp['v'].astype('float32').astype(float);tt=vv[idx];valid=np.linalg.norm(np.cross(tt[:,1]-tt[:,0],tt[:,2]-tt[:,0]),axis=1)>1e-5;pp['i']=idx[valid];matid=f'{P}_material_{j:02d}';pp['material']=matid;parts['hull'].append(pp)
 path,mat=mm[name.lower()];deps[str(path)]=hashlib.sha256(path.read_bytes()).hexdigest();im=readtex(mat,'Base Color Texture');size=(1024,1024)if im else(4,4);clr=rgba(im,size)if im else np.full((*size[::-1],4),255,np.uint8)
 tint=factor(mat,'Base Color Tint',factor(mat,'Albedo Color',[1,1,1]));paint=factor(mat,'Paint Color',[1,1,1]);tint*=paint
 # Color parameter values are linear; convert multiplier to sRGB before baking source BC.
 tint=np.where(tint<=.0031308,tint*12.92,1.055*np.maximum(tint,0)**(1/2.4)-.055);clr[:,:,:3]=np.clip(clr[:,:,:3]*tint,0,255);clr[:,:,3]=255
 Image.fromarray(clr).save(D/'texture-sources'/(matid+'_clr.png'))
 normalim=readtex(mat,'Normal Texture');nrm=rgba(normalim,size)[:,:,:3]if normalim else np.full((*size[::-1],3),[128,128,255],np.uint8);nn=nrm.astype(float)/127.5-1;nn/=np.maximum(np.linalg.norm(nn,axis=2,keepdims=True),1e-9);Image.fromarray(np.clip((nn+1)*127.5,0,255).astype('uint8')).save(D/'texture-sources'/(matid+'_nrm.png'))
 orm=np.full((*size[::-1],4),[255,185,75,255],np.uint8);Image.fromarray(orm).save(D/'texture-sources'/(matid+'_orm.png'))
 emiss=readtex(mat,'Emissive Texture');mask=np.zeros((*size[::-1],4),np.uint8)
 if emiss is not None:mask[:,:,2]=rgba(emiss,size)[:,:,:3].max(2)
 Image.fromarray(mask).save(D/'texture-sources'/(matid+'_msk.png'))
 mats[matid]={'source_material':name,'source_texture_dimensions':list(im.size)if im else None,'texture_size':size,'base_color_texture':matid+'_clr','occlusion_roughness_metallic_texture':matid+'_orm','normal_texture':matid+'_nrm','mask_texture':matid+'_msk','emissive_factor':1.0,'material_approximation':'Original UV0 and color/normal retained; scalar tint and whole-panel paint approximation. Neutral ORM replaces undocumented Unreal masks; alpha decal cards excluded.'}
# Proven compact independent base/barrel geometry, at roughly source PDC envelope.
donor=json.loads((DONOR/'audit/polish-b/mount-metadata.json').read_text())['rigs'][0];ps=3.0;off=np.array(donor['turret_override']['barrel_position'])*ps;mu=np.array(donor['turret_override']['muzzle_positions'][0])*ps
for kind in ['base','barrel']:
 gg=Gltf(DONOR/'assets/derived/polish-b'/f'expanse_polish_pdc_0_{kind}.gltf');parts['pdc_'+kind]=[]
 for pr in gg.g['meshes'][0]['primitives']:
  pp={k:gg.accessor(pr['attributes'][at]).astype(float)for k,at in [('v','POSITION'),('n','NORMAL'),('t','TANGENT'),('uv','TEXCOORD_0')]};pp['v'][:,2]*=-1;pp['v']*=ps;pp['n'][:,2]*=-1;pp['t'][:,2:4]*=-1;pp.update(i=gg.accessor(pr['indices']).reshape(-1,3),material='mcrn_tachi_material');parts['pdc_'+kind].append(pp)
tri=np.concatenate([p['v'][p['i']]for p in parts['hull']]);ray=Rays(tri,B/'rays');rigs=[];supports=[]
def cylinder(a,b,r=2.8):
 axis=b-a;axis/=np.linalg.norm(axis);u=np.cross(axis,[0,0,1]);u/=np.linalg.norm(u);w=np.cross(axis,u);vv=np.cos(np.arange(20)*np.pi/10)[:,None]*u*r+np.sin(np.arange(20)*np.pi/10)[:,None]*w*r
 for i in range(20):
  j=(i+1)%20;supports.extend([[a+vv[i],a+vv[j],b+vv[j]],[a+vv[i],b+vv[j],b+vv[i]],[a,a+vv[j],a+vv[i]],[b,b+vv[i],b+vv[j]]])
locations=[([0,11,-97],[0,1,0]),([0,-20,-97],[0,-1,0]),([-22,6,14],[-1,0,0]),([22,6,14],[1,0,0]),([-19,-18,-50],[-.707,-.707,0]),([19,-18,-50],[.707,-.707,0])]
for i,(pos,normal) in enumerate(locations):
 up=np.array(normal)@rot;up/=np.linalg.norm(up);origin=cv(pos)+up*100;distance=ray([origin],[-up],300)[0];assert distance>0;contact=origin-up*distance;pivot=contact+up*5;basis=np.column_stack([np.cross(up,[0,0,1]),up,[0,0,1]]);cylinder(contact-up*.7,pivot);name=f'{P}_pdc_{i}'
 mount={'weapon':name,'mesh_point':'child.'+name,'weapon_position':pivot.tolist(),'up':up.tolist(),'forward':[0,0,1],'yaw_arc':{'min_angle':-180.,'max_angle':180.},'pitch_arc':{'min_angle':-85.,'max_angle':-35.}};turret={'type':'biaxial','biaxial_base_mesh':P+'_pdc_base','biaxial_barrel_mesh':P+'_pdc_barrel','barrel_position':off.tolist(),'muzzle_positions':[mu.tolist()]}
 ya=np.arange(-180,181,4.);pa=np.arange(-85,-14,2.);mask,_,_=sample(ray,mount,turret,ya,pa,3.);arcs,area=choose(mask,ya,pa);mount.update(arcs);yy=arcs['yaw_arc'];pp=arcs['pitch_arc'];blocked,ex,n=sample(ray,mount,turret,np.arange(yy['min_angle'],yy['max_angle']+.01,1),np.arange(pp['min_angle'],pp['max_angle']+.01,1),3.);assert not blocked.any(),ex
 rigs.append({'index':i,'kind':'pdc','mount':mount,'basis_columns':basis.tolist(),'yaw_pivot_hull':pivot.tolist(),'pitch_pivot_hull':(pivot+basis@off).tolist(),'muzzle_hull':(pivot+basis@(off+mu)).tolist(),'turret_override':turret,'measured_contact':contact.tolist(),'source_location':pos,'arc_validation':{'blocked':0,'rays':n,'step_degrees':1,'aim_envelope_degrees':3},'skin_alias_map':[{'mesh_alias_name':P+'_pdc_'+k,'mesh_definition':{'mesh':P+'_pdc_'+k,'shader':'ship','is_shadow_blocker':True}}for k in ['base','barrel']]});print(name,arcs,flush=True)
parts['hull'].append(c.frames(np.array(supports),P+'_support'))
ports=[]
for x in [-8.,8.]:
 origin=cv([x,-7,-145]);hit=ray([origin],[[0,0,-1]],150)[0];assert hit>0;contact=origin-np.array([0,0,hit]);ports.append({'position':(contact+[0,0,1]).tolist(),'forward':[0,0,1],'up':[0,1,0],'source':'Measured forward hull launcher retrofit, exact screen tube correspondence unverified'})
ray.close();exhausts=[]
for pos in [[0,-4.1,33.4],[-17.06,5.8,40.6],[17.09,5.76,40.6],[0,-23.8,40.6]]:exhausts.append({'position':cv(pos).tolist(),'forward':[0,0,-1],'up':[0,1,0]})
points=[{'name':'center','translation':[0,0,0]},{'name':'above','translation':[0,60,0]},{'name':'aura','translation':[0,-60,0]}]
for r in rigs:points.append({'name':r['mount']['mesh_point'],'translation':r['yaw_pivot_hull'],'rotation':Rotation.from_matrix(r['basis_columns']).as_quat().tolist()})
for i,p in enumerate(ports):points.append({'name':f'weapon.torpedo.{i}','translation':p['position']})
points.append({'name':'weapon.boarding.0','translation':ports[0]['position']})
for i,p in enumerate(exhausts):points.append({'name':f'exhaust.{i}','translation':p['position'],'rotation':[0,1,0,0]})
sourceframes={};assembled=copy.deepcopy(parts['hull'])
for kind,pp in parts.items():
 c.savegltf(P+('_bane_hull'if kind=='hull'else'_'+kind),pp,points if kind=='hull'else[]);sourceframes[kind]={str(i):{k:p[k].tolist()for k in ['v','n','t','uv']}for i,p in enumerate(pp)}
for r in rigs:
 basis=np.array(r['basis_columns']);origin=np.array(r['yaw_pivot_hull'])
 for kind,offset in [('pdc_base',np.zeros(3)),('pdc_barrel',off)]:
  for pp in parts[kind]:
   p=copy.deepcopy(pp);p['v']=(p['v']+offset)@basis.T+origin;p['n']=p['n']@basis.T;p['t'][:,:3]=p['t'][:,:3]@basis.T;assembled.append(p)
c.savegltf(P+'_editable',assembled,compiler=False);v=np.concatenate([p['v']for p in assembled]);lo=v.min(0);hi=v.max(0);bc=(lo+hi)/2
meta={'status':'COMPILER PENDING','game_directory':str(B/'game'),'hull_mesh':P+'_bane_hull','rigs':rigs,'ship_spatial':{'box':{'center':bc.tolist(),'extents':((hi-lo)/2).tolist()},'radius':float(np.linalg.norm(v-bc,axis=1).max()),'bounds_min':lo.tolist(),'bounds_max':hi.tolist()},'equipment':{'light_torpedo_ports':ports,'torpedo_ports':ports,'light_torpedo_port':ports[0],'exhaust':exhausts[0],'exhausts':exhausts},'counts':{k:sum(len(p['i'])for p in pp)for k,pp in parts.items()},'assembled_triangle_total':sum(len(p['i'])for p in assembled),'meshpoints':{k:points if k=='hull'else[]for k in parts},'editable_source':str(D/(P+'_editable.gltf')),'source_model_triangles':149638,'omitted_geometry':omitted,'scale':{'source_metres':np.ptp(allv,axis=0).tolist(),'game_units_per_metre':scale,'basis':'180 degrees Y; source engine cones +Z, ship forward -Z; game forward +Z','centering':center.tolist(),'comparison':'Same1.875gameunits/metre as current42mTachi78.75game-unitlength; Europa179m becomes335.35game-unitlength.'},'runtime':'NOT RUN'}
write(D/'retained-source-frames.json',sourceframes);write(D/'materials.json',mats);write(A/'integration-spec.json',meta);write(A/'source-dependencies.json',{'source_files':{str(p):hashlib.sha256(p.read_bytes()).hexdigest()for p in [S/'meshes/Europa_Bane_Exterior_A.gltf',S/'meshes/Europa_Bane_Exterior_A.bin']},'materials':deps,'originals_untouched':True});print(meta['counts'],meta['assembled_triangle_total'])
