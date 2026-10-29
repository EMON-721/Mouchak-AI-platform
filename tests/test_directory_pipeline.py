"""Owned synthetic records only: no real clinic, pharmacist or medicine stock."""
import json
import uuid
from datetime import datetime, timedelta, timezone

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import delete

from conftest import Client
from services.model_worker.main import app
from services.model_worker.operations import SourceReview
from services.model_worker.store import Config, DB, Job, Source
from services.model_worker import directories


@pytest.fixture
def directory_team(admin):
    sid = "DEMO-DIR-" + uuid.uuid4().hex
    with DB.begin() as db:
        db.add(Source(id=sid, module="cliniccompass-bd", metadata_json="{}", state="candidate"))
    with TestClient(app) as raw:
        reviewer = Client(raw).register("DEMO independent reviewer").admin("dataset_reviewer")
        yield admin, reviewer, sid
    with DB.begin() as db:
        for slug in directories.MODULES:
            db.execute(delete(Config).where(Config.key == directories.key(slug)))
        db.execute(delete(Config).where(Config.key == "source-review-round:" + sid))
        db.execute(delete(Job).where(Job.source_id == sid))
        db.execute(delete(SourceReview).where(SourceReview.source_id == sid))
        db.execute(delete(Source).where(Source.id == sid))
    directories.search_index.cache_clear()


def rights():
    return {"decision": "approved_train_and_reuse", "asset_url": "https://example.test/DEMO-directory.json",
            "terms_url": "https://example.test/DEMO-terms", "license_uri": "https://creativecommons.org/publicdomain/zero/1.0/",
            "scope": "DEMO synthetic nonpersonal test directory reuse permission only", "coverage": "Bangladesh DEMO only",
            "source_date": "2026-01-01", "evidence": "DEMO owned synthetic records; never a real directory or stock claim",
            "sensitivity": "public_nonpersonal"}


def approve(team):
    first, second, sid = team
    assert first.request("POST", f"/api/admin/sources/{sid}/reviews", json=rights()).json()["state"] == "rights_review"
    response = second.request("POST", f"/api/admin/sources/{sid}/reviews", json=rights())
    assert response.status_code == 201, response.text
    assert response.json()["state"] == "approved_train_and_reuse"


def record(**changes):
    value = {"id": "DEMO-FAC-1", "name_bn": "DEMO পরীক্ষার কেন্দ্র", "name_en": "DEMO test facility",
             "district_bn": "ঢাকা", "district_en": "Dhaka", "address_bn": "DEMO বাস্তব ঠিকানা নয়",
             "address_en": "DEMO no real address", "verified_at": (datetime.now(timezone.utc) - timedelta(minutes=1)).isoformat(),
             "services_bn": ["চোখ পরীক্ষা"], "services_en": ["eye examination"]}
    return {**value, **changes}


def stage(team, values=None, schema="facility_v1"):
    first, _, sid = team
    response = first.request("POST", "/api/admin/directories/dry-run", json={"source_id": sid, "schema_name": schema, "records": values or [record()]})
    assert response.status_code == 201, response.text
    assert response.json()["published"] is False
    return response.json()["id"]


def publish(team, jid, previous=None):
    response = team[1].request("POST", f"/api/admin/directories/{jid}/publish", json={"expected_revision": previous})
    assert response.status_code == 200, response.text
    return response.json()


def run(user, slug="cliniccompass-bd", **inputs):
    return user.request("POST", f"/api/tools/{slug}/runs", json={"inputs": {"text": "চোখ পরীক্ষা", **inputs}, "consent": True})


def test_real_directory_search_isolation_and_withdrawal(directory_team, user):
    approve(directory_team)
    jid = stage(directory_team)
    assert run(user).status_code == 422
    assert directory_team[0].request("POST", f"/api/admin/directories/{jid}/publish", json={}).status_code == 403
    publish(directory_team, jid)
    metadata = user.request("GET", "/api/modules/cliniccompass-bd")
    assert metadata.status_code == 200
    assert metadata.json()["release_status"] == "limited_support"
    assert any(f["key"] == "district" for f in metadata.json()["fields"])
    response = run(user)
    assert response.status_code == 201, response.text
    output = response.json()
    assert output["facts"]["records"][0]["id"] == "DEMO-FAC-1"
    assert "MiniLM" in output["model_version"]
    assert output["source_kind"] == "rights_reviewed_directory"
    assert output["references"][0]["independent_reviewers"] == 2
    assert run(user, district="Khulna").json()["facts"]["matching_records"] == 0
    with TestClient(app) as raw:
        stranger = Client(raw).register()
        assert stranger.request("GET", "/api/runs/" + output["id"]).status_code == 404
    assert directory_team[0].request("POST", f"/api/admin/datasets/import/{jid}/rollback").status_code == 409
    withdrawn = directory_team[1].request("POST", "/api/admin/directories/cliniccompass-bd/withdraw", json={"expected_revision": jid})
    assert withdrawn.status_code == 200
    assert run(user).status_code == 422
    # Re-publishing an unchanged reviewed revision is an explicit rollback.
    publish(directory_team, jid)
    assert run(user).status_code == 201


