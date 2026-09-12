"""Preserve the supplied archive and safely extract its exact contents."""
from common import *
import argparse,hashlib,shutil,zipfile
p=argparse.ArgumentParser();p.add_argument('archive',type=Path);a=p.parse_args()
digest=hashlib.sha256(a.archive.read_bytes()).hexdigest()
assert digest=='47abb4ac87c2af477a906bdab4e87f20551e72917877e6dfa489a11946320142', 'Different asset package: perform a new intake audit first'
original=ROOT/'assets/original/mcrn_tachi_expanse_tv_show.zip';original.parent.mkdir(parents=True,exist_ok=True)
if not original.exists():shutil.copy2(a.archive,original)
assert hashlib.sha256(original.read_bytes()).hexdigest()==digest
with zipfile.ZipFile(original) as z:
    for member in z.infolist():
        path=Path(member.filename)
        assert not path.is_absolute() and '..' not in path.parts
    z.extractall(ROOT/'assets/source/tachi')
print('Original preserved; source extracted:',digest)
