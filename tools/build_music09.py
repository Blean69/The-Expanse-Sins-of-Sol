"""Normalize supplied music and bind only verified TEC music states."""
import argparse,concurrent.futures,copy,json,math,shutil,zipfile
from pathlib import Path
import jsonschema
from build_voice07 import run,probe
from build_polish import write
from validate_experiments import read,require,file_hashes,sha256,compare_tree,verify_pins,verify_zip,provenance

ROOT=Path(__file__).resolve().parents[1];AUDIT=ROOT/'audit/music09';GAME=ROOT.parent/'SteamLibrary/steamapps/common/Sins2';SDK=ROOT.parent/'SteamLibrary/steamapps/common/Sins of a Solar Empire II - Mod Tools'
ORIGINAL=ROOT/'assets/original/music09';EDITABLE=ROOT/'assets/derived/music09/normalized-wav';GENERATED=ROOT/'build/music09/game'
TRACKS={'welwala':'welwala-soundtrack','eros_radio':'track-from-eros-radio-deep-inc-touch','theme':'theme-tune','tachi_station':'tachi-station-soundtrack','signal':'signal-soundtrack','respite':'respite-soundtrack','ready_to_talk':'ready-to-talk-soundtrack','lionel_polanski':'lionel-polanski-soundtrack','lies_and_power':'lies-and-love-of-power-soundtrack','boarded':'boarded-soundtrack','impossible_burden':'an-impossible-burden-soundtrack','lifetime_losing':'a-lifetime-of-losing-soundtrack','expanse_theme':'the-expanse-soundtrack'}
TARGET=-20.0;TP=-2.5
START_SECONDS={'signal':65.0}
TRACKS.update(never_see_them_coming='Never See Them Coming.mp3',hammerlock='Hammerlock.mp3')

def source_filename(name):
    return name if name.endswith('.mp3')else name+'.wav'

def preservation():
    d=read(AUDIT/'checkpoint.json');checks=[compare_tree(x)for x in d['trees']]
    for p,h in d['zips'].items():require(sha256(p)==h,'Earlier ZIP changed: '+p)
    return {'trees':checks,'old_zips_unchanged':len(d['zips']),'pins':verify_pins(ROOT,GAME,SDK)}

def measure(p,start=0.0):
    r=run(['ffmpeg','-hide_banner','-nostats','-ss',str(start),'-i',str(p),'-af',f'loudnorm=I={TARGET}:TP={TP}:LRA=20:print_format=json','-f','null','-'])
    d=json.loads(r.stderr[r.stderr.rfind('{'):r.stderr.rfind('}')+1]);require(all(math.isfinite(float(d[k]))for k in ['input_i','input_tp','input_lra','input_thresh','target_offset']),'Unmeasurable music: '+str(p));return d

def normalize_one(item):
    ident,name=item;p=ORIGINAL/source_filename(name);info=probe(p);channels=info['streams'][0]['channels'];require(channels in [1,2],'Unexpected source layout')
    start=START_SECONDS.get(ident,0.0);require(float(info['format']['duration'])>start,'Crop starts after track end')
    first=measure(p,start);wav=EDITABLE/(ident+'.wav');ogg=GENERATED/'sounds'/('expanse09_music_'+ident+'.ogg')
    filt=f"loudnorm=I={TARGET}:TP={TP}:LRA=20:measured_I={first['input_i']}:measured_TP={first['input_tp']}:measured_LRA={first['input_lra']}:measured_thresh={first['input_thresh']}:offset={first['target_offset']}:linear=true:print_format=json"
    r=run(['ffmpeg','-hide_banner','-nostats','-n','-ss',str(start),'-i',str(p),'-map_metadata','-1','-af',filt,'-ar','44100','-ac',str(channels),'-c:a','pcm_s24le',str(wav)])
    second=json.loads(r.stderr[r.stderr.rfind('{'):r.stderr.rfind('}')+1]);run(['ffmpeg','-hide_banner','-nostats','-n','-i',str(wav),'-map_metadata','-1','-c:a','libvorbis','-q:a','6',str(ogg)])
    actual=measure(ogg);outinfo=probe(ogg);s=outinfo['streams'][0]
    require(abs(float(actual['input_i'])-TARGET)<=.6,'Music loudness mismatch '+ident);require(float(actual['input_tp'])<=-1.5,'Music true peak too high '+ident)
    require(s['codec_name']=='vorbis'and s['channels']==channels and s['sample_rate']=='44100','Wrong music codec/layout')
    require(abs(float(outinfo['format']['duration'])-(float(info['format']['duration'])-start))<.08,'Unexpected timing change')
    write(ogg.with_suffix('.sound'),read(GAME/'sounds/tech_battle.sound'))
    print(ident,actual['input_i'],'LUFS',actual['input_tp'],'dBTP',flush=True)
    return {'id':ident,'source':str(Path('/home/haker/Downloads')/source_filename(name)),'original':str(p),'sha256':sha256(p),'input':info,'start_seconds':start,'first_pass':first,'second_pass':second,'wav':str(wav),'wav_sha256':sha256(wav),'ogg':str(ogg),'ogg_sha256':sha256(ogg),'encoded':outinfo,'measurement':actual,'listening':'NOT RUN; combat assignments approved by user; other moods provisional'}

