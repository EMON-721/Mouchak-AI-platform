from pathlib import Path
import json,csv
root=Path(__file__).resolve().parents[1]
cfg=json.loads((root/'config/MODULES_50.json').read_text(encoding='utf-8'))
mods=cfg['modules']
assert cfg['total']==len(mods)==50
assert [m['number'] for m in mods]==list(range(1,51))
assert len(set(m['slug'] for m in mods))==50
assert len(set(m['route'] for m in mods))==50
assert not {'bonnaproof-ai','accesspath-ai'}&set(m['slug'] for m in mods)
assert all((root/'logos'/f"{m['number']:02d}_{m['slug']}.svg").exists() for m in mods)
models=json.loads((root/'model/MODEL_REGISTRY.json').read_text())['models']
assert len(models)==50
assert set(m['slug'] for m in mods)==set(m['module'] for m in models)
for m in mods[35:]:
 assert (root/'modules-36-to-50'/f"{m['number']:02d}_{m['slug']}_MASTER_SPEC.md").exists()
 assert (root/'modules-36-to-50'/f"{m['number']:02d}_{m['slug']}_PROJECT_SPEC.json").exists()
 assert (root/'modules-36-to-50'/f"{m['number']:02d}_{m['slug']}_INPUT_SCHEMA.csv").exists()
rows=list(csv.DictReader((root/'datasets/SOURCE_REGISTRY.csv').open(encoding='utf-8-sig')))
assert len(rows)>=207+30
assert (root/'reference/central-v1-35/ORIGINAL_CENTRAL_35_README.md').exists()
assert (root/'reference/legacy-v5/ALL_32_MASTER_PROMPTS_V5.md').exists()
print(f'PASSED: {len(mods)} modules, {len(models)} model specs, {len(rows)} candidate source entries, {len(list((root/"logos").glob("*.svg")))} custom SVG marks')
