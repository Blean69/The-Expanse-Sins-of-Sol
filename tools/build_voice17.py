"""Audio-only 0.17 overlay, preserving the frozen 0.16 fleet. No install operations."""
from pathlib import Path
import argparse, copy, json, shutil, zipfile
from build_polish import write
from build_voice07 import run, probe, measure, TARGET, PEAK
from validate_experiments import read, require, sha256, file_hashes, tree_hash, verify_pins, verify_zip, provenance
from update11_validate import schema_check
from amun06_validate_package import AmunResolver
ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT/'build/experiments/expanse_update16'
OUT = ROOT/'build/experiments/expanse_update17'
AUD = ROOT/'audit/update17'
ORIG = ROOT/'assets/original/voice17'
DERIVED = ROOT/'assets/derived/voice17'
GAME = ROOT.parent/'SteamLibrary/steamapps/common/Sins2'
SDK = GAME.parent/'Sins of a Solar Empire II - Mod Tools'
PREFIX = 'expanse17_voice_'
CLIPS = {
 'platform': 'Defence platform reporting for duty.mp3',
 'scirocco': 'Scirocco reporting for duty.mp3',
 'mcrn_orders': 'MCRN what are our orders.mp3',
 'raptor': 'MCRN raptor reporting for duty.mp3',
 'pella_rail_held': 'Pella bringing up the railguns.mp3',
 'pella': 'Aye beltalowda, pella here.mp3',
 'razorback_command': 'I got this command (razorback).mp3',
 'razorback_retreat': 'Good luck catching me (razorback).mp3',
 'unn_crippled': "we're going down! UNN.mp3",
 'construction': 'Construction complete.mp3',
 'unn_scram': 'Reactor scrammed UNN.mp3',
 'unn_juice': 'Here comes the juice UNN.mp3',
 'unn_helm': 'helm, bring us about UNN.mp3',
 'unn_retreat': 'Retreat scared UNN.mp3',
 'unn_cooldown': 'Ability on cooldown UNN.mp3',
 'unn_mass_scared': 'Insufficient reaction mass scaredUNN.mp3',
 'unn_mass': 'Insufficient reaction mass neutralUNN.mp3',
 'unn_rail': 'warming up railguns UNN.mp3',
 'unn_contact': "Hostile contact PDC's to auto UNN.mp3",
 'unn_attack': 'Attack order received.mp3',
 'unn_course': 'Plotting course correction.mp3',
 'unn_orders_scared': 'Looking tough out here UNN.mp3',
 'unn_duty': 'Reporting for Duty UNN.mp3',
 'morrigan': 'Morrigan awaiting orders.mp3',
}
SKINS = ['expanse15_missile_defense', 'expanse12_scirocco', 'expanse12_raptor',
 'expanse_mcrn_corvette', 'expanse12_pella', 'trader_scout_corvette',
 'trader_light_frigate', 'expanse15_truman', 'expanse_amun_ra', 'expanse_donnager_battleship']
PROFILE = {'is_positionable': False, 'is_looping': False, 'is_streaming': True}

def checkpoint():
    require(not (AUD/'checkpoint.json').exists(), 'Checkpoint already exists')
    prior = read(ROOT/'audit/update16/package-summary.json')
    require(tree_hash(file_hashes(BASE)) == prior['tree_sha256'], '0.16 tree drift')
    require(sha256(BASE.with_suffix('.zip')) == prior['zip_sha256'], '0.16 archive drift')
    sources = {str(Path('/home/haker/Downloads')/n): sha256(Path('/home/haker/Downloads')/n) for n in CLIPS.values()}
    write(AUD/'checkpoint.json', {'source_commit': run(['git', '-C', str(ROOT), 'rev-parse', 'HEAD']).stdout.strip(),
        'baseline': str(BASE), 'tree_sha256': prior['tree_sha256'], 'zip_sha256': prior['zip_sha256'], 'originals': sources,
        'pins': verify_pins(ROOT, GAME, SDK)})

