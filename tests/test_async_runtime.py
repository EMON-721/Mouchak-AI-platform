import hashlib, io, json, os, subprocess, sys, time, uuid, wave
from concurrent.futures import ThreadPoolExecutor
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import delete, select, func
from services.model_worker import inference_queue as queue, uploads, rate_limit
from services.model_worker.main import app
from services.model_worker.store import DB, Run, User, Session, Asset, open_sealed
from conftest import Client
from test_domain import SAMPLES


@pytest.fixture
def queued(monkeypatch):
    monkeypatch.setenv("ENABLE_DURABLE_INFERENCE", "1")
    with DB.begin() as db:
        db.execute(delete(queue.InferenceJob))
    yield
    with DB.begin() as db:
        db.execute(delete(queue.InferenceJob))


def job(c, key=None, inputs=None):
    return c.request("POST", "/api/tools/billdetect-ai/jobs", json={
        "inputs": inputs or SAMPLES["bill"], "consent": True,
        "idempotency_key": key or uuid.uuid4().hex,
    })


def test_real_queue_worker_result_is_owned_encrypted_and_idempotent(user, queued):
    key = uuid.uuid4().hex
    r = job(user, key)
    assert r.status_code == 202, r.text
    jid = r.json()["id"]
    assert job(user, key).json()["id"] == jid
    with DB() as db:
        j = db.get(queue.InferenceJob, jid)
        assert j.encrypted.startswith("gAAAA")
        assert open_sealed(j.encrypted)["inputs"] == SAMPLES["bill"]
    claimed = queue.claim()
    # This is a real separate worker process, not a replaced inference response.
    completed = subprocess.run([sys.executable, "-m", "services.model_worker.inference_worker", "--execute-claim"],
                               input=json.dumps(claimed), text=True, capture_output=True, timeout=60)
    assert completed.returncode == 0, completed.stderr
    status = user.request("GET", "/api/jobs/" + jid).json()
    assert status["state"] == "succeeded", status
    result = user.request("GET", "/api/runs/" + status["run_id"])
    assert result.status_code == 200
    assert result.json()["output"]["module"] == "billdetect-ai"
    assert queue.publish_claim(claimed) is False
    with DB() as db:
        assert db.scalar(select(func.count()).select_from(Run).where(Run.idempotency_key == "job:" + jid)) == 1
        assert open_sealed(db.get(queue.InferenceJob, jid).encrypted) == {}
    with TestClient(app) as raw:
        other = Client(raw).register().admin()
        assert other.request("GET", "/api/jobs/" + jid).status_code == 404
        assert other.request("POST", "/api/jobs/" + jid + "/cancel").status_code == 404
        assert jid not in other.request("GET", "/api/jobs").text


def test_queue_input_mismatch_and_active_capacity(user, queued):
    key = uuid.uuid4().hex
    assert job(user, key).status_code == 202
    assert job(user, key, {"text": "different input"}).status_code == 409
    assert job(user).status_code == 202
    assert job(user).status_code == 429


def test_queue_mode_cannot_be_bypassed_and_correction_preserves_lineage(user, queued):
    payload = {"inputs": SAMPLES["bill"], "consent": True, "idempotency_key": uuid.uuid4().hex}
    assert user.request("POST", "/api/tools/billdetect-ai/runs", json=payload).status_code == 409
    first = job(user).json()["id"]
    assert queue.publish_claim(queue.claim())
    parent = user.request("GET", "/api/jobs/" + first).json()["run_id"]
    corrected = user.request("POST", f"/api/runs/{parent}/correct", json=payload)
    assert corrected.status_code == 202, corrected.text
    assert queue.publish_claim(queue.claim())
    rid = user.request("GET", "/api/jobs/" + corrected.json()["id"]).json()["run_id"]
    with DB() as db:
        assert db.get(Run, rid).parent_id == parent


def test_queue_cancellation_fences_worker(user, queued):
    jid = job(user).json()["id"]
    claimed = queue.claim()
    assert user.request("POST", "/api/jobs/" + jid + "/cancel").json()["state"] == "cancelled"
    assert queue.publish_claim(claimed) is False
    with DB() as db:
        assert not db.scalar(select(Run).where(Run.idempotency_key == "job:" + jid))
        assert open_sealed(db.get(queue.InferenceJob, jid).encrypted) == {}


def test_crashed_worker_lease_is_reclaimed_and_old_token_cannot_publish(user, queued):
    jid = job(user).json()["id"]
    first = queue.claim()
    assert queue.claim() is None
    with DB.begin() as db:
        db.get(queue.InferenceJob, jid).lease_until = 0
    second = queue.claim()
    assert first["token"] != second["token"]
    assert queue.publish_claim(first) is False
    assert queue.publish_claim(second) is True


