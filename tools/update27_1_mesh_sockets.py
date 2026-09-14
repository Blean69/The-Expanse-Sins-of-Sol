"""Add compiler-verified socket metadata; preserve every geometry/material byte."""
from pathlib import Path
import struct,json,os,subprocess,hashlib
from common import ROOT,SDK,read_mesh,write,read
BASE=ROOT/'build/experiments/expanse_update27'
OUT=ROOT/'build/update27_1-sockets';AUD=ROOT/'audit/update27_1'
WINE=Path('/home/haker/.var/app/com.valvesoftware.Steam/.local/share/Steam/steamapps/common/Proton 10.0/files/bin/wine64')
PREFIX=ROOT.parent/'expanse-workers/tachi-one-pdc/build/polish-b/proton-prefix'
ENV=dict(os.environ,WINEPREFIX=str(PREFIX),WINEDEBUG='-all',DISPLAY='',MANGOHUD='0',WINEDLLOVERRIDES='mscoree,mshtml=')
IDENTITY=[1.,0.,0.,0.,1.,0.,0.,0.,1.]
def sha(b):return hashlib.sha256(b).hexdigest()
def section(b):
    """Offsets cross-checked with common.read_mesh and official A/B compilation."""
    assert b[4]==0
    n=struct.unpack_from('<Q',b,53)[0];off=61
    for _ in range(n):off+=49+(8 if b[off+48] else 0)
    n=struct.unpack_from('<Q',b,off)[0];off+=8+4*n
    n=struct.unpack_from('<Q',b,off)[0];off+=8+10*n
    start=off;n=struct.unpack_from('<Q',b,off)[0];off+=8
    for _ in range(n):
        size=struct.unpack_from('<I',b,off)[0];off+=4+size+50
    return start,off

def encode(points):
    data=struct.pack('<Q',len(points))
    for p in points:
        n=p['name'].encode();data+=struct.pack('<I',len(n))+n+struct.pack('<12fh',*p['position'],*p.get('rotation',IDENTITY),p.get('bone_index',0))
    return data

def prove_layout():
    OUT.mkdir(exist_ok=True);src=OUT/'socket-proof';src.mkdir(exist_ok=True)
    positions=[0.,0.,0.,1.,0.,0.,0.,1.,.25];blob=struct.pack('<9f',*positions)+struct.pack('<3I',0,1,2);(src/'proof.bin').write_bytes(blob)
    g={'asset':{'version':'2.0'},'scene':0,'scenes':[{'nodes':[0]}],'nodes':[{'name':'proof','mesh':0}], 'meshes':[{'primitives':[{'attributes':{'POSITION':0},'indices':1}]}], 'buffers':[{'uri':'proof.bin','byteLength':len(blob)}], 'bufferViews':[{'buffer':0,'byteOffset':0,'byteLength':36},{'buffer':0,'byteOffset':36,'byteLength':12}], 'accessors':[{'bufferView':0,'componentType':5126,'count':3,'type':'VEC3','min':[0,0,0],'max':[1,1,.25]},{'bufferView':1,'componentType':5125,'count':3,'type':'SCALAR'}]}
    for semantic,typ,data in [('NORMAL','VEC3',[0.,-.242535625,.9701425]*3),('TANGENT','VEC4',[1.,0.,0.,1.]*3),('TEXCOORD_0','VEC2',[0.,0.,1.,0.,0.,1.])]:
        offset=len(blob);chunk=struct.pack('<'+'f'*len(data),*data);blob+=chunk
        g['bufferViews'].append({'buffer':0,'byteOffset':offset,'byteLength':len(chunk)})
        index=len(g['accessors']);g['accessors'].append({'bufferView':len(g['bufferViews'])-1,'componentType':5126,'count':3,'type':typ})
        g['meshes'][0]['primitives'][0]['attributes'][semantic]=index
    g['materials']=[{'name':'proof_surface','pbrMetallicRoughness':{'baseColorFactor':[1.,1.,1.,1.]}}];g['meshes'][0]['primitives'][0]['material']=0
    g['buffers'][0]['byteLength']=len(blob);(src/'proof.bin').write_bytes(blob)
    outputs=[]
    for label in ['without','with']:
        if label=='with':
            g['nodes'][0]['children']=[1,2];g['nodes'] += [{'name':'child.socket_proof','translation':[.5,1.,-2.]},{'name':'turret_muzzle.0','translation':[0.,.4,-3.]}]
        write(src/'proof.gltf',g);dest=src/label;dest.mkdir(exist_ok=True)
        with (src/(label+'.log')).open('w') as f:subprocess.run([str(WINE),str(SDK/'MeshBuilder/bin/MeshBuilder.exe'),'--input_path=Z:'+str(src/'proof.gltf'),'--output_folder_path=Z:'+str(dest),'--mesh_output_format=binary','--fill_triangle_facing_grid'],env=ENV,stdout=f,stderr=subprocess.STDOUT,check=True,timeout=60)
        outputs.append(dest/'proof.mesh')
    a,b=[p.read_bytes() for p in outputs];sa,ea=section(a);sb,eb=section(b);pts=read_mesh(outputs[1])['meshpoints']
    assert len(pts)==2 and pts[0]['position']==[.5,1.,2.]
    assert a[:sa]==b[:sb] and a[ea:]==b[eb:],'Compiler changes outside socket block'
    assert encode(pts)==b[sb:eb],'Serializer disagrees with official compiler'
    return {'status':'PASS','compiler_ab_only_socket_block_changed':True,'official_point_serialization_matches':True,'without_sha256':sha(a),'with_sha256':sha(b),'points':pts}

