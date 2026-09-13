"""Normalize supplied generic Martian-captain audio; no package/install mutation."""
from pathlib import Path
import argparse, copy, hashlib, json, shutil, sys
MAIN=Path('/run/media/haker/NVME 2/expanse-mod')
sys.path.insert(0,str(MAIN/'tools'))
import build_voice07 as audio
import jsonschema
ROOT=Path(__file__).resolve().parents[1]
ORIGINAL=ROOT/'assets/original/donnager10-voice'
EDITABLE=ROOT/'assets/derived/donnager10-c/normalized-wav'
OUT=ROOT/'build/donnager10-c/voice';AUDIT=ROOT/'audit/donnager10-c'
PREFIX='expanse10_donnager_'
CLIPS=[
 ('railguns','Bringing up railguns, neutral..mp3','attack_order_issued','neutral'),
 ('course','Plotting course correction neutral.mp3','order_issued','neutral'),
 ('bogies',"Multiple bogies, bringing up the PDC's (either).mp3",'attack_order_issued','neutral'),
 ('orders_scared','Looking tough out here, what are our orders (scared).mp3','selected','scared'),
 ('hammers','For mars! Bringing up the hammers (either).mp3','attack_order_issued','smug'),
 ('reaction_mass','Insufficient reaction mass (neutral).mp3','insufficient_antimatter','neutral'),
 ('reaction_mass_scared','Insufficient reaciton mass (scared).mp3','insufficient_antimatter','scared'),
 ('cooldown','Ability on cooldown (neutral).mp3','ability_cooldown_is_not_completed','neutral'),
 ('armor','Armor down! (scared).mp3','armor_down','scared'),
 ('attack','Attack order recieved (neutral).mp3','attack_order_issued','neutral'),
 ('retreat','retreat neutral.mp3','retreat','neutral'),
 ('retreat_scared','Retreat scared.mp3','retreat','scared'),
 ('juice','Here comes the juice (reactor overcharge or jump).mp3','hyperspace_charge_started','neutral'),
 ('crippled','Were going down! (crippled).mp3','became_crippled','scared'),
 ('duty','Reporting for duty.mp3','spawned','neutral'),
 ('standing_by','standing by for orders.mp3','selected','neutral'),
 ('contact',"Hostile contact! PDC's to auto track.mp3",'attack_order_issued','neutral'),
 ('reactor_scram','Reactores scrammed, we cant engage the drives.mp3','cannot_hyperspace','neutral'),
 ('construction','Construction finished.mp3','ship_component_finished_building','neutral'),
 ('destroyed','Ship destroyed voice.mp3','destroyed','neutral'),
]
def write(p,d):p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(d,indent=2)+'\n')
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def require(ok,message):
 if not ok:raise AssertionError(message)
def dialogue():
 d={}
 for ident,name,event,mood in CLIPS:d.setdefault(event,{}).setdefault(mood,[]).append(PREFIX+ident)
 # "either" supplied takes also cover the ordinary neutral/scared attack pools.
 d['attack_order_issued']['neutral'].append(PREFIX+'hammers')
 d['attack_order_issued']['scared']=[PREFIX+'bogies',PREFIX+'hammers',PREFIX+'contact']
 d['became_crippled']['neutral']=[PREFIX+'crippled'];d['destroyed']['scared']=[PREFIX+'destroyed']
 return d

