"""Add the supplied PDC burst to a new combined0.10.1 package; no installation."""
from pathlib import Path
import argparse,copy,json,shutil,subprocess,zipfile
from validate_experiments import read,require,sha256,file_hashes,verify_zip,verify_pins,provenance
ROOT=Path(__file__).resolve().parents[1];BASE=ROOT/'build/experiments/expanse_donnager10';OUT=ROOT/'build/experiments/expanse_donnager10_pdc_audio'
GAME=ROOT.parent/'SteamLibrary/steamapps/common/Sins2';SDK=ROOT.parent/'SteamLibrary/steamapps/common/Sins of a Solar Empire II - Mod Tools'
AUDIT=ROOT/'audit/pdc-audio10';ORIGINAL=ROOT/'assets/original/pdc-audio10/PDC.mp3';WAV=ROOT/'assets/derived/pdc-audio10/PDC-normalized.wav';GENERATED=ROOT/'build/pdc-audio10/game/sounds'
SOURCE=ROOT.parent/'expanse-audio-work/PDC.mp3';SOUND='expanse10_pdc_burst';ALIAS='trader_antifighter_frigate_point_defense_autocannon_weapon_muzzle'
SHIPS=['trader_light_frigate','expanse_rocinante_hero','expanse_amun_ra','expanse_donnager_battleship']
def write(p,d):p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(d,indent=2)+'\n')
def run(args):return subprocess.run(args,check=True,capture_output=True,text=True)
def probe(p):return json.loads(run(['ffprobe','-v','error','-show_format','-show_streams','-of','json',str(p)]).stdout)
def measure(p):
 s=run(['ffmpeg','-hide_banner','-nostats','-i',str(p),'-af','loudnorm=I=-18:TP=-3:LRA=7:print_format=json','-f','null','-']).stderr
 return json.loads(s[s.rfind('{'):s.rfind('}')+1])
def skin(name):
 d=read(BASE/'entities'/(name+'.unit_skin'));count=0
 for stage in d['skin_stages']:
  for row in stage['effects']['effect_alias_bindings']:
   if row['alias_name']==ALIAS:row['alias_binding']['sounds']=[SOUND];count+=1
 require(count==1,'Expected exactly one PDC muzzle binding on '+name);return d

