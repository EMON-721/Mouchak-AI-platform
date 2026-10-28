"""Synthetic owned fixtures test mechanics, never Bangladesh model accuracy."""
import io, json, time
import pytest
from PIL import Image, ImageDraw, ImageFont
from fastapi.testclient import TestClient
from sqlalchemy import select
from services.model_worker.main import app
from services.model_worker.store import DB, User, Workspace, open_sealed
from services.model_worker import bills
from conftest import Client


def workspace(c):
    return c.request("GET", "/api/workspaces").json()[0]["id"]


def sample(wid, index=0):
    # Test-only input assertions, not a production training corpus.
    return {"workspace_id": wid, "bill_type": "electricity",
            "month": f"{2022 + index // 12}-{index % 12 + 1:02}", "period_days": 30,
            "units": str(100 + index * 3), "consumption_bdt": str(1000 + index * 15),
            "fixed_bdt": "50", "tax_bdt": "75", "adjustment_bdt": "0",
            "stated_bdt": str(1125 + index * 15), "confirmed": True,
            "processing_consent": True, "allow_personal_model": True, "is_demo": False}


def seed(c, count=25, **overrides):
    wid = workspace(c)
    ids = []
    for index in range(count):
        r = c.request("POST", "/api/bills/history", json={**sample(wid, index), **overrides})
        assert r.status_code == 201, r.text
        ids.append(r.json()["id"])
    return wid, ids


def fit(c, wid):
    return c.request("POST", "/api/bills/model/train", json={"workspace_id": wid, "bill_type": "electricity", "consent": True})


def test_real_private_model_fits_persists_reloads_predicts_and_exports(user):
    wid, ids = seed(user)
    fitted = fit(user, wid)
    assert fitted.status_code == 200, fitted.text
    result = fitted.json()
    card = result["card"]
    assert card["rows"] == 25 and card["export_max_absolute_error"] < 1e-5
    assert card["shared_training"] is False and card["bangladesh_holdout_evaluated"] is False
    assert fit(user, wid).json()["reused"] is True
    with DB() as db:
        stored = db.get(bills.BillModel, result["model_id"])
        assert "onnx" not in stored.encrypted and "1000.00" not in stored.encrypted
        session, _ = bills.load_artifact(stored)
        assert session.get_providers() == ["CPUExecutionProvider"]
    baseline = user.request("POST", "/api/bills/predict", json=sample(wid, 12))
    extreme = user.request("POST", "/api/bills/predict", json={**sample(wid, 12), "units": "50000000", "consumption_bdt": "50000000", "stated_bdt": "50000125"})
    assert baseline.status_code == extreme.status_code == 201
    assert baseline.json()["facts"]["decision_score"] != extreme.json()["facts"]["decision_score"]
    assert extreme.json()["facts"]["unusual_against_your_baseline"] is True
    assert extreme.json()["details"]["confidence"] is None
    assert extreme.json()["full_module_complete"] is False
    assert user.request("GET", "/api/runs/" + extreme.json()["id"]).status_code == 200
    exported = user.request("GET", f"/api/bills/export?workspace_id={wid}&bill_type=electricity")
    assert len(exported.json()["bills"]) == 25 and "onnx" not in exported.text
    with TestClient(app) as raw:
        other = Client(raw).register().admin()
        assert other.request("GET", f"/api/bills/history?workspace_id={wid}&bill_type=electricity").status_code == 404
        assert other.request("DELETE", "/api/bills/history/" + ids[0]).status_code == 404
        assert other.request("GET", f"/api/bills/export?workspace_id={wid}&bill_type=electricity").status_code == 404


@pytest.mark.parametrize("overrides", [{"is_demo": True}, {"allow_personal_model": False}])
def test_demo_or_nonconsenting_records_cannot_train(user, overrides):
    wid, _ = seed(user, **overrides)
    assert fit(user, wid).status_code == 422
    assert user.request("POST", "/api/bills/predict", json=sample(wid)).status_code == 409


def test_minimum_confirmations_duplicates_and_bengali_amounts(user):
    wid = workspace(user)
    p = {**sample(wid), "units": "১০০", "consumption_bdt": "১,০০০", "fixed_bdt": "৫০", "tax_bdt": "৭৫", "stated_bdt": "১,১২৫"}
    assert user.request("POST", "/api/bills/history", json={**p, "confirmed": False}).status_code == 422
    assert user.request("POST", "/api/bills/history", json={**p, "processing_consent": False}).status_code == 422
    r = user.request("POST", "/api/bills/history", json=p)
    assert r.status_code == 201
    assert r.json()["computed_bdt"] == "1125.00" and r.json()["difference_bdt"] == "0.00"
    assert user.request("POST", "/api/bills/history", json=p).status_code == 409
    assert fit(user, wid).status_code == 422
    for invalid in [{"units": "NaN"}, {"stated_bdt": "Infinity"}, {"period_days": 0}, {"month": "2024-99"}, {"month": "2100-01"}, {"customer_number": "forbidden"}]:
        assert user.request("POST", "/api/bills/history", json={**sample(wid, 1), **invalid}).status_code == 422


