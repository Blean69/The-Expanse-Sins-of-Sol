"""Rebuild shading on changed faces, preserving 30-degree geometric creases.
Source material partitions and UV coordinates remain distinct.
"""
from update11_donnager_common import *
from collections import defaultdict
z=np.load(OUT/'probe.npz');meta=read(AUDIT/'optimization-probe.json');out={};checks=[]
for r in meta['parts']:
 k=r['key'];v=z[k+'_v'];old=z[k+'_n'];uv=z[k+'_uv'];idx=z[k+'_i'];tri=v[idx];cross=np.cross(tri[:,1]-tri[:,0],tri[:,2]-tri[:,0]);area=np.linalg.norm(cross,axis=1);edge=np.max(np.linalg.norm(tri-np.roll(tri,1,axis=1),axis=2),axis=1);keep=(area>1e-7)&(area/np.maximum(edge**2,1e-20)>1e-7);removed=int(sum(~keep));idx=idx[keep];cross=cross[keep];area=area[keep];flip=np.sum(cross*old[idx].mean(1),axis=1)<0;idx[flip]=idx[flip][:,[0,2,1]];cross[flip]*=-1;face=cross/area[:,None];_,weld=np.unique(np.round(v,5),axis=0,return_inverse=True);wi=weld[idx];adj=defaultdict(list)
 for fi,row in enumerate(wi):
  for vi in row:adj[int(vi)].append(fi)
 n=np.empty((len(idx),3,3))
 for fi,row in enumerate(wi):
  for ci,vi in enumerate(row):
   neighbors=adj[int(vi)];near=[j for j in neighbors if np.dot(face[fi],face[j])>=.866025403784];value=cross[near].sum(0);n[fi,ci]=value/np.linalg.norm(value)
 out[k+'_v']=v[idx].reshape(-1,3);out[k+'_n']=n.reshape(-1,3);out[k+'_uv']=uv[idx].reshape(-1,2);out[k+'_i']=np.arange(len(idx)*3).reshape(-1,3);checks.append({'node':r['node'],'material':r['material'],'triangles':len(idx),'removed_numerical_slivers':removed,'normals_reconstructed_on_final_faces':True,'crease_degrees':30,'source_triangles':r['source_triangles'],'simplifier_attribute_error':r['error']});r['triangles']=len(idx)
np.savez(OUT/'optimized.npz',**out);write(AUDIT/'normal-reconstruction.json',checks);meta['triangles']=sum(r['triangles'] for r in meta['parts']);write(AUDIT/'optimized-parts.json',meta);print('Corrective topology',meta['triangles'],'triangles; removed',sum(q['removed_numerical_slivers'] for q in checks))
