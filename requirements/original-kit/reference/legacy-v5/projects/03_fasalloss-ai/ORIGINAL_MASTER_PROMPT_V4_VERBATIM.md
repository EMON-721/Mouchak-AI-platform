# FasalLoss AI — COMPLETE BANGLADESH AI WEBSITE BUILD MASTER PROMPT V4

**Independent, end-to-end Work prompt | Edition: 2026-10-25 | Project 03/32 | Original V2 included unchanged**

# V4 FULL EXPANSION — EXECUTABLE BANGLADESH-FIRST PRODUCT CONTRACT

**Paste this entire file, by itself, into ChatGPT Work.** It includes the previous full V2 master prompt unabridged below, plus detailed expansion requirements and Bangladesh data source records. Do not request a separate generic prompt. Do not treat this prompt as proof that an app or model already exists.

## 00 — ACTUAL BUILD, SCOPE, OWNERSHIP, AND SOURCE-OF-TRUTH
You are a full delivery team (product, design, frontend, backend, data engineer, applied ML, NLP, security, QA, developer experience). Build a real, usable Bangladesh-first product; create code and runnable tests rather than a plan-only response. As these 28 projects are NOT among the four already reported as built, create a separate new repository only if the owner authorizes it. If a project codebase already exists, audit and **UPGRADE** it in place: never overwrite existing routes, remove data, reset DB, force-push or create a duplicate repository. Read current code, create change plan and reversible DB migrations. The public website should be simple enough for a first-time visitor on a low-end Bangladeshi Android device to complete the main job in three steps, while the authenticated product contains deeper optional capabilities and the admin app is comprehensive.

The output must include working code, real input-dependent operations, seed import path, admin CMS, role gates, tests, source registry, privacy controls, docs, and GitHub push verification if authorized. Show what is really working; ML not deployed = ML feature labeled unavailable, never mocked as if real. Do not require spreadsheet uploads for end users. Set locale bn-BD default, Asia/Dhaka dates, BDT, correct Unicode Bengali typography, optional English only with full translation, responsive at 320/360/768/1024/1440 and slow/mobile network support.

## 01 — DELIVER AN EXPANDED, NOT OVERCOMPLICATED, INFORMATION ARCHITECTURE
The public navigation has 4–5 visible top-level items maximum: Home, Start, How it Works/Resources, Help, Sign In. Guest's primary CTA is obvious. Logged-in user obtains Dashboard, New task, Timeline/History, Saved Reports, Profile, Account & Privacy, Alerts with explicit consent, Personal Workspace and Export/Delete. Features are shown contextually, not as 24 confusing menu items. Keep a breadcrumb and mobile bottom bar with ≤4 items. Ship working empty, loading, retry, offline-draft, expired-session, permissions, and data-source-unavailable states. Onboarding: language preference, anonymous try-first option where safe, example walkthrough clearly labeled demo, data-consent explanation, progress indicator (three steps only), editable review screen and downloadable result.

The public site must provide editable Home hero and benefits, product screenshots that reflect actual UI, About, Project Bio, Editorial Team with placeholder until owner supplies real information, Contact, FAQ, Terms, Privacy, Accessibility, Sources, Model & Data Limitations, Transparency, Feedback and Status. All claimed endorsements, accuracy percentages, public uptake figures, AI model benchmarks and partner logos require evidence; do not invent. Content pages must not become broken links. Support simple SMS-length Bangla instructions where feasible but do not claim actual SMS delivery without provider.

## 02 — SUPER ADMIN AND ROLE-BASED CONTROL PLANE (COMPLETE CMS)
Create a real separated `/admin` console, server-protected APIs and a permission matrix. At least: Super Admin, Site Manager, Editorial Admin, Data Curator, AI Reviewer, Security Auditor, Support (metadata-only), Moderator and scoped Project Operator; only Super Admin can grant powerful roles. No superadmin hardcoded secret or public default password. MFA, least privilege, approval of sensitive changes, audit trails, session invalidation. Provide UI and APIs for all:
1. Executive dashboard: real counters only, incidents, queued jobs, stale data, failure rates, import status, adoption funnel, and source freshness.
2. Site CMS: every section of Home, About, project Bio, mission, team, testimonials (only verified), contacts, notices, terms, privacy, FAQs, help articles, tutorials, onboarding copy, errors, footer, navigation, internal/external links, CTA, marketing SEO, Open Graph and robots/sitemap.
3. Visual builder: typography, color tokens, logo SVG upload, light/dark theme, section layout, image assets, responsive previews; revision history, staging preview, scheduled publication, rollback, ownership and moderation.
4. User administration: searches, account health, ban/unban, delete request workflow, anonymization, consent receipt, data export, impersonation PROHIBITED without tightly controlled audited support protocol; never show private content to arbitrary staff.
5. Permissions: page-level and action-level server-side RBAC, separation between support and sensitive uploads; sensitive-source access uses explicit review authorization.
6. Data collection studio: source catalog, licensing metadata, manual CSV/JSON/PDF imports with admin validation, schema mapping, deduplication, quarantine, manual review, approval/publish/unpublish, revisions, provenance, stale alerts, daily import history and rollback.
7. AI studio: model provider adapters, prompt templates with versioning, inference logs with PII redacted, class labels, configurable thresholds, no arbitrary accuracy claims, A/B testing only where ethical, evaluation sets and release approval.
8. RAG studio when relevant: documents, OCR preview, licensed corpus scope, embedding job queue, chunk viewer, citation inspector, indexing failures, relevance score checks, prompt injection quarantine, old-source retirement.
9. Reports and exports: feedback, flag queue, review decisions, dashboard charts, PDF/CSV exports based on permissions, audit logs, abuse monitoring, deletion proofs.
10. Security & operations: API keys stored in server secrets, storage expiry, backups, restore drills, retention rules, moderation, signed media links, rate limiting, feature flags, incident log, site maintenance, system health, deployment checklist, admin activity export.
11. Location/localization: editable division/district/upazila data only from verified source, BN/EN translations, units, calendar display, glossary and data-source provenance.
12. Domain-specific admin workflows below. No admin panel permission can override privacy unlawfully; opt-in and logging remain required.

## 03 — ARCHITECTURE / ACTUAL SERVICES AND DATABASE
Prefer Next.js stable App Router + TypeScript + Tailwind + accessible components + Zod + PostgreSQL/Supabase if owner has authorized credentials, otherwise reproducible local development with SQLite/Postgres and `.env.example`. Add migrations and typed schema for: users/profiles, role assignments, permissions, projects/records, media objects, jobs, predictions, user-corrections, dataset_sources, import_batches, source_records, source_versions, content_pages, content_revisions, consent_events, audit_events, notifications, support_cases, flags, system_settings, feature_flags, RAG documents/chunks/citations if used. Use unique compound keys, transaction boundaries, tenancy/ownership, timestamps with provenance; indexes on user_id, project domain lookup, history date and source version. Row-level security and server authorization on *every* user-content access. No user private data in public aggregation without consent and anonymization. No public storage bucket for uploads or child/health data. Keep Backoffice APIs and end-user APIs separate, protected and integration-tested.

Repository layout: `app/(public)`, `app/(workspace)`, `app/admin`, `components/{ui,domain}`, `lib/{auth,db,validation,source,ai,privacy}`, `models/` only small metadata, `data/seed/`, `scripts/import-data.*`, `migrations/`, `tests/{unit,integration,e2e}`, `docs/{USER_GUIDE_BN,ADMIN_GUIDE_BN,DATASET_REGISTER,MODEL_CARD,SECURITY,QA_RESULTS,DEPLOYMENT}.md`, `config/{content,features}.json`, `.github/workflows/ci.yml`. Use a clean adapter boundary for heavy inference deployed elsewhere; free Vercel serverless is not an unlimited ML GPU host. Ship honest deterministic/numeric/keyword baseline as applicable, make heavyweight model optional and avoid false AI labels.

