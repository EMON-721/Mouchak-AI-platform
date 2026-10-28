-- Additive purpose-limited sharing and operations. Existing records are preserved.

CREATE TABLE IF NOT EXISTS support_access_grants (
	id VARCHAR NOT NULL, 
	user_id VARCHAR NOT NULL, 
	recipient_id VARCHAR NOT NULL, 
	run_id VARCHAR NOT NULL, 
	encrypted TEXT NOT NULL, 
	expires_at INTEGER NOT NULL, 
	revoked_at INTEGER, 
	created_at VARCHAR NOT NULL, 
	PRIMARY KEY (id), 
	FOREIGN KEY(user_id) REFERENCES users (id) ON DELETE CASCADE, 
	FOREIGN KEY(recipient_id) REFERENCES users (id) ON DELETE CASCADE, 
	FOREIGN KEY(run_id) REFERENCES tool_runs (id) ON DELETE CASCADE
)

;
CREATE INDEX IF NOT EXISTS ix_support_access_grants_recipient_id ON support_access_grants (recipient_id);
CREATE INDEX IF NOT EXISTS ix_support_access_grants_run_id ON support_access_grants (run_id);
CREATE INDEX IF NOT EXISTS ix_support_access_grants_user_id ON support_access_grants (user_id);
ALTER TABLE support_access_grants ENABLE ROW LEVEL SECURITY;
ALTER TABLE support_access_grants FORCE ROW LEVEL SECURITY;
DROP POLICY IF EXISTS scoped_access ON support_access_grants;
CREATE POLICY scoped_access ON support_access_grants USING ((user_id = current_setting('app.user_id',true)) OR (recipient_id=current_setting('app.user_id',true) AND COALESCE(NULLIF(current_setting('app.mfa_until',true),''),'0')::bigint > EXTRACT(EPOCH FROM CURRENT_TIMESTAMP) AND revoked_at IS NULL AND expires_at>EXTRACT(EPOCH FROM CURRENT_TIMESTAMP) AND EXISTS(SELECT 1 FROM users u WHERE u.id=recipient_id AND NOT u.banned AND u.mfa_enabled AND u.role IN ('support_agent','super_admin')))) WITH CHECK (user_id = current_setting('app.user_id',true) AND EXISTS(SELECT 1 FROM tool_runs r WHERE r.id=run_id AND r.user_id=support_access_grants.user_id) AND EXISTS(SELECT 1 FROM users u WHERE u.id=recipient_id AND NOT u.banned AND u.mfa_enabled AND u.role IN ('support_agent','super_admin')));

CREATE TABLE IF NOT EXISTS tool_transfers (
	id VARCHAR NOT NULL, 
	user_id VARCHAR NOT NULL, 
	source_run_id VARCHAR NOT NULL, 
	workspace_id VARCHAR NOT NULL, 
	target_module VARCHAR NOT NULL, 
	encrypted TEXT NOT NULL, 
	state VARCHAR NOT NULL, 
	consumed_run_id VARCHAR, 
	created_at VARCHAR NOT NULL, 
	PRIMARY KEY (id), 
	FOREIGN KEY(user_id) REFERENCES users (id) ON DELETE CASCADE, 
	FOREIGN KEY(source_run_id) REFERENCES tool_runs (id) ON DELETE CASCADE, 
	FOREIGN KEY(workspace_id) REFERENCES workspaces (id) ON DELETE CASCADE
)

;
CREATE INDEX IF NOT EXISTS ix_tool_transfers_source_run_id ON tool_transfers (source_run_id);
CREATE INDEX IF NOT EXISTS ix_tool_transfers_user_id ON tool_transfers (user_id);
CREATE INDEX IF NOT EXISTS ix_tool_transfers_workspace_id ON tool_transfers (workspace_id);
ALTER TABLE tool_transfers ENABLE ROW LEVEL SECURITY;
ALTER TABLE tool_transfers FORCE ROW LEVEL SECURITY;
DROP POLICY IF EXISTS scoped_access ON tool_transfers;
CREATE POLICY scoped_access ON tool_transfers USING (user_id = current_setting('app.user_id',true)) WITH CHECK (user_id = current_setting('app.user_id',true) AND EXISTS(SELECT 1 FROM tool_runs r WHERE r.id=source_run_id AND r.user_id=tool_transfers.user_id) AND EXISTS(SELECT 1 FROM workspaces w WHERE w.id=workspace_id AND w.user_id=tool_transfers.user_id) AND (consumed_run_id IS NULL OR EXISTS(SELECT 1 FROM tool_runs r WHERE r.id=consumed_run_id AND r.user_id=tool_transfers.user_id)));

