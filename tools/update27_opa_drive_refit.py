"""Art-only actual Tachi drive interior graft; source UVs/materials retained."""
import copy,json,numpy as np
import update27_opa_common as o
from update27_opa_geometry import loadparts,saveparts
from update26_command_art import unpack

DONOR='expanse03_hull'
CENTER=np.array([0.,-10.112395286560059,-49.331363677978516])

def subset(p,keep):
 q=copy.deepcopy(p);ids=p['i'][keep];used,inv=np.unique(ids,return_inverse=True)
 for k in ['v','n','t','uv']:q[k]=q[k][used]
 q['i']=inv.reshape(-1,3);return q

def extract():
 ps,_,_=unpack(o.BASE/'meshes'/(DONOR+'.mesh'));result=[]
 for p in ps:
  t=p['v'][p['i']];r=np.linalg.norm(t[:,:,:2]-CENTER[:2],axis=2)
  # Measured native engine recess: excludes outer hull collar/arms and decals.
  keep=(t[:,:,2].max(1)<-35.)&(r.max(1)<10.1)
  if keep.any():result.append(subset(p,keep))
 assert len(result)==2
 return result

def refit(name):
 report_path=o.AUD/(name+'-geometry.json');r=o.read(report_path)
 backup=o.SOURCE/(name+'-pre-drive-parts.npz');br=o.SOURCE/(name+'-pre-drive-geometry.json')
 if not r.get('actual_drive_donor'):
  backup.write_bytes((o.SOURCE/(name+'-parts.npz')).read_bytes());br.write_bytes(report_path.read_bytes())
 else:
  (o.SOURCE/(name+'-parts.npz')).write_bytes(backup.read_bytes());r=o.read(br)
 parts=loadparts(name);donor=extract();newparts=[];removed=0
 if name.endswith('dark_star'):
  # Existing circular engine spans roughly22gameunits radius, with its mouth
  # at the inherited exhaust point. Clear only its central recessed solid mesh.
  aperture=20.8;engine=np.array(r['exhausts'][0]['position'])
  for p in parts:
   tri=p['v'][p['i']];rad=np.linalg.norm(tri[:,:,:2]-engine[:2],axis=2);keep=~((rad.max(1)<aperture*1.02)&(tri[:,:,2].min(1)<engine[2]+37.))
   removed+=int((~keep).sum());newparts.append(subset(p,keep))
  engines=[(engine,aperture)]
 else:
  # Existing nozzle material contains96outer+96inner faces per engine.
  # Retain the shaped external bell while replacing its simple inner cone.
  for p in parts:
   if p['material'].endswith('_nozzle'):
    assert len(p['i'])==1536
    keep=np.zeros(len(p['i']),bool);keep[:768]=True;removed+=int((~keep).sum());newparts.append(subset(p,keep))
   else:newparts.append(p)
  engines=[(np.array(e['position']),e['aperture_radius']*.97)for e in r['exhausts']]
 donor_mats={};transforms=[]
 # One primitive per donor material merges all eight instances for cheap draw
 # calls while retaining exact native normals/tangents/UVs for each instance.
 max_radius=max(np.linalg.norm(p['v'][:,:2]-CENTER[:2],axis=1).max() for p in donor)
 for j,p in enumerate(donor):
  instances=[]
  for engine,aperture in engines:
   s=aperture/max_radius;q=copy.deepcopy(p);q['v']=(q['v']-CENTER)*s+engine
   # Pull the donor lip slightly inside the unchanged outer nozzle mouth.
   q['v'][:,2]+=.15*s;instances.append(q)
  m=name+f'_epstein_donor_{j}';donor_mats[m]=p['old_material'];merged={k:np.concatenate([q[k]for q in instances])for k in ['v','n','t','uv']};offset=0;ids=[]
  for q in instances:ids.append(q['i']+offset);offset+=len(q['v'])
  merged['i']=np.concatenate(ids);merged['material']=m;newparts.append(merged)
 for engine,aperture in engines:transforms.append({'mouth_center':engine.tolist(),'radius':aperture,'uniform_scale':aperture/max_radius,'donor_axis_origin':CENTER.tolist()})
 hull=np.concatenate([p['v'][p['i']]for p in newparts]);oldh=np.concatenate([p['v'][p['i']]for p in parts]);assert (hull.max((0,1))<=oldh.max((0,1))+1e-3).all();assert(hull.min((0,1))>=oldh.min((0,1))-1e-3).all()
 count=o.safety(hull,r['rigs']);assert count==r['checks']['sampled_muzzle_rays_clear']
 hashes={str(o.BASE/'meshes'/(DONOR+'.mesh')):o.sha(o.BASE/'meshes'/(DONOR+'.mesh'))}
 for m in donor_mats.values():
  f=o.BASE/'mesh_materials'/(m+'.mesh_material');hashes[str(f)]=o.sha(f)
  for k,v in o.read(f).items():
   if k.endswith('_texture'):f=o.BASE/'textures'/(v+'.dds');hashes[str(f)]=o.sha(f)
 r['actual_drive_donor']={'donor_mesh':DONOR,'sources_sha256':hashes,'selection':'All face vertices Z<-35 and radialdistance<10.1 about Tachi exhaust XY;2 actual source materials, original UVs/normals/tangents','donor_triangles_per_engine':sum(len(p['i'])for p in donor),'removed_old_interior_triangles':removed,'new_triangles':sum(len(p['i'])for p in newparts),'instances':transforms,'original_spatial_meshpoints_rigs_exhausts_unchanged':True,'sampled_rays_rechecked':count};r['donor_materials']=donor_mats
 saveparts(name,newparts,r['meshpoints'],r);print(json.dumps({'id':name,'refit':r['actual_drive_donor']}),flush=True)

if __name__=='__main__':
 o.dirs()
 for name in ['expanse27_dark_star','expanse27_behemoth']:refit(name)

def closeups():
 from PIL import Image
 from polish_ui import render
 for name in ['expanse27_dark_star','expanse27_behemoth']:
  r=o.read(o.AUD/(name+'-geometry.json'));engine=r['actual_drive_donor']['instances'][0];center=np.array(engine['mouth_center']);radius=engine['radius'];meshes=[]
  for p in loadparts(name):
   tri=p['v'][p['i']];cent=tri.mean(1);keep=(np.linalg.norm(cent[:,:2]-center[:2],axis=1)<radius*1.38)&(cent[:,2]<center[2]+radius*2.1)
   if not keep.any():continue
   mat=p['material']
   if mat in r.get('donor_materials',{}):m=o.read(o.BASE/'mesh_materials'/(r['donor_materials'][mat]+'.mesh_material'));source=o.BASE/'textures'/(m['base_color_texture']+'.dds')
   else:source=o.SOURCE/'textures'/(mat+'_clr.png')
   tex=np.array(Image.open(source).convert('RGBA').resize((1024,1024)));meshes.append((tri[keep],p['uv'][p['i'][keep]],tex,[1,1,1,1],'OPAQUE'))
  render(meshes,(1200,1000),np.array([[1,0,0],[0,.966,-.259],[0,-.259,-.966]])).save(o.BUILD/(name+'-epstein-closeup.png'))

if __name__=='__main__':closeups()
