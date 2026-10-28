# DokanLens AI — EXISTING WEBSITE EXPANSION MASTER PROMPT V3
**This is an executable upgrade brief, NOT a new website prompt. Paste this entire file into ChatGPT Work and attach this project folder or ZIP. All critical instructions and URLs are self-contained in this master prompt; seed datasets are also included for direct import.**

**Existing project:** DokanLens AI  
**Purpose:** Bangladesh-first phone-enabled shop inventory, receipting, and explainable sales insights  
**Owner status:** Already built; must preserve existing project and user data.  
**Reference date:** 2026-10-25; government and dataset sources require rechecking at time of actual import.  
**Implementation priority:** preserve → audit → seed original data → improve one complete user journey → admin CMS → verified-source imports → ML optional → tests → authorized existing GitHub push.

## 00 — CRITICAL: UPGRADE AN EXISTING BUILT WEBSITE, DO NOT REBUILD FROM SCRATCH
You are ChatGPT Work, functioning as principal full-stack engineer, model engineer, Bangladesh data curator, interaction designer, DB migration specialist and QA/release lead. The owner ALREADY BUILT THIS PRODUCT. **Your first operation must be to locate the EXISTING owner-authorized GitHub repository in the connected GitHub/workspace or user-provided link. Do not create a duplicate app or brand new repository.** If repository identity cannot be established, work on a patch branch/reviewable files and report that remote integration remains blocked; do not invent a path or use an unrelated repository. Never ask for passwords/secrets in chat. Never claim to have pushed/deployed when no tool verification exists.

The original full master prompt is preserved in the **APPENDIX below** verbatim. V3 instructions at the TOP override old text ONLY where it says 'create new / fresh Work task / empty database / new GitHub repository' and now requires a safe, backward-compatible upgrade. Preserve every existing successful feature, old user account, old dataset, old prompt/test fixture, route, slug, theme preference, SEO identity and admin policy unless absolutely necessary to fix an actual security bug. Before edits inventory current routes, schema, environment names, UI flows, model providers, owner users, git history and existing issues. Create `docs/BEFORE_AFTER_AUDIT.md`, document working/current/missing and take backup/export where access allows. Use a feature branch and reversible migrations; no drop/truncate/reset/force push. Run tests before editing. Work from actual codebase, never from assumptions.

MANDATORY DELIVERABLES IN THIS WORK SESSION:
- ship source code updates, migrations, importer(s), data seeds, admin pages, real app flows, tests, documentation and merge-ready commits to authorized EXISTING repo if available;
- demonstrably improve at least 1 complete real user journey, 1 AI/rules pipeline, 1 admin editing workflow, 1 non-demo data ingestion/curation capability, and error/empty states;
- disclose blockers by item and keep functioning rule-based/manual fallback rather than simulated intelligence;
- no apparent button without function, no fake progress percentages, no fake live records or fake model scores.

## 01 — FULL USER + ADMIN PRODUCT CONTRACT
The PUBLIC side must stay SIMPLE despite large capability. Mobile home has only one primary call to action; maximum four bottom tabs; all complex features live behind progressive disclosure. The full admin panel is comprehensive but separate. New user should finish the main task in 3 steps: INPUT → REVIEW/CORRECT → RESULT/ACTION, with a 'try without account' mode when privacy permits. Existing customers must not relearn navigation unnecessarily. Include accessible onboarding, tooltip explanations, empty/slow/offline/error states, autosave local draft, resume, history, export, full deletion, Bangla default, English optional only if translated, local BDT, responsive 320/360/768/1440 widths, keyboard semantics, screen reader labels, no unnecessary animation. Theme, About, Bio, Privacy, Team, help, FAQ, homepage blocks, examples, illustrations, SEO and footer all editable through published Content CMS. Always render a genuine date/provenance/uncertainty tag for externally sourced information.

Separate roles/permissions: Super Admin; Operations Admin; Content Publisher; Dataset Curator; ML Reviewer; Moderator; Support (redacted only); Security Auditor (read-only); ordinary User, and domain-specific specialist roles if appropriate. Permission checks enforced both server and DB (RLS if using Supabase). Super Admin can edit every *public website content item* and bounded operation configuration, never read private content merely because they are admin, disable auth, change deployment secrets, falsify audit, or bypass consent. On admin dashboard include sections: Overview & KPIs, User & Role Management, Site Builder/CMS, Page Sections, Menu/Footer/About/Bio, Visual Theme, Images/Icons, UI Localizations, Docs/FAQ, Notifications & Templates, Approval Queue, Dataset Explorer, Import/Export, Source Registry, Label Review, ML Model Registry/Version/Canary, Prompt & Retrieval Rules, Feature Flags, Thresholds, Cost/Quota Budget, Request Analytics, Error/Latency Monitoring, Audit Logs, Privacy & Consent, Data Deletion Requests, Backups/Migrations, SEO/Redirects, Support Tickets, Policy Versioning, Experiment Toggles, Deployment Readiness. Every control must have server endpoint + RBAC + validation + successful state + rollback + tests; hide unreleasable menu items rather than display dead interfaces. Data revisions need who/when/why and staging→review→publish with rollback.

