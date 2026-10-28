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
])
  await db.exec(await readFile(`database/migrations/${file}.sql`, "utf8"));
await db.exec(`CREATE ROLE scoped_test NOSUPERUSER NOBYPASSRLS;
GRANT USAGE ON SCHEMA public TO scoped_test;
GRANT SELECT ON workspaces,tool_runs,dataset_sources TO scoped_test;
GRANT SELECT,INSERT ON notifications TO scoped_test;
GRANT SELECT(id,role,banned,mfa_enabled) ON users TO scoped_test;
GRANT SELECT,INSERT,UPDATE ON support_access_grants,tool_transfers,cms_publish_schedules,source_rights_reviews TO scoped_test;
CREATE ROLE mouchak_scheduler NOSUPERUSER NOBYPASSRLS;
GRANT USAGE ON SCHEMA public TO mouchak_scheduler;
GRANT SELECT(id,role,banned,mfa_enabled) ON users TO mouchak_scheduler;
GRANT SELECT,UPDATE ON cms_publish_schedules TO mouchak_scheduler;
INSERT INTO users(id,email,password,name,role,verified,banned,language,mfa_enabled,created_at) VALUES
('A','a@test.invalid','fixture','A','user',true,false,'bn',false,'2026-10-28'),
('B','b@test.invalid','fixture','B','user',true,false,'bn',false,'2026-10-28'),
('S','s@test.invalid','fixture','S','support_agent',true,false,'bn',true,'2026-10-28'),
('R','r@test.invalid','fixture','R','dataset_reviewer',true,false,'bn',true,'2026-10-28'),
('C','c@test.invalid','fixture','C','content_editor',true,false,'bn',true,'2026-10-28'),
('U','u@test.invalid','fixture','U','super_admin',true,false,'bn',true,'2026-10-28');
INSERT INTO workspaces(id,user_id,name) VALUES('WA','A','A'),('WB','B','B');
INSERT INTO tool_runs(id,user_id,workspace_id,module,encrypted,saved,created_at) VALUES('RA','A','WA','repairright-bd','private A',false,'2026-10-28'),('RB','B','WB','repairright-bd','private B',false,'2026-10-28');
INSERT INTO support_access_grants(id,user_id,recipient_id,run_id,encrypted,expires_at,created_at) VALUES('G','A','S','RA','selected snapshot',EXTRACT(EPOCH FROM CURRENT_TIMESTAMP)+3600,'2026-10-28');
INSERT INTO tool_transfers(id,user_id,source_run_id,workspace_id,target_module,encrypted,state,created_at) VALUES('T','A','RA','WA','scamsignal-bd','private draft','draft','2026-10-28');
INSERT INTO cms_versions(id,page,body,status,author,created_at) VALUES('V','home','{}','draft','C','2026-10-28');
INSERT INTO cms_publish_schedules(id,version_id,author,due_at,base_hash,state,created_at) VALUES('P','V','C',0,'test','scheduled','2026-10-28');
INSERT INTO dataset_sources(id,module,metadata_json,state) VALUES('DS','cliniccompass-bd','{}','candidate');
INSERT INTO source_rights_reviews(id,source_id,reviewer,round,decision,asset_hash,evidence,created_at) VALUES('RR','DS','R',0,'approved_reference_only','fixture','{}','2026-10-28');
SET ROLE scoped_test;`);
assert.equal(
  (await db.query("SELECT * FROM support_access_grants")).rows.length,
  0,
);
assert.equal((await db.query("SELECT * FROM tool_transfers")).rows.length, 0);
await db.query("SELECT set_config('app.user_id','B',false)");
assert.equal(
  (await db.query("SELECT * FROM support_access_grants")).rows.length,
  0,
);
assert.equal((await db.query("SELECT * FROM tool_transfers")).rows.length, 0);
await db.query("SELECT set_config('app.user_id','S',false)");
assert.equal(
  (await db.query("SELECT * FROM support_access_grants")).rows.length,
  0,
);
await db.query(
  "SELECT set_config('app.mfa_until',(EXTRACT(EPOCH FROM CURRENT_TIMESTAMP)::bigint+900)::text,false)",
);
assert.equal(
  (await db.query("SELECT * FROM support_access_grants")).rows.length,
  1,
);
assert.equal((await db.query("SELECT * FROM tool_runs")).rows.length, 0);
let recipientWriteDenied = false;
try {
  await db.exec(
    "UPDATE support_access_grants SET encrypted='changed' WHERE id='G'",
  );
} catch {
  recipientWriteDenied = true;
}
assert.ok(recipientWriteDenied);
await db.query("SELECT set_config('app.user_id','A',false)");
assert.equal((await db.query("SELECT * FROM tool_transfers")).rows.length, 1);
let crossLinkDenied = false;
try {
  await db.exec("UPDATE tool_transfers SET workspace_id='WB' WHERE id='T'");
} catch {
  crossLinkDenied = true;
}
assert.ok(crossLinkDenied);
await db.exec("UPDATE support_access_grants SET revoked_at=1 WHERE id='G'");
await db.query("SELECT set_config('app.user_id','S',false)");
assert.equal(
  (await db.query("SELECT * FROM support_access_grants")).rows.length,
  0,
);
assert.equal(
  (await db.query("SELECT * FROM cms_publish_schedules")).rows.length,
  0,
);
await db.query("SELECT set_config('app.user_id','A',false)");
assert.equal(
  (await db.query("SELECT * FROM source_rights_reviews")).rows.length,
  0,
);
await db.query("SELECT set_config('app.user_id','R',false)");
assert.equal(
  (await db.query("SELECT * FROM source_rights_reviews")).rows.length,
  1,
);
let forgedReviewerDenied = false;
try {
  await db.exec(
    "INSERT INTO source_rights_reviews(id,source_id,reviewer,round,decision,asset_hash,evidence,created_at) VALUES('FORGED','DS','C',0,'approved_reference_only','fixture2','{}','2026-10-28')",
  );
} catch {
  forgedReviewerDenied = true;
}
assert.ok(forgedReviewerDenied);
await db.query("SELECT set_config('app.user_id','C',false)");
assert.equal(
  (await db.query("SELECT * FROM cms_publish_schedules")).rows.length,
  1,
);
let ordinaryNoticeDenied = false;
try {
  await db.exec(
    "INSERT INTO notifications(id,user_id,body,read,created_at) VALUES('BADN','A','fixture',false,'2026-10-28')",
  );
} catch {
  ordinaryNoticeDenied = true;
}
assert.ok(ordinaryNoticeDenied);
await db.query("SELECT set_config('app.user_id','U',false)");
await db.exec(
  "INSERT INTO notifications(id,user_id,body,read,created_at) VALUES('GOODN','A','fixture',false,'2026-10-28')",
);
assert.equal((await db.query("SELECT * FROM notifications")).rows.length, 0);
await db.query("SELECT set_config('app.user_id','A',false)");
assert.equal((await db.query("SELECT * FROM notifications")).rows.length, 1);
await db.exec("RESET ROLE; SET ROLE mouchak_scheduler;");
await db.query("SELECT set_config('app.user_id','',false)");
assert.equal(
  (await db.query("SELECT * FROM cms_publish_schedules")).rows.length,
  1,
);
await db.exec("RESET ROLE");
const tables = await db.query(
  "SELECT count(*)::int AS n FROM information_schema.tables WHERE table_schema='public' AND table_type='BASE TABLE'",
);
const result = {
  engine: (await db.query("SELECT version()")).rows[0].version,
  schema_tables: tables.rows[0].n,
  tests: {
    no_identity_denied: true,
    cross_owner_denied: true,
    selected_snapshot_only: true,
    recipient_mutation_denied: true,
    revocation_denies: true,
    transfer_cross_workspace_link_denied: true,
    cms_role_isolation: true,
    dedicated_scheduler_role: true,
    rights_review_role_isolation: true,
    forged_reviewer_denied: true,
    operator_notice_insert_without_private_read: true,
    sql_recent_mfa_required: true,
  },
  external_postgres_networking_tested: false,
};
await writeFile(
  "docs/audit/collaboration-postgres.json",
  JSON.stringify(result, null, 2),
);
console.log(JSON.stringify(result));
await db.close();
