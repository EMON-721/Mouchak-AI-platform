# Consented collaboration and audited operations

This continuation starts from commit `dab5b9956c77eac89d79e0c6bf15ea32d1e7a04e`. Earlier requirements, records, identities and the original acceptance matrix are preserved. This adds shared infrastructure; it does not certify the full 50 specialized tools.

## User workflows

Open `/workspace/sharing`, choose a result from the current workspace, and select the exact information to transfer or share. The pane resets when the user/workspace changes.

**Temporary support:** enter the exact email of an eligible MFA-enabled support agent or Super Admin, choose result facts, give a purpose and an expiry of 1–60 minutes, and explicitly consent. The recipient sees an encrypted immutable snapshot of those selected facts only, through `/admin/support`. Inputs, raw images/PDFs, asset IDs and other results remain inaccessible. Fresh MFA, current role, recipient identity, owner status, expiry and revocation are checked. Every view is audited. `/workspace/sharing` can revoke future access immediately; previously seen information cannot be recalled. This is not a blanket document-access grant.

**Cross-tool transfer:** choose a different available tool, map declared compatible input fields, inspect the preview and consent. Only selected input values are copied; units are not silently converted and raw uploads never transfer. Open the private draft in its destination workspace, review/edit it and separately consent to processing. A successful run records its original source run as lineage and consumes the draft once. Invalid ownership, wrong target/workspace, incompatible types, unavailable tools and repeat processing are rejected. Deleting the source result/account cascades its sharing records and drafts. Saved destination results retain their own separately consented record lifecycle.

Privacy exports now include grants/drafts, owner notifications and submitted feedback. Support grants are encrypted; audit logs contain actions and identifiers rather than shared fact values.

## Admin workflows

All of these routes use the existing central identity and fresh MFA. Menu visibility does not grant permission.

| Route | Permission | Implemented action |
|---|---|---|
| `/admin/support` | Support Agent or Super Admin | View only current grants addressed to that exact account |
| `/admin/publishing` | Content Editor or Super Admin | Schedule an existing CMS version; inspect status; cancel pending schedules |
| `/admin/rights` | Dataset Reviewer or Super Admin | Record structured asset-level rights and inspect independent reviews |
| `/admin/feedback` | Support Agent or Super Admin | Classify submitted feedback and update its triage state |
| `/admin/notifications` | Super Admin | Create a bilingual in-app notice for one selected account; inspect own dispatch metadata |

Sensitive training/reuse approval requires two distinct authorized reviewers agreeing on the same exact asset, terms, license, source date, coverage, scope and sensitivity. One reviewer cannot count twice. Revocation starts a new review round; old approvals do not silently reactivate it. Reference-only approval is distinct from training/reuse. Evidence is reviewer-supplied; automated tests use synthetic evidence and do not grant rights to any actual source. Approval does not itself import, embed, train or validate a dataset/model. Schema-specific publication and evaluation gates remain unfinished.

The notice INSERT policy allows the authorized operator to create a recipient-owned notice; it does not grant that operator general read access to the recipient's notifications. The recipient can mark their own notice read/unread. Operational dispatch lists contain IDs/timestamps, not recipient message bodies.

## Durable CMS scheduler

Development, alongside the existing web/API process:

```bash
.venv/bin/python -m services.model_worker.scheduler
```

A one-poll operational command is also available:

```bash
.venv/bin/python -m services.model_worker.manage run-scheduled
```

The worker polls persisted rows, claims due schedules transactionally and publishes each once. A manually changed page produces `conflict`; a banned/deleted/demoted author produces `author_unavailable`. Cancelled/completed jobs are not republished. A heartbeat is available at `/api/admin/publishing/health`. The API is not proof that a production worker was deployed.

Apply migration 004 after 001–003. Production uses a separate `mouchak_scheduler` database role, TLS and the same stable data key. Do not grant the API role membership in the scheduler role. Provision the scheduler login/password through your secret-management process, then grant only the required access, for example:

```sql
-- Provision mouchak_scheduler as LOGIN NOSUPERUSER NOCREATEDB NOCREATEROLE NOBYPASSRLS.
GRANT USAGE ON SCHEMA public TO mouchak_scheduler;
GRANT SELECT(id, role, banned, mfa_enabled) ON users TO mouchak_scheduler;
GRANT SELECT, UPDATE ON cms_publish_schedules, cms_versions TO mouchak_scheduler;
GRANT SELECT, INSERT, UPDATE ON configuration TO mouchak_scheduler;
GRANT SELECT, INSERT ON admin_audit_events TO mouchak_scheduler;
```

`deploy/compose.yaml` includes a scheduler service with `SCHEDULER_DATABASE_URL`. Its process refuses an ordinary application database role in production. The API sets transaction-local user identity and recent-MFA expiry; migration 004 enforces these at SQL level. Do not grant arbitrary UPDATE/DELETE on support snapshots, source reviews or private runs to external clients. Support expiry/revocation and ownership remain server/SQL checked. Separate background-worker permissions do not become public HTTP capabilities.

## Encrypted local recovery drill

The implemented archive tool covers local development SQLite and encrypted local assets only. It deliberately refuses production PostgreSQL/S3. Configure an independent `BACKUP_ENCRYPTION_KEY`, kept outside source control and separate from `DATA_ENCRYPTION_KEY`.

```bash
.venv/bin/python -m services.model_worker.backup create --state .state --archive /PRIVATE-LOCATION/checkpoint.mouchak
.venv/bin/python -m services.model_worker.backup restore --archive /PRIVATE-LOCATION/checkpoint.mouchak --destination /NEW-LOCATION/restored-state --dry-run
.venv/bin/python -m services.model_worker.backup restore --archive /PRIVATE-LOCATION/checkpoint.mouchak --destination /NEW-LOCATION/restored-state
```

The tool takes a consistent SQLite snapshot, includes the data key and encrypted local assets inside a separately authenticated encrypted archive, verifies checksums, rejects symlinks/unsafe paths and refuses overwrite. The local limit is 100 MiB. Restore uses a new directory, relocates asset paths, revokes old sessions/tokens and support grants, and cancels pending publication. Existing live data is never overwritten. Keep restored data offline until operator review; backups have independent retention and cannot silently resurrect consent. Production provider snapshots, bucket versioning, key recovery and live restore drills remain pending.

## Evidence and limits

`tests/test_collaboration_operations.py`, `tests/test_backup_recovery.py` and `scripts/test-collaboration-postgres.mjs` verify API authorization, SQL isolation, expiry/revocation, fresh MFA, encrypted snapshots, strict transfer mapping, conflict rollback, independent reviews, notices, recovery tamper/path safety and a real scheduler subprocess publishing a due job and exiting cleanly. Final suite: `docs/audit/continuation-regression.xml` (257 passed, zero failures/errors/skips). PostgreSQL WASM checks cover all 20 tables/migrations; external server networking is not verified.

Browser observations verify live web/API health, language switching, 12 reading passages and word toggles, the 81-entry dictionary, dynamic price rows and logged-out guards. Authenticated User/Admin browser E2E and three viewport widths remain unverified. Secure browser rules require the user to supply credentials or complete signup; no credential-entry or authentication bypass was added.
