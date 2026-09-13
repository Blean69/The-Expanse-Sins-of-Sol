from donnager10_geometry_common import *
from scipy.spatial.transform import Rotation
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest();m=read(AUDIT/'mount-metadata.json');layout=read(AUDIT/'layout-candidates.json');source=read(INTAKE/'preserved-source-hashes.json')
for rel,h in source['master_files'].items():assert sha(SRC/rel)==h,rel
for key in ['supplied_archive','preserved_archive']:assert sha(source[key])==source['archive_sha256']
donor=old['source_dependencies']
for p,h in donor.items():assert sha(p)==h,p
prior=[]
for checkpoint in ['geometry04-b','torpedo05-b','amun06-b']:
 record=read(ROOT/'audit'/checkpoint/'final-provenance.json')
 for p,h in record['files'].items():assert sha(p)==h,p
 prior.append({'checkpoint':checkpoint,'files_preserved':len(record['files'])})
assert len(m['rigs'])==18 and sum(r['kind']=='pdc' for r in m['rigs'])==16;assert len({r['mount']['weapon'] for r in m['rigs']})==18;mountchecks=[]
for r in m['rigs']:
 B=np.array(r['basis_columns']);assert np.allclose(B.T@B,np.eye(3),atol=1e-8);assert np.linalg.det(B)>.999999;origin=np.array(r['yaw_pivot_hull']);t=r['turret_override'];tip=np.array(t['muzzle_positions'][0]);offset=np.array(t.get('barrel_position',[0,0,0]));error=float(np.max(abs(origin+B@(tip+offset)-r['muzzle_hull'])));assert error<1e-7
 if r['kind']=='pdc':
  s=r['measured_support']['support'];up=B[:,1];assert r['donor_scale']==1.;heights=[np.dot(q['position'],up) for q in s['foot_samples']];assert min(heights)>s['bottom'] and max(heights)<s['top'];assert r['measured_support']['source_surface_normal_dot_up']>.99
 mountchecks.append({'index':r['index'],'type':r['kind'],'muzzle_transform_error':error,'one_weapon_id_per_physical_mount':True})
railchecks=[]
for r in layout['rails']:
 outside=0
 for s in r['sweep']:
  for c in s['contact_samples']:
   if c['drum_distance_xz']>11.2 or abs(c['point'][1]-r['pivot'][1])>19:outside+=1
 assert outside==0
 railchecks.append({'index':r['index'],'angles':[-2,-1,0,1,2],'vertices_sampled_per_pose':400,'contacts_outside_drum_bearing_envelope':outside,'contact_envelope_radius':11.2,'contact_envelope_axial_half_span':19,'caveat':'Sampled radial clearance only. Original drum intersects source bearing hardware at neutral; this expected bearing region is excluded. Exact internal collision and continuous sweep NOT VERIFIED.'})
for port in m['equipment']['heavy_torpedo_ports']:assert port['axis_clearance']<-.19
assert all(len(p['custom_collar']['support_sample_z'])==5 for p in m['equipment']['light_torpedo_ports']);assert len(m['equipment']['exhausts'])==4;assert m['equipment']['hangar']['clearance_from_static_hatch']==60
v=Gltf(OUT/'donnager10_editable.gltf');triangles=sum(v.g['accessors'][p['indices']]['count']//3 for n in v.g['nodes'] if 'mesh' in n for p in v.g['meshes'][n['mesh']]['primitives']);assert triangles==m['assembled_triangle_total']==76299
write(AUDIT/'independent-checks.json',{'status':'PASS BOUNDED OFFLINE CHECKS; RUNTIME NOT RUN','master_files_preserved':len(source['master_files']),'original_archives_preserved':2,'source_archive_sha256':source['archive_sha256'],'donor_dependencies_preserved':len(donor),'prior_frozen_checkpoints':prior,'unique_weapon_mounts':18,'mount_checks':mountchecks,'rail_sampled_clearance_checks':railchecks,'aft_aperture_outward_rays_clear':4,'front_custom_support_footprints':2,'editable_active_nodes':len(v.g['nodes']),'assembled_triangles':triangles,'launch_hangar_caveat':'Corvettes spawn60units outside actual staticclosedhatch, no animated opening or through-hull passage claimed','runtime':'NOT RUN'});print('PASS: master/archive/donor/prior hashes,18 mounts,16 supports, bounded rail sweep, source-derived ports')
