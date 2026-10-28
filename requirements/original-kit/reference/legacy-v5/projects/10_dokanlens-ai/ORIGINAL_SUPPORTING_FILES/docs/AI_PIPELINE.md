# AI/ML production plan — DokanLens AI

1. Upload photo => compress/rotate/private validation => detection or OCR model candidate => crop/word box => candidate product match => user correction => stable stock transaction
2. Barcode scan decodes string but never automatically asserts SKU identity from global barcode DB; compare with owner-entered mapping; unknown remains unknown
3. Catalogue semantic search: Bangla English aliases and fuzzy matching, alias collision dialog; pack unit interpretation and variant differentiation
4. Visual object detection: integrate open-source compatible model only after model license and local shelf evaluation; not a random rectangle overlay or fake “99%”; support staged per-shop labeled image set
5. Receipt/expiry OCR: date parsing handles DD-MM-YYYY, printed abbreviations, Bangla digits, ambiguous labels and manufacture/expiry difference; require human verify before alerts
6. Stock integer/decimal arithmetic invariant and optimistic locking; track damaged/expired/returns separately; no negative saleable quantity without explicit backorder flag
7. Demand trend: trailing-day moving average / exponential smoothing based on shop history (minimum sample count), holdout MAE/MAPE where meaningful, no manufactured projections
8. Optional anomaly detection: sudden stock gap from ledger with audit trail, not fraud accusation; explain why flagged

No performance claims before live evaluation and model card.
