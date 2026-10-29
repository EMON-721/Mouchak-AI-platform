# Current architecture and implementation boundaries

One Next.js 16 application owns the bilingual catalogue, 50 /tools/[slug] workspaces, anonymous /work and protected /admin pages. There are no public login/signup/profile pages. Server-side /api/* proxying connects to private FastAPI; browser cookies and CSRF share the website origin. No Python process runs inside a Cloudflare Worker.

## Services and data flow

1. The website creates an opaque temporary visitor scope; the browser receives an HttpOnly cookie and uses the issued CSRF token for writes.
2. FastAPI validates transport/origin/session/owner/permissions, stages encrypted uploaded chunks and records the private request.
3. Durable inference workers lease encrypted jobs, run real available local adapters and commit results with lease fencing. Unavailable model/data gates fail explicitly.
4. /work reopens the current owner's result/export; support sharing uses selected snapshots and typed transfers, not a global private-data bypass.
5. Separate scheduler and retention processes publish due authorized CMS work and delete expired visitor records/assets. Scanner feed updates/model initialization are separate operational services.

## Persistence and authorization

Python SQLAlchemy owns relational data. PostgreSQL migrations 001–006 currently define 26 application tables; secure provisioning adds a checksum migration ledger as a separate table. Dedicated API/inference/scheduler/retention roles must not own tables, bypass RLS or inherit unrelated permissions. Migration-owner credentials must not enter normal runtime containers.

Development uses explicitly local SQLite and encrypted local files. Production requires PostgreSQL and stable encryption, private S3, verified transport, scanning and operator SMTP. Actual disposable Docker TLS PostgreSQL/S3/scanner/inference/MFA/retention checks passed in the historical integration evidence. They are not a live provider deployment or restore test.

Operator roles cover selected CMS/source/module/model-inspection/support/audit/operations controls and require recent MFA. They do not implement every original Super Admin feature, organization tenancy or guardian workflow. General Super Admin endpoints do not bypass owner-private result/file checks.

## AI scope

Tesseract BN/EN, MiniLM ONNX/BM25 cited extractive retrieval, OpenCV registration/difference statistics and private IsolationForest-to-ONNX mechanics run real code. Optional Whisper/pose are experimental; required Bangladesh holdouts and domain approvals have not passed. Deterministic support calculators are labelled calculations, not trained predictions.

The retrieval starter has five project-authored CC0 passages; the attributed legacy reading collection is separate. 244 source candidates are metadata, not approved imported datasets. Full advanced classifiers, generative/domain RAG, real-time directories and most original release/evaluation workflows remain incomplete.

## Portability and preview

Canonical pnpm build/start now use Next.js Node. Both web/API have non-root Docker runtime images, configurable ports and explicit environment contracts. The full Compose topology includes workers/model/scanner initialization and Caddy; backend-only and local-preview variants remain distinct.

Native development selects Windows or POSIX virtualenv paths, waits for the real API and propagates the exact browser origin to both servers. The optional private Codespaces configuration prepares the same real backend and forwards only website port 3000. It does not create a provider account or a public production service.

See README.md, API_REFERENCE.md, DEPLOYMENT.md, PREVIEW.md, MODULE_PROGRESS.csv and IMPLEMENTATION_REPORT.md for current scope, commands and verification.