## 04 — TRUSTWORTHY AI / ML / NLP / RAG IMPLEMENTATION
Use project-specific pipeline below. At minimum ship typed input schema, parser/normalization (Bangla digit support), review/confirm step, deterministic baseline or actually integrated evaluated open model, confidence + abstention, source provenance, error budget, evaluation harness, and logs with personal data redacted. Real model claims require model ID, artifact checksum, license, dataset card, train/validation/test split, calibration, latency/accuracy per subgroup and Bangladesh relevance. Sourced answers show cited pages and date; say 'I cannot verify from available sources' rather than hallucinate. No generic prompt alone can transform a mock rule into a working neural model. Make safe case handling deterministic. Guard RAG against document prompt injection, cross-user search leakage, mis-citations and obsolete law/medical guidance. Prefer retrieval lexical search + reviewed snippets as functional first release where vector retrieval is unavailable; make reranker/vector adapter optional.

Build background ingestion idempotently: fetch where allowed, parse/validate, preserve raw reference metadata and hash, quarantine invalid, compare previous version, admin approve, publish, roll back and show user-facing as-of date. Provide units and formulas and sample error tests. For computer vision, do image-quality assessment, request another photo if uncertain, avoid unsupported numeric measurement from pixel-only evidence; allow user correction. For audio, explicit consent and do not record by default. For geospatial, honor location fuzzing, source resolution and sensitive redaction.

## 05 — DATA ACQUISITION CONTRACT: REAL LINKS, NOT FAKE GOVERNMENT CSVs
Use the project-specific `DATASET_SOURCES.json` below as a candidate reference registry, NOT guaranteed downloadable training data. Try lawful accessible public government/statistical pages, official download links, reviewed reference publications, and voluntary privacy-preserving local reports. For every import, record original URL, publisher, title, observed publication date, fetched timestamp, source format, geographic/temporal coverage, accessible API/file/manual mode, attribution, copyright/terms, permitted usage, review status, checksum, row count, schema and data gaps. Do not scrape at scale, bypass rate limits, ignore login barriers or assume public data grants redistribution/ML-training rights. Where non-downloadable, support MANUAL ADMIN PDF/CSV upload with rights verification, source-date tagging, and show 'No verified data published here yet' to users. Data imported solely as fixtures must have `is_demo=true`, cannot feed real dashboards, and cannot masquerade as government data. Do not request users to acquire data in order to make app minimally functional: starter taxonomy/demo paths and user-input-first features must work now.

## 06 — VISUAL, USER RESEARCH, DESIGN & CONTENT
Create distinctive brand colors based on the project's topic; avoid repeated gradient dashboard templates. Design a recognizable SVG icon/logo, bespoke illustration, polished card anatomy, readable Bangla font fallbacks, accessible contrast, pointer and keyboard targets, simplified mobile capture/search forms, sticky primary action, informed onboarding, charts/tables with alt text, printing and correct Bengali PDFs. Admin-controlled brand kit and CMS drive live website appearance. Avoid stock image reliance or unverifiable statistics. Adopt UX copy testing in simple Bengali, error states that explain corrective actions, and the 3-step first task test. Include real downloadable sample reports for synthetic test cases labeled SAMPLE.

## 07 — TESTS, SECURITY AND SHIP CRITERIA
Run typecheck, lint, tests, build and Playwright happy path where environment allows. At least 30 unit cases, 12 backend tests and 8 end-to-end scenarios: anonymous core flow, signed-in save/history/export/delete, admin content publish/rollback, dataset import/checksum rollback, cross-user record leakage denied, media rejection and PII scrub, source loss gracefully handled, model unavailable, Bengali text width, and mobile responsive. Add at least six adversarial ML/RAG cases and domain-specific risk cases below. Record actual pass/fail results and screenshots only when produced. Provide quickstart one command, seeded local demo, Docker optional; no unaudited clinical or legal advice. Keep secrets uncommitted. End by creating or updating the owner-authorized individual GitHub repository and verify the remote commit. No simulated push. If lacking GitHub write permission, deliver exact local code and command sequence and say remote push not performed.

## 08 — SPECIFIC PRODUCT: FasalLoss AI (MAJOR V4 EXPANSION)
**About / mission in Bangla:** কৃষক ফসলের ক্ষতির ছবি, জমির পরিমাণ ও নিজের ব্যাখ্যা দিয়ে ক্ষতির ডায়েরি এবং সহায়তা চাওয়ার প্রমাণভিত্তিক সারাংশ বানাতে পারবেন।
**Domain:** Agriculture / Climate Recovery. **Core modalities:** Field images/videos; acreage/quantity numbers; farmer explanation. This is NOT a one-size-fits-all photo app. Let users start from the lowest-friction appropriate input (typed text, number, map pin, audio, photo, video, uploaded document); do not force camera or signup.

### A. Guided public interaction, with concrete screens
1. **Entry / Discover:** state in Bengali what the site does, 1 prominent CTA, 3 short examples, data limitation, and optional no-login exploration.
2. **Step 1 — Capture / Type:** সহজ ইনপুট দিন—Field images/videos, acreage/quantity numbers, farmer explanation. Provide phone camera/file/keyboard alternatives as appropriate, explicit consent, photo/audio preview, saved draft and field help.
3. **Step 2 — Verify / Correct:** AI/নিয়মের শনাক্ত তথ্য নিজে যাচাই করুন. Show extracted fields alongside original input (not obscured), edit numeric units, checkbox provenance and unknown-data flag.
4. **Step 3 — Understand / Act:** সূত্রসহ ফলাফল দেখুন, ভুল সংশোধন করুন এবং নিজের রিপোর্ট সংরক্ষণ/শেয়ার করুন. Provide evidence-linked actionable summary, what data were used, what AI could NOT establish, next-step checklist, report download and source date.
5. **Revisit:** saved project dashboard, date filters, compare visits, bookmarks, safe share/export when opted-in, history and permanent-delete request.
6. **Failure:** invalid input, null confidence, broken source, inaccessible model, duplicate evidence, offline, slow connection, unauthenticated access and private-document conflicts all have tested UX.

### B. Functionally separate feature modules (each complete and working)
1. **Crop loss journal by plot and season**: implement not only navigation, but database state, working form/API, view, export, role check, and error/empty behavior.
2. **Multi-photo annotation with review**: implement not only navigation, but database state, working form/API, view, export, role check, and error/empty behavior.
3. **Itemized input-cost evidence vault**: implement not only navigation, but database state, working form/API, view, export, role check, and error/empty behavior.
4. **Weather event reference and sourced timeline**: implement not only navigation, but database state, working form/API, view, export, role check, and error/empty behavior.
5. **Damage documentation export**: implement not only navigation, but database state, working form/API, view, export, role check, and error/empty behavior.
6. **Consent-only anonymized aggregated insights**: implement not only navigation, but database state, working form/API, view, export, role check, and error/empty behavior.

### C. User profile / information architecture
Pages: branded Home, Guided Tool, Results, Compare/History, Evidence Sources, Learning Library, My Saved Items, Downloads, Notifications if consented, Help, Contact, About, Mission/Bio, Privacy/Terms, Accessibility. Settings for Bangladesh region, preferred units, language, offline-draft, accessibility, profile update, data export and account deletion. Public site top navigation <=5 visible items. Keep advanced modules beneath context tabs.

