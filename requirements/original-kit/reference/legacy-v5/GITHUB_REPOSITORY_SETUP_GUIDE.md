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

# GitHub example (run *only* inside a fully built site repo, with explicit owner permission)

```bash
gh auth status
git status
git remote -v
npm ci && npm run build && npm run test
# after audit, no local private uploads or credentials
git switch -c upgrade/v5-real-models   # existing repo only, if branch doesn't already exist
git add -A
git diff --cached --check
git commit -m "feat: real Bangladesh AI model, datasets and admin workflows"
git push -u origin upgrade/v5-real-models
gh pr create --fill
```

For a brand-new site: obtain chosen owner and visibility, create remotely via GitHub connector or `gh repo create OWNER/REPO --private --source=. --remote=origin --push` only AFTER code was actually built, tested, and ownership/visibility approved. Substitute `--public` only if expressly chosen. Record actual GitHub URL and commit SHA.
