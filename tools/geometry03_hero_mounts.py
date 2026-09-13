"""Measure actual supplied hero assemblies; unresolved equipment remains explicit."""
from common import *
from scipy.spatial import cKDTree
from PIL import Image,ImageDraw
out=ROOT/'assets/derived/geometry03-b/hero';audit=ROOT/'audit/geometry03-b';orig=Gltf(ROOT/'assets/derived/geometry03-b/hero-master/Rocinante_(The_Expanse).gltf');deployed=Gltf(out/'rocinante_stand_free_deployed.gltf');meta=read(audit/'hero-mount-metadata.json');norm=meta['normalization'];C=np.array(norm['source_to_game_rotation']);center=np.array(norm['source_rotated_center']);scale=norm['scale'];target=np.array(norm['target_center']);by_mesh={n['mesh']:i for i,n in enumerate(deployed.g['nodes'])}
def descendants(i):
 ids=[i]
 for c in orig.g['nodes'][i].get('children',[]):ids.extend(descendants(c))
 return ids
def verts(i):
 vv=[]
 for ni in descendants(i):
  n=orig.g['nodes'][ni]
  if 'mesh' not in n:continue
  di=by_mesh.get(n['mesh'])
  if di is None:continue
  for p in deployed.g['meshes'][n['mesh']]['primitives']:vv.append(deployed.positions(di,p))
 v=np.concatenate(vv);return (v@C.T-center)*scale+target
def vertices_normals(i):
 vv=[];nn=[]
 for ni in descendants(i):
  node=orig.g['nodes'][ni]
  if 'mesh' not in node:continue
  di=by_mesh.get(node['mesh'])
  if di is None:continue
  for primitive in deployed.g['meshes'][node['mesh']]['primitives']:
   vv.append((deployed.positions(di,primitive)@C.T-center)*scale+target)
   n=deployed.accessor(primitive['attributes']['NORMAL'])@np.linalg.inv(deployed.world[di][:3,:3])@C.T;n/=np.linalg.norm(n,axis=1)[:,None];nn.append(n)
 return np.concatenate(vv),np.concatenate(nn)
from collections import Counter
def plane_axes(forward):
 up=np.array([0.,1.,0.]);up-=forward*np.dot(up,forward);up/=np.linalg.norm(up);return np.cross(up,forward),up
def dominant_normal(n,mask=None):
 selected=n if mask is None else n[mask];key=Counter(map(tuple,np.round(selected,4))).most_common(1)[0][0];axis=n[np.all(np.round(n,4)==key,axis=1)].mean(0);return axis/np.linalg.norm(axis)
wrappers=[(111,117,140),(174,180,200),(212,218,238),(250,256,276),(288,294,314),(326,332,352)];mounts=[]
for i,(housing,barrel,frame) in enumerate(wrappers):
 bv,bn=vertices_normals(barrel);forward=dominant_normal(bn);projection=bv@forward;cap=np.unique(np.round(bv[projection>projection.max()-.001],6),axis=0);right,up=plane_axes(forward);xy=cap@np.column_stack([right,up]);cap_center=(xy.min(0)+xy.max(0))/2;tip=right*cap_center[0]+up*cap_center[1]+forward*np.mean(cap@forward);tip+=forward*.04
 assert len(cap)>100 and np.ptp(cap@forward)<.001
 mounts.append({'index':i,'source_housing_node':housing,'source_cannon_node':barrel,'source_frame_node':frame,'weapon_position':tip.tolist(),'muzzle_hull':tip.tolist(),'forward':forward.tolist(),'up':up.tolist(),'tip_plane_unique_vertices':len(cap),'tip_plane_flatness':float(np.ptp(cap@forward)),'geometry_basis':'Visually isolated cannon1 contains actual long barrel. Most frequent authored normal identifies barrel cap plane; center from full cap circumference bounds in that plane plus 0.04 outward clearance. cannon2 is a trunnion block and is not used. Source deployed pose is retained, including reversed #3.','status':'Static source barrel cap measured; emission/clearance NOT RUN; not a rotating turret pivot'})
