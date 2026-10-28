# Administrator guide

Create the first operator through the CLI password prompt. Public registration is disabled. Operators sign in at `/admin/login` and enroll TOTP at `/admin/security`. Privileged requests require MFA verified within 15 minutes.

Implemented consoles: aggregate overview, module titles/descriptions and feature switches, CMS drafts/publish/version rollback, operator roles/ban controls, source-rights review, runtime/model inspection, CSV dry-run/staging/rollback and hash-linked audit. A privileged role does not grant raw private record access.

CMS page keys: `about`, `methodology`, `privacy`, `terms`, `help`, `contact`, `brand`. Text pages read `title_bn`, `title_en`, `body_bn`, `body_en`; brand reads `name_bn`, `name_en`, `tagline_bn`, `tagline_en`. Use plain text. Executable script/iframe/SVG content is rejected. Re-publish a prior version for rollback.

This is not the complete CMS/operations scope. Scheduled publishing, every homepage/layout/locale/form field, logo upload, organizations, support grants, notification moderation, model hot-swap/canary/drift, re-embedding, automatic backups and distributed queue management are unfinished. Their requirements remain in the ledger.

Never put private medical/legal/child data into public CMS/shared datasets. Candidate sources require asset-level permission evidence. High-sensitivity imports remain blocked until dual review exists. Staging is not publication of a training corpus. Installed model files are not a production evaluation pass.

Additional working controls: `/admin/support`, `/admin/publishing`, `/admin/rights`, `/admin/feedback`, `/admin/notifications`. Read [COLLABORATION_AND_OPERATIONS.md](COLLABORATION_AND_OPERATIONS.md) for precise scopes, fresh-MFA/RLS requirements, worker setup and the difference between rights approval, import staging and production validation.
