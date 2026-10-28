import time, json
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import select, func
from conftest import Client
from services.model_worker.main import app
from services.model_worker.store import (
    DB,
    Run,
    Config,
    Source,
    Consent,
    Audit,
    open_sealed,
)
from services.model_worker.collaboration import SupportGrant, ToolTransfer
from services.model_worker.operations import run_due, PublishSchedule


def example(c, slug="repairright-bd", **inputs):
    p = {"repair": "500", "replace": "2000", "text": "নিজের দেখা মেরামতের সমস্যা"}
    p.update(inputs)
    r = c.request(
        "POST", f"/api/tools/{slug}/runs", json={"consent": True, "inputs": p}
    )
    assert r.status_code == 201, r.text
    return r.json()


def grant(c, run, recipient, **changes):
    p = {
        "run_id": run["id"],
        "recipient_email": recipient.user["email"],
        "fact_keys": list(run["facts"])[:1],
        "reason": "Help me understand this selected result",
        "minutes": 15,
        "consent": True,
    }
    p.update(changes)
    return c.request("POST", "/api/support/grants", json=p)


@pytest.fixture
def helper():
    with TestClient(app) as raw:
        yield Client(raw).register().admin("support_agent")


def test_support_selected_snapshot_and_private_boundary(user, helper):
    r = example(user)
    g = grant(user, r, helper)
    assert g.status_code == 201, g.text
    gid = g.json()["id"]
    assert helper.request("GET", "/api/runs/" + r["id"]).status_code == 404
    view = helper.request("GET", "/api/admin/support/" + gid)
    assert view.status_code == 200, view.text
    assert list(view.json()["facts"]) == list(r["facts"])[:1]
    assert not {"inputs", "assets", "asset_ids", "email"} & view.json().keys()
    assert len(helper.request("GET", "/api/admin/support").json()) == 1
    with DB() as db:
        row = db.get(SupportGrant, gid)
        assert "Help me" not in row.encrypted
        assert db.scalar(
            select(Audit).where(
                Audit.action == "support_selected_facts_read", Audit.target == gid
            )
        )
    assert user.request("POST", f"/api/support/grants/{gid}/revoke").status_code == 200
    assert helper.request("GET", "/api/admin/support/" + gid).status_code == 404
    assert helper.request("GET", "/api/admin/support").json() == []


def test_support_owner_consent_expiry_and_wrong_recipient(user, helper):
    r = example(user)
    assert grant(user, r, helper, consent=False).status_code == 422
    assert grant(user, r, helper, fact_keys=["asset_ids"]).status_code == 422
    assert grant(user, r, helper, minutes=61).status_code == 422
    assert grant(user, r, helper, minutes=1.2).status_code == 422
    g = grant(user, r, helper).json()
    with TestClient(app) as raw:
        other = Client(raw).register().admin()
        assert other.request("GET", "/api/admin/support/" + g["id"]).status_code == 404
        assert (
            other.request(
                "POST", "/api/support/grants/" + g["id"] + "/revoke"
            ).status_code
            == 404
        )
        assert grant(other, r, helper).status_code == 404
    with DB.begin() as db:
        db.get(SupportGrant, g["id"]).expires_at = int(time.time()) - 1
    assert helper.request("GET", "/api/admin/support/" + g["id"]).status_code == 404


def test_support_requires_live_role_and_mfa(user, helper):
    from services.model_worker.store import User, Session

    r = example(user)
    g = grant(user, r, helper).json()
    with DB.begin() as db:
        db.get(User, helper.user["id"]).role = "user"
    assert helper.request("GET", "/api/admin/support/" + g["id"]).status_code == 403


def transfer_payload(user, r, **changes):
    w = user.request("GET", "/api/workspaces").json()[0]["id"]
    p = {
        "source_run_id": r["id"],
        "target_module": "scamsignal-bd",
        "workspace_id": w,
        "mapping": [{"source": "text", "target": "text"}],
        "consent": True,
    }
    p.update(changes)
    return p