CREATE TABLE IF NOT EXISTS cms_publish_schedules (
	id VARCHAR NOT NULL, 
	version_id VARCHAR NOT NULL, 
	author VARCHAR NOT NULL, 
	due_at INTEGER NOT NULL, 
	base_hash VARCHAR NOT NULL, 
	state VARCHAR NOT NULL, 
	created_at VARCHAR NOT NULL, 
	PRIMARY KEY (id), 
	FOREIGN KEY(version_id) REFERENCES cms_versions (id) ON DELETE CASCADE
)

;
CREATE INDEX IF NOT EXISTS ix_cms_publish_schedules_due_at ON cms_publish_schedules (due_at);
CREATE INDEX IF NOT EXISTS ix_cms_publish_schedules_version_id ON cms_publish_schedules (version_id);
ALTER TABLE cms_publish_schedules ENABLE ROW LEVEL SECURITY;
ALTER TABLE cms_publish_schedules FORCE ROW LEVEL SECURITY;
DROP POLICY IF EXISTS scoped_access ON cms_publish_schedules;
CREATE POLICY scoped_access ON cms_publish_schedules USING (current_user='mouchak_scheduler' OR (EXISTS (SELECT 1 FROM users u WHERE u.id=current_setting('app.user_id',true) AND NOT u.banned AND COALESCE(NULLIF(current_setting('app.mfa_until',true),''),'0')::bigint > EXTRACT(EPOCH FROM CURRENT_TIMESTAMP) AND u.role IN ('super_admin','content_editor')))) WITH CHECK (current_user='mouchak_scheduler' OR (EXISTS (SELECT 1 FROM users u WHERE u.id=current_setting('app.user_id',true) AND NOT u.banned AND COALESCE(NULLIF(current_setting('app.mfa_until',true),''),'0')::bigint > EXTRACT(EPOCH FROM CURRENT_TIMESTAMP) AND u.role IN ('super_admin','content_editor'))));

CREATE TABLE IF NOT EXISTS source_rights_reviews (
	id VARCHAR NOT NULL, 
	source_id VARCHAR NOT NULL, 
	reviewer VARCHAR NOT NULL, 
	round INTEGER NOT NULL, 
	decision VARCHAR NOT NULL, 
	asset_hash VARCHAR NOT NULL, 
	evidence TEXT NOT NULL, 
	created_at VARCHAR NOT NULL, 
	PRIMARY KEY (id), 
	FOREIGN KEY(source_id) REFERENCES dataset_sources (id) ON DELETE CASCADE
)

;
CREATE INDEX IF NOT EXISTS ix_source_rights_reviews_source_id ON source_rights_reviews (source_id);
ALTER TABLE source_rights_reviews ENABLE ROW LEVEL SECURITY;
ALTER TABLE source_rights_reviews FORCE ROW LEVEL SECURITY;
DROP POLICY IF EXISTS scoped_access ON source_rights_reviews;
CREATE POLICY scoped_access ON source_rights_reviews USING (EXISTS (SELECT 1 FROM users u WHERE u.id=current_setting('app.user_id',true) AND NOT u.banned AND COALESCE(NULLIF(current_setting('app.mfa_until',true),''),'0')::bigint > EXTRACT(EPOCH FROM CURRENT_TIMESTAMP) AND u.role IN ('super_admin','dataset_reviewer'))) WITH CHECK (EXISTS (SELECT 1 FROM users u WHERE u.id=current_setting('app.user_id',true) AND NOT u.banned AND COALESCE(NULLIF(current_setting('app.mfa_until',true),''),'0')::bigint > EXTRACT(EPOCH FROM CURRENT_TIMESTAMP) AND u.role IN ('super_admin','dataset_reviewer')) AND reviewer=current_setting('app.user_id',true));
-- A fresh MFA-gated Super Admin API may create an in-app service notice.
-- This adds INSERT only; the owner-only SELECT/UPDATE/DELETE policy stays in force.
DROP POLICY IF EXISTS operator_notice_insert ON notifications;
CREATE POLICY operator_notice_insert ON notifications FOR INSERT WITH CHECK (
  EXISTS(SELECT 1 FROM users u WHERE u.id=current_setting('app.user_id',true)
    AND NOT u.banned AND u.mfa_enabled AND COALESCE(NULLIF(current_setting('app.mfa_until',true),''),'0')::bigint > EXTRACT(EPOCH FROM CURRENT_TIMESTAMP) AND u.role='super_admin')
);
