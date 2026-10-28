# HospitalBillGuard BD — V5 Work package

Use `MASTER_PROMPT_V5.md` as a single stand-alone prompt. It contains all new V5 requirements followed by the entire prior original prompt without changing it. Previous extra files are under `ORIGINAL_SUPPORTING_FILES/`.

- Project number: 29
- Existing codebase upgrade: False
- GitHub suggestion: `hospitalbillguard-bd` (never presume repo exists)
- Required real models: Tesseract OCR with ben+eng language packs, sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2, sklearn.ensemble.IsolationForest
- Local Bangladesh data: Anonymized consented patient bills and approved public hospital fee schedules
- No government dataset payload downloaded in this ZIP.
- Model checkpoint weights are not bundled. Work needs permitted download/inference runtime.

Check `MODEL_IMPLEMENTATION_SPEC.json` and `DATASET_SOURCE_REGISTRY.json`. See `GITHUB_PUSH_AND_CI.md` for repo workflow.
