"""Compile the private Behemoth hull using pinned MeshBuilder and accepted PDCs.

Tangent-only repair follows the accepted fleet pipeline, retaining the official
triangle-facing grid. No installation, manifests or shared gameplay mutations.
"""
from pathlib import Path
import copy, hashlib, json, os, struct, subprocess, sys
import numpy as np
from scipy.spatial import cKDTree
from scipy.spatial.transform import Rotation
import jsonschema
ROOT=Path(__file__).resolve().parents[1]
MAIN=Path('/run/media/haker/NVME 2/expanse-mod')
sys.path.insert(0,str(MAIN/'tools'))
from common import Gltf, read, read_mesh, write
from flight03_effects import scale_effect, check_structure
from build_update12 import phase_effect
BASE=MAIN/'build/experiments/expanse_update20'
BUILD=ROOT/'build/update24-behemoth';OUT=BUILD/'source';GAME=BUILD/'game';AUD=ROOT/'docs/audit/update24-behemoth'
SDK=Path('/run/media/haker/NVME 2/SteamLibrary/steamapps/common/Sins of a Solar Empire II - Mod Tools')
INSTALLED=SDK.parent/'Sins2'
WINE=Path('/home/haker/.var/app/com.valvesoftware.Steam/.local/share/Steam/steamapps/common/Proton 10.0/files/bin/wine64')
PREFIX=Path('/run/media/haker/NVME 2/expanse-workers/tachi-one-pdc/build/polish-b/proton-prefix')
NAME='expanse24_behemoth_hull'
ENV=dict(os.environ,WINEPREFIX=str(PREFIX),OMP_NUM_THREADS='4',MANGOHUD='0',WINEDEBUG='-all',DISPLAY='',WINEDLLOVERRIDES='mscoree,mshtml=')
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def compile(fmt,suffix=''):
    dest=BUILD/('compiler-'+fmt);dest.mkdir(parents=True,exist_ok=True)
    with (BUILD/(NAME+suffix+'-'+fmt+'.log')).open('w')as log:
        subprocess.run([str(WINE),str(SDK/'MeshBuilder/bin/MeshBuilder.exe'),'--input_path=Z:'+str(OUT/(NAME+'.gltf')),'--output_folder_path=Z:'+str(dest),'--mesh_output_format='+fmt,'--fill_triangle_facing_grid'],env=ENV,stdout=log,stderr=subprocess.STDOUT,check=True,timeout=300)

