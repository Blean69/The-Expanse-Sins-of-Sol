"""Verify existing Worker B compiler outputs against editable and frozen baseline.
Asset-dependent; no rebuild, installation, or source writes. SciPy is local-only.
"""
from common import Gltf,ROOT,read,write
import argparse,struct,json
from pathlib import Path
import numpy as np
try:from scipy.spatial import cKDTree
except ImportError:raise SystemExit('MISSING DEPENDENCY scipy; baseline comparison NOT PASSED')
p=argparse.ArgumentParser();p.add_argument('--source-root',type=Path,required=True);args=p.parse_args()
base=args.source_root/'build/compiler-json/mcrn_corvette_baseline.mesh_json'
if not base.is_file():raise SystemExit('MISSING DEPENDENCY; NOT PASSED: '+str(base))
meta=read(ROOT/'audit/workers/b/mount-metadata.json');results={};exp=[]
def vertex_rows(m):return np.array([v['p']+v['n']+v['t']+v['uv0'] for v in m['non_skinned_vertices']])[m['vertex_indices']]
for kind in ['hull','base','barrel']:
 name='expanse_tachi_one_pdc_'+kind;sp=ROOT/'assets/derived/worker-b'/(name+'_editable.gltf');jp=ROOT/'build/worker-b/compiler-json'/(name+'.mesh_json')
 for f in [sp,jp]:
  if not f.is_file():raise SystemExit('MISSING DEPENDENCY; NOT PASSED: '+str(f))
 a=Gltf(sp);m=read(jp);rows=vertex_rows(m);by_material={}
 for prim in a.g['meshes'][0]['primitives']:
  i=a.accessor(prim['indices']).flatten();by_material[prim['material']]=a.accessor(prim['attributes']['POSITION'])[i]
 maxerr=0.;windings={}
 for prim in m['primitives']:
  expected=by_material[prim['material_index']].reshape(-1,3,3);start=prim['vertex_index_start'];actual=rows[start:start+prim['vertex_index_count'],:3].reshape(-1,3,3)
  # The importer chooses winding per material. Verify all indexed corners,
  # allowing that representation change; compare full attributes below.
  direct=float(np.abs(expected-actual).max());rev=float(np.abs(expected-actual[:,[0,2,1]]).max());err=min(direct,rev);assert err<2e-5,(kind,prim['material_index'],err);maxerr=max(maxerr,err);windings[str(prim['material_index'])]='same' if direct<rev else 'reversed'
 if kind!='hull':
  B=np.diag([-1.,1.,-1.]);origin=np.array(meta['yaw_pivot_hull'] if kind=='base' else meta['pitch_pivot_hull']);rows[:,:3]=rows[:,:3]@B.T+origin;rows[:,3:6]=rows[:,3:6]@B.T;rows[:,6:9]=rows[:,6:9]@B.T
 exp.append(rows);results[kind]={'triangles':len(rows)//3,'all_indexed_positions_max_error':maxerr,'compiler_winding_relative_to_editable_by_material':windings,'status':'PASS'}
expected=vertex_rows(read(base));actual=np.concatenate(exp);assert actual.shape==expected.shape
# Compare position/normal/UV both ways. MeshBuilder regenerates Mikk tangents
# (pinned SDK mesh_pbr_utility.hlsli:152); record tangent differences explicitly.
cols=[0,1,2,3,4,5,10,11]
d1,i1=cKDTree(expected[:,cols]).query(actual[:,cols]);d2,i2=cKDTree(actual[:,cols]).query(expected[:,cols])
maxerr=float(max(d1.max(),d2.max()));assert maxerr<2e-4,('baseline positions/normals/UV differ',maxerr)
full_d,_=cKDTree(expected).query(actual);drift={'indexed_corners_without_full_attribute_match_within_2e_minus4':int(np.sum(full_d>2e-4)),'max_full_attribute_distance':float(full_d.max()),'note':'full attribute comparison includes regenerated tangent XYZ/W; position/normal/UV comparison separately passes'}
err=np.abs(actual-expected[i1]);attr={k:float(err[:,a:b].max()) for k,a,b in [('position',0,3),('normal',3,6),('tangent_xyz',6,9),('tangent_w',9,10),('uv',10,12)]}
# Verify actual output shading frames rather than asserting tangent equality.
frame_errors={}
for j,kind in enumerate(['hull','base','barrel']):
 rows=exp[j];nn=np.linalg.norm(rows[:,3:6],axis=1);tt=np.linalg.norm(rows[:,6:9],axis=1);dot=np.abs(np.sum(rows[:,3:6]*rows[:,6:9],axis=1));finite=bool(np.isfinite(rows).all());unit_bad=int(np.sum(np.abs(tt-1)>2e-5));orth_bad=int(np.sum(dot>2e-5));norm_bad=int(np.sum(np.abs(nn-1)>2e-5));sign_bad=int(np.sum(np.abs(rows[:,9])!=1));frame_ok=finite and not(unit_bad or orth_bad or norm_bad or sign_bad)
 name='expanse_tachi_one_pdc_'+kind;b=(ROOT/'build/worker-b/compiler-binary'/(name+'.mesh')).read_bytes();count=struct.unpack_from('<Q',b,53)[0];off=61;binary=[]
 for _ in range(count):
  vals=struct.unpack_from('<12f?',b,off);off+=49
  if vals[-1]:off+=8
  binary.append(vals[:-1])
 jm=read(ROOT/'build/worker-b/compiler-json'/(name+'.mesh_json'));js=np.array([v['p']+v['n']+v['t']+v['uv0'] for v in jm['non_skinned_vertices']]);parity=float(np.abs(np.array(binary)-js).max());assert parity<2e-5
 frame_errors[kind]={'finite_unit_orthogonal_tangents':'PASS' if frame_ok else 'FAIL','zero_tangent_indexed_corners':int(np.sum(tt<1e-5)),'nonunit_tangent_indexed_corners':unit_bad,'nonorthogonal_indexed_corners':orth_bad,'max_normal_tangent_dot':float(dot.max()),'normal_unit_invalid_corners':norm_bad,'tangent_sign_invalid_corners':sign_bad,'json_binary_vertex_max_error':parity,'binary_json_parity':'PASS'}
# Compiler-input comparison isolates regeneration from source edits.
def input_rows(path):
 a=Gltf(path);return np.concatenate([np.concatenate([a.accessor(pr['attributes'][k]) for k in ['POSITION','NORMAL','TANGENT','TEXCOORD_0']],axis=1)[a.accessor(pr['indices']).flatten()] for pr in a.g['meshes'][0]['primitives']])
br=input_rows(args.source_root/'assets/derived/baseline/mcrn_corvette_baseline.gltf');er=input_rows(ROOT/'assets/derived/worker-b/expanse_tachi_one_pdc_hull.gltf');dd,ii=cKDTree(br[:,cols]).query(er[:,cols]);source_error=np.abs(er-br[ii]).max(0);assert dd.max()<2e-5 and source_error.max()<2e-5
bt=np.linalg.norm(expected[:,6:9],axis=1);bd=np.abs(np.sum(expected[:,3:6]*expected[:,6:9],axis=1));baseline_bad={'zero_tangent_indexed_corners':int(np.sum(bt<1e-5)),'nonunit_tangent_indexed_corners':int(np.sum(np.abs(bt-1)>2e-5)),'nonorthogonal_indexed_corners':int(np.sum(bd>2e-5)),'max_normal_tangent_dot':float(bd.max())}
write(ROOT/'audit/workers/b/compiler-geometry-check.json',{'environment':'REQUIRES ignored normalized assets, official outputs and scipy','checks':results,'baseline_rest_pose_position_normal_uv_check':{'status':'PASS','indexed_corners':len(actual),'max_feature_distance_both_directions':maxerr,'max_absolute_errors':attr},'source_hull_attributes_preserved':{'status':'PASS','max_absolute_error':float(source_error.max())},'emitted_tangent_drift':drift,'emitted_tangent_equality':'NOT PRESERVED: official MeshBuilder regenerates Mikk tangents after partition; normal-map appearance requires runtime inspection','tangent_source_evidence':'Pinned SDK Shaders/mesh/mesh_pbr_utility.hlsli:152','output_shading_and_binary_checks':frame_errors,'frozen_baseline_shading_observation':baseline_bad,'package_gate':'BLOCKED: invalid generated tangent frames; candidate-only','runtime':'NOT RUN'})
print(json.dumps({'indexed_corners':len(actual),'position_normal_uv_max_error':maxerr,'input_attributes_max_error':float(source_error.max()),'output_frames':frame_errors,'emitted_tangent_equality':'NOT PRESERVED'}))

if any(v['finite_unit_orthogonal_tangents']!='PASS' for v in frame_errors.values()):
 meta['status']='COMPILED CANDIDATE ONLY; tangent frame gate FAILED; NOT READY TO PACKAGE; RUNTIME NOT RUN';meta['package_gate']='BLOCKED: generated tangent frames include zero/nonorthogonal tangents; see compiler-geometry-check.json';meta['checks']['generated_tangent_frames']='FAIL';write(ROOT/'audit/workers/b/mount-metadata.json',meta)
 raise SystemExit('FAIL: generated tangent frame gate; candidate outputs must not be packaged')
