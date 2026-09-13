from common import *
SRC=Path('/run/media/haker/NVME 2/expanse-workers/validation/assets/derived/amun05-c/master');SOURCE=SRC/'Amun-Ra_Class_Stealth_Ship_[The_Expanse].gltf';a=Gltf(SOURCE);cancel=np.linalg.inv(a.world[3]);AUDIT=ROOT/'audit/amun06-b';OUT=ROOT/'assets/derived/amun06-b';BUILD=ROOT/'build/amun06-b'
def descendants(i):
 out=[i]
 for c in a.g['nodes'][i].get('children',[]):out.extend(descendants(c))
 return out
def matrix(i):return cancel@a.world[i]
def arrays(i,root_inverse=None):
 n=a.g['nodes'][i];result=[]
 if 'mesh' not in n:return result
 M=(cancel if root_inverse is None else root_inverse)@a.world[i]
 for pr in a.g['meshes'][n['mesh']]['primitives']:
  idx=a.accessor(pr['indices']).flatten();used,remap=np.unique(idx,return_inverse=True);v=a.accessor(pr['attributes']['POSITION'])[used]@M[:3,:3].T+M[:3,3];no=a.accessor(pr['attributes']['NORMAL'])[used]@np.linalg.inv(M[:3,:3]);no/=np.linalg.norm(no,axis=1)[:,None];ta=a.accessor(pr['attributes']['TANGENT'])[used];ta[:,:3]=ta[:,:3]@M[:3,:3].T;ta[:,:3]/=np.linalg.norm(ta[:,:3],axis=1)[:,None];uv=a.accessor(pr['attributes']['TEXCOORD_0'])[used];result.append({'v':v,'n':no,'t':ta,'uv':uv,'i':remap.reshape(-1,3),'node':i})
 return result
