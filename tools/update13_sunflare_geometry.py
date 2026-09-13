"""Whole-model proper roll from frozen optimized Sunflare; no UV/texture changes."""
from pathlib import Path
import copy,json,os,hashlib
import numpy as np
from scipy.spatial.transform import Rotation
from common import Gltf
from polish_ui import write
ROOT=Path(__file__).resolve().parents[1];OLD=Path('/run/media/haker/NVME 2/expanse-workers/validation');SRC=OLD/'assets/derived/update12-c';OUT=ROOT/'assets/derived/update13-c';AUD=ROOT/'audit/update13-c';BUILD=ROOT/'build/update13-c'
Q=np.diag([-1.,-1.,1.]);assert np.linalg.det(Q)==1
asset=Gltf(SRC/'expanse12_sunflare_editable.gltf');pr=asset.g['meshes'][0]['primitives'][0];v0=asset.accessor(pr['attributes']['POSITION']);n0=asset.accessor(pr['attributes']['NORMAL']);t0=asset.accessor(pr['attributes']['TANGENT']);uv=asset.accessor(pr['attributes']['TEXCOORD_0']);idx=asset.accessor(pr['indices']);v=v0@Q.T;n=n0@Q.T;t=t0.copy();t[:,:3]=t0[:,:3]@Q.T
meta=json.loads((OLD/'audit/update12-c/integration-spec.json').read_text());meta['status']='COMPILER PENDING';meta['game_directory']=str(BUILD/'game');meta['editable_source']=str(OUT/'expanse12_sunflare_editable.gltf')
ex=meta['equipment']['exhaust'];ex['position']=(np.array(ex['position'])@Q.T).tolist();ex['forward']=(np.array(ex['forward'])@Q.T).tolist();ex['up']=(np.array(ex['up'])@Q.T).tolist();ex['source']+='; whole-model 180 degree longitudinal roll applied in update13';meta['equipment']['exhausts']=[copy.deepcopy(ex)];meta['exhaust_geometry']=copy.deepcopy(ex)
lo=v.min(0);hi=v.max(0);bc=(lo+hi)/2;meta['ship_spatial']={'box':{'center':bc.tolist(),'extents':((hi-lo)/2).tolist()},'radius':float(np.linalg.norm(v-bc,axis=1).max()),'bounds_min':lo.tolist(),'bounds_max':hi.tolist()}
points=[{'name':'center','translation':[0.,0.,0.]},{'name':'above','translation':[0.,float(hi[1]+1),0.]},{'name':'aura','translation':[0.,float(lo[1]-1),0.]},{'name':'exhaust.0','translation':ex['position'],'rotation':Rotation.from_matrix(Q@np.diag([-1.,1.,-1.])).as_quat().tolist()}]
meta['meshpoints']['hull']=points;meta['normalization']['proper_rotation']=(Q@np.array(meta['normalization']['proper_rotation'])).tolist();meta['normalization']['update13_roll_degrees']=180;meta['normalization']['update13_game_rotation']=Q.tolist();meta['normalization']['orientation_limit']='Three-prong source has no canonical top annotation. 180-degree proper roll brings a lettered central prong upward; camera-side glyph readability remains runtime-dependent.'
for compiler,name in [(False,'expanse12_sunflare_editable'),(True,'expanse12_sunflare_hull')]:
 g=copy.deepcopy(asset.g);g['nodes']=[{'name':name,'mesh':0,'children':list(range(1,5))}]+copy.deepcopy(points);g['scenes']=[{'nodes':[0]}];g['scene']=0;g['bufferViews']=[];g['accessors']=[];buf=bytearray()
 for im in g.get('images',[]):im['uri']=os.path.relpath((SRC/im['uri']).resolve(),OUT)
 def acc(value,typ,ct=5126):
  value=np.asarray(value,dtype='<f4'if ct==5126 else'<u4');buf.extend(b'\0'*((-len(buf))%4));off=len(buf);buf.extend(value.tobytes());g['bufferViews'].append({'buffer':0,'byteOffset':off,'byteLength':value.nbytes});at={'bufferView':len(g['bufferViews'])-1,'componentType':ct,'count':len(value),'type':typ}
  if typ=='VEC3':at.update(min=value.min(0).tolist(),max=value.max(0).tolist())
  g['accessors'].append(at);return len(g['accessors'])-1
 vv=v.copy();nn=n.copy();tt=t.copy()
 if compiler:
  vv[:,2]*=-1;nn[:,2]*=-1;tt[:,2]*=-1;tt[:,3]*=-1
  for p in g['nodes'][1:]:
   p['translation'][2]*=-1
   if 'rotation'in p:p['rotation'][0]*=-1;p['rotation'][1]*=-1
  g['materials']=[{'name':'expanse12_sunflare_material','pbrMetallicRoughness':{'baseColorFactor':[1,1,1,1]}}]
  for key in ['images','textures','samplers','extensionsUsed']:g.pop(key,None)
 g['meshes']=[{'primitives':[{'mode':4,'material':0,'indices':acc(idx,'SCALAR',5125),'attributes':{'POSITION':acc(vv,'VEC3'),'NORMAL':acc(nn,'VEC3'),'TANGENT':acc(tt,'VEC4'),'TEXCOORD_0':acc(uv,'VEC2')}}]}];g['buffers']=[{'uri':name+'.bin','byteLength':len(buf)}];OUT.mkdir(parents=True,exist_ok=True);(OUT/(name+'.bin')).write_bytes(buf);write(OUT/(name+'.gltf'),g)
write(OUT/'retained-source-frames.json',{'hull':{'0':{'v':v.tolist(),'n':n.tolist(),'t':t.tolist(),'uv':uv.tolist()}}});write(AUD/'integration-spec.json',meta)
np.savez(OUT/'optimized.npz',v=v,n=n,t=t,uv=uv,i=idx.reshape(-1,3))
write(AUD/'rotation-evidence.json',{'status':'PASS OFFLINE','rotation':Q.tolist(),'determinant':1,'triangles':len(idx)//3,'same_triangle_indices':True,'UVs_unchanged':True,'source_primitive_sha256':hashlib.sha256((SRC/'expanse12_sunflare_editable.bin').read_bytes()).hexdigest(),'maximum_inverse_position_error':float(abs(v@Q-v0).max()),'longitudinal_positions_unchanged':bool(np.array_equal(v[:,2],v0[:,2])),'semantic_points':'Exhaust full pose rotates with hull; above/aura are re-anchored to new world-up/down bounds, not swapped.','runtime':'NOT RUN'})
print('Proper 180-degree roll; triangles',len(idx)//3)
