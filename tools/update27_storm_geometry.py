"""Correct frozen Storm stern connection, smooth small surface noise, enlarge15%."""
from update27_mars_assets import *
from scipy.sparse import csr_matrix
NAME='expanse24_storm_hull';SCALE=1.15
v,ix=loadmesh(NAME);info=read_mesh(BASE/'meshes'/(NAME+'.mesh'));hulls=[];drive=[]
for p in info['primitives']:
 q=ix.reshape(-1)[p['vertex_index_start']:p['vertex_index_start']+p['vertex_index_count']].reshape(-1,3)
 (drive if info['materials'][p['material_index']].endswith('storm_drive')else hulls).append(v[q,:3])
t=np.concatenate(hulls);old=t.copy();oldmeta=read(MAIN/'audit/update24-storm/integration-spec.json');u,inv=np.unique(np.round(t.reshape(-1,3),5),axis=0,return_inverse=True);ii=inv.reshape(-1,3);e=np.concatenate([ii[:,[0,1]],ii[:,[1,2]],ii[:,[2,0]]]);e=np.concatenate([e,e[:,::-1]]);A=coo_matrix((np.ones(len(e)),(e[:,0],e[:,1])),shape=(len(u),len(u))).tocsr();A.data[:]=1;A=diags(1/np.maximum(np.array(A.sum(1)).ravel(),1))@A
# Local smoothing changes actual printable bumps, not just shader normals. Protect
# the keel tip, stern fitting surface and a 35-unit neighborhood around each gun.
protect=(u[:,2]>145)|(u[:,2]<-140)
for rig in oldmeta['rigs']:protect|=np.linalg.norm(u-rig['position'],axis=1)<35
original=u.copy()
for _ in range(15):
 for rate in [.32,-.31]:
  delta=(A@u-u)*rate;delta[protect]=0;u+=delta
delta=u-original;length=np.linalg.norm(delta,axis=1);u=original+delta*np.minimum(1.,1.25/np.maximum(length,1e-12))[:,None];shift=np.linalg.norm(u-original,axis=1);t=u[ii];q=np.cross(t[:,1]-t[:,0],t[:,2]-t[:,0]);t=t[np.linalg.norm(q,axis=1)>1e-7]
# Measured elliptical body root; a capped annular collar intersects both the
# original hull and the engine flange, removing the prior open air gap.
angles=np.arange(64)*2*np.pi/64;dirs=np.column_stack([np.cos(angles),np.sin(angles),np.zeros(64)]);root=[]
for d in dirs:root.append(rayhit(t,d*100+[0,0,-145],-d))
root=np.array(root);rad=np.linalg.norm(root[:,:2],axis=1);outer0=root+dirs*.4;inner0=root-dirs*.7
outer1=dirs*14.0+[0,0,-187.0];inner1=dirs*12.9+[0,0,-187.0]
# Outer taper, inner lining, fore and aft annuli: continuous closed connector.
collar=np.concatenate([rings([outer1,outer0]),rings([inner0,inner1]),rings([outer0,inner0]),rings([inner1,outer1])]);parts=[frames(t*SCALE,'storm_silver',smooth=55),frames(collar*SCALE,'storm_dark',smooth=60)]
# Read original UV/material-bearing drive instead of losing its machinery colors.
for p in info['primitives']:
 if not info['materials'][p['material_index']].endswith('storm_drive'):continue
 q=ix.reshape(-1)[p['vertex_index_start']:p['vertex_index_start']+p['vertex_index_count']].reshape(-1,3);used,remap=np.unique(q,return_inverse=True);r=v[used];parts.append({'v':r[:,:3]*SCALE,'n':r[:,3:6],'t':r[:,6:10],'uv':r[:,10:12],'i':remap.reshape(-1,3),'material':'drive'})
points=[]
for p in info['meshpoints']:
 points.append({'name':p['name'],'translation':(np.array(p['position'])*SCALE).tolist(),'rotation':Rotation.from_matrix(np.array(p['rotation']).reshape(3,3).T).as_quat().tolist()})
