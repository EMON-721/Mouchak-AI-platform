"""Real isolated TLS PostgreSQL/S3/container checks; never deploys a cloud host.

No model/API responses are mocked. A tiny owned ClamAV test signature verifies
the scanner rejection path; it is not a current threat-signature feed.
"""
import base64, hashlib, io, json, os, re, secrets, socket, ssl, subprocess, sys, tempfile, time, traceback, uuid
from pathlib import Path
import boto3, httpx, psycopg
from botocore.config import Config
from cryptography.fernet import Fernet
from PIL import Image, ImageDraw, ImageFont
from argon2 import PasswordHasher

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from services.model_worker.provision import provision, ROLES


def wait_for(callback, seconds=90):
    deadline = time.monotonic() + seconds
    last = None
    while time.monotonic() < deadline:
        try:
            result = callback()
            if result:
                return result
        except Exception as error:
            last = {"class": type(error).__name__}
            response = getattr(error, "response", None)
            if isinstance(response, dict):
                last["provider_code"] = response.get("Error", {}).get("Code")
                last["http_status"] = response.get("ResponseMetadata", {}).get("HTTPStatusCode")
            # Only allowlisted diagnostics, never full exception/response bodies.
            message = str(error).lower()
            for label, pattern in [("certificate_verify_failed", "certificate verify failed"), ("wrong_tls_version", "wrong version number"), ("connection_refused", "connection refused"), ("connection_timeout", "timed out")]:
                if pattern in message:
                    last["reason"] = label
        time.sleep(0.5)
    raise AssertionError("Timed out waiting for fixture operation: " + json.dumps(last))


def certificates(directory):
    directory.mkdir(mode=0o755)
    def openssl(*args):
        subprocess.run(["openssl", *args], cwd=directory, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    openssl("req", "-x509", "-newkey", "rsa:2048", "-nodes", "-keyout", "ca.key", "-out", "ca.crt", "-days", "2", "-subj", "/CN=Mouchak Disposable Integration CA",
            "-addext", "keyUsage=critical,keyCertSign,cRLSign")
    openssl("req", "-newkey", "rsa:2048", "-nodes", "-keyout", "server.key", "-out", "server.csr", "-subj", "/CN=localhost")
    (directory / "extensions").write_text("subjectAltName=DNS:localhost,DNS:database,DNS:objectstore,IP:127.0.0.1\nextendedKeyUsage=serverAuth\nbasicConstraints=critical,CA:FALSE\nkeyUsage=critical,digitalSignature,keyEncipherment\nsubjectKeyIdentifier=hash\nauthorityKeyIdentifier=keyid,issuer\n")
    openssl("x509", "-req", "-in", "server.csr", "-CA", "ca.crt", "-CAkey", "ca.key", "-CAcreateserial", "-out", "server.crt", "-days", "2", "-extfile", "extensions")
    (directory / "public.crt").write_bytes((directory / "server.crt").read_bytes())
    (directory / "private.key").write_bytes((directory / "server.key").read_bytes())
    for name in ["ca.key", "server.key", "private.key"]:
        (directory / name).chmod(0o600)
    # The CA signing key must not be mounted into any service.
    (directory / "ca.key").unlink()


def own_png(marker=None):
    picture = Image.new("RGB", (600, 160), "white")
    draw = ImageDraw.Draw(picture)
    font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 28)
    draw.text((20, 30), "Owned integration fixture 123", fill="black", font=font)
    out = io.BytesIO(); picture.save(out, "PNG")
    return out.getvalue() + (marker or b"")


