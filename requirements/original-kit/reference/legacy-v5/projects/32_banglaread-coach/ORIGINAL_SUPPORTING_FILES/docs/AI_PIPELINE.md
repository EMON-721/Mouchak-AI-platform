# AI/ML production plan — BanglaRead Coach

1. Deterministic tokenization + Bangla Unicode normalization; grapheme clusters (conjunct vowels signs) and word-level highlighting; test Bengali numerals and ZWJ/ZWNJ
2. Rule-based grapheme and syllable segmentation with teacher-reviewed exception lexicon; do not pretend it is a complete linguistic morphological analyzer
3. Word frequency/leitner SRS; transparent adaptive scheduling formula using review history, not falsely claiming a trained ML model
4. Optional ASR integration: evaluate Whisper or permissively licensed Bengali model on held-out Bengali speech with speaker-disjoint train/test; never equate WER with speech sound diagnosis
5. Acoustic input quality gate (silence clipping noise VAD); high uncertainty returns “শব্দটি পরিষ্কার শোনা যায়নি”, offer rerecord, manual tap mode always available
6. Alignment per word with timestamps if model supports; score display only supported dimensions (words detected/missed with uncertainty), do not calculate fabricated phoneme diagnosis
7. Language variation fairness test by region/age/gender only with consent, avoid child voice datasets without guardian and lawful basis
8. ML metrics: WER, CER, word recall, manual reviewer agreement, failure rates on noisy audio; show metrics only after real measured eval

No performance claims before live evaluation and model card.
