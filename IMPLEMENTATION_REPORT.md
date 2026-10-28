# Mouchak AI implementation report — 28 October 2026

**Tested account-free platform checkpoint; the full 50-tool production release is not finished.** Continued from the verified GitHub publication head, preserving all original requirements and prior implementation. The owner now selected Netlify for the website and a separate Linux/Docker host for the AI backend; Cloudflare may be added later for DNS/CDN.

The owner's latest instruction removes public login, signup and visitor profiles, superseding the ZIP's end-user account-screen requirements. The Super Admin/operator system retains passwords, roles and MFA. See `docs/PUBLIC_ACCESS.md` for the decision and security details.

## Current backend/BillDetect continuation — 28 October 2026

Resumed the previous source without regenerating the original kit. The owner handles Netlify. Added encrypted private monthly bill history, editable real OCR drafts, separate training consent, real private IsolationForest → ONNX export/inference and per-owner model cards. Experimental training/prediction remain blocked in production pending Bangladesh holdouts and release review; history and arithmetic work independently. See [Bill pipeline](docs/BILL_PIPELINE.md).

Added secure, additive PostgreSQL provisioning on stdin with four isolated SCRAM roles, verified TLS, checksum migration ledger and all six migrations (26 application tables). Actual GitHub platform checks passed: **359 Python tests**, original source/registry verification, lint, TypeScript, PostgreSQL WASM, transport and Next production build. [Run 40700792724](https://github.com/EMON-721/Mouchak-AI-platform/actions/runs/40700792724) has a successful **platform job**, but its separate private-stack job failed at S3 readiness; it is not an overall successful CI run. The fixture actually verified networked PostgreSQL TLS, migration replay and safe role attributes. Storage/container/operator/retention checks after that step remain unverified until the corrected integration completes.

Browser confirmed a Bangla-digit **DEMO** bill, arithmetic difference 25 BDT and retained history after reload. DEMO remains excluded from model training. Browser PDF export remains blocked by the browser security policy; no bypass or completed PDF browser claim. No live host/bucket/database, production restore or all-50 release is certified. See [backend operations](docs/BACKEND_OPERATIONS.md) and [Netlify runbook](docs/NETLIFY.md).

---

## Netlify/Linux continuation — 28 October 2026

- Completed the previously interrupted local fetch and merged the verified publication head without source changes or history loss.
- Added owner-scoped encrypted 1 MiB chunk uploads, preserving the 10 MiB file contract, SHA-256 integrity, quota reservations, identical scanner/signature checks, idempotent finalization and expiry/clear cascades.
- Added encrypted durable inference jobs with separate worker subprocesses, bounded attempts/timeouts, crash recovery, lease fencing, cancellation, live session checks and atomic run/consent/transfer publication. Queue mode refuses synchronous bypasses; corrections preserve lineage. The website polls jobs, offers cancellation and reopens completed work from `/work` without visitor accounts.
- Added shared PostgreSQL request counters, per-owner and transport ceilings, HMAC-protected keys and fail-closed storage behavior. Forwarded client IPs remain untrusted; a shared proxy ceiling and high-volume abuse/load testing are explicit limits.
- Added migration 005 (24 tables total), separate worker grants, a Netlify Next.js configuration/preflight and a Linux-only Compose/TLS/signature-update template. Actual Docker/Netlify/Linux deployment remains unverified because the required host/account/services are unavailable.
- Current regression: **343 tests passed**; TypeScript, lint and Next production build pass. All five migrations/RLS/grants/fencing/UPSERT checks pass in actual PostgreSQL WASM. Client chunk/queue/preflight contract checks pass. Evidence: `docs/audit/async-*` and `scripts/test-private-processing.mjs`.
- Managed browser: an original Bengali evaporation question went through a waiting job, actual MiniLM/BM25 retrieval and a completed result; it reopened through `/work`. Screenshot: `docs/audit/async-browser-rag.jpg`. Browser chunk upload and hosted operation are not claimed.
- Deployment target and exact secure setup/remaining dependencies: [Netlify + Linux runbook](docs/NETLIFY.md). The 47 support flows, three production-unavailable cores, all advanced model/data/expert gates and the original 430 full-scope acceptance scenarios keep their previous statuses.

The sections below retain earlier checkpoint evidence. New counts and infrastructure source changes above supersede their older totals; they do not certify cloud operation.

## Resolution update after the account-free checkpoint

- Added a real, pinned MediaPipe/BlazePose CPU pipeline for GoliCoach: private bounded MP4 upload, decoded frame timestamps, 33 body landmarks, visible 2D joint angles, optional two-clip comparison and skeleton-only replay controls. It requires local experimental opt-in and is always disabled in production. Bangladesh camera-angle holdouts, cricket-specific alignment and coach-reviewed suggestions remain incomplete. Eight real-model/API tests pass; this is not a fourth production-complete module or a Bangladesh accuracy benchmark.
- Automatic approval review blocked an unexpected Microsoft telemetry attempt in an earlier regression run. Default runtime telemetry was not disabled then. The application now disables ONNX 1DS telemetry before runtime import, also disables Hugging Face telemetry, and applies the ONNX API opt-out afterward. A fresh run with this fix passed all 325 tests. No prior-traffic absence claim is made. See `docs/POSE_PIPELINE.md`.
- Fixed development `.env` loading and restored a compatible Python executable path after environment maintenance. The actual live browser showed GoliCoach experimental controls. Upload automation timed out; its outcome is unknown and no completed browser pose processing is claimed.
- Diagnosed the PDF verification issue as a cloud browser security/URL block (`ERR_BLOCKED_BY_CLIENT`), rather than a demonstrated PDF-generation failure. Actual API and readable-document checks pass. The browser restriction was not bypassed.
- Added a checksum-controlled model-init Compose job, copied acquisition scripts/manifests into the API image, aligned image state/model paths, and made the API wait for successful model acquisition. Compose references are validated; no Docker daemon/image execution or cloud deployment is claimed.
- Checked available hosting connections. The owner selected the connected Supabase organization. It quoted $0/month, then refused creation because the two-active-free-project quota was exhausted. No new project, pause/delete, paid upgrade or production deployment occurred. GitHub write access is now restored and complete source publication is verified. Exact remaining account actions are in `docs/ISSUE_RESOLUTION.md`.

## Completed in this continuation

- Public pages automatically establish a temporary HttpOnly browser scope without collecting visitor name, email, password or profile. All 50 exact tool routes remain directly accessible. Public authentication/profile routes are removed; valid registration/profile API requests return Gone; end-user password sign-in is disabled.
- `/work` contains current-session history, reopen/export links, selected-facts support, typed transfers, session export and explicitly confirmed clearing. Lifetime is at most 24 hours. Losing the cookie has no account recovery; users are told to download reports they need.
- Strict owner checks, consent, origin/CSRF protection and encryption remain. Visitors cannot read other visitors' results or use privileged APIs. Historical user data is preserved. The former account interface remains inert reference text.
- A real retention worker and CLI purge expired guest scopes only. Compose includes the worker. A subprocess drill verifies removal and graceful shutdown while preserving active visitors and historical accounts. Guest support grants are capped to scope expiry; expired owners are denied before purge.
- Operator sign-in/reset/verification/security live under `/admin`. Password/MFA and current-role checks remain. The operator team list does not expose guests as public profiles. No default admin password exists.
- The browser reproduced an HTTP-preview failure from unavailable `crypto.randomUUID()`. Cryptographic `getRandomValues` fallback fixed submission; a clean browser then completed real processing.
- The supplied Bengali font has its embedded attribution notice and upstream SIL OFL alongside it. Source excludes secrets, weights and private records.

## Verified results and limits

| Area | Actual evidence | Limit |
|---|---|---|
| Requirements | All 778 original-kit files, checksums and 16,269 indexed requirement entries retained | Indexing is not implementation; the 430 original acceptance cases are not all passed |
| Public tools | All 50 API routes exercised without registration; 47 current support flows process inputs; three cores return explicit errors | No full advanced module is certified complete |
| Security/privacy | Visitor isolation, expiry rotation, CSRF, clearing, upload/export, legacy preservation, expired-owner support denial and fresh operator MFA tested | Live PostgreSQL/S3/TLS and browser operator MFA still need staging |
| Tests | **359 passed in the latest GitHub platform job** (earlier checkpoint: 343 passed) (59 public-access cases, eight real pose cases and one new pre-import privacy case). Authoritative current suite: `docs/audit/async-regression.xml`; focused new cases: `public-sessions.xml` | Earlier artifacts remain historical; they do not replace current results |
| Frontend | TypeScript, lint and Next.js production build passed. Logs: `docs/audit/resolution-*.log` | Build success is not cloud operation proof |
| Browser | No signup: synthetic bill line 125, stated 150, difference 25; result reopened under `/work`; Bengali/English switch; JSON downloaded/parsed; `/admin` guarded; `/register` not found | PDF navigation is blocked by the cloud browser URL/security policy; pose upload automation timed out. Completed browser pose inference, three-width accessibility/responsiveness and operator MFA remain unverified |
| PDF | Exact browser JSON rendered a valid 473,753-byte PDF locally in 0.08 seconds; anonymous API test opens a readable PDF | This is not a successful browser PDF download claim |
| Real inference | Existing Bengali/English Tesseract, ONNX multilingual MiniLM + BM25 extractive retrieval, OpenCV registration and optional experimental anomaly/Whisper retained | Bangladesh holdouts, advanced domain/generative pipelines and production speech validation incomplete |
| Data/legacy | Three local V3 snapshots (25 files), selected original-JS parity tests, 12 CC-BY reading passages, 81-entry commodity dictionary without prices, encrypted stock ledger | Four full remote repos/live migrations unavailable; candidate sources are not approved datasets |
| Database/operations | 26-table schema/migrations 001–006 and additive provisioning ledger; previous tables preserved; PostgreSQL WASM RLS checks; CMS scheduler, dual rights review, triage, support/transfers and local encrypted recovery retained | External PostgreSQL, production backups, hosted distributed limits/queues and cloud operations unverified |
| GitHub | Complete source published to main at `d93b4f3`; fresh fetch/tree match verified; initial commit retained | GitHub Actions completed successfully; production deployment remains separate |

## All 50 modules

`MODULE_PROGRESS.csv` and `docs/audit/module-progress.json` retain every exact module's status, evidence, model readiness and remaining dependency. The entire advanced scope remains in `requirements/original-kit/`.

The **47 support workflows** perform actual current calculations/limited processing: bill reconciliation, unit-price comparisons, stock/expiry records, text differences, land units, pay scenarios, energy costs, break-even, private trends, checklists, user-provided graph routing, observations, phraseboards and cited original-passage retrieval. They are labelled rules/calculations or limited inference, never fabricated specialized predictions.

The **three unavailable cores** remain ClinicCompass BD (approved facility records), OshudhKhoj BD (approved pharmacy/stock records), and GoliCoach AI (production-evaluated cricket pose/video). GoliCoach now has the additional real development-only observation pipeline described above. Production routes refuse to invent results. Removing accounts does not supply their missing dependencies.

## Partial and blocked requirements

| Requirement | Current status | Remaining work/dependency |
|---|---|---|
| Complete advanced 50-tool pipelines | Partial; no full-module completion claim | Domain CV/PPE/crop/water segmentation, pose/video coaching, audio-event classification, evaluated forecasting, generative RAG and original workflows |
| Bangladesh datasets/evaluation | Candidate registry and reviewed-import controls | Source-specific rights/freshness/provenance approval, labelled holdouts and expert medical/legal/child review; 244 candidates remain unapproved/unimported |
| Full Super Admin scope | Selected controls implemented | Full layout/logo/form/locales CMS, remaining moderation, organization/guardian tenancy, canaries/hot-swap/drift, re-embedding and full model lifecycle controls |
| Public user scope | Account-free processing implemented as instructed | Persistent profiles, cross-device accounts and signup intentionally removed. Notification API remains; public notification UI is not exposed |
| Browser E2E | Public processing/history/JSON verified | Browser PDF blocked by cloud security policy; pose upload/inference unverified after automation timeout; operator MFA and accessibility/responsive matrix outstanding |
| Production infrastructure | Templates/runbooks prepared | Private Python host, TLS domain, PostgreSQL roles, S3/scanner, SMTP, monitoring, distributed limits and production restore/retention not provisioned/verified |
| GitHub publication | Published and verified; previous authorization blocker resolved | CI result and production deployment are separate checks |

The government Open Data terms endpoint previously returned 403. No restricted corpus was scraped and no government, facility, pharmacy, price or model-evaluation data was invented. Dataset/model references remain preserved for lawful continuation.

## GitHub publication result

The owner authorized repository access. Complete source was published to `main` at [d93b4f3](https://github.com/EMON-721/Mouchak-AI-platform/commit/d93b4f36163a1e0c8ab24bba40ea96b078f8a4da), preserving the initial remote parent `d84fe4327693cb73dae0e0b80f936b9567eafd54`. A fresh fetch verified tree `62570204e17e97886dd69fe82590d80d7c2575ef` exactly matches tested local source checkpoint `4c03fc0`. All 1,127 files, including all 778 original-kit files, are present. The Git Data API publication has its own commit metadata/SHA; the complete local development history remains in the delivered bundle.

The previous integration 403 is resolved. [GitHub Actions](https://github.com/EMON-721/Mouchak-AI-platform/actions/runs/40680371782) completed successfully, including installation, lint/typecheck, tests, PostgreSQL checks and build. No production deployment or all-50 advanced-module certification is implied by publishing source.

## Deliverables and continuation

Latest detailed status and resume instructions: `docs/ISSUE_RESOLUTION.md`, `docs/POSE_PIPELINE.md` and `docs/PROGRESS_LEDGER.md`.

The source package contains the monorepo, full original kit, all 50 definitions/routes, implemented backend/inference, protected operator controls, account-free frontend, tests/evidence, environment template, CI, deployment configuration, report and full Git history bundle. Runtime databases, credentials, private files, downloaded weights and dependencies are excluded; installation/download scripts and checksums remain.

Resume the latest prepared branch and current artifacts. Finish outstanding modules against their exact original acceptance cases and approved data. Do not regenerate completed pages, discard advanced scope, request the supplied destination again, or label support slices production complete.