def test_transfer_preview_consent_then_process_lineage(user):
    r = example(user)
    p = transfer_payload(user, r)
    preview = user.request(
        "POST", "/api/transfers/preview", json={**p, "consent": False}
    )
    assert preview.status_code == 200, preview.text
    assert preview.json()["inputs"] == {"text": "নিজের দেখা মেরামতের সমস্যা"}
    assert (
        user.request("POST", "/api/transfers", json={**p, "consent": False}).status_code
        == 422
    )
    t = user.request("POST", "/api/transfers", json=p)
    assert t.status_code == 201, t.text
    tid = t.json()["id"]
    with DB() as db:
        assert "নিজের" not in db.get(ToolTransfer, tid).encrypted
    # Destination is a draft, never automatically analysed. Edited text remains explicit user input.
    inp = {
        "text": "Edited by the owner",
        "area": "100",
        "roof_cost": "200",
        "temperature_before": "32",
        "temperature_after": "31",
    }
    from services.model_worker.domain import F

    target = "scamsignal-bd"
    # Use text -> text transfer to a second deterministic text tool for an executable destination.
    p["target_module"] = target
    t = user.request("POST", "/api/transfers", json=p)
    assert t.status_code == 201, t.text
    tid = t.json()["id"]
    run = user.request(
        "POST",
        f"/api/tools/{target}/runs",
        json={
            "consent": True,
            "transfer_id": tid,
            "workspace_id": p["workspace_id"],
            "inputs": {"text": "আপনার পাসওয়ার্ড কাউকে দেবেন না", "url": ""},
        },
    )
    assert run.status_code == 201, run.text
    with DB() as db:
        assert db.get(Run, run.json()["id"]).parent_id == r["id"]
    assert user.request("GET", "/api/transfers/" + tid).json()["state"] == "processed"
    assert (
        user.request(
            "POST",
            f"/api/tools/{target}/runs",
            json={
                "consent": True,
                "transfer_id": tid,
                "workspace_id": p["workspace_id"],
                "inputs": {"text": "another example", "url": ""},
            },
        ).status_code
        == 409
    )


def test_transfer_rejects_cross_owner_and_incompatible_fields(user):
    r = example(user)
    p = transfer_payload(user, r)
    assert (
        user.request(
            "POST",
            "/api/transfers",
            json={**p, "mapping": [{"source": "repair", "target": "text"}]},
        ).status_code
        == 422
    )
    assert (
        user.request(
            "POST",
            "/api/transfers",
            json={**p, "mapping": [{"source": "password", "target": "text"}]},
        ).status_code
        == 422
    )
    with TestClient(app) as raw:
        other = Client(raw).register()
        assert other.request("POST", "/api/transfers", json=p).status_code == 404
        p["workspace_id"] = other.request("GET", "/api/workspaces").json()[0]["id"]
        assert user.request("POST", "/api/transfers", json=p).status_code == 404


def test_collaboration_exports_and_source_delete_cascade(user, helper):
    r = example(user)
    g = grant(user, r, helper).json()
    t = user.request("POST", "/api/transfers", json=transfer_payload(user, r)).json()
    data = user.request("GET", "/api/privacy/export").json()["collaboration"]
    assert data["support_grants"][0]["id"] == g["id"]
    assert data["transfers"][0]["id"] == t["id"]
    assert user.request("DELETE", "/api/runs/" + r["id"]).status_code == 200
    with DB() as db:
        assert db.get(SupportGrant, g["id"]) is None
        assert db.get(ToolTransfer, t["id"]) is None


def draft(admin, page="test-publishing"):
    r = admin.request(
        "POST",
        "/api/admin/cms",
        json={
            "value": {
                "page": page,
                "body": {"title_bn": "নতুন লেখা", "title_en": "New content"},
            }
        },
    )
    assert r.status_code == 201, r.text
    return r.json()["id"]


def test_scheduler_publishes_once_and_cancellation(admin):
    v = draft(admin)
    due = int(time.time()) + 60
    s = admin.request(
        "POST", "/api/admin/publishing", json={"version_id": v, "due_at": due}
    )
    assert s.status_code == 201, s.text
    assert (
        admin.request(
            "POST", "/api/admin/publishing", json={"version_id": v, "due_at": due}
        ).status_code
        == 409
    )
    with DB.begin() as db:
        assert run_due(db, due - 1) == []
    with DB.begin() as db:
        assert run_due(db, due)[0]["state"] == "published"
    with DB.begin() as db:
        assert run_due(db, due + 1) == []
        assert (
            json.loads(db.get(Config, "cms:test-publishing").value)["title_en"]
            == "New content"
        )
    v = draft(admin, "cancel-test")
    s = admin.request(
        "POST", "/api/admin/publishing", json={"version_id": v, "due_at": due}
    ).json()
    assert (
        admin.request(
            "POST", "/api/admin/publishing/" + s["id"] + "/cancel"
        ).status_code
        == 200
    )
    with DB.begin() as db:
        assert run_due(db, due) == []