def normalize():
    require(not DERIVED.exists(), 'Refusing to overwrite audio derivatives')
    require(read(GAME/'sounds/trader_light_frigate_selected_neutral_0.sound') == PROFILE, 'Native voice profile changed')
    ORIG.mkdir(parents=True, exist_ok=True)
    (DERIVED/'sounds').mkdir(parents=True)
    (DERIVED/'wav').mkdir()
    rows = []
    for ident, filename in CLIPS.items():
        source = Path('/home/haker/Downloads')/filename
        original = ORIG/filename
        if not original.exists(): shutil.copy2(source, original)
        require(sha256(source) == sha256(original), 'Original copy differs')
        row = {'id': ident, 'source': str(source), 'original': str(original), 'source_sha256': sha256(source)}
        if ident.endswith('_held'):
            row['status'] = 'HELD: Pella has no railgun; no game resource generated'
        else:
            first = measure(original)
            wav = DERIVED/'wav'/(ident+'.wav')
            ogg = DERIVED/'sounds'/(PREFIX+ident+'.ogg')
            filt = f"aformat=channel_layouts=mono,loudnorm=I={TARGET}:TP={PEAK}:LRA=11:measured_I={first['input_i']}:measured_TP={first['input_tp']}:measured_LRA={first['input_lra']}:measured_thresh={first['input_thresh']}:offset={first['target_offset']}:linear=true"
            def encode(w, o, f):
                run(['ffmpeg','-hide_banner','-nostats','-n','-i',str(original),'-map_metadata','-1','-af',f,'-ar','44100','-ac','1','-c:a','pcm_s24le',str(w)])
                run(['ffmpeg','-hide_banner','-nostats','-n','-i',str(w),'-map_metadata','-1','-c:a','libvorbis','-q:a','6',str(o)])
            encode(wav, ogg, filt)
            measured = measure(ogg)
            good = lambda m: abs(float(m['input_i'])-TARGET) <= .6 and float(m['input_tp']) <= -1.5
            if not good(measured):
                attempts = DERIVED/'attempts'/ident
                attempts.mkdir(parents=True)
                wav.rename(attempts/'initial.wav'); ogg.rename(attempts/'initial.ogg')
                gain = TARGET-float(first['input_i']); row['limiter_attempts'] = []
                for i in range(4):
                    w = attempts/(str(i)+'.wav'); o = w.with_suffix('.ogg')
                    encode(w,o,f'aformat=channel_layouts=mono,volume={gain}dB,alimiter=limit={10**(-3/20)}:attack=5:release=50:level=false:latency=true')
                    measured = measure(o)
                    row['limiter_attempts'].append({'gain_db': gain, 'measurement': measured})
                    if good(measured): shutil.copy2(w,wav); shutil.copy2(o,ogg); break
                    gain += TARGET-float(measured['input_i'])
            require(ogg.exists() and good(measured), 'Normalization failed: '+ident)
            inp, outp = probe(original), probe(ogg)
            stream = outp['streams'][0]
            require((stream['codec_name'],stream['sample_rate'],stream['channels']) == ('vorbis','44100',1), 'Encoding mismatch')
            require(abs(float(inp['format']['duration'])-float(outp['format']['duration'])) <= .08, 'Unexpected duration change')
            write(ogg.with_suffix('.sound'), PROFILE)
            row.update(status='PASS measured normalization', input_measurement=first, output_measurement=measured,
                input_duration=float(inp['format']['duration']), output_duration=float(outp['format']['duration']),
                wav_sha256=sha256(wav), ogg_sha256=sha256(ogg))
        rows.append(row)
        print(ident, row['status'], flush=True)
    write(AUD/'audio-intake.json', {'records': rows, 'target_lufs': TARGET, 'tolerance_lufs': .6,
        'true_peak_limit_dbtp': -1.5, 'sample_rate': 44100, 'channels': 1, 'codec': 'Vorbis q6',
        'timing': 'Full clip preserved; no trimming or missing-word reconstruction',
        'listening': 'NOT RUN', 'runtime': 'NOT RUN', 'ffmpeg': run(['ffmpeg','-version']).stdout.splitlines()[0]})
    write(AUD/'generated-hashes.json', file_hashes(DERIVED/'sounds'))