### D. AI contracts and validation
**Required domain-specific baseline:** Image damage-area annotation with explicit scale uncertainty; OCR for receipts; conservative crop-type recognition where trained; calculators using user-entered area/yield; Bangla RAG agronomic recovery guidance.
Break the implementation into data parsing, deterministic validator, genuine ML/OCR/speech/vision model only if real model + runtime are available, optional grounded RAG, source citations, unit rules and user correction. Provide a JSON model output schema with `input_id, modality, extracted_fields, confirmed_fields, model_id, model_version, source_urls, dataset_version, confidence, unknown_fields, warnings, limitations, human_review_required, processed_at`. A confidence score requires empirical calibration, not hardcoding. Each model has a model card, test cases, reproducibility, latency measurements, and error analysis for Bangladesh examples; absent local training data = label as unvalidated baseline. Implement dataset-splitting rules appropriate to place/person/time/document origin and evaluate domain shift.

### E. Data schema / sample fixtures / data governance
Core dataset fields must include project-specific concepts from starter taxonomy: `field_01` (ফসলের নাম), `field_02` (জমির পরিমাণ), `field_03` (ক্ষতির ছবি), `field_04` (বৃষ্টির নথি), `field_05` (ঝড়ের ঘটনা), `field_06` (বন্যার পানি), `field_07` (চারা নষ্ট), `field_08` (পাতার ক্ষতি), plus `record_id, owner_id, collected_at, location_scope, evidence_file_id, reviewer_id, consent_version, provenance, source_date, is_demo`. Explicitly annotate which domain fields are a **measured lab value**, a **user claim**, a **model inference** or a **verified official publication**. Never intermingle them in numeric charts. Use provided `SEED_TAXONOMY.json`, `SEED_TAXONOMY.csv`, `EVALUATION_CASES.json`, `DATASET_SOURCES.json` as initial fixture and imports; these contain human-authored category names and simulated QA cases, not secretly fabricated facts. Add SQL migrations, data import UI, editorial approval, source expiration alerts, quality dashboards, CSV export/import with validation and a dictionary of Bengali synonyms. Research source pages and fetch only allowed files with documented rights, then persist source checksums/rights.

### F. Dedicated admin modules for this project's domain
- Crop loss journal by plot and season: Admin must configure taxonomy, upload evidence rules, view redacted model/output metrics, approve reviewed content, and publish/rollback with audit.
- Multi-photo annotation with review: Admin must configure taxonomy, upload evidence rules, view redacted model/output metrics, approve reviewed content, and publish/rollback with audit.
- Itemized input-cost evidence vault: Admin must configure taxonomy, upload evidence rules, view redacted model/output metrics, approve reviewed content, and publish/rollback with audit.
- Weather event reference and sourced timeline: Admin must configure taxonomy, upload evidence rules, view redacted model/output metrics, approve reviewed content, and publish/rollback with audit.
- Damage documentation export: Admin must configure taxonomy, upload evidence rules, view redacted model/output metrics, approve reviewed content, and publish/rollback with audit.
- Consent-only anonymized aggregated insights: Admin must configure taxonomy, upload evidence rules, view redacted model/output metrics, approve reviewed content, and publish/rollback with audit.
Also: domain field editor, safe thresholds approved by expert when required, local region maintenance, per-role dataset approval, de-identification queue, model feedback error tracker, public taxonomy moderation, evidence access by least privilege, export with audit, deletion and consent proof, file storage retention and versioned model rollback. 

### G. Domain safety boundary
**PROPORTIONATE CAUTION:** no confident safety guarantee, official prediction, legal conclusion, calibrated measurement or certification when not supported by actual evidence; provide uncertainty and referral as appropriate.

### H. Screens that must exist in final acceptance
- Mobile Home with working CTA and sample walkthrough marked DEMO.
- Main input -> confirmation -> output full journey connected to backend and persistent state if signed in.
- Side-by-side original and extracted data (for uploaded media), source evidence, limitations and easy correction.
- Dashboard with actual own records, useful graph/table, export, edit, delete and helpful empty state.
- Admin Content Builder with editable brand, homepage, About/Bio, FAQ and live staging preview.
- Admin Dataset Manager with URL metadata, JSON/CSV import, quarantine, review, version changes and rollback.
- Admin AI manager with visible model adapter status, evaluation outcomes and redacted error reports.
- Admin User/RBAC and privacy audit with negative privilege tests.

### I. Milestone sequence / measurable definition of done
- **M1 Foundations:** functional mobile forms, navigation, permissions, DB migrations, tests, Bangla content and audit.
- **M2 Core computation:** input-dependent baseline that truly works, verified calculations / retrieval as applicable, confirmations, source transparency.
- **M3 Data and AI:** reviewed imports, evaluation dataset, licensed model integration if possible; otherwise clear feature-gate and working deterministic baseline.
- **M4 Admin:** all CMS/editors, source lifecycle, role gates, audit and reversible configurations.
- **M5 Release:** QA passing, security review, deploy docs, source attribution, README, optional GitHub push authorization.
Do not stop after drawing a landing page: every milestone must have code, API, tests and documentation.

## 09 — API, DATA VALIDATION, ACCESSIBILITY, OBSERVABILITY AND RELEASE DETAILS
Implement typed REST handlers/server actions (actual code) for `POST /api/records`, `GET /api/records`, `GET /api/records/[id]`, `PATCH /api/records/[id]`, `DELETE /api/records/[id]`, `POST /api/analyze`, `POST /api/uploads/presign`, `GET /api/sources`, `POST /api/feedback`; admin `/api/admin/content`, `/api/admin/content/[id]/publish`, `/api/admin/sources`, `/api/admin/imports`, `/api/admin/imports/[id]/approve`, `/api/admin/models`, `/api/admin/audit` gated by role. For each endpoint specify method, required role, Zod input schema, response type, rate limits, error codes, idempotency behavior, test cases and pagination. Never expose cross-user documents or sensitive exact geolocation via path guessing.

Data import workflow: register source -> legal/ToS/license note -> upload/authorized fetch -> file hash -> parser -> column mapping -> validation -> dedup -> staging -> QA sampling -> admin approval -> publish -> dated public source badge -> revision / unpublish. CSV/JSON seed importer includes `--dry-run`, `--batch-id`, `--rollback` and no destructive reset. Add documentation on which seeds are curated labels, what counts are true official observations, how to fetch lawful data, how to label user contributions and provenance.

Observability: non-PII traces, error grouping, rate-limit telemetry, model adapter status, source freshness, import error counts and performance budget. Test on low-end phone CPU; cache public static source summaries and lazy-load maps/models. Implement accessibility semantics, keyboard, color contrast, focus, screen reader output, localized date/number, reduced motion, print to PDF correctly rendered in Bangla and source citation links.

Failure budgets: an inaccessible source should not break independent user input tools; a failing ML backend must be labeled unavailable with a functional non-model fallback; incomplete clinical/lab/legal sources must never yield unsupported certainty; an authorized admin must be able to disable a faulty source/model instantly while preserving provenance.

### Required implementation documents and files
`README.md`, `.env.example` (no secrets), `docs/APP_ARCHITECTURE.md`, `docs/DATASET_REGISTER.md`, `docs/DATA_LICENSE_REVIEW.md`, `docs/USER_GUIDE_BN.md`, `docs/ADMIN_GUIDE_BN.md`, `docs/AI_MODEL_CARD.md`, `docs/PRIVACY.md`, `docs/TEST_PLAN.md`, `docs/QA_RESULTS.md`, `docs/DEPLOYMENT_VERCEL.md`, `db/migrations/*`, `scripts/seed.*`, `.github/workflows/ci.yml` and realistic sample reports.

