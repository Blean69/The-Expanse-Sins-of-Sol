"""Bind sampled PDC hull geometry to final compiled meshes and native mount frames."""
from pathlib import Path
import argparse,hashlib,json,struct
import numpy as np
from common import read_mesh


def canonical(tri):
    # Exact float32 game positions; sort corners then faces. Winding/order irrelevant.
    t=np.asarray(tri,dtype=np.float32)
    order=np.lexsort((t[:,:,2],t[:,:,1],t[:,:,0]),axis=1)
    t=np.take_along_axis(t,order[:,:,None],axis=1).reshape(-1,9)
    return t[np.lexsort(tuple(t[:,i]for i in range(8,-1,-1)))].copy()


def bind(mesh,npz,unit):
    b=mesh.read_bytes();assert b[4]==0,'Skinned mesh unsupported'
    count=struct.unpack_from('<Q',b,53)[0];assert 0<count<10000000;offset=61;v=[]
    for _ in range(count):
        row=struct.unpack_from('<12f?',b,offset);offset+=49+(8 if row[-1]else 0);v.append(row[:3])
    ni=struct.unpack_from('<Q',b,offset)[0];offset+=8;i=np.frombuffer(b,dtype='<u4',count=ni,offset=offset).reshape(-1,3)
    tri=np.array(v)[i];source=np.load(npz)['tri'];a,c=canonical(tri),canonical(source)
    assert a.shape==c.shape,(a.shape,c.shape)
    error=float(np.max(np.abs(a.astype(float)-c.astype(float))))
    assert error<=2e-5,('Source and shipped triangle geometry differ',error)
    model=read_mesh(mesh);frames=[]
    for mount in json.loads(unit.read_text())['weapons']['weapons']:
        if '_pdc_'not in mount['weapon']:continue
        point=next(p for p in model['meshpoints']if p['name']==mount['mesh_point']);matrix=np.array(point['rotation']).reshape(3,3)
        expected=np.array([np.cross(mount['up'],mount['forward']),mount['up'],mount['forward']])
        assert np.allclose(matrix,expected,rtol=0,atol=2e-5)
        assert np.allclose(point['position'],mount['weapon_position'],rtol=0,atol=2e-5)
        frames.append({'weapon':mount['weapon'],'status':'PASS','max_basis_error':float(np.max(abs(matrix-expected))),'max_position_error':float(np.max(abs(np.array(point['position'])-mount['weapon_position'])))})
    assert len(frames)==9
    return {'status':'PASS','identity':unit.stem,'mesh_path':str(mesh),'mesh_sha256':hashlib.sha256(b).hexdigest(),'npz_path':str(npz),'npz_sha256':hashlib.sha256(npz.read_bytes()).hexdigest(),'triangle_count':len(tri),'correspondence':'Triangle vertex coordinates canonicalized after float32 conversion; corners and triangles sorted independently, ignoring winding and order. Full coordinate arrays compared, not centroid/count-only.','absolute_tolerance':2e-5,'max_coordinate_error':error,'exact_float32_match':bool(np.array_equal(a,c)),'canonical_compiled_triangle_sha256':hashlib.sha256(a.tobytes()).hexdigest(),'canonical_source_triangle_sha256':hashlib.sha256(c.tobytes()).hexdigest(),'mount_frames':frames}


def main():
    ap=argparse.ArgumentParser();ap.add_argument('--hulls-root',type=Path,required=True);ap.add_argument('--baseline',type=Path,required=True);ap.add_argument('--audit',type=Path,required=True);a=ap.parse_args();results=[]
    for kind in ['raptor','pella']:
        name='expanse12_'+kind;p=json.loads((a.audit/(name+'-proposal.json')).read_text());npz=Path(p['hull_source']);assert hashlib.sha256(npz.read_bytes()).hexdigest()==p['hull_sha256']
        mesh=a.hulls_root/'build/update14-hulls'/kind/'game/meshes'/(name+'_hull.mesh')
        results.append(bind(mesh,npz,a.baseline/'entities'/(name+'.unit')))
    out={'status':'PASS','runtime':'NOT RUN','ships':results,'limits':'This establishes the sampled hull is the shipped geometry, not continuous line-of-fire proof. Each proposal and its native unit basis are bound to the final compiled hull.'}
    (a.audit/'final-compiled-geometry.json').write_text(json.dumps(out,indent=2)+'\n');print(json.dumps([{k:x[k]for k in ['identity','triangle_count','exact_float32_match','max_coordinate_error','mesh_sha256']}for x in results],indent=2))


if __name__=='__main__':main()
