# Private BillDetect continuation

This adds a real, owner-specific pipeline to the existing bill arithmetic tool. It does **not** complete the original BillDetect scope, validate government tariffs, detect fraud or forecast future bills. Public accounts remain removed. Private histories and artifacts share the expiring cookie scope; they are not permanent accounts. Default visitor expiry is 24 hours.

## Implemented behavior

- A dedicated bilingual workbench supports electricity, gas, water and internet bills. It saves, edits, deletes and exports confirmed private monthly records, with separate processing and optional training consent. Bengali numerals are normalized. Duplicate months in a workspace/type are rejected. At most 500 records are stored per series.
- Charge arithmetic compares the entered total to consumption + fixed + tax + adjustments using decimal arithmetic. A discrepancy is not a wrong-charge or fraud verdict. No official tariff database is connected.
- Actual Tesseract Bengali/English OCR produces word boxes and raw engine confidence in a single text/TSV pass. One selected PDF page is rendered per extraction; resolution bounds apply before rendering. Unambiguous labelled numeric candidates become an editable draft. Unknown or multiple amounts are not silently chosen. The user must confirm every value.
- Detected account/customer/meter identifier lines are hidden heuristically. This is **not complete PII redaction**; names, addresses, missed identifiers and OCR errors may remain in private output. Original document/field side-by-side editing and comprehensive redaction remain incomplete.
- History values are application-encrypted, with owner and workspace authorization in the API and PostgreSQL RLS. Migration 006 adds `bill_history_entries` and `bill_personal_models`; all previous tables remain intact. Privileged operator status alone does not permit viewing another visitor's private bills.

## Real experimental model

In a nonproduction evaluation environment, an owner can separately consent to fit a genuine `sklearn.IsolationForest` using at least 25 individually consented, confirmed, non-DEMO records from the same workspace/type. At least five feature vectors must differ. These remain **owner assertions**, not independently verified utility observations. Training never joins other owners' records.

The four features are log1p units/day, log1p consumption BDT/day, log1p stated BDT/day and billing days/31. The forest has 100 trees, random seed 42 and `contamination="auto"`. `skl2onnx` exports an ONNX artifact; the API executes the actual artifact with ONNX Runtime CPU. No pickle/joblib deserialization is used. Artifact size is bounded, SHA-256 verified and bytes encrypted in the database.

Before persistence, native and ONNX decision scores must differ by less than 1e-5. This export parity check proves serialization mechanics, **not predictive accuracy**. Model cards retain package versions, feature definitions, row IDs, baseline digest, consent version, timestamps, checksum and unvalidated status. Unchanged baselines reuse the artifact. Edits, row deletion or training-consent withdrawal erase the active derived model. Backup expiry is a separate operational requirement.

A prediction produces an encrypted normal run that can be reopened and exported. Scores are exploratory deviations against that owner's history. There is no calibrated probability, Bangladesh holdout benchmark, official tariff validation, guaranteed error detection or future-bill prediction.

**Production training and prediction return HTTP 503.** The UI explains this gate. History/arithmetic remain available. An admin tool flag cannot bypass the missing Bangladesh evaluation/release review. DEMO data are visibly labelled and excluded from fitting.

## Verification evidence

- `tests/test_bills.py`: real fitted/exported ONNX inference, encryption/ownership, numeric validation, consent/revocation/invalidation, integrity, actual owned-image OCR and production gate checks.
- `tests/test_backend_configuration.py`: strict X.509 fixture verification, verified HTTPS S3 SDK configuration and provisioning preflight rejection.
- Browser: Bangla-digit DEMO entry 100 units, consumption 1000, fixed 50, tax 75, stated 1150 → computed 1125 and difference 25. Reload retained history; eligible training count remained 0/25. `docs/audit/bill-browser-history.jpg` records this development-only check. No fixture was added to a shared dataset or fitted as real billing data.
- Full production-stack network integration is tracked independently in `docs/BACKEND_OPERATIONS.md` and GitHub CI. Browser OCR upload, full responsive/accessibility matrix, browser PDF export and original BillDetect acceptance remain unverified.
