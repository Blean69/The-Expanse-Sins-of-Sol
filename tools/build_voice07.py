"""Local normalized Rocinante dialogue variants; originals and existing mods read-only."""
from pathlib import Path
import argparse,copy,json,math,shutil,subprocess,zipfile
import jsonschema
from validate_experiments import read,require,sha256,file_hashes,compare_tree,verify_pins,verify_zip,provenance
from build_polish import write

ROOT=Path(__file__).resolve().parents[1]
DRIVE=ROOT.parent
GAME=DRIVE/'SteamLibrary/steamapps/common/Sins2'
SDK=DRIVE/'SteamLibrary/steamapps/common/Sins of a Solar Empire II - Mod Tools'
ORIGINAL=ROOT/'assets/original/voice07'
EDITABLE=ROOT/'assets/derived/voice07/normalized-wav'
GENERATED=ROOT/'build/voice07/game'
AUDIT=ROOT/'audit/voice07'
CLIPS=[
 ('retreat','cut-out-the-computer-cores-it-s-time-to-leave.wav','retreat','scared'),
 ('mars_navy','i-flew-with-the-mars-navy-for-20-years.wav','selected','neutral'),
 ('asteroid_ride','we-re-gonna-take-em-for-a-ride-alex-go-around-the-asteroid.wav','attack_order_issued','smug'),
 ('antenna','the-antenna-array-up-top-has-seen-better-days.wav','armor_down','neutral'),
 ('xo_held','hey-hey-you-seen-the-xo.wav',None,None),
 ('enemy_railguns','shit-i-think-they-re-diverting-power-to-the-rail-guns.wav','attack_order_issued','scared'),
 ('thanks','in-the-case-i-have-to-kill-you-i-just-wanted-to-say-thanks.wav','attack_order_issued','smug'),
 ('juice_long','here-comes-the-juice (1).wav','hyperspace_charge_started','neutral'),
 ('captain','captain-of-the-rocinante.wav','spawned','neutral'),
 ('freighter_joke','the-only-way-this-ship-ll-pass-for-a-freighter-is-if-no-one-looks-close-enough.wav','selected','neutral'),
 ('good_news','avasarala-you-ll-get-the-good-news-in-short-order.wav','order_issued','neutral'),
 ('churn','welcome-to-the-churn.wav','attack_order_issued','smug'),
]
TARGET=-18.0;PEAK=-2.5
VOICE_PREFIX='expanse07_roci_'
LIMITER_ROOT=ROOT/'build/voice07/limiter-attempts'

def run(args):
    p=subprocess.run(args,capture_output=True,text=True)
    require(p.returncode==0,'Command failed: '+repr(args)+'\n'+p.stderr)
    return p

def probe(p):
    return json.loads(run(['ffprobe','-v','error','-show_streams','-show_format','-of','json',str(p)]).stdout)

def measure(p):
    result=run(['ffmpeg','-hide_banner','-nostats','-i',str(p),'-af',f'aformat=channel_layouts=mono,loudnorm=I={TARGET}:TP={PEAK}:LRA=11:print_format=json','-f','null','-'])
    report=json.loads(result.stderr[result.stderr.rfind('{'):result.stderr.rfind('}')+1])
    require(all(math.isfinite(float(report[k])) for k in ['input_i','input_tp','input_lra','input_thresh','target_offset']),'Cannot measure usable loudness: '+str(p))
    return report

def preservation():
    d=read(AUDIT/'checkpoint.json')
    trees=[compare_tree(x)for x in d['trees']]
    for p,h in d['zips'].items():require(sha256(p)==h,'Existing ZIP changed: '+p)
    return {'trees':trees,'zips_unchanged':len(d['zips']),'pins':verify_pins(ROOT,GAME,SDK)}

