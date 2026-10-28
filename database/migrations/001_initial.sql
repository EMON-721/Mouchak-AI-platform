-- Initial schema. Generated from versioned SQLAlchemy domain definitions.
-- No DROP or destructive data rewrite.

CREATE TABLE admin_audit_events (
	id VARCHAR NOT NULL, 
	actor VARCHAR NOT NULL, 
	action VARCHAR NOT NULL, 
	target VARCHAR NOT NULL, 
	detail TEXT NOT NULL, 
	previous_hash VARCHAR NOT NULL, 
	event_hash VARCHAR NOT NULL, 
	created_at VARCHAR NOT NULL, 
	PRIMARY KEY (id)
)

;

CREATE TABLE cms_versions (
	id VARCHAR NOT NULL, 
	page VARCHAR NOT NULL, 
	body TEXT NOT NULL, 
	status VARCHAR NOT NULL, 
	author VARCHAR NOT NULL, 
	created_at VARCHAR NOT NULL, 
	PRIMARY KEY (id)
)

;
CREATE INDEX ix_cms_versions_page ON cms_versions (page);

CREATE TABLE configuration (
	key VARCHAR NOT NULL, 
	value TEXT NOT NULL, 
	PRIMARY KEY (key)
)

;

CREATE TABLE dataset_sources (
	id VARCHAR NOT NULL, 
	module VARCHAR NOT NULL, 
	metadata_json TEXT NOT NULL, 
	state VARCHAR NOT NULL, 
	evidence TEXT, 
	reviewer VARCHAR, 
	PRIMARY KEY (id)
)

;
CREATE INDEX ix_dataset_sources_module ON dataset_sources (module);

CREATE TABLE ingestion_jobs (
	id VARCHAR NOT NULL, 
	source_id VARCHAR NOT NULL, 
	owner VARCHAR NOT NULL, 
	payload TEXT NOT NULL, 
	state VARCHAR NOT NULL, 
	checksum VARCHAR NOT NULL, 
	created_at VARCHAR NOT NULL, 
	PRIMARY KEY (id)
)

;

CREATE TABLE users (
	id VARCHAR NOT NULL, 
	email VARCHAR NOT NULL, 
	password TEXT NOT NULL, 
	name VARCHAR NOT NULL, 
	role VARCHAR NOT NULL, 
	verified BOOLEAN NOT NULL, 
	banned BOOLEAN NOT NULL, 
	language VARCHAR NOT NULL, 
	mfa_secret TEXT, 
	mfa_enabled BOOLEAN NOT NULL, 
	created_at VARCHAR NOT NULL, 
	PRIMARY KEY (id)
)

;
CREATE UNIQUE INDEX ix_users_email ON users (email);

CREATE TABLE auth_tokens (
	id VARCHAR NOT NULL, 
	user_id VARCHAR NOT NULL, 
	purpose VARCHAR NOT NULL, 
	expires INTEGER NOT NULL, 
	PRIMARY KEY (id), 
	FOREIGN KEY(user_id) REFERENCES users (id) ON DELETE CASCADE
)

;

CREATE TABLE feedback (
	id VARCHAR NOT NULL, 
	user_id VARCHAR NOT NULL, 
	body TEXT NOT NULL, 
	created_at VARCHAR NOT NULL, 
	PRIMARY KEY (id), 
	FOREIGN KEY(user_id) REFERENCES users (id) ON DELETE CASCADE
)

;

CREATE TABLE notifications (
	id VARCHAR NOT NULL, 
	user_id VARCHAR NOT NULL, 
	body TEXT NOT NULL, 
	read BOOLEAN NOT NULL, 
	created_at VARCHAR NOT NULL, 
	PRIMARY KEY (id), 
	FOREIGN KEY(user_id) REFERENCES users (id) ON DELETE CASCADE
)

;
CREATE INDEX ix_notifications_user_id ON notifications (user_id);

CREATE TABLE private_assets (
	id VARCHAR NOT NULL, 
	user_id VARCHAR NOT NULL, 
	kind VARCHAR NOT NULL, 
	size INTEGER NOT NULL, 
	checksum VARCHAR NOT NULL, 
	path VARCHAR NOT NULL, 
	scan_state VARCHAR NOT NULL, 
	created_at VARCHAR NOT NULL, 
	PRIMARY KEY (id), 
	FOREIGN KEY(user_id) REFERENCES users (id) ON DELETE CASCADE
)

;
CREATE INDEX ix_private_assets_user_id ON private_assets (user_id);

CREATE TABLE sessions (
	id VARCHAR NOT NULL, 
	user_id VARCHAR NOT NULL, 
	csrf VARCHAR NOT NULL, 
	expires INTEGER NOT NULL, 
	last_seen INTEGER NOT NULL, 
	mfa_until INTEGER NOT NULL, 
	device VARCHAR NOT NULL, 
	PRIMARY KEY (id), 
	FOREIGN KEY(user_id) REFERENCES users (id) ON DELETE CASCADE
)

;
CREATE INDEX ix_sessions_user_id ON sessions (user_id);

CREATE TABLE user_consents (
	id VARCHAR NOT NULL, 
	user_id VARCHAR NOT NULL, 
	module VARCHAR NOT NULL, 
	purpose VARCHAR NOT NULL, 
	granted BOOLEAN NOT NULL, 
	created_at VARCHAR NOT NULL, 
	PRIMARY KEY (id), 
	FOREIGN KEY(user_id) REFERENCES users (id) ON DELETE CASCADE
)

;
CREATE INDEX ix_user_consents_user_id ON user_consents (user_id);

CREATE TABLE workspaces (
	id VARCHAR NOT NULL, 
	user_id VARCHAR NOT NULL, 
	name VARCHAR NOT NULL, 
	PRIMARY KEY (id), 
	FOREIGN KEY(user_id) REFERENCES users (id) ON DELETE CASCADE
)

;
CREATE INDEX ix_workspaces_user_id ON workspaces (user_id);

CREATE TABLE tool_runs (
	id VARCHAR NOT NULL, 
	user_id VARCHAR NOT NULL, 
	workspace_id VARCHAR NOT NULL, 
	module VARCHAR NOT NULL, 
	encrypted TEXT NOT NULL, 
	parent_id VARCHAR, 
	saved BOOLEAN NOT NULL, 
	idempotency_key VARCHAR, 
	created_at VARCHAR NOT NULL, 
	PRIMARY KEY (id), 
	FOREIGN KEY(user_id) REFERENCES users (id) ON DELETE CASCADE, 
	FOREIGN KEY(workspace_id) REFERENCES workspaces (id) ON DELETE CASCADE
)

;
CREATE INDEX ix_tool_runs_user_id ON tool_runs (user_id);
CREATE INDEX ix_tool_runs_workspace_id ON tool_runs (workspace_id);
CREATE INDEX ix_tool_runs_module ON tool_runs (module);
CREATE INDEX ix_tool_runs_idempotency_key ON tool_runs (idempotency_key);
