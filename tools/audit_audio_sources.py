"""Read-only local sound intake. Writes metadata, never copies/converts audio."""
from pathlib import Path
import hashlib, json, wave, subprocess, shutil, xml.etree.ElementTree as ET
from collections import Counter

ROOT = Path(__file__).resolve().parents[1]
LIB = ROOT.parent / 'SteamLibrary/steamapps'
WORKSHOP = LIB / 'workshop/content/244850'
GAME = LIB / 'common/Sins2'
DEFINITIONS = {
    '2394430829': 'Data/AryxLynxonEpsteinDrives_Audio.sbc',
    '2036872575': 'Data/Audio_PDC.sbc',
    '2860576438': 'Data/Audio/AudioImpakt.sbc',
}

def sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()

def main():
    result = {'scope': 'selected local candidates, not exhaustive; no listening/conversion/runtime test',
              'workshop_root': str(WORKSHOP), 'sources': [], 'runtime': 'NOT RUN'}
    for ident, definition in DEFINITIONS.items():
        root = WORKSHOP / ident
        if not (root / definition).is_file():
            raise SystemExit(f'BLOCKED: missing local definition {root / definition}')
        entry = {'workshop_id': ident, 'source_url': f'https://steamcommunity.com/sharedfiles/filedetails/?id={ident}',
                 'creator': 'not established from local metadata', 'permission': 'audio reuse not established',
                 'definition': definition, 'definition_sha256': sha(root / definition), 'files': [], 'events': []}
        for p in sorted(root.rglob('*')):
            if p.suffix.lower() not in {'.wav', '.ogg', '.xwm', '.mp3'}:
                continue
            item = {'path': str(p.relative_to(root)), 'bytes': p.stat().st_size, 'sha256': sha(p)}
            if p.suffix.lower() == '.wav':
                try:
                    with wave.open(str(p)) as w:
                        item.update(channels=w.getnchannels(), rate=w.getframerate(), sample_bytes=w.getsampwidth(),
                                    duration_seconds=round(w.getnframes()/w.getframerate(), 4))
                except (wave.Error, EOFError) as e:
                    item['header_probe'] = str(e)
            if shutil.which('ffprobe'):
                probe = subprocess.run(['ffprobe', '-v', 'error', '-show_entries',
                                        'stream=codec_name,sample_rate,channels:format=duration',
                                        '-of', 'json', str(p)], capture_output=True, text=True)
                item['ffprobe'] = json.loads(probe.stdout) if probe.returncode == 0 else {'error': probe.stderr}
            else:
                item['ffprobe'] = {'status': 'BLOCKED: ffprobe unavailable; no dependency installed'}
            entry['files'].append(item)
        for sound in ET.parse(root / definition).getroot().findall('./Sounds/Sound'):
            event = {'id': sound.findtext('./Id/SubtypeId'), 'waves': []}
            for wave_node in sound.findall('./Waves/Wave'):
                refs = {n.tag: n.text for n in wave_node}
                event['waves'].append({'type': wave_node.get('Type'), 'references': refs,
                                      'present': {k: (root / v.replace('\\', '/')).is_file() for k, v in refs.items()}})
            entry['events'].append(event)
        if (root / 'LICENSE').exists():
            entry['license_file'] = {'path': 'LICENSE', 'sha256': sha(root / 'LICENSE'),
                                     'heading': (root / 'LICENSE').read_text().splitlines()[:2],
                                     'scope': 'root GPL v3 text; per-audio authorship/scope not established'}
        result['sources'].append(entry)
    keys = Counter()
    for p in (GAME / 'sounds').glob('*.sound'):
        keys.update(json.loads(p.read_text()).keys())
    result['installed_sound_field_counts'] = dict(keys)
    result['engine_definition'] = json.loads((GAME / 'sounds/ENGINE_TECHFRIGATESHIP.sound').read_text())
    result['engine_skin_pointer'] = 'entities/trader_light_frigate.unit_skin#/skin_stages/0/sounds/move_sounds/engine'
    out = ROOT / 'audit/audio/local-source-audit.json'
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(result, indent=2) + '\n')
    print(f'Wrote {out}: {sum(len(s["files"]) for s in result["sources"])} media headers/hashes; no media copied')

if __name__ == '__main__':
    main()
