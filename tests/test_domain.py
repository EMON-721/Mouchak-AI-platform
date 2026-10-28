from datetime import date, timedelta
import pytest, json
from services.model_worker.domain import process, F, number, InputError
from services.model_worker.main import MODULES


@pytest.fixture(scope="module")
def user():
    from fastapi.testclient import TestClient
    from services.model_worker.main import app
    from conftest import Client

    with TestClient(app) as raw:
        yield Client(raw).register("Tool contract test account")


TODAY = str(date.today())
SAMPLES = {
    "observation": {
        "text": "রাজশাহীর পুকুরে সকালে মাছের খাবার পর্যবেক্ষণ।",
        "ph": "৭.২",
        "oxygen": "৫.৫",
    },
    "image_compare": {"text": "একই নদীতীরের দুই দিনের পর্যবেক্ষণ।"},
    "crop_diary": {
        "text": "নিজে দেখা ধানের ক্ষতি।",
        "area": "১০",
        "affected": "২",
        "unit": "decimal",
    },
    "roof": {"area": "100", "rate": "250", "rain": "20", "coefficient": ".8"},
    "audio": {},
    "contract": {
        "text": "ভাড়া মাসে ১০০০০ টাকা।\nজামানত ফেরতযোগ্য।",
        "comparison": "ভাড়া মাসে ১১০০০ টাকা।\nজামানত ফেরতযোগ্য।",
    },
    "bill": {
        "rows": [
            {"name": "এনার্জি", "amount": "১০০.১০"},
            {"name": "ফি", "amount": "২০.২০"},
        ],
        "declared": "১২০.৩০",
    },
    "care": {"text": "ডাক্তারের নির্দেশনা: পরের ভিজিটে রিপোর্ট সঙ্গে নেব।"},
    "video": {"text": "নিজের ক্রিকেট ভিডিও"},
    "inventory": {
        "rows": [{"name": "চাল", "quantity": "2", "minimum": "3", "expiry": TODAY}]
    },
    "prices": {
        "rows": [
            {
                "name": "চাল",
                "market": "নিজের দেখা দোকান",
                "price": "50",
                "quantity": "500",
                "unit": "g",
                "date": TODAY,
            },
            {
                "name": "চাল",
                "market": "নিজের দেখা বাজার",
                "price": "90",
                "quantity": "1",
                "unit": "kg",
                "date": TODAY,
            },
        ]
    },
    "home": {"text": "নিজের দেয়ালে স্যাঁতসেঁতে দাগ দেখেছি।"},
    "waste": {"text": "battery ব্যাটারি"},
    "worksite": {"text": "আমার দেখা স্থানে হাঁটার পথে বাধা আছে।"},
    "directory": {"text": "Dhaka"},
    "lab": {
        "unit": "mg/dL",
        "rows": [
            {"date": "2026-01-01", "value": "100"},
            {"date": "2026-02-01", "value": "110"},
        ],
    },
    "prescription": {
        "text": "নিজের নিশ্চিত করা প্রেসক্রিপশনের লেখা; কোনো নতুন ডোজ নয়।"
    },
    "vaccine": {"rows": [{"name": "নিজের কার্ডের টিকা", "date": "2026-01-01"}]},
    "maternal": {"text": "আগামী ভিজিটে নিজের রিপোর্ট নিয়ে যাব।"},
    "counts": {
        "rows": [
            {"date": "2026-01-01", "value": "10"},
            {"date": "2026-01-02", "value": "20"},
        ]
    },
    "rent": {
        "rent": "10000",
        "service": "1000",
        "utilities": "1500",
        "deposit": "20000",
    },
    "road": {
        "location": "নিজের আনুমানিক ওয়ার্ড",
        "text": "রাস্তার ক্ষয় নিয়ে নিজের পর্যবেক্ষণ।",
    },
    "route": {
        "origin": "A",
        "destination": "C",
        "rows": [
            {"from": "A", "to": "B", "cost": "3"},
            {"from": "B", "to": "C", "cost": "4"},
            {"from": "A", "to": "C", "cost": "10"},
        ],
    },
    "water": {
        "rows": [
            {"name": "pH", "value": "7.2", "unit": "pH", "lower": "6.5", "upper": "8.5"}
        ]
    },
    "farm": {"cost": "10000", "yield": "500", "price": "25"},
    "livestock": {
        "unit": "kg",
        "rows": [
            {"date": "2026-01-01", "value": "100"},
            {"date": "2026-02-01", "value": "110"},
        ],
    },
    "form": {"required": "ছবি\nআবেদন", "available": "ছবি"},
    "heat": {"temperature": "৩২", "humidity": "৭০"},
    "blood": {
        "group": "O+",
        "district": "নিজের দেওয়া জেলা",
        "date": str(date.today() + timedelta(days=1)),
    },
    "rag": {"text": "বাষ্পীভবন কী?"},
    "reading": {
        "passage_id": "AUTH-READ-01",
        "text": "রিমা সকালে তার ছোট বাগানে যায়।",
    },
    "land": {"value": "০.৪৫১৪", "unit": "acre", "comparison": "০.৪৫"},
    "wage": {
        "hours": "160",
        "rate": "100",
        "overtime": "10",
        "multiplier": "2",
        "paid": "17000",
    },
    "phraseboard": {"text": "আমার সাহায্য দরকার।"},
    "drain": {"location": "সাধারণ এলাকা", "text": "বৃষ্টির পর জলাবদ্ধতার পর্যবেক্ষণ।"},
    "fire": {"exits": "3", "blocked": "1", "text": "নিজের তৈরি মহড়ার নোট।"},
    "energy": {
        "rows": [{"name": "ফ্যান", "watts": "৭৫", "hours": "৮", "count": "২"}],
        "days": "৩০",
        "rate": "৮",
    },
    "scam": {
        "text": "জরুরি পুরস্কার! OTP 123456 এখনই পাঠান।",
        "url": "http://example.test",
    },
    "pharmacy": {"text": "নিজের ওষুধের বানান"},
    "skills": {"skills": "Python", "required": "Python\nSQL"},
    "food": {
        "text": "Ingredients: milk, wheat and sugar.",
        "allergens": "milk\npeanut",
    },
    "repair": {"repair": "1000", "replace": "5000", "text": "ওয়ারেন্টি যাচাই করব।"},
    "bulletin": {
        "text": "ব্যবহারকারীর দেওয়া বুলেটিনের লেখা।",
        "issued_at": "2026-10-27T10:00:00+06:00",
        "source_url": "https://example.test/bulletin",
    },
    "school": {"text": "ব্যস্ত মোড়ে অভিভাবকের দেখা বাধা।"},
    "cashbook": {
        "opening": "1000",
        "rows": [{"name": "নিজের বিক্রয়", "incoming": "500", "outgoing": "100"}],
        "counted": "1400",
    },
}
for a, b in [
    ("hospital_bill", "bill"),
    ("soil", "water"),
    ("service", "form"),
    ("travel", "route"),
    ("benefits", "form"),
]:
    SAMPLES[a] = SAMPLES[b]


