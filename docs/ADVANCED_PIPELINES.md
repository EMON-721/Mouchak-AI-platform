# Advanced continuation: actual audio inference, 50-tool routing and lawful BD references

This continuation adds working pipelines to the existing platform. It does **not** certify the complete original advanced scope of any of the 50 tools. Hosting stays paused; public visitors still have no account/signup/profile. Existing private records, requirements and model release gates are preserved.

## NoiseTrace: actual YAMNet, with explicit local experimental opt-in

`services/model_worker/noise_runtime.py` runs the official **google/yamnet/classification-tflite/1** checkpoint using `ai-edge-litert==2.1.0`, two CPU threads and a lock around interpreter tensors. It verifies the exact model/class-map hashes, input/output signature, finite score bounds and recording shape. It is neither a mock endpoint nor a remote AI API. Runtime health separately reports verified weights, runtime package presence and whether an interpreter has actually loaded in that process.

```bash
python scripts/download-noise.py
# Local development only; keep production disabled until the real release gate passes.
# In the owner's private development environment: ENABLE_EXPERIMENTAL_NOISE=1
```

The exact official model URL, Apache-2.0 evidence, bytes and hashes are in `docs/audit/noise-assets.json`. The downloader reads only the expected bounded archive member; it does not extract archive paths. Class-map CSV is pinned to TensorFlow's source commit. Model licensing is not a licence to redistribute the original AudioSet recordings; this project downloads none of those recordings.

The user explicitly chooses `signal` or `events`. Signal statistics remain available independently. Events require opt-in, checksum-verified assets, operator policy and the existing private-processing consent. **Production event inference stays disabled**, including if the environment opt-in is set; installing weights is not Bangladesh validation. No unavailable model silently returns fabricated tags.

The pipeline accepts 16-bit mono/stereo PCM WAV, 0.975–60 seconds, 8–96 kHz, at most 10 MiB. It rejects malformed/truncated audio, downmixes/resamples to 16 kHz, runs 15,600-sample windows with bounded overlap, aggregates actual scores and reports reviewable temporal tags/RMS waveform. Silence, heavy clipping and low model evidence cause abstention. Scores are **uncalibrated**, never legal/environmental decibels or personal identity evidence. The original 521-class taxonomy is English; selected common labels have Bengali translations and the rest preserve their original source names. The UI makes that distinction explicit.

Owner audio and results use the existing encrypted vault, owner authorization, scanner checks, durable worker, retention and export machinery. They never enter a shared training corpus. The bilingual result studio shows actual waveform values, candidate tags and time segments. `/admin/model-operations` offers audited optimistic-revision disable/restore controls; it cannot turn on a fake stable/production status. Existing full-model/canary/holdout requirements remain separate.

Tests use owned synthetic sine/noise/silence/clipped recordings to prove **mechanics**, including real endpoint and durable-worker inference, two distinct outputs, resampling, checksum failure, consent, private isolation, policy and production refusal. They are not representative Bangladesh street recordings or an accuracy benchmark. Bangladesh annotated event macro-F1, temporal/privacy calibration, consented time-of-day anomaly modelling and reviewed redaction remain incomplete.

## All 50 tools: semantic intent launcher

`services/model_worker/launcher.py` uses the actual checksum-pinned multilingual MiniLM ONNX encoder plus bounded BM25 over all 50 public tool purposes and original query examples. Only public prototype vectors are cached. The service neither saves raw queries nor forwards them to tools, trains on them, opens external links or executes an inferred action. The user reviews suggestions and chooses a destination; blocked tool cores retain their honest readiness labels.

`data/authored/launcher-intents.json` contains 50 original bilingual task pairs (100 query examples), dedicated to CC0 **only for those newly authored examples**. This does not relicense the master kit, code, logos or third-party models. The examples are development data, not real users, a representative population or independent Bangladesh holdout. Exact-name coverage is a routing/indexing sanity check. Similarity is not a calibrated probability. Low-evidence/gibberish queries abstain; urgent medical/safety language stops tool routing and directs people to appropriate help without diagnosis or invented helpline details.

`POST /api/launcher` requires the existing private browser session and write CSRF. It honors disabled tools. Ordinary lexical catalogue search remains available when the model is absent. The search UI runs semantic inference only after an explicit click. Homepage task descriptions travel to Explore through in-memory context rather than being put into query-string URLs; old explicit public catalogue `?q=` links still work. Session refresh clears the pending in-memory description.

## Bangladesh OpenStreetMap: downloaded, prepared and connected

The complete pinned Geofabrik Bangladesh extract was actually downloaded, checked against the publisher MD5 and a recorded SHA-256, and parsed with `osmium==4.3.0`. The source is the dated **2026-10-28** extract, not an invented government CSV:

