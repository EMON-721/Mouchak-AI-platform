# Deployment runbook and remaining actions

One HTTPS domain serves Next.js public, session-work, tool and protected operator pages. `/api/*` proxies server-side to private FastAPI. Never publish port 8000 or the database directly. Set the same stable `PRIVATE_API_TOKEN` in both services and use a private network.

The Next.js container uses the verified `build:next` path. The Sites-compatible Vinext build is an additional target. Sites alone does not host Python inference, PostgreSQL or private S3. A frontend without its API is not a complete deployment.

## Provisioning sequence

1. Provision PostgreSQL with TLS, a separate migration owner and a NOSUPERUSER/NOBYPASSRLS application role.
2. Apply migrations 001–004 as the migration owner. Migration 003 checks stock owner/workspace/item links. Grant stock-item updates and movement insert/read only to the application role; no arbitrary movement UPDATE/DELETE privilege. Seed candidate sources before restricting runtime permissions. The backend sets `app.user_id` inside cookie-scoped owner transactions.
3. Configure a persistent Fernet key, private S3, current malware signatures, SMTP verification/reset email, HTTPS `PUBLIC_ORIGIN` and the internal proxy token. Run actual provider integration tests.
4. Install model assets with the checksum scripts. Keep weights out of the web image/Git. Inference stays private and CPU-based; GPU hosting is not assumed.
5. Configure backups, key recovery and a restore drill. Configure shared rate limits, durable queues, monitoring and retention scheduling before multi-instance use. The current in-process limiter is not a distributed production limiter.
6. Repeat session/MFA/owner-isolation and real-inference tests against staging. Complete required Bangladesh holdouts and expert reviews before enabling specialized AI.
7. Build the web/API images from `deploy/`, connect one domain and verify browser → API → storage → result → download/delete. Docker image execution and live cloud deployment were not verified; no Docker daemon or hosted service configuration was supplied.

Production refuses SQLite and a missing stable encryption key. Uploads fail closed without scanning and private S3. Experimental speech/anomaly endpoints are disabled in production. Sensitive training/reuse requires matching independent asset reviews; schema-specific import/publication and evaluation remain separate gates. An admin flag cannot make a model production-validated.

## GitHub publication

Authorized repository: https://github.com/EMON-721/Mouchak-AI-platform. The earlier integration write 403 was resolved after the owner authorized access. The complete checkpoint was published to `main` at `d93b4f36163a1e0c8ab24bba40ea96b078f8a4da`. Its tree `62570204e17e97886dd69fe82590d80d7c2575ef` was verified against tested local checkpoint `4c03fc0` and fetched back with no source difference. The remote initial commit remains an ancestor, and its README is retained in `docs/reference/github-initial-README.md`. No force-push was used.

Publication used the connected GitHub Git Data API because terminal Git has no HTTPS credential. GitHub's commit SHA differs from the local development checkpoint, but all file contents/modes match cryptographically. The local history bundle preserves earlier development commits.

GitHub Actions completed successfully: https://github.com/EMON-721/Mouchak-AI-platform/actions/runs/40680371782. Cloud deployment, Supabase capacity and the model/domain release gates remain separate. Future updates must fetch/inspect the actual remote, preserve concurrent changes and avoid force-push.

## Account-free session operations

Run `services.model_worker.visitor_retention` as the dedicated worker in `deploy/compose.yaml`. Session lifetime is clamped to 15 minutes–24 hours, default 24 hours. Default cleanup polling is 60 seconds, in batches of 100 expired scopes. A one-shot command is `python -m services.model_worker.manage purge-visitors`. These paths delete only role `guest` scopes with no live session; existing user/operator data remains intact. Selected support grants cannot exceed their guest owner's session expiry; expired guests cannot be read through support before cleanup.

The worker requires narrowly granted access to guest owner/session rows plus child cascades and storage delete permissions. Validate these privileges and deletion under actual PostgreSQL/S3 before production. The current real-worker drill uses development SQLite and encrypted local assets; it does not prove cloud deletion or backup expiry. Run more worker capacity if measured expiry volume exceeds one batch per polling interval.

For scheduler roles and encrypted local recovery, read [COLLABORATION_AND_OPERATIONS.md](COLLABORATION_AND_OPERATIONS.md). Local recovery testing is not a production PostgreSQL/S3 backup proof. Public account-free browser processing/history/JSON export are now observed. Protected operator browser MFA and production staging remain unverified.

## Resolution findings and corrected container setup

The API image now sets `MOUCHAK_STATE_DIR=/app/state` and `MODEL_DIR=/app/models`, copies checksum-controlled acquisition scripts/manifests, and includes inference telemetry opt-outs. The Compose `model-init` job downloads the recorded OCR/embedding assets into the shared model volume; API startup depends on its successful exit. It never fabricates missing model files. Apply database migrations separately with the migration owner before starting runtime services. These are validated source/configuration changes, not a verified Docker/cloud deployment.

Vercel Services (currently Beta) can compose a Next.js frontend and private Python/container backend using bindings; Python is not categorically unsupported by that provider. No Mouchak Vercel project exists and none was deployed. Its stateless runtime, model packaging, workers, 4.5 MB request limit versus the existing 10 MB upload contract, private storage/scanning and operational prerequisites need a tested design before migration. Do not deploy a frontend that cannot reach its API and call it the complete platform. Reference: https://vercel.com/docs/services and https://vercel.com/docs/functions/limitations.

Supabase: the owner selected the connected organization, the project quote was $0/month, and actual creation was rejected by its two-active-free-project cap. Existing projects were not changed. The remaining owner action is to make an approved dedicated project slot available, upgrade through the provider's billing flow, or supply a separately authorized PostgreSQL target. No paid plan or destructive change is authorized implicitly by the earlier $0 quote.
