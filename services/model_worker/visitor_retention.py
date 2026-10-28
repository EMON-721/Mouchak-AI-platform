"""Expired anonymous-scope deletion worker. Never deletes historical accounts."""

import json, os, signal, threading
from .store import DB, PRODUCTION, migrate
from sqlalchemy import text
from . import anonymous, retail, collaboration, operations, uploads, rate_limit


def verify_role(db):
    if PRODUCTION and db.scalar(text("SELECT current_user")) != "mouchak_retention":
        raise RuntimeError("Production cleanup requires dedicated mouchak_retention role")


def main():
    with DB() as db:
        verify_role(db)
    if not PRODUCTION:
        migrate()
    interval = max(5, min(3600, int(os.getenv("VISITOR_RETENTION_POLL_SECONDS", "60"))))
    stopped = threading.Event()
    for sig in [signal.SIGTERM, signal.SIGINT]:
        signal.signal(sig, lambda *_: stopped.set())
    while not stopped.is_set():
        try:
            print(json.dumps(anonymous.purge_expired()), flush=True)
            with DB.begin() as db:
                verify_role(db)
                uploads.cleanup(db)
                rate_limit.cleanup(db)
        except Exception:
            print(
                json.dumps(
                    {
                        "expired_visitor_cleanup": "failed",
                        "retry_after_seconds": interval,
                    }
                ),
                flush=True,
            )
        stopped.wait(interval)


if __name__ == "__main__":
    main()
