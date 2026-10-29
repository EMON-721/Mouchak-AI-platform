"""Selected public-source checks. Reports paths/rules only, never secret values."""
import argparse
import re
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RULES = {
    "private-key": re.compile(rb"-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----"),
    "github-token": re.compile(rb"gh[pousr]_[A-Za-z0-9]{36,}"),
    "openai-key": re.compile(rb"sk-(?:proj-|svcacct-)?[A-Za-z0-9_-]{32,}"),
    "aws-key": re.compile(rb"AKIA[0-9A-Z]{16}"),
}
URI = re.compile(rb"(?:postgres(?:ql)?(?:\+psycopg)?|mysql|mongodb(?:\+srv)?|rediss?)://[^/\s:@]+:([^@\s]+)@([^\s/'\"<>]+)", re.I)
DUMMY = re.compile(rb"replace|example|test|fixture|placeholder|your[_-]|change[_-]?me|^password$|^secret$|^unused$|^x+$|\$\{|^<|^\{[A-Za-z_][A-Za-z0-9_]*(?:\[[A-Za-z_][A-Za-z0-9_]*\])?\}$", re.I)


def findings(path, data):
    issues = set()
    pieces = Path(path).parts
    if any(p in {".state", ".venv", "node_modules", "backups", "upload"} for p in pieces):
        issues.add("private-runtime-artifact")
    name = Path(path).name
    if name.startswith(".env") and name != ".env.example":
        issues.add("environment-file")
    if name.endswith((".clixml", ".dpapi", ".mouchak", ".db", ".sqlite", ".sqlite3", ".key")):
        issues.add("private-runtime-artifact")
    if b"\x00" in data:
        return sorted(issues)
    for rule, pattern in RULES.items():
        if pattern.search(data):
            issues.add(rule)
    for match in URI.finditer(data):
        if not DUMMY.search(match.group(1)):
            issues.add("credential-bearing-database-url")
    return sorted(issues)


def git(*args):
    return subprocess.check_output(["git", *args], cwd=ROOT)


def check(history=False):
    issues = set()
    paths = git("ls-files", "--cached", "--others", "--exclude-standard", "-z").split(b"\0")
    for raw in set(paths) - {b""}:
        path = raw.decode()
        file = ROOT / path
        if file.is_file():
            for rule in findings(path, file.read_bytes()):
                issues.add((path, rule))
    blobs = 0
    if history:
        objects = {}
        for line in git("rev-list", "--objects", "--all").decode().splitlines():
            sha, _, path = line.partition(" ")
            if path:
                objects.setdefault(sha, path)
        sizes = subprocess.check_output(
            ["git", "cat-file", "--batch-check=%(objectname) %(objecttype) %(objectsize)"],
            input=("\n".join(objects) + "\n").encode(), cwd=ROOT,
        ).decode().splitlines()
        selected = [line.split()[0] for line in sizes if line.split()[1] == "blob"]
        process = subprocess.Popen(["git", "cat-file", "--batch"], stdin=subprocess.PIPE, stdout=subprocess.PIPE, cwd=ROOT)
        try:
            for sha in selected:
                process.stdin.write((sha + "\n").encode()); process.stdin.flush()
                header = process.stdout.readline().split()
                data = process.stdout.read(int(header[2]))
                process.stdout.read(1)
                blobs += 1
                for rule in findings(objects[sha], data):
                    issues.add(("history:" + objects[sha], rule))
        finally:
            process.stdin.close()
            process.stdout.close()
            process.wait()
    for path, rule in sorted(issues):
        print(f"BLOCKED {rule}: {path}")
    print(f"Public-source selected-pattern check: {len(issues)} finding(s); {blobs} historical blobs checked.")
    print("This does not certify every secret, personal identifier or redistribution right.")
    return not issues


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--history", action="store_true")
    raise SystemExit(0 if check(parser.parse_args().history) else 1)