# Fit the full nozzle opening in its authored axial plane. A minimum game-Z
# slice incorrectly selected one edge because the nozzle is slightly tilted.
ev,en=vertices_normals(2);axis=dominant_normal(en,en[:,2]<-.9);projection=ev@axis;rim=np.unique(np.round(ev[projection>projection.max()-.001],6),axis=0);right,up=plane_axes(axis);xy=rim@np.column_stack([right,up]);guess=(xy.min(0)+xy.max(0))/2;radii=np.linalg.norm(xy-guess,axis=1);ordered=np.sort(radii);gaps=np.diff(ordered);split=(ordered[np.argmax(gaps)]+ordered[np.argmax(gaps)+1])/2;inner=xy[radii<split];fit=np.linalg.lstsq(np.column_stack([2*inner,np.ones(len(inner))]),(inner*inner).sum(1),rcond=None)[0];radius=np.sqrt(fit[2]+np.dot(fit[:2],fit[:2]));nozzle=right*fit[0]+up*fit[1]+axis*np.mean(rim@axis);exhaust=(nozzle+axis*.1).tolist();residual=float(abs(np.linalg.norm(inner-fit[:2],axis=1)-radius).max());angles=np.sort(np.arctan2(*(inner-fit[:2]).T[::-1]));gap=float(np.diff(np.r_[angles,angles[0]+2*np.pi]).max());assert residual<.01 and gap<.7 and len(inner)>=60
exhaust_metadata={'position':exhaust,'opening_center':nozzle.tolist(),'forward':axis.tolist(),'up':up.tolist(),'source_nodes':[2,3,4,5,6],'basis':'Full aftmost s3_3c authored axial plane; inner/outer rim separated by largest radial gap, inner circumference least-squares circle fitted. 0.1 outward clearance.','rim_unique_vertices':len(rim),'inner_rim_vertices':len(inner),'opening_radius':float(radius),'circle_max_radial_residual':residual,'maximum_angular_gap_radians':gap,'plane_flatness':float(np.ptp(rim@axis)),'runtime':'NOT RUN'}
# The archive does not identify torpedo or railgun parts by name. Avoid reusing
# Tachi positions or calling an antenna an authored railgun.
allnames=[{'node':i,'name':n.get('name')} for i,n in enumerate(orig.g['nodes']) if any(w in n.get('name','').lower() for w in ['torpedo','rail','launcher'])]
result={'status':'Static hero muzzle estimates only; runtime NOT RUN','pdc_mounts':mounts,'exhaust':exhaust_metadata,'railgun':{'status':'UNRESOLVED: no railgun-labelled geometry found; antenna-like nose parts must not be misidentified','candidate_position':None},'torpedo_bays':{'status':'UNRESOLVED: no torpedo/launcher-labelled geometry found; requires visual annotation of source parts','candidate_positions':[]},'equipment_name_matches':allnames,'hero_scale':scale};write(audit/'hero-equipment-mounts.json',result)
# Front/side orthographic view annotated with actual six measured muzzles.
static=Gltf(out/'expanse03_hero_static.gltf');tris=[]
for p in static.g['meshes'][0]['primitives']:
 v=static.accessor(p['attributes']['POSITION']);v[:,2]*=-1;idx=static.accessor(p['indices']).flatten().reshape(-1,3)
 for q in v[idx]:tris.append((q,p['material']))
im=Image.new('RGB',(1400,900),'#151b24');dr=ImageDraw.Draw(im);colors=['#515357','#999c9f','#b25410']
for panel,haxis in enumerate([0,1]):
 cx=350+700*panel;sortedtris=sorted(tris,key=lambda item:item[0][:,1-haxis].mean())
 for q,mat in sortedtris:dr.polygon([(float(cx+p[haxis]*6),float(430-p[2]*6)) for p in q],fill=colors[mat],outline=colors[mat])
 for r in mounts:
  p=r['muzzle_hull'];x=cx+p[haxis]*6;y=430-p[2]*6;dr.ellipse((x-6,y-6,x+6,y+6),outline='#57e6ff',width=2);dr.text((x+8,y),str(r['index']),fill='#57e6ff')
 p=exhaust;x=cx+p[haxis]*6;y=430-p[2]*6;dr.ellipse((x-6,y-6,x+6,y+6),outline='#ff6666',width=2)
dr.text((20,20),'HERO STATIC DEPLOYED SOURCE POSE / SIX CANNON-TIP ESTIMATES / NOT RUNTIME PROOF',fill='white');dr.text((20,850),'Torpedo and railgun geometry identities remain unresolved. Red marker = named s3 aft rim exhaust estimate.',fill='white');im.save(audit/'hero-equipment-view.png');print('Six actual named PDC cannon-tip estimates; exhaust measured; railgun/torpedo identities unresolved')
# Add measured static weapon points and replace the old bounding-box exhaust
# placeholder in this new compiler derivative only.
from scipy.spatial.transform import Rotation
cg=read(out/'expanse03_hero_static.gltf');ps=meta['meshpoints']['hero_static'];ps=[p for p in ps if not p['name'].startswith('weapon.hero_pdc_')]
for p in ps:
 if p['name']=='exhaust.0':
  p['translation']=exhaust;B=np.column_stack([np.cross(exhaust_metadata['up'],exhaust_metadata['forward']),exhaust_metadata['up'],exhaust_metadata['forward']]);p['rotation']=Rotation.from_matrix(B).as_quat().tolist()
for r in mounts:
 B=np.column_stack([np.cross(r['up'],r['forward']),r['up'],r['forward']]);q=Rotation.from_matrix(B).as_quat();ps.append({'name':f'weapon.hero_pdc_{r["index"]}','translation':r['muzzle_hull'],'rotation':q.tolist()});r['mesh_point']=f'weapon.hero_pdc_{r["index"]}'
cg['nodes']=cg['nodes'][:1];cg['nodes'][0]['children']=[]
for point in ps:
 cp=__import__('copy').deepcopy(point);cp['translation'][2]*=-1
 if 'rotation' in cp:cp['rotation'][0]*=-1;cp['rotation'][1]*=-1
 cg['nodes'][0]['children'].append(len(cg['nodes']));cg['nodes'].append(cp)
meta['meshpoints']['hero_static']=ps;meta['measured_static_weapon_mounts']=mounts;meta['exhaust_geometry']=result['exhaust'];write(out/'expanse03_hero_static.gltf',cg);write(audit/'hero-mount-metadata.json',meta);write(audit/'hero-equipment-mounts.json',result)
