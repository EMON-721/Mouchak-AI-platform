"""Encrypted local recovery archives for development/restore drills.

Production PostgreSQL and S3 need provider-native consistent backups; this tool
refuses that topology rather than claiming a local SQLite copy covers it.
"""

import argparse, hashlib, io, json, os, re, shutil, sqlite3, tempfile, time, zipfile
from pathlib import Path
from cryptography.fernet import Fernet, InvalidToken

MAX_BYTES = 100 * 1024 * 1024


def cipher(key):
    try:
        return Fernet(key.encode() if isinstance(key, str) else key)
    except Exception as e:
        raise ValueError("A valid independent BACKUP_ENCRYPTION_KEY is required") from e


def create_backup(state, archive, backup_key, data_key=None):
    state = Path(state).resolve()
    archive = Path(archive)
    if archive.exists():
        raise ValueError("Archive already exists; choose a new path")
    if (
        state not in (state / "development.db").resolve().parents
        or not (state / "development.db").is_file()
    ):
        raise ValueError("An existing local development database is required")
    key = (data_key.encode() if isinstance(data_key, str) else data_key) or (
        state / "encryption.key"
    ).read_bytes().strip()
    if (state / "encryption.key").is_symlink():
        raise ValueError("Symlinked data keys are not supported")
    cipher(key)
    if key == (backup_key.encode() if isinstance(backup_key, str) else backup_key):
        raise ValueError("Backup and data encryption keys must be different")
    enc = cipher(backup_key)
    files = {}
    with tempfile.TemporaryDirectory(prefix="mouchak-backup-") as folder:
        snapshot = Path(folder) / "snapshot.db"
        with sqlite3.connect(
            f'file:{state / "development.db"}?mode=ro', uri=True
        ) as src, sqlite3.connect(snapshot) as dest:
            src.backup(dest)
        with sqlite3.connect(snapshot) as db:
            if db.execute("PRAGMA integrity_check").fetchone()[0] != "ok":
                raise ValueError("Database integrity check failed")
            tables = {
                r[0]
                for r in db.execute("SELECT name FROM sqlite_master WHERE type='table'")
            }
            if "private_assets" in tables:
                if db.execute(
                    "SELECT count(*) FROM private_assets WHERE path LIKE 's3:%'"
                ).fetchone()[0]:
                    raise ValueError(
                        "S3 object backup requires provider-native backup coordination"
                    )
        if snapshot.stat().st_size + len(key) > MAX_BYTES:
            raise ValueError("Local database exceeds the recovery size limit")
        files["development.db"] = snapshot.read_bytes()
        files["encryption.key"] = key
        asset_root = state / "assets"
        if asset_root.is_symlink():
            raise ValueError("Symlinked asset roots are not supported")
        if asset_root.exists():
            for p in asset_root.iterdir():
                if (
                    p.is_symlink()
                    or not p.is_file()
                    or not re.fullmatch(r"[A-Za-z0-9-]{1,100}", p.name)
                ):
                    raise ValueError("Unexpected private asset entry")
                if sum(map(len, files.values())) + p.stat().st_size > MAX_BYTES:
                    raise ValueError("Private assets exceed the recovery size limit")
                files["assets/" + p.name] = p.read_bytes()
        with sqlite3.connect(snapshot) as db:
            if "private_assets" in tables:
                for (aid,) in db.execute("SELECT id FROM private_assets"):
                    if "assets/" + aid not in files:
                        raise ValueError(
                            "An asset changed or is missing; retry a consistent backup"
                        )
    size = sum(map(len, files.values()))
    if size > MAX_BYTES:
        raise ValueError("Local recovery archive exceeds the 100 MiB limit")
    manifest = {
        "format": "mouchak-local-recovery-v1",
        "created_at_epoch": int(time.time()),
        "production_postgres": False,
        "files": {
            name: {"bytes": len(value), "sha256": hashlib.sha256(value).hexdigest()}
            for name, value in files.items()
        },
    }
    if size + len(json.dumps(manifest).encode()) > MAX_BYTES:
        raise ValueError("Recovery manifest exceeds the archive limit")
    stream = io.BytesIO()
    with zipfile.ZipFile(stream, "w", zipfile.ZIP_DEFLATED) as z:
        z.writestr("manifest.json", json.dumps(manifest))
        for name, value in files.items():
            z.writestr(name, value)
    token = enc.encrypt(stream.getvalue())
    archive.parent.mkdir(parents=True, exist_ok=True)
    fd = os.open(archive, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
    with os.fdopen(fd, "wb") as f:
        f.write(token)
    return {
        "archive_created": True,
        "files": len(files),
        "encrypted_bytes": len(token),
        "sha256": hashlib.sha256(token).hexdigest(),
        "production_backup_verified": False,
    }


def read_archive(archive, backup_key):
    p = Path(archive)
    if p.stat().st_size > MAX_BYTES * 2:
        raise ValueError("Recovery archive is too large")
    try:
        clear = cipher(backup_key).decrypt(p.read_bytes())
    except InvalidToken as e:
        raise ValueError("Recovery archive authentication failed") from e
    with zipfile.ZipFile(io.BytesIO(clear)) as z:
        names = z.namelist()
        if (
            len(names) != len(set(names))
            or sum(i.file_size for i in z.infolist()) > MAX_BYTES
        ):
            raise ValueError("Invalid or oversized recovery entries")
        manifest = json.loads(z.read("manifest.json"))
        if manifest.get("format") != "mouchak-local-recovery-v1" or set(names) != set(
            manifest.get("files", {})
        ) | {"manifest.json"}:
            raise ValueError("Unsupported recovery manifest")
        files = {}
        for name, meta in manifest["files"].items():
            if name not in ["development.db", "encryption.key"] and not re.fullmatch(
                r"assets/[A-Za-z0-9-]{1,100}", name
            ):
                raise ValueError("Unsafe recovery path")
            value = z.read(name)
            if (
                len(value) != meta["bytes"]
                or hashlib.sha256(value).hexdigest() != meta["sha256"]
            ):
                raise ValueError("Recovery checksum mismatch")
            files[name] = value
        if not {"development.db", "encryption.key"} <= files.keys() or not files[
            "development.db"
        ].startswith(b"SQLite format 3\0"):
            raise ValueError("Missing recovery data")
        cipher(files["encryption.key"])
        return manifest, files


def restore_backup(archive, destination, backup_key, dry_run=False):
    manifest, files = read_archive(archive, backup_key)
    target = Path(destination).resolve()
    if target.exists():
        raise ValueError(
            "Restore destination must be a new directory; existing data is never overwritten"
        )
    if dry_run:
        return {
            "verified": True,
            "files": len(files),
            "dry_run": True,
            "production_backup_verified": False,
        }
    target.parent.mkdir(parents=True, exist_ok=True)
    target.mkdir(mode=0o700)
    try:
        for name, value in files.items():
            p = target / name
            p.parent.mkdir(parents=True, exist_ok=True, mode=0o700)
            p.write_bytes(value)
            p.chmod(0o600)
        with sqlite3.connect(target / "development.db") as db:
            if db.execute("PRAGMA integrity_check").fetchone()[0] != "ok":
                raise ValueError("Restored database integrity check failed")
            tables = {
                r[0]
                for r in db.execute("SELECT name FROM sqlite_master WHERE type='table'")
            }
            # Never revive old logins, support access or scheduled publication.
            for table in ["sessions", "auth_tokens"]:
                if table in tables:
                    db.execute(f"DELETE FROM {table}")
            if "support_access_grants" in tables:
                db.execute(
                    "UPDATE support_access_grants SET revoked_at=? WHERE revoked_at IS NULL",
                    (int(time.time()),),
                )
            if "cms_publish_schedules" in tables:
                db.execute(
                    "UPDATE cms_publish_schedules SET state='cancelled_on_restore' WHERE state IN ('scheduled','processing')"
                )
            if "private_assets" in tables:
                for (aid,) in db.execute("SELECT id FROM private_assets").fetchall():
                    if "assets/" + aid not in files:
                        raise ValueError("Missing restored asset")
                    db.execute(
                        "UPDATE private_assets SET path=? WHERE id=?",
                        (str(target / "assets" / aid), aid),
                    )
            db.commit()
    except Exception:
        shutil.rmtree(target)
        raise
    return {
        "restored": True,
        "files": len(files),
        "sessions_revoked": True,
        "support_grants_revoked": True,
        "scheduled_publishing_cancelled": True,
        "production_backup_verified": False,
    }


def main():
    p = argparse.ArgumentParser()
    p.add_argument("command", choices=["create", "restore"])
    p.add_argument("--archive", required=True)
    p.add_argument("--state", default=".state")
    p.add_argument("--destination")
    p.add_argument("--dry-run", action="store_true")
    args = p.parse_args()
    if os.getenv("MOUCHAK_ENV") == "production" or os.getenv(
        "DATABASE_URL", ""
    ).startswith("postgresql"):
        raise SystemExit(
            "Use provider-native PostgreSQL/S3 backups and a separately verified recovery runbook"
        )
    key = os.getenv("BACKUP_ENCRYPTION_KEY", "")
    try:
        if args.command == "create":
            result = create_backup(
                args.state, args.archive, key, os.getenv("DATA_ENCRYPTION_KEY")
            )
        else:
            if not args.destination:
                raise ValueError("--destination is required")
            result = restore_backup(args.archive, args.destination, key, args.dry_run)
        print(json.dumps(result))
    except (ValueError, OSError, KeyError, zipfile.BadZipFile) as e:
        raise SystemExit(str(e))


if __name__ == "__main__":
    main()
