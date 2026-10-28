import io, json, time
import pytest
from services.model_worker.main import app, MODULES
from services.model_worker.store import (
    DB,
    Run,
    Asset,
    User,
    CMSVersion,
    Source,
    Audit,
    Session,
    open_sealed,
)
from services.model_worker.auth import totp, digest
from fastapi.testclient import TestClient
from conftest import Client
from test_domain import SAMPLES


def make_run(c, slug="billdetect-ai", inputs=None, key=None):
    return c.request(
        "POST",
        f"/api/tools/{slug}/runs",
        json={
            "inputs": inputs or SAMPLES[MODULES[slug]["engine"]],
            "consent": True,
            "idempotency_key": key,
        },
    )


def test_privacy_owner_and_superadmin_are_not_universal_readers(user):
    r = make_run(user)
    assert r.status_code == 201
    r = r.json()
    rid = r["id"]
    with TestClient(app) as raw:
        other = Client(raw).register().admin()
        assert other.request("GET", "/api/runs/" + rid).status_code == 404
        assert other.request("DELETE", "/api/runs/" + rid).status_code == 404
        assert other.request("GET", "/api/runs/" + rid + "/export").status_code == 404
        assert other.request("GET", "/api/admin/overview").status_code == 200
        overview = other.request("GET", "/api/admin/overview").json()
        assert "inputs" not in str(overview)


def test_csrf_guard(user):
    r = user.client.post(
        "/api/tools/billdetect-ai/runs",
        json={"inputs": SAMPLES["bill"], "consent": True},
    )
    assert r.status_code == 403
    assert (
        user.request(
            "POST",
            "/api/tools/billdetect-ai/runs",
            json={"inputs": SAMPLES["bill"], "consent": True},
            headers={"origin": "https://attacker.test"},
        ).status_code
        == 403
    )


def test_client_cannot_assign_own_admin(client):
    r = client.request(
        "POST",
        "/api/auth/register",
        json={
            "email": "admin-attempt@example.test",
            "password": "Test-password-12345!",
            "name": "Attempt",
            "role": "super_admin",
        },
    )
    assert r.status_code == 422


def test_user_cannot_edit_cms(user):
    assert (
        user.request(
            "POST", "/api/admin/cms", json={"value": {"page": "home", "body": {}}}
        ).status_code
        == 403
    )


def test_admin_requires_mfa(user):
    with DB.begin() as db:
        db.get(User, user.user["id"]).role = "super_admin"
    r = user.request("GET", "/api/admin/overview")
    assert r.status_code == 403 and r.json()["detail"] == "MFA_REQUIRED"


def test_mfa_replay_is_rejected(admin):
    r = admin.request(
        "POST", "/api/auth/mfa/verify", json={"value": {"code": totp(admin.secret)}}
    )
    assert r.status_code == 401


def test_encrypted_at_rest(user):
    private = "PRIVATE-UNIQUE-SECRET-RECORD"
    r = make_run(user, "carejourney-ai", {"text": private})
    assert r.status_code == 201
    with DB() as db:
        stored = db.get(Run, r.json()["id"])
        assert private not in stored.encrypted
        assert open_sealed(stored.encrypted)["inputs"]["text"] == private
    export = user.request("GET", "/api/privacy/export")
    assert private in export.text


def test_versioned_cms_publish_and_rollback(admin):
    ids = []
    for title in ["First controlled title", "Second controlled title"]:
        r = admin.request(
            "POST",
            "/api/admin/cms",
            json={"value": {"page": "qa-only", "body": {"title_en": title}}},
        )
        assert r.status_code == 201
        ids.append(r.json()["id"])
        assert (
            admin.request("POST", "/api/admin/cms/" + ids[-1] + "/publish").status_code
            == 200
        )
    assert (
        admin.request("GET", "/api/public/cms/qa-only").json()["title_en"]
        == "Second controlled title"
    )
    assert (
        admin.request("POST", "/api/admin/cms/" + ids[0] + "/publish").status_code
        == 200
    )
    assert (
        admin.request("GET", "/api/public/cms/qa-only").json()["title_en"]
        == "First controlled title"
    )
    with DB() as db:
        assert db.get(CMSVersion, ids[1]).body.find("Second controlled title") >= 0