**Final status format:** routes created / user flows verified / admin flows verified / seeded original vocabulary count / real licensed source data rows actually imported / model available yes/no / benchmark measurement / tests run & results / deployment status / GitHub remote commit URL if verified / remaining blockers.

## 10 — DATA REFERENCES IN THIS PROMPT (EACH PROJECT SELF-CONTAINED)
- **01. FFWC observation portal** — https://ffwc.gov.bd/app/observed-water-level
  - Intended use: rain/flood contextual evidence, not plot-specific loss records; Access: Verified public observation interface; download rights unknown (2026-10-25); Copyright/licensing: verify per source, not presumed free to retrain.
- **02. BAMIS — agricultural weather and advisories** — https://www.bamis.gov.bd/en/home/
  - Intended use: Crop weather, 64-district advisories, climate tables and agriculture risk context; Access: historical candidate link; verify live accessibility; Copyright/licensing: verify per source, not presumed free to retrain.
- **03. Bangladesh Open Data — searchable datasets** — https://data.gov.bd/dataset
  - Intended use: Find filtered Bangladesh CSV/XLSX datasets by topic and year; Access: historical candidate link; verify live accessibility; Copyright/licensing: verify per source, not presumed free to retrain.
- **04. FFWC — flood and river hydrological information** — https://ffwc.gov.bd/
  - Intended use: River levels, flood/water situation, station context; Access: Verified public FFWC dashboard (2026-10-25); Copyright/licensing: verify per source, not presumed free to retrain.

Official public web page does NOT imply an accessible bulk dataset. Every link above is a candidate source/reference. For reproducible source import build `scripts/import_sources` for only permitted download endpoints; otherwise use admin-assisted upload after rights and permission are verified. Document what is actually available, checked, or unavailable. Do NOT use a source's domain name as proof that data have been loaded. The separate files in this kit are supporting convenience, not prerequisites to understand this self-contained prompt.

### Starter data actually included
`SEED_TAXONOMY.json` and `.csv`: 18 original curated vocabulary/category labels for ফসলের ক্ষতি নথি. `EVALUATION_CASES.json`: 14 synthetic QA / abuse cases, not genuine observations. `PROJECT_CONFIG.json`: user/admin/modules/AI contract. `DATASET_SOURCES.json`: source URL register with licensing limitations. No real private patient records, child speech, live prices, flood observations, or third-party copyrighted documents are included. For medical, vaccine, safe-donation, legal or water-quality use, do not invent clinical thresholds or official schedules; refer to reviewed, dated published sources.

## 11 — IN-PROMPT ORIGINAL BANGLA STARTER SEED AND QA BLUEPRINT
These are **original project vocabulary/field labels only**, not government-published observation or supervised training examples. Build working selector, search/filter, onboarding explanations and import scaffolding with these even when external permissions are not available.

**All curated labels, in recommended initial display order:**
1. ফসলের নাম
2. জমির পরিমাণ
3. ক্ষতির ছবি
4. বৃষ্টির নথি
5. ঝড়ের ঘটনা
6. বন্যার পানি
7. চারা নষ্ট
8. পাতার ক্ষতি
9. ফলনের অনুমান
10. বাজারদর উৎস
11. সার খরচ
12. বীজ খরচ
13. শ্রম খরচ
14. ঘটনার তারিখ
15. প্রমাণপত্র
16. ক্ষতির অংশ
17. কৃষকের মন্তব্য
18. সহায়তার আবেদন

**Evaluation behavior and negative cases:**
- TEST-001: স্বাভাবিক ইনপুট -> ব্যবহারকারী প্রথমবার কাজ সম্পন্ন করে; source limitation দৃশ্যমান
- TEST-002: অসম্পূর্ণ ইনপুট -> সব প্রয়োজনীয় অনুপস্থিত মান বাংলায় চিহ্নিত; অনুমান নয়
- TEST-003: বাংলা সংখ্যা -> বাংলা ডিজিটকে সঠিক সংখ্যায় normalise; ইউনিট ধরে রাখা
- TEST-004: দ্ব্যর্থক টেক্সট -> review step; low-confidence abstain
- TEST-005: অতিরিক্ত বড় ফাইল -> safe rejection; clear limit + retry
- TEST-006: অনুমতি না থাকা ডেটা -> সুস্পষ্ট unavailable; ভুয়া live data নয়
- TEST-007: ডেটাসেটের পুরোনো সংস্করণ -> as-of এবং downgrade/report alert
- TEST-008: অনুমতি ছাড়া অন্যের ডেটা -> 403 deny; audit event
- TEST-009: admin data quarantine -> publish disabled until license reviewed
- TEST-010: বেঠিক ইউনিট -> validation rejection; কোনো মিথ্যা পরামর্শ নয়
- TEST-011: AI model বন্ধ -> simple rule/manual fallback and honest badge
- TEST-012: অ্যাডমিন কন্টেন্ট rollback -> previous published version restored with log
- TEST-013: ডেটা মুছে ফেলা -> data removed according to retention policy, verified
- TEST-014: প্রমাণ ছাড়া আত্মবিশ্বাসী দাবি -> explain uncertainty and citation requirement

The corresponding CSV/JSON files are supplied in this project folder for direct use in the repository. If Work sees only this prompt, generate the equivalent seed files from these in-prompt labels and cases; no separate prompt or owner copy-paste is necessary. Do not mistake the taxonomy for scientific training examples.

---

# APPENDIX A — ORIGINAL V2 COMPLETE MASTER PROMPT (UNCHANGED)
The entire earlier prompt is retained below for compatibility and detailed prior sections 00–20. If an earlier generic directive conflicts with this V4's more specific data provenance, privacy or correctness requirement, follow the safer V4 rule.

# PROJECT 03 — FasalLoss AI

**Paste this entire prompt into a fresh ChatGPT Work task.**

## 00. YOUR ROLE, NON-NEGOTIABLE OUTCOME, AND AUTHORIZED ACCESS
You are ChatGPT Work acting as a senior Bangladesh-first product team: product researcher, UX/UI designer, full-stack engineer, AI/ML/NLP specialist, privacy/security engineer, QA lead, and release engineer. BUILD THE WORKING PRODUCT IN YOUR WORKSPACE, not just mockups, advice, or plans. Write the actual files, run tests, inspect failures, fix them, and document results. Do not claim tests/deployment/push succeeded unless confirmed by tool output. Preserve working progress in commit-sized milestones. Complete the maximal useful implementation in this work session; transparently report remaining external blockers.

Product identity: **FasalLoss AI**. Domain: Agriculture / Climate Recovery. Primary audience: people in Bangladesh with low-end Android phones, variable networks, Bengali-first needs, and no CSV/Excel files. Primary input: Field images/videos; acreage/quantity numbers; farmer explanation. Specific impact: Help farmers record climate-related crop damage and generate structured evidence, not insurer-grade valuations.

Use real methods and honest limitations. Do NOT pretend an unavailable external model, dataset, government API, real-time feed, identity provider, doctor, law firm, weather alert, or database is connected. Never silently insert fake production records. Synthetic/demo fixtures must be clearly labeled "DEMO DATA" and must never contaminate production claims.

## 01. PROJECT-SPECIFIC USER PRODUCT — IMPLEMENT EVERY FLOW
Crop selection, sowing date, land-size input in decimal/bigha/hectare with regional unit warnings; guided before-after capture; observed damage tags; loss diary; receipt scan; tentative impact summary; downloadable application checklist.

Turn that experience into complete end-to-end journeys: (a) guest explores public content, (b) user starts an analysis through the lowest-friction input, (c) validates any extracted fields, (d) receives a sourced, interpretable result, (e) saves, revisits, edits, exports and deletes their own result, (f) reports error and requests correction, (g) recovers safely from missing connection, unavailable model, unknown answer or invalid input. Every primary flow needs loading, empty, success, warning, error, permission-denied and mobile offline/interrupted states. Design graceful anonymous mode when sensitive records need not be stored; account creation must be optional until private save/sharing is requested.

