"""Separately frozen cumulative balance candidates; never install or launch."""
from pathlib import Path
import copy,json,subprocess
from common import ROOT,GAME,read,write
from validate_experiments import require,file_hashes,sha256,tree_hash
from doctrine_package import package
from build_update27_3 import stage
from update27_3_loadfixes import check
BASE=ROOT/'build/experiments/expanse_update27_5_menu'
AUD=ROOT/'audit/balance28'

def differences(a,b,path=''):
    if isinstance(a,dict) and isinstance(b,dict):
        return sum((differences(a.get(k),b.get(k),path+'/'+k) for k in sorted(set(a)|set(b))),[])
    if isinstance(a,list) and isinstance(b,list) and len(a)==len(b):
        return sum((differences(x,y,path+'/'+str(i)) for i,(x,y) in enumerate(zip(a,b))),[])
    return [] if a==b else [{'path':path,'before':a,'after':b}]

def check_candidate(out,base,edits):
    report=check(out);report['crash_reproduction']='NOT RUN for this candidate; historical user test of 0.27.5 is baseline evidence only.'
    old=file_hashes(BASE);new=file_hashes(out)
    preserved=[r for r in old if r.startswith(('meshes/','textures/','sounds/','scenarios/')) or r.endswith(('.ogg','.sound'))]
    for rel in preserved:require(old[rel]==new[rel],'Unrelated audiovisual/menu drift '+rel)
    for p in (out/'entities').glob('expanse_menu*.unit'):
        require(sha256(p)==sha256(BASE/'entities'/p.name),'Menu display hull changed '+p.name)
    from balance28_access import PLAYERS,BATTERY
    access={}
    for pid in PLAYERS:
        p=read(out/'entities'/f'{pid}.player');known=set(p['research']['research_subjects'])
        u=read(out/'entities'/f'{BATTERY}.unit')
        require(BATTERY in p['structures'],'Battery missing construction menu '+pid)
        branches=u['build']['prerequisites'];available=[branch for branch in branches if set(branch)<=known]
        require(available,'Battery hidden behind foreign research '+pid)
        for branch in available:
            for subject in branch:
                n=read(out/'entities'/f'{subject}.research_subject')
                require(any(set(b)<=known for b in n.get('prerequisites',[[]])),'Unreachable battery prerequisite '+pid)
        require([x['unit_limit'] for x in p['unit_limits']['planet'] if x['tag']==BATTERY]==[2],'Battery cap bucket drift '+pid)
        require(p['max_supply']==read(BASE/'entities'/f'{pid}.player')['max_supply'],'Supply target changed '+pid)
        require(p['research']['research_domains']['civilian']==read(BASE/'entities'/f'{pid}.player')['research']['research_domains']['civilian'],'Civilian domain altered '+pid)
        access[pid]=available
    report['battery_access_branches']=access
    report['preserved_audio_art_scenario_files']=len(preserved)
    report['numeric_changes']={r:differences(read(base/r),d) if (base/r).exists() else [{'path':'','before':None,'after':d}] for r,d in edits.items() if r.endswith(('.unit','.weapon','.research_subject'))}
    report['runtime']='NOT RUN: no game launched or installed'
    return report

def freeze(label,base,edits,origins,details):
    out=ROOT/'build/experiments'/('expanse_balance28_'+label);audit=AUD/label;doc=ROOT/'docs'/('balance28_'+label+'.md')
    require(not out.with_suffix('.zip').exists(),'Candidate already frozen '+label)
    edits=copy.deepcopy(edits)
    meta=read(base/'.mod_meta_data');meta.update(display_version='0.28-'+label,display_name='The Expanse — 0.28 '+label,short_description='Targeted Martian Quality balance candidate; preserved Expanse fleet menu.',long_description='Cumulative offline-checked candidate. Fresh games only. See PLAYTEST-README for exact scope and known limitations. Runtime testing is not performed by the build process.')
    edits['.mod_meta_data']=meta
    doc.parent.mkdir(exist_ok=True)
    doc.write_text('# The Expanse 0.28 — '+label+'\n\n'+details+'\n\n## Evidence and limits\n\nBaseline: user-confirmed 0.27.5 Finished Fleet Menu, source `8e55e93550b938e0dc62508a9ee8c6ac350332d4`, ZIP SHA-256 `98ca0c15b7ff6e9eaa09b0a5d96774da039bc39d39d6496ba6a2536bea8ccfbc`. Installed baseline matched all 2,285 files. Rollback retained unchanged.\n\nThis candidate has **offline validation only**. Game loading, cap/queue/capture behavior, weapon geometry, damage timing, save/reload, existing/new research effects and multiplayer comparisons are **NOT RUN**. Fresh games are the supported test. No install, enable, publish, push or game launch was performed.\n\nModels, audio, menu scene, civilian economy and unrelated faction features are preserved. No generic shields or protomolecule plating added by this targeted increment.\n',encoding='utf-8')
    stage(base,out,edits,{},doc)
    report=check_candidate(out,base,edits);write(audit/'acceptance.json',report)
    replacements={}
    for rel,d in edits.items():
        if (base/rel).exists() and ((rel.endswith('.weapon') and 'rail' in rel) or 'magazine' in rel or ('torpedo' in rel and rel.endswith('.unit'))):
            delta=differences(read(base/rel),d)
            if delta:replacements[rel]={'before_sha256':sha256(base/rel),'changed_paths':[x['path'] for x in delta],'reason':'Active Martian Quality brief and explicit PDC/rail range override; complete values in acceptance.json.'}
    source={p.relative_to(ROOT).as_posix():sha256(p) for p in (ROOT/'tools').glob('*28*.py')}
    write(audit/'source.json',{'git_base':subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),'implementation_files':source,'runtime':'NOT RUN'})
    result=package(base,out,edits,origins,doc,audit,package_existing=True,balance_replacements=replacements)
    print(label,json.dumps(result),flush=True)
    return out,result

if __name__=='__main__':
    import sys
    if sys.argv[1]=='A':
        from balance28_economics import changes as economics
        from balance28_access import changes as access
        e,o,r=economics(BASE);e,oa,ra=access(BASE,e);o.update(oa)
        write(AUD/'A-economics.json',r);write(AUD/'A-access.json',ra)
        details=(AUD/'A-description.md').read_text()
        freeze('A',BASE,e,o,details)
    elif sys.argv[1] in ('B120','B95','B-tracking-control','C-cadence'):
        from balance28_weapons import changes as weapons
        label=sys.argv[1];stage_a=ROOT/'build/experiments/expanse_balance28_A'
        e,o,r=weapons(stage_a,BASE,tachi_supply=95 if label=='B95' else 120,
                      heavy_tracking=label!='B-tracking-control',donnager_cadence=label=='C-cadence')
        o={k:v['source'] for k,v in o.items()}
        write(AUD/label/'weapon-proposal.json',r)
        details=(AUD/'B-description.md').read_text()
        if label=='B95':details='**Supply control:** Tachi remains 95 supply; all other B changes match B120. Four ships cost 380 supply.\n\n'+details
        elif label=='B-tracking-control':details='**Tracking control:** original heavy tracking speeds retained; all other B120 changes apply.\n\n'+details
        elif label=='C-cadence':details='**Optional comparison only; not the recommended baseline.** Same as B120, except both Donnager heavy guns reload in 24 seconds instead of 30. Unchanged first volley; theoretical sustained throughput rises 25%. Gameplay comparison has NOT RUN. Use only after the A/B checks.\n\n'+details
        freeze(label,stage_a,e,o,details)
