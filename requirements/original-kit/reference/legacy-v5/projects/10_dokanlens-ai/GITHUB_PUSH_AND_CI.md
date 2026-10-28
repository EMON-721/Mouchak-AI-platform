# GitHub repository plan (32 distinct repos, V5)

Owner must authorize GitHub connection and choose visibility. The package includes *prompts and supporting data, not 32 implemented websites*. Use one existing repository per already built project; never overwrite/recreate or force-push. New repositories only after working app code and tests exist.

For each:
1. Open `MASTER_PROMPT_V5.md` in a dedicated ChatGPT Work task (attach the full project folder for seeds).
2. Ask Work to read existing source repo if marked `existing_upgrade`. Audit, back up and create reversible migrations.
3. Implement functioning licensed model inference service and `/api/ai/health`, not a mocked AI label.
4. Verify dataset rights, source URLs, evaluation and real tests. Do not push private data or weights unless redistribution is allowed.
5. Authenticated GitHub access only; choose owner and visibility; create or update correct remote; push feature branch and open PR; verify actual SHA.
6. GitHub Actions CI should run lint, typecheck, unit/API tests, build, and a separate model-smoke job (mock-free, weights downloaded only when license permits and resources available). Explain if a costly ML job cannot run on GitHub hosted runners.
7. Merge only with explicit release authority. Deploy UI to Vercel and inference separately where required. No fake deployment success.

Repo slug: `dokanlens-ai`. Existing site: `True`. Never include uploads, keys, donor lists or private documents.
