# CivicForm AI — V5 Work package

Use `MASTER_PROMPT_V5.md` as a single stand-alone prompt. It contains all new V5 requirements followed by the entire prior original prompt without changing it. Previous extra files are under `ORIGINAL_SUPPORTING_FILES/`.

- Project number: 27
- Existing codebase upgrade: False
- GitHub suggestion: `civicform-ai` (never presume repo exists)
- Required real models: Tesseract OCR with ben+eng language packs, sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2, rank-bm25 lexical retrieval
- Local Bangladesh data: Bangladesh National Portal public service pages and owner-written process summaries
- No government dataset payload downloaded in this ZIP.
- Model checkpoint weights are not bundled. Work needs permitted download/inference runtime.

Check `MODEL_IMPLEMENTATION_SPEC.json` and `DATASET_SOURCE_REGISTRY.json`. See `GITHUB_PUSH_AND_CI.md` for repo workflow.
