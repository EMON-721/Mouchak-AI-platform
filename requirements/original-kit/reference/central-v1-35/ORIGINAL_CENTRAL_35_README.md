# JibonSetu AI — One Bangladesh, 35 Real AI Tools

> **CENTRAL MASTER README / SINGLE CHATGPT WORK BUILD PROMPT**  
> Version: Central V1 · 27 October 2026 · Languages: বাংলা + English  
> **একটি domain · একটি Next.js app · একটি shared authentication · একটি Super Admin · ৩৫টি integrated modules · একটি GitHub monorepo**  
> **অবস্থা:** এটি comprehensive product/build specification; ৩৫টি deployed website বা trained model ইতিমধ্যে তৈরি হয়েছে—এমন দাবি নয়।

---

## 0. Instructions for ChatGPT Work — READ FIRST, ACT NOW

You are the lead product engineer, UI/UX designer, accessibility engineer, data engineer, Bangla NLP/ML engineer, security reviewer and QA owner. **Build one real production-oriented bilingual Bangladesh AI super-platform named JibonSetu AI, not 35 independent websites.** Execute this file from top to bottom. Do not stop at scaffolding, pretty cards or a nonfunctional prototype; produce actual navigable working flows and report clearly any real model/data/hosting blockers. Use user-approved GitHub actions only.

### Non-negotiable commands
1. Treat this README as the **highest-priority product and architecture instruction**. `reference/legacy-v5/projects/*/MASTER_PROMPT_V5.md` contains the unchanged previously approved feature requirements for the original 32 projects. Preserve their *feature intent, datasets, ML requirements, user/Admin features* but **override** any legacy instructions to create 32 separate sites, separate GitHub repositories, login pages, domains, marketing sites or super-admin panels. Legacy instructions about external model APIs are subordinate to this file's data protection rules.
2. Implement **all 35 tools as first-class modules in a SINGLE app** at `/tools/{slug}`, sharing design-system, user profile, workspace, object storage, audit, auth, search, source governance, notification center and CMS. A separate Python inference worker or queue is allowed internally; it must NOT become another public-facing website or second login.
3. Four modules already have independently built user repositories: **BanglaRead Coach, DokanLens AI, BazarCompare AI, ChuktiShield AI**. First inspect their real accessible GitHub repositories with permission. **Do not re-create, replace, force-push, delete data or assume their latest code matches the V5 documents.** Create migration branches, extract reusable features and components, map existing users and data carefully, retain original repositories as backups until parity is verified.
4. Every active AI tool must use a **real, identifiable model/rule engine where appropriate**, with source/model version, tests and honest error states; **never fake an AI response**. Deterministic calculations may be rules, but call them rule/calculator rather than ML. Training is NOT compulsory if a suitable pre-trained licensed model is effective; evaluation on Bangladesh examples IS compulsory. Models not working yet must show a clearly labeled unavailability state, not fabricate certainty.
5. Bangladesh-first is mandatory: Bangla-first copy, Bangla/English full translation, local units (decimal, shotok, bigha only with region-aware definitions), Bangladesh dates, taka, administrative geography, practical low-bandwidth usage. **User must never be forced to upload CSV**: offer text, camera, voice, PDF, number entry or manual form according to tool.
6. All links in `datasets/SOURCE_REGISTRY.csv` are **candidate sources/reference locations**, NOT a claim that the dataset bytes, permissions, API, latestness or trained model already exist. Before ingestion, verify publisher, authority, file-level license, scope, collection date, terms, PII sensitivity, allowed use, provenance and retention. If blocked, record it and activate a user-consented or originally authored dataset collection workflow; never bypass controls, never secretly scrape restricted pages.
7. Make every shared page editable through one RBAC-protected Central CMS: logo, footer, about, bio, home layout, banners, slogans, categories, tool pages, FAQ, instructions, translations, feature flags, menu order, themes, forms, legal notices, sources, content references, email templates and dashboards. Super Admin cannot automatically read private medical/legal/land records—privacy and consent apply to everyone.
8. Output actual runnable source, database migrations, tests, role-seeding, `.env.example`, deployment guide, model manifests, migration mapping and GitHub CI. **A GitHub push happens only after user authorization; record commit SHAs and URL evidence; do not claim push if unavailable.**
9. Prioritize useful completed user journeys over 35 decorative demo cards. Do not leave placeholder routes with fake 'success'. Each module: functional input → verifiable processing → understandable output → save/export/delete. Stage release when external dependencies are limited and flag unfinished tools as Preview/Unavailable with reasons.
10. Work with the artifacts included beside this README; nothing from an unrelated conversation should need to be copied. If file access to the original four GitHub repositories is not granted, build migration adapters/mapping documents and complete independent modules without touching the live repos; disclose those remaining integration dependencies.

## 1. Product Vision and Naming

**Brand:** JibonSetu AI / জীবনসেতু এআই. **Tagline (BN):** “প্রতিদিনের দরকারে, বুঝে-শুনে AI।” **Tagline (EN):** “Practical AI for everyday Bangladesh.” This is a proposed brand, not a registered trademark or domain ownership assertion; perform trademark/domain conflict checks before launch.

**Why ONE hub?** A Bangladeshi user can learn Bengali, evaluate expenses, understand a medical instruction, examine a form, compare market costs or document a road problem without making another account. Every result is explainable and connected to a source/record/history. Cross-tool sharing is **explicit opt-in only**; neither the user’s land deed nor child's voice is fed to an unrelated tool by default.

**Three NEW needs, not cosmetic variations:**
- **33 · LandLedger BD:** land-document consistency companion for Bangladeshi ownership records—field-by-field OCR, dag/khatian/mouza comparison, shotok/decimal/acre conversion *with unit confirmation*, contradiction flags, official portal guides, redacted export. **Never certify ownership.**
- **34 · WageGuard BD:** worker-first payroll and overtime evidence notebook—manually entered hours or payslip, arithmetic verification, explainable wage calculation based on versioned applicable Bangladesh law and sector context, monthly evidence bundles. **Never assert a legal entitlement without checking applicable rules, industry, dates, exemptions and amendments.**
- **35 · ShobdoSetu BD:** communication accessibility—Bangla live-caption support for consented conversations, large-text phraseboard, fast tap-to-speak, bilingual text, privacy-sensitive audio processing. Does **not** pretend to be a verified sign-language interpreter; make offline, low-bandwidth options available when feasible.

**Platform signature:** Quiet, confident public-service quality; not a clone of a familiar generic AI dashboard. A content-led approach with a clear utility launcher, workspaces that feel like purposeful instruments (reading studio, receipt bench, legal clause lens, land document comparison, waveform captions), coordinated design language and recognizable differences for each module. Usability must trump animation and huge complex screens.

## 2. Audience, Product Scope and Global Journeys

Primary audiences: students/guardians, family caregivers, small retailers, agricultural and fisheries workers, day laborers, farmers, community volunteers, tenants/households and everyday citizens. Public unregistered users may browse catalogue, tools' explanation pages and verified references; analysis of sensitive uploads requires logged-in consent. Apply age-appropriate guardian workflows for children's audio and educational records.

**Core 3-step default experience:** (1) Choose a problem or ask the smart launcher → (2) enter a short text/number or upload photo/audio/doc only when needed → (3) receive a clear Bangla/English outcome with the reason, limitations, sources and next practical step. Progressively reveal advanced controls, not immediately. Each result has timestamp, revision, confidence/provenance, copy/share-redacted/PDF options and removal control.

**User routes:** `/` home, `/explore` 35 tools, `/tools/{slug}` 35 seamless screens, `/login` central login, `/register`, `/workspace`, `/workspace/history`, `/workspace/files`, `/workspace/saved`, `/workspace/reports`, `/workspace/notifications`, `/workspace/privacy`, `/settings/profile`, `/settings/security`, `/settings/language`, `/help`, `/about`, `/contact`, `/sources`, `/methodology`, `/privacy`, `/terms`, `/status`. Guard routes by roles.

**Connected experiences, only with prompt-driven permission:**
- `BillDetect → BazarCompare`: user chooses to send manually entered household items from one private record into a comparison workspace; never automatically transmit a utility bill to vendors.
- `DokanLens → BazarCompare → AgroPrice Planner`: consensual share of normalized commodity names/unit and prices, preserving all original sources and dates, avoiding silent business-insight leakage.
- `ChuktiShield → RentalFair → LandLedger`: voluntary “Document Pack” lets a person compare their own contracts, rents and land papers without exposing sensitive source files to broader search.
- `ClinicCompass → CareJourney → LabTrend`: optional personal health workspace with extra privacy and purpose-specific authorization. Do not combine patient data across people.
- `ShikkhaRAG → BanglaRead Coach`: parent-approved learning activities and progress, never child audio in research corpus by default.
- `RoadFix → CivicForm → WorkSafe`: export a redacted civic complaint package for the person to review and submit themselves, no claim of an official government integration.
- `ShobdoSetu → ClinicCompass/CivicForm`: reusable user-selected accessibility phrases, not automatic access to private health documents.

**Discoverability:** A single smart launcher uses intent classification/search, not a new 36th paid product. Query “ভাড়া চুক্তিটা বুঝব”, “পুকুরের পানি সবুজ”, “my salary overtime”, “বাচ্চার বাংলা পড়া” → route to precise module. The launcher must say why it recommended the tool; explicitly disambiguate health emergencies and redirect to professionals when needed.

## 3. Extraordinary UI/UX System — Not 35 Copies of One Template

**Name the visual system: “Riverlight Utility Studio”.** A uniquely Bangladeshi yet globally polished digital-public-goods identity, drawing from river deltas, rice fields, notebook grids and local printing; avoid clichés, heavy flag graphics and childlike government-site aesthetics. Set deep ink `#142C32`, monsoon teal `#116F6E`, off-white paper `#F6F4ED`, terracotta `#C57053`, warm yellow `#DBAA4D`, sky `#D7EDF0`, charcoal `#25343B`. Colors must pass WCAG contrast AA. Two complete palette modes: light and dark; dark `#101C21` with controlled contrast.

**Type:** Bengali UI uses Noto Sans Bengali (or an available properly licensed equivalent); Latin text uses Inter or Manrope. Do not ship proprietary fonts without rights. Harmonize line heights and layouts. **Brand mark** concept: a small continuous river-like curve connecting three dots (learn, act, improve), not another brain/robot neon icon. Admin can replace logo SVG, favicon, taglines, colors and typography through the CMS with validated formats.

**Desktop layout:** small left icon rail only in authenticated workspace; top strip with search, language, access preference, notification, account; centre canvas with generous space; contextual right rail only inside complex tools for helpful citations/history. Homepage Hero states real value in simple language, followed by task-based actions (“একটা কাগজ বুঝতে চাই”, “দাম তুলনা”, “শব্দ থেকে লেখা”, “কৃষি সাহায্য”), featured flows, trust/source practices, 35 tool catalogue and honest methodology. **Mobile:** bottom 4-position nav (Home, Explore, Workspace, Profile), no triple nested menus, minimum 44px touch targets, keyboard and one-handed use.

**Distinct module screen systems, not one repeated card grid:** document tools = evidence desk with left image and right extracted fields; health = large type, low distraction, timestamp prominent; education = bright but restrained learning progression; agriculture = measurement-first observation panel; civic = map/form timeline; audio = caption/waveform studio; sports = frames-and-motion overlay; shopping = comparison tables and receipts. Load heavier surfaces only when requested, and use proper accessible tables instead of 3D graphics.

**Design delivery criteria:** create a real design token file, documented UI primitives, 35 illustrated (SVG/icon) module identity marks or opt-in legally licensed media (never random uncited stock), responsive screenshots from Playwright at 390/768/1440 widths, RTL NOT needed for Bangla, and working bilingual strings. Provide component variants for 35 tool workspaces. Avoid decorative hero animations that delay interaction; reduced motion accessible.

**Accessibility:** proper skip links; focus rings; full keyboard navigation; high contrast; screen reader semantics; upload alternatives; dyslexia-friendly modes where possible; large font option; simpler Bangla reading mode; errors in both languages; offline phraseboard and educational reading passage caching where technically feasible; video captions/transcripts. Never require speaking/recording/camera access for text-compatible actions.

## 4. Technical Architecture — One Monorepo and One Domain

**Reference implementation:** Next.js App Router + React + TypeScript, Tailwind CSS + accessible component primitives, PostgreSQL + pgvector, Prisma/Drizzle as one consistent ORM, Auth.js (email/password with proper hashing and Google optional), private S3-compatible object storage, Redis-backed queue where justified, FastAPI/Python workers for CPU/GPU NLP/audio/CV jobs. Use Next.js server actions only when authorized and validating input. A heavy Python model service is an internal dependency reached via authenticated API, **not a second public website**. Avoid putting multi-GB transformer weights in Vercel serverless functions.

**Deployment topology:** `jibonsetu.example` hosts public+app+admin through ONE frontend deployment; one private API boundary, one PostgreSQL database, one private storage bucket hierarchy, worker as separately deployed back-end service only if necessary; production DNS/domain selected by owner. Vercel deployment is feasible for the web frontend; persistent inference, background jobs and large files need an approved suitable runtime. No imaginary free persistent GPU.

```text
                   ONE domain: jibonsetu.example
                             │
                 Next.js single application
                             │
     ┌──────────────┬──────────────┬──────────────┐
     │ Shared Auth  │ Shared Shell │ Central CMS  │
     └──────────────┴──────────────┴──────────────┘
                             │
        /tools/[slug] → Module Registry (35 entries)
                             │
      Ingestion→Validation→ML/Rule/RAG→Evidence→Report
             │                │             │
       Private Storage   Python Worker   PostgreSQL
                             │
              Approved source & model registries
                             │
                  Unified audit & observability
```

**Monorepo proposed tree:**

```text
jibonsetu-ai/
├─ apps/web/app/(public)/                 # home, tools, about, sources
├─ apps/web/app/(auth)/                   # one login/register/session
├─ apps/web/app/(workspace)/              # saved, reports, profile, privacy
├─ apps/web/app/(admin)/                  # centralized protected CMS
├─ apps/web/app/tools/[slug]/             # one dynamic tool shell
├─ apps/web/components/                   # accessible shared primitives
├─ apps/web/locales/bn.json + en.json
├─ packages/module-registry/              # all 35 declarative definitions
├─ packages/domain/                       # typed input/output contracts
├─ packages/authz/                        # RBAC, ABAC and consent
├─ packages/ui-tokens/                    # theme + variants
├─ packages/connectors/                   # permitted data import adapters
├─ packages/rag/                          # chunking/index/source verification
├─ services/model-worker/                 # FastAPI routes and real model runners
├─ services/job-worker/                   # scanning, ingestion and batch jobs
├─ prisma/ or drizzle/ + migrations/
├─ tests/                                  # unit, integration, E2E, eval sets
├─ data/approved/                          # no protected dataset in public Git
├─ docs/                                   # data provenance, deploy, ADR, audits
├─ .github/workflows/ci.yml
├─ .env.example
└─ README.md
```

**Modularity:** every module implements `ModuleDefinition` with `slug/category/name/i18n/inputSchema/outputSchema/aiPipeline/datasetSourceIds/consentRequirements/resultRenderer/adminConfig`. Shared services are a dependency, never copied 35 times. New modules can be enabled in CMS when gates pass. For long tasks, progress persists via job ID and retries are safe/idempotent. Rate limit uploads and AI endpoints per user plus daily quotas. File type validation by magic bytes, antivirus scanning, OCR extraction and local data normalization (BN digits to decimal) are platform services.

## 5. Unified Login, User Dashboard and Roles

**Unified login**: email+password and optional Google sign-in; verified email, passkeys/MFA for privileged admins, forgot/reset, session revocation, device list and inactivity timeout. No duplicate admin and user authentication systems. Role assigned server-side; NEVER grant admin from a URL, email claim alone, query parameter or visible menu. Only Super Admin can invite/approve additional admins. Users retain old imported identities using a migration-specific verified linking procedure; do not merge by display-name similarity.

**New user onboarding:** select language, accessibility preference, areas of interest (optional), agree to privacy, see 3 popular activities, don't force address/phone/medical history. Users may maintain multiple named workspaces for household or small business with explicit separation. Guest usage permitted for informational features only.

**Role hierarchy** (permissioned, never blanket private-record access): Guest, Registered User, Guardian, Organization/Shop Staff, Content Editor, Dataset Reviewer, Model Operator, Support Agent, Module Manager, Auditor, Super Admin. Organization-level roles need separate tenant boundaries. Super Admin can configure every part of the public website, tools and admin team; **raw private medical/legal/land/child documents remain purpose-protected**. Any special support access requires explicit user-consent grant, short expiry, reason and complete audit; emergency exception policies need a separate formal review.

**Workspace panes:** my activity timeline (filter by module), private vault, recent results, download center, notifications, source freshness, models used, unresolved review flags, delete/export data, opted-in contribution requests, security devices and integrations. User can correct OCR fields and rerun; original and edited values tracked without data loss. Sensitive module results never used for public leaderboard or marketing.

## 6. Super Admin: Complete Central CMS and Operational Controls

**Admin URLs:** `/admin` guarded by MFA where relevant; `/admin/overview`, `/admin/pages`, `/admin/brand`, `/admin/locales`, `/admin/navigation`, `/admin/tools`, `/admin/users`, `/admin/roles`, `/admin/organizations`, `/admin/datasets`, `/admin/models`, `/admin/rag`, `/admin/jobs`, `/admin/reports`, `/admin/feedback`, `/admin/moderation`, `/admin/notifications`, `/admin/sources`, `/admin/billing` (disabled unless enabled), `/admin/security`, `/admin/audit`, `/admin/retention`, `/admin/backups`, `/admin/deployment`, `/admin/settings`.