- Source: <https://download.geofabrik.de/asia/bangladesh-261028.osm.pbf>
- Publisher checksum: <https://download.geofabrik.de/asia/bangladesh-261028.osm.pbf.md5>
- Source bytes: **355,896,654**; SHA-256 `59b394608adbffe28185091d637806954ddd65fd48d39ddbdf29ad90cfb1bf27`.
- **12,811,257** ways examined; **476,738** eligible non-private road ways; **32,285** named/ref-bearing rows prepared; **444,453** eligible ways had neither usable name nor ref. These omissions are disclosed, not silently invented.
- Derived canonical JSONL SHA-256: `d44f93332ec305a89be79606b3d513bd7e5b7cc1bced0c39d54060d7c76f3c52`.
- Original producer evidence, category counts and first 20 actual records: `docs/audit/bd-roads-preparation-20261030.json`. The small public fixture `data/public/bd-road-reference-sample.json` is explicitly licensed **ODbL-1.0**, attributed to **© OpenStreetMap contributors** and labelled an arbitrary development slice.

Geofabrik explicitly licenses OSM-derived downloads under ODbL-1.0, with attribution and share-alike for derived databases: <https://www.geofabrik.de/data/download.html>. OSM copyright/licensing: <https://www.openstreetmap.org/copyright>. The new dataset retains that licence; it does not acquire a project-wide CC0 licence. No map-tile scraping, private contributor metadata or official government partnership is claimed.

Prepare on the operator's Linux backend checkout/workstation with the optional data dependencies. No cloud service or paid account is created:

```bash
python -m pip install -r requirements-data.txt
python scripts/prepare-bd-roads.py --download
```

The first download is approximately 339 MiB. The script processes all qualifying ways in the pinned extract, reports omissions and writes `roads.jsonl`, `roads.sqlite` (FTS5) and `manifest.json` under `.state/public-datasets/bd-roads-20261028/`. Raw/cache files and model binaries stay out of Git; the pinned downloader, schema, canonical digest, full statistics, legal attribution and public fixture are committed. Re-running verifies the source and regenerates the full reference index. SQLite byte digests can depend on the SQLite build; the canonical JSONL digest identifies the actual row content. Mount/copy the **prepared directory** read-only to the API and set `PUBLIC_DATASET_DIR` to its parent. The running API does not need osmium or write access to its published index.

Derived references deliberately exclude coordinates and contributor metadata. They contain public road names/refs/way IDs/types only. The extract can include boundary-crossing features and OSM omissions; this is not a complete official road register. It contains **no road-defect, current traffic, crash-probability or safe-route labels** and cannot train/certify those specialized models.

### Dataset operator workflow

1. `/admin/road-data` verifies prepared bytes and shows provenance/counts. A current dataset reviewer/super admin registers the exact prepared index as a candidate source. No automatic approval is invented.
2. Two different current MFA-enabled dataset reviewers record matching rights evidence through the existing `/admin/rights` workflow: exact dated source URL, terms link, ODbL licence, source date and `public_nonpersonal` sensitivity. Those are real operator actions; automated fixtures do not substitute for production human approval.
3. A different operator from the stager publishes with an optimistic revision. Approval binds the source round/evidence hash, exact derived rows/index hashes and reviewer identities. Source changes, revoked/banned/demoted reviewers and index tampering fail closed. Generic source-state edits cannot replace the two actual rights-review records.
4. RoadFix's explicit-consent reference lookup searches the actual read-only FTS5 index, returns original way IDs and source links with attribution/date/limits, and never stores the query or claims image detection/safety. It respects a disabled RoadFix tool. It does not submit a complaint or send user information to OSM.
5. Source revocation takes effect on the next request, without a warm-query cache. Withdrawal is audited and revision guarded. Rebuilding/replacing the published bytes requires re-review/publication; no private history is rewritten.

The source was legally acquired and the full derived index prepared. **Production application approval has not been impersonated**; the default public lookup remains unavailable until actual independent operators publish it. This is a genuine review gate, not a missing search implementation.

## Verification boundaries

The new tests execute real model inference, durable processing, ordinary/adversarial routing, actual FTS queries over a licensed road-name fixture, source/reviewer revocation, tampering, consent, role/CSRF checks and private-owner isolation. Disposable Docker/TLS integration is extended to prepare/use the full real OSM index and actual YAMNet CPU weights while preserving the production refusal gate. Exact observed CI/browser outcomes belong in the current implementation report; adding a test is not proof that it passed.

Remaining original scope includes the other specialized pipelines, proper Bangladesh domain-labelled datasets/holdouts/expert review, full NoiseTrace temporal/redaction evaluation, broader model lifecycle/RAG/moderation/tenancy workflows and any browser acceptance not actually observed. The 778-file kit and all module identities remain unchanged. No full advanced module or full 50-tool production release is certified by this continuation.