def normalize():
    require(not ORIGINAL.exists()and not EDITABLE.exists()and not GENERATED.exists(),'Fresh music derivative destinations required')
    for name in TRACKS.values():require((Path('/home/haker/Downloads')/source_filename(name)).is_file(),'Missing supplied track '+name)
    ORIGINAL.mkdir(parents=True);EDITABLE.mkdir(parents=True);(GENERATED/'sounds').mkdir(parents=True)
    for name in TRACKS.values():
        source=Path('/home/haker/Downloads')/source_filename(name);target=ORIGINAL/source.name;shutil.copy2(source,target);require(sha256(source)==sha256(target),'Original preservation failed')
    require(read(GAME/'sounds/tech_battle.sound')=={'is_streaming':True,'is_looping':True},'Re-audit music sound convention')
    with concurrent.futures.ThreadPoolExecutor(max_workers=2)as pool:records=list(pool.map(normalize_one,TRACKS.items()))
    write(AUDIT/'audio-intake.json',{'target_lufs':TARGET,'true_peak_target_dbtp':TP,'records':records,'ffmpeg':run(['ffmpeg','-version']).stdout.splitlines()[0],'original_channels_preserved':True,'start_seconds':START_SECONDS,'listening':'NOT RUN'})
    write(AUDIT/'generated-hashes.json',file_hashes(GENERATED))

def pool(names,first=None,ambient=False):
    d={'exhaustive_shuffle':True,'music_tracks':[{'sound':'expanse09_music_'+n,'weight':1}for n in names]}
    if first is not None:d['first_music_track_index']=first
    if ambient:d['extra_music_tracks_pool_type']='ambient'
    return d

def music_pools():
    return {
      'front_end':pool(['theme','expanse_theme'],first=0),
      'loading':pool(['expanse_theme','respite']),
      'ambient':pool(['respite','ready_to_talk','tachi_station','lionel_polanski','eros_radio']),
      'early_game_neutral':pool(['tachi_station','ready_to_talk'],ambient=True),
      'early_game_winning':pool(['tachi_station','expanse_theme'],ambient=True),
      'early_game_losing':pool(['lionel_polanski','lifetime_losing'],ambient=True),
      'mid_game_neutral':pool(['lionel_polanski','lies_and_power'],ambient=True),
      'mid_game_winning':pool(['ready_to_talk','expanse_theme'],ambient=True),
      'mid_game_losing':pool(['lifetime_losing','impossible_burden'],ambient=True),
      'late_game_neutral':pool(['lies_and_power','lionel_polanski'],ambient=True),
      'late_game_winning':pool(['expanse_theme','tachi_station'],ambient=True),
      'late_game_losing':pool(['impossible_burden','lifetime_losing'],ambient=True),
      'battle_neutral':pool(['boarded','welwala','signal','never_see_them_coming','hammerlock']),
      'battle_winning':pool(['welwala','boarded','signal','never_see_them_coming','hammerlock']),
      'battle_losing':pool(['signal','boarded','welwala','never_see_them_coming','hammerlock']),
      'game_won':pool(['expanse_theme','respite'],first=0),
      'game_lost':pool(['lifetime_losing','impossible_burden'],first=0)}

def race_uniform():
    d=read(GAME/'uniforms/player_race.uniforms');d['overwrite_races']=True
    race=next(r for r in d['races']if r['name']=='trader');require(set(race['music']['in_game_music_pools'])==set(music_pools()),'Installed music states changed')
    race['music']['in_game_music_pools']=music_pools();return d

def audio_checks():
    d=read(AUDIT/'audio-intake.json');require(len(d['records'])==len(TRACKS),'Missing soundtrack recording')
    for x in d['records']:
        for k in ['source','original']:require(sha256(x[k])==x['sha256'],'Original soundtrack changed')
        require(sha256(x['wav'])==x['wav_sha256'] and sha256(x['ogg'])==x['ogg_sha256'],'Normalized soundtrack drift')
        start=START_SECONDS.get(x['id'],0.0);require(x.get('start_seconds',0)==start,'Required source crop missing')
        require(abs(float(x['encoded']['format']['duration'])-(float(x['input']['format']['duration'])-start))<.08,'Encoded crop duration mismatch')
    require(file_hashes(GENERATED)==read(AUDIT/'generated-hashes.json'),'Generated music drift')

