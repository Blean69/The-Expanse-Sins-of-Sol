"""Apply generated Free Navy paint to existing Pella plating, without layered geometry."""
from pathlib import Path
import sys,json,copy,hashlib,shutil,numpy as np
sys.path.insert(0,'/run/media/haker/NVME 2/expanse-mod/tools')
from common import Gltf
from polish_ui import write
ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'assets/derived/update14-hulls/pella';AUD=ROOT/'audit/update14-hulls/pella';MAT='expanse12_pella_free_navy';SRC=Path('/run/media/haker/NVME 2/expanse-workers/weapon-behavior/assets/derived/update12-a/pella/emblem-sources/generated-charcoal-panel.png')
texture=OUT/'texture-sources'/f'{MAT}_clr.png';texture.parent.mkdir(exist_ok=True);shutil.copyfile(SRC,texture)
archive=OUT/'before-emblem';archive.mkdir(exist_ok=True)
# Vertex layout: position3 normal3 tangent4 UV2. Clip only measured upward fore plating.
def clip(poly,axis,edge,greater):
 out=[]
 for a,b in zip(poly,poly[1:]+poly[:1]):
  aa=a[axis]>=edge if greater else a[axis]<=edge;bb=b[axis]>=edge if greater else b[axis]<=edge
  if aa:out.append(a)
  if aa!=bb:out.append(a+(b-a)*((edge-a[axis])/(b[axis]-a[axis])))
 return out

def cut(t):
 pending=[list(t)];outside=[]
 for axis,edge,greater in [(0,-9,True),(0,9,False),(2,54,True),(2,72,False)]:
  nxt=[]
  for p in pending:
   a=clip(p,axis,edge,greater);b=clip(p,axis,edge,not greater)
   if len(a)>=3:nxt.append(a)
   if len(b)>=3:outside.append(b)
  pending=nxt
 def tris(polys):
  result=[]
  for p in polys:
   for i in range(1,len(p)-1):
    q=np.array([p[0],p[i],p[i+1]])
    if np.linalg.norm(np.cross(q[1,:3]-q[0,:3],q[2,:3]-q[0,:3]))>1e-8:result.append(q)
  return result
 return tris(outside),tris(pending)

