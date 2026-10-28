// Fail visibly before publishing a frontend whose private backend is missing.
export async function verifyBackend(env = process.env, fetcher = fetch) {
  const fail = () => {
    throw Error(
      "Configure an HTTPS PRIVATE_API_URL and a private token (32+ characters) in Netlify Builds and Functions scopes. See docs/NETLIFY.md.",
    );
  };
  let base;
  try {
    base = new URL(env.PRIVATE_API_URL);
  } catch {
    fail();
  }
  if (
    base.protocol !== "https:" ||
    base.username ||
    base.password ||
    base.search ||
    base.hash ||
    base.pathname !== "/" ||
    ["localhost", "127.0.0.1", "[::1]"].includes(base.hostname) ||
    (env.PRIVATE_API_TOKEN || "").length < 32
  )
    fail();
  let response;
  try {
    response = await fetcher(new URL("/api/health", base), {
      headers: { "x-internal-api-token": env.PRIVATE_API_TOKEN },
      redirect: "error",
      cache: "no-store",
      signal: AbortSignal.timeout(10000),
    });
    const state = await response.json();
    if (
      !response.ok ||
      state.api !== "ok" ||
      state.tools !== 50 ||
      state.processing_mode !== "queued"
    )
      throw Error("not ready");
    return {
      private_backend_reachable: true,
      processing_mode: "queued",
      full_production_scope_certified: false,
    };
  } catch {
    throw Error(
      "Private backend check failed. Verify TLS, matching internal tokens and ENABLE_DURABLE_INFERENCE=1 on the Linux host. No credentials were logged.",
    );
  }
}

if (
  process.argv[1] &&
  import.meta.url === new URL(process.argv[1], "file:").href
) {
  try {
    console.log(JSON.stringify(await verifyBackend()));
  } catch (e) {
    console.error(e.message);
    process.exitCode = 1;
  }
}
