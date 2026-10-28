# Mouchak AI · মৌচাক এআই

**Implementation checkpoint, not a fully production-ready release.** One bilingual Next.js website, 50 tool routes, a private FastAPI backend, account-free visitor sessions, a protected operator console and real local inference adapters. All original requirements remain under `requirements/original-kit/`; no legacy website was overwritten.

Read **[IMPLEMENTATION_REPORT.md](IMPLEMENTATION_REPORT.md)** first for tested scope, partial features and blockers. `MODULE_PROGRESS.csv` tracks every tool separately. The original 430 acceptance scenarios have not all passed; a successful support-flow test does not certify an advanced AI module.

## Run locally

Requirements: Node 24, Python 3.12 with venv support, pnpm 11.25, Tesseract Bengali/English and FFmpeg. Use WSL or the deployment containers on Windows.

```bash
pnpm install --frozen-lockfile
python3 -m venv .venv
.venv/bin/python -m pip install -r requirements-python.txt
.venv/bin/python scripts/download-models.py
.venv/bin/python scripts/download-speech.py
.venv/bin/python -m services.model_worker.manage migrate
pnpm dev
```

The development wrapper starts the private API first and then the website. `PUBLIC_ORIGIN` must match the browser origin exactly for CSRF protection. For ordinary local Next.js development, run these in two terminals instead:

```bash
.venv/bin/python -m uvicorn services.model_worker.main:app --host 127.0.0.1 --port 8000
pnpm exec next dev
```

Browse `http://localhost:3000` and open any tool directly. There is no visitor login, signup or profile. A private HttpOnly cookie isolates temporary results for up to 24 hours; download anything you need to keep. `/work` shows the current session. Historical accounts are preserved but end-user password login and registration are disabled.

Only authorized operators sign in at `/admin/login` and manage MFA at `/admin/security`. Production operator verification/reset uses SMTP; production also requires PostgreSQL and a stable encryption key. There is **no default admin password**.

Create an operator through a password prompt, then enroll and verify MFA in the same website:

```bash
.venv/bin/python -m services.model_worker.manage create-admin --email YOUR-EMAIL
```

Do not commit `.env`, `.state`, private records, model binaries or generated test fixtures. Never replace a persistent encryption key without a migration and recovery plan.

## Verify

```bash
pnpm typecheck
pnpm lint
.venv/bin/python scripts/check-registry.py
.venv/bin/python -m pytest tests -q
node scripts/test-postgres.mjs
pnpm build:next
```

Inference tests run actual OCR, multilingual embedding/retrieval, OpenCV and anomaly operations. Download models first. Test fixtures are synthetic/original, not a Bangladesh performance benchmark. Speech runtime evidence is separate from Bengali validation. PostgreSQL SQL/RLS tests use PGlite; an external PostgreSQL deployment still needs connection, migration and restore tests.

## Structure

- `app/`, `components/mouchak/`: one Next.js public/user/admin app and API proxy.
- `services/model_worker/`: FastAPI, authorization, encryption, domain engines, inference and operational CLI.
- `packages/module-registry/`: all 50 definitions, forms, model candidates and sources.
- `data/authored/`: five original, nonofficial Bengali/English learning passages.
- `data/legacy/`, `reference/legacy-snapshots/`: attributed additions and complete original local V3 static source.
- `database/migrations/`: PostgreSQL schema, owner RLS and additive stock/sharing/operations migrations 003–004.
- `deploy/`, `.github/workflows/`: deployment templates and CI.
- `docs/audit/`: source analysis, hashes, test evidence and readiness records.
- `requirements/original-kit/`: the entire unchanged input kit.

## Deployment and GitHub

Source repository: [EMON-721/Mouchak-AI-platform](https://github.com/EMON-721/Mouchak-AI-platform). GitHub write authorization is now verified, and the complete 1,127-file checkpoint was published to `main` in [commit `d93b4f3`](https://github.com/EMON-721/Mouchak-AI-platform/commit/d93b4f36163a1e0c8ab24bba40ea96b078f8a4da). A fresh fetch verified its tree `62570204e17e97886dd69fe82590d80d7c2575ef` exactly matches tested local source checkpoint `4c03fc0`. The original remote initial commit remains an ancestor. GitHub Actions [run 40680371782](https://github.com/EMON-721/Mouchak-AI-platform/actions/runs/40680371782) completed successfully, including tests, PostgreSQL checks and the Next build. Production hosting remains unconfigured. See [docs/DEPLOYMENT.md](docs/DEPLOYMENT.md).

Run the visitor retention worker alongside the API:

```bash
.venv/bin/python -m services.model_worker.visitor_retention
# One-shot equivalent:
.venv/bin/python -m services.model_worker.manage purge-visitors
```

`ANONYMOUS_SESSION_TTL_SECONDS` is capped at 86,400 seconds. The worker removes expired visitor scopes and their files/records, while preserving active visitors and historical accounts. Production S3 deletion/retention, PostgreSQL service roles and backup expiry must be verified on staging. Losing the cookie does not recover a session; it does not immediately erase server data before expiry/cleanup.

Shared support/transfer/rights/scheduling setup: [docs/COLLABORATION_AND_OPERATIONS.md](docs/COLLABORATION_AND_OPERATIONS.md). Public access decision and security details: [docs/PUBLIC_ACCESS.md](docs/PUBLIC_ACCESS.md). Latest evidence is listed in [IMPLEMENTATION_REPORT.md](IMPLEMENTATION_REPORT.md). The complete original 50-tool advanced scope remains incomplete.

## Latest resolution checkpoint

325 automated tests pass after adding eight actual pose-pipeline tests and a pre-import inference privacy test. TypeScript, lint and the current Next production build pass. [Experimental GoliCoach setup](docs/POSE_PIPELINE.md) includes private MP4 inference, 33 landmarks, timestamps, 2D angle comparison and skeleton replay. Enable only for local evaluation; production remains disabled until Bangladesh holdouts and coach review pass.

ONNX/Hugging Face telemetry is disabled before model-runtime import. The API image and CI carry the same settings. Compose now includes a checksum-verified model-init service and blocks API startup until model acquisition succeeds. Its image/mount state paths agree. Docker image execution remains unverified because no daemon is available.

The owner-selected Supabase organization returned a $0 quote but refused project creation because its two-active-free-project quota is full. No project was created, paused, deleted or upgraded. GitHub publication is verified; the earlier integration 403 is resolved. Browser PDF navigation is blocked by the cloud browser security policy; pose upload automation timed out, so no completed browser inference/upload claim is made. Current hosting/model blockers and next actions are in [docs/ISSUE_RESOLUTION.md](docs/ISSUE_RESOLUTION.md).
