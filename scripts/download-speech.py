from pathlib import Path
import urllib.request, json, hashlib

root = Path(__file__).resolve().parents[1]
directory = root / "models/whisper-tiny"
directory.mkdir(exist_ok=True)
base = "https://huggingface.co/Systran/faster-whisper-tiny/resolve/main/"
manifest = []
for name in ["config.json", "model.bin", "tokenizer.json", "vocabulary.txt"]:
    target = directory / name
    if not target.exists():
        with urllib.request.urlopen(base + name, timeout=90) as source, target.open(
            "wb"
        ) as out:
            while block := source.read(1024 * 1024):
                out.write(block)
    manifest.append(
        {
            "asset": "whisper-tiny/" + name,
            "url": base + name,
            "status": "downloaded",
            "sha256": hashlib.sha256(target.read_bytes()).hexdigest(),
            "bytes": target.stat().st_size,
        }
    )
    print(name, target.stat().st_size, flush=True)
(root / "docs/audit/speech-downloads.json").write_text(json.dumps(manifest, indent=2))
# Public-domain U.S. government speech test distributed with the official
# Whisper repository. This tests runtime English ASR, never Bangla accuracy.
u = "https://raw.githubusercontent.com/openai/whisper/main/tests/jfk.flac"
target = root / "tests/generated/jfk.flac"
target.parent.mkdir(exist_ok=True)
with urllib.request.urlopen(u, timeout=30) as r:
    target.write_bytes(r.read())
