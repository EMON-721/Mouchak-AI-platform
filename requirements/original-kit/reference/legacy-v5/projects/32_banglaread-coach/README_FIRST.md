# BanglaRead Coach — V5 Work package

Use `MASTER_PROMPT_V5.md` as a single stand-alone prompt. It contains all new V5 requirements followed by the entire prior original prompt without changing it. Previous extra files are under `ORIGINAL_SUPPORTING_FILES/`.

- Project number: 32
- Existing codebase upgrade: True
- GitHub suggestion: `banglaread-coach` (never presume repo exists)
- Required real models: openai/whisper-small, sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2
- Local Bangladesh data: 120 original passages and words already in V3, OpenSLR53 CC-BY-SA 4.0 terms; NCTB index as reference only
- No government dataset payload downloaded in this ZIP.
- Model checkpoint weights are not bundled. Work needs permitted download/inference runtime.

Check `MODEL_IMPLEMENTATION_SPEC.json` and `DATASET_SOURCE_REGISTRY.json`. See `GITHUB_PUSH_AND_CI.md` for repo workflow.
