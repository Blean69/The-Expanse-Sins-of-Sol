"""Independently check the armed hero binary before package integration."""
from pathlib import Path
import argparse,struct
import numpy as np
from validate_experiments import read,sha256,require
from build_polish import ROOT,write

def main(worker):
    report=read(worker/'audit/geometry03-b/hero-armed-output-validation.json')
    require(report['status']=='PASS OFFLINE ONLY' and report['triangle_total']==26935,'Hero compile incomplete')
    require(len(report['outputs'])==1,'Unexpected hero mesh count')
    row=next(iter(report['outputs'].values()));p=Path(row['mesh']);require(sha256(p)==row['sha256'],'Hero mesh drift')
    b=p.read_bytes();n=struct.unpack_from('<Q',b,53)[0];offset=61;vertices=[]
    for _ in range(n):
        v=struct.unpack_from('<12f?',b,offset);offset+=49+(8 if v[-1] else 0);vertices.append(v[:-1])
    v=np.array(vertices);ni=struct.unpack_from('<Q',b,offset)[0];offset+=8;idx=np.frombuffer(b,dtype='<u4',count=ni,offset=offset).reshape(-1,3)
    require(np.isfinite(v).all() and idx.max()<n and len(idx)==26935,'Bad hero vertices/indices')
    normal=v[:,3:6];tangent=v[:,6:9];require(abs((normal*tangent).sum(1)).max()<2e-5 and abs(np.linalg.norm(tangent,axis=1)-1).max()<2e-5,'Bad hero tangent frames')
    tri=v[:,:3][idx];f=np.cross(tri[:,1]-tri[:,0],tri[:,2]-tri[:,0]);ns=normal[idx].mean(1);a=(f*ns).sum(1)/np.maximum(np.linalg.norm(f,axis=1)*np.linalg.norm(ns,axis=1),1e-15)
    require(not (a< -1e-5).any(),'Hero opposed winding')
    require(row['only_tangent_fields_changed'] and row['trailer_sha256_before']==row['trailer_sha256_after'] and row['orthogonal_fallback_vertex_count']==0,'Unsafe hero binary repair')
    game=p.parent.parent
    for m in row['materials']:
        material=read(game/'mesh_materials'/(m+'.mesh_material'))
        for k,val in material.items():
            if k.endswith('_texture'):require((game/'textures'/(val+'.dds')).is_file(),'Missing hero texture '+val)
    spec={'status':'PASS','mesh_id':p.stem,'mesh':str(p),'sha256':sha256(p),'triangles':len(idx),'game_root':str(game),'worker_report':str(worker/'audit/geometry03-b/hero-armed-output-validation.json'),'runtime':'NOT RUN'}
    write(ROOT/'build/combat03-inputs/hero/integration-spec.json',spec);write(ROOT/'audit/combat03/hero-integrator-mesh-check.json',spec)
    print('PASS: armed hero binary, shading frames, winding, materials/textures; runtime NOT RUN')
if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--worker',type=Path,required=True);main(p.parse_args().worker)
