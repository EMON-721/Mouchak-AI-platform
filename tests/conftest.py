import os, sys, tempfile, shutil
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
TEST_STATE = tempfile.mkdtemp(prefix="mouchak-tests-")
os.environ["MOUCHAK_STATE_DIR"] = TEST_STATE
os.environ["MOUCHAK_ENV"] = "test"
os.environ["OPENBLAS_NUM_THREADS"] = "2"
import pytest
from fastapi.testclient import TestClient
from services.model_worker.main import app, RATE
from services.model_worker.store import DB, User
from services.model_worker.auth import totp


class Client:
    def __init__(self, client):
        self.client = client
        self.csrf = None

    def request(self, method, path, **kw):
        headers = kw.pop("headers", {})
        if self.csrf:
            headers["x-csrf-token"] = self.csrf
        return self.client.request(method, path, headers=headers, **kw)

    def register(self, name="Test user"):
        import uuid

        # Seed historical principals privately for the preserved legacy/security
        # regression cases. Public visitors use /api/session without this setup.
        email = f"{uuid.uuid4().hex}@example.test"
        r = self.request("POST", "/api/session")
        assert r.status_code == 200, r.text
        self.csrf = r.json()["csrf"]
        from services.model_worker.auth import PH

        with DB.begin() as db:
            actor = db.get(User, r.json()["visitor_id"])
            actor.email = email
            actor.name = name
            actor.password = PH.hash("Test-password-12345!")
            actor.role = "user"
        self.user = {
            "id": r.json()["visitor_id"],
            "email": email,
            "name": name,
            "role": "user",
        }
        return self

    def admin(self, role="super_admin"):
        with DB.begin() as db:
            db.get(User, self.user["id"]).role = role
        r = self.request("POST", "/api/auth/mfa/enroll")
        assert r.status_code == 200, r.text
        self.secret = r.json()["secret"]
        r = self.request(
            "POST", "/api/auth/mfa/verify", json={"value": {"code": totp(self.secret)}}
        )
        assert r.status_code == 200, r.text
        return self


@pytest.fixture(scope="session", autouse=True)
def application():
    with TestClient(app) as c:
        yield c
    shutil.rmtree(TEST_STATE, ignore_errors=True)


@pytest.fixture(autouse=True)
def rate_reset():
    RATE.clear()


@pytest.fixture
def client():
    with TestClient(app) as c:
        yield Client(c)


@pytest.fixture
def user(client):
    return client.register()


@pytest.fixture
def admin(user):
    return user.admin()