### User-facing navigation and pages
Implement a public homepage with a distinctive hero, real use-case explainer, exactly described capabilities, interactive mini-demo with clearly marked demo results, How it Works, evidence/limitations, About and Team Bio (editable by admin), FAQ, educational resources, contact/feedback, data-source provenance, privacy policy, terms, accessibility, and 404/maintenance pages. The authenticated workspace should include Dashboard, New Analysis, History/Records, one fully working feature-specific analysis flow, Results/Explainability, Saved Reports, Personal Settings, Notifications, Download/Export, Help/Feedback and Data Deletion. Adapt the nav to actual FasalLoss AI concepts; remove unrelated generic menu entries. Never let an apparently usable button do nothing.

### Bangladesh accessibility and usability
Default UI language Bangla; add English switch only if actual translations are implemented. Bangladesh location picker must handle division→district→upazila as supported by validated geography reference, and show missing regions honestly. BDT currency, metric units with clearly labeled local unit conversions, Asia/Dhaka dates, phone-sized layouts and readable Bangla fonts. Implement responsive desktop/tablet/mobile, keyboard focus, WCAG-oriented contrast, screen-reader labels, reduced-motion support, field validation in simple Bengali, audio/voice only if supported, and printable Bangla PDFs with correct Unicode. Do not require CSV/Excel; accept suitable text, numbers, photos, audio/video or PDF per feature and explain what each can/cannot prove. Provide consent and file limits before upload.

## 02. UNIQUE VISUAL DESIGN SYSTEM — NOT A TEMPLATE CLONE
Art direction: Paddy-gold + forest green, farmer-first one-screen capture and clear photo evidence ledger.
Build a polished original visual system: typographic scale and Bangla-capable fallback stack; mobile-first 8-point spacing grid; 5 accessible semantic colors; light/dark if feasible; responsive navbar; recognizable project logo/SVG created in code; cohesive cards, input controls, loading skeletons, empty states, alerts, charts, icons and report print stylesheet. Avoid cookie-cutter purple-gradient AI dashboards, fake user counts, stock-photo heroes or empty dashboards. Showcase the product-specific main interaction above the fold. Use your own code-based illustrations/icons, not unauthorized logos or stock photos. All labels, image descriptions, microcopy and error states must be useful, including first-time onboarding and assisted-use hints.

## 03. AI, ML, NLP, RAG AND NUMERIC COMPUTATION — BUILD, MEASURE, EXPLAIN
Product-specific inference contract: Image damage-area annotation with explicit scale uncertainty; OCR for receipts; conservative crop-type recognition where trained; calculators using user-entered area/yield; Bangla RAG agronomic recovery guidance.
Separate (1) deterministic code/calculators, (2) OCR/ASR/media inference, (3) ML classification/ranking/anomaly components and (4) RAG answers; implement ONLY modalities justified above. Prefer inspectable open-source models and light dependencies. Prioritize affordable CPU/on-device inference; decide whether to run in the browser, in Next.js server actions, or in a small documented FastAPI service based on actual model size and host limits. If a model is too heavy for free Vercel functions, do NOT quietly bundle it: ship a fully working honest smaller baseline, with optional inference adapter, documented alternative hosting and accurate capability labels.

Create typed input/output schemas, confidence/abstention thresholds for probabilistic components, source citations with dates, provenance records and a Human Review/Edit step. Implement model/dataset version display and no unsupported scientific measurements from an image. If RAG: ingestion, text extraction, deduplication, metadata, chunks, embedding/index or feasible keyword hybrid retrieval, permissions/collection access, document versioning, grounded answers linking to exact source passage, empty-corpus refusal, prompt-injection filtering and retrieval evaluation. If numerical: preserve units, formula and assumptions, and unit tests; if vision/audio: validate consent/media safety and measure per-class errors. No magic "AI analysis" consisting of random labels or hardcoded success response.

## 04. BANGLADESH DATASET AND EVIDENCE PLAN — MUST BE REALISTIC
Sources and data targets for THIS project: BAMIS crop-weather bulletins; DAE agricultural guidance; official crop and district reference data; opt-in field examples; no copyrighted photo scraping.
Research each source FIRST and build `docs/DATA_SOURCES.md`: title, publisher, URL, fetched date, update cadence, area coverage, content, quality, API/file/manual access, applicable license/ToS, accessibility, user-consent considerations, known gaps and whether use in a public commercial site is allowed. Public visibility is NOT automatically an open redistribution or scraping license. Respect robots/rate limits; obtain permissions/credentials only through user-authorized steps. Do not assume a public DGHS dashboard provides patient-level open records or a BMD page grants free bulk climate data. Create a small verified reproducible seed set where permitted; for unavailable data, design importer/admin approval and show "No verified data yet" rather than fabricated Bangladesh data. If global licensed models train or pretrain the baseline, label them distinctly; do not claim Bangladesh-trained results without verifiable Bangladesh-specific training/evaluation. Provide dataset/model cards, split by location/time/person to avoid leakage as appropriate, limitations, bias checks and reproducible metrics.

## 05. USER AUTH, PRIVACY AND DATA OWNERSHIP
Support public guest pages and authenticated user roles; choose a practical zero-/low-cost auth such as Supabase Auth only if owner connection/keys exist. If no connection is authorized, build testable local development auth/mock identities with prominent DEV ONLY guard and a proper real-auth adapter; never publish a fake login system. Use verified server-side authorization and Row Level Security or equivalent for per-user ownership; protection on every API and object path. Password/secret reset, session expiry, export and delete own data, consent records, upload deletion and clear privacy notices. Encrypt sensitive data at rest where supported and use HTTPS, signed media URLs, virus/type/size checks, rate limiting and abuse monitoring. No API keys in client bundles or GitHub. For minors/health, stronger access, retention and opt-in rules apply. Do not send private uploads to third-party AI providers without clear opt-in, a lawful basis and disclosed terms.

## 06. MASTER ADMIN — EVERY WEBSITE PART EDITABLE, GOVERNED AND AUDITED
Build a genuine **Super Admin Console**, not a decorative admin screenshot. Implement RBAC: Super Admin, Content Editor, Data Curator, Moderator, Support (minimal privileges), Auditor (read-only), and optional Verified Expert; make permissions adjustable by Super Admin without granting unrestricted access to patient/private documents. All user-visible text/images/links and website structure should be backed by editable content/config records where safe; preserve security-critical code gates. Administrative modules:
1. Executive dashboard with DAU/MAU, submissions, completed analyses, failures, referral/feedback trends, model cost/latency, health and privacy events; figures derived from real events only.
2. Website builder/CMS: brand name, logo, favicon, domain metadata, nav order, hero headings, landing sections, cards, labels, onboarding, About/Bio/team, Contact, social URLs, footer, FAQ, help articles, legal/policy pages, SEO/Open Graph, sitemap, redirects, Bangla/English content, home announcements, themes/tokens, media gallery, draft/preview/publish/unpublish/rollback, page visibility and maintenance mode. No need to edit source code to change ordinary content.
3. User directory: search/filter, account state, moderation cases, bans/suspensions with reason and appeal, deletion requests, aggregate usage and consent status; security-safe impersonation never allowed. Never show passwords, raw tokens or unrelated private records.
4. Project operations: inspect all **authorized** public/aggregate workflow events, tickets, moderation queues and explicit support-share sessions; do NOT grant default unrestricted view of medical/contract/private user content. User authorizes selective access with visible audit, scope and expiry. Provide a clear distinction between admin operational visibility and user-record confidentiality.
5. AI control center: model versions, inference routes, evaluations, source allowlists, chunking/index refresh, moderation rules, confidence thresholds, disabled-feature toggles, prompt templates with reviewed versioning, error traces with PII redaction, rollback and safe canary tests.
6. Dataset center: list sources, license approval, importer, schema validation, provenance, freshness/expiry, manual reviewer, duplicate detection, geographic coverage, publish status, source takedown and full lineage.
7. Reporting center: date/district/category aggregates; trend graphs; CSV/PDF exports of non-private reports; audit log; feedback taxonomy; retention/deletion log; admin activity and role changes.
8. Communication center: in-app announcements, notification templates, opt-in messages, reports/issues/appeals and response drafts. Do not send SMS/email unless a service is configured and approved.
9. Security operations: MFA for admin when available, invite-only admin creation, access approvals, session kill, rate-limit settings, secrets configuration indicators but no secret display, backups/migrations status and immutable audit events.
10. Crop catalogue, regional units, weather event categories, approved guidance, review suspected duplicates, human annotation, safe suggestion whitelist.
Implement CRUD with confirmation, optimistic/error handling, bulk operations where appropriate, permission denial, draft publish workflow and automated admin tests. **No Super Admin button should bypass privacy consent or security restrictions.** Record each admin action with actor/time/target and restore strategy.

