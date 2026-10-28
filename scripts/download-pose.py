"""Fetch only pinned public model assets. Test photo stays outside source/Git."""

import argparse, hashlib, json, os, urllib.request
from pathlib import Path

root = Path(__file__).resolve().parents[1]
p = argparse.ArgumentParser()
p.add_argument("--test-fixture", action="store_true")
args = p.parse_args()
manifest = json.loads((root / "docs/audit/pose-assets.json").read_text())
target = Path(os.getenv("MODEL_DIR", root / "models")) / "pose"
target.mkdir(parents=True, exist_ok=True)
for asset in manifest["assets"]:
    if asset["kind"] == "test_fixture" and not args.test_fixture:
        continue
    path = target / asset["file"]
    if (
        path.exists()
        and hashlib.sha256(path.read_bytes()).hexdigest() == asset["sha256"]
    ):
        continue
    temp = path.with_suffix(path.suffix + ".partial")
    try:
        with urllib.request.urlopen(asset["url"], timeout=120) as source, temp.open(
            "wb"
        ) as out:
            while chunk := source.read(1024 * 1024):
                out.write(chunk)
        if (
            temp.stat().st_size != asset["bytes"]
            or hashlib.sha256(temp.read_bytes()).hexdigest() != asset["sha256"]
        ):
            raise RuntimeError("Pose asset checksum mismatch: " + asset["file"])
        temp.replace(path)
        print("Verified", asset["file"])
    finally:
        temp.unlink(missing_ok=True)
print("Pose assets acquired; production evaluation remains a separate unmet gate.")
