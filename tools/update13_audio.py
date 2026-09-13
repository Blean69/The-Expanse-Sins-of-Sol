"""Short PDC report variations: audio-only mitigation for rapid repeated triggers."""
from pathlib import Path
import json, subprocess, shutil
import numpy as np
from validate_experiments import read, require, sha256, file_hashes
from build_polish import write
ROOT=Path(__file__).resolve().parents[1]
BASE=ROOT/'build/experiments/expanse_update12'
SOURCE=ROOT/'assets/derived/pdc-audio10/PDC-normalized.wav'
OUT=ROOT/'build/update13-audio/game'
EDIT=ROOT/'assets/derived/update13-audio'
AUD=ROOT/'audit/update13/audio.json'
STARTS=[.06,.25,.44,.63]

def run(cmd):
 p=subprocess.run(cmd,capture_output=True)
 require(p.returncode==0, 'Audio command failed: '+p.stderr.decode(errors='replace'))
 return p.stdout

def pcm(path):return np.frombuffer(run(['ffmpeg','-v','error','-i',str(path),'-f','f32le','-ac','1','-ar','48000','-']),dtype='<f4')

def metrics(path):
 info=json.loads(run(['ffprobe','-v','error','-show_entries','format=duration','-of','json',str(path)]));x=pcm(path);return {'container_duration':float(info['format']['duration']),'samples':len(x),'duration':len(x)/48000,'peak_dbfs':float(20*np.log10(max(np.max(abs(x)),1e-12))),'rms_dbfs':float(20*np.log10(max(np.sqrt(np.mean(x*x)),1e-12)))}

def main():
 intake=read(ROOT/'audit/pdc-audio10/audio-intake.json');require(SOURCE.is_file(),'Missing ignored normalized PDC WAV: '+str(SOURCE));require(sha256(SOURCE)==intake['wav_sha256'],'Normalized PDC source changed')
 require(not OUT.exists() and not EDIT.exists(),'Refusing prior audio derivative output');(OUT/'sounds').mkdir(parents=True);EDIT.mkdir(parents=True)
 profile=read(BASE/'sounds/expanse10_pdc_burst.sound');require(set(profile)=={'is_positionable','is_looping','is_streaming','min_attenuation_distance','sound_group'},'Re-audit changed sound profile')
 profile['min_attenuation_distance']=70.
 rows=[]
 for i,start in enumerate(STARTS):
  name='expanse13_pdc_report_'+str(i);wav=EDIT/(name+'.wav');ogg=OUT/'sounds'/(name+'.ogg')
  run(['ffmpeg','-v','error','-n','-ss',str(start),'-t','0.20','-i',str(SOURCE),'-af','volume=-10dB,afade=t=in:d=0.004,afade=t=out:st=0.175:d=0.025','-ar','48000','-ac','1','-c:a','pcm_s24le',str(wav)])
  run(['ffmpeg','-v','error','-n','-i',str(wav),'-c:a','libvorbis','-q:a','6',str(ogg)]);write(OUT/'sounds'/(name+'.sound'),profile)
  m=metrics(ogg);require(abs(m['container_duration']-.2)<.001 and .19<=m['duration']<=.225,'Encoded report timing exceeds checked Vorbis block padding');require(m['peak_dbfs'] < -14.,'Report is louder than intended headroom')
  rows.append({'id':name,'source_start_seconds':start,'source_duration_seconds':.2,'gain_db':-10,'fade_in_seconds':.004,'fade_out_seconds':.025,'wav_sha256':sha256(wav),'ogg_sha256':sha256(ogg),'decoded':m})
 # Deterministic same-position/synchronized synthetic mix; not an engine recording.
 def mix(clips):
  y=np.zeros(48000*3,dtype=float)
  for shot in range(8):
   for gun in range(16):
    x=clips[(gun+shot)%len(clips)];pos=shot*12000;y[pos:pos+len(x)]+=x
  return {'unlimited_mix_peak_dbfs':float(20*np.log10(np.max(abs(y)))),'unlimited_mix_rms_dbfs':float(20*np.log10(np.sqrt(np.mean(y*y)))),'samples_exceeding_full_scale':int((abs(y)>1).sum())}
 old=pcm(BASE/'sounds/expanse10_pdc_burst.ogg');clips=[pcm(OUT/'sounds'/(r['id']+'.ogg'))for r in rows]
 write(AUD,{'status':'PASS OFFLINE AUDIO ENCODING','source':str(SOURCE),'source_sha256':sha256(SOURCE),'original_sha256':sha256(ROOT/'assets/original/pdc-audio10/PDC.mp3'),'old':metrics(BASE/'sounds/expanse10_pdc_burst.ogg'),'reports':rows,'sound_profile':profile,'synthetic_mix_16_guns_at_four_triggers_per_second':{'old':mix([old]),'new':mix(clips),'warning':'Deliberately coherent unattenuated sum without engine limiter/spatialization; not a listening or runtime pass'},'game_directory':str(OUT),'files':file_hashes(OUT),'runtime':'NOT RUN','limitations':'No verified per-ship concurrency cap. Short reports and varied waveform starts reduce repeat overlap; finite gain/attenuation does not guarantee a clean whole-fleet mix. No firing rate or damage changed.'})
 print(json.dumps(read(AUD)['synthetic_mix_16_guns_at_four_triggers_per_second'],indent=2))
if __name__=='__main__':main()
