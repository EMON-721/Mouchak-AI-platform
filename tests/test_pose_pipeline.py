"""Actual pinned inference; photo-derived clips are not cricket validation."""

import hashlib, json, math
from pathlib import Path
import cv2
import numpy as np
import pytest
from fastapi.testclient import TestClient
from services.model_worker.main import app
from services.model_worker.store import DB, Run, Asset
from services.model_worker.domain import InputError
from services.model_worker.pose_runtime import (
    PoseRuntime,
    ASSETS,
    availability,
    verify_models,
)
from services.model_worker.pose_video import analyze, probe, validate_upload


@pytest.fixture(scope="module")
def clips(tmp_path_factory):
    fixture = Path("models/pose/smoke-fixture.jpg")
    assert fixture.exists(), "Run scripts/download-pose.py --test-fixture"
    assert (
        hashlib.sha256(fixture.read_bytes()).hexdigest()
        == "c8a830ed683c0276d713dd5aeda28f415f10cd6291972084a40d0d8b934ed62b"
    )
    photo = cv2.resize(cv2.imread(str(fixture)), (800, 534))
    directory = tmp_path_factory.mktemp("pose-fixtures")
    result = {}
    for name, mode in [("static", 0), ("motion", 1), ("blank", 2)]:
        p = directory / (name + ".mp4")
        writer = cv2.VideoWriter(str(p), cv2.VideoWriter_fourcc(*"mp4v"), 8, (800, 534))
        assert writer.isOpened()
        for i in range(16):
            matrix = cv2.getRotationMatrix2D(
                (400, 267), 5 * math.sin(i / 5) if mode == 1 else 0, 1
            )
            frame = (
                photo * 0 if mode == 2 else cv2.warpAffine(photo, matrix, (800, 534))
            )
            writer.write(frame)
        writer.release()
        result[name] = p.read_bytes()
    return result


@pytest.fixture
def experimental(monkeypatch):
    monkeypatch.setenv("ENABLE_EXPERIMENTAL_POSE", "1")
    monkeypatch.setenv("MOUCHAK_ENV", "test")
    assert availability()["experimental_enabled"] is True


def scope(c):
    r = c.post("/api/session")
    assert r.status_code == 200
    c.headers["x-csrf-token"] = r.json()["csrf"]


def upload(c, data):
    return c.post(
        "/api/upload",
        files={"file": ("practice.mp4", data, "video/mp4")},
        data={"consent": "true"},
    )


def test_default_and_production_refuse_experimental_pose(clips, monkeypatch):
    monkeypatch.delenv("ENABLE_EXPERIMENTAL_POSE", raising=False)
    assert availability()["experimental_enabled"] is False
    with pytest.raises(InputError):
        analyze([clips["static"]])
    monkeypatch.setenv("ENABLE_EXPERIMENTAL_POSE", "1")
    monkeypatch.setenv("MOUCHAK_ENV", "production")
    assert availability()["experimental_enabled"] is False
    with pytest.raises(InputError):
        analyze([clips["static"]])


def test_missing_and_tampered_weights_abstain(tmp_path, monkeypatch):
    monkeypatch.setenv("MODEL_DIR", str(tmp_path))
    with pytest.raises(InputError):
        verify_models()
    (tmp_path / "pose").mkdir()
    for name in ASSETS:
        (tmp_path / "pose" / name).write_bytes(b"Not a model")
    with pytest.raises(InputError):
        PoseRuntime()
    assert availability()["weights_verified"] is False


def test_actual_video_landmarks_comparison_and_timestamps(clips, experimental):
    r = analyze([clips["motion"], clips["static"]])
    assert r["status"] == "experimental_observation"
    assert r["facts"]["pose_evidence_available"] is True
    assert r["facts"]["coaching_suggestions_validated"] is False
    assert r["model_version"].endswith("/onnx-cpu")
    a, b = r["details"]["clips"]
    assert a["tracked_frames"] >= 3 and a["valid_frame_percentage"] >= 60
    assert a["frames"][0]["timestamp_seconds"] == 0
    assert all(
        y["timestamp_seconds"] > x["timestamp_seconds"]
        for x, y in zip(a["frames"], a["frames"][1:])
    )
    for frame in a["frames"]:
        if frame["status"] == "tracked":
            assert len(frame["landmarks"]) == 33
            assert {p["id"] for p in frame["landmarks"]} == set(range(33))
            assert all(
                math.isfinite(p["x"]) and math.isfinite(p["y"])
                for p in frame["landmarks"]
            )
    comparison = r["details"]["comparison"]
    assert comparison["comparable"] is True
    assert max(comparison["mean_absolute_angle_difference_degrees"].values()) > 0.01
    assert comparison["skill_score"] is None and a["raw_frames_returned"] is False
    assert not any(k in json.dumps(r).lower() for k in ["base64", "injury_risk_score"])


