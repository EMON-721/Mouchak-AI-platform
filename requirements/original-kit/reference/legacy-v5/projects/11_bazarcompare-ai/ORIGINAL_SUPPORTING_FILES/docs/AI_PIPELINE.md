# AI/ML production plan — BazarCompare AI

1. OCR handwritten/printed list => detect product and quantity candidates => user correction; never trust OCR price without user validation
2. Bangla spelling normalization, aliases and phonetic search; product entity linking to stable ontology id; “আলু” not mistaken for “পেঁয়াজ”
3. Price type semantics: wholesale/retail, location, grade, origin, units, and observation_date must match before comparison
4. Unit pricing formula library (kg/g, l/ml, dozen/piece); uncertainty range for range price, never treat range as precise observed price
5. Outlier screening using product-market-season price history where enough approved actual observations; flag not delete outliers silently
6. Time-series on verified price records only; if insufficient data disable forecast button with explanation and alternatives
7. Sources ranks: official report / verified store / moderated crowd / unverified user input; explicit age of data and licensing audit
8. RAG about commodity info or consumer complaint process optionally built from rights-cleared official texts; never use LLM to invent current prices

No performance claims before live evaluation and model card.
