# Selected ports from local V3 snapshots

This continuation begins at preserved commit `e16e2706d2811b2e3408476a880ccf66bbc66594`. No earlier platform work was regenerated. Three user-owned static deployment archives already present in the workspace supplied the source. All 25 files are preserved byte-for-byte under `reference/legacy-snapshots/`, with hashes in `docs/audit/legacy-snapshot-manifest.json`. They are source references, not active separate websites or a live database backup.

| Tool | Newly integrated into the central workspace | Preserved but not yet ported in full |
|---|---|---|
| BanglaRead | 12 attributed passages, word taps, optional comprehension reflection, central private save/export/delete | Spaced repetition/grapheme helpers, complete legacy progress/admin/export UI and child/guardian continuity; no evaluated speech model |
| DokanLens | Counted stock and exact paisa costs, sale/purchase/return/damage/supplier-return movements, negative-stock protection, item revisions, owner-scoped retries, private history and observed velocity threshold | Full product catalogue/import mapping UI, expiry ambiguity parser, shop customization, complete reports/admin workflows and live records |
| BazarCompare | 81-entry original dictionary, dated private baskets, exact unit/price comparison, grade/origin/retail-wholesale matching, stale/future/flagged rejection and explicit missing prices | Complete import quarantine UI, full legacy content/admin/report workflows, historical records and approved live feeds |

`tests/test_resume_workflows.py` executes the preserved pure JavaScript engines using Node through `scripts/legacy-golden.mjs`, then compares the selected behavior with the central Python/API results. This is not browser automation or a claim of full feature parity. Strict central validation deliberately rejects invalid selected indices and fractional counted stock. Private data is held centrally with owner checks, consent, encrypted payloads and account/workspace cascading deletion. Local browser accounts and sessions are not copied or automatically linked.

Freshness uses elapsed time from the observation day's midnight in Asia/Dhaka, preserving the original boundary behavior: a seven-day-old observation is expired after midnight on day seven. Current-day stock movements record the actual timestamp; historical dates use noon Asia/Dhaka because users provide only a calendar day. Velocity requires at least five sales on three distinct days within 28 days. It is descriptive net sales per observed day, not a forecast. History displays at most the latest 1,000 events and declares truncation; the velocity query independently examines the 28-day window and abstains above 10,000 records.

No government prices, stock, curriculum alignment, model accuracy or production migration is fabricated. The existing original requirements and 430 acceptance cases remain unchanged and incomplete.
