# Portable deployment runbook — hosting paused

**Owner decision, 29 October 2026:** keep source on GitHub; do not deploy production now. No provider is selected or required by this runbook. Render/Netlify/Railway setup was paused. Existing resources are not deleted, upgraded or modified by this repository update.

## Supported boundaries

| Part | Portable runtime |
|---|---|
| Web/UI/same-origin API proxy | Node 24, Next.js standalone; pnpm build + pnpm start or deploy/Dockerfile.web |
| API | Python 3.12 + native OCR/FFmpeg/OpenCV/ClamAV libraries; deploy/Dockerfile.api |
| Inference | Separate durable worker using the API image and dedicated PostgreSQL role |
| Database | PostgreSQL with verified TLS, additive migrations 001–006 and least-privilege roles |
| Storage | Private S3-compatible storage over verified HTTPS, application encryption + SSE |
| Operations | Scheduler, visitor retention, current scanner signatures, SMTP, TLS, monitoring and recovery |

No vendor database SDK, edge compute, paid LLM API or provider login is required for the source. A host must actually support these runtimes, memory/native dependencies and worker processes. Static-only hosts and small edge isolates cannot execute this complete backend.

## Web build

```bash
pnpm install --frozen-lockfile
pnpm build
pnpm start
```

Set PRIVATE_API_URL and PRIVATE_API_TOKEN only on the server. The browser calls /api/* at the website origin. A private Docker-network URL such as http://api:8000 is appropriate inside the same protected host/network. A separately hosted backend requires verified HTTPS, matching internal tokens and restricted ingress; do not expose it as an unauthenticated public API.

The container sets HOSTNAME=0.0.0.0, defaults to port 3000 and supports provider PORT configuration. Its non-root Node user owns the traced build/static files. Optional Netlify instructions remain in NETLIFY.md; they are not the default dependency. Optional Sites/Vinext scripts are explicitly build:sites/start:sites, not pnpm build/start.

## API image and migrations

```bash
docker build -f deploy/Dockerfile.api -t mouchak-api .
docker build -f deploy/Dockerfile.web -t mouchak-web .
```

The API entry point is python -m services.model_worker.serve; PORT defaults to 8000 and rejects invalid values. The image includes database/migrations and deploy SQL grants so the existing secure provisioning CLI is usable from the built image.

Create a dedicated database. Provision with python -m services.model_worker.provision using JSON on stdin, verified-full TLS and four independent role passwords. Never put a DSN/password in shell arguments, chat, source, build arguments or public logs. See BACKEND_OPERATIONS.md for the exact contract. A migration-owner connection is for provisioning only; the web/API must not run as that owner. Preserve existing schema/data, verify checksums and take a recovery backup before applying migrations to a nonempty installation.

Production rejects SQLite/missing stable encryption keys; protected API middleware rejects an absent/short internal token. Uploads fail closed without private storage and current scanning. An admin switch cannot enable an unevaluated specialized model.

## Full service topology on one compatible Linux/Docker host

```bash
docker compose --env-file .env -f deploy/compose.yaml up -d --build
```

This is an explicit future deployment command, not executed by CI or by updating source. Prepare the reviewed secret environment, database, private bucket, domain and SMTP first. SITE_HOSTNAME is the public website hostname; PUBLIC_ORIGIN is its exact HTTPS origin; TLS_EMAIL is for certificate management.

The topology includes web, API, inference, scheduler, retention, checksum-controlled model-init, ClamAV initial signatures/updates and Caddy TLS. Only Caddy publishes 80/443. API/database/worker ports must remain private. The service definitions reuse compose.backend.yaml so queue/scanner/retention services are not silently omitted.

For a separate compatible frontend host, deploy/compose.backend.yaml supplies API-side services and its API_HOSTNAME TLS entry point. The frontend still needs the same transport token, exact browser origin, persistent backend and real model/storage services. Do not point a public frontend at a sleeping/unconfigured API and call it complete.

## Environment contract

See .env.example. Required production groups:
- Exact HTTPS PUBLIC_ORIGIN and a cryptographically random server-only PRIVATE_API_TOKEN (32–512 ASCII characters).
- Stable DATA_ENCRYPTION_KEY; separate protected backup-key recovery. Replacing a key without re-encryption loses access to old ciphertext.
- Verified-TLS DATABASE_URL (mouchak_app), INFERENCE_DATABASE_URL, SCHEDULER_DATABASE_URL and RETENTION_DATABASE_URL. Do not share the migration owner.
- Private S3 bucket, region and credentials; optional HTTPS endpoint and trusted CA; current malware signatures.
- SMTP sender/authentication for production operator verification/reset.
- ENABLE_DURABLE_INFERENCE=1; ENABLE_EXPERIMENTAL_POSE=0; runtime telemetry off.
- Provider-managed volume ownership, resource sizing, backup/restore, expiry/deletion and health monitoring.

.env.example contains placeholders only. No real credentials or runtime datasets belong in Git or Docker build context.

## Release validation before any future public service

1. Verify DNS/TLS and private ingress; configure all roles and owner RLS.
2. Execute the owned-fixture deployment_smoke CLI against the real HTTPS target; it clears only its own disposable scopes. See LIVE_BACKEND_CHECK.md.
3. Verify current scanner feeds, queue worker recovery, cancellation, retention/database/S3 deletion and backups with an actual provider restore drill.
4. Perform browser visitor/admin MFA/permission workflows and responsive/accessibility checks.
5. Complete each tool's missing approved Bangladesh data, holdout and domain/expert release gates.
6. Verify observability, resource/abuse/load limits, failure handling and an owner-approved operating budget.

A successful build, CI container test or public GitHub repository is not a complete advanced 50-tool production release. No current public deployment, provider restore, uptime or Bangladesh accuracy is claimed.

## Development preview

Use docs/PREVIEW.md and deploy/compose.local.yaml. That template intentionally needs no cloud database or paid hosting and uses development storage. Do not promote its development configuration to production.
