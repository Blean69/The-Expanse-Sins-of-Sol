"""Private update26 art helpers: explicit mesh frames, SDK compile, no game install."""
from pathlib import Path
import copy,json,os,struct,subprocess
import numpy as np
from scipy.spatial import cKDTree
from scipy.spatial.transform import Rotation
from common import Gltf,read,read_mesh,write
import update23_murphy_art as old
WINE=old.WINE;SDK=old.SDK;ENV=old.ENV

def load_parts(path):
 b=path.read_bytes();count=struct.unpack_from('<Q',b,53)[0];off=61;rows=[]
 for _ in range(count):
  x=struct.unpack_from('<12f?',b,off);rows.append(x[:-1]);off+=49+(8 if x[-1]else 0)
 rows=np.array(rows);count=struct.unpack_from('<Q',b,off)[0];off+=8;indices=np.frombuffer(b,dtype='<u4',count=count,offset=off);info=read_mesh(path);parts=[]
 for p in info['primitives']:
  ids=indices[p['vertex_index_start']:p['vertex_index_start']+p['vertex_index_count']].reshape(-1,3);parts.append({'v':rows[:,:3].copy(),'n':rows[:,3:6].copy(),'t':rows[:,6:10].copy(),'uv':rows[:,10:12].copy(),'i':ids.copy(),'material':info['materials'][p['material_index']]})
 return parts

def export(name,parts,points,out):
 out.mkdir(parents=True,exist_ok=True);g={'asset':{'version':'2.0','generator':'Update26 private art with retained source frames'},'scene':0,'scenes':[{'nodes':[0]}],'nodes':[{'name':name,'mesh':0,'children':[]}],'meshes':[{'name':name,'primitives':[]}],'materials':[],'buffers':[],'bufferViews':[],'accessors':[]};buf=bytearray();refs=[]
 def acc(x,typ,ct=5126):
  x=np.asarray(x,dtype='<u4'if ct==5125 else'<f4');buf.extend(b'\0'*((-len(buf))%4));off=len(buf);buf.extend(x.tobytes());g['bufferViews'].append({'buffer':0,'byteOffset':off,'byteLength':x.nbytes});a={'bufferView':len(g['bufferViews'])-1,'componentType':ct,'count':len(x),'type':typ}
  if typ=='VEC3':a.update(min=x.min(0).tolist(),max=x.max(0).tolist())
  g['accessors'].append(a);return len(g['accessors'])-1
 for p in parts:
  # Discard unused donor vertices only; selected triangles are unchanged.
  used,inv=np.unique(p['i'].ravel(),return_inverse=True);p={**p,**{k:p[k][used]for k in ['v','n','t','uv']},'i':inv.reshape(-1,3)};refs.append({k:p[k].tolist()for k in ['v','n','t','uv']});v,n,t=[p[k].copy()for k in ['v','n','t']]
  for a in[v,n,t]:a[:,2]*=-1
  t[:,3]*=-1;g['materials'].append({'name':p['material'],'pbrMetallicRoughness':{'baseColorFactor':[1,1,1,1]}});g['meshes'][0]['primitives'].append({'mode':4,'material':len(g['materials'])-1,'indices':acc(p['i'].ravel(),'SCALAR',5125),'attributes':{'POSITION':acc(v,'VEC3'),'NORMAL':acc(n,'VEC3'),'TANGENT':acc(t,'VEC4'),'TEXCOORD_0':acc(p['uv'],'VEC2')}})
 for pt in points:
  q=copy.deepcopy(pt);q['translation'][2]*=-1
  if'rotation'in q:q['rotation'][0]*=-1;q['rotation'][1]*=-1
  g['nodes'][0]['children'].append(len(g['nodes']));g['nodes'].append(q)
 g['buffers']=[{'uri':name+'.bin','byteLength':len(buf)}];(out/(name+'.bin')).write_bytes(buf);write(out/(name+'.gltf'),g);write(out/'source-frames.json',refs)

