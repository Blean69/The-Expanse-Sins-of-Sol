"""Copy a built mod to the observed Proton user-mod directory, never enable it."""
from common import *
import argparse, shutil

p=argparse.ArgumentParser();p.add_argument('variant',choices=['name','visual']);p.add_argument('--mods-dir',type=Path);a=p.parse_args()
name={'name':'expanse_cobalt_name','visual':'expanse_corvette_visual'}[a.variant]
mods=a.mods_dir or GAME.parents[1]/'compatdata/1575940/pfx/drive_c/users/steamuser/AppData/Local/sins2/mods'
assert mods.is_dir(), f'Mods directory does not exist: {mods}'
target=mods/name
if target.exists():raise SystemExit(f'Refusing to overwrite {target}; remove or back up that project mod manually first.')
assert not target.resolve().is_relative_to(GAME.resolve())
shutil.copytree(ROOT/'build'/name,target)
print('Installed, not enabled:',target)
