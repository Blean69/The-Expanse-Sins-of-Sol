"""Project paths and read-only asset readers. No writes to installed content."""
from pathlib import Path
import json, os, struct
import numpy as np

ROOT = Path(__file__).resolve().parents[1]
GAME = Path(os.environ.get('SINS2_GAME', ROOT.parent / 'SteamLibrary/steamapps/common/Sins2'))
SDK = Path(os.environ.get('SINS2_SDK', ROOT.parent / 'SteamLibrary/steamapps/common/Sins of a Solar Empire II - Mod Tools'))

def read(path):
    return json.loads(Path(path).read_text(encoding='utf-8-sig'))

def write(path, data):
    path = Path(path)
    if path.resolve().is_relative_to(GAME.resolve()) or path.resolve().is_relative_to(SDK.resolve()):
        raise ValueError('Installed data is read-only')
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False) + '\n')

def read_mesh(path):
    """Read the installed unskinned binary layout, fail closed on unknown layout.

    Prefix layout cross-checked with linked Blender extension binary_reader.py.
    Current files also have an opaque trailer; this reader is NOT an exporter.
    """
    b = Path(path).read_bytes(); offset = 0
    def take(fmt):
        nonlocal offset
        v = struct.unpack_from('<'+fmt, b, offset); offset += struct.calcsize('<'+fmt)
        return v[0] if len(v) == 1 else list(v)
    def string():
        nonlocal offset
        size = take('I'); s=b[offset:offset+size].decode(); offset += size; return s
    def count():
        n=take('Q'); assert n < 10000000; return n
    header=take('4s').hex(); assert take('?') is False, 'Skinned mesh unsupported'
    box=take('6f'); sphere=take('4f'); padding=take('Q')
    n=count(); positions=[]
    for _ in range(n):
        positions.append(take('3f')); take('3f'); take('4f'); take('2f')
        if take('?'): take('2f')
    ni=count(); indices=[take('I') for _ in range(ni)]
    primitives=[{'material_index':take('h'),'vertex_index_start':take('I'),'vertex_index_count':take('I')} for _ in range(count())]
    points=[]
    for _ in range(count()):
        points.append({'name':string(),'position':take('3f'),'rotation':take('9f'),'bone_index':take('h')})
    assert count() == 0, 'Bones unsupported'
    materials=[string() for _ in range(count())]
    assert offset <= len(b)
    assert max(indices) < n
    return dict(header=header,vertices=n,triangles=ni//3,box=box,sphere=sphere,meshpoints=points,materials=materials,primitives=primitives,parsed_prefix_bytes=offset,opaque_trailer_bytes=len(b)-offset)

class Gltf:
    def __init__(self,path):
        self.path=Path(path); self.g=read(path)
        self.buffers=[(self.path.parent/b['uri']).read_bytes() for b in self.g['buffers']]
        self.world={}; self.parents={}
        def walk(i, parent):
            n=self.g['nodes'][i]
            if 'matrix' in n: m=np.array(n['matrix']).reshape(4,4).T
            else:
                x,y,z,w=n.get('rotation',[0,0,0,1])
                m=np.eye(4); m[:3,:3]=np.array([[1-2*(y*y+z*z),2*(x*y-z*w),2*(x*z+y*w)],[2*(x*y+z*w),1-2*(x*x+z*z),2*(y*z-x*w)],[2*(x*z-y*w),2*(y*z+x*w),1-2*(x*x+y*y)]]) @ np.diag(n.get('scale',[1,1,1]))
                m[:3,3]=n.get('translation',[0,0,0])
            self.world[i]=parent@m
            for c in n.get('children',[]): self.parents[c]=i; walk(c,self.world[i])
        for i in self.g['scenes'][self.g.get('scene',0)]['nodes']: walk(i,np.eye(4))
    def accessor(self,i):
        a=self.g['accessors'][i]; assert 'sparse' not in a
        v=self.g['bufferViews'][a['bufferView']]
        dtype={5126:'<f4',5125:'<u4',5123:'<u2',5121:'u1'}[a['componentType']]
        size={'SCALAR':1,'VEC2':2,'VEC3':3,'VEC4':4}[a['type']]
        d=np.dtype(dtype); stride=v.get('byteStride',size*d.itemsize)
        return np.ndarray((a['count'],size),dtype=d,buffer=self.buffers[v['buffer']],offset=v.get('byteOffset',0)+a.get('byteOffset',0),strides=(stride,d.itemsize)).copy()
    def positions(self,i,primitive):
        v=self.accessor(primitive['attributes']['POSITION']); m=self.world[i]
        return v@m[:3,:3].T+m[:3,3]
