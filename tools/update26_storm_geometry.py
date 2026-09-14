"""Storm appearance-only revision from frozen0.25 bytes, with an existing drive kitbash."""
from pathlib import Path
import sys,struct,copy,hashlib
import numpy as np
from scipy.sparse import coo_matrix
from scipy.sparse.csgraph import connected_components
MAIN=Path('/run/media/haker/NVME 2/expanse-mod');sys.path.insert(0,str(MAIN/'tools'))
from common import read,write,read_mesh
import update12_scirocco_common as h
ROOT=Path(__file__).resolve().parents[1];BASE=MAIN/'build/experiments/expanse_update25';OUT=ROOT/'assets/derived/update26-storm';BUILD=ROOT/'build/update26-storm';AUD=ROOT/'audit/update26-storm';NAME='expanse24_storm_hull'
for p in [OUT,BUILD,AUD]:p.mkdir(parents=True,exist_ok=True)
h.OUT=OUT
def load(name):
 p=BASE/'meshes'/(name+'.mesh');b=p.read_bytes();cnt=struct.unpack_from('<Q',b,53)[0];off=61;rows=[]
 for _ in range(cnt):
  vals=struct.unpack_from('<12f?',b,off);rows.append(vals[:-1]);off+=49+(8 if vals[-1]else 0)
 count=struct.unpack_from('<Q',b,off)[0];return np.array(rows),np.frombuffer(b,'<u4',count,off+8).reshape(-1,3)
v,ix=load(NAME);tri=v[ix,:3];original_tri=tri.copy();old=read(MAIN/'audit/update24-storm/integration-spec.json');points=copy.deepcopy(old['meshpoints']);rigs=copy.deepcopy(old['rigs']);frozen=read(BASE/'entities/expanse24_gathering_storm.unit');oldspatial=copy.deepcopy(frozen['spatial']);oldspatial.pop('collision_rank',None)
# Subtract a small sixteen-sided engine aperture from stern faces only. Plane
# partition clips triangles rather than deleting broad hull surfaces by centroid.
planes=[(np.array([np.cos(a),np.sin(a),0.]),13.8)for a in np.arange(16)*2*np.pi/16]+[(np.array([0.,0.,1.]),-164.)]
def split(poly,n,d):
 inside=[];outside=[]
 for i,a in enumerate(poly):
  b=poly[(i+1)%len(poly)];da=float(a@n-d);db=float(b@n-d)
  (inside if da<=0 else outside).append(a)
  if (da<=0)!=(db<=0):
   q=a+(b-a)*da/(da-db);inside.append(q);outside.append(q)
 return inside,outside
result=[];touched=0
for t in tri:
 if t[:,2].min()>-164 or (t[:,:2].min(0)>13.81).any() or (t[:,:2].max(0)<-13.81).any():result.append(t);continue
 remains=list(t);pieces=[]
 for n,d in planes:
  if len(remains)<3:break
  remains,outside=split(remains,n,d)
  if len(outside)>=3:pieces.extend([[outside[0],outside[i],outside[i+1]]for i in range(1,len(outside)-1)])
 if len(remains)>=3:touched+=1
 result.extend(pieces)
tri=np.array(result);q=np.cross(tri[:,1]-tri[:,0],tri[:,2]-tri[:,0]);tri=tri[np.linalg.norm(q,axis=1)>1e-7]
# Broad spatial regions avoid the previous normal-sign-based paint speckling.
mid=tri.mean(1);labels=np.full(len(tri),'ice',dtype='<U8');labels[mid[:,0]>4]='blush';labels[mid[:,1]>14]='pearl';labels[(mid[:,2]>140)&(np.abs(mid[:,0])<4)]='dark'
colors={'pearl':[.50,.56,.63,1],'ice':[.25,.38,.48,1],'blush':[.42,.32,.40,1],'dark':[.055,.07,.085,1]}
def flat(t,material):
 v=t.reshape(-1,3);q=np.cross(t[:,1]-t[:,0],t[:,2]-t[:,0]);n=q/np.linalg.norm(q,axis=1,keepdims=True);n=np.repeat(n,3,axis=0)
 # Stable orthonormal tangent frame, no cross-facet normal averaging.
 axes=np.eye(3)[np.argmin(abs(n),axis=1)];tan=axes-n*(axes*n).sum(1,keepdims=True);tan/=np.linalg.norm(tan,axis=1,keepdims=True);uv=np.full((len(v),2),.5)
 return {'v':v,'n':n,'t':np.column_stack([tan,np.ones(len(v))]),'uv':uv,'i':np.arange(len(v)).reshape(-1,3),'material':material}
