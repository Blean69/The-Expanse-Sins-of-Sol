"""Preserve and audit the supplied Donnager; editable normalization, no game package.
All writes remain in this worker's new donnager04-c directories. Asset text is data.
"""
from pathlib import Path
import argparse,copy,hashlib,json,sys,zipfile
import numpy as np
from PIL import Image,ImageDraw,ImageFont
from scipy.sparse import coo_matrix
from scipy.sparse.csgraph import connected_components
from common import Gltf,read_mesh
ROOT=Path(__file__).resolve().parents[1]
ASSETS=ROOT/'assets/derived/donnager04-c';AUDIT=ROOT/'audit/donnager04-c';BUILD=ROOT/'build/donnager04-c'
MAIN=Path('/run/media/haker/NVME 2/expanse-mod')
DONOR=Path('/run/media/haker/NVME 2/expanse-workers/tachi-one-pdc')
GAME=Path('/run/media/haker/NVME 2/SteamLibrary/steamapps/common/Sins2')

def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def write(p,d):p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(d,indent=2)+'\n')
def preserve(p,data):
 p.parent.mkdir(parents=True,exist_ok=True)
 if p.exists():
  if p.read_bytes()!=data:raise ValueError('Preserved source differs; refusing overwrite: '+str(p))
 else:p.write_bytes(data)
def font(n):
 try:return ImageFont.truetype('/usr/share/fonts/TTF/DejaVuSans.ttf',n)
 except OSError:return ImageFont.load_default(size=n)
def bounds(v):return {'min':v.min(0).tolist(),'max':v.max(0).tolist(),'dimensions':np.ptp(v,axis=0).tolist()}
def meshes(g):
 for i,n in enumerate(g.g['nodes']):
  if i not in g.world or 'mesh'not in n:continue
  for pi,p in enumerate(g.g['meshes'][n['mesh']]['primitives']):
   assert p.get('mode',4)==4,'Non-triangle primitive'
   v=g.positions(i,p);idx=g.accessor(p['indices']).reshape(-1,3)
   yield i,pi,p,v,idx

def draw_view(tri,colors,basis,size=(1250,550),fill=.90):
 # Full-source triangle painter; centroid ordering is adequate for audit previews,
 # but not a physically accurate renderer or occlusion/hidden-face proof.
 xyz=tri@np.array(basis).T;lo=xyz[:,:,:2].min((0,1));hi=xyz[:,:,:2].max((0,1));scale=min(size[0]*fill/(hi[0]-lo[0]),size[1]*fill/(hi[1]-lo[1]));xy=(xyz[:,:,:2]-(lo+hi)/2)*scale;xy[:,:,1]*=-1;xy+=np.array(size)/2
 im=Image.new('RGB',size,'#101722');d=ImageDraw.Draw(im)
 # Faces projecting below a quarter square pixel do not affect audit silhouette
 # appreciably and are omitted from preview rasterization only, never source.
 edge_a=xy[:,1]-xy[:,0];edge_b=xy[:,2]-xy[:,0];area=np.abs(edge_a[:,0]*edge_b[:,1]-edge_a[:,1]*edge_b[:,0])/2
 ids=np.nonzero(area>=.25)[0];order=ids[np.argsort(xyz[ids,:,2].mean(1))]
 for i in order:d.polygon([tuple(x)for x in xy[i]],fill=tuple(colors[i]))
 return im,{'projected_triangles_drawn':len(order),'source_triangles':len(tri),'subpixel_cutoff_square_pixels':.25,'basis':basis,'projection_scale':scale,'projected_center':((lo+hi)/2).tolist()}

