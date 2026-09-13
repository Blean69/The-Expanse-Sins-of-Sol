"""Correct alternative ability sets; append six normalized Rocinante recordings."""
import argparse,copy,json,shutil,zipfile
from pathlib import Path
import jsonschema
import build_voice07 as audio
from build_polish import write
from validate_experiments import read,require,file_hashes,sha256,verify_zip,provenance,compare_tree,verify_pins
from amun06_validate_package import AmunResolver,check_action_values,check_boarding
from amun06_behavior_validate import validate_cloak_candidate
from build_combat03 import check_actions

ROOT=Path(__file__).resolve().parents[1];AUDIT=ROOT/'audit/update08';GAME=audio.GAME;SDK=audio.SDK
CLIPS=[('easy_partner','easy-there-partner.wav','order_issued','neutral'),('donkey_balls','donkey-balls.wav','selected','neutral'),('donkey_reply','did-you-just-say-donkey-balls.wav','selected','neutral'),('debris_field','debris-field-buckle-up.wav','order_issued','neutral'),('pursuit','damn-straight-do-not-lose-that-ship.wav','attack_order_issued','smug'),('drill','could-you-pass-me-the-drill.wav','selected','neutral')]
GENERATED=ROOT/'build/voice08/game';ORIGINAL=ROOT/'assets/original/voice08';EDITABLE=ROOT/'assets/derived/voice08/normalized-wav'

def extra_dialogue():
    d={}
    for ident,_,cat,mood in CLIPS:d.setdefault(cat,{}).setdefault(mood,[]).append('expanse08_roci_'+ident)
    d['attack_order_issued']['neutral']=list(d['attack_order_issued']['smug'])
    return d

def configure_audio():
    audio.ORIGINAL=ORIGINAL;audio.EDITABLE=EDITABLE;audio.GENERATED=GENERATED;audio.AUDIT=AUDIT;audio.CLIPS=CLIPS
    audio.VOICE_PREFIX='expanse08_roci_';audio.LIMITER_ROOT=ROOT/'build/voice08/limiter-attempts';audio.dialogue=extra_dialogue

def check_single_set(unit,expected):
    require(unit['abilities']==[{'abilities':expected}],'Abilities must coexist in one unconditional set; separate entries are alternatives')
    require(len(expected)==len(set(expected)),'Repeated ability definition')

def corrected_unit(original):
    result=copy.deepcopy(original);groups=original['abilities']
    require(all(set(g)=={'abilities'} for g in groups),'Refusing to flatten conditional player/special-operation ability sets')
    names=[name for g in groups for name in g['abilities']]
    result['abilities']=[{'abilities':names}];check_single_set(result,names);return result

def skin_with_more_voice(base):
    result=copy.deepcopy(base);d=result['skin_stages'][0]['sounds']['dialogue']
    for category,moods in extra_dialogue().items():
        for mood,names in moods.items():d.setdefault(category,{}).setdefault(mood,[]).extend(names)
    return result

def boarding_ui(base):
    result=copy.deepcopy(base);stock=read(GAME/'entities/pirate_boarding_crew.ability')['gui']
    result['gui']['targeting']=stock['targeting'];result['gui']['tooltip_picture']=stock['tooltip_picture'];return result

def localized(base,cloak):
    d=copy.deepcopy(base)
    d['expanse06_amun_magazine.description']='Eight torpedoes. Launches two every 10 seconds while an eligible target is available; reloads for 120 seconds after the last pair.'
    d['expanse06_amun_boarding.name']='Launch boarding pod'
    d['expanse06_amun_boarding.description']='Target an enemy capital ship within range. A timed pod visual is followed by one 10% capture attempt after 3 seconds. Requires enough free fleet supply for the target. Cooldown: 180 seconds. The visual pod cannot be intercepted.'
    if cloak:d['expanse06_amun_cloak.name']='Activate cloak'
    return d