parts=[flat(tri[labels==k],'storm_'+k)for k in colors if (labels==k).any()]
# Reuse exact connected component185 of the reviewed Truman drive, located by
# its measured original bounds; retain its UVs and normals under uniform scale.
dv,di=load('expanse15_truman_hull');box=np.array([[-115.8251,-83.3203,-428.4792],[-37.9893,-5.4845,-381.2714]]);selected=di[((dv[di,:3]>=box[0]-1e-3)&(dv[di,:3]<=box[1]+1e-3)).all((1,2))];tt=dv[selected,:3];unique,inv=np.unique(np.round(tt.reshape(-1,3),3),axis=0,return_inverse=True);w=inv.reshape(-1,3);e=np.concatenate([w[:,[0,1]],w[:,[1,2]],w[:,[0,2]]]);_,lab=connected_components(coo_matrix((np.ones(len(e)),(e[:,0],e[:,1])),shape=(len(unique),len(unique))),directed=False);lab=lab[w[:,0]];which=int(np.argmax(np.bincount(lab)));bell_count=int((lab==which).sum());assert bell_count==2240;di=selected # Complete bounded engine cluster includes the inner throat and support rings.
used,remap=np.unique(di,return_inverse=True);rows=dv[used];srcv=rows[:,:3];lo=srcv.min(0);hi=srcv.max(0);scale=27./max(hi[:2]-lo[:2]);center=np.r_[(lo[:2]+hi[:2])/2,lo[2]];newv=(srcv-center)*scale+[0,0,-187.5];drive={'v':newv,'n':rows[:,3:6].copy(),'t':rows[:,6:10].copy(),'uv':rows[:,10:12].copy(),'i':remap.reshape(-1,3),'material':'storm_drive'};parts.append(drive)
for pt in points:
 if pt['name']=='exhaust.0':pt['translation']=[0.,0.,-187.9]
for suffix,compiler in [('_hull',True),('_editable',False)]:
 name='expanse24_storm'+suffix;h.savegltf(name,parts,points,compiler);p=OUT/(name+'.gltf');g=read(p)
 for m in g['materials']:
  key=m['name'].removeprefix('storm_');m['pbrMetallicRoughness']={'baseColorFactor':colors.get(key,[.25,.25,.25,1]),'metallicFactor':.28,'roughnessFactor':.55}
 g['asset']['generator']='Storm0.26 hard-facet normals; restrained crystalline regions; native Truman drive kitbash';write(p,g)
np.savez_compressed(OUT/'reference-frames.npz',**{f'{i}_{k}':p[k]for i,p in enumerate(parts)for k in ['v','n','t','uv']})
vv=np.concatenate([p['v']for p in parts]);assert np.all(vv.max(0)<=original_tri.max((0,1))+1e-4) and np.all(vv.min(0)>=original_tri.min((0,1))-1e-4)
assert np.allclose(original_tri.min((0,1)),vv.min(0),atol=1e-4)and np.allclose(original_tri.max((0,1)),vv.max(0),atol=1e-4)
report={'status':'GEOMETRY READY; COMPILATION PENDING','hull_mesh':NAME,'colors':colors,'meshpoints':points,'rigs':rigs,'spatial':oldspatial,'fixed_rail':old['fixed_rail'],'source':{'remaining_triangles':sum(len(p['i'])for p in parts),'original_hull_triangles':len(original_tri),'aperture_touched_faces':touched,'new_hull_triangles':len(tri),'drive_triangles':len(di),'source_game_hull':str(BASE/'meshes'/(NAME+'.mesh')),'source_game_hull_sha256':hashlib.sha256((BASE/'meshes'/(NAME+'.mesh')).read_bytes()).hexdigest()},'drive':{'source_game_mesh':'expanse15_truman_hull','source_component':'185 bell plus contained engine hardware','source_bounds':[lo.tolist(),hi.tolist()],'source_uvs_preserved':True,'uniform_scale':float(scale),'final_opening_center':[0.,0.,-187.5],'opening_diameter':27.,'exhaust_old':old['meshpoints'][-1]['translation'],'exhaust_new':[0.,0.,-187.9],'adaptation':'Native human drive cone kitbashed as readable gameplay machinery, not canonical Laconian drive reconstruction.'},'changes':['Flat face normals remove inappropriate smoothing across printable facets.','Muted coherent spatial color regions replace per-normal paint speckling.','Material roughness0.55/metallic0.28 reduce blown-out triangle reflections.','Stern aperture with preserved original outer bounds accepts an existing detailed drive cone.'],'source_reference':'https://expanse.fandom.com/wiki/Gathering_Storm','runtime':'NOT RUN','adaptations':['Wiki appearance paragraph describes crystalline knife form, pink/blue facets and unusual tail drive; no plot events used.','Same375gameunit silhouette bounds, same gun/mount points and required gameplay spatial values.','Six PDCs remain separate native rotating meshes.','Existing fan hull print seams remain; no claim of canonical model.']}
write(AUD/'integration-spec.json',report);print(len(tri),'hull triangles +',len(di),'drive-cluster triangles; bounds preserved')
