# Netlify website + private Linux AI backend

The owner selected this architecture on 28 October 2026. Vercel is not the deployment target. Cloudflare DNS/CDN can be added later; it is not required for this release configuration. Existing Sites/Vinext sources remain preserved.

**This is tested source and a deployment runbook, not a completed cloud deployment or certification of all 50 advanced tools.** No Netlify site credentials, authorized Linux host, API domain, operational database or private bucket have been supplied. No paid resource was purchased. The selected Supabase organization's free-project cap remains unresolved; do not modify its other projects.

## What is configured

The website uses the canonical Next.js build through Netlify's current automatic OpenNext adapter. `netlify.toml` publishes `.next`; do not select the optional Vinext `build`/`dist` target for Netlify. Node 24 and the existing package-manager pin are retained. A build preflight refuses a missing HTTPS backend, short/missing internal token, failed health response or disabled durable inference. It checks reachability/configuration, **not worker availability, domain-model validation or overall production readiness**.

Browser requests stay on the website origin. The Next.js route proxy injects the private service token server-side, forwards only necessary request headers, refuses redirects, disables caching and bounds Netlify upstream calls to 55 seconds. It does not forward a visitor-supplied internal token. The backend must have TLS and still requires its token, owner session, processing consent and CSRF checks. Private port 8000 and PostgreSQL are never published by the backend Compose file.

Netlify currently documents a 60-second synchronous function limit and a 6 MB buffered payload limit, effectively about 4.5 MB for binary requests. The website sends private uploads in **1 MiB chunks**, preserving the **10 MiB per-file** contract. The backend reserves a bounded owner quota, encrypts staged parts in PostgreSQL, checks part order, length and SHA-256, then applies the existing signature/resolution/malware/private-storage checks before creating an asset. Staging expires after 15 minutes, is limited to two active uploads per owner and is erased by the cleanup worker or owner clearing. Failed or interrupted uploads do not become usable assets. Original filenames are not stored.

With `ENABLE_DURABLE_INFERENCE=1`, normal submissions use encrypted durable jobs and short polling requests. The old synchronous run route refuses a queue bypass. Corrections return HTTP 202 and retain the original result lineage after worker completion. Results can be reopened from `/work` after leaving the tool page, without a public account. Queue inputs are erased after terminal processing; the normal encrypted run retains its intended data/redaction policy. Pending inputs are included in the owner's private export.

The worker claims jobs using PostgreSQL row locking/`SKIP LOCKED`, a random lease token and a 300-second lease. A separate inference process has a 240-second wall timeout. Crashed attempts are reclaimed after lease expiry, with at most three attempts and a 15-minute submission lifetime capped by session expiry. Cancellation, revoked/expired sessions, removed owners, disabled tools or a stale lease cannot publish a new result. Model execution is **at least once** after crashes; run/consent/transfer publication and the current lease fence commit atomically. This queue must not be used for payments, notifications or other external side effects.

Production request counters use atomic PostgreSQL UPSERTs shared across replicas. Each valid owner receives 60 writes per fixed clock-minute and route group. Unauthenticated callers share 60; each transport peer/group also has a ceiling of 600. Raw IPs/cookies are not stored in counters; the key is HMAC protected. Storage failure returns 503, never an unguarded success. Fixed windows allow boundary bursts. Forwarded IP headers are not trusted: Netlify/Caddy traffic can share transport ceilings. A reviewed edge identity/abuse layer and load testing remain necessary before high-volume public operation.

## Backend setup

1. Use an authorized Linux host with Docker Compose, adequate measured CPU/RAM/disk, outbound access to the documented model/signature sources and ports 80/443. Select a region, backup policy and budget explicitly. No host was provisioned in this session.
2. Provision TLS PostgreSQL. Securely create separate `mouchak_app`, `mouchak_inference`, `mouchak_scheduler` and `mouchak_retention` logins: NOSUPERUSER, NOCREATEDB, NOCREATEROLE, NOINHERIT, NOBYPASSRLS. They must not own application tables or inherit one another. Keep the migration owner separate.
3. Run `python -m services.model_worker.manage migrate` with the migration-owner connection to create/seed additively. Apply SQL migrations **001–005**, then `deploy/app-grants.sql`, `deploy/runtime-grants.sql` and the scheduler grants in `COLLABORATION_AND_OPERATIONS.md`. Use a secure PostgreSQL service/secret manager; never put passwords in command arguments, source or chat. Test every actual role and owner boundary on the real server before release. The automated SQL evidence uses PGlite, not a live networked PostgreSQL host.
4. Configure the private S3 bucket, restricted service credentials, encryption key recovery and deletion/retention. Keep the bucket private; assets are additionally application-encrypted. Validate the chosen S3-compatible provider's encryption/API behavior. SMTP credentials must permit the operator verification/reset sender. There is no default admin password.
5. Put backend-only settings from `.env.example` into the host's secret manager/ignored `.env`: `DATABASE_URL` (app), `INFERENCE_DATABASE_URL`, `SCHEDULER_DATABASE_URL`, `RETENTION_DATABASE_URL`, `DATA_ENCRYPTION_KEY`, `PRIVATE_API_TOKEN`, S3/AWS values, SMTP values, `API_HOSTNAME`, `TLS_EMAIL` and the exact Netlify/custom-domain HTTPS `PUBLIC_ORIGIN`. Use a stable cryptographically random internal token of at least 32 characters, separate from the Fernet key. A temporary local preview key is not a production key.
6. With DNS pointing the API hostname to this host, start the supplied backend:

   ```bash
   docker compose --env-file .env -f deploy/compose.backend.yaml up -d --build
   ```

   The template includes checksum-controlled model initialization, initial and continuous malware-signature updates, FastAPI, an inference worker, scheduled publishing, expiry cleanup and Caddy TLS. Only the TLS ingress publishes ports. Model downloads/signature updates must actually succeed. Scanning fails closed when unavailable. Resource caps and restart behavior are included; image execution has not been tested here because Docker is unavailable.

