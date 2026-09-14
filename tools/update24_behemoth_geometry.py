"""Private Behemoth art prototype; original STL and release package are read-only.

Run with the project's dependency Python. No gameplay definitions or installation.
Preserves every source face; UVs/materials and eight defensive mounts are authored.
"""
from pathlib import Path
import copy, hashlib, json, math, sys, zipfile
import numpy as np
from PIL import Image, ImageDraw, ImageFont
from scipy.spatial.transform import Rotation

ROOT = Path(__file__).resolve().parents[1]
MAIN = Path('/run/media/haker/NVME 2/expanse-mod')
sys.path.insert(0, str(MAIN / 'tools'))
from common import Gltf, read, write
import update12_scirocco_common as c
from polish_ui import render

BUILD = ROOT / 'build/update24-behemoth'
OUT = BUILD / 'source'
AUD = ROOT / 'docs/audit/update24-behemoth'
ZIP = Path('/home/haker/Downloads/nauvoobehemothmedina-station-the-expanse-model_files.zip')
NAME = 'expanse24_behemoth_hull'
UNITS_PER_METRE = 104.987 / 46.
LENGTH_METRES = 2000.
PALETTE = {'shell': (68, 78, 81), 'ends': (95, 92, 78), 'fittings': (49, 57, 62)}


def sha(p):
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()


def materials():
    """Cylindrical mechanical panel atlas, not projected photography.

    B channel is emissive mask, R team color and G bloom remain zero, per the
    existing Sunflare/Truman conversion; every color texture is fully opaque.
    """
    dest = OUT / 'textures'; dest.mkdir(parents=True, exist_ok=True)
    rng = np.random.default_rng(24046)
    for mat, col in PALETTE.items():
        w, h = (2048, 1024) if mat == 'shell' else (512, 512)
        noise = rng.normal(0, 1.5, (h, w, 1))
        rgb = np.clip(np.array(col)[None, None, :] + noise, 0, 255).astype('uint8')
        im = Image.fromarray(rgb).convert('RGBA'); draw = ImageDraw.Draw(im)
        mask = Image.new('RGBA', (w, h), (0, 0, 0, 0)); md = ImageDraw.Draw(mask)
        step_x, step_y = (64, 32) if mat == 'shell' else (64, 64)
        for y in range(0, h, step_y):
            for x in range(0, w, step_x):
                delta = int(rng.integers(-9, 10)); cc = tuple(max(0, min(255, v + delta)) for v in col)
                draw.rectangle((x+1, y+1, x+step_x-2, y+step_y-2), fill=cc)
                draw.line((x+3,y+3,x+step_x-4,y+3), fill=tuple(min(255,v+15) for v in cc), width=1)
                draw.line((x+3,y+4,x+3,y+step_y-4), fill=tuple(min(255,v+9) for v in cc), width=1)
                if rng.random() < .1: draw.rectangle((x+7,y+10,x+22,y+13), fill=(134,132,109))
        if mat == 'shell':
            # A weathered civilian industrial hull; narrow ochre replacement bands.
            for y in [int(h*v) for v in [.252,.306,.528,.718,.79]]:
                draw.rectangle((0,y,w,y+9), fill=(137,114,65))
                draw.line((0,y+11,w,y+11), fill=(24,31,36), width=2)
                for x in range(8,w,64):
                    draw.rectangle((x,y+14,x+7,y+16), fill=(159,203,209))
                    md.rectangle((x,y+14,x+7,y+16), fill=(0,0,160,0))
            font = ImageFont.truetype('/usr/share/fonts/TTF/DejaVuSans.ttf', 27)
            small = ImageFont.truetype('/usr/share/fonts/TTF/DejaVuSans.ttf', 13)
            for x in [200,1224]:
                draw.rectangle((x-12,614,x+320,671),fill=(45,53,55))
                draw.text((x,620),'O.P.A.  BEHEMOTH',font=font,fill=(190,183,149))
                draw.text((x,653),'ENGINEERING / HABITAT / TRANSFER',font=small,fill=(151,159,147))
        if mat == 'shell':
            # Two-period atlas keeps seam-crossing cylindrical UVs inside [0,1].
            doubled=Image.new('RGBA',(w*2,h));doubled.paste(im,(0,0));doubled.paste(im,(w,0));im=doubled
            doubled=Image.new('RGBA',(w*2,h));doubled.paste(mask,(0,0));doubled.paste(mask,(w,0));mask=doubled;w*=2
        im.save(dest / (mat+'_clr.png')); mask.save(dest / (mat+'_msk.png'))
        Image.new('RGBA',(w,h),(255,175,130,255)).save(dest/(mat+'_orm.png'))
        Image.new('RGBA',(w,h),(128,128,255,255)).save(dest/(mat+'_nrm.png'))


