# User features — DokanLens AI

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

# Specialized Admin features

1. SKU ontology manager with merge/split aliases, variant packaging, local product term moderation and source provenance
2. Model annotation studio for owner-opted-in shelf crops with bounding boxes and label versions, anonymization and retention
3. Store abuse / fraud suspicion moderation limited to platform fraud; no unrestricted owner transactions or private photos
4. Feature flags OCR/detection/alerts per shop plan, rollout canary, per-model errors and consent audit
5. Inventory transaction dispute workflow and admin-approved generic fixes with shop-owner confirmation