**CMS editing: EVERYTHING user-visible (by explicit page permissions):** Homepage hero, section order, tool titles/descriptions/keywords/icons, category labels, call-to-action button copy, page images, menu placements, logo, favicon, footer, contact, bio/team/About, FAQ, privacy/terms, accessibility statement, banner campaigns, sitemap metadata, blog/news, app-wide Bangla/English translations, static illustrations, help/how-to tutorials, input-field labels/descriptions, examples, error texts, report templates, downloadable resources, maintenance status, model/source disclaimers. Each editable item: draft preview, locale fallback, publish scheduling, version history, rollback, moderation review, immutable author/time record.

**Platform operations:** role provisioning/revocation, rate/quota policy, retention policy, feature flags, model readiness per module, dataset source reviews, approved import jobs, offline status, queue retries, feedback classification, moderation, export of aggregate non-identifying analytics, security incident review, uptime, errors and alert thresholds. Use dry-run for CSV imports, allow row conflict preview and reversible rollback. Never let an admin silently change another user's consent or rewrite raw private results; auditable support actions only.

**Model console:** exact architecture/checkpoint/hash/license/status, evaluation scorecard, drift metrics, false-positive/false-negative samples with privacy safeguards, hot-swap canary deployment, revert model, disable unreliable model without taking the entire app offline. **RAG console:** source-approved collections, index version, chunk preview, crawl rights state, stale-content badge, deletion and re-embedding queue, citation spot audit.

**Dataset console:** original publisher URL, terms, authorization evidence, sensitivity class, access method, ingestion timestamp, geographic coverage, license URI, human reviewer, checksums, schema and missing values, collection date, opt-in terms, published/paused/revoked status. Dataset changes that affect medical/financial/legal information require a separate review gate. Audit support access and all exports. Credential management uses secret vault/runtime secrets; never display plaintext database secrets in the admin.

## 7. Bangladesh Dataset Policy — Permission Before Import, Transparency Always

**DO NOT mistake a government website for a downloadable training dataset.** A public government source may contain a PDF, lookup form or statistics and still limit copying, automated fetching, redistribution or model training. The official **Bangladesh Open Data Terms** are a starting point: https://data.gov.bd/terms-of-use. Check the specific asset and current terms. The centralized candidate registry has **207 link entries**, inherited primarily from the earlier V5 prompts; it is a discovery inventory, **not 207 downloaded/verified training sets**.

**Allowed acquisition lanes, in priority order:**
1. Officially open/licensed Bangladesh dataset with machine-readable file and documented scope. Record dataset-level rights, download bytes, checksum and source date.
2. A Bangladesh government report/manual openly viewable but without bulk/training grant: **link and cite** the published reference; seek permission before full ingestion or model training, avoid robots bypass; use approved small excerpts only if law and rights allow.
3. Public-web or academic Bangladesh-specific data with author/publisher permission, research licence and source-level citation; permission to view ≠ licence to redistribute/train.
4. Original content authored for this project (e.g., example reading passages, illustrations, instructions, standardized vocabulary), explicitly label authored and not official.
5. Voluntary opt-in public or privately retained user submissions, separately consented for service operation versus model training. Delete on withdrawal; sanitize names, phone numbers, ID numbers, images of children, property documents and patient records.
6. Anonymous synthetic test data solely for demonstrations/tests; mark `synthetic`, never published as a true observation or real legal/medical record.

**Record states:** `candidate`, `access_review`, `rights_review`, `approved_reference_only`, `approved_train_and_reuse`, `imported`, `quarantined`, `revoked`. None of these URLs are auto-import enabled by default. A scheduled job checks availability/metadata via compliant API or approved method only; if a page blocks access, do NOT evade. Review provider updates, source freshness and legal restrictions with a human reviewer. Show precise source timestamps and version in every report. Re-ingest/embeddings after reapproval, audit changes. Medical records and children’s audio are never added to a shared corpus by default.

**File location:** `datasets/SOURCE_REGISTRY.csv` (human review), `datasets/SOURCE_REGISTRY.json` (machine control), `reference/legacy-v5/projects/*/DATASET_SOURCE_REGISTRY.json` (original preserved details). `seed/*` contains only empty templates or explicitly original phrase examples, **not acquired confidential government records**. If imported data can be used under a view-only condition, keep outward links, not copied corpus assets. RAG ingestion is a separate rights-controlled operation from model training.

**Key verified entry points (October 2026):** DGHS Facility Registry https://hris.mohfw.gov.bd/public/facility-registry/ ; DGHS Dengue https://dashboard.dghs.gov.bd/pages/heoc_dengue_v1.php ; DAM prices https://market.dam.gov.bd/market_daily_price_report ; Bangladesh labour law https://bdlaws.minlaw.gov.bd/act-details-952.html?lang=en ; Labour Ministry amendment list https://mole.gov.bd/pages/legislative-informations ; land mutation https://mutation.land.gov.bd/ ; land survey https://settlement.gov.bd/ . Always verify field-level publication dates and underlying asset rights before a production import.

## 8. Shared Model Infrastructure — Real Inference Required

**All 35 modules require implemented intelligence—not identical ML for each one.** Distinguish deterministic computation from ML. Core framework: `ModelRegistry`, `DatasetRegistry`, `InferenceGateway`, `RuleEngine`, `RAGCollection`, `PromptVersion`, `EvaluationRun`, `ModelCard`, `SafetyGuard`, `ConfidencePolicy`. Model candidate list is in `model/MODEL_REGISTRY.json`, and original specifications for the 32 modules remain in `reference/legacy-v5/projects/.../MODEL_IMPLEMENTATION_SPEC.json`.

**Pipeline for camera/docs:** antivirus + image normalization → Bengali/English OCR (Tesseract or better evaluated model) → token normalization → typed entity/schema validation → uncertainty per field → domain-specific calculation/comparison/RAG → source-cited report. For files: explicitly check content type, max size, page count, rotated scans and Bangla Unicode. OCR must show unrecognized portions and let the user correct them.

**Pipeline for audio:** permission → channel/language validation → ASR with speaker/latency limitations → Bangla orthographic normalizer → confidence marks → editable transcript → private history. Bangla ASR needs actual Bangla evaluation; Whisper on its own is not proof of acceptable Bengali performance. Optional TTS voice must be rights-cleared. Provide low-latency phraseboard as reliable fallback.

**Pipeline for numeric/time series:** input validation, units, boundaries and impossible-value flags → transparent baseline/statistic/ML if sufficient historical data exists → sample size and confidence bands → source dates and calculator assumptions. If history is too small, avoid training a fake forecast; show deterministic calculations or insufficient data.

**Pipeline for RAG:** source registration → rights gate → parse/split and attach page/section/grade/year metadata → vector index + BM25 hybrid retrieval → reranking → generation only within grounded passages → answer verification → passage-level source citations → refuse unsupported questions. Never use free-form generation as a substitute for legal or medical advice. ShikkhaRAG must load a real sentence-embedding checkpoint, retrieve useful original approved Bangla snippets, test source IDs, and output a source-cited answer with no false page numbers.

**Minimum test gate per module:** real process started, model identity/version logged; 3 ordinary Bangladesh examples + 3 adversarial examples; low-quality input, wrong units, Bangla digits, English/Banglish mixed input, no-evidence answer, hallucination and privacy leakage tests; human-reviewed representative holdout; baseline vs model comparison and latency/memory logs. For medical/legal/wage/land, avoid unsupported labels, route to expert where needed. Never publish accuracy % before evaluation and a disclosed test sample size.

**Model lifecycle:** `unavailable`, `experimental`, `verified_for_limited_use`, `public_beta`, `stable`, `disabled`. Admin may toggle visibility, inspect test failures and rollback. **Do not present the 35 tools as fully trained/verified until proven.** CPU-preferred models for common text; use separate approved GPU/CPU inference where needed. Cache public retrieval only, not private PDFs/transcripts across users.

## 9. Database and Data Relationships

**Shared relational base:** `users`, `identities`, `sessions`, `organizations`, `memberships`, `roles`, `permissions`, `user_consents`, `portal_modules`, `module_content`, `cms_pages`, `cms_versions`, `tool_runs`, `tool_inputs`, `tool_outputs`, `private_assets`, `saved_reports`, `dataset_sources`, `dataset_versions`, `source_permissions`, `ingestion_jobs`, `model_versions`, `model_eval_runs`, `rag_documents`, `rag_chunks`, `notifications`, `feedback`, `admin_audit_events`, `support_access_grants`, `privacy_deletion_requests`, `export_jobs`, `migration_checkpoints`. Keep high-sensitivity tables logically and sometimes physically separate; use tenant_id/workspace_id and row-level authorization checks in every read/write.

**Typed storage:** Input files encrypted at rest in private object storage, per-user signed short-lived access URLs, original vs OCR corrected text provenance, no public CDN for sensitive documents. PostgreSQL structured records and results, pgvector for licensed RAG, jobs for long video/audio analyses. Never store large raw files in Git. Use DB transactions for app records; idempotency keys for reprocessing and uploads. Retention configurable by category and explicit user control.

**Public index:** Only public tool metadata and licensed/reference source pages are discoverable by search engines; `/workspace`, `/admin`, raw reports, user audio/docs and public share tokens default to `noindex`. Analytics aggregate only after consent and thresholding; avoid ID leakage through filenames, URLs and logs.

**Starter SQL file:** `database/BASELINE_POSTGRES.sql` is a partial design reference, not a production-ready authorization migration. ChatGPT Work must build/test the complete schema and account permissions in code. User can export a portable privacy-aware archive and delete the account; scheduled retention executes documented deletion. Maintain hard backup + restore test with key management and source revocation.

## 10. REST/Typed API Surface and Typed Result Standard

Create typed API endpoints (or equivalent authenticated server actions) under one domain. Public browse: `GET /api/modules`, `/api/modules/:slug`, `/api/sources`. User: `POST /api/tools/:slug/runs` with schema validation and module-specific rules, `GET /api/runs/:id`, `POST /api/runs/:id/correct`, `/export`, `/delete`, `GET /api/workspaces/:id/history`, `POST /api/upload/init`, `POST /api/upload/complete` (scanned), `POST /api/consent`, `DELETE /api/consent/:id`. Admin: `/api/admin/modules`, `/api/admin/cms`, `/api/admin/sources`, `/api/admin/models`, `/api/admin/datasets/import/dry-run`, `/api/admin/datasets/import/approve`, `/api/admin/audit`, `/api/admin/permissions`, `/api/admin/jobs` with server-enforced RBAC and audit.

**Result JSON contract (illustration, NOT a fake inference):**

```json
{
  "run_id": "uuid", "module": "billdetect-ai", "status": "completed",
  "language": "bn", "source_kind": "user_uploaded_document",
  "source_as_of": null, "model_version": "actual-model-checkpoint-id",
  "human_readable_summary": "Reviewed arithmetic summary",
  "facts": [{"key":"amount", "value": 0, "unit":"BDT", "evidence_ref":"page-1-line-9"}],
  "uncertainties": ["Field XYZ was not readable"],
  "references": [{"title":"Source document", "url": null, "page": 1}],
  "next_actions": ["Verify with the issuer"],
  "disclaimer_key": "tool.billdetect.information_only"
}
```

Never return `completed` without the processing actually happening. Do not invent reference page IDs or expose raw user uploads outside owner scope. Bad input → 422 localized feedback; rate-limit → 429; queued → 202 and job ID. One module's failure must not take the platform down.

## 11. Real Bangladesh Localization and Units

All UI fully translated in Bangla and English, `bn-BD` default. Locale keys versioned in JSON, editable in CMS under review. Bengali digits accepted and normalized to exact decimals without silent unit conversions; show original and derived value side-by-side. Land `shotok/decimal`, `acre`, regional `bigha` must be interpreted only with confirmed unit and jurisdiction. Financial amounts stored as integer paisa or decimal money, NEVER floating calculations that drift. Taka displayed as ৳, user time zone Asia/Dhaka, source timestamps ISO 8601.

Support Banglish queries to find a tool, yet show health/legal/land safety instructions in clear BN/EN with accurate citations. Offer text input as alternative to audio and images; provide printable low-ink PDFs, accessible tables, large typography, readable errors, and step-by-step explanations for low digital literacy.

## 12. Privacy, Safety, and Responsible Use

**Healthcare:** organize/teach from records, not diagnosis or novel dose recommendations. Urgent symptoms require professional care; doctors verify. Extra protections for children/maternal records. **Blood:** only opt-in donors, concealed contact data, time-limited requests, professional compatibility checks. **Land/legal/wages:** flag discrepancies and explain publicly documented rules, not legal certification or final wage entitlement. **Road, roof, water and climate:** observations rather than structural, water-quality or official safety certification. **Accessibility:** do not claim universal sign language translation or 100% accurate speech transcription.

Security: MFA for privileged roles, secure sessions, CSRF guards, CSP, signed upload URLs, file signature/virus scan, encryption, sensitive data redaction, safe Unicode rendering, prompt-injection defense for PDFs and RAG, DB-enforced per-user scoping, secrets via runtime store not Git, storage retention, abuse/rate limits, immutable admin audit and incident process. Public aggregate analytics only with consent, group thresholds and no private record leakage.

## 13. Four Already-Built Websites — Risk-Controlled Consolidation