def main():
    report=read(AUD/'integration-spec.json')
    assert report['source_triangles_retained']==24046
    for d in ['meshes','mesh_materials','textures','effects']:(GAME/d).mkdir(parents=True,exist_ok=True)
    z=np.load(OUT/'reference.npz');parts=[]
    for j in range(len([k for k in z if k.endswith('_v')])):
        p={k:z[str(j)+'_'+k].copy()for k in ['v','n','t','uv','i']};p['material']=str(z[str(j)+'_material']);parts.append(p)
    compile('json');m=read(BUILD/'compiler-json'/(NAME+'.mesh_json'));g=Gltf(OUT/(NAME+'.gltf'));buf=bytearray(g.buffers[0])
    v=np.array([q['p']for q in m['non_skinned_vertices']]);n=np.array([q['n']for q in m['non_skinned_vertices']]);indices=np.array(m['vertex_indices']);flips=0
    for primitive in m['primitives']:
        mat=m['materials'][primitive['material_index']];pr=next(p for p in g.g['meshes'][0]['primitives']if mat.endswith('_'+g.g['materials'][p['material']]['name']))
        ii=indices[primitive['vertex_index_start']:primitive['vertex_index_start']+primitive['vertex_index_count']].reshape(-1,3)
        cross=np.cross(v[ii[:,1]]-v[ii[:,0]],v[ii[:,2]]-v[ii[:,0]]);flip=(cross*n[ii].mean(1)).sum(1)<0
        ac=g.g['accessors'][pr['indices']];bv=g.g['bufferViews'][ac['bufferView']];a=np.ndarray((ac['count']//3,3),dtype='<u4',buffer=buf,offset=bv.get('byteOffset',0)+ac.get('byteOffset',0));assert len(a)==len(ii)
        a[flip]=a[flip][:,[0,2,1]];flips+=int(flip.sum())
    if flips:(OUT/(NAME+'.bin')).write_bytes(buf);compile('json','-winding')
    compile('binary');bp=BUILD/'compiler-binary'/(NAME+'.mesh');original=bp.read_bytes();b=bytearray(original);m=read(BUILD/'compiler-json'/(NAME+'.mesh_json'))
    count=struct.unpack_from('<Q',b,53)[0];off=61;rows=[];offsets=[]
    for _ in range(count):
        vals=struct.unpack_from('<12f?',b,off);rows.append(vals[:-1]);offsets.append(off+24);off+=49+(8 if vals[-1]else 0)
    binary=np.array(rows);features=np.column_stack([binary[:,:6],binary[:,10:12]])
    lookup=np.concatenate([np.column_stack([p['v'],p['n'],p['uv']])for p in parts]);tangents=np.concatenate([p['t']for p in parts]);dist,match=cKDTree(lookup).query(features);assert dist.max()<5e-4,dist.max()
    tang=tangents[match].copy();n=binary[:,3:6];tang[:,:3]-=n*(tang[:,:3]*n).sum(1)[:,None];tn=np.linalg.norm(tang[:,:3],axis=1);assert tn.min()>1e-8;tang[:,:3]/=tn[:,None]
    allowed=np.zeros(len(b),bool)
    for j,pos in enumerate(offsets):struct.pack_into('<4f',b,pos,*tang[j]);allowed[pos:pos+16]=True
    assert np.all((np.frombuffer(original,np.uint8)==np.frombuffer(b,np.uint8))|allowed)
    info=read_mesh(bp);assert b[info['parsed_prefix_bytes']:]==original[info['parsed_prefix_bytes']:]
    ii=np.array(m['vertex_indices']).reshape(-1,3);v=binary[:,:3];cross=np.cross(v[ii[:,1]]-v[ii[:,0]],v[ii[:,2]]-v[ii[:,0]]);opposed=int(((cross*n[ii].mean(1)).sum(1)<-1e-5).sum());assert opposed==0
    assert len(ii)==report['counts']['hull']
    # Sample the authored outward firing cone against the original hull. Zero
    # pitch grazed raised drum bands, so mounts stop 15 degrees above the tangent.
    tri=np.concatenate([p['v'][p['i']]for p in parts if p['material']!='fittings'])
    e1=tri[:,1]-tri[:,0];e2=tri[:,2]-tri[:,0];ray_count=0
    for rig in report['rigs']:
        basis=np.array(rig['basis']);origin=np.array(rig['position'])+np.array(rig['up'])*5
        for yaw in np.linspace(rig['yaw_arc']['min_angle'],rig['yaw_arc']['max_angle'],13):
            for pitch in np.linspace(rig['pitch_arc']['min_angle'],rig['pitch_arc']['max_angle'],8):
                yy,pp=np.radians([yaw,pitch]);di=basis@np.array([np.sin(yy)*np.cos(pp),-np.sin(pp),np.cos(yy)*np.cos(pp)])
                hh=np.cross(np.broadcast_to(di,e2.shape),e2);det=(e1*hh).sum(1);inv=np.divide(1,det,out=np.zeros_like(det),where=abs(det)>1e-8);ss=origin-tri[:,0];uu=(ss*hh).sum(1)*inv;qq=np.cross(ss,e1);vv=(di*qq).sum(1)*inv;dd=(e2*qq).sum(1)*inv
                assert not ((abs(det)>1e-8)&(uu>=0)&(vv>=0)&(uu+vv<=1)&(dd>0)).any();ray_count+=1
    for actual,expected in zip(info['meshpoints'],report['meshpoints'],strict=True):
        assert actual['name']==expected['name']and np.allclose(actual['position'],expected['translation'],atol=3e-4)
        assert np.allclose(np.array(actual['rotation']).reshape(3,3),Rotation.from_quat(expected.get('rotation',[0,0,0,1])).as_matrix().T,atol=2e-5)
    (GAME/'meshes'/(NAME+'.mesh')).write_bytes(b)
    # Exact native-compiled donor gun files. Their texture identities are retained.
    sources={};donormats=set()
    for new,old in [('expanse24_behemoth_pdc_base','expanse10_donnager_pdc_base'),('expanse24_behemoth_pdc_barrel','expanse10_donnager_pdc_barrel')]:
        p=BASE/'meshes'/(old+'.mesh');(GAME/'meshes'/(new+'.mesh')).write_bytes(p.read_bytes());sources[str(p)]=sha(p);donormats.update(read_mesh(p)['materials'])
    textures=set()
    for mat in donormats:
        p=BASE/'mesh_materials'/(mat+'.mesh_material');(GAME/'mesh_materials'/p.name).write_bytes(p.read_bytes());sources[str(p)]=sha(p)
        for k,val in read(p).items():
            if k.endswith('_texture'):textures.add(val)
    for tex in textures:
        p=BASE/'textures'/(tex+'.dds');(GAME/'textures'/p.name).write_bytes(p.read_bytes());sources[str(p)]=sha(p)
    # Full mip-chain BC7 color/ORM/mask and signed BC5 normals; no alpha blending.
    for mat in ['shell','ends','fittings']:
        for channel in ['clr','nrm','orm','msk']:
            p=OUT/'textures'/(mat+'_'+channel+'.png');dest=GAME/'textures';out=dest/('expanse24_behemoth_'+p.stem+'.dds');stamp=BUILD/(out.stem+'.source-sha256')
            if not out.exists()or not stamp.exists()or stamp.read_text()!=sha(p):
                cmd=[str(WINE),str(MAIN/'.tools/texconv.exe'),'-f','BC5_SNORM'if channel=='nrm'else'BC7_UNORM','-y','-m','0','-nogpu','--single-proc','-o','Z:'+str(dest)]+(['--x2-bias']if channel=='nrm'else['-bc','q'])+['Z:'+str(p)]
                with (BUILD/'texture-conversion.log').open('a')as log:subprocess.run(cmd,env=ENV,stdout=log,stderr=subprocess.STDOUT,check=True,timeout=180)
                (dest/(p.stem+'.dds')).rename(out);stamp.write_text(sha(p))
        key=next(name for name in m['materials']if name.endswith('_'+mat))
        write(GAME/'mesh_materials'/(key+'.mesh_material'),{'version':1,'base_color_texture':f'expanse24_behemoth_{mat}_clr','normal_texture':f'expanse24_behemoth_{mat}_nrm','occlusion_roughness_metallic_texture':f'expanse24_behemoth_{mat}_orm','mask_texture':f'expanse24_behemoth_{mat}_msk','emissive_factor':.65 if mat=='shell'else 0.})
    # Verified native blue exhaust template and existing eight-nozzle phase helper.
    effect_source=INSTALLED/'effects/exhaust_tech_medium_01.particle_effect';originalfx=read(effect_source)
    idle=scale_effect(originalfx,7.5,12.,blue=True);check_structure(idle,originalfx)
    phase=phase_effect(report['equipment']['exhausts'],7.5,36.)
    write(GAME/'effects/expanse24_behemoth_idle_plume.particle_effect',idle);write(GAME/'effects/expanse24_behemoth_phase_plume.particle_effect',phase)
    for fx in [idle,phase]:
        for key in ['nodes','emitters','modifiers']:assert len({q['id']for q in fx[key]})==len(fx[key])
        for att in fx['emitter_to_node_attachments']:assert att['attacher_id']in {x['id']for x in fx['emitters']}and att['attachee_id']in {x['id']for x in fx['nodes']}
        for att in fx['modifier_to_emitter_attachments']:assert att['attacher_id']in {x['id']for x in fx['modifiers']}and att['attachee_id']in {x['id']for x in fx['emitters']}
    # SDK does not ship a particle-effect schema; preserve its known field shapes.
    # No mesh-material schema is shipped either. Match the accepted six-key shape.
    material_keys={'version','base_color_texture','normal_texture','occlusion_roughness_metallic_texture','mask_texture','emissive_factor'}
    for p in (GAME/'mesh_materials').glob('*.mesh_material'):
        assert set(read(p))==material_keys
        for k,val in read(p).items():
            if k.endswith('_texture'):assert (GAME/'textures'/(val+'.dds')).is_file()
    sources[str(effect_source)]=sha(effect_source)
    for p in [SDK/'MeshBuilder/bin/MeshBuilder.exe',MAIN/'tools/flight03_effects.py',MAIN/'tools/build_update12.py',MAIN/'tools/build_combat04.py',MAIN/'tools/update12_scirocco_common.py',MAIN/'tools/common.py']:sources[str(p)]=sha(p)
    report['status']='PASS OFFLINE ART COMPILATION; NOT INSTALLED OR RUNTIME TESTED'
    report['checks'].update(official_meshbuilder=True,opposed_winding_triangles=opposed,source_attribute_max_error=float(dist.max()),official_facing_grid_preserved=True,tangent_bytes_only_repaired=True,meshpoint_positions_and_rotations_match=True,donor_mesh_bytes_unchanged=True,material_observed_field_shapes_pass=True,all_material_textures_resolve=True,particle_ids_and_links_valid=True)
    report['compiled_materials']=m['materials'];report['initial_winding_flips']=flips;report['source_dependencies_sha256']=sources;report['files']={str(p.relative_to(GAME)):sha(p)for p in sorted(GAME.rglob('*'))if p.is_file()}
    report['checks']['outward_cone_rays_clear_of_source_hull']=ray_count
    report['limitations'].append('Firing-cone sampling uses the established negative-pitch convention and a raised mount origin; it is not an engine aiming or continuous swept-muzzle proof.')
    report['plumes']={'idle':'expanse24_behemoth_idle_plume','phase':'expanse24_behemoth_phase_plume','native_template':str(effect_source),'width_scalar':7.5,'idle_length_scalar':12.,'phase_length_scalar':36.,'note':'Blue native template; idle bound per exhaust meshpoint, phase effect contains all eight measured nozzles. Scale is a visual adaptation, not a propulsion-stat change.'}
    write(AUD/'integration-spec.json',report);print(json.dumps({'status':report['status'],'checks':report['checks'],'files':len(report['files'])}))

if __name__=='__main__':main()
