# Reviewed facility and pharmacy directory pipeline

This implements the missing schema-specific ingestion, publication and retrieval path for `cliniccompass-bd` and `oshudhkhoj-bd`. **No actual provider/pharmacy dataset is bundled or approved.** Default production availability therefore remains blocked. Test records are explicitly owned DEMO fixtures and are never installed as real directories. No full original clinical/medicine module certification is implied.

## Workflow and permissions

1. A `dataset_reviewer` or `super_admin` with recent TOTP MFA selects a matching candidate source under `/admin/rights`. Two different reviewers must record the same current asset-level `approved_train_and_reuse` decision with `public_nonpersonal` sensitivity. A legacy single-review state flag is insufficient. The asset must have a credential-free HTTPS reference. Rights evidence must cover the specific supplied records and their public directory reuse; this is a human rights review, not automatic licence discovery.
2. Under `/admin/directories`, submit the schema-specific record array. Dry-run validates every record, timestamps, location bounds, row limit, duplicate identifiers and extra fields. It creates an encrypted immutable ingestion snapshot with the current source-review round and evidence fingerprint. It does not publish anything.
3. A **different** authorized operator opens the complete batch, examines the records/source/rights/checksum and explicitly publishes it. Optimistic `expected_revision` protection prevents an outdated page from overwriting a newer active revision. PostgreSQL transaction advisory locks serialize competing publications/withdrawals before the active pointer exists. The active snapshot and ingestion states are changed in one transaction.
4. Public account-free workspaces use the existing consent, owner-isolated run, durable inference queue and exports. Search runs the installed quantized multilingual MiniLM ONNX model plus BM25. District filtering is exact after Unicode/Bengali-digit normalization. Pharmacy results additionally require literal product-name evidence; semantic proximity alone cannot substitute a medicine. It returns at most 20 records and the source licence/date/verification timestamps. No diagnosis, dosage, substitution, provider endorsement or guaranteed current stock is generated.
5. Every search checks current source approval, review round, evidence fingerprint and each record's verification age. Facility records expire after **90 days**, pharmacy observations after **24 hours**. These are conservative application freshness limits, not guarantees of factual accuracy. Revocation or an evidence change immediately makes the snapshot unavailable for new searches. Historical private exports remain dated records, not live claims.
6. Withdraw the active revision without deleting its staged history. A second operator can explicitly republish a retired revision as rollback, provided its original rights snapshot and records are still valid and fresh. The generic dataset rollback cannot remove a published directory behind its active pointer.

The independent inference PostgreSQL role receives read access to the source registry and public configuration snapshot, never blanket access to encrypted ingestion jobs. Existing owner record RLS, privileged recent MFA, internal transport authorization, CSRF, audit and encryption remain in force. There is no new table or destructive migration; the existing `configuration` and `ingestion_jobs` tables hold versioned snapshots. Reapplying the additive runtime grants supplies the worker's additional source-registry read permission.

## Schemas

Every record requires the following fields. Only public institutional directory details belong here. Patient details, private contact lists, identification numbers, credentials, arbitrary additional columns and free-form medical histories are outside the schema and rejected. Names/addresses are still human-reviewed: the software cannot prove that a purported public institutional address is nonpersonal.

| Field | Rule |
|---|---|
| `id` | 1–80 ASCII letters, digits, underscore or hyphen; unique within batch |
| `name_bn`, `name_en` | Public facility/pharmacy name, 1–160 characters |
| `district_bn`, `district_en` | District names, 1–80 characters |
| `address_bn`, `address_en` | Public institutional address, 1–240 characters |
| `latitude`, `longitude` | Optional pair; coarse Bangladesh bounds 20–27 N, 88–93 E; no user GPS collection or distance claims |
| `verified_at` | ISO 8601 datetime with explicit timezone, not in the future and within the schema freshness window |

`facility_v1` also requires `services_bn` and `services_en`: arrays of 1–20 nonempty service labels, each at most 100 characters.

`pharmacy_v1` also requires `product_name` (1–160), `strength` (1–80), `formulation` (1–80) and `reported_availability`, one of `reported_available`, `reported_unavailable`, `not_confirmed`. The status is a dated source observation, not inventory reservation or medical advice. Strength/formulation are source transcription, never inferred from a query. No price, stock quantity, medicine recommendation or dosing field is invented.

Each batch holds 1–200 records, at most 200,000 serialized JSON characters. Each new publication replaces the active **single-source batch** for that tool. Multi-source federation, provider verification, official directory acquisition and clinical validation remain separate unfinished requirements.

## APIs

All routes below require the existing internal production token, authorized operator session and recent MFA. Writes also require CSRF and trusted origin. Use the website proxy `/api/*`; never expose the private service token in a browser or GitHub.

| Method/path | Payload or result |
|---|---|
| `GET /api/admin/directories` | Active revision IDs and batch metadata |
| `POST /api/admin/directories/dry-run` | `{ "source_id": "<reviewed-source-id>", "schema_name": "facility_v1", "records": [...] }` |
| `GET /api/admin/directories/{job_id}` | Complete batch, source/rights snapshot and checksum for authorized review |
| `POST /api/admin/directories/{job_id}/publish` | `{ "expected_revision": null }` initially, otherwise the current revision ID |
| `POST /api/admin/directories/{slug}/withdraw` | `{ "expected_revision": "<current-revision-id>" }` |

Public processing uses the existing `POST /api/tools/{slug}/jobs` (or synchronous `/runs` when durable execution is disabled), with `inputs: { "text": "<service or medicine name>", "district": "<optional exact district>" }` and explicit `consent: true`. It records and exports an owner-private result. Missing approved/current data returns a clear unavailable error, never synthetic records. The public tool becomes limited-support available only while a valid snapshot exists; full advanced evaluation status remains false.

## Verification

`tests/test_directory_pipeline.py` uses explicitly synthetic isolated fixtures with the actual local ONNX model. It tests independent review/publication, stale/invalid/private schema refusal, real retrieval, district filtering, medicine literal-match refusal, revision conflicts/rollback, rights revocation, query-time expiry, CSRF/role checks and cross-owner run denial. `scripts/test-production-stack.py` additionally exercises two actual operator password/MFA sessions, source reviews, publication, the isolated PostgreSQL role and real queued ONNX retrieval over verified TLS in disposable Docker services, followed by revocation/withdrawal. Check the latest CI report for the actual run result; the presence of test code is not a passing claim.

No real Bangladesh provider dataset, clinical benchmark or live stock validation has passed through this pipeline. Acquiring those rights-cleared and current records remains an external data requirement. This feature does not complete the remaining 50-tool advanced scope.
