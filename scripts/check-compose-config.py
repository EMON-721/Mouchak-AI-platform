"""Validate portable topology syntax with explicit non-runtime dummy values."""
import os, re, subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
files = ["compose.local.yaml", "compose.backend.yaml", "compose.yaml"]
required = set()
for name in files:
    required.update(re.findall(r"\$\{([A-Z_]+):\?required\}", (ROOT / "deploy" / name).read_text()))
env = {**os.environ, **{key: "test-only-configuration-placeholder" for key in required}}
for name in files:
    subprocess.run(["docker", "compose", "--file", str(ROOT / "deploy" / name), "config", "--quiet"], env=env, cwd=ROOT, check=True, timeout=30)
print("Local, backend-only and complete production Compose syntax passed; no services/resources created.")