def cylinder(parts, center, axis, radius, height, segments=16):
    axis=np.array(axis,float); axis/=np.linalg.norm(axis)
    ax=np.eye(3)[np.argmin(abs(axis))]; ax-=axis*np.dot(ax,axis); ax/=np.linalg.norm(ax); by=np.cross(axis,ax)
    ring=np.array([ax*math.cos(a)+by*math.sin(a) for a in np.linspace(0,2*math.pi,segments,endpoint=False)])*radius
    bottom=np.array(center); top=bottom+axis*height; tris=[]
    for j in range(segments):
        k=(j+1)%segments
        tris += [[bottom+ring[j],bottom+ring[k],top+ring[k]], [bottom+ring[j],top+ring[k],top+ring[j]], [top,top+ring[j],top+ring[k]], [bottom,bottom+ring[k],bottom+ring[j]]]
    parts.append(c.frames(tris,'fittings'))


def main():
    for p in [BUILD,OUT,AUD]:p.mkdir(parents=True,exist_ok=True)
    materials()
    data=zipfile.ZipFile(ZIP).read('part31behemoth.stl')
    raw=np.frombuffer(data,offset=84,dtype=[('n','<f4',(3,)),('v','<f4',(3,3)),('attr','<u2')])
    source=raw['v'].astype(float); lo=source.min((0,1)); hi=source.max((0,1)); center=(lo+hi)/2
    scale=LENGTH_METRES*UNITS_PER_METRE/(hi[2]-lo[2]); tri=(source-center)*scale
    normal=np.cross(tri[:,1]-tri[:,0],tri[:,2]-tri[:,0]); norm=np.linalg.norm(normal,axis=1)
    assert len(tri)==24046 and norm.min()>0
    normal/=norm[:,None]
    # Original model faces define the visible exterior. Repair only normal-facing
    # consistency against the STL's supplied normals; no faces removed or invented.
    flip=(normal*raw['n']).sum(1)<0; tri[flip]=tri[flip][:,[0,2,1]]; normal[flip]*=-1
    cap=abs(normal[:,2])>.65
    parts=[]
    for mat,mask in [('shell',~cap),('ends',cap)]:
        p=c.frames(tri[mask],mat)
        if mat=='shell':
            pts=p['v']; ang=np.arctan2(pts[:,1],pts[:,0])/(2*np.pi)+.5
            a=ang.reshape(-1,3); seam=np.ptp(a,axis=1)>.5; a[seam]=np.where(a[seam]<.5,a[seam]+1,a[seam])
            uv=np.column_stack([a.ravel()/2,(pts[:,2]/scale+center[2])/hi[2]])
            tangent=np.column_stack([-pts[:,1],pts[:,0],np.zeros(len(pts))]); n=p['n']
            tangent-=n*(tangent*n).sum(1)[:,None]; tangent/=np.maximum(np.linalg.norm(tangent,axis=1)[:,None],1e-12)
            bad=np.linalg.norm(tangent,axis=1)<.5; tangent[bad]=p['t'][bad,:3]
            p['uv']=uv; p['t']=np.column_stack([tangent,np.ones(len(pts))])
        parts.append(p)
    source_parts=[copy.deepcopy(p) for p in parts]
    def world(x):return (np.array(x,float)-center)*scale
    def ray(origin,direction):
        e1=tri[:,1]-tri[:,0];e2=tri[:,2]-tri[:,0];h=np.cross(np.broadcast_to(direction,e2.shape),e2);det=(e1*h).sum(1);ok=abs(det)>1e-10;inv=np.zeros(len(det));inv[ok]=1/det[ok];s=origin-tri[:,0];u=(s*h).sum(1)*inv;q=np.cross(s,e1);v=(direction*q).sum(1)*inv;t=(e2*q).sum(1)*inv;good=ok&(u>=-1e-7)&(v>=-1e-7)&(u+v<=1.0000001)&(t>0)
        assert good.any(),origin
        return origin+direction*t[good].min()
    source_rig=read('/run/media/haker/NVME 2/expanse-workers/tachi-one-pdc/audit/update11-b/mount-metadata.json')['rigs'][0]['turret_override']
    turret=copy.deepcopy(source_rig);turret.update(biaxial_base_mesh='expanse24_behemoth_pdc_base',biaxial_barrel_mesh='expanse24_behemoth_pdc_barrel')
    points=[{'name':'center','translation':[0,0,0]},{'name':'above','translation':[0,float(hi[0]*scale+40),0]},{'name':'aura','translation':[0,float(-hi[0]*scale-40),0]}];rigs=[]
    for z in [57.,164.]:
        for theta in [0.,np.pi/2,np.pi,3*np.pi/2]:
            outward=np.array([math.cos(theta),math.sin(theta),0.]); hit=ray(world([0,0,z])+outward*1200,-outward)
            pos=hit+outward*3.;j=len(rigs);basis=np.column_stack([np.cross(outward,[0,0,1]),outward,[0,0,1]])
            cylinder(parts,hit-outward, outward, 5., 4.)
            pt={'name':f'child.expanse24_behemoth_pdc_{j}','translation':pos.tolist(),'rotation':Rotation.from_matrix(basis).as_quat().tolist()};points.append(pt)
            rigs.append({'kind':'pdc','mesh_point':pt['name'],'position':pos.tolist(),'up':outward.tolist(),'forward':[0,0,1],'basis':basis.tolist(),'yaw_arc':{'min_angle':-85.,'max_angle':85.},'pitch_arc':{'min_angle':-80.,'max_angle':-15.},'turret_override':copy.deepcopy(turret),'surface_contact':hit.tolist(),'placement':'Four cardinal mounts on each fixed fore/aft external collar; proposed retrofit, not a screen-count claim.'})
    # Measured centers of all eight authored nozzle mouth rings at STL z=0.
    v=np.unique(source.reshape(-1,3),axis=0);mouth=v[v[:,2]<1e-4];groups=np.round(np.arctan2(mouth[:,1],mouth[:,0])/(np.pi/4)).astype(int)%8;exhausts=[]
    for j in range(8):
        sp=mouth[groups==j].mean(0);pos=world(sp);pos[2]-=.5
        exhausts.append({'position':pos.tolist(),'forward':[0,0,-1],'up':[0,1,0],'source_position':sp.tolist(),'aperture_radius_game_units':3.81*scale})
        points.append({'name':f'exhaust.{j}','translation':pos.tolist(),'rotation':[0,1,0,0]})
    torps=[]
    for j,sign in enumerate([-1,1]):
        pos=world([sign*34,0,170.5]);cylinder(parts,pos,[0,0,1],3.2,4.);muzzle=pos+np.array([0,0,4.2])
        point={'name':f'weapon.torpedo.{j}','translation':muzzle.tolist()};points.append(point);torps.append({'mesh_point':point['name'],'position':muzzle.tolist(),'forward':[0,0,1],'count':1,'cosmetic_port_only':True})
    # Merge materials once: compiler emits one primitive per unique material.
    merged={}
    for p in parts:
        mat=p['material']
        if mat not in merged:merged[mat]=copy.deepcopy(p)
        else:
            q=merged[mat];offset=len(q['v']);q['i']=np.concatenate([q['i'],p['i']+offset])
            for k in ['v','n','t','uv']:q[k]=np.concatenate([q[k],p[k]])
    parts=list(merged.values());c.OUT=OUT;c.savegltf(NAME,parts,points);c.savegltf('expanse24_behemoth_editable',parts,points,compiler=False)
    editable=read(OUT/'expanse24_behemoth_editable.gltf');editable['images']=[];editable['textures']=[]
    for mat in editable['materials']:
        editable['images'].append({'uri':'textures/'+mat['name']+'_clr.png'});editable['textures'].append({'source':len(editable['images'])-1});mat['pbrMetallicRoughness']={'baseColorTexture':{'index':len(editable['textures'])-1},'baseColorFactor':[1,1,1,1],'metallicFactor':.5,'roughnessFactor':.7}
    write(OUT/'expanse24_behemoth_editable.gltf',editable)
    np.savez_compressed(OUT/'reference.npz',**{str(j)+'_'+k:p[k] for j,p in enumerate(parts) for k in ['v','n','t','uv','i','material']})
    previews=[]
    for p in parts:
        tex=np.array(Image.open(OUT/'textures'/(p['material']+'_clr.png')).convert('RGBA'));previews.append((p['v'][p['i']],p['uv'][p['i']],tex,[1,1,1,1],'OPAQUE'))
    # Preview only: accepted donor meshes remain separate child meshes at runtime.
    donor=Path('/run/media/haker/NVME 2/expanse-workers/tachi-one-pdc/assets/derived/polish-b');donor_vertices=[]
    for r in rigs:
        for kind in ['base','barrel']:
            g=Gltf(donor/f'expanse_polish_pdc_0_{kind}.gltf')
            for prim in g.g['meshes'][0]['primitives']:
                v=g.accessor(prim['attributes']['POSITION']).astype(float);v[:,2]*=-1
                if kind=='barrel':v+=np.array(turret['barrel_position'])
                v=v@np.array(r['basis']).T+np.array(r['position']);idx=g.accessor(prim['indices']).reshape(-1,3);donor_vertices.append(v)
                previews.append((v[idx],np.zeros((len(idx),3,2)),np.full((2,2,4),255,dtype='uint8'),[.2,.23,.25,1],'OPAQUE'))
    basis=np.array([[.8,0,-.6],[.24,.9165,.32],[.55,-.4,.733]])
    render(previews,(1600,950),basis).save(BUILD/'behemoth-oblique.png')
    render(previews,(1600,850),np.array([[0,0,1],[0,1,0],[-1,0,0]])).save(BUILD/'behemoth-side.png')
    render(previews,(1100,1100),np.array([[1,0,0],[0,1,0],[0,0,-1]])).save(BUILD/'behemoth-aft.png')
    vertices=np.concatenate([p['v'] for p in parts]+donor_vertices);lo=vertices.min(0);hi=vertices.max(0);mid=(lo+hi)/2
    report={'status':'GEOMETRY PREPARED; COMPILATION PENDING','output_game':str(BUILD/'game'),'hull_mesh':NAME,'source_zip':str(ZIP),'source_zip_sha256':sha(ZIP),'source_entry':'part31behemoth.stl','source_entry_sha256':hashlib.sha256(data).hexdigest(),'source_triangles':24046,'source_triangles_retained':24046,'source_orientation':'STL +Z is bow/antenna, -Z is aft engine cluster; +Y retained as game up','source_center':center.tolist(),'uniform_scale':scale,'length_metres_design_assumption':LENGTH_METRES,'units_per_metre':UNITS_PER_METRE,'scale_reference':'Tachi 104.987 game units / 46 metres; 2000 m rounded Behemoth lore length, source aspect ratio retained.','counts':{'hull':sum(len(p['i'])for p in parts),'source_hull':24046,'added_fixed_fittings':sum(len(p['i'])for p in parts)-24046,'pdc_mounts':8,'pdc_base':138,'pdc_barrel':539,'assembled':sum(len(p['i'])for p in parts)+8*(138+539)},'ship_spatial':{'box':{'center':mid.tolist(),'extents':((hi-lo)/2).tolist()},'radius':float(np.linalg.norm(vertices-mid,axis=1).max()),'bounds_min':lo.tolist(),'bounds_max':hi.tolist()},'meshpoints':points,'rigs':rigs,'equipment':{'exhausts':exhausts,'torpedo_ports':torps},'material_intent':'Charcoal industrial hull, weathered ochre repair bands, opaque flat-normal materials, subtle cool-white lights; no Martian orange military scheme.','checks':{'all_source_triangles_preserved':True,'source_facing_corrections':int(flip.sum()),'pdc_pedestals_meet_raycast_exterior':True,'nozzle_centres_measured_from_eight_source_mouths':True},'limitations':['Static drum: no spin animation authored.','Source is complete but simplified: no interior, hangar/docking animation, physical opening torpedo doors or launchable boats.','Eight PDCs and two ports are a bounded mod retrofit, not a claim about screen-canonical weapon count.','PDCs retain donor physical scale; small against the 2 km hull by design.','Procedural panel atlases add surface detail but do not fabricate missing source geometry.','Source proportions imply about 781 m maximum width at rounded 2 km length; this is preserved model interpretation, not a canonical width assertion.','No gameplay, fleet supply, price, titan-slot rule or ability semantics changed.','Preview renderer is double-sided and does not validate game culling or shader emission.']}
    write(AUD/'integration-spec.json',report);print(json.dumps({'hull':report['counts'],'spatial':report['ship_spatial']}))


if __name__=='__main__':main()
