# Data and model provenance

## Input kit

All 778 source files were read as bytes and decoded, JSON/CSV files were parsed, and source checksums were verified with no mismatch. There are 695 distinct byte contents. The audit records paths, hashes, duplicates, parsed status, headings and requirement-bearing lines. The 16,269 extracted entries are a traceability index; `NOT_VERIFIED` is deliberately not a completion claim. The original 430 acceptance scenarios remain preserved.

## Government and external data

The kit lists 244 candidate source entries. No entry is assumed licensed because it is public. The Bangladesh Open Data terms URL returned HTTP 403 during acquisition checks. No government dataset was ingested, no restricted page was scraped and no real-world observations were fabricated. The UI and database preserve candidate/rights-review state. The source-review console requires asset-level evidence; sensitive training/reuse now requires two independent asset-level reviews; schema-specific publication and evaluation remain separate unfinished gates. No real source was approved by synthetic test reviews. CSV imports currently stop at an encrypted, reversible staging step and do not silently publish a corpus.

## Original data

`data/authored/learning.json` contains five project-authored Bengali/English starter passages, explicitly CC0, nonofficial and dated. The original kit's ten authored accessibility phrases supply the phraseboard. Empty market/property/wage templates remain empty. Tests use clearly synthetic or originally drawn fixtures; they are not production observations or local accuracy benchmarks.

## Real runtimes

- Tesseract 5 with Bengali/English language data. A newly rendered, owned Bengali/Latin numeric image was processed. This establishes runtime operation, not a representative character-error benchmark.
- `Xenova/paraphrase-multilingual-MiniLM-L12-v2`, quantized ONNX, with the original sentence-transformers model identified as Apache-2.0 in model metadata. It produces real 384-dimensional embeddings. BM25 uses stop-word-filtered lexical evidence; the current answer is an exact cited passage. The threshold is experimental, not a calibrated accuracy claim.
- OpenCV feature registration and image-difference statistics. Originally drawn repeated patterns pass; blank views abstain. No riverbank erosion or water extent is inferred.
- `sklearn.IsolationForest`: experimental private-baseline adapter, at least 25 confirmed measurements. Synthetic mechanics tests are not Bangladesh evaluation.
- `Systran/faster-whisper-tiny`: quantized CPU transcription adapter, MIT metadata. The public-domain JFK test distributed by the official Whisper repository was transcribed; Bengali holdout evaluation is not complete. Child audio is not enabled. The production speech endpoint remains disabled.

Model-download URLs, byte counts and checksums are in `docs/audit/model-downloads.json` and `speech-downloads.json`. Weights are excluded from Git/source ZIP; the checksum-verifying acquisition scripts recreate them. Do not mark a checkpoint stable solely because its files exist.

## Unfinished model/data work

The entire original model registry remains authoritative and preserved. Local labelled vision datasets, semantic medicine/facility directories, statutory legal/labour collections, NCTB permissions, pharmacy stock freshness, weather/bulletin ingestion and reviewed Bangladesh holdouts remain dependencies. Specialist classification, diagnosis, legal certification, compensation, official tariffs, future forecasts and real-time availability are never manufactured in their absence.

## Attributed local V3 additions

`data/legacy/banglaread-passages.json` retains 12 original passages from the user-owned BanglaRead V3 static snapshot, with CC-BY-4.0, contributor attribution and original date 2026-10-25 attached. IDs are namespaced `legacy:`; no official curriculum provenance or model evaluation is inferred. These are used for reflection, not added silently to the existing retrieval collection.

`data/legacy/commodity-dictionary.json` preserves 81 original reference entries from BazarCompare V3. It contains product names/aliases/units, no market prices. Every comparison uses private, dated user observations; no synthetic observation is presented as real market data. Complete source snapshots and file hashes are in `reference/legacy-snapshots/` and `docs/audit/legacy-snapshot-manifest.json`. Local source files contain no live account or user database export.
