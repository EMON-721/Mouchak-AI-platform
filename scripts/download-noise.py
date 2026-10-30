"""Acquire only checksum-pinned official Apache-2.0 YAMNet model assets."""
from pathlib import Path
import hashlib, io, json, os, tarfile, urllib.request
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
    with urllib.request.urlopen(manifest['archive_url'],timeout=120) as source: data=source.read(32*1024*1024+1)
    if len(data)>32*1024*1024: raise RuntimeError('Noise archive exceeds bounded size')
    with tarfile.open(fileobj=io.BytesIO(data),mode='r:gz') as archive:
        # Never extract archive paths, symlinks, directories or arbitrary members.
        member=archive.getmember(manifest['archive_member'])
        if not member.isfile() or member.size!=manifest['assets']['classification.tflite']['bytes']: raise RuntimeError('Unexpected model archive member')
        save('classification.tflite',archive.extractfile(member).read(member.size+1))
if not valid('class_map.csv'):
    with urllib.request.urlopen(manifest['assets']['class_map.csv']['url'],timeout=60) as source: save('class_map.csv',source.read(20000))
print('Verified official YAMNet model and 521-class map; Bangladesh production evaluation remains unpassed.')