def build():
    proof=prove_layout();audit=read(AUD/'turret-socket-audit.json');requests={};consumers={}
    # Engine asks for point TYPES (child / turret_muzzle), not an exact alias
    # spelling. Native examples have intentionally different suffixes.
    for r in audit['bad']:
        for kind,index,field,prefix in [('base',0,'barrel_position','child.'),('barrel',1,'muzzle_positions','turret_muzzle.')]:
            old=r['points'][index]
            if any(p['name'].startswith(prefix) for p in old):continue
            name=r[kind];assert name.startswith('expanse') and not old,'Only empty custom socket tables'
            vals=[r['turret'][field]] if kind=='base' else r['turret'][field]
            points=[{'name':('child.'+r['barrel_alias']) if kind=='base' else 'turret_muzzle.'+str(i),'position':v,'rotation':IDENTITY,'bone_index':0} for i,v in enumerate(vals)]
            if name in requests:assert requests[name]==points,'Incompatible shared socket transforms '+name
            requests[name]=points;consumers.setdefault(name,set()).add(r['unit'])
    records=[]
    for name,points in sorted(requests.items()):
        p=BASE/'meshes'/(name+'.mesh');raw=p.read_bytes();start,end=section(raw);assert end-start==8 and struct.unpack_from('<Q',raw,start)[0]==0
        revised=raw[:start]+encode(points)+raw[end:];dst=OUT/'game/meshes'/p.name;dst.parent.mkdir(parents=True,exist_ok=True);dst.write_bytes(revised);got=read_mesh(dst);before=read_mesh(p)
        for k in ['vertices','triangles','box','sphere','materials','primitives']:assert got[k]==before[k],k
        assert revised[got['parsed_prefix_bytes']:]==raw[before['parsed_prefix_bytes']:]
        assert [p['name'] for p in got['meshpoints']]==[p['name'] for p in points]
        records.append({'path':'meshes/'+p.name,'source':str(dst),'previous_sha256':sha(raw),'sha256':sha(revised),'consumers':sorted(consumers[name]),'meshpoints':got['meshpoints'],'geometry_material_and_acceleration_bytes_unchanged':True})
    write(AUD/'socket-repair.json',{'status':'PASS OFFLINE','official_compiler_proof':proof,'files':records,'runtime':'NOT RUN'});print('Added verified sockets to',len(records),'custom meshes')
if __name__=='__main__':build()