def test_expiry_during_inference_rolls_back_result_and_consent(user, queued, monkeypatch):
    jid = job(user).json()["id"]
    claimed = queue.claim()
    at = int(time.time())
    calls = iter([at, at, at, at + 1000])
    monkeypatch.setattr(queue, "clock", lambda db: next(calls))
    assert queue.publish_claim(claimed) is False
    with DB() as db:
        assert not db.scalar(select(Run).where(Run.idempotency_key == "job:" + jid))
        assert db.get(queue.InferenceJob, jid).state == "running"


def test_queue_expired_session_and_exhaustion_fail_closed(user, queued):
    jid = job(user).json()["id"]
    claimed = queue.claim()
    with DB.begin() as db:
        j = db.get(queue.InferenceJob, jid)
        db.get(Session, j.session_id).expires = 0
    assert queue.publish_claim(claimed) is False
    with DB() as db:
        assert db.get(queue.InferenceJob, jid).state == "failed"
        assert not db.scalar(select(Run).where(Run.idempotency_key == "job:" + jid))


def test_queue_reaper_bounds_retries_and_clears_payload(user, queued):
    jid = job(user).json()["id"]
    with DB.begin() as db:
        j = db.get(queue.InferenceJob, jid)
        j.state, j.attempts, j.lease_until = "running", 3, 0
    assert queue.claim() is None
    status = user.request("GET", "/api/jobs/" + jid).json()
    assert status["state"] == "failed"
    assert "token" not in json.dumps(status) and "encrypted" not in status


def test_queue_feature_flag_and_csrf(user, monkeypatch):
    monkeypatch.setenv("ENABLE_DURABLE_INFERENCE", "0")
    assert job(user).status_code == 503
    assert user.client.post("/api/tools/billdetect-ai/jobs", json={"inputs": {}, "consent": True}).status_code == 403


def test_queue_runs_actual_multilingual_retrieval(user, queued):
    from services.model_worker.main import MODULES
    slug = next(slug for slug, module in MODULES.items() if module["engine"] == "rag")
    r = user.request("POST", f"/api/tools/{slug}/jobs", json={
        "inputs": SAMPLES["rag"], "consent": True, "idempotency_key": uuid.uuid4().hex,
    })
    assert r.status_code == 202
    assert queue.publish_claim(queue.claim()) is True
    status = user.request("GET", "/api/jobs/" + r.json()["id"]).json()
    result = user.request("GET", "/api/runs/" + status["run_id"]).json()["output"]
    assert result["references"]
    assert result["full_module_complete"] is False


def test_clearing_guest_scope_cascades_pending_jobs_and_chunks(client, queued):
    session = client.request("POST", "/api/session").json()
    client.csrf = session["csrf"]
    jid = job(client).json()["id"]
    data = wav_bytes(300)
    upload_id = begin(client, data).json()["id"]
    parts(client, upload_id, data)
    r = client.request("POST", "/api/session/clear", json={"confirm": True})
    assert r.status_code == 200
    with DB() as db:
        assert not db.get(queue.InferenceJob, jid)
        assert not db.get(uploads.ChunkUpload, upload_id)
        assert not db.scalar(select(uploads.UploadPart).where(uploads.UploadPart.upload_id == upload_id))