def test_real_blank_frames_abstain(clips, experimental):
    r = analyze([clips["blank"]])
    assert r["status"] == "evidence_insufficient"
    assert (
        r["facts"]["pose_evidence_available"] is False
        and r["facts"]["angle_ranges_2d"] is None
    )
    assert all(not f["landmarks"] for f in r["details"]["clips"][0]["frames"])


def test_group_fixture_abstains_when_people_cannot_be_resolved():
    photo = cv2.resize(cv2.imread("models/pose/smoke-fixture.jpg"), (400, 268))
    r = PoseRuntime().infer(np.concatenate([photo, photo], axis=1))
    # This real composite currently has no reliable detections; it is not a
    # group-detector recall benchmark. Either ambiguity/refusal is acceptable.
    assert r["status"] in ["multiple_people", "no_person"] and not r["landmarks"]


def test_mp4_signature_decoder_and_limits(clips, tmp_path):
    assert validate_upload(clips["static"])["duration_seconds"] == 2
    with pytest.raises(InputError):
        validate_upload(b"0000ftyp" + b"x" * 100)
    with pytest.raises(InputError):
        validate_upload(b"x" * (10 * 1024 * 1024 + 1))
    path = tmp_path / "too-long.mp4"
    writer = cv2.VideoWriter(str(path), cv2.VideoWriter_fourcc(*"mp4v"), 8, (80, 80))
    for _ in range(88):
        writer.write(np.zeros((80, 80, 3), np.uint8))
    writer.release()
    with pytest.raises(InputError):
        probe(path)


def test_public_pose_consent_private_storage_and_exports(clips, experimental):
    with TestClient(app) as owner, TestClient(app) as other:
        scope(owner)
        scope(other)
        assert (
            owner.get("/api/modules/golicoach-ai").json()["release_status"]
            == "experimental"
        )
        bad = owner.post(
            "/api/upload",
            files={"file": ("p.mp4", clips["static"], "video/mp4")},
            data={"consent": "false"},
        )
        assert bad.status_code == 422
        a = upload(owner, clips["motion"])
        assert a.status_code == 201, a.text
        aid = a.json()["id"]
        p = {"inputs": {}, "asset_ids": [aid], "consent": False}
        assert owner.post("/api/tools/golicoach-ai/runs", json=p).status_code == 422
        assert (
            other.post(
                "/api/tools/golicoach-ai/runs", json={**p, "consent": True}
            ).status_code
            == 404
        )
        run = owner.post("/api/tools/golicoach-ai/runs", json={**p, "consent": True})
        assert run.status_code == 201, run.text
        rid = run.json()["id"]
        assert (
            run.json()["full_module_complete"] is False
            and run.json()["status"] == "experimental_observation"
        )
        assert other.get("/api/runs/" + rid).status_code == 404
        assert other.get("/api/runs/" + rid + "/export?format=json").status_code == 404
        doc = owner.get("/api/runs/" + rid + "/export?format=json").json()
        assert doc["output"]["details"]["clips"][0]["tracked_frames"] >= 3
        with DB() as db:
            assert "landmarks" not in db.get(Run, rid).encrypted
            a = db.get(Asset, aid)
            assert a.kind == "mp4" and Path(a.path).read_bytes() != clips["motion"]


def test_disabled_upload_and_invalid_asset_type(clips, monkeypatch, experimental):
    with TestClient(app) as c:
        scope(c)
        assert (
            c.post(
                "/api/tools/golicoach-ai/runs", json={"inputs": {}, "consent": True}
            ).status_code
            == 422
        )
        monkeypatch.delenv("ENABLE_EXPERIMENTAL_POSE")
        assert upload(c, clips["static"]).status_code == 503
        assert c.get("/api/modules/golicoach-ai").json()["release_status"] == "blocked"
