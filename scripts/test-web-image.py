"""Run only this test's disposable loopback web container; no cloud deployment."""
import json, subprocess, time, urllib.request, urllib.error, uuid

name = "mouchak-web-check-" + uuid.uuid4().hex[:12]
def docker(*args):
    return subprocess.check_output(["docker", *args], text=True).strip()

try:
    docker("run", "--detach", "--name", name, "--publish", "127.0.0.1::3000", "mouchak-web:ci")
    state = json.loads(docker("inspect", name))[0]
    assert state["Config"]["User"] == "node"
    port = state["NetworkSettings"]["Ports"]["3000/tcp"][0]["HostPort"]
    base = "http://127.0.0.1:" + port
    for attempt in range(40):
        try:
            with urllib.request.urlopen(base, timeout=3) as response:
                body = response.read()
                assert response.status == 200 and b"Mouchak" in body
                assert response.headers.get("X-Content-Type-Options") == "nosniff"
                assert response.headers.get("X-Frame-Options") == "DENY"
            break
        except (urllib.error.URLError, ConnectionError):
            if attempt == 39:
                raise RuntimeError("Disposable web container did not become ready") from None
            time.sleep(0.5)
    for path, framing, ancestor in [('/admin/site-preview/DEMO-unpublished-version','SAMEORIGIN',"frame-ancestors 'self'"),('/admin/site-builder','DENY',"frame-ancestors 'none'"),('/work','DENY',"frame-ancestors 'none'")]:
        with urllib.request.urlopen(base+path, timeout=10) as response:
            html=response.read().decode()
            assert response.status==200
            assert response.headers.get('X-Frame-Options')==framing
            assert ancestor in response.headers.get('Content-Security-Policy','')
            assert 'noindex' in html
    try:
        urllib.request.urlopen(base + "/api/modules", timeout=10)
        raise AssertionError("An absent private backend must not appear successful")
    except urllib.error.HTTPError as error:
        assert error.code == 503
    print("Actual non-root standalone web image: HTTP page, security headers, narrowly scoped preview framing, private noindex and absent-backend 503 passed.")
finally:
    subprocess.run(["docker", "rm", "--force", name], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