def dialogue():
    d={}
    for ident,filename,category,mood in CLIPS:
        if category:d.setdefault(category,{}).setdefault(mood,[]).append('expanse07_roci_'+ident)
    d['selected']['neutral'].insert(0,'expanse07_roci_captain')
    # Ordinary-state responses remain available; retain the requested scared/smug pools.
    # No assumption about fallback between missing moods or invented probability fields.
    d['retreat']['neutral']=list(d['retreat']['scared'])
    d['attack_order_issued']['neutral']=list(d['attack_order_issued']['smug'])
    return d

def intake_and_normalize():
    require(not EDITABLE.exists() and not GENERATED.exists(),'Fresh derivative required; use --package-only for reviewed existing audio')
    for _,name,_,_ in CLIPS:require((Path('/home/haker/Downloads')/name).is_file(),'Missing supplied audio; normalization NOT RUN: '+name)
    ORIGINAL.mkdir(parents=True,exist_ok=True);EDITABLE.mkdir(parents=True);(GENERATED/'sounds').mkdir(parents=True)
    profile=read(GAME/'sounds/trader_light_frigate_selected_neutral_0.sound')
    require(profile=={'is_positionable':False,'is_looping':False,'is_streaming':True},'Re-audit changed stock voice profile')
    records=[]
    for ident,name,category,mood in CLIPS:
        source=Path('/home/haker/Downloads')/name;original=ORIGINAL/name
        if not original.exists():shutil.copy2(source,original)
        record={'id':ident,'source':str(source),'original':str(original),'sha256':sha256(source),'probe':probe(original),'category':category,'mood':mood,'status':'HELD for another ship' if not category else 'PENDING'}
        require(sha256(original)==record['sha256'],'Original copy mismatch')
        if category:
            first=measure(original);record['first_pass']=first
            wav=EDITABLE/(ident+'.wav');ogg=GENERATED/'sounds'/(VOICE_PREFIX+ident+'.ogg')
            filt=f"aformat=channel_layouts=mono,loudnorm=I={TARGET}:TP={PEAK}:LRA=11:measured_I={first['input_i']}:measured_TP={first['input_tp']}:measured_LRA={first['input_lra']}:measured_thresh={first['input_thresh']}:offset={first['target_offset']}:linear=true:print_format=json"
            r=run(['ffmpeg','-hide_banner','-nostats','-n','-i',str(original),'-map_metadata','-1','-af',filt,'-ar','44100','-ac','1','-c:a','pcm_s24le',str(wav)])
            record['second_pass']=json.loads(r.stderr[r.stderr.rfind('{'):r.stderr.rfind('}')+1])
            run(['ffmpeg','-hide_banner','-nostats','-n','-i',str(wav),'-map_metadata','-1','-c:a','libvorbis','-q:a','6',str(ogg)])
            measured=measure(ogg)
            if abs(float(measured['input_i'])-TARGET)>.6:
                # Short peak-heavy clips can be gain-limited by loudnorm. Apply an
                # explicit lookahead limiter, then remeasure the encoded result.
                attempts=LIMITER_ROOT/ident;attempts.mkdir(parents=True)
                wav.rename(attempts/'initial.wav');ogg.rename(attempts/'initial.ogg')
                gain=TARGET-float(first['input_i']);record['limiter_attempts']=[]
                for index in range(4):
                    candidate=attempts/(str(index)+'.wav');encoded=candidate.with_suffix('.ogg')
                    limit=10**(-3.0/20)
                    run(['ffmpeg','-hide_banner','-nostats','-n','-i',str(original),'-map_metadata','-1','-af',f'aformat=channel_layouts=mono,volume={gain}dB,alimiter=limit={limit}:attack=5:release=50:level=false:latency=true','-ar','44100','-ac','1','-c:a','pcm_s24le',str(candidate)])
                    run(['ffmpeg','-hide_banner','-nostats','-n','-i',str(candidate),'-map_metadata','-1','-c:a','libvorbis','-q:a','6',str(encoded)])
                    measured=measure(encoded);record['limiter_attempts'].append({'gain_db':gain,'sample_peak_limit_db':-3.0,'encoded_measurement':measured})
                    if abs(float(measured['input_i'])-TARGET)<=.6 and float(measured['input_tp'])<=-1.5:
                        shutil.copy2(candidate,wav);shutil.copy2(encoded,ogg);break
                    gain+=TARGET-float(measured['input_i'])
                require(ogg.exists(),'Peak-limited clip could not meet measured target: '+ident)
            output_probe=probe(ogg);s=output_probe['streams'][0]
            require(s['codec_name']=='vorbis' and s['sample_rate']=='44100' and s['channels']==1,'Wrong game voice encoding')
            require(abs(float(measured['input_i'])-TARGET)<=.6,'Loudness outside tolerance: '+ident)
            require(float(measured['input_tp'])<=-1.5,'Encoded true peak exceeds safety margin: '+ident)
            require(abs(float(output_probe['format']['duration'])-float(record['probe']['format']['duration']))<=.08,'Audio length unexpectedly changed: '+ident)
            write(ogg.with_suffix('.sound'),profile)
            record.update(status='PASS measured normalization; listening/runtime NOT RUN',normalized_wav=str(wav),wav_sha256=sha256(wav),ogg=str(ogg),ogg_sha256=sha256(ogg),output_measurement=measured,output_probe=output_probe)
        records.append(record);print(ident,record['status'],flush=True)
    write(AUDIT/'audio-intake.json',{'records':records,'target_lufs':TARGET,'normalizer_peak_dbtp':PEAK,'encoded_peak_limit_dbtp':-1.5,'lufs_tolerance':.6,'ffmpeg':run(['ffmpeg','-version']).stdout.splitlines()[0],'missing_optional_short_juice':'/home/haker/Downloads/here-comes-the-juice.wav','no_trimming_or_word_reconstruction':True,'source_rights':'User supplied recordings and requested local mod integration. Creator, upstream recording provenance, license and redistribution terms unspecified. Model permission is not applied to audio. No publishing.'})
    write(AUDIT/'generated-hashes.json',file_hashes(GENERATED))
    write(AUDIT/'dialogue-map.json',dialogue())

