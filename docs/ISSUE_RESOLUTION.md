# Issue resolution and exact remaining actions

This is the continuation of the existing platform, not a new homepage build. Public login/signup/profile remain removed. Operators retain role and MFA protection. All original-kit files remain unchanged.

| Issue | Completed work | Remaining restriction |
|---|---|---|
| GitHub 403 | Verified the supplied repository, preserved its initial commit and prepared the full source/history branch | Connected integration still rejects blob writes; no push or remote CI succeeded |
| Full advanced models | Implemented and tested actual experimental GoliCoach person/pose inference, private MP4 handling, timestamps, angles, comparison and replay controls | No Bangladesh cricket holdout or coach-approved suggestions; all 50 full advanced acceptance gates remain incomplete |
| Hosting | Inspected connected providers; corrected container state/model paths, acquisition tooling and Compose model-init dependency | Supabase project creation rejected at the two-active-free-project quota; live private compute/storage/scanning/SMTP/operations remain unconfigured |
| Browser PDF | Actual API generation/readable PDF verified; identified `ERR_BLOCKED_BY_CLIENT` and explicit cloud browser URL/security denial | Browser download verification is blocked by this environment; no workaround/bypass or browser-pass claim |
| Runtime telemetry | Disabled ONNX 1DS before import, disabled Hugging Face telemetry, added API opt-out, CI/container settings and initialization-order test | Earlier automatic-review-blocked telemetry attempt is historical; no prior absence-of-traffic claim |
| Verification | 325 tests passed; TypeScript, lint and Next production build passed; exact registry/source checksums retained | Pose upload automation timed out; completed pose browser E2E, operator MFA browser flow and responsive/accessibility matrix are not verified |

## GitHub — the URL is already known

Target: https://github.com/EMON-721/Mouchak-AI-platform. The actual error is `403 Resource not accessible by integration`. User push/admin rights in repository metadata do not give the integration those rights.

The required owner action is to authorize a write-capable GitHub connection for this exact repository. It needs Contents write access, and permission to publish the tracked workflow. Review the installed app/repository selection and any pending permission update. If that integration cannot request write access, use secure authenticated Git in your own environment instead. Changing GitHub Actions workflow-token permissions does not repair this external connector's token. Do not paste credentials into chat.

The complete prepared branch is `feat/public-tools-no-accounts`. Its history already includes remote initial commit `d84fe4327693cb73dae0e0b80f936b9567eafd54`; the initial README text is retained. After authorization, fetch/inspect changes and push without force:

```bash
git remote add github https://github.com/EMON-721/Mouchak-AI-platform.git # only if absent
git fetch github main
git log --oneline --all -8
git push github feat/public-tools-no-accounts:feat/public-tools-no-accounts
```

If remote main changed, integrate that history first. Record the actual pushed commit and remote CI afterward. Nothing in this delivery claims that they already succeeded.

GitHub's official explanation: https://docs.github.com/en/rest/using-the-rest-api/troubleshooting-the-rest-api#resource-not-accessible

## Hosting — creation was attempted, not assumed

The owner selected the connected Supabase organization. The quote was $0/month; the actual create operation failed because its two active free projects exhausted the account cap. No Mouchak project was created. No existing project, schema, data, billing plan or visibility was changed.

To proceed, make a dedicated project slot available through an owner-approved plan/resource decision, or provide a separately authorized PostgreSQL target. A paid upgrade or pausing/deleting another project requires a new explicit decision; the earlier free-project choice does not authorize it. Never send database passwords in chat. The selected database must have the migration/app/scheduler roles and owner RLS described in `DEPLOYMENT.md`.

Then provision private Python compute, private S3/scanning, stable encryption/proxy secrets, SMTP, retention/scheduler workers, backups and monitoring. The new model-init job supplies checksum-verified baseline weights; it does not supply missing domain training data or production validation. Docker images and live provider connections need staging verification before a production claim.

Vercel Services can host a private container/Python service and Next.js in one deployment; it is currently Beta. No Mouchak project was created there. Existing 10 MB uploads exceed the documented 4.5 MB Function request limit, and background daemons/stateless storage need a tested platform-specific design. The current container/worker deployment remains the prepared baseline.

Provider references: https://supabase.com/docs/guides/platform/billing-on-supabase and https://vercel.com/docs/services.

## Model and browser scope

Read `POSE_PIPELINE.md`: the real new pipeline is deliberately experimental and disabled in production. Runtime success over synthetic-motion reference clips is not Bangladesh performance validation. No clinic/pharmacy stock records, market observations, labelled holdouts or expert approvals were fabricated.

Browser PDF navigation is blocked by the cloud browser policy. Pose controls rendered correctly; the later file-upload action timed out with no verified outcome and was not automatically repeated. API/test evidence is reported separately from browser evidence.

Resume the newest source/history bundle and this branch. Do not recreate completed modules, repeat the kit inventory, discard original advanced requirements, re-enable public accounts or request the supplied GitHub destination again.