def audio_checks():
    d=read(AUDIT/'audio-intake.json');require(len(d['records'])==6,'Expected six new clips')
    for x in d['records']:
        for key in ['source','original']:require(sha256(x[key])==x['sha256'],'Original audio changed')
        require(sha256(x['normalized_wav'])==x['wav_sha256'],'Normalized WAV drift')
        require(sha256(x['ogg'])==x['ogg_sha256'],'Ogg drift')
        require(abs(float(x['output_measurement']['input_i'])+18)<=.6 and float(x['output_measurement']['input_tp'])<=-1.5,'Audio measurement gate failed')
    require(file_hashes(GENERATED)==read(AUDIT/'generated-hashes.json'),'Generated media drift')

def validate(out,base,cloak):
    old=file_hashes(base);new=file_hashes(out)
    allowed={'.mod_meta_data','ASSET-SOURCES.md','localized_text/en.localized_text','entities/expanse_amun_ra.unit','entities/expanse_rocinante_hero.unit','entities/expanse_rocinante_hero.unit_skin','entities/expanse06_amun_boarding.ability'}
    require(not set(old)-set(new),'Base files removed')
    for p,h in old.items():
        if p not in allowed:require(new[p]==h,'Unrelated change '+p)
    require(set(new)-set(old)==set(read(AUDIT/'generated-hashes.json')),'Unexpected new files')
    resolver=AmunResolver(out,GAME);unitchecks={}
    for name in ['expanse_amun_ra','expanse_rocinante_hero']:
        unit=read(out/'entities'/(name+'.unit'));original=read(base/'entities'/(name+'.unit'))
        require(unit==corrected_unit(original),'Unit change exceeds ability-set correction')
        known=copy.deepcopy(unit);require(known.pop('corruption')==read(GAME/'entities/trader_light_frigate.unit')['corruption'],'Inherited corruption differs from installed Cobalt')
        known.pop('cloak_ability',None)
        schema=read(SDK/'json_schemas/unit-schema.json');jsonschema.Draft7Validator(schema).validate(known);jsonschema.Draft202012Validator(schema).validate(known)
        resolver.unit(name,'corrected ability set');check_actions(out,resolver,name);check_action_values(out,GAME,resolver,unit)
        for aid in unit['abilities'][0]['abilities']:
            ability=read(out/'entities'/(aid+'.ability'));require('gui'in ability and ability['gui']['hud_icon'],'Missing ability GUI')
            jsonschema.Draft7Validator(read(SDK/'json_schemas/ability-schema.json')).validate(ability)
        unitchecks[name]=unit['abilities']
    skinpath='entities/expanse_rocinante_hero.unit_skin';skin=read(out/skinpath)
    require(skin==skin_with_more_voice(read(base/skinpath)),'Unexpected hero skin change')
    jsonschema.Draft202012Validator(read(SDK/'json_schemas/unit-skin-schema.json')).validate(skin)
    for moodset in skin['skin_stages'][0]['sounds']['dialogue'].values():
        for names in moodset.values():
            for name in names:
                p=out/'sounds'/(name+'.sound');require(read(p)==read(GAME/'sounds/trader_light_frigate_selected_neutral_0.sound'),'Unexpected speech profile');require(p.with_suffix('.ogg').is_file(),'Missing voice media')
    for p,h in read(AUDIT/'generated-hashes.json').items():require(new[p]==h,'New packaged audio mismatch')
    require(read(out/'entities/expanse06_amun_boarding.ability')==boarding_ui(read(base/'entities/expanse06_amun_boarding.ability')),'Boarding behavior changed')
    require(read(out/'localized_text/en.localized_text')==localized(read(base/'localized_text/en.localized_text'),cloak),'Unexpected localization change')
    boarding=check_boarding(out,resolver);optional=validate_cloak_candidate(out/'entities',SDK,GAME,unit_definition=read(out/'entities/expanse_amun_ra.unit')) if cloak else {'present':False}
    if not cloak:require('cloak_ability'not in read(out/'entities/expanse_amun_ra.unit'),'Cloak leaked into fallback')
    audio_checks()
    return {'status':'PASS OFFLINE ONLY','runtime':'NOT RUN','expected_single_sets':unitchecks,'boarding':boarding,'cloak':optional,'only_changed_existing_files':sorted(allowed),'new_voice_files':12,'preserved_gameplay_values':True,'references':resolver.edges,'preservation':audio.preservation()}

