-- Additive durable inference, private chunk uploads and shared request guard.

CREATE TABLE IF NOT EXISTS request_rate_buckets (
	subject VARCHAR(64) NOT NULL, 
	window_start INTEGER NOT NULL, 
	used INTEGER NOT NULL, 
	expires_at INTEGER NOT NULL, 
	PRIMARY KEY (subject, window_start)
)

;
CREATE INDEX IF NOT EXISTS ix_request_rate_buckets_expires_at ON request_rate_buckets (expires_at);

CREATE TABLE IF NOT EXISTS chunk_uploads (
	id VARCHAR NOT NULL, 
	user_id VARCHAR NOT NULL, 
	size INTEGER NOT NULL, 
	checksum VARCHAR(64) NOT NULL, 
	expires_at INTEGER NOT NULL, 
	asset_id VARCHAR, 
	state VARCHAR NOT NULL, 
	PRIMARY KEY (id), 
	FOREIGN KEY(user_id) REFERENCES users (id) ON DELETE CASCADE, 
	FOREIGN KEY(asset_id) REFERENCES private_assets (id) ON DELETE SET NULL
)

;
CREATE INDEX IF NOT EXISTS ix_chunk_uploads_expires_at ON chunk_uploads (expires_at);
CREATE INDEX IF NOT EXISTS ix_chunk_uploads_user_id ON chunk_uploads (user_id);

CREATE TABLE IF NOT EXISTS upload_parts (
	id VARCHAR NOT NULL, 
	upload_id VARCHAR NOT NULL, 
	part INTEGER NOT NULL, 
	checksum VARCHAR(64) NOT NULL, 
	encrypted TEXT NOT NULL, 
	PRIMARY KEY (id), 
	CONSTRAINT uq_upload_part UNIQUE (upload_id, part), 
	FOREIGN KEY(upload_id) REFERENCES chunk_uploads (id) ON DELETE CASCADE
)

;
CREATE INDEX IF NOT EXISTS ix_upload_parts_upload_id ON upload_parts (upload_id);

CREATE TABLE IF NOT EXISTS inference_jobs (
	id VARCHAR NOT NULL, 
	user_id VARCHAR NOT NULL, 
	session_id VARCHAR NOT NULL, 
	module VARCHAR NOT NULL, 
	request_key VARCHAR NOT NULL, 
	fingerprint VARCHAR(64) NOT NULL, 
	encrypted TEXT NOT NULL, 
	state VARCHAR NOT NULL, 
	attempts INTEGER NOT NULL, 
	claim_token VARCHAR, 
	lease_until INTEGER NOT NULL, 
	created_at INTEGER NOT NULL, 
	expires_at INTEGER NOT NULL, 
	run_id VARCHAR, 
	error VARCHAR, 
	PRIMARY KEY (id), 
	CONSTRAINT uq_inference_request UNIQUE (user_id, module, request_key), 
	FOREIGN KEY(user_id) REFERENCES users (id) ON DELETE CASCADE, 
	FOREIGN KEY(session_id) REFERENCES sessions (id) ON DELETE CASCADE, 
	FOREIGN KEY(run_id) REFERENCES tool_runs (id) ON DELETE SET NULL
)

;
CREATE INDEX IF NOT EXISTS ix_inference_claim ON inference_jobs (state, lease_until, created_at);
CREATE INDEX IF NOT EXISTS ix_inference_jobs_expires_at ON inference_jobs (expires_at);
CREATE INDEX IF NOT EXISTS ix_inference_jobs_session_id ON inference_jobs (session_id);
CREATE INDEX IF NOT EXISTS ix_inference_jobs_state ON inference_jobs (state);
CREATE INDEX IF NOT EXISTS ix_inference_jobs_user_id ON inference_jobs (user_id);

-- These are private server tables, never browser-accessible data APIs.
REVOKE ALL ON request_rate_buckets,chunk_uploads,upload_parts,inference_jobs FROM PUBLIC;
ALTER TABLE request_rate_buckets ENABLE ROW LEVEL SECURITY;
ALTER TABLE request_rate_buckets FORCE ROW LEVEL SECURITY;
DROP POLICY IF EXISTS service_only ON request_rate_buckets;
CREATE POLICY service_only ON request_rate_buckets
USING (current_user::text IN ('mouchak_app','mouchak_retention'))
WITH CHECK (current_user::text IN ('mouchak_app','mouchak_retention'));
ALTER TABLE chunk_uploads ENABLE ROW LEVEL SECURITY;
ALTER TABLE chunk_uploads FORCE ROW LEVEL SECURITY;
DROP POLICY IF EXISTS upload_owner ON chunk_uploads;
CREATE POLICY upload_owner ON chunk_uploads
USING (user_id=current_setting('app.user_id',true) OR current_user::text='mouchak_retention')
WITH CHECK (user_id=current_setting('app.user_id',true) AND
 (asset_id IS NULL OR EXISTS(SELECT 1 FROM private_assets a WHERE a.id=asset_id AND a.user_id=chunk_uploads.user_id)));
ALTER TABLE upload_parts ENABLE ROW LEVEL SECURITY;
ALTER TABLE upload_parts FORCE ROW LEVEL SECURITY;
DROP POLICY IF EXISTS part_owner ON upload_parts;
CREATE POLICY part_owner ON upload_parts
USING (current_user::text='mouchak_retention' OR EXISTS(SELECT 1 FROM chunk_uploads c WHERE c.id=upload_id AND c.user_id=current_setting('app.user_id',true)))
WITH CHECK (EXISTS(SELECT 1 FROM chunk_uploads c WHERE c.id=upload_id AND c.user_id=current_setting('app.user_id',true) AND c.state='uploading'));
ALTER TABLE inference_jobs ENABLE ROW LEVEL SECURITY;
ALTER TABLE inference_jobs FORCE ROW LEVEL SECURITY;
DROP POLICY IF EXISTS inference_owner ON inference_jobs;
CREATE POLICY inference_owner ON inference_jobs
USING (user_id=current_setting('app.user_id',true) OR current_user::text='mouchak_inference')
WITH CHECK (current_user::text='mouchak_inference' OR (user_id=current_setting('app.user_id',true) AND EXISTS(SELECT 1 FROM sessions s WHERE s.id=session_id AND s.user_id=inference_jobs.user_id)));
