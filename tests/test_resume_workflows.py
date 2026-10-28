from datetime import datetime, timedelta
from zoneinfo import ZoneInfo
import json, pytest
from fastapi.testclient import TestClient
from services.model_worker.main import app
from services.model_worker.legacy_workflows import (
    READING,
    reading_reflection,
    basket_compare,
)
from services.model_worker.domain import InputError
from services.model_worker.store import DB, open_sealed
from services.model_worker.retail import StockItem, StockMovement
from conftest import Client


def wid(c):
    return c.request("GET", "/api/workspaces").json()[0]["id"]


def item(c, w=None, **kw):
    w = w or wid(c)
    p = {
        "name": "নিজের চাল",
        "sku": "MY-RICE",
        "quantity": 10,
        "minimum": 3,
        "unit_cost": "১০.১৫",
        "unit": "packet",
        "consent": True,
    }
    p.update(kw)
    r = c.request("POST", f"/api/retail/{w}/items", json=p)
    assert r.status_code == 201, r.text
    return r.json()


def move(c, w, i, **kw):
    p = {
        "type": "sale",
        "quantity": 2,
        "expected_revision": i["revision"],
        "idempotency_key": "movement-unique-001",
        "consent": True,
    }
    p.update(kw)
    return c.request("POST", f'/api/retail/{w}/items/{i["id"]}/movements', json=p)


def test_reading_source_attribution_and_no_answer_leak(client):
    response = client.request("GET", "/api/reading/passages")
    assert response.status_code == 200
    assert len(response.json()) == 12
    assert all(
        "answer" not in p and p["license"] == "CC-BY-4.0" for p in response.json()
    )


@pytest.mark.parametrize("passage", READING, ids=lambda p: p["id"])
def test_original_reading_reflection(passage):
    r = reading_reflection(
        {
            "passage_id": passage["id"],
            "difficult_indices": [0, 0],
            "answer": passage["answer"],
        }
    )
    assert r["facts"]["comprehension"] == "matched"
    assert r["facts"]["reviewed_words"] == len(passage["text"].split()) - 1
    assert r["references"][0]["publisher"] == passage["publisher"]
    assert r["full_module_complete"] is False


@pytest.mark.parametrize("positions", [[999], [-1], [True], ["0"]])
def test_reading_invalid_selection(positions):
    with pytest.raises(InputError):
        reading_reflection(
            {"passage_id": READING[0]["id"], "difficult_indices": positions}
        )


def test_reading_private_saved_result(user):
    p = READING[0]
    r = user.request(
        "POST",
        "/api/tools/banglaread-coach/runs",
        json={
            "consent": True,
            "inputs": {
                "passage_id": p["id"],
                "difficult_indices": [0],
                "answer": p["answer"],
            },
        },
    )
    assert r.status_code == 201, r.text
    assert r.json()["references"][0]["license"] == "CC-BY-4.0"
    assert user.request("GET", "/api/runs/" + r.json()["id"]).status_code == 200


def test_exact_freshness_semantic_basket():
    now = datetime(2026, 10, 27, 8, tzinfo=ZoneInfo("Asia/Dhaka"))
    base = {
        "product": "rice",
        "quantity": "500",
        "unit": "g",
        "price_type": "retail",
        "grade": "standard",
        "origin": "local",
        "price": "৪৫.১০",
        "vendor": "নিজের দোকান",
        "market": "নিজের বাজার",
        "date": "2026-10-27",
    }
    p = {
        "freshness_days": 7,
        "basket": [
            {
                "product": "চাল",
                "quantity": "২",
                "unit": "kg",
                "price_type": "retail",
                "grade": "standard",
                "origin": "local",
            }
        ],
        "offers": [
            base,
            {**base, "price": "1", "price_type": "wholesale"},
            {**base, "price": "1", "grade": "other"},
            {**base, "price": "1", "date": "2026-09-01"},
            {**base, "price": "1", "date": "2026-10-28"},
        ],
    }
    r = basket_compare(p, now)
    assert r["facts"]["known_lines_subtotal_bdt"] == "180.40"
    assert len(r["details"]["lines"][0]["comparable_offers"]) == 1
    assert r["facts"]["excluded_observations"] == 2


def test_missing_price_stays_missing():
    r = basket_compare(
        {"basket": [{"product": "ডিম", "quantity": "1", "unit": "dozen"}], "offers": []}
    )
    assert r["facts"]["fully_covered"] is False
    assert r["details"]["lines"][0]["lowest_observed_cost_bdt"] is None


