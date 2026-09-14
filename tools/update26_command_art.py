"""Uniform, private OPA-command derivative of the accepted 0.25 compiled meshes.

Recompile facing grids with the pinned native MeshBuilder. Preserve every source
triangle, UV and material; scale all local geometry and attachment translations.
"""
from pathlib import Path
import copy, hashlib, json, struct, sys
import numpy as np
from scipy.spatial import cKDTree
from scipy.spatial.transform import Rotation
ROOT=Path(__file__).resolve().parents[1]
MAIN=Path('/run/media/haker/NVME 2/expanse-mod')
sys.path.insert(0,str(MAIN/'tools'))
from common import read,read_mesh,write,Gltf
import update12_scirocco_common as c
from flight03_effects import scale_effect,check_structure
sys.path.insert(0,str(ROOT/'tools'))
import update24_behemoth_compile as compiler
BASE=MAIN/'build/experiments/expanse_update25'
BUILD=ROOT/'build/update26-command';OUT=BUILD/'source';GAME=BUILD/'game';AUD=ROOT/'audit/update26-command'
ID='expanse26_opa_command'
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def scale():
    a=read(BASE/'entities/expanse21_opa_command.unit')['spatial']['box']['extents'][2]
    b=read(BASE/'entities/expanse12_scirocco.unit')['spatial']['box']['extents'][2]
    return b/a

def unpack(path,scalar=1.):
    info=read_mesh(path);b=path.read_bytes();count=struct.unpack_from('<Q',b,53)[0];off=61;rows=[]
    for _ in range(count):
        row=struct.unpack_from('<12f?',b,off);assert not row[-1], 'Skinned input needs explicit bone handling';rows.append(row[:-1]);off+=49
    count=struct.unpack_from('<Q',b,off)[0];ii=np.frombuffer(b,dtype='<u4',count=count,offset=off+8);a=np.array(rows);parts=[]
    for j,p in enumerate(info['primitives']):
        ids=ii[p['vertex_index_start']:p['vertex_index_start']+p['vertex_index_count']];unique,inverse=np.unique(ids,return_inverse=True);q=a[unique]
        parts.append({'v':q[:,:3]*scalar,'n':q[:,3:6].copy(),'t':q[:,6:10].copy(),'uv':q[:,10:12].copy(),'i':inverse.reshape(-1,3),'material':f'material_{j:02d}','old_material':info['materials'][p['material_index']]})
    points=[{'name':p['name'],'translation':(np.array(p['position'])*scalar).tolist(),'rotation':Rotation.from_matrix(np.array(p['rotation']).reshape(3,3).T).as_quat().tolist()}for p in info['meshpoints']]
    return parts,points,info

