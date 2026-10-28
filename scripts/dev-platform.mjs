import { spawn } from "node:child_process";
import { mkdirSync, openSync, appendFileSync, existsSync } from "node:fs";
import { readExecutionProfile } from "./execution-profile.mjs";
if (existsSync(".env")) process.loadEnvFile(".env");
mkdirSync(".state", { recursive: true });
const log = openSync(".state/development-api.log", "a");
const python =
  process.env.MOUCHAK_PYTHON ||
  (existsSync(".venv/bin/python") ? ".venv/bin/python" : "python3");
const raw = process.argv.slice(2);
const managed = readExecutionProfile() === "managed-linux";
const suppliedPort = raw[raw.indexOf("--port") + 1];
const port = raw.includes("--port") ? suppliedPort : "3000";
const origin =
  process.env.PUBLIC_ORIGIN ||
  (managed ? `http://terminal.local:${port}` : `http://localhost:${port}`);
const backend = spawn(
  python,
  [
    "-m",
    "uvicorn",
    "services.model_worker.main:app",
    "--host",
    "127.0.0.1",
    "--port",
    "8000",
    "--no-access-log",
  ],
  {
    stdio: ["ignore", log, log],
    env: {
      ...process.env,
      PUBLIC_ORIGIN: origin,
      OPENBLAS_NUM_THREADS: "2",
      OMP_NUM_THREADS: "2",
    },
  },
);
// Use the app's canonical Next.js runtime for its private API proxy. The optional
// Sites/Vinext build remains available separately; the Python worker is not
// hosted inside a Cloudflare Worker during full-stack development.
const args = raw
  .filter((a) => a !== "--strictPort")
  .map((a) => (a === "--host" ? "--hostname" : a));
const frontend = spawn(
  process.execPath,
  ["node_modules/next/dist/bin/next", "dev", ...args],
  { stdio: "inherit", env: { ...process.env, NEXT_TELEMETRY_DISABLED: "1" } },
);
let stopping = false;
let inference;
async function startInference() {
  if (process.env.ENABLE_DURABLE_INFERENCE !== "1") return;
  for (let attempt = 0; attempt < 60 && !stopping; attempt++) {
    try {
      const ready = await fetch("http://127.0.0.1:8000/api/health", {
        signal: AbortSignal.timeout(1000),
      });
      if (ready.ok && !stopping) {
        inference = spawn(
          python,
          ["-m", "services.model_worker.inference_worker"],
          {
            stdio: ["ignore", log, log],
            env: {
              ...process.env,
              OPENBLAS_NUM_THREADS: "2",
              OMP_NUM_THREADS: "2",
            },
          },
        );
        inference.on("error", () => {
          stop();
          process.exitCode = 1;
        });
        inference.on("exit", (code) => {
          if (!stopping) {
            stop();
            process.exitCode = code || 1;
          }
        });
        return;
      }
    } catch {
      /* API is still starting; no alternate listener is launched. */
    }
    await new Promise((resolve) => setTimeout(resolve, 500));
  }
  if (!stopping) {
    stop();
    process.exitCode = 1;
  }
}
void startInference();
function stop() {
  if (stopping) return;
  stopping = true;
  inference?.kill("SIGTERM");
  backend.kill("SIGTERM");
  frontend.kill("SIGTERM");
}
backend.on("error", (err) => {
  appendFileSync(".state/development-api.log", err.message + "\n");
  stop();
  process.exitCode = 1;
});
backend.on("exit", (code, signal) => {
  if (!stopping) {
    process.stderr.write("Private API exited: " + code + " " + signal + "\n");
    stop();
    process.exitCode = code || 1;
  }
});
process.on("SIGINT", stop);
process.on("SIGTERM", stop);
frontend.on("exit", (code) => {
  stop();
  process.exitCode = code || 0;
});
