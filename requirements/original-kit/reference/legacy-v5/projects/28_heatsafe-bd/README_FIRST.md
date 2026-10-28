# HeatSafe BD — V5 Work package

Use `MASTER_PROMPT_V5.md` as a single stand-alone prompt. It contains all new V5 requirements followed by the entire prior original prompt without changing it. Previous extra files are under `ORIGINAL_SUPPORTING_FILES/`.

- Project number: 28
- Existing codebase upgrade: False
- GitHub suggestion: `heatsafe-bd` (never presume repo exists)
- Required real models: statsmodels ExponentialSmoothing baseline + prediction intervals when validated, sklearn.ensemble.IsolationForest, sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2
- Local Bangladesh data: BMD weather observation public web pages where allowed; user device records only with consent
- No government dataset payload downloaded in this ZIP.
- Model checkpoint weights are not bundled. Work needs permitted download/inference runtime.

Check `MODEL_IMPLEMENTATION_SPEC.json` and `DATASET_SOURCE_REGISTRY.json`. See `GITHUB_PUSH_AND_CI.md` for repo workflow.
