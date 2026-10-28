"""Durable scheduled-CMS worker. Run with a dedicated PostgreSQL role in production."""

import json, os, signal, threading, time
from sqlalchemy import text
from .store import DB, PRODUCTION, migrate
from . import retail, collaboration, operations


def verify_role(db):
    if PRODUCTION and db.scalar(text("SELECT current_user")) != "mouchak_scheduler":
        raise RuntimeError(
            "Production scheduler requires the dedicated mouchak_scheduler database role"
        )


def main():
    interval = max(1, min(300, int(os.getenv("SCHEDULER_POLL_SECONDS", "15"))))
    if not PRODUCTION:
        migrate()
    stop = threading.Event()
    for sig in [signal.SIGTERM, signal.SIGINT]:
        signal.signal(sig, lambda *_: stop.set())
    while not stop.is_set():
        try:
            with DB.begin() as db:
                verify_role(db)
                done = operations.run_due(db)
            # Counts only. No private inputs, permissions evidence or credentials.
            print(
                json.dumps({"scheduler_poll": "ok", "completed": len(done)}), flush=True
            )
        except Exception:
            # Runtime errors do not print database URLs or credentials.
            print(
                json.dumps({"scheduler_poll": "failed", "retry_seconds": interval}),
                flush=True,
            )
            if PRODUCTION:
                # A role/configuration failure must fail startup visibly.
                with DB() as db:
                    verify_role(db)
        stop.wait(interval)


if __name__ == "__main__":
    main()
