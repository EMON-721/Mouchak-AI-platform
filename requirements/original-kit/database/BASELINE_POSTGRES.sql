-- REFERENCE migration blueprint. Validate with your DB framework before production.
-- UUID type supported by PostgreSQL 13+; application must enforce tenant/owner access.
CREATE TABLE IF NOT EXISTS portal_modules (
  id TEXT PRIMARY KEY, name TEXT NOT NULL, category TEXT NOT NULL,
  enabled BOOLEAN NOT NULL DEFAULT TRUE, menu_order INTEGER NOT NULL DEFAULT 100
);
CREATE TABLE IF NOT EXISTS user_tool_runs (
  run_id UUID PRIMARY KEY, user_id UUID NOT NULL, module_id TEXT NOT NULL REFERENCES portal_modules(id),
  input_type TEXT NOT NULL, status TEXT NOT NULL,
  input_asset_key TEXT, result_json JSONB, model_id TEXT, model_version TEXT,
  source_manifest JSONB, created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);
CREATE INDEX IF NOT EXISTS tool_runs_owner_idx ON user_tool_runs(user_id, created_at DESC);
CREATE TABLE IF NOT EXISTS dataset_sources (
  id UUID PRIMARY KEY, module_id TEXT NOT NULL, url TEXT NOT NULL,
  provenance JSONB NOT NULL, rights_status TEXT NOT NULL DEFAULT 'unreviewed',
  ingestion_status TEXT NOT NULL DEFAULT 'not_imported', approved_by UUID,
  approved_at TIMESTAMPTZ
);
CREATE TABLE IF NOT EXISTS portal_audit_log (
  id UUID PRIMARY KEY, actor_user_id UUID, action TEXT NOT NULL,
  target_type TEXT, target_id TEXT, metadata JSONB, created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);
ALTER TABLE user_tool_runs ENABLE ROW LEVEL SECURITY;
-- Example policy only; depends on set_config in trusted transaction or verified auth token.
-- CREATE POLICY runs_owner ON user_tool_runs FOR SELECT USING
--    (user_id::text = current_setting('app.user_id', true));
-- Real super-admin is NOT exempt from sensitive-data access requirements.
