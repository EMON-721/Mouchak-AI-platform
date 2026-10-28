# Apply V3 safely to existing DokanLens AI site

1. Open a ChatGPT Work task with the **EXISTING** GitHub project connected; upload this project folder or ZIP.
2. Provide `MASTER_PROMPT_UPGRADE_V3.md` (self-contained, old prompt appended) as instruction.
3. Do not create a replacement website/repo. Audit original UI, auth, data and deployment first.
4. Idempotently insert `data/seed` entries; they are curated original taxonomy/training examples, NOT official government or user data.
5. Use `data/sources.json` to implement rights-aware actual import pathways.
6. Run database/test checks, review PR and merge only when authorized.
