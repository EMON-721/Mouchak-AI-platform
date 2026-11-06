# BanglaRead original lesson library

The reading library adds reviewed original lessons to the existing 12 attributed reading passages. It preserves all 120 original-kit passages and 120 comprehension questions in their original files. Seed text, seed answers and the source files' SHA-256 hashes are available only to authorized content editors. Importing a seed into the editor does **not** approve it, establish redistribution rights or publish it.

## Editorial workflow

1. A `content_editor` or `super_admin` with recent MFA opens a seed or writes an original lesson. The editor supplies Bengali text, bilingual title/topic/educational goal/question/options/explanation, level, reader band, publisher, licence and rights evidence. English fields and permissions are deliberately not invented when a seed is loaded.
2. Saving creates an immutable version. Changing any form field clears the selected version and its review controls; the changed text must be saved as another draft.
3. A different authorized editor opens the exact saved content and records a reason plus five checks: spelling, reader suitability, answer grounded in the passage, educational goal and publication rights. Approval requires all checks. Rejection remains recorded; an existing review cannot be overwritten.
4. Publication revalidates the exact content hash, review, current author/reviewer permissions and MFA enrollment, and the expected library revision. A stale draft must be recreated and independently reviewed. Seed identity, source hashes and original copyright wording remain in the restricted provenance record.
5. Published lessons are listed by level. Drag within a level or use the up/down buttons. The server requires every active lesson exactly once, including any lesson currently hidden because an actor's permissions were revoked.
6. Withdrawal removes the active lesson. Rollback can restore only an exact previously published, independently approved version whose actors are still authorized. Every publish, rollback, withdrawal and order change retains a new history snapshot; publication/withdrawal reasons stay in the restricted history. General audit events contain identifiers, not learner text or rights evidence.

The administrative workspace is `/admin/reading-content`. It uses the platform's existing operator login, role checks, current MFA, CSRF and commit-before-response transaction handling. Public visitors still have no account, login, signup or profile.

## Public practice

`GET /api/reading/passages` combines the preserved 12 passages with active reviewed lessons. It exposes the passage, question/options, level, educational goal, attribution and version. It omits the answer key, explanation, rights evidence and editor identities. Unpublished, rejected, altered or unauthorized content is excluded.

Choosing a new lesson presents its bilingual multiple-choice question. A learner may answer or explicitly skip, mark difficult words and consent to saving the practice privately. The request names the exact passage revision. A changed revision is rejected with `409`; a withdrawn/unavailable lesson is rejected with `404`.

The actual result compares the selected option with the reviewed answer key. It reports `matched`, `review` or `skipped`, identifies the chosen difficult words and cites the exact lesson version. Only an answered attempt reveals the correct option and explanation. This is literal comprehension practice and self-reporting, not an AI pronunciation, fluency or clinical score.

Attempts use the existing encrypted, owner-scoped Run/Consent path. The reading studio detects the module's execution mode and uses the durable queue when enabled. A pending job resolves the currently authorized content after it is claimed. PostgreSQL holds a shared publication lock through result commit; publication and withdrawal take the corresponding exclusive lock. Historical owner-only results remain available until the owner clears them or retention removes them; withdrawal does not silently rewrite history.

## API and storage

| Method | Operator endpoint | Purpose |
| --- | --- | --- |
| GET | `/api/admin/reading-content` | Current revision, preserved seed index, immutable versions and active lessons |
| GET | `/api/admin/reading-content/seeds/{seed_id}` | Original source passage/question, source hashes and unpublished state |
| POST | `/api/admin/reading-content/drafts` | Save a new version against the current library revision |
| GET | `/api/admin/reading-content/drafts/{version_id}` | Full saved lesson, provenance, review and publication history indicator |
| POST | `/api/admin/reading-content/drafts/{version_id}/review` | Independent immutable approval or rejection |
| POST | `/api/admin/reading-content/drafts/{version_id}/publish` | Publish or restore a previously published version |
| POST | `/api/admin/reading-content/withdraw` | Withdraw an active lesson with a reason |
| POST | `/api/admin/reading-content/order` | Reorder the complete active set |

All new records use the existing `Config` table under the reserved `reading-content:` namespace. Generic CMS publishing writes only `cms:` keys and cannot activate these lessons. There is no new database schema, sensitive-user-column grant or cloud service dependency. The inference role reads only content configuration and the existing minimal user `id`/`role`/`banned` columns when checking publication eligibility. Public catalogue queries batch-load the active versions, reviews and actors instead of querying once per lesson. Corrupt individual records fail closed.

Limits are explicit: 250 words per passage, five levels, two to six distinct bilingual options, 240 active lessons and 500 retained drafts. Reaching the retained-version limit requires a planned, audited archival migration; the API never discards history to make room. Current revision checks and the PostgreSQL transaction lock prevent concurrent editors from overwriting another publication. SQLite remains a local-development database, not the production concurrency acceptance target.

## Requirement and verification status

| Original BanglaRead requirement | This implementation | Acceptance boundary |
| --- | --- | --- |
| Preserve original authored passages/questions | All 120 + 120 retained byte-for-byte with source hashes | No real seed has been autoapproved or republished |
| Passage editor and bilingual educational goals | Implemented with strict input/option/provenance validation | Editorial quality and rights require real independent editors |
| Independent spelling/content-safety review | Five recorded checks, immutable decisions and actor revalidation | Teacher/guardian moderation and flagged-word queues are separate remaining workflows |
| Lesson tree order and per-level publication | Flat level hierarchy, drag/keyboard order, publish/withdraw/rollback | Does not claim an arbitrary nested curriculum builder |
| Literal comprehension and explanation | Real reviewed-key comparison, optional skip and exact revision citation | No generated or inferred pronunciation correctness |
| Private user practice | Existing consent/encrypted runs/owner controls and durable inference queue | No public learner profile or child-account enablement |
| Private-stack integration | Actual TLS/MFA/PostgreSQL/queue test added to `scripts/test-production-stack.py` | Execution outcome is recorded in the implementation report and CI, never inferred from source presence |
| Remaining specialized scope | Existing speech work preserved | Guardian/teacher linkage, adaptive/phoneme/rubric/lexicon, progress/offline/challenge workflows and Bangladesh child field validation are not certified by this change |

`tests/test_reading_content.py` uses explicitly disposable original text and separate test editors. It covers seed integrity, CSRF/roles/MFA, independent review, invalid input, hidden answers, encrypted owner-only attempts, revision conflicts, rollback, immediate withdrawal, revoked permissions, tampered/corrupt content, exact-set ordering and a real separate inference-worker process. These fixtures are **not** production editorial approvals, labelled Bangladesh field data or AI evaluation results.

The public README remains a concise project overview; detailed verification and remaining scope belong in `IMPLEMENTATION_REPORT.md` and the module progress records.
