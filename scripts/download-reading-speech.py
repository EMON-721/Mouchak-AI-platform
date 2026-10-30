"""Reproducible local safetensors-only Small conversion; no remote model code."""
from pathlib import Path
import hashlib, importlib.metadata, json, os, shutil, urllib.request
ROOT=Path(__file__).resolve().parents[1]
manifest=json.loads((ROOT/'docs/audit/reading-speech-assets.json').read_text())
source_bytes=(ROOT/'docs/audit/reading-speech-source.json').read_bytes()
if hashlib.sha256(source_bytes).hexdigest()!=manifest['source_manifest_sha256']:raise RuntimeError('Source manifest checksum mismatch')
source=json.loads(source_bytes)
target=Path(os.getenv('MODEL_DIR',ROOT/'models'))/manifest['directory']
cache=ROOT/'.state/model-sources/arijitx-whisper-small-bn'

def valid(p,a):
    return not p.is_symlink() and p.is_file() and p.stat().st_size==a['bytes'] and hashlib.file_digest(p.open('rb'),'sha256').hexdigest()==a['sha256']
def verified(folder):return all(valid(folder/n,a) for n,a in manifest['assets'].items())
if verified(target):
    print('All selected Bengali Small assets already checksum verified.');raise SystemExit(0)
for name,version in [('torch','2.9.0+cpu'),('transformers','4.56.2'),('ctranslate2','4.8.4'),('tokenizers','0.22.2'),('safetensors','0.8.0')]:
    if importlib.metadata.version(name)!=version:raise RuntimeError('Use isolated pinned conversion environment: '+name)
cache.mkdir(parents=True,exist_ok=True)
for name,a in source['assets'].items():
    if name.endswith('.bin') or '/' in name:raise RuntimeError('Unsafe model source')
    p=cache/name
    if valid(p,a):continue
    tmp=p.with_suffix(p.suffix+'.partial')
    try:
        with urllib.request.urlopen(a['url'],timeout=120) as remote,tmp.open('wb') as out:
            count=0
            while chunk:=remote.read(1024*1024):
                count+=len(chunk)
                if count>a['bytes']:raise RuntimeError('Source too large: '+name)
                out.write(chunk)
        if not valid(tmp,a):raise RuntimeError('Source checksum mismatch: '+name)
        tmp.replace(p)
    finally:tmp.unlink(missing_ok=True)
config=json.loads((cache/'config.json').read_text())
if config.get('d_model')!=768 or config.get('encoder_layers')!=12 or config.get('decoder_layers')!=12:raise RuntimeError('Expected Whisper Small architecture')
from transformers import AutoTokenizer
from ctranslate2.converters import TransformersConverter
# Save only the backend tokenizer; never rewrite original source metadata/config.
tokenizer=AutoTokenizer.from_pretrained(cache,local_files_only=True,trust_remote_code=False)
tmp=target.with_name(target.name+'.building')
if tmp.exists():raise RuntimeError('Previous conversion directory exists; inspect it before retrying')
tmp.parent.mkdir(parents=True,exist_ok=True)
TransformersConverter(str(cache),load_as_float16=True,copy_files=['preprocessor_config.json'],trust_remote_code=False).convert(str(tmp),quantization='float16')
tokenizer.backend_tokenizer.save(str(tmp/'tokenizer.json'))
# Canonical JSON removes Rust map-order variation between clean converter runs.
tp=tmp/'tokenizer.json'
tp.write_text(json.dumps(json.loads(tp.read_text()),ensure_ascii=False,sort_keys=True,separators=(',',':'))+'\n')
if not verified(tmp):
    actual={n:{'bytes':(tmp/n).stat().st_size,'sha256':hashlib.file_digest((tmp/n).open('rb'),'sha256').hexdigest()} for n in manifest['assets'] if (tmp/n).is_file()}
    print(json.dumps(actual,indent=2));raise RuntimeError('Conversion checksum differs; existing runtime untouched')
if target.exists():
    previous=target.with_name(target.name+'.previous')
    if previous.exists():raise RuntimeError('Previous runtime preserved; inspect before replacing again')
    target.replace(previous)
tmp.replace(target)
print('Verified pinned Bengali Whisper Small conversion. No production/child release approval.')
