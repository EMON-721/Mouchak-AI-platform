import pytest
from services.model_worker.serve import configured_port


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