def main(validate_only=False,recover=False):
 require(SOURCE.is_file(),'Supplied PDC clip missing; audio checks NOT RUN')
 require(sha256(BASE.with_suffix('.zip'))=='2a9650d771178b1ae5ff83d2c5d2076dfcb546290bc233a8d4e352aebcad484f','Donnager checkpoint ZIP changed')
 basecheck=verify_zip(BASE.with_suffix('.zip'),BASE);pins=verify_pins(ROOT,GAME,SDK);before=file_hashes(BASE)
 profile=read(GAME/'sounds/weapon_muzzle_tech_pointdefense_autocannon.sound')
 require(profile=={'is_positionable':True,'is_looping':False,'is_streaming':False,'min_attenuation_distance':100.0,'sound_group':'weapon_muzzle_light'},'Re-audit changed installed PDC sound profile')
 if not validate_only and not recover:
  require(not OUT.exists() and not ORIGINAL.exists() and not WAV.exists() and not GENERATED.exists(),'Refusing to overwrite an existing audio derivative/package')
  ORIGINAL.parent.mkdir(parents=True);WAV.parent.mkdir(parents=True);GENERATED.mkdir(parents=True);shutil.copy2(SOURCE,ORIGINAL)
  initial=measure(ORIGINAL)
  f='loudnorm=I=-18:TP=-3:LRA=7:measured_I={input_i}:measured_TP={input_tp}:measured_LRA={input_lra}:measured_thresh={input_thresh}:offset={target_offset}:linear=true'.format(**initial)
  run(['ffmpeg','-hide_banner','-nostats','-n','-i',str(ORIGINAL),'-map_metadata','-1','-af',f,'-ar','48000','-ac','1','-c:a','pcm_s24le',str(WAV)])
  ogg=GENERATED/(SOUND+'.ogg');run(['ffmpeg','-hide_banner','-nostats','-n','-i',str(WAV),'-map_metadata','-1','-c:a','libvorbis','-q:a','6',str(ogg)])
  write(GENERATED/(SOUND+'.sound'),profile)
  write(AUDIT/'audio-intake.json',{'source':str(SOURCE),'source_sha256':sha256(SOURCE),'preserved_original':str(ORIGINAL),'original_sha256':sha256(ORIGINAL),'wav':str(WAV),'wav_sha256':sha256(WAV),'ogg_sha256':sha256(ogg),'initial':initial,'encoded':measure(ogg),'probe':probe(ogg),'target_lufs':-18,'listening':'NOT RUN','runtime':'NOT RUN','generated_hashes':file_hashes(GENERATED)})
  credit='\n## PDC burst0.10.1\n\nUser-supplied `PDC.mp3`, extracted by the user and explicitly supplied for local PDC sound integration. Source: '+str(SOURCE)+'. SHA-256: '+sha256(SOURCE)+'. Original preserved unchanged; derivative normalizes loudness and converts to mono48kHz Vorbis without intentional trimming. Original work/rightsholder and separate license were not identified in this handoff; no independent license claim or publication is made.\n'
  (AUDIT/'asset-source-record.md').write_text(credit)
  shutil.copytree(BASE,OUT)
  for p in GENERATED.iterdir():shutil.copy2(p,OUT/'sounds'/p.name)
  for n in SHIPS:write(OUT/'entities'/(n+'.unit_skin'),skin(n))
  meta=read(BASE/'.mod_meta_data');meta.update(display_name='The Expanse — 0.10.1 DONNAGER + PDC AUDIO',display_version='0.10.1',short_description='Combined Donnager prototype with the supplied PDC firing sound on all four Expanse ships.');meta['long_description']+=' Adds normalized positional PDC burst audio; weapon gameplay and other audio remain unchanged. New audio playback NOT RUN.';write(OUT/'.mod_meta_data',meta)
  (OUT/'ASSET-SOURCES.md').write_text((BASE/'ASSET-SOURCES.md').read_text()+credit)
 intake=read(AUDIT/'audio-intake.json');ogg=GENERATED/(SOUND+'.ogg');actual=measure(ogg);info=probe(ogg);stream=info['streams'][0]
 require(sha256(SOURCE)==sha256(ORIGINAL)==intake['source_sha256'],'Original clip changed');require(sha256(WAV)==intake['wav_sha256'],'Editable WAV changed');require(sha256(ogg)==intake['ogg_sha256'] and read(GENERATED/(SOUND+'.sound'))==profile,'Generated audio drift')
 require(abs(float(actual['input_i'])+18)<=.6 and float(actual['input_tp'])<=-2,'Encoded loudness/peak outside limits')
 require(stream['codec_name']=='vorbis' and stream['channels']==1 and stream['sample_rate']=='48000','Unexpected output codec/layout')
 require(abs(float(info['format']['duration'])-float(probe(WAV)['format']['duration']))<.025,'Unexpected audio trimming')
 import jsonschema
 schema=read(SDK/'json_schemas/unit-skin-schema.json')
 for n in SHIPS:
  got=read(OUT/'entities'/(n+'.unit_skin'));require(got==skin(n),'Change exceeds PDC sound binding');jsonschema.Draft7Validator(schema).validate(got);jsonschema.Draft202012Validator(schema).validate(got)
  u=read(OUT/'entities'/(n+'.unit'));pdc=0
  for m in u['weapons']['weapons']:
   w=read(OUT/'entities'/(m['weapon']+'.weapon'))
   if 'point_defense' in w.get('tags',[]):require(w['effects']['muzzle_effect']==ALIAS,'PDC lacks updated binding');pdc+=1
  require(pdc=={'trader_light_frigate':6,'expanse_rocinante_hero':6,'expanse_amun_ra':3,'expanse_donnager_battleship':16}[n],'Unexpected gun count')
 after=file_hashes(OUT);allowed={'.mod_meta_data','ASSET-SOURCES.md'}|{'entities/'+n+'.unit_skin'for n in SHIPS}
 require(set(after)-set(before)=={'sounds/'+SOUND+'.ogg','sounds/'+SOUND+'.sound'},'Unexpected extra files')
 require(not set(before)-set(after),'Prior files removed')
 for n,h in before.items():
  if n not in allowed:require(after[n]==h,'Non-PDC content changed: '+n)
 require(file_hashes(BASE)==before,'Donnager checkpoint modified')
 for n,h in file_hashes(GENERATED).items():require(sha256(OUT/'sounds'/n)==h,'Packaged audio differs')
 write(AUDIT/'validation.json',{'status':'PASS OFFLINE ONLY','source_preserved':True,'schemas':4,'ships':SHIPS,'PDC_mounts':31,'only_skin_muzzle_sound_bindings_changed':True,'gameplay_other_audio_music_unchanged':True,'encoded_measurement':actual,'base':basecheck,'pins':pins,'runtime':'NOT RUN','mix_gate':'Check overlapping bursts and zoom attenuation with one ship then a fleet; retains installed positional/nonlooping/light-weapon sound group.'})
 package=OUT.with_name(OUT.name+'_ready').with_suffix('.zip') if recover else OUT.with_suffix('.zip')
 if not validate_only:
  require(not package.exists(),'Refusing existing ZIP destination')
  with zipfile.ZipFile(package,'w',zipfile.ZIP_DEFLATED)as z:
   for p in sorted(OUT.rglob('*')):
    if p.is_file():
     item=zipfile.ZipInfo(p.relative_to(OUT).as_posix(),(2026,9,13,0,0,0));item.compress_type=zipfile.ZIP_DEFLATED;item.external_attr=0o100644<<16;z.writestr(item,p.read_bytes())
 result={'mod_id':OUT.name,**verify_zip(package,OUT),'installed':False,'runtime':'NOT RUN'};write(AUDIT/('recovered-package-summary.json' if recover else 'package-summary.json'),result)
 deps=[BASE,ORIGINAL,WAV,GENERATED];write(package.with_suffix('.provenance.json'),provenance(package,ROOT,deps));print(json.dumps(result,indent=2))
if __name__=='__main__':
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('--validate-only',action='store_true');p.add_argument('--recover',action='store_true',help='Validate existing audio/assembly and create a fresh _ready ZIP without changing originals or the interrupted ZIP');a=p.parse_args();main(a.validate_only,a.recover)