def wav_bytes(size=uploads.CHUNK_BYTES + 200):
    out = io.BytesIO()
    with wave.open(out, "wb") as w:
        w.setnchannels(1)
        w.setsampwidth(1)
        w.setframerate(24000)
        w.writeframes(b"private-audio-marker" * (size // 20))
    return out.getvalue()


def begin(c, data, checksum=None):
    return c.request("POST", "/api/uploads", json={
        "size": len(data), "checksum": checksum or hashlib.sha256(data).hexdigest(), "consent": True
    })


def parts(c, jid, data):
    for index, offset in enumerate(range(0, len(data), uploads.CHUNK_BYTES)):
        r = c.request("PUT", f"/api/uploads/{jid}/parts/{index}", content=data[offset:offset + uploads.CHUNK_BYTES])
        assert r.status_code == 200, r.text


def test_chunk_upload_preserves_full_file_and_encryption(user):
    data = wav_bytes(7 * uploads.CHUNK_BYTES)
    started = begin(user, data)
    assert started.status_code == 201
    jid = started.json()["id"]
    parts(user, jid, data)
    with DB() as db:
        rows = list(db.scalars(select(uploads.UploadPart).where(uploads.UploadPart.upload_id == jid)))
        assert len(rows) > 1
        assert all("private-audio-marker" not in p.encrypted for p in rows)
    done = user.request("POST", f"/api/uploads/{jid}/complete")
    assert done.status_code == 201, done.text
    aid = done.json()["id"]
    assert user.request("GET", "/api/assets/" + aid).content == data
    assert user.request("POST", f"/api/uploads/{jid}/complete").json()["id"] == aid
    with DB() as db:
        assert not db.scalar(select(uploads.UploadPart).where(uploads.UploadPart.upload_id == jid))


def test_chunk_retry_missing_size_and_checksum_checks(user):
    data = wav_bytes()
    jid = begin(user, data).json()["id"]
    first = data[:uploads.CHUNK_BYTES]
    url = f"/api/uploads/{jid}/parts/0"
    assert user.request("PUT", url, content=first).status_code == 200
    assert user.request("PUT", url, content=first).status_code == 200
    assert user.request("PUT", url, content=b"x" * len(first)).status_code == 409
    assert user.request("PUT", url, content=first + b"x").status_code == 413
    assert user.request("PUT", url, content=b"short").status_code == 422
    assert user.request("POST", f"/api/uploads/{jid}/complete").status_code == 409
    assert user.request("DELETE", "/api/uploads/" + jid).status_code == 200
    jid = begin(user, data, "0" * 64).json()["id"]
    parts(user, jid, data)
    assert user.request("POST", f"/api/uploads/{jid}/complete").status_code == 422


def test_chunk_owner_isolation_expiry_and_cleanup(user):
    data = wav_bytes(300)
    jid = begin(user, data).json()["id"]
    parts(user, jid, data)
    with TestClient(app) as raw:
        other = Client(raw).register().admin()
        for method, suffix in [("PUT", "/parts/0"), ("POST", "/complete"), ("DELETE", "")]:
            assert other.request(method, "/api/uploads/" + jid + suffix, content=data if method == "PUT" else None).status_code == 404
    with DB.begin() as db:
        db.get(uploads.ChunkUpload, jid).expires_at = 0
    assert user.request("POST", f"/api/uploads/{jid}/complete").status_code == 410
    with DB.begin() as db:
        uploads.cleanup(db)
    with DB() as db:
        assert not db.get(uploads.ChunkUpload, jid)
        assert not db.scalar(select(uploads.UploadPart).where(uploads.UploadPart.upload_id == jid))


def test_chunk_limits_and_validation_cannot_bypass_original_scanner(user):
    assert user.request("POST", "/api/uploads", json={"size": 10 * uploads.CHUNK_BYTES + 1, "checksum": "0" * 64, "consent": True}).status_code == 422
    data = b"not a permitted file"
    jid = begin(user, data).json()["id"]
    parts(user, jid, data)
    assert user.request("POST", f"/api/uploads/{jid}/complete").status_code == 422
    assert begin(user, data).status_code == 201
    assert begin(user, data).status_code == 429


def test_shared_rate_guard_survives_threads_processes_and_restart():
    identity = "synthetic-rate-" + uuid.uuid4().hex
    with ThreadPoolExecutor(max_workers=8) as pool:
        result = list(pool.map(lambda _: rate_limit.consume(identity, limit=7, at=120)[0], range(20)))
    assert sum(result) == 7
    assert rate_limit.consume(identity, limit=7, at=179) == (False, 1)
    assert rate_limit.consume(identity, limit=7, at=180) == (True, 60)
    identity = uuid.uuid4().hex
    code = "from services.model_worker.rate_limit import consume; import sys; print(sum(consume(sys.argv[1],limit=6,at=120)[0] for _ in range(5)))"
    children = [subprocess.Popen([sys.executable, "-c", code, identity], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True) for _ in range(2)]
    results = [p.communicate(timeout=30) for p in children]
    assert all(p.returncode == 0 for p in children), results
    assert sum(int(r[0]) for r in results) == 6
    with DB() as db:
        assert not db.scalar(select(rate_limit.RateBucket).where(rate_limit.RateBucket.subject == identity))


def test_production_guard_storage_failure_is_not_silently_allowed(client, monkeypatch):
    from services.model_worker import main
    monkeypatch.setattr(main, "PRODUCTION", True)
    token = "test-internal-guard-token-" + "X" * 32
    monkeypatch.setenv("PRIVATE_API_TOKEN", token)
    def unavailable(*args, **kwargs):
        raise RuntimeError("sensitive database details")
    monkeypatch.setattr(rate_limit, "consume", unavailable)
    r = client.request("POST", "/api/session", headers={"x-internal-api-token": token})
    assert r.status_code == 503 and "sensitive" not in r.text


def test_shared_guard_only_assigns_independent_quota_to_verified_session(user):
    peer = "synthetic-peer-" + uuid.uuid4().hex
    cookie = user.client.cookies.get("mouchak_session")
    assert sum(rate_limit.guard(peer, "tools", cookie)[0] for _ in range(61)) == 60
    # Rotating fabricated cookies cannot create independent owner quotas.
    assert sum(rate_limit.guard(peer, "tools", uuid.uuid4().hex)[0] for _ in range(61)) == 60
    with TestClient(app) as raw:
        other = Client(raw).register()
        assert rate_limit.guard(peer, "tools", raw.cookies.get("mouchak_session"))[0] is True
