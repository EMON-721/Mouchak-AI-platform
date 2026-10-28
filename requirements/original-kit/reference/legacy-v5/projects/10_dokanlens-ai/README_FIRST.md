# DokanLens AI — V5 Work package

Use `MASTER_PROMPT_V5.md` as a single stand-alone prompt. It contains all new V5 requirements followed by the entire prior original prompt without changing it. Previous extra files are under `ORIGINAL_SUPPORTING_FILES/`.

- Project number: 10
- Existing codebase upgrade: True
- GitHub suggestion: `dokanlens-ai` (never presume repo exists)
- Required real models: Tesseract OCR with ben+eng language packs, torchvision pretrained MobileNetV3/EfficientNet-B0 feature backbone, sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2, scikit-learn HistGradientBoostingRegressor / RandomForestRegressor
- Local Bangladesh data: Original BD product alias catalog + opted-in retailer shelf photos + BSTI links
- No government dataset payload downloaded in this ZIP.
- Model checkpoint weights are not bundled. Work needs permitted download/inference runtime.

Check `MODEL_IMPLEMENTATION_SPEC.json` and `DATASET_SOURCE_REGISTRY.json`. See `GITHUB_PUSH_AND_CI.md` for repo workflow.
