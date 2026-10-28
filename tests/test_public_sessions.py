import io, time
import pytest
from fastapi.testclient import TestClient
from PIL import Image
from sqlalchemy import select, func
from services.model_worker.main import app, MODULES, RATE
from services.model_worker.store import DB, User, Session, Run, Asset, Workspace, Config
from services.model_worker.anonymous import purge_expired
from test_domain import SAMPLES


@pytest.fixture
def visitor():
    with TestClient(app) as c:
        r = c.post("/api/session")
        assert r.status_code == 200, r.text
        c.headers["x-csrf-token"] = r.json()["csrf"]
        yield c, r.json()


def test_visitor_needs_no_identity_and_idempotent_bootstrap(visitor):
    c, s = visitor
    assert s["mode"] == "anonymous"
    assert s["requires_account"] is False
    assert s["profile_collected"] is False
    assert not {"email", "name", "password", "user", "profile"} & s.keys()
    cookie = c.cookies.get("mouchak_session")
    assert cookie and len(cookie) > 40
    assert (
        "HttpOnly" in c.post("/api/session").headers.get("set-cookie", "")
        or c.cookies.get("mouchak_session") == cookie
    )
    r = c.post(
        "/api/session", json={"visitor_id": "other-owner", "role": "super_admin"}
    ).json()
    assert r["visitor_id"] == s["visitor_id"]
    assert r["role"] == "guest"
    with DB() as db:
        u = db.get(User, s["visitor_id"])
        assert u.name == ""
        assert u.email.endswith("@anonymous.invalid")
        assert u.password == "!anonymous-no-password"
        assert (
            len(list(db.scalars(select(Session).where(Session.user_id == u.id)))) == 1
        )
        assert (
            db.scalar(select(Session).where(Session.user_id == u.id)).device
            == "anonymous browser"
        )


def test_registration_profiles_and_privileged_access_closed(visitor):
    c, s = visitor
    assert (
        c.post(
            "/api/auth/register",
            json={
                "email": "visitor@example.test",
                "password": "Never-created-12345!",
                "name": "Not collected",
            },
        ).status_code
        == 410
    )
    assert (
        c.patch("/api/profile", json={"value": {"name": "Not collected"}}).status_code
        == 410
    )
    assert c.get("/api/auth/me").status_code == 401
    assert c.get("/api/admin/overview").status_code == 403
    assert c.post("/api/auth/mfa/enroll").status_code == 403
    assert (
        c.post(
            "/api/auth/login",
            json={
                "email": s["visitor_id"] + "@anonymous.invalid",
                "password": "!anonymous-no-password",
            },
        ).status_code
        == 401
    )
    assert (
        c.post(
            "/api/auth/login",
            json={
                "email": "nonexistent@example.test",
                "password": "Test-only-1234567!",
            },
        ).status_code
        == 401
    )


def make_run(c, slug="billdetect-ai"):
    assets = []
    if MODULES[slug]["engine"] == "audio":
        import wave, math, struct

        sound = io.BytesIO()
        with wave.open(sound, "wb") as out:
            out.setnchannels(1)
            out.setsampwidth(2)
            out.setframerate(16000)
            out.writeframes(
                b"".join(
                    struct.pack(
                        "<h", int(5000 * math.sin(2 * math.pi * 440 * i / 16000))
                    )
                    for i in range(16000)
                )
            )
        uploaded = c.post(
            "/api/upload",
            files={"file": ("synthetic-tone.wav", sound.getvalue(), "audio/wav")},
            data={"consent": "true"},
        )
        assert uploaded.status_code == 201, uploaded.text
        assets = [uploaded.json()["id"]]
    return c.post(
        "/api/tools/" + slug + "/runs",
        json={
            "consent": True,
            "inputs": SAMPLES[MODULES[slug]["engine"]],
            "asset_ids": assets,
        },
    )


