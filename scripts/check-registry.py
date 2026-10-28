from pathlib import Path
import json, hashlib, csv

root = Path(__file__).resolve().parents[1]
kit = root / "requirements/original-kit"
x = json.loads((root / "packages/module-registry/catalogue.json").read_text())
modules = x["modules"]
assert len(modules) == 50
assert len({m["slug"] for m in modules}) == 50
assert [m["number"] for m in modules] == list(range(1, 51))
assert sum(m["existing_site"] for m in modules) == 4
assert not any("bonnaproof" in m["slug"] or "accesspath" in m["slug"] for m in modules)
for m in modules:
    assert m["route"] == "/tools/" + m["slug"]
    assert (root / "public" / m["logo"].lstrip("/")).is_file()
    assert m["description_bn"]
    assert m["description_en"]
    assert m["full_module_complete"] is False
for f in json.loads((kit / "FILE_MANIFEST_SHA256.json").read_text()):
    assert hashlib.sha256((kit / f["file"]).read_bytes()).hexdigest() == f["sha256"], f[
        "file"
    ]
print(
    "50 exact modules, 50 identities, 4 legacy flags, bilingual descriptions and all source checksums verified."
)
