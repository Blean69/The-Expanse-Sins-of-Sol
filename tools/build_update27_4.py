"""Hephaestus/station load repair and Murphy drive, with menu quarantined."""
import json,shutil
from common import ROOT,GAME,read,write,read_mesh
from validate_experiments import require,sha256,file_hashes
from doctrine_package import package
from build_update27_3 import stage
from update27_3_loadfixes import check
from update21_factions import FACTIONS,WRAPPERS
from update27_1_runtime import get
BASE=ROOT/'build/experiments/expanse_update27_3';OUT=ROOT/'build/experiments/expanse_update27_4';AUD=ROOT/'audit/update27_4';DOC=ROOT/'docs/update27_4.md'

def build():
    require(not OUT.with_suffix('.zip').exists(),'Candidate frozen')
    edits={};fixed=[]
    for p in (BASE/'entities').glob('*.unit'):
        d=read(p);changed=False
        if d.get('ai_attack_target',{}).get('attack_target_type')=='capital_supercapital_heavy':
            require(p.stem=='expanse27_hephaestus','Unexpected target-type consumer');d['ai_attack_target']['attack_target_type']='heavy';changed=True;fixed.append({'unit':p.stem,'field':'ai_attack_target.attack_target_type','before':'capital_supercapital_heavy','after':'heavy'})
        ui=d.get('user_interface',{})
        if ui.get('can_be_controlled_by_selected_planet') and not any(k in d for k in ['carrier','unit_factory','exotic_factory','trade_port']):
            ui['can_be_controlled_by_selected_planet']=False;changed=True;fixed.append({'unit':p.stem,'field':'user_interface.can_be_controlled_by_selected_planet','after':False})
        if p.stem=='expanse_donnager_battleship':
            require(d['build']['prerequisites']==[['trader_unlock_loyalist_titan'],['trader_unlock_rebel_titan']],'Donnager predecessor drift');d['build']['prerequisites']=[['trader_unlock_loyalist_titan']];changed=True;fixed.append({'unit':p.stem,'field':'build.prerequisites','removed_unused_foreign_branch':'trader_unlock_rebel_titan'})
        if changed:edits['entities/'+p.name]=d
    art={};replacements={};artdir=ROOT/'build/update27_4-murphy/game'
    for p in artdir.rglob('*'):
        if not p.is_file():continue
        rel=str(p.relative_to(artdir))
        if (BASE/rel).exists() and sha256(BASE/rel)==sha256(p):continue
        art[rel]=p
        if (BASE/rel).exists():replacements[rel]=sha256(BASE/rel)
    require('meshes/expanse23_murphy_hull.mesh' in art,'Missing Murphy repair')
    source=read_mesh(BASE/'meshes/expanse23_murphy_hull.mesh');revised=read_mesh(art['meshes/expanse23_murphy_hull.mesh'])
    import numpy as np
    for a,b in zip(source['meshpoints'],revised['meshpoints']):
        require(a['name']==b['name'] and np.allclose(a['position'],b['position'],atol=2e-5) and np.allclose(a['rotation'],b['rotation'],atol=2e-5),'Murphy hardpoint moved')
    require(len(source['meshpoints'])==len(revised['meshpoints']),'Murphy hardpoint count changed')
    md=read(AUD/'murphy-drive.json');unit=read(BASE/'entities/expanse23_murphy.unit');box=unit['spatial']['box'];lo=np.array(box['center'])-box['extents'];hi=np.array(box['center'])+box['extents'];require(np.all(np.array(md['bounds_min'])>=lo-.001) and np.all(np.array(md['bounds_max'])<=hi+.001),'Drive exceeds existing bounds')
    meta=read(BASE/'.mod_meta_data');meta.update(display_version='0.27.4',display_name='The Expanse — 0.27.4 Hephaestus Repair',short_description='Hephaestus target type, station controls, Donnager prerequisite and Murphy Epstein drive.',long_description='Standalone repair over regular 0.27.3. Corrects confirmed load errors and replaces Murphy printed drive stub. No custom menu scene. Fleet combat numbers, prices and research costs unchanged. Pella debug-spawn GUI failure remains unconfirmed; runtime retest required. Enable alone.')
    edits['.mod_meta_data']=meta;stage(BASE,OUT,edits,art,DOC)
    refs=[]
    for owner in {**{v:k for k,v in FACTIONS.items()},**WRAPPERS}:
        d=get(OUT,'entities/'+owner+'.player');known=set(d['research']['research_subjects']+d['research'].get('faction_research_subjects',[]))
        for n in d['buildable_units']+d['structures']:
            u=get(OUT,'entities/'+n+'.unit');wanted={r for branch in u.get('build',{}).get('prerequisites',[]) for r in branch};require(wanted<=known,'Foreign procurement prerequisite '+owner+':'+n);refs.append([owner,n])
    require(not (OUT/'scenarios/front_end.scenario').exists(),'Failed menu shipped in control')
    before=file_hashes(BASE);after=file_hashes(OUT)
    for rel in before:
        if rel.endswith(('.weapon','.ability','.buff','.action_data_source','.research_subject','.player','.unit_skin')):require(before[rel]==after[rel],'Combat/research/faction mutation '+rel)
    write(AUD/'acceptance-check.json',{**check(OUT),'crash_reproduction':'NOT RUN; Pella empty-resource fault remains unlocalized','confirmed_definition_fixes':fixed,'owner_procurement_pairs_checked':len(refs),'new_drive_triangles':md['drive_triangles'],'murphy_weapon_exhaust_hardpoints_preserved':True,'murphy_existing_spatial_bounds_contain_drive':True,'menu':'NOT INCLUDED; 0.27.3 menu failed user test','pella_gui':'Serialized GUI and dependencies exist; no proven correction to debug-spawn empty-resource fault.','runtime':'NOT RUN'})
    result=package(BASE,OUT,edits,{},DOC,AUD,art,package_existing=True,art_replacements=replacements);print(json.dumps(result,indent=2))
if __name__=='__main__':build()
