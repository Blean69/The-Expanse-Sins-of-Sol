"""Editable material study on the recovered Tycho core, separate from game output.

No original UVs or paint are recoverable from G-code. Surface colors and small
emissive patches here are new artistic additions. No dynamic light objects.
"""
from pathlib import Path
import json
import numpy as np
from scipy.spatial import cKDTree
import update12_scirocco_common as gltf
from polish_ui import render
from build_polish import write
from validate_experiments import sha256

ROOT=Path(__file__).resolve().parents[1]
SRC=ROOT/'assets/derived/tycho18-recovery-solid'
OUT=ROOT/'assets/derived/tycho18-material-study'
AUD=ROOT/'audit/update18-tycho-art'
COLORS=[[.34,.37,.39,1],[.105,.125,.14,1],[.43,.20,.075,1],
        [.68,.65,.52,1],[1.,.64,.24,1],[.30,.72,1.,1]]
NAMES=['industrial_grey','machinery','ochre_panels','dock_markings',
       'warm_habitat_windows','cool_work_lights']

def main():
    OUT.mkdir(parents=True,exist_ok=True)
    triangles=[]
    for name in ['upper','lower']:
        z=np.load(SRC/(name+'-simplified.npz'));triangles.append(z['v'][z['i']])
    tri=np.concatenate(triangles);center=tri.mean(1)
    cross=np.cross(tri[:,1]-tri[:,0],tri[:,2]-tri[:,0])
    lengths=np.linalg.norm(cross,axis=1)
    keep=lengths>1e-8;discarded=int((~keep).sum())
    tri,center,cross,lengths=tri[keep],center[keep],cross[keep],lengths[keep]
    normals=cross/lengths[:,None]
    radial=np.linalg.norm(center[:,[0,2]],axis=1)
    angle=np.mod(np.arctan2(center[:,2],center[:,0]),2*np.pi)
    sector=np.floor(angle/(2*np.pi)*24).astype(int)
    materials=np.zeros(len(tri),int)
    # Coordinate-defined surface zones are repeatable and independent of team color.
    materials[((radial>71)&(radial<81)) | (abs(center[:,1])>43)]=1
    materials[(radial>82)&(sector%6==0)]=2
    materials[(radial<68)&(radial>43)&(sector%6==0)&(abs(center[:,1])>27)]=2
    materials[(radial>84)&(sector%6==1)&(abs(center[:,1])<2)]=3
    groups=[tri[materials==i] for i in range(4)]
    window_rows=[]
    for kind,radius,yrows,count,w,h in [(4,87,[-3,3],96,.58,.18),(5,69,[-14,15],24,.72,.24)]:
        outward=np.sum(normals[:,[0,2]]*center[:,[0,2]],axis=1)/np.maximum(radial,1)
        eligible=np.flatnonzero((outward>.60)&(abs(radial-radius)<5))
        assert len(eligible)>count
        tree=cKDTree(center[eligible]);patches=[]
        for y in yrows:
            for a in np.arange(count)*2*np.pi/count:
                goal=np.array([radius*np.cos(a),y,radius*np.sin(a)])
                _,ix=tree.query(goal);j=eligible[ix]
                n=normals[j];p=center[j]+n*.045
                right=np.cross([0.,1.,0.],n);right/=np.linalg.norm(right)
                up=np.cross(n,right)
                v=np.array([p-right*w-up*h,p+right*w-up*h,p+right*w+up*h,p-right*w+up*h])
                patches.extend([v[[0,1,2]],v[[0,2,3]]])
        groups.append(np.array(patches));window_rows.append({'material':NAMES[kind],'patches':len(patches)//2})
    parts=[];meshes=[]
    for i,t in enumerate(groups):
        part=gltf.frames(t,'expanse18_tycho_'+NAMES[i]);parts.append(part)
        meshes.append((t,part['uv'].reshape(-1,3,2),np.full((1,1,4),255,np.uint8),COLORS[i],'OPAQUE'))
    gltf.OUT=OUT;name='tycho18_reconstructed_core'
    gltf.savegltf(name,parts,compiler=False)
    path=OUT/(name+'.gltf');d=json.loads(path.read_text())
    d['asset']['generator']='Sins of Sol: approximate ewr2san Tycho G-code reconstruction, material study'
    d['asset']['copyright']='ewr2san, CC BY-NC 4.0; new recovery/material derivative by Sins of Sol'
    for i,m in enumerate(d['materials']):
        m.update(alphaMode='OPAQUE',doubleSided=False)
        m['pbrMetallicRoughness']={'baseColorFactor':COLORS[i],'metallicFactor':.45 if i<4 else 0.,'roughnessFactor':.68}
        if i>=4:m['emissiveFactor']=COLORS[i][:3]
    write(path,d)
    for label,view in [('materials',[[.8,0,-.6],[-.3,.866,-.4],[.52,.5,.69]]),('materials-side',np.eye(3))]:
        render(meshes,(1300,1050),np.array(view),fill=.88).save(AUD/(label+'.png'))
    sdk=ROOT.parent/'SteamLibrary/steamapps/common/Sins of a Solar Empire II - Mod Tools'
    write(AUD/'materials.json',{'status':'EDITABLE GLTF MATERIAL STUDY ONLY; NOT IN GAME PACKAGE',
        'triangles':sum(len(t) for t in groups),'removed_degenerate_triangles':discarded,'materials':NAMES,'emissive_patches':window_rows,
        'dynamic_lights':0,'original_textures_recovered':False,'UVs':'New helper planar per-face projections, no original texture atlas; full texture bake pending',
        'game_mask_contract':{'R':'primary team color','G':'secondary team color','B':'emissive strength','A':'emissive hue strength'},
        'mask_contract_source':str(sdk/'README.md'),'mask_contract_source_sha256':sha256(sdk/'README.md'),
        'game_shader_conversion':'NOT RUN: glTF emissiveFactor is editable preview, not a claim of Iron Engine mask export',
        'units':'Source printed millimeters at 25% print scale; gameplay scale not assigned',
        'limitations':['Missing supported accessories and original assembly orientation','Printed strand and infill artifacts, inferred joined core','No functional mounts or ring animation in art study','Game bloom/night-side and team-color tests NOT RUN'],
        'outputs':{str(p.relative_to(ROOT)):sha256(p) for p in sorted(OUT.iterdir()) if p.is_file()}})
    print('Editable Tycho core/materials:',sum(len(t) for t in groups),'triangles',flush=True)

if __name__=='__main__':main()