def verify_audio():
    audit=read(AUDIT/'audio-intake.json')
    for x in audit['records']:
        require(sha256(x['source'])==x['sha256'] and sha256(x['original'])==x['sha256'],'Supplied source changed: '+x['id'])
        if 'normalized_wav'in x:require(sha256(x['normalized_wav'])==x['wav_sha256'],'Editable normalized WAV drift')
    require(file_hashes(GENERATED)==read(AUDIT/'generated-hashes.json'),'Reviewed generated audio drift')
    return {'supplied':len(audit['records']),'normalized_and_encoded':sum('ogg'in x for x in audit['records']),'held':1,'missing_optional_short_juice':True}

def validate_package(out,base):
    old=file_hashes(base);new=file_hashes(out);skinpath='entities/expanse_rocinante_hero.unit_skin'
    allowed={skinpath,'.mod_meta_data','ASSET-SOURCES.md'}
    require(not set(old)-set(new),'Existing content removed')
    for p,h in old.items():
        if p not in allowed:require(new[p]==h,'Unrelated gameplay/model change: '+p)
    require(set(new)-set(old)==set(read(AUDIT/'generated-hashes.json')),'Unexpected added package files')
    skin=read(out/skinpath);expected=read(base/skinpath)
    expected['skin_stages'][0]['sounds']['dialogue']=dialogue();require(skin==expected,'Skin change exceeds exact voice map')
    schema=read(SDK/'json_schemas/unit-skin-schema.json')
    jsonschema.Draft7Validator(schema).validate(skin)
    jsonschema.Draft202012Validator(schema).validate(skin)
    references=[]
    profile=read(GAME/'sounds/trader_light_frigate_selected_neutral_0.sound')
    for category,moods in dialogue().items():
        for mood,names in moods.items():
            for name in names:
                sound=out/'sounds'/(name+'.sound');ogg=sound.with_suffix('.ogg')
                require(read(sound)==profile,'Sound profile differs from verified installed voice')
                require(ogg.is_file(),'Unresolved dialogue media '+name);references.append({'category':category,'mood':mood,'sound':name,'media':ogg.name})
    for p,h in read(AUDIT/'generated-hashes.json').items():require(new[p]==h,'Packaged audio differs from measured derivative')
    require((out/'ASSET-SOURCES.md').read_text()==(base/'ASSET-SOURCES.md').read_text()+'\n'+(AUDIT/'asset-source-record.md').read_text(),'Missing packaged audio source record')
    return {'status':'PASS OFFLINE ONLY','baseline':str(base),'only_prior_files_changed':sorted(allowed),'added_files':22,'skin_schema':'PASS pinned Draft7 and additional closed-key check','sound_schema':'Not present in pinned SDK; exact installed speech profile and colocated Ogg convention checked','dialogue_references':references,'normalization':verify_audio(),'runtime':'NOT RUN','listening':'NOT RUN; no semantic completeness claim','preservation':preservation()}

