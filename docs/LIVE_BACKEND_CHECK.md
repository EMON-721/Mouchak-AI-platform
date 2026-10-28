# Check an authorized live backend without reusing private user data

The owner handles Netlify. The backend still needs an authorized host and service credentials. Installing/connecting Render supplies account access only after its connection is confirmed; it does not create compute, a database, a bucket or a paid plan. Existing Supabase projects remain untouched.

## Real service verification command

After the authorized host has been configured and the ordinary acquisition/provisioning steps have succeeded, inject the following settings through its existing secret manager/environment:

- `PRIVATE_API_URL`: the exact HTTPS API origin, without path/query/credentials.
- `PRIVATE_API_TOKEN`: the existing private backend token, 32–512 visible ASCII characters. Never put it in a command argument, source or chat.
- `PUBLIC_ORIGIN`: the exact HTTPS Netlify/custom website origin accepted by the backend.
- Optional `MOUCHAK_SMOKE_CA_FILE`: a trusted private CA path. There is no switch to disable TLS verification.

Run from the repository root with the application's installed dependencies:

```bash
python -m services.model_worker.deployment_smoke
```

The command checks actual HTTPS/token isolation, two account-free Secure/HttpOnly visitor scopes, a project-owned visibly DEMO PNG through scanning/private storage, actual OCR, a queued Bengali-numeral bill calculation, two distinct ONNX/MiniLM extractive retrieval answers over the authored starter corpus, JSON export and second-visitor read denial. It then explicitly clears only the temporary scopes it created, including on a processing failure. It does not use browser cookies, take an operator password, alter existing accounts or fit any model from the DEMO inputs. Output contains booleans and a static failure stage, never tokens, cookies, responses, private record IDs or raw driver errors.

Any redirect, TLS failure, rejected origin/token, missing scanner/model, stalled/failed job, unexpected response, cross-owner access or cleanup failure produces a nonzero exit. It is a real input → API → storage/worker/model → saved result → export/clear check, rather than a health-only check. It may consume a small amount of host CPU/storage for the owned fixtures. Run only against the owner's authorized backend.

## What passing means

A pass verifies this limited support path on the target it was actually run against. It does not validate all 50 tools, representative Bangladesh accuracy, official tariffs, provider backups, operator browser MFA, Netlify adapter execution or browser accessibility/PDF behavior. Specialized models retain their existing production gates. The smoke test intentionally reports these limitations instead of a `production_ready=true` claim.

Four local configuration/security tests pass in `tests/test_deployment_smoke_config.py`. The exact CLI is also invoked against real disposable TLS PostgreSQL/S3/API/model containers by `scripts/test-production-stack.py`. Both jobs in [CI run 40731666580](https://github.com/EMON-721/Mouchak-AI-platform/actions/runs/40731666580) passed on runtime source `c7510abe`, including 363 Python cases and the exact CLI against the actual service fixture. This is not evidence of a live owner cloud deployment.

## Resume external hosting work

User confirmed Render installation on 28 October 2026. At that point this active session still exposed no Render capabilities and the connection inventory still reported it unavailable; do not ask the user to reinstall or claim a Render workspace was inspected. Recheck connection on the next refreshed turn. Use an existing authorized workspace/resource when possible, preserve unrelated projects, and obtain a concrete cost decision before creating paid capacity. No paid host/database or account recovery action has been performed.
