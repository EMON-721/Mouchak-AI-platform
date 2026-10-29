import { spawn } from "node:child_process";
import { mkdirSync, openSync, existsSync, writeFileSync } from "node:fs";
import { readExecutionProfile } from "./execution-profile.mjs";
import { developmentConfig } from "./platform-config.mjs";

if (existsSync(".env")) process.loadEnvFile(".env");
const managed = process.env.SITES_MANAGED_LINUX_CONTAINER === "1" || readExecutionProfile() === "managed-linux";
const config = developmentConfig(process.env, process.argv.slice(2), managed);
mkdirSync(".state", { recursive: true });
writeFileSync(".state/development-config.json", JSON.stringify({ origin: config.origin, web_port: config.port, api_port: config.apiPort, managed }), { mode: 0o600 });
const log = openSync(".state/development-api.log", "a", 0o600);
const env = {
  ...process.env, MOUCHAK_ENV: "development", PUBLIC_ORIGIN: config.origin,
  PRIVATE_API_URL: `http://127.0.0.1:${config.apiPort}`,
  NEXT_TELEMETRY_DISABLED: "1", OPENBLAS_NUM_THREADS: "2", OMP_NUM_THREADS: "2",
};
const children = [];
let stopping = false;
function stop(code = 0) {
  if (stopping) return;
  stopping = true;
  process.exitCode = code;
  for (const child of children) child.kill("SIGTERM");
}
function launch(command, args, stdio) {
  const child = spawn(command, args, { stdio, env });
  children.push(child);
  child.on("error", () => {
    console.error("A development service could not start. Check Python/dependencies and .state/development-api.log.");
    stop(1);
  });
  child.on("exit", (code) => { if (!stopping) stop(code || 1); });
  return child;
}
process.on("SIGINT", () => stop());
process.on("SIGTERM", () => stop());
launch(config.python, ["-m", "uvicorn", "services.model_worker.main:app", "--host", "127.0.0.1", "--port", config.apiPort, "--no-access-log"], ["ignore", log, log]);
let ready = false;
for (let attempt = 0; attempt < 60 && !stopping; attempt++) {
  try {
    const response = await fetch(`${env.PRIVATE_API_URL}/api/health`, { signal: AbortSignal.timeout(1000) });
    const health = await response.json();
    if (response.ok && health.api === "ok" && health.tools === 50) { ready = true; break; }
  } catch { /* Bounded startup wait; never substitute fake API responses. */ }
  await new Promise((resolve) => setTimeout(resolve, 500));
}
if (!ready || stopping) {
  if (!stopping) console.error("Private API startup failed. See .state/development-api.log; no frontend was started.");
  stop(1);
} else {
  if (env.ENABLE_DURABLE_INFERENCE === "1")
    launch(config.python, ["-m", "services.model_worker.inference_worker"], ["ignore", log, log]);
  launch(config.python, ["-m", "services.model_worker.visitor_retention"], ["ignore", log, log]);
  launch(config.python, ["-m", "services.model_worker.scheduler"], ["ignore", log, log]);
  launch(process.execPath, ["node_modules/next/dist/bin/next", "dev", ...config.args], "inherit");
  console.log(`Mouchak development origin: ${config.origin}`);
}