def compile_one(old,new,s):
    parts,points,source=unpack(BASE/'meshes'/(old+'.mesh'),s)
    c.OUT=OUT;c.savegltf(new,parts,points)
    compiler.NAME=new;compiler.OUT=OUT;compiler.BUILD=BUILD
    compiler.compile('json')
    m=read(BUILD/'compiler-json'/(new+'.mesh_json'));g=Gltf(OUT/(new+'.gltf'));buf=bytearray(g.buffers[0]);v=np.array([x['p']for x in m['non_skinned_vertices']]);n=np.array([x['n']for x in m['non_skinned_vertices']]);ids=np.array(m['vertex_indices']);flips=0
    for p in m['primitives']:
        mat=m['materials'][p['material_index']];pr=next(x for x in g.g['meshes'][0]['primitives']if mat.endswith('_'+g.g['materials'][x['material']]['name']))
        ii=ids[p['vertex_index_start']:p['vertex_index_start']+p['vertex_index_count']].reshape(-1,3);cross=np.cross(v[ii[:,1]]-v[ii[:,0]],v[ii[:,2]]-v[ii[:,0]]);flip=(cross*n[ii].mean(1)).sum(1)<0
        ac=g.g['accessors'][pr['indices']];bv=g.g['bufferViews'][ac['bufferView']];a=np.ndarray((ac['count']//3,3),dtype='<u4',buffer=buf,offset=bv.get('byteOffset',0)+ac.get('byteOffset',0));a[flip]=a[flip][:,[0,2,1]];flips+=int(flip.sum())
    if flips:(OUT/(new+'.bin')).write_bytes(buf);compiler.compile('json','-winding')
    compiler.compile('binary');bp=BUILD/'compiler-binary'/(new+'.mesh');original=bp.read_bytes();b=bytearray(original);count=struct.unpack_from('<Q',b,53)[0];off=61;rows=[];offsets=[]
    for _ in range(count):
        vals=struct.unpack_from('<12f?',b,off);rows.append(vals[:-1]);offsets.append(off+24);off+=49+(8 if vals[-1]else 0)
    a=np.array(rows);lookup=np.concatenate([np.column_stack([p['v'],p['n'],p['uv']])for p in parts]);ts=np.concatenate([p['t']for p in parts]);dist,match=cKDTree(lookup).query(np.column_stack([a[:,:6],a[:,10:12]]));assert dist.max()<5e-4,dist.max()
    t=ts[match].copy();n=a[:,3:6];t[:,:3]-=n*(t[:,:3]*n).sum(1)[:,None];norm=np.linalg.norm(t[:,:3],axis=1);assert norm.min()>1e-8;t[:,:3]/=norm[:,None];allowed=np.zeros(len(b),bool)
    for j,pos in enumerate(offsets):struct.pack_into('<4f',b,pos,*t[j]);allowed[pos:pos+16]=True
    assert np.all((np.frombuffer(original,np.uint8)==np.frombuffer(b,np.uint8))|allowed)
    info=read_mesh(bp);assert b[info['parsed_prefix_bytes']:]==original[info['parsed_prefix_bytes']:]
    m=read(BUILD/'compiler-json'/(new+'.mesh_json'));ii=np.array(m['vertex_indices']).reshape(-1,3);q=np.cross(a[ii[:,1],:3]-a[ii[:,0],:3],a[ii[:,2],:3]-a[ii[:,0],:3]);assert ((q*n[ii].mean(1)).sum(1)<-1e-5).sum()==0
    assert info['triangles']==source['triangles']
    assert len(info['meshpoints'])==len(points)
    for actual,expected in zip(info['meshpoints'],points):
        assert actual['name']==expected['name'];assert np.allclose(actual['position'],expected['translation'],atol=4e-4)
        assert np.allclose(np.array(actual['rotation']).reshape(3,3),Rotation.from_quat(expected['rotation']).as_matrix().T,atol=2e-5)
    (GAME/'meshes'/(new+'.mesh')).write_bytes(b)
    dependencies={str(BASE/'meshes'/(old+'.mesh')):sha(BASE/'meshes'/(old+'.mesh'))}
    for p in parts:
        mat=next(x for x in m['materials']if x.endswith('_'+p['material']));src=BASE/'mesh_materials'/(p['old_material']+'.mesh_material');d=read(src);write(GAME/'mesh_materials'/(mat+'.mesh_material'),d);dependencies[str(src)]=sha(src)
        for k,v in d.items():
            if k.endswith('_texture'):
                tex=BASE/'textures'/(v+'.dds');assert tex.is_file();dependencies[str(tex)]=sha(tex)
    return {'old':old,'new':new,'triangles':source['triangles'],'meshpoints':points,'source_attribute_max_error':float(dist.max()),'winding_flips':flips,'sources_sha256':dependencies,'checks':{'triangles_retained':True,'meshpoint_positions_rotations_match':True,'official_facing_grid_rebuilt':True,'tangent_only_postcompile_patch':True,'texture_aliases_resolve':True}},parts

def preview(parts,report):
    from PIL import Image,ImageDraw
    from polish_ui import render
    textures={}
    def model(ps):
        result=[]
        for p in ps:
            mat=read(BASE/'mesh_materials'/(p['old_material']+'.mesh_material'));key=mat['base_color_texture']
            if key not in textures:textures[key]=np.array(Image.open(BASE/'textures'/(key+'.dds')).convert('RGBA').resize((512,512)))
            tex=textures[key]
            result.append((p['v'][p['i']],p['uv'][p['i']],tex,[1,1,1,1],'OPAQUE'))
        return result
    # Common scene coordinates provide a true scale comparison, no per-ship fit.
    scene=[]
    for label,old,s,offset in [('Europa', 'expanse19_europa_bane_hull',1.,-160.),('Command','expanse19_europa_bane_hull',scale(),0.),('Scirocco','expanse12_scirocco_hull',1.,190.)]:
        ps,_,_=unpack(BASE/'meshes'/(old+'.mesh'),s)
        for p in ps:p['v'][:,0]+=offset
        scene+=model(ps)
    # Looking at dorsal X/Z plane: screen horizontal X, vertical Z.
    basis=np.array([[1,0,0],[0,0,1],[0,-1,0.]])
    im=render(scene,(1200,1000),basis=basis)
    draw=ImageDraw.Draw(im)
    for x,label in [(130,'Europa: 335.34 units'),(450,'OPA command: 456.52 units'),(830,'Scirocco: 456.52 units')]:draw.text((x,975),label,fill=(255,255,255,255))
    im.save(BUILD/'command-scale-comparison.png')
    assembled=list(parts);unit=read(BASE/'entities/expanse21_opa_command.unit');s=scale()
    for weapon in unit['weapons']['weapons'][:6]:
        up=np.array(weapon['up']);fw=np.array(weapon['forward']);basis=np.column_stack([np.cross(up,fw),up,fw]);position=np.array(weapon['weapon_position'])*s
        turret=read(BASE/'entities'/(weapon['weapon']+'.weapon'))['turret']
        for donor,offset in [('expanse19_europa_pdc_base',np.zeros(3)),('expanse19_europa_pdc_barrel',np.array(turret['barrel_position'])*s)]:
            ps,_,_=unpack(BASE/'meshes'/(donor+'.mesh'),s)
            for p in ps:p['v']=(p['v']+offset)@basis.T+position
            assembled+=ps
    im=render(model(assembled),(1200,900),basis=np.array([[.8,0,-.6],[-.3,.866,-.4],[.5196,.5,.6928]]));im.save(BUILD/'command-oblique.png')
    report['previews']=[str(BUILD/'command-scale-comparison.png'),str(BUILD/'command-oblique.png')]

def main():
    for p in [OUT,AUD,GAME/'meshes',GAME/'mesh_materials',GAME/'effects']:p.mkdir(parents=True,exist_ok=True)
    s=scale();results=[];hull=None
    for old,new in [('expanse19_europa_bane_hull',ID+'_hull'),('expanse19_europa_pdc_base',ID+'_pdc_base'),('expanse19_europa_pdc_barrel',ID+'_pdc_barrel')]:
        r,parts=compile_one(old,new,s);results.append(r)
        if hull is None:hull=parts
    fx_sources={}
    for suffix in ['idle_plume','phase_plume']:
        src=BASE/'effects'/('expanse19_europa_bane_'+suffix+'.particle_effect');original=read(src);effect=scale_effect(original,s,s,blue=False);check_structure(effect,original);write(GAME/'effects'/(ID+'_'+suffix+'.particle_effect'),effect);fx_sources[str(src)]=sha(src)
    report={'status':'PASS OFFLINE ART COMPILATION; NOT INSTALLED OR RUNTIME TESTED','base':str(BASE),'output_game':str(GAME),'scale':s,'target_length':read(BASE/'entities/expanse12_scirocco.unit')['spatial']['box']['extents'][2]*2,'meshes':results,'effect_sources_sha256':fx_sources,'tool_dependencies_sha256':{str(p):sha(p)for p in [compiler.SDK/'MeshBuilder/bin/MeshBuilder.exe',ROOT/'tools/update24_behemoth_compile.py',MAIN/'tools/update12_scirocco_common.py',MAIN/'tools/common.py',MAIN/'tools/flight03_effects.py']},'limitations':['Uniform derivative preserves the accepted shape and full 100867 hull triangles; no new sculpted detail.','Preview renderer is an offline material and scale check, not engine culling or aiming evidence.']}
    report['files']={str(p.relative_to(GAME)):sha(p)for p in sorted(GAME.rglob('*'))if p.is_file()};write(AUD/'art-contract.json',report)
    preview(hull,report);write(AUD/'art-contract.json',report);print(json.dumps({'scale':s,'meshes':[(r['new'],r['triangles'])for r in results],'files':len(report['files'])}))
if __name__=='__main__':main()
