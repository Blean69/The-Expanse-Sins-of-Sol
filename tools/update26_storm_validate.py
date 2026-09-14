"""Read-only gameplay comparison and exact art-only replacement manifest."""
from pathlib import Path
import sys,hashlib,json,struct
import numpy as np
MAIN=Path('/run/media/haker/NVME 2/expanse-mod');sys.path.insert(0,str(MAIN/'tools'))
from common import read,write,read_mesh
ROOT=Path(__file__).resolve().parents[1];BASE=MAIN/'build/experiments/expanse_update25';GAME=ROOT/'build/update26-storm/game';AUD=ROOT/'audit/update26-storm'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
meta=read(AUD/'integration-spec.json');u=read(BASE/'entities/expanse24_gathering_storm.unit');s=read(BASE/'entities/expanse24_gathering_storm.unit_skin');sp=dict(u['spatial']);sp.pop('collision_rank',None);assert sp==meta['spatial'];info=read_mesh(GAME/'meshes/expanse24_storm_hull.mesh');old=read_mesh(BASE/'meshes/expanse24_storm_hull.mesh');oldpts={p['name']:p for p in old['meshpoints']};newpts={p['name']:p for p in info['meshpoints']};assert oldpts.keys()==newpts.keys()
for k in oldpts:
 if k!='exhaust.0':assert oldpts[k]==newpts[k],k
assert np.allclose(newpts['exhaust.0']['position'],[0,0,-187.9],atol=2e-5)
assert np.allclose(info['box']['extents'] if isinstance(info['box'],dict) else info['box'],old['box']['extents'] if isinstance(old['box'],dict)else old['box'],atol=1e-4)
for r,w in zip(meta['rigs'],u['weapons']['weapons'][:6]):
 assert r['mesh_point']==w['mesh_point']and r['position']==w['weapon_position'];assert r['yaw_arc']==w['yaw_arc']and r['pitch_arc']==w['pitch_arc'];assert sha(GAME/'meshes'/ (r['turret_override']['biaxial_base_mesh']+'.mesh'))==sha(BASE/'meshes'/(r['turret_override']['biaxial_base_mesh']+'.mesh'))
assert len(meta['arc_checks'])==6 and sum(x['blocked']for x in meta['arc_checks'])==0
# Confirm every hull-triangle normal is truly face-normal aligned after compiler,
# not merely that average winding agrees. Skip donor drive where source normals stay.
b=(GAME/'meshes/expanse24_storm_hull.mesh').read_bytes();off=61;count=struct.unpack_from('<Q',b,53)[0];rows=[]
for _ in range(count):
 vals=struct.unpack_from('<12f?',b,off);rows.append(vals[:-1]);off+=49+(8 if vals[-1]else 0)
rows=np.array(rows);count=struct.unpack_from('<Q',b,off)[0];indices=np.frombuffer(b,'<u4',count,off+8);cos=[]
for prim in info['primitives']:
 if info['materials'][prim['material_index']].endswith('_storm_drive'):continue
 ii=indices[prim['vertex_index_start']:prim['vertex_index_start']+prim['vertex_index_count']].reshape(-1,3);t=rows[ii,:3];q=np.cross(t[:,1]-t[:,0],t[:,2]-t[:,0]);q/=np.linalg.norm(q,axis=1,keepdims=True);cos.extend(np.sum(rows[ii,3:6]*q[:,None,:],axis=2).ravel())
assert min(cos)>.99,min(cos)
changes=[];unchanged=[]
for p in sorted(GAME.rglob('*')):
 if not p.is_file():continue
 rel=str(p.relative_to(GAME));prior=BASE/rel;h=sha(p)
 if prior.exists() and sha(prior)==h:unchanged.append(rel);continue
 assert rel.startswith(('meshes/','mesh_materials/','textures/')),rel
 changes.append({'path':rel,'action':'replace'if prior.exists()else'add','sha256':h,'previous_sha256':sha(prior)if prior.exists()else None,'bytes':p.stat().st_size})
manifest={'status':'PASS OFFLINE; IN-GAME VISUAL/TARGETING NOT RUN','base':str(BASE),'game_directory':str(GAME),'files':changes,'unchanged_dependencies':unchanged,'gameplay_changes':[],'integration':{'unit_skin_edits_required':False,'mesh_alias_changes_required':False,'exhaust_meshpoint':'exhaust.0','old_position':oldpts['exhaust.0']['position'],'new_position':newpts['exhaust.0']['position'],'rotation_unchanged':oldpts['exhaust.0']['rotation']==newpts['exhaust.0']['rotation'],'note':'Existing idle plume already uses mesh exhaust points; replacing hull relocates it automatically. Preserve native hyperspace and all unit/weapon/ability data. No absolute exhaust positions outside mesh are supplied.'},'checks':{'hull_hard_normal_min_alignment':float(min(cos)),'non_exhaust_points_identical':True,'outer_box_identical':True,'unit_spatial_unchanged':True,'six_frozen_arcs_unchanged':True,'sampled_rays':sum(x['rays']for x in meta['arc_checks']),'blocked_rays':0,'compiled_hull_plus_drive_triangles':info['triangles'],'assembled_with_six_pdcs':meta['assembled_triangles']},'frozen_gameplay_hashes':{str(p.relative_to(BASE)):sha(p)for p in [BASE/'entities/expanse24_gathering_storm.unit',BASE/'entities/expanse24_gathering_storm.unit_skin']}}
write(AUD/'replacement-manifest.json',manifest);print(json.dumps({'changed_files':len(changes),'unchanged_dependencies':len(unchanged),'checks':manifest['checks']}))
