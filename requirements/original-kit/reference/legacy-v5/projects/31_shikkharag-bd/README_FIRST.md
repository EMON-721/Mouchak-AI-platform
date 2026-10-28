# ShikkhaRAG BD — V5 Work package

Use `MASTER_PROMPT_V5.md` as a single stand-alone prompt. It contains all new V5 requirements followed by the entire prior original prompt without changing it. Previous extra files are under `ORIGINAL_SUPPORTING_FILES/`.

- Project number: 31
- Existing codebase upgrade: False
- GitHub suggestion: `shikkharag-bd` (never presume repo exists)
- Required real models: sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2, rank-bm25 lexical retrieval, Qwen/Qwen2.5-1.5B-Instruct, Tesseract OCR with ben+eng language packs
- Local Bangladesh data: NCTB 2026 book INDEX/syllabus reference only pending reuse rights; original lesson examples + admin-approved education sources; BDNC with terms check
- No government dataset payload downloaded in this ZIP.
- Model checkpoint weights are not bundled. Work needs permitted download/inference runtime.

Check `MODEL_IMPLEMENTATION_SPEC.json` and `DATASET_SOURCE_REGISTRY.json`. See `GITHUB_PUSH_AND_CI.md` for repo workflow.
