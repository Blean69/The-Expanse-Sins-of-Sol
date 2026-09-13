"""Read-only G-code raster recovery experiment. Never sends commands to a printer.

Produces an approximate printed core, not the missing original STL. Only the two
station halves have support_material=0, so supported accessories are excluded.
"""
from pathlib import Path
import sys, re, json, zipfile
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'.tools/tycho18-packages'))
import numpy as np
from PIL import Image, ImageDraw
from scipy import ndimage
from skimage.measure import marching_cubes
from validate_experiments import sha256
from build_polish import write
OUT=ROOT/'assets/derived/tycho18-recovery-solid'
AUD=ROOT/'audit/update18-tycho-art'
ARCHIVE=ROOT/'assets/original/tycho18/tycho-station-from-the-expanse-print_files.zip'
STEP=.4
PARTS={'upper':'station-main-antenna-side-b4-v1_25pct-scale_01m.gcode',
       'lower':'station-boehemoth-side-b4-v1_25pct-scale_01mm_p.gcode'}

def parse(text):
    assert '; support_material = 0' in text
    assert 'M83 ; extruder relative mode' in text
    xyz=np.zeros(3); segments=[]; absolute=True; relative_e=True
    for line in text.splitlines():
        code=line.split(';',1)[0].strip()
        if code=='G90': absolute=True
        elif code=='G91': absolute=False
        elif code=='M83': relative_e=True
        elif code=='M82': relative_e=False
        if not (code.startswith('G1 ') or code.startswith('G0 ')):continue
        tokens={k:float(v)for k,v in re.findall(r'([XYZE])(-?\d*\.?\d+)',code)}
        old=xyz.copy()
        for i,k in enumerate('XYZ'):
            if k in tokens:xyz[i]=tokens[k] if absolute else xyz[i]+tokens[k]
        # Skip purge, prime/retract, travel and first three skirt-bearing layers.
        if tokens.get('E',0)>0 and np.linalg.norm(xyz[:2]-old[:2])>.0001 and .6<=xyz[2]<150:
            assert absolute and relative_e, 'Unsupported command mode'
            assert abs(xyz[2]-old[2])<1e-6,'Unexpected extruding Z move'
            segments.append([*old[:2],*xyz[:2],xyz[2]])
    return np.array(segments,dtype=np.float32)

def recover(name,text):
    seg=parse(text)
    xy=seg[:,:4].reshape(-1,2); lo=xy.min(0)-2; hi=xy.max(0)+2
    shape=np.ceil((hi-lo)/STEP).astype(int)+1
    zlo=.2; nz=int(np.ceil((seg[:,4].max()-zlo)/STEP))+6
    vol=np.zeros((nz,shape[1],shape[0]),dtype=bool)
    slices=np.rint((seg[:,4]-zlo)/STEP).astype(int)+2
    pixel=np.rint((seg[:,:4]-np.tile(lo,2))/STEP).astype(int)
    for zi in np.unique(slices):
        img=Image.new('1',tuple(shape),0); draw=ImageDraw.Draw(img)
        for p in pixel[slices==zi]:draw.line(tuple(map(int,p)),fill=1,width=1)
        vol[zi]=np.asarray(img)
    # Close sub-voxel strand gaps and fill enclosed print infill cavities in 3D.
    # Open holes remain connected to exterior, unlike per-slice polygon filling.
    vol=ndimage.binary_closing(vol,iterations=3)
    filled=ndimage.binary_fill_holes(vol)
    labels,n=ndimage.label(filled); counts=np.bincount(labels.ravel()); counts[0]=0
    largest=int(np.argmax(counts)); discarded=int(filled.sum()-counts[largest]); filled=labels==largest
    surface=ndimage.gaussian_filter(filled.astype(np.float32),.65)
    verts,faces,normals,_=marching_cubes(surface,.5,spacing=(STEP,STEP,STEP),allow_degenerate=False)
    # ZYX voxel axes -> X, vertical printed Z, depth Y in an editable glTF.
    v=np.column_stack((verts[:,2]+lo[0]-125,verts[:,0]+zlo-2*STEP-.6,verts[:,1]+lo[1]-105))
    nrm=np.column_stack((normals[:,2],normals[:,0],normals[:,1]))
    if name=='lower':v[:,1]*=-1;v[:,2]*=-1;nrm[:,1]*=-1;nrm[:,2]*=-1
    # Export normals must agree with outward-facing triangle winding.
    q=np.cross(v[faces[:,1]]-v[faces[:,0]],v[faces[:,2]]-v[faces[:,0]])
    flip=(q*nrm[faces].mean(1)).sum(1)<0;faces[flip]=faces[flip][:,[0,2,1]]
    np.savez_compressed(OUT/(name+'.npz'),v=v.astype('float32'),n=nrm.astype('float32'),i=faces.astype('uint32'))
    return {'part':name,'segments':len(seg),'voxel_step_print_mm':STEP,'voxel_shape':list(map(int,vol.shape)),
        'printed_bounds':np.stack([v.min(0),v.max(0)]).tolist(),'vertices':len(v),'triangles':len(faces),
        'discarded_isolated_voxels':discarded,'source_sha256':__import__('hashlib').sha256(text.encode()).hexdigest()}

def main():
    OUT.mkdir(parents=True,exist_ok=True); records=[]
    with zipfile.ZipFile(ARCHIVE)as z:
        for name,filename in PARTS.items():
            p=OUT/(name+'.npz')
            if p.exists(): raise RuntimeError('Refusing existing recovery '+str(p))
            record=recover(name,z.read(filename).decode());record['filename']=filename;records.append(record);print(record,flush=True)
    write(AUD/'recovery.json',{'status':'APPROXIMATE CORE; NOT ORIGINAL STL; REVIEW REQUIRED','archive_sha256':sha256(ARCHIVE),
        'parts':records,'excluded':'Three accessory print jobs contain support_material=1 without semantic path labels; support separation unverified.',
        'losses':'0.4mm voxel sampling at 25% print scale, omitted bottom skirt layers, 1.2mm closing radius at print scale, smoothing and largest-component selection remove detail. Relative half rotation is inferred, not verified source assembly.',
        'orientation':'Both centered on declared 250x210 bed; lower mirrored around X to join nominal ring split planes.',
        'source_terms':'Included Printables PDF identifies ewr2san, model5439, CC BY-NC4.0; no original UV/material data.',
        'runtime':'NOT RUN'})
if __name__=='__main__':main()
