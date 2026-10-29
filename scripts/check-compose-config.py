"""Validate portable topology syntax with explicit non-runtime dummy values."""
import os, re, subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
FILES = ["compose.local.yaml", "compose.backend.yaml", "compose.yaml"]


def configuration_environment():
    required = set()
    for name in FILES:
        required.update(re.findall(r"\$\{([A-Z][A-Z0-9_]*):\?required\}", (ROOT / "deploy" / name).read_text()))
    return {**os.environ, **{key: "test-only-configuration-placeholder" for key in required}}


def main():
    for name in FILES:
        subprocess.run(["docker", "compose", "--file", str(ROOT / "deploy" / name), "config", "--quiet"], env=configuration_environment(), cwd=ROOT, check=True, timeout=30)
    print("Local, backend-only and complete production Compose syntax passed; no services/resources created.")


if __name__ == "__main__":
    main()
