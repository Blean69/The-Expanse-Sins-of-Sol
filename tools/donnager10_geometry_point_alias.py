"""Add accepted hangar spawn alias without touching geometry or editable UI."""
from donnager10_geometry_common import *
import copy
m=read(AUDIT/'mount-metadata.json');points=m['meshpoints']['donnager_hull']
if not any(p['name']=='weapon.boarding.0' for p in points):
 p=copy.deepcopy(next(p for p in points if p['name']=='hangar.0'));p['name']='weapon.boarding.0';points.append(p);write(AUDIT/'mount-metadata.json',m)
f=OUT/'expanse10_donnager_hull.gltf';g=read(f)
if not any(p['name']=='weapon.boarding.0' for p in g['nodes']):
 p=copy.deepcopy(next(p for p in g['nodes'] if p['name']=='hangar.0'));p['name']='weapon.boarding.0';g['nodes'][0]['children'].append(len(g['nodes']));g['nodes'].append(p);write(f,g)
