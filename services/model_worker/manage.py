"""Operational commands. Reads passwords through getpass; never command arguments."""

import argparse, getpass, json, os, hashlib, time
from pathlib import Path
from sqlalchemy import select, delete
from .store import *
from .auth import PH, ROLES, audit, password_valid
from . import (
    storage,
    retail,
    collaboration,
    operations,
    anonymous,
)  # register all additive tables before migration


def main():
    p = argparse.ArgumentParser()
    p.add_argument(
        "command",
        choices=[
            "migrate",
            "create-admin",
            "promote",
            "retention",
            "verify-audit",
            "inventory",
            "run-scheduled",
            "purge-visitors",
        ],
    )
    p.add_argument("--email")
    p.add_argument("--role", choices=sorted(ROLES), default="super_admin")
    p.add_argument("--dry-run", action="store_true")
    args = p.parse_args()
    if args.command == "migrate":
        migrate()
        print("Schema created idempotently; source review states preserved.")
        return
    if args.command == "purge-visitors":
        print(json.dumps(anonymous.purge_expired()))
        return
    with DB.begin() as db:
        if args.command == "run-scheduled":
            from .scheduler import verify_role

            verify_role(db)
            print(json.dumps(operations.run_due(db)))
            return
        if args.command in ["create-admin", "promote"]:
            if not args.email:
                raise SystemExit("--email is required")
            user = db.scalar(select(User).where(User.email == args.email.casefold()))
            if args.command == "create-admin":
                if user:
                    raise SystemExit(
                        "Existing account: use promote; no password was changed."
                    )
                password = getpass.getpass("New administrator password: ")
                password_valid(password)
                user = User(
                    email=args.email.casefold(),
                    password=PH.hash(password),
                    name="Platform administrator",
                    verified=True,
                )
                db.add(user)
                db.flush()
                db.add(Workspace(user_id=user.id, name="Personal"))
            if not user:
                raise SystemExit("Account not found")
            user.role = args.role
            audit(db, "operator-cli", "role_bootstrap", user.id, {"role": args.role})
            print("Role recorded. MFA enrollment and verification are still required.")
        elif args.command == "verify-audit":
            events = list(
                db.scalars(select(Audit).order_by(Audit.created_at, Audit.id))
            )
            prev = "0" * 64
            for event in events:
                expected = hashlib.sha256(
                    "|".join(
                        [
                            prev,
                            event.actor,
                            event.action,
                            event.target,
                            event.detail,
                            event.created_at,
                        ]
                    ).encode()
                ).hexdigest()
                if event.previous_hash != prev or event.event_hash != expected:
                    raise SystemExit("Audit chain verification failed")
                prev = event.event_hash
            print(json.dumps({"events": len(events), "chain_valid": True}))
        elif args.command == "retention":
            # Category policies are explicit and set by the operator, not silently guessed.
            days = int(os.getenv("RETENTION_DAYS", "90"))
            cut = time.time() - days * 86400
            removed = 0
            from datetime import datetime

            for r in db.scalars(select(Run)):
                if datetime.fromisoformat(r.created_at).timestamp() < cut:
                    removed += 1
                    if not args.dry_run:
                        db.delete(r)
            for a in db.scalars(select(Asset)):
                if datetime.fromisoformat(a.created_at).timestamp() < cut:
                    removed += 1
                    if not args.dry_run:
                        storage.remove(a.path)
                        db.delete(a)
            print(
                json.dumps(
                    {
                        "expired_records_and_files": removed,
                        "dry_run": args.dry_run,
                        "days": days,
                    }
                )
            )
        elif args.command == "inventory":
            print(
                json.dumps(
                    {
                        "database_adapter": engine.dialect.name,
                        "production": PRODUCTION,
                        "model_files": [
                            p.name for p in (ROOT / "models").glob("*") if p.is_file()
                        ],
                    }
                )
            )


if __name__ == "__main__":
    main()
