-- Run as migration owner AFTER migrations 001-005 and secure role provisioning.
-- Create the named logins through the host's secret manager, never this file.
-- All roles: NOSUPERUSER NOCREATEDB NOCREATEROLE NOINHERIT NOBYPASSRLS.
-- No API/web role may be a member of a worker role or own application tables.

GRANT USAGE ON SCHEMA public TO mouchak_app,mouchak_inference,mouchak_retention;
GRANT SELECT,INSERT,UPDATE,DELETE ON chunk_uploads,upload_parts TO mouchak_app;
GRANT SELECT,INSERT,UPDATE ON inference_jobs TO mouchak_app;
GRANT SELECT,INSERT,UPDATE ON request_rate_buckets TO mouchak_app;

GRANT SELECT,UPDATE ON inference_jobs TO mouchak_inference;
GRANT SELECT(id,role,banned,verified) ON users TO mouchak_inference;
GRANT SELECT(id,user_id,expires,last_seen) ON sessions TO mouchak_inference;
GRANT SELECT ON workspaces,private_assets,tool_runs,configuration,tool_transfers,admin_audit_events TO mouchak_inference;
GRANT SELECT ON dataset_sources TO mouchak_inference;
GRANT INSERT ON tool_runs,user_consents,admin_audit_events TO mouchak_inference;
GRANT UPDATE(parent_id) ON tool_runs TO mouchak_inference;
GRANT UPDATE(state,consumed_run_id) ON tool_transfers TO mouchak_inference;

GRANT SELECT(id,role),DELETE ON users TO mouchak_retention;
-- PostgreSQL SELECT ... FOR UPDATE requires UPDATE on at least one column.
-- The cleanup code locks this row; it never changes its identifier.
GRANT UPDATE(id) ON users TO mouchak_retention;
GRANT SELECT(id,user_id,expires) ON sessions TO mouchak_retention;
GRANT SELECT ON private_assets TO mouchak_retention;
GRANT SELECT,DELETE ON chunk_uploads,upload_parts,request_rate_buckets TO mouchak_retention;

-- Existing API/auth/CMS and scheduler grants remain in the prior deployment
-- guide. This file adds only the new runtime/cleanup capabilities.

GRANT SELECT,INSERT,UPDATE,DELETE ON bill_history_entries,bill_personal_models TO mouchak_app;
