# BanglaRead speech continuation

This adds a real, bounded **local adult self-recording experiment** to BanglaRead Coach. It does not release the original child-focused advanced module. Existing authored reading, typed practice, tap/reflection, comprehension, history and privacy controls remain intact. Public visitors still have no registration/login/profile. Operator login and current TOTP MFA remain required for model controls. Production hosting remains paused.

## Implemented flow

Choose a currently available passage, open the optional speech panel, select your own 1–30 second 16-bit PCM WAV (mono/stereo, 8–96 kHz, at most 10 MiB), and explicitly confirm adult self-recording consent. The backend runs the actual local Bengali Small model. Review the text and optional word times/alignment; only after separately checking the review box can text be copied into the existing typed practice form. Its existing processing consent is still required to save a practice result. There is no automatic submission or transfer.

The speech endpoint creates no voice asset, tool run, transcript record or voice training record. Request bytes and results are not cached. Multipart processing may use temporary framework spooling during the request; the file is closed after every handler outcome. Normal application request parsing/lifetime is not a promise of forensic memory erasure. Do not configure request-body logging at a proxy. The UI keeps results in component memory and aborts requests on passage/session changes; it writes no speech content to browser storage.

Silence and extensive clipping abstain before model loading. VAD and standard no-speech, average-log-probability and compression gates reject uncertain segments; a Bengali-script gate refuses damaged/foreign-script output. These heuristics do not establish calibrated confidence or complete noise robustness. Accepted words carry actual model/DTW time alignment; substitution/missing/extra labels remain uncertain ASR observations, never child ability, phoneme diagnosis or clinical pronunciation scores. Typed and tap modes remain usable when speech is absent or refused.

## Exact model and dependencies

