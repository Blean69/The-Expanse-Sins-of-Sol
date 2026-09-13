"""Correct compiler input using emitted per-triangle winding; regenerate official grids."""
from common import *
import argparse,subprocess,copy
P=argparse.ArgumentParser();P.add_argument('--sdk',type=Path,required=True);P.add_argument('--wine',type=Path,required=True);args=P.parse_args();out=ROOT/'assets/derived/polish-b';build=ROOT/'build/polish-b';records={}
env=dict(os.environ,WINEPREFIX=str(build/'proton-prefix'),OMP_NUM_THREADS='4',MANGOHUD='0',WINEDEBUG='-all',DISPLAY='',WINEDLLOVERRIDES='mscoree,mshtml=')
for jp in sorted((build/'compiler-json').glob('*.mesh_json')):
 m=read(jp);name=jp.stem;a=Gltf(out/(name+'.gltf'));buf=bytearray(a.buffers[0]);v=np.array([x['p'] for x in m['non_skinned_vertices']]);n=np.array([x['n'] for x in m['non_skinned_vertices']]);allidx=np.array(m['vertex_indices']);record=[]
 for pp in m['primitives']:
  pr=a.g['meshes'][0]['primitives'][pp['material_index']];start=pp['vertex_index_start'];ii=allidx[start:start+pp['vertex_index_count']].reshape(-1,3);vv=v[ii];dot=np.sum(np.cross(vv[:,1]-vv[:,0],vv[:,2]-vv[:,0])*n[ii].mean(1),axis=1);flip=dot< -1e-7
  inp=a.accessor(pr['attributes']['POSITION']);inp[:,2]*=-1;srcidx=a.accessor(pr['indices']).flatten().reshape(-1,3);exp=inp[srcidx]
  # Importer may permute corner order, but preserve each complete triangle.
  errors=[]
  for tri,q in zip(exp,vv):errors.append(min(np.max(np.abs(tri-q[perm])) for perm in [[0,1,2],[0,2,1],[1,0,2],[1,2,0],[2,0,1],[2,1,0]]))
  assert max(errors)<2e-5,(name,'triangle order changed')
  at=a.g['accessors'][pr['indices']];bv=a.g['bufferViews'][at['bufferView']];idx=np.ndarray((at['count']//3,3),dtype='<u4',buffer=buf,offset=bv.get('byteOffset',0)+at.get('byteOffset',0));idx[flip]=idx[flip][:,[0,2,1]];record.append({'material':pp['material_index'],'triangle_count':len(ii),'input_triangles_flipped':int(flip.sum()),'max_triangle_position_error':max(errors)})
 (out/(name+'.bin')).write_bytes(buf);records[name]=record
 if any(r['input_triangles_flipped'] for r in record):
  for fmt in ['json','binary']:
   cmd=[str(args.wine),str(args.sdk/'MeshBuilder/bin/MeshBuilder.exe'),'--input_path=Z:'+str(out/(name+'.gltf')),'--output_folder_path=Z:'+str(build/('compiler-'+fmt)),'--mesh_output_format='+fmt,'--fill_triangle_facing_grid']
   with (build/(name+'-winding-'+fmt+'.log')).open('w') as log:subprocess.run(cmd,env=env,stdout=log,stderr=subprocess.STDOUT,check=True,timeout=300)
 print(name,sum(r['input_triangles_flipped'] for r in record),flush=True)
write(ROOT/'audit/polish-b/winding-correction.json',records)
