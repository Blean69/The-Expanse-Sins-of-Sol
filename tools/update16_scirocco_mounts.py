"""Narrow only the twelve oversized support collars in the accepted compiled mesh.
Retains known native mesh layout, all body/gun geometry and attachment records.
"""
from pathlib import Path
import struct
import numpy as np
from common import read_mesh
from build_combat04 import binary_geometry
from build_polish import write
from validate_experiments import read,require,sha256
ROOT=Path(__file__).resolve().parents[1]
BASE=ROOT/'build/experiments/expanse_update15'
OUT=ROOT/'build/update16-scirocco'
AUD=ROOT/'audit/update16'
REL='meshes/expanse12_scirocco_hull.mesh'

def decode(path):
    raw=bytearray(path.read_bytes());nv=struct.unpack_from('<Q',raw,53)[0];offset=61;rows=[];offsets=[]
    for _ in range(nv):
        offsets.append(offset);v=struct.unpack_from('<12f?',raw,offset);rows.append(v[:-1]);offset+=49+(8 if v[-1] else 0)
    ni=struct.unpack_from('<Q',raw,offset)[0];idx=np.frombuffer(raw,dtype='<u4',count=ni,offset=offset+8).copy().reshape(-1,3)
    return raw,np.array(rows),idx,offsets

def main():
    path=BASE/REL;parsed=read_mesh(path);raw,rows,idx,offsets=decode(path);old=rows.copy()
    section=next(p for p in parsed['primitives']if parsed['materials'][p['material_index']].endswith('_mat_2'))
    start=section['vertex_index_start'];count=section['vertex_index_count'];require(count==3456,'Expected exactly12 authored96-triangle collars')
    chosen=np.zeros(len(idx),dtype=bool);chosen[start//3:(start+count)//3]=True;faces=idx[chosen]
    require(len(faces)==1152 and not set(faces.flat).intersection(idx[~chosen].flat),'Collars must use isolated vertices')
    rigs=[r for r in read(ROOT/'audit/update14-scirocco/integration-spec.json')['rigs']if r['kind']=='pdc']
    origins=np.array([r['yaw_pivot_hull']for r in rigs]);ups=np.array([np.array(r['basis_columns'])[:,1]for r in rigs])
    centers=np.array([o-u*(r['support']['top']-r['support']['bottom'])/2 for o,u,r in zip(origins,ups,rigs)])
    verts=np.unique(faces);assignment=np.argmin(np.linalg.norm(rows[verts,None,:3]-centers[None,:,:],axis=2),axis=1)
    checks=[];body=old[:,:3][idx[~chosen]]
    def surface(o,d):
        e=body[:,1]-body[:,0];f=body[:,2]-body[:,0];h=np.cross(d,f);det=(e*h).sum(1);inv=np.divide(1,det,out=np.zeros_like(det),where=abs(det)>1e-10);v=o-body[:,0];a=(v*h).sum(1)*inv;q=np.cross(v,e);b=q@d*inv;t=(f*q).sum(1)*inv
        ok=(abs(det)>1e-10)&(a>=-1e-7)&(b>=-1e-7)&(a+b<=1+1e-7)&(t>0)
        require(ok.any(),'Support footprint misses preserved hull');return o+d*t[ok].min()
    for j,r in enumerate(rigs):
        ids=verts[assignment==j];require(len(ids)==106,'Unexpected welded collar vertex grouping')
        o=origins[j];up=ups[j];depth=r['support']['top']-r['support']['bottom'];q=rows[ids,:3]-o;z=q@up;rad=q-z[:,None]*up;radius=np.linalg.norm(rad,axis=1)
        require(np.all((abs(z)<1e-4)|(abs(z+depth)<1e-4)),'Unexpected intermediate collar surface')
        require(np.all((radius<1e-4)|(abs(radius-6.6)<1e-4)),'Unexpected collar radius')
        # Keep both attachment planes; upper lip now fits behind the visible gun.
        scale=np.where(abs(z)<1e-4,3.0/6.6,4.0/6.6)
        basis=np.array(r['basis_columns']);heights=[]
        for a in np.arange(8)*np.pi/4:
            lateral=(basis[:,0]*np.cos(a)+basis[:,2]*np.sin(a))*3.8
            contact=surface(o+up*100+lateral,-up);heights.append(float(contact@up))
        bottom=min(r['support']['bottom'],min(heights)-.8)
        new_z=np.where(abs(z)<1e-4,0.,bottom-r['support']['top'])
        rows[ids,:3]=o+new_z[:,None]*up+rad*scale[:,None]
        require(min(heights)>bottom and max(heights)<r['support']['top'],'Narrowed base contact failure')
        checks.append({'weapon':r['mount']['weapon'],'vertices':len(ids),'old_radius':6.6,'new_top_radius':3.,'new_bottom_radius':4.,'gun_attachment_plane_unchanged':True,'old_bottom':r['support']['bottom'],'new_bottom':bottom,'eight_hull_contacts_within_support':True,'contact_heights':heights})
    tri=rows[:,:3][faces];cross=np.cross(tri[:,1]-tri[:,0],tri[:,2]-tri[:,0]);n=cross/np.linalg.norm(cross,axis=1)[:,None]
    require(np.all((n*old[faces,3:6].mean(1)).sum(1)>0),'Support exterior inverted')
    sums=np.zeros((len(rows),3))
    for k in range(3):np.add.at(sums,faces[:,k],cross)
    for v in verts:
        normal=sums[v]/np.linalg.norm(sums[v]);t=old[v,6:9]-normal*np.dot(old[v,6:9],normal);t/=np.linalg.norm(t)
        rows[v,3:6]=normal;rows[v,6:9]=t
    changed=set(verts.tolist());require(np.array_equal(rows[[i for i in range(len(rows))if i not in changed]],old[[i for i in range(len(rows))if i not in changed]]),'Other body vertices changed')
    for v in verts:struct.pack_into('<12f',raw,offsets[v],*rows[v])
    target=OUT/REL;target.parent.mkdir(parents=True,exist_ok=True);target.write_bytes(raw)
    require(read_mesh(target)==parsed,'Native metadata, index buffers or attachments changed')
    geometry=binary_geometry(target)
    # Existing hull finish, scoped to the support-only material; no new textures.
    material='mesh_materials/expanse12_scirocco_hull_expanse12_scirocco_mat_2.mesh_material'
    write(OUT/material,read(BASE/'mesh_materials/expanse12_scirocco_hull_expanse12_scirocco_mat_0.mesh_material'))
    write(AUD/'mount-validation.json',{'status':'PASS OFFLINE','source_mesh_sha256':sha256(path),'geometry':geometry,'body_and_native_metadata_unchanged':True,'support_material':'Same finish as preserved Scirocco hull','mounts':checks,'resources':{REL:str(target),material:str(OUT/material)},'runtime':'NOT RUN; new appearance requires in-game observation'})
    print('PASS twelve narrower supported pedestals; hull/guns/attachments unchanged')
if __name__=='__main__':main()
