"""Meaningful offline checks; does not launch Sins II."""
from common import *
from build import verify_install
import hashlib,struct,zipfile

verify_install();source=read(ROOT/'audit/source-checksums.json')
assert hashlib.sha256((ROOT/'assets/original/mcrn_tachi_expanse_tv_show.zip').read_bytes()).hexdigest()==source['archive_sha256']
for name,digest in source['files'].items():assert hashlib.sha256((ROOT/'assets/source/tachi'/name).read_bytes()).hexdigest()==digest
report=[]
for path in sorted((ROOT/'build/converted-textures').glob('*.dds')):
    b=path.read_bytes();assert b[:4]==b'DDS ';fourcc=b[84:88];height,width=struct.unpack_from('<II',b,12);mips=struct.unpack_from('<I',b,28)[0]
    fmt='BC5_SNORM' if fourcc==b'BC5S' else ('BC7_UNORM' if fourcc==b'DX10' and struct.unpack_from('<I',b,128)[0]==98 else 'UNKNOWN')
    assert fmt==('BC5_SNORM' if path.stem.endswith('_nrm') else 'BC7_UNORM')
    assert width==height and width in [4,2048];assert mips==(12 if width==2048 else 3)
    header=148 if fourcc==b'DX10' else 128
    expected=sum(max(1,(width>>level)+3>>2)*max(1,(height>>level)+3>>2)*16 for level in range(mips))
    assert len(b)==header+expected,(path,len(b),header+expected)
    report.append(dict(file=path.name,format=fmt,width=width,height=height,mips=mips,bytes=len(b)))
assert len(report)==16;write(ROOT/'audit/dds-validation.json',report)
for name in ['expanse_cobalt_name','expanse_corvette_visual']:
    out=ROOT/'build'/name
    with zipfile.ZipFile(out.with_suffix('.zip')) as z:
        assert z.testzip() is None
        assert '.mod_meta_data' in z.namelist()
        assert set(z.namelist())=={str(p.relative_to(out)) for p in out.rglob('*') if p.is_file()}
        for p in out.rglob('*'):
            if p.is_file():assert z.read(str(p.relative_to(out)))==p.read_bytes()
    assert not list(out.rglob('*.weapon'))
binary=read_mesh(ROOT/'build/compiler-binary/mcrn_corvette_baseline.mesh');data=read(ROOT/'build/compiler-json/mcrn_corvette_baseline.mesh_json')
assert binary['triangles']==14622
assert np.allclose([x['position'] for x in binary['meshpoints']],[x['position'] for x in data['points']],atol=1e-5)
assert binary['materials']==data['materials']
assert len(read(ROOT/'audit/pdc-rig-candidates.json')['rigs'])==6
write(ROOT/'audit/offline-results.json',dict(source_integrity='PASS',installed_reference_integrity='PASS',sdk_hashes='PASS (62)',dds_headers_and_sizes='PASS (16)',zip_integrity_and_contents='PASS (2)',binary_json_mesh_agreement='PASS',six_pdc_rig_candidates='PASS (count only)',in_game='NOT RUN'))
print('PASS: source/install integrity, 62 schemas, 16 DDS formats/mips/sizes, 2 ZIPs, mesh JSON/binary agreement. In-game: NOT RUN.')