@pytest.mark.parametrize("slug", list(MODULES))
def test_all_module_support_contracts(slug, user):
    m = MODULES[slug]
    p = SAMPLES[m["engine"]]
    asset_ids = []
    if m["engine"] == "audio":
        import wave, io, numpy as np

        out = io.BytesIO()
        with wave.open(out, "wb") as w:
            w.setnchannels(1)
            w.setsampwidth(2)
            w.setframerate(16000)
            w.writeframes(
                (np.sin(np.arange(16000) * 0.2) * 1000).astype("<i2").tobytes()
            )
        a = user.request(
            "POST",
            "/api/upload",
            data={"consent": "true"},
            files={"file": ("test.wav", out.getvalue(), "audio/wav")},
        )
        assert a.status_code == 201, a.text
        asset_ids = [a.json()["id"]]
    r = user.request(
        "POST",
        f"/api/tools/{slug}/runs",
        json={"inputs": p, "consent": True, "asset_ids": asset_ids},
    )
    if m["engine"] in ["video", "directory", "pharmacy"]:
        assert r.status_code == 422
        assert "Unavailable" in r.text
        return
    assert r.status_code == 201, r.text
    d = r.json()
    assert d["status"] == "support_completed"
    assert d["full_module_complete"] is False
    assert d["model_version"]
    assert d["references"]
    saved = user.request("GET", "/api/runs/" + d["id"])
    assert saved.status_code == 200
    assert saved.json()["output"]["facts"] == d["facts"]
    assert user.request("GET", "/api/runs/" + d["id"] + "/export").status_code == 200
    assert user.request("DELETE", "/api/runs/" + d["id"]).status_code == 200
    assert user.request("GET", "/api/runs/" + d["id"]).status_code == 404


@pytest.mark.parametrize("slug", list(MODULES))
def test_every_tool_requires_consent(slug, user):
    r = user.request(
        "POST", f"/api/tools/{slug}/runs", json={"inputs": {}, "consent": False}
    )
    assert r.status_code == 422


@pytest.mark.parametrize("slug", list(MODULES))
def test_every_tool_rejects_empty(slug, user):
    r = user.request(
        "POST", f"/api/tools/{slug}/runs", json={"inputs": {}, "consent": True}
    )
    assert r.status_code == 422, r.text


@pytest.mark.parametrize(
    "v", ["NaN", "Infinity", "-Infinity", "-1", "abc", True, "১.২.৩"]
)
def test_bad_numbers(v):
    with pytest.raises(InputError):
        number(v)


def test_exact_bengali_money():
    r = process("bill", SAMPLES["bill"])
    assert r["facts"]["line_total_bdt"] == "120.30"
    assert r["facts"]["difference_bdt"] == "0.00"


def test_energy_bengali_digits():
    r = process("energy", SAMPLES["energy"])
    assert r["facts"]["total_kwh"] == "36"
    assert r["facts"]["energy_only_cost_bdt"] == "288.00"


def test_land_no_bigha_guess():
    with pytest.raises(InputError):
        process("land", {"value": "2", "unit": "bigha"})
    assert (
        process("land", {"value": "০.৪৫১৪", "unit": "acre"})["facts"]["decimal"]
        == "45.1400"
    )


def test_route_no_path():
    with pytest.raises(InputError):
        process("route", {**SAMPLES["route"], "destination": "missing"})


def test_units_do_not_mix():
    with pytest.raises(InputError):
        process(
            "prices", {"rows": [{**SAMPLES["prices"]["rows"][0], "unit": "unknown"}]}
        )


def test_no_fabricated_diagnosis():
    r = process("water", SAMPLES["water"])
    assert "certificate" in " ".join(r["uncertainties"])
    assert r["facts"] == {"measurements": 1}


def test_redact_otp_without_fetching():
    r = process("scam", SAMPLES["scam"])
    assert "123456" not in json.dumps(r)
    assert r["facts"]["link_opened"] is False
