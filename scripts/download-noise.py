"""Acquire only checksum-pinned official Apache-2.0 YAMNet model assets."""
from pathlib import Path
import hashlib, json, os, urllib.request
ROOT=Path(__file__).resolve().parents[1]
manifest=json.loads((ROOT/'docs/audit/noise-assets.json').read_text())
target=Path(os.getenv('MODEL_DIR',ROOT/'models'))/'yamnet'
target.mkdir(parents=True,exist_ok=True)
def valid(name):
    p=target/name; asset=manifest['assets'][name]
    return p.is_file() and p.stat().st_size==asset['bytes'] and hashlib.sha256(p.read_bytes()).hexdigest()==asset['sha256']
def save(name,data):
    asset=manifest['assets'][name]
    if len(data)!=asset['bytes'] or hashlib.sha256(data).hexdigest()!=asset['sha256']: raise RuntimeError('Noise asset checksum mismatch: '+name)
    temporary=target/(name+'.partial');temporary.write_bytes(data);temporary.replace(target/name)
if not valid('classification.tflite'):
    asset=manifest['assets']['classification.tflite']
    # Public first-party Google Codelabs release, pinned by commit and by the
    # original model's exact byte count/hash. Never substitute a newer model or
    # try credentials, browser cookies or alternate authenticated download paths.
    with urllib.request.urlopen(asset['url'],timeout=120) as source:
        save('classification.tflite',source.read(asset['bytes']+1))
if not valid('class_map.csv'):
    with urllib.request.urlopen(manifest['assets']['class_map.csv']['url'],timeout=60) as source: save('class_map.csv',source.read(20000))
print('Verified official YAMNet model and 521-class map; Bangladesh production evaluation remains unpassed.')
