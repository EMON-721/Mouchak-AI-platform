# Backend provisioning and integration evidence

Target: the owner handles Netlify; this repository supplies the separate Linux/Docker API, inference, scheduler and expiry services. No Linux cloud host, PostgreSQL service or private bucket has been provisioned in the owner's account. No paid capacity is authorized by these templates. Existing data and unrelated cloud projects must be preserved.

## Secure additive database provisioning

`python -m services.model_worker.provision` accepts a JSON object **on stdin**, preferably streamed from an operator-controlled secret manager. Do not put credentials in command arguments, source, logs or chat. The object has `migration_database_url` (psycopg PostgreSQL URL, not SQLAlchemy's `+psycopg` scheme) and `role_passwords`, containing exactly `mouchak_app`, `mouchak_inference`, `mouchak_scheduler`, `mouchak_retention`. Use four different cryptographically random passwords, 24–128 ASCII characters, and a separate migration-owner credential.

The connection must use `sslmode=verify-full` and the provider's trusted root certificate. The runtime SQLAlchemy connections use `postgresql+psycopg://...` with the same verification. Mount any non-system CA into each container that needs it through an operator-owned Compose override; never disable verification. S3-compatible custom endpoints must also use verified HTTPS. Custom endpoints default to path-style addressing; `S3_ADDRESSING_STYLE` can select `auto`, `path` or `virtual`. A private S3 CA requires `AWS_CA_BUNDLE` plus a read-only CA mount in the actual runtime override; do not set it to an empty string.

Provisioning validates existing-role credentials before writes and never rotates a password. Dedicated roles must be LOGIN, NOSUPERUSER, NOBYPASSRLS, NOCREATEDB, NOCREATEROLE, NOINHERIT, without role memberships, application-table ownership or schema CREATE. Unsafe existing roles fail for operator review rather than being silently altered. New password verifiers use libpq SCRAM-SHA-256; plaintext passwords are not written as SQL literals.

An advisory transaction lock serializes provisioning. Sorted migrations 001–006 are additive, atomically recorded by SHA-256 in `schema_migration_history`. Changed applied files are refused; add a new repair migration instead. The application has 26 tables, plus this provisioning ledger. Repeating provisioning applies no previously recorded migrations and preserves private records/reviews. Existing installations without a ledger still require a backup and schema review; `IF NOT EXISTS` is not a repair for incompatible columns.

Explicit API, inference, scheduler and retention grants are applied separately. The seed step inserts only the kit's 244 candidate **source metadata entries**, preserving existing reviews. It does not download, approve or publish datasets. Keep the migration-owner connection out of runtime containers. PostgreSQL and object storage must remain private to the authorized backend/network.

## Actual container test design

`scripts/test-production-stack.py` runs only an isolated, randomly named Docker Compose project, with ephemeral credentials, a two-day private test CA and loopback-only ingress. It cleans up only that project's volumes; there is no global prune. It builds the real API image and uses PostgreSQL 17.7, SeaweedFS 4.51 S3-compatible storage, Caddy TLS and actual app/worker services. These are test fixtures, not cloud hosting or a recommendation to expose the fixture configuration.

The checks cover TLS, additive migration replay, four least-privilege roles, Secure/HttpOnly visitor cookies, origin/CSRF and owner isolation, actual encrypted S3/SSE round trips, scanner rejection, a real queued worker calculation, production ML release gates, operator password/MFA, private-record denial and expired-visitor database/S3 deletion. A tiny project-owned ClamAV `.ndb` signature tests real scanner execution; it does not establish the freshness or coverage of a production malware feed. The model-init container downloads checksum-controlled real runtime assets.

Earlier runs identified an inaccessible MinIO test image and then a strict X.509 CA key-usage omission. The fixture now uses a different public S3 implementation and certificates with explicit CA/leaf key usage. TLS verification remains enabled throughout. SDK connections/retries are bounded so broken storage fails rather than hanging a website function.

**Current integration outcome: pending the corrected GitHub CI run.** The earlier attempt verified networked PostgreSQL TLS, provisioning replay and all four role attributes, but failed before the S3 stage. Do not mark later checks passed until the corrected run supplies evidence. The full platform test job passed independently on that earlier source.

## Remaining hosting actions

An authorized Linux host/API hostname, TLS PostgreSQL endpoint and private bucket/service credentials are still needed. Netlify itself is the owner's task; no Netlify login is needed for continuing this source work. The previously selected Supabase organization is at its free-project cap; no unrelated project was deleted or upgraded.

Railway's official status reported new signups paused on 28 October 2026 following its security incident. Existing-account recovery depends on the original identity and the provider's official recovery process. This is not a diagnosed user-account error and is not a reason to bypass a signup restriction. References: https://status.railway.com/ and https://blog.railway.com/p/security-disclosure-recommendation-recover-account-access . No recovery email, reset repository or new identity was created.

After the owner supplies an authorized host, use `deploy/compose.backend.yaml` and `docs/NETLIFY.md`; validate actual DNS/TLS, secrets, SMTP, up-to-date scanner feeds, resource sizing, worker recovery, alerts and provider backup/restore on that host. CI container success cannot certify a live cloud deployment, Netlify adapter execution, Bangladesh model accuracy or all 430 original acceptance scenarios.