## 07. REAL DATA MODEL, API, AND DOCUMENTED CONTRACTS
Include domain entities and relationships: Farm, Field, CropCycle, LossObservation, Receipt, DamageAnnotation, Advisory, Export. Add User, Role, RolePermission, ContentPage, ContentBlock, ThemeConfig, MediaAsset, SourceRegistry, DatasetRevision, ModelRegistry, AnalysisJob, ResultRevision, Feedback, ReportExport, Notification, ConsentGrant, AuditEvent and FeatureFlag when appropriate. Every entity needs IDs, timestamps, ownership, lifecycle states, migrations, validation schemas and guarded APIs. Files must use signed object storage when connected; development can use a local adapter clearly labeled local-only. Provide `docs/ERD.md`, `docs/API.md`, OpenAPI/typed route contracts, stable error shapes, export format, and deletion/retention behavior.

## 08. IMPLEMENTATION STACK AND REPO LAYOUT
Prefer Next.js stable App Router + TypeScript + React + Tailwind CSS, accessible component primitives and meaningful charts; Postgres/Supabase optionally connected, with strict RLS policies and migrations. Keep the full stack deployable on Vercel without Cloudflare Workers, R2, Wrangler or `vinext`. Python/FastAPI optional ONLY if genuinely necessary for heavier AI; separate `/ai-service` with requirements and deployment constraints, never pretend it deploys inside ordinary Vercel Node functions. Use adapters/interfaces for AI inference, storage, email, geo and datasets. Include `/app`, `/components`, `/lib`, `/db`, `/tests`, `/scripts`, `/docs`, `/public`, optional `/ai-service` and `/data/samples` (small licensed or explicitly synthetic). Build in a single workspace and ensure `npm install`, typecheck, lint, unit test and production build succeed. Avoid install scripts requiring private keys or billing.

## 09. SECURITY, POLICY AND SOCIAL IMPACT CHECK
Project-specific risk rules: Never claim insurance approval, guaranteed yield or verified monetary loss; avoid unapproved pesticide advice.
For health, legal, disaster and road-safety topics, disclose constraints at the point of action, show emergency/professional routes where appropriate, avoid unsupported personalization, track data reliability and do not give falsely precise scores. Validate malicious PDFs/image decompression, cross-tenant access, prompt injection from uploaded docs, stored XSS in user reports and admin CMS, SSRF from arbitrary URLs, account enumeration, SQL injection, abuse/spam, moderation appeal and object-store path isolation. Collect minimum personal data, publish retention and data deletion policy. Bangladesh-first usability must not sacrifice security. Obtain review if legal/clinical safety claims would otherwise be necessary.

## 10. ACCEPTANCE TESTS AND DEMO SCENARIOS
Project-specific tests: Decimal/bigha conversion tested; poor photo triggers recapture; calculator reproducible and editable.
Additionally implement guest-to-user happy path, admin CMS edit visible on public site, content rollback, admin RBAC denied actions, user A blocked from user B data, upload permission/file-limit states, consent revoke, failed AI provider and missing-data fallback, empty RAG refusal, source citation freshness, actual results change when inputs change, stable recalculation, Bangla typography and PDF output, mobile viewport and keyboard accessibility, auth/logout, backup/migration smoke checks. Use Playwright or equivalent browser tests where available and seed a **DEMO** account/dataset without production secrets. Evaluate domain-specific model baseline with metrics and error cases; report actual numbers only after running evaluations. Record screenshots of responsive screens if tools allow. All links, call-to-actions and menus must work.

## 11. GITHUB, RELEASE, DOCUMENTATION — REQUIRED FINAL STEP
Repository name: `fasalloss-ai-bd`. Create a clean README.md (problem in Bangladesh, features, demo screenshots, AI methods and limitations, data sources/licenses, tech stack, local startup, environment variable names **without secrets**, admin first-user bootstrap, database migration, deployment steps, cost/free-tier limits, privacy warnings, actual tests and known limitations). Add `CONTRIBUTING.md`, `SECURITY.md`, `LICENSE` for original code where appropriate, `.env.example`, `.gitignore`, CI workflow for lint/typecheck/test/build, changelog, issue templates and meaningful atomic commits. Use GitHub connector/connected account **only when the owner has authorized repository creation/write**; then initialize repo, push actual tested code to main and verify the remote commit URL. If GitHub access is not yet granted, never fabricate a successful push: leave a complete local git repo plus exact `git remote add`, `git branch`, `git push` commands and clearly request the required authorization. Do not commit real credentials, protected datasets, identifiable health data or user uploads. Provide Vercel deployment settings and a validated build; claim live deployment only if verified by live URL. In `FINAL_HANDOFF.md` report completed vs not completed, links actually verified, commands/results, sample test steps, technical/data/licensing blockers and precisely what owner action remains.

## 12. EXECUTION ORDER — DO NOT STOP AFTER PROPOSING A PLAN
1. Audit available workspace, authorizations and source access; write a short task checklist.
2. Design and implement user flows and product-specific AI baseline with honest capabilities.
3. Implement schema, auth, API and storage, then full UI and all functional flows.
4. Implement comprehensive admin CMS and domain operations.
5. Ingest only appropriately licensed Bangladesh evidence; label any demo records explicitly.
6. Run tests, fix issues, validate accessibility and real production build.
7. Write docs, commit, push to GitHub with permission, verify links and hand off.
Prefer a smaller fully working truthful product to a huge mock product with nonfunctional AI or broken security. Never repeat completed work; work from actual code and test evidence, not assumptions.


---

# V2 ENHANCEMENT — SELF-CONTAINED, DATASET-LINKED, BANGLA-FIRST (FasalLoss AI)
**IMPORTANT:** Sections 00–12 above are the original master-prompt contract (existing original prompt preserved, expanded with dataset links/admin/usability). Sections 13–20 below extend them; nothing below deletes or overrides valid old domain requirements. The priority is simple PUBLIC UX, a comprehensive governed ADMIN panel, real Bangladesh-specific sources and an authorized separate GitHub repo.

## 13. EASY BANGLA ABOUT COPY (WRITE AND SHOW ON WEBSITE)
**Project name:** FasalLoss AI  
**Category:** Agriculture / Climate Recovery  
**Bangladesh-specific About (editable via Admin > Content > About):** কৃষক ফসলের ক্ষতির ছবি, জমির পরিমাণ ও নিজের ব্যাখ্যা দিয়ে ক্ষতির ডায়েরি এবং সহায়তা চাওয়ার প্রমাণভিত্তিক সারাংশ বানাতে পারবেন।

