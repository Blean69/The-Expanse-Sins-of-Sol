"""UN One assembly, original procedural livery, and SDK art-only compilation.
All shell parts use one common transform. No weapons or gameplay definitions.
"""
from pathlib import Path
import argparse,copy,hashlib,json,os,struct,subprocess,zipfile
import numpy as np
from scipy.spatial import cKDTree
from scipy.spatial.transform import Rotation
from PIL import Image,ImageDraw,ImageFont
from common import Gltf,read,read_mesh,write
import update23_murphy_art as helper
ROOT=Path(__file__).resolve().parents[1];MAIN=Path('/run/media/haker/NVME 2/expanse-mod');BASE=MAIN/'build/experiments/expanse_update19';GAME_NATIVE=Path('/run/media/haker/NVME 2/SteamLibrary/steamapps/common/Sins2')
OUT=ROOT/'assets/derived/update25-unone';BUILD=ROOT/'build/update25-unone';GAME=BUILD/'game';AUD=ROOT/'audit/update25-unone';NAME='expanse25_unone_hull';ZIP=Path('/home/haker/Downloads/un-one-from-the-expanse-tv-show-1100-scale-model_files.zip');ENV=helper.ENV;WINE=helper.WINE;SDK=helper.SDK
for p in[OUT,BUILD,AUD,GAME/'meshes',GAME/'mesh_materials',GAME/'textures',GAME/'effects']:p.mkdir(parents=True,exist_ok=True)
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def prepare():
 archive=zipfile.ZipFile(ZIP);source={};records=[];excluded=[]
 for name in archive.namelist():
  if not name.lower().endswith('.stl'):continue
  raw=archive.read(name);a=np.frombuffer(raw[84:],dtype=[('n','<f4',3),('v','<f4',(3,3)),('a','<u2')]);t=a['v'].astype(float);q=np.cross(t[:,1]-t[:,0],t[:,2]-t[:,0]);record={'member':name,'sha256':hashlib.sha256(raw).hexdigest(),'triangles':len(t),'bounds':[t.reshape(-1,3).min(0).tolist(),t.reshape(-1,3).max(0).tolist()]}
  if 'Stand'in name or 'C1 (x8)'in name or 'R1 (x2)'in name:record['reason']='Printing stand/interface or internal repeated assembly peg';excluded.append(record);continue
  assert np.isfinite(t).all()and(np.linalg.norm(q,axis=1)>0).all();source[name]=t;records.append(record)
 allsource=np.concatenate(list(source.values()));lo=allsource.reshape(-1,3).min(0);hi=allsource.reshape(-1,3).max(0);center=(hi+lo)/2;scale=52*(104.9869586/46)/(hi[0]-lo[0]);transform=lambda t:((np.asarray(t)-center)*scale)[...,[1,2,0]]
 # Original part coordinates join at X=110, -60, -147. Mirrored wing roots
 # remain at Y=+/-85.572853. No piece receives an independent recentering.
 groups={'top':[],'side':[],'wing':[],'engine':[]};frameBounds=np.array([transform(lo),transform(hi)])
 for name,t in source.items():
  game=transform(t);q=np.cross(game[:,1]-game[:,0],game[:,2]-game[:,0]);normal=q/np.linalg.norm(q,axis=1)[:,None]
  if 'Engines'in name:groups['engine'].append(game)
  elif 'Wing'in name or 'wing'in name:groups['wing'].append(game)
  else:
   top=abs(normal[:,1])>=np.maximum(abs(normal[:,0]),abs(normal[:,2]));groups['top'].append(game[top]);groups['side'].append(game[~top])
 parts={k:np.concatenate(v)for k,v in groups.items()};points=[{'name':'center','translation':[0,0,0]},{'name':'above','translation':[0,15,0]},{'name':'aura','translation':[0,-12,0]}];engines=transform(source['UN One - Engines.stl']);nozzles=[];glow=[]
 for j,side in enumerate([-1,1]):
  c=transform([0,side*12,0]);o=np.array([c[0],c[1],frameBounds[0,2]-15]);hit=helper.rayhit(engines,o,[0,0,1]);p=hit+[0,0,-.07];corners=[]
  # Glowing patch follows the actual rear face, including its slant.
  for dx,dy in[(-1.7,-.75),(1.7,-.75),(1.7,.75),(-1.7,.75)]:
   h=helper.rayhit(engines,[p[0]+dx,p[1]+dy,frameBounds[0,2]-15],[0,0,1]);corners.append(h+[0,0,-.05])
  a,b,c,d=np.array(corners);glow.extend([[a,c,b],[a,d,c]]);points.append({'name':f'exhaust.{j}','translation':p.tolist(),'rotation':[0,1,0,0]});nozzles.append({'mesh_point':f'exhaust.{j}','position':p.tolist(),'source_y':side*12,'method':'First rear-facing intersection of actual Engines part; glow patch corners independently ray-projected.'})
 parts['glow']=np.array(glow)
 # Reuse the proven smooth-normal/tangent generator, with UV projection suited
 # to the assembled shuttle. Every source face remains at original relative position.
 original_frames=helper.frames
 def unoneframes(tt):
  p=original_frames(tt);v=p['v'];n=p['n'];face=np.cross(tt[:,1]-tt[:,0],tt[:,2]-tt[:,0]);dominant=np.repeat(np.argmax(abs(face),axis=1),3);top=dominant==1;front=dominant==2;uv=np.zeros((len(v),2));uv[top,0]=(v[top,0]-frameBounds[0,0])/(frameBounds[1,0]-frameBounds[0,0]);uv[top,1]=(v[top,2]-frameBounds[0,2])/(frameBounds[1,2]-frameBounds[0,2]);uv[~top,0]=(v[~top,2]-frameBounds[0,2])/(frameBounds[1,2]-frameBounds[0,2]);uv[~top,1]=(v[~top,1]-frameBounds[0,1])/(frameBounds[1,1]-frameBounds[0,1]);uv[front,0]=(v[front,0]-frameBounds[0,0])/(frameBounds[1,0]-frameBounds[0,0]);p['uv']=uv
  tangent=np.zeros_like(p['t']);tangent[top|front,0]=1;tangent[~(top|front),2]=1;tangent[:,:3]-=n*np.sum(tangent[:,:3]*n,axis=1)[:,None];norm=np.linalg.norm(tangent[:,:3],axis=1);bad=norm<1e-8;tangent[bad,:3]=p['t'][bad,:3];tangent[:,:3]/=np.linalg.norm(tangent[:,:3],axis=1)[:,None];bit=np.where(top[:,None],[0,0,1],[0,1,0]);tangent[:,3]=np.where(np.sum(np.cross(n,tangent[:,:3])*bit,axis=1)<0,-1,1);p['t']=tangent;return p
 helper.NAME=NAME;helper.OUT=OUT;helper.frames=unoneframes;helper.save(parts,points);helper.frames=original_frames
 tex=OUT/'texture-sources';tex.mkdir(exist_ok=True);size=1024;rng=np.random.default_rng(25)
 # White/gray diplomatic livery uses original paint only; no photo projection.
 def panel(color):
  v=np.clip(np.array(color)+rng.integers(-2,3,(size,size,1)),0,255);a=np.zeros((size,size,4),np.uint8);a[:,:,:3]=v;a[:,:,3]=255;return Image.fromarray(a)
 top=panel((171,177,175));draw=ImageDraw.Draw(top)
 # Top UV vertical axis is longitudinal; restrained seam lines and a readable
 # UN ONE legend enhance the source's embossed livery without adding hull geometry.
 for y in range(0,size,128):draw.line((0,y,size,y),fill=(154,159,159),width=1)
 try:font=ImageFont.truetype('/usr/share/fonts/TTF/DejaVuSans.ttf',40)
 except OSError:font=ImageFont.load_default(size=40)
 text='UN ONE';box=draw.textbbox((0,0),text,font=font);label=Image.new('RGBA',(box[2]+8,60));ImageDraw.Draw(label).text((4,2),text,font=font,fill=(34,70,112,255));label=label.rotate(90,expand=True);top.paste(label,((size-label.width)//2,int(size*.48)),label);top.putalpha(255);top.save(tex/'expanse25_unone_top_clr.png')
 wing=panel((171,177,175));draw=ImageDraw.Draw(wing);draw.rectangle((0,0,68,size),fill=(35,78,130));draw.rectangle((size-68,0,size,size),fill=(35,78,130));wing.save(tex/'expanse25_unone_wing_clr.png')
 side=panel((150,156,156));draw=ImageDraw.Draw(side);ztoV=lambda z:int((z-lo[2])/(hi[2]-lo[2])*size);xtoU=lambda x:int((x-lo[0])/(hi[0]-lo[0])*size);draw.rectangle((xtoU(-60),ztoV(-7),xtoU(210),ztoV(9)),fill=(111,97,66));mask=Image.new('RGBA',(size,size),(0,0,0,0));md=ImageDraw.Draw(mask)
 for x in[-32,1,34,67,100,140,177]:
  rect=(xtoU(x-9),ztoV(-2.5),xtoU(x+9),ztoV(3));draw.rectangle(rect,fill=(31,64,90));md.rectangle(rect,fill=(0,0,65,0))
 side.save(tex/'expanse25_unone_side_clr.png');mask.save(tex/'expanse25_unone_windows_msk.png');panel((31,37,43)).save(tex/'expanse25_unone_engine_clr.png');Image.new('RGBA',(16,16),(55,136,200,255)).save(tex/'expanse25_unone_glow_clr.png');Image.new('RGBA',(16,16),(255,180,90,255)).save(tex/'expanse25_unone_orm.png');Image.new('RGBA',(16,16),(0,0,0,0)).save(tex/'expanse25_unone_msk.png');Image.new('RGBA',(16,16),(0,0,120,0)).save(tex/'expanse25_unone_glow_msk.png')
 allgame=np.concatenate(list(parts.values())).reshape(-1,3);counts={k:len(v)for k,v in parts.items()};write(AUD/'integration-spec.json',{'status':'PREPARED','output_game':str(GAME),'base_mesh':NAME,'source':{'archive':str(ZIP),'sha256':sha(ZIP),'author':'Lionel SAVOCA','license':'CC BY-SA 4.0, per included assembly PDF','included':records,'excluded':excluded,'all_included_faces_retained':True,'source_triangles':len(allsource),'source_bounds':[lo.tolist(),hi.tolist()],'coordinate_policy':'One bounding-box centering and cyclic axis permutation [Y,Z,X] for every assembled part; no individual recentering.'},'scale':{'estimated_length_m':52,'basis':'Author describes a 52cm print at 1:100. A model-design estimate, not verified TV dimensions.','game_units_per_metre':104.9869586/46,'source_to_game':scale,'game_length':float(np.ptp(allgame[:,2]))},'counts':{'hull':sum(counts.values()),'source':len(allsource),'material_triangles':counts,'added_glow_faces':4,'weapons':0},'spatial':{'box':{'center':((allgame.max(0)+allgame.min(0))/2).tolist(),'extents':((allgame.max(0)-allgame.min(0))/2).tolist()},'radius':float(np.linalg.norm(allgame,axis=1).max())},'meshpoints':points,'nozzles':nozzles,'role':'Unarmed diplomatic/support ship; classification, capabilities, balance and research owned by main integration.','checks':{'no_individual_part_recentring':True,'stands_and_internal_print_pegs_excluded':True,'all_117822_selected_source_faces_retained':len(allsource)==117822,'degenerate_source_triangles':0},'runtime':'NOT RUN'})
 print('Prepared UN One',len(allsource),'source faces,',counts,flush=True)

def compile():
 def run(fmt,suffix=''):
  dest=BUILD/('compiler-'+fmt);dest.mkdir(exist_ok=True)
  with(BUILD/(NAME+suffix+'-'+fmt+'.log')).open('w')as log:subprocess.run([str(WINE),str(SDK/'MeshBuilder/bin/MeshBuilder.exe'),'--input_path=Z:'+str(OUT/(NAME+'.gltf')),'--output_folder_path=Z:'+str(dest),'--mesh_output_format='+fmt,'--fill_triangle_facing_grid'],env=ENV,stdout=log,stderr=subprocess.STDOUT,check=True,timeout=300)
 run('json');m=read(BUILD/'compiler-json'/(NAME+'.mesh_json'));asset=Gltf(OUT/(NAME+'.gltf'));buf=bytearray(asset.buffers[0]);v=np.array([x['p']for x in m['non_skinned_vertices']]);n=np.array([x['n']for x in m['non_skinned_vertices']]);allidx=np.array(m['vertex_indices']);flips=0
 for prim in m['primitives']:
  mat=m['materials'][prim['material_index']];p=next(p for p in asset.g['meshes'][0]['primitives']if mat.endswith('_'+asset.g['materials'][p['material']]['name']));ii=allidx[prim['vertex_index_start']:prim['vertex_index_start']+prim['vertex_index_count']].reshape(-1,3);q=np.cross(v[ii[:,1]]-v[ii[:,0]],v[ii[:,2]]-v[ii[:,0]]);flip=np.sum(q*n[ii].mean(1),axis=1)<-1e-5;acc=asset.g['accessors'][p['indices']];view=asset.g['bufferViews'][acc['bufferView']];arr=np.ndarray((acc['count']//3,3),dtype='<u4',buffer=buf,offset=view['byteOffset']);expected=asset.accessor(p['attributes']['POSITION']);expected[:,2]*=-1;assert np.allclose(np.sort(expected[arr],axis=1),np.sort(v[ii],axis=1),atol=4e-5);arr[flip]=arr[flip][:,[0,2,1]];flips+=int(flip.sum())
 if flips:(OUT/(NAME+'.bin')).write_bytes(buf);run('json','-winding')
 run('binary');m=read(BUILD/'compiler-json'/(NAME+'.mesh_json'));bp=BUILD/'compiler-binary'/(NAME+'.mesh');original=bp.read_bytes();b=bytearray(original);count=struct.unpack_from('<Q',b,53)[0];off=61;rows=[];offsets=[]
 for _ in range(count):
  vals=struct.unpack_from('<12f?',b,off);rows.append(vals[:-1]);offsets.append(off+24);off+=49+(8 if vals[-1]else 0)
 rows=np.array(rows);ref=read(OUT/'source-frames.json');lookup=np.concatenate([np.concatenate([r['v'],r['n'],r['uv']],axis=1)for r in ref.values()]);distance,match=cKDTree(lookup).query(np.concatenate([rows[:,:6],rows[:,10:12]],axis=1));assert distance.max()<2e-4;t=np.concatenate([r['t']for r in ref.values()])[match];n=rows[:,3:6];t[:,:3]-=n*np.sum(n*t[:,:3],axis=1)[:,None];t[:,:3]/=np.linalg.norm(t[:,:3],axis=1)[:,None];allowed=np.zeros(len(b),bool)
 for i,pos in enumerate(offsets):struct.pack_into('<4f',b,pos,*t[i]);allowed[pos:pos+16]=True
 assert np.all((np.frombuffer(original,np.uint8)==np.frombuffer(b,np.uint8))|allowed);info=read_mesh(bp);prefix=info['parsed_prefix_bytes'];assert original[prefix:]==b[prefix:];idx=np.array(m['vertex_indices']).reshape(-1,3);q=np.cross(rows[idx[:,1],:3]-rows[idx[:,0],:3],rows[idx[:,2],:3]-rows[idx[:,0],:3]);opposed=int((np.sum(q*n[idx].mean(1),axis=1)<-1e-5).sum());assert opposed==0;(GAME/'meshes'/(NAME+'.mesh')).write_bytes(b)
 meta=read(AUD/'integration-spec.json');assert len(idx)==meta['counts']['hull']
 for got,want in zip(info['meshpoints'],meta['meshpoints']):
  assert got['name']==want['name']and np.allclose(got['position'],want['translation'],atol=2e-5);assert np.allclose(np.array(got['rotation']).reshape(3,3),Rotation.from_quat(want.get('rotation',[0,0,0,1])).as_matrix().T,atol=2e-5)
 source_hashes={};tex=OUT/'texture-sources'
 for p in tex.glob('*.png'):
  with(BUILD/('texture-'+p.stem+'.log')).open('w')as log:subprocess.run([str(WINE),str(MAIN/'.tools/texconv.exe'),'-f','BC7_UNORM','-y','-m','0','-nogpu','--single-proc','-o','Z:'+str(GAME/'textures'),'-bc','q','Z:'+str(p)],env=ENV,stdout=log,stderr=subprocess.STDOUT,check=True,timeout=300)
 for mat in m['materials']:
  kind=mat.removeprefix(NAME+'_');assert kind in ['top','side','wing','engine','glow'];mask='windows'if kind=='side'else'glow'if kind=='glow'else'';write(GAME/'mesh_materials'/(mat+'.mesh_material'),{'version':1,'base_color_texture':f'expanse25_unone_{kind}_clr','occlusion_roughness_metallic_texture':'expanse25_unone_orm','normal_texture':'expanse10_donnager_flat_nrm','mask_texture':'expanse25_unone_'+(mask+'_'if mask else'')+'msk','emissive_factor':.6})
 normal=BASE/'textures/expanse10_donnager_flat_nrm.dds';(GAME/'textures'/normal.name).write_bytes(normal.read_bytes());source_hashes[str(normal)]=sha(normal)
 # The model has two rear lobes; effect is attached once per named exhaust point.
 plume_source=BASE/'effects/expanse15_truman_idle_plume.particle_effect';plume=read(plume_source)
 for node in plume['nodes']:
  for key in ['x','y','z']:
   if key in node:node[key]=[v*.12 for v in node[key]]
 for emitter in plume['emitters']:
  if 'forward_velocity'in emitter:emitter['forward_velocity']=[v*.12 for v in emitter['forward_velocity']]
  billboard=emitter['particle'].get('billboard',{})
  for key in ['width','height']:
   if key in billboard:billboard[key]=[v*.12 for v in billboard[key]]
 write(GAME/'effects/expanse25_unone_idle_plume.particle_effect',plume);source_hashes[str(plume_source)]=sha(plume_source)
 meta['skin_contract']={'unit_mesh':{'mesh':NAME,'shader':'ship','is_shadow_blocker':True},'exhaust_effects':{'particle_effects':[{'particle_effect':'expanse25_unone_idle_plume'}]},'notes':'Two actual engine-face origins; no weapons or child aliases. Idle plume only. Main may use normal hyperspace effects; do not reuse a multi-engine absolute phase effect.'};meta['status']='OFFLINE COMPILED ART PASS; RUNTIME UNTESTED';meta['checks'].update(meshpoint_transforms_exact=True,source_frame_error=float(distance.max()),opposed_winding_triangles=opposed,initial_winding_flips=flips,only_tangent_bytes_repaired=True,official_triangle_grid_and_trailer_preserved=True);meta['source_game_hashes']=source_hashes;meta['files']={str(p.relative_to(GAME)):sha(p)for p in sorted(GAME.rglob('*'))if p.is_file()};meta['wine_prefix_used_in_place']=str(helper.PREFIX);meta['wine_prefix_copied']=False;write(AUD/'integration-spec.json',meta);print(meta['status'],flush=True)
def preview():
 from polish_ui import render
 path=GAME/'meshes'/(NAME+'.mesh');b=path.read_bytes();count=struct.unpack_from('<Q',b,53)[0];off=61;rows=[]
 for _ in range(count):
  vals=struct.unpack_from('<12f?',b,off);rows.append(vals[:-1]);off+=49+(8 if vals[-1]else 0)
 rows=np.array(rows);ic=struct.unpack_from('<Q',b,off)[0];off+=8;indices=np.frombuffer(b,dtype='<u4',count=ic,offset=off);info=read_mesh(path);parts=[]
 for p in info['primitives']:
  idx=indices[p['vertex_index_start']:p['vertex_index_start']+p['vertex_index_count']].reshape(-1,3);mat=read(GAME/'mesh_materials'/(info['materials'][p['material_index']]+'.mesh_material'));tex=np.asarray(Image.open(GAME/'textures'/(mat['base_color_texture']+'.dds')).convert('RGBA'));parts.append((rows[:,:3][idx],rows[:,10:12][idx],tex,[1,1,1,1],'OPAQUE'))
 B=np.array([[.8,0,.6],[-.3,.866,.4],[.52,.5,-.693]]);render(parts,(1400,1000),B).save(AUD/'compiled-game-aft-preview.png');render(parts,(1400,1000),B@np.diag([-1,1,-1])).save(AUD/'compiled-game-bow-preview.png');render(parts,(1300,1300),np.array([[1,0,0],[0,0,-1],[0,1,0]])).save(AUD/'compiled-game-top-preview.png');print('Preview uses packaged game mesh/DDS, not runtime.')
if __name__=='__main__':
 parser=argparse.ArgumentParser();parser.add_argument('stage',choices=['prepare','compile','preview']);args=parser.parse_args();globals()[args.stage]()
