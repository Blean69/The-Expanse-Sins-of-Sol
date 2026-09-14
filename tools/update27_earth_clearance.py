"""Recheck actual compiled hull and rail clearance, including intermediate PDC angles."""
import numpy as np
from update27_earth_geometry import GAME,AUD,BUILD,IDS
from update26_platform_common import load_parts
from update14_pdc_arcs import Rays,sample,pose,self_check
from common import read,write

def main():
 report={'ray_backend':self_check(BUILD/'clearance-selftest'),'ships':{}}
 for kind,ID in IDS.items():
  a=read(AUD/(kind+'-integration.json'));hull=np.concatenate([p['v'][p['i']]for p in load_parts(GAME/'meshes'/(a['hull_mesh']+'.mesh'))]);obstacles=[hull];rails=[]
  for r in a['rigs']:
   if r['kind']!='rail':continue
   m=r['mount'];B=np.column_stack([np.cross(m['up'],m['forward']),m['up'],m['forward']]);pos=np.array(m['weapon_position'])
   if r['turret']:
    for p in load_parts(GAME/'meshes'/(r['turret']['gimbal_mesh']+'.mesh')):obstacles.append(p['v'][p['i']]@B.T+pos)
  ray=Rays(np.concatenate(obstacles),BUILD/(kind+'-compiled-clearance'));results=[]
  for r in a['rigs']:
   if r['kind']!='pdc':continue
   m=r['mount'];y=m['yaw_arc'];p=m['pitch_arc'];bad,example,n=sample(ray,m,r['turret'],np.arange(y['min_angle'],y['max_angle']+.01,1),np.arange(p['min_angle'],p['max_angle']+.01,1),3);assert not bad.any(),(r['mount']['weapon'],example);results.append({'weapon':m['weapon'],'samples':n,'blocked':0})
  ray.close();ray=Rays(hull,BUILD/(kind+'-rail-clearance'))
  for r in a['rigs']:
   if r['kind']!='rail':continue
   m=r['mount'];B=np.column_stack([np.cross(m['up'],m['forward']),m['up'],m['forward']]);mu=r['turret']['muzzle_positions']if r['turret']else[[0,0,0]];orig=[];dirs=[]
   for yaw in np.linspace(m['yaw_arc']['min_angle'],m['yaw_arc']['max_angle'],25):
    angle=np.radians(yaw);R=np.array([[np.cos(angle),0,np.sin(angle)],[0,1,0],[-np.sin(angle),0,np.cos(angle)]])
    for q in mu:orig.append(np.array(m['weapon_position'])+B@R@q);dirs.append(B@R@np.array([0,0,1]))
   h=ray(orig,dirs);assert not(h>0).any(),(m['weapon'],h.tolist());rails.append({'weapon':m['weapon'],'samples':len(h),'blocked':0})
  ray.close();report['ships'][ID]={'pdc':results,'rail':rails,'limits':'Stationary hull/resting rails only; excludes moving sibling PDCs. Sampled angles, not continuous proof.'}
 write(AUD/'compiled-clearance.json',report);print('PASS compiled 1-degree PDC grid +3-degree envelope and rail muzzle rays')
if __name__=='__main__':main()
