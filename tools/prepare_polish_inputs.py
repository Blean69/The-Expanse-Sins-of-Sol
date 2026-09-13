"""Review final worker geometry and emit main-owned package integration metadata."""
from pathlib import Path
import argparse, json, struct
import numpy as np
from validate_experiments import read, sha256, require
from build_polish import write, ROOT

def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--worker',type=Path,required=True);a=p.parse_args()
    meta=read(a.worker/'audit/polish-b/mount-metadata.json');checks=read(a.worker/'audit/polish-b/output-validation.json')
    require(checks['status']=='PASS OFFLINE ONLY' and checks['triangle_total']==14622,'Geometry worker checks incomplete')
    spec={'status':'PASS','hull_mesh':'expanse_polish_hull','mounts':[r['mount'] for r in meta['rigs']],
          'meshes':[],'worker_report':str((a.worker/'audit/polish-b/output-validation.json').resolve())}
    records=[]
    for item in checks['outputs'].values():
        path=Path(item['mesh']);require(sha256(path)==item['sha256'],'Compiled mesh hash drift')
        b=path.read_bytes();count=struct.unpack_from('<Q',b,53)[0];offset=61;rows=[]
        for _ in range(count):
            v=struct.unpack_from('<12f?',b,offset);offset+=49+(8 if v[-1] else 0);rows.append(v[:-1])
        v=np.array(rows);ni=struct.unpack_from('<Q',b,offset)[0];offset+=8
        idx=np.frombuffer(b,dtype='<u4',count=ni,offset=offset).reshape(-1,3);normal=v[:,3:6];tangent=v[:,6:9]
        require(np.isfinite(v).all() and np.max(np.abs((normal*tangent).sum(1)))<2e-5 and np.max(np.abs(np.linalg.norm(tangent,axis=1)-1))<2e-5,'Invalid shading frame')
        tri=v[:,:3][idx];face=np.cross(tri[:,1]-tri[:,0],tri[:,2]-tri[:,0]);n=normal[idx].mean(1)
        align=(face*n).sum(1)/np.maximum(np.linalg.norm(face,axis=1)*np.linalg.norm(n,axis=1),1e-15)
        require(not (align< -1e-5).any(),'Opposed triangle winding')
        require(item['only_tangent_fields_changed'] and item['trailer_sha256_before']==item['trailer_sha256_after'] and item['orthogonal_fallback_vertex_count']==0,'Unsafe mesh repair')
        materials={ident:str(ROOT/'assets/derived/baseline/game-materials'/('mcrn_tachi'+ident.split('_mcrn_tachi',1)[1]+'.mesh_material')) for ident in item['materials']}
        require(all(Path(v).is_file() for v in materials.values()),'Missing ignored material source')
        spec['meshes'].append({'path':str(path),'sha256':item['sha256'],'material_sources':materials})
        records.append({'mesh':path.name,'triangles':len(idx),'invalid_tangent_frames':0,'opposed_winding':0,'sha256':sha256(path)})
    require(len(records)==13 and sum(r['triangles'] for r in records)==14622,'Missing meshes or changed triangle budget')
    write(ROOT/'build/polish-inputs/geometry/integration-spec.json',spec)
    write(ROOT/'audit/polish/integrator-mesh-check.json',{'status':'PASS','meshes':records,'runtime':'NOT RUN'})
    print('PASS: thirteen binary meshes independently checked; main integration metadata prepared')

if __name__=='__main__':
    try:main()
    except (ValueError,FileNotFoundError) as e:raise SystemExit(str(e))
