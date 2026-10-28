import json, sqlite3
from pathlib import Path
import pytest
from cryptography.fernet import Fernet
from services.model_worker.backup import create_backup, restore_backup


@pytest.fixture
def state(tmp_path):
    p = tmp_path / "source"
    p.mkdir()
    data_key = Fernet.generate_key()
    (p / "encryption.key").write_bytes(data_key)
    (p / "assets").mkdir()
    (p / "assets" / "owned-file").write_bytes(
        Fernet(data_key).encrypt(b"owned synthetic fixture")
    )
    with sqlite3.connect(p / "development.db") as db:
        db.executescript(
            "CREATE TABLE private_assets(id TEXT,path TEXT);CREATE TABLE sessions(id TEXT);CREATE TABLE auth_tokens(id TEXT);CREATE TABLE support_access_grants(id TEXT,revoked_at INTEGER);CREATE TABLE cms_publish_schedules(id TEXT,state TEXT);CREATE TABLE records(id TEXT,encrypted TEXT);"
        )
        db.execute(
            "INSERT INTO private_assets VALUES (?,?)",
            ("owned-file", str(p / "assets" / "owned-file")),
        )
        db.execute("INSERT INTO sessions VALUES('old-session')")
        db.execute("INSERT INTO auth_tokens VALUES('old-token')")
        db.execute("INSERT INTO support_access_grants VALUES('old-grant',NULL)")
        db.execute(
            "INSERT INTO cms_publish_schedules VALUES('old-schedule','scheduled')"
        )
        db.execute(
            "INSERT INTO records VALUES(?,?)",
            (
                "original-record",
                Fernet(data_key).encrypt(b"private synthetic result").decode(),
            ),
        )
    return p, Fernet.generate_key()


def test_encrypted_backup_restore_drill_preserves_records_and_revokes_access(
    state, tmp_path
):
    p, key = state
    archive = tmp_path / "recovery.mouchak"
    created = create_backup(p, archive, key)
    assert created["archive_created"]
    assert b"private synthetic" not in archive.read_bytes()
    assert archive.stat().st_mode & 0o777 == 0o600
    target = tmp_path / "restored"
    assert restore_backup(archive, target, key, True)["verified"]
    assert not target.exists()
    r = restore_backup(archive, target, key)
    assert r["sessions_revoked"] and r["support_grants_revoked"]
    with sqlite3.connect(target / "development.db") as db:
        assert db.execute("SELECT count(*) FROM sessions").fetchone()[0] == 0
        assert db.execute("SELECT count(*) FROM auth_tokens").fetchone()[0] == 0
        assert db.execute("SELECT revoked_at FROM support_access_grants").fetchone()[0]
        assert (
            db.execute("SELECT state FROM cms_publish_schedules").fetchone()[0]
            == "cancelled_on_restore"
        )
        value = db.execute(
            "SELECT encrypted FROM records WHERE id='original-record'"
        ).fetchone()[0]
        cipher = Fernet((target / "encryption.key").read_bytes())
        assert cipher.decrypt(value.encode()) == b"private synthetic result"
        stored = Path(db.execute("SELECT path FROM private_assets").fetchone()[0])
        assert stored == target / "assets" / "owned-file"
        assert cipher.decrypt(stored.read_bytes()) == b"owned synthetic fixture"


def test_backup_tamper_wrong_key_existing_destination_and_missing_asset(
    state, tmp_path
):
    p, key = state
    archive = tmp_path / "recovery.mouchak"
    create_backup(p, archive, key)
    with pytest.raises(ValueError):
        restore_backup(archive, tmp_path / "wrong-key", Fernet.generate_key())
    target = tmp_path / "existing"
    target.mkdir()
    (target / "keep").write_text("keep")
    with pytest.raises(ValueError):
        restore_backup(archive, target, key)
    assert (target / "keep").read_text() == "keep"
    data = bytearray(archive.read_bytes())
    data[len(data) // 2] ^= 1
    archive.write_bytes(data)
    with pytest.raises(ValueError):
        restore_backup(archive, tmp_path / "tampered", key)
    (p / "assets" / "owned-file").unlink()
    with pytest.raises(ValueError):
        create_backup(p, tmp_path / "missing.mouchak", key)


def test_backup_rejects_key_reuse_symlinks_and_existing_archive(state, tmp_path):
    p, key = state
    with pytest.raises(ValueError):
        create_backup(
            p, tmp_path / "same-key.mouchak", (p / "encryption.key").read_bytes()
        )
    archive = tmp_path / "existing.mouchak"
    archive.write_bytes(b"keep")
    with pytest.raises(ValueError):
        create_backup(p, archive, key)
    assert archive.read_bytes() == b"keep"
    (p / "assets" / "bad-link").symlink_to(tmp_path / "other")
    with pytest.raises(ValueError):
        create_backup(p, tmp_path / "symlink.mouchak", key)


def test_authenticated_archive_rejects_path_traversal_without_writing(state, tmp_path):
    import io, zipfile, hashlib

    p, key = state
    bad = b"owned fixture"
    name = "../escape"
    manifest = {
        "format": "mouchak-local-recovery-v1",
        "files": {name: {"bytes": len(bad), "sha256": hashlib.sha256(bad).hexdigest()}},
    }
    b = io.BytesIO()
    with zipfile.ZipFile(b, "w") as z:
        z.writestr("manifest.json", json.dumps(manifest))
        z.writestr(name, bad)
    archive = tmp_path / "unsafe.mouchak"
    archive.write_bytes(Fernet(key).encrypt(b.getvalue()))
    with pytest.raises(ValueError):
        restore_backup(archive, tmp_path / "target", key)
    assert not (tmp_path / "escape").exists()
    assert not (tmp_path / "target").exists()