def regression():
    cases=[]
    for suffix in ['','_cloak']:
        base=ROOT/'build/experiments'/('expanse_amun06'+suffix+'_voice07')
        for name in ['expanse_amun_ra','expanse_rocinante_hero']:
            old=read(base/'entities'/(name+'.unit'));fixed=corrected_unit(old);names=fixed['abilities'][0]['abilities']
            rejected=False
            try:check_single_set(old,names)
            except ValueError:rejected=True
            require(rejected,'Regression must reject shipped multiple unconditional alternatives');check_single_set(fixed,names)
            cases.append({'base':base.name,'unit':name,'old_separate_sets':'REJECT','corrected_single_set':'PASS'})
    conditional=read(GAME/'entities/trader_orbital_cannon_structure.unit');rejected=False
    try:corrected_unit(conditional)
    except ValueError:rejected=True
    require(rejected,'Must not flatten legitimate conditional vanilla groups')
    write(AUDIT/'regression.json',{'status':'PASS','cases':cases,'conditional_groups_protected':True,'runtime':'NOT RUN'})

def main(a):
    configure_audio();audio.preservation()
    if a.normalize:audio.intake_and_normalize();return
    audio_checks();regression();summaries=[]
    for suffix,label in [('_cloak','CLOAK + BOARDING'),('','COMBAT + BOARDING')]:
        base=ROOT/'build/experiments'/('expanse_amun06'+suffix+'_voice07');out=ROOT/'build/experiments'/('expanse_amun08'+suffix)
        if not a.validate_only:
            require(not out.exists() and not out.with_suffix('.zip').exists(),'Refusing existing update08 package')
            shutil.copytree(base,out)
            for name in ['expanse_amun_ra','expanse_rocinante_hero']:
                p=out/'entities'/(name+'.unit');write(p,corrected_unit(read(p)))
            p=out/'entities/expanse_rocinante_hero.unit_skin';write(p,skin_with_more_voice(read(p)))
            p=out/'entities/expanse06_amun_boarding.ability';write(p,boarding_ui(read(p)))
            p=out/'localized_text/en.localized_text';write(p,localized(read(p),bool(suffix)))
            for p in GENERATED.rglob('*'):
                if p.is_file():shutil.copy2(p,out/p.relative_to(GENERATED))
            meta=read(out/'.mod_meta_data');meta.update(display_name='The Expanse — 0.8 '+label+' + 17 Rocinante voices',display_version='0.8.0',short_description='Corrected ship ability sets and six more normalized voice lines.',long_description='Load this complete variant alone. Corrects Amun/Rocinante ability registration; preserves fleet supply and combat values. Boarding is a manual targeted ability with one timed 10% capture attempt. '+('Includes experimental native cloak; requires Harbinger product gate. ' if suffix else 'No cloak in this fallback. ')+'Contains 17 normalized Rocinante lines. New ability visibility and behavior need runtime testing.');write(out/'.mod_meta_data',meta)
            (out/'ASSET-SOURCES.md').write_text((base/'ASSET-SOURCES.md').read_text()+'\n'+(AUDIT/'asset-source-record.md').read_text())
        report=validate(out,base,bool(suffix));write(AUDIT/(out.name+'-validation.json'),report)
        if not a.validate_only:
            with zipfile.ZipFile(out.with_suffix('.zip'),'w',zipfile.ZIP_DEFLATED)as z:
                for p in sorted(out.rglob('*')):
                    if p.is_file():
                        i=zipfile.ZipInfo(p.relative_to(out).as_posix(),(2026,9,12,0,0,0));i.compress_type=zipfile.ZIP_DEFLATED;i.external_attr=0o100644<<16;z.writestr(i,p.read_bytes())
        result={'mod_id':out.name,**verify_zip(out.with_suffix('.zip'),out),'installed':False,'runtime':'NOT RUN'};summaries.append(result)
        deps=[base,ORIGINAL,EDITABLE,GENERATED];write(out.with_suffix('.dependencies.json'),[str(x)for x in deps]);write(out.with_suffix('.provenance.json'),provenance(out.with_suffix('.zip'),ROOT,deps))
    write(AUDIT/'package-summary.json',summaries);print(json.dumps(summaries,indent=2))

if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--normalize',action='store_true');p.add_argument('--validate-only',action='store_true');main(p.parse_args())
