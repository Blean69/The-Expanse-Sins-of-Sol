"""User-directed final pass: exposed native Tachi bells and thermal-panel UVs."""
from update27_mars_assets import *
import shutil
SNAP=BUILD/'pre-epstein'

def snapshot():
 SNAP.mkdir(exist_ok=True)
 for key in ['storm','laconia','hephaestus']:
  cp=SNAP/(key+'-integration.json')
  if cp.exists():continue
  meta=read(AUD/(key+'-integration.json'))
  for name in set(meta['compiled_meshes'])|set(meta['copied_meshes']):
   d=SNAP/'meshes'/(name+'.mesh');d.parent.mkdir(exist_ok=True);shutil.copy2(GAME/'meshes'/(name+'.mesh'),d)
  write(cp,meta)

def meshrows(path):
 b=path.read_bytes();count=struct.unpack_from('<Q',b,53)[0];off=61;rows=[]
 for _ in range(count):
  r=struct.unpack_from('<12f?',b,off);rows.append(r[:-1]);off+=49+(8 if r[-1]else 0)
 ic=struct.unpack_from('<Q',b,off)[0];return np.array(rows),np.frombuffer(b,'<u4',ic,off+8).reshape(-1,3)

def cut(q,z):
 pts=[]
 for j,a in enumerate(q):
  b=q[(j+1)%3];da=a[2]-z;db=b[2]-z
  if da>=-1e-8:pts.append(a)
  if da*db<0:pts.append(a+(b-a)*da/(da-db))
 return [[pts[0],pts[j],pts[j+1]]for j in range(1,len(pts)-1)]

def surface(t,mat,smooth=40):
 p=frames(t,mat,smooth);q=np.cross(t[:,1]-t[:,0],t[:,2]-t[:,0]);axis=np.argmax(abs(q),axis=1);uv=np.zeros((len(t),3,2))
 # World-aligned projections in 36-unit repeats: fine thermal tiles, not
 # one large stretched photographic patch. Each triangle uses one projection.
 for a,pair in [(0,[2,1]),(1,[2,0]),(2,[0,1])]:uv[axis==a]=t[axis==a][:,:,pair]/36.
 p['uv']=uv.reshape(-1,2)
 du=uv[:,1]-uv[:,0];dv=uv[:,2]-uv[:,0];e1=t[:,1]-t[:,0];e2=t[:,2]-t[:,0];det=du[:,0]*dv[:,1]-du[:,1]*dv[:,0];tan=(e1*dv[:,1,None]-e2*du[:,1,None])/det[:,None];bit=(e2*du[:,0,None]-e1*dv[:,0,None])/det[:,None];tan=np.repeat(tan,3,axis=0);bit=np.repeat(bit,3,axis=0);n=p['n'];tan-=n*(n*tan).sum(1)[:,None];tan/=np.maximum(np.linalg.norm(tan,axis=1)[:,None],1e-12);p['t']=np.column_stack([tan,np.sign((np.cross(n,tan)*bit).sum(1))]);assert np.isfinite(p['t']).all();return p

def tachi_bell(center,diameter):
 rows,ix=loadmesh('expanse03_hull');info=read_mesh(BASE/'meshes/expanse03_hull.mesh');lo=np.array([-9.061,-19.151,-47.959]);hi=np.array([9.061,-1.027,-36.208]);scale=diameter/18.12108;origin=np.array([0.,-10.0899,-47.957733154296875]);parts=[];mapping={}
 for j,pr in enumerate(info['primitives']):
  q=ix.reshape(-1)[pr['vertex_index_start']:pr['vertex_index_start']+pr['vertex_index_count']].reshape(-1,3);p=rows[q,:3];q=q[((p>=lo)&(p<=hi)).all((1,2))]
  if not len(q):continue
  used,inv=np.unique(q,return_inverse=True);r=rows[used];mat='tachi_drive_'+str(j);mapping[mat]=info['materials'][pr['material_index']];parts.append({'v':(r[:,:3]-origin)*scale+center,'n':r[:,3:6],'t':r[:,6:10],'uv':r[:,10:12],'i':inv.reshape(-1,3),'material':mat})
 assert sum(len(p['i'])for p in parts)>1200
 return parts,mapping,center[2]+11.74821854*scale,5.03377*scale

def connector(hull,center,rootz,neckz,neckradius):
 a=np.arange(64)*2*np.pi/64;dirs=np.column_stack([np.cos(a),np.sin(a),np.zeros(64)]);root=[]
 for d in dirs:root.append(rayhit(hull,np.array([*center[:2],rootz])+d*50,-d))
 root=np.array(root);outer=root+dirs*.2;inner=root-dirs*.5;neck=dirs*(neckradius+.22)+[*center[:2],neckz];inside=dirs*(neckradius-.35)+[*center[:2],neckz]
 t=np.concatenate([rings([neck,outer]),rings([inner,inside]),rings([outer,inner]),rings([inside,neck])]);return t,{'root_z':rootz,'neck_z':neckz,'neck_radius':neckradius,'closed_shell':True,'root_crosses_measured_surface':True}

