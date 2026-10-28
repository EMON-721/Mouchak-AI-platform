-- Apply as migration owner after manage migrate. App role must be NOSUPERUSER
-- NOBYPASSRLS and not own the schema. Keep auth/session tables inaccessible
-- directly to browsers. The backend sets app.user_id inside each transaction.
DO $$
DECLARE tab text;
BEGIN
  FOREACH tab IN ARRAY ARRAY['workspaces','tool_runs','private_assets','user_consents','feedback','notifications']
  LOOP
    EXECUTE format('ALTER TABLE %I ENABLE ROW LEVEL SECURITY',tab);
    EXECUTE format('ALTER TABLE %I FORCE ROW LEVEL SECURITY',tab);
    IF NOT EXISTS (SELECT 1 FROM pg_policies WHERE tablename=tab AND policyname='owner_only') THEN
      EXECUTE format('CREATE POLICY owner_only ON %I USING (user_id = current_setting(''app.user_id'',true)) WITH CHECK (user_id = current_setting(''app.user_id'',true))',tab);
    END IF;
  END LOOP;
END $$;
-- Immutable application audit rows: an operational role may insert/read; no
-- application UPDATE/DELETE privilege is granted in the production role guide.
