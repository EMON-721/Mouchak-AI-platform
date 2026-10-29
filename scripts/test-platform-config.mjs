import assert from "node:assert/strict";
import { developmentConfig } from "./platform-config.mjs";
const win = developmentConfig({}, [], false, "win32", (p) => p === ".venv/Scripts/python.exe");
assert.equal(win.python, ".venv/Scripts/python.exe");
assert.equal(win.origin, "http://localhost:3000");
const remote = developmentConfig({ CODESPACE_NAME: "owned-space" }, ["--host", "0.0.0.0", "--port", "3001", "--strictPort"]);
assert.equal(remote.origin, "https://owned-space-3001.app.github.dev");
assert.deepEqual(remote.args, ["--hostname", "0.0.0.0", "--port", "3001"]);
assert.equal(developmentConfig({}, ["--port", "4173"], true).origin, "http://terminal.local:4173");
assert.equal(developmentConfig({ PORT: "4000", PUBLIC_ORIGIN: "https://preview.example.test" }).origin, "https://preview.example.test");
for (const port of ["", "0", "65536", "123x", "NaN"])
  assert.throws(() => developmentConfig({}, ["--port", port]));
assert.throws(() => developmentConfig({ PORT: "8000" }));
assert.throws(() => developmentConfig({ MOUCHAK_ENV: "production" }));
for (const origin of ["https://user:secret@example.test", "https://example.test/path", "https://example.test?key=private", "file:///tmp"])
  assert.throws(() => developmentConfig({ PUBLIC_ORIGIN: origin }));
console.log("Portable Windows/Linux, managed preview, Codespaces origin and invalid configuration checks passed.");
