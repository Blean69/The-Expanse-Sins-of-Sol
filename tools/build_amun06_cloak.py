"""Separate full cloak experiment; explicitly partial official schema coverage."""
import argparse,copy,json,shutil,zipfile
from pathlib import Path
from build_amun06 import ROOT,SHIP,manifests,frozen
from build_polish import write
from validate_experiments import read,require,file_hashes,verify_zip,provenance
from amun06_behavior import validate_components
from amun06_behavior_validate import validate_cloak_candidate
from amun06_validate_package import AmunResolver,check_action_values
from build_combat03 import check_actions

def main(a):
    frozen(a.game,a.sdk)
    core=ROOT/'build/experiments/expanse_amun06';out=core.with_name('expanse_amun06_cloak')
    require(read(ROOT/'audit/amun06/package-validation.json')['status']=='PASS OFFLINE ONLY','Core must pass first')
    core_zip=verify_zip(core.with_suffix('.zip'),core)
    recipe=read(a.behavior/'integration-recipe.json')['optional_cloak']
    expected=read(core/'entities'/f'{SHIP}.unit');expected['abilities'][0]['abilities'].extend(recipe['append_ship_abilities']);expected.update(recipe['unit_hook'])
    loc=read(core/'localized_text/en.localized_text');loc.update(read(a.behavior/'cloak/localization.json'))
    if not a.validate_only:
        require(not out.exists() and not out.with_suffix('.zip').exists(),'Refusing existing cloak experiment')
        shutil.copytree(core,out)
        for p in (a.behavior/'cloak/entities').iterdir():shutil.copy2(p,out/'entities'/p.name)
        write(out/'entities'/f'{SHIP}.unit',expected);write(out/'localized_text/en.localized_text',loc);manifests(out,a.game)
        meta=read(core/'.mod_meta_data');meta.update(display_name='The Expanse — Amun-Ra 0.6 CLOAK EXPERIMENT',short_description='Optional installed-Eidolon cloak plus combat and timed boarding.',long_description='Load this complete variant alone. Requires the installed Harbinger product gate. Cloak fields use explicit supplemental installed-data checks; official schema coverage is partial. Fourth individual torpedo or successful PDC/rail hit starts a fixed 60-second reveal. Missed gun shots do not reveal. Runtime testing pending.')
        write(out/'.mod_meta_data',meta)
    require(read(out/'entities'/f'{SHIP}.unit')==expected,'Unreviewed cloak unit change')
    require(read(out/'localized_text/en.localized_text')==loc,'Unreviewed cloak localization')
    allowed={'.mod_meta_data','entities/'+SHIP+'.unit','localized_text/en.localized_text'}|{'entities/'+e+'.entity_manifest' for e in ['ability','buff','action_data_source']}
    before=file_hashes(core);after=file_hashes(out)
    require(not set(before)-set(after),'Removed core files')
    for p,h in before.items():
        if p not in allowed:require(after[p]==h,'Core drift: '+p)
    require(set(after)-set(before)=={'entities/'+x for x in recipe['files']},'Unexpected optional files')
    for ext in ['unit','unit_skin','weapon','ability','buff','action_data_source']:
        ids=sorted(p.stem for p in (out/'entities').glob('*.'+ext) if not (a.game/'entities'/p.name).exists())
        require(read(out/'entities'/(ext+'.entity_manifest'))=={'ids':ids},'Incorrect optional manifest '+ext)
    behavior=validate_components(out,a.behavior,a.sdk,cloak=True,boarding_model=True)
    supplemental=validate_cloak_candidate(out/'entities',a.sdk,a.game,unit_definition=expected)
    resolver=AmunResolver(out,a.game);resolver.unit(SHIP,'optional package')
    graphs=check_actions(out,resolver,SHIP);values=check_action_values(out,a.game,resolver,expected)
    report={'status':supplemental['status'],'runtime':'NOT RUN','core_package':core_zip,'core_preserved_except_exact_cloak_additions':True,'behavior':behavior,'supplemental':supplemental,'actions':graphs,'values':values,'references':resolver.edges,'preservation':frozen(a.game,a.sdk)}
    write(ROOT/'audit/amun06/cloak-package-validation.json',report)
    if not a.validate_only:
        with zipfile.ZipFile(out.with_suffix('.zip'),'w',zipfile.ZIP_DEFLATED) as z:
            for p in sorted(out.rglob('*')):
                if p.is_file():
                    i=zipfile.ZipInfo(p.relative_to(out).as_posix(),(2026,9,12,0,0,0));i.compress_type=zipfile.ZIP_DEFLATED;i.external_attr=0o100644<<16;z.writestr(i,p.read_bytes())
    summary={'mod_id':out.name,**verify_zip(out.with_suffix('.zip'),out),'runtime':'NOT RUN','installed':False,'schema_coverage':'PARTIAL OFFICIAL; strict installed-extension checks passed'}
    write(ROOT/'audit/amun06/cloak-package-summary.json',summary)
    deps=[core,a.behavior,ROOT/'audit/amun06/checkpoint.json'];write(out.with_suffix('.dependencies.json'),[str(p) for p in deps]);write(out.with_suffix('.provenance.json'),provenance(out.with_suffix('.zip'),ROOT,deps));print(json.dumps(summary,indent=2))

if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__)
    for k in ['game','sdk','behavior']:p.add_argument('--'+k,type=Path,required=True)
    p.add_argument('--validate-only',action='store_true');main(p.parse_args())
