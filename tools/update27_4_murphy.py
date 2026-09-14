"""Replace Murphy's printed aft stub with the existing textured Tachi Epstein bell."""
import sys
import numpy as np
from scipy.spatial.transform import Rotation
from common import ROOT,read,read_mesh,write
from update26_platform_common import load_parts,export,compile as compile_mesh
from update23_murphy_art import frames
BASE=ROOT/'build/experiments/expanse_update27_3';OUT=ROOT/'build/update27_4-murphy';ART=OUT/'game';NAME='expanse23_murphy_hull';AUD=ROOT/'audit/update27_4'

def clip(t,z):
    out=[]
    for a,b in zip(t,np.roll(t,-1,axis=0)):
        da=a[2]-z;db=b[2]-z
        if da>=0:out.append(a)
        if da*db<0:out.append(a+(b-a)*da/(da-db))
    return [[out[0],out[i],out[i+1]] for i in range(1,len(out)-1)]

def prepare():
    parts=load_parts(BASE/'meshes'/(NAME+'.mesh'));old=read_mesh(BASE/'meshes'/(NAME+'.mesh'));points=[{'name':p['name'],'translation':p['position'],'rotation':Rotation.from_matrix(np.array(p['rotation']).reshape(3,3).T).as_quat().tolist()}for p in old['meshpoints']]
    center=np.array(next(p['translation']for p in points if p['name']=='exhaust.0'));center[2]+=.4
    groups=[];materials={};removed=0
    for p in parts:
        mat=p['material'];p['material']=mat.removeprefix(NAME+'_');materials[p['material']]=mat
        if mat.endswith('_nozzle'):removed+=len(p['i']);continue
        if mat.endswith('_machinery'):
            original=p['v'][p['i']];tri=np.array([q for t in original for q in clip(t,-94.)]);removed+=len(original)-len(tri);p={**frames(tri),'material':p['material']}
        groups.append(p)
    source=BASE/'meshes/expanse03_hull.mesh';low=np.array([-9.061,-19.151,-47.959]);high=np.array([9.061,-1.027,-36.208]);origin=np.array([0.,-10.0899,-47.957733154296875]);scale=34/18.12108;bells=[]
    for i,p in enumerate(load_parts(source)):
        tri=p['v'][p['i']];ids=p['i'][((tri>=low)&(tri<=high)).all((1,2))]
        if not len(ids):continue
        p['i']=ids;p['v']=(p['v']-origin)*scale+center;key='epstein_'+str(i);materials[key]=p['material'];p['material']=key;bells.append(p)
    drive_triangles=sum(len(p['i'])for p in bells);assert drive_triangles>1200
    # Closed annular connector overlaps both the retained aft cylinder and bell neck.
    neckz=center[2]+11.74821854*scale;neckr=5.03377*scale;angle=np.arange(64)*2*np.pi/64;ring=np.column_stack([np.cos(angle),np.sin(angle),np.zeros(64)])
    a=ring*17+[*center[:2],-92.];b=ring*(neckr+.2)+[*center[:2],neckz-.2];ai=ring*16.4+[*center[:2],-92.];bi=ring*(neckr-.4)+[*center[:2],neckz-.2];tri=[]
    for r,s in [(a,b),(bi,ai),(ai,a),(b,bi)]:
        for i in range(64):
            j=(i+1)%64;tri += [[r[i],r[j],s[j]],[r[i],s[j],s[i]]]
    materials['connector']=NAME+'_machinery';groups.append({**frames(np.array(tri)),'material':'connector'});groups+=bells
    dest=OUT/'source';export(NAME,groups,points,dest)
    for key,src in materials.items():
        if key=='nozzle':continue
        p=BASE/'mesh_materials'/(src+'.mesh_material');write(ART/'mesh_materials'/(NAME+'_'+key+'.mesh_material'),read(p))
    vertices=np.concatenate([p['v'][np.unique(p['i'])]for p in groups])
    write(AUD/'murphy-drive.json',{'source_mesh':str(source),'drive_triangles':drive_triangles,'hull_triangles':sum(len(p['i'])for p in groups),'opening_center':center.tolist(),'diameter':34,'stub_cut_plane':-94,'neck_z':neckz,'connector_root_z':-92,'old_stub_faces_removed_net':removed,'points':points,'materials':materials,'bounds_min':vertices.min(0).tolist(),'bounds_max':vertices.max(0).tolist(),'status':'PREPARED','runtime':'NOT RUN'})

def compile():
    a=read(AUD/'murphy-drive.json');OUT.mkdir(exist_ok=True);c=compile_mesh(NAME,OUT/'source',OUT,ART,a['points']);a['compiler']=c;a['status']='OFFLINE COMPILED';write(AUD/'murphy-drive.json',a)

def preview():
    from PIL import Image
    from polish_ui import render
    parts=[]
    for p in load_parts(ART/'meshes'/(NAME+'.mesh')):
        material=read(ART/'mesh_materials'/(p['material']+'.mesh_material'));tex=np.asarray(Image.open(BASE/'textures'/(material['base_color_texture']+'.dds')).convert('RGBA'));parts.append((p['v'][p['i']],p['uv'][p['i']],tex,[1,1,1,1],'OPAQUE'))
    B=np.array([[.8,0,.6],[-.3,.866,.4],[.52,.5,-.693]])
    render(parts,(1000,750),B).save(AUD/'murphy-aft.png')
if __name__=='__main__':globals()[sys.argv[1]]()