## 02 — REAL DATA, NOT DECORATIVE SOURCE LINKS
This ZIP contains immediately importable ORIGINAL starter datasets under `data/seed/` and official/research references under `data/sources.json` / `docs/SOURCES.md`. Inspect and wire these files into EXISTING schema using idempotent seed migrations (UPSERT by stable ID, never reset a live table). Include `scripts/seed` and `scripts/import` plus `scripts/validate-data`, migration tests and dataset provenance table. DO NOT overwrite user data. New data is labeled `original_seed` / `demo` / `official_reference` / `downloadable_external_dataset` as applicable. Do not relabel original illustrative seeds as government data. A government webpage is not automatically downloadable, licensed for commercial reuse, or an API. Validate accessible endpoints, latest date, licensing/attribution and intended geography/time before importing third-party material. Document `source_url`, `publisher`, `retrieved_at`, `source_published_at`, `license`, `rights_status`, `geography`, `format`, `checksum`, `reviewer_id`, `import_batch_id`, `quality_status`, `was_user_submitted`, `confidence` as appropriate. If source is not accessible/license-verified, the complete app MUST still work using the included original reference seed and manual user input. No unauthorized scraping or secret bypass.

Build an Admin Source Manager: add URL/upload, capture file metadata, parser, preview detected rows, map Bangla column headers, reconcile units, dedupe, quarantine bad data, batch approve, publish, unpublish, rollback, reprocess and expire stale sources. Human-assisted upload is a valid functioning data acquisition approach if official APIs are unavailable. Provide clear source freshness labels to users. Import no sensitive personal documents for ML training without explicit consent/legal basis.

## 03 — AUTHENTIC AI/ML ENGINEERING
Never make an ordinary LLM prompt pretend to be a trained model. For each ML feature write `docs/MODEL_CARD.md` (task, model version/license, training/validation data, relevant Bangladesh coverage, baselines, precision/recall/WER/MAE as appropriate, sample count and error categories), plus `docs/AI_PIPELINE.md` and input/output Zod/Pydantic schemas. Classify features explicitly as RULES, OCR, ML, RAG or HUMAN REVIEW. Use open-source models only after deployment + license checks. If backend model cannot run Vercel, implement real CPU/lightweight/browser fallback and an optional documented external inference endpoint. When a model is absent, show “এখন এই অটোমেটিক ফিচারটি উপলব্ধ নয়” and fully functional manual alternative. Avoid imaginary model inference, fake 98% accuracy, fixed response regardless of input and made-up citations. Track decision reasons, confidence, corrections, model rollbacks and user feedback. Include tests with genuinely different inputs and different outputs; isolate external model calls behind stable adapter. Do not collect training data from uploads unless user opted in separately.

## 04 — NON-DESTRUCTIVE DATABASE AND SECURITY UPGRADE
Inspect app's current Next.js/Supabase/Firebase/backend stack first. Prefer MINIMAL diffs to old deployment, not forced migrations to fashionable dependencies. If on Next.js, stay standard `next build` with no Cloudflare Workers/R2/vinext. Existing auth provider remains unless compelling reason; avoid creating duplicate sign-ins or temporary prod mock login. For Supabase, write backward-compatible migrations with RLS on every owner-specific table and storage bucket. File upload: MIME sniffer, size quotas, signed URLs, encryption where supported, antivirus/unsafe file screening, PDF/image transcoding if needed, rate limiting and storage lifecycle. CSRF/CORS/auth checks, tenant isolation and privacy-by-default. Database writes transactional, idempotent on retries, currency numeric precision and timezone Asia/Dhaka. Secrets server-only; `.env.example` placeholders only, never commit user credentials. No data used for ad targeting. Add backup and `docs/ROLLBACK.md`; restore test where feasible.

## 05 — SITE DESIGN QUALITY
Keep the existing brand identity if user has already invested in it, but upgrade spacing, Bangla typography (locally/legal hosted font where allowed), task affordances, readable forms and intentional icons. Build screenshot-ready representative empty / with-data / error states. Avoid overlong dashboard, giant modals, fake graphs, irrelevant generic AI cards, 3D animation. Hero explains real action; main flow works on low-end Android with intermittent bandwidth and visual accessibility requirements. Images show actual purpose, not decorative clickbait. Never reuse copyrighted logos/fonts without right. CMS edits should publish correct layout to all devices and have rollback.

## 06 — TEST, CI AND RELEASE GATE
Test baseline before changes. Then run lint, typecheck, unit, integration, schema migration dry-run, Playwright smoke (mobile and desktop), data seed repeated twice to verify idempotence, auth/RLS cross-account probes, moderation/privacy consent, upload security, offline/empty cases, AI abstention and source freshness, admin content edit/publish/rollback, failure of optional API and database backup verification. Add `docs/CHANGELOG_V3.md`, `docs/QA_RESULTS.md`, `docs/KNOWN_LIMITATIONS.md`, `docs/RELEASE_NOTES_BN.md`, `docs/DATA_SOURCES.md`, `docs/USER_GUIDE_BN.md`, `docs/ADMIN_GUIDE_BN.md` and minimal `README` patch without destroying the old README. Separate unit/e2e test fixtures from live database. Git commit into owner-authorized current repository; push/rebase only after verifying branch and permissions. If account connection missing, prepare patch files and exact steps, say not pushed. Never auto-deploy destructive changes to live production.


