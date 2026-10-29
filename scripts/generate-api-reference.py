"""Generate a route index from implemented Python decorators, without importing the app."""
import ast
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
lines = [
    "# Implemented API route index", "",
    "Generated from FastAPI decorators; run python3 scripts/generate-api-reference.py to refresh.", "",
    "The website proxies /api/* to the private Python service. Production requires the server-only internal token on every route. Owner routes additionally enforce cookie/session, owner scope and write CSRF; privileged routes enforce role and recent MFA. Read the handler and tests for its exact policy.", "",
    "A route's presence is not proof that its advanced model/data gate is enabled. Public registration/profile routes are intentionally retired; end-user password login is disabled. The health endpoint is protected in production. No default admin or API key is published.", "",
    "| Method | Path | Handler |", "|---|---|---|",
]
for file in sorted((ROOT / "services/model_worker").glob("*.py")):
    tree = ast.parse(file.read_text())
    prefix = ""
    for node in ast.walk(tree):
        if isinstance(node, ast.Call) and isinstance(node.func, ast.Name) and node.func.id == "APIRouter":
            prefix = next((ast.literal_eval(k.value) for k in node.keywords if k.arg == "prefix"), "")
    for node in tree.body:
        if not isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            continue
        for decorator in node.decorator_list:
            if isinstance(decorator, ast.Call) and isinstance(decorator.func, ast.Attribute) and decorator.func.attr in {"get", "post", "put", "patch", "delete"} and decorator.args:
                route = prefix + ast.literal_eval(decorator.args[0])
                lines.append(f"| {decorator.func.attr.upper()} | `{route}` | `{file.stem}.{node.name}` |")
content = "\n".join(lines) + "\n"
target = ROOT / "docs/API_REFERENCE.md"
if "--check" in sys.argv:
    if not target.exists() or target.read_text() != content:
        raise SystemExit("API reference is stale; regenerate it.")
else:
    target.write_text(content)
print("Implemented API route index verified.")