Make About explain in Bangla: What problem in Bangladesh this solves, who can use it, expected inputs, limits, examples, distinction from official services, source dates, contact/feedback, and privacy. Create Home hero, short Bio/About, 3 icon steps, one real task input box, a useful outcome preview based on genuine test fixtures clearly marked DEMO, frequently asked questions and a public link to source/limitations. Avoid fake '10 million users', fake clinic partnerships, unverified endorsement and generic AI talk.

## 14. USER EXPERIENCE — CONCRETE THREE STEPS AND OPTIONAL FEATURES
1. **Step 1:** সহজ ইনপুট দিন—Field images/videos, acreage/quantity numbers, farmer explanation
2. **Step 2:** AI/নিয়মের শনাক্ত তথ্য নিজে যাচাই করুন
3. **Step 3:** সূত্রসহ ফলাফল দেখুন, ভুল সংশোধন করুন এবং নিজের রিপোর্ট সংরক্ষণ/শেয়ার করুন

Input modalities for this specific website: **Field images/videos; acreage/quantity numbers; farmer explanation**. Use relevant modalities; never force image upload on text-only or number-based flows. Rephrase these 3 steps in genuinely natural Bangla, with a screenshot/illustration and structured confirmation screen. Add previous-results list (only for own account), save/share/report, edit and delete, favorite, complaint, accessibility/high-contrast and a help tooltip. Provide no account required for unsaved public trial except projects with sensitive matching/private donor interactions. Sample values should be user-controlled demo only.

### Public UI simplicity is a binding constraint
Build a **single clear main action on Home** and a three-step guided workflow: **1) লিখুন/আপলোড করুন → 2) যাচাই করুন → 3) ফলাফল দেখুন**. For numeric/text-only projects replace upload with appropriate typed fields. Guest mode must give meaningful real utility without registration where privacy allows. On small 360px Android displays, use 3–5 top-level menu destinations MAX (Home, Start, My Reports, Help, Account); put secondary/About/legal pages in footer/overflow; admin stays separate at /admin. No dashboard wall or 25 menu links for public users; progressive disclosure for expert controls. Easy Bangla labels with English optional; autosave local drafts when safe, skip optional steps, example-fill button only with CLEAR DEMO mark, input placeholders, smart defaults, camera and paste support per project, per-field corrections, undo, keyboard/a11y support, clear no-data state, retry on weak network, copy/share PDF buttons that actually work, support via feedback form, big tap targets and zero deceptive buttons.
A new user should understand the product's key value within 10 seconds, complete a representative task in about three steps, and distinguish real analysis from illustrations or demos. No forced CSV, Excel, NID or account setup. Do not create inaccessible admin-style screens for ordinary users.

## 15. FULL MASTER ADMIN UPGRADES
### New full-control modules (ALL sections must be real and functional)
- **CMS Everything:** Navigation (menu group, order, nested links, visibility), Homepage hero and CTAs, About/Bio/Team, How It Works, Services, AI feature description, FAQs, Resources/Blog, Contact, Terms, Privacy, Data Disclaimer, Cookies, Footer, Branding (site name, favicon, logos, icons, typography and colors), SEO/meta/OpenGraph, banners, maintenance page, accessibly editable alt text and Bangla/English translations. Every content change needs preview, publish/unpublish and rollback.
- **User oversight:** search/filter users and activity metadata; invite, block, suspend/unsuspend, deactivate, delete subject to retention law; view consents and account status; export subject data through audited lawful workflows. Do NOT provide unrestricted access to private medical/child/voice/contract uploads; use case-specific consent and least-privilege access.
- **Data source CMS:** source URL, provider, dataset file type, update frequency, geographic coverage, license evidence, valid_from/valid_to, schema mapping, transform scripts, approved importer jobs, preview rows, provenance, edit history, error logs, disable invalid sources, datasets and model card registry.
- **AI Control Center:** choose allowed inference adapters, prompts and version with rollback; configurable confidence/abstention thresholds with safe bounds; model version and evaluation dashboard; RAG document ingestion/deletion/reindex, retrieval chunk viewer, grounding check, abuse filters, cost and quota monitoring, per-feature kill switch, human-review queues. Never expose API secrets on admin screens or allow unreviewed clinical treatment instructions.
- **Moderation & Support:** complaint/request ticket inbox with status and assignee, private audit logs, user correction requests, scam/spam filters, safe evidence retention, sensitive media masking, resolution message templates and escalation SLA settings.
- **System & Operations:** admin MFA, RBAC permission matrix, role invitations and revoked sessions, audit events (actor, timestamp, before/after, reason), backup schedule and restore drill, health monitor, rate limits, storage/quota metrics, privacy-policy versions/consent texts, analytics switches, email/SMS provider readiness (disabled until authorized), cache refresh, bulk actions with confirmation and dry-run, release toggles, error tracking, and on-site feature usage analytics without violating consent.
- **Admin UX:** left sidebar + command search, responsive tablet admin, contextual help, mass actions with undo where safe, irreversible-action confirmation, CSV export of approved non-sensitive tables, pagination, saved filters, universal content search, autosave draft, per-field validation, revision history, staging-preview vs live state. Super Admin can manage almost all content/configuration and operational settings but NEVER bypass ownership/medical-privacy safeguards or directly change deployment secrets via browser.
- **Concrete verify:** administrator edits the About paragraph and homepage CTA, publishes them, changes a source/threshold setting, then all public views update correctly; test that a Content Editor cannot view patient data or disable security controls and a User cannot call any admin route.

**Project-specialized admin focus:** Crop catalogue, regional units, weather event categories, approved guidance, review suspected duplicates, human annotation, safe suggestion whitelist.

## 16. BANGLADESH DATASET LINKS, DATA MODELS AND LICENSING
### Dataset register with concrete source links — REQUIRED for FasalLoss AI
These are real **starting-source pages** researched on 2026-10-24, not a claim that data was downloaded, an API exists, data is already Bangladesh-trained, or licenses have been cleared. **Do not pretend every link is a machine-readable dataset.**

