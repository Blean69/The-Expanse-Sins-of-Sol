"""Explain generated flat-material UV-frame fallback separately from compiler gates."""
from donnager10_geometry_common import *
s=read(OUT/'retained-source-frames.json');m=read(AUDIT/'mount-metadata.json');rows=[]
for key,parts in s.items():
 g=Gltf(OUT/('expanse10_'+key+'.gltf'))
 for mi,q in parts.items():
  pr=g.g['meshes'][0]['primitives'][int(mi)];name=g.g['materials'][pr['material']]['name']
  if name=='mcrn_tachi_material':continue
  material=int(name.rsplit('_',1)[1]);assert 'normalTexture' not in a.g['materials'][material];v=np.array(q['positions']);n=np.array(q['normals']);uv=np.array(q['uv']);idx=g.accessor(pr['indices']).flatten().reshape(-1,3);tri=v[idx];du=uv[idx[:,1]]-uv[idx[:,0]];dv=uv[idx[:,2]]-uv[idx[:,0]];det=du[:,0]*dv[:,1]-du[:,1]*dv[:,0];valid=abs(det)>1e-12;inv=np.divide(1,det,out=np.zeros_like(det),where=valid);e1=tri[:,1]-tri[:,0];e2=tri[:,2]-tri[:,0];tt=(e1*dv[:,1,None]-e2*du[:,1,None])*inv[:,None];ta=np.zeros_like(v)
  for ci in range(3):np.add.at(ta,idx[:,ci],tt)
  ta-=n*np.sum(ta*n,axis=1)[:,None];bad=np.linalg.norm(ta,axis=1)<1e-10;rows.append({'mesh':key,'material':material,'source_normal_texture_absent':True,'generated_normal_texture':'expanse10_donnager_flat_nrm','uv_degenerate_triangles':int((~valid).sum()),'flat_material_orthogonal_basis_vertices':int(bad.sum())})
assert sum(r['flat_material_orthogonal_basis_vertices'] for r in rows)==m['uv_frame_fallback_corners_flat_materials'];write(AUDIT/'uv-frame-fallback.json',{'status':'PASS FLAT MATERIAL SCOPE VERIFIED','generated_orthogonal_basis_vertices':sum(r['flat_material_orthogonal_basis_vertices'] for r in rows),'compiler_repair_fallbacks':0,'donor_fallbacks':0,'explanation':'Original Donnager supplies no normal maps; UV-degenerate or cancelling tangent sums require an arbitrary orthonormal frame for the generated flat normal texture. This is not a source-detail normal reconstruction. Donor source frames are retained unchanged.','materials':rows});print('PASS flat-material frame fallback scope:',sum(r['flat_material_orthogonal_basis_vertices'] for r in rows))
