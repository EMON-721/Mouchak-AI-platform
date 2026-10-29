import pytest
import runpy
from pathlib import Path
from services.model_worker.serve import configured_port


def test_compose_validation_uses_dummy_values_for_all_required_keys_including_s3(monkeypatch):
    monkeypatch.setenv("S3_BUCKET", "owned-existing-bucket-not-for-ci")
    helper = runpy.run_path(str(Path(__file__).resolve().parents[1] / "scripts/check-compose-config.py"))
    env = helper["configuration_environment"]()
    for key in ["S3_BUCKET", "SITE_HOSTNAME", "API_HOSTNAME", "PRIVATE_API_TOKEN", "DATABASE_URL", "RETENTION_DATABASE_URL"]:
        assert env[key] == "test-only-configuration-placeholder"


def test_service_uses_provider_port_without_secret_arguments(monkeypatch):
    monkeypatch.setenv("PORT", "10000")
    assert configured_port() == 10000
    for invalid in ["0", "65536", "", "abc", "12.3", "৮০০০"]:
        with pytest.raises(ValueError):
            configured_port(invalid)


def test_production_private_api_never_accepts_a_missing_or_placeholder_token(client, monkeypatch):
    from services.model_worker import main
    monkeypatch.setattr(main, "PRODUCTION", True)
    for value in [None, "", "INVALID", "short", "x" * 513]:
        if value is None:
            monkeypatch.delenv("PRIVATE_API_TOKEN", raising=False)
        else:
            monkeypatch.setenv("PRIVATE_API_TOKEN", value)
        response = client.request("GET", "/api/health", headers={"x-internal-api-token": value or "INVALID"})
        assert response.status_code == 403
    token = "test-only-private-transport-token-" + "X" * 32
    monkeypatch.setenv("PRIVATE_API_TOKEN", token)
    assert client.request("GET", "/api/health", headers={"x-internal-api-token": token}).status_code == 200


def test_non_ascii_internal_header_is_denied_without_server_error(client, monkeypatch):
    from services.model_worker import main
    monkeypatch.setattr(main, "PRODUCTION", True)
    monkeypatch.setenv("PRIVATE_API_TOKEN", "test-only-private-transport-token-" + "X" * 32)
    response = client.client.get("/api/health", headers=[(b"x-internal-api-token", b"\xff")])
    assert response.status_code == 403


def test_non_ascii_csrf_is_denied_without_mutating_owner_records(user):
    response = user.client.post("/api/session/clear", headers=[(b"x-csrf-token", b"\xff")], json={"confirm": True})
    assert response.status_code == 403


def test_bengali_totp_digits_and_malformed_unicode_codes():
    from services.model_worker.auth import totp, valid_totp
    secret = "JBSWY3DPEHPK3PXP"
    code = totp(secret)
    assert valid_totp(secret, code)
    assert valid_totp(secret, code.translate(str.maketrans("0123456789", "০১২৩৪৫৬৭৮৯")))
    for invalid in ["é" * 6, "\x00" * 6, "12345", "１２３４５６", "NaN000", "١٢٣٤٥٦"]:
        assert valid_totp(secret, invalid) is False


def test_mfa_replay_cannot_switch_between_bengali_and_ascii_digits(admin):
    import json, time
    from services.model_worker.auth import digest, totp
    from services.model_worker.store import DB, Config
    with DB() as db:
        used = json.loads(db.get(Config, "mfa-replay:" + admin.user["id"]).value)["code"]
    code = next(totp(admin.secret, time.time() + offset) for offset in [-30, 0, 30]
                if digest(totp(admin.secret, time.time() + offset)) == used)
    response = admin.request("POST", "/api/auth/mfa/verify", json={"value": {"code": code.translate(str.maketrans("0123456789", "০১২৩৪৫৬৭৮৯"))}})
    assert response.status_code == 401
    assert "already used" in response.json()["detail"]