def main():
 ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('--archive',type=Path,default=Path('/home/haker/Downloads/mcrn_donnager_the_expanse.zip'));ap.add_argument('--preview-length',type=float,default=100);ap.add_argument('--donnager-meters',type=float,default=475.5);ap.add_argument('--tachi-meters',type=float,default=46);a=ap.parse_args()
 if not a.archive.is_file():raise FileNotFoundError('Required supplied archive is missing: '+str(a.archive))
 for p in [ASSETS,AUDIT,BUILD]:p.mkdir(parents=True,exist_ok=True)
 archive=ASSETS/'original'/a.archive.name;preserve(archive,a.archive.read_bytes());master=ASSETS/'master'
 with zipfile.ZipFile(archive)as z:
  if z.testzip() is not None:raise ValueError('ZIP CRC failure')
  for info in z.infolist():
   if info.is_dir():continue
   dest=master/info.filename
   if not dest.resolve().is_relative_to(master.resolve()):raise ValueError('Unsafe archive member')
   if (info.external_attr>>16)&0o170000==0o120000:raise ValueError('Archive symlink unsupported')
   preserve(dest,z.read(info))
 master_hashes={str(p.relative_to(master)):sha(p)for p in sorted(master.rglob('*'))if p.is_file()};write(AUDIT/'preserved-source-hashes.json',{'supplied_archive':str(a.archive),'archive_sha256':sha(archive),'preserved_archive':str(archive),'extracted_master':str(master),'master_files':master_hashes})
 g=Gltf(master/'scene.gltf');rows=[];geometry=[];allv=[];matcounts=[0]*len(g.g['materials']);groupcounts={};degenerate=0
 for i,pi,p,v,idx in meshes(g):
  assert np.isfinite(v).all();assert idx.min()>=0 and idx.max()<len(v)
  group=g.g['nodes'][g.parents[i]]['name'];tr=v[idx];area2=np.linalg.norm(np.cross(tr[:,1]-tr[:,0],tr[:,2]-tr[:,0]),axis=1);degenerate+=int((area2<1e-10).sum());matcounts[p['material']]+=len(idx);groupcounts[group]=groupcounts.get(group,0)+len(idx);allv.append(v);geometry.append((i,p,v,idx))
  rows.append({'node':i,'name':g.g['nodes'][i]['name'],'group':group,'mesh':g.g['nodes'][i]['mesh'],'primitive':pi,'triangles':len(idx),'vertices':len(v),'material_index':p['material'],'attributes':list(p['attributes']),'world_bounds':bounds(v),'world_origin':g.world[i][:3,3].tolist(),'world_matrix':g.world[i].tolist(),'active':True})
 verts=np.concatenate(allv);b=bounds(verts);lo=verts.min(0);hi=verts.max(0);center=(lo+hi)/2;scale=a.preview_length/(hi[2]-lo[2]);transform=np.eye(4);transform[:3,:3]*=scale;transform[:3,3]=-center*scale
 textures=[]
 for x in g.g.get('images',[]):
  p=master/x['uri']
  with Image.open(p)as im:textures.append({'uri':x['uri'],'size':list(im.size),'mode':im.mode,'bytes':p.stat().st_size,'sha256':sha(p)})
 inventory={'asset':g.g['asset'],'available_formats':['glTF 2.0 JSON + external BIN','JPEG base-color textures'],'unavailable_source_formats':['FBX (DonnyFBX.fbx appears only as a node name; no FBX file supplied)','BLEND'],'triangles':sum(matcounts),'mesh_count':len(g.g['meshes']),'node_count':len(g.g['nodes']),'all_nodes_reachable':len(g.world)==len(g.g['nodes']),'animations':len(g.g.get('animations',[])),'skins':len(g.g.get('skins',[])),'materials':[dict(index=i,triangles=matcounts[i],definition=m)for i,m in enumerate(g.g['materials'])],'textures':textures,'groups':groupcounts,'source_world_bounds':b,'source_center':center.tolist(),'zero_area_triangles_world_tolerance_1e_minus10':degenerate,'nodes':g.g['nodes'],'mesh_nodes':rows,'source_axis_evidence':{'long_axis':'+Z fore / -Z aft inferred from positive-Z rail barrels and negative-Z Engines_Emit_Main_Engine_Blue geometry','up':'+Y consistent with global glTF convention; roll symmetry means dorsal assignment needs visual reference','source_scale':'Uncalibrated exporter units.100x FBX matrices are not evidence of meters.'},'PDC_evidence':'No PDC-named objects, skins, animations or dedicated hierarchy found. Absence of usable PDC assemblies is not proof every surface detail has been semantically identified. No PDC mounts fabricated.'}
 write(AUDIT/'asset-inventory.json',inventory)
 # Root-only normalization retains all original nodes/meshes/materials/buffers.
 norm=copy.deepcopy(g.g);root_index=len(norm['nodes']);oldroots=norm['scenes'][norm.get('scene',0)]['nodes'];norm['nodes'].append({'name':'Donnager04_centered_preview_UNCALIBRATED','matrix':transform.T.ravel().tolist(),'children':oldroots});norm['scenes'][norm.get('scene',0)]['nodes']=[root_index];out=ASSETS/'normalized-preview';out.mkdir(exist_ok=True)
 for p in master.rglob('*'):
  if p.is_file()and p.name not in ['scene.gltf','license.txt']:preserve(out/p.relative_to(master),p.read_bytes())
 write(out/'donnager04_centered.gltf',norm)
 write(out/'normalization-recipe.json',{'status':'EDITABLE PREVIEW ONLY, NOT GAME READY','input_scene':str(master/'scene.gltf'),'master_sha256':master_hashes,'world_to_preview':transform.tolist(),'preview_length':a.preview_length,'preview_units':'Arbitrary length normalization; multiply by final intended game length / preview_length','compiler_conversion':'Not applied. Right-handed glTF; positions/normals need the same verified Z reflection and winding/compiler procedure as existing ship pipeline.','retained':'All source geometry, UVs, node hierarchy and materials; only one parent transform added. No decimation/merging.'})
 ng=Gltf(out/'donnager04_centered.gltf');nv=np.concatenate([v for _,_,_,v,_ in meshes(ng)]);assert abs(np.ptp(nv,axis=0)[2]-a.preview_length)<1e-6
 # Independently enumerate material-chunk rail geometry and connectivity.
 rail=[x for x in geometry if 33<=x[0]<=36];rv=[];ri=[];off=0
 for i,p,v,ix in rail:rv.append(v);ri.append(ix+off);off+=len(v)
 rv=np.concatenate(rv);ri=np.concatenate(ri);unique,inv=np.unique(np.round(rv,4),axis=0,return_inverse=True);wi=inv[ri];edges=np.concatenate([wi[:,[0,1]],wi[:,[1,2]],wi[:,[2,0]]]);graph=coo_matrix((np.ones(len(edges)),(edges[:,0],edges[:,1])),shape=(len(unique),len(unique)));n,labels=connected_components(graph,directed=False);face_labels=labels[wi[:,0]];counts=np.bincount(face_labels);components=[]
 for k in np.argsort(counts)[::-1]:
  if counts[k]==0:continue
  vv=unique[labels==k];components.append({'component':int(k),'triangles':int(counts[k]),'world_bounds':bounds(vv)})
 sides=[]
 for sign in [-1,1]:
  tv=rv[ri];sel=np.all(tv[:,:,0]*sign>0,axis=1);sv=tv[sel].reshape(-1,3);drum=next(x for x in components if x['world_bounds']['min'][0]*sign>0 and x['triangles']==12536);db=drum['world_bounds'];pivot=(np.array(db['min'])+db['max'])/2
  sides.append({'side':'negative_X'if sign<0 else'positive_X','triangles':int(sel.sum()),'world_bounds':bounds(sv),'preview_bounds':bounds((sv-center)*scale),'estimated_drum_center_world':pivot.tolist(),'estimated_drum_center_preview':((pivot-center)*scale).tolist(),'pivot_basis':'Measured bounds center of symmetric main drum component (12,536 triangles), not an authored pivot','provisional_axis_world':[0,1,0],'axis_basis':'Drum is approximately circular in XZ, with axial span along Y; geometric inference only','max_forward_geometry_world':float(sv[:,2].max()),'muzzle_status':'Forwardmost face is not validated as the bore; no game muzzle coordinate emitted','motion_status':'Whole assembly can be selected by sign(X), but fixed cradle versus moving barrel is not separated. Limited rotation, hull sweep and gimbal identity NOT VERIFIED.'})
 assert sum(x['triangles']for x in sides)==len(ri),'Rail triangles cross centerplane; cannot use sign split'
 write(AUDIT/'railgun-geometry.json',{'source_nodes':[33,34,35,36],'triangles':len(ri),'weld_rounding_world_units':.0001,'connected_components':n,'top_components':components[:30],'sides':sides,'rig':'No authored independent yaw/pitch pivots; four material/chunk meshes share one Railguns parent origin. Do not rotate that shared origin.'})
 # A source-selection recipe is safer than inventing a turret hierarchy.
 write(out/'railgun-selection-recipe.json',{'master_nodes':[33,34,35,36],'selections':sides,'select_by':'Every vertex of selected triangles has X<0 or X>0 in evaluated source world space; both sides sum to all126863 source rail triangles.','next_steps':['Classify drum/cradle/barrels separately against reference views','Retopologize the selected derivative without changing master','Verify pivot/axis and limited sweep against hull before emitting game meshpoints']})
 donor_path=DONOR/'assets/derived/polish-b';meta_path=DONOR/'audit/polish-b/mount-metadata.json';base=donor_path/'expanse_polish_pdc_0_base.gltf';barrel=donor_path/'expanse_polish_pdc_0_barrel.gltf';tachi=MAIN/'assets/derived/baseline/mcrn_editable.gltf';required=[meta_path,base,barrel,tachi]
 for p in required:
  if not p.is_file():raise FileNotFoundError('Required read-only PDC donor dependency missing: '+str(p))
 meta=json.loads(meta_path.read_text());parts=[];total=[];dep_hash={str(meta_path):sha(meta_path)}
 for p in [base,barrel]:
  gg=Gltf(p);vv=np.concatenate([v for _,_,_,v,_ in meshes(gg)]);vv[:,2]*=-1 # donor is official compiler input convention
  if p==barrel:vv+=np.array(meta['rigs'][0]['turret_override']['barrel_position'])
  parts.append({'source':str(p),'triangles':sum(len(ix)for _,_,_,_,ix in meshes(gg)),'bounds_in_yaw_frame':bounds(vv)});total.append(vv)
  dep_hash[str(p)]=sha(p)
  for buf in gg.g['buffers']:dep_hash[str(p.parent/buf['uri'])]=sha(p.parent/buf['uri'])
 tg=Gltf(tachi);tp=np.concatenate([v for _,_,_,v,_ in meshes(tg)]);tlen=np.ptp(tp,axis=0)[2];dep_hash[str(tachi)]=sha(tachi)
 for buf in tg.g['buffers']:dep_hash[str(tachi.parent/buf['uri'])]=sha(tachi.parent/buf['uri'])
 pdcb=bounds(np.concatenate(total));stock={}
 for name in ['trader_light_frigate','trader_battle_capital_ship','trader_carrier_capital_ship']:
  p=GAME/'meshes'/f'{name}.mesh'
  if p.is_file():
   m=read_mesh(p);stock[name]={'path':str(p),'sha256':sha(p),'box_center_then_half_extents':m['box'],'dimensions_game_units':[2*x for x in m['box'][3:]],'triangles':m['triangles']}
 comparison={'normalized_Tachi_length_game_units':float(tlen),'donor_PDC_local_parts':parts,'assembled_PDC_yaw_frame_bounds_game_units':pdcb,'donor_triangles_per_PDC':sum(x['triangles']for x in parts),'source_dependencies':dep_hash,'Donnager_source_length_exporter_units':float(hi[2]-lo[2]),'Donnager_preview_length_arbitrary_units':a.preview_length,'physical_scaling':'For common units per meter k=Tachi_game_length/Tachi_canonical_meters: Donnager_game_length=k*Donnager_canonical_meters. Reuse donor PDC geometry at scale1.0 in game units to retain the same physical gun size. Do not multiply donor PDC size by the Donnager/Tachi hull-length ratio.','canonical_lengths':'Await main integrator source research; no physical length asserted here.','placement':'No Donnager PDC coordinates generated. Need surface inspection/spacing/rail sweep and external placement references.','stock_mesh_comparisons':stock}
 ratio=a.donnager_meters/a.tachi_meters;physical_k=tlen/a.tachi_meters;provisional_length=tlen*ratio
 comparison['provisional_lore_scale']={'Donnager_meters':a.donnager_meters,'Tachi_meters':a.tachi_meters,'length_ratio':ratio,'game_units_per_provisional_meter':physical_k,'Donnager_game_length':provisional_length,'Donnager_game_dimensions':[x*provisional_length/(hi[2]-lo[2])for x in b['dimensions']],'donor_PDC_provisional_meters':[x/physical_k for x in pdcb['dimensions']],'provenance':'Main integrator supplied secondary lore convention, not calibrated exporter meters or primary-verified screen scale.'}
 comparison['canonical_lengths']='Provisional secondary convention475.5m/46m only; geometry can be rescaled without touching master.'
 write(AUDIT/'scale-and-pdc-donor.json',comparison)
 physical_scene=copy.deepcopy(norm);pm=np.array(physical_scene['nodes'][-1]['matrix']).reshape(4,4).T;pm[:3,:]*=provisional_length/a.preview_length;physical_scene['nodes'][-1]['matrix']=pm.T.ravel().tolist();physical_scene['nodes'][-1]['name']='Donnager04_PROVISIONAL_475p5m_over_46m_Tachi';write(out/'donnager04_provisional_475p5m.gltf',physical_scene)
 write(out/'provisional-scale-recipe.json',comparison['provisional_lore_scale'])
 # Separate two complete rail assemblies by exact side-of-centerplane selection.
 # Geometry is still high-poly, with pivot estimates, not a functional turret rig.
 railout=ASSETS/'rail-assembly-preview';railout.mkdir(exist_ok=True)
 for side,sign in zip(sides,[-1,1]):
  pivot=np.array(side['estimated_drum_center_world']);rg={'asset':{'version':'2.0','generator':'donnager04_intake.py; whole assembly selection, unverified geometric pivot'},'scene':0,'scenes':[{'nodes':[0]}],'nodes':[{'name':side['side']+'_ESTIMATED_DRUM_PIVOT','translation':((pivot-center)*scale).tolist(),'children':[]}],'meshes':[],'materials':copy.deepcopy(g.g['materials']),'textures':copy.deepcopy(g.g.get('textures',[])),'images':copy.deepcopy(g.g.get('images',[])),'samplers':copy.deepcopy(g.g.get('samplers',[])),'accessors':[],'bufferViews':[]};blob=bytearray()
  for im in rg['images']:im['uri']='../normalized-preview/'+im['uri']
  def acc(data,ctype,typ,target):
   data=np.ascontiguousarray(data,dtype='<f4'if ctype==5126 else'<u4');padding=(-len(blob))%4;blob.extend(b'\0'*padding);offset=len(blob);blob.extend(data.tobytes());vi=len(rg['bufferViews']);rg['bufferViews'].append({'buffer':0,'byteOffset':offset,'byteLength':data.nbytes,'target':target});idx=len(rg['accessors']);spec={'bufferView':vi,'byteOffset':0,'componentType':ctype,'count':len(data),'type':typ}
   if typ=='VEC3':spec.update(min=data.min(0).tolist(),max=data.max(0).tolist())
   rg['accessors'].append(spec);return idx
  for node,p,v,ix in rail:
   selected=ix[np.all(v[ix][:,:,0]*sign>0,axis=1)]
   if not len(selected):continue
   used,newix=np.unique(selected,return_inverse=True);attrs={};attrs['POSITION']=acc((v[used]-pivot)*scale,5126,'VEC3',34962)
   for key,aid in p['attributes'].items():
    if key=='POSITION':continue
    vals=g.accessor(aid)[used]
    if key=='NORMAL':vals=vals@np.linalg.inv(g.world[node][:3,:3]);vals/=np.maximum(np.linalg.norm(vals,axis=1,keepdims=True),1e-12)
    if key=='TANGENT':raise ValueError('Unexpected source tangents need explicit transform')
    attrs[key]=acc(vals,5126,{2:'VEC2',3:'VEC3',4:'VEC4'}[vals.shape[1]],34962)
   meshindex=len(rg['meshes']);rg['meshes'].append({'name':g.g['nodes'][node]['name']+'_'+side['side'],'primitives':[{'attributes':attrs,'indices':acc(newix.reshape(-1),5125,'SCALAR',34963),'material':p['material'],'mode':4}]});ni=len(rg['nodes']);rg['nodes'].append({'name':g.g['nodes'][node]['name']+'_whole_assembly_chunk','mesh':meshindex});rg['nodes'][0]['children'].append(ni)
  stem='donnager04_rail_'+side['side'];(railout/(stem+'.bin')).write_bytes(blob);rg['buffers']=[{'uri':stem+'.bin','byteLength':len(blob)}];write(railout/(stem+'.gltf'),rg);check=Gltf(railout/(stem+'.gltf'));assert sum(len(ix)for _,_,_,_,ix in meshes(check))==side['triangles'];side['editable_candidate']=str(railout/(stem+'.gltf'))
 write(AUDIT/'railgun-geometry.json',{'source_nodes':[33,34,35,36],'triangles':len(ri),'weld_rounding_world_units':.0001,'connected_components':n,'top_components':components[:30],'sides':sides,'rig':'Whole high-poly assemblies selected by side. Estimated drum center is not authored/validated. Fixed cradle vs moving barrel unresolved; no game mount output.'})
 # Render all actual source geometry with flat representative source material colors.
 triangles=[];colors=[];railtri=[];railcolors=[]
 for i,p,v,idx in geometry:
  t=(v[idx]-center)*scale;mat=g.g['materials'][p['material']];pbr=mat.get('pbrMetallicRoughness',{});factor=np.array(pbr.get('baseColorFactor',[1,1,1,1])[:3]);c=np.power(np.clip(factor,0,1),1/2.2)*255
  if 'baseColorTexture'in pbr:
   tex=g.g['textures'][pbr['baseColorTexture']['index']];im=Image.open(master/g.g['images'][tex['source']]['uri']).convert('RGB');im.thumbnail((64,64));c=np.asarray(im).mean((0,1))*factor
  # Studio lift preserves detail in a CAD audit; no UV appearance accuracy claim.
  c=np.maximum(c,30);normal=np.cross(t[:,1]-t[:,0],t[:,2]-t[:,0]);normal/=np.maximum(np.linalg.norm(normal,axis=1,keepdims=True),1e-12);light=np.array([.3,.8,.5]);light/=np.linalg.norm(light);shade=.65+.35*np.abs(normal@light);col=np.clip(c[None,:]*shade[:,None]*1.3,0,255).astype('uint8');triangles.append(t);colors.append(col)
  if 33<=i<=36:railtri.append(t);railcolors.append(col)
 triangles=np.concatenate(triangles);colors=np.concatenate(colors);views=[('TOP: +Z fore to right; +X up',[[0,0,1],[1,0,0],[0,1,0]]),('SIDE: +Z fore to right; +Y up',[[0,0,1],[0,1,0],[-1,0,0]])]
 right=np.array([.50,0,.866]);up=np.array([-.4,.887,.231]);up-=right*np.dot(up,right);up/=np.linalg.norm(up);basis=np.array([right,up,np.cross(right,up)]).tolist();views.append(('OBLIQUE: actual full master geometry',basis));sheet=Image.new('RGB',(1400,1940),'#101722');draw=ImageDraw.Draw(sheet);renderlog=[]
 draw.text((30,18),'DONNAGER | ASSET INTAKE + HARDPOINT PLANNING',font=font(25),fill='white');draw.text((30,52),'1,804,024 source triangles | no game package | no runtime test | preview length100 arbitrary units',font=font(17),fill='#b6c6d6')
 for k,(title,basis)in enumerate(views):
  im,log=draw_view(triangles,colors,basis,size=(1320,500))
  if k==0:
   annot=ImageDraw.Draw(im)
   for sid in sides:
    xyz=np.array(sid['estimated_drum_center_preview'])@np.array(basis).T;xy=(xyz[:2]-log['projected_center'])*log['projection_scale'];xy[1]*=-1;xy+=np.array(im.size)/2;x,y=xy;annot.ellipse((x-9,y-9,x+9,y+9),outline='#67e5ff',width=3);dy=-43 if y<250 else 30;annot.line((x,y,x+50,y+dy),fill='#67e5ff',width=2);annot.text((x+53,y+dy-8),'measured drum / pivot estimate',font=font(14),fill='#b8f0ff')
  sheet.paste(im,(30,110+k*560));draw.text((30,86+k*560),title,font=font(19),fill='#e6eef7');renderlog.append(log)
 draw.text((30,1800),'RAILGUNS: two side assemblies; no authored moving-part hierarchy or valid pivots.',font=font(19),fill='#ffbe68');draw.text((30,1832),'PDC: no donor spliced yet. Preserve donor physical size; choose mounts only after surface/arc clearance.',font=font(17),fill='#b9d9f3');draw.text((30,1865),'Orange/gray are source material averages. No UV or hidden-geometry accuracy claim for this audit view.',font=font(16),fill='#a5b4c5');sheet.save(AUDIT/'donnager-planning-view.png')
 ri_im,log=draw_view(np.concatenate(railtri),np.concatenate(railcolors),basis,size=(1300,700));ri_im.save(AUDIT/'railguns-isolated-view.png');renderlog.append(log)
 scale_sheet=Image.new('RGB',(1400,850),'#101722');sd=ImageDraw.Draw(scale_sheet);sd.text((30,20),'PROVISIONAL RELATIVE SCALE | 475.5 m / 46 m convention',font=font(25),fill='white');sd.text((30,58),'Secondary lore convention supplied by integrator; not a calibrated measurement of the export.',font=font(18),fill='#b9cddd')
  # Reuse the actual top view generated above, with its measured projection scale.
 topview,_=draw_view(triangles,colors,views[0][1],size=(1320,500));scale_sheet.paste(topview,(30,92));sd.text((40,600),f'Donnager {provisional_length:.3f} game units long | Tachi {tlen:.3f} | ratio {ratio:.6f}',font=font(20),fill='white')
 ttri=np.concatenate([v[ix]for _,_,_,v,ix in meshes(tg)]);tcol=np.tile(np.array([185,192,203],dtype='uint8'),(len(ttri),1));twidth=round(1320/ratio);theight=round(twidth*np.ptp(tp,axis=0)[0]/tlen);tv,tl=draw_view(ttri,tcol,views[0][1],size=(twidth,max(20,theight)));scale_sheet.paste(tv,(60,657));sd.text((220,660),'Actual normalized Tachi silhouette at the same length scale',font=font(19),fill='#b9cddd');sd.text((40,730),f'PDC donor:677 triangles | {pdcb["dimensions"][0]/physical_k:.2f} x {pdcb["dimensions"][1]/physical_k:.2f} x {pdcb["dimensions"][2]/physical_k:.2f} provisional meters',font=font(19),fill='#b9cddd');sd.text((40,765),'Keep donor at1.0 game scale to retain gun size. No guessed Donnager PDC network has been placed.',font=font(18),fill='#dcb57a');scale_sheet.save(AUDIT/'provisional-scale-comparison.png')
 write(BUILD/'preview-render-log.json',{'method':'Full actual source geometry, CPU triangle painter, mean-depth order and source material representative averages; triangle projections below.25 square pixels excluded from raster only. No AI image.','views':renderlog})
 preservation={'status':'PASS','archive_sha256':sha(a.archive),'archive_copy_identical':sha(a.archive)==sha(archive),'master_unchanged':master_hashes=={str(p.relative_to(master)):sha(p)for p in sorted(master.rglob('*'))if p.is_file()},'all_triangle_indices_in_range':True,'finite_positions':True,'normalized_long_axis':float(np.ptp(nv,axis=0)[2]),'normalized_triangles_unchanged':sum(len(ix)for _,_,_,_,ix in meshes(ng))==sum(matcounts),'rail_two_sides_partition_all_triangles':sum(x['triangles']for x in sides)==len(ri),'donor_dependency_hashes_unchanged':all(sha(p)==h for p,h in dep_hash.items()),'runtime':'NOT RUN','game_package':'NOT BUILT; high-poly intake and planning only'}
 assert preservation['master_unchanged']and preservation['donor_dependency_hashes_unchanged'];write(AUDIT/'offline-checks.json',preservation);print(json.dumps({'status':'PASS','triangles':sum(matcounts),'groups':groupcounts,'checks':str(AUDIT/'offline-checks.json'),'preview':str(AUDIT/'donnager-planning-view.png')}))
if __name__=='__main__':main()
