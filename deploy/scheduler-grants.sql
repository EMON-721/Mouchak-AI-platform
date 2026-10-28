-- Dedicated login created by the secure provisioning command; no role memberships.
GRANT USAGE ON SCHEMA public TO mouchak_scheduler;
GRANT SELECT(id,role,banned,mfa_enabled) ON users TO mouchak_scheduler;
GRANT SELECT,UPDATE ON cms_publish_schedules,cms_versions TO mouchak_scheduler;
GRANT SELECT,INSERT,UPDATE ON configuration TO mouchak_scheduler;
GRANT SELECT,INSERT ON admin_audit_events TO mouchak_scheduler;