@pytest.mark.parametrize("slug", list(MODULES))
def test_all_public_tool_routes_without_registration(visitor, slug):
    c, s = visitor
    r = make_run(c, slug)
    assert r.status_code == (
        422 if MODULES[slug]["release_status"] == "blocked" else 201
    ), (slug, r.text)
    if r.status_code == 201:
        assert c.get("/api/runs/" + r.json()["id"]).status_code == 200
        assert r.json()["full_module_complete"] is False


def test_anonymous_results_owner_isolation_exports_and_expiry(visitor):
    c, s = visitor
    r = make_run(c)
    assert r.status_code == 201, r.text
    rid = r.json()["id"]
    with TestClient(app) as other:
        new = other.post("/api/session").json()
        other.headers["x-csrf-token"] = new["csrf"]
        for method, path in [
            ("GET", "/api/runs/" + rid),
            ("DELETE", "/api/runs/" + rid),
            ("GET", "/api/runs/" + rid + "/export"),
        ]:
            assert other.request(method, path).status_code == 404
    export = c.get("/api/privacy/export").json()
    assert export["scope"]["mode"] == "anonymous"
    assert "profile" not in export
    assert export["runs"][0]["id"] == rid
    with DB.begin() as db:
        for row in db.scalars(
            select(Session).where(Session.user_id == s["visitor_id"])
        ):
            row.expires = int(time.time()) - 1
    assert c.get("/api/runs/" + rid).status_code == 401
    replacement = c.post("/api/session").json()
    assert replacement["visitor_id"] != s["visitor_id"]
    c.headers["x-csrf-token"] = replacement["csrf"]
    assert c.get("/api/runs/" + rid).status_code == 404


def test_visitor_upload_and_explicit_clear_only_own_scope(visitor):
    c, s = visitor
    img = io.BytesIO()
    Image.new("RGB", (200, 100), "white").save(img, format="PNG")
    upload = c.post(
        "/api/upload",
        files={"file": ("owned-test.png", img.getvalue(), "image/png")},
        data={"consent": "true"},
    )
    assert upload.status_code == 201, upload.text
    rid = make_run(c).json()["id"]
    aid = upload.json()["id"]
    with TestClient(app) as other:
        os = other.post("/api/session").json()
        other.headers["x-csrf-token"] = os["csrf"]
        other_run = make_run(other).json()["id"]
        assert c.post("/api/session/clear", json={"confirm": False}).status_code == 422
        assert (
            c.post(
                "/api/session/clear",
                json={"confirm": True, "visitor_id": os["visitor_id"]},
            ).status_code
            == 422
        )
        assert (
            c.post(
                "/api/session/clear",
                json={"confirm": True},
                headers={"x-csrf-token": "wrong"},
            ).status_code
            == 403
        )
        assert c.post("/api/session/clear", json={"confirm": True}).status_code == 200
        assert c.get("/api/runs/" + rid).status_code == 401
        assert other.get("/api/runs/" + other_run).status_code == 200
    with DB() as db:
        assert db.get(User, s["visitor_id"]) is None
        assert db.get(Asset, aid) is None
        assert db.get(Run, rid) is None


def test_cleanup_preserves_active_visitors_and_historical_accounts(visitor, user):
    c, s = visitor
    rid = make_run(c).json()["id"]
    old = user.user["id"]
    with DB.begin() as db:
        for row in db.scalars(
            select(Session).where(Session.user_id == s["visitor_id"])
        ):
            row.expires = int(time.time()) - 1
    purge_expired()
    with DB() as db:
        assert db.get(User, s["visitor_id"]) is None
        assert db.get(Run, rid) is None
        assert db.get(User, old) is not None
    with TestClient(app) as active:
        fresh = active.post("/api/session").json()
        purge_expired()
        with DB() as db:
            assert db.get(User, fresh["visitor_id"]) is not None


def test_operator_login_stays_private_and_session_clear_denied(admin):
    email = admin.user["email"]
    r = admin.request(
        "POST",
        "/api/auth/login",
        json={"email": email, "password": "Test-password-12345!"},
    )
    assert r.status_code == 200, r.text
    admin.csrf = r.json()["csrf"]
    assert (
        admin.request("POST", "/api/session/clear", json={"confirm": True}).status_code
        == 403
    )
    assert (
        admin.request("GET", "/api/admin/overview").status_code == 403
    )  # Fresh operator session must verify MFA again.


