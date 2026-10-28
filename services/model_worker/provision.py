"""Additive PostgreSQL bootstrap with a checksum ledger and isolated server roles.

CLI credentials arrive via stdin, never argv or stdout. No existing password is
rotated. Use a dedicated authorized database and a TLS migration-owner connection.
"""
import hashlib, json, os, sys
from pathlib import Path
import psycopg
from psycopg import sql

ROOT = Path(__file__).resolve().parents[2]
ROLES = ("mouchak_app", "mouchak_inference", "mouchak_scheduler", "mouchak_retention")


def validate_passwords(passwords):
    if set(passwords) != set(ROLES) or len(set(passwords.values())) != len(ROLES):
        raise ValueError("Provide four distinct dedicated-role passwords")
    if any(not isinstance(v, str) or not 24 <= len(v) <= 128 or not v.isascii() for v in passwords.values()):
        raise ValueError("Dedicated-role passwords must be 24–128 ASCII characters")


def apply(connection, passwords):
    validate_passwords(passwords)
    with connection.transaction():
        connection.execute("SELECT pg_advisory_xact_lock(742006)")
        for role in ROLES:
            existing = connection.execute("SELECT oid,rolsuper,rolbypassrls,rolcreatedb,rolcreaterole,rolinherit,rolcanlogin FROM pg_roles WHERE rolname=%s", (role,)).fetchone()
            if existing:
                if any(existing[1:6]) or not existing[6]:
                    raise ValueError("Existing Mouchak role has unsafe attributes; no automatic role change was made")
                if connection.execute("SELECT 1 FROM pg_auth_members WHERE member=%s LIMIT 1", (existing[0],)).fetchone():
                    raise ValueError("A dedicated role must not be a member of another role")
                if connection.execute("SELECT 1 FROM pg_class WHERE relowner=%s AND relnamespace='public'::regnamespace LIMIT 1", (existing[0],)).fetchone():
                    raise ValueError("An application/worker role must not own application tables")
            else:
                verifier = connection.pgconn.encrypt_password(passwords[role].encode(), role.encode(), algorithm=b"scram-sha-256").decode()
                connection.execute(sql.SQL("CREATE ROLE {} LOGIN NOSUPERUSER NOCREATEDB NOCREATEROLE NOINHERIT NOBYPASSRLS PASSWORD {}").format(sql.Identifier(role), sql.Literal(verifier)))
            if connection.execute("SELECT has_schema_privilege(%s,'public','CREATE')", (role,)).fetchone()[0]:
                raise ValueError("Dedicated server roles must not have CREATE on the application schema")
        connection.execute("""CREATE TABLE IF NOT EXISTS schema_migration_history (
            filename text PRIMARY KEY, checksum text NOT NULL,
            applied_at timestamptz NOT NULL DEFAULT CURRENT_TIMESTAMP)""")
        connection.execute("REVOKE ALL ON schema_migration_history FROM PUBLIC")
        applied = []
        for path in sorted((ROOT / "database/migrations").glob("[0-9][0-9][0-9]_*.sql")):
            data = path.read_bytes()
            checksum = hashlib.sha256(data).hexdigest()
            previous = connection.execute("SELECT checksum FROM schema_migration_history WHERE filename=%s", (path.name,)).fetchone()
            if previous:
                if previous[0] != checksum:
                    raise ValueError("An applied migration changed; additive repair required")
                continue
            connection.execute(data.decode(), prepare=False)
            connection.execute("INSERT INTO schema_migration_history(filename,checksum) VALUES(%s,%s)", (path.name, checksum))
            applied.append(path.name)
        for name in ["app-grants.sql", "runtime-grants.sql", "scheduler-grants.sql"]:
            connection.execute((ROOT / "deploy" / name).read_text(), prepare=False)
        # Public-source metadata only. Preserve every existing source review.
        seed = "source-seed:2026-10-27-v2"
        if not connection.execute("SELECT 1 FROM configuration WHERE key=%s", (seed,)).fetchone():
            sources = json.loads((ROOT / "packages/module-registry/source-candidates.json").read_text())["sources"]
            for index, source in enumerate(sources):
                connection.execute("INSERT INTO dataset_sources(id,module,metadata_json,state) VALUES(%s,%s,%s,'candidate') ON CONFLICT(id) DO NOTHING",
                                   (f"SRC-{index+1:04}", source["module_id"], json.dumps(source, ensure_ascii=False)))
            connection.execute("INSERT INTO configuration(key,value) VALUES(%s,%s) ON CONFLICT(key) DO NOTHING", (seed, "true"))
    return {"applied": applied, "roles_checked": list(ROLES), "existing_passwords_rotated": False}


def provision(dsn, passwords):
    validate_passwords(passwords)
    if psycopg.conninfo.conninfo_to_dict(dsn).get("sslmode") != "verify-full":
        raise ValueError("Use sslmode=verify-full and a trusted PostgreSQL CA")
    with psycopg.connect(dsn) as connection:
        if not connection.pgconn.ssl_in_use:
            raise ValueError("Migration-owner connection must use TLS")
        # Existing roles require the supplied current credentials before any write.
        for role in ROLES:
            if connection.execute("SELECT 1 FROM pg_roles WHERE rolname=%s", (role,)).fetchone():
                with psycopg.connect(dsn, user=role, password=passwords[role]):
                    pass
        connection.commit()
        return apply(connection, passwords)


def main():
    try:
        settings = json.loads(sys.stdin.read(20000))
        result = provision(settings["migration_database_url"], settings["role_passwords"])
        print(json.dumps(result))
    except Exception:
        # Driver exceptions may contain credentials or SQL literals. Never print them.
        print("PostgreSQL provisioning failed; verify TLS, existing role credentials, safe role attributes and migration checksums.", file=sys.stderr)
        raise SystemExit(1)


if __name__ == "__main__":
    main()