def test_stock_sale_purchase_return_and_paisa(user):
    w = wid(user)
    i = item(user, w)
    assert i["unit_cost_paisa"] == 1015
    r = move(user, w, i)
    assert r.status_code == 201, r.text
    i = r.json()["item"]
    assert i["quantity"] == 8
    assert r.json()["event"]["before"] == 10
    r = move(
        user, w, i, type="purchase", quantity=5, idempotency_key="movement-unique-002"
    )
    assert r.status_code == 201
    i = r.json()["item"]
    assert i["quantity"] == 13
    r = move(
        user, w, i, type="return", quantity=1, idempotency_key="movement-unique-003"
    )
    assert r.status_code == 201
    assert r.json()["item"]["quantity"] == 14
    h = user.request("GET", f'/api/retail/{w}/items/{i["id"]}/history').json()
    assert len(h["events"]) == 3
    assert h["velocity"]["status"] == "insufficient"
    assert h["velocity"]["ml_forecast"] is False


def test_stock_negative_stale_revision_and_retry(user):
    w = wid(user)
    i = item(user, w)
    assert move(user, w, i, quantity=11).status_code == 422
    first = move(user, w, i)
    assert first.status_code == 201
    retry = move(user, w, i)
    assert retry.status_code == 201
    assert retry.json()["replayed"] is True
    assert retry.json()["item"]["quantity"] == 8
    assert move(user, w, i, quantity=3).status_code == 409
    assert move(user, w, i, idempotency_key="movement-unique-004").status_code == 409
    with DB() as db:
        assert open_sealed(db.get(StockItem, i["id"]).encrypted)["name"] == "নিজের চাল"
        assert "নিজের চাল" not in db.get(StockItem, i["id"]).encrypted


def test_stock_owner_isolation_even_admin(user):
    w = wid(user)
    i = item(user, w)
    with TestClient(app) as raw:
        other = Client(raw).register().admin()
        assert other.request("GET", f"/api/retail/{w}/items").status_code == 404
        assert (
            other.request("GET", f'/api/retail/{w}/items/{i["id"]}/history').status_code
            == 404
        )
        assert move(other, w, i).status_code == 404


def test_stock_export_and_account_deletion(user):
    w = wid(user)
    i = item(user, w)
    r = move(user, w, i)
    assert r.status_code == 201
    data = user.request("GET", "/api/privacy/export").json()
    assert data["retail"]["items"][0]["sku"] == "MY-RICE"
    assert data["retail"]["movements"][0]["after"] == 8
    assert (
        user.request(
            "DELETE",
            "/api/privacy/account",
            json={"value": {"password": "Test-password-12345!"}},
        ).status_code
        == 200
    )
    with DB() as db:
        assert db.get(StockItem, i["id"]) is None
        assert db.get(StockMovement, r.json()["id"]) is None


def test_stock_consent_and_fractional_rejection(user):
    w = wid(user)
    payload = {"name": "a", "sku": "a", "quantity": 1, "minimum": 0, "consent": False}
    assert (
        user.request("POST", f"/api/retail/{w}/items", json=payload).status_code == 422
    )
    assert (
        user.request(
            "POST",
            f"/api/retail/{w}/items",
            json={**payload, "consent": True, "quantity": 1.5},
        ).status_code
        == 422
    )


@pytest.mark.parametrize("hour,covered", [(0, True), (8, False)])
def test_price_freshness_exact_dhaka_boundary(hour, covered):
    now = datetime(2026, 10, 27, hour, tzinfo=ZoneInfo("Asia/Dhaka"))
    offer = {
        "product": "rice",
        "quantity": "1",
        "unit": "kg",
        "price": "50",
        "vendor": "own",
        "market": "own",
        "date": "2026-10-20",
    }
    r = basket_compare(
        {
            "freshness_days": 7,
            "basket": [{"product": "rice", "quantity": 1, "unit": "kg"}],
            "offers": [offer],
        },
        now,
    )
    assert r["facts"]["fully_covered"] is covered


def test_stock_bad_and_future_dates(user):
    w = wid(user)
    i = item(user, w)
    assert move(user, w, i, date="2026-02-30").status_code == 422
    assert move(user, w, i, date="2999-01-01").status_code == 422