7. Bootstrap the operator with `manage create-admin` under the appropriate operational connection; its password is entered by a prompt. Enroll and verify MFA through the protected operator flow. Never enable public signup/profile screens.
8. Verify real PostgreSQL/S3/SMTP, scanner failures, worker death/restart, queue cancellation, retention, logging/alerts and restore drills on staging. Monitor all worker services; the health endpoint does not currently prove a worker heartbeat. Retain independent backups and keys off-host. The existing local encrypted archive drill is not a production backup system.

## Netlify setup

1. In your Netlify account, import the authorized GitHub repository `EMON-721/Mouchak-AI-platform`, branch `main`. Leave the base directory at the repository root. Keep `netlify.toml`; its command is `node scripts/check-netlify.mjs && pnpm build:next` and publish directory `.next`. Do not configure a SPA `/* /index.html` rewrite or pin a legacy Next adapter.
2. Select the final website hostname before backend `PUBLIC_ORIGIN` configuration. Provide **only** `PRIVATE_API_URL=https://YOUR-AUTHORIZED-API-HOST` and the matching `PRIVATE_API_TOKEN` as Netlify site environment variables, scoped to **both Builds and Functions**. Never use `NEXT_PUBLIC_` for either secret. Database, encryption, bucket and SMTP credentials stay on the Linux backend. Values in `netlify.toml` alone do not supply function secrets.
3. Keep public-repository untrusted deploy previews from receiving production secrets. A preview must use an isolated backend/data/key/origin and appropriately scoped credentials; otherwise disable preview builds. Do not weaken origin/CSRF checks to make a preview work.
4. Deploy after the backend is reachable. The preflight intentionally fails before publishing a disconnected frontend. Verify Netlify's actual OpenNext build, runtime environment and logs; local Next build success is not Netlify adapter execution proof.
5. Run website → upload/queue → actual model → encrypted run → reopen/export/delete, operator MFA/permissions and responsive/accessibility checks on the deployed hostname. Large original-file/private-export downloads may exceed Netlify buffered response limits; validate actual adapter streaming, or implement bounded range/archive delivery before certifying those large-download cases. The cloud browser's earlier PDF security block has not been bypassed or marked passed.

## Evidence and remaining gates

`tests/test_async_runtime.py` executes actual queued calculations/retrieval, a separate worker process, cancellation, lease recovery, session expiry, corrections, chunk integrity/ownership and shared counters across threads/processes. `scripts/test-async-postgres.mjs` applies all five migrations twice where appropriate and checks real PostgreSQL WASM RLS, grants, fencing and UPSERT behavior across 24 tables. `scripts/test-private-processing.mjs` covers browser transport/preflight contracts with test-only responders; it is not hosted inference evidence.

A managed browser submitted the original Bengali evaporation question, observed its waiting state, received an actual MiniLM/BM25 extractive answer and reopened the completed job through `/work`. This is development browser evidence. Browser chunk upload, cloud job recovery, Netlify deployment, live Linux/container operation and the full original 430 acceptance scenarios remain unverified. The 47 limited support flows, three production-unavailable cores, Bangladesh data/rights/holdouts and remaining advanced admin/model scope retain their previous honest statuses.

Official references checked 28 October 2026:

- https://docs.netlify.com/build/frameworks/framework-setup-guides/nextjs/overview/
- https://docs.netlify.com/build/functions/configuration/
- https://docs.netlify.com/build/environment-variables/overview/
- https://docs.netlify.com/build/configure-builds/manage-dependencies/
- https://www.postgresql.org/docs/current/sql-insert.html
- https://www.postgresql.org/docs/current/sql-select.html
