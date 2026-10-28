// Client transport/preflight tests only; actual model/API tests are in pytest.
import assert from "node:assert/strict";
import { readFile } from "node:fs/promises";
import ts from "typescript";
import { verifyBackend } from "./check-netlify.mjs";
const source = await readFile(
  "components/mouchak/private-processing.ts",
  "utf8",
);
const compiled = ts.transpileModule(source, {
  compilerOptions: {
    module: ts.ModuleKind.ESNext,
    target: ts.ScriptTarget.ES2022,
  },
}).outputText;
const { uploadPrivateFile, runQueued } = await import(
  "data:text/javascript;base64," + Buffer.from(compiled).toString("base64")
);
const bytes = new Uint8Array(7 * 1024 * 1024 + 123);
bytes[0] = 87;
bytes[bytes.length - 1] = 99;
const file = new File([bytes], "synthetic-private-file.wav");
const chunks = [];
let fingerprint;
let completed = false;
const api = async (path, options) => {
  if (path === "/api/uploads") {
    fingerprint = JSON.parse(options.body).checksum;
    return { id: "upload-test", chunk_bytes: 1024 * 1024 };
  }
  if (path.includes("/parts/")) {
    assert.equal(options.headers["Content-Type"], "application/octet-stream");
    assert.ok(options.body.size <= 1024 * 1024);
    chunks.push(new Uint8Array(await options.body.arrayBuffer()));
    return {};
  }
  if (path.endsWith("/complete")) {
    completed = true;
    return { id: "private-asset", scan_state: "test-only" };
  }
  assert.fail("Unexpected path");
};
const progress = [];
assert.equal(
  (await uploadPrivateFile(api, file, (n) => progress.push(n))).id,
  "private-asset",
);
assert.equal(completed, true);
assert.deepEqual(new Uint8Array(await new Blob(chunks).arrayBuffer()), bytes);
assert.equal(
  fingerprint,
  Buffer.from(await crypto.subtle.digest("SHA-256", bytes)).toString("hex"),
);
assert.equal(progress.length, 8);
let deleted = false;
await assert.rejects(
  uploadPrivateFile(
    async (path, options) => {
      if (path === "/api/uploads")
        return { id: "failed", chunk_bytes: 1024 * 1024 };
      if (options.method === "DELETE") {
        deleted = true;
        return {};
      }
      throw Error("test connection failure");
    },
    file,
    () => {},
  ),
);
assert.ok(deleted);
let calls = 0;
const controller = new AbortController();
controller.abort();
await assert.rejects(
  runQueued(
    async () => {
      calls++;
    },
    "billdetect-ai",
    "{}",
    controller.signal,
    () => {},
  ),
);
assert.equal(calls, 0);
const states = [];
const result = await runQueued(
  async (path) => {
    if (path.includes("/tools/")) return { id: "job", state: "queued" };
    if (path === "/api/jobs/job")
      return { id: "job", state: "succeeded", run_id: "run" };
    if (path === "/api/runs/run")
      return {
        id: "run",
        output: { module: "billdetect-ai", facts: { test_only: true } },
      };
    assert.fail("Unexpected queue path");
  },
  "billdetect-ai",
  "{}",
  new AbortController().signal,
  (j) => states.push(j.state),
);
assert.deepEqual(states, ["queued", "succeeded"]);
assert.equal(result.id, "run");
const secret = "test-token-32-characters-only-never-live";
const env = {
  PRIVATE_API_URL: "https://backend.example.test",
  PRIVATE_API_TOKEN: secret,
};
let sent;
assert.deepEqual(
  await verifyBackend(env, async (url, options) => {
    assert.equal(url.href, "https://backend.example.test/api/health");
    sent = options.headers["x-internal-api-token"];
    return Response.json({ api: "ok", tools: 50, processing_mode: "queued" });
  }),
  {
    private_backend_reachable: true,
    processing_mode: "queued",
    full_production_scope_certified: false,
  },
);
assert.equal(sent, secret);
for (const url of [
  "http://backend.example.test",
  "https://user:pass@backend.example.test",
  "https://localhost",
  "https://backend.example.test?token=private",
])
  await assert.rejects(
    verifyBackend({ ...env, PRIVATE_API_URL: url }, () =>
      assert.fail("Unsafe URL must not be fetched"),
    ),
  );
await assert.rejects(
  verifyBackend(env, async () => {
    throw Error(secret);
  }),
  (error) => !error.message.includes(secret),
);
console.log(
  "Client chunk integrity, queue polling/abort and Netlify preflight checks passed. No hosted deployment tested.",
);