def validate(out,base):
    old=file_hashes(base);new=file_hashes(out);require(not set(old)-set(new),'Previous content removed')
    for name,h in old.items():
        if name not in ['.mod_meta_data','ASSET-SOURCES.md']:require(new[name]==h,'Music changed existing gameplay/voice content: '+name)
    extra=set(read(AUDIT/'generated-hashes.json'))|{'uniforms/player_race.uniforms'}
    require(set(new)-set(old)==extra,'Unexpected added files')
    expected=race_uniform();actual=read(out/'uniforms/player_race.uniforms');require(actual==expected,'Race override exceeds exact music edit')
    schema=read(SDK/'json_schemas/player-race-uniforms-schema.json')
    jsonschema.Draft7Validator(schema).validate(actual);jsonschema.Draft202012Validator(schema).validate(actual)
    stock=read(GAME/'uniforms/player_race.uniforms');restored=copy.deepcopy(actual);restored.pop('overwrite_races');next(r for r in restored['races']if r['name']=='trader')['music']=next(r for r in stock['races']if r['name']=='trader')['music'];require(restored==stock,'Unrelated faction data changed')
    used=set()
    for state,p in music_pools().items():
        require('first_music_track_index'not in p or 0<=p['first_music_track_index']<len(p['music_tracks']),'Invalid first index')
        for t in p['music_tracks']:
            used.add(t['sound']);path=out/'sounds'/(t['sound']+'.sound');require(read(path)==read(GAME/'sounds/tech_battle.sound'),'Wrong streaming music convention');require(path.with_suffix('.ogg').is_file(),'Missing soundtrack media')
    require(used=={'expanse09_music_'+x for x in TRACKS},'Unused or missing supplied soundtrack')
    for p,h in read(AUDIT/'generated-hashes.json').items():require(new[p]==h,'Packaged audio differs from measurement')
    require((out/'ASSET-SOURCES.md').read_text()==(base/'ASSET-SOURCES.md').read_text()+'\n'+(AUDIT/'asset-source-record.md').read_text(),'Missing soundtrack credit record')
    audio_checks()
    return {'status':'PASS OFFLINE ONLY','runtime':'NOT RUN','music_states':list(music_pools()),'used_tracks':sorted(used),'full_player_race_schema':'PASS pinned Draft7 and additional closed-key check','other_race_and_nonmusic_fields_unchanged':True,'previous_ability_fixes_and_17_voices_unchanged':True,'new_files':2*len(TRACKS)+1,'preservation':preservation()}

def main(a):
    preservation()
    if a.normalize:normalize();return
    audio_checks();write(AUDIT/'playlist-map.json',music_pools());summaries=[]
    for suffix,label in [('_cloak','CLOAK + BOARDING'),('','COMBAT + BOARDING')]:
        base=ROOT/'build/experiments'/('expanse_amun08'+suffix);out=ROOT/'build/experiments'/('expanse_amun09'+suffix)
        if not a.validate_only:
            require(not out.exists()and not out.with_suffix('.zip').exists(),'Refusing existing soundtrack package')
            shutil.copytree(base,out)
            for p in GENERATED.rglob('*'):
                if p.is_file():shutil.copy2(p,out/p.relative_to(GENERATED))
            write(out/'uniforms/player_race.uniforms',race_uniform())
            meta=read(out/'.mod_meta_data');meta.update(display_name='The Expanse — 0.9 '+label+' + VOICES + MUSIC',display_version='0.9.0',short_description='Corrected abilities, 17 Rocinante voices and 15 soundtrack recordings.',long_description=meta['long_description']+' Adds normalized Expanse music to verified TEC menu/loading/ambient/battle/game-phase pools. Five combat tracks approved by user; other mood assignments provisional. Runtime transitions not tested.');write(out/'.mod_meta_data',meta)
            (out/'ASSET-SOURCES.md').write_text((base/'ASSET-SOURCES.md').read_text()+'\n'+(AUDIT/'asset-source-record.md').read_text())
        write(AUDIT/(out.name+'-validation.json'),validate(out,base))
        if not a.validate_only:
            with zipfile.ZipFile(out.with_suffix('.zip'),'w',zipfile.ZIP_DEFLATED)as z:
                for p in sorted(out.rglob('*')):
                    if p.is_file():
                        info=zipfile.ZipInfo(p.relative_to(out).as_posix(),(2026,9,12,0,0,0));info.compress_type=zipfile.ZIP_DEFLATED;info.external_attr=0o100644<<16;z.writestr(info,p.read_bytes())
        result={'mod_id':out.name,**verify_zip(out.with_suffix('.zip'),out),'installed':False,'runtime':'NOT RUN'};summaries.append(result)
        deps=[base,ORIGINAL,EDITABLE,GENERATED];write(out.with_suffix('.dependencies.json'),[str(x)for x in deps]);write(out.with_suffix('.provenance.json'),provenance(out.with_suffix('.zip'),ROOT,deps))
    write(AUDIT/'package-summary.json',summaries);print(json.dumps(summaries,indent=2))

if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--normalize',action='store_true');p.add_argument('--validate-only',action='store_true');main(p.parse_args())
