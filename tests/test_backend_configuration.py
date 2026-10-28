import pytest
from services.model_worker import storage
from services.model_worker.provision import ROLES, provision, validate_passwords


def passwords():
    return {role: role + "-test-only-" + "X" * 24 for role in ROLES}


def test_custom_object_storage_uses_verified_https_and_bounded_sdk(monkeypatch):
    monkeypatch.setattr(storage, "PRODUCTION", True)
    monkeypatch.setenv("S3_ENDPOINT_URL", "https://owned-storage.example.test")
    monkeypatch.setenv("AWS_ACCESS_KEY_ID", "test-only-not-a-live-key")
    monkeypatch.setenv("AWS_SECRET_ACCESS_KEY", "test-only-not-a-live-secret")
    monkeypatch.delenv("S3_ADDRESSING_STYLE", raising=False)
    client = storage.client()
    assert client.meta.config.s3["addressing_style"] == "path"
    assert client.meta.config.connect_timeout == 3
    assert client.meta.config.read_timeout == 15
    assert client.meta.config.retries["total_max_attempts"] == 1
    monkeypatch.setenv("S3_ENDPOINT_URL", "http://owned-storage.example.test")
    with pytest.raises(RuntimeError):
        storage.client()


def test_database_bootstrap_rejects_shared_passwords_or_unverified_tls_before_connect():
    validate_passwords(passwords())
    with pytest.raises(ValueError):
        validate_passwords({role: "same-secret-" + "X" * 30 for role in ROLES})
    with pytest.raises(ValueError):
        provision("postgresql://unused.example.test/test?sslmode=require", passwords())


def test_generated_integration_ca_passes_strict_x509_validation(tmp_path):
    import runpy, subprocess
    from pathlib import Path
    root = Path(__file__).resolve().parents[1]
    helper = runpy.run_path(str(root / "scripts/test-production-stack.py"), run_name="certificate_test")
    directory = tmp_path / "tls"
    helper["certificates"](directory)
    verified = subprocess.run(["openssl", "verify", "-x509_strict", "-CAfile", str(directory / "ca.crt"), str(directory / "server.crt")], capture_output=True)
    assert verified.returncode == 0, verified.stderr.decode()
    assert not (directory / "ca.key").exists()