def test_cms_rejects_active_html(admin):
    assert (
        admin.request(
            "POST",
            "/api/admin/cms",
            json={
                "value": {
                    "page": "qa-only",
                    "body": {"title_en": "<script>alert(1)</script>"},
                }
            },
        ).status_code
        == 422
    )


def test_dataset_cannot_ingest_candidate(admin):
    r = admin.request(
        "POST",
        "/api/admin/datasets/import/dry-run",
        json={"value": {"source_id": "SRC-0001", "csv": "name,value\nx,1"}},
    )
    assert r.status_code == 422
    r = admin.request(
        "PATCH",
        "/api/admin/sources/SRC-0001",
        json={"value": {"state": "approved_train_and_reuse", "evidence": "yes"}},
    )
    assert r.status_code == 422


def test_dataset_rights_dryrun_stage_rollback(admin):
    # Test-only rights evidence, confined to temporary DB. Not a real rights clearance.
    evidence = "TEST-ONLY hypothetical permission, no production approval: CC0 exercise, original synthetic rows, no personal data."
    r = admin.request(
        "PATCH",
        "/api/admin/sources/SRC-0001",
        json={"value": {"state": "approved_train_and_reuse", "evidence": evidence}},
    )
    assert r.status_code == 200
    r = admin.request(
        "POST",
        "/api/admin/datasets/import/dry-run",
        json={
            "value": {
                "source_id": "SRC-0001",
                "csv": "item,value\noriginal-test,1\noriginal-test,1",
            }
        },
    )
    assert r.status_code == 201
    assert r.json()["duplicates"] == 1
    jid = r.json()["job_id"]
    assert (
        admin.request("POST", "/api/admin/datasets/import/" + jid + "/approve").json()[
            "state"
        ]
        == "approved_staged"
    )
    assert (
        admin.request("POST", "/api/admin/datasets/import/" + jid + "/rollback").json()[
            "rolled_back"
        ]
        is True
    )
    admin.request(
        "PATCH",
        "/api/admin/sources/SRC-0001",
        json={"value": {"state": "candidate", "evidence": None}},
    )


def test_source_revocation_blocks_pending_import(admin):
    evidence = "TEST-ONLY original author permission for a local non-production exercise, never real source approval."
    admin.request(
        "PATCH",
        "/api/admin/sources/SRC-0001",
        json={"value": {"state": "approved_train_and_reuse", "evidence": evidence}},
    )
    r = admin.request(
        "POST",
        "/api/admin/datasets/import/dry-run",
        json={"value": {"source_id": "SRC-0001", "csv": "item,value\ntest,1"}},
    )
    assert r.status_code == 201
    jid = r.json()["job_id"]
    admin.request(
        "PATCH",
        "/api/admin/sources/SRC-0001",
        json={"value": {"state": "revoked", "evidence": evidence}},
    )
    assert (
        admin.request(
            "POST", "/api/admin/datasets/import/" + jid + "/approve"
        ).status_code
        == 422
    )
    admin.request(
        "PATCH",
        "/api/admin/sources/SRC-0001",
        json={"value": {"state": "candidate", "evidence": None}},
    )


def test_invalid_and_oversized_file(user):
    assert (
        user.request(
            "POST",
            "/api/upload",
            data={"consent": "true"},
            files={"file": ("not-real.png", b"<svg onload=alert(1)>", "image/png")},
        ).status_code
        == 422
    )
    assert (
        user.request(
            "POST",
            "/api/upload",
            data={"consent": "false"},
            files={"file": ("not-real.png", b"not valid", "image/png")},
        ).status_code
        == 422
    )
    assert (
        user.request(
            "POST",
            "/api/upload",
            data={"consent": "true"},
            files={
                "file": (
                    "too-big.pdf",
                    b"%PDF-" + b"A" * (10 * 1024 * 1024),
                    "application/pdf",
                )
            },
        ).status_code
        == 413
    )


