# Mouchak AI — One GitHub Monorepo Handoff

- Use ONE user-created GitHub repo named `mouchak-ai` (suggested; repository creation not claimed).
- Respect the user's four already created repositories. Inspect them only after the user grants permission. Record current branch, upstream, commit SHA, migrations and data backups before merging any app.
- Never rename or force-push an existing public repository without explicit permission.
- Monorepo directories: `apps/web`, `services/inference`, `packages/ui`, `packages/auth`, `packages/module-registry`, `packages/i18n`, `packages/data-provenance`, `database/migrations`, `modules/`, `public/logos`, `tests/`.
- Transfer original 35 existing configuration with stable IDs, append 36–50 with a disabled feature flag, migrate schema additively, preserve user data, and enable modules after real model+licensing QA.
- Before GitHub remote push: typecheck, lint, DB migration check, security scan, unit tests, source license manifest, integration tests, E2E accessibility and Bengali translations.
- Push only via user-authorized GitHub connection; log actual repository URL and commit SHA. If unavailable, supply a local Git-ready zip and precise instructions, never claim a remote push.
- Vercel may host the frontend, but large persistent ML models require a separately authorized long-lived inference worker; a separate internal worker does NOT constitute a second user website.
