// Real PostgreSQL WASM SQL/RLS tests. No external server or network claim.
import { PGlite } from "@electric-sql/pglite";
import { readFile, writeFile } from "node:fs/promises";
import assert from "node:assert/strict";
const db = new PGlite();
await db.waitReady;
for (const file of [
  "001_initial",
  "002_owner_rls",
  "003_retail_stock",
  "004_collaboration_operations",
  "005_async_runtime",
  "006_private_bills",
])
  await db.exec(await readFile(`database/migrations/${file}.sql`, "utf8"));
// Reapplying the additive migration preserves existing tables and policies.
await db.exec(
  await readFile("database/migrations/005_async_runtime.sql", "utf8"),
);
await db.exec(`
CREATE ROLE mouchak_app NOSUPERUSER NOBYPASSRLS;
CREATE ROLE mouchak_inference NOSUPERUSER NOBYPASSRLS;
CREATE ROLE mouchak_retention NOSUPERUSER NOBYPASSRLS;
INSERT INTO users(id,email,password,name,role,verified,banned,language,mfa_enabled,created_at) VALUES
('A','a@test.invalid','fixture','A','guest',false,false,'bn',false,'2026-10-28'),
('B','b@test.invalid','fixture','B','guest',false,false,'bn',false,'2026-10-28');
INSERT INTO sessions(id,user_id,csrf,expires,last_seen,mfa_until,device) VALUES
('SA','A','fixture',2140000000,0,0,'test'),('SB','B','fixture',2140000000,0,0,'test');
INSERT INTO workspaces(id,user_id,name) VALUES('WA','A','A'),('WB','B','B');
INSERT INTO chunk_uploads(id,user_id,size,checksum,expires_at,state) VALUES('CA','A',10,'hash',0,'uploading'),('CB','B',10,'hash',0,'uploading');
INSERT INTO upload_parts(id,upload_id,part,checksum,encrypted) VALUES('PA','CA',0,'hash','cipher A'),('PB','CB',0,'hash','cipher B');
INSERT INTO inference_jobs(id,user_id,session_id,module,request_key,fingerprint,encrypted,state,attempts,lease_until,created_at,expires_at) VALUES
('JA','A','SA','billdetect-ai','key','hash','cipher A','queued',0,0,0,2140000000),
('JB','B','SB','billdetect-ai','key','hash','cipher B','queued',0,0,0,2140000000);
INSERT INTO bill_history_entries(id,user_id,workspace_id,bill_type,month,encrypted,training_allowed,is_demo,revision,created_at) VALUES
('BA','A','WA','electricity','2026-01','encrypted A',false,true,1,'2026-10-28'),
('BB','B','WB','electricity','2026-01','encrypted B',false,true,1,'2026-10-28');
INSERT INTO bill_personal_models(id,user_id,workspace_id,bill_type,checksum,encrypted,created_at) VALUES
('MA','A','WA','electricity','test-only','encrypted A','2026-10-28'),
('MB','B','WB','electricity','test-only','encrypted B','2026-10-28');
`);
await db.exec(await readFile("deploy/app-grants.sql", "utf8"));
await db.exec(await readFile("deploy/runtime-grants.sql", "utf8"));
await db.exec("SET ROLE mouchak_app");
assert.equal((await db.query("SELECT * FROM inference_jobs")).rows.length, 0);
assert.equal((await db.query("SELECT * FROM upload_parts")).rows.length, 0);
assert.equal(
  (await db.query("SELECT * FROM bill_history_entries")).rows.length,
  0,
);
assert.equal(
  (await db.query("SELECT * FROM bill_personal_models")).rows.length,
  0,
);
await db.query("SELECT set_config('app.user_id','A',false)");
assert.deepEqual(
  (await db.query("SELECT id FROM inference_jobs")).rows.map((r) => r.id),
  ["JA"],
);
assert.deepEqual(
  (await db.query("SELECT id FROM upload_parts")).rows.map((r) => r.id),
  ["PA"],
);
assert.equal(
  (
    await db.query(
      "UPDATE inference_jobs SET state='cancelled' WHERE id='JB' RETURNING id",
    )
  ).rows.length,
  0,
);
assert.deepEqual(
  (await db.query("SELECT id FROM bill_history_entries")).rows.map((r) => r.id),
  ["BA"],
);
assert.deepEqual(
  (await db.query("SELECT id FROM bill_personal_models")).rows.map((r) => r.id),
  ["MA"],
);
assert.equal(
  (
    await db.query(
      "DELETE FROM bill_history_entries WHERE id='BB' RETURNING id",
    )
  ).rows.length,
  0,
);
for (const table of ["bill_history_entries", "bill_personal_models"]) {
  let denied = false;
  try {
    await db.exec(`UPDATE ${table} SET workspace_id='WB' WHERE user_id='A'`);
  } catch {
    denied = true;
  }
  assert.ok(denied, "Cross-owner workspace link must fail");
}
let crossSessionDenied = false;
try {
  await db.exec("UPDATE inference_jobs SET session_id='SB' WHERE id='JA'");
} catch {
  crossSessionDenied = true;
}
assert.ok(crossSessionDenied);
let crossPartDenied = false;
try {
  await db.exec(
    "INSERT INTO upload_parts(id,upload_id,part,checksum,encrypted) VALUES('X','CB',1,'x','x')",
  );
} catch {
  crossPartDenied = true;
}
assert.ok(crossPartDenied);
const upsert = `INSERT INTO request_rate_buckets(subject,window_start,used,expires_at) VALUES('opaque-hmac',60,1,120)
ON CONFLICT(subject,window_start) DO UPDATE SET used=request_rate_buckets.used+1 WHERE request_rate_buckets.used<2 RETURNING used`;
assert.equal((await db.query(upsert)).rows[0].used, 1);
assert.equal((await db.query(upsert)).rows[0].used, 2);
assert.equal((await db.query(upsert)).rows.length, 0);
await db.exec("RESET ROLE; SET ROLE mouchak_inference");
await db.query("SELECT set_config('app.user_id','',false)");
assert.equal((await db.query("SELECT * FROM inference_jobs")).rows.length, 2);
assert.equal((await db.query("SELECT * FROM workspaces")).rows.length, 0);
await db.query("SELECT set_config('app.user_id','A',false)");
assert.equal((await db.query("SELECT * FROM workspaces")).rows[0].id, "WA");
await db.exec(
  "UPDATE inference_jobs SET state='running',claim_token='new-lease',lease_until=2140000000 WHERE id='JA'",
);
assert.equal(
  (
    await db.query(
      "UPDATE inference_jobs SET state='succeeded' WHERE id='JA' AND state='running' AND claim_token='old-lease' RETURNING id",
    )
  ).rows.length,
  0,
);
let rateWorkerDenied = false;
try {
  await db.query("SELECT * FROM request_rate_buckets");
} catch {
  rateWorkerDenied = true;
}
assert.ok(rateWorkerDenied);
let secretDenied = false;
try {
  await db.query("SELECT password FROM users");
} catch {
  secretDenied = true;
}
assert.ok(secretDenied);
for (const table of ["bill_history_entries", "bill_personal_models"]) {
  let denied = false;
  try {
    await db.query(`SELECT * FROM ${table}`);
  } catch {
    denied = true;
  }
  assert.ok(
    denied,
    "Inference queue role must not read private bill training tables",
  );
}
await db.exec("RESET ROLE; SET ROLE mouchak_retention");
await db.query("SELECT set_config('app.user_id','',false)");
assert.equal(
  (await db.query("DELETE FROM chunk_uploads WHERE expires_at=0 RETURNING id"))
    .rows.length,
  2,
);
assert.equal((await db.query("SELECT * FROM upload_parts")).rows.length, 0);
await db.exec("RESET ROLE; DELETE FROM sessions WHERE id='SA'");
assert.equal(
  (await db.query("SELECT * FROM inference_jobs WHERE id='JA'")).rows.length,
  0,
);
await db.exec("DELETE FROM users WHERE id='A'");
assert.equal(
  (await db.query("SELECT * FROM bill_history_entries WHERE user_id='A'")).rows
    .length,
  0,
);
assert.equal(
  (await db.query("SELECT * FROM bill_personal_models WHERE user_id='A'")).rows
    .length,
  0,
);
assert.equal(
  (await db.query("SELECT * FROM bill_history_entries WHERE user_id='B'")).rows
    .length,
  1,
);
const tables = await db.query(
  "SELECT count(*)::int AS total FROM information_schema.tables WHERE table_schema='public' AND table_type='BASE TABLE'",
);
const result = {
  schema_tables: tables.rows[0].total,
  additive_migration_reapplied: true,
  owner_and_worker_rls: "passed",
  private_bill_rls_links_grants_and_cascades: "passed",
  stale_lease_fence: "passed",
  shared_rate_upsert: "passed",
  expiry_and_session_cascades: "passed",
  external_postgres_tested: false,
};
await writeFile(
  "docs/audit/async-postgres.json",
  JSON.stringify(result, null, 2) + "\n",
);
console.log(JSON.stringify(result));
await db.close();