def test_scheduler_refuses_changed_page_or_revoked_author(admin):
    from services.model_worker.store import User

    v = draft(admin, "conflict-test")
    due = int(time.time()) + 60
    s = admin.request(
        "POST", "/api/admin/publishing", json={"version_id": v, "due_at": due}
    ).json()
    with DB.begin() as db:
        db.add(
            Config(key="cms:conflict-test", value='{"title_en":"newer manual version"}')
        )
    with DB.begin() as db:
        assert run_due(db, due)[0]["state"] == "conflict"
        assert "newer manual" in db.get(Config, "cms:conflict-test").value
    v = draft(admin, "revoked-author")
    admin.request(
        "POST", "/api/admin/publishing", json={"version_id": v, "due_at": due}
    )
    with DB.begin() as db:
        db.get(User, admin.user["id"]).role = "user"
    with DB.begin() as db:
        assert run_due(db, due)[0]["state"] == "author_unavailable"


def rights_payload():
    return {
        "decision": "approved_train_and_reuse",
        "asset_url": "https://example.test/owned-asset.csv",
        "terms_url": "https://example.test/terms",
        "license_uri": "https://creativecommons.org/licenses/by/4.0/",
        "scope": "Synthetic test permission, no actual dataset imported",
        "coverage": "Bangladesh test only",
        "source_date": "2026-01-01",
        "evidence": "Synthetic rights evidence used only in isolated automated test",
        "sensitivity": "sensitive",
    }


def test_sensitive_rights_two_distinct_reviewers_and_revocation(admin):
    with DB() as db:
        sid = db.scalar(select(Source).where(Source.module == "cliniccompass-bd")).id
    p = rights_payload()
    first = admin.request("POST", f"/api/admin/sources/{sid}/reviews", json=p)
    assert first.status_code == 201, first.text
    assert first.json()["state"] == "rights_review"
    assert (
        admin.request("POST", f"/api/admin/sources/{sid}/reviews", json=p).status_code
        == 409
    )
    with TestClient(app) as raw:
        second = Client(raw).register().admin("dataset_reviewer")
        approved = second.request("POST", f"/api/admin/sources/{sid}/reviews", json=p)
        assert approved.status_code == 201, approved.text
        assert approved.json()["state"] == "approved_train_and_reuse"
        assert approved.json()["data_imported"] is False
        revoked = admin.request(
            "POST",
            f"/api/admin/sources/{sid}/reviews",
            json={**p, "decision": "revoked"},
        )
        assert revoked.json()["state"] == "revoked"
        new = second.request("POST", f"/api/admin/sources/{sid}/reviews", json=p)
        assert new.json()["state"] == "rights_review"
        assert new.json()["independent_reviewers"] == 1


def test_feedback_triage_and_private_notifications(user, helper):
    f = user.request(
        "POST",
        "/api/feedback",
        json={"value": {"text": "Keyboard focus difficult on this page"}},
    ).json()
    rows = helper.request("GET", "/api/admin/feedback")
    assert rows.status_code == 200
    assert any(x["id"] == f["id"] for x in rows.json())
    assert user.request("GET", "/api/admin/feedback").status_code == 403
    assert (
        helper.request(
            "PATCH",
            "/api/admin/feedback/" + f["id"],
            json={"status": "triaged", "category": "accessibility"},
        ).json()["status"]
        == "triaged"
    )
    with TestClient(app) as raw:
        operator = Client(raw).register().admin()
        n = operator.request(
            "POST",
            "/api/admin/notifications",
            json={
                "user_id": user.user["id"],
                "body_bn": "আপনার মতামত দেখা হয়েছে",
                "body_en": "Your feedback was reviewed",
            },
        )
        assert n.status_code == 201, n.text
        dispatched = operator.request("GET", "/api/admin/notifications").json()
        assert any(row["id"] == n.json()["id"] for row in dispatched)
        assert all("body" not in row for row in dispatched)
    assert (
        helper.request(
            "PATCH", "/api/notifications/" + n.json()["id"], json={"read": True}
        ).status_code
        == 404
    )
    assert (
        user.request(
            "PATCH", "/api/notifications/" + n.json()["id"], json={"read": True}
        ).json()["read"]
        is True
    )
    exported = user.request("GET", "/api/privacy/export").json()
    assert any(row["id"] == n.json()["id"] for row in exported["notifications"])
    assert any(row["id"] == f["id"] for row in exported["feedback"])


def test_scheduler_bad_dates_and_user_permission(user):
    assert (
        user.request(
            "POST",
            "/api/admin/publishing",
            json={"version_id": "none", "due_at": int(time.time()) + 60},
        ).status_code
        == 403
    )
    with TestClient(app) as raw:
        a = Client(raw).register().admin()
        v = draft(a, "invalid-schedule")
        for due in [0, int(time.time()) - 10, int(time.time()) + 400 * 86400]:
            assert (
                a.request(
                    "POST",
                    "/api/admin/publishing",
                    json={"version_id": v, "due_at": due},
                ).status_code
                == 422
            )