- Source: [arijitx/whisper-small-bn](https://huggingface.co/arijitx/whisper-small-bn), pinned revision `061641b318fca06b46bff83dd9500037b2aac764`. This is a Bengali fine-tune of the **Whisper Small** architecture (768 hidden dimension, 12 encoder and 12 decoder layers), not the existing unrelated Tiny baseline.
- The author's pinned card states Apache-2.0 and reports Common Voice 11 Bengali and OpenSLR53 training. That statement does not independently clear all training rights or pretraining overlap. Production rights/field approval is false.
- Source files and safetensors are checked against exact bytes/SHA-256 in `docs/audit/reading-speech-source.json`. Source-manifest SHA is pinned in `reading-speech-assets.json`. No pickle model, remote Python or `trust_remote_code=True` is used.
- An isolated converter uses Torch 2.9.0+cpu, Transformers 4.56.2, CTranslate2 4.8.4, tokenizers 0.22.2 and safetensors 0.8.0. It emits FP16 CTranslate2 weights; runtime loads actual CPU **int8**. The tokenizer JSON is canonicalized (sorted keys, compact UTF-8, final newline) to remove map serialization order variation. Two local conversions matched all five final byte/hash pins.
- Runtime keeps faster-whisper 1.2.1 and pins CTranslate2 4.8.4 and **PyAV 18.1.0**. PyAV 19 removes the `metadata_errors` argument used by this faster-whisper release; [upstream issue](https://github.com/SYSTRAN/faster-whisper/issues/1589). Conversion dependencies are intentionally outside the API environment: its tokenizer version serves existing ONNX code.
- Actual model load checks every asset hash. Loaded-cache calls reject changed file signatures/symlinks; mount weights read-only. Availability reports presence separately from load-time checksum verification.
- Decoding forces Bengali transcription, beam 3, temperature 0, no previous-text conditioning, VAD, no timestamp-token generation and actual word timestamps, maximum 440 new tokens. No expected passage/reference is provided to the decoder. Reference text is used only after inference for edit alignment or benchmark metrics.

## Dataset, attribution and actual evaluation

The additional legally accessible benchmark is [OpenSLR37 Bangladesh Bengali](https://www.openslr.org/37/), not an assertion that all original OpenSLR53 requirements have been fulfilled. Google collected the source. Source/derived benchmark material is **CC-BY-SA-4.0**, including the public references reproduced in the evaluation report; this does not change the application code's licence. Full licence travels with prepared clips.

Please cite Keshan Sodimana, Knot Pipatsrisawat, Linne Ha, Martin Jansche, Oddur Kjartansson, Pasindu De Silva and Supheakmungkol Sarin, “A Step-by-Step Process for Building TTS Voices Using Open Source Data and Framework for Bangla, Javanese, Khmer, Nepali, Sinhala, and Sundanese,” SLTU 2018, pp. 66–70, [DOI 10.21437/SLTU.2018-14](https://doi.org/10.21437/SLTU.2018-14). Copyright Google 2015–2018, as stated in the source licence.

`prepare-bn-speech.py` downloads the pinned 586,288,792-byte `bn_bd.zip`, verifies publisher MD5 `5f7b0a1de746d2ac3541c12883b3117f` and SHA-256 `ea2e57ee593ac91e40cd72f91100aa6e1bffbaec465ba1678923ecf1f4efade8`, and verifies the original transcript index and full source licence. It reads only known regular data members without extracting arbitrary archive paths. Among **1,891** rows, **1,520** meet the fixed 3–8 second mono PCM benchmark criteria; **371** are outside those bounds. Two clips per six source speaker prefixes are selected by SHA-256 of source clip ID **before inference**, giving twelve clips. No transcript-based selection, reference prompt or training is performed.

Actual current evaluation in `docs/audit/reading-speech-evaluation.json`:

| Measure | Observed value |
|---|---|
| Source rows / benchmark clips / source speaker groups | 1,891 / 12 / 6 |
| Accepted clips | 12 (all included in aggregate denominator) |
| Word error rate | **38 / 103 = 36.89%** |
| Character error rate | **157 / 623 = 25.20%** |
| Unicode grapheme error rate | **75 / 400 = 18.75%** |
| Local full benchmark time | 212.38 seconds |

NFC, Bengali-digit conversion, joiner removal and Unicode punctuation/symbol removal precede edit distance; graphemes use Unicode `\X`. Insertions can make error rates exceed 100%, so rates are not clamped. Every per-clip reference, actual accepted hypothesis, refusal status and error numerator/denominator is retained in the report. The benchmark is small and contains substitutions and repetitions. This is **not** independent Bangladesh field validation, a child/guardian holdout or human agreement measurement. Age, gender and region are unknown; pretraining overlap has not been independently excluded. The model author's own WER is not substituted for this measurement.

Raw public audio, the 586 MB archive, model weights, converted weights, caches and private runtime data are ignored by Git. Scripts reconstruct them; do not commit user recordings or upload a source corpus as if it had a new permissive licence.

## Portable setup

Use the normal Node/Python setup from README first. Then, from the repository root:

```bash
python3 -m venv .state/conversion-venv
.state/conversion-venv/bin/pip install -r requirements-reading-conversion.txt
.state/conversion-venv/bin/python scripts/download-reading-speech.py
.venv/bin/python scripts/prepare-bn-speech.py
OMP_NUM_THREADS=2 OPENBLAS_NUM_THREADS=2 .venv/bin/python scripts/evaluate-reading-speech.py
ENABLE_EXPERIMENTAL_READING_ASR=1 pnpm dev
```

The downloader skips already verified converted assets, preserves an existing runtime as `.previous` on a verified replacement and refuses to overwrite a second previous runtime or leftover `.building` output. Inspect such directories rather than deleting a working runtime. Conversion needs roughly 1 GB source download plus CPU Torch and model conversion space; prepared public speech source is another 586 MB. On Windows, use the corresponding `Scripts/python.exe`/`Scripts/pip.exe` paths. Keep the converter environment separate from `.venv`.

Optional Linux/Docker local setup:

```bash
docker compose -f deploy/compose.local.yaml --profile experimental-speech run --build --rm speech-model-init
ENABLE_EXPERIMENTAL_READING_ASR=1 docker compose -f deploy/compose.local.yaml up --build
```

The optional converter image writes only model/source volumes; the API image contains no Torch/Transformers. This profile is a source template until its optional converter image itself has been built and run; do not infer that from ordinary Compose syntax or API-image CI success. There is no hosting-provider lock-in or new live service. ASR is a bounded direct request, not a durable speech queue; a busy per-process worker returns 429. Cold-start latency and deployment-specific timeouts/concurrency still need separate service validation. No Netlify/hosted latency SLA is asserted.

## Operator workflow and API

`/admin/reading-speech` shows the selected manifest, actual stored benchmark, runtime opt-in state, limitations and policy. Only `models` permission with fresh MFA can inspect or change it. Every disable/restore requires a reason and current revision, writes immutable policy history and a chained audit event, and uses a PostgreSQL transaction advisory lock. Concurrent stale changes return 409. Restore permits the existing **local opt-in** only; it cannot enable production, child voice or a stable release.

| Route | Exact scope |
|---|---|
| `GET /api/reading/speech/status` | Nonpersonal availability, opt-in and module/operator disable state |
| `POST /api/reading/speech/transcribe` | Visitor cookie + CSRF; multipart `file`, `recording_subject=self_adult`, `adult_processing_consent=true`, optional current approved passage ID |
| `GET /api/admin/reading-speech` | Model-role + current MFA; no private voice list |
| `POST /api/admin/reading-speech/policy` | Same role/MFA; state `disabled` or `experimental`, `expected_revision`, reason 10–1,000 characters |

Actual incoming multipart bytes are counted before parsing, including bodies without Content-Length; the 10 MiB file limit is separately checked. No new database schema or relaxed grants are required. The existing configuration/audit tables and private API transport protections are used.

## Remaining original requirements

Full BanglaRead completion remains **false**: verified guardian/child workflow and representative consented child field evaluation; independent teacher/rater agreement, age/gender/region variation evidence; original 120 passages/questions' human content approval; chapter/word embedding/adaptive/phoneme-review/parent/offline workflows and original broader acceptance criteria. All 120 original seed items marked awaiting review remain preserved in the unchanged requirements kit; this work does not silently approve or relicense them. OpenSLR37 complements rather than erases the original SLR53/Common Voice/NCTB rights and dataset requirements. The other 49 advanced-module gaps are preserved in the progress checklist.