def compile(name,out,build,game,points):
 def run(fmt,suffix=''):
  dest=build/('compiler-'+fmt);dest.mkdir(parents=True,exist_ok=True)
  with(build/(name+suffix+'-'+fmt+'.log')).open('w')as log:subprocess.run([str(WINE),str(SDK/'MeshBuilder/bin/MeshBuilder.exe'),'--input_path=Z:'+str(out/(name+'.gltf')),'--output_folder_path=Z:'+str(dest),'--mesh_output_format='+fmt,'--fill_triangle_facing_grid'],env=ENV,stdout=log,stderr=subprocess.STDOUT,check=True,timeout=300)
 run('json');m=read(build/'compiler-json'/(name+'.mesh_json'));a=Gltf(out/(name+'.gltf'));buf=bytearray(a.buffers[0]);v=np.array([x['p']for x in m['non_skinned_vertices']]);n=np.array([x['n']for x in m['non_skinned_vertices']]);allidx=np.array(m['vertex_indices']);flips=0
 for p in m['primitives']:
  mat=m['materials'][p['material_index']];pr=next(q for q in a.g['meshes'][0]['primitives']if mat.endswith('_'+a.g['materials'][q['material']]['name']));ii=allidx[p['vertex_index_start']:p['vertex_index_start']+p['vertex_index_count']].reshape(-1,3);q=np.cross(v[ii[:,1]]-v[ii[:,0]],v[ii[:,2]]-v[ii[:,0]]);flip=np.sum(q*n[ii].mean(1),axis=1)<-1e-5;acc=a.g['accessors'][pr['indices']];view=a.g['bufferViews'][acc['bufferView']];arr=np.ndarray((acc['count']//3,3),dtype='<u4',buffer=buf,offset=view['byteOffset']);expected=a.accessor(pr['attributes']['POSITION']);expected[:,2]*=-1;assert np.allclose(np.sort(expected[arr],axis=1),np.sort(v[ii],axis=1),atol=4e-5);arr[flip]=arr[flip][:,[0,2,1]];flips+=int(flip.sum())
 if flips:(out/(name+'.bin')).write_bytes(buf);run('json','-winding')
 run('binary');m=read(build/'compiler-json'/(name+'.mesh_json'));bp=build/'compiler-binary'/(name+'.mesh');original=bp.read_bytes();b=bytearray(original);count=struct.unpack_from('<Q',b,53)[0];off=61;rows=[];offsets=[]
 for _ in range(count):
  vals=struct.unpack_from('<12f?',b,off);rows.append(vals[:-1]);offsets.append(off+24);off+=49+(8 if vals[-1]else 0)
 rows=np.array(rows);refs=read(out/'source-frames.json');features=np.concatenate([np.concatenate([r['v'],r['n'],r['uv']],axis=1)for r in refs]);distance,match=cKDTree(features).query(np.concatenate([rows[:,:6],rows[:,10:12]],axis=1));assert distance.max()<2e-4;t=np.concatenate([r['t']for r in refs])[match];n=rows[:,3:6];t[:,:3]-=n*np.sum(n*t[:,:3],axis=1)[:,None];t[:,:3]/=np.linalg.norm(t[:,:3],axis=1)[:,None];allowed=np.zeros(len(b),bool)
 for i,pos in enumerate(offsets):struct.pack_into('<4f',b,pos,*t[i]);allowed[pos:pos+16]=True
 assert np.all((np.frombuffer(original,np.uint8)==np.frombuffer(b,np.uint8))|allowed);info=read_mesh(bp);assert b[info['parsed_prefix_bytes']:]==original[info['parsed_prefix_bytes']:];idx=np.array(m['vertex_indices']).reshape(-1,3);q=np.cross(rows[idx[:,1],:3]-rows[idx[:,0],:3],rows[idx[:,2],:3]-rows[idx[:,0],:3]);opposed=int((np.sum(q*n[idx].mean(1),axis=1)<-1e-5).sum());assert opposed==0
 assert len(info['meshpoints'])==len(points)
 for got,want in zip(info['meshpoints'],points):
  assert got['name']==want['name']and np.allclose(got['position'],want['translation'],atol=2e-5);assert np.allclose(np.array(got['rotation']).reshape(3,3),Rotation.from_quat(want.get('rotation',[0,0,0,1])).as_matrix().T,atol=2e-5)
 (game/'meshes').mkdir(parents=True,exist_ok=True);(game/'meshes'/(name+'.mesh')).write_bytes(b)
 return {'triangles':len(idx),'materials':m['materials'],'source_frame_error':float(distance.max()),'opposed_winding_triangles':opposed,'initial_winding_flips':flips,'meshpoints_unchanged':True,'only_tangent_bytes_repaired':True,'official_triangle_grid_and_trailer_preserved':True}