def packages(validate_only=False):
    results=[]
    for name,label in [('expanse_amun06','COMBAT & BOARDING'),('expanse_amun06_cloak','CLOAK EXPERIMENT')]:
        base=ROOT/'build/experiments'/name;out=base.with_name(name+'_voice07')
        require(base.is_dir(),'Missing accepted base package '+str(base))
        if not validate_only:
            require(not out.exists() and not out.with_suffix('.zip').exists(),'Refusing existing voice package')
            shutil.copytree(base,out)
            for p in GENERATED.rglob('*'):
                if p.is_file():
                    target=out/p.relative_to(GENERATED);target.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(p,target)
            skin=read(out/'entities/expanse_rocinante_hero.unit_skin');skin['skin_stages'][0]['sounds']['dialogue']=dialogue();write(out/'entities/expanse_rocinante_hero.unit_skin',skin)
            meta=read(out/'.mod_meta_data');meta.update(display_name='The Expanse — Amun-Ra '+label+' + Rocinante VOICES',display_version='0.7.0',short_description='Adds normalized supplied Rocinante voice lines.',long_description=meta['long_description']+' Adds eleven normalized Rocinante dialogue recordings. Load this complete variant alone. Audio triggers/moods need runtime testing.');write(out/'.mod_meta_data',meta)
            (out/'ASSET-SOURCES.md').write_text((base/'ASSET-SOURCES.md').read_text()+'\n'+(AUDIT/'asset-source-record.md').read_text())
        report=validate_package(out,base);write(AUDIT/(out.name+'-validation.json'),report)
        if not validate_only:
            with zipfile.ZipFile(out.with_suffix('.zip'),'w',zipfile.ZIP_DEFLATED)as z:
                for p in sorted(out.rglob('*')):
                    if p.is_file():
                        i=zipfile.ZipInfo(p.relative_to(out).as_posix(),(2026,9,12,0,0,0));i.compress_type=zipfile.ZIP_DEFLATED;i.external_attr=0o100644<<16;z.writestr(i,p.read_bytes())
        summary={'mod_id':out.name,**verify_zip(out.with_suffix('.zip'),out),'installed':False,'runtime':'NOT RUN'};results.append(summary)
        deps=[base,ORIGINAL,EDITABLE,GENERATED];write(out.with_suffix('.dependencies.json'),[str(x)for x in deps]);write(out.with_suffix('.provenance.json'),provenance(out.with_suffix('.zip'),ROOT,deps))
    write(AUDIT/'package-summary.json',results);print(json.dumps(results,indent=2))

if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--normalize-only',action='store_true');p.add_argument('--package-only',action='store_true');p.add_argument('--validate-only',action='store_true');a=p.parse_args()
    preservation()
    if not a.package_only and not a.validate_only:intake_and_normalize()
    verify_audio()
    if not a.normalize_only:packages(a.validate_only)
