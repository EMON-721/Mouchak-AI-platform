# Public access decision — 28 October 2026

The owner's latest instruction supersedes the original kit's end-user authentication/profile requirements: no public login, signup or user profile. Original files and previous working UI source are preserved; this decision does not mark unrelated original acceptance requirements complete.

## Implemented behavior

- Opening public pages creates or reuses an opaque HttpOnly, SameSite browser session. No visitor name, email, password or profile is requested. Its fixed lifetime is at most 24 hours.
- All 50 exact tool routes remain. Processing still requires explicit input consent. The 47 current support flows execute; the three missing core pipelines return truthful errors. No authentication gate was replaced with fabricated AI.
- `/work` contains current-session results, JSON/PDF export links, sharing/transfer workflows, full session export and explicitly confirmed clearing. Loss of the cookie means no account recovery. Retention cleanup follows expiry; it is not an immediate cookie-loss deletion guarantee.
- Public `/login`, `/register`, `/settings` and `/workspace` routes no longer exist. Registration/profile APIs return Gone for valid requests; visitor/legacy password sign-in is disabled. Operator-only sign-in/reset/verification live under `/admin`.
- Authorized operators retain passwords, verified email in production, roles and fresh MFA. A visitor cannot enroll operator MFA or access the admin console. No default admin password exists.
- Existing owner foreign keys are reused with an internal random marker ending `@anonymous.invalid`, empty name and a non-password sentinel. This is an implementation owner key, not a collected email or recoverable public account. Responses and session exports contain no public profile. Existing historical user data is never silently removed or converted.
- Origin/CSRF checks, encrypted records, strict owner checks and upload consent remain. The browser receives neither operator profile details nor another visitor's results. A public cookie remains sensitive: anyone who steals it may use its current scope. TLS, CSP, expiry and HttpOnly are still necessary.
- The retention worker deletes expired guest scopes and encrypted active files while preserving current visitors and historical/operator accounts. It is included in Compose. API tests and a real subprocess exercise expiry, isolation, clearing, cleanup and termination. PostgreSQL/S3 and separate backup-retention operations need staging verification.
- Selected-facts support access is consented and capped at the visitor session expiry. Support is denied after owner expiry even before cleanup runs. A support role still cannot read the raw private run/upload through ordinary routes.

## Preservation and limits

The former user-account UI is retained as inert reference text in `reference/retired-user-interface/`. Existing account tables/data remain for historical preservation and operators. Changing owner storage to a separate table would require a future reversible migration; no working data was dropped.

Public named profiles, recovery, cross-device account history and end-user signup are intentionally removed by the owner's instruction. The temporary public history is not a persistent multi-device account. Notification records/APIs remain but their previous user-profile-based UI is not exposed as a public profile. Complete organization/guardian tenancy, advanced models, reviewed datasets and cloud operations remain incomplete as recorded in the implementation report.

## Browser findings

The real managed browser initially found `crypto.randomUUID is not a function` on HTTP. Client idempotency tokens now use `crypto.getRandomValues` when UUID is unavailable; no noncryptographic fallback is used. A clean browser reload then processed a synthetic bill (125 total against 150 stated, 25 difference), reopened its result under `/work`, switched Bengali/English and downloaded JSON without registration.

The browser's PDF download event timed out twice. Exact downloaded JSON renders a valid 473,753-byte PDF locally in 0.08 seconds, and the anonymous API PDF test verifies a readable document. This is not a successful browser PDF-download claim. Operator browser MFA and three-size responsive/accessibility checks remain outstanding.