def dialogues():
    maps = {n: copy.deepcopy(read(BASE/'entities'/(n+'.unit_skin'))['skin_stages'][0]['sounds']['dialogue']) for n in SKINS}
    def put(n, event, ids, mood='neutral'):
        maps[n].setdefault(event,{})[mood] = [PREFIX+i for i in ids]
    # Remove reused introductions from order/selection pools on non-Donnager hulls.
    # Other generic warnings remain; filenames are not treated as speech transcripts.
    for n in SKINS:
        if n == 'expanse_donnager_battleship': continue
        for moods in maps[n].values():
            for mood, ids in moods.items():
                moods[mood] = [i for i in ids if i not in {'expanse10_donnager_duty','expanse10_donnager_standing_by'}]
    for n, ident in [('expanse12_raptor','raptor'),('expanse12_scirocco','scirocco')]:
        put(n,'spawned',[ident]); put(n,'selected',['mcrn_orders']); put(n,'selected',['mcrn_orders'],'scared')
    put('expanse_mcrn_corvette','selected',['mcrn_orders'])
    for event in ['spawned','selected']: put('trader_light_frigate',event,['morrigan'])
    put('trader_light_frigate','selected',['morrigan'],'scared')
    for event in ['spawned','selected']: put('expanse15_missile_defense',event,['platform'])
    put('expanse15_missile_defense','selected',['platform'],'scared')
    put('expanse12_pella','spawned',['pella'])
    put('expanse12_pella','selected',['pella'])
    # One greeting entry beside the existing generic request for orders. No
    # unverified weighting fields or duplicated entries to imply rarity.
    maps['expanse12_pella']['selected']['neutral'].append('expanse10_donnager_orders_scared')
    for event in ['spawned','order_issued']: put('trader_scout_corvette',event,['razorback_command'])
    for event in ['selected','retreat']:
        for mood in ['neutral','scared']: put('trader_scout_corvette',event,['razorback_retreat'],mood)
    # This unarmed scout should not acknowledge attacks by bringing up PDCs.
    maps['trader_scout_corvette'].pop('attack_order_issued',None)
    for n in ['expanse15_truman','expanse_amun_ra']:
        for event, ids in {
            'spawned':['unn_duty'], 'selected':['unn_duty'],
            'order_issued':['unn_course','unn_helm'],
            'attack_order_issued':['unn_attack','unn_contact','unn_rail'],
            'hyperspace_charge_started':['unn_juice'], 'cannot_hyperspace':['unn_scram'],
            'ability_cooldown_is_not_completed':['unn_cooldown'],
            'insufficient_antimatter':['unn_mass'], 'became_crippled':['unn_crippled'], 'retreat':['unn_retreat']
        }.items():
            maps[n][event] = {}; put(n,event,ids)
        for event, ids in {
            'selected':['unn_orders_scared'], 'order_issued':['unn_helm','unn_course'],
            'attack_order_issued':['unn_contact'], 'cannot_hyperspace':['unn_scram'],
            'ability_cooldown_is_not_completed':['unn_cooldown'], 'insufficient_antimatter':['unn_mass_scared'],
            'became_crippled':['unn_crippled'], 'retreat':['unn_retreat']
        }.items(): put(n,event,ids,'scared')
        put(n,'attack_order_issued',['unn_attack'],'smug')
        maps[n].pop('shields_down',None)
    for n in ['expanse15_truman','expanse12_raptor','expanse12_scirocco','expanse12_pella','expanse_donnager_battleship']:
        put(n,'ship_component_finished_building',['construction'])
    require(all(ids for d in maps.values() for moods in d.values() for ids in moods.values()), 'Empty voice pool')
    return maps

def expected():
    edits = {}
    for n, dialogue in dialogues().items():
        rel = 'entities/'+n+'.unit_skin'; skin = read(BASE/rel)
        skin['skin_stages'][0]['sounds']['dialogue'] = dialogue; edits[rel] = skin
    meta = read(BASE/'.mod_meta_data')
    meta.update(display_name='The Expanse — 0.17 FLEET VOICES',display_version='0.17.0',
        short_description='Distinct fleet introductions, UNN crew responses and normalized ship dialogue.',
        long_description='Complete 0.16 fleet and balance with 23 normalized voice recordings. Load alone as TEC Enclave. Audio trigger, save/reload and multiplayer listening checks remain for playtest; 0.16 rollback retained.')
    edits['.mod_meta_data'] = meta
    return edits