rigs=copy.deepcopy(oldmeta['rigs'])
for r in rigs:
 r['position']=(np.array(r['position'])*SCALE).tolist();turret=r['turret_override'];turret['barrel_position']=(np.array(turret['barrel_position'])*SCALE).tolist();turret['muzzle_positions']=(np.array(turret['muzzle_positions'])*SCALE).tolist()
 for kind in ['base','barrel']:turret['biaxial_'+kind+'_mesh']='expanse27_storm_pdc_'+kind
rail=copy.deepcopy(oldmeta['fixed_rail']);rail['weapon_position']=(np.array(rail['weapon_position'])*SCALE).tolist()
mesh=save(NAME,parts,points);meshes=[mesh];native_materials={'drive':'expanse24_storm_hull_storm_drive'}
for kind in ['base','barrel']:
 original_name='expanse24_storm_pdc_'+kind;rr,idx=loadmesh(original_name);mi=read_mesh(BASE/'meshes'/(original_name+'.mesh'));pp=[]
 for pr in mi['primitives']:
  ids=idx.reshape(-1)[pr['vertex_index_start']:pr['vertex_index_start']+pr['vertex_index_count']].reshape(-1,3);used,remap=np.unique(ids,return_inverse=True);rows=rr[used];mat=mi['materials'][pr['material_index']];native_materials[mat]=mat;pp.append({'v':rows[:,:3]*SCALE,'n':rows[:,3:6],'t':rows[:,6:10],'uv':rows[:,10:12],'i':remap.reshape(-1,3),'material':mat})
 ppts=[{'name':p['name'],'translation':(np.array(p['position'])*SCALE).tolist(),'rotation':Rotation.from_matrix(np.array(p['rotation']).reshape(3,3).T).as_quat().tolist()}for p in mi['meshpoints']];meshes.append(save('expanse27_storm_pdc_'+kind,pp,ppts))
allv=np.concatenate([p['v']for p in parts]);lo=allv.min(0);hi=allv.max(0);frozen=read(BASE/'entities/expanse24_gathering_storm.unit');patch=copy.deepcopy(frozen['spatial']);patch['radius']*=SCALE;patch['box']['center']=(np.array(patch['box']['center'])*SCALE).tolist();patch['box']['extents']=(np.array(patch['box']['extents'])*SCALE).tolist()
meta={'id':'storm','hull_mesh':NAME,'meshes':meshes,'meshpoints':points,'rigs':rigs,'fixed_rail':rail,'colors':{'storm_silver':[.40,.435,.46,1],'storm_dark':[.16,.18,.20,1]},'native_materials':native_materials,'copied_meshes':{},'scale':SCALE,'spatial':patch,'counts':{'hull':mesh['triangles'],'source_hull':len(old),'collar':len(collar)},'collar':{'root_z':-145*SCALE,'root_measured_radii':rad.tolist(),'root_penetration':.7*SCALE,'flange_outer_radius':14*SCALE,'flange_inner_radius':12.9*SCALE,'engine_opening_radius':13.5*SCALE,'rim_z':-187*SCALE,'closed_shell':True,'connection':'Root annulus crosses measured body surface; aft annulus crosses retained engine flange. Continuous64-segment capped collar.'},'smoothing':{'iterations':15,'lambda':.32,'mu':-.31,'protected_keel_mounts_stern':True,'maximum_vertex_shift_before_scale':float(shift.max()),'mean_vertex_shift':float(shift.mean()),'normal_angle':55},'runtime':'NOT RUN'}
# Exact numeric patch contract only; main merges and retains all weapon timings.
wp=[]
for p in frozen['weapons']['weapons']:
 q=copy.deepcopy(p)
 for key in ['weapon_position','non_turret_muzzle_positions']:
  if key in q:q[key]=(np.array(q[key])*SCALE).tolist()
 wp.append(q)
weapons=copy.deepcopy(frozen['weapons']);weapons['weapons']=wp;meta['unit_patch']={'spatial':patch,'weapons':weapons};meta['exhausts']=[p for p in points if p['name'].startswith('exhaust')];write(AUD/'storm-integration.json',meta);print('Storm geometry',mesh['triangles'],'max smoothing shift',shift.max(),flush=True)