def test_grant_without_fresh_mfa_and_consent_types(user, helper):
    from services.model_worker.store import Session

    r = example(user)
    assert grant(user, r, helper, consent="yes").status_code == 422
    assert grant(user, r, helper, reason=" " * 20).status_code == 422
    g = grant(user, r, helper).json()
    with DB.begin() as db:
        for s in db.scalars(
            select(Session).where(Session.user_id == helper.user["id"])
        ):
            s.mfa_until = 0
    assert helper.request("GET", "/api/admin/support/" + g["id"]).status_code == 403


def test_rights_rejects_credentials_future_date_and_unauthorized_user(user):
    with DB() as db:
        sid = db.scalar(select(Source)).id
    assert (
        user.request(
            "POST", f"/api/admin/sources/{sid}/reviews", json=rights_payload()
        ).status_code
        == 403
    )
    with TestClient(app) as raw:
        a = Client(raw).register().admin("dataset_reviewer")
        assert (
            a.request(
                "POST",
                f"/api/admin/sources/{sid}/reviews",
                json={
                    **rights_payload(),
                    "asset_url": "https://name:password@example.test/asset",
                },
            ).status_code
            == 422
        )
        assert (
            a.request(
                "POST",
                f"/api/admin/sources/{sid}/reviews",
                json={**rights_payload(), "source_date": "2999-01-01"},
            ).status_code
            == 422
        )


def test_transfer_draft_invisible_to_other_owner_and_wrong_target_rolls_back(user):
    r = example(user)
    p = transfer_payload(user, r)
    draft = user.request("POST", "/api/transfers", json=p).json()
    with TestClient(app) as raw:
        other = Client(raw).register()
        assert other.request("GET", "/api/transfers/" + draft["id"]).status_code == 404
    with DB() as db:
        before = db.scalar(
            select(func.count()).select_from(Run).where(Run.user_id == user.user["id"])
        )
    failed = user.request(
        "POST",
        "/api/tools/repairright-bd/runs",
        json={
            "consent": True,
            "inputs": {"repair": "10", "replace": "20", "text": "owned fixture"},
            "transfer_id": draft["id"],
        },
    )
    assert failed.status_code == 404
    with DB() as db:
        assert (
            db.scalar(
                select(func.count())
                .select_from(Run)
                .where(Run.user_id == user.user["id"])
            )
            == before
        )


@pytest.mark.parametrize("blocked_target", ["cliniccompass-bd", "oshudhkhoj-bd"])
def test_transfer_refuses_unavailable_target(user, blocked_target):
    r = example(user)
    p = transfer_payload(user, r, target_module=blocked_target)
    assert user.request("POST", "/api/transfers/preview", json=p).status_code == 503


def test_scheduler_process_publishes_durable_job_and_exits_cleanly(tmp_path):
    import os, subprocess, sqlite3

    env = {
        **os.environ,
        "MOUCHAK_STATE_DIR": str(tmp_path / "worker-state"),
        "MOUCHAK_ENV": "test",
        "SCHEDULER_POLL_SECONDS": "1",
    }
    seed = """
from services.model_worker.main import app
from services.model_worker.store import DB,migrate,User,CMSVersion
from services.model_worker.operations import PublishSchedule,fingerprint
migrate()
with DB.begin() as db:
 db.add(User(id='worker-author',email='worker@example.test',password='test-only fixture',name='Worker fixture',role='content_editor',verified=True,banned=False,language='bn',mfa_enabled=True));db.flush()
 db.add(CMSVersion(id='worker-version',page='worker-drill',body='{"title_en":"Published by real worker process"}',status='draft',author='worker-author'));db.flush()
 db.add(PublishSchedule(id='worker-schedule',version_id='worker-version',author='worker-author',due_at=0,base_hash=fingerprint(None),state='scheduled'))
"""
    subprocess.run(
        [os.sys.executable, "-c", seed], env=env, capture_output=True, check=True
    )
    worker = subprocess.Popen(
        [os.sys.executable, "-m", "services.model_worker.scheduler"],
        env=env,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
    )
    found = False
    try:
        until = time.monotonic() + 10
        while time.monotonic() < until:
            with sqlite3.connect(tmp_path / "worker-state/development.db") as db:
                row = db.execute(
                    "SELECT value FROM configuration WHERE key='cms:worker-drill'"
                ).fetchone()
            if row:
                assert (
                    json.loads(row[0])["title_en"] == "Published by real worker process"
                )
                found = True
                break
            time.sleep(0.1)
        assert found, "Worker did not publish the durable due schedule"
    finally:
        worker.terminate()
        out, err = worker.communicate(timeout=5)
    assert worker.returncode == 0, err
    assert '"scheduler_poll": "ok"' in out