**Existing:** ChuktiShield AI (#06), DokanLens AI (#10), BazarCompare AI (#11), BanglaRead Coach (#32). They already exist separately in the user's development workflow, but actual current repo URLs/branches and code have not been shared in this conversation. Never pretend current code state is known.

1. Read four real repos using authorized GitHub access; record branch/commit, license, migrations, provider and build diagnostics. Backup DB and assets safely before modifying anything.
2. Create a NEW central repo `jibonsetu-ai` only with owner consent. Import reusable UI/domain code to central monorepo namespaced modules, remove duplicated auth/menus/admin only after parity.
3. Identity mapping via verified linking; do not merge by name or transfer protected documents without separate consent/legal basis. Keep old IDs/mappings and a reversible backfill ledger.
4. Stage `/tools/chuktishield-ai`, `/tools/dokanlens-ai`, `/tools/bazarcompare-ai`, `/tools/banglaread-coach` behind flags. Run input/output regression, screenshots and user-data continuity tests.
5. Leave original repositories and deployments intact until owner reviews full parity and redirects. No force-push, delete, archive or DNS redirect without explicit approval; verify rollback.
6. If connected GitHub access unavailable, build integration adapters and write a precise dependency list, continue the central website with other modules; NEVER say originals have been migrated.

## 14. ONE GitHub Repository, CI/CD and Deployment

**One monorepo:** `jibonsetu-ai` under authorized owner's GitHub identity (not 35 repos). Use branches `main` (protected), `feature/central-auth`, `feature/cms`, `feature/module-{slug}`, `migration/{slug}`. PR checks: lint, typecheck, unit, integration, migrations, module registry count=35, i18n key parity, schema checks, E2E, security scan, safe source registry, and separately marked **real model smoke tests** for each published tool. Do not turn dummy model tests green and call them integration.

**One website deployment:** frontend on Vercel or equivalent approved account, PostgreSQL and private blob storage, separately deployed internal Python model worker when necessary (real persistent container/compute required). A serverless Next.js UI cannot pretend to host large GPU weights. Support staging, review deployments, secrets via protected host settings, production release tags, rollback and restore drills.

```bash
npm ci
npm run lint
npm run typecheck
npm run test
npm run build
# Only after owner authorizes a newly created central repo:
git checkout -b feature/central-platform
git add .
git commit -m "feat: integrate 35 Bangladesh AI tools in one portal"
git push -u origin feature/central-platform
```

Push proof includes GitHub URL, actual SHA, branch, PR and CI status; if GitHub approval missing, write exact remaining steps and DO NOT claim remote push.

## 15. Build Phases and Strict Exit Gates

**Phase 0: baseline & licences.** Inventory four existing repos, full 32 legacy prompts, new 3 features, data-source rights and selected model runtimes; produce gap matrix.

**Phase 1: platform shell.** Build brand, theme, bilingual landing + about + all 35 discoverable catalogue pages, shared login, permissions, CMS page editor, working sidebar/mobile nav, user workspace and admin. 35 routes resolve with real honest readiness status.

**Phase 2: migrate four.** Integrate BanglaRead, DokanLens, BazarCompare, ChuktiShield with real feature parity, existing-account continuity and rollback; migrate only with user approval.

**Phase 3: distinctive high-need tools.** LandLedger, WageGuard, ShobdoSetu with real working workflows and verifiable sources, initial model baseline and tight safety/consent.

**Phase 4: remaining 28.** Cluster by agriculture/environment, health, civic/housing and education; for each tool implement one full functional real pipeline and then expand to advanced features from original V5.

**Phase 5: evaluation/hardening.** Approved Bangladesh holdout evaluation, source rights and confidence reviews, zero-hallucination unsupported citation tests, performance/accessibility/security and backup/restore exercises.

**Phase 6: production handoff.** Owner-authorized GitHub repo push and Vercel/frontend and model-worker deployment; provide real deployment addresses, runbooks and tests.

If resources insufficient, finish a tested vertical slice and write `docs/PROGRESS_LEDGER.md` (done/blocked/not-started with proof). Future Work tasks MUST resume from real last checkpoint, not duplicate generated code. No public beta claims for untested ML.

## 16. Definition of Done, QA and No-Fake Policy

At platform level: exactly 35 registered tool slugs, 35 route screens, one login, one admin, one PostgreSQL-backed workspace, all visible strings fully BN/EN, responsive 390/768/1440px, keyboard accessibility, source/AI model/provenance transparency, privacy export/delete, feature status labels and shared navigation. At feature level: actual input → validated real processing → explainable result → owner-private save/export/retry/delete, with low-confidence cases and failure tests.

`qa/ACCEPTANCE_MATRIX.csv` contains 280 initial test cases, initially all `NOT_RUN`. Pass only after running them, storing evidence. Publish security tests: guessed run ID cannot fetch another user's result, admin without grant cannot read raw child/medical/land uploads, model cannot return fabricated government figures, source permissions gate prevents accidental training, file type/size invalid uploads fail safely, Bangla numeric parsing works.

Deliver one running codebase, real frontend/backend, migrations, tests, full Super Admin CMS, dataset/model registries, i18n, CI, GitHub proof (if approved), deploy plan, transparent source limitations, and no synthetic current market/medical/legal claims. No placeholders passed off as completed tools.

## 17. Complete Module-by-Module Requirements (35)

**Status key:** `existing repo migration` for 4 already-built projects, `new module` for others. The **32 complete previous V5 master prompts** and their data/model/QA specifications are preserved under `reference/legacy-v5`; ingest their *unique feature requirements* but never obey their old instruction to create separate websites. The new portal architecture in this README takes precedence.

### 01 · PukurSOS AI — Agriculture & Fisheries

**Status:** Planned V5 project — integrate · **Single-domain URL:** `/tools/pukursos-ai` · **Shared workspace:** `/workspace` · **Central Admin configuration:** `/admin/tools/pukursos-ai`.

**About (বাংলাদেশে কী সমস্যা সমাধান):** ব্যবহারকারী সহজে **পুকুরের পানির ছবি, মাছের আচরণের ভিডিও, pH/DO মাপ** দিলে **পানির অবস্থা লগ, সম্ভাব্য সতর্কতা ও পরীক্ষার পরামর্শ** পাবে। এই টুলের নিজস্ব visual identity এবং value feature হলো **পুকুরের স্বাস্থ্য ডায়েরি ও মৌসুমি গ্রাফ**। এটি ৩৪টি টুলের generic wrapper হবে না।

**User screen:** simple About + safety promise → picture/text/audio/numeric input choice (only supported modalities, CSV optional not mandatory) → privacy consent → extracted preview/correction → processing progress and model status → primary Bangla result in ≤3 clear main actions → expandable evidence/source timestamps, download/share privately and delete. Design input/output forms for elderly and low-data mobile conditions.

**Model work that must actually run:** water-quality anomaly detection + video-event classification. Candidate checkpoints: **torchvision pretrained MobileNetV3/EfficientNet-B0 feature backbone; sklearn.ensemble.IsolationForest; sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2**. Execute at least one real relevant pipeline, write model card, version, test cases and fallback, and use deterministic rules explicitly named as rules. Include Bangladesh-specific test examples, confidence and error evaluation. **Never label an unrun model “integrated”.**

**Data plan:** fish water measurement user logs. Relevant references (NOT automatically licensed training datasets):
- Department of Fisheries public yearbooks: https://fisheries.gov.bd/pages/static-pages/6922e13e933eb65569e2b13e — **candidate; confirm access, dataset-specific licence, freshness**.
- Department of Fisheries — Fisheries Statistics Yearbooks: https://fisheries.portal.gov.bd/pages/static-pages/6922e13e933eb65569e2b13e — **candidate; confirm access, dataset-specific licence, freshness**.
- BAMIS — agricultural weather and advisories: https://www.bamis.gov.bd/en/home/ — **candidate; confirm access, dataset-specific licence, freshness**.

**User trust and safety:** pH/DO ছাড়া অক্সিজেনের সংখ্যা অনুমান নিষিদ্ধ। Advanced panel থাকবে, কিন্তু সাধারণ ব্যবহারকারীর জন্য তিন ধাপের flow; evidence/uncertainty panel যুক্ত থাকবে।

**Central Admin module panel:** configure localized title/about/help/input schema/upload limits/report template/theme accents and navigation, model choice/version, source permission state, dataset import preview, reviewer queue, QA scores, per-tool quota/retention, moderation, canary rollout, feature-disable switch, error logs and version history. All server-authorized.

**Release acceptance:** valid original or approved test input produces stored owner-only outcome with evidence; real model/rule tested; invalid image/file/text/numbers fail gracefully; BN/EN; mobile layout; download/delete; private test and no unsupported claim.

### 02 · NodiWatch AI — Environment & Climate

**Status:** Planned V5 project — integrate · **Single-domain URL:** `/tools/nodiwatch-ai` · **Shared workspace:** `/workspace` · **Central Admin configuration:** `/admin/tools/nodiwatch-ai`.

**About (বাংলাদেশে কী সমস্যা সমাধান):** ব্যবহারকারী সহজে **নদীতীরের তারিখসহ ছবি, GPS ঐচ্ছিক** দিলে **দুই দিনের পরিবর্তন ও স্থানীয় পর্যবেক্ষণ রিপোর্ট** পাবে। এই টুলের নিজস্ব visual identity এবং value feature হলো **Before/After স্লাইডার ও পর্যবেক্ষণ টাইমলাইন**। এটি ৩৪টি টুলের generic wrapper হবে না।

**User screen:** simple About + safety promise → picture/text/audio/numeric input choice (only supported modalities, CSV optional not mandatory) → privacy consent → extracted preview/correction → processing progress and model status → primary Bangla result in ≤3 clear main actions → expandable evidence/source timestamps, download/share privately and delete. Design input/output forms for elderly and low-data mobile conditions.

**Model work that must actually run:** image alignment + change detection + geospatial comparison. Candidate checkpoints: **torchvision pretrained MobileNetV3/EfficientNet-B0 feature backbone; sklearn.ensemble.IsolationForest**. Execute at least one real relevant pipeline, write model card, version, test cases and fallback, and use deterministic rules explicitly named as rules. Include Bangladesh-specific test examples, confidence and error evaluation. **Never label an unrun model “integrated”.**

**Data plan:** riverbank photo pairs with consent. Relevant references (NOT automatically licensed training datasets):
- FFWC observed water levels: https://ffwc.gov.bd/app/observed-water-level — **candidate; confirm access, dataset-specific licence, freshness**.
- FFWC API docs landing: https://api.ffwc.gov.bd/?format=json — **candidate; confirm access, dataset-specific licence, freshness**.
- BWDB Hydrology — river/water monitoring: https://hydrology.bwdb.gov.bd/ — **candidate; confirm access, dataset-specific licence, freshness**.

**User trust and safety:** ভবিষ্যৎ ভাঙনের নিশ্চয়তা নয়। Advanced panel থাকবে, কিন্তু সাধারণ ব্যবহারকারীর জন্য তিন ধাপের flow; evidence/uncertainty panel যুক্ত থাকবে।

**Central Admin module panel:** configure localized title/about/help/input schema/upload limits/report template/theme accents and navigation, model choice/version, source permission state, dataset import preview, reviewer queue, QA scores, per-tool quota/retention, moderation, canary rollout, feature-disable switch, error logs and version history. All server-authorized.

**Release acceptance:** valid original or approved test input produces stored owner-only outcome with evidence; real model/rule tested; invalid image/file/text/numbers fail gracefully; BN/EN; mobile layout; download/delete; private test and no unsupported claim.

### 03 · FasalLoss AI — Agriculture & Fisheries

**Status:** Planned V5 project — integrate · **Single-domain URL:** `/tools/fasalloss-ai` · **Shared workspace:** `/workspace` · **Central Admin configuration:** `/admin/tools/fasalloss-ai`.

**About (বাংলাদেশে কী সমস্যা সমাধান):** ব্যবহারকারী সহজে **ফসলের ছবি, ফসলের ধরন, ক্ষতিগ্রস্ত জমির মাপ** দিলে **ক্ষতির দৃশ্যমান শ্রেণিবিন্যাস ও আবেদন উপযোগী বিবরণ** পাবে। এই টুলের নিজস্ব visual identity এবং value feature হলো **ফসলের ক্ষতি পর্যবেক্ষণ ও মৌসুমভিত্তিক নোট**। এটি ৩৪টি টুলের generic wrapper হবে না।

**User screen:** simple About + safety promise → picture/text/audio/numeric input choice (only supported modalities, CSV optional not mandatory) → privacy consent → extracted preview/correction → processing progress and model status → primary Bangla result in ≤3 clear main actions → expandable evidence/source timestamps, download/share privately and delete. Design input/output forms for elderly and low-data mobile conditions.

**Model work that must actually run:** crop image segmentation + uncertainty calibration. Candidate checkpoints: **torchvision pretrained MobileNetV3/EfficientNet-B0 feature backbone; sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2**. Execute at least one real relevant pipeline, write model card, version, test cases and fallback, and use deterministic rules explicitly named as rules. Include Bangladesh-specific test examples, confidence and error evaluation. **Never label an unrun model “integrated”.**

**Data plan:** Bangladesh crop photo labels opt-in. Relevant references (NOT automatically licensed training datasets):
- FFWC observation portal: https://ffwc.gov.bd/app/observed-water-level — **candidate; confirm access, dataset-specific licence, freshness**.
- BAMIS — agricultural weather and advisories: https://www.bamis.gov.bd/en/home/ — **candidate; confirm access, dataset-specific licence, freshness**.
- Bangladesh Open Data — searchable datasets: https://data.gov.bd/dataset — **candidate; confirm access, dataset-specific licence, freshness**.

**User trust and safety:** শতাংশ বা টাকার ক্ষতি যাচাই ছাড়া নয়। Advanced panel থাকবে, কিন্তু সাধারণ ব্যবহারকারীর জন্য তিন ধাপের flow; evidence/uncertainty panel যুক্ত থাকবে।

**Central Admin module panel:** configure localized title/about/help/input schema/upload limits/report template/theme accents and navigation, model choice/version, source permission state, dataset import preview, reviewer queue, QA scores, per-tool quota/retention, moderation, canary rollout, feature-disable switch, error logs and version history. All server-authorized.

**Release acceptance:** valid original or approved test input produces stored owner-only outcome with evidence; real model/rule tested; invalid image/file/text/numbers fail gracefully; BN/EN; mobile layout; download/delete; private test and no unsupported claim.

### 04 · RoofWise AI — Housing & Home

**Status:** Planned V5 project — integrate · **Single-domain URL:** `/tools/roofwise-ai` · **Shared workspace:** `/workspace` · **Central Admin configuration:** `/admin/tools/roofwise-ai`.

**About (বাংলাদেশে কী সমস্যা সমাধান):** ব্যবহারকারী সহজে **ছাদ/ঘরের ছবি, আয়তন, দিক ও বাজেট** দিলে **শীতল ছাদ, পানি নিষ্কাশন ও সাশ্রয়ী সংস্কারের বিকল্প** পাবে। এই টুলের নিজস্ব visual identity এবং value feature হলো **কত খরচে কী সুবিধা—তুলনামূলক কার্ড**। এটি ৩৪টি টুলের generic wrapper হবে না।

**User screen:** simple About + safety promise → picture/text/audio/numeric input choice (only supported modalities, CSV optional not mandatory) → privacy consent → extracted preview/correction → processing progress and model status → primary Bangla result in ≤3 clear main actions → expandable evidence/source timestamps, download/share privately and delete. Design input/output forms for elderly and low-data mobile conditions.

**Model work that must actually run:** scene understanding + rule calculator + weather context. Candidate checkpoints: **torchvision pretrained MobileNetV3/EfficientNet-B0 feature backbone; scikit-learn HistGradientBoostingRegressor / RandomForestRegressor**. Execute at least one real relevant pipeline, write model card, version, test cases and fallback, and use deterministic rules explicitly named as rules. Include Bangladesh-specific test examples, confidence and error evaluation. **Never label an unrun model “integrated”.**

**Data plan:** roof photo with consent and location context. Relevant references (NOT automatically licensed training datasets):
- BAMIS — agricultural weather and advisories: https://www.bamis.gov.bd/en/home/ — **candidate; confirm access, dataset-specific licence, freshness**.
- FFWC — flood and river hydrological information: https://ffwc.gov.bd/ — **candidate; confirm access, dataset-specific licence, freshness**.
- Bangladesh Open Data — searchable datasets: https://data.gov.bd/dataset — **candidate; confirm access, dataset-specific licence, freshness**.

**User trust and safety:** স্ট্রাকচারাল সার্টিফিকেট নয়। Advanced panel থাকবে, কিন্তু সাধারণ ব্যবহারকারীর জন্য তিন ধাপের flow; evidence/uncertainty panel যুক্ত থাকবে।

**Central Admin module panel:** configure localized title/about/help/input schema/upload limits/report template/theme accents and navigation, model choice/version, source permission state, dataset import preview, reviewer queue, QA scores, per-tool quota/retention, moderation, canary rollout, feature-disable switch, error logs and version history. All server-authorized.

**Release acceptance:** valid original or approved test input produces stored owner-only outcome with evidence; real model/rule tested; invalid image/file/text/numbers fail gracefully; BN/EN; mobile layout; download/delete; private test and no unsupported claim.

### 05 · NoiseTrace AI — Environment & Climate

**Status:** Planned V5 project — integrate · **Single-domain URL:** `/tools/noisetrace-ai` · **Shared workspace:** `/workspace` · **Central Admin configuration:** `/admin/tools/noisetrace-ai`.

**About (বাংলাদেশে কী সমস্যা সমাধান):** ব্যবহারকারী সহজে **নিজের রেকর্ড করা অডিও** দিলে **শব্দের উৎস শ্রেণি ও দৈনিক noise journal** পাবে। এই টুলের নিজস্ব visual identity এবং value feature হলো **অডিও ওয়েভফর্ম, উৎস লেবেল, প্রতিবেদন**। এটি ৩৪টি টুলের generic wrapper হবে না।

**User screen:** simple About + safety promise → picture/text/audio/numeric input choice (only supported modalities, CSV optional not mandatory) → privacy consent → extracted preview/correction → processing progress and model status → primary Bangla result in ≤3 clear main actions → expandable evidence/source timestamps, download/share privately and delete. Design input/output forms for elderly and low-data mobile conditions.

**Model work that must actually run:** audio event detection + calibrated optional measurement. Candidate checkpoints: **YAMNet audio event classifier; sklearn.ensemble.IsolationForest**. Execute at least one real relevant pipeline, write model card, version, test cases and fallback, and use deterministic rules explicitly named as rules. Include Bangladesh-specific test examples, confidence and error evaluation. **Never label an unrun model “integrated”.**

**Data plan:** consented audio clips. Relevant references (NOT automatically licensed training datasets):
- Department of Environment — daily AQI report: https://doe.portal.gov.bd/pages/static-pages/6922dfba933eb65569e23b0a — **candidate; confirm access, dataset-specific licence, freshness**.
- Bangladesh Open Data — searchable datasets: https://data.gov.bd/dataset — **candidate; confirm access, dataset-specific licence, freshness**.
- OpenStreetMap — Bangladesh Geofabrik extract: https://download.geofabrik.de/asia/bangladesh.html — **candidate; confirm access, dataset-specific licence, freshness**.

**User trust and safety:** মোবাইলের ক্যালিব্রেশন ছাড়া dB আইনি প্রমাণ নয়। Advanced panel থাকবে, কিন্তু সাধারণ ব্যবহারকারীর জন্য তিন ধাপের flow; evidence/uncertainty panel যুক্ত থাকবে।

**Central Admin module panel:** configure localized title/about/help/input schema/upload limits/report template/theme accents and navigation, model choice/version, source permission state, dataset import preview, reviewer queue, QA scores, per-tool quota/retention, moderation, canary rollout, feature-disable switch, error logs and version history. All server-authorized.

**Release acceptance:** valid original or approved test input produces stored owner-only outcome with evidence; real model/rule tested; invalid image/file/text/numbers fail gracefully; BN/EN; mobile layout; download/delete; private test and no unsupported claim.

### 06 · ChuktiShield AI — Civic, Worker Rights & Legal

**Status:** ALREADY BUILT — migrate conservatively · **Single-domain URL:** `/tools/chuktishield-ai` · **Shared workspace:** `/workspace` · **Central Admin configuration:** `/admin/tools/chuktishield-ai`.

**About (বাংলাদেশে কী সমস্যা সমাধান):** ব্যবহারকারী সহজে **নিজের চুক্তির ছবি, PDF বা টেক্সট** দিলে **শর্তের সারাংশ, প্রশ্ন ও আইনি উৎসসহ সতর্কতা** পাবে। এই টুলের নিজস্ব visual identity এবং value feature হলো **Clause Lens ও পাশাপাশি দুটি চুক্তি তুলনা**। এটি ৩৪টি টুলের generic wrapper হবে না।

**User screen:** simple About + safety promise → picture/text/audio/numeric input choice (only supported modalities, CSV optional not mandatory) → privacy consent → extracted preview/correction → processing progress and model status → primary Bangla result in ≤3 clear main actions → expandable evidence/source timestamps, download/share privately and delete. Design input/output forms for elderly and low-data mobile conditions.

**Model work that must actually run:** Bangla OCR + clause classification + legal hybrid RAG. Candidate checkpoints: **Tesseract OCR with ben+eng language packs; sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2; rank-bm25 lexical retrieval**. Execute at least one real relevant pipeline, write model card, version, test cases and fallback, and use deterministic rules explicitly named as rules. Include Bangladesh-specific test examples, confidence and error evaluation. **Never label an unrun model “integrated”.**

**Data plan:** redacted sample clauses + permitted law refs. Relevant references (NOT automatically licensed training datasets):
- Laws of Bangladesh — Contract Act 1872: https://bdlaws.minlaw.gov.bd/act-details-26.html?lang=en — **candidate; confirm access, dataset-specific licence, freshness**.
- Laws of Bangladesh — Transfer of Property Act 1882: https://bdlaws.minlaw.gov.bd/act-print-48.html — **candidate; confirm access, dataset-specific licence, freshness**.
- Laws of Bangladesh — Labour Act 2006: https://bdlaws.minlaw.gov.bd/act-details-952.html?lang=en — **candidate; confirm access, dataset-specific licence, freshness**.

**User trust and safety:** আইনি মতামতের বদলি নয়; ব্যক্তিগত কাগজ গোপন। Advanced panel থাকবে, কিন্তু সাধারণ ব্যবহারকারীর জন্য তিন ধাপের flow; evidence/uncertainty panel যুক্ত থাকবে।

**Central Admin module panel:** configure localized title/about/help/input schema/upload limits/report template/theme accents and navigation, model choice/version, source permission state, dataset import preview, reviewer queue, QA scores, per-tool quota/retention, moderation, canary rollout, feature-disable switch, error logs and version history. All server-authorized.

**Release acceptance:** valid original or approved test input produces stored owner-only outcome with evidence; real model/rule tested; invalid image/file/text/numbers fail gracefully; BN/EN; mobile layout; download/delete; private test and no unsupported claim.

### 07 · BillDetect AI — Shopping & Expenses

**Status:** Planned V5 project — integrate · **Single-domain URL:** `/tools/billdetect-ai` · **Shared workspace:** `/workspace` · **Central Admin configuration:** `/admin/tools/billdetect-ai`.

**About (বাংলাদেশে কী সমস্যা সমাধান):** ব্যবহারকারী সহজে **বিদ্যুৎ/পানি/গ্যাস বিলের ছবি এবং ঐচ্ছিক আগের বিল** দিলে **চার্জ breakdown, যোগফল ও অস্বাভাবিক পার্থক্য** পাবে। এই টুলের নিজস্ব visual identity এবং value feature হলো **চার্জ ব্যাখ্যার ভিজ্যুয়াল রসিদ**। এটি ৩৪টি টুলের generic wrapper হবে না।

**User screen:** simple About + safety promise → picture/text/audio/numeric input choice (only supported modalities, CSV optional not mandatory) → privacy consent → extracted preview/correction → processing progress and model status → primary Bangla result in ≤3 clear main actions → expandable evidence/source timestamps, download/share privately and delete. Design input/output forms for elderly and low-data mobile conditions.

**Model work that must actually run:** OCR + arithmetic validation + anomaly model. Candidate checkpoints: **Tesseract OCR with ben+eng language packs; sklearn.ensemble.IsolationForest**. Execute at least one real relevant pipeline, write model card, version, test cases and fallback, and use deterministic rules explicitly named as rules. Include Bangladesh-specific test examples, confidence and error evaluation. **Never label an unrun model “integrated”.**

**Data plan:** user-owned utility bills masked. Relevant references (NOT automatically licensed training datasets):
- National Consumer Rights Protection — complaints and rules: https://dncrp.gov.bd/ — **candidate; confirm access, dataset-specific licence, freshness**.
- Consumer Complaint Management System: https://dncrp.com/ — **candidate; confirm access, dataset-specific licence, freshness**.
- Bangladesh Open Data — searchable datasets: https://data.gov.bd/dataset — **candidate; confirm access, dataset-specific licence, freshness**.

**User trust and safety:** ভুল চার্জকে নিশ্চিত প্রতারণা বলা নয়। Advanced panel থাকবে, কিন্তু সাধারণ ব্যবহারকারীর জন্য তিন ধাপের flow; evidence/uncertainty panel যুক্ত থাকবে।

**Central Admin module panel:** configure localized title/about/help/input schema/upload limits/report template/theme accents and navigation, model choice/version, source permission state, dataset import preview, reviewer queue, QA scores, per-tool quota/retention, moderation, canary rollout, feature-disable switch, error logs and version history. All server-authorized.

**Release acceptance:** valid original or approved test input produces stored owner-only outcome with evidence; real model/rule tested; invalid image/file/text/numbers fail gracefully; BN/EN; mobile layout; download/delete; private test and no unsupported claim.

### 08 · CareJourney AI — Healthcare Support

**Status:** Planned V5 project — integrate · **Single-domain URL:** `/tools/carejourney-ai` · **Shared workspace:** `/workspace` · **Central Admin configuration:** `/admin/tools/carejourney-ai`.

**About (বাংলাদেশে কী সমস্যা সমাধান):** ব্যবহারকারী সহজে **ডাক্তারের নির্দেশনা টেক্সট/PDF, সম্মতিসহ অডিও** দিলে **Follow-up checklist, বোঝার মতো সারাংশ** পাবে। এই টুলের নিজস্ব visual identity এবং value feature হলো **পরবর্তী ভিজিটের প্রস্তুতি কার্ড**। এটি ৩৪টি টুলের generic wrapper হবে না।

**User screen:** simple About + safety promise → picture/text/audio/numeric input choice (only supported modalities, CSV optional not mandatory) → privacy consent → extracted preview/correction → processing progress and model status → primary Bangla result in ≤3 clear main actions → expandable evidence/source timestamps, download/share privately and delete. Design input/output forms for elderly and low-data mobile conditions.

**Model work that must actually run:** medical OCR + transcription + grounded extraction. Candidate checkpoints: **openai/whisper-small; Tesseract OCR with ben+eng language packs; sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2**. Execute at least one real relevant pipeline, write model card, version, test cases and fallback, and use deterministic rules explicitly named as rules. Include Bangladesh-specific test examples, confidence and error evaluation. **Never label an unrun model “integrated”.**

**Data plan:** private user uploads only. Relevant references (NOT automatically licensed training datasets):
- DGHS — Bangladesh Facility Registry: https://hris.mohfw.gov.bd/public/facility-registry/ — **candidate; confirm access, dataset-specific licence, freshness**.
- DGHS — official health services portal: https://dghs.gov.bd/ — **candidate; confirm access, dataset-specific licence, freshness**.
- DGDA — Directorate General of Drug Administration: https://dgda.gov.bd/ — **candidate; confirm access, dataset-specific licence, freshness**.

**User trust and safety:** নতুন ডোজ/রোগ নির্ণয় নয়। Advanced panel থাকবে, কিন্তু সাধারণ ব্যবহারকারীর জন্য তিন ধাপের flow; evidence/uncertainty panel যুক্ত থাকবে।

**Central Admin module panel:** configure localized title/about/help/input schema/upload limits/report template/theme accents and navigation, model choice/version, source permission state, dataset import preview, reviewer queue, QA scores, per-tool quota/retention, moderation, canary rollout, feature-disable switch, error logs and version history. All server-authorized.

**Release acceptance:** valid original or approved test input produces stored owner-only outcome with evidence; real model/rule tested; invalid image/file/text/numbers fail gracefully; BN/EN; mobile layout; download/delete; private test and no unsupported claim.

### 09 · GoliCoach AI — Sports

**Status:** Planned V5 project — integrate · **Single-domain URL:** `/tools/golicoach-ai` · **Shared workspace:** `/workspace` · **Central Admin configuration:** `/admin/tools/golicoach-ai`.

**About (বাংলাদেশে কী সমস্যা সমাধান):** ব্যবহারকারী সহজে **ক্রিকেট অনুশীলনের ছোট ভিডিও** দিলে **ফুটওয়ার্ক ও বডি পোজ পরিবর্তন ট্র্যাক** পাবে। এই টুলের নিজস্ব visual identity এবং value feature হলো **ফ্রেমভিত্তিক pose overlay এবং drill তালিকা**। এটি ৩৪টি টুলের generic wrapper হবে না।

**User screen:** simple About + safety promise → picture/text/audio/numeric input choice (only supported modalities, CSV optional not mandatory) → privacy consent → extracted preview/correction → processing progress and model status → primary Bangla result in ≤3 clear main actions → expandable evidence/source timestamps, download/share privately and delete. Design input/output forms for elderly and low-data mobile conditions.

**Model work that must actually run:** pose estimation + motion-series comparison. Candidate checkpoints: **MediaPipe Pose Landmark model; sklearn.ensemble.IsolationForest**. Execute at least one real relevant pipeline, write model card, version, test cases and fallback, and use deterministic rules explicitly named as rules. Include Bangladesh-specific test examples, confidence and error evaluation. **Never label an unrun model “integrated”.**

**Data plan:** consented practice video. Relevant references (NOT automatically licensed training datasets):
- BD Sports-10 — Bangladesh traditional sports video dataset: https://data.mendeley.com/datasets/rnh3x48nfb/2 — **candidate; confirm access, dataset-specific licence, freshness**.
- Cric-360 — cricket broadcast ground frames (not Bangladesh-specific): https://huggingface.co/datasets/sarimshahzad/Cric-360 — **candidate; confirm access, dataset-specific licence, freshness**.
- Bangladesh Open Data — searchable datasets: https://data.gov.bd/dataset — **candidate; confirm access, dataset-specific licence, freshness**.

**User trust and safety:** এক ভিডিওতে দক্ষতা বা injury diagnosis নয়। Advanced panel থাকবে, কিন্তু সাধারণ ব্যবহারকারীর জন্য তিন ধাপের flow; evidence/uncertainty panel যুক্ত থাকবে।

**Central Admin module panel:** configure localized title/about/help/input schema/upload limits/report template/theme accents and navigation, model choice/version, source permission state, dataset import preview, reviewer queue, QA scores, per-tool quota/retention, moderation, canary rollout, feature-disable switch, error logs and version history. All server-authorized.

**Release acceptance:** valid original or approved test input produces stored owner-only outcome with evidence; real model/rule tested; invalid image/file/text/numbers fail gracefully; BN/EN; mobile layout; download/delete; private test and no unsupported claim.

### 10 · DokanLens AI — Retail

**Status:** ALREADY BUILT — migrate conservatively · **Single-domain URL:** `/tools/dokanlens-ai` · **Shared workspace:** `/workspace` · **Central Admin configuration:** `/admin/tools/dokanlens-ai`.

**About (বাংলাদেশে কী সমস্যা সমাধান):** ব্যবহারকারী সহজে **তাকের ছবি, বারকোড ও manual stock entry** দিলে **স্টক তালিকা, মেয়াদ সতর্কতা ও reorder suggestions** পাবে। এই টুলের নিজস্ব visual identity এবং value feature হলো **মোবাইল স্টক স্ক্যানার ও low-stock board**। এটি ৩৪টি টুলের generic wrapper হবে না।

**User screen:** simple About + safety promise → picture/text/audio/numeric input choice (only supported modalities, CSV optional not mandatory) → privacy consent → extracted preview/correction → processing progress and model status → primary Bangla result in ≤3 clear main actions → expandable evidence/source timestamps, download/share privately and delete. Design input/output forms for elderly and low-data mobile conditions.

**Model work that must actually run:** OCR + product matching + demand forecasting. Candidate checkpoints: **Tesseract OCR with ben+eng language packs; torchvision pretrained MobileNetV3/EfficientNet-B0 feature backbone; sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2**. Execute at least one real relevant pipeline, write model card, version, test cases and fallback, and use deterministic rules explicitly named as rules. Include Bangladesh-specific test examples, confidence and error evaluation. **Never label an unrun model “integrated”.**

**Data plan:** merchant-owned catalog, voluntary transactions. Relevant references (NOT automatically licensed training datasets):
- BSTI mandatory product categories: https://bsti.portal.gov.bd/pages/static-pages/6922dcba933eb65569e11af8 — **candidate; confirm access, dataset-specific licence, freshness**.
- BBS Economic Census: https://bbs.gov.bd/ — **candidate; confirm access, dataset-specific licence, freshness**.
- Bangladesh Open Data: https://data.gov.bd/dataset — **candidate; confirm access, dataset-specific licence, freshness**.

**User trust and safety:** অদেখা স্টকের পরিমাণ অনুমান নয়। Advanced panel থাকবে, কিন্তু সাধারণ ব্যবহারকারীর জন্য তিন ধাপের flow; evidence/uncertainty panel যুক্ত থাকবে।

**Central Admin module panel:** configure localized title/about/help/input schema/upload limits/report template/theme accents and navigation, model choice/version, source permission state, dataset import preview, reviewer queue, QA scores, per-tool quota/retention, moderation, canary rollout, feature-disable switch, error logs and version history. All server-authorized.

**Release acceptance:** valid original or approved test input produces stored owner-only outcome with evidence; real model/rule tested; invalid image/file/text/numbers fail gracefully; BN/EN; mobile layout; download/delete; private test and no unsupported claim.

### 11 · BazarCompare AI — Shopping & Expenses

**Status:** ALREADY BUILT — migrate conservatively · **Single-domain URL:** `/tools/bazarcompare-ai` · **Shared workspace:** `/workspace` · **Central Admin configuration:** `/admin/tools/bazarcompare-ai`.

**About (বাংলাদেশে কী সমস্যা সমাধান):** ব্যবহারকারী সহজে **বাজারের দামের ছবি, manually entered prices, shopping list** দিলে **একক দরের তুলনা ও বাজেট পরিকল্পনা** পাবে। এই টুলের নিজস্ব visual identity এবং value feature হলো **তিন বাজারের তুলনা ও saved basket**। এটি ৩৪টি টুলের generic wrapper হবে না।

**User screen:** simple About + safety promise → picture/text/audio/numeric input choice (only supported modalities, CSV optional not mandatory) → privacy consent → extracted preview/correction → processing progress and model status → primary Bangla result in ≤3 clear main actions → expandable evidence/source timestamps, download/share privately and delete. Design input/output forms for elderly and low-data mobile conditions.

**Model work that must actually run:** Bangla OCR + unit normalization + price outlier detection. Candidate checkpoints: **Tesseract OCR with ben+eng language packs; sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2; scikit-learn HistGradientBoostingRegressor / RandomForestRegressor**. Execute at least one real relevant pipeline, write model card, version, test cases and fallback, and use deterministic rules explicitly named as rules. Include Bangladesh-specific test examples, confidence and error evaluation. **Never label an unrun model “integrated”.**

**Data plan:** date-stamped DAM refs + consented local prices. Relevant references (NOT automatically licensed training datasets):
- Department of Agricultural Marketing: https://market.dam.gov.bd/?L=E — **candidate; confirm access, dataset-specific licence, freshness**.
- DAM commodity-wise report: https://market.dam.gov.bd/commodity_wise_report/damweb/PublicPortal/ — **candidate; confirm access, dataset-specific licence, freshness**.
- Trading Corporation of Bangladesh daily retail prices: https://tcb.gov.bd/pages/daily-rmps — **candidate; confirm access, dataset-specific licence, freshness**.

**User trust and safety:** সোর্স-তারিখ ছাড়া live market price নয়। Advanced panel থাকবে, কিন্তু সাধারণ ব্যবহারকারীর জন্য তিন ধাপের flow; evidence/uncertainty panel যুক্ত থাকবে।

**Central Admin module panel:** configure localized title/about/help/input schema/upload limits/report template/theme accents and navigation, model choice/version, source permission state, dataset import preview, reviewer queue, QA scores, per-tool quota/retention, moderation, canary rollout, feature-disable switch, error logs and version history. All server-authorized.

**Release acceptance:** valid original or approved test input produces stored owner-only outcome with evidence; real model/rule tested; invalid image/file/text/numbers fail gracefully; BN/EN; mobile layout; download/delete; private test and no unsupported claim.

### 12 · HomeHazard AI — Housing & Home

**Status:** Planned V5 project — integrate · **Single-domain URL:** `/tools/homehazard-ai` · **Shared workspace:** `/workspace` · **Central Admin configuration:** `/admin/tools/homehazard-ai`.

**About (বাংলাদেশে কী সমস্যা সমাধান):** ব্যবহারকারী সহজে **দেয়ালের ফাটল/স্যাঁতসেঁতে অংশের ছবি** দিলে **দৃশ্যমান সমস্যা, প্রাথমিক নিরাপত্তা গাইড** পাবে। এই টুলের নিজস্ব visual identity এবং value feature হলো **রুমভিত্তিক সমস্যা ট্র্যাকার**। এটি ৩৪টি টুলের generic wrapper হবে না।

**User screen:** simple About + safety promise → picture/text/audio/numeric input choice (only supported modalities, CSV optional not mandatory) → privacy consent → extracted preview/correction → processing progress and model status → primary Bangla result in ≤3 clear main actions → expandable evidence/source timestamps, download/share privately and delete. Design input/output forms for elderly and low-data mobile conditions.

**Model work that must actually run:** visual classification + retrieval-based guidance. Candidate checkpoints: **torchvision pretrained MobileNetV3/EfficientNet-B0 feature backbone; sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2**. Execute at least one real relevant pipeline, write model card, version, test cases and fallback, and use deterministic rules explicitly named as rules. Include Bangladesh-specific test examples, confidence and error evaluation. **Never label an unrun model “integrated”.**

**Data plan:** consented household images. Relevant references (NOT automatically licensed training datasets):
- BAMIS — agricultural weather and advisories: https://www.bamis.gov.bd/en/home/ — **candidate; confirm access, dataset-specific licence, freshness**.
- Bangladesh Open Data — searchable datasets: https://data.gov.bd/dataset — **candidate; confirm access, dataset-specific licence, freshness**.
- FFWC — flood and river hydrological information: https://ffwc.gov.bd/ — **candidate; confirm access, dataset-specific licence, freshness**.

**User trust and safety:** নিরাপদ ভবনের সার্টিফিকেট নয়। Advanced panel থাকবে, কিন্তু সাধারণ ব্যবহারকারীর জন্য তিন ধাপের flow; evidence/uncertainty panel যুক্ত থাকবে।

**Central Admin module panel:** configure localized title/about/help/input schema/upload limits/report template/theme accents and navigation, model choice/version, source permission state, dataset import preview, reviewer queue, QA scores, per-tool quota/retention, moderation, canary rollout, feature-disable switch, error logs and version history. All server-authorized.

**Release acceptance:** valid original or approved test input produces stored owner-only outcome with evidence; real model/rule tested; invalid image/file/text/numbers fail gracefully; BN/EN; mobile layout; download/delete; private test and no unsupported claim.

### 13 · WasteWise BD — Environment & Climate

**Status:** Planned V5 project — integrate · **Single-domain URL:** `/tools/wastewise-bd` · **Shared workspace:** `/workspace` · **Central Admin configuration:** `/admin/tools/wastewise-bd`.

**About (বাংলাদেশে কী সমস্যা সমাধান):** ব্যবহারকারী সহজে **বর্জ্যের ছবি অথবা নাম** দিলে **বর্জ্যের ধরন ও স্থানীয় উপযুক্ত নিষ্পত্তির ধারণা** পাবে। এই টুলের নিজস্ব visual identity এবং value feature হলো **Sorting Assistant ও recycling habit tracker**। এটি ৩৪টি টুলের generic wrapper হবে না।

**User screen:** simple About + safety promise → picture/text/audio/numeric input choice (only supported modalities, CSV optional not mandatory) → privacy consent → extracted preview/correction → processing progress and model status → primary Bangla result in ≤3 clear main actions → expandable evidence/source timestamps, download/share privately and delete. Design input/output forms for elderly and low-data mobile conditions.

**Model work that must actually run:** image classification + recycling RAG. Candidate checkpoints: **torchvision pretrained MobileNetV3/EfficientNet-B0 feature backbone; sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2**. Execute at least one real relevant pipeline, write model card, version, test cases and fallback, and use deterministic rules explicitly named as rules. Include Bangladesh-specific test examples, confidence and error evaluation. **Never label an unrun model “integrated”.**

**Data plan:** community waste photos opt-in. Relevant references (NOT automatically licensed training datasets):
- Bangladesh Open Data — searchable datasets: https://data.gov.bd/dataset — **candidate; confirm access, dataset-specific licence, freshness**.
- OpenStreetMap — Bangladesh Geofabrik extract: https://download.geofabrik.de/asia/bangladesh.html — **candidate; confirm access, dataset-specific licence, freshness**.
- OpenStreetMap — license and attribution: https://www.openstreetmap.org/copyright — **candidate; confirm access, dataset-specific licence, freshness**.

**User trust and safety:** পুনর্ব্যবহার কেন্দ্রের অবস্থান যাচাই ছাড়া নয়। Advanced panel থাকবে, কিন্তু সাধারণ ব্যবহারকারীর জন্য তিন ধাপের flow; evidence/uncertainty panel যুক্ত থাকবে।

**Central Admin module panel:** configure localized title/about/help/input schema/upload limits/report template/theme accents and navigation, model choice/version, source permission state, dataset import preview, reviewer queue, QA scores, per-tool quota/retention, moderation, canary rollout, feature-disable switch, error logs and version history. All server-authorized.

**Release acceptance:** valid original or approved test input produces stored owner-only outcome with evidence; real model/rule tested; invalid image/file/text/numbers fail gracefully; BN/EN; mobile layout; download/delete; private test and no unsupported claim.

### 14 · WorkSafe Vision AI — Civic, Worker Rights & Legal

**Status:** Planned V5 project — integrate · **Single-domain URL:** `/tools/worksafe-vision-ai` · **Shared workspace:** `/workspace` · **Central Admin configuration:** `/admin/tools/worksafe-vision-ai`.

**About (বাংলাদেশে কী সমস্যা সমাধান):** ব্যবহারকারী সহজে **কারখানা/নির্মাণস্থলের অনুমতিপ্রাপ্ত ছবি** দিলে **দৃশ্যমান ঝুঁকি তালিকা ও করণীয়** পাবে। এই টুলের নিজস্ব visual identity এবং value feature হলো **Annotated site-check checklist**। এটি ৩৪টি টুলের generic wrapper হবে না।

**User screen:** simple About + safety promise → picture/text/audio/numeric input choice (only supported modalities, CSV optional not mandatory) → privacy consent → extracted preview/correction → processing progress and model status → primary Bangla result in ≤3 clear main actions → expandable evidence/source timestamps, download/share privately and delete. Design input/output forms for elderly and low-data mobile conditions.

**Model work that must actually run:** PPE and hazard object detector + safety RAG. Candidate checkpoints: **torchvision pretrained MobileNetV3/EfficientNet-B0 feature backbone; sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2**. Execute at least one real relevant pipeline, write model card, version, test cases and fallback, and use deterministic rules explicitly named as rules. Include Bangladesh-specific test examples, confidence and error evaluation. **Never label an unrun model “integrated”.**

**Data plan:** consented workplace images. Relevant references (NOT automatically licensed training datasets):
- Laws of Bangladesh — legislation search: https://bdlaws.minlaw.gov.bd/ — **candidate; confirm access, dataset-specific licence, freshness**.
- Bangladesh Open Data — searchable datasets: https://data.gov.bd/dataset — **candidate; confirm access, dataset-specific licence, freshness**.
- DGHS — official health services portal: https://dghs.gov.bd/ — **candidate; confirm access, dataset-specific licence, freshness**.

**User trust and safety:** কোনো আইনি safety inspection-এর বিকল্প নয়। Advanced panel থাকবে, কিন্তু সাধারণ ব্যবহারকারীর জন্য তিন ধাপের flow; evidence/uncertainty panel যুক্ত থাকবে।

**Central Admin module panel:** configure localized title/about/help/input schema/upload limits/report template/theme accents and navigation, model choice/version, source permission state, dataset import preview, reviewer queue, QA scores, per-tool quota/retention, moderation, canary rollout, feature-disable switch, error logs and version history. All server-authorized.

**Release acceptance:** valid original or approved test input produces stored owner-only outcome with evidence; real model/rule tested; invalid image/file/text/numbers fail gracefully; BN/EN; mobile layout; download/delete; private test and no unsupported claim.

### 15 · ClinicCompass BD — Healthcare Support

**Status:** Planned V5 project — integrate · **Single-domain URL:** `/tools/cliniccompass-bd` · **Shared workspace:** `/workspace` · **Central Admin configuration:** `/admin/tools/cliniccompass-bd`.

**About (বাংলাদেশে কী সমস্যা সমাধান):** ব্যবহারকারী সহজে **অবস্থান, সুবিধার ধরন, সেবা নির্বাচন** দিলে **যাচাইকৃত চিকিৎসাকেন্দ্র খোঁজা ও ফোন/ঠিকানা** পাবে। এই টুলের নিজস্ব visual identity এবং value feature হলো **ক্লিনিক ফিল্টার ও প্রস্তুতি চেকলিস্ট**। এটি ৩৪টি টুলের generic wrapper হবে না।

**User screen:** simple About + safety promise → picture/text/audio/numeric input choice (only supported modalities, CSV optional not mandatory) → privacy consent → extracted preview/correction → processing progress and model status → primary Bangla result in ≤3 clear main actions → expandable evidence/source timestamps, download/share privately and delete. Design input/output forms for elderly and low-data mobile conditions.

**Model work that must actually run:** verified registry search + semantic matching. Candidate checkpoints: **sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2**. Execute at least one real relevant pipeline, write model card, version, test cases and fallback, and use deterministic rules explicitly named as rules. Include Bangladesh-specific test examples, confidence and error evaluation. **Never label an unrun model “integrated”.**

**Data plan:** DGHS health facility registry. Relevant references (NOT automatically licensed training datasets):
- DGHS — Bangladesh Facility Registry: https://hris.mohfw.gov.bd/public/facility-registry/ — **candidate; confirm access, dataset-specific licence, freshness**.
- DGHS — official health services portal: https://dghs.gov.bd/ — **candidate; confirm access, dataset-specific licence, freshness**.
- OpenStreetMap — Bangladesh Geofabrik extract: https://download.geofabrik.de/asia/bangladesh.html — **candidate; confirm access, dataset-specific licence, freshness**.

**User trust and safety:** হাসপাতাল এখন খোলা বা আসন খালি বলে দাবি নয়। Advanced panel থাকবে, কিন্তু সাধারণ ব্যবহারকারীর জন্য তিন ধাপের flow; evidence/uncertainty panel যুক্ত থাকবে।

**Central Admin module panel:** configure localized title/about/help/input schema/upload limits/report template/theme accents and navigation, model choice/version, source permission state, dataset import preview, reviewer queue, QA scores, per-tool quota/retention, moderation, canary rollout, feature-disable switch, error logs and version history. All server-authorized.

**Release acceptance:** valid original or approved test input produces stored owner-only outcome with evidence; real model/rule tested; invalid image/file/text/numbers fail gracefully; BN/EN; mobile layout; download/delete; private test and no unsupported claim.

### 16 · LabTrend BD — Healthcare Support

**Status:** Planned V5 project — integrate · **Single-domain URL:** `/tools/labtrend-bd` · **Shared workspace:** `/workspace` · **Central Admin configuration:** `/admin/tools/labtrend-bd`.

**About (বাংলাদেশে কী সমস্যা সমাধান):** ব্যবহারকারী সহজে **ল্যাব রিপোর্টের ছবি/PDF ও টেস্টের তারিখ** দিলে **তারিখ অনুযায়ী মানের চার্ট এবং পরীক্ষার ব্যাখ্যা** পাবে। এই টুলের নিজস্ব visual identity এবং value feature হলো **প্রতি টেস্টের ট্রেন্ড ও রিপোর্ট মিলানো**। এটি ৩৪টি টুলের generic wrapper হবে না।

**User screen:** simple About + safety promise → picture/text/audio/numeric input choice (only supported modalities, CSV optional not mandatory) → privacy consent → extracted preview/correction → processing progress and model status → primary Bangla result in ≤3 clear main actions → expandable evidence/source timestamps, download/share privately and delete. Design input/output forms for elderly and low-data mobile conditions.

**Model work that must actually run:** OCR + entity/unit parser + longitudinal trend. Candidate checkpoints: **Tesseract OCR with ben+eng language packs; sklearn.ensemble.IsolationForest**. Execute at least one real relevant pipeline, write model card, version, test cases and fallback, and use deterministic rules explicitly named as rules. Include Bangladesh-specific test examples, confidence and error evaluation. **Never label an unrun model “integrated”.**

**Data plan:** private user lab reports; reference intervals manual. Relevant references (NOT automatically licensed training datasets):
- DGHS — official health services portal: https://dghs.gov.bd/ — **candidate; confirm access, dataset-specific licence, freshness**.
- DGHS — Bangladesh Facility Registry: https://hris.mohfw.gov.bd/public/facility-registry/ — **candidate; confirm access, dataset-specific licence, freshness**.
- DGDA — Directorate General of Drug Administration: https://dgda.gov.bd/ — **candidate; confirm access, dataset-specific licence, freshness**.

**User trust and safety:** ডায়াগনসিস নয়; ল্যাবভেদে রেফারেন্স রেঞ্জ আলাদা। Advanced panel থাকবে, কিন্তু সাধারণ ব্যবহারকারীর জন্য তিন ধাপের flow; evidence/uncertainty panel যুক্ত থাকবে।

**Central Admin module panel:** configure localized title/about/help/input schema/upload limits/report template/theme accents and navigation, model choice/version, source permission state, dataset import preview, reviewer queue, QA scores, per-tool quota/retention, moderation, canary rollout, feature-disable switch, error logs and version history. All server-authorized.

**Release acceptance:** valid original or approved test input produces stored owner-only outcome with evidence; real model/rule tested; invalid image/file/text/numbers fail gracefully; BN/EN; mobile layout; download/delete; private test and no unsupported claim.

### 17 · DoseClear BD — Healthcare Support

**Status:** Planned V5 project — integrate · **Single-domain URL:** `/tools/doseclear-bd` · **Shared workspace:** `/workspace` · **Central Admin configuration:** `/admin/tools/doseclear-bd`.

**About (বাংলাদেশে কী সমস্যা সমাধান):** ব্যবহারকারী সহজে **প্রেসক্রিপশন ও ওষুধের লেখা** দিলে **পড়া যায় এমন নির্দেশনার plain-language summary** পাবে। এই টুলের নিজস্ব visual identity এবং value feature হলো **ওষুধের নির্দেশনা বোঝার কার্ড**। এটি ৩৪টি টুলের generic wrapper হবে না।

**User screen:** simple About + safety promise → picture/text/audio/numeric input choice (only supported modalities, CSV optional not mandatory) → privacy consent → extracted preview/correction → processing progress and model status → primary Bangla result in ≤3 clear main actions → expandable evidence/source timestamps, download/share privately and delete. Design input/output forms for elderly and low-data mobile conditions.

**Model work that must actually run:** handwriting OCR + entity extraction + confidence gate. Candidate checkpoints: **Tesseract OCR with ben+eng language packs; sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2**. Execute at least one real relevant pipeline, write model card, version, test cases and fallback, and use deterministic rules explicitly named as rules. Include Bangladesh-specific test examples, confidence and error evaluation. **Never label an unrun model “integrated”.**

**Data plan:** consented prescriptions, approved drug glossary. Relevant references (NOT automatically licensed training datasets):
- DGDA — Directorate General of Drug Administration: https://dgda.gov.bd/ — **candidate; confirm access, dataset-specific licence, freshness**.
- DGHS — official health services portal: https://dghs.gov.bd/ — **candidate; confirm access, dataset-specific licence, freshness**.
- DGHS — Bangladesh Facility Registry: https://hris.mohfw.gov.bd/public/facility-registry/ — **candidate; confirm access, dataset-specific licence, freshness**.

**User trust and safety:** অস্পষ্ট ডোজ অনুমান/বদল নয়। Advanced panel থাকবে, কিন্তু সাধারণ ব্যবহারকারীর জন্য তিন ধাপের flow; evidence/uncertainty panel যুক্ত থাকবে।

**Central Admin module panel:** configure localized title/about/help/input schema/upload limits/report template/theme accents and navigation, model choice/version, source permission state, dataset import preview, reviewer queue, QA scores, per-tool quota/retention, moderation, canary rollout, feature-disable switch, error logs and version history. All server-authorized.

**Release acceptance:** valid original or approved test input produces stored owner-only outcome with evidence; real model/rule tested; invalid image/file/text/numbers fail gracefully; BN/EN; mobile layout; download/delete; private test and no unsupported claim.

### 18 · VaccinePath BD — Healthcare Support

**Status:** Planned V5 project — integrate · **Single-domain URL:** `/tools/vaccinepath-bd` · **Shared workspace:** `/workspace` · **Central Admin configuration:** `/admin/tools/vaccinepath-bd`.

**About (বাংলাদেশে কী সমস্যা সমাধান):** ব্যবহারকারী সহজে **টিকার কার্ডের ছবি বা হাতে দেওয়া তারিখ** দিলে **রেকর্ড টাইমলাইন ও অনুমোদিত রুটিনের reference** পাবে। এই টুলের নিজস্ব visual identity এবং value feature হলো **টিকা ক্যালেন্ডার ও missing info prompt**। এটি ৩৪টি টুলের generic wrapper হবে না।

**User screen:** simple About + safety promise → picture/text/audio/numeric input choice (only supported modalities, CSV optional not mandatory) → privacy consent → extracted preview/correction → processing progress and model status → primary Bangla result in ≤3 clear main actions → expandable evidence/source timestamps, download/share privately and delete. Design input/output forms for elderly and low-data mobile conditions.

**Model work that must actually run:** OCR + rules engine + source-backed RAG. Candidate checkpoints: **sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2; rank-bm25 lexical retrieval**. Execute at least one real relevant pipeline, write model card, version, test cases and fallback, and use deterministic rules explicitly named as rules. Include Bangladesh-specific test examples, confidence and error evaluation. **Never label an unrun model “integrated”.**

**Data plan:** official vaccine schedules plus private logs. Relevant references (NOT automatically licensed training datasets):
- DGHS — official health services portal: https://dghs.gov.bd/ — **candidate; confirm access, dataset-specific licence, freshness**.
- DGHS — Bangladesh Facility Registry: https://hris.mohfw.gov.bd/public/facility-registry/ — **candidate; confirm access, dataset-specific licence, freshness**.
- Bangladesh Open Data — searchable datasets: https://data.gov.bd/dataset — **candidate; confirm access, dataset-specific licence, freshness**.

**User trust and safety:** যোগ্যতা/ডোজের চূড়ান্ত নির্দেশ নয়। Advanced panel থাকবে, কিন্তু সাধারণ ব্যবহারকারীর জন্য তিন ধাপের flow; evidence/uncertainty panel যুক্ত থাকবে।

**Central Admin module panel:** configure localized title/about/help/input schema/upload limits/report template/theme accents and navigation, model choice/version, source permission state, dataset import preview, reviewer queue, QA scores, per-tool quota/retention, moderation, canary rollout, feature-disable switch, error logs and version history. All server-authorized.

**Release acceptance:** valid original or approved test input produces stored owner-only outcome with evidence; real model/rule tested; invalid image/file/text/numbers fail gracefully; BN/EN; mobile layout; download/delete; private test and no unsupported claim.

### 19 · MaternalRoute BD — Healthcare Support

**Status:** Planned V5 project — integrate · **Single-domain URL:** `/tools/maternalroute-bd` · **Shared workspace:** `/workspace` · **Central Admin configuration:** `/admin/tools/maternalroute-bd`.

**About (বাংলাদেশে কী সমস্যা সমাধান):** ব্যবহারকারী সহজে **গর্ভাবস্থার সাধারণ তথ্য, ভিজিটের তারিখ, পছন্দ** দিলে **ভিজিটের প্রস্তুতি ও বিপদের লক্ষণের শিক্ষা** পাবে। এই টুলের নিজস্ব visual identity এবং value feature হলো **প্রসব-পূর্ব ভিজিটের জার্নি**। এটি ৩৪টি টুলের generic wrapper হবে না।

**User screen:** simple About + safety promise → picture/text/audio/numeric input choice (only supported modalities, CSV optional not mandatory) → privacy consent → extracted preview/correction → processing progress and model status → primary Bangla result in ≤3 clear main actions → expandable evidence/source timestamps, download/share privately and delete. Design input/output forms for elderly and low-data mobile conditions.

**Model work that must actually run:** triage-safe rule engine + guideline RAG. Candidate checkpoints: **sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2; rank-bm25 lexical retrieval**. Execute at least one real relevant pipeline, write model card, version, test cases and fallback, and use deterministic rules explicitly named as rules. Include Bangladesh-specific test examples, confidence and error evaluation. **Never label an unrun model “integrated”.**

**Data plan:** authorized maternal guideline text. Relevant references (NOT automatically licensed training datasets):
- DGHS — official health services portal: https://dghs.gov.bd/ — **candidate; confirm access, dataset-specific licence, freshness**.
- DGHS — Bangladesh Facility Registry: https://hris.mohfw.gov.bd/public/facility-registry/ — **candidate; confirm access, dataset-specific licence, freshness**.
- Bangladesh Open Data — searchable datasets: https://data.gov.bd/dataset — **candidate; confirm access, dataset-specific licence, freshness**.

**User trust and safety:** উচ্চ ঝুঁকির লক্ষণে জরুরি স্বাস্থ্যসেবা পরামর্শ। Advanced panel থাকবে, কিন্তু সাধারণ ব্যবহারকারীর জন্য তিন ধাপের flow; evidence/uncertainty panel যুক্ত থাকবে।

**Central Admin module panel:** configure localized title/about/help/input schema/upload limits/report template/theme accents and navigation, model choice/version, source permission state, dataset import preview, reviewer queue, QA scores, per-tool quota/retention, moderation, canary rollout, feature-disable switch, error logs and version history. All server-authorized.

**Release acceptance:** valid original or approved test input produces stored owner-only outcome with evidence; real model/rule tested; invalid image/file/text/numbers fail gracefully; BN/EN; mobile layout; download/delete; private test and no unsupported claim.

### 20 · DengueSignal BD — Healthcare Support

**Status:** Planned V5 project — integrate · **Single-domain URL:** `/tools/denguesignal-bd` · **Shared workspace:** `/workspace` · **Central Admin configuration:** `/admin/tools/denguesignal-bd`.

**About (বাংলাদেশে কী সমস্যা সমাধান):** ব্যবহারকারী সহজে **জেলা, সময়সীমা ও সরকারি aggregation** দিলে **এলাকার প্রকাশিত ডেঙ্গু পরিস্থিতি ও ট্রেন্ড** পাবে। এই টুলের নিজস্ব visual identity এবং value feature হলো **টাইমলাইন ও source timestamp**। এটি ৩৪টি টুলের generic wrapper হবে না।

**User screen:** simple About + safety promise → picture/text/audio/numeric input choice (only supported modalities, CSV optional not mandatory) → privacy consent → extracted preview/correction → processing progress and model status → primary Bangla result in ≤3 clear main actions → expandable evidence/source timestamps, download/share privately and delete. Design input/output forms for elderly and low-data mobile conditions.

**Model work that must actually run:** temporal forecasting with calibration + outbreak reporting. Candidate checkpoints: **statsmodels ExponentialSmoothing baseline + prediction intervals when validated; scikit-learn HistGradientBoostingRegressor / RandomForestRegressor; sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2**. Execute at least one real relevant pipeline, write model card, version, test cases and fallback, and use deterministic rules explicitly named as rules. Include Bangladesh-specific test examples, confidence and error evaluation. **Never label an unrun model “integrated”.**

**Data plan:** DGHS aggregated dashboard snapshots by permission. Relevant references (NOT automatically licensed training datasets):
- DGHS dengue dynamic dashboard: https://dashboard.dghs.gov.bd/pages/heoc_dengue_v1.php — **candidate; confirm access, dataset-specific licence, freshness**.
- DGHS — Dengue clinical guidelines: https://dghs.gov.bd/pages/static-pages/6922e05c933eb65569e26afe — **candidate; confirm access, dataset-specific licence, freshness**.
- Bangladesh Open Data — searchable datasets: https://data.gov.bd/dataset — **candidate; confirm access, dataset-specific licence, freshness**.

**User trust and safety:** ব্যক্তির রোগ ঝুঁকির নির্ভুল ভবিষ্যদ্বাণী নয়। Advanced panel থাকবে, কিন্তু সাধারণ ব্যবহারকারীর জন্য তিন ধাপের flow; evidence/uncertainty panel যুক্ত থাকবে।

**Central Admin module panel:** configure localized title/about/help/input schema/upload limits/report template/theme accents and navigation, model choice/version, source permission state, dataset import preview, reviewer queue, QA scores, per-tool quota/retention, moderation, canary rollout, feature-disable switch, error logs and version history. All server-authorized.

**Release acceptance:** valid original or approved test input produces stored owner-only outcome with evidence; real model/rule tested; invalid image/file/text/numbers fail gracefully; BN/EN; mobile layout; download/delete; private test and no unsupported claim.

### 21 · RentalFair BD — Housing & Home

**Status:** Planned V5 project — integrate · **Single-domain URL:** `/tools/rentalfair-bd` · **Shared workspace:** `/workspace` · **Central Admin configuration:** `/admin/tools/rentalfair-bd`.

**About (বাংলাদেশে কী সমস্যা সমাধান):** ব্যবহারকারী সহজে **ভাড়ার মূল্য, চুক্তি, সুবিধা ও এলাকা** দিলে **মাসিক খরচ, চুক্তির প্রশ্ন, তুলনা** পাবে। এই টুলের নিজস্ব visual identity এবং value feature হলো **ভাড়া তুলনা ও tenancy checklist**। এটি ৩৪টি টুলের generic wrapper হবে না।

**User screen:** simple About + safety promise → picture/text/audio/numeric input choice (only supported modalities, CSV optional not mandatory) → privacy consent → extracted preview/correction → processing progress and model status → primary Bangla result in ≤3 clear main actions → expandable evidence/source timestamps, download/share privately and delete. Design input/output forms for elderly and low-data mobile conditions.

**Model work that must actually run:** NLP clause review + unit cost comparator. Candidate checkpoints: **Tesseract OCR with ben+eng language packs; sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2; scikit-learn HistGradientBoostingRegressor / RandomForestRegressor**. Execute at least one real relevant pipeline, write model card, version, test cases and fallback, and use deterministic rules explicitly named as rules. Include Bangladesh-specific test examples, confidence and error evaluation. **Never label an unrun model “integrated”.**

**Data plan:** voluntary anonymized rent listings. Relevant references (NOT automatically licensed training datasets):
- Laws of Bangladesh — legislation search: https://bdlaws.minlaw.gov.bd/ — **candidate; confirm access, dataset-specific licence, freshness**.
- Bangladesh Open Data — searchable datasets: https://data.gov.bd/dataset — **candidate; confirm access, dataset-specific licence, freshness**.
- National Consumer Rights Protection — complaints and rules: https://dncrp.gov.bd/ — **candidate; confirm access, dataset-specific licence, freshness**.

**User trust and safety:** বাজারের ন্যায্য ভাড়া ঘোষণা নয়। Advanced panel থাকবে, কিন্তু সাধারণ ব্যবহারকারীর জন্য তিন ধাপের flow; evidence/uncertainty panel যুক্ত থাকবে।

**Central Admin module panel:** configure localized title/about/help/input schema/upload limits/report template/theme accents and navigation, model choice/version, source permission state, dataset import preview, reviewer queue, QA scores, per-tool quota/retention, moderation, canary rollout, feature-disable switch, error logs and version history. All server-authorized.

**Release acceptance:** valid original or approved test input produces stored owner-only outcome with evidence; real model/rule tested; invalid image/file/text/numbers fail gracefully; BN/EN; mobile layout; download/delete; private test and no unsupported claim.

### 22 · RoadFix BD — Civic, Worker Rights & Legal

**Status:** Planned V5 project — integrate · **Single-domain URL:** `/tools/roadfix-bd` · **Shared workspace:** `/workspace` · **Central Admin configuration:** `/admin/tools/roadfix-bd`.

**About (বাংলাদেশে কী সমস্যা সমাধান):** ব্যবহারকারী সহজে **নিজের রাস্তার ছবি ও এলাকা** দিলে **গর্ত/ক্ষয়ক্ষতির শ্রেণি, evidence bundle** পাবে। এই টুলের নিজস্ব visual identity এবং value feature হলো **লোকেশনভিত্তিক road log**। এটি ৩৪টি টুলের generic wrapper হবে না।

**User screen:** simple About + safety promise → picture/text/audio/numeric input choice (only supported modalities, CSV optional not mandatory) → privacy consent → extracted preview/correction → processing progress and model status → primary Bangla result in ≤3 clear main actions → expandable evidence/source timestamps, download/share privately and delete. Design input/output forms for elderly and low-data mobile conditions.

**Model work that must actually run:** pothole detection + geo duplicate matching. Candidate checkpoints: **torchvision pretrained MobileNetV3/EfficientNet-B0 feature backbone; sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2**. Execute at least one real relevant pipeline, write model card, version, test cases and fallback, and use deterministic rules explicitly named as rules. Include Bangladesh-specific test examples, confidence and error evaluation. **Never label an unrun model “integrated”.**

**Data plan:** opt-in road photographs + route metadata. Relevant references (NOT automatically licensed training datasets):
- DMP road crash dashboard: https://roadcrashinfo.dmp.gov.bd/ — **candidate; confirm access, dataset-specific licence, freshness**.
- RHD Traffic Insight Hub: https://gis.rhd.gov.bd/trafficsurvey — **candidate; confirm access, dataset-specific licence, freshness**.
- OpenStreetMap — Bangladesh Geofabrik extract: https://download.geofabrik.de/asia/bangladesh.html — **candidate; confirm access, dataset-specific licence, freshness**.

**User trust and safety:** সরকারে অভিযোগ অটো জমা নয়। Advanced panel থাকবে, কিন্তু সাধারণ ব্যবহারকারীর জন্য তিন ধাপের flow; evidence/uncertainty panel যুক্ত থাকবে।

**Central Admin module panel:** configure localized title/about/help/input schema/upload limits/report template/theme accents and navigation, model choice/version, source permission state, dataset import preview, reviewer queue, QA scores, per-tool quota/retention, moderation, canary rollout, feature-disable switch, error logs and version history. All server-authorized.

**Release acceptance:** valid original or approved test input produces stored owner-only outcome with evidence; real model/rule tested; invalid image/file/text/numbers fail gracefully; BN/EN; mobile layout; download/delete; private test and no unsupported claim.

### 23 · SafeRoute BD — Civic, Worker Rights & Legal

**Status:** Planned V5 project — integrate · **Single-domain URL:** `/tools/saferoute-bd` · **Shared workspace:** `/workspace` · **Central Admin configuration:** `/admin/tools/saferoute-bd`.

**About (বাংলাদেশে কী সমস্যা সমাধান):** ব্যবহারকারী সহজে **গন্তব্য, ভ্রমণের ধরন ও যাচাইকৃত সড়ক রিপোর্ট** দিলে **ঐতিহাসিক ঝুঁকির ব্যাখ্যা ও বিকল্প রুট তথ্য** পাবে। এই টুলের নিজস্ব visual identity এবং value feature হলো **যাত্রা প্রস্তুতির route cards**। এটি ৩৪টি টুলের generic wrapper হবে না।

**User screen:** simple About + safety promise → picture/text/audio/numeric input choice (only supported modalities, CSV optional not mandatory) → privacy consent → extracted preview/correction → processing progress and model status → primary Bangla result in ≤3 clear main actions → expandable evidence/source timestamps, download/share privately and delete. Design input/output forms for elderly and low-data mobile conditions.

**Model work that must actually run:** geospatial risk score with transparent historic source. Candidate checkpoints: **scikit-learn HistGradientBoostingRegressor / RandomForestRegressor; sklearn.ensemble.IsolationForest**. Execute at least one real relevant pipeline, write model card, version, test cases and fallback, and use deterministic rules explicitly named as rules. Include Bangladesh-specific test examples, confidence and error evaluation. **Never label an unrun model “integrated”.**

**Data plan:** verified historical accident and map data. Relevant references (NOT automatically licensed training datasets):
- DMP road crash dashboard: https://roadcrashinfo.dmp.gov.bd/ — **candidate; confirm access, dataset-specific licence, freshness**.
- Bangladesh Road Traffic Accident Dataset 2007–2024 — Figshare: https://figshare.com/articles/dataset/Bangladesh_Road_Traffic_Accident_Dataset_2007_2024_Multi-Source_Integration_/30631292 — **candidate; confirm access, dataset-specific licence, freshness**.
- BRTA — Road Safety data and limitations: https://www.bsp.brta.gov.bd/roadSafety?lan=en — **candidate; confirm access, dataset-specific licence, freshness**.

**User trust and safety:** যাত্রাপথকে নিশ্চয়ই নিরাপদ বলা নয়। Advanced panel থাকবে, কিন্তু সাধারণ ব্যবহারকারীর জন্য তিন ধাপের flow; evidence/uncertainty panel যুক্ত থাকবে।

**Central Admin module panel:** configure localized title/about/help/input schema/upload limits/report template/theme accents and navigation, model choice/version, source permission state, dataset import preview, reviewer queue, QA scores, per-tool quota/retention, moderation, canary rollout, feature-disable switch, error logs and version history. All server-authorized.

**Release acceptance:** valid original or approved test input produces stored owner-only outcome with evidence; real model/rule tested; invalid image/file/text/numbers fail gracefully; BN/EN; mobile layout; download/delete; private test and no unsupported claim.

### 24 · WaterGuard BD — Environment & Climate

**Status:** Planned V5 project — integrate · **Single-domain URL:** `/tools/waterguard-bd` · **Shared workspace:** `/workspace` · **Central Admin configuration:** `/admin/tools/waterguard-bd`.

**About (বাংলাদেশে কী সমস্যা সমাধান):** ব্যবহারকারী সহজে **পানির পরীক্ষার ছবি বা হাতে সংখ্যাগত মান** দিলে **মানের সীমা-তুলনা ও পুনঃপরীক্ষার পরামর্শ** পাবে। এই টুলের নিজস্ব visual identity এবং value feature হলো **পানি পরীক্ষার trend tracker**। এটি ৩৪টি টুলের generic wrapper হবে না।

**User screen:** simple About + safety promise → picture/text/audio/numeric input choice (only supported modalities, CSV optional not mandatory) → privacy consent → extracted preview/correction → processing progress and model status → primary Bangla result in ≤3 clear main actions → expandable evidence/source timestamps, download/share privately and delete. Design input/output forms for elderly and low-data mobile conditions.

**Model work that must actually run:** numeric rules + quality anomaly + water safety RAG. Candidate checkpoints: **Tesseract OCR with ben+eng language packs; sklearn.ensemble.IsolationForest**. Execute at least one real relevant pipeline, write model card, version, test cases and fallback, and use deterministic rules explicitly named as rules. Include Bangladesh-specific test examples, confidence and error evaluation. **Never label an unrun model “integrated”.**

**Data plan:** private water test entries + published guideline refs. Relevant references (NOT automatically licensed training datasets):
- DPHE — water quality testing system links: https://dphe.gov.bd/pages/static-pages/6922dd01933eb65569e13226 — **candidate; confirm access, dataset-specific licence, freshness**.
- WHO 2026 drinking-water quality guidelines: https://www.who.int/publications/i/item/9789240121225 — **candidate; confirm access, dataset-specific licence, freshness**.
- Bangladesh Open Data — searchable datasets: https://data.gov.bd/dataset — **candidate; confirm access, dataset-specific licence, freshness**.

**User trust and safety:** ছবি থেকে নিরাপদ পানির মান নিশ্চিত নয়। Advanced panel থাকবে, কিন্তু সাধারণ ব্যবহারকারীর জন্য তিন ধাপের flow; evidence/uncertainty panel যুক্ত থাকবে।

**Central Admin module panel:** configure localized title/about/help/input schema/upload limits/report template/theme accents and navigation, model choice/version, source permission state, dataset import preview, reviewer queue, QA scores, per-tool quota/retention, moderation, canary rollout, feature-disable switch, error logs and version history. All server-authorized.

**Release acceptance:** valid original or approved test input produces stored owner-only outcome with evidence; real model/rule tested; invalid image/file/text/numbers fail gracefully; BN/EN; mobile layout; download/delete; private test and no unsupported claim.

### 25 · AgroPrice Planner — Agriculture & Fisheries

**Status:** Planned V5 project — integrate · **Single-domain URL:** `/tools/agroprice-planner` · **Shared workspace:** `/workspace` · **Central Admin configuration:** `/admin/tools/agroprice-planner`.

**About (বাংলাদেশে কী সমস্যা সমাধান):** ব্যবহারকারী সহজে **ফসল, শ্রম/বীজ/সার খরচ, সম্ভাব্য বিক্রয়মূল্য** দিলে **লাভ/ক্ষতির দৃশ্যপট ও break-even** পাবে। এই টুলের নিজস্ব visual identity এবং value feature হলো **What-if price slider ও সহজ cost sheet**। এটি ৩৪টি টুলের generic wrapper হবে না।

**User screen:** simple About + safety promise → picture/text/audio/numeric input choice (only supported modalities, CSV optional not mandatory) → privacy consent → extracted preview/correction → processing progress and model status → primary Bangla result in ≤3 clear main actions → expandable evidence/source timestamps, download/share privately and delete. Design input/output forms for elderly and low-data mobile conditions.

**Model work that must actually run:** regression on validated price history + scenario calculator. Candidate checkpoints: **scikit-learn HistGradientBoostingRegressor / RandomForestRegressor; statsmodels ExponentialSmoothing baseline + prediction intervals when validated; sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2**. Execute at least one real relevant pipeline, write model card, version, test cases and fallback, and use deterministic rules explicitly named as rules. Include Bangladesh-specific test examples, confidence and error evaluation. **Never label an unrun model “integrated”.**

**Data plan:** DAM time-stamped commodity prices & manual costs. Relevant references (NOT automatically licensed training datasets):
- DAM daily market report: https://market.dam.gov.bd/market_daily_price_report — **candidate; confirm access, dataset-specific licence, freshness**.
- Sadai market portal: https://sadai.gov.bd/ — **candidate; confirm access, dataset-specific licence, freshness**.
- BAMIS — agricultural weather and advisories: https://www.bamis.gov.bd/en/home/ — **candidate; confirm access, dataset-specific licence, freshness**.

**User trust and safety:** নিশ্চিত ফসলের দাম/লাভ নয়। Advanced panel থাকবে, কিন্তু সাধারণ ব্যবহারকারীর জন্য তিন ধাপের flow; evidence/uncertainty panel যুক্ত থাকবে।

**Central Admin module panel:** configure localized title/about/help/input schema/upload limits/report template/theme accents and navigation, model choice/version, source permission state, dataset import preview, reviewer queue, QA scores, per-tool quota/retention, moderation, canary rollout, feature-disable switch, error logs and version history. All server-authorized.

**Release acceptance:** valid original or approved test input produces stored owner-only outcome with evidence; real model/rule tested; invalid image/file/text/numbers fail gracefully; BN/EN; mobile layout; download/delete; private test and no unsupported claim.

### 26 · LivestockCare Log — Agriculture & Fisheries

**Status:** Planned V5 project — integrate · **Single-domain URL:** `/tools/livestockcare-log` · **Shared workspace:** `/workspace` · **Central Admin configuration:** `/admin/tools/livestockcare-log`.

**About (বাংলাদেশে কী সমস্যা সমাধান):** ব্যবহারকারী সহজে **গবাদিপশুর পরিচর্যার নোট, খাবার, ছবি, ওজন** দিলে **কেয়ার লগ ও অস্বাভাবিক পরিবর্তনের flag** পাবে। এই টুলের নিজস্ব visual identity এবং value feature হলো **প্রাণীভিত্তিক পরিচর্যা টাইমলাইন**। এটি ৩৪টি টুলের generic wrapper হবে না।

**User screen:** simple About + safety promise → picture/text/audio/numeric input choice (only supported modalities, CSV optional not mandatory) → privacy consent → extracted preview/correction → processing progress and model status → primary Bangla result in ≤3 clear main actions → expandable evidence/source timestamps, download/share privately and delete. Design input/output forms for elderly and low-data mobile conditions.

**Model work that must actually run:** time-series anomaly + optional veterinary RAG. Candidate checkpoints: **sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2; sklearn.ensemble.IsolationForest**. Execute at least one real relevant pipeline, write model card, version, test cases and fallback, and use deterministic rules explicitly named as rules. Include Bangladesh-specific test examples, confidence and error evaluation. **Never label an unrun model “integrated”.**

**Data plan:** consented herd health logs. Relevant references (NOT automatically licensed training datasets):
- Ministry of Fisheries and Livestock Annual Reports: https://mofl.gov.bd/pages/annual-reports/ — **candidate; confirm access, dataset-specific licence, freshness**.
- BAMIS — agricultural weather and advisories: https://www.bamis.gov.bd/en/home/ — **candidate; confirm access, dataset-specific licence, freshness**.
- Bangladesh Open Data — searchable datasets: https://data.gov.bd/dataset — **candidate; confirm access, dataset-specific licence, freshness**.

**User trust and safety:** ভেটেরিনারি রোগ নির্ণয় বা ওষুধ নয়। Advanced panel থাকবে, কিন্তু সাধারণ ব্যবহারকারীর জন্য তিন ধাপের flow; evidence/uncertainty panel যুক্ত থাকবে।

**Central Admin module panel:** configure localized title/about/help/input schema/upload limits/report template/theme accents and navigation, model choice/version, source permission state, dataset import preview, reviewer queue, QA scores, per-tool quota/retention, moderation, canary rollout, feature-disable switch, error logs and version history. All server-authorized.

**Release acceptance:** valid original or approved test input produces stored owner-only outcome with evidence; real model/rule tested; invalid image/file/text/numbers fail gracefully; BN/EN; mobile layout; download/delete; private test and no unsupported claim.

### 27 · CivicForm AI — Civic, Worker Rights & Legal

**Status:** Planned V5 project — integrate · **Single-domain URL:** `/tools/civicform-ai` · **Shared workspace:** `/workspace` · **Central Admin configuration:** `/admin/tools/civicform-ai`.

**About (বাংলাদেশে কী সমস্যা সমাধান):** ব্যবহারকারী সহজে **সরকারি ফর্মের ছবি/PDF বা ফর্মের নাম** দিলে **ফর্ম ফিল্ড ব্যাখ্যা ও missing-document checklist** পাবে। এই টুলের নিজস্ব visual identity এবং value feature হলো **Step-by-step field helper**। এটি ৩৪টি টুলের generic wrapper হবে না।

**User screen:** simple About + safety promise → picture/text/audio/numeric input choice (only supported modalities, CSV optional not mandatory) → privacy consent → extracted preview/correction → processing progress and model status → primary Bangla result in ≤3 clear main actions → expandable evidence/source timestamps, download/share privately and delete. Design input/output forms for elderly and low-data mobile conditions.

**Model work that must actually run:** document OCR + form field extraction + source-grounded RAG. Candidate checkpoints: **Tesseract OCR with ben+eng language packs; sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2; rank-bm25 lexical retrieval**. Execute at least one real relevant pipeline, write model card, version, test cases and fallback, and use deterministic rules explicitly named as rules. Include Bangladesh-specific test examples, confidence and error evaluation. **Never label an unrun model “integrated”.**

**Data plan:** official form instructions verified links. Relevant references (NOT automatically licensed training datasets):
- Laws of Bangladesh — legislation search: https://bdlaws.minlaw.gov.bd/ — **candidate; confirm access, dataset-specific licence, freshness**.
- Bangladesh Open Data — searchable datasets: https://data.gov.bd/dataset — **candidate; confirm access, dataset-specific licence, freshness**.
- National Consumer Rights Protection — complaints and rules: https://dncrp.gov.bd/ — **candidate; confirm access, dataset-specific licence, freshness**.

**User trust and safety:** বিভাগে স্বয়ংক্রিয় আবেদন নয়। Advanced panel থাকবে, কিন্তু সাধারণ ব্যবহারকারীর জন্য তিন ধাপের flow; evidence/uncertainty panel যুক্ত থাকবে।

**Central Admin module panel:** configure localized title/about/help/input schema/upload limits/report template/theme accents and navigation, model choice/version, source permission state, dataset import preview, reviewer queue, QA scores, per-tool quota/retention, moderation, canary rollout, feature-disable switch, error logs and version history. All server-authorized.

**Release acceptance:** valid original or approved test input produces stored owner-only outcome with evidence; real model/rule tested; invalid image/file/text/numbers fail gracefully; BN/EN; mobile layout; download/delete; private test and no unsupported claim.

### 28 · HeatSafe BD — Environment & Climate

**Status:** Planned V5 project — integrate · **Single-domain URL:** `/tools/heatsafe-bd` · **Shared workspace:** `/workspace` · **Central Admin configuration:** `/admin/tools/heatsafe-bd`.

**About (বাংলাদেশে কী সমস্যা সমাধান):** ব্যবহারকারী সহজে **এলাকা, তাপ/আর্দ্রতার প্রকাশিত মান, কাজের ধরন** দিলে **হিট সতর্কতার ব্যাখ্যা ও কাজের বিরতি planner** পাবে। এই টুলের নিজস্ব visual identity এবং value feature হলো **Heat diary ও কর্মঘণ্টার সচেতনতা**। এটি ৩৪টি টুলের generic wrapper হবে না।

**User screen:** simple About + safety promise → picture/text/audio/numeric input choice (only supported modalities, CSV optional not mandatory) → privacy consent → extracted preview/correction → processing progress and model status → primary Bangla result in ≤3 clear main actions → expandable evidence/source timestamps, download/share privately and delete. Design input/output forms for elderly and low-data mobile conditions.

**Model work that must actually run:** heat index rules + weather observations + explainability. Candidate checkpoints: **statsmodels ExponentialSmoothing baseline + prediction intervals when validated; sklearn.ensemble.IsolationForest; sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2**. Execute at least one real relevant pipeline, write model card, version, test cases and fallback, and use deterministic rules explicitly named as rules. Include Bangladesh-specific test examples, confidence and error evaluation. **Never label an unrun model “integrated”.**

**Data plan:** licensed meteorological observations. Relevant references (NOT automatically licensed training datasets):
- BAMIS — agricultural weather and advisories: https://www.bamis.gov.bd/en/home/ — **candidate; confirm access, dataset-specific licence, freshness**.
- BAMIS — About the portal and data coverage: https://www.bamis.gov.bd/en/page/about-bamis-portal/ — **candidate; confirm access, dataset-specific licence, freshness**.
- Department of Environment — daily AQI report: https://doe.portal.gov.bd/pages/static-pages/6922dfba933eb65569e23b0a — **candidate; confirm access, dataset-specific licence, freshness**.

**User trust and safety:** জরুরি সতর্কতা অফিসিয়াল তথ্যের বিকল্প নয়। Advanced panel থাকবে, কিন্তু সাধারণ ব্যবহারকারীর জন্য তিন ধাপের flow; evidence/uncertainty panel যুক্ত থাকবে।

**Central Admin module panel:** configure localized title/about/help/input schema/upload limits/report template/theme accents and navigation, model choice/version, source permission state, dataset import preview, reviewer queue, QA scores, per-tool quota/retention, moderation, canary rollout, feature-disable switch, error logs and version history. All server-authorized.

**Release acceptance:** valid original or approved test input produces stored owner-only outcome with evidence; real model/rule tested; invalid image/file/text/numbers fail gracefully; BN/EN; mobile layout; download/delete; private test and no unsupported claim.

### 29 · HospitalBillGuard BD — Healthcare Support

**Status:** Planned V5 project — integrate · **Single-domain URL:** `/tools/hospitalbillguard-bd` · **Shared workspace:** `/workspace` · **Central Admin configuration:** `/admin/tools/hospitalbillguard-bd`.

**About (বাংলাদেশে কী সমস্যা সমাধান):** ব্যবহারকারী সহজে **হাসপাতালের বিল বা estimate** দিলে **চার্জের ব্যাখ্যা ও যোগফল/ডুপ্লিকেট যাচাই** পাবে। এই টুলের নিজস্ব visual identity এবং value feature হলো **প্রক্রিয়াভিত্তিক billing breakdown**। এটি ৩৪টি টুলের generic wrapper হবে না।

**User screen:** simple About + safety promise → picture/text/audio/numeric input choice (only supported modalities, CSV optional not mandatory) → privacy consent → extracted preview/correction → processing progress and model status → primary Bangla result in ≤3 clear main actions → expandable evidence/source timestamps, download/share privately and delete. Design input/output forms for elderly and low-data mobile conditions.

**Model work that must actually run:** medical service OCR + duplicate-item matching. Candidate checkpoints: **Tesseract OCR with ben+eng language packs; sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2; sklearn.ensemble.IsolationForest**. Execute at least one real relevant pipeline, write model card, version, test cases and fallback, and use deterministic rules explicitly named as rules. Include Bangladesh-specific test examples, confidence and error evaluation. **Never label an unrun model “integrated”.**

**Data plan:** user-owned invoices and approved service dictionary. Relevant references (NOT automatically licensed training datasets):
- DGHS — Bangladesh Facility Registry: https://hris.mohfw.gov.bd/public/facility-registry/ — **candidate; confirm access, dataset-specific licence, freshness**.
- National Consumer Rights Protection — complaints and rules: https://dncrp.gov.bd/ — **candidate; confirm access, dataset-specific licence, freshness**.
- Consumer Complaint Management System: https://dncrp.com/ — **candidate; confirm access, dataset-specific licence, freshness**.

**User trust and safety:** অবৈধ billing সিদ্ধান্ত নয়। Advanced panel থাকবে, কিন্তু সাধারণ ব্যবহারকারীর জন্য তিন ধাপের flow; evidence/uncertainty panel যুক্ত থাকবে।

**Central Admin module panel:** configure localized title/about/help/input schema/upload limits/report template/theme accents and navigation, model choice/version, source permission state, dataset import preview, reviewer queue, QA scores, per-tool quota/retention, moderation, canary rollout, feature-disable switch, error logs and version history. All server-authorized.

**Release acceptance:** valid original or approved test input produces stored owner-only outcome with evidence; real model/rule tested; invalid image/file/text/numbers fail gracefully; BN/EN; mobile layout; download/delete; private test and no unsupported claim.

### 30 · SafeBlood Connect BD — Healthcare Support

**Status:** Planned V5 project — integrate · **Single-domain URL:** `/tools/safeblood-connect-bd` · **Shared workspace:** `/workspace` · **Central Admin configuration:** `/admin/tools/safeblood-connect-bd`.

**About (বাংলাদেশে কী সমস্যা সমাধান):** ব্যবহারকারী সহজে **রক্তের গ্রুপ ও স্বেচ্ছায় অংশগ্রহণের পছন্দ** দিলে **consent-based donor request matching** পাবে। এই টুলের নিজস্ব visual identity এবং value feature হলো **Privacy-first donor request timeline**। এটি ৩৪টি টুলের generic wrapper হবে না।

**User screen:** simple About + safety promise → picture/text/audio/numeric input choice (only supported modalities, CSV optional not mandatory) → privacy consent → extracted preview/correction → processing progress and model status → primary Bangla result in ≤3 clear main actions → expandable evidence/source timestamps, download/share privately and delete. Design input/output forms for elderly and low-data mobile conditions.

**Model work that must actually run:** matching/ranking rules; optional NLP request parsing. Candidate checkpoints: **sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2**. Execute at least one real relevant pipeline, write model card, version, test cases and fallback, and use deterministic rules explicitly named as rules. Include Bangladesh-specific test examples, confidence and error evaluation. **Never label an unrun model “integrated”.**

**Data plan:** opt-in donor availability with expiration. Relevant references (NOT automatically licensed training datasets):
- DGHS — official health services portal: https://dghs.gov.bd/ — **candidate; confirm access, dataset-specific licence, freshness**.
- DGHS — Bangladesh Facility Registry: https://hris.mohfw.gov.bd/public/facility-registry/ — **candidate; confirm access, dataset-specific licence, freshness**.
- Bangladesh Open Data — searchable datasets: https://data.gov.bd/dataset — **candidate; confirm access, dataset-specific licence, freshness**.

**User trust and safety:** ব্লাড গ্রুপ/উপযুক্ততা চিকিৎসক দ্বারা যাচাইযোগ্য। Advanced panel থাকবে, কিন্তু সাধারণ ব্যবহারকারীর জন্য তিন ধাপের flow; evidence/uncertainty panel যুক্ত থাকবে।

**Central Admin module panel:** configure localized title/about/help/input schema/upload limits/report template/theme accents and navigation, model choice/version, source permission state, dataset import preview, reviewer queue, QA scores, per-tool quota/retention, moderation, canary rollout, feature-disable switch, error logs and version history. All server-authorized.

**Release acceptance:** valid original or approved test input produces stored owner-only outcome with evidence; real model/rule tested; invalid image/file/text/numbers fail gracefully; BN/EN; mobile layout; download/delete; private test and no unsupported claim.

### 31 · ShikkhaRAG BD — Learning

**Status:** Planned V5 project — integrate · **Single-domain URL:** `/tools/shikkharag-bd` · **Shared workspace:** `/workspace` · **Central Admin configuration:** `/admin/tools/shikkharag-bd`.

**About (বাংলাদেশে কী সমস্যা সমাধান):** ব্যবহারকারী সহজে **ক্লাস, বিষয়, অধ্যায়, নিজ প্রশ্ন** দিলে **অনুমোদিত টেক্সটের উৎসসহ উত্তর ও কুইজ** পাবে। এই টুলের নিজস্ব visual identity এবং value feature হলো **Citation tutor ও chapter learning map**। এটি ৩৪টি টুলের generic wrapper হবে না।

**User screen:** simple About + safety promise → picture/text/audio/numeric input choice (only supported modalities, CSV optional not mandatory) → privacy consent → extracted preview/correction → processing progress and model status → primary Bangla result in ≤3 clear main actions → expandable evidence/source timestamps, download/share privately and delete. Design input/output forms for elderly and low-data mobile conditions.

**Model work that must actually run:** embedding + BM25 + reranking + grounded text generation. Candidate checkpoints: **sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2; rank-bm25 lexical retrieval; Qwen/Qwen2.5-1.5B-Instruct**. Execute at least one real relevant pipeline, write model card, version, test cases and fallback, and use deterministic rules explicitly named as rules. Include Bangladesh-specific test examples, confidence and error evaluation. **Never label an unrun model “integrated”.**

**Data plan:** NCTB curriculum metadata; licensed educational passages. Relevant references (NOT automatically licensed training datasets):
- NCTB — official textbooks and curriculum: https://nctb.gov.bd/ — **candidate; confirm access, dataset-specific licence, freshness**.
- NCTB — secondary and higher-secondary book lists 2026: https://nctb.gov.bd/pages/static-pages/695b98afc4774958d7b7044c — **candidate; confirm access, dataset-specific licence, freshness**.
- BANBEIS — education statistics and reports: https://banbeis.gov.bd/ — **candidate; confirm access, dataset-specific licence, freshness**.

**User trust and safety:** unlicensed textbook content training নয়। একটি বাস্তব, অনুমোদিত বাংলা passage corpus-এ embedding ও BM25 চালিয়ে citation-hit পরীক্ষা বাধ্যতামূলক; NCTB লেখা train করা যাবে এমন ধরে নয়।

**Central Admin module panel:** configure localized title/about/help/input schema/upload limits/report template/theme accents and navigation, model choice/version, source permission state, dataset import preview, reviewer queue, QA scores, per-tool quota/retention, moderation, canary rollout, feature-disable switch, error logs and version history. All server-authorized.

**Release acceptance:** valid original or approved test input produces stored owner-only outcome with evidence; real model/rule tested; invalid image/file/text/numbers fail gracefully; BN/EN; mobile layout; download/delete; private test and no unsupported claim.

### 32 · BanglaRead Coach — Learning

**Status:** ALREADY BUILT — migrate conservatively · **Single-domain URL:** `/tools/banglaread-coach` · **Shared workspace:** `/workspace` · **Central Admin configuration:** `/admin/tools/banglaread-coach`.

**About (বাংলাদেশে কী সমস্যা সমাধান):** ব্যবহারকারী সহজে **বয়স-উপযোগী বাংলা পাঠ, voice practice** দিলে **শব্দভিত্তিক reading feedback ও অনুশীলন** পাবে। এই টুলের নিজস্ব visual identity এবং value feature হলো **বড় বাংলা টাইপ ও অভিভাবক dashboard**। এটি ৩৪টি টুলের generic wrapper হবে না।

**User screen:** simple About + safety promise → picture/text/audio/numeric input choice (only supported modalities, CSV optional not mandatory) → privacy consent → extracted preview/correction → processing progress and model status → primary Bangla result in ≤3 clear main actions → expandable evidence/source timestamps, download/share privately and delete. Design input/output forms for elderly and low-data mobile conditions.

**Model work that must actually run:** Bangla ASR + alignment + pronunciation scoring calibration. Candidate checkpoints: **openai/whisper-small; sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2**. Execute at least one real relevant pipeline, write model card, version, test cases and fallback, and use deterministic rules explicitly named as rules. Include Bangladesh-specific test examples, confidence and error evaluation. **Never label an unrun model “integrated”.**

**Data plan:** original reading passages; consented child audio. Relevant references (NOT automatically licensed training datasets):
- NCTB primary 2026 textbooks: https://nctb.gov.bd/pages/static-pages/695b9b7cc4774958d7b70a12 — **candidate; confirm access, dataset-specific licence, freshness**.
- NCTB grade 1 book metadata: https://nctb.gov.bd/pages/static-pages/695b9adec4774958d7b708cd — **candidate; confirm access, dataset-specific licence, freshness**.
- Mozilla Common Voice Bengali: https://commonvoice.mozilla.org/bn/datasets — **candidate; confirm access, dataset-specific licence, freshness**.

**User trust and safety:** স্বরভঙ্গিকে রোগ বা IQ হিসেবে মূল্যায়ন নয়। আগের আসল বাংলায় লেখা original passages, শিশুর progress ও guardian profile অক্ষত থাকবে। Child audio training-এর জন্য আলাদা guardian opt-in চাইবে।

**Central Admin module panel:** configure localized title/about/help/input schema/upload limits/report template/theme accents and navigation, model choice/version, source permission state, dataset import preview, reviewer queue, QA scores, per-tool quota/retention, moderation, canary rollout, feature-disable switch, error logs and version history. All server-authorized.

**Release acceptance:** valid original or approved test input produces stored owner-only outcome with evidence; real model/rule tested; invalid image/file/text/numbers fail gracefully; BN/EN; mobile layout; download/delete; private test and no unsupported claim.

### 33 · LandLedger BD — Civic, Worker Rights & Legal

**Status:** NEW distinctive project · **Single-domain URL:** `/tools/landledger-bd` · **Shared workspace:** `/workspace` · **Central Admin configuration:** `/admin/tools/landledger-bd`.

**About (বাংলাদেশে কী সমস্যা সমাধান):** ব্যবহারকারী সহজে **খতিয়ান/দলিল/নামজারি কাগজের ছবি, জমির পরিমাপ** দিলে **নাম-দাগ-খতিয়ান-পরিমাণের অসংগতির খসড়া তালিকা** পাবে। এই টুলের নিজস্ব visual identity এবং value feature হলো **পাশাপাশি নথি তুলনা ও field confidence**। এটি ৩৪টি টুলের generic wrapper হবে না।

**User screen:** simple About + safety promise → picture/text/audio/numeric input choice (only supported modalities, CSV optional not mandatory) → privacy consent → extracted preview/correction → processing progress and model status → primary Bangla result in ≤3 clear main actions → expandable evidence/source timestamps, download/share privately and delete. Design input/output forms for elderly and low-data mobile conditions.

**Model work that must actually run:** Bangla OCR + entity linking + cross-document consistency rules + legal RAG. Candidate checkpoints: **Tesseract OCR ben+eng; Multilingual MiniLM**. Execute at least one real relevant pipeline, write model card, version, test cases and fallback, and use deterministic rules explicitly named as rules. Include Bangladesh-specific test examples, confidence and error evaluation. **Never label an unrun model “integrated”.**

**Data plan:** land.gov.bd & mutation portal as reference; user-owned redacted docs. Relevant references (NOT automatically licensed training datasets):
- Ministry of Land: https://land.gov.bd/ — **candidate; confirm access, dataset-specific licence, freshness**.
- Mutation Service: https://mutation.land.gov.bd/ — **candidate; confirm access, dataset-specific licence, freshness**.
- Land record survey: https://settlement.gov.bd/ — **candidate; confirm access, dataset-specific licence, freshness**.

**User trust and safety:** মালিকানা সত্যায়ন, ভুয়া দলিল শনাক্তের নিশ্চয়তা নয়। খসড়া খতিয়ানকে চূড়ান্ত মালিকানা নয়; OCR confidence ও unit confirmation না পেলে comparison block করবে। ক্ষেত্রফল conversion exact decimal ব্যবহার করে original value বজায় রাখবে।

**Central Admin module panel:** configure localized title/about/help/input schema/upload limits/report template/theme accents and navigation, model choice/version, source permission state, dataset import preview, reviewer queue, QA scores, per-tool quota/retention, moderation, canary rollout, feature-disable switch, error logs and version history. All server-authorized.

**Release acceptance:** valid original or approved test input produces stored owner-only outcome with evidence; real model/rule tested; invalid image/file/text/numbers fail gracefully; BN/EN; mobile layout; download/delete; private test and no unsupported claim.

### 34 · WageGuard BD — Civic, Worker Rights & Legal

**Status:** NEW distinctive project · **Single-domain URL:** `/tools/wageguard-bd` · **Shared workspace:** `/workspace` · **Central Admin configuration:** `/admin/tools/wageguard-bd`.

**About (বাংলাদেশে কী সমস্যা সমাধান):** ব্যবহারকারী সহজে **পে-স্লিপ, দৈনিক কাজের ঘণ্টা, মজুরির পরিমাণ** দিলে **হিসাবের অমিল, overtime what-if ও প্রশ্নের তালিকা** পাবে। এই টুলের নিজস্ব visual identity এবং value feature হলো **Monthly pay timeline ও explainable calculator**। এটি ৩৪টি টুলের generic wrapper হবে না।

**User screen:** simple About + safety promise → picture/text/audio/numeric input choice (only supported modalities, CSV optional not mandatory) → privacy consent → extracted preview/correction → processing progress and model status → primary Bangla result in ≤3 clear main actions → expandable evidence/source timestamps, download/share privately and delete. Design input/output forms for elderly and low-data mobile conditions.

**Model work that must actually run:** payslip OCR + rule versioning + numeric anomaly + labor-law RAG. Candidate checkpoints: **Tesseract OCR ben+eng; Isolation Forest scikit-learn**. Execute at least one real relevant pipeline, write model card, version, test cases and fallback, and use deterministic rules explicitly named as rules. Include Bangladesh-specific test examples, confidence and error evaluation. **Never label an unrun model “integrated”.**

**Data plan:** public labor-law revisions; opt-in redacted pay logs. Relevant references (NOT automatically licensed training datasets):
- Bangladesh Labour Act: https://bdlaws.minlaw.gov.bd/act-details-952.html?lang=en — **candidate; confirm access, dataset-specific licence, freshness**.
- Ministry of Labour legislation: https://mole.gov.bd/pages/legislative-informations — **candidate; confirm access, dataset-specific licence, freshness**.
- Labour ministry: https://mole.gov.bd/ — **candidate; confirm access, dataset-specific licence, freshness**.

**User trust and safety:** সঠিক আইনি পাওনা যাচাই ছাড়া ঘোষিত নয়। একটি শ্রমআইনের আইনগত সংস্করণ সকল শ্রমিকের জন্য প্রযোজ্য ধরে নেবে না; শিল্প, সময়, চুক্তি, প্রযোজ্য বিধান ও হালনাগাদ যাচাই করবে। ভুল legal certainty প্রকাশ করবে না।

**Central Admin module panel:** configure localized title/about/help/input schema/upload limits/report template/theme accents and navigation, model choice/version, source permission state, dataset import preview, reviewer queue, QA scores, per-tool quota/retention, moderation, canary rollout, feature-disable switch, error logs and version history. All server-authorized.

**Release acceptance:** valid original or approved test input produces stored owner-only outcome with evidence; real model/rule tested; invalid image/file/text/numbers fail gracefully; BN/EN; mobile layout; download/delete; private test and no unsupported claim.

### 35 · ShobdoSetu BD — Accessibility

**Status:** NEW distinctive project · **Single-domain URL:** `/tools/shobdosetu-bd` · **Shared workspace:** `/workspace` · **Central Admin configuration:** `/admin/tools/shobdosetu-bd`.

**About (বাংলাদেশে কী সমস্যা সমাধান):** ব্যবহারকারী সহজে **বাংলা অডিও/টেক্সট ও আগে থেকে বাছা প্রয়োজনীয় বাক্য** দিলে **বাংলা লাইভ ক্যাপশন, বাক্য-কার্ড ও বড় লেখা/কথা আউটপুট** পাবে। এই টুলের নিজস্ব visual identity এবং value feature হলো **Tap-to-speak phraseboard এবং Live Caption**। এটি ৩৪টি টুলের generic wrapper হবে না।

**User screen:** simple About + safety promise → picture/text/audio/numeric input choice (only supported modalities, CSV optional not mandatory) → privacy consent → extracted preview/correction → processing progress and model status → primary Bangla result in ≤3 clear main actions → expandable evidence/source timestamps, download/share privately and delete. Design input/output forms for elderly and low-data mobile conditions.

**Model work that must actually run:** Bangla ASR + text normalization + optional TTS. Candidate checkpoints: **Whisper small multilingual; Piper TTS or deployable Bengali voice with checked license**. Execute at least one real relevant pipeline, write model card, version, test cases and fallback, and use deterministic rules explicitly named as rules. Include Bangladesh-specific test examples, confidence and error evaluation. **Never label an unrun model “integrated”.**

**Data plan:** permissioned adult audio samples; original phrasebook. Relevant references (NOT automatically licensed training datasets):
- Department of Social Services: https://dss.gov.bd/ — **candidate; confirm access, dataset-specific licence, freshness**.
- Bangladesh National Corpus: https://corpus.bangla.gov.bd/ — **candidate; confirm access, dataset-specific licence, freshness**.
- Bangladesh Open Data: https://data.gov.bd/dataset — **candidate; confirm access, dataset-specific licence, freshness**.

**User trust and safety:** Sign-language translator বলে দাবি নয়; উচ্চারণ ভুল হতে পারে। মাইক্রোফোন ছাড়াই phraseboard চলবে, বড় লেখা ও নির্ভরযোগ্য tap-to-speak ফিচার; Live Caption ভুল হলে মানুষ edit করতে পারবে। Sign language translation দাবি নয়।

**Central Admin module panel:** configure localized title/about/help/input schema/upload limits/report template/theme accents and navigation, model choice/version, source permission state, dataset import preview, reviewer queue, QA scores, per-tool quota/retention, moderation, canary rollout, feature-disable switch, error logs and version history. All server-authorized.

**Release acceptance:** valid original or approved test input produces stored owner-only outcome with evidence; real model/rule tested; invalid image/file/text/numbers fail gracefully; BN/EN; mobile layout; download/delete; private test and no unsupported claim.

## 18. Every Required File and How ChatGPT Work Must Use It

| Path | Contents | Required action |
|---|---|---|
| `README.md` | This ONE complete central Master Prompt | highest priority for architecture, UX, execution |
| `config/MODULES_35.json` | 35 tool IDs/slugs/routes/features/inputs | generate catalogue and central module registry |
| `config/MODULES_35.csv` | 35 human-readable module specifications | project audit and parity check |
| `model/MODEL_REGISTRY.json` | 35 model candidate configurations and smoke tests | real inference+evaluation, no fabricated passes |
| `datasets/SOURCE_REGISTRY.csv` | 207 reference entries incl. two portal-level sources | verify rights, access, freshness before data ingest |
| `datasets/SOURCE_REGISTRY.json` | same machine-readable provenance | seed admin review console, all initial not approved |
| `qa/ACCEPTANCE_MATRIX.csv` | 280 not-yet-run test scenarios | run each and record evidence |
| `database/BASELINE_POSTGRES.sql` | reference-only core tables and security reminders | extend with fully tested migrations/RLS |
| `config/.env.example` | required keys without secrets | configure approved production env, never leak secrets |
| `seed/SEED_MARKET_PRICES_TEMPLATE.csv` | only columns, no made-up live market prices | safe verified import, no fake observations |
| `seed/SEED_WORKER_LOG_TEMPLATE.csv` | private wage-log schema | per-user form; protect workers' records |
| `seed/SEED_PROPERTY_DOC_FIELDS_TEMPLATE.csv` | safe property field extraction headers | OCR fields and human verification |
| `seed/SEED_ACCESSIBILITY_PHRASES.csv` | 10 original Bangla/English communication phrases | usable initial ShobdoSetu offline phraseboard |
| `reference/legacy-v5/projects/*/MASTER_PROMPT_V5.md` | **32 original full V5 prompts unchanged** | preserve individual features, override standalone-site commands |
| `reference/legacy-v5/projects/*/DATASET_SOURCE_REGISTRY.json` | each of 32 earlier detailed data links | keep deeper project-specific references and caveats |
| `reference/legacy-v5/projects/*/MODEL_IMPLEMENTATION_SPEC.json` | each of 32 actual model design | implement models and verify actual inference |
| `site-preview/index.html` | central product interactive static concept | UX reference only, not implemented website |

**CSV import contract:** UTF-8/BOM; schema validation, human preview, duplicate rules, source rights record, license ID, date/geo metadata, rollback. Never export untrusted input into spreadsheet formula execution. CSV input optional for end users; admin/owners may import datasets only after rights approval.

**JSON validation:** fail CI if not exactly 35 unique slugs, malformed route, missing BN explanation, wrong `existing_site`, empty model requirements or unsupported category. Block dataset import lacking licence evidence. Keep actual completed deployment state separate from aspirational specification.

## 19. Copy-Paste Handoff to ChatGPT Work

**START:** Read `README.md` and all bundled configuration files. Build ONE bilingual, high-quality mobile-first Bangladesh AI platform **JibonSetu AI** with all 35 integrated module routes, single user login, one central editable super-admin CMS, shared workspace, real verified AI/ML/NLP/RAG pipelines, consent and private document protections, source/rights metadata and one GitHub monorepo. Preserve earlier 32 V5 feature requirements in `reference/legacy-v5` while ignoring their old separate-repository and separate-login instructions. Migrate the existing 4 websites carefully only after actual authenticated repo access, backup, parity tests and user consent as applicable. Use source registry URLs as candidates and do not assume government portal information can be automatically trained on or redistributed. Implement meaningful working feature slices, real model tests, truthful ready/blocked labels, complete documentation and modern Riverlight design. Use the existing static HTML preview as a reference, not a substitute for code. GitHub create/push and hosting changes only with user authorization and report actual commit/deploy evidence. Work through phases and maintain checkpoint progress; never leave 35 fake success screens.

**Owner responsibilities:** authorize connected GitHub/hosting and any protected data/provider credentials when requested; choose final brand/domain if naming conflicts exist. Those are prerequisites for remote actions, not reasons to skip building local code.

**End goal:** one production-ready source repository, one public domain, 35 useful modular AI experiences with honest release flags, one genuinely powerful admin area, unified secure account and accessible bilingual UX; show exactly what is implemented and what remains.

