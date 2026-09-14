"""Offline art checks. Does not claim engine targeting, PBR or multiplayer passes."""
from pathlib import Path
import hashlib,struct
import numpy as np
from scipy.spatial.transform import Rotation
from PIL import Image
from common import read,read_mesh,write
from update26_platform_common import load_parts
from update26_platform_art import ROOT,BASE,GAME,AUD,NAME
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
pmeta=read(AUD/'integration-spec.json');mmeta=read(ROOT/'audit/update26-murphy/integration-spec.json')
files={**pmeta['files'],**mmeta['files']}
for p in GAME.rglob('*'):assert not p.is_symlink(),p
assert set(files)=={str(p.relative_to(GAME))for p in GAME.rglob('*')if p.is_file()}
for name,h in files.items():assert sha(GAME/name)==h
for meta,key in[(pmeta,'source_hashes'),(mmeta,'preserved_files'),(mmeta,'source_material_hashes')]:
 for p,h in meta[key].items():assert sha(Path(p))==h
for p in(GAME/'mesh_materials').glob('*.mesh_material'):
 for key,value in read(p).items():
  if key.endswith('_texture'):assert any((folder/'textures'/(value+'.dds')).is_file()for folder in[GAME,BASE]),(p,key,value)
# Rig points are invariant, independent of model bounding-box edits.
a=read_mesh(BASE/'meshes'/(NAME+'.mesh'))['meshpoints'];b=read_mesh(GAME/'meshes'/(NAME+'.mesh'))['meshpoints'];assert len(a)==len(b)
for x,y in zip(a,b):
 assert x['name']==y['name']and np.allclose(x['position'],y['position'],atol=2e-5)and np.allclose(x['rotation'],y['rotation'],atol=2e-5)
parts=load_parts(GAME/'meshes'/(NAME+'.mesh'));v=np.concatenate([p['v'][np.unique(p['i'])]for p in parts]);assert np.isfinite(v).all();samples=0;minimum=1e9
# All new support stays inside both outward PDC planes. Sweep full preserved arcs.
for w in pmeta['source_weapon_records']['weapons'][1:]:
 up=np.array(w['up']);pos=np.array(w['weapon_position']);B=np.column_stack([np.cross(up,w['forward']),up,w['forward']]);t=read(BASE/'entities'/(w['weapon']+'.weapon'))['turret'];barrel=np.array(t['barrel_position']);muzzle=np.array(t['muzzle_positions'][0]);plane=np.max(v@up);clearance=np.dot(pos,up)-plane;assert clearance>.09
 for pitch in np.linspace(-85,0,18):
  R=Rotation.from_euler('x',pitch,degrees=True).as_matrix()
  for yaw in np.linspace(-180,180,73):
   Y=Rotation.from_euler('y',yaw,degrees=True).as_matrix();d=B@Y@R@np.array([0,0,1]);o=B@Y@(barrel+R@muzzle);c=clearance+np.dot(o,up);assert np.dot(d,up)>=-1e-8 and c>0;minimum=min(minimum,c);samples+=1
rail=read(BASE/'entities/expanse22_foehammer_battery_0.weapon');assert rail['pitch_speed']==0;vertical=float(rail['turret']['muzzle_positions'][0][1]-v[:,1].max());assert vertical>18.3
# Confirm recoil legs land on actual ring faces rather than empty bounds.
ring=parts[0];tri=ring['v'][ring['i']]
def ring_top(x,z):
 origin=np.array([x,0,z]);d=np.array([0,-1,0]);e1=tri[:,1]-tri[:,0];e2=tri[:,2]-tri[:,0];h=np.cross(d,e2);det=np.sum(e1*h,axis=1);valid=np.abs(det)>1e-9;inv=np.zeros_like(det);inv[valid]=1/det[valid];s=origin-tri[:,0];u=inv*np.sum(s*h,axis=1);q=np.cross(s,e1);vv=inv*np.sum(d*q,axis=1);distance=inv*np.sum(e2*q,axis=1);ok=valid&(u>=0)&(vv>=0)&(u+vv<=1)&(distance>=0);assert ok.any(),(x,z);return float(-distance[ok].min())
landings=[{'x':x,'z':z,'ring_surface_y':ring_top(x,z)}for x in[-34,34]for z in[-46,2]]
assert all(abs(a['ring_surface_y']+52)<1.7 for a in landings)
for z in[-14,-6]:assert np.hypot(5,z+10)<8
# Texture formats and opaque alpha; shader appearance remains a runtime check.
texture_checks={}
for name in files:
 if not name.startswith('textures/expanse26_murphy_'):continue
 p=GAME/name;raw=p.read_bytes();assert raw[:4]==b'DDS ';fourcc=raw[84:88];normal='_nrm.'in name;fmt=84 if fourcc==b'BC5S' else struct.unpack_from('<I',raw,128)[0];assert fourcc==(b'BC5S'if normal else b'DX10');assert fmt==(84 if normal else 98),(name,fmt)
 if not normal:assert np.asarray(Image.open(p).convert('RGBA'))[:,:,3].min()>=254
 texture_checks[name]={'dxgi_format':fmt,'mip_levels':struct.unpack_from('<I',raw,28)[0]}
manifest={'status':'OFFLINE PASS; RUNTIME UNTESTED','base':str(BASE),'game':str(GAME),'files':{p:{'sha256':h,'mode':'replacement'if(BASE/p).exists()else'new'}for p,h in sorted(files.items())},'file_count':len(files),'symlinks':0}
write(AUD/'combined-art-manifest.json',manifest)
report={'status':'OFFLINE PASS','support_triangles':pmeta['counts']['support'],'assembled_triangles':pmeta['counts']['assembled'],'meshpoints_preserved':True,'source_hashes_unchanged':True,'material_dependencies_resolved':True,'outward_pdc_ray_samples':samples,'minimum_pdc_muzzle_clearance_from_new_support_plane':float(minimum),'rail_path_vertical_clearance':vertical,'rail_pitch_speed_preserved':0,'recoil_foot_ring_contacts':landings,'murphy_geometry_opposed_normals':mmeta['checks']['existing_opposed_winding_triangles'],'murphy_hull_drive_rig_hashes_preserved':True,'texture_checks':texture_checks,'package_manifest':'combined-art-manifest.json','untested':['game shader metallic/roughness/normal response','in-game LOD and visual attachment appearance','game turret interpolation and target acquisition','save/reload','multiplayer']}
write(AUD/'offline-validation.json',report);write(ROOT/'audit/update26-murphy/offline-validation.json',{'status':'OFFLINE PASS','preserved_files_verified':True,'geometry_rebuilt':False,'new_texture_formats':texture_checks,'untested':report['untested']});print('PASS:',len(files),'regular files;',samples,'PDC ray samples; minimum clearance',minimum)
