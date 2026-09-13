from common import *
import hashlib
SRC=Path('/run/media/haker/NVME 2/expanse-workers/validation/assets/derived/donnager04-c/master');SOURCE=SRC/'scene.gltf';a=Gltf(SOURCE);OUT=ROOT/'assets/derived/donnager10-b';AUDIT=ROOT/'audit/donnager10-b';BUILD=ROOT/'build/donnager10-b';INTAKE=Path('/run/media/haker/NVME 2/expanse-mod/audit/donnager04-c');old=read(INTAKE/'scale-and-pdc-donor.json');scale=old['provisional_lore_scale']['Donnager_game_length']/old['Donnager_source_length_exporter_units'];center=np.array([-.000046789646,42.71978135,274.714836017]);target=np.zeros(3)
def source_parts():
 for ni,n in enumerate(a.g['nodes']):
  if 'mesh' not in n:continue
  M=a.world[ni]
  for pi,p in enumerate(a.g['meshes'][n['mesh']]['primitives']):
   v=a.accessor(p['attributes']['POSITION'])@M[:3,:3].T+M[:3,3];no=a.accessor(p['attributes']['NORMAL'])@np.linalg.inv(M[:3,:3]);no/=np.maximum(np.linalg.norm(no,axis=1)[:,None],1e-30);uv=a.accessor(p['attributes']['TEXCOORD_0']);idx=a.accessor(p['indices']).flatten().reshape(-1,3)
   yield {'node':ni,'primitive':pi,'material':p['material'],'v':(v-center)*scale,'n':no,'uv':uv,'i':idx,'world':v,'name':n['name']}
