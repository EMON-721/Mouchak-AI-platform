# HospitalBillGuard BD — V4 self-contained Work Prompt

**Status:** Detailed, standalone build prompt + original curated seed fixtures, NOT a built website.

1. Attach or paste `MASTER_PROMPT_V4.md` into a separate ChatGPT Work task.
2. The prompt includes its own source links, modules, User/Admin architecture, AI tasks, prior V2 prompt, tests and mandatory GitHub process. No common/shared prompt to paste.
3. `seed/SEED_TAXONOMY.csv/json` is 18 authored vocabulary labels, **NOT** real collected Bangladesh observations.
4. `seed/EVALUATION_CASES.json` has 14 synthetic reliability/security test scenarios.
5. `DATASET_SOURCES.json` has 3 external source candidates; permissions and available files need verification.
6. `UI_PREVIEW.svg` is a prior conceptual wireframe, not a screenshot of built software.
7. With owner-authorized GitHub connection, Work should create/run/test/push the actual code; absent connection, report push not done.

## About (BN)
হাসপাতাল বা ডায়াগনস্টিক সেন্টারের বিলের ছবি/সংখ্যা দিয়ে পরিষ্কার চার্জ তালিকা, মোট টাকা যাচাই এবং অভিযোগ/প্রশ্নের নথি তৈরি করবে—ভুল বিল নিশ্চিত ঘোষণার বদলে প্রমাণ দেখাবে।

## Core product modules
- Invoice OCR and line-item edit table
- Arithmetic validation and repeated-charge check
- Patient-identifying details redaction
- Missing official tariff status warnings
- Evidence-based provider questions
- Private PDF summary
