-- Existing API capabilities, private server login only. Apply as migration owner.
-- mouchak_app must not own tables, be superuser, inherit worker roles or bypass RLS.
GRANT USAGE ON SCHEMA public TO mouchak_app;
GRANT SELECT,INSERT,UPDATE,DELETE ON users,sessions,auth_tokens TO mouchak_app;
GRANT SELECT,INSERT,UPDATE,DELETE ON workspaces,tool_runs,private_assets,user_consents,feedback,notifications TO mouchak_app;
GRANT SELECT,INSERT,UPDATE ON configuration,cms_versions,dataset_sources,ingestion_jobs TO mouchak_app;
GRANT SELECT,INSERT ON admin_audit_events,stock_movements,source_rights_reviews TO mouchak_app;
GRANT SELECT,INSERT,UPDATE ON stock_items,support_access_grants,tool_transfers,cms_publish_schedules TO mouchak_app;
-- New inference/chunk/rate capabilities and separate worker grants:
-- apply runtime-grants.sql after this file. Never grant any of these to anon,
-- authenticated, browser clients, or a publicly exposed SQL/data API.