def main(verify=False):
 game=audio.GAME;sdk=audio.SDK
 require(game.is_dir() and sdk.is_dir(),'Missing installed game/SDK: dependent checks NOT RUN')
 if verify:
  d=json.loads((AUDIT/'voice-intake.json').read_text())
  for r in d['records']:
   for key,h in [('source','source_sha256'),('original','source_sha256'),('wav','wav_sha256'),('ogg','ogg_sha256')]:require(sha(r[key])==r[h],'Dependency/output changed: '+r[key])
  require({str(p.relative_to(OUT/'game')):sha(p) for p in sorted((OUT/'game').rglob('*')) if p.is_file()}==json.loads((AUDIT/'voice-generated-hashes.json').read_text()),'Generated audio drift')
  print('PASS hash verification; runtime/listening NOT RUN');return
 sources=[Path('/home/haker/Downloads')/x[1] for x in CLIPS]
 for p in sources:require(p.is_file(),'Missing supplied MP3; dependent checks NOT RUN: '+str(p))
 require(not OUT.exists() and not EDITABLE.exists(),'Refusing existing derivative directory; use --verify')
 ORIGINAL.mkdir(parents=True,exist_ok=True);EDITABLE.mkdir(parents=True);(OUT/'game/sounds').mkdir(parents=True)
 profile=json.loads((game/'sounds/trader_light_frigate_selected_neutral_0.sound').read_text())
 require(profile=={'is_positionable':False,'is_looping':False,'is_streaming':True},'Installed voice profile changed')
 records=[]
 for ident,name,event,mood in CLIPS:
  src=Path('/home/haker/Downloads')/name;original=ORIGINAL/name;sh=sha(src)
  if not original.exists():shutil.copy2(src,original)
  require(sha(original)==sh,'Preserved source copy mismatch')
  first=audio.measure(original);wav=EDITABLE/(ident+'.wav');ogg=OUT/'game/sounds'/(PREFIX+ident+'.ogg')
  filt=f"aformat=channel_layouts=mono,loudnorm=I=-18:TP=-2.5:LRA=11:measured_I={first['input_i']}:measured_TP={first['input_tp']}:measured_LRA={first['input_lra']}:measured_thresh={first['input_thresh']}:offset={first['target_offset']}:linear=true:print_format=json"
  result=audio.run(['ffmpeg','-hide_banner','-nostats','-n','-i',str(original),'-map_metadata','-1','-af',filt,'-ar','44100','-ac','1','-c:a','pcm_s24le',str(wav)])
  audio.run(['ffmpeg','-hide_banner','-nostats','-n','-i',str(wav),'-map_metadata','-1','-c:a','libvorbis','-q:a','6',str(ogg)])
  measured=audio.measure(ogg);probe=audio.probe(ogg);input_probe=audio.probe(original);s=probe['streams'][0]
  require(abs(float(measured['input_i'])+18)<=.6,'Loudness outside tolerance; candidate held: '+ident)
  require(float(measured['input_tp'])<=-1.5,'Decoded true peak above limit; candidate held: '+ident)
  require(s['codec_name']=='vorbis' and s['sample_rate']=='44100' and s['channels']==1,'Wrong audio encoding')
  require(abs(float(probe['format']['duration'])-float(input_probe['format']['duration']))<=.08,'Duration drift: '+ident)
  write(ogg.with_suffix('.sound'),profile)
  records.append({'id':ident,'source_filename':name,'source':str(src),'original':str(original),'source_sha256':sh,'wav':str(wav),'wav_sha256':sha(wav),'ogg':str(ogg),'ogg_sha256':sha(ogg),'event':event,'mood':mood,'source_probe':input_probe,'output_probe':probe,'first_measurement':first,'output_measurement':measured,'second_pass':json.loads(result.stderr[result.stderr.rfind('{'):result.stderr.rfind('}')+1]),'status':'PASS measured normalization; listening/runtime NOT RUN'})
  print(ident,measured['input_i'],measured['input_tp'],flush=True)
  write(AUDIT/'voice-intake-progress.json',records)
 d=dialogue();stock=json.loads((game/'entities/trader_loyalist_titan.unit_skin').read_text())
 for event,moods in d.items():
  for mood in moods:require(mood in stock['skin_stages'][0]['sounds']['dialogue'].get(event,{}),'Category/mood not observed on installed titan: '+event+'/'+mood)
 candidate=copy.deepcopy(stock);candidate['skin_stages'][0]['sounds']['dialogue']=d
 schema=json.loads((sdk/'json_schemas/unit-skin-schema.json').read_text())
 for validator in [jsonschema.Draft7Validator,jsonschema.Draft202012Validator]:validator(schema).validate(candidate)
 for r in records:require(sha(r['source'])==r['source_sha256'] and sha(r['original'])==r['source_sha256'],'Source changed while processing')
 write(OUT/'dialogue.json',d);write(AUDIT/'voice-generated-hashes.json',{str(p.relative_to(OUT/'game')):sha(p) for p in sorted((OUT/'game').rglob('*')) if p.is_file()})
 write(AUDIT/'voice-intake.json',{'status':'PASS OFFLINE AUDIO','records':records,'target_lufs':-18,'lufs_tolerance':.6,'encoded_peak_limit_dbtp':-1.5,'timing':'Full source timing preserved; MP3 padding tolerance80ms; no trims or silence removal','voice_identity':'User-provided/user-described AI-generated generic Martian captain; generation provider, underlying voice identity and license unspecified; no claim copied from model permissions','ffmpeg':audio.run(['ffmpeg','-version']).stdout.splitlines()[0],'runtime':'NOT RUN','listening':'NOT RUN','read_only_helper':{'path':str(MAIN/'tools/build_voice07.py'),'sha256':sha(MAIN/'tools/build_voice07.py')},'reference_hashes':{str(p):sha(p) for p in [game/'entities/trader_loyalist_titan.unit_skin',game/'sounds/trader_light_frigate_selected_neutral_0.sound',sdk/'json_schemas/unit-skin-schema.json']}})
 write(AUDIT/'voice-integration-spec.json',{'status':'PASS OFFLINE AUDIO','game_directory':str(OUT/'game'),'dialogue_json':str(OUT/'dialogue.json'),'skin_pointer':'/skin_stages/0/sounds/dialogue','apply_only':'new Donnager skin; never replace Rocinante dialogue','files':40,'records':20,'entity_manifests_required':[],'runtime':'NOT RUN','held_callbacks':['No enemy-detection/PDC-interception event: PDC lines acknowledge attack orders','Construction line only ship_component_finished_building, not newly produced fleet ships','Reactor warning only cannot_hyperspace; no reactor or drive-failure detector','Reaction mass is flavor for existing insufficient_antimatter; no separate fuel resource','Juice uses hyperspace_charge_started; no reactor-overcharge ability sound binding proposed']})
 print('PASS20 normalized lines;40 game files; dialogue schema verified; runtime/listening NOT RUN')
if __name__=='__main__':
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('--verify',action='store_true');main(p.parse_args().verify)
