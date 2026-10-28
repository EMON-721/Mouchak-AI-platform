# RoadFix BD — V5 Work package

Use `MASTER_PROMPT_V5.md` as a single stand-alone prompt. It contains all new V5 requirements followed by the entire prior original prompt without changing it. Previous extra files are under `ORIGINAL_SUPPORTING_FILES/`.

- Project number: 22
- Existing codebase upgrade: False
- GitHub suggestion: `roadfix-bd` (never presume repo exists)
- Required real models: torchvision pretrained MobileNetV3/EfficientNet-B0 feature backbone, sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2
- Local Bangladesh data: Opt-in local road photos and road authority public statistics
- No government dataset payload downloaded in this ZIP.
- Model checkpoint weights are not bundled. Work needs permitted download/inference runtime.

Check `MODEL_IMPLEMENTATION_SPEC.json` and `DATASET_SOURCE_REGISTRY.json`. See `GITHUB_PUSH_AND_CI.md` for repo workflow.
