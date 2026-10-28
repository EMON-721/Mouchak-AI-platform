# Experimental GoliCoach pose pipeline

This continuation installs actual checksum-pinned OpenCV Zoo MediaPipe/BlazePose person and body-landmark models. It does not certify cricket skill, injury risk or the complete original module.

## Run and verify

```bash
.venv/bin/python scripts/download-pose.py --test-fixture
# Local development only, in the ignored .env file:
# ENABLE_EXPERIMENTAL_POSE=1
pnpm dev
```

The development wrapper loads `.env` before starting the API. Open `/tools/golicoach-ai` without an account, give processing consent and choose one MP4 plus an optional reference. You can swap clip order. The text note is optional. The result includes an accessible frame slider, skeleton-only replay at 0.25/0.5/1× and reference overlay. JSON exports retain time-indexed landmarks. Raw pixels, faces and video are not included in the report; the original upload stays in encrypted owner storage until clearing/retention.

Default remains disabled. Even with the flag set, `MOUCHAK_ENV=production` refuses experimental pose. An admin switch does not override evaluation or privacy gates. Production still has three unavailable full core workflows; GoliCoach now additionally has a real optional development observation pipeline.

## What actually runs

- Two Apache-2.0 ONNX checkpoints, source commit and SHA-256/size checks recorded in `docs/audit/pose-assets.json`. Downloaded weights are excluded from Git.
- ONNX Runtime CPU inference with explicit model output names. OpenCV 5 changes detector output ordering; using the older positional assumption produced invalid shapes. The wrapper uses the pinned regression/score names and unchanged upstream transforms instead.
- MP4 signature plus ffprobe validation: at most 10 MB, 10 seconds, 1080p and 60 fps, one supported video stream. Frames use decoded timestamps, not invented time values. At most 40 samples per clip are processed.
- One detected person is required. Missing, multiple-detection and low-confidence evidence abstains. A detector can miss people: this is not a guaranteed group/privacy classifier. Input must contain one consenting person.
- 33 body landmarks and visible image-plane knee/elbow angles. Missing joints remain null. Optional comparison reports mean absolute angle differences over normalized clip time; this is not stroke-phase alignment or a skill score.
- A separate Linux subprocess with 35-second wall timeout, 30-second CPU cap, 3 GiB virtual address cap and descriptor/output limits. Temporary decoded inputs are cleaned up. Two concurrent workers per API process; no distributed inference queue is claimed.
- Consent, encrypted MP4 storage, visitor ownership, private run/export and existing 24-hour retention apply. Production scanning/storage checks remain intact; experimental uploads are unavailable in production.

## Evidence and unmet gates

Eight focused tests execute the real checkpoints. They cover actual time-indexed inference and distinct clip comparison, blank/group-fixture abstention, missing/tampered models, disabled/production gates, malformed/oversized/long clips, consent, encrypted storage and cross-visitor export denial. The group fixture currently yields no reliable detection; it is not a group-detector recall benchmark.

The public Google MediaPipe photograph is downloaded only for local smoke testing; it is not redistributed with source and no training, RAG or public dataset rights are asserted. Test videos contain synthetic motion derived from that photograph. They are not Bangladesh cricket inputs, held-out phone-angle evaluation, coach-approved drills or production accuracy evidence.

The live browser showed the experimental tool description and controls. The upload automation timed out with an unknown outcome; completed browser processing/replay is not claimed. API processing and the full regression evidence are separate.

Original gaps remain: Bangladesh consented drill data, independent rights review, representative camera-angle holdouts, cricket phase alignment, batting stance feedback, coach-reviewed suggestions and the full acceptance matrix. `full_module_complete` remains false.

## Inference privacy

Default ONNX telemetry was not disabled in the earlier checkpoint. Automatic approval review blocked an unnecessary Microsoft telemetry request during regression. The worker package now forces `ORT_DISABLE_TELEMETRY=1` before ONNX Runtime is imported, also disables Hugging Face telemetry and applies the ONNX API opt-out afterward. CI and the API image declare the same opt-outs. The pre-import test proves initialization order; the subsequent regression passed. Earlier initialization/traffic behavior is not represented as verified absent.

Reference: https://github.com/microsoft/onnxruntime/blob/main/docs/Privacy.md — the environment opt-out prevents 1DS initialization; calling only the Python API after import may be too late for an initialization event.