@pytest.mark.parametrize("action", ["withdraw_row", "delete_row", "withdraw_training_grant"])
def test_revocation_erases_derived_artifact_and_requires_new_consent(user, action):
    wid, ids = seed(user)
    fitted = fit(user, wid).json()
    if action == "withdraw_row":
        r = user.request("PATCH", "/api/bills/history/" + ids[0], json={**sample(wid), "allow_personal_model": False})
    elif action == "delete_row":
        r = user.request("DELETE", "/api/bills/history/" + ids[0])
    else:
        consents = user.request("GET", "/api/consent").json()
        consent = next(c for c in consents if c["purpose"] == "private_bill_model_training")
        r = user.request("DELETE", "/api/consent/" + consent["id"])
    assert r.status_code == 200, r.text
    with DB() as db:
        assert db.get(bills.BillModel, fitted["model_id"]) is None
    assert user.request("POST", "/api/bills/predict", json=sample(wid)).status_code == 409
    assert fit(user, wid).status_code == 422


def test_artifact_corruption_fails_closed(user):
    wid, _ = seed(user)
    model = fit(user, wid).json()
    with DB.begin() as db:
        db.get(bills.BillModel, model["model_id"]).checksum = "0" * 64
    assert user.request("POST", "/api/bills/predict", json=sample(wid)).status_code == 503


def test_production_cannot_bypass_model_release_gate(user, monkeypatch):
    wid = workspace(user)
    monkeypatch.setattr(bills, "PRODUCTION", True)
    assert fit(user, wid).status_code == 503
    assert user.request("POST", "/api/bills/predict", json=sample(wid)).status_code == 503
    status = user.request("GET", f"/api/bills/model?workspace_id={wid}&bill_type=electricity").json()
    assert status["status"] == "production_blocked" and status["evaluation_available"] is False


def test_guest_expiry_cascades_model_and_history(client):
    s = client.request("POST", "/api/session").json()
    client.csrf = s["csrf"]
    wid, ids = seed(client)
    model = fit(client, wid).json()
    r = client.request("POST", "/api/session/clear", json={"confirm": True})
    assert r.status_code == 200
    with DB() as db:
        assert not db.get(bills.BillModel, model["model_id"])
        assert not db.get(bills.BillEntry, ids[0])


@pytest.mark.parametrize("total,energy", [(1125, 1000), (2250, 2000)])
def test_owned_bill_photo_real_ocr_layout_extraction_and_redaction(user, total, energy):
    image = Image.new("RGB", (1000, 500), "white")
    draw = ImageDraw.Draw(image)
    font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 38)
    for index, line in enumerate(["Customer account 12345678", f"Energy charge {energy}.00", "Fixed charge 50.00", "VAT 75.00", f"Total due {total}.00", "Units used 120"]):
        draw.text((30, 20 + index * 65), line, fill="black", font=font)
    out = io.BytesIO(); image.save(out, "PNG")
    asset = user.request("POST", "/api/upload", files={"file": ("owned-test-bill.png", out.getvalue(), "image/png")}, data={"consent": "true"}).json()
    r = user.request("POST", "/api/bills/extract/" + asset["id"])
    assert r.status_code == 200, r.text
    result = r.json()
    assert result["draft_fields"]["stated_bdt"] == f"{total}.00"
    assert result["draft_fields"]["consumption_bdt"] == f"{energy}.00"
    assert result["candidates"][0]["boxes"]
    assert result["confidence"] is None and result["human_review_required"] is True
    assert "12345678" not in r.text


def test_ambiguous_or_missing_evidence_does_not_invent_an_amount():
    words = []
    for index, text in enumerate(["Total", "100.00", "200.00"]):
        words.append({"text": text, "line": "1", "engine_word_confidence": 50,
                      "low_confidence_heuristic": True, "x": index * 30, "y": 0, "width": 25, "height": 10})
    result = bills.draft_fields({"pages": [{"page": 1, "words": words}], "model": "test_parser_fixture", "page_count": 1})
    assert result["draft_fields"]["stated_bdt"] is None