def build(key):
 snapshot();meta=read(SNAP/(key+'-integration.json'));name=meta['hull_mesh'];rows,ix=meshrows(SNAP/'meshes'/(name+'.mesh'));mi=read_mesh(SNAP/'meshes'/(name+'.mesh'));groups=[]
 for pr in mi['primitives']:
  mat=mi['materials'][pr['material_index']];q=ix.reshape(-1)[pr['vertex_index_start']:pr['vertex_index_start']+pr['vertex_index_count']].reshape(-1,3)
  if key=='storm':
   if not mat.endswith('storm_silver'):continue
   material='storm_silver'
  elif key=='laconia':
   if mat.endswith('_drive'):continue
   material=next(k for k in ['armor','orange','dark']if mat.endswith('_'+k))
  else:material=next(k for k in ['armor','orange','dark']if mat.endswith('_'+k))
  tri=rows[q,:3]
  if key=='storm':tri=np.array([r for t in tri for r in cut(t,-168.)])
  elif key=='laconia':tri=np.array([r for t in tri for r in cut(t,-62.)])
  elif key=='hephaestus':
   centers=np.array([p['translation'][:2]for p in meta['exhausts']]);which=np.min(np.linalg.norm(tri.mean(1)[:,None,:2]-centers[None,:,:],axis=2),axis=1)<18.
   tri=np.array([r for q,inside in zip(tri,which)for r in(cut(q,-117.)if inside else[q])])
  tri=tri[np.linalg.norm(np.cross(tri[:,1]-tri[:,0],tri[:,2]-tri[:,0]),axis=1)>1e-7]
  if len(tri):groups.append(surface(tri,material,55 if key=='storm' else 40))
 hull=np.concatenate([p['v'][p['i']]for p in groups]);connections=[];native={};bells=[]
 placements=([([0,0,-215.625],27.,-166.75)]if key=='storm'else[([0,0,-80.],22.,-60.)]if key=='laconia'else[([*p['translation'][:2],-136.],28.,-116.)for p in meta['exhausts']])
 for center,diameter,rootz in placements:
  bell,mp,front,r=tachi_bell(center,diameter);native.update(mp);col,proof=connector(hull,center,rootz,front+.15,r);groups.append(surface(col,'storm_dark'if key=='storm'else'dark',60));bells+=bell
  # Thin open metallic lip makes the native dark throat legible from side/stern.
  groups.append(frames(cylinder(np.array(center)+[0,0,-.22],np.array(center)+[0,0,.15],diameter*.505,64,inner=diameter*.483),'rim',50))
  connections.append({**proof,'opening_center':center,'diameter':diameter,'source_mesh':'expanse03_hull','source_part':'Connected Tachi bell component 192 and contained engine details','source_uvs_preserved':True})
 groups+=bells;points=copy.deepcopy(meta['meshpoints'])
 for pt in points:
  if pt['name'].startswith('exhaust'):
   j=int(pt['name'].split('.')[-1]);pt['translation']=list(placements[j][0]);pt['translation'][2]-=.4
 main=save(name,groups,points);meta['meshes']=[main]+[m for m in meta['meshes']if m['name']!=name];meta['colors']['rim']=[.46,.49,.53,1];meta['native_materials']=native if key!='storm'else{**{k:v for k,v in meta['native_materials'].items()if k!='drive'},**native};meta['meshpoints']=points;meta['exhausts']=[p for p in points if p['name'].startswith('exhaust')]
 allv=[p['v']for p in groups]
 for rig in meta['rigs']:
  B=np.column_stack([np.cross(rig['up'],rig['forward']),rig['up'],rig['forward']]);turret=rig['turret_override'];pos=np.array(rig['position'])
  for field in ['biaxial_base_mesh','biaxial_barrel_mesh','gimbal_mesh']:
   if field not in turret:continue
   rv,_=meshrows(SNAP/'meshes'/(turret[field]+'.mesh'));v=rv[:,:3]
   if field=='biaxial_barrel_mesh':v=v+turret['barrel_position']
   angles=[rig['yaw_arc']['min_angle'],0.,rig['yaw_arc']['max_angle']]if field=='gimbal_mesh'else[0.]
   for angle in angles:allv.append(v@Rotation.from_euler('y',angle,degrees=True).as_matrix().T@B.T+pos)
 v=np.concatenate(allv);lo=v.min(0);hi=v.max(0);meta['spatial']['radius']=float(np.linalg.norm(v,axis=1).max());meta['spatial']['box']={'center':((lo+hi)/2).tolist(),'extents':((hi-lo)/2).tolist()}
 meta['epstein_drive_pass']={'donor':'expanse03_hull (existing MCRN Tachi)','connections':connections,'native_triangles':sum(len(p['i'])for p in bells),'surface_uv_repeat_game_units':36.,'source_texture':'Generated thermal armor tile base color guided by user Paul Kiesling/show references','stage':'geometry ready'}
 for k in ['compiled','compiled_meshes','used_materials','arc_checks','compiled_assembled_triangles']:meta.pop(k,None)
 write(AUD/(key+'-integration.json'),meta);print(key,'exposed Tachi bells',len(placements),'hull triangles',main['triangles'],flush=True)

if __name__=='__main__':build(sys.argv[1])
