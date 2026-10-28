# QA Acceptance — HospitalBillGuard BD

Minimum: 30 unit tests, 12 integration, 8 end-to-end (targets to implement, not tests already run).

- [ ] TEST-001: স্বাভাবিক ইনপুট — ব্যবহারকারী প্রথমবার কাজ সম্পন্ন করে; source limitation দৃশ্যমান
- [ ] TEST-002: অসম্পূর্ণ ইনপুট — সব প্রয়োজনীয় অনুপস্থিত মান বাংলায় চিহ্নিত; অনুমান নয়
- [ ] TEST-003: বাংলা সংখ্যা — বাংলা ডিজিটকে সঠিক সংখ্যায় normalise; ইউনিট ধরে রাখা
- [ ] TEST-004: দ্ব্যর্থক টেক্সট — review step; low-confidence abstain
- [ ] TEST-005: অতিরিক্ত বড় ফাইল — safe rejection; clear limit + retry
- [ ] TEST-006: অনুমতি না থাকা ডেটা — সুস্পষ্ট unavailable; ভুয়া live data নয়
- [ ] TEST-007: ডেটাসেটের পুরোনো সংস্করণ — as-of এবং downgrade/report alert
- [ ] TEST-008: অনুমতি ছাড়া অন্যের ডেটা — 403 deny; audit event
- [ ] TEST-009: admin data quarantine — publish disabled until license reviewed
- [ ] TEST-010: বেঠিক ইউনিট — validation rejection; কোনো মিথ্যা পরামর্শ নয়
- [ ] TEST-011: AI model বন্ধ — simple rule/manual fallback and honest badge
- [ ] TEST-012: অ্যাডমিন কন্টেন্ট rollback — previous published version restored with log
- [ ] TEST-013: ডেটা মুছে ফেলা — data removed according to retention policy, verified
- [ ] TEST-014: প্রমাণ ছাড়া আত্মবিশ্বাসী দাবি — explain uncertainty and citation requirement

- [ ] Real user action fully works without unauthorized API credentials, or honestly marks the feature unavailable.
- [ ] Real and synthetic data are visibly separated.
- [ ] User/admin permissions verified with denied cross-user access.
- [ ] Bangladesh sources/license provenance clear.
- [ ] No secrets/privacy leaks in Git history.
- [ ] GitHub push only claimed if remote confirmed.