| Source and link | What it offers | Access / license realities |
|---|---|---|
| [BAMIS — agricultural weather and advisories](https://www.bamis.gov.bd/en/home/) | Crop weather, 64-district advisories, climate tables and agriculture risk context | Public page; API/bulk download not confirmed; Reuse / redistribution / model-training permission to verify |
| [Bangladesh Open Data — searchable datasets](https://data.gov.bd/dataset) | Find filtered Bangladesh CSV/XLSX datasets by topic and year | Public searchable catalogue; downloadable datasets vary; Check dataset-specific terms and publication dates |
| [FFWC — flood and river hydrological information](https://ffwc.gov.bd/) | River levels, flood/water situation, station context | Public viewer; programmatic access and rights unconfirmed; Reuse / redistribution / model-training permission to verify |

**Dataset execution checklist (must produce artifacts in CODE repo):**
1. Visit each link and verify HTTP availability, last update, coverage, public/restricted access and documented machine formats (CSV/XLSX/PDF/dashboard/manual). Capture source URL and retrieval timestamp in `docs/DATASET_REGISTER.md` and `data/sources.manifest.json`; label sources `VERIFIED_PAGE`, `REUSABLE_DATA_APPROVED`, `REFERENCE_ONLY`, `ACCESS_RESTRICTED`, or `NOT_AVAILABLE`, independently.
2. Read the specific source's copyright/license and ToS. Government publication/public page ≠ open API/training/republishing license. Never scrape protected data, bypass rate limits or republish private personal records; ask owner permission if required.
3. Implement adapter scripts under `scripts/import/` only for sources with permission; schema validation, dedupe, Bangla UTF-8 normalization, district/upazila mapping, timestamps, source provenance, deterministic preprocessing, error quarantine and rollback. Package reproducible small **LICENSE-CLEARED** seed if possible; show 'যাচাইকৃত তথ্য নেই' when not.
4. Domain target: **Image damage-area annotation with explicit scale uncertainty; OCR for receipts; conservative crop-type recognition where trained; calculators using user-entered area/yield; Bangla RAG agronomic recovery guidance.**. Distinguish a training corpus from official reports/lookup pages and from consented user-uploaded data. Do not call an international pretrained model Bangladesh-trained without Bangladesh-specific evidence and held-out evaluation. If truly useful local training data is absent, build functioning deterministic/NLP/RAG baseline with explicit model limitation and targeted ethical dataset collection plan.
5. Provide an ML/RAG evaluation notebook/script: stratified test design by geography/time/person where applicable, ground-truth annotation specification, precision/recall/MAE/answer faithfulness as justified, sample-size disclosure, error and subgroup audits. Never make up metrics.
6. `DATASET_SOURCES.json` is provided alongside this prompt inside the ZIP, but **the prompt itself is complete**: all starting URLs appear in the table above. No requirement to copy some external common prompt. In the project code generate complete source docs and link/cite actual used data in the UI, not just placeholder citations.

## 17. SPECIALIZED AI/ML/NLP/RAG IMPLEMENTATION CRITERIA
**The previously defined domain inference contract MUST stay:** Image damage-area annotation with explicit scale uncertainty; OCR for receipts; conservative crop-type recognition where trained; calculators using user-entered area/yield; Bangla RAG agronomic recovery guidance.
- Build explicit pipeline diagram in `docs/AI_PIPELINE.md`: INPUT → type/content/permission validation → OCR/ASR/PARSE where needed → original rule-based/ML/RAG engine → confidence/refusal and user review → sourced result → private storage only when consented → report/export.
- Input changes must yield meaningful recomputed changes, not canned results. For images/audio, record trained/pretrained model provenance and actual local evaluation if available. For numbers, formula/unit and boundary-tests in code. For RAG, cite *exact* ingested, licensed passages and abstain when empty. Multiple approaches can coexist but only with a justified workflow.
- Keep batch training/admin ingestion separate from public requests; never attempt expensive always-on training in a public Vercel request. Config feature flags for heavy inference, use a functioning privacy-safe text/numeric fallback when necessary. Missing third-party APIs are documented blockers, never imaginary integrations.
- Add **Bangladesh localization evaluation**: Bangla OCR/ASR variants only where appropriate; Bangla numerals ০১২৩৪৫৬৭৮৯, local number separators, BDT, land measurement units where applicable, district/upazila spelling aliases and low-network behavior; test at least 8 scenario fixtures (positive/negative/ambiguous/missing/invalid/privacy/error/out-of-distribution/real-user-correction).

## 18. SIMPLE UNIQUE WEBSITE VISUAL + ABOUT + PREVIEW REFERENCE
Create a distinctive **code-built brand** guided by old Section 02, not a cloned SaaS template. The ZIP includes `UI_PREVIEW.svg` as a **conceptual wireframe only**, not an actual website screenshot. Derive product-specific screen structure, icons, Bangla copy, 3-step progress, trustworthy source citations and subtle accessible colors. Use standard responsive components, not animations that slow users. Include both user-facing pages and an information-dense but accessible separate admin workspace. The logo and hero are editable in the Admin CMS; don't download unlicensed stock photos.

## 19. FINAL END-TO-END BUILD, QA AND GITHUB HANDOFF
### Product delivery, security, MVP and GitHub instructions
- **MVP should actually work:** Real input → validated extraction/model/rules → transparent output; implement one honest primary end-to-end flow FIRST, then add optional enhancements only if tests pass. Avoid turning a simple public site into an unusable enterprise dashboard.
- Produce operational `.env.example`, typed DB migrations, model/data adapters, fixture privacy labels, `config/features.json`, `config/site-content.json`, `docs/USER_GUIDE_BN.md`, `docs/ADMIN_GUIDE_BN.md`, `docs/DATASET_REGISTER.md`, `docs/AI_MODEL_CARD.md`, `docs/DEPLOYMENT.md`, `docs/QA_RESULTS.md` and README with actual commands; make files self-consistent.
- Security: no fabricated production logins or fake paid subscriptions; user data isolated server-side, strict RLS, upload validation (MIME/size/malware), object storage signed URLs, PII retention/deletion, prompt-injection defence for uploaded RAG files, admin MFA and audited RBAC; on health and minors keep stronger consent and data minimization.
- Stack recommendation: Next.js stable + TypeScript + Tailwind + test suite; Supabase Postgres/Auth/Storage if connection is authorized, otherwise local SQLite/Postgres for honest dev and a production adapter. Where heavy vision/ASR can't run serverless, use documented CPU-friendly inference / a separate model service; no false all-free unlimited guarantees.
- Full tests: user guest/new/saved flow, source-empty fallback, AI failure, real input-dependent output, admin content publish/rollback, prohibited admin access, cross-user isolation, privacy delete, consent, Bangla rendering at 360/768/1440px, slow/offline recovery, source citations and functional export, CI lint/types/tests/build, end-to-end Playwright where feasible. Record actual pass/fail, no fabricated screenshots.
- **MANDATORY FINAL STEP: GITHUB PUSH.** Use ONLY owner-connected and owner-authorized GitHub. Create **a separate repository for this specific project**, git commit, push actual code, verify remote branch and commit URL. If no authorized connection, prepare repo and exact instructions; explicitly state 'GitHub push not completed' without claiming success. NEVER commit `.env`, model API keys, raw medical records, private donor info, children's speech, unauthorized data. Provide deployable Vercel instructions and flag any needed server/inference services. Work in current task through file creation, tests and maximal permitted commit—not a plan-only answer.

## 20. NOT A MOCK PROJECT — HONEST RELEASE CHECK
Return code/files, actual data import readiness and validated pages; a real working baseline matters more than speculative ML. Document any unavailable Bangladesh training dataset, restricted official API, unmet permission or optional model integration, including what remains unbuilt. Show the user what works without paid services and exactly what must be configured by the owner. Run README commands when possible. Do not ask the user to paste any generic shared prompt: **this entire file is standalone**.


---

# MANDATORY FINAL STEP — GITHUB REPOSITORY, PUSH, REVIEW AND VERIFIED HANDOFF
1. Create/locate **this project's own** authorized GitHub repository; if project exists, preserve and upgrade, never reset the existing project or force push. GitHub requires owner's connected account and explicit permissions.
2. Provide a working code tree, migrations, original curated seed fixtures with origin labels, consent/privacy config, model/data cards, Vercel architecture, security docs, test output and screenshot only if produced.
3. Run project commands `npm ci`, `npm run lint`, `npm run typecheck`, `npm run test`, `npm run build` where the project configuration implements them; document missing commands precisely rather than inventing pass results.
4. Commit code only, not passwords, tokens, private medical records, children's speech, donor phone numbers, copied restricted datasets or `.env`; push the working branch and verify remote repo/commit hash and README links.
5. If a real external key/license/hosting authorization remains unavailable, prepare implementation and state that exact blocker; do not pretend a GitHub push, government API access or live ML deployment succeeded.
6. Deliver a concise completion report with audited functionality, files, tests, actual dataset row counts vs curated/demo row counts, live model readiness, current deployment restrictions and next actions.