## 07 — DOKANLENS AI USER EXPERIENCE, FULL FEATURE BREAKDOWN
Each module below needs UI states, explicit APIs, DB schema and tests. High-complexity flows are secondary screens, NEVER dozens of competing homepage CTAs.

1. First-run store setup (shop name, type, location optional, working units, reorder preference) without importing spreadsheets; offer short Bangla illustrated wizard
2. Dashboard: actual stock-value range with unknown prices excluded, today purchases/sales, low-stock list, soon-expiry count and scanner quick action
3. Add stock by camera: photo shelf scan, proposals only when actually detected, boxes crop and confidence labels, confirm SKU and count manually; phone barcode keyboard fallback
4. Add by name voice/text search in Bangla/English across seeded ontology, allow custom product/brand/pack-size and owner-verified barcode
5. Inventory: variants (500g vs 1kg), opening stock, shelf/warehouse locations, reorder thresholds, batch/lot/date history, spoilage and returns, stock movement audit
6. Quick sale: tap product + quantity + optional sale price, basket total BDT, cash/credit tagging, correctable receipt, refund/return transaction
7. Quick purchase: supplier optional, invoice photograph OCR -> editable line items, batch expiry confirmations, add to stock with source audit
8. Expiry: only confirmed printed manufacturing/expiry dates, uncertain OCR -> no countdown until owner review, FEFO picking suggestions
9. Cashbook: income/expense and credit ledger separated; record corrections never silently rewrite a posted sale, cash reconciliation
10. Insights: simple weekly product velocity calculated from own movements, low-stock forecast only when enough actual records, unknown model/data flag
11. Multiple staff: cashier, owner, stock manager; invite, scoped capabilities and staff activity audit; offline-first local transaction queue with conflict resolution
12. Shop exports: printable inventory register, BDT invoice, Excel-compatible CSV with UTF-8, backup/import, deletion and recovery guide

### End-to-end customer stories to implement
- Unregistered visitor reaches a real interactive input within one tap, with no forced sign-up.
- Saved/private mode requires verified auth and protects each record server-side.
- Mobile data interrupted mid-work should never corrupt an earlier saved record; drafts must be resumable.
- Extracted fields or detections are ALWAYS correctable before being stored as owner-verified data.
- No confirmed input or available external source: return useful text/manual/calculator fallback, never a made-up analysis.

## 08 — DOMAIN AI/ML/NLP/RAG AND DETERMINISTIC ENGINES
Every item below must either be implemented with a tested legitimate baseline or explicitly flagged as optional/unavailable, rather than appearing as a working fake feature.

1. Upload photo => compress/rotate/private validation => detection or OCR model candidate => crop/word box => candidate product match => user correction => stable stock transaction
2. Barcode scan decodes string but never automatically asserts SKU identity from global barcode DB; compare with owner-entered mapping; unknown remains unknown
3. Catalogue semantic search: Bangla English aliases and fuzzy matching, alias collision dialog; pack unit interpretation and variant differentiation
4. Visual object detection: integrate open-source compatible model only after model license and local shelf evaluation; not a random rectangle overlay or fake “99%”; support staged per-shop labeled image set
5. Receipt/expiry OCR: date parsing handles DD-MM-YYYY, printed abbreviations, Bangla digits, ambiguous labels and manufacture/expiry difference; require human verify before alerts
6. Stock integer/decimal arithmetic invariant and optimistic locking; track damaged/expired/returns separately; no negative saleable quantity without explicit backorder flag
7. Demand trend: trailing-day moving average / exponential smoothing based on shop history (minimum sample count), holdout MAE/MAPE where meaningful, no manufactured projections
8. Optional anomaly detection: sudden stock gap from ledger with audit trail, not fraud accusation; explain why flagged

**Acceptance criterion:** Change at least three realistic inputs and demonstrate three different meaningful outputs. Record evaluation methodology, held-out data splits and missing-resource blockers. RAG must never answer from a non-indexed document with invented section citations.

## 09 — BANGLADESH DATA SOURCES, ACTUAL DELIVERED SEEDS, AND IMPORTS
The included original data are curated by this prompt author (not official downloads); their precise provenance is in each row. They make genuine baseline features usable right away, without claiming real-time prices, shops, government records or training metrics. Distinguish text reference, business owner data, demonstration fixtures and actual licensed ML training corpora.

1. data/seed/bd_product_ontology.csv: Bangladesh common commodity taxonomy with 80+ product canonical names, Bengali aliases and default unit; NO barcode, price or stock fabricated
2. data/seed/inventory_rules.json: real deterministic conversion and accounting rules + precision policy
3. data/seed/sample_ledger_DEMO_ONLY.csv: explicitly fictitious isolated sample only for CI/demo
4. BSTI reference can support product standards/categories but cannot identify store photos or barcodes; merchant-consented photo annotation import is necessary for local CV training
5. Real sales/stock is always entered/confirmed by owner; build import plus user-assisted capture, not imaginary shops