def validate():
    c = read(AUD/'checkpoint.json'); before, after = file_hashes(BASE), file_hashes(OUT)
    require(tree_hash(before) == c['tree_sha256'] and sha256(BASE.with_suffix('.zip')) == c['zip_sha256'], 'Rollback drift')
    for p,h in c['originals'].items(): require(sha256(p) == h and sha256(ORIG/Path(p).name) == h, 'Original drift')
    generated = read(AUD/'generated-hashes.json'); edits = expected()
    require(set(after)-set(before) == {'sounds/'+p for p in generated}, 'Unexpected added files')
    require(not set(before)-set(after), 'Deleted baseline files')
    for p,h in before.items(): require(after[p] == h or p in edits or p == 'ASSET-SOURCES.md', 'Unrelated change: '+p)
    for p,d in edits.items(): require(read(OUT/p) == d, 'Unexpected definition change: '+p)
    for p,h in generated.items(): require(after['sounds/'+p] == h == sha256(DERIVED/'sounds'/p), 'Measured audio changed')
    for row in read(AUD/'audio-intake.json')['records']:
        if 'wav_sha256' in row: require(sha256(DERIVED/'wav'/(row['id']+'.wav')) == row['wav_sha256'], 'WAV drift')
    resolver = AmunResolver(OUT,GAME); schemas=[]; used=set()
    for n,d in dialogues().items():
        schemas.append(schema_check(OUT/'entities'/(n+'.unit_skin'),BASE/'entities'/(n+'.unit_skin')))
        resolver.skin(n,'0.17 voice overlay')
        for event,moods in d.items():
            for mood,ids in moods.items():
                for ident in ids:
                    if ident.startswith(PREFIX):
                        used.add(ident); require(read(OUT/'sounds'/(ident+'.sound')) == PROFILE, 'Voice profile mismatch')
                        require((OUT/'sounds'/(ident+'.ogg')).is_file(), 'Missing audio')
        if n != 'expanse_donnager_battleship':
            require('expanse10_donnager_duty' not in json.dumps(d) and 'expanse10_donnager_standing_by' not in json.dumps(d), 'Shared introduction retained')
    require(used == {PREFIX+i for i in CLIPS if not i.endswith('_held')}, 'Unused or held clip included')
    require((OUT/'ASSET-SOURCES.md').read_text() == (BASE/'ASSET-SOURCES.md').read_text()+'\n'+(AUD/'asset-source-record.md').read_text(), 'Audio source record mismatch')
    return {'status':'PASS OFFLINE', 'schemas':schemas, 'references':resolver.edges, 'new_clips_used':len(used),
        'changed_existing_files':sorted(p for p in before if before[p] != after[p]), 'new_files':len(set(after)-set(before)),
        'gameplay_models_music_pdc_audio_rocinante_byte_identical':True, 'rollback_preserved':True,
        'pins':verify_pins(ROOT,GAME,SDK), 'listening_runtime_save_reload_multiplayer':'NOT RUN'}

def main(args):
    if not args.validate_only and not args.package_existing:
        checkpoint(); normalize()
        require(not OUT.exists() and not OUT.with_suffix('.zip').exists(), 'Refusing existing package')
        shutil.copytree(BASE,OUT)
        for p,d in expected().items(): write(OUT/p,d)
        shutil.copytree(DERIVED/'sounds',OUT/'sounds',dirs_exist_ok=True)
        (OUT/'ASSET-SOURCES.md').write_text((BASE/'ASSET-SOURCES.md').read_text()+'\n'+(AUD/'asset-source-record.md').read_text())
        write(AUD/'dialogue-map.json',dialogues())
    write(AUD/'package-validation.json',validate())
    if args.validate_only: print('PASS OFFLINE 0.17'); return
    archive=OUT.with_suffix('.zip'); require(not archive.exists(),'Archive already exists')
    with zipfile.ZipFile(archive,'w',zipfile.ZIP_DEFLATED) as z:
        for p in sorted(OUT.rglob('*')):
            if p.is_file():
                zi=zipfile.ZipInfo(p.relative_to(OUT).as_posix(),(2026,9,13,0,0,0)); zi.compress_type=zipfile.ZIP_DEFLATED; zi.external_attr=0o100644<<16; z.writestr(zi,p.read_bytes())
    result={'mod_id':OUT.name,**verify_zip(archive,OUT),'installed':False,'runtime':'NOT RUN'}
    write(AUD/'package-summary.json',result)
    OUT.with_suffix('.sha256').write_text(result['zip_sha256']+'  '+archive.name+'\n')
    deps=[BASE,ORIG,DERIVED,AUD/'audio-intake.json']; write(OUT.with_suffix('.dependencies.json'),list(map(str,deps)))
    write(OUT.with_suffix('.provenance.json'),provenance(archive,ROOT,deps)); print(json.dumps(result,indent=2))

if __name__ == '__main__':
    p=argparse.ArgumentParser(); g=p.add_mutually_exclusive_group(); g.add_argument('--validate-only',action='store_true'); g.add_argument('--package-existing',action='store_true'); main(p.parse_args())
