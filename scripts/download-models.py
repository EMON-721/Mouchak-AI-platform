"""Download only recorded public model/font assets, with verified checksums."""

from pathlib import Path
import urllib.request, hashlib, json, shutil, os

root = Path(__file__).resolve().parents[1]
manifest = json.loads((root / "docs/audit/model-downloads.json").read_text())
for asset in manifest:
    if asset["status"] != "downloaded":
        continue
    path = root / "models" / asset["asset"]
    path.parent.mkdir(exist_ok=True, parents=True)
    if (
        path.exists()
        and hashlib.sha256(path.read_bytes()).hexdigest() == asset["sha256"]
    ):
        continue
    temporary = path.with_suffix(path.suffix + ".partial")
    try:
        with urllib.request.urlopen(
            asset["url"], timeout=120
        ) as source, temporary.open("wb") as target:
            shutil.copyfileobj(source, target)
        if hashlib.sha256(temporary.read_bytes()).hexdigest() != asset["sha256"]:
            raise RuntimeError("Model checksum mismatch: " + asset["asset"])
        temporary.replace(path)
        print("Downloaded and verified", asset["asset"])
    finally:
        temporary.unlink(missing_ok=True)
for name in ["eng", "osd"]:
    for directory in [
        "/usr/share/tesseract-ocr/5/tessdata",
        "/usr/share/tessdata",
        "/usr/share/tesseract-ocr/4.00/tessdata",
    ]:
        source = Path(directory) / (name + ".traineddata")
        if source.exists():
            shutil.copy2(source, root / "models" / source.name)
            break
print("Model acquisition complete. Production evaluation is a separate gate.")