### Verified source starting points
| Official/research source | Content / integration role | Status and rights note |
|---|---|---|
| [BSTI mandatory product categories](https://bsti.portal.gov.bd/pages/static-pages/6922dcba933eb65569e11af8) | Mandatory product/certification list, not product barcode or stock dataset. | `official_reference` — verify reuse/updates; do not treat as SKU registry |
| [BBS Economic Census](https://bbs.gov.bd/) | Bangladesh business statistics and sector context, not individual stock. | `official_reference` — specific publication rights; browse manually |
| [Bangladesh Open Data](https://data.gov.bd/dataset) | Searchable public data catalogue; check individual dataset format and license. | `catalogue` — each dataset separately approved |
| [Bangladesh administrative divisions](https://bangladesh.gov.bd/site/view/division-list/division-list) | Official division list for address select. | `official_reference` — metadata reference |


### Files INCLUDED with this prompt (real starter content, no extra prompting needed)
- **bd_product_ontology.csv**: `data/seed/bd_product_ontology.csv` (81 records)
- **sample_ledger_DEMO_ONLY.csv**: `data/seed/sample_ledger_DEMO_ONLY.csv` (5 records)
- **bd_divisions.json**: `data/seed/bd_divisions.json` (8 records)

### Non-negotiable ingestion sequence
1. Read `data/sources.json` and each source page; save `retrieved_at`, `license_evidence_url`, `download_link`, availability, update time, checksum, territorial coverage.
2. Distinguish raw reference page from a downloadable structured data file. Download only when permitted and technically possible; never bypass login, robots, paywalls, consent or private data restrictions.
3. Build/repair app schema and idempotent import code that maps all included original seed records to search/select/list features. Log inserted/updated/skipped totals after testing; run seed script twice.
4. For official PDF/data, provide admin upload form, status `awaiting_review`, audit/source viewer, reviewer approval then publication with time/version/license label. A human can download and upload source if the portal has no API. Never tell user an auto-sync exists if it does not.
5. Add data coverage dashboard: original seed rows, imported verified rows, missing data types, scheduled update backlog and source freshness. Show relevant limitations publicly.
6. For supervised learning create strict user-consented collection workflows, annotations, train/val/test, model card, bias metrics and rollback. Avoid zero-shot pretrained model described as Bangladesh-fine-tuned.

## 10 — SPECIALIZED SUPER ADMIN EXTENSIONS
The shared admin contract in Section 01 already requires page editing, all public settings, dataset imports, moderation, analytics, audit, roles and features. Add THESE project-specific real admin functions with server RBAC and approval records:

1. SKU ontology manager with merge/split aliases, variant packaging, local product term moderation and source provenance
2. Model annotation studio for owner-opted-in shelf crops with bounding boxes and label versions, anonymization and retention
3. Store abuse / fraud suspicion moderation limited to platform fraud; no unrestricted owner transactions or private photos
4. Feature flags OCR/detection/alerts per shop plan, rollout canary, per-model errors and consent audit
5. Inventory transaction dispute workflow and admin-approved generic fixes with shop-owner confirmation

**Administration information architecture:** Overview, Website CMS, Data Center, AI Lab, Users/Support, Security/Privacy, System/Deploy. Each opens functional nested pages; role-specific visibility, no fake menu entries. Publish actions have preview, reviewer attribution and rollback; each configurable item documents schema and safe bound. Add a Super Admin ‘Site Health’ page that detects missing dataset, disabled model, broken links, unconfigured email and failed cron rather than faking success. Sensitive content must not be broadly exposed to admins.

## 11 — UI COMPONENT STRUCTURE AND DESIGN DIRECTION
**Design:** Retail orange + dark ink + teal; bold product tiles, sticky bottom “বেচা” “কেনা” “স্ক্যান” controls, camera-first scan wizard and quiet accounting screen.

Public navigation should show Home, Start, History (login required), Help or equivalent 3–4 top-level items. Footer: About, Team Bio, Accessibility, Privacy, Terms, Data Sources, Contact, Legal/Safety notes as applicable. User settings include exports/deletion and safe notifications. Admin is a separate protected `/admin` space. Components: BanglaHero, InputStepper, CorrectionPanel, EvidenceChip, ConfidenceWithReason, EmptyDatasetCard, PrivacyConsent, SourceFooter, AdminReviewQueue, ModelStatusPill, ImportWizard, AuditDiff, UndoToast, ResponsiveReportPrint. Each reusable component must contain real handlers and tests, not sample markup disconnected from API. Make old site visually improved WITHOUT changing its brand/name by default. Ensure real-state screenshots, no dummy KPI counter.

## 12 — DATABASE SCHEMA / API / STATE MANAGEMENT REQUIREMENTS
Create or extend these generic tables with existing naming compatibility where possible: `site_sections`, `content_revisions`, `admin_permissions`, `role_assignments`, `source_registry`, `dataset_import_batches`, `data_quality_issues`, `dataset_reviews`, `models`, `model_releases`, `inference_events` (NO raw sensitive uploads), `feature_flags`, `user_feedback`, `audit_logs`, `privacy_consents`, `deletion_requests`. Add domain-specific entities based on features in Sections 07–09; do not create meaningless tables not used by UI. All migrations additive/backward-compatible. Provide API contracts with request/response examples, idempotency keys for user writes, Zod validation and normalized Bengali search. Row ownership enforced DB + server. Data imports have dry-run, row quarantine, source attribution and rollback. Use transaction histories when money/stock involved; don't simply overwrite totals.

## 13 — COMPLETE TEST MATRIX, INCLUDING PROJECT-SPECIFIC CASES
1. Create shop, add SKU without photo and record sale; stock counts reflect ledger
2. Unknown barcode returns “পণ্য চিনতে পারিনি” + add manually, never fake identity
3. Two SKUs with same name but different pack sizes stay separate
4. Expiry OCR cannot add date without user confirmation
5. Negative stock protection and offline duplicate-sync tested
6. Two stores never access each other’s receipts or photos
- Old users & records still exist post migration
- Existing homepage, navigation and URLs do not regress
- Each seed can import twice without duplicate rows
- No DEMO row appears as authentic external feed
- Admin edits About and publishes to live visible immediately
- Support role cannot read raw personal uploaded document/audio
- Another user cannot list or fetch any private uploads
- Deleted user object remains inaccessible
- Empty external data gives explicit no-data banner
- GitHub commit and CI run results accurately documented
- No API key in client chunk, git index or browser logs
- Mobile 360px viewport no horizontal scroll
- Bangla Unicode text and PDF export verified
- Source citation links and retrieval timestamps visible when data present

Also demonstrate 3 core forms and 3 admin workflows with screenshots if tools allow and code links. Every test result must state executed/passed/failed/skipped with command and date; never fabricate success. Update readme with before/after file list and feature status. If AI optional service unavailable, test fallback, don't mark AI test passed.

## 14 — EXECUTION STEPS FOR CHATGPT WORK (DO THE WORK, NOT JUST ADVICE)
1. Inspect connected **existing** repository: latest main branch, dependencies, current deployment, migrations and current data.
2. Record baseline tests, create a feature branch `feature/v3-data-ai-admin` (or an available branch name), log acceptance criteria.
3. Build idempotent seed loader from provided included data, verify counts against actual files.
4. Refactor core 3-step UX with state-safe API and real calculations/parser/AI adapter; add graceful offline/manual/error behavior.
5. Add CMS/editable every public section, model/source registry, data approval/rollback and scoped admin roles.
6. Integrate real external data only after source/rights/license and technical format verification; otherwise deliver operational admin uploader and visible no-data fallback.
7. Implement honest ML/RAG where adequate data/licensing/compute exist; produce tested deterministic fallbacks for models that cannot run.
8. Run tests, inspect build, repair failures and inspect schema diff and privacy implications. Preserve old data and routes.
9. Commit/push to owner-authorized CURRENT GitHub repository, verify commit URL; otherwise package a reviewable patch and truthfully report blocker.
10. Deliver exact changed files, before/after comparison, seed/import counts, user/admin features executed, API/model status, real source references, screenshots, QA results, deployment steps and outstanding limitations.

## 15 — STRICT USER DATA / OFFICIAL SOURCE HONESTY RULE
Do not say that attached original seed is an official dataset. Do not fabricate real prices, medical findings, legal verdicts, real store inventory, actual student's voice scores, model accuracies, country-specific coverage or successful direct GitHub integrations. Information might be useful even when only deterministic/manual baseline exists. For a source requiring rights or manually downloaded files, provide concrete human-assisted curator workflow and editable status — not an imaginary automatic importer. If source is stale, prominently show observation/publication date and coverage.

---
# APPENDIX A — ENTIRE PREVIOUS MASTER PROMPT, PRESERVED VERBATIM
The following is the original full prior prompt (Sections 00–20 and its integrated appendices when present), kept so earlier features do not disappear. When it says build a new project or create a new repo, the overriding EXISTING-SITE-ONLY instructions above supersede that procedural step. All other valid requirements remain.

# PROJECT 10 — DokanLens AI

**Paste this entire prompt into a fresh ChatGPT Work task.**

## 00. YOUR ROLE, NON-NEGOTIABLE OUTCOME, AND AUTHORIZED ACCESS
You are ChatGPT Work acting as a senior Bangladesh-first product team: product researcher, UX/UI designer, full-stack engineer, AI/ML/NLP specialist, privacy/security engineer, QA lead, and release engineer. BUILD THE WORKING PRODUCT IN YOUR WORKSPACE, not just mockups, advice, or plans. Write the actual files, run tests, inspect failures, fix them, and document results. Do not claim tests/deployment/push succeeded unless confirmed by tool output. Preserve working progress in commit-sized milestones. Complete the maximal useful implementation in this work session; transparently report remaining external blockers.

Product identity: **DokanLens AI**. Domain: Small Business / Retail Vision. Primary audience: people in Bangladesh with low-end Android phones, variable networks, Bengali-first needs, and no CSV/Excel files. Primary input: Shelf photos; barcode/manual SKU; optional receipts. Specific impact: Help small Bangladeshi shopkeepers maintain rough inventory counts using a phone, without requiring spreadsheets.

Use real methods and honest limitations. Do NOT pretend an unavailable external model, dataset, government API, real-time feed, identity provider, doctor, law firm, weather alert, or database is connected. Never silently insert fake production records. Synthetic/demo fixtures must be clearly labeled "DEMO DATA" and must never contaminate production claims.

## 01. PROJECT-SPECIFIC USER PRODUCT — IMPLEMENT EVERY FLOW
Create shop/category; shelf photo capture; detected product proposals; manual verify pack counts; barcode add; purchase/sale quick taps; expiry reminders only from legible print; low-stock alerts; cashbook summary; daily export.

Turn that experience into complete end-to-end journeys: (a) guest explores public content, (b) user starts an analysis through the lowest-friction input, (c) validates any extracted fields, (d) receives a sourced, interpretable result, (e) saves, revisits, edits, exports and deletes their own result, (f) reports error and requests correction, (g) recovers safely from missing connection, unavailable model, unknown answer or invalid input. Every primary flow needs loading, empty, success, warning, error, permission-denied and mobile offline/interrupted states. Design graceful anonymous mode when sensitive records need not be stored; account creation must be optional until private save/sharing is requested.

### User-facing navigation and pages
Implement a public homepage with a distinctive hero, real use-case explainer, exactly described capabilities, interactive mini-demo with clearly marked demo results, How it Works, evidence/limitations, About and Team Bio (editable by admin), FAQ, educational resources, contact/feedback, data-source provenance, privacy policy, terms, accessibility, and 404/maintenance pages. The authenticated workspace should include Dashboard, New Analysis, History/Records, one fully working feature-specific analysis flow, Results/Explainability, Saved Reports, Personal Settings, Notifications, Download/Export, Help/Feedback and Data Deletion. Adapt the nav to actual DokanLens AI concepts; remove unrelated generic menu entries. Never let an apparently usable button do nothing.

### Bangladesh accessibility and usability
Default UI language Bangla; add English switch only if actual translations are implemented. Bangladesh location picker must handle division→district→upazila as supported by validated geography reference, and show missing regions honestly. BDT currency, metric units with clearly labeled local unit conversions, Asia/Dhaka dates, phone-sized layouts and readable Bangla fonts. Implement responsive desktop/tablet/mobile, keyboard focus, WCAG-oriented contrast, screen-reader labels, reduced-motion support, field validation in simple Bengali, audio/voice only if supported, and printable Bangla PDFs with correct Unicode. Do not require CSV/Excel; accept suitable text, numbers, photos, audio/video or PDF per feature and explain what each can/cannot prove. Provide consent and file limits before upload.

## 02. UNIQUE VISUAL DESIGN SYSTEM — NOT A TEMPLATE CLONE
Art direction: Tangerine + indigo retail dashboard, camera-centric SKU wizard, large stock chips and compact sales register.
Build a polished original visual system: typographic scale and Bangla-capable fallback stack; mobile-first 8-point spacing grid; 5 accessible semantic colors; light/dark if feasible; responsive navbar; recognizable project logo/SVG created in code; cohesive cards, input controls, loading skeletons, empty states, alerts, charts, icons and report print stylesheet. Avoid cookie-cutter purple-gradient AI dashboards, fake user counts, stock-photo heroes or empty dashboards. Showcase the product-specific main interaction above the fold. Use your own code-based illustrations/icons, not unauthorized logos or stock photos. All labels, image descriptions, microcopy and error states must be useful, including first-time onboarding and assisted-use hints.

## 03. AI, ML, NLP, RAG AND NUMERIC COMPUTATION — BUILD, MEASURE, EXPLAIN
Product-specific inference contract: Object detection on locally captured SKU photos, OCR expiry reading with review; inventory arithmetic; demand trend estimates from actual recorded sales only; no fake product recognition.
Separate (1) deterministic code/calculators, (2) OCR/ASR/media inference, (3) ML classification/ranking/anomaly components and (4) RAG answers; implement ONLY modalities justified above. Prefer inspectable open-source models and light dependencies. Prioritize affordable CPU/on-device inference; decide whether to run in the browser, in Next.js server actions, or in a small documented FastAPI service based on actual model size and host limits. If a model is too heavy for free Vercel functions, do NOT quietly bundle it: ship a fully working honest smaller baseline, with optional inference adapter, documented alternative hosting and accurate capability labels.

Create typed input/output schemas, confidence/abstention thresholds for probabilistic components, source citations with dates, provenance records and a Human Review/Edit step. Implement model/dataset version display and no unsupported scientific measurements from an image. If RAG: ingestion, text extraction, deduplication, metadata, chunks, embedding/index or feasible keyword hybrid retrieval, permissions/collection access, document versioning, grounded answers linking to exact source passage, empty-corpus refusal, prompt-injection filtering and retrieval evaluation. If numerical: preserve units, formula and assumptions, and unit tests; if vision/audio: validate consent/media safety and measure per-class errors. No magic "AI analysis" consisting of random labels or hardcoded success response.

## 04. BANGLADESH DATASET AND EVIDENCE PLAN — MUST BE REALISTIC
Sources and data targets for THIS project: Owner-consented Bangladeshi shop SKU image set; GTIN/barcode entries where licensed; no assumption universal packaging database exists.
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
10. SKU normalization, product variants, photo label review, import/export, staff roles, low-stock defaults, transaction dispute trail and bulk corrections.
Implement CRUD with confirmation, optimistic/error handling, bulk operations where appropriate, permission denial, draft publish workflow and automated admin tests. **No Super Admin button should bypass privacy consent or security restrictions.** Record each admin action with actor/time/target and restore strategy.

## 07. REAL DATA MODEL, API, AND DOCUMENTED CONTRACTS
Include domain entities and relationships: Shop, ShelfPhoto, SKU, InventoryCount, Purchase, Sale, ExpiryCheck, StockAdjustment. Add User, Role, RolePermission, ContentPage, ContentBlock, ThemeConfig, MediaAsset, SourceRegistry, DatasetRevision, ModelRegistry, AnalysisJob, ResultRevision, Feedback, ReportExport, Notification, ConsentGrant, AuditEvent and FeatureFlag when appropriate. Every entity needs IDs, timestamps, ownership, lifecycle states, migrations, validation schemas and guarded APIs. Files must use signed object storage when connected; development can use a local adapter clearly labeled local-only. Provide `docs/ERD.md`, `docs/API.md`, OpenAPI/typed route contracts, stable error shapes, export format, and deletion/retention behavior.

## 08. IMPLEMENTATION STACK AND REPO LAYOUT
Prefer Next.js stable App Router + TypeScript + React + Tailwind CSS, accessible component primitives and meaningful charts; Postgres/Supabase optionally connected, with strict RLS policies and migrations. Keep the full stack deployable on Vercel without Cloudflare Workers, R2, Wrangler or `vinext`. Python/FastAPI optional ONLY if genuinely necessary for heavier AI; separate `/ai-service` with requirements and deployment constraints, never pretend it deploys inside ordinary Vercel Node functions. Use adapters/interfaces for AI inference, storage, email, geo and datasets. Include `/app`, `/components`, `/lib`, `/db`, `/tests`, `/scripts`, `/docs`, `/public`, optional `/ai-service` and `/data/samples` (small licensed or explicitly synthetic). Build in a single workspace and ensure `npm install`, typecheck, lint, unit test and production build succeed. Avoid install scripts requiring private keys or billing.

## 09. SECURITY, POLICY AND SOCIAL IMPACT CHECK
Project-specific risk rules: Image counts often approximate and blocked by occlusion; never overwrite verified stock without review; protect supplier/pricing data.
For health, legal, disaster and road-safety topics, disclose constraints at the point of action, show emergency/professional routes where appropriate, avoid unsupported personalization, track data reliability and do not give falsely precise scores. Validate malicious PDFs/image decompression, cross-tenant access, prompt injection from uploaded docs, stored XSS in user reports and admin CMS, SSRF from arbitrary URLs, account enumeration, SQL injection, abuse/spam, moderation appeal and object-store path isolation. Collect minimum personal data, publish retention and data deletion policy. Bangladesh-first usability must not sacrifice security. Obtain review if legal/clinical safety claims would otherwise be necessary.

## 10. ACCEPTANCE TESTS AND DEMO SCENARIOS
Project-specific tests: Wrong product match correctable; two staff edits audited; no stock changes before human acceptance.
Additionally implement guest-to-user happy path, admin CMS edit visible on public site, content rollback, admin RBAC denied actions, user A blocked from user B data, upload permission/file-limit states, consent revoke, failed AI provider and missing-data fallback, empty RAG refusal, source citation freshness, actual results change when inputs change, stable recalculation, Bangla typography and PDF output, mobile viewport and keyboard accessibility, auth/logout, backup/migration smoke checks. Use Playwright or equivalent browser tests where available and seed a **DEMO** account/dataset without production secrets. Evaluate domain-specific model baseline with metrics and error cases; report actual numbers only after running evaluations. Record screenshots of responsive screens if tools allow. All links, call-to-actions and menus must work.

## 11. GITHUB, RELEASE, DOCUMENTATION — REQUIRED FINAL STEP
Repository name: `dokanlens-ai-bd`. Create a clean README.md (problem in Bangladesh, features, demo screenshots, AI methods and limitations, data sources/licenses, tech stack, local startup, environment variable names **without secrets**, admin first-user bootstrap, database migration, deployment steps, cost/free-tier limits, privacy warnings, actual tests and known limitations). Add `CONTRIBUTING.md`, `SECURITY.md`, `LICENSE` for original code where appropriate, `.env.example`, `.gitignore`, CI workflow for lint/typecheck/test/build, changelog, issue templates and meaningful atomic commits. Use GitHub connector/connected account **only when the owner has authorized repository creation/write**; then initialize repo, push actual tested code to main and verify the remote commit URL. If GitHub access is not yet granted, never fabricate a successful push: leave a complete local git repo plus exact `git remote add`, `git branch`, `git push` commands and clearly request the required authorization. Do not commit real credentials, protected datasets, identifiable health data or user uploads. Provide Vercel deployment settings and a validated build; claim live deployment only if verified by live URL. In `FINAL_HANDOFF.md` report completed vs not completed, links actually verified, commands/results, sample test steps, technical/data/licensing blockers and precisely what owner action remains.

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

# V2 ENHANCEMENT — SELF-CONTAINED, DATASET-LINKED, BANGLA-FIRST (DokanLens AI)
**IMPORTANT:** Sections 00–12 above are the original master-prompt contract (existing original prompt preserved, expanded with dataset links/admin/usability). Sections 13–20 below extend them; nothing below deletes or overrides valid old domain requirements. The priority is simple PUBLIC UX, a comprehensive governed ADMIN panel, real Bangladesh-specific sources and an authorized separate GitHub repo.

## 13. EASY BANGLA ABOUT COPY (WRITE AND SHOW ON WEBSITE)
**Project name:** DokanLens AI  
**Category:** Small Business / Retail Vision  
**Bangladesh-specific About (editable via Admin > Content > About):** দোকানদার তাকের ছবি, বারকোড বা পণ্যের নাম লিখে স্টক তালিকা সাজাতে ও আগের দিনের সঙ্গে পরিবর্তন তুলতে পারবেন।

Make About explain in Bangla: What problem in Bangladesh this solves, who can use it, expected inputs, limits, examples, distinction from official services, source dates, contact/feedback, and privacy. Create Home hero, short Bio/About, 3 icon steps, one real task input box, a useful outcome preview based on genuine test fixtures clearly marked DEMO, frequently asked questions and a public link to source/limitations. Avoid fake '10 million users', fake clinic partnerships, unverified endorsement and generic AI talk.

## 14. USER EXPERIENCE — CONCRETE THREE STEPS AND OPTIONAL FEATURES
1. **Step 1:** সহজ ইনপুট দিন—Shelf photos, barcode/manual SKU, optional receipts
2. **Step 2:** AI/নিয়মের শনাক্ত তথ্য নিজে যাচাই করুন
3. **Step 3:** সূত্রসহ ফলাফল দেখুন, ভুল সংশোধন করুন এবং নিজের রিপোর্ট সংরক্ষণ/শেয়ার করুন

Input modalities for this specific website: **Shelf photos; barcode/manual SKU; optional receipts**. Use relevant modalities; never force image upload on text-only or number-based flows. Rephrase these 3 steps in genuinely natural Bangla, with a screenshot/illustration and structured confirmation screen. Add previous-results list (only for own account), save/share/report, edit and delete, favorite, complaint, accessibility/high-contrast and a help tooltip. Provide no account required for unsaved public trial except projects with sensitive matching/private donor interactions. Sample values should be user-controlled demo only.

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

**Project-specialized admin focus:** SKU normalization, product variants, photo label review, import/export, staff roles, low-stock defaults, transaction dispute trail and bulk corrections.

## 16. BANGLADESH DATASET LINKS, DATA MODELS AND LICENSING
### Dataset register with concrete source links — REQUIRED for DokanLens AI
These are real **starting-source pages** researched on 2026-10-24, not a claim that data was downloaded, an API exists, data is already Bangladesh-trained, or licenses have been cleared. **Do not pretend every link is a machine-readable dataset.**

| Source and link | What it offers | Access / license realities |
|---|---|---|
| [Bangladesh Open Data — searchable datasets](https://data.gov.bd/dataset) | Find filtered Bangladesh CSV/XLSX datasets by topic and year | Public searchable catalogue; downloadable datasets vary; Check dataset-specific terms and publication dates |
| [National Consumer Rights Protection — complaints and rules](https://dncrp.gov.bd/) | Consumer complaint steps, supporting receipts, and official referral | Public guidance; no direct authorization to submit complaints for users; Reuse / redistribution / model-training permission to verify |
| [BBS — Economic Census 2024 tables](https://bbs.gov.bd/pages/static-pages/695b99a3c4774958d7b705e2) | Bangladesh retail/economic unit context and published business statistics, NOT user-store stock labels | Published PDF and Excel tables listed; verify resource access and rights; Reuse / redistribution / model-training permission to verify |

**Dataset execution checklist (must produce artifacts in CODE repo):**
1. Visit each link and verify HTTP availability, last update, coverage, public/restricted access and documented machine formats (CSV/XLSX/PDF/dashboard/manual). Capture source URL and retrieval timestamp in `docs/DATASET_REGISTER.md` and `data/sources.manifest.json`; label sources `VERIFIED_PAGE`, `REUSABLE_DATA_APPROVED`, `REFERENCE_ONLY`, `ACCESS_RESTRICTED`, or `NOT_AVAILABLE`, independently.
2. Read the specific source's copyright/license and ToS. Government publication/public page ≠ open API/training/republishing license. Never scrape protected data, bypass rate limits or republish private personal records; ask owner permission if required.
3. Implement adapter scripts under `scripts/import/` only for sources with permission; schema validation, dedupe, Bangla UTF-8 normalization, district/upazila mapping, timestamps, source provenance, deterministic preprocessing, error quarantine and rollback. Package reproducible small **LICENSE-CLEARED** seed if possible; show 'যাচাইকৃত তথ্য নেই' when not.
4. Domain target: **Object detection on locally captured SKU photos, OCR expiry reading with review; inventory arithmetic; demand trend estimates from actual recorded sales only; no fake product recognition.**. Distinguish a training corpus from official reports/lookup pages and from consented user-uploaded data. Do not call an international pretrained model Bangladesh-trained without Bangladesh-specific evidence and held-out evaluation. If truly useful local training data is absent, build functioning deterministic/NLP/RAG baseline with explicit model limitation and targeted ethical dataset collection plan.
5. Provide an ML/RAG evaluation notebook/script: stratified test design by geography/time/person where applicable, ground-truth annotation specification, precision/recall/MAE/answer faithfulness as justified, sample-size disclosure, error and subgroup audits. Never make up metrics.
6. `DATASET_SOURCES.json` is provided alongside this prompt inside the ZIP, but **the prompt itself is complete**: all starting URLs appear in the table above. No requirement to copy some external common prompt. In the project code generate complete source docs and link/cite actual used data in the UI, not just placeholder citations.

## 17. SPECIALIZED AI/ML/NLP/RAG IMPLEMENTATION CRITERIA
**The previously defined domain inference contract MUST stay:** Object detection on locally captured SKU photos, OCR expiry reading with review; inventory arithmetic; demand trend estimates from actual recorded sales only; no fake product recognition.
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