def process(stem,compiler):
 path=OUT/(stem+'.gltf');bp=OUT/(stem+'.bin')
 for p in [path,bp]:
  target=archive/p.name
  if not target.exists():shutil.copyfile(p,target)
 a=Gltf(archive/path.name);g=copy.deepcopy(a.g);parts=[];marks=[];oldcount=0;selected=0
 for pr in g['meshes'][0]['primitives']:
  at=pr['attributes'];v=a.accessor(at['POSITION']);n=a.accessor(at['NORMAL']);t=a.accessor(at['TANGENT']);uv=a.accessor(at['TEXCOORD_0']);ii=a.accessor(pr['indices']).reshape(-1,3)
  if compiler:v[:,2]*=-1;n[:,2]*=-1;t[:,2:4]*=-1
  data=np.c_[v,n,t,uv][ii];oldcount+=len(ii);mat=g['materials'][pr['material']]['name'];keep=[]
  for q in data:
   xyz=q[:,:3];face=np.cross(xyz[1]-xyz[0],xyz[2]-xyz[0]);face/=max(np.linalg.norm(face),1e-20)
   if mat.startswith('expanse12_pella_mat_') and xyz[:,1].min()>18 and abs(face[1])>.4 and xyz[:,0].max()>-9 and xyz[:,0].min()<9 and xyz[:,2].max()>54 and xyz[:,2].min()<72:
    o,m=cut(q);keep.extend(o);marks.extend(m);selected+=bool(m)
   else:keep.append(q)
  if keep:parts.append((np.array(keep),pr['material']))
 assert marks,'No actual forward hull triangles selected'
 mi=len(g['materials']);g['materials'].append({'name':MAT,'pbrMetallicRoughness':{'baseColorFactor':[1,1,1,1],'baseColorTexture':{'index':0},'metallicFactor':.2,'roughnessFactor':.7}});g['images']=[{'uri':'texture-sources/'+texture.name}];g['textures']=[{'source':0}]
 marks=np.array(marks);marks[:,:,10]=(marks[:,:,0]+9)/18;marks[:,:,11]=(72-marks[:,:,2])/18;parts.append((marks,mi));buf=bytearray();g['buffers']=[];g['bufferViews']=[];g['accessors']=[];g['meshes'][0]['primitives']=[];frames={}
 def acc(arr,typ,ct=5126):
  arr=np.array(arr,dtype='<f4' if ct==5126 else '<u4');buf.extend(b'\0'*((-len(buf))%4));start=len(buf);buf.extend(arr.tobytes());g['bufferViews'].append({'buffer':0,'byteOffset':start,'byteLength':arr.nbytes});x={'bufferView':len(g['bufferViews'])-1,'componentType':ct,'count':len(arr),'type':typ}
  if typ=='VEC3':x.update(min=arr.min(0).tolist(),max=arr.max(0).tolist())
  g['accessors'].append(x);return len(g['accessors'])-1
 for j,(data,material) in enumerate(parts):
  data=data.reshape(-1,12);v=data[:,:3].copy();n=data[:,3:6].copy();n/=np.linalg.norm(n,axis=1)[:,None];t=data[:,6:10].copy();t[:,:3]-=n*np.sum(n*t[:,:3],axis=1)[:,None];t[:,:3]/=np.linalg.norm(t[:,:3],axis=1)[:,None];t[:,3]=np.where(t[:,3]<0,-1,1);uv=data[:,10:12].copy();frames[str(j)]={k:v0.tolist() for k,v0 in [('v',v),('n',n),('t',t),('uv',uv)]}
  if compiler:v[:,2]*=-1;n[:,2]*=-1;t[:,2:4]*=-1
  g['meshes'][0]['primitives'].append({'mode':4,'material':material,'indices':acc(np.arange(len(v)),'SCALAR',5125),'attributes':{'POSITION':acc(v,'VEC3'),'NORMAL':acc(n,'VEC3'),'TANGENT':acc(t,'VEC4'),'TEXCOORD_0':acc(uv,'VEC2')}})
 g['buffers']=[{'uri':stem+'.bin','byteLength':len(buf)}];bp.write_bytes(buf);write(path,g);newcount=sum(len(x)for x,_ in parts)
 if compiler:
  sf=json.loads((OUT/'retained-source-frames.json').read_text());sf['hull']=frames;write(OUT/'retained-source-frames.json',sf)
 return {'old_triangles':oldcount,'new_triangles':newcount,'paint_triangles':len(marks),'selected_source_faces':selected,'bounds':{'x':[-9,9],'z':[54,72],'y_min':18},'added_geometry_layers':0,'method':'Clip original triangles along paint boundary and replace material/UV, preserving all positions on existing plating'}
h=process('expanse12_pella_hull',True);e=process('expanse12_pella_editable',False);meta=json.loads((AUD/'integration-spec.json').read_text());meta['counts']['hull']=h['new_triangles'];meta['assembled_triangle_total']=e['new_triangles'];meta['free_navy_emblem']=h;meta['free_navy_emblem']['texture_source']=str(texture);write(AUD/'integration-spec.json',meta)
write(AUD/'emblem-source.json',{'status':'PASS offline source preparation; compiled validation pending','reference':'/tmp/codex-clipboard-3fac540f-2f08-44e8-a6b3-a3e204fac1a9.png','placement_reference':'/tmp/codex-clipboard-872e1a76-e69c-4245-867e-02fb6414a1d3.png','generated_with':'Built-in image_gen, two passes; cleaned eagle silhouette then opaque charcoal panel texture','source':str(texture),'sha256':hashlib.sha256(texture.read_bytes()).hexdigest(),'prompt':'Preserve reference Free Navy eagle silhouette, pale gray paint on charcoal background, clean edges, no text or border.','placement':h,'runtime':'NOT RUN','limitations':'Reference-guided recreation and prototype fore dorsal panel placement, not exact screen UV authoring.'});print(h,e)
