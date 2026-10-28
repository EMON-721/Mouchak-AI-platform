# CareJourney AI — V4 self-contained Work Prompt

**Status:** Detailed, standalone build prompt + original curated seed fixtures, NOT a built website.

1. Attach or paste `MASTER_PROMPT_V4.md` into a separate ChatGPT Work task.
2. The prompt includes its own source links, modules, User/Admin architecture, AI tasks, prior V2 prompt, tests and mandatory GitHub process. No common/shared prompt to paste.
3. `seed/SEED_TAXONOMY.csv/json` is 18 authored vocabulary labels, **NOT** real collected Bangladesh observations.
4. `seed/EVALUATION_CASES.json` has 14 synthetic reliability/security test scenarios.
5. `DATASET_SOURCES.json` has 3 external source candidates; permissions and available files need verification.
6. `UI_PREVIEW.svg` is a prior conceptual wireframe, not a screenshot of built software.
7. With owner-authorized GitHub connection, Work should create/run/test/push the actual code; absent connection, report push not done.

## About (BN)
ডাক্তার দেখানোর পর নিজের নোট/অনুমতিসহ অডিও থেকে ফলো-আপ কাজ ও ডাক্তারের কাছে জিজ্ঞেস করার প্রশ্নের তালিকা তৈরি করবে; চিকিৎসা বদলাবে না।

## Core product modules
- Doctor visit timeline and notes
- Consent-aware optional Bengali speech transcription
- Task extraction with user confirmation
- Family shared view with explicit permission
- Medication instruction uncertainty gate
- Visit question composer