def test_ocr_file_ownership(user):
    from PIL import Image

    buf = io.BytesIO()
    Image.new("RGB", (100, 100), "white").save(buf, format="PNG")
    r = user.request(
        "POST",
        "/api/upload",
        data={"consent": "true"},
        files={"file": ("owned.png", buf.getvalue(), "image/png")},
    )
    assert r.status_code == 201
    aid = r.json()["id"]
    with DB() as db:
        asset = db.get(Asset, aid)
        assert b"PNG" not in __import__("pathlib").Path(asset.path).read_bytes()[:10]
    with TestClient(app) as raw:
        other = Client(raw).register().admin()
        for method, path in [
            ("GET", "/api/assets/" + aid),
            ("DELETE", "/api/assets/" + aid),
            ("POST", "/api/assets/" + aid + "/ocr"),
        ]:
            assert other.request(method, path).status_code == 404
    assert user.request("DELETE", "/api/assets/" + aid).status_code == 200


def test_correction_keeps_parent(user):
    old = make_run(user).json()
    r = user.request(
        "POST",
        "/api/runs/" + old["id"] + "/correct",
        json={"inputs": {**SAMPLES["bill"], "declared": "130.00"}, "consent": True},
    )
    assert r.status_code == 201
    assert r.json()["id"] != old["id"]
    assert user.request("GET", "/api/runs/" + r.json()["id"]).status_code == 200
    assert (
        user.request("GET", "/api/runs/" + old["id"]).json()["output"]["facts"][
            "stated_total_bdt"
        ]
        == "120.30"
    )


def test_idempotent_retry(user):
    a = make_run(user, key="qa-retry")
    b = make_run(user, key="qa-retry")
    assert a.json()["id"] == b.json()["id"]


def test_workspace_boundary(user):
    with TestClient(app) as raw:
        other = Client(raw).register()
        wid = other.request("GET", "/api/workspaces").json()[0]["id"]
        r = user.request(
            "POST",
            "/api/tools/billdetect-ai/runs",
            json={"inputs": SAMPLES["bill"], "consent": True, "workspace_id": wid},
        )
        assert r.status_code == 404
        assert (
            user.request("GET", "/api/workspaces/" + wid + "/history").status_code
            == 404
        )


def test_consent_withdrawal(user):
    r = user.request(
        "POST",
        "/api/consent",
        json={
            "value": {
                "module": "carejourney-ai",
                "purpose": "training_contribution",
                "granted": True,
            }
        },
    )
    assert r.status_code == 201
    assert (
        user.request("DELETE", "/api/consent/" + r.json()["id"]).json()[
            "training_corpus_uses"
        ]
        == 0
    )


def test_account_deletion(user):
    r = make_run(user).json()
    assert (
        user.request(
            "DELETE", "/api/privacy/account", json={"value": {"password": "wrong"}}
        ).status_code
        == 401
    )
    d = user.request(
        "DELETE",
        "/api/privacy/account",
        json={"value": {"password": "Test-password-12345!"}},
    )
    assert d.status_code == 200
    with DB() as db:
        assert db.get(User, user.user["id"]) is None
        assert db.get(Run, r["id"]) is None
    assert user.request("GET", "/api/auth/me").status_code == 401


def test_audit_chain_no_private_payload(admin):
    admin.request(
        "POST",
        "/api/admin/cms",
        json={"value": {"page": "audit-test", "body": {"title_en": "TEST-CMS"}}},
    )
    r = admin.request("GET", "/api/admin/audit")
    assert r.status_code == 200
    assert r.json()
    latest = r.json()[0]
    assert len(latest["event_hash"]) == 64
    assert "password" not in json.dumps(r.json()).lower()


def test_role_change_revokes_sessions(admin):
    with TestClient(app) as raw:
        other = Client(raw).register()
        uid = other.user["id"]
        assert (
            admin.request(
                "PATCH",
                "/api/admin/users/" + uid,
                json={"value": {"role": "content_editor"}},
            ).status_code
            == 200
        )
        assert other.request("GET", "/api/auth/me").status_code == 401