def test_stock_today_counts_and_velocity_threshold(user):
    today = datetime.now(ZoneInfo("Asia/Dhaka")).date()
    w = wid(user)
    i = item(user, w, quantity=100)
    for n, ago in enumerate([2, 2, 1, 0, 0]):
        r = move(
            user,
            w,
            i,
            quantity=1,
            date=str(today - timedelta(days=ago)),
            idempotency_key=f"velocity-test-{n}",
        )
        assert r.status_code == 201, r.text
        i = r.json()["item"]
    h = user.request("GET", f'/api/retail/{w}/items/{i["id"]}/history').json()
    assert h["velocity"]["status"] == "descriptive_rule"
    assert h["velocity"]["records"] == 5
    assert h["velocity"]["days"] == 3
    assert h["velocity"]["ml_forecast"] is False


@pytest.fixture(scope="module")
def legacy_golden():
    import subprocess
    from pathlib import Path

    return json.loads(
        subprocess.check_output(
            ["node", "scripts/legacy-golden.mjs"],
            cwd=Path(__file__).resolve().parents[1],
            text=True,
        )
    )


def test_original_js_reading_parity(legacy_golden):
    for case in legacy_golden["reading"]:
        got = reading_reflection(case["input"])["facts"]
        expected = case["expected"]
        assert (
            got["total_words"],
            got["reviewed_words"],
            got["self_marked_difficult_words"],
            got["comprehension"],
        ) == (
            expected["total"],
            expected["reviewed"],
            expected["difficult"],
            expected["comprehension"],
        )


def test_original_js_basket_parity(legacy_golden):
    from decimal import Decimal

    for case in legacy_golden["baskets"]:
        p = case["input"]
        for row in p["basket"] + p["offers"]:
            row["price_type"] = row.pop("priceType")
        got = basket_compare(p, datetime.fromisoformat(case["now"]))["details"][
            "lines"
        ][0]
        expected = case["expected"][0]
        assert len(got["comparable_offers"]) == len(expected["offers"])
        assert (
            None
            if got["lowest_observed_cost_bdt"] is None
            else Decimal(got["lowest_observed_cost_bdt"])
        ) == (None if expected["cost"] is None else Decimal(str(expected["cost"])))


def test_original_js_stock_parity(user, legacy_golden):
    w = wid(user)
    i = item(user, w)
    for n, case in enumerate(legacy_golden["movements"]):
        r = move(
            user,
            w,
            i,
            type=case["type"],
            quantity=case["quantity"],
            idempotency_key=f"original-source-{n}",
        )
        assert r.status_code == 201, r.text
        i = r.json()["item"]
        assert (i["quantity"], i["revision"]) == (
            case["expected"]["stock"],
            case["expected"]["revision"],
        )


def test_preserved_legacy_source_integrity():
    from pathlib import Path
    import hashlib

    root = Path(__file__).resolve().parents[1]
    for row in json.loads(
        (root / "docs/audit/legacy-snapshot-manifest.json").read_text()
    ):
        assert (
            hashlib.sha256((root / row["file"]).read_bytes()).hexdigest()
            == row["sha256"]
        )


def test_operational_cli_registers_additive_stock_tables(tmp_path):
    import subprocess, os, sqlite3

    env = {**os.environ, "MOUCHAK_STATE_DIR": str(tmp_path / "migration-state")}
    subprocess.run(
        [os.sys.executable, "-m", "services.model_worker.manage", "migrate"],
        env=env,
        check=True,
        capture_output=True,
    )
    with sqlite3.connect(tmp_path / "migration-state/development.db") as db:
        names = {
            r[0]
            for r in db.execute("SELECT name FROM sqlite_master WHERE type='table'")
        }
    assert {"stock_items", "stock_movements", "users", "tool_runs"} <= names


def test_stock_consent_persisted_once_on_retry(user):
    from services.model_worker.store import Consent
    from sqlalchemy import select, func

    w = wid(user)
    i = item(user, w)

    def count():
        with DB() as db:
            return db.scalar(
                select(func.count())
                .select_from(Consent)
                .where(
                    Consent.user_id == user.user["id"], Consent.module == "dokanlens-ai"
                )
            )

    assert count() == 1
    assert move(user, w, i).status_code == 201
    assert count() == 2
    assert move(user, w, i).json()["replayed"] is True
    assert count() == 2
