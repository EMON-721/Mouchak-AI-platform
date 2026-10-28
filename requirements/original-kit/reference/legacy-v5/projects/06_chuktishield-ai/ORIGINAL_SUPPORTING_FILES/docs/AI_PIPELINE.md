# AI/ML production plan — ChuktiShield AI

1. Bangla/English document OCR with page offsets, table-aware extraction, layout and PII recognition/redaction; confidence per span
2. Clause segmentation and label assignment from curated taxonomy, regex/deterministic first then ML classifier with held-out labeled data, never treat labels as legal findings
3. Extract critical terms into JSON schema: parties, dates, BDT payment, deposit, late charges, jurisdiction, notice period, termination, signature conditions, with direct page evidence
4. Simple rule-based term checks distinguish missing clause vs cannot read vs explicitly restrictive text; all explanations cite the literal user document segment
5. Legal RAG: indexed official Bangladesh Acts filtered by exact version/effective date/jurisdiction and source section, cite bdlaws URL and section ID, return abstention if relevant law not ingested or stale
6. Protection against uploaded prompt injection (“ignore rules”) and malicious PDF; RAG corpus rights review, refresh monitoring and human legal expert acceptance before public legal guidance
7. Comparative semantic diff reports clauses added/removed/modified, confidence and original text side-by-side; never invent clauses
8. Quality: span extraction F1, OCR CER, clause macro-F1, citation precision, hallucination tests, abstention, version correctness on actual labeled held-out eval

No performance claims before live evaluation and model card.
