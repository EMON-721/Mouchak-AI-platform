import importlib.util
from pathlib import Path

spec = importlib.util.spec_from_file_location("public_source_check", Path(__file__).resolve().parents[1] / "scripts/check-public-source.py")
checker = importlib.util.module_from_spec(spec)
spec.loader.exec_module(checker)


def test_publication_scan_catches_credentials_and_private_artifacts_without_returning_values():
    token = ("gh" + "p_" + "a" * 40).encode()
    assert checker.findings("source.txt", token) == ["github-token"]
    url = b"postgresql://owner:" + b"not" + b"safe123456789@dpg-owned.render.com/db"
    assert checker.findings("config.txt", url) == ["credential-bearing-database-url"]
    assert "private-runtime-artifact" in checker.findings(".state/development.db", b"binary")
    assert "environment-file" in checker.findings(".env.production", b"")
    assert not checker.findings(".env.example", b"DATABASE_URL=postgresql://user:REPLACE@postgres/db")
