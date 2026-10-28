"""Opt-in real HTTPS backend smoke test using only owned temporary fixtures.

Credentials come from environment/secret injection, never argv or output. No
operator account, existing visitor record or external dataset is modified.
"""
import io
import json
import os
import ssl
import time
import uuid
from urllib.parse import urlsplit

import httpx
from PIL import Image, ImageDraw


class SmokeError(Exception):
    def __init__(self, stage):
        self.stage = stage
        super().__init__("Backend smoke check failed at " + stage)


def configuration(env):
    def origin(name):
        value = env.get(name, "")
        try:
            parts = urlsplit(value)
            valid = (parts.scheme == "https" and parts.hostname and not parts.username
                     and not parts.password and not parts.query and not parts.fragment
                     and parts.path in ("", "/") and parts.port != 0
                     and not any(ord(c) < 33 or ord(c) == 127 for c in value))
        except ValueError:
            valid = False
        if not valid:
            raise SmokeError("configuration")
        return value.rstrip("/")
    base, public = origin("PRIVATE_API_URL"), origin("PUBLIC_ORIGIN")
    token = env.get("PRIVATE_API_TOKEN", "")
    if not 32 <= len(token) <= 512 or not token.isascii() or any(c.isspace() or not 33 <= ord(c) <= 126 for c in token):
        raise SmokeError("configuration")
    try:
        context = ssl.create_default_context(cafile=env.get("MOUCHAK_SMOKE_CA_FILE") or None)
    except (OSError, ssl.SSLError):
        raise SmokeError("configuration") from None
    return base, public, token, context


def fixture_png():
    image = Image.new("RGB", (640, 160), "white")
    ImageDraw.Draw(image).text((20, 40), "DEMO owned deployment fixture 123", fill="black", font_size=26)
    output = io.BytesIO()
    image.save(output, "PNG")
    return output.getvalue()


def verify_backend(env=None):
    base, public, token, context = configuration(os.environ if env is None else env)
    headers = {"x-internal-api-token": token, "origin": public}
    clients = [httpx.Client(base_url=base, headers=headers, verify=context,
                           follow_redirects=False, timeout=httpx.Timeout(30, connect=5)) for _ in range(2)]
    active = []
    checks = {}
    stage = "health"
    failure = None

    def require(condition):
        if not condition:
            raise SmokeError(stage)

    def request(client, method, path, expected=200, **kwargs):
        response = client.request(method, path, **kwargs)
        require(response.status_code == expected)
        return response

    def queued(client, slug, inputs):
        job = request(client, "POST", f"/api/tools/{slug}/jobs", 202,
                      json={"inputs": inputs, "consent": True, "idempotency_key": uuid.uuid4().hex}).json()
        deadline = time.monotonic() + 120
        while time.monotonic() < deadline:
            current = request(client, "GET", "/api/jobs/" + job["id"]).json()
            if current["state"] == "succeeded":
                return request(client, "GET", "/api/runs/" + current["run_id"]).json()
            require(current["state"] not in ("failed", "cancelled", "expired"))
            time.sleep(0.5)
        raise SmokeError(stage)

    try:
        first, second = clients
        health = request(first, "GET", "/api/health").json()
        require(health.get("api") == "ok" and health.get("tools") == 50 and health.get("processing_mode") == "queued")
        with httpx.Client(base_url=base, verify=context, follow_redirects=False, timeout=10) as outsider:
            require(outsider.get("/api/health").status_code == 403)
        checks["private_https_boundary"] = True
        stage = "visitor"
        for client in clients:
            response = request(client, "POST", "/api/session")
            # Record the scope before parsing/checking so failure still attempts cleanup.
            active.append(client)
            session = response.json()
            require(session.get("mode") == "anonymous" and session.get("profile_collected") is False)
            cookie = response.headers.get("set-cookie", "").lower()
            require("secure" in cookie and "httponly" in cookie)
            client.headers["x-csrf-token"] = session["csrf"]
        checks["account_free_secure_visitors"] = True
        stage = "upload"
        picture = fixture_png()
        asset = request(first, "POST", "/api/upload", 201,
                        files={"file": ("DEMO-owned-smoke.png", picture, "image/png")}, data={"consent": "true"}).json()
        require(asset.get("scan_state") == "clean")
        aid = asset["id"]
        require(request(first, "GET", "/api/assets/" + aid).content == picture)
        checks["private_scanned_storage_roundtrip"] = True
        stage = "ocr"
        output = request(first, "POST", "/api/assets/" + aid + "/ocr").json()
        require("Tesseract" in output.get("model", "") and any("123" in page["text"] for page in output["pages"]))
        checks["real_tesseract"] = True
        stage = "queued_calculation"
        bill = queued(first, "billdetect-ai", {"rows": [{"name": "DEMO owned smoke", "amount": "১২৫"}], "declared": "১৫০"})
        require(bill["output"]["facts"].get("difference_bdt") == "25.00")
        checks["real_worker_bengali_decimal_calculation"] = True
        stage = "retrieval"
        answers = []
        for question in ["বাষ্পীভবন কী?", "সালোকসংশ্লেষণ কী?"]:
            run = queued(first, "shikkharag-bd", {"text": question})
            result = run["output"]
            require(result.get("references") and result["facts"].get("supported")
                    and result.get("full_module_complete") is False and "MiniLM" in result.get("method", ""))
            answers.append(result["facts"]["answer"])
        require(answers[0] != answers[1])
        checks["two_distinct_real_onnx_retrieval_answers"] = True
        stage = "export"
        exported = request(first, "GET", f"/api/runs/{bill['id']}/export?format=json").json()
        require(exported["output"]["facts"]["difference_bdt"] == "25.00")
        checks["owned_result_export"] = True
        stage = "owner_isolation"
        require(second.get("/api/runs/" + bill["id"]).status_code == 404)
        require(second.get("/api/assets/" + aid).status_code == 404)
        checks["second_visitor_private_read_denied"] = True
    except Exception:
        # Never emit driver errors, URLs, response bodies, cookies or secret values.
        failure = SmokeError(stage)
    finally:
        cleared = True
        for client in active:
            try:
                cleared = client.post("/api/session/clear", json={"confirm": True}).status_code == 200 and cleared
            except Exception:
                cleared = False
        for client in clients:
            client.close()
        if active:
            checks["owned_temporary_scopes_cleared"] = cleared
            if not cleared:
                failure = SmokeError("cleanup")
    if failure:
        raise failure from None
    return {"result": "passed", "checks": checks, "fixtures": "owned_temporary_demo_only",
            "operator_browser_mfa_verified": False, "provider_backup_restore_verified": False,
            "bangladesh_domain_accuracy_verified": False, "full_production_scope_certified": False}


def main():
    try:
        print(json.dumps(verify_backend()))
        return 0
    except SmokeError as error:
        print(json.dumps({"result": "failed", "stage": error.stage, "secrets_logged": False}))
        return 1
    except Exception:
        print(json.dumps({"result": "failed", "stage": "configuration", "secrets_logged": False}))
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