def totp(secret):
    # Standard test authenticator only; no secret is logged or exported.
    import hmac, struct
    key = base64.b32decode(secret + "=" * ((8 - len(secret) % 8) % 8))
    mac = hmac.new(key, struct.pack(">Q", int(time.time()) // 30), hashlib.sha1).digest()
    offset = mac[-1] & 15
    return f"{(struct.unpack('>I', mac[offset:offset+4])[0] & 0x7fffffff) % 1000000:06d}"



def check_directory_integration(operator, client, pg_dsn, secret_values, visitor):
    """Actual HTTPS + role-limited PostgreSQL + independent queue worker."""
    from datetime import datetime, timedelta, timezone
    second_id, password = str(uuid.uuid4()), secrets.token_urlsafe(24)
    secret_values.append(password)
    sid = "DEMO-DIR-" + uuid.uuid4().hex
    with psycopg.connect(pg_dsn) as owner:
        owner.execute("INSERT INTO users(id,email,password,name,role,verified,banned,language,mfa_enabled,created_at) VALUES(%s,%s,%s,'DEMO independent reviewer','dataset_reviewer',true,false,'bn',false,%s)",
                      (second_id, "reviewer@integration.invalid", PasswordHasher(time_cost=3,memory_cost=65536,parallelism=2).hash(password), datetime.now(timezone.utc).isoformat()))
        owner.execute("INSERT INTO workspaces(id,user_id,name) VALUES(%s,%s,'DEMO reviewer work')", (str(uuid.uuid4()), second_id))
        owner.execute("INSERT INTO dataset_sources(id,module,metadata_json,state) VALUES(%s,'cliniccompass-bd','{}','candidate')", (sid,))
    with client() as reviewer:
        login = reviewer.post("/api/auth/login", json={"email": "reviewer@integration.invalid", "password": password})
        assert login.status_code == 200
        reviewer.headers["x-csrf-token"] = login.json()["csrf"]
        enrollment = reviewer.post("/api/auth/mfa/enroll").json()
        code = totp(enrollment["secret"])
        bengali = code.translate(str.maketrans("0123456789", "০১২৩৪৫৬৭৮৯"))
        assert reviewer.post("/api/auth/mfa/verify", json={"value": {"code": bengali}}).status_code == 200
        assert reviewer.post("/api/auth/mfa/verify", json={"value": {"code": code}}).status_code == 401
        rights = {"decision": "approved_train_and_reuse", "asset_url": "https://example.test/DEMO-fixture-directory.json",
                  "terms_url": "https://example.test/DEMO-terms", "license_uri": "https://creativecommons.org/publicdomain/zero/1.0/",
                  "scope": "Owned synthetic nonpersonal disposable fixture only", "coverage": "Bangladesh DEMO only", "source_date": "2026-01-01",
                  "evidence": "Owned DEMO facility record only; never real provider or stock information", "sensitivity": "public_nonpersonal"}
        assert operator.post(f"/api/admin/sources/{sid}/reviews", json=rights).json()["state"] == "rights_review"
        assert reviewer.post(f"/api/admin/sources/{sid}/reviews", json=rights).json()["state"] == "approved_train_and_reuse"
        row = {"id": "DEMO-TLS-FACILITY", "name_bn": "DEMO পরীক্ষার কেন্দ্র", "name_en": "DEMO test facility",
               "district_bn": "ঢাকা", "district_en": "Dhaka", "address_bn": "DEMO বাস্তব ঠিকানা নয়", "address_en": "DEMO no real address",
               "verified_at": (datetime.now(timezone.utc) - timedelta(minutes=1)).isoformat(), "services_bn": ["চোখ পরীক্ষা"], "services_en": ["eye examination"]}
        staged = operator.post("/api/admin/directories/dry-run", json={"source_id": sid, "schema_name": "facility_v1", "records": [row]})
        assert staged.status_code == 201, "TLS directory dry-run failed"
        revision = staged.json()["id"]
        assert operator.post(f"/api/admin/directories/{revision}/publish", json={}).status_code == 403
        assert reviewer.post(f"/api/admin/directories/{revision}/publish", json={}).status_code == 200
        queued = visitor.post("/api/tools/cliniccompass-bd/jobs", json={"inputs": {"text": "চোখ পরীক্ষা"}, "consent": True, "idempotency_key": uuid.uuid4().hex})
        assert queued.status_code == 202
        def completed_directory():
            status = visitor.get("/api/jobs/" + queued.json()["id"]).json()
            assert status["state"] != "failed", "Directory worker or database grant failed"
            return status if status["state"] == "succeeded" else None
        done = wait_for(completed_directory)
        output = visitor.get("/api/runs/" + done["run_id"]).json()["output"]
        assert output["facts"]["records"][0]["id"] == "DEMO-TLS-FACILITY"
        assert output["references"][0]["independent_reviewers"] == 2
        assert output["source_kind"] == "rights_reviewed_directory"
        # Revoke real source rights and require immediate public unavailability.
        assert reviewer.post(f"/api/admin/sources/{sid}/reviews", json={**rights, "decision": "revoked"}).status_code == 201
        metadata = visitor.get("/api/modules/cliniccompass-bd")
        assert metadata.status_code == 200
        assert metadata.json()["release_status"] == "blocked"
        assert reviewer.post("/api/admin/directories/cliniccompass-bd/withdraw", json={"expected_revision": revision}).status_code == 200


def main():
    project = "mouchak-integration-" + uuid.uuid4().hex[:10]
    role_passwords = {role: secrets.token_urlsafe(32) for role in ROLES}
    pg_password, api_token, s3_password = [secrets.token_urlsafe(32) for _ in range(3)]
    s3_user = "fixture" + secrets.token_hex(8)
    data_key = Fernet.generate_key().decode()
    secret_values = [*role_passwords.values(), pg_password, api_token, s3_password, data_key]
    report = {"fixture_only": True, "cloud_deployment": False, "full_50_tool_scope_certified": False}
    # Replace checked-in historical evidence before any operation. A failed run
    # must never upload an older passing report under the current workflow ID.
    evidence = ROOT / "docs/audit/production-stack.json"
    evidence.write_text(json.dumps({**report, "result": "running"}, indent=2) + "\n")
    with tempfile.TemporaryDirectory(prefix="mouchak-stack-") as temporary:
        folder = Path(temporary); folder.chmod(0o755)
        certificates(folder / "tls")
        signatures = folder / "signatures"; signatures.mkdir(mode=0o755)
        marker = b"MOUCHAK_OWNED_SCANNER_TEST_ONLY_7bfc62"
        (signatures / "test-only.ndb").write_text("Mouchak.Owned.TestOnly:0:*:" + marker.hex() + "\n")
        env = {**os.environ, "MOUCHAK_TEST_DIR": str(folder), "MOUCHAK_TEST_IMAGE": project + ":tested",
               "MOUCHAK_TEST_PG_PASSWORD": pg_password, "MOUCHAK_TEST_API_TOKEN": api_token,
               "MOUCHAK_TEST_DATA_KEY": data_key, "MOUCHAK_TEST_S3_USER": s3_user,
               "MOUCHAK_TEST_S3_PASSWORD": s3_password,
               "MOUCHAK_TEST_S3_KEK": secrets.token_hex(32)}
        for role in ROLES:
            label = role.removeprefix("mouchak_").upper()
            env[f"MOUCHAK_TEST_{label}_DSN"] = f"postgresql+psycopg://{role}:{role_passwords[role]}@database:5432/mouchak_integration?sslmode=verify-full&sslrootcert=/test-ca/ca.crt"
        compose = ["docker", "compose", "--project-name", project, "--file", str(ROOT / "deploy/compose.integration.yaml")]
        failed_operation = []
        def run(*args, timeout=600):
            result = subprocess.run([*compose, *args], cwd=ROOT, env=env, capture_output=True, text=True, timeout=timeout)
            if result.returncode:
                failed_operation.append(result.stdout[-12000:] + result.stderr[-12000:])
                raise RuntimeError("Compose operation failed: " + " ".join(args[:2]))
            return result.stdout.strip()
        def port(service, internal):
            return int(run("port", service, str(internal)).rsplit(":", 1)[1])
        try:
            run("build", "api", timeout=900)
            run("up", "-d", "database", "objectdata", "objectstore")
            pg_port, object_port = port("database", 5432), port("objectstore", 9000)
            pg_dsn = f"postgresql://postgres:{pg_password}@127.0.0.1:{pg_port}/mouchak_integration?sslmode=verify-full&sslrootcert={folder}/tls/ca.crt"
            def database_ready():
                with psycopg.connect(pg_dsn) as connection:
                    return connection.pgconn.ssl_in_use
            wait_for(database_ready)
            first = provision(pg_dsn, role_passwords)
            second = provision(pg_dsn, role_passwords)
            assert first["applied"] and second["applied"] == []
            report["postgres_tls_verified"] = True
            report["migration_ledger_idempotent"] = True
            with psycopg.connect(pg_dsn) as owner:
                roles = owner.execute("SELECT rolname,rolsuper,rolbypassrls,rolcreatedb,rolcreaterole,rolinherit FROM pg_roles WHERE rolname=ANY(%s)", (list(ROLES),)).fetchall()
                assert len(roles) == 4 and all(not any(row[1:]) for row in roles)
            report["four_isolated_roles"] = True
            s3_context = ssl.create_default_context(cafile=str(folder / "tls/ca.crt"))
            def verified_object_tls():
                with socket.create_connection(("127.0.0.1", object_port), timeout=3) as raw_socket:
                    with s3_context.wrap_socket(raw_socket, server_hostname="127.0.0.1") as verified_socket:
                        return bool(verified_socket.getpeercert())
            wait_for(verified_object_tls)
            report["s3_tls_handshake_verified"] = True
            s3 = boto3.client("s3", endpoint_url=f"https://127.0.0.1:{object_port}",
                              aws_access_key_id=s3_user, aws_secret_access_key=s3_password,
                              region_name="us-east-1", verify=str(folder / "tls/ca.crt"),
                              config=Config(s3={"addressing_style":"path"}, connect_timeout=3, read_timeout=5, retries={"total_max_attempts":1}))
            wait_for(lambda: s3.list_buckets() is not None, seconds=180)
            s3.create_bucket(Bucket="mouchak-private-test")
            report["s3_tls_verified"] = True
            run("up", "-d", "api", "inference", "scheduler", "retention", "gateway", timeout=600)
            base = f"https://127.0.0.1:{port('gateway', 443)}"
            ssl_context = ssl.create_default_context(cafile=str(folder / "tls/ca.crt"))
            headers = {"x-internal-api-token": api_token, "origin": "https://mouchak.integration.test"}
            def client():
                return httpx.Client(base_url=base, headers=headers, verify=ssl_context, timeout=60)
            with client() as probe:
                wait_for(lambda: probe.get("/api/health").is_success)
                with httpx.Client(base_url=base, verify=ssl_context) as outsider:
                    assert outsider.get("/api/health").status_code == 403
                response = probe.post("/api/session"); assert response.status_code == 200
                scope = response.json(); probe.headers["x-csrf-token"] = scope["csrf"]
                assert "Secure" in response.headers["set-cookie"] and "HttpOnly" in response.headers["set-cookie"]
                wid = probe.get("/api/workspaces").json()[0]["id"]
                assert probe.post("/api/workspaces", json={"value": {"name": "Rejected"}}, headers={"origin": "https://untrusted.integration.test"}).status_code == 403
                with client() as stranger:
                    visitor = stranger.post("/api/session").json(); stranger.headers["x-csrf-token"] = visitor["csrf"]
                    assert stranger.get(f"/api/workspaces/{wid}/history").status_code == 404
                report["secure_cookie_origin_csrf_and_owner_boundaries"] = True
                image = own_png()
                asset = probe.post("/api/upload", files={"file": ("owned.png", image, "image/png")}, data={"consent": "true"})
                assert asset.status_code == 201, "Real S3/scanner upload failed"
                aid = asset.json()["id"]; assert asset.json()["scan_state"] == "clean"
                raw = s3.get_object(Bucket="mouchak-private-test", Key="private/" + aid)
                assert raw["ServerSideEncryption"] == "AES256"
                ciphertext = raw["Body"].read(); assert ciphertext != image and Fernet(data_key.encode()).decrypt(ciphertext) == image
                assert probe.get("/api/assets/" + aid).content == image
                blocked = probe.post("/api/upload", files={"file": ("scanner-test.png", own_png(marker), "image/png")}, data={"consent": "true"})
                assert blocked.status_code == 422
                assert len(s3.list_objects_v2(Bucket="mouchak-private-test").get("Contents", [])) == 1
                with httpx.Client(verify=ssl_context) as public:
                    assert public.get(f"https://127.0.0.1:{object_port}/mouchak-private-test/private/{aid}").status_code == 403
                report["s3_private_ciphertext_sse_roundtrip"] = True
                report["real_clamav_test_signature_rejection"] = True
                queued = probe.post("/api/tools/billdetect-ai/jobs", json={"inputs": {"rows": [{"name": "Owned", "amount": "125"}], "declared": "150"}, "consent": True, "idempotency_key": uuid.uuid4().hex})
                assert queued.status_code == 202
                jid = queued.json()["id"]
                def completed():
                    status = probe.get("/api/jobs/" + jid).json()
                    if status["state"] == "failed": raise AssertionError("Inference worker failed")
                    return status if status["state"] == "succeeded" else None
                completed_job = wait_for(completed)
                assert probe.get("/api/runs/" + completed_job["run_id"]).status_code == 200
                report["dedicated_worker_real_queued_run"] = True
                # Execute actual downloaded OCR and embedding models in containers,
                # not just a presence/health check or the arithmetic support flow.
                extracted = probe.post("/api/assets/" + aid + "/ocr")
                assert extracted.status_code == 200
                assert any("123" in page["text"] for page in extracted.json()["pages"])
                report["container_real_tesseract_inference"] = True
                catalogue = json.loads((ROOT / "packages/module-registry/catalogue.json").read_text())
                rag_slug = next(module["slug"] for module in catalogue["modules"] if module["engine"] == "rag")
                answers = []
                for question in ["বাষ্পীভবন কী?", "সালোকসংশ্লেষণ কী?"]:
                    response = probe.post(f"/api/tools/{rag_slug}/jobs", json={"inputs": {"text": question}, "consent": True, "idempotency_key": uuid.uuid4().hex})
                    assert response.status_code == 202
                    jid = response.json()["id"]
                    retrieved_job = wait_for(completed)
                    answer = probe.get("/api/runs/" + retrieved_job["run_id"]).json()["output"]
                    assert answer["references"] and answer["facts"]["supported"]
                    assert answer["full_module_complete"] is False
                    answers.append(answer["facts"]["answer"])
                assert answers[0] != answers[1]
                report["container_real_onnx_retrieval_two_distinct_answers"] = True
                # Train/predict via actual production-mode network endpoints; fixtures
                # are synthetic and never presented as Bangladesh performance data.
                for index in range(25):
                    data = {"workspace_id": wid, "bill_type": "electricity", "month": f"{2022+index//12}-{index%12+1:02}",
                            "period_days": 30, "units": str(100+index*3), "consumption_bdt": str(1000+index*15),
                            "fixed_bdt": "50", "tax_bdt": "75", "stated_bdt": str(1125+index*15),
                            "confirmed": True, "processing_consent": True, "allow_personal_model": True, "is_demo": False}
                    assert probe.post("/api/bills/history", json=data).status_code == 201
                trained = probe.post("/api/bills/model/train", json={"workspace_id": wid, "bill_type": "electricity", "consent": True})
                assert trained.status_code == 503
                assert probe.post("/api/bills/predict", json=data).status_code == 503
                report["production_model_release_gate_enforced"] = True
                # Verify operator password login + fresh MFA on the same deployed API.
                operator_id, password = str(uuid.uuid4()), secrets.token_urlsafe(24)
                secret_values.append(password)
                with psycopg.connect(pg_dsn) as owner:
                    owner.execute("INSERT INTO users(id,email,password,name,role,verified,banned,language,mfa_enabled,created_at) VALUES(%s,%s,%s,'Integration operator','super_admin',true,false,'bn',false,%s)",
                                  (operator_id, "operator@integration.invalid", PasswordHasher(time_cost=3,memory_cost=65536,parallelism=2).hash(password), "2026-10-28T00:00:00+00:00"))
                    owner.execute("INSERT INTO workspaces(id,user_id,name) VALUES(%s,%s,'Operator work')", (str(uuid.uuid4()), operator_id))
                with client() as operator:
                    login = operator.post("/api/auth/login", json={"email": "operator@integration.invalid", "password": password})
                    assert login.status_code == 200
                    operator.headers["x-csrf-token"] = login.json()["csrf"]
                    assert operator.get("/api/admin/overview").status_code == 403
                    enrollment = operator.post("/api/auth/mfa/enroll").json()
                    assert operator.post("/api/auth/mfa/verify", json={"value": {"code": totp(enrollment["secret"])}}).status_code == 200
                    assert operator.get("/api/admin/overview").status_code == 200
                    assert operator.get("/api/runs/" + completed_job["run_id"]).status_code == 404
                    check_directory_integration(operator, client, pg_dsn, secret_values, probe)
                    report["rights_reviewed_directory_real_tls_queue_and_revocation"] = True
                report["real_operator_login_mfa_and_private_record_denial"] = True
                # A real retention worker must erase expired guests + actual S3
                # bytes + derived artifacts, without deleting the operator.
                with psycopg.connect(pg_dsn) as owner:
                    owner.execute("UPDATE sessions SET expires=0 WHERE user_id=%s", (scope["visitor_id"],))
                def removed():
                    with psycopg.connect(pg_dsn) as owner:
                        return owner.execute("SELECT 1 FROM users WHERE id=%s", (scope["visitor_id"],)).fetchone() is None
                wait_for(removed, seconds=30)
                assert s3.list_objects_v2(Bucket="mouchak-private-test").get("KeyCount", 0) == 0
                with psycopg.connect(pg_dsn) as owner:
                    assert owner.execute("SELECT 1 FROM users WHERE id=%s", (operator_id,)).fetchone()
                report["real_expiry_worker_history_db_and_s3_deletion"] = True
            # Run the exact operator-facing CLI against this real TLS/container
            # stack; it creates/clears only its own additional visitor scopes.
            smoke = subprocess.run([sys.executable, "-m", "services.model_worker.deployment_smoke"],
                                   cwd=ROOT, env={**os.environ, "PRIVATE_API_URL": base,
                                   "PUBLIC_ORIGIN": "https://mouchak.integration.test", "PRIVATE_API_TOKEN": api_token,
                                   "MOUCHAK_SMOKE_CA_FILE": str(folder / "tls/ca.crt")},
                                   capture_output=True, text=True, timeout=300)
            if smoke.returncode:
                failed_operation.append(smoke.stdout[-2000:])
                raise AssertionError("Deployment smoke CLI did not pass")
            assert json.loads(smoke.stdout)["result"] == "passed"
            report["deployment_smoke_cli_verified_in_fixture"] = True
            report["result"] = "passed"
            (ROOT / "docs/audit/production-stack.json").write_text(json.dumps(report, indent=2) + "\n")
            print(json.dumps(report))
        except Exception as error:
            evidence.write_text(json.dumps({**report, "result": "failed", "error_class": type(error).__name__}, indent=2) + "\n")
            # Never dump request/response bodies, passwords, tokens or raw DB URLs.
            logs = subprocess.run([*compose, "logs", "--no-color", "--tail", "180"], cwd=ROOT, env=env, capture_output=True, text=True).stdout
            logs = "\n".join(failed_operation) + "\n" + logs
            for secret in [*secret_values, env["MOUCHAK_TEST_S3_KEK"]]:
                logs = logs.replace(secret, "[REDACTED]")
            logs = re.sub(r"SCRAM-SHA-256\$[^\s'\",]+|\$argon2(?:id|i|d)\$[^\s'\",]+", "[HASH REDACTED]", logs)
            print(json.dumps({"error_class": type(error).__name__, "sqlstate": getattr(error, "sqlstate", None)}), file=sys.stderr)
            print(json.dumps({"completed_checks": report, "failure_location": [{"file": Path(frame.filename).name, "line": frame.lineno} for frame in traceback.extract_tb(error.__traceback__)][-3:], "wait_diagnostic": str(error) if isinstance(error, AssertionError) and str(error).startswith("Timed out waiting for fixture operation:") else None}), file=sys.stderr)
            print(logs[-36000:], file=sys.stderr)
            raise RuntimeError("Isolated production-stack integration failed; sanitized service logs above") from None
        finally:
            # Exact randomized fixture project only. Never prune other resources.
            subprocess.run([*compose, "down", "--volumes", "--remove-orphans"], cwd=ROOT, env=env, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, timeout=90)


if __name__ == "__main__":
    main()
