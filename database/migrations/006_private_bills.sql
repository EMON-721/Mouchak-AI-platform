-- Private bill histories and owner-specific ONNX artifacts; no shared training.

CREATE TABLE IF NOT EXISTS bill_history_entries (
	id VARCHAR NOT NULL,
	user_id VARCHAR NOT NULL,
	workspace_id VARCHAR NOT NULL,
	bill_type VARCHAR NOT NULL,
	month VARCHAR NOT NULL,
	encrypted TEXT NOT NULL,
	training_allowed BOOLEAN NOT NULL,
	is_demo BOOLEAN NOT NULL,
	revision INTEGER NOT NULL,
	created_at VARCHAR NOT NULL,
	PRIMARY KEY (id),
	CONSTRAINT uq_private_bill_month UNIQUE (user_id, workspace_id, bill_type, month),
	FOREIGN KEY(user_id) REFERENCES users (id) ON DELETE CASCADE,
	FOREIGN KEY(workspace_id) REFERENCES workspaces (id) ON DELETE CASCADE
)

;
CREATE INDEX IF NOT EXISTS ix_bill_history_entries_user_id ON bill_history_entries (user_id);
CREATE INDEX IF NOT EXISTS ix_bill_history_entries_workspace_id ON bill_history_entries (workspace_id);
ALTER TABLE bill_history_entries ENABLE ROW LEVEL SECURITY;
ALTER TABLE bill_history_entries FORCE ROW LEVEL SECURITY;
DROP POLICY IF EXISTS bill_owner ON bill_history_entries;
CREATE POLICY bill_owner ON bill_history_entries USING (user_id=current_setting('app.user_id',true))
WITH CHECK (user_id=current_setting('app.user_id',true) AND EXISTS(SELECT 1 FROM workspaces w WHERE w.id=workspace_id AND w.user_id=bill_history_entries.user_id));
REVOKE ALL ON bill_history_entries FROM PUBLIC;

CREATE TABLE IF NOT EXISTS bill_personal_models (
	id VARCHAR NOT NULL,
	user_id VARCHAR NOT NULL,
	workspace_id VARCHAR NOT NULL,
	bill_type VARCHAR NOT NULL,
	checksum VARCHAR(64) NOT NULL,
	encrypted TEXT NOT NULL,
	created_at VARCHAR NOT NULL,
	PRIMARY KEY (id),
	CONSTRAINT uq_private_bill_model UNIQUE (user_id, workspace_id, bill_type),
	FOREIGN KEY(user_id) REFERENCES users (id) ON DELETE CASCADE,
	FOREIGN KEY(workspace_id) REFERENCES workspaces (id) ON DELETE CASCADE
)

;
CREATE INDEX IF NOT EXISTS ix_bill_personal_models_user_id ON bill_personal_models (user_id);
CREATE INDEX IF NOT EXISTS ix_bill_personal_models_workspace_id ON bill_personal_models (workspace_id);
ALTER TABLE bill_personal_models ENABLE ROW LEVEL SECURITY;
ALTER TABLE bill_personal_models FORCE ROW LEVEL SECURITY;
DROP POLICY IF EXISTS bill_owner ON bill_personal_models;
CREATE POLICY bill_owner ON bill_personal_models USING (user_id=current_setting('app.user_id',true))
WITH CHECK (user_id=current_setting('app.user_id',true) AND EXISTS(SELECT 1 FROM workspaces w WHERE w.id=workspace_id AND w.user_id=bill_personal_models.user_id));
REVOKE ALL ON bill_personal_models FROM PUBLIC;
