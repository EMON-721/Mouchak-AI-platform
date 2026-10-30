# Mouchak AI · মৌচাক এআই

বাংলা speech continuation: BanglaRead-এ বাস্তব pinned Bengali Whisper Small, অস্থায়ী adult self-recording processing, word-time/alignment এবং MFA-নিয়ন্ত্রিত speech lab যুক্ত হয়েছে। ১,৮৯১টি বৈধ OpenSLR37 Bangladesh source row থেকে নির্দিষ্ট ১২ clip-এ measured WER **৩৬.৮৯%**; এটি child/guardian field validation নয়। Production ও শিশু-কণ্ঠ বন্ধ। Raw voice/transcript default-এ রাখা হয় না; manual practice চালু আছে। [ব্যবহার, API, model/dataset licence, setup ও বাকি scope](docs/READING_SPEECH.md)। Source `eabe937`-এর [CI 41031736096](https://github.com/EMON-721/Mouchak-AI-platform/actions/runs/41031736096)-এ দুই job সফল: **৪৮১ test + ১৭ subtest**। Browser-এ নতুন reading panel ও বাস্তব typed result দেখা গেছে; PDF download, তিনটি viewport ও protected admin যাচাই সম্পূর্ণ নয়। আগের CI ফল নিচে ঐতিহাসিক; নতুন source-এর যাচাই [implementation report](IMPLEMENTATION_REPORT.md)-এ আলাদা থাকবে।

নতুন advanced continuation: বাস্তব YAMNet CPU sound-event inference (local experimental, production gate বন্ধ), ৫০ tool-এর MiniLM/BM25 semantic launcher এবং বাস্তবে downloaded/processed ৩২,২৮৫ ODbL Bangladesh road-reference row-এর review/publication/search workflow যুক্ত হয়েছে। Full specialized ৫০-tool scope এখনও certified নয়। [ব্যবহার, source, licence ও সীমাবদ্ধতা](docs/ADVANCED_PIPELINES.md)। সংশোধিত model/data source-এর [CI 41002816619](https://github.com/EMON-721/Mouchak-AI-platform/actions/runs/41002816619)-এ দুই job সফল: ৪৫৩ test + ১৭ subtest। Browser-এ actual Bengali RAG, semantic ranking ও WAV→YAMNet result দেখা গেছে। HTTP preview checksum bug-ও ঠিক হয়েছে; সর্বশেষ runtime source `ee3ac5f`-এর [CI 41005839012](https://github.com/EMON-721/Mouchak-AI-platform/actions/runs/41005839012)-তে দুই job সফল (৪৫৩ test + ১৭ subtest, ৭৪.৩৮ সেকেন্ড)। Protected admin/MFA, তিনটি viewport ও browser PDF download এখনও পুরো যাচাই হয়নি।


সর্বশেষ code continuation: `/admin/site-builder`-এ bilingual brand/logo/favicon, theme, menu/footer, homepage/FAQ, public pages, ৫০ tool-এর নাম/field help/placeholder, নির্বাচিত locale/category ও SEO সম্পাদনা যুক্ত হয়েছে। ব্যক্তিগত immutable draft → আলাদা MFA সম্পাদকের review → publish/schedule/rollback। [ব্যবহার, নিরাপত্তা ও সীমাবদ্ধতা](docs/SITE_BUILDER.md)। এটি পূর্ণ ৫০ advanced pipeline শেষ হওয়ার দাবি নয়; hosting বন্ধ আছে।
API transaction-এর commit এখন successful response-এর আগে শেষ হয়; commit ব্যর্থ হলে success/session cookie পাঠানো হয় না। এতে তাৎক্ষণিক save ও rights-revocation check পুরোনো অবস্থা পড়ার race বন্ধ হয়।



**বাংলাদেশের সাধারণ মানুষের জন্য একটি কেন্দ্রীয়, বাংলা–ইংরেজি AI সহায়ক প্ল্যাটফর্ম।** কৃষি, শিক্ষা, স্বাস্থ্যসংক্রান্ত নথি, বাসা, ব্যবসা ও নাগরিক সেবার জন্য একই website-এ ৫০টি tool workspace। Next.js frontend, private Python/FastAPI API, database, worker, বাস্তব local inference adapter, protected operator console এবং automated tests একই monorepo-তে রয়েছে।

**Repository-first checkpoint — production hosting আপাতত স্থগিত।** কোনো Render, Netlify, Railway, Vercel, Cloudflare বা নির্দিষ্ট database account বাধ্যতামূলক নয়। কোড local machine, private developer container অথবা সামঞ্জস্যপূর্ণ Node/Python/Docker infrastructure-এ চালানোর জন্য প্রস্তুত করা হয়েছে। শুধু GitHub Pages-এর static hosting পূর্ণ Python/API website চালাতে পারবে না।

> **সত্যিকারের বর্তমান অবস্থা:** ৫০টি route/workspace আছে; ৪৭টি সীমিত support flow আছে; GoliCoach, ClinicCompass ও OshudhKhoj-এর production core বন্ধ। কোনো tool-এর সম্পূর্ণ original advanced production scope certified নয়। বাস্তব OCR/retrieval/model mechanics-কে Bangladesh accuracy, চিকিৎসা সিদ্ধান্ত বা সম্পূর্ণ ৫০-tool release হিসেবে দাবি করা হয় না। [Implementation report](IMPLEMENTATION_REPORT.md) ও [per-tool checklist](MODULE_PROGRESS.csv) দেখুন।

[![CI](https://github.com/EMON-721/Mouchak-AI-platform/actions/workflows/ci.yml/badge.svg)](https://github.com/EMON-721/Mouchak-AI-platform/actions/workflows/ci.yml)
[Open a private developer preview in Codespaces](https://codespaces.new/EMON-721/Mouchak-AI-platform) · [Preview guide](docs/PREVIEW.md) · [API reference](docs/API_REFERENCE.md) · [Deployment guide](docs/DEPLOYMENT.md)

## কারা ব্যবহার করবেন

- সাধারণ বাংলা/ইংরেজিভাষী মানুষ: নিজের নথি, হিসাব, পর্যবেক্ষণ ও প্রয়োজনীয় checklist প্রস্তুত করতে।
- শিক্ষার্থী ও অভিভাবক: মূল বাংলা passage, comprehension, cited learning retrieval ও parent-reviewed notes।
- ছোট ব্যবসায়ী, ক্রেতা ও কৃষক: নিজের দেওয়া stock, price, bill, cashbook ও farming cost হিসাব করতে।
- পরিচর্যাকারী ও নাগরিক: নিজের confirmed record ও প্রশ্ন গুছিয়ে সংশ্লিষ্ট পেশাজীবী/অফিসের সঙ্গে কথা বলতে।
- অনুমোদিত operator: content/source review, module control, selected operations এবং audit পরিচালনা করতে।

## কেন্দ্রীয় website-এ কী আছে

| অংশ | বর্তমান সুবিধা |
|---|---|
| Home ও Explore | ৫০ tool-এর catalogue, category/search, আলাদা tool identity/logo এবং release status |
| Tool workspace | Tool-specific form, consent, বাস্তব processing বা স্পষ্ট unavailable response |
| `/work` | এই browser-এর temporary history, result reopen, export, selected-facts support ও confirmed clearing |
| Public access | **Visitor login, signup ও profile নেই**; opaque HttpOnly cookie দিয়ে সর্বোচ্চ ২৪ ঘণ্টার owner-isolated session |
| Upload | সর্বোচ্চ ১০ MiB; encrypted ১ MiB chunks, checksum, quota, cancellation/cleanup; production scanner ও private S3 প্রয়োজন |
| Results | নির্দিষ্ট domain-এর হিসাব/notes, JSON/PDF generation; browser PDF verification-এর সীমা report-এ আছে |
| Operator console | `/admin/login`, password ও TOTP MFA, role-based selected controls; কোনো default admin password নেই |
| Background services | Durable inference queue, lease/retry/cancellation, scheduled publishing, expired-visitor cleanup |
| ভাষা ও UI | বাংলা/English switch, responsive components, নিজস্ব ৫০ tool logo এবং reviewed Site Builder; পূর্ণ accessibility/browser certification এখনও হয়নি |

## ৫০টি tool ও বর্তমান সেবা

**সীমিত** মানে নিচের বাস্তব support অংশটি আছে; original advanced ML/data/workflow scope সম্পূর্ণ নয়। **Core বন্ধ** মানে প্রয়োজনীয় verified model/dataset ছাড়া production result বানিয়ে দেখানো হয় না। প্রতিটি tool-এর URL হলো `/tools/<slug>`। বিস্তারিত machine-readable অগ্রগতি: [MODULE_PROGRESS.csv](MODULE_PROGRESS.csv)।

| # | Tool ও slug | এখন কী করে / সীমা | অবস্থা |
|---|---|---|---|
| 1 | [PukurSOS AI](packages/module-registry/catalogue.json) · `pukursos-ai` | নিজের মাপা পুকুরের পানি ও মাছের আচরণের লগ। | সীমিত |
| 2 | [NodiWatch AI](packages/module-registry/catalogue.json) · `nodiwatch-ai` | তারিখসহ দুই ছবি মিলিয়ে দৃশ্যমান পরিবর্তনের পরিসংখ্যান। | সীমিত |
| 3 | [FasalLoss AI](packages/module-registry/catalogue.json) · `fasalloss-ai` | নিজের তথ্য দিয়ে ফসলের ক্ষতির ডায়েরি। | সীমিত |
| 4 | [RoofWise AI](packages/module-registry/catalogue.json) · `roofwise-ai` | ছাদ সংস্কার, খরচ ও বৃষ্টির পানি ব্যবহারের হিসাব। | সীমিত |
| 5 | [NoiseTrace AI](packages/module-registry/catalogue.json) · `noisetrace-ai` | অডিও সিগন্যালের পরিসংখ্যান ও ব্যক্তিগত শব্দের ডায়েরি। | সীমিত |
| 6 | [ChuktiShield AI](packages/module-registry/catalogue.json) · `chuktishield-ai` | চুক্তির লেখা ও দুই খসড়ার পার্থক্য পর্যালোচনা। | সীমিত |
| 7 | [BillDetect AI](packages/module-registry/catalogue.json) · `billdetect-ai` | বিলের হিসাব, ব্যক্তিগত মাসিক ইতিহাস ও বাস্তব OCR draft। | সীমিত |
| 8 | [CareJourney AI](packages/module-registry/catalogue.json) · `carejourney-ai` | নিজের লিখিত চিকিৎসা নির্দেশনার review checklist। | সীমিত |
| 9 | [GoliCoach AI](packages/module-registry/catalogue.json) · `golicoach-ai` | ভিডিও/pose-এর পরীক্ষামূলক স্থানীয় pipeline; production core বন্ধ। | Core বন্ধ |
| 10 | [DokanLens AI](packages/module-registry/catalogue.json) · `dokanlens-ai` | নিশ্চিত stock, expiry, movement history ও reorder হিসাব। | সীমিত |
| 11 | [BazarCompare AI](packages/module-registry/catalogue.json) · `bazarcompare-ai` | নিজের তারিখসহ দেওয়া বাজারদর একই unit-এ তুলনা। | সীমিত |
| 12 | [HomeHazard AI](packages/module-registry/catalogue.json) · `homehazard-ai` | বাড়ির দৃশ্যমান উদ্বেগ ও বিশেষজ্ঞকে দেখানোর নোট। | সীমিত |
| 13 | [WasteWise BD](packages/module-registry/catalogue.json) · `wastewise-bd` | নিজে শনাক্ত করা বর্জ্যের disposal guidance। | সীমিত |
| 14 | [WorkSafe Vision AI](packages/module-registry/catalogue.json) · `worksafe-vision-ai` | কর্মক্ষেত্রের hazard ও corrective-action নথি। | সীমিত |
| 15 | [ClinicCompass BD](packages/module-registry/catalogue.json) · `cliniccompass-bd` | Reviewed directory import/publication/search আছে; অনুমোদিত বাস্তব facility data না থাকায় core বন্ধ। | Core বন্ধ |
| 16 | [LabTrend BD](packages/module-registry/catalogue.json) · `labtrend-bd` | আসল unit ও নিজের reference range-সহ laboratory value tracking। | সীমিত |
| 17 | [DoseClear BD](packages/module-registry/catalogue.json) · `doseclear-bd` | নিশ্চিত prescription text পড়া; dose অনুমান করে না। | সীমিত |
| 18 | [VaccinePath BD](packages/module-registry/catalogue.json) · `vaccinepath-bd` | নথিভুক্ত vaccine date সাজিয়ে clinician review। | সীমিত |
| 19 | [MaternalRoute BD](packages/module-registry/catalogue.json) · `maternalroute-bd` | নিজের তথ্য দিয়ে মাতৃসেবা visit checklist। | সীমিত |
| 20 | [DengueSignal BD](packages/module-registry/catalogue.json) · `denguesignal-bd` | দেওয়া তারিখভিত্তিক dengue count-এর বর্ণনা; forecast নয়। | সীমিত |
| 21 | [RentalFair BD](packages/module-registry/catalogue.json) · `rentalfair-bd` | ভাড়া ও নিয়মিত বাসার খরচের তুলনা। | সীমিত |
| 22 | [RoadFix BD](packages/module-registry/catalogue.json) · `roadfix-bd` | সড়ক মেরামতের evidence packet ও redaction workflow। | সীমিত |
| 23 | [SafeRoute BD](packages/module-registry/catalogue.json) · `saferoute-bd` | নিজের দেওয়া route network ও ঐতিহাসিক নোটের তুলনা। | সীমিত |
| 24 | [WaterGuard BD](packages/module-registry/catalogue.json) · `waterguard-bd` | পানির মাপের সঙ্গে নিজের laboratory reference range তুলনা। | সীমিত |
| 25 | [AgroPrice Planner](packages/module-registry/catalogue.json) · `agroprice-planner` | কৃষি খরচ, break-even ও বিক্রয়মূল্যের scenario হিসাব। | সীমিত |
| 26 | [LivestockCare Log](packages/module-registry/catalogue.json) · `livestockcare-log` | পশুর পরিচর্যা ও মাপা ওজনের পরিবর্তনের লগ। | সীমিত |
| 27 | [CivicForm AI](packages/module-registry/catalogue.json) · `civicform-ai` | নিজের প্রয়োজনীয় কাগজের তালিকা অনুযায়ী form checklist। | সীমিত |
| 28 | [HeatSafe BD](packages/module-registry/catalogue.json) · `heatsafe-bd` | মাপা temperature/humidity থেকে heat-index estimate। | সীমিত |
| 29 | [HospitalBillGuard BD](packages/module-registry/catalogue.json) · `hospitalbillguard-bd` | হাসপাতালের bill যোগফল ও হুবহু duplicate line শনাক্ত। | সীমিত |
| 30 | [SafeBlood Connect BD](packages/module-registry/catalogue.json) · `safeblood-connect-bd` | মেয়াদযুক্ত private blood-request record; live donor matching নয়। | সীমিত |
| 31 | [ShikkhaRAG BD](packages/module-registry/catalogue.json) · `shikkharag-bd` | পাঁচটি original passage থেকে বাস্তব ONNX/BM25 cited retrieval। | সীমিত |
| 32 | [BanglaRead Coach](packages/module-registry/catalogue.json) · `banglaread-coach` | মূল বাংলা passage, comprehension ও reading reflection। | সীমিত |
| 33 | [LandLedger BD](packages/module-registry/catalogue.json) · `landledger-bd` | স্পষ্ট land unit conversion ও দেওয়া document field তুলনা। | সীমিত |
| 34 | [WageGuard BD](packages/module-registry/catalogue.json) · `wageguard-bd` | নিজের নিশ্চিত rate দিয়ে wage scenario হিসাব। | সীমিত |
| 35 | [ShobdoSetu BD](packages/module-registry/catalogue.json) · `shobdosetu-bd` | বড় লেখার Bengali/English phraseboard। | সীমিত |
| 36 | [DrainPulse BD](packages/module-registry/catalogue.json) · `drainpulse-bd` | তারিখভিত্তিক drainage/waterlogging observations তুলনা। | সীমিত |
| 37 | [AgunPath BD](packages/module-registry/catalogue.json) · `agunpath-bd` | দেওয়া exit constraints থেকে fire-drill checklist। | সীমিত |
| 38 | [MatiSense BD](packages/module-registry/catalogue.json) · `matisense-bd` | মাটির মাপ ও দেওয়া laboratory interval সাজানো। | সীমিত |
| 39 | [BiddutPlan BD](packages/module-registry/catalogue.json) · `biddutplan-bd` | যন্ত্রের energy use ও সম্পাদনাযোগ্য বিদ্যুৎ খরচ। | সীমিত |
| 40 | [ScamSignal BD](packages/module-registry/catalogue.json) · `scamsignal-bd` | সন্দেহজনক message/URL-এর লক্ষণ; লিঙ্ক খুলে না। | সীমিত |
| 41 | [OshudhKhoj BD](packages/module-registry/catalogue.json) · `oshudhkhoj-bd` | Reviewed pharmacy import/publication/search আছে; অনুমোদিত হালনাগাদ বাস্তব data না থাকায় core বন্ধ। | Core বন্ধ |
| 42 | [ShebaQueue BD](packages/module-registry/catalogue.json) · `shebaqueue-bd` | সেবা নেওয়ার ধাপ ও document checklist। | সীমিত |
| 43 | [JatraPulse BD](packages/module-registry/catalogue.json) · `jatrapulse-bd` | নিজের দেওয়া travel graph থেকে path খোঁজা। | সীমিত |
| 44 | [SkillBridge BD](packages/module-registry/catalogue.json) · `skillbridge-bd` | দেওয়া skill-কে নিজের job/course checklist-এর সঙ্গে মিলানো। | সীমিত |
| 45 | [FoodLabel Lens BD](packages/module-registry/catalogue.json) · `foodlabel-lens-bd` | লেবেলের লেখা ও সরাসরি নাম থাকা allergen চিহ্নিত করা। | সীমিত |
| 46 | [OdhikarSetu BD](packages/module-registry/catalogue.json) · `odhikarsetu-bd` | নির্বাচিত support programme-এর প্রশ্ন ও কাগজ প্রস্তুতি। | সীমিত |
| 47 | [RepairRight BD](packages/module-registry/catalogue.json) · `repairright-bd` | মেরামত বনাম replacement খরচের scenario। | সীমিত |
| 48 | [JhorAlert BD](packages/module-registry/catalogue.json) · `jhoralert-bd` | নিজের দেওয়া weather bulletin ও source-time সংরক্ষণ/তুলনা। | সীমিত |
| 49 | [SchoolRoute BD](packages/module-registry/catalogue.json) · `schoolroute-bd` | অভিভাবক-পর্যালোচিত school-area hazard notes; child GPS নয়। | সীমিত |
| 50 | [HishabBondhu BD](packages/module-registry/catalogue.json) · `hishabbondhu-bd` | Cash in/out, receivable ও জানা business cost reconciliation। | সীমিত |

## বাস্তব AI/API processing

| Runtime | বাস্তব implementation | সীমা |
|---|---|---|
| OCR | Tesseract Bengali/English; বিলের editable text/box/confidence draft | OCR ভুল হতে পারে; user confirmation দরকার; identifier hiding সম্পূর্ণ PII redaction নয় |
| NLP/RAG | Quantized multilingual MiniLM ONNX embeddings + BM25 + source passage citation | পাঁচটি project-authored CC0 starter passage; extractive retrieval, generative LLM বা official NCTB corpus নয় |
| Computer vision | OpenCV registration ও image-difference statistics | Validated erosion/crop/water/PPE classifier নয় |
| Private anomaly model | Opt-in confirmed non-DEMO bill history থেকে IsolationForest → ONNX, owner-specific encrypted model | অন্তত ২৫ eligible row; consent withdrawal invalidates derived model; production train/predict বন্ধ |
| Speech | Optional local quantized Whisper adapter | Bengali holdout অসম্পূর্ণ; production speech বন্ধ |
| Pose/video | Optional local BlazePose/MediaPipe ৩৩ landmark pipeline, 2D angles ও skeleton replay | Opt-in experimental evaluation; cricket alignment/coach review/BD holdout অসম্পূর্ণ; production বন্ধ |
| Reviewed directories | ClinicCompass/OshudhKhoj-এর typed import, দুই reviewer, independent publication, rollback/revocation, real ONNX/BM25 search | বাস্তব approved data নেই; facility ৯০ দিন/pharmacy ২৪ ঘণ্টার freshness gate; [pipeline details](docs/DIRECTORY_PIPELINE.md) |
| Other calculations | Decimal bill/cost/unit/stock/network/checklist engines | যেখানে deterministic হিসাব, সেটিকে trained ML prediction হিসেবে দেখানো হয় না |

কোনো paid AI API key ছাড়াই documented local OCR/retrieval/support অংশ চালানো যায়। Missing model বা unavailable service-এর জন্য API fake result তৈরি করে না।

## Super Admin / operator permissions

| Role | বাস্তব permission boundary |
|---|---|
| `super_admin` | Implemented operator controls; private owner data পড়ার blanket bypass নেই |
| `content_editor` | CMS draft/review/publish |
| `dataset_reviewer` | Candidate source, dual asset rights review, typed directory preview/publication/withdrawal ও selected import-job controls |
| `model_operator` | Model availability/inspection; evaluation gate bypass নয় |
| `module_manager` | Module availability/feature controls |
| `support_agent` | Owner-authorized selected-facts support snapshot |
| `auditor` | Implemented audit views |
| `guest` | Current anonymous owner scope |
| `user`, `guardian`, `organization_staff` | Preserved/reserved role names; নতুন public account/organization tenancy চালু নেই |

Operator MFA-তে বাংলা/ASCII অঙ্ক গ্রহণ করা হয়; অঙ্কের লিপি বদলে একই code পুনরায় ব্যবহার করা যায় না। Malformed Unicode transport/CSRF token 403 পায়।

Privileged operation-এ recent MFA লাগে। [Typed Site Builder](docs/SITE_BUILDER.md)-এ logo/favicon, theme, section order, pages, field labels/help/placeholders, নির্বাচিত locale/category ও review/publish/schedule/rollback আছে। Arbitrary page/component layout, advanced moderation, guardian/organization tenancy এবং পূর্ণ model lifecycle এখনও অসম্পূর্ণ।

ClinicCompass/OshudhKhoj-এর `/admin/directories` console ও [directory pipeline](docs/DIRECTORY_PIPELINE.md) দিয়ে অনুমোদিত public nonpersonal records যাচাই/প্রকাশ/প্রত্যাহার করা যায়। বাস্তব dataset ছাড়া কোনো demo record চালু হয় না।

## Hosting ছাড়াই preview

### Option A — GitHub Codespaces, browser-এ private preview

[Open in Codespaces](https://codespaces.new/EMON-721/Mouchak-AI-platform) → create/open a codespace → setup শেষ হলে terminal-এ:

```bash
pnpm dev --host 0.0.0.0
```

**Ports → 3000 → Open in Browser**। Visibility **Private** রাখুন; private API port 8000 forward করবেন না। `.devcontainer/` Python 3.12, Node 24, OCR/FFmpeg এবং checksum-controlled baseline models প্রস্তুত করে। Website ও API একই codespace-এ চলে; origin স্বয়ংক্রিয়ভাবে forwarded HTTPS URL-এর সঙ্গে মেলে।

এটি public production deployment নয়। GitHub account entitlement/usage quota বা billing প্রযোজ্য হতে পারে; এই repository কোনো codespace বা paid resource নিজে তৈরি করে না। Codespaces provisioning এই checkpoint-এর CI-তে চালানো হয়নি। Browser-friendly code editor `github.dev` একা server চালায় না।

### Option B — local Docker preview

Docker Engine/Desktop ও Compose plugin প্রস্তুত থাকলে:

```bash
docker compose -f deploy/compose.local.yaml up --build
```

Open `http://localhost:3000`। PostgreSQL/Render/SMTP account/API key লাগে না। Actual API, OCR/model-init, inference, scheduler ও retention service ব্যবহৃত হয়। SQLite ও encrypted files শুধু local preview volume-এ থাকে। Development scanner status unscanned হলে সেটি production-scanned হিসেবে দেখানো হয় না। শুধু নিজের test inputs ব্যবহার করুন।

বন্ধ করতে `docker compose -f deploy/compose.local.yaml down`। `down -v` volume/data মুছে দেয়; প্রয়োজন ছাড়া ব্যবহার করবেন না।

### Option C — native development

পূর্ণ runtime-এর tested target: **Node 24, pnpm 11.25.0, Python 3.12, Tesseract Bengali/English এবং FFmpeg**। Windows-এ [preview guide](docs/PREVIEW.md)-এর PowerShell পথ বা WSL/Docker ব্যবহার করুন।

```bash
pnpm install --frozen-lockfile
python3 -m venv .venv
.venv/bin/python -m pip install -r requirements-python.txt
.venv/bin/python scripts/download-models.py
pnpm dev
```

Open `http://localhost:3000`। Development wrapper API ready হওয়া পর্যন্ত অপেক্ষা করে, এরপর website, scheduler/retention এবং opt-in queue worker চালায়। Preview settings ও real processing verification: [docs/PREVIEW.md](docs/PREVIEW.md)।

## পরে যেকোনো সামঞ্জস্যপূর্ণ platform-এ deployment

```bash
pnpm build
pnpm start
```

এই সাধারণ commands এখন canonical **Next.js Node server** চালায়। `deploy/Dockerfile.web` standalone web image; `deploy/Dockerfile.api` private Python image। API `PORT` environment variable মেনে চলে। Provider-specific Cloudflare build ঐচ্ছিক `build:sites`/`start:sites` নামে preserved; কোনো Cloudflare account দরকার নেই।

পূর্ণ future production topology: [deploy/compose.yaml](deploy/compose.yaml)। আলাদা frontend থাকলে backend-only [deploy/compose.backend.yaml](deploy/compose.backend.yaml)। Private database/S3/SMTP/secrets, model/scanner initialization, worker, TLS ও verified migrations configure করতে হবে। Static-only hosts বা small edge isolates-এ এই Python/ONNX stack চলবে না; “যেকোনো platform” মানে এই runtimes ও resources সমর্থন করা platform।

**বর্তমানে কোনো production deploy চালানো হচ্ছে না।** Netlify configuration একটি optional adapter মাত্র। [Portable deployment runbook](docs/DEPLOYMENT.md) দেখুন।

## Environment ও operator setup

`.env.example`-এ documented keys আছে; **নিজের real `.env` Git-এ যাবে না**। Development-এ private local key তৈরি হয়। Existing encrypted data থাকলে key বদলালে data recovery ভেঙে যেতে পারে।

Production-এ প্রয়োজন: stable `DATA_ENCRYPTION_KEY`, matching server-only `PRIVATE_API_TOKEN` (৩২–৫১২ ASCII characters), verified-TLS PostgreSQL URLs with separate API/inference/scheduler/retention roles, private S3 credentials/region, current malware signatures, SMTP, exact HTTPS `PUBLIC_ORIGIN`, domain ও backup/key recovery। এগুলো frontend-এর `NEXT_PUBLIC_*` variable-এ রাখবেন না।

Local operator তৈরি করতে:

```bash
.venv/bin/python -m services.model_worker.manage create-admin --email YOUR-EMAIL
```

Password prompt-এ দিন, তারপর `/admin/login` থেকে sign in করে MFA enroll/verify করুন। কোনো default credential বা anonymous admin bypass নেই। Production database-এ additive SQL provisioning-এর জন্য [backend operations](docs/BACKEND_OPERATIONS.md) অনুসরণ করুন; SQLite development migration production provisioning-এর বিকল্প নয়।

## API ও source map

[সম্পূর্ণ implemented route index](docs/API_REFERENCE.md)। Main families: `/api/session`, `/api/modules`, `/api/tools/{slug}/jobs`, `/api/jobs`, `/api/runs`, `/api/uploads`, `/api/assets`, `/api/bills`, `/api/workspaces`, `/api/privacy/export`, `/api/admin/*`। Website proxy private token server-side যোগ করে; owner/MFA/CSRF checks backend-এ enforce হয়।

| Directory | দায়িত্ব |
|---|---|
| `app/`, `components/mouchak/` | Central Next.js UI ও same-origin API proxy |
| `services/model_worker/` | FastAPI, domain/inference, encryption/authorization, queue/operations CLI |
| `packages/module-registry/` | ৫০ module, form, model candidate ও source registry |
| `database/migrations/` | ০০১–০০৬ additive PostgreSQL migration, RLS ও role grants |
| `data/authored/`, `data/legacy/` | ছোট original/attributed starter content; private production dataset নয় |
| `requirements/original-kit/` | সম্পূর্ণ অপরিবর্তিত original ৭৭৮-file kit |
| `deploy/`, `.devcontainer/` | Portable production/local templates ও private developer preview |
| `tests/`, `scripts/`, `.github/workflows/` | Regression, SQL/inference/integration, publication checks ও CI |
| `docs/audit/` | Historical test evidence; date/source/result মিলিয়ে পড়তে হবে |

## যাচাই

```bash
pnpm typecheck
pnpm lint
pnpm test:portable
node scripts/test-site-presentation.mjs
python3 scripts/check-public-source.py --history
python3 scripts/check-registry.py
python3 scripts/generate-api-reference.py --check
.venv/bin/python -m pytest tests --ignore=tests/verify_postgres.py -q
node scripts/test-postgres.mjs
node scripts/test-collaboration-postgres.mjs
node scripts/test-async-postgres.mjs
pnpm test:transport
pnpm build
```

Model-dependent tests-এর আগে baseline models এবং pose test fixture acquisition দরকার। CI এই steps চালায় এবং actual isolated Docker PostgreSQL/S3/TLS/scanner/inference integration চালায়। বর্তমান checkpoint-এর ফল [implementation report](IMPLEMENTATION_REPORT.md)-এ আছে; পুরোনো সংখ্যা নতুন run-এর প্রমাণ নয়। Full original ৪৩০ acceptance scenario এখনও সব passed নয়।

সর্বশেষ tested runtime: `6c9a84df38e55a378f86450b09cc29f751912786`; [CI 40922696790](https://github.com/EMON-721/Mouchak-AI-platform/actions/runs/40922696790)-এর platform ও private-stack দুটো job সফল। **৪১৫টি Python test ও ১৭টি subtest** (110.31 সেকেন্ড), actual presentation-helper tests, type/lint/build, SQL/RLS, ৭৭৮ original file-এর checksum, selected-pattern source/history scan (০ finding; ১,২৫৫ historical blob), বাস্তব TLS/database/storage/model/directory ও reviewed Site Builder publication/scheduler/rollback পাস করেছে। Actual standalone web image-এ narrow same-origin preview framing, private noindex ও absent-backend 503-ও পাস করেছে।

সম্পূর্ণ ৫০-tool advanced acceptance পাস দাবি করা হয়নি। বর্তমান browser-এ বাংলা/English UI, ৫০ tool catalogue ও filtering দেখা হয়েছে। Visitor-session origin mismatch মেরামতের পর browser URL policy পুনরায় navigation আটকে দিয়েছে; পূর্ণ inference/admin/MFA, তিন viewport ও PDF acceptance এখনও unverified। [সর্বশেষ implementation report](IMPLEMENTATION_REPORT.md) ও [নির্দিষ্ট evidence/limitations](docs/audit/site-builder-release-20261029.json) দেখুন।

## Dataset, privacy ও public repository

- ২৪৪টি Bangladesh-focused candidate source registry entry আছে; এগুলো approved/downloaded dataset নয়। Restricted government data scrape বা fabricated real-world observation ব্যবহার করা হয়নি।
- User input private; processing consent ও training/reuse consent এক নয়। Models/exports/visitor records owner-isolated।
- Credentials, uploads, runtime database, trained weights, recovery archive, CLIXML/DPAPI secret export বা password-সহ screenshot source-এ রাখা যাবে না। Current source ও Git history-তে selected-pattern publication scan আছে; সেটি সব ধরনের secret/PII বা rights-এর certification নয়।
- Exposed credential provider-এ rotate/revoke করতে হবে; file মুছলে secret revoke হয় না। [SECURITY.md](SECURITY.md)।
- Third-party/source/model licence আলাদা। Public visibility নিজে blanket open-source licence দেয় না। [THIRD_PARTY_NOTICES.md](THIRD_PARTY_NOTICES.md) ও [provenance](docs/DATA_AND_MODEL_PROVENANCE.md) দেখুন।

## কী বাকি

Bangladesh-labelled/evaluated advanced classifiers, full generative/domain RAG, approved facility/pharmacy/live directories, forecasting, full original clinical/legal/cricket workflows, remaining admin/model-lifecycle controls, accessibility/browser matrix ও provider-level backup/restore/load validation বাকি। Infrastructure থাকলেও dataset/model/expert review ছাড়া এগুলোকে ready বলা যাবে না। Original requirements ও acceptance traceability অক্ষত আছে।

**এই repository-তে বর্তমান implemented frontend, backend, API, database migrations, real inference adapters, worker, tests ও runbooks সংরক্ষিত আছে। সম্পূর্ণ advanced ৫০-tool production release দাবি করা হচ্ছে না।**