def test_directory_rights_cannot_be_forged_by_single_review(directory_team):
    first, _, sid = directory_team
    first.request("POST", f"/api/admin/sources/{sid}/reviews", json=rights())
    # Even a manually set source flag cannot substitute for the two asset reviews.
    with DB.begin() as db:
        db.get(Source, sid).state = "approved_train_and_reuse"
    response = first.request("POST", "/api/admin/directories/dry-run", json={"source_id": sid, "schema_name": "facility_v1", "records": [record()]})
    assert response.status_code == 422


def test_directory_revocation_and_stale_publication_fail_closed(directory_team, user):
    approve(directory_team)
    jid = stage(directory_team)
    publish(directory_team, jid)
    first, _, sid = directory_team
    revoked = first.request("POST", f"/api/admin/sources/{sid}/reviews", json={**rights(), "decision": "revoked"})
    assert revoked.status_code == 201
    assert user.request("GET", "/api/modules/cliniccompass-bd").json()["release_status"] == "blocked"
    assert run(user).status_code == 422
    assert first.request("POST", "/api/admin/directories/dry-run", json={"source_id": sid, "schema_name": "facility_v1", "records": [record()]}).status_code == 422


def test_directory_concurrent_revision_conflict_and_rollback(directory_team, user):
    approve(directory_team)
    one = stage(directory_team)
    two = stage(directory_team, [record(id="DEMO-FAC-2")])
    publish(directory_team, one)
    assert directory_team[1].request("POST", f"/api/admin/directories/{two}/publish", json={}).status_code == 409
    publish(directory_team, two, one)
    assert run(user).json()["facts"]["records"][0]["id"] == "DEMO-FAC-2"
    publish(directory_team, one, two)
    assert run(user).json()["facts"]["records"][0]["id"] == "DEMO-FAC-1"


@pytest.mark.parametrize("changes", [{"latitude": 91}, {"latitude": "NaN", "longitude": 90},
    {"verified_at": "2026-01-01T00:00:00"}, {"verified_at": "2999-01-01T00:00:00+00:00"},
    {"verified_at": "2020-01-01T00:00:00+00:00"}, {"patient_name": "Prohibited identifier"}])
def test_directory_rejects_stale_invalid_and_private_schema(directory_team, changes):
    approve(directory_team)
    response = directory_team[0].request("POST", "/api/admin/directories/dry-run", json={"source_id": directory_team[2], "schema_name": "facility_v1", "records": [record(**changes)]})
    assert response.status_code == 422
    assert "Prohibited identifier" not in response.text


def test_directory_rechecks_age_on_every_query(directory_team, user):
    approve(directory_team)
    jid = stage(directory_team)
    publish(directory_team, jid)
    with DB.begin() as db:
        conf = db.get(Config, directories.key("cliniccompass-bd"))
        value = json.loads(conf.value)
        value["records"][0]["verified_at"] = "2020-01-01T00:00:00+00:00"
        conf.value = json.dumps(value)
    assert run(user).status_code == 422


def test_pharmacy_requires_literal_product_and_fresh_records(directory_team, user):
    with DB.begin() as db:
        db.get(Source, directory_team[2]).module = "oshudhkhoj-bd"
    approve(directory_team)
    value = record(id="DEMO-PHARM-1")
    del value["services_bn"], value["services_en"]
    value.update(product_name="DEMO-product-ALPHA", strength="DEMO-only", formulation="DEMO-only", reported_availability="not_confirmed")
    jid = stage(directory_team, [value], "pharmacy_v1")
    publish(directory_team, jid)
    output = run(user, "oshudhkhoj-bd", text="DEMO-product-ALPHA").json()
    assert output["facts"]["records"][0]["reported_availability"] == "not_confirmed"
    assert run(user, "oshudhkhoj-bd", text="DEMO-product-BETA").json()["facts"]["matching_records"] == 0
    stale = {**value, "verified_at": (datetime.now(timezone.utc) - timedelta(days=2)).isoformat()}
    assert directory_team[0].request("POST", "/api/admin/directories/dry-run", json={"source_id": directory_team[2], "schema_name": "pharmacy_v1", "records": [stale]}).status_code == 422


def test_directory_operator_permissions_and_csrf(user):
    assert user.request("GET", "/api/admin/directories").status_code == 403
    assert user.request("POST", "/api/admin/directories/dry-run", json={}).status_code == 403
    assert user.client.post("/api/admin/directories/cliniccompass-bd/withdraw", json={}).status_code == 403
