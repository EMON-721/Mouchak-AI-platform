// Actual PostgreSQL engine in WebAssembly, used for SQL/RLS verification only.
// This does not verify an external server, psycopg networking or production ops.
import { PGlite } from "@electric-sql/pglite";
import { readFile, writeFile } from "node:fs/promises";
import assert from "node:assert/strict";
const db = new PGlite();
await db.waitReady;
await db.exec(await readFile("database/migrations/001_initial.sql", "utf8"));
await db.exec(await readFile("database/migrations/002_owner_rls.sql", "utf8"));
await db.exec(
  await readFile("database/migrations/003_retail_stock.sql", "utf8"),
);
await db.exec(
  "CREATE ROLE mouchak_test NOSUPERUSER NOBYPASSRLS; GRANT USAGE ON SCHEMA public TO mouchak_test; GRANT SELECT,INSERT,DELETE ON workspaces TO mouchak_test; GRANT SELECT,INSERT,UPDATE,DELETE ON stock_items,stock_movements TO mouchak_test;",
);
await db.exec(
  "INSERT INTO users(id,email,password,name,role,verified,banned,language,mfa_enabled,created_at) VALUES ('A','a@example.test','test-only','A','user',true,false,'bn',false,'2026-10-27'),('B','b@example.test','test-only','B','user',true,false,'bn',false,'2026-10-27'); INSERT INTO workspaces(id,user_id,name) VALUES ('WA','A','A private'),('WB','B','B private'); INSERT INTO stock_items(id,user_id,workspace_id,sku_hash,encrypted,quantity,minimum,revision,archived,created_at) VALUES ('IA','A','WA','hashA','cipherA',10,1,0,false,'2026-10-27'),('IB','B','WB','hashB','cipherB',20,1,0,false,'2026-10-27'); SET ROLE mouchak_test;",
);
let noIdentity = await db.query("SELECT * FROM workspaces");
assert.equal(noIdentity.rows.length, 0);
assert.equal((await db.query("SELECT * FROM stock_items")).rows.length, 0);
await db.query("SELECT set_config('app.user_id','A',false)");
let a = await db.query("SELECT * FROM workspaces");
assert.equal(a.rows.length, 1);
assert.equal(a.rows[0].id, "WA");
assert.equal((await db.query("SELECT * FROM stock_items")).rows[0].id, "IA");
assert.equal(
  (
    await db.query(
      "UPDATE stock_items SET quantity=0 WHERE id='IB' RETURNING id",
    )
  ).rows.length,
  0,
);
let blocked = false;
try {
  await db.exec(
    "INSERT INTO workspaces(id,user_id,name) VALUES ('EVIL','B','blocked')",
  );
} catch {
  blocked = true;
}
assert.equal(blocked, true);
let badStockLink = false;
try {
  await db.exec(
    "INSERT INTO stock_items(id,user_id,workspace_id,sku_hash,encrypted,quantity,minimum,revision,archived,created_at) VALUES ('CROSS','A','WB','x','test',1,0,0,false,'2026-10-27')",
  );
} catch {
  badStockLink = true;
}
assert.equal(badStockLink, true);
let badMovementLink = false;
try {
  await db.exec(
    "INSERT INTO stock_movements(id,user_id,workspace_id,item_id,idempotency_key,encrypted,occurred_at,created_at) VALUES ('CROSS-M','A','WA','IB','cross-retry','test','2026-10-27','2026-10-27')",
  );
} catch {
  badMovementLink = true;
}
assert.equal(badMovementLink, true);
await db.query("SELECT set_config('app.user_id','B',false)");
let b = await db.query("SELECT * FROM workspaces");
assert.equal(b.rows.length, 1);
assert.equal(b.rows[0].id, "WB");
await db.exec("RESET ROLE");
const version = await db.query("SELECT version()");
const result = {
  engine_version: version.rows[0].version,
  schema_tables: 16,
  tests: {
    schema_migration: "passed",
    identity_absent_denies: "passed",
    owner_A_isolation: "passed",
    owner_B_isolation: "passed",
    cross_owner_write_denied: "passed",
    stock_no_identity_denied: "passed",
    stock_owner_isolation: "passed",
    stock_cross_owner_update_denied: "passed",
    stock_cross_owner_links_denied: "passed",
  },
  external_postgres_networking_tested: false,
  production_database: false,
};
await writeFile(
  "docs/audit/postgres-sql.json",
  JSON.stringify(result, null, 2),
);
console.log(JSON.stringify(result));
await db.close();