def test_visitor_support_cannot_outlive_browser_scope(visitor, admin):
    from services.model_worker.collaboration import SupportGrant

    c, s = visitor
    run = make_run(c).json()
    with DB.begin() as db:
        scope = db.scalar(select(Session).where(Session.user_id == s["visitor_id"]))
        scope.expires = int(time.time()) + 180
        expiry = scope.expires
    granted = c.post(
        "/api/support/grants",
        json={
            "run_id": run["id"],
            "recipient_email": admin.user["email"],
            "fact_keys": list(run["facts"])[:1],
            "reason": "Explain my selected bill total",
            "minutes": 60,
            "consent": True,
        },
    )
    assert granted.status_code == 201, granted.text
    gid = granted.json()["id"]
    assert granted.json()["expires_at"] == expiry
    assert admin.request("GET", "/api/admin/support/" + gid).status_code == 200
    with DB.begin() as db:
        db.scalar(select(Session).where(Session.user_id == s["visitor_id"])).expires = (
            int(time.time()) - 1
        )
        # Even a previously issued, still-future snapshot is inaccessible once
        # its anonymous owner has no live browser scope, before purge runs.
        db.get(SupportGrant, gid).expires_at = int(time.time()) + 60
    assert admin.request("GET", "/api/admin/support/" + gid).status_code == 404


def test_real_retention_worker_purges_expired_scope_and_preserves_legacy(tmp_path):
    import os, subprocess, sqlite3

    state = tmp_path / "retention-state"
    env = {**os.environ, "MOUCHAK_STATE_DIR": str(state), "MOUCHAK_ENV": "test"}
    seed = """
from services.model_worker.main import app
from services.model_worker.store import DB,migrate,User,Session
migrate()
with DB.begin() as db:
 for identity,role in [('expired','guest'),('historical','user'),('active','guest')]:
  db.add(User(id=identity,email=identity+'@example.test',password='fixture only',name='',role=role,verified=False,language='bn'))
 db.flush()
 db.add(Session(id='expired-token',user_id='expired',csrf='fixture',expires=1,last_seen=1,device='anonymous browser'))
 db.add(Session(id='active-token',user_id='active',csrf='fixture',expires=4102444800,last_seen=1,device='anonymous browser'))
"""
    subprocess.run(
        [os.sys.executable, "-c", seed], env=env, capture_output=True, check=True
    )
    worker = subprocess.Popen(
        [os.sys.executable, "-m", "services.model_worker.visitor_retention"],
        env=env,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
    )
    try:
        found = False
        until = time.monotonic() + 10
        while time.monotonic() < until:
            with sqlite3.connect(state / "development.db") as db:
                ids = {r[0] for r in db.execute("SELECT id FROM users")}
            if "expired" not in ids:
                assert ids == {"historical", "active"}
                found = True
                break
            time.sleep(0.1)
        assert found, "Retention worker did not remove expired visitor scope"
    finally:
        worker.terminate()
        out, err = worker.communicate(timeout=5)
    assert worker.returncode == 0, err
    assert '"expired_visitor_scopes_removed": 1' in out
    manual = subprocess.run(
        [os.sys.executable, "-m", "services.model_worker.manage", "purge-visitors"],
        env=env,
        capture_output=True,
        text=True,
        check=True,
    )
    assert '"expired_visitor_scopes_removed": 0' in manual.stdout


def test_visitor_exports_real_pdf_and_json_without_profile(visitor):
    import fitz

    c, _ = visitor
    r = make_run(c).json()
    exported = c.get("/api/runs/" + r["id"] + "/export?format=pdf")
    assert exported.status_code == 200
    assert exported.headers["content-type"] == "application/pdf"
    document = fitz.open(stream=exported.content, filetype="pdf")
    assert document.page_count >= 1
    assert "mouchak-" in exported.headers["content-disposition"]
    data = c.get("/api/runs/" + r["id"] + "/export?format=json").json()
    assert data["output"]["facts"] == r["facts"]
