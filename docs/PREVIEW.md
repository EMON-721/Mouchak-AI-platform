# Private full-stack preview — no production hosting

The owner paused production hosting on 29 October 2026. Do not provision Render/Netlify/Railway/Cloudflare resources to follow this guide. A website screenshot or static GitHub Pages page is not a working Python inference backend.

## GitHub Codespaces (optional browser-based development)

1. Open https://codespaces.new/EMON-721/Mouchak-AI-platform or Code → Codespaces in this repository.
2. Review your GitHub included usage/billing before creating compute. This repository does not create a codespace or charge a hosting account.
3. The devcontainer installs Node 24, Python 3.12, pnpm 11.25.0, Tesseract BN/EN, FFmpeg, dependencies and checksum-controlled baseline OCR/ONNX assets. Wait for post-create setup to finish.
4. Run `pnpm dev --host 0.0.0.0`.
5. In Ports, open 3000 in the browser; keep visibility Private. Do not forward 8000. Other ports are set to ignore automatic forwarding.
6. The wrapper derives PUBLIC_ORIGIN from the Codespaces name/forwarding domain before starting both servers. This fixes browser mutation/CSRF failures caused by localhost origins. An explicit PUBLIC_ORIGIN overrides it; it must exactly match the browser's origin.
7. Exercise an owned bill calculation, retrieval question and /work history. Optional specialized models remain clearly unavailable until separately downloaded/evaluated.
8. Stop the development command and stop/delete the codespace through GitHub when finished. Keep any needed private result encrypted/offline; deleting development volumes destroys their records.

Codespaces configuration is source-prepared, not a claim that an owner codespace has been provisioned or tested. GitHub's static github.dev editor cannot run the backend. Official port guidance: https://docs.github.com/en/codespaces/developing-in-a-codespace/forwarding-ports-in-your-codespace .

## Local Docker, including Windows with Docker Desktop

```bash
docker compose -f deploy/compose.local.yaml up --build
```

Open http://localhost:3000. The browser sees one Next.js origin; the Python API stays inside the Docker network. The template starts real model acquisition/API/inference/scheduler/retention services. It uses local encrypted SQLite/files for development, not a cloud database or mock API. Uploads may be explicitly unscanned in development; do not submit sensitive real documents. No production scanner, remote SMTP or paid AI API is simulated.

Change MOUCHAK_WEB_PORT before starting if 3000 is occupied. The template publishes only to loopback. Use localhost consistently for PUBLIC_ORIGIN, rather than switching between localhost and 127.0.0.1.

`docker compose -f deploy/compose.local.yaml down` stops services without deleting volumes. Do not add -v unless you intend to erase this preview's data. To create a local operator:
```bash
docker compose -f deploy/compose.local.yaml exec api python -m services.model_worker.manage create-admin --email YOUR-EMAIL
```
Enter the password in the prompt, then sign in at /admin/login and enroll MFA. No seeded default administrator exists.

## Native Linux/macOS/WSL

Install Node 24, Python 3.12, pnpm 11.25.0, Tesseract Bengali/English and FFmpeg. On Debian/Ubuntu, OCR packages include tesseract-ocr, tesseract-ocr-ben and tesseract-ocr-eng.
```bash
pnpm install --frozen-lockfile
python3 -m venv .venv
.venv/bin/python -m pip install -r requirements-python.txt
.venv/bin/python scripts/download-models.py
pnpm dev
```

Do not copy a production .env into a development checkout. The API automatically creates its local schema and a private encryption key; no manual remote SQL step is needed for a local preview. To use durable jobs, set ENABLE_DURABLE_INFERENCE=1 in the development environment before running pnpm dev. The wrapper starts the corresponding worker after the API is ready. Pose remains off unless explicitly enabled outside production.

## Native Windows PowerShell

Use the project folder, not C:\\WINDOWS\\system32. Python 3.11 used for the previous connection probe is not the tested full application target; install/use Python 3.12 for this full stack, or use WSL/Docker.

```powershell
Set-Location "YOUR-EXISTING-PROJECT-FOLDER"
pnpm install --frozen-lockfile
py -3.12 -m venv .venv
.\\.venv\\Scripts\\python.exe -m pip install -r requirements-python.txt
.\\.venv\\Scripts\\python.exe scripts/download-models.py
pnpm dev
```

No virtualenv activation or execution-policy change is required. The launcher now selects .venv/Scripts/python.exe on Windows. Tesseract/FFmpeg must be on PATH and the language assets present. Windows/macOS full inference is not separately certified by Linux CI. Docker/Codespaces is the consistent Linux environment.

## What to check

- Home/Explore: 50 workspaces, Bengali/English, no public signup/profile.
- BillDetect: owned DEMO values and a real arithmetic result; reopen through /work.
- ShikkhaRAG: ask about an existing original passage and check its citation. An unsupported question should abstain.
- Upload/OCR: use a synthetic/owned image, check actual extracted text, and retain the explicit scanner status.
- Admin: protected login, own MFA enrollment and authorized controls. Do not bypass authentication to preview admin pages.
- Privacy: export/clear the current scope; another browser session cannot read its run IDs.
- API absence: a 503 is an unavailable backend, not a successful or fake AI answer.

The managed ChatGPT preview is internal QA and can expire between sessions. Its terminal.local URL is not a public production URL. Codespaces is the repeatable owner-controlled online developer preview path.

## Troubleshooting

| Symptom | Action |
|---|---|
| Python/uvicorn unavailable | Verify the selected .venv interpreter and install requirements in that interpreter |
| API exits before website | Read ignored .state/development-api.log; the wrapper now stops instead of opening a disconnected frontend |
| 403 origin/CSRF | Set the exact PUBLIC_ORIGIN or use the automatic Codespaces origin; do not disable CSRF |
| Model unavailable | Run the recorded checksum acquisition script; missing weights are not replaced with static responses |
| Expired browser preview tab | Restart/open the current private developer preview; old handoff links are temporary |
| Browser PDF blocked by policy | Keep the recorded browser limitation; do not use a tunnel/security bypass or claim a verified browser download |
