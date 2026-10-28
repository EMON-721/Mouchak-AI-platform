# LivestockCare Log — V5 Work package

Use `MASTER_PROMPT_V5.md` as a single stand-alone prompt. It contains all new V5 requirements followed by the entire prior original prompt without changing it. Previous extra files are under `ORIGINAL_SUPPORTING_FILES/`.

- Project number: 26
- Existing codebase upgrade: False
- GitHub suggestion: `livestockcare-log` (never presume repo exists)
- Required real models: sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2, sklearn.ensemble.IsolationForest
- Local Bangladesh data: DLS public livestock reference, consented herd logs and vet-authored original notes
- No government dataset payload downloaded in this ZIP.
- Model checkpoint weights are not bundled. Work needs permitted download/inference runtime.

Check `MODEL_IMPLEMENTATION_SPEC.json` and `DATASET_SOURCE_REGISTRY.json`. See `GITHUB_PUSH_AND_CI.md` for repo workflow.
